from datetime import date
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workout import BodyMetric, SessionExercise, TemplateExercise, WorkoutSession, WorkoutTemplate
from app.repositories.workout_repository import (
    BodyMetricsRepository,
    WorkoutSessionRepository,
    WorkoutTemplateRepository,
)
from app.schemas.metrics import BodyMetricCreate, BodyMetricRead, BodyMetricUpdate
from app.schemas.workout import (
    CalendarDaySessions,
    SessionExerciseCreate,
    TemplateExerciseCreate,
    WorkoutSessionCreate,
    WorkoutSessionUpdate,
    WorkoutSessionRead,
    WorkoutTemplateCreate,
    WorkoutTemplateUpdate,
    WorkoutTemplateRead,
    WorkoutSessionExerciseUpdate,
)


class WorkoutService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._templates = WorkoutTemplateRepository(db)
        self._sessions = WorkoutSessionRepository(db)
        self._metrics = BodyMetricsRepository(db)

    async def list_templates(self, user_id: int) -> Sequence[WorkoutTemplateRead]:
        templates = await self._templates.list_for_user(user_id)
        return [WorkoutTemplateRead.from_orm(t) for t in templates]

    def _session_to_read(self, session: WorkoutSession) -> WorkoutSessionRead:
        template_ids = [link.template_id for link in session.template_links]
        return WorkoutSessionRead(
            id=session.id,
            user_id=session.user_id,
            date=session.date,
            template_id=session.template_id,
            template_ids=template_ids,
            notes=session.notes,
            created_at=session.created_at,
            exercises=[exercise for exercise in session.exercises],
        )

    async def _get_template_or_404(self, template_id: int, user_id: int) -> WorkoutTemplate:
        template = await self._templates.get_by_id_for_user(template_id, user_id)
        if template is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found",
            )
        return template

    async def _get_session_or_404(self, session_id: int, user_id: int) -> WorkoutSession:
        session = await self._sessions.get_by_id_for_user(session_id, user_id)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
        return session

    async def _get_metric_or_404(self, metric_id: int, user_id: int) -> BodyMetric:
        metric = await self._metrics.get_by_id_for_user(metric_id, user_id)
        if metric is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Metric not found",
            )
        return metric

    async def _sync_template_links_and_exercises(
        self,
        user_id: int,
        session: WorkoutSession,
        template_ids: list[int],
        copy_exercises: bool,
    ) -> None:
        deduped_ids = list(dict.fromkeys(template_ids))
        templates: list[WorkoutTemplate] = []
        for template_id in deduped_ids:
            templates.append(await self._get_template_or_404(template_id, user_id))

        await self._sessions.clear_template_links(session.id)
        for template in templates:
            await self._sessions.add_template_link(session.id, template.id)

        if copy_exercises:
            for template in templates:
                for exercise in template.exercises:
                    await self._sessions.add_exercise(
                        session_id=session.id,
                        exercise_name=exercise.exercise_name,
                        sets=exercise.sets_default,
                        reps=exercise.reps_default,
                        weight=exercise.weight_default,
                        is_completed=False,
                    )

    async def create_template(
        self,
        user_id: int,
        payload: WorkoutTemplateCreate,
    ) -> WorkoutTemplateRead:
        template = await self._templates.create(user_id=user_id, name=payload.name)

        for exercise in payload.exercises:
            await self._templates.add_exercise(
                template_id=template.id,
                exercise_name=exercise.exercise_name,
                sets_default=exercise.sets_default,
                reps_default=exercise.reps_default,
                weight_default=exercise.weight_default,
            )

        await self._db.commit()
        await self._db.refresh(template)
        return WorkoutTemplateRead.from_orm(template)

    async def update_template(
        self,
        template_id: int,
        user_id: int,
        payload: WorkoutTemplateUpdate,
    ) -> WorkoutTemplateRead:
        template = await self._get_template_or_404(template_id, user_id)
        template.name = payload.name
        await self._templates.clear_exercises(template.id)

        for exercise in payload.exercises:
            await self._templates.add_exercise(
                template_id=template.id,
                exercise_name=exercise.exercise_name,
                sets_default=exercise.sets_default,
                reps_default=exercise.reps_default,
                weight_default=exercise.weight_default,
            )

        await self._db.commit()
        await self._db.refresh(template)
        return WorkoutTemplateRead.from_orm(template)

    async def add_template_exercise(
        self,
        template_id: int,
        user_id: int,
        payload: TemplateExerciseCreate,
    ) -> TemplateExercise:
        await self._get_template_or_404(template_id, user_id)
        exercise = await self._templates.add_exercise(
            template_id=template_id,
            exercise_name=payload.exercise_name,
            sets_default=payload.sets_default,
            reps_default=payload.reps_default,
            weight_default=payload.weight_default,
        )
        await self._db.commit()
        return exercise

    async def delete_template(self, template_id: int, user_id: int) -> None:
        await self._get_template_or_404(template_id, user_id)
        await self._templates.delete(template_id=template_id, user_id=user_id)
        await self._db.commit()

    async def get_calendar_for_date(
        self,
        user_id: int,
        day: date,
    ) -> CalendarDaySessions:
        sessions = await self._sessions.get_for_user_and_date(user_id=user_id, session_date=day)
        return CalendarDaySessions(
            date=day,
            sessions=[self._session_to_read(s) for s in sessions],
        )

    async def create_session(
        self,
        user_id: int,
        payload: WorkoutSessionCreate,
    ) -> WorkoutSessionRead:
        template_ids = list(payload.template_ids)
        if payload.template_id is not None and payload.template_id not in template_ids:
            template_ids.insert(0, payload.template_id)

        session = await self._sessions.create_session(
            user_id=user_id,
            session_date=payload.date,
            template_id=payload.template_id,
            notes=payload.notes,
        )
        if template_ids:
            await self._sync_template_links_and_exercises(
                user_id=user_id,
                session=session,
                template_ids=template_ids,
                copy_exercises=True,
            )

        # Add custom exercises, if any
        for ex in payload.exercises:
            await self._sessions.add_exercise(
                session_id=session.id,
                exercise_name=ex.exercise_name,
                sets=ex.sets,
                reps=ex.reps,
                weight=ex.weight,
                is_completed=ex.is_completed,
            )

        await self._db.commit()
        await self._db.refresh(session)
        return self._session_to_read(session)

    async def update_session(
        self,
        session_id: int,
        user_id: int,
        payload: WorkoutSessionUpdate,
    ) -> WorkoutSessionRead:
        session = await self._get_session_or_404(session_id, user_id)
        if "date" in payload.model_fields_set:
            session.date = payload.date
        if "notes" in payload.model_fields_set:
            session.notes = payload.notes
        if "template_ids" in payload.model_fields_set and payload.template_ids is not None:
            await self._sync_template_links_and_exercises(
                user_id=user_id,
                session=session,
                template_ids=payload.template_ids,
                copy_exercises=False,
            )

        await self._db.commit()
        await self._db.refresh(session)
        return self._session_to_read(session)

    async def delete_session(self, session_id: int, user_id: int) -> None:
        await self._get_session_or_404(session_id, user_id)
        await self._sessions.delete_session(session_id=session_id, user_id=user_id)
        await self._db.commit()

    async def update_session_exercise(
        self,
        session_id: int,
        exercise_id: int,
        user_id: int,
        payload: WorkoutSessionExerciseUpdate,
    ) -> SessionExercise:
        await self._get_session_or_404(session_id, user_id)
        exercise = await self._sessions.get_exercise_for_user(
            exercise_id=exercise_id,
            user_id=user_id,
            session_id=session_id,
        )
        if exercise is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session exercise not found",
            )

        if "exercise_name" in payload.model_fields_set and payload.exercise_name is not None:
            exercise.exercise_name = payload.exercise_name
        if "sets" in payload.model_fields_set and payload.sets is not None:
            exercise.sets = payload.sets
        if "reps" in payload.model_fields_set and payload.reps is not None:
            exercise.reps = payload.reps
        if "weight" in payload.model_fields_set:
            exercise.weight = payload.weight
        if "is_completed" in payload.model_fields_set and payload.is_completed is not None:
            exercise.is_completed = payload.is_completed

        await self._db.commit()
        await self._db.refresh(exercise)
        return exercise

    async def add_session_exercise(
        self,
        session_id: int,
        user_id: int,
        payload: SessionExerciseCreate,
    ) -> SessionExercise:
        await self._get_session_or_404(session_id, user_id)
        exercise = await self._sessions.add_exercise(
            session_id=session_id,
            exercise_name=payload.exercise_name,
            sets=payload.sets,
            reps=payload.reps,
            weight=payload.weight,
            is_completed=payload.is_completed,
        )
        await self._db.commit()
        await self._db.refresh(exercise)
        return exercise

    async def delete_session_exercise(
        self,
        session_id: int,
        exercise_id: int,
        user_id: int,
    ) -> None:
        await self._get_session_or_404(session_id, user_id)
        deleted = await self._sessions.delete_exercise_for_user(
            exercise_id=exercise_id,
            user_id=user_id,
            session_id=session_id,
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session exercise not found",
            )
        await self._db.commit()

    async def create_body_metric(
        self,
        user_id: int,
        payload: BodyMetricCreate,
    ) -> BodyMetricRead:
        metric = await self._metrics.create(
            user_id=user_id,
            date_value=payload.date,
            weight=payload.weight,
            height=payload.height,
            chest=payload.chest,
            waist=payload.waist,
            hips=payload.hips,
            biceps=payload.biceps,
            notes=payload.notes,
        )
        await self._db.commit()
        return BodyMetricRead.from_orm(metric)

    async def get_metric_by_date(self, user_id: int, metric_date: date) -> BodyMetricRead:
        metric = await self._metrics.get_for_user_by_date(user_id=user_id, date_value=metric_date)
        if metric is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Metric not found for date",
            )
        return BodyMetricRead.from_orm(metric)

    async def get_metrics_history(self, user_id: int) -> list[BodyMetricRead]:
        history = await self._metrics.history_for_user(user_id=user_id)
        return [BodyMetricRead.from_orm(m) for m in history]

    async def update_body_metric(
        self,
        metric_id: int,
        user_id: int,
        payload: BodyMetricUpdate,
    ) -> BodyMetricRead:
        metric = await self._get_metric_or_404(metric_id, user_id)
        if "date" in payload.model_fields_set:
            metric.date = payload.date
        if "weight" in payload.model_fields_set:
            metric.weight = payload.weight
        if "height" in payload.model_fields_set:
            metric.height = payload.height
        if "chest" in payload.model_fields_set:
            metric.chest = payload.chest
        if "waist" in payload.model_fields_set:
            metric.waist = payload.waist
        if "hips" in payload.model_fields_set:
            metric.hips = payload.hips
        if "biceps" in payload.model_fields_set:
            metric.biceps = payload.biceps
        if "notes" in payload.model_fields_set:
            metric.notes = payload.notes

        await self._db.commit()
        await self._db.refresh(metric)
        return BodyMetricRead.from_orm(metric)

    async def delete_body_metric(self, metric_id: int, user_id: int) -> None:
        await self._get_metric_or_404(metric_id, user_id)
        await self._metrics.delete(metric_id=metric_id, user_id=user_id)
        await self._db.commit()
