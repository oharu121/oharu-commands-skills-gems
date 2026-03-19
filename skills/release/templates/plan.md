# Template: Plan File

Create `.plans/<slugified-title>.md` with this structure. **Quality matters** — this plan
is embedded in the GitHub issue and read by future contributors. Write at narrative depth,
not as a changelog.

---

## Template

```markdown
# Plan: <Title>

**Status:** Completed
**Date:** <YYYY-MM-DD>

## Context

<The problem story. What was happening before? What triggered the need for this change?
A future reader should understand WHY without reading code.>

## Approach

<The solution strategy. Why this approach over alternatives? What existing patterns or
infrastructure are we reusing? What constraints shaped the design?>

## Changes

<Organized by component or numbered steps. For each change:
- What was added/modified and why
- Implementation specifics: command names, config fields, API endpoints
- How it connects to existing commands or structure>

## Files Modified

| File | Change |
|------|--------|
| [file.md](path/to/file.md) | <what changed and why> |

## Guard Rails

| Scenario | Behavior |
|----------|----------|
| <realistic edge case> | <what happens> |

## Verification

<Specific runnable steps to confirm it works end-to-end.>

## Breaking Changes

<List or "None">
```

---

## Rules

- **Context and Approach are narrative** — tell a story, not bullet points
- **Changes names specific things**: command names, config fields, API endpoints, not vague descriptions
- **Guard Rails are realistic**: scenarios that can actually happen, not hypothetical edge cases
- **Verification is runnable**: steps someone can actually execute, not "test it works"
