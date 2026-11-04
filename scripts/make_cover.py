#!/usr/bin/env python3
"""Compose an edition's illustrated front-page cover.

The illustrated frame is FIXED (masthead, plate, paper, borders — generated
once, no variable text). What changes daily is typeset from the edition's
REAL data in the locked typography: the Nous mark, the Vol./No./date box,
and the giant lead headline (editorial rule: newest release leads).
The ghost print in the frame's columns is faded to pure texture — no word
on a cover is readable unless the edition itself supplied it.

Usage: make_cover.py EDITION_DIR [--out cover.png]   (needs Pillow + ffmpeg)
"""
import argparse, json, subprocess, sys
from datetime import date as date_type
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "gazette" / "assets"
FIRST = date_type(2026, 11, 4)
INK = (24, 17, 10)


def _font(size, weight=900):
    from PIL import ImageFont
    f = ImageFont.truetype(str(ASSETS / "fonts" / "PlayfairDisplay-Black.ttf"), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def _fit(draw, text, max_w, start, weight=900):
    size = start
    while size > 20:
        f = _font(size, weight)
        if draw.textlength(text, font=f) <= max_w:
            return f, size
        size -= 4
    return f, size


def _wrap_headline(draw, text, max_w, start, band_h=0):
    """One line for short heads; else the most balanced two lines."""
    f, size = _fit(draw, text, max_w, start)
    if size >= 96 and len(text) <= 18:
        return [text], f, size
    words = text.split()
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        w = max(draw.textlength(a, font=_font(start)), draw.textlength(b, font=_font(start)))
        if best is None or w < best[0]:
            best = (w, a, b)
    if best is None:
        return [text], f, size
    _, a, b = best
    f, size = _fit(draw, a, max_w, start)
    f2, size2 = _fit(draw, b, max_w, start)
    size = min(size, size2)
    if band_h:
        size = min(size, int(band_h / 2.12))
    return [a, b], _font(size), size


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("edition_dir")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    try:
        from PIL import Image, ImageDraw, ImageFilter
    except ImportError:
        print("Pillow is required (pip install pillow)", file=sys.stderr)
        return 2
    ed_dir = Path(a.edition_dir)
    edition = json.loads((ed_dir / "edition.json").read_text())
    items = [i for s in edition["sections"].values() for i in s]
    if not items:
        print("empty edition", file=sys.stderr)
        return 1
    lead = next((i for i in items if "release" in i.get("source", "").lower()), items[0])
    headline = lead["title"].upper()
    d = date_type.fromisoformat(edition["date"][:10])
    issue = max(1, (d - FIRST).days + 1)

    img = Image.open(ASSETS / "cover-frame.webp").convert("RGB")
    W, H = img.size
    # Fade the frame's ghost print (columns region) into pure texture.
    region = img.crop((0, int(H * 0.695), W, int(H * 0.955)))
    faded = region.filter(ImageFilter.GaussianBlur(1.6))
    img.paste(Image.blend(region, faded, 0.75), (0, int(H * 0.695)))
    draw = ImageDraw.Draw(img)

    # The Nous mark in the left box (interior approx.).
    mark = Image.open(ASSETS / "nous-mark.png")
    bx0, by0, bx1, by1 = int(W * 0.045), int(H * 0.112), int(W * 0.138), int(H * 0.20)
    mark.thumbnail((bx1 - bx0, by1 - by0))
    img.paste(mark, (bx0 + (bx1 - bx0 - mark.width) // 2, by0 + (by1 - by0 - mark.height) // 2), mark)

    # Data box (right): Vol. — No. / date / Price — Free.
    rx0, rx1 = int(W * 0.867), int(W * 0.964)
    lines = [f"VOL. I — No. {issue}", d.strftime("%b. %-d, %Y").upper(), "PRICE — FREE"]
    y = int(H * 0.190)
    for ln in lines:
        f2, _ = _fit(draw, ln, rx1 - rx0 - 8, 28, 700)
        draw.text(((rx0 + rx1) / 2, y), ln, font=f2, fill=INK, anchor="ma")
        y += 37

    # The giant headline in the empty band.
    hx0, hx1 = int(W * 0.075), int(W * 0.925)
    hy0, hy1 = int(H * 0.252), int(H * 0.345)
    hl_lines, f_hl, size = _wrap_headline(draw, headline, hx1 - hx0, 190, hy1 - hy0)
    line_h = size * 1.04
    total = line_h * len(hl_lines)
    y = hy0 + (hy1 - hy0 - total) / 2
    for ln in hl_lines:
        draw.text(((hx0 + hx1) / 2, y), ln, font=f_hl, fill=INK, anchor="ma")
        y += line_h

    raw = ed_dir / ".cover-raw.png"
    out = Path(a.out) if a.out else ed_dir / "cover.png"
    img.save(raw)
    fc = ("[0:v]colorbalance=rs=0.05:gs=0.01:bs=-0.08,noise=alls=10:allf=t,"
          "vignette=PI/5.6,eq=contrast=1.04:saturation=0.94[out]")
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw),
                        "-filter_complex", fc, "-map", "[out]", "-frames:v", "1",
                        str(out)], capture_output=True, text=True)
    raw.unlink(missing_ok=True)
    if r.returncode:
        print(r.stderr[-300:], file=sys.stderr)
        return r.returncode
    print(f"cover -> {out} (lead: {lead['title']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
