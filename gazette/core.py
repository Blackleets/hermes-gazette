"""Build one edition of the Gazette from configured sources."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import feeds as feedmod

# Default sources: only endpoints that follow the standard GitHub Atom
# pattern for the official NousResearch/hermes-agent repo. Users add their
# own sections/feeds in gazette.config.json — see config.example.json.
DEFAULT_CONFIG = {
    "title": "The Hermes Gazette",
    "subtitle": "The newspaper of the Nous Research ecosystem",
    "language": "en",
    "max_age_hours": 168,          # one week; the daily cron keeps editions fresh
    "max_items_per_section": 6,
    "sources": [
        {
            "name": "Hermes Agent — Releases",
            "section": "Hermes Agent",
            "url": "https://github.com/NousResearch/hermes-agent/releases.atom",
        },
        {
            "name": "Hermes Agent — Commits",
            "section": "Under the Hood",
            "url": "https://github.com/NousResearch/hermes-agent/commits/main.atom",
        },
    ],
}


def load_config(path: str | Path | None = None) -> dict:
    """Load user config if present, else the defaults (shallow-merged)."""
    config = dict(DEFAULT_CONFIG)
    if path and Path(path).exists():
        user = json.loads(Path(path).read_text(encoding="utf-8"))
        config.update({k: v for k, v in user.items() if v is not None})
    return config


def build_edition(config: dict | None = None, *, now: datetime | None = None,
                  fetcher=None, sample_items: list[dict] | None = None) -> dict:
    """Fetch, verify, dedupe and section the stories for one edition.

    - fetcher(url) -> bytes is injectable for tests/offline use.
    - sample_items bypasses fetching entirely and marks the edition as a
      SAMPLE on its front page (demo data is never presented as real news).
    - A source that fails degrades to a note in `errors`; it never kills
      the whole edition and never leaves a silent gap.
    """
    config = config or load_config()
    now = now or datetime.now(timezone.utc)
    max_age = timedelta(hours=int(config.get("max_age_hours", 168)))
    per_section = int(config.get("max_items_per_section", 6))
    fetcher = fetcher or feedmod.fetch

    errors: list[str] = []
    collected: list[dict] = []
    is_sample = sample_items is not None

    if is_sample:
        collected = list(sample_items)
    else:
        for source in config.get("sources", []):
            try:
                body = fetcher(source["url"])
                collected.extend(feedmod.parse_feed(body, source))
            except Exception as exc:  # degrade, don't die
                errors.append(f"{source.get('name', source.get('url'))}: {exc}")

    # Freshness + dedupe + sort
    seen: set[str] = set()
    fresh: list[dict] = []
    for item in collected:
        published = feedmod.parse_date(item.get("published"))
        if published is None:
            continue
        if not is_sample and now - published > max_age:
            continue
        if item["link"] in seen:
            continue
        seen.add(item["link"])
        fresh.append(item)
    fresh.sort(key=lambda i: i["published"], reverse=True)

    sections: dict[str, list[dict]] = {}
    for item in fresh:
        bucket = sections.setdefault(item.get("section", "Community"), [])
        if len(bucket) < per_section:
            bucket.append(item)

    return {
        "title": config.get("title", "The Hermes Gazette"),
        "subtitle": config.get("subtitle", ""),
        "date": now.date().isoformat(),
        "generated_at": now.isoformat(),
        "is_sample": is_sample,
        "story_count": sum(len(v) for v in sections.values()),
        "sections": sections,
        "errors": errors,
    }
