from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class CalendarType(str, Enum):
    solar = "solar"
    lunar = "lunar"


class Gender(str, Enum):
    male = "male"
    female = "female"
    unknown = "unknown"


class BirthInfo(BaseModel):
    calendar_type: CalendarType
    birth_datetime: datetime
    gender: Gender
    birth_place: str = Field(min_length=1, max_length=200)
    timezone: str = Field(min_length=1, max_length=100)
    longitude: float | None = None

    @field_validator("birth_datetime")
    @classmethod
    def validate_birth_datetime_timezone(cls, v: datetime) -> datetime:
        if v.tzinfo is None or v.utcoffset() is None:
            raise ValueError("birth_datetime must be timezone-aware")
        return v

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        try:
            from zoneinfo import ZoneInfo

            ZoneInfo(v)
        except Exception:
            raise ValueError(f"Invalid IANA timezone: {v}")
        return v
