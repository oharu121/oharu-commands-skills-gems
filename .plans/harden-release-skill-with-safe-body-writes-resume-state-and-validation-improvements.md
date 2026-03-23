# Plan: Harden release skill with safe body writes, resume state, and validation improvements

**Status:** Completed
**Date:** 2026-03-24

## Context

The release skill was functional but had several reliability gaps that surfaced during real-world use. GitHub issue and release body creation used `--body` with bash heredocs, which silently broke when markdown content contained backticks, tables, or special characters — resulting in empty or malformed bodies on the created issues and releases. If the release flow was interrupted mid-way (e.g., by context window limits or user cancellation), there was no way to resume, forcing users to manually clean up orphaned issues and restart from scratch. The terminology also used "pre-flight" inconsistently across files, and the Python pattern lacked type checking (pyright) and used verbose `python -m` invocations instead of a clean runner prefix.

## Approach

Rather than patching individual issues, this release takes a holistic pass across the entire skill. Reusable patterns (Safe GitHub Body Write, Resume State) are defined once in SKILL.md and referenced from steps that need them, avoiding duplication. The "pre-flight" → "validation" rename is applied consistently across all files. Pattern files are made more robust by adding pyright type checking to Python, format:check to npm, and a Version Bump section to skills-gems. A new release-notes template standardizes the GitHub release format. The state schema includes a `schema_version` field for forward compatibility.

## Changes

### 1. Safe GitHub Body Write Pattern
Added a reusable pattern in SKILL.md that writes markdown content to `.release-tmp/<filename>.md` using the Write tool, then passes `--body-file` to `gh`. Includes a verification step that checks body length via `gh <resource> view` and stops the flow if the body is empty. Both issue creation (Step 6b) and release creation (Step 12) now reference this pattern.

### 2. Resume State Pattern
Added state persistence via `.release-tmp/state.json`. State is saved at the end of Phase 1 and Phase 2. On startup, the skill checks for an existing state file and offers to resume from the next phase. The "start fresh" option also asks whether to close any orphaned GitHub issue from the previous run. The schema includes a `schema_version` field for forward compatibility.

### 3. Validation Rename
Renamed "pre-flight" to "validation" across all files: SKILL.md frontmatter and heading, all four pattern files (npm, python, monorepo, skills-gems), Phase 0 confirmation prompts, and error handling table.

### 4. Release Notes Template
Added `templates/release-notes.md` with a user-facing format: What's New, Changes, Breaking Changes. Rules enforce behavior-oriented language (no file paths or function names) and require migration steps for breaking changes.

### 5. Python Pattern Improvements
Introduced a `$RUNNER` variable (set to `uv run` or empty based on `uv.lock` presence). Added `pyright` type checking as a new step. All commands now use `$RUNNER ruff check .`, `$RUNNER pyright .`, and `$RUNNER pytest` — consistent and portable.

### 6. npm Format Check
Added `npm run format:check` step to the npm validation pattern, with skip-if-missing logic matching the existing lint and test steps.

### 7. Safer Commit Staging
Changed `git add .` in Step 9 to `git add <specific-files>` to prevent accidentally staging unrelated files.

### 8. Gitignore Entry
Added `.release-tmp/` to `.gitignore` to prevent accidental commits of temporary release state.

### 9. skills-gems Version Bump Section
Added a Version Bump section to `skills-gems.md` clarifying that this mode uses tags only for versioning — no version file to bump.

## Files Modified

| File | Change |
|------|--------|
| [SKILL.md](.claude/skills/release/SKILL.md) | Added Safe Body Write + Resume State patterns, validation rename, safer staging, updated Steps 6b and 12 |
| [monorepo.md](.claude/skills/release/patterns/monorepo.md) | Pre-flight → validation rename, "full validation suite" wording |
| [npm.md](.claude/skills/release/patterns/npm.md) | Validation rename, added format:check step with skip-if-missing |
| [python.md](.claude/skills/release/patterns/python.md) | Validation rename, $RUNNER pattern, added pyright type checking |
| [skills-gems.md](.claude/skills/release/patterns/skills-gems.md) | Validation rename, added Version Bump section (tags only) |
| [release-notes.md](.claude/skills/release/templates/release-notes.md) | New file — release notes template |
| [.gitignore](.gitignore) | New file — added `.release-tmp/` |

## Guard Rails

| Scenario | Behavior |
|----------|----------|
| Markdown with backticks in issue body | Safe Body Write uses `--body-file`, avoids shell quoting issues |
| Release interrupted after issue creation | Resume State offers to pick up from next phase; "start fresh" asks about orphaned issue |
| `.release-tmp/` left behind after crash | Gitignored, won't be committed; next run detects state and offers resume |
| Issue or release body is empty after creation | Verification step catches it and stops the flow |
| npm project has no format:check script | Skipped with a note, does not fail |
| Python project without pyright | Skipped with a note, does not fail |
| State file from older schema version | `schema_version` field enables detection and graceful handling |

## Verification

1. Run `grep -ri "pre-flight" .claude/skills/release/` — confirm no occurrences remain
2. Run `grep -r "rubyclaw" .claude/skills/release/` — confirm no hardcoded project paths
3. Run `grep "release-tmp" .gitignore` — confirm `.release-tmp/` is gitignored
4. Inspect SKILL.md Step 6b and Step 12 — confirm both use `--body-file` pattern with verification
5. Inspect SKILL.md Step 9 — confirm `git add <specific-files>` instead of `git add .`
6. Run `/release` in this repo — confirm config is read, mode is auto-detected, and validation runs the sensitive data audit

## Breaking Changes

None
