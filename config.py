import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
NAIRA_DOLLAR_CONVERSION = 1000