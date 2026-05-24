from pydantic import BaseModel, Field


class Star(BaseModel):
    name: str
    brightness: str | None = None
    category: str | None = None
    scope: str | None = None


class DecadalRange(BaseModel):
    """Represents a decadal (大限) range in ziwei astrology."""

    start_age: int
    end_age: int
    heavenly_stem: str | None = None
    earthly_branch: str | None = None
    palace_index: int | None = None
    palace_name: str | None = None


class FourHua(BaseModel):
    hua_lu: str | None = None
    hua_quan: str | None = None
    hua_ke: str | None = None
    hua_ji: str | None = None


class ChartMetadata(BaseModel):
    """Metadata about the ziwei chart from provider."""

    lunar_date: str | None = None
    chinese_date: str | None = None
    soul_palace_earthly_branch: str | None = None
    body_palace_earthly_branch: str | None = None
    body: str | None = None
    five_elements_class: str | None = None


class Palace(BaseModel):
    index: int = Field(ge=0, le=11)
    name: str
    heavenly_stem: str | None = None
    earthly_branch: str | None = None
    stars: list[Star] = Field(default_factory=list)
    four_hua: FourHua | None = None
    is_body_palace: bool = False
    opposite_palace_index: int | None = None
    san_fang_si_zheng_indexes: list[int] | None = None
    is_empty: bool | None = None
    borrowed_from_index: int | None = None
    borrowed_major_stars: list[str] | None = None
    decadal: DecadalRange | None = None


class RawChart(BaseModel):
    source: str = "stub"
    chart_id: str
    birth_info_snapshot: dict
    palaces: list[Palace] = Field(default_factory=list)
    four_hua: FourHua | None = None
    metadata: ChartMetadata | None = None
    current_age: int | None = None
    current_decadal: DecadalRange | None = None


class NormalizedChart(BaseModel):
    chart_id: str
    source: str
    summary: str
    palaces: list[Palace] = Field(default_factory=list)
    four_hua: FourHua | None = None
    ming_palace_index: int | None = None
    body_palace_index: int | None = None
    five_elements_class: str | None = None
    lunar_info: dict | None = None
    metadata: ChartMetadata | None = None
    current_age: int | None = None
    current_decadal: DecadalRange | None = None
