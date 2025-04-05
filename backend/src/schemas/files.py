from pydantic import BaseModel, UUID4, Field


class File(BaseModel):
    uuid: UUID4
    filename: str = Field(..., min_length=1)
    size_bytes: int = Field(..., gt=0)
    num_slices: int = Field(..., gt=0)
    is_public: bool