from __future__ import annotations

import textwrap
from pathlib import Path

from orchestrator.adapters.backlog_store import MarkdownBacklogStore
from orchestrator.entities import StoryStatus


def _write_story(backlog_dir: Path, story_id: str, content: str) -> Path:
    path = backlog_dir / f"{story_id}.md"
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    return path


def test_get_story_exposes_frontmatter_and_prose_body(tmp_path: Path):
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    _write_story(
        backlog_dir,
        "ST-0100",
        """\
        ---
        id: ST-0100
        epic: Status & Backlog Views
        title: Detail story
        classification: standard
        status: pending
        outputs: [src/detail.py]
        ---

        # Detail story

        This is the human-facing prose body.
        """,
    )

    story = MarkdownBacklogStore(backlog_dir).get_story("ST-0100")

    assert story.id == "ST-0100"
    assert story.title == "Detail story"
    assert "This is the human-facing prose body." in story.body


def test_stories_by_epic_groups_stories_and_retains_status(tmp_path: Path):
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    _write_story(
        backlog_dir,
        "ST-0101",
        """\
        ---
        id: ST-0101
        epic: Alpha
        title: Alpha story
        classification: standard
        status: pending
        outputs: [src/a.py]
        ---

        Body.
        """,
    )
    _write_story(
        backlog_dir,
        "ST-0102",
        """\
        ---
        id: ST-0102
        epic: Beta
        title: Beta story
        classification: standard
        status: done
        outputs: [src/b.py]
        ---

        Body.
        """,
    )
    _write_story(
        backlog_dir,
        "ST-0103",
        """\
        ---
        id: ST-0103
        epic: Alpha
        title: Second alpha story
        classification: standard
        status: blocked
        outputs: [src/c.py]
        ---

        Body.
        """,
    )

    grouped = MarkdownBacklogStore(backlog_dir).stories_by_epic()

    assert set(grouped.keys()) == {"Alpha", "Beta"}
    assert [story.id for story in grouped["Alpha"]] == ["ST-0101", "ST-0103"]
    assert [story.id for story in grouped["Beta"]] == ["ST-0102"]
    assert grouped["Alpha"][0].status is StoryStatus.PENDING
    assert grouped["Alpha"][1].status is StoryStatus.BLOCKED
    assert grouped["Beta"][0].status is StoryStatus.DONE


def test_stories_by_epic_empty_backlog_returns_empty_mapping(tmp_path: Path):
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()

    grouped = MarkdownBacklogStore(backlog_dir).stories_by_epic()

    assert grouped == {}


def test_ready_stories_includes_pending_with_done_deps_excludes_unmet_dep(
    tmp_path: Path,
):
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    _write_story(
        backlog_dir,
        "ST-0110",
        """\
        ---
        id: ST-0110
        epic: Deps
        title: Dependency done
        classification: standard
        status: done
        outputs: [src/dep-done.py]
        ---

        Body.
        """,
    )
    _write_story(
        backlog_dir,
        "ST-0111",
        """\
        ---
        id: ST-0111
        epic: Deps
        title: Dependency pending
        classification: standard
        status: pending
        outputs: [src/dep-pending.py]
        ---

        Body.
        """,
    )
    _write_story(
        backlog_dir,
        "ST-0112",
        """\
        ---
        id: ST-0112
        epic: Deps
        title: Ready story
        classification: standard
        status: pending
        deps: [ST-0110]
        outputs: [src/ready.py]
        ---

        Body.
        """,
    )
    _write_story(
        backlog_dir,
        "ST-0113",
        """\
        ---
        id: ST-0113
        epic: Deps
        title: Not-ready story
        classification: standard
        status: pending
        deps: [ST-0111]
        outputs: [src/not-ready.py]
        ---

        Body.
        """,
    )

    ready = MarkdownBacklogStore(backlog_dir).ready_stories()

    ready_ids = [story.id for story in ready]
    assert "ST-0112" in ready_ids
    assert "ST-0113" not in ready_ids
    # Non-pending stories never appear, regardless of their own deps.
    assert "ST-0110" not in ready_ids


def test_ready_stories_empty_deps_list_satisfied_trivially(tmp_path: Path):
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    _write_story(
        backlog_dir,
        "ST-0120",
        """\
        ---
        id: ST-0120
        epic: Deps
        title: No deps
        classification: standard
        status: pending
        deps: []
        outputs: [src/no-deps.py]
        ---

        Body.
        """,
    )

    ready = MarkdownBacklogStore(backlog_dir).ready_stories()

    assert [story.id for story in ready] == ["ST-0120"]


def test_ready_stories_excludes_dependency_not_present_in_snapshot(tmp_path: Path):
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    _write_story(
        backlog_dir,
        "ST-0130",
        """\
        ---
        id: ST-0130
        epic: Deps
        title: Unresolvable dependency
        classification: standard
        status: pending
        deps: [ST-9999]
        outputs: [src/unresolvable.py]
        ---

        Body.
        """,
    )

    ready = MarkdownBacklogStore(backlog_dir).ready_stories()

    assert ready == []


def test_ready_stories_empty_backlog_returns_empty_list(tmp_path: Path):
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()

    ready = MarkdownBacklogStore(backlog_dir).ready_stories()

    assert ready == []


def test_stories_by_epic_and_ready_stories_do_not_mutate_backlog_files(
    tmp_path: Path,
):
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()
    path = _write_story(
        backlog_dir,
        "ST-0140",
        """\
        ---
        id: ST-0140
        epic: Deps
        title: Read-only check
        classification: standard
        status: pending
        deps: []
        outputs: [src/read-only.py]
        ---

        Body.
        """,
    )
    before = path.read_text(encoding="utf-8")
    before_mtime = path.stat().st_mtime_ns

    store = MarkdownBacklogStore(backlog_dir)
    store.stories_by_epic()
    store.ready_stories()

    assert path.read_text(encoding="utf-8") == before
    assert path.stat().st_mtime_ns == before_mtime
