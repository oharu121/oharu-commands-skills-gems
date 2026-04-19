# Changelog

All notable changes to this project will be documented in this file.

## [v1.6.0](https://github.com/oharu121/oharu-commands-skills-gems/releases/tag/v1.6.0) - 2026-04-19

### Added

- **Skills**
  - `generate-bruno-files` — promoted from `commands/generate-bruno-files.md` with skill frontmatter (`user-invocable: true`, `allowed-tools`, `argument-hint`); retains `/generate-bruno-files` slash-command invocation
  - `migrate-env-to-1password` — promoted from `commands/migrate-env-to-1password.md` (Japanese) with equivalent frontmatter; retains `/migrate-env-to-1password` invocation
- **Install via Vercel skills CLI** — `npx skills add oharu121/oharu-commands-skills-gems/<name>` (or `pnpm dlx skills add ...`) is now the primary install path; auto-detects `.claude/`, `.cursor/`, `.codex/`, and 40+ other agents

### Changed

- **README** — rewrote install section to document `npx skills add` and `pnpm dlx skills add`; merged Commands table into Skills table; added cross-agent support note

### Removed

- **`INSTALL.md`** — custom prose-based install wizard; superseded by `npx skills add`
- **`BUNDLES.md`** — bundle manifest and docs; three of four entries were single-skill aliases, and the sole genuine pairing (aws-architecture-diagram + aws-cost-estimate) now lives as a one-line note in README
- **`commands/` directory** — both commands promoted to skills; directory no longer exists

### Breaking

- The old install one-liner `claude "Read https://raw.../INSTALL.md and follow the wizard"` returns 404 — switch to `npx skills add oharu121/oharu-commands-skills-gems/<name>`
- `commands/*.md` raw URLs now 404 — the promoted skills live at `skills/generate-bruno-files/` and `skills/migrate-env-to-1password/`

## [v1.5.1](https://github.com/oharu121/oharu-commands-skills-gems/releases/tag/v1.5.1) - 2026-03-24

### Changed

- **Skills**
  - `release` — added Safe GitHub Body Write pattern (`--body-file` instead of `--body`) with empty-body verification, Resume State pattern (`.release-tmp/state.json`) for interrupted flow recovery, renamed "pre-flight" to "validation" across all files, added release-notes template, improved Python pattern with `$RUNNER` prefix and pyright type checking, added `format:check` to npm pattern, safer commit staging with explicit file listing, added `.release-tmp/` to `.gitignore`

## [v1.5.0](https://github.com/oharu121/oharu-commands-skills-gems/releases/tag/v1.5.0) - 2026-03-23

### Added

- **Skills**
  - `devio` — DevelopersIO blog workflow: draft articles with `tags --search` integration for guaranteed Contentful-valid tags, publish to Contentful with automatic tag ID resolution and `targetLocales: ["en"]` auto-translation; includes `tags --refresh/--search/--resolve` CLI subcommands and a local tag cache at `.claude/tags-cache.json`

### Removed

- **Commands**
  - `write-developersio-articles` — replaced by `skills/devio` (`/devio article <topic>`)
  - `publish-developersio-articles` — replaced by `skills/devio` (`/devio publish <file>`)

## [v1.4.0](https://github.com/oharu121/oharu-commands-skills-gems/releases/tag/v1.4.0) - 2026-03-23

### Added

- **Install wizard** — one-liner setup via `claude "Read https://raw.githubusercontent.com/oharu121/oharu-commands-skills-gems/main/INSTALL.md and follow the wizard"`: interactive scope selection, bundle recommendations, existing-install detection with skip/overwrite, automatic command wrapper creation for skills, and Gemini gem instructions
- **`INSTALL.md`** — wizard meta-prompt that Claude executes to drive the install flow; fetches files from raw GitHub URLs and writes them to the correct local paths
- **`BUNDLES.md`** — file manifest for all skills and commands plus four curated bundles: `aws-toolkit`, `blogging-workflow`, `aws-bedrock`, `release-automation`

## [v1.3.1](https://github.com/oharu121/oharu-commands-skills-gems/releases/tag/v1.3.1) - 2026-03-19

### Added

- **Skills**
  - `release` — config file support (`language`, `repo_mode`, `preflight_confirm`) for persistent preferences; skips language and mode prompts on subsequent runs while always running validation

## [v1.3.0](https://github.com/oharu121/oharu-commands-skills-gems/releases/tag/v1.3.0) - 2026-03-19

### Added

- **Skills**
  - `release` — restructured from a monolithic command into a modular skill with repo detection, `AskUserQuestion`-driven validation confirmation, and pattern files for skills-gems, npm, Python, and monorepo repos

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
