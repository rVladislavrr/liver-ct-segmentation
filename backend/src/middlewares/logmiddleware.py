import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from src.logger import api_logger


class LogExecutionTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        if response.status_code == 500:
            api_logger.error(f"{request.method};{response.status_code};{request.url.path};{process_time:.4f}s")
        else:
            api_logger.info(f"{request.method};{response.status_code};{request.url.path};{process_time:.4f}s")
        return response