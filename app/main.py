from fastapi import FastAPI
from app.routes.query_router import router as query_router
from app.routes.upload_router import router as upload_router
from app.routes.hackrx import router as hackrx_router

from app.logger.logger import LoggingMiddleware  # 👈 import middleware

app = FastAPI()

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Register routes
app.include_router(upload_router, prefix="/upload")
app.include_router(query_router, prefix="/ask")
app.include_router(hackrx_router, prefix="/api/v1/hackrx")


@app.get("/")
def root():
    return {"message": "RAG API running"}
