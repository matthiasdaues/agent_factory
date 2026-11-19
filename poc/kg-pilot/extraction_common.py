"""Shared helpers for the extraction scripts."""

from __future__ import annotations

import json
from pathlib import Path

EXTRACTIONS = {"local": Path("out/extraction-local.json"), "claude": Path("out/extraction-claude.json")}


def norm(text: str) -> str:
    return " ".join(text.split())


def load_spans(path: Path) -> dict[str, dict]:
    return {s["span_id"]: s for s in (json.loads(line) for line in path.open(encoding="utf-8"))}


def load_extraction(name: str) -> dict:
    return json.loads(EXTRACTIONS[name].read_text(encoding="utf-8"))


def quote_check(decision: dict, spans: dict[str, dict]) -> str:
    """exact, whitespace (only whitespace differs), or missing; unknown_span if the id does not exist."""
    span = spans.get(str(decision.get("span_id", "")).strip())
    if span is None:
        return "unknown_span"
    quote = decision.get("quote", "")
    if quote and quote in span["text"]:
        return "exact"
    if quote and norm(quote) in norm(span["text"]):
        return "whitespace"
    return "missing"
