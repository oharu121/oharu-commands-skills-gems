# /logo ship \<dir>

Turn the chosen concept into real assets. Everything before this was scratch;
this is the first step that writes into the user's project.

## 1. Confirm what is being produced

A mark is rarely one file. Ask with AskUserQuestion which of these are wanted:

- **Favicon** — the mark alone, square, no wordmark
- **Header lockup** — mark plus wordmark, plus a narrow-screen variant
- **Standalone mark** for avatars, OG images, and social profiles

Then settle the narrow-screen behaviour explicitly, because it is the one
discovered late: a wordmark cannot ellipsis the way text can, so a header that
relied on truncation needs either a mark-only variant below a breakpoint or a
scaled-down lockup. Decide now, and check it at 320px in step 4.

## 2. Bake the outlines

For anything containing letterforms, feed `outline.py` a JSON job list on stdin:

```bash
echo '[{"id":"word","font":"Fraunces.ttf","text":"oharu",
        "axes":{"wght":700,"WONK":1,"opsz":144}}]' \
  | LOGO_FONT_DIR=./.fonts uv run --with fonttools --with uharfbuzz \
    python SKILLS_DIR/scripts/outline.py
```

Each result carries `d` (the path, already flipped into SVG's y-down space and
normalised to a 1000-unit em), `width`, and `bbox`.

Three traps, all of which have cost real time:

- **Do not compute a bounding box by parsing the path text.** `SVGPathPen` emits
  `H`/`V` shorthand carrying a *single* coordinate, so any code assuming the
  numbers alternate x,y silently returns wrong bounds for every glyph after the
  first horizontal or vertical segment. That is why `outline.py` returns `bbox`
  from `BoundsPen`. Use it
- **Round coordinates to integers** at a 1000-unit em. At any real render size
  the error is far below a pixel, and the path data shrinks by roughly a third
- **Fonts are the caller's problem.** Fetch them into `LOGO_FONT_DIR` (they are
  large and usually licensed), and keep that directory out of version control

## 3. Compose the assets

- **Responsive variants.** If the mark is shorter than the wordmark's ink
  height, you cannot produce the narrow variant by clipping the full lockup to a
  square. Emit two SVGs and let CSS choose between them
- **Theming.** Parts that should follow the page use `fill="currentColor"`;
  parts that are fixed carry their hex. An external `favicon.svg` cannot inherit
  `currentColor` at all — if it must theme, embed a `prefers-color-scheme` block
  inside the file

## 4. Wire it in

- The mark is artwork, so the **accessible name must come from the markup around
  it** — an `aria-label` on the wrapping link, sourced from existing i18n strings
  rather than duplicated into the SVG. Mark the SVGs `aria-hidden`
- Delete the CSS the old text brand needed (`text-overflow`, `white-space`, font
  sizing). It no longer applies and will mislead the next reader
- **Note the colour decision in the component itself** — what themes, what is
  fixed, and why. A bare hex with no explanation reads as an oversight and gets
  "fixed" later

## 5. Verify by looking

Run the project's checks, then open it:

- **320px and a desktop width** — confirm the narrow variant from step 1, and
  that the mark does not collide with adjacent controls
- **Both themes** — themeable parts invert, fixed parts do not
- **Every locale**, if the project is multilingual
- **A real browser tab** — hard-reload and confirm the favicon reads at 16px

## 6. Record the reproduction path

Baked path data is unreadable and unmaintainable by hand. In the component
header, state:

- That the outlines are generated, and the exact command that regenerates them
- The source faces and their axis settings
- That the wordmark string is frozen, and what has to change if it is localised

**Commit the generator, not just its output.** A generator living in a scratch
directory is a generator that does not exist — the artwork becomes
irreproducible the moment the session ends.
