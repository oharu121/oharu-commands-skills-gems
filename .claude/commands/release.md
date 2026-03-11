# /release

Create a GitHub issue, commit, tag, and push a release for developersio-articles.

This is a markdown-only repo with Claude Code custom commands for DevelopersIO blog article writing and Contentful publishing. No build or deploy steps — pushing to GitHub is the release.

## Instructions

You have access to the full conversation context. Use it to understand what was implemented.

---

## Phase 1: Issue Creation (Steps 1-7)

### Step 1: Gather Context

From the session, identify:
- What feature/fix was implemented
- Which files were modified
- What the key changes were
- Any breaking changes

### Step 2: Ask for Title

Use AskUserQuestion with:
- 3 suggested titles based on the work done (concise, action-oriented)
- "Other" option allows free input

### Step 3: Ask for Labels

Use AskUserQuestion with multiSelect=true:
- Options: enhancement, bug, documentation, refactor
- "Other" option allows custom labels (comma-separated)

### Step 4: Ask for Version

Read the latest git tag:

```bash
git describe --tags --abbrev=0 2>/dev/null || echo "none"
```

If no tags exist, treat current version as v0.0.0.

Parse the version (strip "v" prefix), then use AskUserQuestion:
- patch: v{x}.{y}.{z+1}
- minor: v{x}.{y+1}.0
- major: v{x+1}.0.0
- Skip (no tag or release)

Always prefix versions with "v" for tags and milestone names. **Store the selected version** for later steps.

### Step 5: Create Plan File

Create `.plans/<slugified-title>.md` using the template below. **Quality matters** — this plan is embedded in the GitHub issue. Write it at the depth of the example, not as a changelog.

**Template:**

```markdown
# Plan: <Title>

**Status:** Completed
**Date:** <YYYY-MM-DD>

## Context

<The problem story. What was happening before? What triggered the need for this change? A future reader should understand WHY without reading code.>

## Approach

<The solution strategy. Why this approach over alternatives? What existing patterns or infrastructure are we reusing? What constraints shaped the design?>

## Changes

<Organized by component or numbered steps. For each change:>
<- What was added/modified and why>
<- Implementation specifics: command names, config fields, API endpoints>
<- How it connects to existing commands or structure>

## Files Modified

| File | Change |
|------|--------|
| [file.md](path/to/file.md) | <what changed and why> |

## Guard Rails

| Scenario | Behavior |
|----------|----------|
| <realistic edge case> | <what happens> |

## Verification

<Specific steps to confirm it works end-to-end.>

## Breaking Changes

<List or "None">
```

**Example** (shows the expected quality — match this depth):

```markdown
# Plan: Add /publish command with Contentful integration

**Status:** Completed
**Date:** 2026-03-05

## Context

Articles were written locally as Markdown but had to be manually copy-pasted into
Contentful's web UI. This was tedious and error-prone — frontmatter metadata (title,
slug, tags) had to be entered separately in Contentful's form fields.

## Approach

Use Claude Code's custom command feature to create a `/publish` slash command that
reads the local Markdown file, parses its YAML frontmatter, and calls the Contentful
Content Management API to create a draft entry. The command handles first-time setup
(token validation, content model auto-discovery) so new users can onboard with zero
manual configuration.

Key constraint: Contentful's CMA token is space-level, not user-level — author identity
must be stored in a local config file, not derived from the token.

## Changes

### 1. CMA token validation
The command checks `.env` for `CONTENTFUL_CMA_TOKEN` before proceeding. If missing,
it guides the user to the Contentful token generation page and stops.

### 2. Auto-discovery of content model
If `.claude/contentful-config.json` doesn't exist, the command uses the CMA API to:
- `GET /spaces` to find the space ID
- `GET /content_types` to identify the blogPost content type
- `GET /entries?content_type=authorProfile` to list authors for user selection
Results are saved to `contentful-config.json` for future runs.

### 3. Draft creation via CMA API
Parses frontmatter (title, slug, tags) and body from the Markdown file, then
`POST /entries` with `X-Contentful-Content-Type: blogPost`. Entries are created
as drafts by default — no accidental publishing.

## Files Modified

| File | Change |
|------|--------|
| [.claude/commands/publish.md](.claude/commands/publish.md) | **New** — publish command definition |
| [.claude/contentful-config.json](.claude/contentful-config.json) | **New** — auto-generated Contentful config |
| [.env.example](.env.example) | Added CMA token template |
| [.gitignore](.gitignore) | Added `.env` and config to ignore list |

## Guard Rails

| Scenario | Behavior |
|----------|----------|
| Missing CMA token | Command stops with setup instructions |
| Missing config file | Auto-discovery flow runs before publish |
| Invalid token | Contentful API returns 401 — command shows error |
| Duplicate slug | Contentful API returns validation error — command reports it |

## Verification

1. Run `/publish macos/open-with-vscode-from-finder-right-click-menu.md`
2. Confirm draft appears in Contentful web UI with correct title, slug, tags, and body
3. Run with missing `.env` — confirm setup instructions are shown

## Breaking Changes

None
```

**Key rules:**
- Context and Approach are **narrative** — they tell a story, not list bullets
- Changes section names **specific commands, config fields, and API endpoints** being used
- Guard Rails lists **realistic scenarios**, not hypothetical ones
- Verification has **runnable steps**, not "test it works"

### Step 6: Create GitHub Issue

#### 6a: Handle Milestone (if version was selected)

```bash
# Check if milestone exists
gh api repos/{owner}/{repo}/milestones --jq '.[] | select(.title == "<version>") | .title'
```

If it doesn't exist, create it:

```bash
gh api repos/{owner}/{repo}/milestones -f title="<version>" -f state="open"
```

#### 6b: Create the Issue

```bash
gh issue create \
  --title "<title>" \
  --label "<labels>" \
  --assignee "@me" \
  --milestone "<version>" \
  --body "<body>"
```

Omit `--milestone` if user selected "Skip".

Issue body format - Include the FULL plan file content followed by acceptance criteria:

```markdown
<Full content of the plan file from .plans/<filename>.md>

---

## Acceptance Criteria

### AC-1: <First criterion name>

| Criteria | Description |
|----------|-------------|
| Given | <precondition> |
| When | <action> |
| Then | <expected result> |
| Verify | <`auto — <command>` or `auto` or `manual`> |
| Evidence | |

### AC-2: <Second criterion name>

| Criteria | Description |
|----------|-------------|
| Given | <precondition> |
| When | <action> |
| Then | <expected result> |
| Verify | <`auto — <command>` or `auto` or `manual`> |
| Evidence | |

---

Plan file: [.plans/<filename>.md](.plans/<filename>.md)
```

**Verify field guidelines:**
- `auto — <command>`: A shell command to verify (e.g., `auto — cat .claude/commands/publish.md | head -1`)
- `auto`: Verification can be determined from the Given/When/Then (no specific command)
- `manual`: Requires human eyes (UI, subjective behavior)

IMPORTANT: The issue body should contain the COMPLETE plan file content, NOT a summary.

### Step 7: Generate Commit Message

Parse the issue URL to get the issue number, then generate:

```
feat(<scope>): <description> (#<issue-number>)
```

Use `fix()` for bug fixes, `docs()` for documentation, `refactor()` for refactoring.

Output:
```
Issue created: <full-url>

Proceeding with release automation...
```

---

## Phase 2: Release Automation (Steps 8-13)

### Step 8: Check Remote Status

```bash
git fetch
git rev-list --count HEAD..@{u}
```

If remote has new commits:
1. Inform user
2. Check for uncommitted changes (`git status --porcelain`)
3. If uncommitted changes, ask: "Commit with WIP message before pulling?"
4. Pull with rebase: `git pull --rebase`
5. Stop on merge conflicts

### Step 9: Show Changes & Commit

Display changes:

```bash
git status --short
```

Use AskUserQuestion to confirm:
- "Commit these changes?"
- Show the commit message from Step 7
- Options: "Yes, use this message", "No, use custom message", "Cancel"

If confirmed:

```bash
git add .
git commit -m "<commit-message>"
```

### Step 10: Tag Version

**If user selected "Skip" in Step 4:** Skip tagging entirely, proceed to push.

**If version was selected:**

```bash
git tag v<new-version>
```

### Step 11: Push to Remote

Use AskUserQuestion:
- "Push commits and tags to remote?"
- Options: "Yes, push now", "No, I'll push manually", "Cancel"

If Yes:

```bash
git push && git push --tags
```

If push fails, show manual command. If No, remind user to push manually.

### Step 12: Create GitHub Release

**Skip if version was skipped.**

```bash
gh release create v<version> \
  --title "<version> - <plan-title>" \
  --notes "<plan-content-without-header>"
```

If `gh` is not available, provide the manual release URL.

### Step 13: Close Issue & Output

Close the issue created in Step 6:

```bash
gh issue close <issue-number> --comment "Released in v<version>"
```

If version was skipped, close with the commit reference instead:

```bash
gh issue close <issue-number> --comment "Shipped in <commit-sha>"
```

**If version was tagged:**
```
Release complete!

Issue: <issue-url>
Version: <old-version> -> <new-version>
Tag: v<new-version>
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
| Remote fetch fails | Warn and continue (might be offline) |
| Pull fails (conflicts) | Stop, instruct to resolve manually |
| Commit fails | Stop (likely pre-commit hook) |
| Tag already exists | Stop, suggest different version |
| Push fails | Warn, show manual command |
| gh not installed | Warn, provide manual release URL |

---

## Example Session

User runs `/release` after adding the /publish command:

1. **Phase 1 - Issue Creation:**
   - Title: "Add /publish command with Contentful integration"
   - Labels: enhancement
   - Version: minor (v0.1.0)
   - Creates `.plans/add-publish-command-with-contentful-integration.md`
   - Creates GitHub issue #1
   - Commit message: `feat(publish): add Contentful draft publishing command (#1)`

2. **Phase 2 - Release Automation:**
   - Remote check: up to date
   - Shows changes, confirms commit
   - Tags v0.1.0
   - Pushes to remote
   - Creates GitHub release
   - Closes issue #1

3. **Output:**
   ```
   Release complete!

   Issue: https://github.com/<owner>/developersio-articles/issues/1
   Version: v0.0.0 -> v0.1.0
   Tag: v0.1.0
   Release: https://github.com/<owner>/developersio-articles/releases/tag/v0.1.0
   ```
