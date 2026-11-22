"""Integration tests of the Python measuring-command template of setup-crap-score.

Rule: User measures each part of the code with a measuring command the
project owns (docs/spec/features/crap-gate-setup.feature, BR-130).

Each test writes a small project in tmp_path, without `.agent-factory/`,
copies the template into it with TEST_COMMAND filled in, as setup-crap-score
does, and runs it for real with radon and coverage.py.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import REPO_ROOT

TEMPLATE = REPO_ROOT / "packages" / "factory" / "skills" / "setup-crap-score" / "crap-measure-python"
SIX_FIELDS = {"file", "function", "start_line", "end_line", "complexity", "coverage_pct"}

PARSER = """\
class Parser:
    def parse(self, text):
        if not text:
            return []
        return text.split(",")
"""

IMPORT_ORDERS = """\
#!/usr/bin/env python3
\"\"\"Import orders from a CSV line.\"\"\"


def parse_row(line):
    if not line:
        return None
    return line.strip().split(";")
"""

TEST_PARSER = """\
import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.parser import Parser  # noqa: E402

_loader = SourceFileLoader("import_orders", str(ROOT / "scripts" / "import-orders"))
import_orders = importlib.util.module_from_spec(importlib.util.spec_from_loader("import_orders", _loader))
_loader.exec_module(import_orders)


def test_parse():
    assert Parser().parse("a,b") == ["a", "b"]
    assert Parser().parse("") == []


def test_parse_row():
    assert import_orders.parse_row("a;b") == ["a", "b"]
    assert import_orders.parse_row("") is None
"""


def _write_project(root: Path, test_command: list[str] | None = None) -> Path:
    """Write the demo project and the filled-in template; return the command."""
    (root / "src").mkdir()
    (root / "src" / "parser.py").write_text(PARSER)
    (root / "scripts").mkdir()
    (root / "scripts" / "import-orders").write_text(IMPORT_ORDERS)
    (root / "tests").mkdir()
    (root / "tests" / "test_parser.py").write_text(TEST_PARSER)
    if test_command is None:
        test_command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"]
    text, count = re.subn(
        r"^TEST_COMMAND: list\[str\] = \[\]$",
        f"TEST_COMMAND: list[str] = {test_command!r}",
        TEMPLATE.read_text(),
        flags=re.MULTILINE,
    )
    assert count == 1, "the template has no empty TEST_COMMAND constant"
    command = root / "scripts" / "crap-measure-python"
    command.write_text(text)
    command.chmod(0o755)
    return command


def _run(root: Path, **patterns: str) -> subprocess.CompletedProcess:
    """Run the template; *patterns* sets GATE_FILES and GATE_EXCLUDE, as crap-score does."""
    # A gate run of this suite sets COVERAGE_* variables. The real template
    # would inherit them and write its data into that run, so strip them here.
    env = {
        k: v for k, v in os.environ.items()
        if not k.startswith("COVERAGE_") and k not in ("GATE_FILES", "GATE_EXCLUDE")
    }
    env["GATE_OUTPUT"] = "rows.json"
    env.update(patterns)
    return subprocess.run(
        ["uv", "run", "--quiet", "--script", "scripts/crap-measure-python"],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )


def _rows(root: Path) -> list[dict]:
    return json.loads((root / "rows.json").read_text())


@pytest.fixture(scope="module")
def measured(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, subprocess.CompletedProcess]:
    """The demo project after one run of the template."""
    root = tmp_path_factory.mktemp("project")
    _write_project(root)
    return root, _run(root)


def _row(rows: list[dict], file: str, function: str) -> dict:
    matches = [r for r in rows if r.get("file") == file and r.get("function") == function]
    assert len(matches) == 1, f"expected one row for {file} {function}, got {rows}"
    return matches[0]


@pytest.mark.spec("CG-03-IT-01")
def test_cg_03_the_template_writes_six_field_rows_to_gate_output(measured) -> None:
    """Scenario: The measuring command writes its rows to the path in GATE_OUTPUT.

    Scenario: A person runs a measuring command without the Factory.
    """
    root, result = measured
    assert result.returncode == 0, result.stderr
    assert not (root / ".agent-factory").exists()
    rows = _rows(root)
    assert isinstance(rows, list) and rows
    for row in rows:
        assert set(row) == SIX_FIELDS, row
        assert not Path(row["file"]).is_absolute()
        assert (root / row["file"]).is_file()
    row = _row(rows, "src/parser.py", "Parser.parse")
    assert (row["start_line"], row["end_line"], row["complexity"]) == (2, 5, 2)
    assert row["coverage_pct"] == 100.0


@pytest.mark.spec("CG-03-IT-02")
def test_cg_03_the_template_reports_the_qualified_name_of_a_method(measured) -> None:
    """Scenario: The measuring command reports the qualified name of a method."""
    root, result = measured
    assert result.returncode == 0, result.stderr
    functions = {r["function"] for r in _rows(root) if r["file"] == "src/parser.py"}
    assert functions == {"Parser.parse"}


@pytest.mark.spec("CG-03-IT-03")
def test_cg_03_the_template_measures_a_script_without_a_file_ending(measured) -> None:
    """Scenario: A script without a file ending is measured like any other file."""
    root, result = measured
    assert result.returncode == 0, result.stderr
    row = _row(_rows(root), "scripts/import-orders", "parse_row")
    assert row["coverage_pct"] == 100.0
    assert not any(r["file"] == "scripts/crap-measure-python" for r in _rows(root))


FAILING_TEST = """\
def test_fails():
    assert False
"""

UNREACHED_SCRIPT = """\
#!/usr/bin/env python3


def sync_stock(count):
    return count
"""


@pytest.mark.spec("CG-03-IT-04")
@pytest.mark.parametrize(
    ("path", "content", "cause"),
    [
        ("tests/test_fails.py", FAILING_TEST, "the test run failed with exit 1"),
        ("scripts/sync-stock", UNREACHED_SCRIPT, "coverage cannot reach scripts/sync-stock"),
    ],
    ids=["failed test run", "coverage cannot reach"],
)
def test_cg_03_the_template_exits_non_zero_for_a_case_it_cannot_measure(
    tmp_path: Path, path: str, content: str, cause: str
) -> None:
    """Scenario Outline: A measuring command reports a case it cannot measure with a non-zero exit."""
    _write_project(tmp_path)
    assert _run(tmp_path).returncode == 0
    (tmp_path / path).write_text(content)

    result = _run(tmp_path)

    assert result.returncode == 1
    assert cause in result.stderr
    # No row, also none of the earlier run, reports a function as 0 % covered.
    assert not (tmp_path / "rows.json").exists()


@pytest.mark.spec("CG-03-IT-04")
@pytest.mark.parametrize(
    ("path", "patterns"),
    [
        ("scripts/sync-stock", {"GATE_FILES": "**", "GATE_EXCLUDE": "docs/**\nscripts/sync-stock\n"}),
        ("tools/sync-stock", {"GATE_FILES": "src/**\nscripts/**", "GATE_EXCLUDE": ""}),
        ("scripts/tools/sync-stock", {"GATE_FILES": "scripts/*\nsrc/*"}),
    ],
    ids=["excluded", "outside files", "star stays in one segment"],
)
def test_cg_03_the_template_skips_an_untested_script_that_the_measure_leaves_out(
    tmp_path: Path, path: str, patterns: dict[str, str]
) -> None:
    """IMPL-0090, DEC-65: a script that GATE_FILES or GATE_EXCLUDE leaves out stops no measure."""
    _write_project(tmp_path)
    (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / path).write_text(UNREACHED_SCRIPT)

    result = _run(tmp_path, **patterns)

    assert result.returncode == 0, result.stderr
    assert not any(r["file"] == path for r in _rows(tmp_path))
    _row(_rows(tmp_path), "src/parser.py", "Parser.parse")


@pytest.mark.spec("CG-03-IT-04")
def test_cg_03_the_template_still_stops_for_an_untested_script_inside_files(tmp_path: Path) -> None:
    """IMPL-0090, DEC-65: a script that GATE_FILES keeps and coverage cannot reach still stops the measure."""
    _write_project(tmp_path)
    (tmp_path / "scripts" / "sync-stock").write_text(UNREACHED_SCRIPT)

    result = _run(tmp_path, GATE_FILES="scripts/*", GATE_EXCLUDE="scripts/import-orders")

    assert result.returncode == 1
    assert "coverage cannot reach scripts/sync-stock" in result.stderr
    assert not (tmp_path / "rows.json").exists()


@pytest.mark.spec("CG-03-IT-05")
def test_cg_03_the_template_reports_a_file_it_cannot_parse_as_a_parse_error_row(
    tmp_path: Path,
) -> None:
    """Scenario: A measuring command reports a file it cannot parse as a row with parse_error."""
    _write_project(tmp_path)
    (tmp_path / "src" / "broken.py").write_text("def broken(:\n    pass\n")

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    broken = [r for r in _rows(tmp_path) if r["file"] == "src/broken.py"]
    assert len(broken) == 1
    assert set(broken[0]) == {"file", "parse_error"}
    assert broken[0]["parse_error"]
    assert "src/broken.py" in result.stderr
    _row(_rows(tmp_path), "src/parser.py", "Parser.parse")


INSTALLED_SCRIPT = """\
#!/usr/bin/env -S uv run --script


def next_id(prefix):
    return prefix + "-0001"
"""


@pytest.mark.spec("CG-03-IT-01")
def test_cg_03_the_template_skips_a_folder_that_git_ignores(tmp_path: Path) -> None:
    """Scenario: The measuring command writes its rows to the path in GATE_OUTPUT.

    IMPL-0065: an ignored folder with a Python script, such as the installed
    Factory in a run by hand, gets no row and does not stop the measure.
    """
    _write_project(tmp_path)
    ignored = tmp_path / "installed" / "scripts"
    ignored.mkdir(parents=True)
    (ignored / "next-id").write_text(INSTALLED_SCRIPT)
    (tmp_path / ".gitignore").write_text("/installed/\n")
    subprocess.run(["git", "init", "--quiet"], cwd=tmp_path, check=True)

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert not any(r["file"].startswith("installed/") for r in _rows(tmp_path))
    _row(_rows(tmp_path), "src/parser.py", "Parser.parse")


UNUSED = """\
def lonely(value):
    if value:
        return 1
    return 0
"""


@pytest.mark.spec("CG-03-IT-01")
def test_cg_03_the_template_reports_an_untested_module_outside_a_package_as_0_percent(
    tmp_path: Path,
) -> None:
    """Scenario: The measuring command writes its rows to the path in GATE_OUTPUT.

    IMPL-0066: coverage reaches an untested file in a folder without
    __init__.py, so its function gets a row with coverage_pct 0.
    """
    _write_project(tmp_path)
    (tmp_path / "src" / "unused.py").write_text(UNUSED)

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert _row(_rows(tmp_path), "src/unused.py", "lonely")["coverage_pct"] == 0.0


NESTED_PARSER = """\
class Parser:
    def parse(self, text):
        if not text:
            return []
        return text.split(",")

    class Options:
        def strict(self, flag):
            if flag:
                return True
            return False
"""


@pytest.mark.spec("CG-03-IT-02")
def test_cg_03_the_template_reports_a_method_of_a_nested_class(tmp_path: Path) -> None:
    """Scenario: The measuring command reports the qualified name of a method.

    IMPL-0067: a method of a nested class gets one row under its qualified name.
    """
    _write_project(tmp_path)
    (tmp_path / "src" / "parser.py").write_text(NESTED_PARSER)

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    row = _row(_rows(tmp_path), "src/parser.py", "Parser.Options.strict")
    assert (row["start_line"], row["end_line"], row["complexity"]) == (8, 11, 2)


@pytest.mark.spec("CG-03-IT-01")
def test_cg_03_the_template_runs_the_test_command_in_the_environment_of_its_caller(
    tmp_path: Path,
) -> None:
    """Scenario: The measuring command writes its rows to the path in GATE_OUTPUT.

    IMPL-0091: TEST_COMMAND names the interpreter by name, so `python3` must
    resolve on the caller's PATH, not in the template's own uv environment,
    which holds radon and coverage.py but not pytest.
    """
    _write_project(tmp_path, ["python3", "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"])
    project_bin = str(Path(sys.executable).parent)

    result = _run(tmp_path, PATH=os.pathsep.join([project_bin, os.environ["PATH"]]))

    assert result.returncode == 0, result.stderr
    _row(_rows(tmp_path), "src/parser.py", "Parser.parse")
