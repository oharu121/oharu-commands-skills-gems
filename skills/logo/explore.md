# /logo new \<brief>

The round structure. Each round ends at a gate where the user picks and you stop.

## 1. Establish the brief

Ask with AskUserQuestion only what you cannot infer. Four things decide the
design more than taste does:

- **Where it appears** — a site header, an app icon, print? A header mark can be
  wide; an app icon is a square with no wordmark
- **Smallest real size** — usually 16px if there is a favicon. This is the
  constraint that eliminates the most candidates
- **Wordmark text, and whether it is fixed** — baked outlines freeze the string.
  If it might be localised or edited later, the wordmark has to stay live text
- **Anything personal or cultural in play** — a name's meaning, characters,
  symbolism. **Never assume these.** See non-negotiable 4

Also confirm whether the mark must theme (light/dark) or may carry a fixed
palette. Both are legitimate; they produce different concepts.

## 2. Reference study

Follow [references.md](references.md) end to end. Report the contradiction table
and the territory list before generating anything.

## 3. Generate a wide round

Write concepts to a scratch directory — **never into the repo**:

```
SCRATCH/logo/round-1/
  c01.svg … cNN.svg
  concepts.json
```

`concepts.json` drives the sheet's grouping, ordering, and captions:

```json
[
  { "id": "c01", "name": "Aperture", "note": "Ring with a gap; reads as a lens",
    "group": "Editorial serif", "fixedColour": false }
]
```

Sections appear in the order groups first appear in this file, so order it as
the argument you want to make. Mark `fixedColour: true` on any concept whose
palette is baked rather than inheriting `currentColor`.

Rules for the concepts themselves:

- **One group per territory** from step 2. Six to twenty concepts total is
  plenty; more is not more range
- **Vary the thing that matters**, not the decoration. Two marks differing only
  in corner radius are one mark
- **Include a no-mark candidate** — type plus one colour is a real answer
- **Prefer solid fills.** Strokes close up at 16px (non-negotiable 3)
- **`fill="currentColor"`** unless the concept is deliberately fixed-palette, so
  the sheet can theme it
- Hand-authored geometry only for genuinely geometric marks. Anything involving
  letterforms uses baked outlines (non-negotiable 5)

## 4. Build the sheet and look at it

```bash
node SKILLS_DIR/scripts/gallery.mjs SCRATCH/logo/round-1 --port 4599 --title "Round 1"
```

Then open `http://localhost:4599/`, screenshot it, and **read your own
screenshot**. Check specifically:

- Is anything visually broken — a clipped glyph, a collision, a mark at the
  wrong scale beside its wordmark?
- Does the 16px column still read?
- **Do these concepts actually differ?** If they share a skeleton, you generated
  one concept *N* times. Go back to step 2; a new prompt will not fix it

Fix what is broken and rebuild before showing the user anything. Presenting a
sheet with a broken letterform wastes their attention on a bug instead of the
design.

## 5. Gate: the user picks a direction

Present with AskUserQuestion. Give them:

- Your honest ranking, with reasons
- **What you would cut and why** — this is more useful than the ranking. Name
  the concepts that fail at 16px, that read as something unintended, or that are
  the generic default
- Any constraint the sheet revealed that they should know about, even when it
  contradicts what they asked for

Wait. Do not advance on your own preference.

## 6. Refine the chosen direction

A new round, same mechanics, exploring *within* the winner rather than across
territories: weights, axis settings, proportions, the mark-to-wordmark ratio,
colour pairings.

This is where colour gets decided by comparison — put the pairings side by side
(non-negotiable 6). If the mark will sit next to existing UI colours, include
those in the comparison, not just the mark alone.

Build the sheet, look at it, present, gate again. Repeat until the user settles
on one. Two refinement rounds is normal; more usually means the brief in step 1
was underspecified, so go back and ask rather than generating again.

## 7. Ship

Follow [ship.md](ship.md).
