import os
import uuid
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# --- Load environment variables ---
load_dotenv()
ELASTIC_CLOUD_URL = os.getenv("ELASTIC_CLOUD_URL")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")

# --- Connect to Elasticsearch ---
es = Elasticsearch(
    ELASTIC_CLOUD_URL,
    api_key=ELASTIC_API_KEY,
    verify_certs=True
)

# --- Create index if it doesn't exist ---
def create_index_if_not_exists(index_name):
    if not es.indices.exists(index=index_name):
        es.indices.create(
            index=index_name,
            body={
                "settings": {"number_of_shards": 1, "number_of_replicas": 0},
                "mappings": {
                    "properties": {
                        "clause_id": {"type": "keyword"},
                        "text": {"type": "text"},
                        "source_doc": {"type": "keyword"},
                        "metadata": {"type": "object"}
                    }
                }
            }
        )
        print(f"✅ Created index: {index_name}")

# --- Delete all documents from the index ---
def delete_all_documents(index_name):
    es.delete_by_query(index=index_name, body={"query": {"match_all": {}}})
    print(f"🗑️ Deleted all documents from index: {index_name}")

# --- Index new chunks ---
def index_chunks(chunks, index_name):
    actions = []
    for i, chunk in enumerate(chunks):
        action = {
            "_index": index_name,
            "_id": str(uuid.uuid4()),
            "_source": {
                "text": chunk.get("text", ""),
                "metadata": chunk["metadata"],
                "source_doc": chunk.get("source_doc", "unknown"),
                "clause_id": f"clause_{i + 1}"
            }
        }
        actions.append(action)

    success, _ = bulk(es, actions)
    print(f"✅ Indexed {success} documents into {index_name}")
    return success

# --- Upsert Function ---
def Upsert(text_chunks, index_name):
    create_index_if_not_exists(index_name)
    # delete_all_documents(index_name)
    indexed = index_chunks(text_chunks, index_name)
    return f"✅ {indexed} clauses upserted to index '{index_name}'"

# --- Main block for testing ---
if __name__ == "__main__":
    # Example test chunks
    test_chunks = [
        {
            "text": "Clause 1: Coverage begins after 30 days of continuous enrollment.",
            "metadata": {"waiting_period": "30 days", "category": "General"}
        },
        {
            "text": "Clause 2: Accidental hospitalization is covered from day one.",
            "metadata": {"waiting_period": "0 days", "category": "Emergency"}
        }
    ]

    namespace = "policy_test_index_001"  # Dynamic index name
    result = Upsert(test_chunks, index_name=namespace)
    print(result)
