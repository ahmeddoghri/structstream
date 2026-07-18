"""Repair the near-miss JSON failures that models produce constantly.

Every fix here targets a specific, common failure mode. The order matters: we
strip wrappers first, then fix structural punctuation, then close anything left
open. Each step is conservative, so text that is already valid passes through
untouched.

This is a pragmatic repairer, not a full grammar. It handles the failures that
show up in real model output. It is not trying to parse adversarial garbage.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field


@dataclass
class RepairResult:
    ok: bool
    value: object = None
    repaired_text: str = ""
    fixes_applied: list[str] = field(default_factory=list)
    error: str = ""


def _strip_code_fences(text: str, fixes: list[str]) -> str:
    # ```json ... ``` or ``` ... ```
    fenced = re.match(r"\s*```(?:json)?\s*(.*?)\s*```\s*$", text, re.DOTALL)
    if fenced:
        fixes.append("stripped_code_fence")
        return fenced.group(1)
    return text


def _extract_json_span(text: str, fixes: list[str]) -> str:
    """Grab the outermost {...} or [...] and drop prose around it.

    Models love to say "Here is your JSON:" before the object and "Let me know
    if you need anything else!" after it.
    """
    start = min(
        [i for i in (text.find("{"), text.find("[")) if i != -1],
        default=-1,
    )
    if start == -1:
        return text
    # find matching close by scanning from the end for the last } or ]
    end = max(text.rfind("}"), text.rfind("]"))
    if end <= start:
        return text
    span = text[start : end + 1]
    if span != text.strip():
        fixes.append("extracted_json_span")
    return span


def _remove_trailing_commas(text: str, fixes: list[str]) -> str:
    fixed = re.sub(r",(\s*[}\]])", r"\1", text)
    if fixed != text:
        fixes.append("removed_trailing_comma")
    return fixed


def _quote_fixes(text: str, fixes: list[str]) -> str:
    # single-quoted strings -> double-quoted (common when models mimic Python)
    before = text
    # only convert 'quotes' that look like JSON string boundaries
    text = re.sub(r"(?<=[:\[,{\s])'([^']*)'", r'"\1"', text)
    if text != before:
        fixes.append("single_to_double_quotes")
    return text


def _quote_bare_keys(text: str, fixes: list[str]) -> str:
    before = text
    text = re.sub(r'([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*:)', r'\1"\2"\3', text)
    if text != before:
        fixes.append("quoted_bare_keys")
    return text


def _close_unbalanced(text: str, fixes: list[str]) -> str:
    """Close brackets/braces the model left open because it ran out of tokens."""
    stack = []
    in_string = False
    escape = False
    for ch in text:
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch in "{[":
            stack.append(ch)
        elif ch in "}]":
            if stack:
                stack.pop()
    if in_string:
        text += '"'
        fixes.append("closed_open_string")
    if stack:
        closers = {"{": "}", "[": "]"}
        text += "".join(closers[c] for c in reversed(stack))
        fixes.append("closed_open_brackets")
    return text


def repair_json(text: str) -> RepairResult:
    """Try to turn near-miss model output into a parsed JSON value.

    Returns a RepairResult with the parsed value and the list of fixes applied,
    or ok=False and an error if it could not be salvaged.
    """
    fixes: list[str] = []

    # fast path: already valid
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
    candidate = _remove_trailing_commas(candidate, fixes)
    candidate = _close_unbalanced(candidate, fixes)

    try:
        value = json.loads(candidate)
        return RepairResult(ok=True, value=value, repaired_text=candidate, fixes_applied=fixes)
    except json.JSONDecodeError as e:
        return RepairResult(ok=False, repaired_text=candidate, fixes_applied=fixes,
                            error=str(e))
