"""Does repair handle a failure the bundled benchmark never tests?

None of ``corpus.SAMPLES`` contains a Python-literal ``True``/``False``/
``None`` in place of JSON's ``true``/``false``/``null``, so the published
"100% recovery" number never had to face one of the most common real
failure modes. This module reruns the same recovery measurement against
:mod:`structstream.adversarial`'s samples, for both the original
``repair_json`` and the fixed ``repair_json_v2``.

    python -m structstream.eval_v2
"""
from __future__ import annotations

import argparse
import json
from typing import Callable, Dict, List, Sequence

from .adversarial import ADVERSARIAL_SAMPLES, HOLDOUT_SAMPLES, SCHEMA
from .repair import repair_json
from .repair_v2 import repair_json_v2
from .schema import matches


def _score(repair_fn: Callable, samples: Sequence[tuple]) -> Dict:
    recovered = 0
    misses: List[str] = []
    for label, raw in samples:
        result = repair_fn(raw)
        if result.ok and matches(result.value, SCHEMA):
            recovered += 1
        else:
            misses.append(label)
    return {
        "recovered": recovered,
        "n": len(samples),
        "rate": round(recovered / len(samples), 4),
        "misses": misses,
    }


def build_report() -> Dict:
    return {
        "adversarial": {
            "v1": _score(repair_json, ADVERSARIAL_SAMPLES),
            "v2": _score(repair_json_v2, ADVERSARIAL_SAMPLES),
        },
        "holdout": {
            "v1": _score(repair_json, HOLDOUT_SAMPLES),
            "v2": _score(repair_json_v2, HOLDOUT_SAMPLES),
        },
    }


def format_report(report: Dict) -> str:
    lines = [
        "recovery rate on samples using Python-literal True/False/None",
        "=" * 66,
        f"{'corpus / version':<22}{'recovered':>14}{'rate':>10}",
        "-" * 66,
    ]
    for corpus_name in ("adversarial", "holdout"):
        for v in ("v1", "v2"):
            row = report[corpus_name][v]
            lines.append(
                f"{corpus_name + ' / ' + v:<22}{row['recovered']:>8}/{row['n']:<5}{row['rate']:>10.0%}"
            )
        lines.append("")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", default=None)
    args = parser.parse_args(argv)

    report = build_report()
    print(format_report(report))

    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
            handle.write("\n")
        print(f"\nWrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
