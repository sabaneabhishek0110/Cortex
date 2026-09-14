from app.services.embedder import get_embedding
from app.utils.pinecone_client import index
from app.services.logic import enhance_query
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from app.services.elasticSearch.elasticQuerySearch import elasticSearchByQuery
from typing import List, Dict, Any
import logging
from functools import lru_cache
import asyncio
import re
import logging

# Initialize Gemini model
MODEL = genai.GenerativeModel("gemini-2.0-flash")

# 🔹 Sub-question decomposition
def decompose_query_heuristic(question: str) -> list[str]:
    # Normalize spaces and remove extra punctuation spacing
    question = re.sub(r'\s+', ' ', question).strip()
    
    # Split by conjunctions or commas
    parts = re.split(r'\b(?:and|or|as well as|,)\b', question, flags=re.IGNORECASE)

    # Clean up and filter
    subqueries = [p.strip().capitalize() for p in parts if len(p.strip()) > 8]

    # Fallback: if nothing was extracted, return the original
    return subqueries if subqueries else [question]


# 🔹 Summarizer for multiple answers
def multiple_query_summarizer(answers: List[str]) -> str:
    prompt = f"""
You’re an expert assistant synthesizing the final answer for the user.  
You have these partial answers to sub-questions (or retrieved contexts):

{answers}

❓ User wants a single, coherent response that includes **all relevant points** found above.

🔑 Instructions:
- Craft a **complete answer** rather than a disjointed summary of bullet points.
- Include **every piece of information** that directly answers any part of the original question.
- Keep it **concise**—aim for 3–5 sentences maximum.
- Maintain a **natural, human tone** (as if you’re explaining to a friend).
- Start with “Yes” or “No” when appropriate.
- **Do not** prefix with “Here’s a summary” or use list formatting.
- **Do not** omit any critical detail that answers the user’s question.

📝 Final Answer:
"""
    try:
        response = MODEL.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.warning(f"❌ Summarization failed: {e}")
        return " ".join(answers)


# 🔹 Query runner (shared)
async def _run_query(query: str, top_k: int = 5, similarity_threshold: float = 0.4, namespace: str = "default") -> str:
    query_vector = get_embedding(query)
    response = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        include_values=False,
        namespace=namespace
    )

    high_quality_matches = [
        match.get('metadata', {}).get('text', '').strip()
        for match in response.get('matches', [])
        if match.get('score', 0) >= similarity_threshold
    ]
    high_quality_matches = [text for text in high_quality_matches if text]

    max_context_length = 3000
    context_parts, current_length = [], 0
    for text in high_quality_matches:
        if current_length + len(text) > max_context_length:
            break
        context_parts.append(text)
        current_length += len(text)

    context = "\n\n".join(context_parts)
    elastic_data = elasticSearchByQuery(query, index_name=namespace)

    prompt = f"""Based on the following context, provide a concise and accurate answer.

Context:
{context}

ElasticSearch Context:
{elastic_data}

Question: {query}

Instructions:
- Answer strictly in 2 sentences maximum with all information from the context.
- If the answer is Yes/No, start with that.
- If the question is vague or has no context, say "Not relevant to the context".
- If no direct answer, offer relevant insight.
- Be specific and factual.
- give only precise information without any additional commentary.
- don't add words like "chunk"
- don't add source file name or document or any other metadata strictly
-don't add any extra information that is not present in the context strictly
Answer:"""

    response = MODEL.generate_content(
        prompt,
        generation_config=GenerationConfig(
            temperature=0.3,
            max_output_tokens=150,
            top_p=0.8,
            top_k=40
        )
    )
    return response.text.strip()


# 🔹 Main query handler

async def query_documents(user_query: str, top_k: int = 5, similarity_threshold: float = 0.4, namespace: str = "default") -> str:
    try:
        

        # 🔍 Step 2: Proceed with Gemini-based logic
        if len(user_query) > 90:
            subquestions = decompose_query_heuristic(user_query)
            # print(f"🔎 Decomposed subquestions: {subquestions}")

            # Run all _run_query calls concurrently using asyncio.gather
            all_answers = await asyncio.gather(*[
                _run_query(q, top_k, similarity_threshold, namespace)
                for q in subquestions
            ])

            return multiple_query_summarizer(all_answers)

        return await _run_query(user_query, top_k, similarity_threshold, namespace)

    except Exception as e:
        logging.error(f"Error in query_documents: {str(e)}")
        return "❌ I encountered an error while processing your question. Please try again."




# 🔁 Batch processing
async def query_documents_batch(queries: List[str], top_k: int = 5, namespace: str = "default") -> List[str]:
    results = []
    try:
        for query in queries:
            result = await query_documents(query, top_k=top_k, namespace=namespace)
            results.append(result)
    except Exception as e:
        logging.error(f"Batch processing error: {str(e)}")
        results = ["Error processing query" for _ in queries]
    return results


# 🧠 Sync cache wrapper
@lru_cache(maxsize=100)
def query_documents_cached(user_query: str, top_k: int = 5, namespace: str = "default") -> str:
    return asyncio.run(query_documents(user_query, top_k=top_k, namespace=namespace))