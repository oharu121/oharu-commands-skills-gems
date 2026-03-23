# Bundles & Manifest

## Bundles

Curated collections of related items. When a bundle is installed, all included items are installed together.

### bundle: aws-toolkit
description: AWS architecture diagram + cost estimate — design first, then price it
items:
- skill: aws-architecture-diagram
- skill: aws-cost-estimate

### bundle: blogging-workflow
description: Write and publish DevelopersIO articles end-to-end (Japanese)
items:
- command: write-developersio-articles
- command: publish-developersio-articles

### bundle: aws-bedrock
description: Full AWS Bedrock KB + S3 pipeline management with safety guardrails
items:
- skill: bedrock-ops

### bundle: release-automation
description: Repo-aware release automation with pre-flight checks
items:
- skill: release

---

## Skills

### skill: aws-architecture-diagram
description: Generates Draw.io XML diagrams with accurate AWS service icons (technical and non-technical modes)
files:
- skills/aws-architecture-diagram/SKILL.md
- skills/aws-architecture-diagram/references/compute.md
- skills/aws-architecture-diagram/references/storage-database.md
- skills/aws-architecture-diagram/references/networking.md
- skills/aws-architecture-diagram/references/app-integration.md
- skills/aws-architecture-diagram/references/analytics-ml.md
- skills/aws-architecture-diagram/references/security.md
- skills/aws-architecture-diagram/references/common.md
- skills/aws-architecture-diagram/references/layout-guidelines.md
- skills/aws-architecture-diagram/templates/base.drawio.xml

### skill: aws-cost-estimate
description: Generates AWS cost estimates from architecture documents using the AWS Price List API
files:
- skills/aws-cost-estimate/SKILL.md
- skills/aws-cost-estimate/references/pricing-api.md
- skills/aws-cost-estimate/references/calculator-automation.md
- skills/aws-cost-estimate/references/permissions.md

### skill: bedrock-ops
description: Manages AWS Bedrock KB + S3 data pipeline with safety guardrails and MFA session auto-refresh
files:
- skills/bedrock-ops/SKILL.md
- skills/bedrock-ops/scripts/aws_safe.py
- skills/bedrock-ops/scripts/session.py
- skills/bedrock-ops/scripts/setup_project.py
- skills/bedrock-ops/scripts/totp.py

### skill: release
description: Repo-aware release automation with pre-flight checks, GitHub issue creation, commit, tag, push, and GitHub release
files:
- skills/release/SKILL.md
- skills/release/patterns/npm.md
- skills/release/patterns/python.md
- skills/release/patterns/skills-gems.md
- skills/release/patterns/monorepo.md
- skills/release/templates/github-issue-body.md
- skills/release/templates/plan-file.md

---

## Commands

### command: generate-bruno-files
description: Reads source code to extract HTTP requests and generates .bru files for the Bruno API client
files:
- commands/generate-bruno-files.md

### command: migrate-env-to-1password
description: Interactively migrates .env secrets to 1Password using op CLI, replacing values with op:// references (Japanese)
files:
- commands/migrate-env-to-1password.md

### command: publish-developersio-articles
description: Publishes Markdown articles to Contentful CMS as drafts, with create and update support
files:
- commands/publish-developersio-articles.md

### command: write-developersio-articles
description: DevelopersIO blog writing assistant that follows media guidelines and handles frontmatter (Japanese)
files:
- commands/write-developersio-articles.md

---

## Gems

Gems are system prompts for Gemini Gems — they cannot be auto-installed. The wizard will show the raw URL for each selected gem so you can paste the content into a new Gemini Gem manually.

### gem: daily-briefing
description: Morning briefing that pulls Google Calendar events and Gmail priority emails
url: https://raw.githubusercontent.com/oharu121/oharu-commands-skills-gems/main/gems/daily-briefing.md

### gem: jp-communication-enhancer
description: Transforms English drafts into 3 levels of Japanese business communication (Slack, email, formal)
url: https://raw.githubusercontent.com/oharu121/oharu-commands-skills-gems/main/gems/jp-communication-enhancer.md

### gem: thumbnail-generator
description: Generates thumbnail variations for tech articles using visual metaphors
url: https://raw.githubusercontent.com/oharu121/oharu-commands-skills-gems/main/gems/thumbnail-generator.md
