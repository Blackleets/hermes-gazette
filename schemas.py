"""Tool schemas — what the LLM sees."""

GAZETTE_GENERATE = {
    "name": "gazette_generate",
    "description": (
        "Generate today's edition of The Hermes Gazette: fetch the configured "
        "Nous/Hermes ecosystem feeds, keep only stories with a verified "
        "publication date, dedupe, and save the edition as HTML (mobile-first "
        "newspaper), Markdown and JSON. Returns a short JSON summary."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "sample": {
                "type": "boolean",
                "description": "Build the clearly-labelled SAMPLE edition from bundled demo data instead of live feeds.",
                "default": False,
            }
        },
        "required": [],
    },
}

GAZETTE_LATEST = {
    "name": "gazette_latest",
    "description": (
        "Return the most recent saved Gazette edition as Markdown (for reading "
        "in chat or delivery to a phone). If no edition exists yet, say so — "
        "never invent one."
    ),
    "parameters": {"type": "object", "properties": {}, "required": []},
}
