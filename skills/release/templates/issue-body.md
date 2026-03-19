# Template: Issue Body

Use this format when creating the GitHub issue in Step 6b.

**IMPORTANT:** Include the COMPLETE plan file content, not a summary.

---

## Format

```markdown
<Full content of .plans/<filename>.md — copy verbatim>

---

## Acceptance Criteria

### AC-1: <First criterion name>

| Criteria | Description |
|----------|-------------|
| Given | <precondition> |
| When | <action> |
| Then | <expected result> |
| Verify | <see Verify field guidelines below> |
| Evidence | |

### AC-2: <Second criterion name>

| Criteria | Description |
|----------|-------------|
| Given | <precondition> |
| When | <action> |
| Then | <expected result> |
| Verify | <see Verify field guidelines below> |
| Evidence | |

---

Plan file: [.plans/<filename>.md](.plans/<filename>.md)
```

---

## Verify Field Guidelines

| Value | When to use |
|-------|-------------|
| `auto — <command>` | A shell command can verify this (e.g. `auto — grep -r "pattern" src/`) |
| `auto` | Determinable from Given/When/Then without a specific command |
| `manual` | Requires human eyes — UI behaviour, subjective output, visual checks |

## AC Rules

- Write 2–4 ACs per issue — one per meaningful behaviour, not one per file changed
- Each AC should be independently verifiable
- "Evidence" is left blank — filled in when the issue is closed
