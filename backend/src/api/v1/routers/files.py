import io
import pickle

from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, Response, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.db.db import get_async_session
from src.db.manager_files import fileManager
from src.schemas.predict import Predict
from src.service.model import modelManager
from src.service.redis_conn import load_files_redis, get_files_redis, get_result_cached, load_result_cached
from src.service.s3 import s3_client, load_files_s3
from src.schemas import files
router = APIRouter()


async def check_nii_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.nii'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Only .nii files are supported'
                            )

    try:
        file_bytes = await file.read()
        image_volume = modelManager.read_nii(file_bytes)
        image_volume = modelManager.preprocess_im(image_volume)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Only .nii files are supported'
                            )
    return file.filename, image_volume, len(file_bytes), file_bytes


@router.post('/upload/')
async def upload_file(background_task: BackgroundTasks,
                      metafile=Depends(check_nii_file),
                      session: AsyncSession = Depends(get_async_session)) -> files.File:
    filename, image_volume, size_file, file_bytes = metafile
    num_slices = image_volume.shape[2] - 1

    fileOrm = await fileManager.create(session, {
        'filename': filename,
        'size_bytes': size_file,
        'num_slices': num_slices,
    })

    obj_name = str(fileOrm.uuid) + '.nii'

    await load_files_redis(fileOrm.uuid,
                           image_volume,
                           num_slices)
    load_files_s3(background_task,
                  obj_name,
                  file_bytes,
                  image_volume)

    return fileOrm


@router.post('/predict/')
async def predict(predict_request: Predict,
                  session: AsyncSession = Depends(get_async_session)
                  ):
    if result_img := await get_result_cached(predict_request.uuid_file, predict_request.num_images):
        return Response(content=result_img, media_type="image/png")

    file_bytes = await get_files_redis(predict_request.uuid_file, predict_request.num_images)

    if file_bytes is None:
        print('miss')
        file_db = await fileManager.get_metafile(session, predict_request.uuid_file, predict_request.num_images)

        s3_file_bytes = await s3_client.download_file(predict_request.uuid_file + ".nii.processed",
                                                      settings.S3_BUCKET_NAME)
        buffer = io.BytesIO(s3_file_bytes)
        file_bytes = pickle.load(buffer)

        await load_files_redis(file_db.uuid, file_bytes, file_db.num_slices)
    else:
        print('cache')
    result_img = modelManager.get_result(file_bytes, predict_request.num_images)

    await load_result_cached(predict_request.uuid_file, predict_request.num_images, result_img)
    return Response(content=result_img, media_type="image/png")
