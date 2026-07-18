"""A tiny JSON-schema validator: does the parsed value match what you asked for?

Repairing JSON gets you a value. It does not get you the *right* value. A model
can return perfectly valid JSON that has the wrong keys or the wrong types, and
your code downstream still breaks. So structstream validates the parsed result
against a compact schema and tells you exactly what is wrong.

This supports the common subset: object with typed properties and required keys,
arrays with a typed item, and the scalar types. It is intentionally small and
readable, not a full JSON Schema implementation.
"""
from __future__ import annotations


class SchemaError(Exception):
    pass


_TYPES = {
    "string": str,
    "number": (int, float),
    "integer": int,
    "boolean": bool,
    "object": dict,
    "array": list,
}


def validate(value: object, schema: dict, path: str = "$") -> None:
    """Raise SchemaError if ``value`` does not match ``schema``. Return None if ok."""
    t = schema.get("type")
    if t is None:
        return

    expected = _TYPES.get(t)
    if expected is None:
        raise SchemaError(f"{path}: unknown schema type {t!r}")

    # bool is a subclass of int in Python; keep them distinct here
    if t in ("number", "integer") and isinstance(value, bool):
        raise SchemaError(f"{path}: expected {t}, got boolean")
    if not isinstance(value, expected):
        raise SchemaError(f"{path}: expected {t}, got {type(value).__name__}")

    if t == "object":
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                raise SchemaError(f"{path}: missing required key {key!r}")
        for key, subschema in props.items():
            if key in value:
                validate(value[key], subschema, f"{path}.{key}")

    if t == "array":
        item_schema = schema.get("items")
        if item_schema is not None:
            for i, item in enumerate(value):
                validate(item, item_schema, f"{path}[{i}]")


def matches(value: object, schema: dict) -> bool:
    try:
        validate(value, schema)
        return True
    except SchemaError:
        return False
