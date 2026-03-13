# Required Permissions

This skill uses different tools depending on the pricing method and whether the user wants a Calculator link.

## Core (always needed)

```
WebSearch
WebFetch(domain:aws.amazon.com)
```

## AWS CLI pricing (preferred path)

```
Bash(aws pricing get-products:*)
Bash(aws sts get-caller-identity:*)
Bash(which aws)
```

## AWS Pricing Calculator link (optional, step 4)

Playwright MCP tools for browser automation:

```
mcp__plugin_playwright_playwright__browser_navigate
mcp__plugin_playwright_playwright__browser_wait_for
mcp__plugin_playwright_playwright__browser_click
mcp__plugin_playwright_playwright__browser_snapshot
mcp__plugin_playwright_playwright__browser_type
mcp__plugin_playwright_playwright__browser_fill_form
```

## Where to configure

Add these to project-scoped `settings.local.json` under `permissions.allow`:

```json
{
  "permissions": {
    "allow": [
      "WebSearch",
      "WebFetch(domain:aws.amazon.com)",
      "Bash(aws pricing get-products:*)",
      "Bash(aws sts get-caller-identity:*)",
      "Bash(which aws)",
      "mcp__plugin_playwright_playwright__browser_navigate",
      "mcp__plugin_playwright_playwright__browser_wait_for",
      "mcp__plugin_playwright_playwright__browser_click",
      "mcp__plugin_playwright_playwright__browser_snapshot",
      "mcp__plugin_playwright_playwright__browser_type",
      "mcp__plugin_playwright_playwright__browser_fill_form"
    ]
  }
}
```

Note: If the user hasn't pre-configured these, Claude Code will prompt for permission at runtime. The skill works without pre-configuration — it just requires more approval clicks.
