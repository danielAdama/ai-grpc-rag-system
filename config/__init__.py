from pathlib import Path
import os
from groq import Groq
import redis
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

BASE_DIR = Path(__file__).absolute().parent.parent

PROMPT_DIR = BASE_DIR / "gen_ai" / "prompt" / "templates"
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

redis_client = redis.Redis(
    host=os.environ.get("REDIS_HOST"), 
    port=int(os.environ.get("REDIS_PORT")),
    # db=os.environ.get("REDIS_DB"),
    password=os.environ.get("REDIS_PASSWORD")
)