# Plan: Add AWS cost estimate skill with pricing API integration

**Status:** Completed
**Date:** 2026-03-13

## Context

When working on an AWS RAG helpdesk architecture, generating cost estimates required multiple rounds of web searching that was slow, unreliable, and often failed to get region-specific pricing (Tokyo). AWS pricing pages render pricing tables dynamically, making WebFetch ineffective at extracting regional rates. The result was estimates that fell back to US pricing with caveats — not ideal for customer-facing deliverables.

The existing `aws-architecture-diagram` skill proved that complex, reference-heavy workflows work well as skills with supporting files. A cost estimation skill would complement it, completing the architecture → diagram → cost estimate workflow.

## Approach

Build an `aws-cost-estimate` skill that prioritizes the AWS Price List API (`aws pricing get-products`) for exact regional pricing, falling back to web search only when the CLI is unavailable. The skill follows the same directory structure as `aws-architecture-diagram` — a lean SKILL.md workflow with heavy reference material extracted to `references/`.

The skill also offers an optional AWS Pricing Calculator shareable link via Playwright browser automation, since the Calculator has no API. This is kept as an explicit opt-in step because it's slow (~2-5 min) and requires Playwright MCP tools.

## Changes

### 1. Core skill workflow (`SKILL.md`)

Four-step workflow:
1. **Parse architecture** — extract services, data flows, scale assumptions from a provided document
2. **Verify pricing** — silently check AWS CLI availability, use Price List API if available, fall back to web search
3. **Generate report** — structured cost breakdown with math, sources, scaling options, and caveats
4. **Offer Calculator link** — optional Playwright-driven shareable URL generation

Supports `--lang` (ja/en) and `--currency` (usd/jpy) arguments. Includes common pitfalls section for services like OpenSearch Serverless (OCU minimums), S3 endpoints (Gateway = free), and Bedrock (separate embedding vs generation charges).

### 2. AWS Price List API reference (`references/aws-pricing-api.md`)

Complete reference for using `aws pricing get-products`:
- Prerequisites and auth check commands
- Service code lookup table (AmazonEC2, AmazonES, AmazonBedrock, etc.)
- Ready-to-use query examples for EC2, OpenSearch Serverless, S3, Transit Gateway, VPC Endpoints
- JSON response parsing with `jq` examples
- Tips on filter syntax and regional location names

### 3. Permissions reference (`references/permissions.md`)

Documents all tool permissions needed at each stage:
- Core: WebSearch, WebFetch
- AWS CLI: Bash patterns for `aws pricing` and `aws sts`
- Calculator automation: 6 Playwright MCP tools
- Includes a ready-to-paste `settings.local.json` snippet

### 4. Calculator automation guide (`references/calculator-automation.md`)

Playwright workflow documentation:
- Step-by-step flow for adding services to calculator.aws
- Known limitations: chatbot overlay blocking clicks, OCU integer-only fields
- Service-specific tips for OpenSearch Serverless, EC2, VPC/Transit Gateway

## Files Modified

| File | Change |
|------|--------|
| [skills/aws-cost-estimate/SKILL.md](skills/aws-cost-estimate/SKILL.md) | **New** — main skill workflow with 4-step process |
| [skills/aws-cost-estimate/references/aws-pricing-api.md](skills/aws-cost-estimate/references/aws-pricing-api.md) | **New** — AWS Price List API reference with examples |
| [skills/aws-cost-estimate/references/permissions.md](skills/aws-cost-estimate/references/permissions.md) | **New** — required tool permissions for each step |
| [skills/aws-cost-estimate/references/calculator-automation.md](skills/aws-cost-estimate/references/calculator-automation.md) | **New** — Playwright browser automation guide |

## Guard Rails

| Scenario | Behavior |
|----------|----------|
| AWS CLI not installed | Silently falls back to web search — no error shown to user |
| AWS credentials not configured | `aws sts get-caller-identity` fails → falls back to web search |
| Price List API returns no results for a service | Flag as unverified in the Caveats section, use web search for that service |
| User declines Calculator link | Step 4 is skipped entirely |
| Playwright MCP not available | Calculator step cannot proceed — inform user and skip |
| JPY currency selected | Skill asks user for exchange rate before calculating |

## Verification

1. Copy `skills/aws-cost-estimate/` to a project's `.claude/skills/` directory
2. Run `/aws-cost-estimate .docs/rag-helpdesk-architecture.md --lang ja --currency jpy`
3. Confirm the skill checks AWS CLI availability before searching
4. Confirm the report includes math, sources, and scaling options
5. Confirm step 4 asks about Calculator link generation

## Breaking Changes

None
