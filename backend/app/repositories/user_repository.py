from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_if_not_exists(self, telegram_id: int) -> User:
        user = await self.get_by_telegram_id(telegram_id)
        if user is not None:
            return user

        user = User(telegram_id=telegram_id)
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

