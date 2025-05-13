from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, func, Text

from src.models.base import Base


class Users(Base):
    __tablename__ = 'users'

    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
                                       server_default=func.gen_random_uuid())
    name: Mapped[str] = mapped_column(Text, nullable=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hash_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)

    files: Mapped[list["Files"]] = relationship(back_populates='author', lazy="select")
    author_photos: Mapped[list['Photos']] = relationship(back_populates='author', lazy="select")
    contours: Mapped[list['Contours']] = relationship(back_populates='author_counters', lazy="select")
    user_saved_photos: Mapped[list['UserSavedPhoto']] = relationship(
        back_populates='user', lazy='select', overlaps="saved_photos_direct,saved_by_users"
    )
    saved_photos_direct: Mapped[list['Photos']] = relationship(
        'Photos',
        secondary='user_saved_photos',
        back_populates='saved_by_users',
        lazy='select',
        overlaps="user_saved_photos,user_saved_by"
    )
