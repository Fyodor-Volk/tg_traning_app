from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.user import UserRead
from app.schemas.workout import (
    CalendarDaySessions,
    SessionExerciseCreate,
    WorkoutSessionCreate,
    WorkoutSessionExerciseUpdate,
    WorkoutSessionUpdate,
    WorkoutSessionRead,
    SessionExerciseRead,
)
from app.services.workout_service import WorkoutService


router = APIRouter(tags=["sessions"])


@router.get("/calendar/{day}", response_model=CalendarDaySessions)
async def get_calendar_for_day(
    day: date,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CalendarDaySessions:
    service = WorkoutService(db)
    return await service.get_calendar_for_date(current_user.id, day)


@router.post("/sessions", response_model=WorkoutSessionRead)
async def create_session(
    payload: WorkoutSessionCreate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WorkoutSessionRead:
    service = WorkoutService(db)
    return await service.create_session(current_user.id, payload)


@router.put("/sessions/{session_id}", response_model=WorkoutSessionRead)
async def update_session(
    session_id: int,
    payload: WorkoutSessionUpdate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WorkoutSessionRead:
    service = WorkoutService(db)
    return await service.update_session(session_id, current_user.id, payload)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = WorkoutService(db)
    await service.delete_session(session_id, current_user.id)


@router.post(
    "/sessions/{session_id}/exercises",
    response_model=SessionExerciseRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_session_exercise(
    session_id: int,
    payload: SessionExerciseCreate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SessionExerciseRead:
    service = WorkoutService(db)
    exercise = await service.add_session_exercise(session_id, current_user.id, payload)
    return SessionExerciseRead.from_orm(exercise)


@router.put("/sessions/{session_id}/exercises/{exercise_id}", response_model=SessionExerciseRead)
async def update_session_exercise(
    session_id: int,
    exercise_id: int,
    payload: WorkoutSessionExerciseUpdate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SessionExerciseRead:
    service = WorkoutService(db)
    exercise = await service.update_session_exercise(
        session_id=session_id,
        exercise_id=exercise_id,
        user_id=current_user.id,
        payload=payload,
    )
    return SessionExerciseRead.from_orm(exercise)


@router.delete(
    "/sessions/{session_id}/exercises/{exercise_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_session_exercise(
    session_id: int,
    exercise_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = WorkoutService(db)
    await service.delete_session_exercise(
        session_id=session_id,
        exercise_id=exercise_id,
        user_id=current_user.id,
    )
