#!/usr/bin/env python3
"""Make the 'photographed front page' poster for an edition.

Renders the edition's sheet with a headless browser, then grades it like a
photograph of a printed broadsheet: photographic paper material over the
sheet, warm light, film grain, vignette, soft shadow on a dark ground.

Optional tooling (not required by the plugin itself): playwright + ffmpeg.
Usage: make_poster.py EDITION.html [--out poster.png] [--desk TEXTURE.webp]
"""
import argparse, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "gazette" / "assets" / "paper.webp"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("edition")
    ap.add_argument("--out", default="poster.png")
    ap.add_argument("--desk", default="")
    a = ap.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright is required for the poster (pip install playwright)",
              file=sys.stderr)
        return 2
    raw = Path(a.out).with_suffix(".raw.png")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1240, "height": 1650},
                        device_scale_factor=2)
        pg.goto(Path(a.edition).resolve().as_uri())
        pg.wait_for_timeout(700)
        box = pg.locator(".page").bounding_box()
        h = min(box["height"], box["width"] * 1.30)
        pg.screenshot(path=str(raw), clip={"x": box["x"], "y": box["y"],
                                           "width": box["width"], "height": h})
        b.close()
    desk_in = (["-i", a.desk] if a.desk else
               ["-f", "lavfi", "-i", "color=c=0x17110b:s=1600x2000"])
    fc = (
        "[0:v]scale=1600:2000:force_original_aspect_ratio=increase,crop=1600:2000[desk];"
        "[1:v]scale=1408:-1,format=rgba[pg];"
        "[1:v]scale=1408:-1,format=rgba,colorchannelmixer=rr=0:gg=0:bb=0:aa=0.5,gblur=sigma=16[sh];"
        "[2:v]scale=1408:1830,format=rgba,colorchannelmixer=aa=0.34[tex];"
        "[desk][sh]overlay=(W-w)/2+18:(H-h)/2+34[t1];"
        "[t1][pg]overlay=(W-w)/2:(H-h)/2[t2];"
        "[t2][tex]overlay=(W-w)/2:(H-h)/2[t3];"
        "[t3]colorbalance=rs=0.07:gs=0.01:bs=-0.11,noise=alls=12:allf=t,"
        "vignette=PI/4.9,eq=contrast=1.05:saturation=0.92[out]"
    )
    cmd = (["ffmpeg", "-y", "-loglevel", "error"] + desk_in +
           ["-i", str(raw), "-i", str(PAPER), "-filter_complex", fc,
            "-map", "[out]", "-frames:v", "1", a.out])
    r = subprocess.run(cmd, capture_output=True, text=True)
    raw.unlink(missing_ok=True)
    if r.returncode:
        print(r.stderr[-400:], file=sys.stderr)
        return r.returncode
    print(f"poster -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
