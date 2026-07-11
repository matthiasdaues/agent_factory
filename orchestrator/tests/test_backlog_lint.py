"""Tests for backlog-lint — the planning phase's deterministic gate.

Each test creates a minimal backlog directory in tmp_path and runs the linter's
check_backlog() or main() function directly. Covers the happy path and every
defect class the linter must catch (VR-022, ADR-0008).
"""

from __future__ import annotations

import textwrap
from pathlib import Path


# backlog-lint is a script without .py extension; register in sys.modules
# before exec so dataclasses can resolve the module on Python 3.14.
import importlib.util
import sys
from importlib.machinery import SourceFileLoader

_SCRIPT = Path(__file__).resolve().parents[2] / "factory" / "scripts" / "backlog-lint"
_loader = SourceFileLoader("backlog_lint", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("backlog_lint", _loader)
backlog_lint = importlib.util.module_from_spec(_spec)
sys.modules["backlog_lint"] = backlog_lint
_loader.exec_module(backlog_lint)

check_backlog = backlog_lint.check_backlog
parse_frontmatter = backlog_lint.parse_frontmatter
Finding = backlog_lint.Finding


def _write_story(d: Path, name: str, content: str) -> Path:
    p = d / name
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


VALID_STORY = """\
---
id: ST-0001
epic: Core wiring
title: Implement PhaseRunner state machine
classification: standard
status: pending
deps: [ST-0002]
traces: [UC-02, BR-020]
outputs: [src/orchestrator/phase_runner.py]
---

# Implement PhaseRunner state machine

As an operator I want the orchestrator to drive the author→gate→review loop
so that each phase proceeds deterministically.

## Acceptance Criteria

- PhaseRunner executes the loop.
"""

VALID_STORY_2 = """\
---
id: ST-0002
epic: Core wiring
title: Wire ModelResolver
classification: trivial
status: pending
outputs: [src/orchestrator/model_resolver.py]
---

# Wire ModelResolver

Minimal resolver that reads the matrix.
"""


# --- Happy path ---------------------------------------------------------------


class TestHappyPath:
    def test_valid_stories_zero_errors(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(bd, "ST-0001.md", VALID_STORY)
        _write_story(bd, "ST-0002.md", VALID_STORY_2)
        findings, count = check_backlog(bd)
        errors = [f for f in findings if f.severity == "error"]
        assert count == 2
        assert errors == [], [f.line() for f in errors]

    def test_main_exit_zero(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(
            bd,
            "ST-0001.md",
            VALID_STORY_2.replace("ST-0001", "ST-0001").replace("ST-0002", "ST-0001"),
        )
        # Rewrite properly
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-0001
epic: Test
title: Test story
classification: trivial
status: pending
outputs: [foo.py]
---

Body.
""",
        )
        rc = backlog_lint.main(["--backlog-dir", str(bd)])
        assert rc == 0

    def test_json_format(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-0001
epic: Test
title: Test story
classification: trivial
status: pending
outputs: [foo.py]
---

Body.
""",
        )
        rc = backlog_lint.main(["--backlog-dir", str(bd), "--format", "json"])
        assert rc == 0


# --- Missing frontmatter ------------------------------------------------------


class TestParsing:
    def test_no_frontmatter(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(bd, "ST-0001.md", "# Just a heading\n\nNo frontmatter here.\n")
        findings, _ = check_backlog(bd)
        codes = [f.code for f in findings if f.severity == "error"]
        assert "BL-PARSE" in codes

    def test_frontmatter_parses_block_sequence(self):
        text = textwrap.dedent("""\
        ---
        id: ST-0001
        deps:
          - ST-0002
          - ST-0003
        ---

        Body.
        """)
        fm, body = parse_frontmatter(text)
        assert fm["deps"] == ["ST-0002", "ST-0003"]
        assert "Body." in body


# --- Required fields -----------------------------------------------------------


class TestRequiredFields:
    def test_missing_required_field(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        # Missing 'outputs'
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-0001
epic: Test
title: Test
classification: trivial
status: pending
---

Body.
""",
        )
        findings, _ = check_backlog(bd)
        missing = [f for f in findings if f.code == "BL-MISSING"]
        assert any("outputs" in f.message for f in missing)


# --- ID / filename mismatch ---------------------------------------------------


class TestIdFilename:
    def test_id_filename_mismatch(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-9999
epic: Test
title: Test
classification: trivial
status: pending
outputs: [x.py]
---

Body.
""",
        )
        findings, _ = check_backlog(bd)
        ids = [
            f
            for f in findings
            if f.code == "BL-ID" and "does not match filename" in f.message
        ]
        assert len(ids) == 1


# --- Enum validation -----------------------------------------------------------


class TestEnums:
    def test_bad_classification(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-0001
epic: Test
title: Test
classification: extreme
status: pending
outputs: [x.py]
---

Body.
""",
        )
        findings, _ = check_backlog(bd)
        assert any(
            f.code == "BL-ENUM" and "classification" in f.message for f in findings
        )

    def test_bad_status(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-0001
epic: Test
title: Test
classification: trivial
status: cancelled
outputs: [x.py]
---

Body.
""",
        )
        findings, _ = check_backlog(bd)
        assert any(f.code == "BL-ENUM" and "status" in f.message for f in findings)


# --- Output existence / status consistency -----------------------------------


class TestOutputs:
    def test_done_story_requires_existing_output(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-0001
epic: Test
title: Test
classification: trivial
status: done
outputs: [src/missing.py]
---

Body.
""",
        )
        findings, _ = check_backlog(bd)
        assert any(f.code == "VR-027" and f.severity == "error" for f in findings)

    def test_done_story_with_empty_outputs_is_error(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-0001
epic: Test
title: Test
classification: trivial
status: done
outputs: []
---

Body.
""",
        )
        findings, _ = check_backlog(bd)
        assert any(f.code == "VR-027" and f.severity == "error" for f in findings)

    def test_undone_story_warns_when_output_exists(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "existing.py").write_text("print('ok')\n", encoding="utf-8")
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-0001
epic: Test
title: Test
classification: trivial
status: pending
outputs: [src/existing.py]
---

Body.
""",
        )
        findings, _ = check_backlog(bd)
        assert any(f.code == "VR-028" and f.severity == "warning" for f in findings)

    def test_undone_story_with_missing_output_stays_quiet(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-0001
epic: Test
title: Test
classification: trivial
status: pending
outputs: [src/missing.py]
---

Body.
""",
        )
        findings, _ = check_backlog(bd)
        assert not any(f.code == "VR-028" for f in findings)


# --- Dep referential integrity ------------------------------------------------


class TestDeps:
    def test_dep_nonexistent(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-0001
epic: Test
title: Test
classification: trivial
status: pending
deps: [ST-9999]
outputs: [x.py]
---

Body.
""",
        )
        findings, _ = check_backlog(bd)
        assert any(f.code == "BL-DEP" and "non-existent" in f.message for f in findings)

    def test_dep_bad_pattern(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-0001
epic: Test
title: Test
classification: trivial
status: pending
deps: [FOO-01]
outputs: [x.py]
---

Body.
""",
        )
        findings, _ = check_backlog(bd)
        assert any(f.code == "BL-DEP" and "pattern" in f.message for f in findings)


# --- Duplicate IDs -------------------------------------------------------------


class TestDuplicateIds:
    def test_duplicate_story_id(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-0001
epic: Test
title: Test
classification: trivial
status: pending
outputs: [x.py]
---

Body.
""",
        )
        _write_story(
            bd,
            "ST-0002.md",
            """\
---
id: ST-0001
epic: Test
title: Test duplicate
classification: trivial
status: pending
outputs: [y.py]
---

Body.
""",
        )
        findings, _ = check_backlog(bd)
        assert any(f.code == "BL-DUP-ID" for f in findings)


# --- Circular deps -------------------------------------------------------------


class TestCycles:
    def test_circular_deps(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-0001
epic: Test
title: A
classification: trivial
status: pending
deps: [ST-0002]
outputs: [x.py]
---

Body.
""",
        )
        _write_story(
            bd,
            "ST-0002.md",
            """\
---
id: ST-0002
epic: Test
title: B
classification: trivial
status: pending
deps: [ST-0001]
outputs: [y.py]
---

Body.
""",
        )
        findings, _ = check_backlog(bd)
        assert any(f.code == "BL-CYCLE" for f in findings)


# --- Machine field in body -----------------------------------------------------


class TestMachineFieldInBody:
    def test_heading_restates_machine_field(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-0001
epic: Test
title: Test
classification: trivial
status: pending
outputs: [x.py]
---

# Outputs

- x.py
""",
        )
        findings, _ = check_backlog(bd)
        assert any(f.code == "BL-DUP" and "outputs" in f.message for f in findings)


# --- Extra fields --------------------------------------------------------------


class TestExtraFields:
    def test_unknown_field_warns(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-0001
epic: Test
title: Test
classification: trivial
status: pending
outputs: [x.py]
priority: high
---

Body.
""",
        )
        findings, _ = check_backlog(bd)
        assert any(f.code == "BL-EXTRA" and "priority" in f.message for f in findings)


# --- Empty backlog dir ---------------------------------------------------------


class TestEmptyBacklog:
    def test_no_stories(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        findings, count = check_backlog(bd)
        assert count == 0
        assert any(f.code == "BL-EMPTY" for f in findings)

    def test_nonexistent_dir(self, tmp_path: Path):
        bd = tmp_path / "nope"
        findings, count = check_backlog(bd)
        assert any(f.code == "BL-DIR" for f in findings)


# --- report-only exit code -----------------------------------------------------


class TestReportOnly:
    def test_report_only_exits_zero(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        # No stories => info finding, but --report-only should exit 0
        rc = backlog_lint.main(["--backlog-dir", str(bd), "--report-only"])
        assert rc == 0


# --- Traces / traceability (FAGAN-0030, VR-022) ------------------------------


class TestTraces:
    def test_traces_type_must_be_array(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-0001
epic: Test
title: Test
classification: trivial
status: pending
traces: not-an-array
outputs: [x.py]
---

Body.
""",
        )
        findings, _ = check_backlog(bd)
        assert any(f.code == "BL-TYPE" and "traces" in f.message for f in findings)

    def test_empty_traces_accepted(self, tmp_path: Path):
        """Empty traces array is valid — not all stories trace to UCs."""
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-0001
epic: Test
title: Test
classification: trivial
status: pending
traces: []
outputs: [x.py]
---

Body.
""",
        )
        findings, _ = check_backlog(bd)
        errors = [f for f in findings if f.severity == "error"]
        assert errors == []

    def test_valid_traces_accepted(self, tmp_path: Path):
        bd = tmp_path / "backlog"
        bd.mkdir()
        _write_story(
            bd,
            "ST-0001.md",
            """\
---
id: ST-0001
epic: Test
title: Test
classification: trivial
status: pending
traces: [UC-02, BR-020]
outputs: [x.py]
---

Body.
""",
        )
        findings, _ = check_backlog(bd)
        errors = [f for f in findings if f.severity == "error"]
        assert errors == []
