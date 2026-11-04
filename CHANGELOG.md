# Changelog

## 0.7.0 — 2026-11-04 · the illustrated cover, with real words

- **Cover system** (`scripts/make_cover.py`, optional Pillow + ffmpeg):
  a FIXED illustrated front-page frame (blackletter masthead, engraved
  caduceus & coffee plate, aged paper, torn edges — generated once, no
  variable text) + the day's REAL data typeset into it in the locked
  typography (Playfair Display, OFL): the Nous mark in its box, the
  Vol./No./date/Price box, and the giant lead headline under the same
  editorial rule as the front page (newest release leads). The frame's
  ghost print is faded to pure texture before composition — every
  readable word on the cover comes from the edition itself.

## 0.6.0 — 2026-11-04 · the mark, always

- **The Nous Research mark prints in every edition's masthead** (left box,
  ink on the paper) — Lee's rule: "el logo siempre". Extracted to clean
  transparent ink from the mark he supplied.
- **Typography locked by the same rule:** blackletter masthead, Playfair
  headlines, Georgia body — the same in every edition, never restyled
  per issue.

## 0.5.0 — 2026-11-04 · the material of paper

- **Photographic paper material:** the front sheet now prints over a real
  aged-paper photograph (fibers, foxing, water stains — generated as a
  blank material asset, embedded in the edition), multiplied into the
  print instead of a flat CSS gradient. The paper reads as paper.
- **Photographed front-page poster** (`scripts/make_poster.py`, optional
  playwright + ffmpeg): the edition's face for delivery and sharing —
  the sheet graded like a photograph of a printed broadsheet: paper
  material over the sheet, warm light, film grain, vignette, soft shadow.
  The readable edition stays HTML behind it, links intact.

## 0.4.0 — 2026-11-04 · the full broadsheet system

- **Front page composed like the reference broadsheets:** giant lead
  headline with italic standfirst and a "From our own wires" dateline,
  the standing engraved plate (caduceus & morning cup, generated in the
  antique style, embedded as data — the edition stays one portable file),
  and a rail with "What Builders Should Know" (the day's next stories,
  linked) and "The Paper in Brief" (the edition's real numbers).
- **Editorial lead rule:** the front page leads with the newest release
  when the edition has one; a fresher commit no longer takes the front
  page from a product release.
- Bylines get newspaper dates ("Nov. 4, 2026"). 14 offline tests.

## 0.3.0 — 2026-11-04 · the vintage broadsheet

- **New skin, same paper:** the edition now renders as an antique
  broadsheet — aged sepia paper with procedural grain and blotches (SVG,
  no image files), a framed page, blackletter masthead with volume/date/
  price boxes, the builders' strip, a giant lead headline with italic
  standfirst, justified columns with rules and drop caps on real
  paragraphs.
- **Honest furniture:** the issue number is real (days since the first
  edition: 2026-11-04 = No. 1) and the price box says "Free".
- Dashboard tab and desktop page inherit the new look automatically.

## 0.2.0 — 2026-11-04 · the readability release

- **Readable headlines:** conventional-commit prefixes (`fix(bot-mode): …`)
  are stripped for display; the source link keeps the original.
- **Human release headlines:** a bare version tag (`v0.22.7+canary.…`) now
  prints as "Hermes Agent v0.22.7 released", and `rc.1-v0.22.7` as
  "Hermes Agent v0.22.7 — release candidate 1".
- **Clean summaries (new `gazette/polish.py`):** headline repetitions are
  dropped word-safely, run-on bullet lists become readable sentences,
  "Release Date:" boilerplate is removed (the byline carries the date), and
  release-automation JSON metadata never prints as copy.
- **Sections:** developer commits move to their own "Under the Hood"
  section instead of crowding the front page.
- **Editorial skill:** a plain-language pass lets the agent rewrite
  technical summaries strictly from the fetched text — same facts, readable
  words, link and date untouched.
- 13 offline tests (was 6).

## 0.1.0 — 2026-11-04 · first release

- Feed engine (RSS 2.0 / Atom / JSON Feed, stdlib only): verified dates or
  no story, per-source failure declared on the front page.
- Mobile-first newsprint rendering (HTML / Markdown / JSON) from one model.
- Unified Hermes plugin: `gazette_generate` / `gazette_latest` tools,
  `/gazette` command, bundled editorial skill, dashboard tab, desktop page.
- Standalone CLI (`scripts/generate_edition.py`), sample edition clearly
  labelled as demo data, 6 offline tests.
