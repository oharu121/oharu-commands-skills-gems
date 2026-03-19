---
name: release
description: Create a GitHub issue, commit, tag, and push a release. Detects repo type and runs mode-specific pre-flight checks with user confirmation at every step.
user-invocable: true
---

# Release Skill

Orchestrate a full release: repo detection, pre-flight, GitHub issue, commit, tag, push.

**IMPORTANT:** Every interaction with the user MUST go through `AskUserQuestion`. Never
prompt with plain text and wait for a reply — always use the tool.

## Path Variables

- `SKILLS_DIR` = `.claude/skills/release`

---

## Phase 0: Repo Detection

Run these checks:

```bash
ls package.json pyproject.toml uv.lock skills/ 2>/dev/null
git status --short
```

Classify into one or more modes:

| Signal detected | Mode |
|-----------------|------|
| `skills/` directory exists AND changed files are under `skills/` | **skills-gems** |
| `package.json` exists | **npm** |
| `pyproject.toml` or `uv.lock` exists | **python** |
| Two or more of the above | **monorepo** |
| None of the above | **generic** |

Use AskUserQuestion to announce the detected mode and confirm pre-flight steps:

> "Detected: **\<mode\>**. Pre-flight will run: \<summary from pattern file\>. Proceed?"

Options:
- "Yes, proceed" (Recommended)
- "Skip pre-flight"
- "Override mode" → follow-up AskUserQuestion: skills-gems / npm / python / monorepo / generic

---

## Phase 1: Pre-flight

Read and follow `SKILLS_DIR/patterns/<detected-mode>.md`.

If pre-flight passes or is skipped, continue to Phase 2.
If pre-flight fails, stop — do not continue until resolved.

---

## Phase 2: Issue Creation

### Step 1: Gather Context

From the session, identify:
- What feature/fix was implemented
- Which files were modified
- What the key changes were
- Any breaking changes

### Step 2: Ask for Title

Use AskUserQuestion:
- 3 suggested titles (concise, action-oriented)
- "Other" option for free input

### Step 3: Ask for Labels

Use AskUserQuestion with multiSelect=true:
- Options: enhancement, bug, documentation, refactor
- "Other" for custom labels (comma-separated)

### Step 4: Ask for Version

```bash
git describe --tags --abbrev=0 2>/dev/null || echo "none"
```

Treat missing tags as v0.0.0. Use AskUserQuestion:
- patch: v{x}.{y}.{z+1}
- minor: v{x}.{y+1}.0
- major: v{x+1}.0.0
- Skip (no tag or release)

Always prefix with "v". **Store the selected version** for later steps.

### Step 5: Create Plan File

Read `SKILLS_DIR/templates/plan.md` for the template and rules.

Create `.plans/<slugified-title>.md` filled with real content from the session.

### Step 6: Create GitHub Issue

#### 6a: Handle Milestone (if version selected)

```bash
gh api repos/{owner}/{repo}/milestones --jq '.[] | select(.title == "<version>") | .title'
```

If missing:

```bash
gh api repos/{owner}/{repo}/milestones -f title="<version>" -f state="open"
```

#### 6b: Create the Issue

Read `SKILLS_DIR/templates/issue-body.md` for the body format.

```bash
gh issue create \
  --title "<title>" \
  --label "<labels>" \
  --assignee "@me" \
  --milestone "<version>" \
  --body "<body>"
```

Omit `--milestone` if version was skipped.

### Step 7: Generate Commit Message

```
feat(<scope>): <description> (#<issue-number>)
```

Use `fix()` for bugs, `docs()` for documentation, `refactor()` for refactoring.

Output: `Issue created: <url> — proceeding with release automation...`

---

## Phase 3: Release Automation

### Step 8: Check Remote Status

```bash
git fetch
git rev-list --count HEAD..@{u}
```

If remote has new commits, use AskUserQuestion:
- "Remote has new commits. Pull with rebase before continuing?"
- Options: "Yes, pull --rebase", "No, continue anyway", "Cancel"

Pull: `git pull --rebase` — stop on merge conflicts.

### Step 9: Show Changes & Commit

```bash
git status --short
```

Use AskUserQuestion:
- "Commit these changes?" — show proposed commit message
- Options: "Yes, use this message", "No, use custom message", "Cancel"

If custom: use AskUserQuestion "Other" for free input.

```bash
git add .
git commit -m "<message>"
```

### Step 10: Tag Version

Skip if version was skipped. Otherwise:

```bash
git tag v<new-version>
```

### Step 11: Push to Remote

Use AskUserQuestion:
- "Push commits and tags to remote?"
- Options: "Yes, push now", "No, I'll push manually", "Cancel"

```bash
git push && git push --tags
```

On failure: show manual command.

### Step 12: Create GitHub Release

Skip if version was skipped.

```bash
gh release create v<version> \
  --title "<version> - <plan-title>" \
  --notes "<plan-content-without-header>"
```

### Step 13: Close Issue & Output

```bash
gh issue close <issue-number> --comment "Released in v<version>"
# or if skipped:
gh issue close <issue-number> --comment "Shipped in <commit-sha>"
```

**If version was tagged:**
```
Release complete!

Issue: <issue-url>
Version: <old> -> <new>
Tag: v<new>
Release: <github-release-url>
```

**If version was skipped:**
```
Changes committed and pushed!

Issue: <issue-url>
Commit: <commit-message>

No version tag or GitHub release (skipped).
```

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Remote fetch fails | Warn and continue |
| Pull conflicts | Stop, instruct to resolve manually |
| Pre-flight fails | Stop, AskUserQuestion: skip or fix |
| Commit fails | Stop (likely pre-commit hook) |
| Tag already exists | Stop, AskUserQuestion with next version suggestion |
| Push fails | Warn, show manual command |
| gh not installed | Warn, provide manual release URL |
