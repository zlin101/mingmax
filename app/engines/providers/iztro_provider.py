import hashlib
from zoneinfo import ZoneInfo

from iztro_py import astro

from app.engines.errors import UnsupportedGenderError
from app.engines.time_calibration import infer_longitude_from_timezone, true_solar_time_offset
from app.schemas.birth import BirthInfo, Gender
from app.schemas.chart import ChartMetadata, DecadalRange, FourHua, Palace, RawChart, Star

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
        scope = s.scope if hasattr(s, "scope") else None
        stars.append(Star(name=name, brightness=brightness, category=category, scope=scope))
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
    from datetime import datetime

    gender = _map_gender(birth_info.gender)
    date_str, hour = _get_local_date_hour(birth_info)
    chart = astro.by_solar_hour(date_str, hour, gender)

    # Extract metadata from chart
    five_elements_class = None
    if hasattr(chart, "five_elements_class"):
        five_elements_class = chart.five_elements_class

    metadata = ChartMetadata(
        lunar_date=chart.lunar_date if hasattr(chart, "lunar_date") else None,
        chinese_date=chart.chinese_date if hasattr(chart, "chinese_date") else None,
        soul_palace_earthly_branch=(
            chart.earthly_branch_of_soul_palace if hasattr(chart, "earthly_branch_of_soul_palace") else None
        ),
        body_palace_earthly_branch=(
            chart.earthly_branch_of_body_palace if hasattr(chart, "earthly_branch_of_body_palace") else None
        ),
        body=chart.body if hasattr(chart, "body") else None,
        five_elements_class=five_elements_class,
    )

    # Calculate current age (using 虚岁 approximate: current year - birth year + 1)
    current_year = datetime.now().year
    birth_year = birth_info.birth_datetime.year
    current_age = current_year - birth_year + 1  # 虚岁近似

    # Find current decadal using chart.horoscope() API
    current_decadal = None
    if hasattr(chart, "horoscope"):
        try:
            # Get today's date as solar date string for horoscope calculation
            today = datetime.now()
            solar_date = today.strftime("%Y-%m-%d")

            # Call horoscope API with solar date
            horoscope = chart.horoscope(solar_date)
            if horoscope:
                # Use nominal_age from horoscope if available
                nominal_age = horoscope.nominal_age if hasattr(horoscope, "nominal_age") else current_age
                current_age = nominal_age

                # Get current decadal from horoscope
                if hasattr(horoscope, "decadal"):
                    decadal = horoscope.decadal
                    if decadal:
                        # Get the palace index from the decadal item
                        palace_index = int(decadal.index) if hasattr(decadal, "index") else None

                        # Find the corresponding palace decadal to get complete info (including range)
                        if palace_index is not None and palace_index < len(chart.palaces):
                            palace_obj = chart.palaces[palace_index]
                            if hasattr(palace_obj, "decadal") and palace_obj.decadal:
                                d = palace_obj.decadal
                                palace_range = d.range if hasattr(d, "range") else None
                                if palace_range and len(palace_range) >= 2:
                                    # Get palace name from the palace object (use translated name)
                                    palace_name = (
                                        palace_obj.translate_name()
                                        if hasattr(palace_obj, "translate_name")
                                        else (palace_obj.name if hasattr(palace_obj, "name") else None)
                                    )

                                    current_decadal = DecadalRange(
                                        start_age=palace_range[0],
                                        end_age=palace_range[1],
                                        heavenly_stem=d.heavenly_stem if hasattr(d, "heavenly_stem") else None,
                                        earthly_branch=d.earthly_branch if hasattr(d, "earthly_branch") else None,
                                        palace_index=palace_index,
                                        palace_name=palace_name,
                                    )
        except AttributeError:
            # horoscope API structure different, skip current decadal
            pass
        except IndexError, ValueError, TypeError:
            # If decadal extraction fails due to data structure issues, continue without it
            # This is an optional enrichment for current context analysis
            pass

    palaces = []
    for i, p in enumerate(chart.palaces):
        palace_name = p.translate_name() if hasattr(p, "translate_name") else str(p.name)
        heavenly_stem = p.translate_heavenly_stem() if hasattr(p, "translate_heavenly_stem") else None
        earthly_branch = p.translate_earthly_branch() if hasattr(p, "translate_earthly_branch") else None

        stars = _parse_stars(p.major_stars, "major")
        stars += _parse_stars(p.minor_stars, "minor")
        stars += _parse_stars(p.adjective_stars, "adjective")

        is_body = hasattr(p, "is_body_palace") and p.is_body_palace

        hua_map: dict[str, str] = {}
        for s in p.major_stars:
            if s.mutagen:
                mutagen_map = {"禄": "hua_lu", "权": "hua_quan", "科": "hua_ke", "忌": "hua_ji"}
                field = mutagen_map.get(s.mutagen)
                if field:
                    star_name = s.translate_name() if hasattr(s, "translate_name") else str(s.name)
                    hua_map[field] = star_name
        palace_four_hua = FourHua(**hua_map) if hua_map else None

        # Extract decadal information for this palace
        palace_decadal = None
        if hasattr(p, "decadal") and p.decadal:
            d = p.decadal
            decadal_range = d.range if hasattr(d, "range") else None
            if decadal_range and len(decadal_range) >= 2:
                palace_decadal = DecadalRange(
                    start_age=decadal_range[0],
                    end_age=decadal_range[1],
                    heavenly_stem=d.heavenly_stem if hasattr(d, "heavenly_stem") else None,
                    earthly_branch=d.earthly_branch if hasattr(d, "earthly_branch") else None,
                    palace_index=i,
                    palace_name=palace_name,
                )

        palaces.append(
            Palace(
                index=i,
                name=palace_name,
                heavenly_stem=heavenly_stem,
                earthly_branch=earthly_branch,
                stars=stars,
                four_hua=palace_four_hua,
                is_body_palace=is_body,
                decadal=palace_decadal,
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
        metadata=metadata,
        current_age=current_age,
        current_decadal=current_decadal,
    )
