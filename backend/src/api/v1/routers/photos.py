from fastapi import APIRouter, Request, BackgroundTasks, Depends, HTTPException, status, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_async_session
from src.db.manager_files import fileManager
from src.db.manager_photos import photos_manager
from src.schemas.photos import PhotoCreate
from src.schemas.users import UserPhoto
from src.service.model import modelManager
from src.service.redis_conn import get_metadata, get_contours_cached, load_contours_cached, \
    load_clear_photo, get_clear_photo_cached
from src.service.s3 import create_add_photo_s3
from src.utils.file import get_file_bytes

router = APIRouter(prefix='/photos')


@router.post('/save')
async def saved_photos(
        request: Request,
        photo_data: PhotoCreate,
        background_task: BackgroundTasks,
        session: AsyncSession = Depends(get_async_session),
):
    request_id = request.state.request_id
    user_id = request.state.user_id
    metadata_file = await get_metadata(photo_data.uuid_file)

    # проверка слайса
    if metadata_file is None:
        await fileManager.get_metafile(
            session, photo_data.uuid_file, photo_data.num_images, request_id
        )

    else:
        if metadata_file.get('num_slices') < photo_data.num_images:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"msg": 'Requested number of images exceeds available slices in file', "request_id": request_id},
            )

    photoOrm = await photos_manager.create_with_author(session, photo_data, user_id, request_id)
    background_task.add_task(create_add_photo_s3, photoOrm, request_id)

    return photoOrm


@router.get('/')
async def get_photo(request: Request, session: AsyncSession = Depends(get_async_session)) -> UserPhoto:
    request_id = request.state.request_id
    user_id = request.state.user_id
    return await photos_manager.get_photo_with_author(session, user_id, request_id)


@router.delete('/{photo_id}/delete')
async def delete_photo(photo_id: UUID4,
                       background_task: BackgroundTasks,
                       request: Request,
                       session: AsyncSession = Depends(get_async_session)):
    request_id = request.state.request_id
    user_id = request.state.user_id
    photo_delete = await photos_manager.delete_photo(session, photo_id, user_id, request_id)
    background_task.add_task(photos_manager.delete_photos_all, photo_id, user_id, request_id)

    return photo_delete


@router.get('/{file_uuid}/{num_slices}/photos')
async def get_file_photo(background_task: BackgroundTasks, file_uuid: str, num_slices: int, request: Request,
                         session=Depends(get_async_session)):

    request_id = request.state.request_id
    if img := await get_clear_photo_cached(file_uuid, num_slices):
        return Response(content=img, media_type="image/png")

    file_bytes = await get_file_bytes(background_task, file_uuid, session=session, request_id=request_id,
                                      num_images=num_slices)
    image = modelManager.pred_image(file_bytes, num_slices)
    img = modelManager.get_photo(image)
    background_task.add_task(load_clear_photo, file_uuid, num_slices, img)

    return Response(content=img, media_type="image/png")


@router.get('/{file_uuid}/{num_slices}/contours')
async def get_file_photo(background_task: BackgroundTasks, file_uuid: str, num_slices: int, request: Request,
                         session=Depends(get_async_session)):
    try:
        if con := await get_contours_cached(file_uuid, num_slices):
            return con
        else:
            request_id = request.state.request_id
            file_bytes = await get_file_bytes(background_task, file_uuid, session=session, request_id=request_id,
                                              num_images=num_slices)
            image = modelManager.pred_image(file_bytes, num_slices)
            con = modelManager.get_result_contours(image)
            background_task.add_task(load_contours_cached, file_uuid, num_slices, con)
            return con
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(500)
