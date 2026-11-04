#!/usr/bin/env python3
"""Generate a Gazette edition without Hermes (standalone CLI).

Usage:
  python scripts/generate_edition.py              # live feeds -> ./editions/<date>/
  python scripts/generate_edition.py --sample     # labelled SAMPLE edition (offline demo)
  python scripts/generate_edition.py --config my.json --out out/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from gazette.core import build_edition, load_config
from gazette.render import render_html, render_markdown


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate The Hermes Gazette")
    ap.add_argument("--sample", action="store_true", help="use bundled demo data (labelled SAMPLE)")
    ap.add_argument("--config", default=None, help="path to gazette.config.json")
    ap.add_argument("--out", default="editions", help="output directory root")
    args = ap.parse_args()

    config = load_config(args.config)
    sample_items = None
    if args.sample:
        sample_items = json.loads(
            (Path(__file__).parent.parent / "examples" / "sample_items.json").read_text(encoding="utf-8"))

    edition = build_edition(config, sample_items=sample_items)
    out = Path(args.out) / edition["date"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "edition.json").write_text(json.dumps(edition, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "edition.html").write_text(render_html(edition), encoding="utf-8")
    (out / "edition.md").write_text(render_markdown(edition), encoding="utf-8")

    print(f"Edition {edition['date']}: {edition['story_count']} stories "
          f"({'SAMPLE' if edition['is_sample'] else 'live'}) -> {out}/")
    for err in edition["errors"]:
        print(f"  source failed: {err}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
