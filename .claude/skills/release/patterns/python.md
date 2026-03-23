# Validation Pattern: python

**Summary for Phase 0 announcement:** lint (ruff), type check (pyright), and tests (pytest).

## Steps

Detect whether the project uses `uv` and set the runner prefix:

```bash
if [ -f uv.lock ]; then
  RUNNER="uv run"
else
  RUNNER=""
fi
```

Then run the full validation suite:

```bash
$RUNNER ruff check . 2>&1
$RUNNER pyright . 2>&1
$RUNNER pytest 2>&1
```

If `ruff` is not installed/configured, skip lint and note it.
If `pyright` is not installed/configured, skip type check and note it.
If no test files are found, skip pytest and note it.

## On Failure

Use AskUserQuestion:
- "Lint/type check/tests failed. How do you want to proceed?"
- Options: "Fix first (cancel release)", "Skip validation and continue"

Show the failing output before asking.

## On Pass

State: "Python lint, type check, and tests passed." and continue to Phase 2.
