from fastapi import HTTPException, status

from src.config import settings
from src.db.base import BaseManager
from src.logger import database_logger
from src.models import Files


class FileManager(BaseManager):
    model = Files

    async def create(
            self,
            session,
            file_data,
            request_id
    ) -> Files:
        try:
            user_id = file_data.get("author_id")

            if user_id is None:
                file_data['is_public'] = True

            file_orm = Files(
                **file_data
            )

            session.add(file_orm)
            await session.flush()
            await session.refresh(file_orm)

            # # Generate S3 URLs
            # obj_name = f"{file_orm.uuid}.nii"
            # file_orm.s3_url = f"{settings.S3_ENDPOINT}/{obj_name}"
            # file_orm.s3_url_processed = f"{settings.S3_ENDPOINT}/{obj_name}.processed"

            await session.commit()

            database_logger.info(
                "File created successfully",
                extra={
                    "file_uuid": str(file_orm.uuid),
                    "file_name": file_orm.filename,
                    "request_id": request_id,
                }
            )
            return file_orm

        except Exception as e:
            await session.rollback()
            database_logger.error(
                "Failed to create file record",
                exc_info=e,
                extra={
                    "error": str(e),
                    "file_data": file_data,
                    "request_id": request_id,
                }
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"msg": "Failed to create file record in database", "request_id": request_id}
            )

    async def get_metafile(
            self,
            session,
            file_uuid,
            num_images,
            request_id
    ):
        try:
            file_db = await session.get(Files, file_uuid)

            if not file_db:
                database_logger.warning(
                    "File not found",
                    extra={
                        "file_uuid": str(file_uuid),
                        "request_id": request_id,
                    }
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"msg": "File not found", "request_id": request_id}
                )

            if num_images > file_db.num_slices:
                database_logger.warning(
                    "Requested number of images exceeds available slices",
                    extra={
                        "file_uuid": str(file_uuid),
                        "requested_images": num_images,
                        "available_slices": file_db.num_slices,
                        "request_id": request_id,
                    }
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"msg": 'Requested number of images exceeds available slices in file',
                            "request_id": request_id}
                )

            database_logger.info(
                "File metadata retrieved successfully",
                extra={
                    "file_uuid": str(file_uuid),
                    "request_id": request_id,
                }
            )
            return file_db

        except HTTPException:
            raise
        except Exception as e:
            database_logger.error(
                "Failed to retrieve file metadata",
                exc_info=e,
                extra={
                    "file_uuid": str(file_uuid),
                    "request_id": request_id,
                    "error": str(e),
                }
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"msg": 'Failed to retrieve file metadata',
                            "request_id": request_id}
            )


fileManager = FileManager()
