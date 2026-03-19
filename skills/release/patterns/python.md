# Pre-flight Pattern: python

**Summary for Phase 0 announcement:** lint (ruff) and tests (pytest).

## Steps

Detect whether the project uses `uv`:

```bash
if [ -f uv.lock ]; then
  uv run ruff check . 2>&1
  uv run pytest 2>&1
else
  python -m ruff check . 2>&1
  python -m pytest 2>&1
fi
```

If `ruff` is not installed/configured, skip lint and note it.
If no test files are found, skip pytest and note it.

## On Failure

Use AskUserQuestion:
- "Lint/tests failed. How do you want to proceed?"
- Options: "Fix first (cancel release)", "Skip pre-flight and continue"

Show the failing output before asking.

## On Pass

State: "Python lint and tests passed." and continue to Phase 2.
