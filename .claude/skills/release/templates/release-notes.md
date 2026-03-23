# Template: Release Notes

Use this format when writing release notes for the GitHub release in Step 12.

---

## Format

```markdown
## What's New

- <Behavior-oriented description of new features or capabilities>

## Changes

- <Behavior-oriented description of improvements, refactors, or fixes>

## Breaking Changes

- <Description of breaking change with migration steps>

_or_

None
```

---

## Rules

- **Use behavior-oriented language** — describe what users can now do or what changed
  from their perspective, not internal implementation details
- **No file paths or function names** — users don't need to know which files changed;
  that's what the commit history is for
- **Breaking changes require migration steps** — if something will break for existing
  users, explain exactly what they need to do
- **Omit empty sections** — if there are no breaking changes, omit the section entirely
  rather than writing "None" (keep "None" only if there were breaking changes in the
  plan but they were resolved before release)
- **Keep it concise** — one bullet per logical change, not one per file
