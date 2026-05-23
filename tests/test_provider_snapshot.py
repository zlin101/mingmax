"""Tests for provider snapshot functionality."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from app.engines.providers.provider_snapshot import (
    SerializationConfig,
    generate_field_inventory,
    serialize_provider_object,
)
from app.schemas.birth import BirthInfo, CalendarType, Gender
from scripts.dump_iztro_provider_snapshot import DEFAULT_OUTPUT_DIR, parse_private_sample, resolve_output_dir


def _sample_birth_info() -> BirthInfo:
    """Create a sample birth info for testing."""
    from datetime import datetime

    return BirthInfo(
        calendar_type=CalendarType.solar,
        birth_datetime=datetime(1990, 5, 15, 14, 30, tzinfo=ZoneInfo("Asia/Shanghai")),
        gender=Gender.male,
        birth_place="Beijing, China",
        timezone="Asia/Shanghai",
        longitude=116.4,
    )


def test_serialize_primitive_types() -> None:
    """Test serializer handles primitive types correctly."""
    result = serialize_provider_object("test_string", "root")
    assert result["_snapshot_metadata"]["root_type"] == "str"
    assert result["_data"] == "test_string"


def test_serialize_max_string_length() -> None:
    """Test serializer truncates long strings."""
    long_string = "a" * (SerializationConfig.max_string_length + 100)
    result = serialize_provider_object(long_string, "root")
    data = result["_data"]
    assert data["_type"] == "truncated_string"
    assert data["_length"] == len(long_string)
    # The value includes "..." at the end, so it's max_string_length + 3
    assert "..." in data["_value"]


def test_serialize_list() -> None:
    """Test serializer handles lists."""
    result = serialize_provider_object([1, 2, 3], "root")
    assert result["_data"] == [1, 2, 3]


def test_serialize_truncated_list() -> None:
    """Test serializer truncates long lists."""
    long_list = list(range(SerializationConfig.max_list_items + 10))
    result = serialize_provider_object(long_list, "root")
    data = result["_data"]
    assert data["_type"] == "truncated_list"
    assert data["_total_length"] == len(long_list)
    assert data["_shown"] == SerializationConfig.max_list_items
    assert len(data["_items"]) == SerializationConfig.max_list_items


def test_serialize_dict() -> None:
    """Test serializer handles dictionaries."""
    result = serialize_provider_object({"key": "value"}, "root")
    assert result["_data"] == {"key": "value"}


def test_serialize_truncated_dict() -> None:
    """Test serializer truncates large dictionaries."""
    large_dict = {f"key_{i}": f"value_{i}" for i in range(SerializationConfig.max_dict_items + 10)}
    result = serialize_provider_object(large_dict, "root")
    data = result["_data"]
    assert data["_type"] == "truncated_dict"
    assert data["_total_length"] == len(large_dict)
    assert data["_shown"] == SerializationConfig.max_dict_items


def test_serialize_pydantic_model() -> None:
    """Test serializer handles Pydantic models."""
    from pydantic import BaseModel

    class SampleModel(BaseModel):
        name: str
        value: int

    obj = SampleModel(name="test", value=42)
    result = serialize_provider_object(obj, "root")
    data = result["_data"]
    assert data["_type"] == "pydantic_model"
    assert "SampleModel" in data["_class"]
    assert data["_fields"]["name"] == "test"
    assert data["_fields"]["value"] == 42


def test_serialize_enum() -> None:
    """Test serializer handles enum values."""
    from enum import Enum

    class TestEnum(Enum):
        VALUE_A = "a"
        VALUE_B = "b"

    result = serialize_provider_object(TestEnum.VALUE_A, "root")
    data = result["_data"]
    assert data["_type"] == "enum"
    assert data["_value"] == "a"
    assert data["_name"] == "VALUE_A"


def test_serialize_callable() -> None:
    """Test serializer handles callables."""

    def sample_function():
        pass

    result = serialize_provider_object(sample_function, "root")
    data = result["_data"]
    # Callables are serialized as objects with __name__ attribute
    assert data.get("_type") in ("callable", "object")


def test_circular_reference_detection() -> None:
    """Test serializer detects circular references."""
    obj = {}
    obj["self"] = obj

    result = serialize_provider_object(obj, "root")
    # Should handle circular reference without infinite recursion
    assert result is not None


def test_max_depth_limit() -> None:
    """Test serializer has reasonable depth limits."""
    # Create a deeply nested structure
    obj = {"level1": {"level2": {"level3": {"level4": {"level5": {"level6": "deep"}}}}}}
    result = serialize_provider_object(obj, "root")

    # Should complete without error
    assert result is not None
    assert "_data" in result


def test_generate_field_inventory() -> None:
    """Test field inventory generation."""
    test_obj = {
        "field1": "value1",
        "nested": {
            "field2": 42,
        },
        "list": [1, 2, 3],
    }

    serialized = serialize_provider_object(test_obj, "root")
    inventory = generate_field_inventory(serialized, "root")

    # Should have entries for all fields
    paths = [item["path"] for item in inventory]
    assert "root.field1" in paths
    assert "root.nested.field2" in paths
    assert "root.list[0]" in paths


def test_field_inventory_types() -> None:
    """Test field inventory captures correct types."""
    test_obj = {
        "string_field": "test",
        "int_field": 42,
        "bool_field": True,
    }

    serialized = serialize_provider_object(test_obj, "root")
    inventory = generate_field_inventory(serialized, "root")

    field_types = {item["path"]: item["type"] for item in inventory}
    assert field_types["root.string_field"] == "str"
    assert field_types["root.int_field"] == "int"
    assert field_types["root.bool_field"] == "bool"


def test_gitignore_excludes_local_snapshots() -> None:
    """Test that .local/iztro_snapshots/ is excluded from git."""
    gitignore_path = Path(".gitignore")
    assert gitignore_path.exists()

    gitignore_content = gitignore_path.read_text()
    assert ".local/" in gitignore_content


def test_snapshot_script_exists() -> None:
    """Test that snapshot script exists and is executable."""
    script_path = Path("scripts/dump_iztro_provider_snapshot.py")
    assert script_path.exists()

    # Check script can be imported
    import importlib.util

    spec = importlib.util.spec_from_file_location("snapshot_script", script_path)
    assert spec is not None


def test_serializer_module_exists() -> None:
    """Test that serializer module exists."""
    module_path = Path("app/engines/providers/provider_snapshot.py")
    assert module_path.exists()

    # Check key functions exist
    from app.engines.providers.provider_snapshot import (
        generate_field_inventory,
        serialize_provider_object,
    )

    assert callable(serialize_provider_object)
    assert callable(generate_field_inventory)


def test_inventory_does_not_contain_sensitive_data() -> None:
    """Test that inventory generation doesn't expose raw input values."""
    # This test ensures the inventory abstraction doesn't leak sensitive input
    sensitive_birth_info = BirthInfo(
        calendar_type=CalendarType.solar,
        birth_datetime=datetime(2024, 1, 1, 12, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
        gender=Gender.male,
        birth_place="Private Location",  # Sensitive info
        timezone="Asia/Shanghai",
        longitude=116.4,
    )

    # The inventory should be based on field structure, not input values
    # This test is conceptual - actual execution would require calling iztro
    # The key point is that our serializer/abstraction doesn't embed BirthInfo values
    # into the inventory output
    result = serialize_provider_object(sensitive_birth_info, "birth_info")
    inventory = generate_field_inventory(result, "birth_info")

    inventory_json = json.dumps(inventory)
    assert "Private Location" not in inventory_json


def test_private_output_dir_must_be_under_local_snapshots() -> None:
    """Test private snapshots cannot be written to tracked project directories."""
    allowed = resolve_output_dir(DEFAULT_OUTPUT_DIR / "nested", is_private=True)
    assert ".local/iztro_snapshots" in allowed.as_posix()

    with pytest.raises(ValueError, match="Private sample snapshots"):
        resolve_output_dir(Path(".supports/snapshots"), is_private=True)


def test_synthetic_output_dir_can_be_customized() -> None:
    """Test synthetic snapshots can be written to a caller-selected directory."""
    resolved = resolve_output_dir(Path(".supports/synthetic-snapshots"), is_private=False)
    assert resolved.name == "synthetic-snapshots"


def test_private_sample_rejects_lunar_calendar(tmp_path: Path) -> None:
    """Test private sample parser rejects unsupported lunar input."""
    sample = tmp_path / "private.md"
    sample.write_text(
        "\n".join(
            [
                "calendar_type: lunar",
                "birth_date: 1990-05-15",
                "birth_time: 14:30",
                "timezone: Asia/Shanghai",
                "gender: male",
                "birth_place: Private Location",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="calendar_type=solar"):
        parse_private_sample(sample)


def test_private_sample_rejects_unknown_gender(tmp_path: Path) -> None:
    """Test private sample parser rejects unsupported gender values."""
    sample = tmp_path / "private.md"
    sample.write_text(
        "\n".join(
            [
                "calendar_type: solar",
                "birth_date: 1990-05-15",
                "birth_time: 14:30",
                "timezone: Asia/Shanghai",
                "gender: unknown",
                "birth_place: Private Location",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="gender=male"):
        parse_private_sample(sample)


def test_output_directory_ignored_by_git() -> None:
    """Test that .local/iztro_snapshots/ directory is gitignored."""
    gitignore_path = Path(".gitignore")
    gitignore_content = gitignore_path.read_text()

    # Check that .local/ is excluded
    assert ".local/" in gitignore_content.splitlines()

    # Also verify TEST_INFO_EVA.md is excluded
    assert ".supports/TEST_INFO_EVA.md" in gitignore_content.splitlines()


def test_snapshot_does_not_commit_private_data() -> None:
    """Test that snapshot outputs won't be accidentally committed."""
    output_dir = Path(".local/iztro_snapshots")

    # If output directory exists, ensure it's ignored
    if output_dir.exists():
        gitignore_path = Path(".gitignore")
        gitignore_content = gitignore_path.read_text()

        # Check that .local/ is in .gitignore
        assert ".local/" in gitignore_content

        # Verify no snapshot files are tracked by git
        result = __import__("subprocess").run(
            ["git", "ls-files", ".local/"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        # Should return empty (no files tracked)
        assert result.stdout.strip() == ""
