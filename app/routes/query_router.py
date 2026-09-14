from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.query_service import query_documents
from app.auth.token_auth import verify_token
from app.services.query_service import query_documents_batch

router = APIRouter()

class QueryRequest(BaseModel):
    query: list

@router.post("/query", dependencies=[Depends(verify_token)])
async def query_route(req: QueryRequest):
    try:
        response = await query_documents_batch(req.query)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
