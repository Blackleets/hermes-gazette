"""Offline tests: feed parsing, freshness rules, rendering, plugin registration."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from gazette.core import build_edition
from gazette.feeds import parse_feed
from gazette.render import render_html, render_markdown

RSS = b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>t</title>
<item><title>Fresh story</title><link>https://example.com/a</link>
<description>Something happened.</description>
<pubDate>Tue, 03 Nov 2026 10:00:00 GMT</pubDate></item>
<item><title>Undated story</title><link>https://example.com/b</link>
<description>No date - must be dropped.</description></item>
</channel></rss>"""

ATOM = b"""<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<entry><title>Atom story</title><link href="https://example.com/c"/>
<summary>Atom works.</summary><updated>2026-11-03T12:00:00Z</updated></entry>
</feed>"""

NOW = datetime(2026, 11, 4, 9, 0, tzinfo=timezone.utc)
SOURCE = {"name": "Test Wire", "section": "Hermes Agent"}


def test_rss_drops_undated():
    items = parse_feed(RSS, SOURCE)
    assert [i["title"] for i in items] == ["Fresh story"]


def test_atom_parses():
    items = parse_feed(ATOM, SOURCE)
    assert len(items) == 1 and items[0]["link"] == "https://example.com/c"


def test_stale_story_not_printed():
    cfg = {"title": "T", "sources": [], "max_age_hours": 24}
    old = [{"title": "Old", "link": "https://example.com/old", "summary": "",
            "published": "2026-10-01T00:00:00+00:00", "source": "S", "section": "X"}]
    edition = build_edition(cfg, now=NOW, sample_items=None, fetcher=lambda u: b"")
    assert edition["story_count"] == 0
    # sample path bypasses freshness but is labelled
    sample = build_edition(cfg, now=NOW, sample_items=old)
    assert sample["is_sample"] is True and sample["story_count"] == 1


def test_failing_source_degrades_with_note():
    cfg = {"title": "T", "sources": [{"name": "Down", "section": "X", "url": "https://x.invalid/feed"}]}
    edition = build_edition(cfg, now=NOW, fetcher=lambda u: (_ for _ in ()).throw(OSError("boom")))
    assert edition["story_count"] == 0 and edition["errors"] and "Down" in edition["errors"][0]


def test_render_marks_sample_and_links_source():
    cfg = {"title": "The Hermes Gazette", "subtitle": "s", "sources": []}
    items = json.loads((Path(__file__).parent.parent / "examples" / "sample_items.json").read_text())
    edition = build_edition(cfg, now=NOW, sample_items=items)
    html_out = render_html(edition)
    assert "SAMPLE EDITION" in html_out and "https://example.com/gazette-demo/lead" in html_out
    md_out = render_markdown(edition)
    assert md_out.startswith("# 📰") and "SAMPLE EDITION" in md_out


def test_plugin_registration_with_fake_ctx():
    registered = {"tools": [], "commands": [], "skills": []}

    class FakeCtx:
        def register_tool(self, name, toolset, schema, handler, **kw):
            registered["tools"].append(name)
        def register_command(self, name, handler, description=""):
            registered["commands"].append(name)
        def register_skill(self, name, path):
            registered["skills"].append(name)

    # Load the plugin package the way Hermes does: as a package directory.
    import importlib.util
    root = Path(__file__).parent.parent
    spec = importlib.util.spec_from_file_location(
        "hermes_gazette_plugin", root / "__init__.py",
        submodule_search_locations=[str(root)])
    mod = importlib.util.module_from_spec(spec)
    sys.modules["hermes_gazette_plugin"] = mod
    spec.loader.exec_module(mod)
    mod.register(FakeCtx())
    assert registered["tools"] == ["gazette_generate", "gazette_latest"]
    assert registered["commands"] == ["gazette"]
    assert registered["skills"] == ["hermes-gazette"]


def test_headline_strips_conventional_commit_prefix():
    from gazette.feeds import headline
    assert headline("fix(bot-mode): gateway rooms survive a failed bot list") == \
        "Gateway rooms survive a failed bot list"
    assert headline("docs: link Sprites to fly.io/sprites") == "Link Sprites to fly.io/sprites"
    assert headline("A normal headline stays") == "A normal headline stays"


def test_clean_summary_drops_repeated_headline_and_bullets():
    from gazette.polish import clean_summary
    raw = ("gateway rooms survive a failed bot list and never resurrect "
           "Review fixes on the roster rows: - A failed or still-loading bot list "
           "no longer hides gateway rooms. - The `groups.list` read writes nothing.")
    out = clean_summary(raw, title="Gateway rooms survive a failed bot list and never resurrect")
    assert "gateway rooms survive" not in out.lower()[:20] or out.startswith("Review")
    assert "`" not in out
    assert out[0].isupper()


def test_clean_summary_caps_sentences_and_marks_truncation():
    from gazette.polish import clean_summary
    raw = "First real sentence here. Second one follows it. Third should be cut off entirely now."
    out = clean_summary(raw, title="Unrelated headline")
    assert out.startswith("First real sentence here.")
    assert "Third" not in out


def test_humanize_release_title():
    from gazette.polish import humanize_release_title
    title, note = humanize_release_title("V0.22.7+canary.20261104T064347Z", "Hermes Agent — Releases")
    assert title == "Hermes Agent v0.22.7 released"
    assert note == "Canary build."
    title2, note2 = humanize_release_title("Some feature announcement", "Hermes Agent — Releases")
    assert title2 == "Some feature announcement" and note2 == ""


def test_default_commits_section_is_under_the_hood():
    from gazette.core import DEFAULT_CONFIG
    sections = {s["name"]: s["section"] for s in DEFAULT_CONFIG["sources"]}
    assert sections["Hermes Agent — Commits"] == "Under the Hood"
    assert sections["Hermes Agent — Releases"] == "Hermes Agent"


def test_clean_summary_handles_truncated_feed_title_and_json():
    from gazette.polish import clean_summary
    raw = ("gateway rooms survive a failed bot list and never resurrect "
           "Review fixes on the roster rows. A failed bot list no longer hides rooms.")
    out = clean_summary(raw, title="Gateway rooms survive a failed bot list and never resu…")
    assert out.startswith("Review fixes on the roster rows.")
    assert clean_summary('{"attempt":1,"autopublish":false}', title="Rc.1-v0.22.7") == ""


def test_humanize_release_candidate_title():
    from gazette.polish import humanize_release_title
    title, note = humanize_release_title("Rc.1-v0.22.7", "Hermes Agent — Releases")
    assert title == "Hermes Agent v0.22.7 — release candidate 1"
    assert note == "Pre-release build for testing."


def test_front_page_leads_with_release_over_newer_commit():
    from gazette.render import render_html
    edition = {
        "title": "The Hermes Gazette", "subtitle": "x", "date": "2026-11-04",
        "story_count": 2, "is_sample": False, "errors": [],
        "sections": {"Under the Hood": [
            {"title": "Fix the minimal working example", "link": "https://example.com/c1",
             "summary": "A commit.", "published": "2026-11-04T15:00:00+00:00",
             "source": "Hermes Agent — Commits", "section": "Under the Hood"},
        ], "Hermes Agent": [
            {"title": "Hermes Agent v9.9.9 released", "link": "https://example.com/r1",
             "summary": "A release.", "published": "2026-11-04T09:00:00+00:00",
             "source": "Hermes Agent — Releases", "section": "Hermes Agent"},
        ]},
    }
    out = render_html(edition)
    assert out.index("Hermes Agent v9.9.9 released") < out.index("What Builders")
