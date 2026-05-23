#!/usr/bin/env python3
"""
Generate iztro-py provider snapshot for field audit.

This script calls iztro-py with synthetic or user-provided birth info,
then generates a comprehensive snapshot of the provider's raw output
for field capability auditing.

Usage:
    # Use default synthetic sample
    uv run python scripts/dump_iztro_provider_snapshot.py

    # Use private sample (output goes to .local/ directory, not committed)
    uv run python scripts/dump_iztro_provider_snapshot.py --private /path/to/sample.md
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.engines.providers.iztro_provider import _get_local_date_hour, _map_gender, build_chart_from_iztro  # noqa: E402
from app.engines.providers.provider_snapshot import (  # noqa: E402
    generate_field_inventory,
    serialize_provider_object,
)
from app.schemas.birth import BirthInfo, CalendarType, Gender  # noqa: E402

DEFAULT_OUTPUT_DIR = Path(".local/iztro_snapshots")


def resolve_output_dir(output_dir: Path, is_private: bool) -> Path:
    resolved = output_dir if output_dir.is_absolute() else project_root / output_dir
    resolved = resolved.resolve()

    if is_private:
        allowed_root = (project_root / DEFAULT_OUTPUT_DIR).resolve()
        if resolved != allowed_root and allowed_root not in resolved.parents:
            raise ValueError("Private sample snapshots must be written under .local/iztro_snapshots/")

    return resolved


def get_synthetic_birth_info() -> BirthInfo:
    """Generate a synthetic birth info sample for testing."""
    from zoneinfo import ZoneInfo

    return BirthInfo(
        calendar_type=CalendarType.solar,
        birth_datetime=datetime(1990, 5, 15, 14, 30, tzinfo=ZoneInfo("Asia/Shanghai")),
        gender=Gender.male,
        birth_place="Beijing, China",
        timezone="Asia/Shanghai",
        longitude=116.4,
    )


def parse_private_sample(file_path: Path) -> BirthInfo:
    """
    Parse a private sample file.

    Expected format (simple key=value or key: value):
    calendar_type: solar
    birth_date: 1990-05-15
    birth_time: 14:30
    timezone: Asia/Shanghai
    gender: male
    birth_place: Beijing, China
    longitude: 116.4

    Note: This function should NOT commit or log the actual values from the file.
    The output will be written to .local/ which is gitignored.
    """
    from zoneinfo import ZoneInfo

    data = {}
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Support both : and = as separators
            if ":" in line:
                key, value = line.split(":", 1)
            elif "=" in line:
                key, value = line.split("=", 1)
            else:
                continue

            data[key.strip()] = value.strip()

    # Parse datetime
    birth_date = data.get("birth_date", "1990-01-01")
    birth_time = data.get("birth_time", "12:00")
    tz_str = data.get("timezone", "Asia/Shanghai")
    birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo(tz_str))

    gender_str = data.get("gender", "male").lower()
    if gender_str not in {"male", "female"}:
        raise ValueError("Only gender=male or gender=female is supported for provider snapshots")
    gender = Gender.male if gender_str == "male" else Gender.female

    calendar_str = data.get("calendar_type", "solar").lower()
    if calendar_str != "solar":
        raise ValueError("Provider snapshot currently supports only calendar_type=solar")

    return BirthInfo(
        calendar_type=CalendarType.solar,
        birth_datetime=birth_datetime,
        gender=gender,
        birth_place=data.get("birth_place", "Unknown"),
        timezone=tz_str,
        longitude=float(data["longitude"]) if data.get("longitude") else None,
    )


def call_iztro_directly(birth_info: BirthInfo) -> object:
    """
    Call iztro-py directly and return the raw astrolabe object.

    This bypasses our provider wrapper to capture the original object structure.
    """
    from iztro_py import astro

    gender = _map_gender(birth_info.gender)
    date_str, hour = _get_local_date_hour(birth_info)
    chart = astro.by_solar_hour(date_str, hour, gender)

    return chart


def generate_inventory_markdown(inventory: list[dict], output_path: Path) -> None:
    """Generate a markdown inventory from the field inventory."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# iztro-py Provider Field Inventory\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        f.write(f"Total fields found: {len(inventory)}\n\n")

        # Group by top-level path component
        by_section: dict[str, list[dict]] = {}
        for item in inventory:
            path = item.get("path", "")
            top_level = path.split(".")[0] if path else "root"
            if top_level not in by_section:
                by_section[top_level] = []
            by_section[top_level].append(item)

        # Write sections
        for section in sorted(by_section.keys()):
            f.write(f"## {section}\n\n")
            for item in sorted(by_section[section], key=lambda x: x.get("path", "")):
                f.write(f"### `{item.get('path', '')}`\n\n")
                f.write(f"- **Type**: `{item.get('type', 'unknown')}`\n")
                if item.get("sample_value") is not None:
                    sample = str(item["sample_value"])[:100]
                    f.write(f"- **Sample Value**: `{sample}`\n")
                f.write(f"- **Description**: {item.get('description', 'N/A')}\n")
                f.write(f"- **Exists**: {item.get('exists', False)}\n")
                f.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate iztro-py provider snapshot for field audit")
    parser.add_argument(
        "--private",
        type=Path,
        help="Path to private sample file (output goes to .local/ directory)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for snapshots (default: .local/iztro_snapshots/)",
    )
    args = parser.parse_args()

    try:
        output_dir = resolve_output_dir(args.output_dir, args.private is not None)
    except ValueError as e:
        print(f"Invalid output directory: {e}", file=sys.stderr)
        return 2

    output_dir.mkdir(parents=True, exist_ok=True)

    if args.private:
        print("Using private sample from local path")
        try:
            birth_info = parse_private_sample(args.private)
        except Exception as e:
            print(f"Failed to parse private sample: {e}", file=sys.stderr)
            return 2
        output_suffix = "private"
    else:
        print("Using synthetic birth info sample")
        birth_info = get_synthetic_birth_info()
        output_suffix = "synthetic"

    # Generate timestamp for output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Call iztro-py directly
    print("Calling iztro-py...")
    try:
        raw_astrolabe = call_iztro_directly(birth_info)
        print("✓ iztro-py call successful")
    except Exception as e:
        print(f"✗ iztro-py call failed: {e}")
        return 1

    # Serialize the raw astrolabe object
    print("Serializing astrolabe object...")
    try:
        serialized = serialize_provider_object(raw_astrolabe, "astrolabe")
        print("✓ Serialization successful")
    except Exception as e:
        print(f"✗ Serialization failed: {e}")
        return 1

    # Generate field inventory
    print("Generating field inventory...")
    try:
        inventory = generate_field_inventory(serialized, "astrolabe")
        print(f"✓ Found {len(inventory)} fields")
    except Exception as e:
        print(f"✗ Inventory generation failed: {e}")
        return 1

    # Write JSON snapshot
    json_path = output_dir / f"{timestamp}-{output_suffix}-raw-provider-snapshot.json"
    print(f"Writing JSON snapshot to: {json_path}")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(serialized, f, indent=2, ensure_ascii=False)

    # Write markdown inventory
    md_path = output_dir / f"{timestamp}-{output_suffix}-field-inventory.md"
    print(f"Writing markdown inventory to: {md_path}")
    generate_inventory_markdown(inventory, md_path)

    # Also call through our provider for comparison
    print("Calling through mingmax provider...")
    try:
        raw_chart = build_chart_from_iztro(birth_info)
        provider_path = output_dir / f"{timestamp}-{output_suffix}-mingmax-provider.json"
        with open(provider_path, "w", encoding="utf-8") as f:
            # Convert to dict for JSON serialization
            json.dump(raw_chart.model_dump(mode="json"), f, indent=2, ensure_ascii=False)
        print(f"✓ mingmax provider output written to: {provider_path}")
    except Exception as e:
        print(f"✗ mingmax provider call failed: {e}")
        # This is not a critical error, so continue

    print("\n✓ Snapshot generation complete!")
    print(f"  - Raw snapshot: {json_path}")
    print(f"  - Field inventory: {md_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
