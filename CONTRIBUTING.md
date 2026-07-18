# Contributing

Thanks for taking a look. New real-world failure modes are especially welcome.

## Development setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

## Before opening a pull request

- Keep changes focused. One logical change per PR, not a drive-by rewrite.
- Add or update tests for any behaviour you change. CI runs `pytest` on
  Python 3.9, 3.11, and 3.13, plus the example and benchmark, so it will
  find you.
- Run `ruff check .` and `pytest -q` locally before you push.
- Saw a malformed output this does not fix? Add it to `structstream/corpus.py`
  with a descriptive label, add the repair step to `structstream/repair.py`, and
  make sure the whole corpus still recovers. Keep repairs conservative: valid
  JSON must always pass through untouched.

## Reporting bugs

Open an issue with a minimal reproduction, the expected versus actual result,
and your Python version. For security issues see [SECURITY.md](SECURITY.md).
