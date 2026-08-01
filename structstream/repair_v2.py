"""``repair_json`` with one more fix: Python-literal booleans and null.

The bundled 15-sample corpus in :mod:`structstream.corpus` never once
contains ``True``, ``False``, or ``None`` in place of JSON's ``true``,
``false``, ``null``, so the "100% recovery" headline never had to face it.
It is one of the most common real failure modes: a model that has seen
far more Python dict literals than JSON objects in training drifts into
Python syntax, especially for booleans and null, even while getting
everything else about the JSON right. The original ``repair_json`` has no
fix for it at all:

    >>> from structstream.repair import repair_json
    >>> repair_json('{"active": True, "name": "Ada"}').ok
    False

``repair_json_v2`` adds ``_fix_python_literals``, which walks the text
tracking whether it's inside a double-quoted string (the same technique
``_close_unbalanced`` already uses) and only replaces whole-word ``True``/
``False``/``None`` outside of strings, so a legitimate string value like
``"True Detective"`` is left untouched.
"""
from __future__ import annotations

import json
import re

from .repair import (
    RepairResult,
    _close_unbalanced,
    _extract_json_span,
    _quote_bare_keys,
    _quote_fixes,
    _remove_trailing_commas,
    _strip_code_fences,
)

_TRUE = re.compile(r"True\b")
_FALSE = re.compile(r"False\b")
_NONE = re.compile(r"None\b")


def _fix_python_literals(text: str, fixes: list[str]) -> str:
    out: list[str] = []
    in_string = False
    escape = False
    i, n = 0, len(text)
    changed = False
    while i < n:
        ch = text[i]
        if in_string:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue
        for pattern, replacement in ((_TRUE, "true"), (_FALSE, "false"), (_NONE, "null")):
            m = pattern.match(text, i)
            if m:
                out.append(replacement)
                changed = True
                i = m.end()
                break
        else:
            out.append(ch)
            i += 1
    if changed:
        fixes.append("python_literals")
    return "".join(out)


def repair_json_v2(text: str) -> RepairResult:
    fixes: list[str] = []

    try:
        return RepairResult(ok=True, value=json.loads(text), repaired_text=text)
    except (json.JSONDecodeError, TypeError):
        pass

    if not isinstance(text, str):
        return RepairResult(ok=False, error="input is not a string")

    candidate = text
    candidate = _strip_code_fences(candidate, fixes)
    candidate = _extract_json_span(candidate, fixes)
    candidate = _quote_bare_keys(candidate, fixes)
    candidate = _quote_fixes(candidate, fixes)
    candidate = _fix_python_literals(candidate, fixes)
    candidate = _remove_trailing_commas(candidate, fixes)
    candidate = _close_unbalanced(candidate, fixes)

    try:
        value = json.loads(candidate)
        return RepairResult(ok=True, value=value, repaired_text=candidate, fixes_applied=fixes)
    except json.JSONDecodeError as e:
        return RepairResult(ok=False, repaired_text=candidate, fixes_applied=fixes, error=str(e))
