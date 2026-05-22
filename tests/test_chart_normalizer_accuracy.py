from app.engines.chart_normalizer import ChartNormalizer
from app.schemas.chart import FourHua, Palace, RawChart, Star


def _star(name: str, category: str) -> Star:
    return Star(name=name, brightness="庙", category=category)


def _raw_chart() -> RawChart:
    palaces = [
        Palace(
            index=0,
            name="命宫",
            heavenly_stem="丁",
            earthly_branch="巳",
            stars=[_star("廉贞", "major"), _star("贪狼", "major"), _star("文昌", "minor")],
            four_hua=FourHua(hua_lu="贪狼"),
            is_body_palace=False,
        ),
        Palace(
            index=1,
            name="兄弟宫",
            heavenly_stem="丙",
            earthly_branch="辰",
            stars=[_star("太阴", "major"), _star("陀罗", "minor")],
            four_hua=FourHua(hua_quan="太阴"),
            is_body_palace=False,
        ),
        Palace(
            index=2,
            name="夫妻宫",
            heavenly_stem="乙",
            earthly_branch="卯",
            stars=[_star("天府", "major")],
            is_body_palace=True,
        ),
    ]
    return RawChart(
        source="test_source",
        chart_id="test-raw",
        birth_info_snapshot={},
        palaces=palaces,
        four_hua=FourHua(hua_lu="贪狼", hua_quan="太阴", hua_ke="右弼", hua_ji="天机"),
    )


def test_normalizer_preserves_palace_count() -> None:
    raw = _raw_chart()
    normalized = ChartNormalizer().normalize(raw)
    assert len(normalized.palaces) == len(raw.palaces)


def test_normalizer_preserves_palace_names() -> None:
    raw = _raw_chart()
    normalized = ChartNormalizer().normalize(raw)
    for rp, np in zip(raw.palaces, normalized.palaces):
        assert np.name == rp.name


def test_normalizer_preserves_major_stars() -> None:
    raw = _raw_chart()
    normalized = ChartNormalizer().normalize(raw)
    for rp, np in zip(raw.palaces, normalized.palaces):
        raw_major = sorted(s.name for s in rp.stars if s.category == "major")
        norm_major = sorted(s.name for s in np.stars if s.category == "major")
        assert norm_major == raw_major, f"Palace {rp.name}: major stars lost in normalization"


def test_normalizer_preserves_minor_stars() -> None:
    raw = _raw_chart()
    normalized = ChartNormalizer().normalize(raw)
    for rp, np in zip(raw.palaces, normalized.palaces):
        raw_minor = sorted(s.name for s in rp.stars if s.category == "minor")
        norm_minor = sorted(s.name for s in np.stars if s.category == "minor")
        assert norm_minor == raw_minor, f"Palace {rp.name}: minor stars lost"


def test_normalizer_preserves_heavenly_stem() -> None:
    raw = _raw_chart()
    normalized = ChartNormalizer().normalize(raw)
    for rp, np in zip(raw.palaces, normalized.palaces):
        assert np.heavenly_stem == rp.heavenly_stem, f"Palace {rp.name}: stem lost"


def test_normalizer_preserves_earthly_branch() -> None:
    raw = _raw_chart()
    normalized = ChartNormalizer().normalize(raw)
    for rp, np in zip(raw.palaces, normalized.palaces):
        assert np.earthly_branch == rp.earthly_branch, f"Palace {rp.name}: branch lost"


def test_normalizer_preserves_four_hua() -> None:
    raw = _raw_chart()
    normalized = ChartNormalizer().normalize(raw)
    assert normalized.four_hua is not None
    assert normalized.four_hua.hua_lu == raw.four_hua.hua_lu
    assert normalized.four_hua.hua_quan == raw.four_hua.hua_quan
    assert normalized.four_hua.hua_ke == raw.four_hua.hua_ke
    assert normalized.four_hua.hua_ji == raw.four_hua.hua_ji


def test_normalizer_preserves_body_palace() -> None:
    raw = _raw_chart()
    normalized = ChartNormalizer().normalize(raw)
    body_palaces = [p for p in normalized.palaces if p.is_body_palace]
    assert len(body_palaces) == 1
    assert body_palaces[0].name == "夫妻宫"


def test_normalizer_preserves_star_brightness() -> None:
    raw = _raw_chart()
    normalized = ChartNormalizer().normalize(raw)
    for rp, np in zip(raw.palaces, normalized.palaces):
        for rs, ns in zip(rp.stars, np.stars):
            assert ns.brightness == rs.brightness, f"Star {rs.name}: brightness lost"


def test_normalizer_preserves_star_category() -> None:
    raw = _raw_chart()
    normalized = ChartNormalizer().normalize(raw)
    for rp, np in zip(raw.palaces, normalized.palaces):
        raw_cats = [s.category for s in rp.stars]
        norm_cats = [s.category for s in np.stars]
        assert norm_cats == raw_cats, f"Palace {rp.name}: star categories lost"
