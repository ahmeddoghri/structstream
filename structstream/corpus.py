"""Realistic malformed JSON, the kind models actually emit.

Every entry here is a failure I have seen come out of a real model when asked for
JSON. They are grouped by failure mode so the benchmark can report which repairs
matter most. The target schema is a simple object so we can also check that the
repaired value is not just valid JSON but the *right shape*.
"""
from __future__ import annotations

# The schema every sample is supposed to conform to.
SCHEMA = {
    "type": "object",
    "required": ["name", "age", "active"],
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "active": {"type": "boolean"},
    },
}

# (label, raw_model_output). All are meant to become {"name": ..., "age": ..., "active": ...}
SAMPLES: list[tuple[str, str]] = [
    ("already_valid", '{"name": "Ada", "age": 36, "active": true}'),
    ("code_fence", '```json\n{"name": "Ada", "age": 36, "active": true}\n```'),
    ("bare_fence", '```\n{"name": "Ada", "age": 36, "active": true}\n```'),
    ("prose_prefix", 'Here is the JSON you asked for:\n{"name": "Ada", "age": 36, "active": true}'),
    ("prose_suffix", '{"name": "Ada", "age": 36, "active": true}\nLet me know if you need anything else!'),
    ("trailing_comma", '{"name": "Ada", "age": 36, "active": true,}'),
    ("trailing_comma_nested", '{"name": "Ada", "age": 36, "active": true, "tags": [1, 2, 3,]}'),
    ("single_quotes", "{'name': 'Ada', 'age': 36, 'active': true}"),
    ("bare_keys", '{name: "Ada", age: 36, active: true}'),
    ("unclosed_object", '{"name": "Ada", "age": 36, "active": true'),
    ("unclosed_string", '{"name": "Ada", "age": 36, "active": true, "note": "in progre'),
    ("fence_and_prose", 'Sure!\n```json\n{"name": "Ada", "age": 36, "active": true}\n```\nHope that helps.'),
    ("fence_and_trailing_comma", '```json\n{"name": "Ada", "age": 36, "active": true,}\n```'),
    ("bare_keys_and_single_quotes", "{name: 'Ada', age: 36, active: true}"),
    ("everything_at_once", "Here you go:\n```json\n{name: 'Ada', age: 36, active: true,}\n```"),
]
