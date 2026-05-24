from datetime import datetime, timedelta, timezone

import pytest

from app.engines.chart_normalizer import ChartNormalizer
from app.engines.ziwei_chart_engine import UnsupportedCalendarTypeError, UnsupportedGenderError, ZiweiChartEngine
from app.schemas.birth import BirthInfo, Gender


def _birth_info(
    year: int = 1995,
    month: int = 5,
    day: int = 17,
    hour: int = 8,
    gender: Gender = Gender.female,
) -> BirthInfo:
    return BirthInfo(
        calendar_type="solar",
        birth_datetime=datetime(year, month, day, hour, 30, tzinfo=timezone(timedelta(hours=8))),
        gender=gender,
        birth_place="Shanghai, China",
        timezone="Asia/Shanghai",
    )


def _birth_info_sample_2() -> BirthInfo:
    return BirthInfo(
        calendar_type="solar",
        birth_datetime=datetime(1988, 11, 23, 14, 0, tzinfo=timezone(timedelta(hours=8))),
        gender="male",
        birth_place="Beijing, China",
        timezone="Asia/Shanghai",
    )


def _birth_info_sample_3() -> BirthInfo:
    return BirthInfo(
        calendar_type="solar",
        birth_datetime=datetime(2000, 1, 15, 0, 0, tzinfo=timezone(timedelta(hours=8))),
        gender="female",
        birth_place="Guangzhou, China",
        timezone="Asia/Shanghai",
    )


def test_engine_returns_iztro_source() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info())
    assert chart.source == "iztro_py"
    assert chart.source != "stub"


def test_engine_returns_12_palaces() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info())
    assert len(chart.palaces) == 12


def test_engine_palaces_have_chinese_names() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info())
    for palace in chart.palaces:
        assert palace.name
        assert "宫" in palace.name


def test_engine_palaces_have_earthly_branches() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info())
    branches = [p.earthly_branch for p in chart.palaces]
    assert all(b is not None for b in branches)


def test_engine_chart_id_format() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info())
    assert chart.chart_id.startswith("iztro_py-")


def test_engine_chart_id_is_deterministic() -> None:
    engine = ZiweiChartEngine()
    birth = _birth_info()

    chart1 = engine.build_chart(birth)
    chart2 = engine.build_chart(birth)

    assert chart1.chart_id == chart2.chart_id


def test_engine_stars_non_empty() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info())
    total_stars = sum(len(p.stars) for p in chart.palaces)
    assert total_stars > 0, "Real chart should have stars"


def test_engine_sample_2_stable() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info_sample_2())
    assert chart.source == "iztro_py"
    assert len(chart.palaces) == 12


def test_engine_sample_3_stable() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info_sample_3())
    assert chart.source == "iztro_py"
    assert len(chart.palaces) == 12


def test_engine_rejects_unsupported_lunar_calendar() -> None:
    engine = ZiweiChartEngine()
    birth = BirthInfo(
        calendar_type="lunar",
        birth_datetime=datetime(1995, 5, 17, 8, 30, tzinfo=timezone(timedelta(hours=8))),
        gender="female",
        birth_place="Shanghai, China",
        timezone="Asia/Shanghai",
    )

    with pytest.raises(UnsupportedCalendarTypeError, match="Unsupported calendar type: lunar"):
        engine.build_chart(birth)


def test_engine_rejects_unknown_gender() -> None:
    engine = ZiweiChartEngine()
    birth = BirthInfo(
        calendar_type="solar",
        birth_datetime=datetime(1995, 5, 17, 8, 30, tzinfo=timezone(timedelta(hours=8))),
        gender="unknown",
        birth_place="Shanghai, China",
        timezone="Asia/Shanghai",
    )

    with pytest.raises(UnsupportedGenderError, match="not supported"):
        engine.build_chart(birth)


def test_engine_preserves_birth_info() -> None:
    engine = ZiweiChartEngine()
    birth = _birth_info()
    chart = engine.build_chart(birth)
    assert chart.birth_info_snapshot["gender"] == "female"
    assert chart.birth_info_snapshot["calendar_type"] == "solar"


def test_engine_four_hua_present() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info())
    assert chart.four_hua is not None
    assert chart.four_hua.hua_lu or chart.four_hua.hua_quan or chart.four_hua.hua_ke or chart.four_hua.hua_ji


def test_normalizer_output_structure() -> None:
    engine = ZiweiChartEngine()
    normalizer = ChartNormalizer()
    raw = engine.build_chart(_birth_info())
    normalized = normalizer.normalize(raw)

    assert normalized.chart_id == raw.chart_id
    assert normalized.source == "iztro_py"
    assert "12 palaces" in normalized.summary
    assert "Stub" not in normalized.summary
    assert len(normalized.palaces) == 12


def test_normalizer_preserves_palaces() -> None:
    engine = ZiweiChartEngine()
    normalizer = ChartNormalizer()
    raw = engine.build_chart(_birth_info())
    normalized = normalizer.normalize(raw)

    for rp, np in zip(raw.palaces, normalized.palaces):
        assert rp.name == np.name
        assert rp.index == np.index


# --- Provider field extraction tests (Branch 16/17) ---


def test_engine_metadata_from_provider() -> None:
    """Provider should extract lunar_date, chinese_date, and five_elements_class from iztro-py."""
    engine = ZiweiChartEngine()
    raw = engine.build_chart(_birth_info())

    assert raw.metadata is not None
    assert raw.metadata.lunar_date is not None
    assert raw.metadata.chinese_date is not None
    # five_elements_class should be extracted from chart.five_elements_class
    assert raw.metadata.five_elements_class is not None


def test_engine_star_scope_present_when_provider_has_scope() -> None:
    """Stars should have scope field when provider provides it."""
    engine = ZiweiChartEngine()
    raw = engine.build_chart(_birth_info())

    # Check that stars have scope field (even if value is None)
    all_stars = [s for p in raw.palaces for s in p.stars]
    assert len(all_stars) > 0, "Should have stars in the chart"
    # All stars should have scope attribute (even if None)
    for star in all_stars:
        assert hasattr(star, "scope"), f"Star {star.name} should have scope attribute"


def test_engine_decadal_information_present() -> None:
    """Provider should extract decadal information from palaces."""
    engine = ZiweiChartEngine()
    raw = engine.build_chart(_birth_info())

    # Check that palaces have decadal information
    palaces_with_decadal = [p for p in raw.palaces if p.decadal is not None]
    # Most palaces should have decadal info
    assert len(palaces_with_decadal) > 0


def test_normalizer_preserves_metadata_and_decadal() -> None:
    """Normalizer should preserve metadata and decadal fields from raw chart."""
    engine = ZiweiChartEngine()
    normalizer = ChartNormalizer()
    raw = engine.build_chart(_birth_info())
    normalized = normalizer.normalize(raw)

    # Metadata should be preserved
    assert normalized.metadata is not None
    assert normalized.metadata.lunar_date == raw.metadata.lunar_date
    assert normalized.metadata.chinese_date == raw.metadata.chinese_date

    # five_elements_class should be from metadata.five_elements_class, not derived
    if raw.metadata.five_elements_class:
        assert normalized.five_elements_class == raw.metadata.five_elements_class

    # Current age and decadal should be preserved
    assert raw.current_age is not None, "Raw chart should have current_age populated"
    assert raw.current_decadal is not None, "Raw chart should have current_decadal populated"
    assert normalized.current_age == raw.current_age
    assert normalized.current_decadal == raw.current_decadal

    # Current decadal should be semantically consistent with palace-level decadal facts
    idx = raw.current_decadal.palace_index
    assert idx is not None, "Current decadic should have a palace_index"
    assert (
        raw.current_decadal.palace_name == raw.palaces[idx].name
    ), "Current decadic palace_name should match the palace name at the same index"
    assert (
        raw.current_decadal.start_age == raw.palaces[idx].decadal.start_age
    ), "Current decadic start_age should match the palace decadal start_age"
    assert (
        raw.current_decadal.end_age == raw.palaces[idx].decadal.end_age
    ), "Current decadic end_age should match the palace decadal end_age"

    # Palace decadal info should be preserved
    for rp, np in zip(raw.palaces, normalized.palaces):
        assert rp.decadal == np.decadal


def test_chart_facts_includes_metadata_scope_decadal_evidence() -> None:
    """Chart facts should include metadata, scope, and decadal in evidence and output."""
    from app.engines.chart_facts import build_chart_facts

    engine = ZiweiChartEngine()
    normalizer = ChartNormalizer()
    raw = engine.build_chart(_birth_info())
    normalized = normalizer.normalize(raw)
    chart_facts = build_chart_facts(normalized)

    # Metadata should be in chart_facts
    if normalized.metadata:
        assert "metadata" in chart_facts
        assert chart_facts["metadata"]["lunar_date"] == normalized.metadata.lunar_date

    # Evidence index should have metadata entries
    evidence_types = {e["type"] for e in chart_facts["evidence_index"]}
    assert "metadata" in evidence_types

    # Evidence index should have decadal entries
    assert "decadal" in evidence_types

    # Star facts should include scope
    palace_with_stars = next((p for p in chart_facts["palaces"] if p.get("major_star_facts")), None)
    if palace_with_stars:
        # Check that star_facts structure includes scope key
        assert "scope" in palace_with_stars["major_star_facts"][0], "Star facts should include scope field"

    # Current analysis context should be present
    assert normalized.current_age is not None, "Current age should be populated"
    assert "current_age" in chart_facts, "Current age should be in chart_facts"
    assert normalized.current_decadal is not None, "Current decadal should be populated"
    assert "current_decadal" in chart_facts, "Current decadal should be in chart_facts"
