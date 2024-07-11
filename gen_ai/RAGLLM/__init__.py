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
        self.messages.append({'role': 'user', 'content': user_prompt.format(query=query)})
        completion2 = self.client.chat.completions.create(
            messages=self.messages,
            model="llama3-8b-8192", #self.model
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        conversation = completion2.choices[0].message.content
        self.messages.append({'role': 'assistant', 'content': conversation})
        self.save_messages()

        return conversation