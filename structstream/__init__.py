"""structstream: get valid JSON out of a model that keeps almost getting it right.

You ask for JSON. The model gives you JSON with a trailing comma, a stray
```json fence, a single quote where a double should be, or it just stops
mid-object because it ran out of tokens. Your parser throws, your pipeline dies,
and you retry the whole expensive call.

There are two honest ways to fix this. Constrain the decoding so only valid
tokens are ever emitted (the grammar-constrained approach, like the ideas behind
Outlines and llguidance), or repair the almost-valid output after the fact. This
package does both: a repair pass that fixes the common near-miss failures, and a
schema validator that tells you whether what you got actually matches what you
asked for. It ships a benchmark of realistic malformed outputs so you can see
how much repair actually buys you.
"""
from structstream.repair import RepairResult, repair_json
from structstream.schema import SchemaError, validate

__all__ = ["repair_json", "RepairResult", "validate", "SchemaError"]

__version__ = "0.1.0"
