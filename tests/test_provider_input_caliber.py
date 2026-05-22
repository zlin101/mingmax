from datetime import datetime, timedelta, timezone

from app.engines.providers.iztro_provider import _get_local_date_hour, build_chart_from_iztro
from app.schemas.birth import BirthInfo, Gender


def _birth(
    year: int = 2004,
    month: int = 3,
    day: int = 6,
    hour: int = 16,
    minute: int = 20,
    gender: Gender = Gender.female,
    longitude: float | None = None,
) -> BirthInfo:
    return BirthInfo(
        calendar_type="solar",
        birth_datetime=datetime(year, month, day, hour, minute, tzinfo=timezone(timedelta(hours=8))),
        gender=gender,
        birth_place="Test City",
        timezone="Asia/Shanghai",
        longitude=longitude,
    )


def test_provider_without_longitude_uses_inferred_true_solar_time() -> None:
    info = _birth(hour=16)
    date_str, hour = _get_local_date_hour(info)
    assert date_str == "2004-03-06"
    assert hour == 16


def test_provider_without_longitude_different_timezone() -> None:
    info = BirthInfo(
        calendar_type="solar",
        birth_datetime=datetime(2003, 6, 15, 12, 30, tzinfo=timezone(timedelta(hours=5))),
        gender=Gender.male,
        birth_place="Test",
        timezone="Asia/Karachi",
    )
    date_str, hour = _get_local_date_hour(info)
    assert hour == 12


def test_provider_with_longitude_uses_true_solar_hour() -> None:
    info = _birth(hour=16, minute=20, longitude=113.264)
    date_str, hour = _get_local_date_hour(info)
    assert date_str == "2004-03-06"
    assert hour == 15


def test_provider_builds_chart_without_longitude() -> None:
    info = _birth(hour=8, gender=Gender.female)
    chart = build_chart_from_iztro(info)
    assert chart.source == "iztro_py"
    assert len(chart.palaces) == 12


def test_provider_builds_chart_with_longitude() -> None:
    info = _birth(hour=16, minute=20, gender=Gender.female, longitude=113.264)
    chart = build_chart_from_iztro(info)
    assert chart.source == "iztro_py"
    assert len(chart.palaces) == 12


def test_provider_with_longitude_matches_expected_layout() -> None:
    info = _birth(hour=16, minute=20, gender=Gender.female, longitude=113.264)
    chart = build_chart_from_iztro(info)
    palace_5 = chart.palaces[5]
    assert palace_5.name == "命宫", f"Expected 命宫 at index 5, got {palace_5.name}"
    major_names = sorted(s.name for s in palace_5.stars if s.category == "major")
    assert "天府" in major_names


def test_provider_four_hua_with_longitude() -> None:
    info = _birth(hour=16, minute=20, gender=Gender.female, longitude=113.264)
    chart = build_chart_from_iztro(info)
    assert chart.four_hua is not None
    assert chart.four_hua.hua_lu == "廉贞"
    assert chart.four_hua.hua_quan == "破军"
    assert chart.four_hua.hua_ke == "武曲"
    assert chart.four_hua.hua_ji == "太阳"


def test_provider_body_palace_with_longitude() -> None:
    info = _birth(hour=16, minute=20, gender=Gender.female, longitude=113.264)
    chart = build_chart_from_iztro(info)
    body_palaces = [p for p in chart.palaces if p.is_body_palace]
    assert len(body_palaces) == 1
    assert body_palaces[0].name == "官禄宫"


def test_provider_male_female_mapping_stable() -> None:
    male_info = _birth(gender=Gender.male, longitude=113.264)
    female_info = _birth(gender=Gender.female, longitude=113.264)
    male_chart = build_chart_from_iztro(male_info)
    female_chart = build_chart_from_iztro(female_info)
    assert male_chart.chart_id != female_chart.chart_id
