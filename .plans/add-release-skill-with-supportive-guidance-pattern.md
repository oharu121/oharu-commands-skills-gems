# Plan: Add release skill with supportive guidance pattern

**Status:** Completed
**Date:** 2026-03-19

## Context

The `/release` command started as a single monolithic markdown file (`commands/release.md`)
with all logic hardcoded for one specific repo type — DevelopersIO article writing with
Contentful. As new skills were added to the repo, it became clear that different projects
need different pre-flight steps: a skills-gems repo needs a sensitive data audit, an npm
project needs lint and test, a Python project needs ruff and pytest. There was no clean
way to extend the single file without it growing into an unmaintainable blob.

Two approaches were considered: fully adaptive (Claude silently detects and decides) and
multiple per-repo commands. The adaptive approach was unpredictable — you couldn't tell
what it skipped or why. The multiple-commands approach meant maintaining near-identical
files that diverge over time. A third option emerged: a single skill with explicit
detection, user confirmation via `AskUserQuestion` before any pre-flight runs, and
pattern files loaded on demand per detected mode.

## Approach

The skill is structured as a router: `SKILL.md` handles detection and universal phases,
while `patterns/<mode>.md` files contain the mode-specific pre-flight logic. Claude reads
only the relevant pattern file at runtime — not all of them — keeping context lean.
`templates/` holds the plan and issue-body formats so they can be updated independently
from orchestration logic.

The "supportive guidance" constraint — every user interaction through `AskUserQuestion`,
never plain text prompts — was added to keep the UX interactive and consistent. Phase 0
announces the detected mode and proposed pre-flight steps, and the user confirms or
overrides before anything runs. This makes the detection transparent and correctable.

## Changes

### 1. skills/release/SKILL.md — router and universal phases
Phase 0 detects repo mode from filesystem signals (`package.json`, `pyproject.toml`,
`uv.lock`, `skills/`). Announces via `AskUserQuestion` with proceed / skip / override
options. Phase 1 delegates to `SKILLS_DIR/patterns/<mode>.md`. Phases 2–3 handle the
universal issue creation, commit, tag, push, and GitHub release flow unchanged from
the previous version, but all user interactions are explicitly annotated as
`AskUserQuestion` calls.

### 2. skills/release/patterns/skills-gems.md
Runs three targeted greps against changed `skills/` files: 12-digit account IDs
(`\b\d{12}\b`), hardcoded `s3://` URIs (filtered for placeholders), and real ARNs
(`arn:aws:iam::\d{12}:`). Lists approved placeholder values for each finding type.
Blocks progression to Phase 2 until clean.

### 3. skills/release/patterns/npm.md
Runs `npm run lint` then `npm test`. On failure, uses `AskUserQuestion` to offer
"fix first" or "skip pre-flight" — does not silently continue.

### 4. skills/release/patterns/python.md
Detects `uv.lock` to decide between `uv run ruff`/`uv run pytest` vs direct
`python -m` invocations. Same failure handling pattern as npm.

### 5. skills/release/patterns/monorepo.md
Identifies changed package directories from `git diff --name-only`, then dispatches
to the appropriate pattern file per package. Reports pass/fail per package before
asking how to proceed on any failure.

### 6. skills/release/templates/plan.md and issue-body.md
Extracted from inline instructions in the old monolithic command into standalone
files. Plan template includes narrative rules (Context/Approach are stories, not
bullets; Verification must be runnable). Issue body template includes AC format and
Verify field guidelines (`auto — <cmd>`, `auto`, `manual`).

### 7. commands/release.md and .claude/commands/release.md — thin wrappers
Both reduced to 3 lines: load and follow `SKILLS_DIR/SKILL.md`. The public
`commands/release.md` was subsequently removed as redundant — the skill in
`skills/release/` is the distributable artifact; the internal
`.claude/commands/release.md` is the installed entry point.

## Files Modified

| File | Change |
|------|--------|
| [skills/release/SKILL.md](skills/release/SKILL.md) | **New** — router with Phase 0 detection and universal Phases 2–3 |
| [skills/release/patterns/skills-gems.md](skills/release/patterns/skills-gems.md) | **New** — sensitive data audit pattern |
| [skills/release/patterns/npm.md](skills/release/patterns/npm.md) | **New** — npm lint + test pattern |
| [skills/release/patterns/python.md](skills/release/patterns/python.md) | **New** — ruff + pytest pattern with uv detection |
| [skills/release/patterns/monorepo.md](skills/release/patterns/monorepo.md) | **New** — per-package pre-flight dispatch |
| [skills/release/templates/plan.md](skills/release/templates/plan.md) | **New** — plan file template and authoring rules |
| [skills/release/templates/issue-body.md](skills/release/templates/issue-body.md) | **New** — issue body format and AC guidelines |
| [.claude/commands/release.md](.claude/commands/release.md) | **Replaced** — was monolithic, now a 3-line pointer to SKILL.md |
| commands/release.md | **Deleted** — redundant now that skill is the distributable |

## Guard Rails

| Scenario | Behavior |
|----------|----------|
| User overrides detected mode | Follow-up `AskUserQuestion` with mode options; loads the chosen pattern |
| Pre-flight grep finds placeholder values (`123456789012`) | Not flagged — pattern file lists approved placeholders explicitly |
| npm has no `lint` script | Step skipped with a note; does not fail pre-flight |
| No test files found in python project | pytest skipped with a note |
| Monorepo with mixed npm + python packages | Each package runs its own pattern independently; results reported together |
| User chooses "Skip pre-flight" | Jumps directly to Phase 2 with no pre-flight output |

## Verification

1. Run `/release` in this repo with `skills/release/` as changed files — confirm Phase 0 announces "skills-gems" mode with audit summary.
2. Confirm `AskUserQuestion` appears for mode confirmation before any greps run.
3. Confirm audit greps run and pass (no real account IDs in the release skill files).
4. Confirm title/labels/version questions appear via `AskUserQuestion`.
5. In an npm project, copy `skills/release/` to `.claude/skills/release/` and add the wrapper command — confirm Phase 0 announces "npm" mode and runs lint + test.

## Breaking Changes

The old monolithic `commands/release.md` is removed. Anyone who copied it to their
`.claude/commands/release.md` will need to install the skill (`skills/release/`) and
replace their command file with the thin wrapper.
