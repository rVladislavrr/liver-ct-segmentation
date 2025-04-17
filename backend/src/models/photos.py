from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, func, String, ForeignKey, UniqueConstraint

from src.models.base import Base


class Photos(Base):
    __tablename__ = 'photos'

    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), server_default=func.gen_random_uuid(),
                                       nullable=False, index=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    num_images: Mapped[int] = mapped_column(nullable=False)
    author_uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.uuid'))
    file_uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('files.uuid'))
    url: Mapped[str] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint("author_uuid", "file_uuid", "num_images", name="uq_photo"),
    )

    author: Mapped["Users"] = relationship(back_populates='author_photos', lazy="select")
    file: Mapped['Files'] = relationship(back_populates='saved_photos_file', lazy="select")

    user_saved_by: Mapped[list['UserSavedPhoto']] = relationship(
        back_populates='photo', lazy='select', overlaps="saved_by_users,saved_photos_direct"
    )

    saved_by_users: Mapped[list['Users']] = relationship(
        'Users',
        secondary='user_saved_photos',
        back_populates='saved_photos_direct',
        lazy='select',
        overlaps="user_saved_by,user_saved_photos"
    )