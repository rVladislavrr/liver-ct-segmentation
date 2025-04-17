from datetime import datetime

from pydantic import BaseModel, UUID4, Field

from src.schemas.files import File


class PhotoCreate(BaseModel):
    uuid_file: UUID4
    num_images: int = Field(..., ge=0)

class PhotoSave(BaseModel):
    uuid: UUID4
    name: str
    file_uuid: UUID4
    author_uuid: UUID4
    num_images: int = Field(..., ge=0)
    url: str
    create_at: datetime

class PhotoWithFile(PhotoSave):
    file: File