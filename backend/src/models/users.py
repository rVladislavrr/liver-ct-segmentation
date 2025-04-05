from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, func

from src.models.base import Base

class Users(Base):
    __tablename__ = 'users'

    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
                                       server_default=func.gen_random_uuid())
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hash_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)

    files: Mapped[list["Files"]] = relationship( back_populates='author', lazy="select")
