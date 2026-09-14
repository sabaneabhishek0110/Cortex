import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from keybert import KeyBERT

# --- Load environment variables ---
load_dotenv()

ELASTIC_CLOUD_URL = os.getenv("ELASTIC_CLOUD_URL")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")

# --- Initialize KeyBERT model ---
kw_model = KeyBERT(model='all-MiniLM-L6-v2')

# --- Connect to Elasticsearch ---
es = Elasticsearch(
    ELASTIC_CLOUD_URL,
    api_key=ELASTIC_API_KEY,
    verify_certs=True
)

# --- Extract keywords from query using KeyBERT ---
def extract_keywords(query: str, top_n: int = 5) -> str:
    try:
        keywords = kw_model.extract_keywords(query, keyphrase_ngram_range=(1, 3), stop_words='english', top_n=top_n)
        keyword_phrases = [kw[0] for kw in keywords]
        return ", ".join(keyword_phrases)
    except Exception as e:
        print(f"❌ KeyBERT keyword extraction failed: {e}")
        return query  # fallback

# --- Search top matching clause from Elasticsearch ---
def search_best_clause(user_query: str, index_name: str) -> list[dict]:
    keywords = extract_keywords(user_query)
    # print(f"🔍 Extracted keywords: {keywords}")

    def run_search(query_string):
        return es.search(index=index_name, body={
            "size": 5,
            "query": {
                "match": {
                    "metadata.text": {
                        "query": query_string,
                        "operator": "OR",
                        "fuzziness": "AUTO"
                    }
                }
            }
        })

    # Try keyword-based query first
    response = run_search(keywords)

    # Fallback to raw user query if nothing found
    if not response["hits"]["hits"]:
        print("⚠️ No results with keywords, trying raw query.")
        response = run_search(user_query)

    if not response["hits"]["hits"]:
        return [{
            "score": 0.0,
            "text": "❌ No relevant clause found.",
            "source_doc": None,
            "clause_id": None,
            "metadata": {}
        }]

    # Return top 3 results
    results = []
    for hit in response["hits"]["hits"]:
        results.append({
            "score": hit["_score"],
            "text": hit["_source"]["metadata"]["text"],
            "source_doc": hit["_source"]["metadata"].get("source_doc"),
            "clause_id": hit["_source"]["metadata"].get("clause_id"),
            "metadata": hit["_source"]["metadata"]
        })
    return results

# --- Final callable function ---
def elasticSearchByQuery(user_query: str, index_name: str) -> list[dict]:
    return search_best_clause(user_query, index_name)

# --- Run locally ---
if __name__ == "__main__":
    query = input("🧠 Enter your query: ")
    index = input("📂 Enter the ElasticSearch index name (namespace): ")
    results = elasticSearchByQuery(query, index)

    print("\n🔍 Top Matches:\n")
    for i, r in enumerate(results):
        print(f"Result {i+1}")
        print(f"Score: {r['score']}")
        print(f"Clause: {r['text']}")
        print(f"Doc: {r['source_doc']} | Clause ID: {r['clause_id']}")
        print("-" * 60)
