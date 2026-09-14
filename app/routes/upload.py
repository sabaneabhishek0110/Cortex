from fastapi import APIRouter, UploadFile, File
from app.services.document_loader import load_document
from app.services.chunker import chunk_text
from app.services.embedder import embed_chunks

upload_router = APIRouter()

@upload_router.post("/")
async def upload_doc(file: UploadFile = File(...)):
    text = await load_document(file)
    chunks = chunk_text(text)
    await embed_chunks(chunks)
    return {"status": "Uploaded and stored in Pinecone"}
