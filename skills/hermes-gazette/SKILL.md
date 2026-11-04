---
name: hermes-gazette
description: "Produce the daily Hermes Gazette — a newspaper-style edition about the Nous Research / Hermes ecosystem: verified, dated stories only, rendered as a mobile-first newspaper page and delivered to the user's phone."
version: 0.7.0
author: Lee Renteria (Blackleets)
license: MIT
platforms: [macos, linux, windows]
---

# Hermes Gazette — editorial skill

Use this skill when the user asks for the Gazette, the newspaper, the daily
Nous/Hermes edition, or when the daily Gazette cron fires.

## Editorial rules (non-negotiable)

1. **Every story needs a verified publication date.** If a story has no date
   you can check, it does not print. Never backfill news from memory.
2. **Never invent stories, quotes, dates or numbers.** A thin edition is
   honest; a fabricated one kills the paper's credibility.
3. **Every story links to its source.** No source link, no story.
4. **A failed source is declared, not hidden.** The edition lists sources
   that could not be reached.
5. Sample/demo data is only ever printed in the SAMPLE edition, which is
   labelled as demo data on its front page.

## Procedure

1. Run the `gazette_generate` tool (or `/gazette`). It fetches the configured
   feeds, applies the freshness window, dedupes and saves
   `edition.html` / `edition.md` / `edition.json` in the plugin data dir.
2. Read the result JSON. If `story_count` is 0, tell the user plainly and
   show the source errors — do not pad the edition.
3. Optional curation pass (only with sources in hand): reorder sections,
   write a one-line standfirst for the lead story. Do not add facts that are
   not in the fetched items.
4. **Plain-language pass (the polish that makes it a newspaper, not a log):**
   technical feeds (commits, changelogs) arrive as developer notes. Before
   delivering, you MAY rewrite a story's summary in plain language under
   these rules — and only these:
   - Rewrite **only from that story's fetched text**. Every name, number,
     date and claim in your version must already be in the fetched item.
   - Say what changed and why it matters to a reader, in at most 2 short
     sentences. Drop code identifiers, file paths and internal jargon.
   - Never soften a fact into a different fact: "rooms survive a failed bot
     list" stays exactly that claim, just readable.
   - Keep the story's link, date and source untouched. If you are unsure a
     rewrite is faithful, keep the engine's summary instead.
   - Example — fetched: "fix(bot-mode): gateway rooms survive a failed bot
     list and never resurrect. Review fixes on the roster's gateway Group
     Chat rows: a failed bot list no longer hides gateway rooms…"
     Plain: "Group chat rooms no longer disappear when the bot list fails
     to load, and rooms from a disbanded group no longer come back."
4. Deliver:
   - **Chat / mobile gateway:** send the Markdown edition (or attach the HTML).
   - **Dashboard / desktop:** the Gazette tab reads the same saved edition.
   - **Daily routine:** a Hermes cron at the configured hour runs this skill
     and delivers to the user's home device (see `docs/mobile.md`).

## Configuration

Sources live in `gazette.config.json` in the plugin data dir
(`~/.hermes/plugin-data/hermes-gazette/`). Start from `config.example.json`
in the repo. Each source is `{name, section, url}` pointing at an RSS, Atom
or JSON Feed. Add community feeds (blogs, Reddit RSS, GitHub repos, X via an
RSS bridge the user provides) — the engine verifies dates for all of them.
