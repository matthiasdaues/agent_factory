"""Regression tests for the dependency-check and crap-score gates."""

from __future__ import annotations

import json

from conftest import load_script

dc = load_script("dependency-check")
cs = load_script("crap-score")

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


COVERED_SOURCE = """\
def choose(flag):
    if flag:
        return 1
    return 2
"""


def test_BUG_0072_coverage_keys_relative_to_project_root_match(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    (src / "module.py").write_text(COVERED_SOURCE, encoding="utf-8")
    coverage = tmp_path / "coverage.json"
    coverage.write_text(
        json.dumps(
            {
                "files": {
                    "src/module.py": {
                        "executed_lines": [1, 2, 3, 4],
                        "missing_lines": [],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    reports = tmp_path / "reports"
    monkeypatch.chdir(tmp_path)

    code = cs.main(
        [
            "--source-root",
            "src",
            "--coverage-json",
            "coverage.json",
            "--report-dir",
            str(reports),
            "--story-id",
            "ST-0000",
            "--threshold",
            "2",
        ]
    )

    rows = json.loads((reports / "ST-0000.json").read_text(encoding="utf-8"))
    assert rows[0]["coverage_pct"] == 100.0
    assert code == 0


def test_BUG_0072_coverage_keys_relative_to_source_root_match(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    (src / "module.py").write_text(COVERED_SOURCE, encoding="utf-8")
    coverage = tmp_path / "coverage.json"
    coverage.write_text(
        json.dumps(
            {
                "files": {
                    "module.py": {
                        "executed_lines": [1, 2, 3, 4],
                        "missing_lines": [],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    reports = tmp_path / "reports"
    monkeypatch.chdir(tmp_path)

    code = cs.main(
        [
            "--source-root",
            "src",
            "--coverage-json",
            "coverage.json",
            "--report-dir",
            str(reports),
            "--story-id",
            "ST-0000",
            "--threshold",
            "2",
        ]
    )

    rows = json.loads((reports / "ST-0000.json").read_text(encoding="utf-8"))
    assert rows[0]["coverage_pct"] == 100.0
    assert code == 0


def _run_crap_score_on(src, reports):
    return cs.main(
        [
            "--source-root",
            str(src),
            "--report-dir",
            str(reports),
            "--story-id",
            "ST-0000",
            "--threshold",
            "1000",
        ]
    )


def test_BUG_0072_syntax_error_file_fails_the_gate(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "broken.py").write_text("def broken(:\n    pass\n", encoding="utf-8")
    (src / "good.py").write_text(COVERED_SOURCE, encoding="utf-8")
    reports = tmp_path / "reports"

    code = _run_crap_score_on(src, reports)

    rows = json.loads((reports / "ST-0000.json").read_text(encoding="utf-8"))
    by_file = {row["file"]: row for row in rows}
    assert by_file["good.py"]["function"] == "choose"
    assert by_file["good.py"]["pass_fail"] == "pass"
    assert by_file["broken.py"]["pass_fail"] == "fail"
    assert "invalid syntax" in by_file["broken.py"]["function"]
    assert code == 1


def test_BUG_0072_undecodable_file_fails_the_gate(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "latin.py").write_bytes("NAME = 'caf\xe9'\n".encode("latin-1"))
    reports = tmp_path / "reports"

    code = _run_crap_score_on(src, reports)

    rows = json.loads((reports / "ST-0000.json").read_text(encoding="utf-8"))
    assert [row["file"] for row in rows] == ["latin.py"]
    assert rows[0]["pass_fail"] == "fail"
    assert "utf-8" in rows[0]["function"]
    assert code == 1


def _write_coverage(path, keys_to_executed):
    files = {
        key: {
            "executed_lines": [1, 2, 3, 4] if covered else [],
            "missing_lines": [] if covered else [1, 2, 3, 4],
        }
        for key, covered in keys_to_executed.items()
    }
    path.write_text(json.dumps({"files": files}), encoding="utf-8")


def _run_crap_score_with_coverage(source_root, coverage_json, reports):
    return cs.main(
        [
            "--source-root",
            source_root,
            "--coverage-json",
            coverage_json,
            "--report-dir",
            str(reports),
            "--story-id",
            "ST-0000",
            "--threshold",
            "2",
        ]
    )


def test_BUG_0072_same_named_file_in_cwd_does_not_take_coverage(tmp_path, monkeypatch):
    (tmp_path / "src").mkdir()
    (tmp_path / "m.py").write_text(COVERED_SOURCE, encoding="utf-8")
    (tmp_path / "src" / "m.py").write_text(COVERED_SOURCE, encoding="utf-8")
    _write_coverage(tmp_path / "coverage.json", {"m.py": True, "src/m.py": False})
    reports = tmp_path / "reports"
    monkeypatch.chdir(tmp_path / "src")

    code = _run_crap_score_with_coverage(".", "../coverage.json", reports)

    rows = json.loads((reports / "ST-0000.json").read_text(encoding="utf-8"))
    assert [(row["file"], row["coverage_pct"]) for row in rows] == [("m.py", 0.0)]
    assert code == 1


def test_BUG_0072_uncovered_file_does_not_borrow_root_namesake(tmp_path, monkeypatch):
    (tmp_path / "src").mkdir()
    (tmp_path / "m.py").write_text(COVERED_SOURCE, encoding="utf-8")
    (tmp_path / "src" / "m.py").write_text(COVERED_SOURCE, encoding="utf-8")
    _write_coverage(tmp_path / "coverage.json", {"m.py": True})
    reports = tmp_path / "reports"
    monkeypatch.chdir(tmp_path)

    code = _run_crap_score_with_coverage("src", "coverage.json", reports)

    rows = json.loads((reports / "ST-0000.json").read_text(encoding="utf-8"))
    assert [(row["file"], row["coverage_pct"]) for row in rows] == [("m.py", 0.0)]
    assert code == 1
