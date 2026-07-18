"""Sixty-second tour of structstream.

    python examples/quickstart.py
"""
from structstream.repair import repair_json
from structstream.schema import matches

schema = {
    "type": "object",
    "required": ["name", "age"],
    "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
}

# The kind of thing a model actually returns when you ask for JSON.
messy = "Sure! Here you go:\n```json\n{name: 'Ada', age: 36,}\n```"

result = repair_json(messy)
print(f"ok           : {result.ok}")
print(f"value        : {result.value}")
print(f"fixes        : {result.fixes_applied}")
print(f"matches schema: {matches(result.value, schema)}")
