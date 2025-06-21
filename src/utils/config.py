"""
Configuration loader for PromoAgent.
"""
import os
from dotenv import load_dotenv


load_dotenv()

# reddit api config
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ALCHEMYST_API_KEY = os.getenv("ALCHEMYST_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def get_brand_instructions() -> str:
    """
    Load brand instructions from a file or environment variable.
    """
    return os.getenv("BRAND_INSTRUCTIONS", "") 

