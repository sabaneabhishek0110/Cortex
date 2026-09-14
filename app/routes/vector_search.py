from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List
from app.services.retrive_from_query import search_vector_db

# Initialize router
vector_search_router = APIRouter()

# Input model
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

# Output model
class SearchResult(BaseModel):
    score: float
    text: str
    chunk_index: int
    page_number: int
    document_type: str
    file_name: str
    source: str
    language: str

# POST route for vector search
@vector_search_router.post("/search", response_model=List[SearchResult])
async def search(request: SearchRequest):
    return search_vector_db(request.query, request.top_k)
