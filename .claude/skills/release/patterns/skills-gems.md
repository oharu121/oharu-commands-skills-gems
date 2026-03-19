# Pre-flight Pattern: skills-gems

**Summary for Phase 0 announcement:** sensitive data audit on new/modified skill files.

## Trigger

Run if any files under `skills/` are new or modified in the current changes.

## Steps

Scan all changed skill files for the following patterns:

| Pattern | What to look for |
|---------|-----------------|
| AWS account IDs | 12-digit numbers (`\b\d{12}\b`) in ARNs or standalone |
| Real ARNs | `arn:aws:iam::\d{12}:` with a non-placeholder account ID |
| TOTP / MFA secrets | Base32 strings in config examples or comments |
| Personal profile names | Hardcoded `--profile <name>` not wrapped in `<angle-bracket placeholders>` |
| Personal S3 buckets | Hardcoded `s3://` URIs that aren't placeholders |
| API keys / tokens | Any string that looks like a secret key |

```bash
# 12-digit account IDs
grep -rn '\b[0-9]\{12\}\b' skills/<changed-skill>/

# Hardcoded s3:// URIs (filter out obvious placeholders)
grep -rn 's3://[a-z0-9-]\+/' skills/<changed-skill>/ | grep -v '<bucket\|example\|your-'

# Real ARNs
grep -rn 'arn:aws:[a-z]*::[0-9]\{12\}:' skills/<changed-skill>/
```

## On Findings

Report each finding with file path and line number. Fix or redact before proceeding.

Approved placeholders:
- Account IDs → `123456789012`
- S3 buckets → `<your-bucket>`
- TOTP secrets → `YOUR_BASE32_SECRET`
- MFA ARNs → `arn:aws:iam::123456789012:mfa/your-username`

Re-run the greps after fixing to confirm clean.

## On Pass

State: "Audit passed — no sensitive data found." and continue to Phase 2.
