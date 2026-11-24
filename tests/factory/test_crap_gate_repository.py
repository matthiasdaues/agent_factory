"""Checks of the CRAP gate setup of this repository (docs/spec/features/crap-gate-setup.feature).

Rule: Factory maintainer runs the CRAP gate on this repository for Python
and TypeScript (CG-13).

The text checks read `docs/testing.yaml`, the two measuring commands and the
scripts of this repository. The integration tests copy each measuring command
into a project in tmp_path and run it there, never on the repository root.
CG-13-IT-03 is the one-time setup run (`gate-setup-proof` and `crap-score
--all`); no retained test stands for it.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from conftest import REPO_ROOT

TESTING_YAML = REPO_ROOT / "docs" / "testing.yaml"
SCRIPTS = REPO_ROOT / "packages" / "factory" / "scripts"
PYTHON_COMMAND = REPO_ROOT / "scripts" / "crap-measure-python"
TYPESCRIPT_COMMAND = REPO_ROOT / "scripts" / "crap-measure-typescript"
UV_RUN_LINE = "#!/usr/bin/env -S uv run --script"
PLAIN_LINE = "#!/usr/bin/env python3"
UNTESTED_SCRIPTS = (
    "generate-codex-agents",
    "generate-copilot-agents",
    "openrouter-discover",
    "policy-validate",
    "resolve-model",
    "session-reconcile",
    "usage-capture-lifecycle",
    "usage-query",
)
GATE_VARIABLES = ("GATE_FILES", "GATE_EXCLUDE", "GATE_SCOPE", "GATE_CHANGED_FILES", "GATE_OUTPUT")


def _entry() -> dict:
    return yaml.safe_load(TESTING_YAML.read_text())["gates"]["crap-score"]


def _measure(name: str) -> dict:
    return next(m for m in _entry()["measures"] if m["name"] == name)


def _first_line(path: Path) -> str:
    return path.read_text().splitlines()[0]


def _matches(pattern: str, path: str) -> bool:
    """Glob match as crap-score reads it: * within a segment, ** across segments, ? one character."""
    regex = ""
    i = 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            regex += "(?:.*/)?"
            i += 3
        elif pattern.startswith("**", i):
            regex += ".*"
            i += 2
        elif pattern[i] == "*":
            regex += "[^/]*"
            i += 1
        elif pattern[i] == "?":
            regex += "[^/]"
            i += 1
        else:
            regex += re.escape(pattern[i])
            i += 1
    return re.fullmatch(regex, path) is not None


@pytest.mark.spec("CG-13-LN-01")
def test_cg_13_the_entry_is_enabled_with_a_python_and_a_typescript_measure() -> None:
    """Scenario: The gate is enabled with a measure for Python and one for TypeScript."""
    entry = _entry()
    assert entry["enabled"] is True
    assert isinstance(entry["threshold"], int)
    assert isinstance(entry["measured_minutes"], int)
    assert "ready" not in entry
    assert sorted(m["name"] for m in entry["measures"]) == ["python", "typescript"]
    for measure in entry["measures"]:
        assert (REPO_ROOT / measure["command"]).is_file()


@pytest.mark.spec("CG-13-LN-01")
def test_cg_13_the_time_limit_covers_the_measured_run_time() -> None:
    """Scenario: The time limit covers the measured run time."""
    entry = _entry()
    assert entry["timeout_minutes"] >= entry["measured_minutes"] > 0


@pytest.mark.spec("CG-13-LN-01")
def test_cg_13_the_typescript_measure_uses_the_test_runner_of_node() -> None:
    """Scenario: The TypeScript measure uses the test runner of node."""
    text = TYPESCRIPT_COMMAND.read_text()
    assert "--experimental-test-coverage" in text
    assert '"--test",' in text
    assert _measure("typescript")["command"] == "scripts/crap-measure-typescript"
    assert not (REPO_ROOT / "package.json").exists()


@pytest.mark.spec("CG-13-LN-01")
def test_cg_13_the_measuring_commands_refer_to_nothing_under_agent_factory() -> None:
    """Scenario: The measuring commands depend on no installed Factory copy."""
    for command in (PYTHON_COMMAND, TYPESCRIPT_COMMAND):
        assert ".agent-factory" not in command.read_text(), command.name


@pytest.mark.spec("CG-13-LN-01")
def test_cg_13_no_exclude_pattern_matches_a_script_that_starts_with_uv_run() -> None:
    """Scenario: The scripts that start with uv run show measured coverage."""
    measure = _measure("python")
    uv_scripts = [p for p in SCRIPTS.iterdir() if p.is_file() and _first_line(p) == UV_RUN_LINE]
    assert uv_scripts
    for script in uv_scripts:
        relative = f"packages/factory/scripts/{script.name}"
        assert _matches(measure["files"], relative)
        for pattern in measure["exclude"]:
            assert not _matches(pattern, relative), f"{pattern} matches {relative}"


@pytest.mark.spec("CG-13-LN-02")
@pytest.mark.parametrize("script", UNTESTED_SCRIPTS)
def test_cg_13_the_measure_python_excludes_a_script_that_no_test_runs_by_name_with_a_reason(
    script: str,
) -> None:
    """Scenario Outline: The measure python excludes a script that no test runs, by name with a reason."""
    path = f"packages/factory/scripts/{script}"
    assert _first_line(REPO_ROOT / path) == PLAIN_LINE
    assert path in _measure("python")["exclude"]
    lines = TESTING_YAML.read_text().splitlines()
    index = lines.index(f'          - "{path}"')
    assert lines[index - 1].lstrip().startswith("#")
    assert "No test runs it yet" in lines[index - 1]


@pytest.mark.spec("CG-13-LN-03")
@pytest.mark.parametrize("script", ["trigger", "validate"])
def test_cg_13_the_scripts_that_tests_run_start_with_uv_run(script: str) -> None:
    """Scenario: The scripts that tests run and that start with python3 switch to uv run."""
    assert _first_line(SCRIPTS / script) == UV_RUN_LINE
    relative = f"packages/factory/scripts/{script}"
    for pattern in _measure("python")["exclude"]:
        assert not _matches(pattern, relative)


def _clean_env() -> dict[str, str]:
    return {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("COVERAGE_", "NODE_V8_COVERAGE")) and k not in GATE_VARIABLES
    }


def _fill(source: Path, target: Path, pattern: str, replacement: str) -> None:
    """Copy *source* to *target* with one match of *pattern* replaced."""
    text, count = re.subn(
        pattern, lambda _m: replacement, source.read_text(), count=1, flags=re.DOTALL | re.MULTILINE
    )
    assert count == 1, f"{source.name} has no match for {pattern}"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    target.chmod(0o755)


PLANTED_SCRIPT = """\
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
import sys


def shout(word):
    if not word:
        return ""
    return word.upper()


if __name__ == "__main__":
    print(shout(sys.argv[1] if len(sys.argv) > 1 else ""))
"""

PLANTED_SCRIPT_TEST = """\
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "shout"


def test_shout():
    result = subprocess.run(
        ["uv", "run", "--quiet", "--script", str(SCRIPT), "hi"], capture_output=True, text=True
    )
    assert result.stdout.strip() == "HI"
"""


@pytest.mark.spec("CG-13-IT-01")
def test_cg_13_the_python_command_shows_coverage_for_a_uv_run_script(tmp_path: Path) -> None:
    """Scenario: The scripts that start with uv run show measured coverage."""
    (tmp_path / "tools").mkdir()
    script = tmp_path / "tools" / "shout"
    script.write_text(PLANTED_SCRIPT)
    script.chmod(0o755)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_shout.py").write_text(PLANTED_SCRIPT_TEST)
    command = tmp_path / "scripts" / "crap-measure-python"
    test_command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"]
    _fill(
        PYTHON_COMMAND,
        command,
        r"^TEST_COMMAND: list\[str\] = \[.*?^\]$",
        f"TEST_COMMAND: list[str] = {test_command!r}",
    )
    _fill(command, command, r"^SELECT_COMMAND: list\[str\] = \[.*?\]$", "SELECT_COMMAND: list[str] = []")
    env = _clean_env()
    env["GATE_OUTPUT"] = "rows.json"
    result = subprocess.run(
        ["uv", "run", "--quiet", "--script", "scripts/crap-measure-python"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    rows = json.loads((tmp_path / "rows.json").read_text())
    shout = [r for r in rows if r.get("function") == "shout" and r["file"] == "tools/shout"]
    assert len(shout) == 1, rows
    assert shout[0]["coverage_pct"] > 0


PLANTED_TS = """\
export function sign(n: number): string {
  if (n < 0) {
    return "negative";
  }
  return "positive";
}
"""

PLANTED_TS_TEST = """\
import { test } from "node:test";
import assert from "node:assert";
import { sign } from "./sign.ts";

test("sign", () => {
  assert.strictEqual(sign(-1), "negative");
  assert.strictEqual(sign(1), "positive");
});
"""


@pytest.mark.spec("CG-13-IT-02")
def test_cg_13_the_typescript_command_reports_a_planted_function(tmp_path: Path) -> None:
    """Scenario: The TypeScript measure uses the test runner of node."""
    subprocess.run(["git", "init", "--quiet"], cwd=tmp_path, check=True)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "sign.ts").write_text(PLANTED_TS)
    (tmp_path / "src" / "sign.test.ts").write_text(PLANTED_TS_TEST)
    _fill(
        TYPESCRIPT_COMMAND,
        tmp_path / "scripts" / "crap-measure-typescript",
        r"^const TEST_COMMAND = \[.*?^\];$",
        'const TEST_COMMAND = [process.execPath, "--experimental-strip-types", "--test", "src/**/*.test.ts"];',
    )
    env = _clean_env()
    env["GATE_OUTPUT"] = "rows.json"
    env["GATE_FILES"] = "src/*.ts"
    env["GATE_EXCLUDE"] = "src/*.test.ts"
    result = subprocess.run(
        ["node", "scripts/crap-measure-typescript"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    rows = json.loads((tmp_path / "rows.json").read_text())
    sign = [r for r in rows if r.get("function") == "sign"]
    assert len(sign) == 1, rows
    assert sign[0]["complexity"] == 2
    assert sign[0]["coverage_pct"] == 100


def _run_typescript(
    tmp_path: Path,
    files: dict[str, str],
    env_extra: dict[str, str] | None = None,
    test_command: str = '[process.execPath, "--experimental-strip-types", "--test", "src/**/*.test.ts"]',
) -> subprocess.CompletedProcess[str]:
    """Plant *files* in a git folder and run the TypeScript command there."""
    subprocess.run(["git", "init", "--quiet"], cwd=tmp_path, check=True)
    for name, text in files.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(text)
    _fill(
        TYPESCRIPT_COMMAND,
        tmp_path / "scripts" / "crap-measure-typescript",
        r"^const TEST_COMMAND = \[.*?^\];$",
        f"const TEST_COMMAND = {test_command};",
    )
    env = _clean_env()
    env["GATE_OUTPUT"] = "rows.json"
    env["GATE_FILES"] = "src/*.ts"
    env["GATE_EXCLUDE"] = "src/*.test.ts"
    env.update(env_extra or {})
    return subprocess.run(
        [shutil.which("node") or "node", "scripts/crap-measure-typescript"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )


def _rows(tmp_path: Path) -> list[dict]:
    return json.loads((tmp_path / "rows.json").read_text())


UNCALLED_TS = """\
export const used = (n: number): number => n + 1;

export const pick = (a: number, b: number, c: number): number => a > 0 ? (b > 0 ? (c > 0 ? 1 : 2) : (c > 0 ? 3 : 4)) : (b > 0 ? (c > 0 ? 5 : 6) : 7);

export const never = (xs: number[]): number[] => xs.filter((x) => {
  if (x > 1) return true;
  return false;
});

export function skipped(xs: number[]): number[] {
  return xs.filter((x) => {
    if (x > 1) return true;
    return false;
  });
}

export const box: any = {};
box.assigned = (a: number, b: number, c: number): number => a > 0 ? (b > 0 ? (c > 0 ? 1 : 2) : (c > 0 ? 3 : 4)) : (b > 0 ? (c > 0 ? 5 : 6) : 7);

export const pair = { first: (n: number): number => n > 0 ? 1 : 2, second: (n: number): number => n > 0 ? 3 : 4 };

export const split = { warm: (n: number): number => n + 1, late:
  (a: number): number => a > 0 ? (a > 1 ? (a > 2 ? (a > 3 ? (a > 4 ? 1 : 2) : 3) : 4) : 5) : 6, ok:
  (a: number): number => a > 0 ? (a > 1 ? (a > 2 ? (a > 3 ? (a > 4 ? 1 : 2) : 3) : 4) : 5) : 6 };

export function ran(xs: number[]): number[] {
  return xs.filter((x) => {
    if (x > 1) return true;
    return false;
  });
}
"""

UNCALLED_TS_TEST = """\
import { test } from "node:test";
import assert from "node:assert";
import { used, ran, skipped, pair, split } from "./pick.ts";

test("used", () => {
  assert.strictEqual(used(1), 2);
  assert.deepStrictEqual(ran([1, 2]), [2]);
  assert.deepStrictEqual(skipped([]), []);
  assert.strictEqual(pair.second(1), 3);
  assert.strictEqual(split.warm(1), 2);
  assert.strictEqual(split.ok(1), 5);
});
"""


@pytest.mark.spec("CG-13-IT-02")
def test_cg_13_a_function_that_no_test_calls_gets_zero_coverage(tmp_path: Path) -> None:
    """IMPL-0105: lcov marks a shared line as run; the function records tell better."""
    result = _run_typescript(tmp_path, {"src/pick.ts": UNCALLED_TS, "src/pick.test.ts": UNCALLED_TS_TEST})
    assert result.returncode == 0, result.stdout + result.stderr
    by_name = {r["function"]: r for r in _rows(tmp_path)}
    assert by_name["pick"]["complexity"] == 7
    assert by_name["pick"]["coverage_pct"] == 0
    assert by_name["never"]["coverage_pct"] == 0
    callbacks = [r for r in by_name.values() if r["function"].startswith("never.(anonymous)")]
    assert callbacks and all(r["coverage_pct"] == 0 for r in callbacks), by_name
    assert by_name["used"]["coverage_pct"] == 100
    assert by_name["late"]["complexity"] == 6
    assert by_name["late"]["coverage_pct"] == 0
    assert by_name["ok"]["coverage_pct"] == 100
    assert by_name["assigned"]["complexity"] == 7
    assert by_name["assigned"]["coverage_pct"] == 0
    assert by_name["first"]["coverage_pct"] == 0
    assert by_name["second"]["coverage_pct"] == 100
    skipped = [r for r in by_name.values() if r["function"].startswith("skipped.(anonymous)")]
    assert skipped and all(r["coverage_pct"] == 0 for r in skipped), by_name
    assert by_name["ran"]["coverage_pct"] == 100
    ran_callback = [r for r in by_name.values() if r["function"].startswith("ran.(anonymous)")]
    assert ran_callback and all(r["coverage_pct"] > 0 for r in ran_callback), by_name


PROPERTY_TS = """\
export const handlers = {
  first: function (n: number): number {
    if (n > 0) return 1;
    return 0;
  },
};
"""

CLASS_FIELD_TS = """\
export class Box {
  f = (a: number): number => (a > 0 ? 1 : 2);
}
"""

CLASS_FIELD_TS_TEST = """\
import { test } from "node:test";
import assert from "node:assert";
import { Box } from "./box.ts";

test("f", () => {
  assert.equal(new Box().f(1), 1);
});
"""

PROPERTY_TS_TEST = """\
import { test } from "node:test";
import assert from "node:assert";
import { handlers } from "./obj.ts";

test("first", () => {
  assert.equal(handlers.first(1), 1);
  assert.equal(handlers.first(0), 0);
});
"""


@pytest.mark.spec("CG-13-IT-02")
def test_cg_13_a_function_expression_as_an_object_value_gets_a_row(tmp_path: Path) -> None:
    """IMPL-0106: the function is named as ESLint and lcov name it."""
    result = _run_typescript(tmp_path, {"src/obj.ts": PROPERTY_TS, "src/obj.test.ts": PROPERTY_TS_TEST})
    assert result.returncode == 0, result.stdout + result.stderr
    rows = _rows(tmp_path)
    assert [r["function"] for r in rows] == ["first"], rows
    assert rows[0]["complexity"] == 2
    assert rows[0]["coverage_pct"] == 100


@pytest.mark.spec("CG-13-IT-02")
def test_cg_13_an_arrow_function_as_a_class_field_gets_a_row(tmp_path: Path) -> None:
    """IMPL-0110: the arrow function of a class field is measured, not a stop."""
    result = _run_typescript(tmp_path, {"src/box.ts": CLASS_FIELD_TS, "src/box.test.ts": CLASS_FIELD_TS_TEST})
    assert result.returncode == 0, result.stdout + result.stderr
    rows = _rows(tmp_path)
    assert [r["function"] for r in rows] == ["Box.f"], rows
    assert rows[0]["complexity"] == 2
    assert rows[0]["coverage_pct"] == 100


FAKE_RUNNER = """\
// Stands in for the test run: it writes an lcov report with one function
// record for a line that holds two functions.
const fs = require("node:fs");
const flag = process.execArgv.filter((a) => a.startsWith("--test-reporter-destination=")).pop();
fs.writeFileSync(flag.split("=")[1], "SF:src/two.ts\\nFN:1,only\\nFNDA:1,only\\nDA:1,1\\nend_of_record\\n");
"""


@pytest.mark.spec("CG-13-IT-02")
def test_cg_13_two_functions_on_a_line_with_one_record_both_get_zero_coverage(tmp_path: Path) -> None:
    """IMPL-0111: a function that pairs with no single record fails safe."""
    files = {
        "src/two.ts": "export const two = [(a: number) => a > 0 ? 1 : 2, (b: number) => b > 0 ? 3 : 4];\n",
        "fake-runner.cjs": FAKE_RUNNER,
    }
    result = _run_typescript(
        tmp_path, files, test_command='[process.execPath, "--no-warnings", "fake-runner.cjs"]'
    )
    assert result.returncode == 0, result.stdout + result.stderr
    rows = _rows(tmp_path)
    assert len(rows) == 2, rows
    assert [r["coverage_pct"] for r in rows] == [0, 0]


def _assert_no_rows(tmp_path: Path, result: subprocess.CompletedProcess[str], cause: str) -> None:
    assert result.returncode != 0, result.stdout + result.stderr
    assert "cannot measure" in result.stderr
    assert cause in result.stderr, result.stderr
    assert not (tmp_path / "rows.json").exists()


@pytest.mark.spec("CG-13-IT-02")
def test_cg_13_a_failed_test_run_exits_non_zero_and_writes_no_rows(tmp_path: Path) -> None:
    failing = PLANTED_TS_TEST.replace('"positive");', '"wrong");')
    result = _run_typescript(tmp_path, {"src/sign.ts": PLANTED_TS, "src/sign.test.ts": failing})
    _assert_no_rows(tmp_path, result, "the test run failed")


@pytest.mark.spec("CG-13-IT-02")
def test_cg_13_a_file_that_no_test_loads_exits_non_zero_and_writes_no_rows(tmp_path: Path) -> None:
    files = {
        "src/sign.ts": PLANTED_TS,
        "src/sign.test.ts": PLANTED_TS_TEST,
        "src/lonely.ts": "export const lonely = (): number => 1;\n",
    }
    result = _run_typescript(tmp_path, files)
    _assert_no_rows(tmp_path, result, "coverage cannot reach src/lonely.ts")


@pytest.mark.spec("CG-13-IT-02")
def test_cg_13_eslint_that_cannot_start_exits_non_zero_and_writes_no_rows(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name in ("git",):
        found = subprocess.run(["which", name], capture_output=True, text=True, check=True).stdout.strip()
        (bin_dir / name).symlink_to(found)
    work = tmp_path / "work"
    work.mkdir()
    result = _run_typescript(
        work,
        {"src/sign.ts": PLANTED_TS, "src/sign.test.ts": PLANTED_TS_TEST},
        {"PATH": str(bin_dir)},
    )
    _assert_no_rows(work, result, "ESLint cannot start")
