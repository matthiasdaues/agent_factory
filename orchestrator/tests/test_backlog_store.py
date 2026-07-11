from __future__ import annotations

import os
import textwrap
from pathlib import Path

import pytest

from orchestrator.adapters.backlog_store import MarkdownBacklogStore
from orchestrator.entities import Tier, StoryStatus


def _write_story(backlog_dir: Path, story_id: str, content: str) -> Path:
    path = backlog_dir / f"{story_id}.md"
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    return path


def test_list_stories_returns_all_stories_sorted(tmp_path: Path):
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    _write_story(
        backlog_dir,
        "ST-0002",
        """\
        ---
        id: ST-0002
        epic: Delivery
        title: Second story
        tier: strong
        status: done
        outputs: [src/two.py]
        ---

        Body two.
        """,
    )
    _write_story(
        backlog_dir,
        "ST-0001",
        """\
        ---
        id: ST-0001
        epic: Delivery
        title: First story
        tier: economy
        status: pending
        outputs: [src/one.py]
        ---

        Body one.
        """,
    )

    stories = MarkdownBacklogStore(backlog_dir).list_stories()

    assert [story.id for story in stories] == ["ST-0001", "ST-0002"]


def test_get_story_returns_correct_story(tmp_path: Path):
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    _write_story(
        backlog_dir,
        "ST-0003",
        """\
        ---
        id: ST-0003
        epic: Routing
        title: Read one story
        tier: standard
        status: in-progress
        deps: [ST-0001, ST-0002]
        traces: [UC-01]
        outputs: [src/story.py]
        ---

        Story body.
        """,
    )

    story = MarkdownBacklogStore(backlog_dir).get_story("ST-0003")

    assert story.id == "ST-0003"
    assert story.title == "Read one story"
    assert story.deps == ["ST-0001", "ST-0002"]
    assert story.status is StoryStatus.IN_PROGRESS


def test_get_story_missing_raises_key_error(tmp_path: Path):
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()

    with pytest.raises(KeyError):
        MarkdownBacklogStore(backlog_dir).get_story("ST-9999")


@pytest.mark.parametrize("story_id", ["../docs/spec/prd", "ST-../../docs/spec/prd"])
def test_get_story_rejects_invalid_story_ids(tmp_path: Path, story_id: str):
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()

    with pytest.raises(KeyError, match="invalid story id"):
        MarkdownBacklogStore(backlog_dir).get_story(story_id)


def test_update_status_changes_frontmatter_without_altering_body(tmp_path: Path):
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    path = _write_story(
        backlog_dir,
        "ST-0004",
        """\
        ---
        id: ST-0004
        epic: Routing
        title: Update status
        tier: standard
        status: pending
        outputs: [src/status.py]
        ---

        # Body heading

        This prose must stay the same.
        """,
    )
    original = path.read_text(encoding="utf-8")

    MarkdownBacklogStore(backlog_dir).update_status("ST-0004", "done")

    updated = path.read_text(encoding="utf-8")
    assert "status: done" in updated
    assert updated.split("---\n", 2)[2] == original.split("---\n", 2)[2]


def test_update_status_rejects_invalid_story_id(tmp_path: Path):
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()

    with pytest.raises(KeyError, match="invalid story id"):
        MarkdownBacklogStore(backlog_dir).update_status("../docs/spec/prd", "done")


def test_update_status_uses_atomic_replace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    path = _write_story(
        backlog_dir,
        "ST-0008",
        """\
        ---
        id: ST-0008
        epic: Delivery
        title: Atomic update
        tier: standard
        status: pending
        outputs: [src/atomic.py]
        ---
        """,
    )
    original_replace = os.replace
    replace_calls: list[tuple[Path, Path]] = []

    def record_replace(src: Path | str, dst: Path | str) -> None:
        replace_calls.append((Path(src), Path(dst)))
        original_replace(src, dst)

    monkeypatch.setattr(
        "orchestrator.adapters.backlog_store.os.replace", record_replace
    )

    MarkdownBacklogStore(backlog_dir).update_status("ST-0008", "done")

    assert len(replace_calls) == 1
    temp_path, replaced_path = replace_calls[0]
    assert replaced_path == path
    assert temp_path.name.startswith(".ST-0008.md.")
    assert temp_path.suffix == ".tmp"
    assert not temp_path.exists()
    assert "status: done" in path.read_text(encoding="utf-8")


def test_parse_frontmatter_handles_inline_and_block_sequences(tmp_path: Path):
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    store = MarkdownBacklogStore(backlog_dir)

    inline_fm, inline_body = store._parse_frontmatter(
        textwrap.dedent(
            """\
            ---
            id: ST-0005
            deps: [ST-0001, ST-0002]
            traces: [UC-01, UC-02]
            ---

            Inline body.
            """
        )
    )
    block_fm, block_body = store._parse_frontmatter(
        textwrap.dedent(
            """\
            ---
            id: ST-0006
            deps:
              - ST-0003
              - ST-0004
            outputs:
              - src/one.py
              - src/two.py
            ---

            Block body.
            """
        )
    )

    assert inline_fm["deps"] == ["ST-0001", "ST-0002"]
    assert inline_fm["traces"] == ["UC-01", "UC-02"]
    assert block_fm["deps"] == ["ST-0003", "ST-0004"]
    assert block_fm["outputs"] == ["src/one.py", "src/two.py"]
    assert "Inline body." in inline_body
    assert "Block body." in block_body


def test_to_story_maps_tier_and_status_enums(tmp_path: Path):
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    store = MarkdownBacklogStore(backlog_dir)

    story = store._to_story(
        {
            "id": "ST-0007",
            "epic": "Enums",
            "title": "Map enums",
            "tier": "strong",
            "status": "blocked",
            "deps": [],
            "traces": [],
            "outputs": ["src/enums.py"],
        }
    )

    assert story.tier is Tier.STRONG
    assert story.status is StoryStatus.BLOCKED


def test_to_story_requires_frontmatter_fields(tmp_path: Path):
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    store = MarkdownBacklogStore(backlog_dir)

    with pytest.raises(ValueError, match="story frontmatter missing required fields"):
        store._to_story(
            {
                "id": "ST-0009",
                "epic": "Enums",
                "tier": "strong",
                "status": "blocked",
            }
        )
