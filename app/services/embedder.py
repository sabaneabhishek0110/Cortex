import os
import re
import uuid
import asyncio
import concurrent.futures
from typing import List
from dotenv import load_dotenv
from app.utils.pinecone_client import index
import google.generativeai as genai
from app.services.elasticSearch.elasticSearchUpsert import Upsert as ElasticUpsert
from app.services.delete_vectors import delete_all_vectors

# Load environment variables
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ------------------------
# Clause grouping function
# ------------------------
def group_clauses(text: str) -> List[str]:
    """Enhanced clause grouping with regex patterns."""
    pattern = r'(\n\d+\)\s.*?\(Code\s-\w+\)|\n[a-z]\.\s)'
    parts = re.split(pattern, text)
    grouped_clauses = []
    if parts[0] and parts[0].strip():
        grouped_clauses.append(parts[0].strip())
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        grouped_clauses.append(f"{heading}\n{content}")
    return [clause for clause in grouped_clauses if clause]

# -----------------------
# Generate Gemini embeddings
# -----------------------
def get_embedding(text: str) -> List[float]:
    response = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return response["embedding"]

# ------------------------
# Run embedding async
# ------------------------
async def embed_chunk_async(executor, chunk):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, get_embedding, chunk)

# -------------------------
# Main async function
# -------------------------
async def embed_chunks_async(text_chunks, source_name, metadata_info, batch_size=10, np='default'):
    # STEP 0: Group clauses
    # delete_all_vectors()
    grouped_chunks = []
    for raw_text in text_chunks:
        grouped_chunks.extend(group_clauses(raw_text))

    grouped_chunks = [chunk.strip() for chunk in grouped_chunks if chunk.strip()]
    executor = concurrent.futures.ThreadPoolExecutor()

    # STEP 1: Embeddings
    tasks = [embed_chunk_async(executor, chunk) for chunk in grouped_chunks]
    embeddings = await asyncio.gather(*tasks)

    # STEP 2: Build metadata
    pinecone_data = []
    for i, (chunk, embedding) in enumerate(zip(grouped_chunks, embeddings)):
        metadata = {
            "text": chunk,
            "file_name": os.path.basename(source_name),
            "loc.lines.from": i * 10 + 1,
            "loc.lines.to": i * 10 + 10,
            "blobType": "application/pdf",
            "pdf.info.Author": metadata_info.get("author", "Unknown"),
            "pdf.info.CreationDate": metadata_info.get("creation_date", "Unknown"),
            "pdf.info.Creator": metadata_info.get("creator", "Unknown"),
            "source": metadata_info.get("source", "unknown"),
            "page_number": metadata_info.get("page_number", i + 1),
            "document_type": metadata_info.get("document_type", "unknown"),
            "language": metadata_info.get("language", "en"),
            "doc_version": metadata_info.get("doc_version", "v1.0"),
            "chunk_index": i,
            "namespace": np,
            "source_name": source_name
        }

        pinecone_data.append({
            "id": str(uuid.uuid4()),
            "values": embedding,
            "metadata": metadata
        })

    # STEP 3: Upsert to Pinecone
    with concurrent.futures.ThreadPoolExecutor() as thread_pool:
        futures = []
        for i in range(0, len(pinecone_data), batch_size):
            batch = pinecone_data[i:i + batch_size]
            futures.append(thread_pool.submit(index.upsert, batch, namespace=np))


        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                future.result()
                # print(f"✅ Batch {i + 1}/{len(futures)} inserted")
            except Exception as e:
                print(f"❌ Batch {i + 1} failed: {e}")

    # STEP 4: Also upsert to Elastic
    try:
        ElasticUpsert(pinecone_data, index_name=np)
        # print("✅ Data upserted to ElasticSearch")
    except Exception as e:
        print(f"❌ ElasticSearch upsert failed: {e}")

# -------------------------------
# Entrypoint function
# -------------------------------
async def embed_chunks(chunks,np='default'):
    await embed_chunks_async(chunks, source_name ="/Users/shubhamrade/Desktop/Bajaj/BAJHLIP23020V012223.pdf" , metadata_info = {},np=np)
