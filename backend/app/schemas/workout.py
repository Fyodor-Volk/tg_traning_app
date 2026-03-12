from datetime import date as DateType
from datetime import datetime
from typing import Sequence

from pydantic import BaseModel, Field


class TemplateExerciseCreate(BaseModel):
    exercise_name: str = Field(..., max_length=255)
    sets_default: int = Field(..., ge=1, le=50)
    reps_default: int = Field(..., ge=1, le=200)
    weight_default: float | None = Field(default=None, ge=0)


class TemplateExerciseRead(TemplateExerciseCreate):
    id: int

    class Config:
        from_attributes = True


class WorkoutTemplateCreate(BaseModel):
    name: str = Field(..., max_length=255)
    exercises: list[TemplateExerciseCreate] = Field(default_factory=list)


class WorkoutTemplateUpdate(BaseModel):
    name: str = Field(..., max_length=255)
    exercises: list[TemplateExerciseCreate] = Field(default_factory=list)


class WorkoutTemplateRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    exercises: Sequence[TemplateExerciseRead]

    class Config:
        from_attributes = True


class WorkoutSessionExerciseUpdate(BaseModel):
    exercise_name: str | None = Field(default=None, max_length=255)
    sets: int | None = Field(default=None, ge=1, le=50)
    reps: int | None = Field(default=None, ge=1, le=200)
    weight: float | None = Field(default=None, ge=0)
    is_completed: bool | None = None


class SessionExerciseCreate(BaseModel):
    exercise_name: str = Field(..., max_length=255)
    sets: int = Field(..., ge=1, le=50)
    reps: int = Field(..., ge=1, le=200)
    weight: float | None = Field(default=None, ge=0)
    is_completed: bool = False


class SessionExerciseRead(SessionExerciseCreate):
    id: int

    class Config:
        from_attributes = True


class WorkoutSessionCreate(BaseModel):
    date: DateType
    template_id: int | None = None
    template_ids: list[int] = Field(default_factory=list)
    notes: str | None = Field(default=None, max_length=2000)
    exercises: list[SessionExerciseCreate] = Field(default_factory=list)


class WorkoutSessionUpdate(BaseModel):
    date: DateType | None = None
    notes: str | None = Field(default=None, max_length=2000)
    template_ids: list[int] | None = None


class WorkoutSessionRead(BaseModel):
    id: int
    user_id: int
    date: DateType
    template_id: int | None
    template_ids: list[int] = Field(default_factory=list)
    notes: str | None
    created_at: datetime
    exercises: Sequence[SessionExerciseRead]

    class Config:
        from_attributes = True


class CalendarDaySessions(BaseModel):
    date: DateType
    sessions: list[WorkoutSessionRead]
