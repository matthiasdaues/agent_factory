"""Contract tests for arc42.projected gating in factory/scripts/arch-lint.

Validates that the workspace property ``arc42.projected`` gates the
correct checks: staleness/diagram-export and missing-chapter-5 severity
when ``"true"`` vs ``"false"`` or absent, while coupling and ADR checks
remain independent.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import types
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Module import — arch-lint has no .py extension; use importlib to load it.
# ---------------------------------------------------------------------------

_SCRIPT = (
    Path(__file__).resolve().parent.parent.parent / "factory" / "scripts" / "arch-lint"
)

_loader = importlib.machinery.SourceFileLoader("arch_lint", str(_SCRIPT))
_spec = importlib.util.spec_from_file_location(
    "arch_lint", str(_SCRIPT), loader=_loader
)
_mod = types.ModuleType("arch_lint")
_mod.__spec__ = _spec
_loader.exec_module(_mod)

dsl_workspace_property = _mod.dsl_workspace_property
main = _mod.main


# ---------------------------------------------------------------------------
# DSL fixture helpers
# ---------------------------------------------------------------------------


def _dsl(projected: str | None = None) -> str:
    """Return a minimal Structurizr DSL workspace.

    When *projected* is given, a workspace-level ``properties`` block
    declares ``arc42.projected`` to that value.  When ``None``, no
    properties block is emitted.
    """
    props = ""
    if projected is not None:
        props = f"""
    properties {{
        "arc42.projected" "{projected}"
    }}"""
    return f"""workspace "Test" "Test workspace" {{{props}
    model {{
        a = softwareSystem "A"
    }}
    views {{}}
}}"""


def _dsl_with_component(projected: str | None = None, component: str = "Alpha") -> str:
    """Return a DSL with a named component inside a ``core`` container."""
    props = ""
    if projected is not None:
        props = f"""
    properties {{
        "arc42.projected" "{projected}"
    }}"""
    return f"""workspace "Test" "Test workspace" {{{props}
    model {{
        sys = softwareSystem "System" {{
            core = container "Core" {{
                x = component "{component}"
            }}
        }}
    }}
    views {{}}
}}"""


def _ch5(component: str = "Beta") -> str:
    """Return a minimal chapter-5 markdown with one component row."""
    return f"""# 5. Building Block View

## 5.2 Components

| Component | Description |
|-----------|-------------|
| **{component}** | test component |

## 5.5 Interfaces Summary
"""


def _setup_arc42(tmp_path: Path, dsl_text: str, ch5_text: str | None = None) -> Path:
    """Create the directory structure main() expects and return the arc42 dir."""
    arc42_dir = tmp_path / "arc42"
    arc42_dir.mkdir()
    (arc42_dir / "architecture.dsl").write_text(dsl_text, encoding="utf-8")
    if ch5_text is not None:
        (arc42_dir / "05_building_block_view.md").write_text(ch5_text, encoding="utf-8")
    return arc42_dir


# ---------------------------------------------------------------------------
# Parser tests — dsl_workspace_property
# ---------------------------------------------------------------------------


class TestDslWorkspaceProperty:
    """Unit tests for ``dsl_workspace_property`` extraction."""

    def test_property_returns_true(self) -> None:
        assert dsl_workspace_property(_dsl("true"), "arc42.projected") == "true"

    def test_property_returns_false(self) -> None:
        assert dsl_workspace_property(_dsl("false"), "arc42.projected") == "false"

    def test_property_absent(self) -> None:
        assert dsl_workspace_property(_dsl(), "arc42.projected") is None

    def test_property_scoped_to_preamble(self) -> None:
        """A ``properties`` block inside ``model { }`` must not match;
        only the workspace-level block in the preamble counts."""
        dsl = """workspace "Test" "Test workspace" {
    properties {
        "arc42.projected" "true"
    }
    model {
        a = softwareSystem "A" {
            properties {
                "arc42.projected" "false"
            }
        }
    }
    views {}
}"""
        result = dsl_workspace_property(dsl, "arc42.projected")
        assert result == "true"


# ---------------------------------------------------------------------------
# Gating tests — main() with tmp_path fixtures
# ---------------------------------------------------------------------------


class TestProjectedGating:
    """End-to-end tests for arc42.projected gating behaviour in main()."""

    def test_projected_false_no_ch5_exits_zero(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """When projected is ``"false"`` and chapter 5 is absent, exit 0
        (INFO findings only, no errors)."""
        arc42_dir = _setup_arc42(tmp_path, _dsl("false"))
        rc = main(["--docs-dir", str(arc42_dir), "--no-validate"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "0 error(s)" in out

    def test_projected_absent_no_ch5_exits_zero(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """When the properties block is missing entirely and chapter 5 is
        absent, exit 0 (same as ``"false"``)."""
        arc42_dir = _setup_arc42(tmp_path, _dsl())
        rc = main(["--docs-dir", str(arc42_dir), "--no-validate"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "0 error(s)" in out

    def test_projected_true_no_ch5_exits_one(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """When projected is ``"true"`` and chapter 5 is absent, exit 1
        with an ARCH-MISSING error."""
        arc42_dir = _setup_arc42(tmp_path, _dsl("true"))
        rc = main(["--docs-dir", str(arc42_dir), "--no-validate"])
        assert rc == 1
        out = capsys.readouterr().out
        assert "ARCH-MISSING" in out

    def test_projected_false_skips_export(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """When projected is ``"false"``, diagram export is skipped (INFO)
        and no ARCH-EXPORT error is raised."""
        arc42_dir = _setup_arc42(tmp_path, _dsl("false"))
        main(["--docs-dir", str(arc42_dir), "--no-validate"])
        out = capsys.readouterr().out
        assert "skipping diagram export" in out
        assert "ARCH-EXPORT" not in out

    def test_coupling_runs_regardless(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Coupling check runs regardless of projected value.  A DSL
        component not in chapter 5 (and vice-versa) produces ARCH-COUPLE
        findings even when projected is ``"false"``."""
        arc42_dir = _setup_arc42(
            tmp_path, _dsl_with_component("false", "Alpha"), _ch5("Beta")
        )
        main(["--docs-dir", str(arc42_dir), "--no-validate"])
        out = capsys.readouterr().out
        assert "ARCH-COUPLE" in out

    def test_adr_independent(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """ADR check runs regardless of arc42.projected value."""
        arc42_dir = _setup_arc42(tmp_path, _dsl("false"))
        adr_dir = tmp_path / "adr"
        adr_dir.mkdir()
        # ADR with missing status — triggers ARCH-ADR-STATUS error
        (adr_dir / "ADR-001.md").write_text(
            "---\nevaluation: none\n---\n# ADR-001\n",
            encoding="utf-8",
        )
        main(["--docs-dir", str(arc42_dir), "--no-validate"])
        out = capsys.readouterr().out
        assert "ARCH-ADR-STATUS" in out
