from pydantic import BaseModel, EmailStr, Field, UUID4

from src.schemas.photos import PhotoWithFile, PhotoContourWithFile


class Token(BaseModel):
    token_type: str = 'Bearer'
    accessToken: str


class UserAuthenticate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserCreate(UserAuthenticate):
    name: str = Field(min_length=2, )


class UserInfo(BaseModel):
    uuid: UUID4
    is_active: bool
    is_verified: bool


class UserPhoto(UserInfo):
    name: str | None = Field(None,min_length=2, )
    email: EmailStr
    saved_photos_direct: list[PhotoWithFile]
    contours: list[PhotoContourWithFile]
