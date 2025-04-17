from fastapi import APIRouter, Request, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_async_session
from src.db.manager_files import fileManager
from src.db.manager_photos import photos_manager
from src.schemas.photos import PhotoCreate
from src.schemas.users import UserPhoto
from src.service.redis_conn import get_metadata
from src.service.s3 import create_add_photo_s3

router = APIRouter(prefix='/photos')


@router.post('/save')
async def saved_photos(
        request: Request,
        photo_data: PhotoCreate,
        background_task: BackgroundTasks,
        session: AsyncSession = Depends(get_async_session),
):
    # Достать из редиса информацию о файле и сравнить слайс входит ли он или нет, если нет в редисе то достать из бд
    # и если нет вернуть ошибку
    # сохранить информацию о файле и сделать фоновую задачу на загрузку в s3

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
                detail='Requested number of images exceeds available slices in file'
            )

    # добавление инфы в бд что пользователь сохранил
    photoOrm = await photos_manager.create_with_author(session, photo_data, user_id, request_id)
    background_task.add_task(create_add_photo_s3, photoOrm, request_id)

    return photoOrm


@router.get('')
async def get_photo(request: Request, session: AsyncSession = Depends(get_async_session)) -> UserPhoto:
    request_id = request.state.request_id
    user_id = request.state.user_id
    return await photos_manager.get_photo_with_author(session, user_id, request_id)
