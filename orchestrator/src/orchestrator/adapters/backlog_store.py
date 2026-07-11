"""Markdown-backed backlog store (ADR-0008)."""

from __future__ import annotations

import os
import re
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from orchestrator.entities import Story, Tier, StoryStatus

_STORY_ID_RE = re.compile(r"^ST-\d{4,}$")


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _parse_yaml_value(raw: str) -> Any:
    value = raw.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_unquote(item.strip()) for item in inner.split(",") if item.strip()]
    if value in {"", "~", "null"}:
        return None
    return _unquote(value)


class MarkdownBacklogStore:
    """Reads story frontmatter from ``backlog/ST-NNNN.md`` files."""

    def __init__(self, backlog_dir: Path) -> None:
        self.backlog_dir = backlog_dir

    def list_stories(self) -> List[Story]:
        stories = [
            self._to_story(self._parse_frontmatter(path.read_text(encoding="utf-8"))[0])
            for path in self.backlog_dir.glob("ST-*.md")
        ]
        return sorted(stories, key=lambda story: story.id)

    def get_story(self, story_id: str) -> Story:
        """Return the story's full frontmatter and prose body (FR-U5, BR-060)."""
        path = self._story_path(story_id)
        if not path.is_file():
            raise KeyError(story_id)
        fm, body = self._parse_frontmatter(path.read_text(encoding="utf-8"))
        return self._to_story(fm, body=body)

    def stories_by_epic(self) -> Dict[str, List[Story]]:
        """Group the loaded snapshot's stories under their epic (FR-U3, BR-059).

        Read-only: derived entirely from :meth:`list_stories`, no extra file
        access and no mutation of backlog data.
        """
        grouped: "OrderedDict[str, List[Story]]" = OrderedDict()
        for story in self.list_stories():
            grouped.setdefault(story.epic, []).append(story)
        return {epic: grouped[epic] for epic in sorted(grouped)}

    def ready_stories(self) -> List[Story]:
        """Return pending stories whose every dep resolves to a done story.

        Evaluated against a single loaded snapshot (FR-U4, BR-057, VR-040):
        an empty ``deps`` list is trivially satisfied; a dep id that is not
        present in the snapshot, or that resolves to a non-``done`` story,
        excludes the story.
        """
        snapshot = self.list_stories()
        by_id = {story.id: story for story in snapshot}
        return [
            story
            for story in snapshot
            if story.status is StoryStatus.PENDING
            and all(
                by_id.get(dep_id) is not None
                and by_id[dep_id].status is StoryStatus.DONE
                for dep_id in story.deps
            )
        ]

    def update_status(self, story_id: str, new_status: str) -> None:
        path = self._story_path(story_id)
        if not path.is_file():
            raise KeyError(story_id)

        new_value = StoryStatus(new_status).value
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        end_idx = self._frontmatter_end_index(lines)

        for index in range(1, end_idx):
            if not re.match(r"^\s*status\s*:", lines[index]):
                continue

            newline = ""
            if lines[index].endswith("\r\n"):
                newline = "\r\n"
                content = lines[index][:-2]
            elif lines[index].endswith("\n"):
                newline = "\n"
                content = lines[index][:-1]
            else:
                content = lines[index]

            match = re.match(r"^(\s*status\s*:\s*).*$", content)
            if match is None:
                break
            lines[index] = f"{match.group(1)}{new_value}{newline}"
            temp = path.parent / f".{path.name}.{os.getpid()}.tmp"
            try:
                temp.write_text("".join(lines), encoding="utf-8")
                os.replace(temp, path)
            finally:
                if temp.exists():
                    temp.unlink()
            return

        raise ValueError(f"Story {story_id} is missing a status field")

    def _parse_frontmatter(self, text: str) -> Tuple[Dict[str, Any], str]:
        lines = text.split("\n")
        if not lines or lines[0].strip() != "---":
            raise ValueError("Missing YAML frontmatter")

        end_idx = None
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                end_idx = index
                break
        if end_idx is None:
            raise ValueError("Missing YAML frontmatter terminator")

        fm: Dict[str, Any] = {}
        current_key: str | None = None
        current_list: List[str] | None = None

        for line in lines[1:end_idx]:
            list_item = re.match(r"^\s*-\s+(.+)$", line)
            if list_item and current_key is not None:
                if current_list is None:
                    current_list = []
                current_list.append(_unquote(list_item.group(1).strip()))
                continue

            if current_key is not None and current_list is not None:
                fm[current_key] = current_list
                current_key = None
                current_list = None

            match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$", line)
            if match is None:
                continue

            key, raw_value = match.group(1), match.group(2).strip()
            if raw_value:
                fm[key] = _parse_yaml_value(raw_value)
                current_key = None
                current_list = None
                continue

            fm[key] = None
            current_key = key
            current_list = None

        if current_key is not None and current_list is not None:
            fm[current_key] = current_list

        body = "\n".join(lines[end_idx + 1 :])
        return fm, body

    def _to_story(self, fm: Dict[str, Any], body: str = "") -> Story:
        required = {"id", "epic", "title", "tier", "status"}
        missing = sorted(
            field for field in required if field not in fm or fm[field] is None
        )
        if missing:
            raise ValueError(f"story frontmatter missing required fields: {missing}")
        return Story(
            id=str(fm["id"]),
            epic=str(fm["epic"]),
            title=str(fm["title"]),
            tier=Tier(str(fm["tier"])),
            status=StoryStatus(str(fm["status"])),
            deps=list(fm.get("deps") or []),
            traces=list(fm.get("traces") or []),
            outputs=list(fm.get("outputs") or []),
            body=body,
        )

    def _frontmatter_end_index(self, lines: List[str]) -> int:
        if not lines or lines[0].strip() != "---":
            raise ValueError("Missing YAML frontmatter")
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                return index
        raise ValueError("Missing YAML frontmatter terminator")

    def _story_path(self, story_id: str) -> Path:
        if not _STORY_ID_RE.match(story_id):
            raise KeyError(f"invalid story id: {story_id}")

        root = self.backlog_dir.resolve()
        path = (self.backlog_dir / f"{story_id}.md").resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise KeyError(f"path traversal in story id: {story_id}") from exc
        return path
