import hashlib
from zoneinfo import ZoneInfo

from iztro_py import astro

from app.engines.errors import UnsupportedGenderError
from app.engines.time_calibration import infer_longitude_from_timezone, true_solar_time_offset
from app.schemas.birth import BirthInfo, Gender
from app.schemas.chart import FourHua, Palace, RawChart, Star

GENDER_MAP = {
    Gender.male: "男",
    Gender.female: "女",
}

SOURCE = "iztro_py"


def _get_local_date_hour(birth_info: BirthInfo) -> tuple[str, int]:
    tz = ZoneInfo(birth_info.timezone)
    local_dt = birth_info.birth_datetime.astimezone(tz)

    longitude = birth_info.longitude if birth_info.longitude is not None else infer_longitude_from_timezone(local_dt)
    tst_offset = true_solar_time_offset(local_dt, longitude)
    true_solar_dt = local_dt + tst_offset
    date_str = true_solar_dt.strftime("%Y-%m-%d")
    hour = true_solar_dt.hour

    return date_str, hour


def _map_gender(gender: Gender) -> str:
    mapped = GENDER_MAP.get(gender)
    if mapped is None:
        raise UnsupportedGenderError(
            f"Gender '{gender.value}' is not supported by the chart engine. "
            f"Supported: {', '.join(g.value for g in GENDER_MAP)}"
        )
    return mapped


def _parse_stars(iztro_stars: list, category: str) -> list[Star]:
    stars = []
    for s in iztro_stars:
        name = s.translate_name() if hasattr(s, "translate_name") else str(s.name)
        brightness = s.translate_brightness() if (hasattr(s, "translate_brightness") and s.brightness) else None
        stars.append(Star(name=name, brightness=brightness, category=category))
    return stars


def _extract_four_hua(palaces: list) -> FourHua | None:
    hua_map: dict[str, str] = {}
    for palace in palaces:
        for s in palace.major_stars:
            if s.mutagen:
                star_name = s.translate_name() if hasattr(s, "translate_name") else str(s.name)
                mutagen_map = {"禄": "hua_lu", "权": "hua_quan", "科": "hua_ke", "忌": "hua_ji"}
                field = mutagen_map.get(s.mutagen)
                if field:
                    hua_map[field] = star_name
    if not hua_map:
        return None
    return FourHua(**hua_map)


def build_chart_from_iztro(birth_info: BirthInfo) -> RawChart:
    gender = _map_gender(birth_info.gender)
    date_str, hour = _get_local_date_hour(birth_info)
    chart = astro.by_solar_hour(date_str, hour, gender)

    palaces = []
    for i, p in enumerate(chart.palaces):
        palace_name = p.translate_name() if hasattr(p, "translate_name") else str(p.name)
        heavenly_stem = p.translate_heavenly_stem() if hasattr(p, "translate_heavenly_stem") else None
        earthly_branch = p.translate_earthly_branch() if hasattr(p, "translate_earthly_branch") else None

        stars = _parse_stars(p.major_stars, "major")
        stars += _parse_stars(p.minor_stars, "minor")
        stars += _parse_stars(p.adjective_stars, "adjective")

        is_body = hasattr(p, "is_body_palace") and p.is_body_palace

        palace_four_hua = None
        for s in p.major_stars:
            if s.mutagen:
                mutagen_map = {"禄": "hua_lu", "权": "hua_quan", "科": "hua_ke", "忌": "hua_ji"}
                field = mutagen_map.get(s.mutagen)
                if field:
                    star_name = s.translate_name() if hasattr(s, "translate_name") else str(s.name)
                    palace_four_hua = FourHua(**{field: star_name})
                    break

        palaces.append(
            Palace(
                index=i,
                name=palace_name,
                heavenly_stem=heavenly_stem,
                earthly_branch=earthly_branch,
                stars=stars,
                four_hua=palace_four_hua,
                is_body_palace=is_body,
            )
        )

    four_hua = _extract_four_hua(chart.palaces)

    payload = birth_info.model_dump_json()
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]

    return RawChart(
        source=SOURCE,
        chart_id=f"{SOURCE}-{digest}",
        birth_info_snapshot=birth_info.model_dump(mode="json"),
        palaces=palaces,
        four_hua=four_hua,
    )
