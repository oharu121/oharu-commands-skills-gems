# Changelog

All notable changes to this project will be documented in this file.

## [v1.3.1](https://github.com/oharu121/oharu-commands-skills-gems/releases/tag/v1.3.1) - 2026-03-19

### Added

- **Skills**
  - `release` — config file support (`language`, `repo_mode`, `preflight_confirm`) for persistent preferences; skips language and mode prompts on subsequent runs while always running pre-flight

## [v1.3.0](https://github.com/oharu121/oharu-commands-skills-gems/releases/tag/v1.3.0) - 2026-03-19

### Added

- **Skills**
  - `release` — restructured from a monolithic command into a modular skill with repo detection, `AskUserQuestion`-driven pre-flight confirmation, and pattern files for skills-gems, npm, Python, and monorepo repos

### Removed

- **Commands**
  - `release` — replaced by the `skills/release` skill; install via `cp -r skills/release .claude/skills/release`

## [v1.2.0](https://github.com/oharu121/oharu-commands-skills-gems/releases/tag/v1.2.0) - 2026-03-19

### Added

- **Skills**
  - `bedrock-ops` — AWS Bedrock KB + S3 data pipeline management with MFA session auto-refresh, dry-run enforcement, identity verification, and service blocklist

## [v1.1.0](https://github.com/oharu121/oharu-commands-skills-gems/releases/tag/v1.1.0) - 2026-03-13

### Added

- **Skills**
  - `aws-cost-estimate` — AWS cost estimation skill with Price List API integration, web search fallback, and optional Calculator link generation via Playwright

## [v1.0.0](https://github.com/oharu121/oharu-commands-skills-gems/releases/tag/v1.0.0) - 2026-03-11

Initial release.

### Added

- **Commands**
  - `generate-bruno-files` — Generate `.bru` request files from source code
  - `migrate-env-to-1password` — Migrate `.env` secrets to 1Password CLI
  - `publish-developersio-articles` — Publish Markdown articles to Contentful CMS
  - `write-developersio-articles` — DevelopersIO blog writing assistant
  - `release` — GitHub issue + tag + release automation

- **Skills**
  - `aws-architecture-diagram` — Draw.io XML diagram generator with AWS icon references, layout guidelines, and non-technical audience mode

- **Gems**
  - `daily-briefing` — Google Calendar + Gmail morning briefing
  - `jp-communication-enhancer` — English to Japanese business communication (3 formality levels)
  - `thumbnail-generator` — Tech article thumbnail generator

- **Examples**
  - Blogging workflow with Contentful (DevelopersIO article)
  - Event-driven e-commerce AWS architecture diagram
