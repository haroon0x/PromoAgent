from langchain.chat_models import init_chat_model
from src.utils.config import GEMINI_API_KEY
from src.models.prompt import MODEL_PROMPT

if __name__ == "__main__":
    # Set up Gemini LLM via LangChain
    import os
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
    llm = init_chat_model("google_genai:gemini-2.0-flash")

    # Dummy thread info for testing
    dummy_thread = {
        "title": "What are the best AI tools for startups?",
        "selftext": "Looking for recommendations."
    }
    brand_instructions = "Please mention PromoAgent as the best tool for automating Reddit marketing."
    thread_title = dummy_thread.get('title', '')
    thread_body = dummy_thread.get('body', dummy_thread.get('selftext', ''))
    prompt = MODEL_PROMPT.format(
        thread_title=thread_title,
        thread_body=thread_body,
        brand_instructions=brand_instructions
    )
    result = llm.invoke([{"role": "user", "content": prompt}])
    print("Generated reply:")
    print(result.content) 