"""Every YAML file the factory writes, and every YAML example it gives agents,
begins with the document marker `---` (ST-0308).

The rule lives in rulebooks/conventions/yaml-format.md. Two sources are
checked: the factory's YAML writers, run against a scratch target, and every
fenced `yaml`/`yml` block in the factory's markdown (skills, templates,
rulebooks, agents, playbooks, config). The first line that is neither blank
nor a comment must be `---`.

An excerpt is exempt: a fragment shown to be added to an existing file or
front matter. It is marked by the line `<!-- yaml-excerpt -->` directly above
its fence (blank lines between them are allowed). An excerpt must not begin
with `---`, because a pasted marker would close the front matter early.
"""

from __future__ import annotations

import re
from pathlib import Path

import dispatch_lib as lib
import pytest
from conftest import load_script

REPO_ROOT = Path(__file__).resolve().parents[2]
FACTORY = REPO_ROOT / "packages" / "factory"
PRECOMMIT_TEMPLATE = FACTORY / "config" / "pre-commit-config.yaml"

inf = load_script("init-factory")
index_lint = load_script("index-lint")
concern_lint = load_script("concern-lint")

_FENCE = re.compile(r"^(?P<indent>[ \t]*)```[ \t]*ya?ml[ \t]*\n(?P<body>.*?)^(?P=indent)```", re.DOTALL | re.MULTILINE)
EXCERPT_MARK = "<!-- yaml-excerpt -->"


def _first_content_line(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return None


def _is_excerpt(text: str, fence_start: int) -> bool:
    before = [line.strip() for line in text[:fence_start].splitlines()]
    previous = next((line for line in reversed(before) if line), "")
    return previous == EXCERPT_MARK


def _yaml_blocks() -> list[tuple[str, str, bool]]:
    blocks: list[tuple[str, str, bool]] = []
    for md in sorted(FACTORY.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        for match in _FENCE.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            body = match.group("body")
            indent = match.group("indent")
            body = "\n".join(line.removeprefix(indent) for line in body.splitlines())
            where = f"{md.relative_to(REPO_ROOT)}:{line_no}"
            blocks.append((where, body, _is_excerpt(text, match.start())))
    return blocks


BLOCKS = _yaml_blocks()
EXAMPLES = [(where, body) for where, body, excerpt in BLOCKS if not excerpt]
EXCERPTS = [(where, body) for where, body, excerpt in BLOCKS if excerpt]


def test_yaml_examples_exist():
    assert EXAMPLES, "no fenced yaml example found under packages/factory"


@pytest.mark.parametrize(("where", "body"), EXAMPLES, ids=[w for w, _ in EXAMPLES])
def test_yaml_example_begins_with_document_marker(where, body):
    assert _first_content_line(body) == "---", f"{where}: yaml example lacks leading ---"


@pytest.mark.parametrize(
    "path",
    [
        "packages/factory/rulebooks/conventions/agent-context-composition.md",
        "packages/factory/rulebooks/conventions/dispatch-contract.md",
    ],
)
def test_known_excerpts_are_marked(path):
    assert any(where.startswith(f"{path}:") for where, _ in EXCERPTS), f"{path}: excerpt lacks {EXCERPT_MARK}"


@pytest.mark.parametrize(("where", "body"), EXCERPTS, ids=[w for w, _ in EXCERPTS])
def test_yaml_excerpt_omits_document_marker(where, body):
    assert _first_content_line(body) != "---", f"{where}: excerpt begins with ---"


def test_concerns_excerpt_pasted_into_story_front_matter_keeps_concerns():
    path = "packages/factory/rulebooks/conventions/agent-context-composition.md"
    excerpt = next(body for where, body, _ in BLOCKS if where.startswith(f"{path}:") and "concerns:" in body)
    story = f"---\nid: ST-9999\ntitle: Example\n{excerpt.strip()}\nstatus: pending\n---\n\n# Example\n"
    front_matter = concern_lint._parse_story_frontmatter(story)
    assert front_matter is not None
    assert front_matter.get("concerns") == {"domain": ["payments"], "technical": ["backend", "frontend"]}
    assert front_matter.get("status") == "pending"


def test_init_factory_testing_yaml_begins_with_document_marker(tmp_path):
    (tmp_path / "Makefile").write_text("test:\n\tpytest\n", encoding="utf-8")
    inf.detect_test_regime(tmp_path, [])
    written = (tmp_path / "docs" / "testing.yaml").read_text(encoding="utf-8")
    assert _first_content_line(written) == "---"


def test_init_factory_fresh_precommit_config_begins_with_document_marker():
    written = inf._fresh_precommit_text(PRECOMMIT_TEMPLATE)
    assert _first_content_line(written) == "---"


def test_dispatch_ledger_and_manifest_begin_with_document_marker_pyyaml():
    pytest.importorskip("yaml")
    assert lib.yaml is not None
    written = lib._dump_yaml({"mode": "automated", "stories": []})
    assert _first_content_line(written) == "---"


def test_dispatch_ledger_and_manifest_begin_with_document_marker_stdlib(monkeypatch):
    monkeypatch.setattr(lib, "yaml", None)
    written = lib._dump_yaml({"mode": "automated", "stories": []})
    assert _first_content_line(written) == "---"


def test_index_lint_index_begins_with_document_marker(tmp_path):
    written, _ = index_lint.render_index(
        FACTORY / "agents",
        FACTORY / "skills",
        FACTORY / "playbooks",
        FACTORY / "rulebooks",
        tmp_path / "INDEX.yaml",
    )
    assert _first_content_line(written) == "---"
