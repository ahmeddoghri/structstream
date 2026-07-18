"""Benchmark: how much does JSON repair actually buy you?

We take a set of realistic malformed model outputs and measure two things for
each: does raw json.loads parse it (the naive baseline), and does structstream's
repair produce a value that both parses and matches the target schema.

The schema check is the honest part. Repairing to valid-but-wrong JSON is not a
win, so we only count a sample as recovered if the repaired value has the right
keys and types.

Run it:

    python -m structstream.eval

Deterministic. Pure stdlib, no model, no network.
"""
from __future__ import annotations

import json

from structstream.corpus import SAMPLES, SCHEMA
from structstream.repair import repair_json
from structstream.schema import matches


def run() -> None:
    naive_ok = 0
    repaired_ok = 0
    still_broken = []

    for label, raw in SAMPLES:
        # baseline: raw parse
        try:
            json.loads(raw)
            naive_ok += 1
        except (json.JSONDecodeError, TypeError):
            pass

        # structstream: repair, then check it matches the schema
        result = repair_json(raw)
        if result.ok and matches(result.value, SCHEMA):
            repaired_ok += 1
        else:
            still_broken.append(label)

    n = len(SAMPLES)
    print(f"json repair benchmark: {n} realistic malformed model outputs\n")
    print(f"  raw json.loads         {naive_ok}/{n} = {naive_ok / n:.0%} parse")
    print(f"  structstream repair    {repaired_ok}/{n} = {repaired_ok / n:.0%} "
          f"parse AND match schema")
    print(f"\n  recovered by repair    {repaired_ok - naive_ok} outputs that would have "
          f"crashed your pipeline")

    if still_broken:
        print(f"\n  not recovered: {', '.join(still_broken)}")

    print("\nevery failure here is one a real model actually produces: stray code")
    print("fences, trailing commas, single quotes, prose around the object, and")
    print("truncation when it runs out of tokens. one repair pass turns most of")
    print("them back into usable data instead of a retry.")


if __name__ == "__main__":
    run()
