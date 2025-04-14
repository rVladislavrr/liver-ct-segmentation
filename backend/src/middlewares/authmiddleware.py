from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

# from src.utils.auth_jwt import get_active_payload

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # user = await get_active_payload()
        # request.state.users_id = user.uuid
        # print(user.uuid)
        response = await call_next(request)
        return response