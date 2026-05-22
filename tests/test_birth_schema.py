import pytest
from pydantic import ValidationError

from app.schemas.birth import BirthInfo, CalendarType, Gender


def _valid_birth_info(**overrides) -> dict:
    base = {
        "calendar_type": "solar",
        "birth_datetime": "1995-05-17T08:30:00+08:00",
        "gender": "female",
        "birth_place": "Shanghai, China",
        "timezone": "Asia/Shanghai",
    }
    base.update(overrides)
    return base


def test_valid_birth_info() -> None:
    info = BirthInfo(**_valid_birth_info())
    assert info.calendar_type == CalendarType.solar
    assert info.gender == Gender.female
    assert info.timezone == "Asia/Shanghai"


def test_valid_birth_info_all_genders() -> None:
    for gender in ("male", "female", "unknown"):
        info = BirthInfo(**_valid_birth_info(gender=gender))
        assert info.gender.value == gender


def test_missing_required_field() -> None:
    for field in ("calendar_type", "birth_datetime", "gender", "birth_place", "timezone"):
        data = _valid_birth_info()
        del data[field]
        with pytest.raises(ValidationError, match=field):
            BirthInfo(**data)


def test_invalid_calendar_type() -> None:
    with pytest.raises(ValidationError):
        BirthInfo(**_valid_birth_info(calendar_type="julian"))


def test_invalid_gender() -> None:
    with pytest.raises(ValidationError):
        BirthInfo(**_valid_birth_info(gender="other"))


def test_invalid_datetime() -> None:
    with pytest.raises(ValidationError):
        BirthInfo(**_valid_birth_info(birth_datetime="not-a-date"))


def test_birth_datetime_requires_timezone_offset() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        BirthInfo(**_valid_birth_info(birth_datetime="1995-05-17T08:30:00"))


def test_invalid_timezone() -> None:
    with pytest.raises(ValidationError, match="Invalid IANA timezone"):
        BirthInfo(**_valid_birth_info(timezone="Invalid/Zone"))


def test_empty_birth_place() -> None:
    with pytest.raises(ValidationError):
        BirthInfo(**_valid_birth_info(birth_place=""))


def test_longitude_must_be_in_valid_range() -> None:
    for longitude in (-180.1, 180.1):
        with pytest.raises(ValidationError):
            BirthInfo(**_valid_birth_info(longitude=longitude))


def test_lunar_calendar_not_accepted_yet() -> None:
    info = BirthInfo(**_valid_birth_info(calendar_type="lunar"))
    assert info.calendar_type == CalendarType.lunar
