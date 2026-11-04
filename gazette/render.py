"""Render an edition as a vintage newspaper (HTML) and as Markdown.

The HTML is a single self-contained file (inline CSS, no external assets)
so it can be delivered as an attachment to a phone, opened from the Hermes
dashboard tab, or printed. The design follows the antique broadsheet the
project was inspired by: aged sepia paper (procedural SVG grain — no image
files), a blackletter masthead with volume/price boxes, a giant lead
headline, justified columns with rules, fleuron ornaments.

Honesty in the furniture: the issue number is real (days since the first
edition, 2026-11-04 = No. 1) and the price box tells the truth — "FREE".
"""

from __future__ import annotations

import html
from datetime import date as date_type

# Procedural aged-paper grain (SVG turbulence, URL-encoded). Two layers:
# fine grain + broad blotches, both in sepia-brown with low opacity.
_GRAIN = (
    "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E"
    "%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E"
    "%3CfeColorMatrix values='0 0 0 0 0.23 0 0 0 0 0.16 0 0 0 0 0.05 0 0 0 0.6 0'/%3E%3C/filter%3E"
    "%3Crect width='300' height='300' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E\")"
)
_BLOTCH = (
    "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='600' height='600'%3E"
    "%3Cfilter id='b'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.012 0.02' numOctaves='3'/%3E"
    "%3CfeColorMatrix values='0 0 0 0 0.36 0 0 0 0 0.24 0 0 0 0 0.08 0 0 0 0.55 0'/%3E%3C/filter%3E"
    "%3Crect width='600' height='600' filter='url(%23b)' opacity='0.35'/%3E%3C/svg%3E\")"
)

_CSS = """
:root{--paper:#e9d8ab;--paper2:#dfc891;--ink:#241a10;--muted:#6d5a38;--rule:#241a10;--accent:#7c1d1d}
*{box-sizing:border-box}
body{margin:0;background:#2e2620 radial-gradient(1200px 800px at 50% -10%, #453829, #2e2620);
color:var(--ink);font-family:Georgia,'Times New Roman',serif;padding:18px 10px 30px}
.page{position:relative;max-width:920px;margin:0 auto;padding:30px 30px 26px;overflow:hidden;
background:
 radial-gradient(900px 500px at 15% 0%, rgba(122,84,32,.20), transparent 60%),
 radial-gradient(700px 900px at 95% 85%, rgba(101,67,33,.22), transparent 55%),
 radial-gradient(500px 300px at 70% 30%, rgba(255,246,214,.35), transparent 70%),
 linear-gradient(160deg, #efdfae, var(--paper) 45%, var(--paper2));
box-shadow:inset 0 0 90px rgba(101,67,33,.5), inset 0 0 14px rgba(101,67,33,.55), 0 24px 60px rgba(0,0,0,.6);
border:1px solid #8a6f3e}
.page::before{content:"";position:absolute;inset:0;background-image:GRAIN,BLOTCH;opacity:.5;
pointer-events:none;mix-blend-mode:multiply}
.page::after{content:"";position:absolute;inset:9px;border:2px solid rgba(36,26,16,.75);
outline:1px solid rgba(36,26,16,.5);outline-offset:3px;pointer-events:none}
.page>*{position:relative;z-index:1}
.sample{background:var(--accent);color:#f7ead0;text-align:center;font-family:Helvetica,Arial,sans-serif;
font-size:13px;letter-spacing:.14em;padding:8px 6px;margin:-6px 0 16px;border:1px solid #4d0f0f}
/* masthead */
.mast-top{display:flex;gap:14px;align-items:stretch}
.box{border:2.5px solid var(--rule);padding:10px 8px;text-align:center;display:flex;flex-direction:column;
justify-content:center;gap:3px;min-width:118px}
.box .big{font-family:'UnifrakturMaguntia','Old English Text MT','Cloister Black',Georgia,serif;
font-size:34px;line-height:1}
.box .sm{font-family:Helvetica,Arial,sans-serif;font-size:10px;letter-spacing:.07em;text-transform:uppercase;line-height:1.5}
.box img.mark{width:64px;height:64px;object-fit:contain;display:block;margin:0 auto}
.masthead{flex:1;text-align:center;padding:2px 4px 0}
.masthead h1{font-family:'UnifrakturMaguntia','Old English Text MT','Cloister Black','Playfair Display',Georgia,serif;
font-weight:900;font-size:clamp(40px,9vw,76px);line-height:.98;margin:0;letter-spacing:.005em}
.masthead .chronicle{font-family:Helvetica,Arial,sans-serif;font-size:12.5px;letter-spacing:.3em;
text-transform:uppercase;margin-top:8px}
.strip{display:flex;align-items:center;gap:14px;border-top:2.5px solid var(--rule);
border-bottom:1px solid var(--rule);margin-top:12px;padding:6px 2px}
.strip .mid{flex:1;text-align:center;font-family:Helvetica,Arial,sans-serif;font-size:12px;
letter-spacing:.26em;text-transform:uppercase}
.strip .orn{font-size:15px}
/* lead */
.lead{padding:20px 0 4px;border-bottom:1px solid var(--rule);text-align:center}
.lead h2{font-family:'Playfair Display',Georgia,serif;font-weight:900;font-size:clamp(38px,8.6vw,72px);
line-height:1.0;margin:0 0 12px;letter-spacing:-.005em}
.lead .standfirst{font-style:italic;font-size:clamp(17px,2.6vw,21px);line-height:1.45;color:#3d2c17;
max-width:640px;margin:0 auto 10px}
.lead .byline{display:block;text-align:center}
.lead .read{margin-top:2px}
/* sections & stories */
h3.section{font-family:'Playfair Display',Georgia,serif;font-weight:900;text-align:center;
font-size:clamp(20px,3.4vw,27px);margin:24px 0 4px;letter-spacing:.01em}
h3.section::before,h3.section::after{content:"";display:block;border-top:2.5px solid var(--rule);
margin:0 auto 7px;width:100%}
h3.section::after{border-top:1px solid var(--rule);margin:7px auto 0}
.cols{columns:3;column-gap:30px;column-rule:1px solid rgba(36,26,16,.55);padding:10px 0 2px}
@media(max-width:820px){.cols{columns:2}}
@media(max-width:560px){.cols{columns:1}}
article{break-inside:avoid;padding:8px 0 12px;border-bottom:1px dotted rgba(36,26,16,.5)}
article h4{font-family:'Playfair Display',Georgia,serif;font-weight:800;font-size:20px;line-height:1.18;
margin:0 0 6px;text-align:center}
article p{font-size:15.5px;line-height:1.52;margin:0 0 7px;text-align:justify;hyphens:auto}
article p.first::first-letter{font-family:'Playfair Display',Georgia,serif;font-weight:900;
font-size:44px;line-height:.85;float:left;padding:3px 7px 0 0}
.byline{display:flex;gap:8px;align-items:baseline;font-family:Helvetica,Arial,sans-serif;
font-size:11px;color:var(--muted);letter-spacing:.09em;text-transform:uppercase;margin:0 0 6px}
article .byline{justify-content:center;text-align:center}
a{color:var(--ink);text-decoration:none}a:hover{text-decoration:underline}
.read{display:block;text-align:center;font-family:Helvetica,Arial,sans-serif;font-size:11.5px;
color:var(--accent);letter-spacing:.1em;text-transform:uppercase}
/* the front sheet carries photographic paper material over the print */
.frontsheet{position:relative}
.frontsheet::before{content:"";position:absolute;inset:-14px -16px;background-size:cover;
background-position:center 18%;opacity:.5;mix-blend-mode:multiply;pointer-events:none}
.frontsheet>*{position:relative;z-index:1}
/* front-page composition: lead + rail */
.front{display:grid;grid-template-columns:1fr 318px;gap:28px;padding:16px 0 4px;border-bottom:1px solid var(--rule)}
@media(max-width:820px){.front{grid-template-columns:1fr}}
.front .lead{border-bottom:none;padding:0;text-align:left}
.front .lead h2{text-align:center}
.front .lead .standfirst{text-align:center}
.dateline{font-family:Helvetica,Arial,sans-serif;font-size:11.5px;letter-spacing:.16em;
text-transform:uppercase;margin:0 0 8px}
.leadbody{font-size:16.5px;line-height:1.58;text-align:justify;hyphens:auto;margin:0 0 8px}
.leadbody::first-letter{font-family:'Playfair Display',Georgia,serif;font-weight:900;
font-size:52px;line-height:.85;float:left;padding:4px 8px 0 0}
figure.plate{margin:14px 0 4px;border:1px solid rgba(36,26,16,.6);padding:6px;background:rgba(255,248,224,.35)}
figure.plate img{width:100%;display:block;filter:sepia(.25) contrast(1.02)}
figure.plate figcaption{text-align:center;font-style:italic;font-size:13px;color:#4c3a1e;padding:7px 4px 3px}
.rail{display:flex;flex-direction:column;gap:20px}
.sidebox{border:2.5px solid var(--rule);padding:14px 16px 10px;background:rgba(255,248,224,.28)}
.sidebox h5{font-family:'Playfair Display',Georgia,serif;font-weight:900;font-size:20px;
text-align:center;margin:0 0 9px;line-height:1.15}
.sidebox ul{margin:0;padding-left:19px}
.sidebox li{font-size:14.5px;line-height:1.42;margin-bottom:8px}
.pullquote{border-top:2.5px solid var(--rule);border-bottom:1px solid var(--rule);padding:12px 4px;text-align:center}
.pullquote .q{font-style:italic;font-size:19.5px;line-height:1.45}
.pullquote .attr{font-family:Helvetica,Arial,sans-serif;font-size:11px;letter-spacing:.12em;
text-transform:uppercase;color:var(--muted);margin-top:8px}
.empty,.errors{font-style:italic;color:#4c3a1e;font-size:14.5px;padding:10px 0;text-align:center}
.orn-divider{text-align:center;font-size:19px;letter-spacing:.6em;margin:16px 0 2px;color:#3d2c17}
footer{margin-top:20px;border-top:2.5px solid var(--rule);padding-top:9px;text-align:center}
footer .cols3{display:flex;justify-content:space-between;gap:10px;font-family:Helvetica,Arial,sans-serif;
font-size:11px;letter-spacing:.14em;text-transform:uppercase}
footer .fine{font-size:12.5px;font-style:italic;color:#4c3a1e;margin-top:8px}
@media(max-width:560px){.box{min-width:88px}.box .big{font-size:25px}
.masthead .chronicle{font-size:10px;letter-spacing:.18em}.strip .mid{font-size:10px;letter-spacing:.14em}}
""".replace("GRAIN", _GRAIN).replace("BLOTCH", _BLOTCH)

_FIRST_EDITION = date_type(2026, 11, 4)  # No. 1 — the day the Gazette was born


def _esc(value: str) -> str:
    return html.escape(value or "", quote=True)


_ASSET_CACHE: dict[str, str] = {}


def _asset_uri(filename: str) -> str:
    """Embed a package asset (image) as a data URI so the edition stays a
    single portable file. Empty string when missing — the page prints
    without that layer."""
    if filename in _ASSET_CACHE:
        return _ASSET_CACHE[filename]
    try:
        import base64
        from pathlib import Path
        data = (Path(__file__).parent / "assets" / filename).read_bytes()
        mime = "image/png" if filename.endswith(".png") else "image/webp"
        _ASSET_CACHE[filename] = f"data:{mime};base64," + base64.b64encode(data).decode()
    except Exception:
        _ASSET_CACHE[filename] = ""
    return _ASSET_CACHE[filename]


def _mark_uri() -> str:
    """The Nous Research mark — printed in every edition's masthead."""
    return _asset_uri("nous-mark.png")


def _artwork_uri() -> str:
    """The standing frontispiece (engraved caduceus & coffee plate)."""
    return _asset_uri("frontispiece.webp")


def _paper_uri() -> str:
    """Photographic aged-paper material for the front sheet."""
    return _asset_uri("paper.webp")


def _nice_date(iso: str) -> str:
    try:
        return date_type.fromisoformat((iso or "")[:10]).strftime("%b. %-d, %Y")
    except ValueError:
        return (iso or "")[:10]


def _issue_no(edition: dict) -> int:
    try:
        d = date_type.fromisoformat((edition.get("date") or "")[:10])
        return max(1, (d - _FIRST_EDITION).days + 1)
    except ValueError:
        return 1


def _dateline(edition: dict) -> tuple[str, str]:
    """(weekday, date) for the masthead box — abbreviated so it always fits."""
    try:
        d = date_type.fromisoformat((edition.get("date") or "")[:10])
        return d.strftime("%A").upper(), d.strftime("%b. %-d, %Y").upper()
    except ValueError:
        return "", _esc(edition.get("date") or "")


def _story_html(item: dict, lead: bool = False) -> str:
    date = (item.get("published") or "")[:10]
    summary = item.get("summary", "")
    if lead:
        standfirst = f'<p class="standfirst">{_esc(summary)}</p>' if summary else ""
        return (
            f"<article><h2>{_esc(item['title'])}</h2>{standfirst}"
            f'<p class="byline">{_esc(item.get("source", ""))} · {date}</p>'
            f'<a class="read" href="{_esc(item["link"])}">Read the source →</a></article>'
        )
    # Drop caps only earn their place on a real paragraph, not a one-liner.
    pclass = ' class="first"' if len(summary) > 140 else ""
    body = f'<p{pclass}>{_esc(summary)}</p>' if summary else ""
    return (
        f"<article><h4>{_esc(item['title'])}</h4>"
        f'<p class="byline">{_esc(item.get("source", ""))} · {_nice_date(date)}</p>'
        f"{body}"
        f'<a class="read" href="{_esc(item["link"])}">Read the source →</a></article>'
    )


def _front_html(edition: dict, lead_item: dict, rest_items: list[dict]) -> str:
    """The broadsheet front: giant lead, engraved plate, rail with the
    'What Builders Should Know' box and a pull-quote from the lead story."""
    weekday, datestr = _dateline(edition)
    summary = lead_item.get("summary", "")
    standfirst = f'<p class="standfirst">{_esc(summary)}</p>' if summary else ""
    plate = ""
    art = _artwork_uri()
    if art:
        plate = (f'<figure class="plate"><img src="{art}" alt="Engraving: the winged caduceus beside a cup of coffee">'
                 f'<figcaption>The Messenger and the Morning Cup — the Gazette\u2019s standing plate.</figcaption></figure>')
    lead = (
        f'<div class="lead"><article><h2>{_esc(lead_item["title"])}</h2>{standfirst}'
        f'<p class="dateline" style="text-align:center">From our own wires — {weekday}, {datestr}.</p>'
        f'<p class="byline" style="justify-content:center">{_esc(lead_item.get("source", ""))} · {_nice_date(lead_item.get("published", ""))}</p>'
        f'<a class="read" href="{_esc(lead_item["link"])}">Read the source →</a></article>{plate}</div>'
    )
    rail_parts = []
    if rest_items:
        bullets = "".join(
            f'<li><a href="{_esc(i["link"])}">{_esc(i["title"])}</a></li>' for i in rest_items[:5])
        rail_parts.append(
            f'<div class="sidebox"><h5>What Builders<br>Should Know</h5><ul>{bullets}</ul></div>')
    section_names = list(edition.get("sections", {}).keys())
    brief_rows = [
        f'{edition.get("story_count", 0)} stories in this edition',
        "Sections: " + " · ".join(section_names) if section_names else "",
        "Every story dated & verified before printing",
        "No story without a source link — ever",
    ]
    brief = "".join(f"<li>{_esc(r)}</li>" for r in brief_rows if r)
    rail_parts.append(f'<div class="sidebox"><h5>The Paper<br>in Brief</h5><ul>{brief}</ul></div>')
    rail = f'<div class="rail">{"".join(rail_parts)}</div>' if rail_parts else ""
    return f'<div class="front">{lead}{rail}</div>'


def render_html(edition: dict) -> str:
    sections = edition.get("sections", {})
    all_items = [i for items in sections.values() for i in items]
    lead_html, lead_item = "", None
    if all_items:
        # Editorial rule: the front page leads with the newest RELEASE when
        # the edition has one — a product release outranks a fresher commit,
        # exactly as a human editor would play it. Else, the newest story.
        lead_item = next(
            (i for i in all_items if "release" in (i.get("source", "").lower())),
            all_items[0],
        )
        lead_html = _front_html(
            edition, lead_item, [i for i in all_items if i is not lead_item])

    body_sections = []
    for name, items in sections.items():
        rest = [i for i in items if i is not lead_item]
        if not rest:
            continue
        stories = "".join(_story_html(i) for i in rest)
        body_sections.append(
            f'<h3 class="section">{_esc(name)}</h3><div class="cols">{stories}</div>')

    sample = ('<div class="sample">SAMPLE EDITION — DEMO DATA, NOT REAL NEWS</div>'
              if edition.get("is_sample") else "")
    errors = ""
    if edition.get("errors"):
        listed = "<br>".join(_esc(e) for e in edition["errors"])
        errors = f'<p class="errors">Some sources could not be reached in this edition:<br>{listed}</p>'
    empty = '<p class="empty">No fresh stories in this edition yet.</p>' if not all_items else ""
    issue = _issue_no(edition)

    paper = _paper_uri()
    material = (f'.frontsheet::before{{background-image:url("{paper}")}}'
                if paper else "")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(edition.get('title'))} — {_esc(edition.get('date'))}</title>
<style>{_CSS}{material}</style></head>
<body><main class="page">
{sample}
<div class="frontsheet">
<div class="mast-top">
  <div class="box">{f'<img class="mark" src="{_mark_uri()}" alt="Nous Research">' if _mark_uri() else '<span class="big">HG</span>'}<span class="sm">Nous Research</span><span class="sm">Daily Edition</span></div>
  <header class="masthead"><h1>{_esc(edition.get('title'))}</h1>
  <div class="chronicle">— A Chronicle of Machine Intelligence and Open Research —</div></header>
  <div class="box"><span class="sm">Vol. I — No. {issue}</span><span class="sm">{_dateline(edition)[0]}</span><span class="sm">{_dateline(edition)[1]}</span><span class="sm">Price — Free</span></div>
</div>
<div class="strip"><span class="orn">❦</span><span class="mid">Published for the builders of open intelligence</span><span class="orn">❦</span></div>
<div class="strip" style="border-top:none;margin-top:0"><span class="mid" style="letter-spacing:.12em">{edition.get('story_count', 0)} stories · every story links to its source · generated by Hermes Agent</span></div>
{lead_html}
</div>
{''.join(body_sections)}
{empty}{errors}
<div class="orn-divider">✶ ✶ ✶</div>
<footer><div class="cols3"><span>Vol. I — No. {issue}</span><span>Published for the builders of open intelligence</span><span>Free — Forever</span></div>
<div class="fine">The Hermes Gazette — built for the Nous Research community. Freshness rule: no story is printed without a verified publication date.</div></footer>
</main></body></html>
"""


def render_markdown(edition: dict) -> str:
    lines = [f"# 📰 {edition.get('title')}", f"*{edition.get('subtitle')}*",
             f"**{edition.get('date')}** · {edition.get('story_count', 0)} stories", ""]
    if edition.get("is_sample"):
        lines += ["> ⚠️ SAMPLE EDITION — demo data, not real news.", ""]
    for name, items in edition.get("sections", {}).items():
        lines.append(f"## {name}")
        for item in items:
            lines.append(f"### [{item['title']}]({item['link']})")
            lines.append(f"_{item.get('source', '')} · {(item.get('published') or '')[:10]}_")
            if item.get("summary"):
                lines.append(item["summary"])
            lines.append("")
    if edition.get("errors"):
        lines.append("---")
        lines.append("Sources that could not be reached: " + "; ".join(edition["errors"]))
    return "\n".join(lines).rstrip() + "\n"
