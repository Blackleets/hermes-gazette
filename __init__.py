"""Hermes Gazette plugin — registration.

Wires the gazette tools, the /gazette slash command and the bundled skill
into Hermes, using only the public plugin surface (register(ctx)).
"""

import logging
import sys
from pathlib import Path

try:  # normal path: Hermes loads this directory as a package
    from . import schemas, tools
except ImportError:  # standalone import (e.g. pytest package-node setup)
    sys.path.insert(0, str(Path(__file__).parent))
    import schemas  # type: ignore
    import tools  # type: ignore

logger = logging.getLogger(__name__)


def _gazette_command(raw_args: str) -> str:
    """Implement /gazette [sample] — generate (or show) today's edition."""
    raw = (raw_args or "").strip().lower()
    if raw in ("latest", "show", "read"):
        import json
        result = json.loads(tools.gazette_latest({}))
        return result.get("markdown", result.get("error", "No edition available."))
    result = tools.gazette_generate({"sample": raw == "sample"})
    import json
    summary = json.loads(result)
    if not summary.get("ok"):
        return f"📰 Gazette failed: {summary.get('error')}"
    kind = "SAMPLE edition" if summary.get("is_sample") else "edition"
    return (f"📰 The Hermes Gazette {kind} for {summary['date']} is ready: "
            f"{summary['story_count']} stories. HTML: {summary['files']['html']}")


def register(ctx):
    ctx.register_tool(name="gazette_generate", toolset="hermes-gazette",
                      schema=schemas.GAZETTE_GENERATE, handler=tools.gazette_generate)
    ctx.register_tool(name="gazette_latest", toolset="hermes-gazette",
                      schema=schemas.GAZETTE_LATEST, handler=tools.gazette_latest)
    ctx.register_command("gazette", _gazette_command,
                         description="Generate or read today's Hermes Gazette newspaper")

    skills_dir = Path(__file__).parent / "skills"
    if skills_dir.exists():
        for child in sorted(skills_dir.iterdir()):
            skill_md = child / "SKILL.md"
            if child.is_dir() and skill_md.exists():
                ctx.register_skill(child.name, skill_md)

    logger.info("hermes-gazette registered: gazette_generate, gazette_latest, /gazette")
