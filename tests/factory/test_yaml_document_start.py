"""Every YAML file the factory writes, and every YAML example it gives agents,
begins with the document marker `---` (ST-0308).

The rule lives in rulebooks/conventions/yaml-format.md. Two sources are
checked: the factory's YAML writers, run against a scratch target, and every
fenced `yaml`/`yml` block in the factory's markdown (skills, templates,
rulebooks, agents, playbooks, config). The first line that is neither blank
nor a comment must be `---`.
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

_FENCE = re.compile(r"^(?P<indent>[ \t]*)```[ \t]*ya?ml[ \t]*\n(?P<body>.*?)^(?P=indent)```", re.DOTALL | re.MULTILINE)


def _first_content_line(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return None


def _yaml_examples() -> list[tuple[str, int]]:
    examples: list[tuple[str, int]] = []
    for md in sorted(FACTORY.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        for match in _FENCE.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            body = match.group("body")
            indent = match.group("indent")
            body = "\n".join(line.removeprefix(indent) for line in body.splitlines())
            examples.append((f"{md.relative_to(REPO_ROOT)}:{line_no}", body))
    return examples


EXAMPLES = _yaml_examples()


def test_yaml_examples_exist():
    assert EXAMPLES, "no fenced yaml example found under packages/factory"


@pytest.mark.parametrize(("where", "body"), EXAMPLES, ids=[w for w, _ in EXAMPLES])
def test_yaml_example_begins_with_document_marker(where, body):
    assert _first_content_line(body) == "---", f"{where}: yaml example lacks leading ---"


def test_init_factory_testing_yaml_begins_with_document_marker(tmp_path):
    (tmp_path / "Makefile").write_text("test:\n\tpytest\n", encoding="utf-8")
    inf.detect_test_regime(tmp_path, [])
    written = (tmp_path / "docs" / "testing.yaml").read_text(encoding="utf-8")
    assert _first_content_line(written) == "---"


def test_init_factory_fresh_precommit_config_begins_with_document_marker():
    written = inf._fresh_precommit_text(PRECOMMIT_TEMPLATE)
    assert _first_content_line(written) == "---"


@pytest.mark.parametrize("pyyaml", [True, False], ids=["pyyaml", "stdlib"])
def test_dispatch_ledger_and_manifest_begin_with_document_marker(monkeypatch, pyyaml):
    if not pyyaml:
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
