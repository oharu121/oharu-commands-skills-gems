# Validation Pattern: monorepo

**Summary for Phase 0 announcement:** per-package validation for each changed package.

## Steps

### 1. Identify changed packages

```bash
git diff --name-only HEAD
git status --short
```

Group changed files by their top-level package directory (e.g. `packages/api/`, `apps/web/`).

### 2. Run full validation suite per changed package

For each changed package directory, detect its type and run the matching pattern:

| Package signal | Pattern to follow |
|----------------|------------------|
| `package.json` present | npm pattern |
| `pyproject.toml` or `uv.lock` present | python pattern |
| `skills/` directory present | skills-gems pattern |

Read and follow the appropriate `SKILLS_DIR/patterns/<type>.md` for each package.

### 3. Report results

Report pass/fail per package before continuing. Example:

```
Validation results:
  packages/api      → npm lint ✓, tests ✓
  packages/worker   → python ruff ✓, pytest ✓
  skills/my-skill   → audit ✓
```

## On Any Failure

Use AskUserQuestion:
- "Validation failed in \<package\>. How do you want to proceed?"
- Options: "Fix first (cancel release)", "Skip failed package and continue", "Skip all validation"

## On Full Pass

State: "All package validations passed." and continue to Phase 2.
