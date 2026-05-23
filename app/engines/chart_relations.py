def opposite_palace_index(index: int) -> int:
    if not 0 <= index <= 11:
        raise ValueError(f"Palace index must be 0-11, got {index}")
    return (index + 6) % 12


def san_fang_si_zheng_indexes(index: int) -> list[int]:
    if not 0 <= index <= 11:
        raise ValueError(f"Palace index must be 0-11, got {index}")
    return [index, (index + 4) % 12, opposite_palace_index(index), (index + 8) % 12]


def is_empty_palace(major_stars: list[str]) -> bool:
    return len(major_stars) == 0


def borrowed_from_index(index: int) -> int:
    return opposite_palace_index(index)


def borrowed_major_stars(index: int, opposite_major_stars: list[str]) -> list[str]:
    borrowed_from_index(index)
    return list(opposite_major_stars)
