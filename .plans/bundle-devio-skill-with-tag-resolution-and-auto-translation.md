# Plan: feat(devio): bundle devio skill with tag resolution and auto-translation

**Status:** Completed
**Date:** 2026-03-23

## Context

The DevelopersIO blog publishing workflow was previously split across two separate Claude Code commands — `write-developersio-articles` and `publish-developersio-articles` — with a supporting Python CLI living in `scripts/contentful.py` at the project root. This structure had three problems that accumulated over time.

First, the tag system was silently broken. Contentful stores blog post tags as numeric ID strings (e.g., `"20064"` for "Claude Code"), but the publish flow was forwarding human-readable tag names from frontmatter as-is. Every article published through this workflow had incorrect tag values that didn't resolve to the actual Contentful tag taxonomy — a master list of over 2,000 tags stored in a `blogTags` content type entry.

Second, the article drafting command had no way to look up what tags actually exist in Contentful, so it invented names freely. Those invented names couldn't be resolved at publish time, creating a broken end-to-end flow.

Third, the commands weren't portable. The Python CLI's path was hardcoded relative to the project root, and the commands were two separate files with no shared context — not a reusable skill that could be installed in other repos.

The fix in `oharu121/developersio-articles#7` resolved all three issues in that repo. This release ports the consolidated skill into this collection.

## Approach

The solution replaces the two old commands with a single self-contained `devio` skill directory. The skill follows the same pattern as other skills in this repo: a `SKILL.md` router at the top level, instruction files alongside it, and a `scripts/` subdirectory for the Python CLI.

Tag resolution uses a local cache strategy: `tags --refresh` fetches the full master list from Contentful once and writes it to `.claude/tags-cache.json`. All subsequent `create` and `update` operations resolve frontmatter tag names to numeric IDs via the cache at publish time, rather than forwarding raw names. The article drafting instruction now runs `tags --search` before suggesting tags so all suggestions are guaranteed to exist in the master list.

Auto-translation was a Contentful UI-only setting — the `targetLocales` field defaulted to empty, meaning English auto-translation wasn't triggered on programmatic publish. The script now sets `targetLocales: ["en"]` in every create and update payload.

## Changes

### 1. `skills/devio/` — New consolidated skill

- `SKILL.md` — router that dispatches `/devio article <topic>` and `/devio publish <file>`, with usage guidance if invoked without arguments
- `article.md` — moved from `commands/write-developersio-articles.md`; now runs `tags --search` before presenting tag options to ensure all suggestions exist in Contentful
- `publish.md` — moved from `commands/publish-developersio-articles.md`; documents tag resolution flow and staleness warning
- `scripts/contentful.py` — moved from the article repo's `scripts/`; added `tags` command (`--refresh`, `--search`, `--resolve`), tag resolution in `cmd_create`/`cmd_update`, reverse mapping in `cmd_get`, `targetLocales` field in both create and update payloads, and `Path.cwd()`-relative config path for portability

### 2. Removed commands

- `commands/write-developersio-articles.md` — superseded by `skills/devio/article.md`
- `commands/publish-developersio-articles.md` — superseded by `skills/devio/publish.md`
- `.claude/commands/release.md` — superseded by the `skills/release` skill installed in v1.3.0

## Files Modified

| File | Change |
|------|--------|
| [skills/devio/SKILL.md](skills/devio/SKILL.md) | New: skill router |
| [skills/devio/article.md](skills/devio/article.md) | New: article drafting with tag search integration |
| [skills/devio/publish.md](skills/devio/publish.md) | New: publish flow with tag resolution and auto-translation |
| [skills/devio/scripts/contentful.py](skills/devio/scripts/contentful.py) | New: Python CLI with tag cache, resolve, auto-translation |
| [commands/write-developersio-articles.md](commands/write-developersio-articles.md) | Deleted: replaced by devio skill |
| [commands/publish-developersio-articles.md](commands/publish-developersio-articles.md) | Deleted: replaced by devio skill |
| [.claude/commands/release.md](.claude/commands/release.md) | Deleted: superseded by release skill |

## Guard Rails

| Scenario | Behavior |
|----------|----------|
| Tag cache missing at article time | `article.md` instructs Claude to run `tags --refresh` first |
| Tag cache stale (>7 days) | Script emits a warning; user is prompted to refresh |
| Tag name not in Contentful master list | `tags --resolve` exits with error and substring-match suggestions |
| `/devio` invoked without subcommand | SKILL.md router displays usage for `article` and `publish` |

## Verification

1. Install the skill: copy `skills/devio/` to `.claude/skills/devio/` and add command wrapper
2. Run `/devio article <topic>` — verify it runs `tags --search` before presenting tag options
3. Run `python3 .claude/skills/devio/scripts/contentful.py tags --refresh` — verify cache written to `.claude/tags-cache.json`
4. Run `tags --resolve "Claude Code"` — verify returns numeric ID `"20064"`
5. Run `tags --resolve "nonexistent"` — verify exits with "Did you mean" suggestions
6. Run `/devio publish <file>` — verify Contentful entry is created with correct tag IDs and `targetLocales: ["en"]`

## Breaking Changes

- `/write-developersio-articles` → `/devio article <topic>`
- `/publish-developersio-articles` → `/devio publish <file>`
- Tags in article frontmatter must match Contentful master list names exactly (previously silently incorrect)
