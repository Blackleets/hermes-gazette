# 📰 The Hermes Gazette

**A daily newspaper for the Nous Research / Hermes ecosystem — built as a
Hermes Agent plugin.**

Your Hermes agent reads the ecosystem's feeds, keeps only stories with a
**verified publication date**, and prints a mobile-first newsprint edition:
lead story, sections, sources linked. Read it in the Hermes dashboard, in
Hermes Desktop, or on your phone via gateway delivery.

![status](https://img.shields.io/badge/version-0.1.0-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![deps](https://img.shields.io/badge/dependencies-stdlib%20only-brightgreen) ![keys](https://img.shields.io/badge/API%20keys-none-brightgreen)

## Why

The Nous/Hermes ecosystem moves fast — releases, plugins, models, community
builds — and nobody should have to doom-scroll to keep up. The Gazette turns
it into a newspaper: one edition, finite, dated, sourced. Like the best
catalog plugins (morning-briefing, hermes-newswire), it is honest about
freshness: **no story prints without a verified date, failed sources are
declared, and demo data only ever appears in a clearly labelled SAMPLE
edition.**

## What it does

- **Feed engine (zero LLM tokens, stdlib only):** RSS 2.0, Atom and JSON Feed;
  dedupe by link; freshness window; per-source failure degrades to a note,
  never a silent gap.
- **Newspaper rendering:** a single self-contained `edition.html` — masthead,
  lead story, sections; two columns on desktop, one readable column on a
  phone. Plus `edition.md` (the phone/chat edition) and `edition.json`.
- **Hermes plugin (unified package):** tools `gazette_generate` /
  `gazette_latest`, slash command `/gazette`, a bundled editorial skill, a
  dashboard tab, and a Desktop page — one install, every surface.

## Install

```bash
hermes plugins install Blackleets/hermes-gazette
hermes plugins enable hermes-gazette
```

Or manually: copy this repo to `~/.hermes/plugins/hermes-gazette/` and enable
it in `~/.hermes/config.yaml` (`plugins.enabled: [hermes-gazette]`), then
restart Hermes / the dashboard.

Then, in chat:

```
/gazette          -> generate today's edition from your configured feeds
/gazette sample   -> the labelled SAMPLE edition (offline demo)
/gazette latest   -> read the latest saved edition
```

Validate like catalog CI does:

```bash
hermes plugins doctor . --ci
hermes plugins validate . --install-deps
```

## Configure your sources

Copy `config.example.json` to `gazette.config.json` in the plugin data dir
(`~/.hermes/plugin-data/hermes-gazette/`) and edit the `sources` list. Each
source is `{name, section, url}` pointing at any RSS/Atom/JSON feed. Defaults
follow the official `NousResearch/hermes-agent` GitHub Atom feeds; add
community blogs, subreddit RSS, other GitHub repos, or an X RSS bridge you
control.

## Read it on your phone

Short version: a daily Hermes cron generates the edition and your gateway
delivers the Markdown + HTML to your phone; the dashboard Gazette tab is
mobile-responsive. Hermes Mobile access is rolling out via waitlist and has
no public third-party plugin SDK yet — see **[docs/mobile.md](docs/mobile.md)**
for the honest breakdown and the plan to adopt the official surface when it
lands.

## Use it without Hermes

```bash
python scripts/generate_edition.py --sample   # offline demo edition
python scripts/generate_edition.py            # live edition from default feeds
```

## Tests

```bash
python -m pytest tests/ -q
```

Offline tests cover feed parsing (undated stories are dropped), the
freshness rule, graceful source failure, sample labelling, and plugin
registration through a fake Hermes context.

## Layout

```
plugin.yaml                  manifest (name, tools, config schema)
__init__.py                  register(ctx): tools, /gazette command, bundled skill
schemas.py / tools.py        tool definitions and handlers
gazette/                     the engine: feeds.py, core.py, render.py (stdlib only)
skills/hermes-gazette/       editorial skill (freshness + honesty rules, delivery)
dashboard/                   web dashboard tab (manifest.json, dist/, plugin_api.py)
desktop/plugin.js            Hermes Desktop page (Desktop Plugin SDK)
scripts/generate_edition.py  standalone CLI
examples/sample_items.json   demo data — only used by the labelled SAMPLE edition
docs/mobile.md               the honest mobile story
```

## Roadmap

- Adopt the official Hermes Mobile plugin surface when Nous publishes one.
- Per-user sections/topics config in the Desktop settings form.
- Submit to the official Hermes Plugin Catalog (submission pack prepared).

## License

MIT — see `LICENSE`.

---

### Resumen en español

**The Hermes Gazette** es un plugin para Hermes Agent (Nous Research) que
genera un periódico diario del ecosistema: recoge feeds RSS/Atom/JSON,
verifica la fecha de cada historia (sin fecha verificada, no se publica),
deduplica y maqueta una edición tipo periódico pensada para móvil (HTML +
Markdown + JSON). Se instala con `hermes plugins install`, añade las
herramientas `gazette_generate`/`gazette_latest`, el comando `/gazette`, una
skill editorial, pestaña en el dashboard y página en Hermes Desktop. La
edición diaria puede llegar al móvil por el gateway/cron de Hermes; la app
móvil nativa de Hermes está en lista de espera y aún no tiene SDK público de
plugins — el detalle honesto está en `docs/mobile.md`.
