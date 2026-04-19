# skills

A collection of custom skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and system prompts for [Gemini](https://gemini.google.com). Previously published as `oharu-commands-skills-gems`.

## Install

All skills follow the open [Agent Skills specification](https://agentskills.io) and install via any compatible CLI. Pick whichever is easiest:

```bash
# GitHub CLI (gh v2.90+) — official, preview before install
gh skill install oharu121/skills <name>

# npm / node
npx skills add oharu121/skills/<name>

# pnpm
pnpm dlx skills add oharu121/skills/<name>
```

Use `gh skill preview oharu121/skills <name>` to inspect a skill's content before installing. Pass `-g` to install user-scoped (`~/.claude/skills/`). Update with `gh skill update` or `npx skills update`; remove with `gh skill remove` or `npx skills remove`.

Works with any agent supported by these CLIs — both auto-detect `.claude/`, `.cursor/`, `.codex/`, and 40+ others. Claude Code is the primary target (some skills use Claude-specific frontmatter like `user-invocable`); other agents still work but may have a reduced experience.

## Skills

Richer packages with reference data, templates, and scripts. Skills marked with `user-invocable: true` are also callable as `/skill-name` slash commands.

| Skill | Description | Install |
|-------|-------------|---------|
| [aws-architecture-diagram](skills/aws-architecture-diagram/) | Generates Draw.io XML diagrams with accurate AWS service icons, supporting technical and non-technical audience modes | `npx skills add oharu121/skills/aws-architecture-diagram` |
| [aws-cost-estimate](skills/aws-cost-estimate/) | Generates AWS cost estimates from architecture documents using the AWS Price List API, with optional Calculator link generation | `npx skills add oharu121/skills/aws-cost-estimate` |
| [bedrock-ops](skills/bedrock-ops/) | Manages the AWS Bedrock KB + S3 data pipeline with safety guardrails: S3 sync with force-upload, KB ingestion polling, cost monitoring, and MFA session auto-refresh | `npx skills add oharu121/skills/bedrock-ops` |
| [devio](skills/devio/) | DevelopersIO blog workflow: draft articles with tag search integration, publish to Contentful with tag resolution and auto-translation (Japanese) | `npx skills add oharu121/skills/devio` |
| [generate-bruno-files](skills/generate-bruno-files/) | Reads source code to extract HTTP requests and generates `.bru` files for the [Bruno](https://www.usebruno.com/) API client | `npx skills add oharu121/skills/generate-bruno-files` |
| [migrate-env-to-1password](skills/migrate-env-to-1password/) | Interactively migrates `.env` secrets to 1Password using `op` CLI, replacing values with `op://` references (Japanese) | `npx skills add oharu121/skills/migrate-env-to-1password` |
| [release](skills/release/) | Repo-aware release automation with validation checks, GitHub issue + plan file creation, commit, tag, push, and GitHub release. Supports npm, Python, and skills-gems repos with safe body writes and resume state | `npx skills add oharu121/skills/release` |

Install `aws-architecture-diagram` and `aws-cost-estimate` together for a design → price workflow.

The AWS diagram skill includes:
- 7 icon reference files covering Compute, Storage/Database, Networking, App Integration, Analytics/ML, Security, and Common icons
- Layout guidelines for spacing, nesting, and style
- A base Draw.io XML template
- Non-technical audience mode with step-numbered edges and simplified labels

The AWS cost estimate skill includes:
- AWS Price List API reference with service codes, example queries, and jq parsing
- Permissions reference for CLI, web search, and Playwright tools
- Calculator automation guide for generating shareable links via browser automation

## Gems

System prompts for [Gemini Gems](https://gemini.google.com/gems). Vercel's skills CLI doesn't install these — create a new Gem in Gemini and paste the file content as the gem instructions.

| Gem | Description |
|-----|-------------|
| [daily-briefing](gems/daily-briefing.md) | Morning briefing that pulls Google Calendar events and Gmail priority emails |
| [jp-communication-enhancer](gems/jp-communication-enhancer.md) | Transforms English drafts into 3 levels of Japanese business communication (Slack, email, formal) |
| [thumbnail-generator](gems/thumbnail-generator.md) | Generates thumbnail variations for tech articles using visual metaphors |

## Examples

The [.examples/](.examples/) directory contains real-world usage samples:

- [custom-commands-for-blogging-with-contentful.md](.examples/custom-commands-for-blogging-with-contentful.md) — Blog article showing the full blogging workflow
- [event-driven-ecommerce.drawio](.examples/event-driven-ecommerce.drawio) / [.md](.examples/event-driven-ecommerce.md) — Sample AWS architecture diagram output

## License

MIT
