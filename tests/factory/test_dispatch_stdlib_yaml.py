"""The stdlib YAML loader in dispatch_lib reads what PyYAML reads (BUG-0085).

dispatch runs under `uv run --script` without PyYAML, so `_stdlib_load`
parses docs/testing.yaml and the ledger. Each test runs `_stdlib_load` and
`yaml.safe_load` over the same text and requires equal results.
"""

from __future__ import annotations

import itertools
import re
from pathlib import Path

import dispatch_lib as lib
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL = REPO_ROOT / "packages" / "factory" / "skills" / "detect-test-regime" / "SKILL.md"


def _assert_same(text: str) -> None:
    assert lib._stdlib_load(text) == yaml.safe_load(text)


def _schema_example() -> str:
    """The testing.yaml schema example under 'Output schema' in the skill."""
    section = SKILL.read_text().split("## Output schema", 1)[1]
    match = re.search(r"```yaml\n(.*?)```", section, re.DOTALL)
    assert match, f"no yaml block under 'Output schema' in {SKILL}"
    return match.group(1)


# An installed project: the command on line 10, a folded scalar on line 103.
_FILLER = "".join(f"  - name: suite{n}\n    run_all: \"make s{n}\"\n" for n in range(44))
INSTALLED_PROJECT = (
    "# Code is the source of truth. Re-run the detect-test-regime skill when\n"
    "# the project's test setup changes.\n"
    "\n"
    "testing_strategy: docs/testing-strategy.md\n"
    "\n"
    "test_all: \"make test && make frontend_test\"   # composite command\n"
    "\n"
    "# Compatibility command read by the dispatch script.\n"
    "\n"
    "test_command: \"make test && make frontend_test\"\n"
    "\n"
    "suites:\n"
    + _FILLER
    + "\n"
    "# Where CI and local runs differ.\n"
    "ci_divergence: >-\n"
    "  CI runs the backend suite inside the compose stack, while local runs\n"
    "  use the host interpreter.\n"
    "\n"
    "  The frontend suite runs only on CI.\n"
)
assert INSTALLED_PROJECT.splitlines()[9].startswith("test_command:")
assert INSTALLED_PROJECT.splitlines()[102] == "ci_divergence: >-"

FOLDED_TEST_ALL = (
    "testing_strategy: docs/testing-strategy.md\n"
    "test_all: >-\n"
    "  make test && make frontend_test\n"
    "suites: []\n"
)


def test_the_documented_schema_example_loads_as_pyyaml_reads_it():
    _assert_same(_schema_example())


@pytest.mark.parametrize("text", [INSTALLED_PROJECT, FOLDED_TEST_ALL])
def test_real_testing_yaml_shapes_load_as_pyyaml_reads_them(text):
    _assert_same(text)


BODIES = {
    "two_lines": ["line one", "line two"],
    "empty_lines_inside": ["a", "b", "", "c", "", "", "d"],
    "more_indented": ["a", "b", "  indented", "  more", "c", "", "  deep", "d"],
    "leading_empty_line": ["", "first", "second"],
    "comment_like": ["run # not a comment", "x: y"],
}

# (prefix lines, header line template, body indent, sibling line)
POSITIONS = {
    "top_level": ([], "text: {h}", 2, "after: 1"),
    "nested": (["outer:"], "  text: {h}", 4, "  after: 1"),
    "list_item_first_key": (["items:"], "  - text: {h}", 6, "    after: 1"),
    "list_item_later_key": (["items:", "  - name: x"], "    text: {h}", 6, "    after: 1"),
    "list_scalar": (["items:"], "  - {h}", 4, "  - tail"),
}


def _block_doc(
    header: str, body: list[str], position: str, trailing_empty: int, last: bool
) -> str:
    prefix, header_line, indent, sibling = POSITIONS[position]
    lines = [*prefix, header_line.format(h=header)]
    lines += [(" " * indent + line) if line else "" for line in body]
    lines += [""] * trailing_empty
    if not last:
        lines.append(sibling)
    return "\n".join(lines) + "\n"


@pytest.mark.parametrize(
    ("header", "body", "position", "trailing_empty", "last"),
    [
        (style + chomp, body, position, trailing, last)
        for style, chomp in itertools.product("|>", ["", "-", "+"])
        for body, position in itertools.product(BODIES, POSITIONS)
        for trailing, last in [(0, False), (2, False), (0, True), (2, True)]
    ],
)
def test_block_scalars_load_as_pyyaml_reads_them(
    header, body, position, trailing_empty, last
):
    _assert_same(_block_doc(header, BODIES[body], position, trailing_empty, last))


@pytest.mark.parametrize("header", ["|", ">-", "|+"])
def test_a_block_scalar_at_the_end_of_a_file_without_a_newline(header):
    _assert_same(f"a: 1\nb: {header}\n  one\n\n  two")


@pytest.mark.parametrize("header", ["|", ">", "|+", ">-"])
def test_an_empty_block_scalar_loads_as_pyyaml_reads_it(header):
    _assert_same(f"a: {header}\nb: 1\n")


def test_a_header_comment_is_ignored():
    _assert_same("a: >-  # folded\n  one\n  two\nb: 1\n")


def test_an_explicit_indentation_indicator_is_rejected():
    with pytest.raises(ValueError, match="explicit indentation indicator"):
        lib._stdlib_load("a: |2\n   text\n")


def test_a_ledger_with_multi_line_text_round_trips_without_pyyaml(tmp_path, monkeypatch):
    reason = "red suite:\n\n  test_x failed # see log\n'quoted' and \"double\"\n"
    evidence = "line one\nline two"
    ledger = lib.Ledger()
    ledger.stories["ST-0001"] = lib.StoryEntry(
        id="ST-0001", status=lib.StoryState.BLOCKED, reason=reason, evidence=evidence
    )
    path = tmp_path / "ledger.yaml"
    monkeypatch.setattr(lib, "yaml", None)

    ledger.save(path)
    loaded = lib.Ledger.load(path)

    assert loaded.stories["ST-0001"].reason == reason
    assert loaded.stories["ST-0001"].evidence == evidence
    assert yaml.safe_load(path.read_text())["stories"]["ST-0001"]["reason"] == reason
