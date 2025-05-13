from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, func, String, BIGINT, ForeignKey

from src.models.base import Base


class Files(Base):
    __tablename__ = 'files'

    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), server_default=func.gen_random_uuid(),
                                       nullable=False, index=True, primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BIGINT, nullable=False)
    num_slices: Mapped[int] = mapped_column(nullable=False)
    author_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('users.uuid'), nullable=True,
                                                   default=None)
    is_public: Mapped[bool] = mapped_column(nullable=False, default=False)

    author: Mapped["Users"] = relationship(back_populates='files', lazy="select")
    saved_photos_file: Mapped[list['Photos']] = relationship(back_populates='file', lazy="select")
    contours_file: Mapped[list['Contours']] = relationship(back_populates='file', lazy="select")
