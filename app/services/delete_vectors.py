import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load your environment variables from .env file
load_dotenv()

# Initialize Pinecone client
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Replace with your actual index name
index_name = os.getenv("PINECONE_INDEX_NAME")  # Or hardcode as: "your-index-name"
index = pc.Index(index_name)

# --- Method 1: Delete ALL vectors ---
def delete_all_vectors():
    # print(f"Deleting all vectors from index: {index_name}")
    index.delete(delete_all=True)
    # print("✅ All vectors deleted.")

# --- Method 2: Delete by specific vector IDs ---
def delete_vectors_by_ids(ids):
    print(f"Deleting vectors with IDs: {ids}")
    index.delete(ids=ids)
    print("✅ Selected vectors deleted.")

# --- Optional: Delete by metadata filter ---
def delete_vectors_by_metadata(metadata_filter: dict):
    print(f"Deleting vectors with metadata filter: {metadata_filter}")
    index.delete(filter=metadata_filter)
    print("✅ Vectors matching metadata deleted.")


if __name__ == "__main__":
    # Example usage:

    # 1. To delete ALL vectors
    delete_all_vectors()

    # 2. To delete specific vector IDs:
    # delete_vectors_by_ids(["doc-1", "doc-2"])

    # 3. To delete using metadata filter:
    # delete_vectors_by_metadata({"source": "notes.pdf"})
