# Plan: Bootstrap oharu-commands-skills-gems repo

**Status:** Completed
**Date:** 2026-03-11

## Context

Custom commands, gems, and skills for Claude Code were scattered across projects or existed
only as local configurations. There was no central, shareable repository where these prompt
assets could be versioned, discovered, and reused. Anyone wanting to use these assets had to
copy them manually, and there was no way to track what existed or how they evolved over time.

## Approach

Create a single public GitHub repository organized by asset type — commands, gems, and skills —
following Claude Code's conventions. Commands are Markdown instruction files that define slash
commands (e.g., `/generate-bruno-files`, `/publish`). Gems are system prompts for Claude's
Projects feature (daily briefing, Japanese communication, thumbnails). Skills are richer packages
with reference data and templates (the AWS architecture diagram skill includes icon references
and a Draw.io XML template).

The repo is markdown-only with no build steps — pushing to GitHub is the release. An `.examples/`
directory provides real-world usage examples showing how the commands and skills produce output.

## Changes

### 1. Custom Commands (5 commands)
- `commands/generate-bruno-files.md` — Reads source code to extract HTTP requests and generates
  `.bru` files for the Bruno API client, with proper variable substitution and sequence numbering
- `commands/migrate-env-to-1password.md` — Interactive migration of `.env` secrets to 1Password
  using `op` CLI, replacing plaintext values with `op://` references (written in Japanese)
- `commands/publish-developersio-articles.md` — Publishes Markdown articles to Contentful CMS
  via `scripts/contentful.py`, handling both new draft creation and updates with excerpt management
- `commands/write-developersio-articles.md` — DevelopersIO blog writing assistant that follows
  the media guidelines, handles frontmatter, folder/tag selection, and Japanese article structure
- `commands/release.md` — Two-phase release automation: creates a GitHub issue with a detailed
  plan file, then handles commit, tag, push, and GitHub release creation

### 2. Claude Gems (3 gems)
- `gems/daily-briefing.md` — Morning briefing that pulls Google Calendar events and Gmail
  priority emails into a "Today's Schedule" and "Action Required" format
- `gems/jp-communication-enhancer.md` — Transforms English drafts into three levels of Japanese
  business communication (Slack casual, standard business email, formal client-facing), with
  IT-specific vocabulary like 起票, プルリク, and cushion word suggestions
- `gems/thumbnail-generator.md` — Generates 2-3 thumbnail variations for tech articles using
  visual metaphors, with strict rules against using third-party logos

### 3. AWS Architecture Diagram Skill
- `skills/aws-architecture-diagram/SKILL.md` — Generates Draw.io XML diagrams with accurate
  AWS icons, supporting technical and non-technical audience modes (step-numbered edges,
  simplified Japanese labels, swim lanes)
- `skills/aws-architecture-diagram/references/` — 7 icon reference files covering Compute,
  Storage/Database, Networking, App Integration, Analytics/ML, Security, and Common icons
- `skills/aws-architecture-diagram/templates/base.drawio.xml` — Skeleton Draw.io XML template

### 4. Examples
- `.examples/custom-commands-for-blogging-with-contentful.md` — Real-world example of the
  blogging workflow
- `.examples/event-driven-ecommerce.drawio` and `.md` — Sample AWS architecture diagram output

## Files Modified

| File | Change |
|------|--------|
| [commands/generate-bruno-files.md](commands/generate-bruno-files.md) | **New** — Bruno API client .bru file generator |
| [commands/migrate-env-to-1password.md](commands/migrate-env-to-1password.md) | **New** — .env to 1Password migration (Japanese) |
| [commands/publish-developersio-articles.md](commands/publish-developersio-articles.md) | **New** — Contentful CMS publishing command |
| [commands/write-developersio-articles.md](commands/write-developersio-articles.md) | **New** — DevelopersIO article writing assistant |
| [commands/release.md](commands/release.md) | **New** — Release automation with issue tracking |
| [gems/daily-briefing.md](gems/daily-briefing.md) | **New** — Daily calendar + email briefing |
| [gems/jp-communication-enhancer.md](gems/jp-communication-enhancer.md) | **New** — Japanese business communication helper |
| [gems/thumbnail-generator.md](gems/thumbnail-generator.md) | **New** — Tech article thumbnail generator |
| [skills/aws-architecture-diagram/SKILL.md](skills/aws-architecture-diagram/SKILL.md) | **New** — AWS diagram skill definition |
| [skills/aws-architecture-diagram/references/](skills/aws-architecture-diagram/references/) | **New** — 7 AWS icon reference files |
| [skills/aws-architecture-diagram/templates/base.drawio.xml](skills/aws-architecture-diagram/templates/base.drawio.xml) | **New** — Draw.io XML template |

## Guard Rails

| Scenario | Behavior |
|----------|----------|
| User copies a command without the required scripts (e.g., `contentful.py`) | The publish command's Step 1 checks for the script and stops with setup instructions |
| User runs `/release` on a repo without `gh` CLI | Error handling table in release.md covers this — provides manual release URL |
| AWS icon name not found in reference files | Skill rule #1 mandates looking up icons before generating XML — never guesses |
| Non-technical audience receives a diagram with protocol labels | Non-Technical Audience Mode replaces labels with circled step numbers and simplified descriptions |

## Verification

1. Clone the repo: `git clone https://github.com/oharu121/oharu-commands-skills-gems`
2. Verify directory structure: `ls commands/ gems/ skills/`
3. Confirm each command file is valid Markdown with clear step-by-step instructions
4. Open `.examples/event-driven-ecommerce.drawio` in Draw.io to verify the skill's output format
5. Check that all internal links in this plan resolve to existing files

## Breaking Changes

None — this is the initial release.
