"""Contract tests for arch-lint gate script."""

from __future__ import annotations

from conftest import load_script

al = load_script("arch-lint")


class TestDslWorkspaceProperty:
    DSL_WITH_PROPERTY = """\
workspace "test" {
    properties {
        "arc42.projected" "true"
        "version" "1.0"
    }
    model {
        softwareSystem "X" {
            properties {
                "arc42.projected" "false"
            }
        }
    }
}
"""

    def test_reads_workspace_property(self):
        assert (
            al.dsl_workspace_property(self.DSL_WITH_PROPERTY, "arc42.projected")
            == "true"
        )

    def test_ignores_model_level_property(self):
        result = al.dsl_workspace_property(self.DSL_WITH_PROPERTY, "arc42.projected")
        assert result == "true"

    def test_missing_key_returns_none(self):
        assert al.dsl_workspace_property(self.DSL_WITH_PROPERTY, "nonexistent") is None

    def test_no_properties_block_returns_none(self):
        assert al.dsl_workspace_property("workspace { model { } }", "any") is None


class TestDslCoreComponents:
    def test_extracts_component_names(self):
        dsl = """
        core = container "Core" {
            validator = component "Validator"
            dispatcher = component "Dispatcher"
        }
        """
        result = al.dsl_core_components(dsl)
        assert "Validator" in result
        assert "Dispatcher" in result

    def test_empty_dsl_returns_empty(self):
        assert al.dsl_core_components("") == set()


class TestDslPorts:
    def test_extracts_port_names(self):
        dsl = 'ports = component "Ports" "Adapters: CLI, HTTP, File"'
        result = al.dsl_ports(dsl)
        assert "CLI" in result
        assert "HTTP" in result
        assert "File" in result

    def test_no_ports_returns_empty(self):
        assert al.dsl_ports("no ports here") == set()


class TestCh5CoreComponents:
    def test_extracts_bold_names(self):
        md = """\
## 5.2 Validation Layer

| Component | Description |
|---|---|
| **RuleEngine** | Validates rules |
| **Parser** | Parses input |

## 5.5 Interfaces Summary
"""
        result = al.ch5_core_components(md)
        assert "RuleEngine" in result
        assert "Parser" in result

    def test_no_section_returns_empty(self):
        assert al.ch5_core_components("no sections here") == set()


class TestParseAdrFrontmatter:
    def test_valid_frontmatter(self):
        text = "---\nid: ADR-0001\nstatus: accepted\nevaluation: pugh-matrix\n---\nBody"
        fm = al._parse_adr_frontmatter(text)
        assert fm["status"] == "accepted"
        assert fm["evaluation"] == "pugh-matrix"

    def test_no_frontmatter_returns_none(self):
        assert al._parse_adr_frontmatter("No frontmatter here") is None

    def test_missing_closing_returns_none(self):
        assert al._parse_adr_frontmatter("---\nstatus: accepted\n") is None


class TestParseAdrStatusLine:
    def test_accepted(self):
        assert (
            al._parse_adr_status_line("**Status**: Accepted — some reason")
            == "accepted"
        )

    def test_proposed(self):
        assert al._parse_adr_status_line("**Status**: Proposed") == "proposed"

    def test_superseded(self):
        text = "**Status**: superseded by [ADR-0005](adr-0005.md)"
        assert al._parse_adr_status_line(text) == "superseded by ADR-0005"

    def test_no_status_returns_none(self):
        assert al._parse_adr_status_line("No status line here") is None


class TestCheckCoupling:
    def test_matching_components_no_errors(self):
        dsl = """
        core = container "Core" {
            a = component "Alpha"
            b = component "Beta"
        }
        """
        ch5 = """\
## 5.2 Components

| Component | Description |
|---|---|
| **Alpha** | Does alpha |
| **Beta** | Does beta |

## 5.5 Summary
"""
        rep = al.Report()
        al.check_coupling(rep, dsl, ch5)
        errors = [i for i in rep.items if i[0] == "ERROR"]
        assert errors == []

    def test_missing_in_ch5_errors(self):
        dsl = """
        core = container "Core" {
            a = component "Alpha"
            b = component "Extra"
        }
        """
        ch5 = "## 5.2 Components\n| **Alpha** | desc |\n## 5.5 end\n"
        rep = al.Report()
        al.check_coupling(rep, dsl, ch5)
        errors = [i for i in rep.items if i[0] == "ERROR" and "Extra" in i[2]]
        assert len(errors) >= 1

    def test_empty_sets_warn(self):
        rep = al.Report()
        al.check_coupling(rep, "", "## 5.2 x\n## 5.5 end\n")
        warnings = [i for i in rep.items if i[0] == "WARNING"]
        assert len(warnings) >= 1


class TestCheckAdrEvaluation:
    def test_valid_adr_passes(self, tmp_path):
        adr = tmp_path / "adr-0001.md"
        adr.write_text("---\nstatus: accepted\nevaluation: none\n---\nBody text.")
        rep = al.Report()
        al.check_adr_evaluation(rep, tmp_path)
        errors = [i for i in rep.items if i[0] == "ERROR"]
        assert errors == []

    def test_pugh_matrix_without_table_errors(self, tmp_path):
        adr = tmp_path / "adr-0002.md"
        adr.write_text(
            "---\nstatus: accepted\nevaluation: pugh-matrix\n---\nNo table here."
        )
        rep = al.Report()
        al.check_adr_evaluation(rep, tmp_path)
        errors = [i for i in rep.items if i[0] == "ERROR" and "ARCH-ADR-EVAL" in i[1]]
        assert len(errors) == 1

    def test_none_with_table_errors(self, tmp_path):
        adr = tmp_path / "adr-0003.md"
        adr.write_text(
            "---\nstatus: proposed\nevaluation: none\n---\n"
            "| Criteria | A | B |\n|---|---|---|\n| **Weighted total** | 5 | 3 |\n"
        )
        rep = al.Report()
        al.check_adr_evaluation(rep, tmp_path)
        errors = [i for i in rep.items if i[0] == "ERROR" and "ARCH-ADR-EVAL" in i[1]]
        assert len(errors) == 1

    def test_missing_status_errors(self, tmp_path):
        adr = tmp_path / "adr-0004.md"
        adr.write_text("---\nevaluation: none\n---\nBody.")
        rep = al.Report()
        al.check_adr_evaluation(rep, tmp_path)
        errors = [i for i in rep.items if i[0] == "ERROR" and "STATUS" in i[1]]
        assert len(errors) >= 1

    def test_bold_prose_status_fallback(self, tmp_path):
        adr = tmp_path / "adr-0005.md"
        adr.write_text("# ADR-0005\n\n**Status**: Accepted — good reason\n\nBody text.")
        rep = al.Report()
        al.check_adr_evaluation(rep, tmp_path)
        errors = [i for i in rep.items if i[0] == "ERROR"]
        assert errors == []

    def test_invalid_evaluation_value_errors(self, tmp_path):
        adr = tmp_path / "adr-0006.md"
        adr.write_text("---\nstatus: accepted\nevaluation: invalid\n---\nBody.")
        rep = al.Report()
        al.check_adr_evaluation(rep, tmp_path)
        errors = [i for i in rep.items if i[0] == "ERROR" and "ARCH-ADR-EVAL" in i[1]]
        assert len(errors) == 1


class TestReport:
    def test_counts_severities(self):
        rep = al.Report()
        rep.error("A", "msg1")
        rep.error("B", "msg2")
        rep.warn("C", "msg3")
        rep.info("D", "msg4")
        assert rep.n("ERROR") == 2
        assert rep.n("WARNING") == 1
        assert rep.n("INFO") == 1


class TestMainRoundTrip:
    """Integration: main() wires parsing → checking → exit code."""

    def test_no_arc42_no_adr_exits_zero(self, tmp_path):
        docs = tmp_path / "docs" / "arc42"
        docs.mkdir(parents=True)
        rc = al.main(["--docs-dir", str(docs), "--no-validate"])
        assert rc == 0

    def test_dsl_only_no_ch5_with_projected_exits_nonzero(self, tmp_path):
        docs = tmp_path / "docs" / "arc42"
        docs.mkdir(parents=True)
        (docs / "architecture.dsl").write_text(
            'workspace "x" {\n'
            '  properties { "arc42.projected" "true" }\n'
            "  model { }\n}\n"
        )
        rc = al.main(["--docs-dir", str(docs), "--no-validate"])
        assert rc > 0

    def test_dsl_only_not_projected_exits_zero(self, tmp_path):
        docs = tmp_path / "docs" / "arc42"
        docs.mkdir(parents=True)
        (docs / "architecture.dsl").write_text('workspace "x" { model { } }\n')
        rc = al.main(["--docs-dir", str(docs), "--no-validate"])
        assert rc == 0

    def test_adr_valid_exits_zero(self, tmp_path):
        docs = tmp_path / "docs" / "arc42"
        docs.mkdir(parents=True)
        adr = docs.parent / "adr"
        adr.mkdir()
        (adr / "adr-0001.md").write_text(
            "---\nstatus: accepted\nevaluation: none\n---\nBody."
        )
        rc = al.main(["--docs-dir", str(docs), "--no-validate"])
        assert rc == 0

    def test_adr_invalid_exits_nonzero(self, tmp_path):
        docs = tmp_path / "docs" / "arc42"
        docs.mkdir(parents=True)
        adr = docs.parent / "adr"
        adr.mkdir()
        (adr / "adr-0001.md").write_text(
            "---\nstatus: accepted\nevaluation: pugh-matrix\n---\nNo matrix."
        )
        rc = al.main(["--docs-dir", str(docs), "--no-validate"])
        assert rc > 0
