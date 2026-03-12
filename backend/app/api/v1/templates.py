from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.user import UserRead
from app.schemas.workout import (
    TemplateExerciseCreate,
    WorkoutTemplateCreate,
    WorkoutTemplateRead,
    WorkoutTemplateUpdate,
)
from app.services.workout_service import WorkoutService


router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=list[WorkoutTemplateRead])
async def list_templates(
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[WorkoutTemplateRead]:
    service = WorkoutService(db)
    return list(await service.list_templates(current_user.id))


@router.post("", response_model=WorkoutTemplateRead, status_code=status.HTTP_201_CREATED)
async def create_template(
    payload: WorkoutTemplateCreate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WorkoutTemplateRead:
    service = WorkoutService(db)
    return await service.create_template(current_user.id, payload)


@router.put("/{template_id}", response_model=WorkoutTemplateRead)
async def update_template(
    template_id: int,
    payload: WorkoutTemplateUpdate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WorkoutTemplateRead:
    service = WorkoutService(db)
    return await service.update_template(template_id, current_user.id, payload)


@router.post("/{template_id}/exercises", status_code=status.HTTP_201_CREATED)
async def add_template_exercise(
    template_id: int,
    payload: TemplateExerciseCreate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = WorkoutService(db)
    exercise = await service.add_template_exercise(template_id, current_user.id, payload)
    return {"id": exercise.id}


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = WorkoutService(db)
    await service.delete_template(template_id, current_user.id)
