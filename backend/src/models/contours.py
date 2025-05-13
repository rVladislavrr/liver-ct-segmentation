from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, func, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from src.models.base import Base


class Contours(Base):
    __tablename__ = 'contours'

    id: Mapped[int] = mapped_column(nullable=False, index=True, primary_key=True)

    author_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('users.uuid'), nullable=True, )
    num_images: Mapped[int] = mapped_column(nullable=False)
    file_uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('files.uuid'))
    contours: Mapped[JSONB] = mapped_column(JSONB, nullable=False, )
    version: Mapped[int] = mapped_column(nullable=False, default=0)
    url: Mapped[str] = mapped_column(nullable=False)

    file: Mapped['Files'] = relationship(back_populates='contours_file', lazy="select")
    author_counters: Mapped["Users"] = relationship(back_populates='contours', lazy="select")
