from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger("api-request")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
        return response
