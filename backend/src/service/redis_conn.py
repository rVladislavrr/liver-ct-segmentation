import asyncio
import io
import json
import pickle

import redis.asyncio as redis
from fastapi import HTTPException, status

from src.config import settings
from src.logger import database_logger


class RedisClient:
    exp: int = settings.REDIS_EXP

    def __init__(self):
        self.redis = None

    async def connect(self):
        if self.redis is None:
            for attempt in range(3):
                try:
                    self.redis = await redis.from_url(settings.REDIS_BASE_URL, decode_responses=False)
                    await self.redis.ping()
                    print("✅ Successfully connected to Redis")
                    return
                except Exception as e:
                    print(f"⚠️ Redis connection failed (attempt {attempt + 1}/3): {e}")
                    await asyncio.sleep(2)

            print("❌ Could not connect to Redis after 3 attempts")
            raise RuntimeError("Redis connection failed")

    async def get_redis(self):
        if self.redis is None:
            print("🔄 Reconnecting to Redis...")
            await self.connect()

        if self.redis is None:
            raise ConnectionError("❌ Redis is unavailable")
        return self.redis

    async def close(self):
        if self.redis:
            await self.redis.close()


async def load_files_redis(uuid, image_volume, num_slices, author_id, is_public):
    try:
        redis = await redis_client.get_redis()
        pipe = redis.pipeline()

        pipe.setex(f'file:{uuid}',
                   redis_client.exp,
                   pickle.dumps(image_volume)
                   )

        pipe.setex(f'file_metadata:{uuid}',
                   redis_client.exp,
                   json.dumps({'num_slices': num_slices,
                               "author_id": author_id,
                               "is_public": is_public})
                   )
        await pipe.execute()
    except Exception as e:
        database_logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Obj is not cached')


async def load_result_cached(uuid, num_slices, data):
    try:
        redis = await redis_client.get_redis()
        await redis.setex(f'result:{uuid}:{num_slices}',
                          60 * 30,
                          pickle.dumps(data)
                          )
    except Exception as e:
        database_logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Obj is not cached')


async def get_result_cached(uuid, num_slices):
    try:
        redis = await redis_client.get_redis()
        data = await redis.get(f'result:{uuid}:{num_slices}')

        if data is not None:
            print('cache result')
            buffer = io.BytesIO(data)
            return pickle.load(buffer)
        else:
            print('miss result')
            return data

    except Exception as e:
        database_logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='redis dead')

async def get_metadata(uuid):
    try:
        redis = await redis_client.get_redis()
        metadata_file = await redis.get(f'file_metadata:{uuid}')

        if not metadata_file:
            return None
        return json.loads(metadata_file)
    except Exception as e:
        database_logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='redis dead')

async def get_files_redis(uuid):
    try:
        redis = await redis_client.get_redis()
        file = await redis.get(f'file:{uuid}')
        buffer = io.BytesIO(file)
        if buffer is None:
            print('miss file')
        return pickle.load(buffer)
    except Exception as e:
        database_logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='redis dead')

redis_client = RedisClient()
