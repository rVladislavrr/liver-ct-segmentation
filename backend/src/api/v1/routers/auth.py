from fastapi import (APIRouter, Response,
                     Depends, Request,
                     status)
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.db.db import get_async_session
from src.db.manager_user import users_manager
from src.schemas.users import Token, UserCreate, UserAuthenticate
from src.utils.auth_jwt import create_tokens, get_payload_refresh

router = APIRouter(prefix='/auth', responses={401: {'detail': "NOT AUTHORIZED"}}, tags=["Auth"])


@router.post('/registration', status_code=status.HTTP_201_CREATED,
             description='Регистрация пользователя')
async def register(request: Request,
                   response: Response,
                   user_data: UserCreate,
                   session: AsyncSession = Depends(get_async_session)) -> Token:
    request_id = request.state.request_id
    user_inf = await users_manager.create(session, user_data, request_id)

    return create_tokens(user_inf, response)


@router.post('/login', description='Авторизация или вход пользователя')
async def auth(request: Request,
               response: Response,
               user_data: UserAuthenticate,
               session: AsyncSession = Depends(get_async_session)) -> Token:
    request_id = request.state.request_id
    user_inf = await users_manager.authorization(session, user_data, request_id)
    return create_tokens(user_inf, response)


@router.post('/logout', description='Выход из аккаунта')
async def logout(request: Request, response: Response):
    if request.cookies.get(settings.auth_jwt.key_cookie):
        response.delete_cookie(settings.auth_jwt.key_cookie)
    return {
        'detail': {"msg": "Ok", "request_id": request.state.request_id}
    }


@router.post('/refresh', description='Обновление ассес токена через рефреш')
async def refresh(response: Response,
                  data=Depends(get_payload_refresh),
                  session: AsyncSession = Depends(get_async_session)) -> Token:
    user_data, request_id = data
    user_inf = await users_manager.get_user(session, user_data, request_id)
    return create_tokens(user_inf, response)
