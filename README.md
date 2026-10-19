# structstream

**Get valid JSON out of a model that keeps almost getting it right.**

[![tests](https://github.com/ahmeddoghri/structstream/actions/workflows/tests.yml/badge.svg)](https://github.com/ahmeddoghri/structstream/actions/workflows/tests.yml)
![python](https://img.shields.io/badge/python-3.9%2B-blue)
![deps](https://img.shields.io/badge/runtime%20deps-none-success)
![license](https://img.shields.io/badge/license-MIT-black)
[![case study](https://img.shields.io/badge/case%20study-adoghri.com-e0703e)](https://adoghri.com/project-17.html)

![structstream](docs/cover.jpg)

> **Raw `json.loads` parses 7% of realistic malformed model output. One repair
> pass recovers 100%, and checks it matches your schema.** No retries, no
> dependencies: `python -m structstream.eval`.
>
> **Update:** that "100%" never had to face one of the most common real
> failure modes, a model emitting Python's `True`/`False`/`None` instead of
> JSON's `true`/`false`/`null`. None of the 15 bundled samples contain it.
> Against samples that do, the original repairer recovers **0%**.
> Fixed: `python -m structstream.eval_v2`.

You asked for JSON. The model gave you JSON wrapped in a ```json fence, with a
trailing comma, using single quotes, preceded by "Sure, here you go!" like a
customer service rep, and cut off mid-string because it hit the token limit
mid-thought. Your parser throws. Your pipeline dies. You retry the whole
expensive call and pray to a distribution you don't control.

There are two honest ways out. Constrain the decoding so only valid tokens are
ever emitted (the grammar approach behind tools like Outlines), or repair the
almost-valid output after the fact, which is cheaper and doesn't require
rearchitecting your inference stack. structstream does the second, plus the
part everyone conveniently forgets: it validates the repaired value against
your schema, because valid-but-wrong JSON breaks your code exactly as hard
as invalid JSON does, just with more confidence on the way down.

Pure stdlib. No model, no network, no dependencies, no eval() anywhere near
it. Every repair is a few lines you can actually read.

---

## The result in one command

```bash
python -m structstream.eval
```
```
json repair benchmark: 15 realistic malformed model outputs

  raw json.loads         1/15 = 7% parse
  structstream repair    15/15 = 100% parse AND match schema

  recovered by repair    14 outputs that would have crashed your pipeline
```

Every one of those 15 is a failure a real model actually produces, not a
synthetic edge case I invented to pad the number. The single one raw
`json.loads` handles is the already-valid case, the model having one good
day. The other 14 are the daily-driver failures: code fences, trailing
commas, single quotes, prose around the object, truncation. structstream
turns all of them back into usable data, and confirms each result has the
right keys and types before it hands them back, instead of celebrating too
early.

## Install

```bash
git clone https://github.com/ahmeddoghri/structstream
cd structstream && pip install -e .
python examples/quickstart.py
```

## Use it

```python
from structstream.repair import repair_json
from structstream.schema import matches

schema = {
    "type": "object",
    "required": ["name", "age"],
    "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
}

messy = "Here you go:\n```json\n{name: 'Ada', age: 36,}\n```"

result = repair_json(messy)
print(result.ok)              # True
print(result.value)           # {"name": "Ada", "age": 36}
print(result.fixes_applied)   # what it had to fix, so nothing is a black box
print(matches(result.value, schema))   # True: right shape, not just valid JSON
```

## What it fixes

Each repair targets a specific, common failure, applied in a safe order. Text
that is already valid passes straight through untouched.

| Fix | Handles |
|---|---|
| `stripped_code_fence` | ` ```json ... ``` ` and bare ` ``` ` wrappers |
| `extracted_json_span` | "Here is your JSON:" and other prose around the object |
| `quoted_bare_keys` | `{name: 1}` to `{"name": 1}` |
| `single_to_double_quotes` | `{'a': 'b'}` to `{"a": "b"}` |
| `removed_trailing_comma` | `[1, 2, 3,]` and `{"a": 1,}` |
| `closed_open_brackets` | objects and arrays cut off at the token limit |
| `closed_open_string` | a string the model never closed |

## The corpus never tested the failure that matters most

I checked what the bundled 15-sample corpus actually covers. Code fences,
prose, trailing commas, single quotes, truncation, all real. Not one
sample contains a Python-literal `True`, `False`, or `None` in place of
JSON's `true`, `false`, `null`. That's not a rare edge case, it's one of
the most common real failures: a model trained on far more Python dict
literals than JSON objects drifts into Python syntax, often while getting
everything else about the structure exactly right.

```python
from structstream.repair import repair_json
repair_json('{"name": "Ada", "age": 36, "active": True}').ok   # False
```

```bash
python -m structstream.eval_v2
```
```
corpus / version           recovered      rate
adversarial / v1              0/8            0%
adversarial / v2              8/8          100%

holdout / v1                  0/5            0%
holdout / v2                  5/5          100%
```

`structstream/repair_v2.py` adds `_fix_python_literals`, which walks the
text tracking whether it's inside a double-quoted string (the same
technique `_close_unbalanced` already uses) and only replaces whole-word
`True`/`False`/`None` outside of strings, so a legitimate value like
`"True Detective"` stays a string instead of becoming a boolean. 0% to
100% on 8 adversarial samples and a 5-sample holdout evaluated exactly
once. `repair.py` is untouched, so `repair_json` keeps its exact published
15/15 number; `repair_json_v2` is opt-in.

## Why the schema check matters

Repairing to valid JSON is only half the job. A model can hand you flawless JSON
with the wrong keys or a string where you needed a number, and your code
downstream breaks exactly the same way. The bundled validator supports the
common subset (typed object properties, required keys, typed arrays, scalars),
so `repair_json` plus `matches` gives you a value that is both parseable and the
right shape. The benchmark only counts a sample as recovered if it clears both
bars.

## Tests

```bash
pip install pytest && pytest -q      # 28 passing
```

## License

MIT © Ahmed Doghri
