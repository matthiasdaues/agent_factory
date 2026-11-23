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
GATE_VARIABLES = ("GATE_FILES", "GATE_EXCLUDE", "GATE_SCOPE", "GATE_CHANGED_FILES")
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


def _write_project(
    root: Path, test_command: list[str] | None = None, select_command: list[str] | None = None
) -> Path:
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
    if select_command is not None:
        text, count = re.subn(
            r"^SELECT_COMMAND: list\[str\] = \[\]$",
            f"SELECT_COMMAND: list[str] = {select_command!r}",
            text,
            flags=re.MULTILINE,
        )
        assert count == 1, "the template has no empty SELECT_COMMAND constant"
    command = root / "scripts" / "crap-measure-python"
    command.write_text(text)
    command.chmod(0o755)
    return command


def _run(root: Path, outer: Path | None = None, **patterns: str) -> subprocess.CompletedProcess:
    """Run the template; *patterns* sets the GATE_* variables, as crap-score does.

    With *outer*, that script starts the template, as crap-score started by
    dispatch does.
    """
    # A gate run of this suite sets COVERAGE_* variables. The real template
    # would inherit them and write its data into that run, so strip them here.
    env = {
        k: v for k, v in os.environ.items()
        if not k.startswith("COVERAGE_") and k not in GATE_VARIABLES
    }
    env["GATE_OUTPUT"] = "rows.json"
    env.update(patterns)
    return subprocess.run(
        [*([str(outer)] if outer else []), "uv", "run", "--quiet", "--script", "scripts/crap-measure-python"],
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


SHAPE = """\
import typing
from typing import overload


class Box:
    def __init__(self):
        self._width = 0

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if value < 0:
            raise ValueError(value)
        self._width = value

    @width.deleter
    def width(self):
        self._width = 0


@overload
def scale(value: int) -> int: ...
@typing.overload
def scale(value: str) -> str: ...
def scale(value):
    if isinstance(value, str):
        return value * 2
    return value * 2
"""

TEST_SHAPE = """\
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.shape import Box, scale  # noqa: E402


def test_box():
    box = Box()
    box.width = 3
    assert box.width == 3
    del box.width
    assert box.width == 0


def test_scale():
    assert scale(2) == 4
    assert scale("a") == "aa"
"""


@pytest.mark.spec("CG-03-IT-02")
def test_bug_0133_the_template_names_a_property_accessor_and_skips_overload_stubs(
    tmp_path: Path,
) -> None:
    """Scenario: The measuring command reports the qualified name of a method.

    BUG-0133: a property setter and deleter share the name of the getter,
    and @overload stubs share the name of the implementation. Each
    accessor gets its own name, and a stub gets no row, so no qualified
    name appears twice (DEC-12).
    """
    _write_project(tmp_path)
    (tmp_path / "src" / "shape.py").write_text(SHAPE)
    (tmp_path / "tests" / "test_shape.py").write_text(TEST_SHAPE)

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    rows = [r for r in _rows(tmp_path) if r["file"] == "src/shape.py"]
    assert sorted(r["function"] for r in rows) == [
        "Box.__init__",
        "Box.width",
        "Box.width.deleter",
        "Box.width.setter",
        "scale",
    ]
    assert _row(rows, "src/shape.py", "Box.width.setter")["start_line"] == 14
    assert _row(rows, "src/shape.py", "scale")["start_line"] == 28


ALIASED = """\
import typing as t
from typing import overload as ov


class Sizer:
    @ov
    def size(self, value: int) -> int: ...
    @t.overload
    def size(self, value: str) -> str: ...
    def size(self, value):
        return value


@t.overload
def grow(value: int) -> int: ...
def grow(value):
    return value
"""

TEST_ALIASED = """\
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.aliased import Sizer, grow  # noqa: E402


def test_aliased():
    assert Sizer().size(1) == 1
    assert grow(2) == 2
"""


@pytest.mark.spec("CG-03-IT-02")
def test_bug_0133_the_template_skips_overload_stubs_under_an_import_alias(tmp_path: Path) -> None:
    """Scenario: The measuring command reports the qualified name of a method.

    BUG-0133 review: `import typing as t` and `from typing import
    overload as ov` still mark a stub, so the stub gets no row.
    """
    _write_project(tmp_path)
    (tmp_path / "src" / "aliased.py").write_text(ALIASED)
    (tmp_path / "tests" / "test_aliased.py").write_text(TEST_ALIASED)

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    rows = [r for r in _rows(tmp_path) if r["file"] == "src/aliased.py"]
    assert sorted(r["function"] for r in rows) == ["Sizer.size", "grow"]


GETTER = """\
class Dial:
    def __init__(self):
        self._p = 0

    @property
    def p(self):
        return self._p

    @p.getter
    def p(self):
        return self._p + 1
"""

TEST_GETTER = """\
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.dial import Dial  # noqa: E402


def test_dial():
    assert Dial().p == 1
"""


@pytest.mark.spec("CG-03-IT-02")
def test_bug_0133_the_template_names_a_property_getter_accessor(tmp_path: Path) -> None:
    """Scenario: The measuring command reports the qualified name of a method.

    BUG-0133 review: a `@p.getter` that replaces the getter of a property
    gets the name `Dial.p.getter`, so it does not repeat `Dial.p`.
    """
    _write_project(tmp_path)
    (tmp_path / "src" / "dial.py").write_text(GETTER)
    (tmp_path / "tests" / "test_dial.py").write_text(TEST_GETTER)

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    rows = [r for r in _rows(tmp_path) if r["file"] == "src/dial.py"]
    assert sorted(r["function"] for r in rows) == ["Dial.__init__", "Dial.p", "Dial.p.getter"]


MYLIB = """\
def overload(func):
    return func
"""

MULTI = """\
from src.mylib import overload


@overload
def area(kind, size):
    if kind == "square":
        return size * size
    if kind == "circle":
        return 3 * size * size
    if kind == "line":
        return 0
    return None
"""

TEST_MULTI = """\
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.multi import area  # noqa: E402


def test_area():
    assert area("square", 2) == 4
"""


@pytest.mark.spec("CG-03-IT-02")
def test_bug_0135_the_template_measures_a_function_under_an_overload_of_another_library(
    tmp_path: Path,
) -> None:
    """Scenario: The measuring command reports the qualified name of a method.

    BUG-0135: only an overload of typing or typing_extensions marks a stub.
    A function under an overload decorator of another module runs, so it
    gets its row.
    """
    _write_project(tmp_path)
    (tmp_path / "src" / "mylib.py").write_text(MYLIB)
    (tmp_path / "src" / "multi.py").write_text(MULTI)
    (tmp_path / "tests" / "test_multi.py").write_text(TEST_MULTI)

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert _row(_rows(tmp_path), "src/multi.py", "area")["complexity"] == 4


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


OUTER_SCRIPT = """\
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
import subprocess
import sys

sys.exit(subprocess.run(sys.argv[1:]).returncode)
"""


@pytest.mark.spec("CG-03-IT-01")
def test_cg_03_the_template_started_from_an_outer_uv_script_runs_the_project_interpreter(
    tmp_path: Path,
) -> None:
    """Scenario: The measuring command writes its rows to the path in GATE_OUTPUT.

    IMPL-0091: at the merge, dispatch, premerge-check and crap-score each
    start through uv run --script, so several uv environments lie on PATH
    before the project's interpreter folder. The test command still starts
    the project's python3.
    """
    root = tmp_path / "project"
    root.mkdir()
    _write_project(root, ["python3", "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"])
    outer = tmp_path / "outer"
    outer.write_text(OUTER_SCRIPT)
    outer.chmod(0o755)
    project_bin = str(Path(sys.executable).parent)

    result = _run(root, outer, PATH=os.pathsep.join([project_bin, os.environ["PATH"]]))

    assert result.returncode == 0, result.stderr
    _row(_rows(root), "src/parser.py", "Parser.parse")


PICK = """\
\"\"\"Functions whose body stands on the def line, and two with a body of their own.\"\"\"


def keep(function):
    return function


def pick(a, b, c): return a if a else b if b else c if c else 0


def first(a, b): return a if a else b


@keep
def chosen(a): return a if a else 0


def spread(a):
    if a:
        return 1
    return 2


def unused(a):
    if a:
        return 1
    return 2
"""

TEST_PICK = """\
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.pick import chosen, first, spread  # noqa: E402
from src.solo import solo  # noqa: E402


def test_pick():
    assert first(0, 2) == 2
    assert chosen(3) == 3
    assert spread(1) == 1
    assert solo() == 1
"""


@pytest.mark.spec("CG-03-IT-01")
def test_bug_0134_the_template_counts_a_one_line_function_as_covered_only_when_called(
    tmp_path: Path,
) -> None:
    """Scenario: The measuring command writes its rows to the path in GATE_OUTPUT.

    BUG-0134: the def line of a one-line function runs at import, so its
    line data cannot show a call. An untested one-line function gets 0 %,
    a called one gets 100 %, also under a decorator, and a function with a
    body of its own keeps the share of its body lines that ran. A called
    one-line function that is the only statement of its file and starts
    on line 1 gets 0 %, because the module exits with the same arc.
    """
    _write_project(tmp_path)
    (tmp_path / "src" / "pick.py").write_text(PICK)
    (tmp_path / "src" / "solo.py").write_text("def solo(): return 1\n")
    (tmp_path / "tests" / "test_pick.py").write_text(TEST_PICK)

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    rows = [r for r in _rows(tmp_path) if r["file"] == "src/pick.py"]
    coverage = {r["function"]: r["coverage_pct"] for r in rows}
    assert coverage == {
        "keep": 100.0,
        "pick": 0.0,
        "first": 100.0,
        "chosen": 100.0,
        "spread": 66.67,
        "unused": 0.0,
    }
    assert _row(rows, "src/pick.py", "pick")["complexity"] == 4
    assert _row(_rows(tmp_path), "src/solo.py", "solo")["coverage_pct"] == 0.0


# --- CG-03-IT-04, CG-03-IT-08 to CG-03-IT-10: the scope of a run (DEC-84, DEC-85)


def _files(root: Path) -> set[str]:
    return {row["file"] for row in _rows(root)}


@pytest.mark.spec("CG-03-IT-04")
def test_cg_03_with_changed_the_template_stops_for_a_changed_file_coverage_cannot_reach(
    tmp_path: Path,
) -> None:
    """Scenario Outline: A measuring command reports a case it cannot measure, row "and the run judges that file"."""
    _write_project(tmp_path)
    (tmp_path / "scripts" / "sync-stock").write_text(UNREACHED_SCRIPT)

    result = _run(tmp_path, GATE_SCOPE="changed", GATE_CHANGED_FILES="src/parser.py\nscripts/sync-stock")

    assert result.returncode == 1
    assert "coverage cannot reach scripts/sync-stock" in result.stderr
    assert not (tmp_path / "rows.json").exists()


@pytest.mark.spec("CG-03-IT-08")
def test_cg_03_with_changed_an_unchanged_file_no_test_reaches_does_not_stop_the_measure(
    tmp_path: Path,
) -> None:
    """Scenario: With changed, a file that the diff leaves alone and no test reaches does not stop the measure."""
    _write_project(tmp_path)
    (tmp_path / "scripts" / "sync-stock").write_text(UNREACHED_SCRIPT)

    result = _run(tmp_path, GATE_SCOPE="changed", GATE_CHANGED_FILES="src/parser.py\ndocs/readme.md\n")

    assert result.returncode == 0, result.stderr
    assert _files(tmp_path) == {"src/parser.py"}
    assert _row(_rows(tmp_path), "src/parser.py", "Parser.parse")["coverage_pct"] == 100.0


@pytest.mark.spec("CG-03-IT-08")
def test_cg_03_with_changed_and_no_changed_kept_file_the_template_writes_no_row(tmp_path: Path) -> None:
    """DEC-84: a diff without a file that the measure keeps gives an empty array and exit 0."""
    _write_project(tmp_path)

    result = _run(tmp_path, GATE_SCOPE="changed", GATE_CHANGED_FILES="docs/readme.md")

    assert result.returncode == 0, result.stderr
    assert _rows(tmp_path) == []


SELECTOR = """\
#!/bin/sh
printf '%s\\n' "$@" > "$SELECT_LOG"
exec {python} -m pytest -q -p no:cacheprovider tests
"""


TRACE_CONFTEST = """\
import os

import coverage


def pytest_sessionfinish(session):
    current = coverage.Coverage.current()
    if current is not None and "TRACE_LOG" in os.environ:
        with open(os.environ["TRACE_LOG"], "w") as log:
            log.write("\\n".join(sorted(current.get_data().measured_files())))
"""


def _traced(root: Path, log: Path) -> set[str]:
    """The files that coverage traced in the test run, relative to *root*."""
    base = root.resolve()
    return {str(Path(line).resolve().relative_to(base)) for line in log.read_text().splitlines()}


@pytest.mark.spec("CG-03-IT-09")
def test_cg_03_with_changed_the_template_runs_the_select_command_with_the_changed_paths(
    tmp_path: Path,
) -> None:
    """Scenario: With changed, the Python measuring command runs the tests that the changed paths select."""
    root = tmp_path / "project"
    root.mkdir()
    selector = tmp_path / "select-tests"
    selector.write_text(SELECTOR.format(python=sys.executable))
    selector.chmod(0o755)
    _write_project(root, select_command=[str(selector), "--run"])
    log = tmp_path / "select.log"
    trace_log = tmp_path / "trace.log"
    (root / "tests" / "conftest.py").write_text(TRACE_CONFTEST)

    changed = _run(
        root, GATE_SCOPE="changed", GATE_CHANGED_FILES="src/parser.py\ntests/test_parser.py",
        SELECT_LOG=str(log), TRACE_LOG=str(trace_log),
    )

    assert changed.returncode == 0, changed.stderr
    assert log.read_text().splitlines() == ["--run", "src/parser.py", "tests/test_parser.py"]
    assert _files(root) == {"src/parser.py", "tests/test_parser.py"}
    # The template traces only the changed files that the measure keeps. The
    # test imports scripts/import-orders, so a template that traces every
    # file records it, and the files of the rows cannot show that.
    assert _traced(root, trace_log) == {"src/parser.py", "tests/test_parser.py"}
    log.unlink()

    every = _run(root, GATE_SCOPE="all", GATE_CHANGED_FILES="", SELECT_LOG=str(log))

    assert every.returncode == 0, every.stderr
    assert not log.exists(), "with all, the template runs TEST_COMMAND"
    assert "scripts/import-orders" in _files(root)


TMP_PATH_TEST = """\
import os


def test_writes_into_tmp_path(tmp_path):
    (tmp_path / "data").write_text("x")
    with open(os.environ["TMP_LOG"], "w") as log:
        log.write(str(tmp_path))
"""

WRAPPER = """\
#!/bin/sh
exec {python} -m pytest -q tests
"""


@pytest.mark.spec("CG-03-IT-10")
@pytest.mark.parametrize("wrapped", [False, True], ids=["pytest", "a script that starts pytest"])
def test_cg_03_a_run_of_the_template_leaves_no_pytest_temp_folders_behind(
    tmp_path: Path, wrapped: bool
) -> None:
    """Scenario: A run of the Python measuring command leaves no pytest temp folders behind."""
    root = tmp_path / "project"
    root.mkdir()
    temp = tmp_path / "temp"
    temp.mkdir()
    command = [sys.executable, "-m", "pytest", "-q", "tests"]
    if wrapped:
        wrapper = tmp_path / "run-tests"
        wrapper.write_text(WRAPPER.format(python=sys.executable))
        wrapper.chmod(0o755)
        command = [str(wrapper)]
    _write_project(root, test_command=command)
    (root / "tests" / "test_tmp_path.py").write_text(TMP_PATH_TEST)
    log = tmp_path / "tmp-path.log"

    result = _run(root, TMPDIR=str(temp), TMP_LOG=str(log))

    assert result.returncode == 0, result.stderr
    used = Path(log.read_text())
    assert "crap-measure-python-" in str(used), f"pytest put tmp_path outside the work folder: {used}"
    assert not used.exists()
    assert not (root / ".pytest_cache").exists()
    assert [p.name for p in temp.iterdir() if p.name.startswith("pytest")] == []


NESTED_PYTEST_TEST = """\
import subprocess
import sys


def test_starts_another_pytest(tmp_path):
    mark = tmp_path / "mark"
    mark.write_text("x")
    subprocess.run([sys.executable, "-m", "pytest", "-q", "nested"], check=True)
    assert mark.exists(), "the inner pytest cleared the temp folder of the outer one"
"""

INNER_TEST = """\
def test_inner(tmp_path):
    assert tmp_path.is_dir()
"""


@pytest.mark.spec("CG-03-IT-10")
def test_cg_03_a_pytest_that_a_test_starts_keeps_the_temp_folder_of_its_caller(tmp_path: Path) -> None:
    """DEC-85: each pytest process gets its own --basetemp, so an inner pytest clears no outer tmp_path."""
    _write_project(tmp_path, test_command=[sys.executable, "-m", "pytest", "-q", "tests"])
    (tmp_path / "tests" / "test_nested.py").write_text(NESTED_PYTEST_TEST)
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "test_inner.py").write_text(INNER_TEST)

    result = _run(tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert not (tmp_path / ".pytest_cache").exists()


DEEP_TEST = """\
import os
import subprocess
import sys
from pathlib import Path

LEVELS = {levels!r}


def test_level(tmp_path):
    with open(os.environ["TMP_LOG"], "a") as log:
        log.write(str(tmp_path) + "\\n")
    (tmp_path / "mark").write_text("x")
    if LEVELS:
        # The next pytest starts inside tmp_path, below the --basetemp of this one.
        source = Path(__file__).read_text().replace("LEVELS = " + repr(LEVELS), "LEVELS = " + repr(LEVELS - 1))
        (tmp_path / "test_level.py").write_text(source)
        subprocess.run([sys.executable, "-m", "pytest", "-q", "test_level.py"], cwd=tmp_path, check=True)
    assert (tmp_path / "mark").exists()
"""


@pytest.mark.spec("CG-03-IT-10")
def test_bug_0141_a_pytest_two_levels_deep_keeps_its_own_tmp_path(tmp_path: Path) -> None:
    """BUG-0141: the options of the parents pile up, and one --basetemp lies above the working folder of the inner pytest."""
    root = tmp_path / "project"
    root.mkdir()
    _write_project(root, test_command=[sys.executable, "-m", "pytest", "-q", "tests"])
    (root / "tests" / "test_deep.py").write_text(DEEP_TEST.format(levels=2))
    log = tmp_path / "tmp-path.log"

    result = _run(root, TMP_LOG=str(log))

    assert result.returncode == 0, result.stdout + result.stderr
    used = log.read_text().splitlines()
    assert len(used) == 3, used
    assert len(set(used)) == 3, f"two levels share a tmp_path: {used}"
    assert not any(Path(path).exists() for path in used)


ADDOPTS_TEST = """\
import os


def test_options():
    with open(os.environ["ADDOPTS_LOG"], "w") as log:
        log.write(os.environ["PYTEST_ADDOPTS"])
"""


@pytest.mark.spec("CG-03-IT-10")
def test_bug_0141_a_project_option_of_pytest_addopts_survives_the_template(tmp_path: Path) -> None:
    """BUG-0141: the template replaces only its own two options and keeps the others."""
    _write_project(tmp_path, test_command=[sys.executable, "-m", "pytest", "-q", "tests"])
    (tmp_path / "tests" / "test_addopts.py").write_text(ADDOPTS_TEST)
    log = tmp_path / "addopts.log"

    result = _run(tmp_path, PYTEST_ADDOPTS="--strict-markers", ADDOPTS_LOG=str(log))

    assert result.returncode == 0, result.stdout + result.stderr
    options = log.read_text().split()
    assert "--strict-markers" in options
    assert len([o for o in options if o.startswith("--basetemp")]) == 1
    assert options.count("no:cacheprovider") == 1


ODD_NAMES_TEST = """\
import importlib.util
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"


def _load(name):
    spec = importlib.util.spec_from_file_location("odd", SRC / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_odd_names():
    for name in ("a,b.py", "a[1].py", "a]b.py", "a*b.py"):
        module = _load(name)
        assert module.f(1) == 1
        assert module.f(0) == 2
"""

ODD_NAMES = ("a,b.py", "a[1].py", "a]b.py", "a*b.py")


@pytest.mark.spec("CG-03-IT-09")
def test_cg_03_with_changed_the_template_traces_a_path_with_a_comma_or_a_bracket(tmp_path: Path) -> None:
    """IMPL-0103: coverage.py splits `include` at commas and reads brackets as patterns."""
    _write_project(tmp_path)
    for name in ODD_NAMES:
        (tmp_path / "src" / name).write_text("def f(a):\n    if a:\n        return 1\n    return 2\n")
    (tmp_path / "tests" / "test_odd.py").write_text(ODD_NAMES_TEST)

    result = _run(
        tmp_path, GATE_SCOPE="changed", GATE_FILES="src/*",
        GATE_CHANGED_FILES="\n".join(f"src/{name}" for name in ODD_NAMES),
    )

    assert result.returncode == 0, result.stderr
    assert _files(tmp_path) == {f"src/{name}" for name in ODD_NAMES}
    assert {row["coverage_pct"] for row in _rows(tmp_path)} == {100.0}
