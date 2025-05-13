from fastapi import APIRouter, BackgroundTasks, Request, Path, Depends, HTTPException, status
from pydantic import UUID4, BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.config import settings
from src.db.db import get_async_session
from src.db.manager_files import fileManager
from src.service.redis_conn import get_metadata
from src.models import Contours
from src.utils.s3_jobs import save_add_photo_s3_contour


class ContoursSave(BaseModel):
    points: list[list[list[float]] | list[float]]


router = APIRouter()


@router.post('/{file_uuid}/{num_slices}/save')
async def save_contours(background_task: BackgroundTasks, file_uuid: UUID4, request: Request,
                        contours: ContoursSave,
                        num_slices: int = Path(ge=0),
                        session: AsyncSession = Depends(get_async_session)):
    request_id = request.state.request_id
    user_id = request.state.user_id
    metadata_file = await get_metadata(file_uuid)

    if metadata_file is None:
        await fileManager.get_metafile(
            session, file_uuid, num_slices, request_id
        )

    else:
        if metadata_file.get('num_slices') < num_slices:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"msg": 'Requested number of images exceeds available slices in file', "request_id": request_id},
            )

    res = (await session.execute(
        select(Contours).where(
            Contours.author_id == user_id,
            Contours.file_uuid == file_uuid,
            Contours.num_images == num_slices,
        ).order_by(Contours.version.desc())
    )).first()

    if res:
        version = res[0].version + 1
    else:
        version = 1

    contourOrm = Contours(
        version=version,
        author_id=user_id,
        file_uuid=file_uuid,
        contours=dict(contours),
        num_images=num_slices,
        url=f'.png',
    )
    session.add(contourOrm)
    await session.flush()
    contourOrm.url = f'{settings.S3_ENDPOINT}/contour/{contourOrm.author_id}/{contourOrm.id}_version_{contourOrm.version}.png'
    await session.commit()
    await session.refresh(contourOrm)
    background_task.add_task(save_add_photo_s3_contour, contourOrm, request_id, session)

    return contourOrm
