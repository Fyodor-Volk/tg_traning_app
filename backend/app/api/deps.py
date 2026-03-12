from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRead
from app.telegram.auth import verify_init_data


async def get_current_user(
    x_telegram_init_data: str | None = Header(default=None, alias="X-Telegram-Init-Data"),
    x_dev_telegram_id: str | None = Header(default=None, alias="X-Dev-Telegram-Id"),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    settings = get_settings()

    telegram_id: int | None = None

    if x_telegram_init_data:
        verified = verify_init_data(x_telegram_init_data)
        telegram_user = verified["user"]
        telegram_id = int(telegram_user["id"])
    elif settings.debug:
        # Dev режим: разрешаем авторизацию без Telegram
        if x_dev_telegram_id:
            try:
                telegram_id = int(x_dev_telegram_id)
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid X-Dev-Telegram-Id",
                ) from exc
        else:
            telegram_id = 1
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Telegram auth",
        )

    repo = UserRepository(db)
    user = await repo.create_if_not_exists(telegram_id=telegram_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return UserRead.from_orm(user)

