from datetime import datetime, timedelta, timezone

from app.engines.providers.iztro_provider import _get_local_date_hour, build_chart_from_iztro
from app.schemas.birth import BirthInfo, Gender


def _birth(
    year: int = 1998,
    month: int = 10,
    day: int = 23,
    hour: int = 11,
    minute: int = 45,
    gender: Gender = Gender.male,
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


def test_provider_without_longitude_uses_clock_hour() -> None:
    info = _birth(hour=11)
    date_str, hour = _get_local_date_hour(info)
    assert hour == 11


def test_provider_with_longitude_uses_true_solar_hour() -> None:
    info = _birth(hour=11, minute=45, longitude=104.067)
    date_str, hour = _get_local_date_hour(info)
    assert hour == 10, "True solar time for 104.067E at 11:45 should shift to ~10:56 (巳时)"


def test_provider_builds_chart_without_longitude() -> None:
    info = _birth(hour=8, gender=Gender.female)
    chart = build_chart_from_iztro(info)
    assert chart.source == "iztro_py"
    assert len(chart.palaces) == 12


def test_provider_builds_chart_with_longitude() -> None:
    info = _birth(hour=11, minute=45, gender=Gender.male, longitude=104.067)
    chart = build_chart_from_iztro(info)
    assert chart.source == "iztro_py"
    assert len(chart.palaces) == 12


def test_provider_with_longitude_matches_expected_layout() -> None:
    info = _birth(hour=11, minute=45, gender=Gender.male, longitude=104.067)
    chart = build_chart_from_iztro(info)
    palace_3 = chart.palaces[3]
    assert palace_3.name == "命宫", f"Expected 命宫 at index 3, got {palace_3.name}"
    major_names = sorted(s.name for s in palace_3.stars if s.category == "major")
    assert "廉贞" in major_names
    assert "贪狼" in major_names


def test_provider_four_hua_with_longitude() -> None:
    info = _birth(hour=11, minute=45, gender=Gender.male, longitude=104.067)
    chart = build_chart_from_iztro(info)
    assert chart.four_hua is not None
    assert chart.four_hua.hua_lu == "贪狼"
    assert chart.four_hua.hua_quan == "太阴"
    assert chart.four_hua.hua_ji == "天机"


def test_provider_body_palace_with_longitude() -> None:
    info = _birth(hour=11, minute=45, gender=Gender.male, longitude=104.067)
    chart = build_chart_from_iztro(info)
    body_palaces = [p for p in chart.palaces if p.is_body_palace]
    assert len(body_palaces) == 1
    assert body_palaces[0].name == "夫妻宫"


def test_provider_male_female_mapping_stable() -> None:
    male_info = _birth(gender=Gender.male, longitude=104.067)
    female_info = _birth(gender=Gender.female, longitude=104.067)
    male_chart = build_chart_from_iztro(male_info)
    female_chart = build_chart_from_iztro(female_info)
    assert male_chart.chart_id != female_chart.chart_id
