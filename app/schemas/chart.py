from pydantic import BaseModel, Field


class Star(BaseModel):
    name: str
    brightness: str | None = None
    category: str | None = None


class FourHua(BaseModel):
    hua_lu: str | None = None
    hua_quan: str | None = None
    hua_ke: str | None = None
    hua_ji: str | None = None


class Palace(BaseModel):
    index: int = Field(ge=0, le=11)
    name: str
    heavenly_stem: str | None = None
    earthly_branch: str | None = None
    stars: list[Star] = Field(default_factory=list)
    four_hua: FourHua | None = None
    is_body_palace: bool = False


class RawChart(BaseModel):
    source: str = "stub"
    chart_id: str
    birth_info_snapshot: dict
    palaces: list[Palace] = Field(default_factory=list)
    four_hua: FourHua | None = None


class NormalizedChart(BaseModel):
    chart_id: str
    source: str
    summary: str
    palaces: list[Palace] = Field(default_factory=list)
    four_hua: FourHua | None = None
