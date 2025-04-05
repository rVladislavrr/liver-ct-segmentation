from pydantic import BaseModel, Field, UUID4


class Predict(BaseModel):
    uuid_file: UUID4
    num_images: int = Field(..., ge=0)