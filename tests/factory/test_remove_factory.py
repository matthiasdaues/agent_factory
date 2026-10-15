"""Regression tests for remove-factory (ST-0305).

Each test builds a small installed tree with a hand-written removal manifest,
runs remove-factory against it, and checks what is left on disk.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import load_script

ORIENTATION_BEGIN = "<!-- >>> agent_factory orientation >>>"
ORIENTATION_END = "<!-- <<< agent_factory orientation <<< -->"


@pytest.fixture(scope="module")
def remove_factory():
    return load_script("remove-factory")


def _install(target: Path, **manifest) -> None:
    """Write a removal manifest and the factory tree it points into."""
    factory = target / ".agent-factory/factory"
    (factory / "config").mkdir(parents=True)
    (factory / "config/AGENTS.md").write_text("factory orientation\n")
    payload = {"version": 1, "remove_paths": [], "orientation": {}}
    payload.update(manifest)
    (target / ".agent-factory/install.json").write_text(json.dumps(payload))


def _run(remove_factory, target: Path) -> int:
    return remove_factory.main(["--target", str(target)])


# --- BUG-0074: headers recorded as dictionaries -----------------------------


@pytest.mark.parametrize(
    ("orig_final_newline", "expected"),
    [(True, "# Project\n"), (False, "# Project")],
)
def test_bug_0074_strips_header_recorded_as_dictionary(
    remove_factory, tmp_path, orig_final_newline, expected
):
    agents = tmp_path / "AGENTS.md"
    agents.write_text(
        f"{ORIENTATION_BEGIN}\nread the rules\n{ORIENTATION_END}\n\n# Project\n"
    )
    _install(
        tmp_path,
        orientation={
            "AGENTS.md": {
                "status": "injected",
                "block_digest": "abc",
                "orig_final_newline": orig_final_newline,
            }
        },
    )

    assert _run(remove_factory, tmp_path) == 0

    assert agents.read_text() == expected


def test_bug_0074_keeps_project_link_when_linked_entry_is_dictionary(
    remove_factory, tmp_path
):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/own.md").write_text("project orientation\n")
    agents = tmp_path / "AGENTS.md"
    agents.symlink_to("docs/own.md")
    _install(
        tmp_path,
        orientation={"AGENTS.md": {"status": "linked", "block_digest": ""}},
        remove_paths=["AGENTS.md"],
    )

    assert _run(remove_factory, tmp_path) == 0

    assert agents.is_symlink()
    assert agents.read_text() == "project orientation\n"
