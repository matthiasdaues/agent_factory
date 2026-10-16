"""spec-lint refuses a scope map that reverse-map wrote as a draft (BUG-0096).

Unattended reverse-map marks its scope map with `status: draft` in the
frontmatter. The brownfield Stage 1 exit must not pass until a stakeholder
has confirmed the map, so spec-lint reports the marker as an error.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import load_script

sl = load_script("spec-lint")

BODY = (
    "# Scope Map\n\n"
    "| Rule | Status | Confidence | Sources | Feature Link |\n"
    "| ---- | ------ | ---------- | ------- | ------------ |\n"
)


def _spec_dir(tmp_path: Path, frontmatter: str) -> Path:
    spec = tmp_path / "spec"
    supp = spec / "supplementary_specs"
    supp.mkdir(parents=True)
    (supp / "entity-model.md").write_text("# Entity Model\n", encoding="utf-8")
    (spec / "scope-map.md").write_text(frontmatter + BODY, encoding="utf-8")
    return spec


def _codes(spec: Path) -> list[str]:
    findings, _ = sl.run(spec, Path("missing-context.md"), False)
    return [f.code for f in findings if f.severity == "error"]


def test_draft_scope_map_is_reported_and_fails_the_gate(tmp_path):
    spec = _spec_dir(tmp_path, "---\nscope: global\nstatus: draft\n---\n\n")
    assert "SCOPE001" in _codes(spec)
    assert sl.main(["--spec-dir", str(spec), "--context", "none.md"]) == 1


@pytest.mark.parametrize(
    "frontmatter",
    [
        "---\nscope: global\nstatus: confirmed\n---\n\n",
        "---\nscope: global\n---\n\n",
        "",
    ],
    ids=["confirmed", "marker-removed", "no-frontmatter"],
)
def test_confirmed_scope_map_passes(tmp_path, frontmatter):
    spec = _spec_dir(tmp_path, frontmatter)
    assert "SCOPE001" not in _codes(spec)
    assert sl.main(["--spec-dir", str(spec), "--context", "none.md"]) == 0


def test_draft_word_in_body_is_not_the_marker(tmp_path):
    spec = _spec_dir(tmp_path, "---\nscope: global\n---\n\nstatus: draft\n\n")
    assert "SCOPE001" not in _codes(spec)
