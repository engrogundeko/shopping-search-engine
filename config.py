import os
from dotenv import load_dotenv

load_dotenv()

SEARXNG_BASE_URL= os.getenv("SEARXNG_BASE_URL")
USER_AGENT= os.getenv("USER_AGENT")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
NAIRA_DOLLAR_CONVERSION = 1000
GOOGLE_SEARCH_ID = ...
GOOGLE_SEARCH_API_KEY=...