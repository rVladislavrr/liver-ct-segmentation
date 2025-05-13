
from contextlib import asynccontextmanager
from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from fastapi import HTTPException, status

from src.config import settings
from src.logger import s3_logger



class S3Client:
    def __init__(self):
        self._config = None
        self._session = None

    async def connect(
            self,
            access_key: str,
            secret_key: str,
            endpoint_url: str,
            region_name: str,
    ) -> None:
        self._config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
            "region_name": region_name,
        }
        self._session = get_session()
        await self._test_connection()

    @asynccontextmanager
    async def _get_client(self):
        async with self._session.create_client("s3", **self._config) as client:
            yield client

    async def upload_file(
            self,
            file_obj,
            obj_name,
            bucket_name,
            request_id,
    ) -> None:
        try:
            async with self._get_client() as client:
                await client.put_object(
                    Bucket=bucket_name,
                    Key=obj_name,
                    Body=file_obj
                )
            s3_logger.info(
                "File uploaded to S3 successfully",
                extra={
                    "object_name": obj_name,
                    "bucket": bucket_name,
                    "file_size": len(file_obj) if hasattr(file_obj, '__len__') else None,
                    "request_id": request_id,
                }
            )
        except Exception as e:
            s3_logger.error(
                "Failed to upload file to S3",
                exc_info=e,
                extra={
                    "object_name": obj_name,
                    "bucket": bucket_name,
                    "error": str(e),
                    "request_id": request_id,
                }
            )
            raise

    async def _test_connection(self) -> None:
        try:
            async with self._get_client() as client:
                for bucket in [settings.S3_PRIVATE_BUCKET_NAME, settings.S3_BUCKET_NAME]:
                    await client.head_bucket(Bucket=bucket)
            # s3_logger.info("S3 connection established successfully")
        except Exception as e:
            s3_logger.critical(
                "Failed to connect to S3",
                exc_info=e,
                extra={"error": str(e)}
            )
            raise

    async def download_file(
            self,
            obj_name,
            bucket_name,
            request_id,
    ) -> bytes:
        try:
            async with self._get_client() as client:
                response = await client.get_object(
                    Bucket=bucket_name,
                    Key=obj_name
                )
                data = await response['Body'].read()
                s3_logger.info(
                    "File downloaded from S3",
                    extra={
                        "object_name": obj_name,
                        "bucket": bucket_name,
                        "file_size": len(data),
                        "request_id": request_id,
                    }
                )
                return data
        except ClientError as e:
            s3_logger.warning(
                "File not found in S3",
                extra={
                    "object_name": obj_name,
                    "bucket": bucket_name,
                    "error": str(e),
                    "request_id": request_id,
                }
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"msg": "Not found in S3", })
        except Exception as e:
            s3_logger.error(
                "Failed to download file from S3",
                exc_info=e,
                extra={
                    "object_name": obj_name,
                    "bucket": bucket_name,
                    "error": str(e),
                    "request_id": request_id,
                }
            )
            raise

    async def delete_file(
            self,
            obj_name,
            bucket_name,
            request_id,
    ) -> None:
        print("1.2.0")
        try:
            print("1.2.0.1")
            async with self._get_client() as client:
                print('1.2.1')
                await client.delete_object(
                    Bucket=bucket_name,
                    Key=obj_name
                )
                print('1.2.2')
                s3_logger.info(
                    "File deleted from S3",
                    extra={
                        "object_name": obj_name,
                        "bucket": bucket_name,
                        "request_id": request_id,
                    }
                )
        except ClientError as e:
            s3_logger.warning(
                "Failed to delete file from S3",
                extra={
                    "object_name": obj_name,
                    "bucket": bucket_name,
                    "error": str(e),
                    "request_id": request_id,
                }
            )
        except Exception as e:
            s3_logger.error(
                "Unexpected error while deleting file from S3",
                exc_info=e,
                extra={
                    "object_name": obj_name,
                    "bucket": bucket_name,
                    "error": str(e),
                    "request_id": request_id,
                }
            )


s3_client = S3Client()

