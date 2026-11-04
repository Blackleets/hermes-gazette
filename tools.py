"""Tool handlers for the Hermes Gazette plugin.

Handlers follow the Hermes plugin contract: signature (args: dict, **kwargs),
always return a JSON string, never raise.
State (editions, config) lives in the per-plugin data dir, never in the
install tree — see `hermes plugins doctor` / plugin storage docs.
"""

from __future__ import annotations

import json
from pathlib import Path

try:  # loaded as a Hermes plugin package
    from .gazette.core import build_edition, load_config
    from .gazette.render import render_html, render_markdown
except ImportError:  # standalone / tests
    from gazette.core import build_edition, load_config
    from gazette.render import render_html, render_markdown

_PLUGIN_DIR = Path(__file__).parent


def _data_dir() -> Path:
    """Per-plugin durable data dir (survives `hermes plugins update`)."""
    try:
        from plugins.plugin_storage import plugin_data_dir
        return Path(plugin_data_dir("hermes-gazette"))
    except Exception:
        fallback = Path.home() / ".hermes" / "plugin-data" / "hermes-gazette"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def _config():
    data_cfg = _data_dir() / "gazette.config.json"
    local_cfg = _PLUGIN_DIR / "gazette.config.json"
    return load_config(data_cfg if data_cfg.exists() else local_cfg)


def _save(edition: dict) -> dict:
    out = _data_dir() / "editions" / edition["date"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "edition.json").write_text(json.dumps(edition, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "edition.html").write_text(render_html(edition), encoding="utf-8")
    (out / "edition.md").write_text(render_markdown(edition), encoding="utf-8")
    latest = _data_dir() / "editions" / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    for name in ("edition.json", "edition.html", "edition.md"):
        (latest / name).write_text((out / name).read_text(encoding="utf-8"), encoding="utf-8")
    return {"dir": str(out), "html": str(out / "edition.html"), "md": str(out / "edition.md")}


def gazette_generate(args: dict, **kwargs) -> str:
    try:
        sample_items = None
        if (args or {}).get("sample"):
            sample_file = _PLUGIN_DIR / "examples" / "sample_items.json"
            sample_items = json.loads(sample_file.read_text(encoding="utf-8"))
        edition = build_edition(_config(), sample_items=sample_items)
        paths = _save(edition)
        return json.dumps({
            "ok": True,
            "date": edition["date"],
            "is_sample": edition["is_sample"],
            "story_count": edition["story_count"],
            "sections": {k: len(v) for k, v in edition["sections"].items()},
            "errors": edition["errors"],
            "files": paths,
        })
    except Exception as exc:
        return json.dumps({"ok": False, "error": f"Gazette generation failed: {exc}"})


def gazette_latest(args: dict, **kwargs) -> str:
    try:
        md = _data_dir() / "editions" / "latest" / "edition.md"
        if not md.exists():
            return json.dumps({"ok": False, "error": "No edition yet — run gazette_generate first."})
        return json.dumps({"ok": True, "markdown": md.read_text(encoding="utf-8")})
    except Exception as exc:
        return json.dumps({"ok": False, "error": f"Could not read latest edition: {exc}"})
