"""Malformed JSON featuring a failure the bundled corpus never once tests.

None of :mod:`structstream.corpus`'s 15 samples contain a Python-literal
``True``, ``False``, or ``None`` in place of JSON's ``true``/``false``/
``null``, even though it's one of the most common real failure modes: a
model trained heavily on Python code drifts into Python dict syntax,
especially for booleans and null, sometimes while getting every other part
of the JSON right. Against the original ``repair_json`` (no fix for this at
all), recovery drops off a cliff the moment a sample includes it.
"""
from __future__ import annotations

from .corpus import SCHEMA

# (label, raw_model_output). All are meant to become
# {"name": ..., "age": ..., "active": ...}, matching corpus.SCHEMA.
ADVERSARIAL_SAMPLES: list[tuple[str, str]] = [
    ("python_bool_true", '{"name": "Ada", "age": 36, "active": True}'),
    ("python_bool_false_and_none",
     '{"name": "Ada", "age": 36, "active": False, "note": None}'),
    ("python_dict_literal",
     "{'name': 'Ada', 'age': 36, 'active': True}"),
    ("python_literals_and_bare_keys",
     "{name: 'Ada', age: 36, active: True}"),
    ("python_literals_and_code_fence",
     '```json\n{"name": "Ada", "age": 36, "active": True}\n```'),
    ("python_literals_and_trailing_comma",
     '{"name": "Ada", "age": 36, "active": True,}'),
    ("python_literals_and_truncation",
     '{"name": "Ada", "age": 36, "active": True'),
    ("everything_at_once_python",
     "Here you go:\n```json\n{name: 'Ada', age: 36, active: True,}\n```"),
]

# Written after repair_v2's Python-literal fix was frozen against
# ADVERSARIAL_SAMPLES above. Evaluated exactly once.
HOLDOUT_SAMPLES: list[tuple[str, str]] = [
    ("holdout_none_only", '{"name": "Ada", "age": 36, "active": true, "manager": None}'),
    ("holdout_false_bare_key",
     "{name: 'Ada', age: 36, active: False}"),
    ("holdout_mixed_case_string",
     '{"name": "True Grit", "age": 36, "active": True}'),
    ("holdout_nested_python",
     '{"name": "Ada", "age": 36, "active": True, "meta": {"verified": None}}'),
    ("holdout_prose_and_python",
     'Sure, here it is:\n{"name": "Ada", "age": 36, "active": False}\nEnjoy!'),
]

__all__ = ["ADVERSARIAL_SAMPLES", "HOLDOUT_SAMPLES", "SCHEMA"]
