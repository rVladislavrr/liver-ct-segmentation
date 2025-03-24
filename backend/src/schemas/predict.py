from pydantic import BaseModel, Field


class Predict(BaseModel):
    uuid_file: str
    num_images: int = Field(..., ge=0)