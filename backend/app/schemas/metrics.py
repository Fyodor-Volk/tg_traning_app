from datetime import date as DateType

from pydantic import BaseModel, Field


class BodyMetricCreate(BaseModel):
    date: DateType
    weight: float | None = Field(default=None, ge=0)
    height: float | None = Field(default=None, ge=0)
    chest: float | None = Field(default=None, ge=0)
    waist: float | None = Field(default=None, ge=0)
    hips: float | None = Field(default=None, ge=0)
    biceps: float | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=2000)


class BodyMetricUpdate(BaseModel):
    date: DateType | None = None
    weight: float | None = Field(default=None, ge=0)
    height: float | None = Field(default=None, ge=0)
    chest: float | None = Field(default=None, ge=0)
    waist: float | None = Field(default=None, ge=0)
    hips: float | None = Field(default=None, ge=0)
    biceps: float | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=2000)


class BodyMetricRead(BodyMetricCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True
