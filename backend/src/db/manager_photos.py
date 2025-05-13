from datetime import datetime
from typing import Any

from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload

from src.config import settings
from src.db.base import BaseManager
from src.db.db import get_async_session
from src.logger import database_logger
from src.models import Users, Photos, UserSavedPhoto, Contours
from src.schemas.photos import PhotoCreate
from src.utils.s3_jobs import delete_photo_s3


class PhotosManager(BaseManager):
    model = Photos

    @staticmethod
    async def create_with_author(session: AsyncSession,
                                 photo_inf: PhotoCreate,
                                 author_id,
                                 request_id) -> Any:
        try:
            photoOrm = Photos(
                name=str(photo_inf.num_images) + '.png',
                num_images=photo_inf.num_images,
                author_uuid=author_id,
                file_uuid=photo_inf.uuid_file,
                url=f'.png',
            )
            session.add(photoOrm)
            await session.flush()
            photoOrm.url = f'{settings.S3_ENDPOINT}/{author_id}/{photoOrm.uuid}.png'

            user_photo = UserSavedPhoto(
                user_uuid=author_id,
                photo_uuid=photoOrm.uuid,
            )
            session.add(user_photo)
            await session.flush()

        except IntegrityError as e:
            await session.rollback()

            if "uq_photo" in str(e.orig):
                database_logger.warning(
                    "This photo already exists",
                    extra={
                        "file_uuid": str(photo_inf.uuid_file),
                        "requested_images": photo_inf.num_images,
                        "user_uuid": str(author_id),
                        "request_id": request_id,
                    }
                )
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail={"msg": "This photo already exists", "request_id": request_id})

            database_logger.error(
                "IntegrityError (idk)",
                extra={
                    "file_uuid": str(photo_inf.uuid_file),
                    "requested_images": photo_inf.num_images,
                    "user_uuid": str(author_id),
                    "request_id": request_id,
                },
                exc_info=e,
            )
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail={"msg": "Could not create the saved photo",
                                        "request_id": request_id})
        except Exception as e:
            await session.rollback()
            database_logger.error(
                str(e),
                extra={
                    "file_uuid": str(photo_inf.uuid_file),
                    "requested_images": photo_inf.num_images,
                    "user_uuid": str(author_id),
                    "request_id": request_id,
                },
                exc_info=e,
            )
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail={"msg": "Could not create the saved photo",
                                        "request_id": request_id})
        await session.commit()
        await session.refresh(photoOrm)

        database_logger.info(
            "Photo create successfully",
            extra={
                "user_id": str(photoOrm.author_uuid),
                "photo_uuid": str(photoOrm.uuid),
                "request_id": request_id,
            }
        )

        return photoOrm

    @staticmethod
    async def get_photo_with_author(session: AsyncSession, user_id: str, request_id) -> Any:
        query = select(Users).where(Users.uuid == user_id).options(selectinload(Users.saved_photos_direct)
                                                                   .selectinload(Photos.file), selectinload(Users.contours).
                                                                   selectinload(Contours.file))
        res = (await session.execute(query)).scalar()
        return res

    @staticmethod
    async def delete_photo(session: AsyncSession, photo_id: UUID4, user_id: str, request_id):
        query = (
            select(UserSavedPhoto)
            .join(UserSavedPhoto.user)
            .where(
                Users.uuid == user_id,
                UserSavedPhoto.photo_uuid == photo_id
            )
        )
        userPhoto: UserSavedPhoto | None = (await session.execute(query)).scalar()

        if userPhoto is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'msg': "Photo does not exist",
                                                                               'request_id': request_id})
        await session.delete(userPhoto)
        await session.commit()
        userPhoto.delete_at = datetime.now()
        return userPhoto

    @staticmethod
    async def delete_photos_all(photo_id: UUID4, user_id, request_id):
        async for session in get_async_session():
            query = select(UserSavedPhoto).where(UserSavedPhoto.photo_uuid == photo_id)
            res = [i for i in (await session.execute(query)).scalars()]

            if not res:
                try:
                    photo = await session.get(Photos, photo_id)
                except Exception as e:
                    raise e
                await session.delete(photo)
                await session.commit()
                print('1')
                await delete_photo_s3(photo_id, user_id, request_id)
                print('2')


photos_manager = PhotosManager()
