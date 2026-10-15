"""Regression tests for the dependency-check and crap-score gates."""

from __future__ import annotations

import json

from conftest import load_script

dc = load_script("dependency-check")

RULES = "core must_not_depend_on adapters\n"


def _dependency_tree(tmp_path, files: dict[str, bytes]):
    src = tmp_path / "src"
    for relative, content in files.items():
        path = src / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    dsl = tmp_path / "architecture.dsl"
    dsl.write_text(RULES, encoding="utf-8")
    return src, dsl


def _run_dependency_check(tmp_path, src, dsl):
    reports = tmp_path / "reports"
    code = dc.main(
        [
            "--dsl-path",
            str(dsl),
            "--source-root",
            str(src),
            "--report-dir",
            str(reports),
            "--story-id",
            "ST-0000",
        ]
    )
    rows = json.loads((reports / "ST-0000.json").read_text(encoding="utf-8"))
    return code, rows


def test_BUG_0071_unparseable_file_in_ruled_module_fails(tmp_path):
    src, dsl = _dependency_tree(
        tmp_path,
        {"core/service.py": b"import adapters.db\n\ndef broken(:\n    pass\n"},
    )

    code, rows = _run_dependency_check(tmp_path, src, dsl)

    assert code == 1
    failing = [row for row in rows if row["pass_fail"] == "fail"]
    assert len(failing) == 1
    assert failing[0]["violating_import"]["file"] == "core/service.py"
    assert failing[0]["violating_import"]["parse_error"]


def test_BUG_0071_latin1_file_does_not_crash_the_gate(tmp_path):
    src, dsl = _dependency_tree(
        tmp_path,
        {
            "core/declared.py": (
                "# -*- coding: latin-1 -*-\nimport adapters.db\nNAME = 'café'\n"
            ).encode("latin-1"),
            "core/undeclared.py": "NAME = 'café'\n".encode("latin-1"),
        },
    )

    code, rows = _run_dependency_check(tmp_path, src, dsl)

    assert code == 1
    failing = {
        row["violating_import"]["file"]: row["violating_import"]
        for row in rows
        if row["pass_fail"] == "fail"
    }
    assert failing["core/declared.py"]["imported_module"] == "adapters.db"
    assert failing["core/undeclared.py"]["parse_error"]
