"""Tests for the Python-literal blind spot and its fix."""

from __future__ import annotations

from structstream.adversarial import ADVERSARIAL_SAMPLES, HOLDOUT_SAMPLES, SCHEMA
from structstream.corpus import SAMPLES
from structstream.repair import repair_json
from structstream.repair_v2 import repair_json_v2
from structstream.schema import matches

# --- the finding: the bundled corpus never tests Python literals -----------

def test_bundled_corpus_never_contains_python_literals():
    for _, raw in SAMPLES:
        assert "True" not in raw and "False" not in raw and "None" not in raw


def test_original_repair_fails_on_every_python_literal_sample():
    for label, raw in ADVERSARIAL_SAMPLES:
        r = repair_json(raw)
        assert not (r.ok and matches(r.value, SCHEMA)), label


# --- the fix -----------------------------------------------------------------

def test_fixed_repair_recovers_all_adversarial_samples():
    for label, raw in ADVERSARIAL_SAMPLES:
        r = repair_json_v2(raw)
        assert r.ok and matches(r.value, SCHEMA), (label, r.error)


def test_python_literals_fix_is_recorded():
    r = repair_json_v2('{"name": "Ada", "age": 36, "active": True}')
    assert "python_literals" in r.fixes_applied


def test_fix_does_not_corrupt_string_content_containing_the_words():
    """"True Detective" must stay a string, not become a boolean."""
    r = repair_json_v2('{"name": "True Detective", "age": 5, "active": False}')
    assert r.ok
    assert r.value["name"] == "True Detective"
    assert r.value["active"] is False


def test_fix_handles_none_inside_nested_object():
    r = repair_json_v2('{"a": {"b": None}}')
    assert r.ok
    assert r.value == {"a": {"b": None}}


# --- v2 does not regress the original corpus --------------------------------

def test_v2_still_recovers_the_original_corpus():
    recovered = sum(
        1 for _, raw in SAMPLES
        if (r := repair_json_v2(raw)).ok and matches(r.value, {
            "type": "object",
            "required": ["name", "age", "active"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "active": {"type": "boolean"},
            },
        })
    )
    assert recovered == len(SAMPLES)


# --- held out, evaluated once ------------------------------------------------

def test_holdout_is_disjoint_from_the_tuning_corpus():
    adv_texts = {raw for _, raw in ADVERSARIAL_SAMPLES}
    holdout_texts = {raw for _, raw in HOLDOUT_SAMPLES}
    assert not (adv_texts & holdout_texts)


def test_holdout_fully_recovers_with_the_fix():
    for label, raw in HOLDOUT_SAMPLES:
        r = repair_json_v2(raw)
        assert r.ok and matches(r.value, SCHEMA), (label, r.error)


def test_holdout_still_fails_without_the_fix():
    recovered = sum(
        1 for _, raw in HOLDOUT_SAMPLES
        if (r := repair_json(raw)).ok and matches(r.value, SCHEMA)
    )
    assert recovered == 0


# --- the original module is untouched ---------------------------------------

def test_original_repair_module_untouched():
    import structstream.repair as repair_module

    assert not hasattr(repair_module, "repair_json_v2")


def test_original_benchmark_still_reproduces():
    from structstream.corpus import SCHEMA as ORIGINAL_SCHEMA

    recovered = sum(
        1 for _, raw in SAMPLES
        if (r := repair_json(raw)).ok and matches(r.value, ORIGINAL_SCHEMA)
    )
    assert recovered == len(SAMPLES) == 15


# --- the full report ---------------------------------------------------------

def test_report_is_reproducible():
    from structstream.eval_v2 import build_report

    assert build_report() == build_report()
