from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID, func, String, BIGINT

from src.models.base import Base


class Files(Base):
    __tablename__ = 'files'

    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), server_default=func.gen_random_uuid(),
                                       nullable=False, index=True, primary_key=True)

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    s3_url: Mapped[str] = mapped_column(nullable=True)
    size_bytes: Mapped[int] = mapped_column(BIGINT, nullable=False)
    num_slices: Mapped[int] = mapped_column(nullable=False)
    s3_url_processed: Mapped[str] = mapped_column(nullable=True)

