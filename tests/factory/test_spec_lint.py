"""Contract tests for spec-lint gate script."""

from __future__ import annotations

from pathlib import Path

from conftest import load_script

sl = load_script("spec-lint")


class TestFencedBlocks:
    def test_extracts_matching_language(self):
        text = "```gherkin\nScenario: X\n```\n"
        blocks = sl.fenced_blocks(text, "gherkin")
        assert len(blocks) == 1
        assert "Scenario: X" in blocks[0]

    def test_ignores_other_languages(self):
        text = "```python\nprint('hi')\n```\n"
        assert sl.fenced_blocks(text, "gherkin") == []

    def test_multiple_blocks(self):
        text = "```mermaid\nA\n```\ntext\n```mermaid\nB\n```\n"
        blocks = sl.fenced_blocks(text, "mermaid")
        assert len(blocks) == 2

    def test_empty_text(self):
        assert sl.fenced_blocks("", "any") == []


class TestCheckRequiredArtifacts:
    def test_all_present(self, tmp_path):
        (tmp_path / "prd.md").touch()
        (tmp_path / "scope-map.md").touch()
        supp = tmp_path / "supplementary_specs"
        supp.mkdir()
        (supp / "entity-model.md").touch()
        (supp / "validation-rules.md").touch()
        findings = sl.check_required_artifacts(tmp_path)
        assert findings == []

    def test_missing_prd(self, tmp_path):
        findings = sl.check_required_artifacts(tmp_path)
        assert any(f.code == "STRUCT005" and "prd.md" in f.artifact for f in findings)


class TestCheckUseCases:
    def _make_uc(self, uc_dir: Path, name: str = "UC-01-test.md", content: str = ""):
        if not content:
            content = (
                "# UC-01 Test\n\n"
                "**Realizes**: AG-01\n\n"
                "## Primary Actor\nUser\n\n"
                "## Stakeholders & Interests\nTeam\n\n"
                "## Trigger\nAction\n\n"
                "## Preconditions\nNone\n\n"
                "## Main Success Scenario\n1. Step\n\n"
                "## Extensions\nNone\n\n"
                "## Postconditions\nResult\n\n"
                "## Business Rules\nBR-001\n\n"
                "```gherkin\nScenario: Test\nGiven setup\nWhen action\nThen result\n```\n\n"
                "```mermaid\nstateDiagram\n[*] --> Active\n```\n"
            )
        (uc_dir / name).write_text(content)

    def test_valid_use_case_no_errors(self, tmp_path):
        uc_dir = tmp_path / "use_cases"
        uc_dir.mkdir()
        self._make_uc(uc_dir)
        graph = sl.Graph()
        findings = sl.check_use_cases(tmp_path, graph)
        errors = [f for f in findings if f.severity == "error"]
        assert errors == []

    def test_missing_section_errors(self, tmp_path):
        uc_dir = tmp_path / "use_cases"
        uc_dir.mkdir()
        (uc_dir / "UC-01-test.md").write_text(
            "# UC-01\n\n```gherkin\nScenario: X\nWhen Y\nThen Z\n```\n"
            "```mermaid\nfoo\n```\n"
        )
        graph = sl.Graph()
        findings = sl.check_use_cases(tmp_path, graph)
        struct001 = [f for f in findings if f.code == "STRUCT001"]
        assert len(struct001) > 0

    def test_missing_gherkin_errors(self, tmp_path):
        uc_dir = tmp_path / "use_cases"
        uc_dir.mkdir()
        (uc_dir / "UC-01-test.md").write_text(
            "# UC-01\n## Primary Actor\nU\n## Stakeholders & Interests\nS\n"
            "## Trigger\nT\n## Preconditions\nP\n## Main Success Scenario\n1. Step\n"
            "## Extensions\nE\n## Postconditions\nR\n## Business Rules\nB\n"
            "```mermaid\nfoo\n```\n"
        )
        graph = sl.Graph()
        findings = sl.check_use_cases(tmp_path, graph)
        assert any(f.code == "STRUCT002" for f in findings)
        assert not any(f.code == "STRUCT001" for f in findings)

    def test_placeholder_text_warns(self, tmp_path):
        uc_dir = tmp_path / "use_cases"
        uc_dir.mkdir()
        self._make_uc(
            uc_dir,
            content=(
                "# UC-01\n## Primary Actor\nTODO decide\n"
                "## Stakeholders & Interests\nS\n"
                "## Trigger\nT\n## Preconditions\nP\n## Main Success Scenario\nM\n"
                "## Extensions\nE\n## Postconditions\nR\n## Business Rules\nB\n"
                "```gherkin\nScenario: X\nWhen Y\nThen Z\n```\n"
                "```mermaid\nfoo\n```\n"
            ),
        )
        graph = sl.Graph()
        findings = sl.check_use_cases(tmp_path, graph)
        assert any(f.code == "FMT003" for f in findings)

    def test_no_uc_dir_returns_empty(self, tmp_path):
        graph = sl.Graph()
        assert sl.check_use_cases(tmp_path, graph) == []


class TestCollectGraph:
    def test_collects_use_case_ids(self, tmp_path):
        uc_dir = tmp_path / "use_cases"
        uc_dir.mkdir()
        (uc_dir / "UC-01-test.md").write_text("# UC-01 Test")
        (uc_dir / "UC-02-other.md").write_text("# UC-02 Other")
        graph = sl.Graph()
        sl.collect_graph(tmp_path, graph)
        assert "UC-01" in graph.use_cases
        assert "UC-02" in graph.use_cases

    def test_collects_business_rule_definitions(self, tmp_path):
        uc_dir = tmp_path / "use_cases"
        uc_dir.mkdir()
        (uc_dir / "UC-01-test.md").write_text(
            "# UC-01\n\n- **BR-001**: Must validate\n"
        )
        graph = sl.Graph()
        sl.collect_graph(tmp_path, graph)
        assert "BR-001" in graph.business_rules_defined

    def test_collects_actor_goals(self, tmp_path):
        (tmp_path / "actor-goal-list.md").write_text(
            "| AG-01 | User Goal | Create project |\n"
        )
        graph = sl.Graph()
        sl.collect_graph(tmp_path, graph)
        assert "AG-01" in graph.actor_goals

    def test_collects_entities_from_erd(self, tmp_path):
        supp = tmp_path / "supplementary_specs"
        supp.mkdir()
        (supp / "entity-model.md").write_text(
            "```mermaid\nerDiagram\nUSER {\n  string name\n}\nPROJECT {\n  string title\n}\nUSER ||--o{ PROJECT : owns\n```\n"
        )
        graph = sl.Graph()
        sl.collect_graph(tmp_path, graph)
        assert "USER" in graph.entities
        assert "PROJECT" in graph.entities


class TestCheckTraceability:
    def test_referenced_but_undefined_br_errors(self, tmp_path):
        uc_dir = tmp_path / "use_cases"
        uc_dir.mkdir()
        (uc_dir / "UC-01-test.md").write_text("References BR-099 somewhere\n")
        graph = sl.Graph()
        graph.business_rules_referenced.add("BR-099")
        findings = sl.check_traceability(tmp_path, graph)
        assert any(f.code == "TRACE002" for f in findings)

    def test_defined_but_unused_br_is_info(self, tmp_path):
        uc_dir = tmp_path / "use_cases"
        uc_dir.mkdir()
        graph = sl.Graph()
        graph.business_rules_defined.add("BR-001")
        findings = sl.check_traceability(tmp_path, graph)
        trace003 = [f for f in findings if f.code == "TRACE003"]
        assert len(trace003) == 1
        assert trace003[0].severity == "info"


class TestCheckStateMachines:
    def test_unreachable_state_warns(self, tmp_path):
        supp = tmp_path / "supplementary_specs"
        supp.mkdir()
        (supp / "state-machines.md").write_text(
            "```mermaid\nstateDiagram\n[*] --> A\nA --> B\nC --> B\n```\n"
        )
        findings = sl.check_state_machines(tmp_path)
        assert any(f.code == "SM001" and "C" in f.message for f in findings)

    def test_dead_end_state_warns(self, tmp_path):
        supp = tmp_path / "supplementary_specs"
        supp.mkdir()
        (supp / "state-machines.md").write_text(
            "```mermaid\nstateDiagram\n[*] --> A\nA --> B\n```\n"
        )
        findings = sl.check_state_machines(tmp_path)
        assert any(f.code == "SM002" and "B" in f.message for f in findings)

    def test_valid_machine_no_warnings(self, tmp_path):
        supp = tmp_path / "supplementary_specs"
        supp.mkdir()
        (supp / "state-machines.md").write_text(
            "```mermaid\nstateDiagram\n[*] --> A\nA --> B\nB --> [*]\n```\n"
        )
        findings = sl.check_state_machines(tmp_path)
        assert findings == []


class TestCheckTodos:
    def test_open_todos_found(self, tmp_path):
        (tmp_path / "todos.md").write_text(
            "- [ ] Fix thing\n- [x] Done thing\n- [ ] Another\n"
        )
        findings = sl.check_todos(tmp_path, gate=True)
        assert len(findings) == 1
        assert findings[0].severity == "error"
        assert "2" in findings[0].message

    def test_no_todos_file_returns_empty(self, tmp_path):
        assert sl.check_todos(tmp_path, gate=False) == []

    def test_report_only_mode_is_info(self, tmp_path):
        (tmp_path / "todos.md").write_text("- [ ] Fix thing\n")
        findings = sl.check_todos(tmp_path, gate=False)
        assert findings[0].severity == "info"


class TestRun:
    def test_run_on_empty_spec_dir(self, tmp_path):
        findings, _graph = sl.run(tmp_path, tmp_path / "CONTEXT.md", False)
        struct005 = [f for f in findings if f.code == "STRUCT005"]
        assert len(struct005) == len(sl.REQUIRED_ARTIFACTS)


class TestMainRoundTrip:
    """Integration: main() wires parsing → checking → exit code."""

    def _make_complete_spec(self, spec: Path):
        """Build a minimal valid spec directory."""
        spec.mkdir(parents=True, exist_ok=True)
        (spec / "prd.md").write_text("# PRD\nProduct requirements.")
        (spec / "scope-map.md").write_text("# Scope Map\n")
        supp = spec / "supplementary_specs"
        supp.mkdir()
        (supp / "entity-model.md").write_text("# Entity Model\n")
        (supp / "validation-rules.md").write_text("# Validation Rules\n")

    def test_valid_spec_exits_zero(self, tmp_path):
        spec = tmp_path / "docs" / "spec"
        self._make_complete_spec(spec)
        rc = sl.main(["--spec-dir", str(spec), "--context", str(tmp_path / "C.md")])
        assert rc == 0

    def test_missing_artifacts_exits_nonzero(self, tmp_path):
        spec = tmp_path / "docs" / "spec"
        spec.mkdir(parents=True)
        rc = sl.main(["--spec-dir", str(spec), "--context", str(tmp_path / "C.md")])
        assert rc > 0

    def test_report_only_always_exits_zero(self, tmp_path):
        spec = tmp_path / "docs" / "spec"
        spec.mkdir(parents=True)
        rc = sl.main(
            [
                "--spec-dir",
                str(spec),
                "--context",
                str(tmp_path / "C.md"),
                "--report-only",
            ]
        )
        assert rc == 0

    def test_scope_map_required(self, tmp_path):
        spec = tmp_path / "docs" / "spec"
        spec.mkdir(parents=True)
        (spec / "prd.md").write_text("# PRD\n")
        supp = spec / "supplementary_specs"
        supp.mkdir()
        (supp / "entity-model.md").write_text("# Entity Model\n")
        (supp / "validation-rules.md").write_text("# Validation Rules\n")
        rc = sl.main(["--spec-dir", str(spec), "--context", str(tmp_path / "C.md")])
        assert rc > 0
