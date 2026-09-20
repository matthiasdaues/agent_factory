"""Load agent definitions from YAML frontmatter."""

from __future__ import annotations

from pathlib import Path

import yaml


def _parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        data = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def load_agent_definitions(agents_dir: Path | None = None) -> list[dict]:
    if agents_dir is None:
        agents_dir = Path(__file__).resolve().parent.parent / "agents"

    agents = []
    for path in sorted(agents_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm = _parse_frontmatter(text)
        if fm.get("name"):
            agents.append(fm)
    return agents
