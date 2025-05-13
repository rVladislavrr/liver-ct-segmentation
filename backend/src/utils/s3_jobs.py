import io
import pickle

from fastapi import HTTPException, status, BackgroundTasks

from src.config import settings
from src.logger import s3_logger
from src.service.model import modelManager
from src.service.redis_conn import get_contours_cached
from src.service.s3 import s3_client
from src.utils.file import get_file_bytes


async def upload_files_to_s3(
        background_tasks: BackgroundTasks,
        obj_name,
        file_bytes,
        image_volume,
        request_id,
) -> None:
    try:
        background_tasks.add_task(
            s3_client.upload_file,
            file_obj=file_bytes,
            obj_name=obj_name,
            bucket_name=settings.S3_PRIVATE_BUCKET_NAME,
            request_id=request_id
        )

        buffer = io.BytesIO()
        pickle.dump(image_volume, buffer)
        buffer.seek(0)

        background_tasks.add_task(
            s3_client.upload_file,
            file_obj=buffer.getvalue(),
            obj_name=f"{obj_name}.processed",
            bucket_name=settings.S3_PRIVATE_BUCKET_NAME,
            request_id=request_id
        )

        s3_logger.info(
            "Files scheduled for upload to S3",
            extra={
                "object_name": obj_name,
                "file_size": len(file_bytes),
                "processed_size": buffer.getbuffer().nbytes,
                "request_id": request_id,
            }
        )
    except Exception as e:
        s3_logger.error(
            "Failed to schedule S3 upload",
            exc_info=e,
            extra={
                "object_name": obj_name,
                "error": str(e),
                "request_id": request_id,
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule file upload"
        )


async def create_add_photo_s3(obj, request_id, session):
    try:
        obj.name = f'{obj.author_uuid}/{obj.uuid}.png'
        file_bytes = await get_file_bytes(file_uuid=obj.file_uuid, session=session, request_id=request_id,
                                          num_images=obj.num_images, )

        img = modelManager.pred_image(file_bytes, obj.num_images)
        contours = await get_contours_cached(obj.file_uuid, obj.num_images)
        if contours is None:
            contours = modelManager.get_result_contours(img)
        result_img = modelManager.create_photo_with_contours(img, contours)

        await s3_client.upload_file(result_img, obj.name,
                                    settings.S3_BUCKET_NAME, request_id)
        s3_logger.info(
            "Images scheduled for upload to S3",
            extra={
                "object_name": obj.name,
                "photo_uuid": obj.uuid,
                "request_id": request_id,
            }
        )
    except Exception as e:
        s3_logger.error(
            "Failed to schedule S3 upload",
            exc_info=e,
            extra={"object_name": obj.name,
                   "photo_uuid": obj.uuid,
                   "request_id": request_id, }
        )


async def save_add_photo_s3_contour(obj, request_id, session):
    try:
        name = f'contour/{obj.author_id}/{obj.id}_version_{obj.version}.png'
        file_bytes = await get_file_bytes(file_uuid=obj.file_uuid, session=session, request_id=request_id,
                                          num_images=obj.num_images, )

        img = modelManager.pred_image(file_bytes, obj.num_images)
        contours = obj.contours.get('points')
        result_img = modelManager.create_photo_with_contours(img, contours)

        await s3_client.upload_file(result_img, name,
                                    settings.S3_BUCKET_NAME, request_id)
        s3_logger.info(
            "Images scheduled for upload to S3",
            extra={
                "object_name": name,
                "photo_uuid": obj.id,
                "request_id": request_id,
            }
        )
    except Exception as e:
        s3_logger.error(
            "Failed to schedule S3 upload",
            exc_info=e,
            extra={
                   "photo_uuid": obj.id,
                   "request_id": request_id, }
        )


async def delete_photo_s3(photo_id, user_id, request_id):
    print('1.1')
    name = f'{user_id}/{photo_id}.png'
    print('1.2', name)
    await s3_client.delete_file(name, settings.S3_BUCKET_NAME, request_id)
    print('1.3')
