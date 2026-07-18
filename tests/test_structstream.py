import pytest

from structstream.corpus import SAMPLES, SCHEMA
from structstream.repair import repair_json
from structstream.schema import SchemaError, matches, validate


def test_valid_passes_through():
    r = repair_json('{"a": 1}')
    assert r.ok and r.value == {"a": 1}
    assert r.fixes_applied == []


def test_strips_code_fence():
    r = repair_json('```json\n{"a": 1}\n```')
    assert r.ok and r.value == {"a": 1}
    assert "stripped_code_fence" in r.fixes_applied


def test_removes_trailing_comma():
    r = repair_json('{"a": 1, "b": 2,}')
    assert r.ok and r.value == {"a": 1, "b": 2}


def test_fixes_single_quotes():
    r = repair_json("{'a': 'hello'}")
    assert r.ok and r.value == {"a": "hello"}


def test_quotes_bare_keys():
    r = repair_json('{a: 1, b: 2}')
    assert r.ok and r.value == {"a": 1, "b": 2}


def test_closes_unclosed_object():
    r = repair_json('{"a": 1, "b": 2')
    assert r.ok and r.value == {"a": 1, "b": 2}


def test_strips_prose_around_json():
    r = repair_json('Here you go:\n{"a": 1}\nHope that helps!')
    assert r.ok and r.value == {"a": 1}


def test_everything_at_once():
    r = repair_json("Sure:\n```json\n{name: 'Ada', age: 36, active: true,}\n```")
    assert r.ok
    assert r.value == {"name": "Ada", "age": 36, "active": True}


def test_unrepairable_returns_error():
    r = repair_json("this is not json at all, just a sentence")
    assert not r.ok
    assert r.error


# ---- schema validation ----

def test_schema_accepts_valid():
    assert matches({"name": "Ada", "age": 36, "active": True}, SCHEMA)


def test_schema_rejects_missing_key():
    assert not matches({"name": "Ada", "age": 36}, SCHEMA)


def test_schema_rejects_wrong_type():
    assert not matches({"name": "Ada", "age": "thirty", "active": True}, SCHEMA)


def test_schema_rejects_boolean_as_integer():
    with pytest.raises(SchemaError):
        validate(True, {"type": "integer"})


def test_schema_validates_nested_array():
    schema = {"type": "array", "items": {"type": "integer"}}
    assert matches([1, 2, 3], schema)
    assert not matches([1, "two", 3], schema)


# ---- corpus-level guarantee ----

def test_repair_recovers_most_of_corpus():
    recovered = sum(
        1 for _, raw in SAMPLES
        if (r := repair_json(raw)).ok and matches(r.value, SCHEMA)
    )
    assert recovered / len(SAMPLES) >= 0.9
