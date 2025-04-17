from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload

from src.config import settings
from src.db.base import BaseManager
from src.logger import database_logger
from src.models import Users, Photos, UserSavedPhoto
from src.schemas.photos import PhotoCreate


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
                url=f'{settings.S3_ENDPOINT}/{author_id}/{photo_inf.uuid_file}_{photo_inf.num_images}.png',
            )
            session.add(photoOrm)
            await session.flush()

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
                                    detail="This photo already exists")

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
                                detail="Could not create the saved photo")
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
                                detail="Could not create the saved photo")
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
                                                                   .selectinload(Photos.file))
        res = (await session.execute(query)).scalar()
        return res


photos_manager = PhotosManager()
