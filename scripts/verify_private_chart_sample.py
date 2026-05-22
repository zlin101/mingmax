import argparse
import re
import sys
from datetime import datetime, timedelta, timezone

from app.engines.chart_diff import ChartDiffResult, ExpectedChartSnapshot, ExpectedPalaceSnapshot, diff_charts
from app.engines.chart_normalizer import ChartNormalizer
from app.engines.ziwei_chart_engine import ZiweiChartEngine
from app.schemas.birth import BirthInfo


def _parse_reference(text: str) -> dict:
    result: dict = {"palaces": []}

    gender_match = re.search(r"性别\s*:\s*(男|女)", text)
    if gender_match:
        result["gender"] = "male" if gender_match.group(1) == "男" else "female"

    clock_match = re.search(r"钟表时间\s*:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})", text)
    if clock_match:
        result["clock_time"] = clock_match.group(1).replace(" ", "T")

    longitude_match = re.search(r"地理经度\s*:\s*([\d.]+)", text)
    if longitude_match:
        result["longitude"] = float(longitude_match.group(1))

    body_match = re.search(r"身宫\s*:\s*(\S+)", text)
    if body_match:
        result["body_palace_branch"] = body_match.group(1)

    palace_pattern = re.compile(r"([^\s│├└]+?)\s*宫\[([^\]]+)\]", re.MULTILINE)
    matches = list(palace_pattern.finditer(text))
    for idx, m in enumerate(matches):
        palace_name = m.group(1).replace(" ", "")
        if not palace_name.endswith("宫"):
            palace_name += "宫"
        stem_branch = m.group(2)
        palace_entry = {"name": palace_name, "stem_branch": stem_branch}

        block_start = m.end()
        block_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        block = text[block_start:block_end]

        major_match = re.search(r"主星\s*:\s*(.*)", block)
        if major_match and major_match.group(1).strip() != "无":
            stars_text = major_match.group(1).strip()
            stars = []
            for segment in stars_text.split(","):
                name = ""
                for ch in segment.strip():
                    if "\u4e00" <= ch <= "\u9fff":
                        name += ch
                    else:
                        break
                if name:
                    stars.append(name)
            palace_entry["major_stars"] = stars
        else:
            palace_entry["major_stars"] = []

        if "[身宫]" in block:
            palace_entry["is_body_palace"] = True

        result["palaces"].append(palace_entry)

    mutagen_fields = {"生年禄": "hua_lu", "生年权": "hua_quan", "生年科": "hua_ke", "生年忌": "hua_ji"}
    for line in text.splitlines():
        if "星" not in line:
            continue
        for segment in line.split(","):
            star_match = re.search(r"([\u4e00-\u9fff]+)(?:\[[^\]]+\])+", segment)
            if not star_match:
                continue
            star_name = star_match.group(1)
            markers = re.findall(r"\[([^\]]+)\]", segment)
            for marker in markers:
                field = mutagen_fields.get(marker)
                if field:
                    result[field] = star_name

    return result


def _build_expected(ref: dict) -> ExpectedChartSnapshot:
    palaces = []
    for i, p in enumerate(ref.get("palaces", [])):
        palaces.append(
            ExpectedPalaceSnapshot(
                index=i,
                name=p["name"],
                major_stars=p.get("major_stars", []),
                is_body_palace=p.get("is_body_palace", False),
            )
        )
    return ExpectedChartSnapshot(
        palace_count=len(palaces),
        palaces=palaces,
        hua_lu=ref.get("hua_lu"),
        hua_quan=ref.get("hua_quan"),
        hua_ke=ref.get("hua_ke"),
        hua_ji=ref.get("hua_ji"),
    )


def _count_mismatched_palaces(result: ChartDiffResult) -> int:
    return len({d.palace_index for d in result.diffs if d.palace_index >= 0})


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify chart accuracy against a private sample")
    parser.add_argument("input_file", help="Path to private verification file")
    args = parser.parse_args()

    with open(args.input_file, encoding="utf-8") as f:
        text = f.read()

    ref = _parse_reference(text)

    if "clock_time" not in ref or "gender" not in ref:
        print("ERROR: Could not extract clock_time and gender from input file", file=sys.stderr)
        sys.exit(1)

    dt_str = ref["clock_time"]
    dt = datetime.fromisoformat(dt_str).replace(tzinfo=timezone(timedelta(hours=8)))

    birth_info = BirthInfo(
        calendar_type="solar",
        birth_datetime=dt,
        gender=ref["gender"],
        birth_place="Redacted",
        timezone="Asia/Shanghai",
        longitude=ref.get("longitude"),
    )

    input_mode = "true_solar_hour" if birth_info.longitude else "clock_hour"
    print(f"input_mode={input_mode}")

    engine = ZiweiChartEngine()
    raw = engine.build_chart(birth_info)
    normalizer = ChartNormalizer()
    normalized = normalizer.normalize(raw)

    expected = _build_expected(ref)
    result = diff_charts(normalized, expected)

    compared = min(len(normalized.palaces), expected.palace_count)
    mismatched = _count_mismatched_palaces(result)
    exact = max(0, compared - mismatched)

    print(f"summary={compared} palaces compared, {exact} exact, {mismatched} mismatched")
    print(f"errors={len(result.errors)}")
    print(f"warnings={len(result.warnings)}")

    if result.diffs:
        paths = set()
        for d in result.diffs:
            paths.add(d.field)
        print(f"diff_fields={', '.join(sorted(paths))}")


if __name__ == "__main__":
    main()
