
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from starlette.responses import JSONResponse

from src.logger import api_logger
from src.utils.auth_jwt import get_users_payload


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == 'OPTIONS':
            return await call_next(request)

        if (any(request.url.path.endswith(end) for end in ("/docs", "/openapi.json",))
                or "/auth/" in request.url.path):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")

        if request.url.path.endswith('/predict', ) or request.url.path.endswith('/upload'):
            if auth_header is None:
                return await call_next(request)

        try:
            token = auth_header.split(" ")[1]
        except Exception as e:
            api_logger.error(
                "Failed to auth",
                extra={"request_id": request.state.request_id},
                exc_info=e,
            )
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Invalid token",
                    "request_id": request.state.request_id,
                }
            )
        try:
            user = await get_users_payload(token)
            request.state.user_id = user.uuid
            request.state.user = user
            return await call_next(request)
        except HTTPException:
            api_logger.error(
                "Failed to auth, token invalid or expired",
                extra={"request_id": request.state.request_id},
            )
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Invalid token",
                    "request_id": request.state.request_id,
                }
            )
        except Exception as e:
            api_logger.error(
                str(e),
                extra={"request_id": request.state.request_id},
                exc_info=e,
            )
            raise e
