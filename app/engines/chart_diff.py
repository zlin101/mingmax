from pydantic import BaseModel, Field

from app.schemas.chart import NormalizedChart, Palace


class ExpectedPalaceSnapshot(BaseModel):
    index: int
    name: str
    major_stars: list[str] = Field(default_factory=list)
    is_body_palace: bool = False


class ExpectedChartSnapshot(BaseModel):
    palace_count: int = 12
    palaces: list[ExpectedPalaceSnapshot] = Field(default_factory=list)
    hua_lu: str | None = None
    hua_quan: str | None = None
    hua_ke: str | None = None
    hua_ji: str | None = None


class PalaceDiff(BaseModel):
    palace_index: int
    palace_name: str
    field: str
    expected: str
    actual: str
    severity: str


class ChartDiffResult(BaseModel):
    diffs: list[PalaceDiff] = Field(default_factory=list)

    @property
    def errors(self) -> list[PalaceDiff]:
        return [d for d in self.diffs if d.severity == "error"]

    @property
    def warnings(self) -> list[PalaceDiff]:
        return [d for d in self.diffs if d.severity == "warning"]

    @property
    def is_match(self) -> bool:
        return len(self.errors) == 0


def diff_charts(actual: NormalizedChart, expected: ExpectedChartSnapshot) -> ChartDiffResult:
    diffs: list[PalaceDiff] = []

    if len(actual.palaces) != expected.palace_count:
        diffs.append(
            PalaceDiff(
                palace_index=-1,
                palace_name="",
                field="palace_count",
                expected=str(expected.palace_count),
                actual=str(len(actual.palaces)),
                severity="error",
            )
        )

    actual_by_name: dict[str, Palace] = {p.name: p for p in actual.palaces}

    for ep in expected.palaces:
        ap = actual_by_name.get(ep.name)
        if ap is None:
            diffs.append(
                PalaceDiff(
                    palace_index=ep.index,
                    palace_name=ep.name,
                    field="name",
                    expected=ep.name,
                    actual="(missing)",
                    severity="error",
                )
            )
            continue

        if ap.index != ep.index:
            diffs.append(
                PalaceDiff(
                    palace_index=ep.index,
                    palace_name=ep.name,
                    field="index",
                    expected=str(ep.index),
                    actual=str(ap.index),
                    severity="warning",
                )
            )

        actual_major = sorted(s.name for s in ap.stars if s.category == "major")
        expected_major = sorted(ep.major_stars)
        if actual_major != expected_major:
            diffs.append(
                PalaceDiff(
                    palace_index=ep.index,
                    palace_name=ep.name,
                    field="major_stars",
                    expected=str(expected_major),
                    actual=str(actual_major),
                    severity="error",
                )
            )

        if ep.is_body_palace and not ap.is_body_palace:
            diffs.append(
                PalaceDiff(
                    palace_index=ep.index,
                    palace_name=ep.name,
                    field="is_body_palace",
                    expected="True",
                    actual="False",
                    severity="warning",
                )
            )

    if expected.hua_lu or expected.hua_quan or expected.hua_ke or expected.hua_ji:
        actual_hua = actual.four_hua
        for field_name, expected_val in [
            ("hua_lu", expected.hua_lu),
            ("hua_quan", expected.hua_quan),
            ("hua_ke", expected.hua_ke),
            ("hua_ji", expected.hua_ji),
        ]:
            if expected_val is not None:
                actual_val = getattr(actual_hua, field_name, None) if actual_hua else None
                if actual_val != expected_val:
                    diffs.append(
                        PalaceDiff(
                            palace_index=-1,
                            palace_name="",
                            field=field_name,
                            expected=expected_val,
                            actual=str(actual_val),
                            severity="error",
                        )
                    )

    return ChartDiffResult(diffs=diffs)
