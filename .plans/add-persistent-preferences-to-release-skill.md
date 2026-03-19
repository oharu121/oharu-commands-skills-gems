# Plan: Add persistent preferences to release skill

**Status:** Completed
**Date:** 2026-03-19

## Context

Every run of the release skill asked two questions that almost never change: what language
to write the issue in, and which repo mode pre-flight should use. On this repo the answers
are always "English" and "skills-gems". Asking for confirmation on things that are already
known creates friction without adding safety — especially the mode confirmation gate, which
a user would click "Yes, proceed" on reflexively every single time.

The language prompt was added first, then the question arose: should mode detection also be
configurable to avoid the confirmation gate? The key constraint was that disabling the
confirmation gate must never mean disabling pre-flight itself — that would remove the safety
guarantee the skill was built around.

## Approach

A project-local `config.json` file at `.claude/skills/release/config.json` stores the three
stable preferences. All fields are optional — missing fields fall back to the interactive
flow, so the config is purely additive. On first run the skill asks normally, then offers to
save preferences at the end. On subsequent runs it reads config at startup and skips only
the prompts whose answers are already known.

The `preflight_confirm: false` field is intentionally named to make the distinction explicit
in the file: it disables the *confirmation gate*, not the pre-flight. The pre-flight pattern
file still loads and runs regardless of this setting.

## Changes

### 1. Config file schema (`config.json`)
Three optional fields:
- `language` — `"en"` or `"ja"` or any string; skips Step 1.5 when present
- `repo_mode` — `"skills-gems"` / `"npm"` / `"python"` / `"monorepo"` / `"generic"`;
  skips filesystem detection and uses this mode directly
- `preflight_confirm` — `false` skips the "Detected X, proceed?" `AskUserQuestion` gate;
  pre-flight still executes for the configured/detected mode

### 2. SKILL.md — config read at startup
New "Config File" section documents the schema and field effects. Phase 0 now checks
`repo_mode` before running detection, and checks `preflight_confirm` before showing the
confirmation gate. Step 1.5 is skipped when `language` is present in config.

### 3. SKILL.md — save preferences on first run (Step 13)
After closing the issue, if no config existed at startup, an `AskUserQuestion` offers to
save the language and mode used this run to `config.json` with `preflight_confirm: false`.
This means the first run is fully interactive; every subsequent run is streamlined.

## Files Modified

| File | Change |
|------|--------|
| [skills/release/SKILL.md](skills/release/SKILL.md) | Added config read, conditional detection/confirmation, save-preferences prompt |
| [.claude/skills/release/SKILL.md](.claude/skills/release/SKILL.md) | Synced from source |

## Guard Rails

| Scenario | Behavior |
|----------|----------|
| `config.json` has `repo_mode` but no `preflight_confirm` | Mode used directly, confirmation gate still shown (field defaults to interactive) |
| `preflight_confirm: false` set without `repo_mode` | Detection runs, gate skipped — pre-flight executes for detected mode |
| Pre-flight fails even with `preflight_confirm: false` | Still stops and reports — config only skips the gate, never the check |
| User answers "No" to save preferences | Config not written; next run asks again |
| Config file exists but is malformed JSON | Treat as missing — fall back to interactive flow |

## Verification

1. Delete `.claude/skills/release/config.json` if it exists, run `/release` — confirm language and mode prompts appear, and "save preferences" prompt appears at the end.
2. Answer "Yes" to save preferences — confirm `config.json` is written with correct `language`, `repo_mode`, and `preflight_confirm: false`.
3. Run `/release` again — confirm language and mode confirmation prompts are skipped, pre-flight still runs.
4. Manually set `preflight_confirm: true` in config — confirm confirmation gate reappears.

## Breaking Changes

None. Config is opt-in; missing config produces identical behaviour to before.
