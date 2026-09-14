import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables from .env file
load_dotenv()

# Get the API key and index name from environment
api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME")

# Check if both are set
if not api_key or not index_name:
    raise ValueError("Missing Pinecone API key or index name in .env file.")

# Initialize Pinecone client
pc = Pinecone(api_key=api_key)

# Check if the index exists
if index_name not in pc.list_indexes().names():
    raise ValueError(f"Index '{index_name}' does not exist.")

# Connect to the index
index = pc.Index(index_name)

# Optional: Print confirmation
print(f"Connected to index '{index_name}'")
