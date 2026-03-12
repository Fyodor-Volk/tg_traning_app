from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRead
from app.telegram.auth import verify_init_data


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._users = UserRepository(db)

    async def authenticate_telegram_user(self, init_data: str) -> UserRead:
        verified = verify_init_data(init_data)
        telegram_user = verified["user"]
        telegram_id = int(telegram_user["id"])

        user = await self._users.create_if_not_exists(telegram_id=telegram_id)
        return UserRead.from_orm(user)

