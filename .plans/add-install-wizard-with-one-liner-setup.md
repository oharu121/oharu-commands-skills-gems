# Plan: feat(install): add install wizard with one-liner setup

**Status:** Completed
**Date:** 2026-03-23

## Context

Installing skills and commands from this repo previously required manual steps: cloning the repository, understanding the directory structure, copying files to the right paths (`.claude/commands/` for commands, `.claude/skills/` for skills), creating command wrapper files for each skill, and knowing which skills work well together. There was no guidance on dependencies or recommended groupings — a user discovering `aws-cost-estimate` wouldn't know it pairs naturally with `aws-architecture-diagram`.

The friction made the repo harder to share and adopt. The goal was to reduce installation to a single command that requires no prior setup, no clone, and no knowledge of the file layout.

## Approach

Rather than building a traditional install script (shell, Python, etc.), the solution leans on Claude Code itself as the installer runtime. Claude Code can already fetch URLs via `WebFetch` and write files via `Write` — making it capable of acting as a package manager if given the right instructions.

The key insight: `INSTALL.md` is not documentation for humans, it is a **prompt for Claude**. When a user runs the one-liner, Claude fetches `INSTALL.md`, reads it as instructions, and executes a structured wizard: choosing install scope, presenting options, detecting existing installs, fetching files from raw GitHub URLs, and writing them to disk.

A separate `BUNDLES.md` serves as the manifest and bundle registry. It lists every file path for every item in the repo (so Claude knows what to fetch) and declares named bundles that group related items with a short rationale. This separation means bundles can evolve without touching the core wizard logic.

## Changes

### 1. `INSTALL.md` — The wizard meta-prompt

Instructs Claude to:
- Fetch `BUNDLES.md` from the raw GitHub URL to get the full manifest
- Ask the user for install scope: global (`~/.claude/`) or project (`./.claude/`)
- Present a numbered menu with three sections: Bundles (recommended first), Individual Skills, Individual Commands, and a Gems note section
- Check for existing installs via `ls` and offer skip or overwrite per item (or "overwrite all")
- Fetch each selected file from `https://raw.githubusercontent.com/oharu121/oharu-commands-skills-gems/main/{path}` and write to the correct local path
- For skills, automatically create a command wrapper at `{scope}/commands/{skill-name}.md` so `/skill-name` works in Claude Code without manual setup
- Print a summary table of installed, skipped, and overwritten items

### 2. `BUNDLES.md` — Manifest + bundle registry

Two roles in one file:
- **Manifest**: lists every `files:` entry for each skill and command so Claude knows exactly which files to fetch for multi-file skills like `bedrock-ops` (which has 4 Python scripts) or `release` (which has patterns and templates subdirectories)
- **Bundles**: four curated collections — `aws-toolkit` (diagram + cost estimate), `blogging-workflow` (write + publish), `aws-bedrock`, `release-automation`
- **Gems section**: lists gems with raw URLs and a note that they're for Gemini, not Claude Code

### 3. `README.md` — Quick Install section

Added a `## Quick Install` section at the top of the README with the one-liner:
```bash
claude "Read https://raw.githubusercontent.com/oharu121/oharu-commands-skills-gems/main/INSTALL.md and follow the wizard"
```
Removed the manual `cp` instructions from the Commands and Skills sections since the wizard handles this now.

## Files Modified

| File | Change |
|------|--------|
| [INSTALL.md](INSTALL.md) | New — wizard meta-prompt with install flow, scope selection, update detection |
| [BUNDLES.md](BUNDLES.md) | New — full file manifest for all items + 4 bundle definitions + gems section |
| [README.md](README.md) | Added Quick Install section at top; removed manual copy instructions |

## Guard Rails

| Scenario | Behavior |
|----------|----------|
| Skill already installed | Wizard detects via `ls`, asks skip or overwrite; "overwrite all" option avoids repeated prompts |
| User selects a bundle | Bundle expands to constituent items, deduplicating if the same item appears in multiple selections |
| Skill has subdirectories (e.g. `bedrock-ops/scripts/`) | `BUNDLES.md` lists full relative paths; wizard creates nested directories before writing |
| Gems selected | No file copying — wizard prints raw URL and instructs user to paste into Gemini |
| New skill added to repo | Maintainer adds it to `BUNDLES.md` manifest; wizard picks it up automatically on next run |

## Verification

1. From a directory with no `.claude/` folder, run the one-liner
2. Wizard should greet, ask global vs project scope, and show the bundle + item menu
3. Select `blogging-workflow` bundle — verify both `write-developersio-articles.md` and `publish-developersio-articles.md` are written to the correct path
4. Select a skill (e.g. `aws-architecture-diagram`) — verify `SKILL.md`, all reference files, and the command wrapper are created
5. Re-run the wizard — wizard should detect existing files and offer skip/overwrite
6. Select a gem — verify no files are written; raw URL and paste instructions are shown

## Breaking Changes

None. Manual installation still works unchanged — `INSTALL.md` and `BUNDLES.md` are additive.
