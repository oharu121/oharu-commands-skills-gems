# oharu-commands-skills-gems

A collection of custom commands, skills, and gems for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [Claude](https://claude.ai).

## Commands

Markdown instruction files that define slash commands for Claude Code. Place them in your project's `.claude/commands/` directory to use as `/command-name`.

| Command | Description |
|---------|-------------|
| [generate-bruno-files](commands/generate-bruno-files.md) | Reads source code to extract HTTP requests and generates `.bru` files for the [Bruno](https://www.usebruno.com/) API client |
| [migrate-env-to-1password](commands/migrate-env-to-1password.md) | Interactively migrates `.env` secrets to 1Password using `op` CLI, replacing values with `op://` references (Japanese) |
| [publish-developersio-articles](commands/publish-developersio-articles.md) | Publishes Markdown articles to Contentful CMS as drafts, with create and update support |
| [write-developersio-articles](commands/write-developersio-articles.md) | DevelopersIO blog writing assistant that follows media guidelines and handles frontmatter (Japanese) |
| [release](commands/release.md) | Two-phase release automation: creates a GitHub issue with a plan file, then commits, tags, pushes, and creates a GitHub release |

### Usage

Copy a command file into your project:

```bash
mkdir -p .claude/commands
cp commands/generate-bruno-files.md .claude/commands/generate-bruno-files.md
```

Then use it in Claude Code:

```
/generate-bruno-files src/api/client.ts
```

## Skills

Richer packages with reference data and templates. Skills are used by Claude Code to perform specialized tasks.

| Skill | Description |
|-------|-------------|
| [aws-architecture-diagram](skills/aws-architecture-diagram/) | Generates Draw.io XML diagrams with accurate AWS service icons, supporting technical and non-technical audience modes |

The AWS diagram skill includes:
- 7 icon reference files covering Compute, Storage/Database, Networking, App Integration, Analytics/ML, Security, and Common icons
- Layout guidelines for spacing, nesting, and style
- A base Draw.io XML template
- Non-technical audience mode with step-numbered edges and simplified labels

## Gems

System prompts for [Claude Projects](https://claude.ai). Create a new project on claude.ai and paste the gem content as the project instructions.

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
