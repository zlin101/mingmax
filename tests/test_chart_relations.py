import pytest

from app.engines.chart_relations import (
    borrowed_from_index,
    borrowed_major_stars,
    is_empty_palace,
    opposite_palace_index,
    san_fang_si_zheng_indexes,
)

# --- opposite_palace_index ---


def test_opposite_palace_index_correct_pairs() -> None:
    expected = {0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11, 6: 0, 7: 1, 8: 2, 9: 3, 10: 4, 11: 5}
    for idx, expected_opp in expected.items():
        assert opposite_palace_index(idx) == expected_opp


def test_opposite_palace_is_symmetric() -> None:
    for i in range(12):
        assert opposite_palace_index(opposite_palace_index(i)) == i


def test_opposite_palace_index_out_of_range() -> None:
    with pytest.raises(ValueError):
        opposite_palace_index(-1)
    with pytest.raises(ValueError):
        opposite_palace_index(12)


# --- san_fang_si_zheng_indexes ---


def test_san_fang_si_zheng_returns_four_indexes() -> None:
    result = san_fang_si_zheng_indexes(0)
    assert len(result) == 4


def test_san_fang_si_zheng_contains_self() -> None:
    for i in range(12):
        assert i in san_fang_si_zheng_indexes(i)


def test_san_fang_si_zheng_contains_opposite() -> None:
    for i in range(12):
        result = san_fang_si_zheng_indexes(i)
        assert opposite_palace_index(i) in result


def test_san_fang_si_zheng_known_group() -> None:
    result = set(san_fang_si_zheng_indexes(0))
    assert result == {0, 4, 6, 8}


def test_san_fang_si_zheng_another_group() -> None:
    result = set(san_fang_si_zheng_indexes(1))
    assert result == {1, 5, 7, 9}


def test_san_fang_si_zheng_out_of_range() -> None:
    with pytest.raises(ValueError):
        san_fang_si_zheng_indexes(-1)
    with pytest.raises(ValueError):
        san_fang_si_zheng_indexes(12)


# --- is_empty_palace ---


def test_is_empty_palace_no_major_stars() -> None:
    assert is_empty_palace(major_stars=[])


def test_is_empty_palace_with_major_stars() -> None:
    assert not is_empty_palace(major_stars=["紫微"])


# --- borrowed_from_index ---


def test_borrowed_from_index_returns_opposite() -> None:
    assert borrowed_from_index(2) == 8


# --- borrowed_major_stars ---


def test_borrowed_major_stars_from_opposite() -> None:
    stars = borrowed_major_stars(2, opposite_major_stars=["天府", "廉贞"])
    assert stars == ["天府", "廉贞"]


def test_borrowed_major_stars_empty_opposite() -> None:
    stars = borrowed_major_stars(2, opposite_major_stars=[])
    assert stars == []
