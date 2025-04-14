from pydantic import BaseModel, EmailStr, Field, UUID4


class Token(BaseModel):
    token_type: str = 'Bearer'
    accessToken: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserInfo(BaseModel):
    uuid: UUID4
    is_active: bool
    is_verified: bool