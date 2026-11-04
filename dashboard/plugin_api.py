"""Gazette dashboard backend — FastAPI router mounted at /api/plugins/hermes-gazette/.

Read-only: it serves the latest saved edition (JSON + a pointer to the HTML).
Generation happens through the agent tools / cron, not from the dashboard,
so opening the tab never spends model tokens or hammers feed sources.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse

router = APIRouter()

_PLUGIN_ROOT = Path(__file__).parent.parent
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))


def _latest_dir() -> Path:
    try:
        from plugins.plugin_storage import plugin_data_dir
        base = Path(plugin_data_dir("hermes-gazette"))
    except Exception:
        base = Path.home() / ".hermes" / "plugin-data" / "hermes-gazette"
    return base / "editions" / "latest"


@router.get("/latest")
def latest():
    edition_file = _latest_dir() / "edition.json"
    if not edition_file.exists():
        return JSONResponse(
            {"ok": False, "error": "No edition yet — ask your agent for the Gazette or run /gazette."},
            status_code=404,
        )
    return JSONResponse({"ok": True, "edition": json.loads(edition_file.read_text(encoding="utf-8"))})


@router.get("/latest/markdown", response_class=PlainTextResponse)
def latest_markdown():
    md = _latest_dir() / "edition.md"
    if not md.exists():
        return PlainTextResponse("No edition yet.", status_code=404)
    return PlainTextResponse(md.read_text(encoding="utf-8"), media_type="text/markdown")
