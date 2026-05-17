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

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        try:
            from zoneinfo import ZoneInfo

            ZoneInfo(v)
        except Exception:
            raise ValueError(f"Invalid IANA timezone: {v}")
        return v
