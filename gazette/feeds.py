"""Feed fetching and parsing — RSS 2.0, Atom and JSON Feed, stdlib only.

Design rules (learned from the Hermes plugin catalog's news plugins):
- http/https only; no file/ftp; short timeouts; body size cap.
- Every item MUST carry a parseable publication date. Undated items are
  dropped, never backfilled from model memory — a thin edition is honest,
  stale or invented news is not.
- All feed HTML is stripped before storage/rendering.
"""

from __future__ import annotations

import html
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from . import polish as polishmod

MAX_BODY = 5 * 1024 * 1024  # 5 MB, same cap as hermes-newswire
TIMEOUT = 15

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
# Conventional-commit prefixes ("fix(bot-mode): ", "docs: ") read terribly as
# newspaper headlines — strip them for display; the link keeps the original.
_CC_PREFIX_RE = re.compile(
    r"^(feat|fix|docs|chore|refactor|test|build|ci|perf|style|revert)(\([^)]*\))?!?:\s+",
    re.IGNORECASE,
)


def headline(title: str) -> str:
    cleaned = _CC_PREFIX_RE.sub("", title).strip()
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned


def clean_text(value: str | None, limit: int = 600) -> str:
    if not value:
        return ""
    text = html.unescape(_TAG_RE.sub(" ", value))
    text = _WS_RE.sub(" ", text).strip()
    return text[:limit]


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    # RFC 822 (RSS)
    try:
        dt = parsedate_to_datetime(value)
        if dt is not None:
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        pass
    # ISO 8601 (Atom / JSON Feed)
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def fetch(url: str) -> bytes:
    if not url.startswith(("https://", "http://")):
        raise ValueError(f"Refused non-http(s) feed URL: {url}")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "HermesGazette/0.7 (+https://github.com/Blackleets/hermes-gazette)"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        body = resp.read(MAX_BODY + 1)
    if len(body) > MAX_BODY:
        raise ValueError(f"Feed too large: {url}")
    return body


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _children_text(elem, names: set[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for child in elem:
        name = _local(child.tag)
        if name in names and child.text:
            out[name] = child.text.strip()
        # Atom link is an attribute, not text
        if name == "link":
            href = child.get("href")
            rel = child.get("rel", "alternate")
            if href and rel == "alternate":
                out["link"] = href
            elif child.text and "link" not in out:
                out["link"] = child.text.strip()
    return out


def parse_feed(body: bytes, source: dict) -> list[dict]:
    """Parse one feed body into normalized items for one source."""
    text = body.decode("utf-8", errors="replace").strip()
    items: list[dict] = []

    if text.startswith("{"):
        data = json.loads(text)
        for entry in data.get("items", []):
            published = parse_date(entry.get("date_published") or entry.get("date_modified"))
            if published is None:
                continue
            items.append(_item(entry.get("title"), entry.get("url") or entry.get("external_url"),
                               entry.get("summary") or entry.get("content_text"), published, source))
        return [i for i in items if i]

    root = ET.fromstring(text)
    # RSS: root/channel/item ; Atom: root/entry (namespaced)
    entries = [e for e in root.iter() if _local(e.tag) in ("item", "entry")]
    for entry in entries:
        fields = _children_text(entry, {"title", "link", "description", "summary",
                                        "content", "pubDate", "published", "updated", "date"})
        published = parse_date(fields.get("pubDate") or fields.get("published") or fields.get("updated"))
        if published is None:
            continue
        item = _item(fields.get("title"), fields.get("link"),
                     fields.get("summary") or fields.get("description") or fields.get("content"),
                     published, source)
        if item:
            items.append(item)
    return items


def _item(title, link, summary, published: datetime, source: dict) -> dict | None:
    title = headline(clean_text(title, 240))
    link = (link or "").strip()
    if not title or not link.startswith(("https://", "http://")):
        return None
    title, note = polishmod.humanize_release_title(title, source.get("name", ""))
    summary_raw = _CC_PREFIX_RE.sub("", clean_text(summary, 900)).strip()
    summary_text = polishmod.clean_summary(summary_raw, title=title)
    if not summary_text:
        summary_text = note  # e.g. release-candidate metadata is not copy
    elif note and note.split()[0].lower() not in summary_text.lower():
        summary_text = f"{note} {summary_text}"
    return {
        "title": title,
        "link": link,
        "summary": summary_text,
        "published": published.astimezone(timezone.utc).isoformat(),
        "source": source.get("name", "Unknown source"),
        "section": source.get("section", "Community"),
    }
