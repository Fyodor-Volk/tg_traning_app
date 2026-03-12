from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.metrics import BodyMetricCreate, BodyMetricRead, BodyMetricUpdate
from app.schemas.user import UserRead
from app.services.workout_service import WorkoutService


router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.post("", response_model=BodyMetricRead)
async def create_metric(
    payload: BodyMetricCreate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BodyMetricRead:
    service = WorkoutService(db)
    return await service.create_body_metric(current_user.id, payload)


@router.get("/history", response_model=list[BodyMetricRead])
async def get_metrics_history(
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[BodyMetricRead]:
    service = WorkoutService(db)
    return await service.get_metrics_history(current_user.id)


@router.get("/{day}", response_model=BodyMetricRead)
async def get_metric_for_day(
    day: date,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BodyMetricRead:
    service = WorkoutService(db)
    return await service.get_metric_by_date(current_user.id, day)


@router.put("/{metric_id}", response_model=BodyMetricRead)
async def update_metric(
    metric_id: int,
    payload: BodyMetricUpdate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BodyMetricRead:
    service = WorkoutService(db)
    return await service.update_body_metric(metric_id, current_user.id, payload)


@router.delete("/{metric_id}", status_code=204)
async def delete_metric(
    metric_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = WorkoutService(db)
    await service.delete_body_metric(metric_id, current_user.id)
