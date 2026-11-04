"""Hermes Gazette — a newspaper engine for the Nous / Hermes ecosystem.

Stdlib-only. No API keys, no LLM tokens for the feed engine itself:
fetch -> verify dates -> dedupe -> render (HTML + Markdown + JSON).
"""

from .core import build_edition, load_config, DEFAULT_CONFIG
from .render import render_html, render_markdown

__all__ = ["build_edition", "load_config", "DEFAULT_CONFIG", "render_html", "render_markdown"]
__version__ = "0.7.0"
