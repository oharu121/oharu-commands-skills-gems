# Plan: Improve article formatting rules and add Zenn rich syntax support

**Status:** Completed
**Date:** 2026-03-11

## Context

The `write-developersio-articles` command generates DevelopersIO blog articles in Markdown,
but two formatting issues were causing rendering problems. First, bold markers (`**text**`)
placed directly adjacent to other characters (common in Japanese text) don't render correctly
in some Markdown renderers — a space before or after the asterisks is required. Second, the
command was using numbered lists for general content listings, making it harder to insert
images or other media beneath list items. Additionally, DevelopersIO supports Zenn-compatible
extended Markdown syntax (message boxes, accordions, Mermaid diagrams, etc.), but the command
had no awareness of these features and never used them in generated articles.

## Approach

All three issues are addressed by updating the single command file. The bold spacing and list
style preferences are added as formatting rules in the existing 注意事項 (Notes) section,
where they naturally fit alongside other writing guidelines. The Zenn syntax reference is added
as a new dedicated section at the end of the file, since it's substantial enough to warrant its
own heading and serves as both documentation and instruction for the AI assistant. The 記事の構成
テンプレート section is also converted from a numbered list to an unordered list to lead by example.

## Changes

### 1. Bold formatting rule
Added a guideline in the 注意事項 section requiring spaces around `**太字**` when adjacent
to other text. Includes inline NG/OK examples so the AI assistant can pattern-match correctly.

### 2. List style preference
Added a guideline preferring unordered lists (`-`) over numbered lists, except for sequential
procedures where order matters. The 記事の構成テンプレート section itself was converted from
`1. 2. 3.` to `- - -` to be consistent with this rule.

### 3. Zenn互換リッチ構文 section
Added a comprehensive reference section documenting Zenn-compatible extended Markdown syntax:
- `:::message` / `:::message alert` — message boxes for notes and warnings
- `:::details タイトル` — accordion/toggle for collapsible content
- Code block extensions — filename display (`` ```js:filename.js ``) and diff highlighting (`` ```diff js ``)
- `@[card](URL)` — link cards
- `![alt](URL =250x)` — image width specification
- `*キャプション*` — image captions on the line after an image
- `$$formula$$` / `$formula$` — KaTeX block and inline math
- `[^1]` — footnotes
- `` ```mermaid `` — Mermaid diagram blocks
- External content embedding (YouTube, X/Twitter, GitHub URLs on standalone lines)

Each syntax feature includes a usage description and code example so the AI assistant
knows when and how to apply it.

## Files Modified

| File | Change |
|------|--------|
| [commands/write-developersio-articles.md](commands/write-developersio-articles.md) | Added bold spacing rule, list style guideline, and Zenn reference to 注意事項; converted 構成テンプレート to unordered list; added new Zenn互換リッチ構文 section |

## Guard Rails

| Scenario | Behavior |
|----------|----------|
| Bold text at start of a line (e.g., heading-like usage) | No space needed — rule only applies when adjacent to other characters |
| Sequential procedure in article body | Numbered lists are still allowed per the guideline ("順序が重要な手順を除き") |
| Zenn syntax used but article viewed in plain Markdown | Graceful degradation — `:::message` blocks appear as plain text, code blocks still render |

## Verification

1. Open `commands/write-developersio-articles.md` and confirm the 注意事項 section contains the bold formatting and list style rules
2. Confirm the 記事の構成テンプレート section uses unordered list markers (`-`) instead of numbers
3. Confirm the Zenn互換リッチ構文 section exists at the end of the file with all documented syntax features
4. Run the `/write-developersio-articles` command with a test topic and verify the generated article uses unordered lists, proper bold spacing, and Zenn syntax where appropriate

## Breaking Changes

None
