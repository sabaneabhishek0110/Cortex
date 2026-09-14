from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from uuid import uuid4
import logging
import time
import json

# Setup logging
logging.basicConfig(
    filename="api_logs.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("api_logger")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid4())
        start_time = time.time()

        try:
            req_body = await request.body()
            req_data = req_body.decode("utf-8")
        except Exception:
            req_data = "Could not parse body"

        # --- Process the request and get response ---
        response = await call_next(request)

        # --- Capture response body (must clone it) ---
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        # Recreate the response so FastAPI can send it back
        response = Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )

        end_time = time.time()
        duration_ms = round((end_time - start_time) * 1000, 2)

        try:
            response_text = response_body.decode("utf-8")
        except Exception:
            response_text = "[Non-decodable response]"

        log_message = (
            f"Request ID: {request_id} | "
            f"Method: {request.method} | "
            f"URL: {request.url.path} | "
            f"Request: {req_data} | "
            f"Response: {response_text} | "
            f"Status Code: {response.status_code} | "
            f"Time: {duration_ms} ms"
        )

        logger.info(log_message)
        return response
