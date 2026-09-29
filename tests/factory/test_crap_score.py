"""Contract tests for crap-score gate script."""

from __future__ import annotations

import json

from conftest import load_script

cs = load_script("crap-score")

SOURCE = """\
class Greeter:
    def greet(self, name):
        if name:
            return name
        return "anon"


def helper():
    return 1
"""


def test_each_function_reported_once(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "module.py").write_text(SOURCE, encoding="utf-8")
    reports = tmp_path / "reports"

    cs.main(
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

    results = json.loads((reports / "ST-0000.json").read_text(encoding="utf-8"))
    names = sorted(r["function"] for r in results)
    assert names == ["greet", "helper"]
