# Plan: Add bedrock-ops skill with MFA session management

**Status:** Completed
**Date:** 2026-03-19

## Context

Managing the RAG data pipeline for AWS Bedrock Knowledge Bases involved repetitive
manual steps: uploading files to S3, triggering KB ingestion jobs, polling for
completion, and refreshing MFA sessions before each operation. Each step required
looking up the right AWS CLI incantation and double-checking the profile/region to
avoid accidentally writing to the wrong account. A single Claude Code skill that
wraps all of this with safety guardrails was the obvious solution.

## Approach

The skill delegates all AWS operations to a Python safety wrapper (`aws_safe.py`)
that enforces a consistent set of guardrails: identity verification before writes,
dry-run before sync/cp, and a blocklist for high-risk services. MFA session handling
is separated into `session.py`, which uses `pyotp` to auto-generate TOTP codes and
write temp credentials into `~/.aws/credentials` under a `<profile>-session` profile.
`uv run --with pyotp,boto3` is used throughout so the skill requires no pre-installed
Python packages.

Config is split into a committed `aws-project.json` (profile, account ID, safety
rules) and a gitignored `aws-project.local.json` (TOTP secret, MFA serial) to ensure
secrets never reach version control.

## Changes

### 1. SKILL.md — command routing
Defines all user-facing commands as intent → script mappings. Claude interprets the
intent and routes to the appropriate Python script via `uv run`. Covers: identity &
session management, S3 ls/sync/force-upload/upload/download, cost & resource
queries, KB list/sync/status, and arbitrary `exec` passthrough.

Notable: `kb status` polls every 15 seconds until the ingestion job reaches
`COMPLETE` or `FAILED` and prints elapsed time. `s3 force-upload` uses `aws s3 cp
--recursive` instead of `sync` to bypass the timestamp+size check — required when
file content changes but byte count stays the same (e.g. after inserting chunk
anchors).

### 2. aws_safe.py — safety wrapper
Classifies every AWS CLI invocation as `read`, `write`, or `destructive` by
inspecting the service verb. Before any write/destructive op:
- Checks service against `safety.denied_services` (default: `iam`, `organizations`)
- Verifies `sts get-caller-identity` account matches `account_id` in config
- For commands supporting `--dryrun` (s3 sync/cp/mv/rm): runs dry-run first,
  requires `--execute` flag to proceed
- Blocks `--delete` unless `--i-understand-this-deletes` is passed
- Prints a confirmation banner showing profile, account, region, command, and mode

On `ExpiredToken` errors, automatically re-runs `session.py create` and retries.

### 3. session.py — MFA session lifecycle
Three sub-commands:
- `check` — calls `sts get-caller-identity` on the session profile; exits 0 if valid
- `create` — calls `sts assume-role` with TOTP code from `aws-project.local.json`,
  writes temp credentials to `~/.aws/credentials` under `<profile>-session`
- `ensure` — checks first, creates if expired; used by `aws_safe.py` before ops

TOTP retry: if `assume-role` fails with "invalid MFA", waits 5 seconds for the next
30-second TOTP window and retries once.

### 4. setup_project.py — interactive config generator
Parses `~/.aws/config` and outputs all available profiles as JSON for Claude to
present. If a profile name is passed as an argument, generates `aws-project.json`
and a stub `aws-project.local.json` with `totp_secret: "REPLACE_WITH_YOUR_TOTP_SECRET"`.

### 5. totp.py — standalone TOTP code generator
Reads `totp_secret` from `aws-project.local.json` and prints the current 6-digit
code. Useful for manual MFA situations without triggering a full session refresh.

## Files Modified

| File | Change |
|------|--------|
| [skills/bedrock-ops/SKILL.md](skills/bedrock-ops/SKILL.md) | **New** — skill definition with command routing tables and safety rules |
| [skills/bedrock-ops/scripts/aws_safe.py](skills/bedrock-ops/scripts/aws_safe.py) | **New** — AWS CLI safety wrapper with identity check, dry-run enforcement, and blocklist |
| [skills/bedrock-ops/scripts/session.py](skills/bedrock-ops/scripts/session.py) | **New** — MFA session management with TOTP auto-generation |
| [skills/bedrock-ops/scripts/setup_project.py](skills/bedrock-ops/scripts/setup_project.py) | **New** — interactive project config generator from ~/.aws/config |
| [skills/bedrock-ops/scripts/totp.py](skills/bedrock-ops/scripts/totp.py) | **New** — standalone TOTP code printer |

## Guard Rails

| Scenario | Behavior |
|----------|----------|
| Account ID mismatch before write | Aborts with "Account mismatch!" error before any AWS call |
| s3 sync without `--execute` | Runs `--dryrun`, prints output, exits with "Add --execute to run for real" |
| `--delete` flag without confirmation | Blocked by `block_delete_without_confirmation`; requires `--i-understand-this-deletes` |
| Denied service (e.g. `iam`) | Exits immediately with the denied services list |
| Expired MFA session | Auto-calls `session.py create`, retries the original command |
| TOTP code falls on window boundary | Waits 5s and retries `assume-role` once |
| Missing `aws-project.json` | Scripts walk up from script location then fall back to `cwd`; exit 2 if not found |
| `totp_secret` is the placeholder string | `session.py` and `totp.py` detect it and exit with setup instructions |

## Verification

1. Run `uv run python .claude/skills/bedrock-ops/scripts/setup_project.py` from a project — confirm JSON listing of AWS profiles is printed.
2. Run `uv run python .claude/skills/bedrock-ops/scripts/setup_project.py <profile>` — confirm `aws-project.json` and `aws-project.local.json` are created.
3. Run `/bedrock-ops session` — confirm MFA session is created and written to `~/.aws/credentials`.
4. Run `/bedrock-ops s3 sync ./local s3://bucket/path` — confirm dry-run output is shown and execution is blocked until `--execute` is added.
5. Run `/bedrock-ops kb list` — confirm Bedrock knowledge bases are listed using the session profile.
6. Run `/bedrock-ops cost` — confirm current month's cost breakdown by service is printed.

## Breaking Changes

None
