# Reading the Gazette on your phone — what works today, honestly

Hermes Mobile was announced at NousCon 2026 and access is rolling out via
waitlist/beta. There is **no public third-party plugin SDK for the native
mobile app yet**, so this plugin does not claim to live "inside" the mobile
app. Instead it reaches your phone through the surfaces Hermes already has:

## 1. Gateway delivery (works today, any Hermes install)

Hermes talks to you on Telegram, Discord, Slack, WhatsApp, Signal and email
through its gateway, and cron jobs can deliver to a chosen device — including
through the community `hermes-mobile` WebSocket platform plugin.

Set up the daily edition once, in chat with your agent:

> "Set up the Hermes Gazette every day at 08:00 and send it to my phone."

The bundled skill (`skills/hermes-gazette`) creates a Hermes cron that runs
`gazette_generate` and delivers the Markdown edition (short, phone-readable)
with the HTML newspaper attached. The Markdown is the phone edition: lead
story first, sources linked, no padding.

## 2. The dashboard on a phone browser (works today)

`hermes dashboard` + this plugin adds a **Gazette** tab whose layout is
mobile-first: one column under 640px, big serif headlines, no horizontal
scroll. Open the dashboard from your phone browser and the newspaper reads
like a newspaper.

## 3. The standalone HTML edition (works everywhere)

Every edition is a single self-contained `edition.html` (no external assets).
Save it, share it, print it, open it in any mobile browser — it is the same
file the dashboard tab renders from the same saved data.

## When Hermes Mobile opens a plugin surface

The edition data is a stable JSON (`edition.json`) and the rendering layer is
separate from the feed engine, so a native mobile view only needs to read
`/api/plugins/hermes-gazette/latest` — the same endpoint the dashboard and
desktop plugins already use. The repo will adopt the official mobile plugin
surface when Nous publishes one, rather than faking one today.
