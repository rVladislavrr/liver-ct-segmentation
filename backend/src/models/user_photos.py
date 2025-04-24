from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, func, ForeignKey, UniqueConstraint

from src.models.base import Base


class UserSavedPhoto(Base):
    __tablename__ = 'user_saved_photos'

    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.uuid'), nullable=False)
    photo_uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('photos.uuid'), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_uuid", "photo_uuid", name="uq_user_photo"),
    )

    user: Mapped['Users'] = relationship(
        back_populates='user_saved_photos', overlaps="saved_photos_direct,saved_by_users"
    )
    photo: Mapped['Photos'] = relationship(
        back_populates='user_saved_by', overlaps="saved_by_users,saved_photos_direct"
    )