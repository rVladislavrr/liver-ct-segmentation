from src.service.redis_conn import get_result_cached, get_files_redis

async def create_save_photo(obj, request_id):
    result_photo = await get_result_cached(obj.file_uuid, obj.num_images)
    if result_photo is not None:
        return result_photo, True
    return await get_files_redis(obj.file_uuid), False


