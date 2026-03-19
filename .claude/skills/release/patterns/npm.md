# Pre-flight Pattern: npm

**Summary for Phase 0 announcement:** lint and test via npm scripts.

## Steps

```bash
npm run lint 2>&1
npm test 2>&1
```

If the repo has no `lint` script in `package.json`, skip the lint step and note it.

## On Failure

Use AskUserQuestion:
- "Lint/tests failed. How do you want to proceed?"
- Options: "Fix first (cancel release)", "Skip pre-flight and continue"

Show the failing output before asking.

## On Pass

State: "npm lint and tests passed." and continue to Phase 2.
