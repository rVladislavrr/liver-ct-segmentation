from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from src.config import settings
from src.service.redis_conn import redis_client
from src.service.s3 import s3_client
from src.service.model import modelManager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await s3_client.connect(
        access_key=settings.S3_ACCESS_KEY,
        secret_key=settings.S3_SECRET_KEY,
        endpoint_url=settings.S3_ENDPOINPUT,
        region_name=settings.S3_REGION,
    )
    await redis_client.connect()
    modelManager.upload_model()
    yield
    await redis_client.close()


def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
    )
    return app
