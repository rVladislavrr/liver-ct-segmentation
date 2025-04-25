import io
import pickle

from fastapi import HTTPException, status

from src.config import settings
from src.db.manager_files import fileManager
from src.logger import api_logger
from src.service.redis_conn import get_metadata, get_files_redis, load_files_redis
from src.service.s3 import s3_client


async def get_file_bytes(background_task, file_uuid, session, request_id, num_images: int = 0,
                         user_id: str = '', metadata=None) -> bytes:
    if metadata is None:
        metadata = await get_metadata(file_uuid)
    if metadata:
        if metadata['is_public'] == True or metadata['author_id'] == user_id:
            if num_images > metadata['num_slices']:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail={"msg": 'num_images > num_slices in file', 'request_id': request_id})

            file_bytes = await get_files_redis(file_uuid)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"msg": "Not public file",
                                                                               'request_id': request_id})
    else:

        api_logger.info(
            "Cache miss: loading file from S3",
            extra={
                "file_uuid": file_uuid,
                "request_id": request_id,
            }
        )

        file_db = await fileManager.get_metafile(
            session, file_uuid, num_images, request_id
        )
        s3_file_bytes = await s3_client.download_file(
            f"files/{file_uuid}.nii.processed",
            settings.S3_PRIVATE_BUCKET_NAME,
            request_id
        )

        file_bytes = pickle.load(io.BytesIO(s3_file_bytes))
        background_task.add_task(load_files_redis, file_db.uuid,
                                 file_bytes, file_db.num_slices,
                                 str(file_db.author_id), file_db.is_public)

    return file_bytes
