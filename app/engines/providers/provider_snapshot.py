"""
Safe serializer for iztro-py provider objects.

This module provides utilities to recursively traverse and serialize
iztro-py objects for audit and inspection purposes.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel


class SerializationConfig:
    """Configuration for safe serialization."""

    max_depth = 10
    max_list_items = 100
    max_dict_items = 100
    max_string_length = 1000


class ProviderSnapshotError(Exception):
    """Base exception for provider snapshot errors."""

    pass


def _get_object_type_name(obj: Any) -> str:
    """Get the type name of an object."""
    if isinstance(obj, type):
        return f"type:{obj.__name__}"
    type_name = type(obj).__name__
    module = type(obj).__module__
    if module and module != "builtins":
        return f"{module}.{type_name}"
    return type_name


def _is_callable(obj: Any) -> bool:
    """Check if object is callable (function, method, etc.)."""
    return callable(obj) and not isinstance(obj, (type, BaseModel))


def _serialize_value(
    value: Any,
    path: str,
    depth: int,
    visited: set[int],
    config: SerializationConfig,
) -> Any:
    """
    Recursively serialize a value to a JSON-serializable format.

    Args:
        value: The value to serialize
        path: Current path in the object tree (for debugging)
        depth: Current recursion depth
        visited: Set of object ids already visited (for circular reference detection)
        config: Serialization configuration

    Returns:
        A JSON-serializable representation of the value
    """
    if depth > config.max_depth:
        return {
            "_type": "max_depth_exceeded",
            "_path": path,
            "_original_type": _get_object_type_name(value),
        }

    # Handle None
    if value is None:
        return None

    # Handle primitive types
    if isinstance(value, (str, int, float, bool)):
        if isinstance(value, str) and len(value) > config.max_string_length:
            return {
                "_type": "truncated_string",
                "_value": value[: config.max_string_length] + "...",
                "_length": len(value),
            }
        return value

    # Handle enum
    if isinstance(value, Enum):
        return {
            "_type": "enum",
            "_enum_class": _get_object_type_name(type(value)),
            "_value": value.value,
            "_name": value.name,
        }

    # Handle bytes
    if isinstance(value, bytes):
        return {
            "_type": "bytes",
            "_length": len(value),
            "_preview": value[:100].hex() if len(value) > 0 else "",
        }

    # Handle list/tuple
    if isinstance(value, (list, tuple)):
        if len(value) > config.max_list_items:
            items = value[: config.max_list_items]
            truncated = True
        else:
            items = value
            truncated = False

        result = []
        for i, item in enumerate(items):
            item_path = f"{path}[{i}]"
            try:
                result.append(_serialize_value(item, item_path, depth + 1, visited, config))
            except Exception as e:
                result.append(
                    {
                        "_type": "serialization_error",
                        "_error": str(e),
                        "_path": item_path,
                    }
                )

        if truncated:
            return {
                "_type": "truncated_list",
                "_items": result,
                "_total_length": len(value),
                "_shown": config.max_list_items,
            }
        return result

    # Handle dict
    if isinstance(value, dict):
        if len(value) > config.max_dict_items:
            items = dict(list(value.items())[: config.max_dict_items])
            truncated = True
        else:
            items = value
            truncated = False

        result = {}
        for key, val in items.items():
            key_str = str(key)
            item_path = f"{path}.{key_str}"
            try:
                result[key_str] = _serialize_value(val, item_path, depth + 1, visited, config)
            except Exception as e:
                result[key_str] = {
                    "_type": "serialization_error",
                    "_error": str(e),
                    "_path": item_path,
                }

        if truncated:
            return {
                "_type": "truncated_dict",
                "_items": result,
                "_total_length": len(value),
                "_shown": config.max_dict_items,
            }
        return result

    # Handle Pydantic models
    if isinstance(value, BaseModel):
        obj_id = id(value)
        if obj_id in visited:
            return {
                "_type": "circular_reference",
                "_path": path,
                "_class": _get_object_type_name(value),
            }
        visited.add(obj_id)

        try:
            # Get model fields
            result = {
                "_type": "pydantic_model",
                "_class": _get_object_type_name(value),
                "_fields": {},
            }

            for field_name in type(value).model_fields:
                field_path = f"{path}.{field_name}"
                field_value = getattr(value, field_name, None)
                try:
                    result["_fields"][field_name] = _serialize_value(
                        field_value, field_path, depth + 1, visited, config
                    )
                except Exception as e:
                    result["_fields"][field_name] = {
                        "_type": "field_error",
                        "_error": str(e),
                        "_path": field_path,
                    }

            return result
        finally:
            visited.remove(obj_id)

    # Handle other objects with __dict__
    if hasattr(value, "__dict__"):
        obj_id = id(value)
        if obj_id in visited:
            return {
                "_type": "circular_reference",
                "_path": path,
                "_class": _get_object_type_name(value),
            }
        visited.add(obj_id)

        try:
            result = {
                "_type": "object",
                "_class": _get_object_type_name(value),
                "_attributes": {},
            }

            for attr_name, attr_value in value.__dict__.items():
                if _is_callable(attr_value):
                    continue
                attr_path = f"{path}.{attr_name}"
                try:
                    result["_attributes"][attr_name] = _serialize_value(
                        attr_value, attr_path, depth + 1, visited, config
                    )
                except Exception as e:
                    result["_attributes"][attr_name] = {
                        "_type": "attr_error",
                        "_error": str(e),
                        "_path": attr_path,
                    }

            return result
        finally:
            visited.remove(obj_id)

    # Handle callables
    if _is_callable(value):
        return {
            "_type": "callable",
            "_class": _get_object_type_name(value),
            "_name": getattr(value, "__name__", "unknown"),
        }

    # Fallback for unknown types
    return {
        "_type": "unknown",
        "_class": _get_object_type_name(value),
        "_repr": repr(value)[:200],
    }


def serialize_provider_object(obj: Any, root_name: str = "root") -> dict:
    """
    Serialize an iztro-py provider object to a safe JSON-serializable format.

    Args:
        obj: The object to serialize (typically astrolabe, palace, or star)
        root_name: Name for the root object (for path tracking)

    Returns:
        A dictionary containing the serialized object with metadata
    """
    visited = set()
    config = SerializationConfig()

    serialized = _serialize_value(obj, root_name, 0, visited, config)

    return {
        "_snapshot_metadata": {
            "timestamp": datetime.now().isoformat(),
            "root_name": root_name,
            "root_type": _get_object_type_name(obj),
        },
        "_data": serialized,
    }


def generate_field_inventory(serialized: dict, root_path: str = "") -> list[dict]:
    """
    Generate a flat inventory of all fields from a serialized object.

    Args:
        serialized: The serialized object from serialize_provider_object
        root_path: Current path in the object tree

    Returns:
        A list of field descriptions with path, type, and sample value info
    """
    inventory = []

    def _extract_fields(data: Any, path: str, depth: int) -> None:
        if depth > 15:  # Safety limit
            return

        if data is None:
            return

        # Handle our special wrapper types
        if isinstance(data, dict):
            # Check if this is a special wrapper type
            if "_type" in data:
                dtype = data["_type"]

                # Skip error and circular reference entries
                if dtype in (
                    "serialization_error",
                    "field_error",
                    "attr_error",
                    "circular_reference",
                    "max_depth_exceeded",
                ):
                    inventory.append(
                        {
                            "path": path,
                            "type": dtype,
                            "description": data.get("_error", data.get("_path", "")),
                            "exists": True,
                        }
                    )
                    return

                # Record actual fields
                if dtype == "pydantic_model":
                    class_name = data.get("_class", "unknown")
                    inventory.append(
                        {
                            "path": path,
                            "type": f"pydantic_model:{class_name}",
                            "description": f"Pydantic model with {len(data.get('_fields', {}))} fields",
                            "exists": True,
                        }
                    )

                    for field_name, field_value in data.get("_fields", {}).items():
                        _extract_fields(field_value, f"{path}.{field_name}", depth + 1)
                    return

                if dtype == "object":
                    class_name = data.get("_class", "unknown")
                    inventory.append(
                        {
                            "path": path,
                            "type": f"object:{class_name}",
                            "description": f"Object with {len(data.get('_attributes', {}))} attributes",
                            "exists": True,
                        }
                    )

                    for attr_name, attr_value in data.get("_attributes", {}).items():
                        _extract_fields(attr_value, f"{path}.{attr_name}", depth + 1)
                    return

                # Handle enum
                if dtype == "enum":
                    inventory.append(
                        {
                            "path": path,
                            "type": f"enum:{data.get('_enum_class', '')}",
                            "description": f"Enum value: {data.get('_name')} = {data.get('_value')}",
                            "exists": True,
                            "sample_value": data.get("_value"),
                        }
                    )
                    return

                # Handle callable
                if dtype == "callable":
                    inventory.append(
                        {
                            "path": path,
                            "type": "callable",
                            "description": f"Callable: {data.get('_name', 'unknown')}",
                            "exists": True,
                        }
                    )
                    return

                # Handle truncated types
                if dtype in ("truncated_list", "truncated_dict"):
                    inventory.append(
                        {
                            "path": path,
                            "type": dtype,
                            "description": (
                                f"Truncated: showing {data.get('_shown')} of " f"{data.get('_total_length')} items"
                            ),
                            "exists": True,
                        }
                    )
                    # Still process the shown items
                    if dtype == "truncated_list":
                        for i, item in enumerate(data.get("_items", [])):
                            _extract_fields(item, f"{path}[{i}]", depth + 1)
                    else:
                        for key, val in data.get("_items", {}).items():
                            _extract_fields(val, f"{path}.{key}", depth + 1)
                    return

                # Handle unknown types
                if dtype == "unknown":
                    inventory.append(
                        {
                            "path": path,
                            "type": f"unknown:{data.get('_class', 'any')}",
                            "description": f"Could not serialize: {data.get('_repr', '')[:100]}",
                            "exists": True,
                        }
                    )
                    return

            # Regular dict - process all values
            for key, val in data.items():
                if not key.startswith("_"):  # Skip metadata keys
                    _extract_fields(val, f"{path}.{key}" if path else key, depth + 1)
            return

        # Handle lists
        if isinstance(data, list):
            for i, item in enumerate(data):
                _extract_fields(item, f"{path}[{i}]", depth + 1)
            return

        # Handle primitive values
        if isinstance(data, (str, int, float, bool)):
            item = {
                "path": path,
                "type": type(data).__name__,
                "description": "String value redacted" if isinstance(data, str) else "Primitive value",
                "exists": True,
            }
            if not isinstance(data, str):
                item["sample_value"] = data
            inventory.append(item)
            return

    # Start extraction from _data section
    root_data = serialized.get("_data", serialized)
    _extract_fields(root_data, root_path, 0)

    return inventory
