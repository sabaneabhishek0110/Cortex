import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
# Set this up once at app startup, not every time
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def enhance_query(question: str) -> str:
    """
    Uses Gemini 2.0 Flash to rephrase a user query into a more specific one
    to improve semantic search relevance.
    """
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Gemini's API is synchronous, so run it in a thread
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        def generate_response():
            full_prompt = (
    "You are a query enhancement assistant for a legal and insurance document system.\n"
    "Your task is to rewrite the given short or vague user question into a clear, detailed, and formal question.\n"
    "Preserve the original intent while expanding abbreviations, inferring implied meaning, and adding context for better understanding.\n"
    "Do not answer the question — only rewrite it.\n\n"
    "Original question: {question}\n"
    "Descriptive version:"
)


            return model.generate_content(full_prompt)

        with ThreadPoolExecutor() as executor:
            response = await asyncio.get_event_loop().run_in_executor(executor, generate_response)

        enhanced_q = response.text.strip()
        print(f"Original Query: {question} -> Enhanced Query: {enhanced_q}")
        return enhanced_q

    except Exception as e:
        print(f"Error enhancing query: {e}")
        return question  # Fallback to the original question
