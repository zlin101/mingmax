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
            stars=[_star("紫微", "major"), _star("天府", "major"), _star("文昌", "minor")],
            four_hua=FourHua(hua_lu="紫微"),
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
        four_hua=FourHua(hua_lu="紫微", hua_quan="太阴", hua_ke="右弼", hua_ji="天机"),
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


def test_normalizer_sets_ming_palace_index() -> None:
    raw = _raw_chart()
    normalized = ChartNormalizer().normalize(raw)
    assert normalized.ming_palace_index == 0


def test_normalizer_sets_body_palace_index() -> None:
    raw = _raw_chart()
    normalized = ChartNormalizer().normalize(raw)
    assert normalized.body_palace_index == 2


def test_normalizer_sets_opposite_palace_index() -> None:
    raw = _raw_chart()
    normalized = ChartNormalizer().normalize(raw)
    for p in normalized.palaces:
        assert p.opposite_palace_index == (p.index + 6) % 12


def test_normalizer_sets_san_fang_si_zheng() -> None:
    raw = _raw_chart()
    normalized = ChartNormalizer().normalize(raw)
    for p in normalized.palaces:
        assert p.san_fang_si_zheng_indexes is not None
        assert len(p.san_fang_si_zheng_indexes) == 4
        assert p.index in p.san_fang_si_zheng_indexes


def test_normalizer_detects_empty_palace() -> None:
    palaces = [
        Palace(index=0, name="命宫", stars=[]),
        Palace(index=1, name="兄弟宫", stars=[_star("天机", "major")]),
        Palace(index=2, name="夫妻宫", stars=[_star("太阳", "major")]),
        Palace(index=3, name="子女宫", stars=[_star("武曲", "major")]),
        Palace(index=4, name="财帛宫", stars=[_star("天同", "major")]),
        Palace(index=5, name="疾厄宫", stars=[_star("廉贞", "major")]),
        Palace(index=6, name="迁移宫", stars=[_star("天府", "major")]),
        Palace(index=7, name="交友宫", stars=[]),
        Palace(index=8, name="官禄宫", stars=[]),
        Palace(index=9, name="田宅宫", stars=[]),
        Palace(index=10, name="福德宫", stars=[]),
        Palace(index=11, name="父母宫", stars=[]),
    ]
    raw = RawChart(
        source="test",
        chart_id="test-empty",
        birth_info_snapshot={},
        palaces=palaces,
    )
    normalized = ChartNormalizer().normalize(raw)
    assert normalized.palaces[0].is_empty is True
    assert normalized.palaces[0].borrowed_from_index == 6
    assert normalized.palaces[0].borrowed_major_stars == ["天府"]


def test_normalizer_non_empty_palace_no_borrowing() -> None:
    raw = _raw_chart()
    normalized = ChartNormalizer().normalize(raw)
    for p in normalized.palaces:
        major = [s.name for s in p.stars if s.category == "major"]
        if major:
            assert p.is_empty is False
            assert p.borrowed_from_index is None
            assert p.borrowed_major_stars is None


def test_normalizer_uses_palace_index_not_list_position() -> None:
    palaces = [
        Palace(index=6, name="迁移宫", stars=[_star("天府", "major")]),
        Palace(index=0, name="命宫", stars=[]),
    ]
    raw = RawChart(
        source="test",
        chart_id="test-unordered",
        birth_info_snapshot={},
        palaces=palaces,
    )
    normalized = ChartNormalizer().normalize(raw)
    assert normalized.ming_palace_index == 0
    ming = next(p for p in normalized.palaces if p.name == "命宫")
    assert ming.is_empty is True
    assert ming.borrowed_from_index == 6
    assert ming.borrowed_major_stars == ["天府"]
