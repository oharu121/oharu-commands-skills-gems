# Plan: Adopt Vercel skills CLI; drop custom install wizard

**Status:** Completed
**Date:** 2026-04-19

## Context

This repo started as a personal hub of Claude Code skills, slash commands, and Gemini gems. To let any project install the skills with one command, earlier releases shipped a prose-based install wizard (`INSTALL.md` + `BUNDLES.md`) orchestrated by Claude itself — the user ran `claude "Read https://raw...../INSTALL.md and follow the wizard"`, and Claude fetched files from raw GitHub URLs and wrote them into `.claude/`. It worked, but it was a meta-prompt disguised as documentation: a file that only has meaning when another agent reads it, and that the repo owner has to keep in lockstep with every other file.

Two things changed the calculus. First, Vercel Labs' `skills` npm package (`npx skills add <owner>/<repo>/<name>`) crossed the threshold from hobby project to de-facto ecosystem — v1.5.1 shipped two days before this release, 2.87M downloads/month, 14.5k stars, support for 45+ agents including Claude Code, Cursor, Codex, Copilot, and Gemini. It's install-only by design (no push/publish), which fits this repo's workflow exactly: projects stay atomic, hub edits promote manually via cherry-pick, and there's near-zero lock-in because skills are plain markdown files in the repo. Second, the custom wizard was a single-person maintenance burden — every time a skill changed, `BUNDLES.md` had to agree, and the wizard's prose had to keep working as Claude's model drifted. Ditching it removes that coupling.

The trigger: the repo owner wanted one-command install without managing configuration artifacts, and the conversation landed on "Vercel's CLI already solves this; rebuild the repo to match its conventions." This release does the rebuild.

## Approach

Conform to the `npx skills add` convention rather than invent a parallel mechanism. The Vercel CLI looks for skills at `<repo>/skills/<name>/SKILL.md` as a priority path — this repo already placed every skill there, so the existing layout was compatible without restructuring. The only real gaps were artifacts *outside* the skills folder: two standalone slash commands under `commands/`, the wizard itself (`INSTALL.md`), a now-redundant manifest (`BUNDLES.md`), and a README that pointed users at the wizard instead of the CLI.

The conversion work was mostly consolidation. The two `commands/` files were functionally skills already — markdown instructions with `$ARGUMENTS` handling — so promoting them to skills with `user-invocable: true` frontmatter preserved the existing `/generate-bruno-files` and `/migrate-env-to-1password` slash invocations while making them installable via the same CLI as everything else. The wizard and its manifest became dead weight the moment install-from-GitHub became a one-liner. `BUNDLES.md` collapsed to a single sentence in README because only one of its four "bundles" actually bundled more than one skill.

A push/sync-back CLI was considered and rejected earlier in the design conversation. The owner's sync-back workflow is judgment-heavy — cherry-picking improvements from a project-local edit back to the hub — which is better served by `diff` and manual merge than by a blunt `push` command that would drag project-specific tweaks into canonical skills. This plan deliberately does not ship tooling for that direction.

## Changes

### Promoted commands to skills

- **`commands/generate-bruno-files.md` → `skills/generate-bruno-files/SKILL.md`** with frontmatter `name`, `description`, `user-invocable: true`, `allowed-tools: Bash(ls *), Read, Write, Edit, Glob, Grep, AskUserQuestion`, and `argument-hint`. Body preserved verbatim including `$ARGUMENTS` references.
- **`commands/migrate-env-to-1password.md` → `skills/migrate-env-to-1password/SKILL.md`** (Japanese) with equivalent frontmatter plus `Bash(op *)`, `Bash(which op)`, `Bash(brew install *)` in `allowed-tools`. Body preserved.
- Deleted `commands/generate-bruno-files.md`, `commands/migrate-env-to-1password.md`, and the now-empty `commands/` directory.

### Removed install wizard

- Deleted `INSTALL.md`. Its sole job was orchestrating install-from-GitHub into `.claude/`, which `npx skills add` does in one command.

### Collapsed bundles

- Deleted `BUNDLES.md`. Three of its four entries were single-skill aliases (blogging-workflow = `devio`, aws-bedrock = `bedrock-ops`, release-automation = `release`). The only genuine multi-skill pairing (`aws-architecture-diagram` + `aws-cost-estimate`) now lives as a one-line hint in README.

### Rewrote README install section

- Replaced the "Quick Install" block (wizard one-liner) with `npx skills add oharu121/oharu-commands-skills-gems/<name>` as the primary path, showing both `npx` and `pnpm dlx` variants.
- Merged the Commands table into the Skills table now that commands are skills.
- Added a per-skill install column with the full `npx skills add` command for each skill.
- Added a cross-agent support note: "Works with any agent supported by vercel-labs/skills — the CLI auto-detects `.claude/`, `.cursor/`, `.codex/`, and 40+ others. Claude Code is the primary target; other agents still work but may have a reduced experience."
- Gems section unchanged (Vercel CLI doesn't install Gemini artifacts; manual paste is still the path).

## Files Modified

| File | Change |
|------|--------|
| [skills/generate-bruno-files/SKILL.md](skills/generate-bruno-files/SKILL.md) | **New** — promoted from `commands/generate-bruno-files.md` with skill frontmatter |
| [skills/migrate-env-to-1password/SKILL.md](skills/migrate-env-to-1password/SKILL.md) | **New** — promoted from `commands/migrate-env-to-1password.md` with skill frontmatter |
| [commands/generate-bruno-files.md](commands/generate-bruno-files.md) | **Deleted** — superseded by skill |
| [commands/migrate-env-to-1password.md](commands/migrate-env-to-1password.md) | **Deleted** — superseded by skill |
| [INSTALL.md](INSTALL.md) | **Deleted** — wizard replaced by `npx skills add` |
| [BUNDLES.md](BUNDLES.md) | **Deleted** — single real bundle folded into README |
| [README.md](README.md) | Install section rewritten; commands merged into skills table; cross-agent note added; BUNDLES link removed |

## Guard Rails

| Scenario | Behavior |
|----------|----------|
| User on an older install runs the old wizard one-liner | `INSTALL.md` returns 404 from raw GitHub; user must switch to `npx skills add`. CHANGELOG entry documents the new command. |
| User bookmarked `BUNDLES.md` | 404 on raw GitHub. README now points to the skills table which has per-item install commands. |
| User tries `npx skills add` for a command that's now a skill | Works — the new path `oharu121/oharu-commands-skills-gems/generate-bruno-files` resolves because the skill folder exists under `skills/`. |
| User installs on Cursor/Codex instead of Claude Code | CLI auto-detects the agent, installs to `.cursor/skills/` etc. Claude-specific frontmatter (`user-invocable`, `argument-hint`) is silently ignored per the agentskills.io compatibility spec. |
| User runs `npx skills update` after this release | Lock file's content hash changes for generate-bruno-files/migrate-env-to-1password (moved paths) — CLI treats them as moved and re-installs at the new path. |

## Verification

End-to-end install check in a scratch directory outside this repo, after the release lands on `main`:

```bash
mkdir /tmp/skills-release-test && cd /tmp/skills-release-test
git init

# Install one pre-existing skill
npx skills@latest add oharu121/oharu-commands-skills-gems/release

# Install one newly-promoted command-as-skill
npx skills@latest add oharu121/oharu-commands-skills-gems/generate-bruno-files

ls .claude/skills/                 # expect: release, generate-bruno-files
cat skills-lock.json               # expect: both entries with source + ref + hash
npx skills list                    # expect: both listed
```

Launch Claude Code in the scratch project and verify:

1. `/release` and `/generate-bruno-files` appear as invocable slash commands.
2. Skill bodies render without frontmatter leaking.
3. `npx skills update` is a no-op when hashes match.

Repo-side sanity checks (already run as part of this release):

- Sensitive-data audit under `skills/generate-bruno-files/` and `skills/migrate-env-to-1password/` returned zero matches for 12-digit IDs, real ARNs, or hardcoded S3 URIs.
- No remaining references to `INSTALL.md` or `BUNDLES.md` in README.
- `git status` shows the expected set of adds, modifications, and deletions only.

## Breaking Changes

- The one-liner `claude "Read https://raw..../INSTALL.md and follow the wizard"` no longer works — `INSTALL.md` is deleted. Users must switch to `npx skills add oharu121/oharu-commands-skills-gems/<name>` (or `pnpm dlx skills add ...`). The new README is the source of truth.
- `BUNDLES.md` is deleted. Anyone who linked to it gets 404. The README's skills table contains individual install commands.
- The `commands/` directory is removed. Installers that copied from `commands/` will fail. The promoted skills live at `skills/generate-bruno-files/` and `skills/migrate-env-to-1password/` with identical body content and slash-command invocation.
