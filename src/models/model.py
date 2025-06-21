import os
from langchain_openai import ChatOpenAI
from src.utils.config import ALCHEMYST_API_KEY
from src.models.prompt import MODEL_PROMPT

# For Alchemyst AI proxy - no OpenAI API key needed
BASE_URL_WITH_PROXY = "https://platform-backend.getalchemystai.com/api/v1/proxy/default"

def generate_replies(thread_info: dict, brand_instructions: str) -> str:
    """
    Generate a Reddit reply using Alchemyst AI proxy based on thread info and brand instructions.
    Returns the generated reply string.
    """
    llm = ChatOpenAI(
        api_key=ALCHEMYST_API_KEY,
        model="alchemyst-ai/alchemyst-c1",
        base_url=BASE_URL_WITH_PROXY,
    )
    
    thread_title = thread_info.get('title', '')
    thread_body = thread_info.get('body', thread_info.get('selftext', ''))
    prompt = MODEL_PROMPT.format(
        thread_title=thread_title,
        thread_body=thread_body,
        brand_instructions=brand_instructions
    )
    
    result = llm.invoke([{"role": "user", "content": prompt}])
    return result.content

