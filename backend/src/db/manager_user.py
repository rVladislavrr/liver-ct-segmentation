import hashlib

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import BaseManager
from src.logger import database_logger
from src.models import Users
from src.schemas.users import UserCreate, UserInfo


class UsersManager(BaseManager):
    model = Users

    @staticmethod
    async def conflict_user(email, session, request_id):
        query = select(Users).where(Users.email == email)
        if (await session.execute(query)).scalar():
            database_logger.warning(
                "User already exists",
                extra={
                    "user_email": email,
                    "request_id": request_id,
                }
            )
            raise HTTPException(status_code=409, detail="User already exists")

    async def create(self, session: AsyncSession, data: UserCreate, request_id):
        await self.conflict_user(data.email, session, request_id)
        try:
            hash_password = hashlib.sha256(data.password.encode('utf-8')).hexdigest()

            userOrm = self.model(email=data.email, hash_password=hash_password)
            session.add(userOrm)
            await session.flush()
            database_logger.info(
                "User registered successfully",
                extra={
                    "user_uuid": str(userOrm.uuid),
                    "user_email": userOrm.email,
                    "request_id": request_id,
                }
            )

            await session.refresh(userOrm)
            await session.commit()
            return userOrm

        except Exception as e:
            await session.rollback()
            database_logger.error(
                "Failed to create user record",
                exc_info=e,
                extra={
                    "error": str(e),
                    "request_id": request_id,
                }
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create file record in database"
            )

    @staticmethod
    async def authorization(session: AsyncSession, user_data, request_id):
        try:
            query = select(Users).where(Users.email == user_data.email)
            user = (await session.execute(query)).scalar()
            enter_hash_password = hashlib.sha256(user_data.password.encode('utf-8')).hexdigest()
            if not user or enter_hash_password != user.hash_password:
                database_logger.info(
                    "User authorization failed 'Email or password wrong'",
                    extra={
                        "user_email": user.email,
                        "user_uuid": user.uuid,
                        "request_id": request_id,
                    }
                )
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Email or password wrong')

            database_logger.info(
                "User authorization successfully",
                extra={
                    "user_email": user.email,
                    "user_uuid": user.uuid,
                    "request_id": request_id,
                }
            )

            return user

        except HTTPException as httpE:
            database_logger.warning(
                "Failed to authorize user, email or password wrong",
                extra={
                    "user_email": user_data.email,
                    "request_id": request_id,
                }
            )

            raise httpE

        except Exception as e:
            database_logger.error(
                "Failed to auth user",
                exc_info=e,
                extra={
                    "error": str(e),
                    "request_id": request_id,
                }
            )

    @staticmethod
    async def get_user(session: AsyncSession, user_data: UserInfo, request_id):
        try:
            user = await session.get(Users, user_data.get('uuid'))

            if user is None:

                database_logger.warning(
                    "User not found",
                    extra={
                        "user_uuid": user_data.get('uuid'),
                        "request_id": request_id,
                    }
                )
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User with this uuid not found")

            return user
        except HTTPException as httpE:
            raise httpE
        except Exception as e:
            database_logger.error(
                "Cant get user",
                extra={
                    "user_uuid": user_data.get('uuid'),
                    "request_id": request_id,
                },
                exc_info=e,
            )


users_manager = UsersManager()
