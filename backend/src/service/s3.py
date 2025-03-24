import pickle
from contextlib import asynccontextmanager
import io

from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from fastapi import HTTPException, status

from src.config import settings


def load_files_s3(background_task, obj_name, file_bytes, image_volume):
    try:
        background_task.add_task(s3_client.upload_file,
                                 file_obj=file_bytes,
                                 obj_name=obj_name,
                                 bucket_name=settings.S3_BUCKET_NAME)

        buffer = io.BytesIO()
        pickle.dump(image_volume, buffer)
        buffer.seek(0)

        background_task.add_task(s3_client.upload_file,
                                 file_obj=buffer.getvalue(),
                                 obj_name=obj_name + '.processed',
                                 bucket_name=settings.S3_BUCKET_NAME)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Obj is not saved')


class S3Client:

    def __init__(self):
        self.config = None
        self.session = None

    async def connect(
            self,
            access_key: str,
            secret_key: str,
            endpoint_url: str,
            region_name: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
            "region_name": region_name,
        }
        self.session = get_session()
        await self.ping()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(self, file_obj, obj_name: str, bucket_name: str):
        try:
            async with self.get_client() as client:
                await client.put_object(
                    Bucket=bucket_name,
                    Key=obj_name,
                    Body=file_obj)
        except Exception as e:
            print(e)

    async def ping(self):
        async with self.get_client() as client:
            try:
                await client.head_bucket(Bucket='non-existing-bucket')
            except ClientError as e:
                try:
                    if e.response['Error']['Code'] == '404':
                        print("✅ Подключение к S3 успешно!")
                except e:
                    raise e
            except Exception as e:
                print(f"❌ Ошибка подключения к S3: {e}, {type(e)}")

    async def download_file(self, obj_name: str, bucket_name: str) -> bytes:
        try:
            async with self.get_client() as client:
                response = await client.get_object(Bucket=bucket_name, Key=obj_name)
                return await response['Body'].read()
        except ClientError as e:
            return b""


s3_client = S3Client()
