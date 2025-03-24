from fastapi import HTTPException, status

from src.config import settings
from src.db.base import BaseManager
from src.models import Files


class FileManager(BaseManager):
    model = Files

    async def create(self, session, data):
        try:
            fileOrm = Files(filename=data['filename'],
                            size_bytes=data['size_bytes'],
                            num_slices=data['num_slices'],
                            )

            session.add(fileOrm)
            await session.flush()
            await session.refresh(fileOrm)

            obj_name = str(fileOrm.uuid) + ".nii"
            fileOrm.s3_url = f"{settings.S3_ENDPOIN}/{obj_name}"
            fileOrm.s3_url_processed = f"{settings.S3_ENDPOIN}/{obj_name}.processed"
            await session.commit()
            return fileOrm
        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail='Obj is not saved')

    async def get_metafile(self, session, uuid, num_images=0):
        try:
            try:
                file_db = await session.get(Files, uuid)
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="File Not Found")
            if not file_db:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="File Not Found")
            else:
                if num_images >= file_db.num_slices:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail='num_images >= num_slices in file')
        except HTTPException as httpE:
            raise httpE
        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail='database status unknown')
        return file_db


fileManager = FileManager()
