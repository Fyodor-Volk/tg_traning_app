from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.user import UserRead
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


class TelegramAuthRequest(BaseModel):
    init_data: str


@router.post("/telegram", response_model=UserRead)
async def auth_telegram(
    payload: TelegramAuthRequest,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    service = AuthService(db)
    user = await service.authenticate_telegram_user(payload.init_data)
    return user


@router.get("/me", response_model=UserRead)
async def auth_me(
    current_user: UserRead = Depends(get_current_user),
) -> UserRead:
    return current_user

