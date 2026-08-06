"""
Convert short strings into SVG outline paths using real typefaces.

Hand-rolled geometric letterforms read as generic; borrowing the outlines of a
properly-drawn face and baking them into paths gets real typographic quality at
zero runtime font cost. Shaping goes through HarfBuzz so kerning and variable
axes are correct rather than approximated.

Output is JSON on stdout: one entry per job, with the path already flipped into
SVG's y-down space and normalised so the em box is 1000 units.
"""

import json
import os
import sys

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

# Where the caller has put the .ttf/.otf source faces. Overridable because the
# caller owns them: a generator script that fetches its own fonts wants a cache
# beside itself, while an ad-hoc run wants whatever directory it is already in.
# A job's `font` may also be an absolute path, which bypasses this entirely.
FONT_DIR = os.environ.get("LOGO_FONT_DIR", ".fonts")


def build(job):
    name = job["font"]
    path = name if os.path.isabs(name) else f"{FONT_DIR}/{name}"
    if not os.path.exists(path):
        raise SystemExit(
            f"Font not found: {path}\n"
            f"Put the face there, or set LOGO_FONT_DIR to the directory holding it."
        )
    font = TTFont(path)
    axes = job.get("axes")

    if axes:
        # Pin every requested axis so the glyph source is a static instance;
        # the pen cannot read deltas off a variable glyf table.
        font = instancer.instantiateVariableFont(font, axes, inplace=False)

    upem = font["head"].unitsPerEm
    scale = 1000 / upem

    # Re-serialise so HarfBuzz shapes the *instanced* outlines, not the default
    # master. Without this the advances come from the wrong weight.
    from io import BytesIO

    buf_io = BytesIO()
    font.save(buf_io)
    data = buf_io.getvalue()

    face = hb.Face(data)
    hb_font = hb.Font(face)
    buf = hb.Buffer()
    buf.add_str(job["text"])
    buf.guess_segment_properties()
    hb.shape(hb_font, buf)

    glyph_set = font.getGlyphSet()
    order = font.getGlyphOrder()
    tracking = job.get("tracking", 0) / scale  # caller works in 1000-unit space

    parts = []
    x = 0.0
    # Real inked bounds, accumulated through the same transform as the outlines.
    # These cannot be recovered by parsing the emitted path text: SVGPathPen
    # writes H/V shorthand, whose single coordinate breaks any assumption that
    # the numbers alternate x, y.
    bounds = BoundsPen(glyph_set)
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = order[info.codepoint]
        pen = SVGPathPen(glyph_set, ntos=lambda v: f"{v:.1f}")
        # (1,0,0,-1) flips the y axis into SVG orientation; the translate places
        # the glyph at the running pen position.
        xform = (scale, 0, 0, -scale, (x + pos.x_offset) * scale, 0)
        tpen = TransformPen(pen, xform)
        glyph_set[name].draw(tpen)
        glyph_set[name].draw(TransformPen(bounds, xform))
        d = pen.getCommands()
        if d:
            parts.append(d)
        x += pos.x_advance + tracking

    bx0, by0, bx1, by1 = bounds.bounds if bounds.bounds else (0, 0, 0, 0)

    hhea = font["hhea"]
    return {
        "id": job["id"],
        "d": " ".join(parts),
        "bbox": {
            "x0": round(bx0, 1), "y0": round(by0, 1),
            "x1": round(bx1, 1), "y1": round(by1, 1),
            "w": round(bx1 - bx0, 1), "h": round(by1 - by0, 1),
        },
        "width": round(x * scale, 1),
        "ascender": round(hhea.ascender * scale, 1),
        "descender": round(hhea.descender * scale, 1),
        "capHeight": round(font["OS/2"].sCapHeight * scale, 1)
        if hasattr(font["OS/2"], "sCapHeight")
        else None,
        "xHeight": round(font["OS/2"].sxHeight * scale, 1)
        if hasattr(font["OS/2"], "sxHeight")
        else None,
    }


if __name__ == "__main__":
    jobs = json.load(sys.stdin)
    json.dump([build(j) for j in jobs], sys.stdout)
