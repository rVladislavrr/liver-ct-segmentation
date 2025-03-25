from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


class BaseManager:
    model: Any

    async def create(self, session: AsyncSession, data: dict) -> Any:
        try:
            instance = self.model(**data)
            session.add(instance)
            await session.flush()
            await session.refresh(instance)
        except Exception as e:
            raise e
        await session.commit()
        return instance
