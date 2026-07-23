"""Contract tests for ``factory/scripts/generate-codex-agents``."""

from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest
import tomllib

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "factory" / "scripts" / "generate-codex-agents"
_loader = SourceFileLoader("generate_codex_agents", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("generate_codex_agents", _loader)
generate_codex_agents = importlib.util.module_from_spec(_spec)
sys.modules["generate_codex_agents"] = generate_codex_agents
_loader.exec_module(generate_codex_agents)


def _agent(
    directory: Path,
    name: str,
    description: str,
    body: str = '# Role\n\nFollow the user\'s "request".\n',
) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    source = directory / f"{name}.md"
    source.write_text(
        f"---\nname: {name}\ndescription: {description}\ntier: strong\n---\n\n{body}",
        encoding="utf-8",
    )
    return source


def _read(path: Path) -> dict[str, str]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def test_generates_parseable_unpinned_toml_for_every_agent(tmp_path):
    agents = tmp_path / "factory-agents"
    output = tmp_path / ".codex" / "agents"
    _agent(agents, "author", "Writes code.")
    _agent(agents, "reviewer", "Reviews code.", "# Review\n\nBe independent.\n")

    assert generate_codex_agents.generate(agents, output) == 2

    assert sorted(path.name for path in output.iterdir()) == [
        "author.toml",
        "reviewer.toml",
    ]
    author_text = (output / "author.toml").read_text(encoding="utf-8")
    assert author_text.startswith(generate_codex_agents.OWNED_MARKER)
    assert _read(output / "author.toml") == {
        "name": "author",
        "description": "Writes code.",
        "developer_instructions": '# Role\n\nFollow the user\'s "request".\n',
    }
    for forbidden in ("model", "reasoning_effort", "sandbox", "mcp"):
        assert forbidden not in _read(output / "author.toml")


def test_folds_multiline_description_and_escapes_toml_strings(tmp_path):
    agents = tmp_path / "agents"
    output = tmp_path / "output"
    agents.mkdir()
    (agents / "special.md").write_text(
        "---\n"
        "name: special\n"
        "description: >-\n"
        '  Handles "quoted" input and\n'
        "  paths with backslashes.\n"
        "---\n\n"
        "# Instructions\n\n"
        'Keep C:\\tmp and """ intact.\n',
        encoding="utf-8",
    )

    generate_codex_agents.generate(agents, output)

    assert _read(output / "special.toml") == {
        "name": "special",
        "description": 'Handles "quoted" input and paths with backslashes.',
        "developer_instructions": '# Instructions\n\nKeep C:\\tmp and """ intact.\n',
    }


def test_rerun_refreshes_owned_file_and_is_stable(tmp_path):
    agents = tmp_path / "agents"
    output = tmp_path / "output"
    source = _agent(agents, "worker", "First.")
    generate_codex_agents.generate(agents, output)
    first = (output / "worker.toml").read_bytes()

    generate_codex_agents.generate(agents, output)
    assert (output / "worker.toml").read_bytes() == first

    source.write_text(source.read_text().replace("First.", "Second."), encoding="utf-8")
    generate_codex_agents.generate(agents, output)
    assert _read(output / "worker.toml")["description"] == "Second."


def test_prunes_stale_owned_files_but_preserves_unrelated_files(tmp_path):
    agents = tmp_path / "agents"
    output = tmp_path / "output"
    _agent(agents, "current", "Current.")
    output.mkdir()
    (output / "stale.toml").write_text(
        generate_codex_agents.OWNED_MARKER
        + 'name = "stale"\n'
        + 'description = "old"\n'
        + 'developer_instructions = "old"\n',
        encoding="utf-8",
    )
    (output / "foreign.toml").write_text('name = "foreign"\n', encoding="utf-8")

    generate_codex_agents.generate(agents, output)

    assert not (output / "stale.toml").exists()
    assert (output / "foreign.toml").read_text() == 'name = "foreign"\n'


@pytest.mark.parametrize("collision_kind", ["file", "directory", "symlink"])
def test_foreign_destination_collision_fails_before_any_refresh(
    tmp_path, collision_kind
):
    agents = tmp_path / "agents"
    output = tmp_path / "output"
    _agent(agents, "a-first", "New first.")
    _agent(agents, "z-collision", "Must not overwrite.")
    output.mkdir()
    first = output / "a-first.toml"
    first.write_text(
        generate_codex_agents.OWNED_MARKER
        + 'name = "a-first"\n'
        + 'description = "old first"\n'
        + 'developer_instructions = "old"\n',
        encoding="utf-8",
    )
    collision = output / "z-collision.toml"
    if collision_kind == "file":
        collision.write_text("foreign\n", encoding="utf-8")
    elif collision_kind == "directory":
        collision.mkdir()
    else:
        collision.symlink_to(output / "missing-target")

    with pytest.raises(generate_codex_agents.GenerationError, match="collision"):
        generate_codex_agents.generate(agents, output)

    assert 'description = "old first"' in first.read_text(encoding="utf-8")


def test_invalid_canonical_agent_fails_without_modifying_output(tmp_path):
    agents = tmp_path / "agents"
    output = tmp_path / "output"
    _agent(agents, "valid", "New.")
    (agents / "broken.md").write_text(
        "---\nname: broken\n---\n\n# Missing description\n", encoding="utf-8"
    )
    output.mkdir()
    existing = output / "valid.toml"
    existing.write_text(
        generate_codex_agents.OWNED_MARKER
        + 'name = "valid"\n'
        + 'description = "old"\n'
        + 'developer_instructions = "old"\n',
        encoding="utf-8",
    )

    with pytest.raises(generate_codex_agents.GenerationError, match="description"):
        generate_codex_agents.generate(agents, output)

    assert 'description = "old"' in existing.read_text(encoding="utf-8")
