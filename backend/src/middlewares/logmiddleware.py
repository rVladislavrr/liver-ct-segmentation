import time
from uuid import uuid4
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from src.logger import api_logger


class LogExecutionTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        request_id = str(uuid4())
        request.state.request_id = request_id

        start_time = time.time()

        try:
            response = await call_next(request)
        except Exception as e:
            # Логирование необработанных исключений
            process_time = time.time() - start_time
            api_logger.error(
                f"request_id={request_id} | "
                f"method={request.method} | "
                f"path={request.url.path} | "
                f"error={str(e)} | "
                f"processing_time={process_time:.4f}s | "
                f"status=500"
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "request_id": request_id
                }
            )

        process_time = time.time() - start_time

        # Дополнительная информация для логирования
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "status_code": response.status_code,
            "processing_time": f"{process_time:.4f}s"
        }

        if response.status_code >= 500:
            api_logger.error(log_data)
        elif response.status_code >= 400:
            api_logger.warning(log_data)
        else:
            api_logger.info(log_data)

        # Добавляем request_id в заголовки ответа
        response.headers["X-Request-ID"] = request_id
        return response