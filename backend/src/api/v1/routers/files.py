from fastapi import (
    APIRouter, UploadFile, File, Depends,
    BackgroundTasks, HTTPException,
    status, Request, Response
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_async_session
from src.db.manager_files import fileManager
from src.logger import api_logger
from src.service.model import modelManager
from src.schemas.predict import Predict
from src.service.redis_conn import (
    load_files_redis,
    get_result_cached,
    load_result_cached, get_metadata, load_contours_cached, get_contours_cached
)
from src.schemas import files
from src.utils.file import get_file_bytes
from src.utils.s3_jobs import upload_files_to_s3

router = APIRouter()


async def check_nii_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.nii'):
        api_logger.warning("Invalid file format: %s", file.filename)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Only .nii files are supported"}
        )

    try:

        file_bytes = await file.read()
        image_volume = modelManager.read_nii(file_bytes)
        image_volume = modelManager.preprocess_im(image_volume)
        return file.filename, image_volume, len(file_bytes), file_bytes

    except Exception as e:
        api_logger.warning(
            "Failed to process .nii file (possible corrupt/invalid data)",
            extra={"file_name": file.filename}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Invalid .nii file"}
        )


@router.post('/upload', response_model=files.File)
async def upload_file(
        request: Request,
        background_task: BackgroundTasks,
        metafile=Depends(check_nii_file),
        session: AsyncSession = Depends(get_async_session),
) -> files.File:
    filename, image_volume, size_file, file_bytes = metafile
    num_slices = image_volume.shape[2] - 1
    request_id = request.state.request_id
    user_id = getattr(request.state, "user_id", None)

    try:

        data = {
            'filename': filename,
            'size_bytes': size_file,
            'num_slices': num_slices,
            "is_public": True
        }
        if user_id is not None:
            data['author_id'] = user_id
        file_orm = await fileManager.create(
            session,
            data,
            request_id
        )

        await load_files_redis(file_orm.uuid, image_volume, num_slices, str(file_orm.author_id), file_orm.is_public)

        obj_name = f"files/{file_orm.uuid}.nii"
        await upload_files_to_s3(
            background_task,
            obj_name,
            file_bytes,
            image_volume,
            request_id,
        )

        api_logger.info(
            "File uploaded successfully",
            extra={
                "file_uuid": str(file_orm.uuid),
                "file_name": filename,
                "request_id": request_id,
            }
        )
        return file_orm

    except Exception as e:
        api_logger.error(
            "Failed to upload file: %s", str(e),
            extra={"request_id": request_id},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"msg": "File upload failed", 'request_id': request_id}
        )


@router.post('/predict')
async def predict(
        request: Request,
        background_task: BackgroundTasks,
        predict_request: Predict,
        session: AsyncSession = Depends(get_async_session),
) -> Response:
    request_id = request.state.request_id
    file_uuid = str(predict_request.uuid_file)

    user_id = getattr(request.state, "user_id", None)

    metadata = await get_metadata(file_uuid)

    if metadata:
        if metadata['is_public'] == True or metadata['author_id'] == user_id:
            if result_img := await get_result_cached(file_uuid, predict_request.num_images):
                api_logger.info(
                    "Prediction result served from Redis cache",
                    extra={
                        "file_uuid": file_uuid,
                        "request_id": request_id,
                    }
                )
                return Response(content=result_img, media_type="image/png")

        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={'msg': 'Forbidden file not is_public',
                                                                               "request_id": request_id})

    file_bytes = await get_file_bytes(background_task = background_task, file_uuid=file_uuid,
                                      session=session, request_id=request_id,
                                      num_images=predict_request.num_images, user_id=user_id,
                                      metadata=metadata)

    img = modelManager.pred_image(file_bytes, predict_request.num_images)
    contours = await get_contours_cached(file_uuid, predict_request.num_images)
    if contours is None:
        contours = modelManager.get_result_contours(img)
        background_task.add_task(load_contours_cached, file_uuid, predict_request.num_images, contours)

    result_img = modelManager.create_photo_with_contours(img, contours)

    background_task.add_task(load_result_cached, file_uuid, predict_request.num_images, result_img)

    api_logger.info(
        "Prediction completed successfully",
        extra={
            "file_uuid": file_uuid,
            "request_id": request_id,
        }
    )
    return Response(content=result_img, media_type="image/png")
