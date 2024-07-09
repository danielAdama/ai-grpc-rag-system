import re
import functools
import json
from groq import Groq
import redis
from typing import Optional, AnyStr, List, Union, Dict
from datetime import datetime as dt
from dotenv import load_dotenv, find_dotenv
from config.logger import Logger

_ = load_dotenv(find_dotenv())
logger = Logger(__name__)

class AIGenerator:
    def __init__(
            self, 
            system_prompt: AnyStr,
            context: AnyStr,
            client: Groq,
            redis_client: redis.Redis,
            tools: Union[List, None] = None,
            names_to_functions: Optional[Union[Dict, None]] = None,
            model: str = "llama3-70b-8192", 
            max_tokens: int = 150,
            temperature: float = 0.7,
            user_id: str = "test-user"
        ):
        self.system_prompt = system_prompt
        self.context = context
        self.client = client
        self.redis_client = redis_client
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.tools = tools
        self.names_to_functions = names_to_functions
        self.user_id = user_id
        self.messages = self.load_messages()
    
    def load_messages(self):
        messages = self.redis_client.get(f"{self.user_id}_messages")
        if messages:
            return json.loads(messages)
        return [{"role": "system", "content": self.system_prompt.format(context=self.context)}]
    
    def save_messages(self):
        self.redis_client.set(f"{self.user_id}_messages", json.dumps(self.messages))

    def run_conversation(self, user_prompt, query):
        self.add_user_message(user_prompt, query)

        if not self.tools:
            return self.process_response()

        if self.tools:
            tool_calls = self.check_tool_use()

            if not tool_calls:
                return self.process_response()

            if tool_calls:
                self.process_tool_calls(tool_calls)
                return self.process_response()

    def add_user_message(self, user_prompt, query):
        self.messages.append({'role': 'user', 'content': user_prompt.format(query=query)})
        self.save_messages()

    def process_response(self):
        completion = self.client.chat.completions.create(
            messages=self.messages,
            model="llama3-8b-8192",
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        conversation = completion.choices[0].message.content
        self.messages.append({'role': 'assistant', 'content': conversation})
        self.save_messages()

        return conversation

    def check_tool_use(self):
        completion = self.client.chat.completions.create(
            messages=self.messages,
            model=self.model,
            tools=self.tools,
            tool_choice="auto",
            temperature=0
        )
        response_message = completion.choices[0].message
        tool_calls = response_message.tool_calls
        logger.info(response_message)

        return tool_calls

    def process_tool_calls(self, tool_calls):
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            function_to_call = self.names_to_functions.get(function_name)
            if function_to_call:
                try:
                    function_response = function_to_call(**function_args) if function_args else function_to_call()
                    self.messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    })
                except TypeError as ex:
                    logger.error(f"Error calling function {function_name}: {ex}")
            else:
                logger.error(f"Function {function_name} not found in names_to_functions")

        self.save_messages()