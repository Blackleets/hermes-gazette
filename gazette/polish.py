"""Display polish: turn raw feed text into readable newspaper copy.

Everything here is excerpting and formatting — never invention. The polish
layer may drop a repeated headline, cut a summary at a sentence boundary,
remove markdown/code punctuation and rephrase a bare version tag into a
headline ("v0.22.7" -> "Hermes Agent v0.22.7 released"). It never adds a
fact, a name or a number that was not in the fetched item.
"""

from __future__ import annotations

import re

_WS_RE = re.compile(r"\s+")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_BULLET_RE = re.compile(r"\s+-\s+(?=[A-Z(])")  # run-on " - " list separators
_VERSION_RE = re.compile(r"^[Vv]?(\d+\.\d+(?:\.\d+)?)([+\-].*)?$")

SUMMARY_LIMIT = 240
MAX_SENTENCES = 2


_ELLIPSIS_END_RE = re.compile(r"(\.\.\.|…)\s*$")
_RELEASE_DATE_RE = re.compile(r"^Release Date:\s*[A-Z][a-z]+ \d{1,2}, \d{4}\s*")
_RC_TITLE_RE = re.compile(r"^[Rr][Cc]\.(\d+)-[Vv]?(\d+\.\d+(?:\.\d+)?)$")


def _word_key(word: str) -> str:
    return word.strip(" .,;:!?¡¿\"'()[]—-").lower()


def clean_summary(raw: str | None, title: str = "", limit: int = SUMMARY_LIMIT) -> str:
    """Make a feed summary read like newspaper copy.

    - Removes markdown/code punctuation (backticks, leading hashes).
    - Drops a leading repetition of the headline (commit bodies repeat it).
    - Turns run-on " - " bullet lists into sentences.
    - Keeps at most MAX_SENTENCES sentences / `limit` chars, cut at a
      sentence boundary when possible, with an ellipsis when truncated.
    """
    if not raw:
        return ""
    text = raw.replace("`", "").replace("**", "")
    text = _WS_RE.sub(" ", text).strip()
    if text.startswith("{"):
        return ""  # machine metadata (release-automation JSON), not copy

    # Drop a leading repetition of the headline (commit bodies and release
    # notes repeat it). Word-based matching: feed titles may arrive
    # truncated with an ellipsis, so the last title word only needs to be
    # a prefix of the matching body word. Never slice by character counts
    # of a normalized string — that eats letters.
    if title:
        base = _ELLIPSIS_END_RE.sub("", title.strip())
        t_words = [k for k in (_word_key(w) for w in base.split(" ")) if k]
        b_words = text.split(" ")
        b_keys = [_word_key(w) for w in b_words]
        if t_words and len(b_keys) >= len(t_words):
            head_ok = all(b_keys[i] == t_words[i] for i in range(len(t_words) - 1))
            last_ok = b_keys[len(t_words) - 1].startswith(t_words[-1])
            if head_ok and last_ok:
                text = " ".join(b_words[len(t_words):]).lstrip(" .:;-—")

    # Boilerplate that may surface after the headline drop; the byline
    # already carries the date.
    text = _RELEASE_DATE_RE.sub("", text).strip()

    # Run-on bullets: "rows: - A failed list... - The read writes nothing".
    # A semicolon keeps the list readable without faking sentence breaks;
    # after an existing ":" or ";" a plain space avoids ":;" artifacts.
    text = re.sub(r"([:;])\s+-\s+", r"\1 ", text)
    text = _BULLET_RE.sub("; ", text)
    text = _WS_RE.sub(" ", text).strip()
    if not text:
        return ""

    sentences = [s.strip() for s in _SENTENCE_RE.split(text) if s.strip()]
    picked: list[str] = []
    total = 0
    for sentence in sentences:
        if picked and (len(picked) >= MAX_SENTENCES or total + len(sentence) > limit):
            break
        picked.append(sentence)
        total += len(sentence) + 1
    out = " ".join(picked) if picked else text
    truncated = len(out) < len(text)
    if len(out) > limit:
        out = out[:limit].rsplit(" ", 1)[0]
        truncated = True
    out = out.strip()
    if out:
        out = out[0].upper() + out[1:]
    if truncated and out and out[-1] not in ".!?":
        out = out.rstrip(" .:;-") + "…"
    return out


def humanize_release_title(title: str, source_name: str) -> tuple[str, str]:
    """Turn a bare version tag into a headline.

    Returns (headline, note). `note` is a short factual prefix for the
    summary (e.g. "Canary build.") or "" when nothing applies. Only fires
    for release feeds whose title is exactly a version string.
    """
    if "release" not in (source_name or "").lower():
        return title, ""
    product = (source_name.split("—")[0].split("-")[0] or "Release").strip()
    rc = _RC_TITLE_RE.match(title.strip())
    if rc:
        return (f"{product} v{rc.group(2)} — release candidate {rc.group(1)}",
                "Pre-release build for testing.")
    match = _VERSION_RE.match(title.strip())
    if not match:
        return title, ""
    core = "v" + match.group(1)
    suffix = (match.group(2) or "").lower()
    note = "Canary build." if "canary" in suffix else ""
    return f"{product} {core} released", note
