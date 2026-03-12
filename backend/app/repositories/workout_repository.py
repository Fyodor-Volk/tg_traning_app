from datetime import date
from typing import Sequence

from sqlalchemy import Select, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workout import (
    BodyMetric,
    SessionExercise,
    SessionTemplateLink,
    TemplateExercise,
    WorkoutSession,
    WorkoutTemplate,
)


class WorkoutTemplateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_user(self, user_id: int) -> Sequence[WorkoutTemplate]:
        stmt: Select[WorkoutTemplate] = (
            select(WorkoutTemplate)
            .where(WorkoutTemplate.user_id == user_id)
            .order_by(WorkoutTemplate.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().unique().all()

    async def create(
        self,
        user_id: int,
        name: str,
    ) -> WorkoutTemplate:
        template = WorkoutTemplate(user_id=user_id, name=name)
        self._session.add(template)
        await self._session.flush()
        await self._session.refresh(template)
        return template

    async def get_by_id_for_user(self, template_id: int, user_id: int) -> WorkoutTemplate | None:
        stmt: Select[WorkoutTemplate] = select(WorkoutTemplate).where(
            WorkoutTemplate.id == template_id,
            WorkoutTemplate.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_exercise(
        self,
        template_id: int,
        exercise_name: str,
        sets_default: int,
        reps_default: int,
        weight_default: float | None,
    ) -> TemplateExercise:
        exercise = TemplateExercise(
            template_id=template_id,
            exercise_name=exercise_name,
            sets_default=sets_default,
            reps_default=reps_default,
            weight_default=weight_default,
        )
        self._session.add(exercise)
        await self._session.flush()
        await self._session.refresh(exercise)
        return exercise

    async def delete(self, template_id: int, user_id: int) -> None:
        stmt = delete(WorkoutTemplate).where(
            WorkoutTemplate.id == template_id,
            WorkoutTemplate.user_id == user_id,
        )
        await self._session.execute(stmt)

    async def clear_exercises(self, template_id: int) -> None:
        stmt = delete(TemplateExercise).where(TemplateExercise.template_id == template_id)
        await self._session.execute(stmt)


class WorkoutSessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_for_user_and_date(
        self,
        user_id: int,
        session_date: date,
    ) -> Sequence[WorkoutSession]:
        stmt: Select[WorkoutSession] = (
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.date == session_date,
            )
            .order_by(WorkoutSession.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().unique().all()

    async def get_by_id_for_user(self, session_id: int, user_id: int) -> WorkoutSession | None:
        stmt: Select[WorkoutSession] = select(WorkoutSession).where(
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_session(
        self,
        user_id: int,
        session_date: date,
        template_id: int | None,
        notes: str | None,
    ) -> WorkoutSession:
        session = WorkoutSession(
            user_id=user_id,
            date=session_date,
            template_id=template_id,
            notes=notes,
        )
        self._session.add(session)
        await self._session.flush()
        await self._session.refresh(session)
        return session

    async def add_exercise(
        self,
        session_id: int,
        exercise_name: str,
        sets: int,
        reps: int,
        weight: float | None,
        is_completed: bool,
    ) -> SessionExercise:
        exercise = SessionExercise(
            session_id=session_id,
            exercise_name=exercise_name,
            sets=sets,
            reps=reps,
            weight=weight,
            is_completed=is_completed,
        )
        self._session.add(exercise)
        await self._session.flush()
        await self._session.refresh(exercise)
        return exercise

    async def get_exercise_for_user(
        self,
        exercise_id: int,
        user_id: int,
        session_id: int | None = None,
    ) -> SessionExercise | None:
        stmt: Select[SessionExercise] = (
            select(SessionExercise)
            .join(WorkoutSession, WorkoutSession.id == SessionExercise.session_id)
            .where(
                SessionExercise.id == exercise_id,
                WorkoutSession.user_id == user_id,
            )
        )
        if session_id is not None:
            stmt = stmt.where(SessionExercise.session_id == session_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_session(self, session_id: int, user_id: int) -> None:
        stmt = delete(WorkoutSession).where(
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == user_id,
        )
        await self._session.execute(stmt)

    async def delete_exercise_for_user(
        self,
        exercise_id: int,
        user_id: int,
        session_id: int,
    ) -> bool:
        exercise = await self.get_exercise_for_user(
            exercise_id=exercise_id,
            user_id=user_id,
            session_id=session_id,
        )
        if exercise is None:
            return False

        await self._session.delete(exercise)
        await self._session.flush()
        return True

    async def add_template_link(self, session_id: int, template_id: int) -> None:
        self._session.add(SessionTemplateLink(session_id=session_id, template_id=template_id))
        await self._session.flush()

    async def clear_template_links(self, session_id: int) -> None:
        stmt = delete(SessionTemplateLink).where(SessionTemplateLink.session_id == session_id)
        await self._session.execute(stmt)


class BodyMetricsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        user_id: int,
        *,
        date_value: date,
        weight: float | None,
        height: float | None,
        chest: float | None,
        waist: float | None,
        hips: float | None,
        biceps: float | None,
        notes: str | None,
    ) -> BodyMetric:
        metric = BodyMetric(
            user_id=user_id,
            date=date_value,
            weight=weight,
            height=height,
            chest=chest,
            waist=waist,
            hips=hips,
            biceps=biceps,
            notes=notes,
        )
        self._session.add(metric)
        await self._session.flush()
        await self._session.refresh(metric)
        return metric

    async def history_for_user(self, user_id: int) -> Sequence[BodyMetric]:
        stmt: Select[BodyMetric] = (
            select(BodyMetric)
            .where(BodyMetric.user_id == user_id)
            .order_by(BodyMetric.date.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_for_user_by_date(self, user_id: int, date_value: date) -> BodyMetric | None:
        stmt: Select[BodyMetric] = select(BodyMetric).where(
            BodyMetric.user_id == user_id,
            BodyMetric.date == date_value,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_for_user(self, metric_id: int, user_id: int) -> BodyMetric | None:
        stmt: Select[BodyMetric] = select(BodyMetric).where(
            BodyMetric.id == metric_id,
            BodyMetric.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, metric_id: int, user_id: int) -> None:
        stmt = delete(BodyMetric).where(
            BodyMetric.id == metric_id,
            BodyMetric.user_id == user_id,
        )
        await self._session.execute(stmt)
