"""Contract tests for spec-lint gate script."""

from __future__ import annotations

from pathlib import Path

import pytest
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
        (tmp_path / "scope-map.md").touch()
        (tmp_path / "entity-model.md").touch()
        findings = sl.check_required_artifacts(tmp_path)
        assert findings == []

    def test_missing_scope_map(self, tmp_path):
        findings = sl.check_required_artifacts(tmp_path)
        assert any(
            f.code == "STRUCT005" and "scope-map.md" in f.artifact for f in findings
        )


class TestCollectGraph:
    def test_collects_business_rule_definitions(self, tmp_path):
        (tmp_path / "validation-rules.md").write_text(
            "# Validation Rules\n\n- **BR-001**: Must validate\n"
        )
        graph = sl.Graph()
        sl.collect_graph(tmp_path, graph)
        assert "BR-001" in graph.business_rules_defined

    def test_feature_file_comment_references_a_rule(self, tmp_path):
        (tmp_path / "features").mkdir()
        (tmp_path / "features" / "payments.feature").write_text(
            "Feature: Payments\n  # BR-001\n  Scenario: Pay\n"
        )
        graph = sl.Graph()
        sl.collect_graph(tmp_path, graph)
        assert "BR-001" in graph.business_rules_referenced
        assert "BR-001" not in graph.business_rules_defined

    def test_collects_entities_from_erd(self, tmp_path):
        (tmp_path / "entity-model.md").write_text(
            "```mermaid\nerDiagram\nUSER {\n  string name\n}\nPROJECT {\n  string title\n}\nUSER ||--o{ PROJECT : owns\n```\n"
        )
        graph = sl.Graph()
        sl.collect_graph(tmp_path, graph)
        assert "USER" in graph.entities
        assert "PROJECT" in graph.entities


class TestCheckTraceability:
    def test_defined_but_unused_br_is_info(self, tmp_path):
        graph = sl.Graph()
        graph.business_rules_defined.add("BR-001")
        findings = sl.check_traceability(tmp_path, graph)
        trace003 = [f for f in findings if f.code == "TRACE003"]
        assert len(trace003) == 1
        assert trace003[0].severity == "info"

    def test_relationship_only_entity_is_info_on_entity_model(self, tmp_path):
        graph = sl.Graph()
        graph.entities.add("LEDGER")
        findings = sl.check_traceability(tmp_path, graph)
        trace004 = [f for f in findings if f.code == "TRACE004"]
        assert [f.artifact for f in trace004] == ["docs/spec/entity-model.md"]


class TestCheckStateMachines:
    def test_unreachable_state_warns(self, tmp_path):
        (tmp_path / "state-machines.md").write_text(
            "```mermaid\nstateDiagram\n[*] --> A\nA --> B\nC --> B\n```\n"
        )
        findings = sl.check_state_machines(tmp_path)
        assert any(f.code == "SM001" and "C" in f.message for f in findings)

    def test_dead_end_state_warns(self, tmp_path):
        (tmp_path / "state-machines.md").write_text(
            "```mermaid\nstateDiagram\n[*] --> A\nA --> B\n```\n"
        )
        findings = sl.check_state_machines(tmp_path)
        assert any(f.code == "SM002" and "B" in f.message for f in findings)

    def test_valid_machine_no_warnings(self, tmp_path):
        (tmp_path / "state-machines.md").write_text(
            "```mermaid\nstateDiagram\n[*] --> A\nA --> B\nB --> [*]\n```\n"
        )
        findings = sl.check_state_machines(tmp_path)
        assert findings == []


class TestCheckTodos:
    def _write_todos(self, spec: Path, text: str) -> None:
        (spec / "work").mkdir(exist_ok=True)
        (spec / "work" / "todos.md").write_text(text)

    def test_open_todos_found(self, tmp_path):
        self._write_todos(
            tmp_path, "- [ ] Fix thing\n- [x] Done thing\n- [ ] Another\n"
        )
        findings = sl.check_todos(tmp_path, gate=True)
        assert len(findings) == 1
        assert findings[0].severity == "error"
        assert findings[0].artifact == "docs/spec/work/todos.md"
        assert "2" in findings[0].message

    def test_no_todos_file_returns_empty(self, tmp_path):
        assert sl.check_todos(tmp_path, gate=False) == []

    def test_report_only_mode_is_info(self, tmp_path):
        self._write_todos(tmp_path, "- [ ] Fix thing\n")
        findings = sl.check_todos(tmp_path, gate=False)
        assert findings[0].severity == "info"


class TestGlossaryTerms:
    def test_reads_the_term_column_and_strips_emphasis(self):
        text = (
            "# Glossary\n\n## Payments\n\n"
            "| Term         | Definition       | Avoid |\n"
            "| ------------ | ---------------- | ----- |\n"
            "| **Agent**    | Does the work.   | Bot   |\n"
            "| _Settlement_ | Moves the money. |       |\n\n"
            "| Code | Meaning     |\n| ---- | ----------- |\n| X1   | Not a term. |\n"
        )
        assert sl.glossary_terms(text) == {"Agent", "Settlement"}


class TestRun:
    def test_run_on_empty_spec_dir(self, tmp_path):
        findings, _graph = sl.run(tmp_path, tmp_path / "glossary.md", False)
        struct005 = [f for f in findings if f.code == "STRUCT005"]
        assert len(struct005) == len(sl.REQUIRED_ARTIFACTS)


class TestMainRoundTrip:
    """Integration: main() wires parsing → checking → exit code."""

    def _make_complete_spec(self, spec: Path):
        """Build a minimal valid spec directory."""
        spec.mkdir(parents=True, exist_ok=True)
        (spec / "scope-map.md").write_text("# Scope Map\n")
        (spec / "entity-model.md").write_text("# Entity Model\n")

    def _main(self, spec: Path, *extra: str) -> int:
        glossary = spec / "glossary.md"
        return sl.main(["--spec-dir", str(spec), "--glossary", str(glossary), *extra])

    def test_valid_spec_exits_zero(self, tmp_path):
        spec = tmp_path / "docs" / "spec"
        self._make_complete_spec(spec)
        assert self._main(spec) == 0

    def test_missing_artifacts_exits_nonzero(self, tmp_path):
        spec = tmp_path / "docs" / "spec"
        spec.mkdir(parents=True)
        assert self._main(spec) > 0

    def test_report_only_always_exits_zero(self, tmp_path):
        spec = tmp_path / "docs" / "spec"
        spec.mkdir(parents=True)
        assert self._main(spec, "--report-only") == 0

    def test_scope_map_required(self, tmp_path):
        spec = tmp_path / "docs" / "spec"
        spec.mkdir(parents=True)
        (spec / "entity-model.md").write_text("# Entity Model\n")
        assert self._main(spec) > 0

    def test_gate_todos_names_the_todo_list_in_work(self, tmp_path, capsys):
        spec = tmp_path / "docs" / "spec"
        self._make_complete_spec(spec)
        (spec / "work").mkdir()
        (spec / "work" / "todo.md").write_text("## T-0001 — Retry\n\n- status: open\n")
        assert self._main(spec, "--gate-todos") == 1
        assert "TODO001  docs/spec/work/todo.md" in capsys.readouterr().out


# --- Contract tests of the core artifact layout (CAL-10) -----------------------

GLOSSARY = """\
# Glossary

## Payments

| Term       | Definition                              | Avoid    |
| ---------- | --------------------------------------- | -------- |
| Settlement | The transfer that closes a payment.     | Clearing |
| Payout     | Money the platform sends to a merchant. | Transfer |
"""

# Codes of the removed checks that read use-case files and the actor-goal list.
REMOVED_CODES = {
    "STRUCT001", "STRUCT002", "STRUCT003", "STRUCT004", "STRUCT006",
    "FMT001", "FMT002", "FMT003", "FMT004", "TRACE001", "TRACE006",
}  # fmt: skip


def _new_layout_spec(root: Path) -> Path:
    """The fixture `new-layout-spec`: a core in the new layout, no use-case files."""
    spec = root / "docs" / "spec"
    files = {
        "scope-map.md": "# Scope Map\n",
        "glossary.md": GLOSSARY,
        "work/payments-gaps.md": "# Gaps\n\nSettlement timing is open.\n",
        "features/payments.feature": (
            "Feature: Payments\n"
            "  # BR-001\n"
            "  Scenario: Merchant receives a payout\n"
            "    When the platform sends the Payout\n"
            "    Then the merchant sees it\n"
        ),
        "validation-rules.md": (
            "# Validation Rules\n\n- **BR-001**: A payout is positive.\n"
        ),
        "entity-model.md": (
            "# Entity Model\n\n```mermaid\nerDiagram\nMERCHANT {\n  string name\n}\n```\n"
        ),
    }
    for relative, content in files.items():
        path = spec / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return spec


def _lint(spec: Path) -> list:
    findings, _graph = sl.run(spec, spec / "glossary.md", False)
    return findings


def _main(spec: Path) -> int:
    return sl.main(["--spec-dir", str(spec), "--glossary", str(spec / "glossary.md")])


def _gloss001_terms(findings: list) -> list[str]:
    return [f.message.split("'")[1] for f in findings if f.code == "GLOSS001"]


@pytest.mark.spec("CAL-10")
def test_CAL_10_CT_01_gloss001_reports_a_term_only_glossary_and_work_use(tmp_path):
    spec = _new_layout_spec(tmp_path)
    findings = _lint(spec)
    gloss = [f for f in findings if f.code == "GLOSS001"]
    assert _gloss001_terms(findings) == ["Settlement"]
    assert gloss[0].severity == "info"
    assert _main(spec) == 0


@pytest.mark.spec("CAL-10")
@pytest.mark.parametrize(
    "use",
    ["entity-model.md", "features/payments.feature"],
    ids=["core-file", "feature-file"],
)
def test_CAL_10_CT_01_gloss001_silent_for_a_term_another_core_file_uses(tmp_path, use):
    spec = _new_layout_spec(tmp_path)
    path = spec / use
    path.write_text(path.read_text() + "\nSettlement closes the payment.\n")
    assert "Settlement" not in _gloss001_terms(_lint(spec))


@pytest.mark.spec("CAL-10")
def test_CAL_10_CT_02_trace002_blocks_without_use_case_files(tmp_path, capsys):
    spec = _new_layout_spec(tmp_path)
    feature = spec / "features" / "payments.feature"
    feature.write_text(feature.read_text() + "  # BR-099\n")
    findings = _lint(spec)
    trace002 = [f for f in findings if f.code == "TRACE002"]
    assert [(f.severity, "BR-099" in f.message) for f in trace002] == [("error", True)]
    assert not REMOVED_CODES & {f.code for f in findings}
    assert _main(spec) == 1
    assert "TRACE002" in capsys.readouterr().out


@pytest.mark.spec("CAL-10")
def test_CAL_10_CT_02_runs_trace002_to_trace004_and_no_use_case_check(tmp_path):
    spec = _new_layout_spec(tmp_path)
    (spec / "validation-rules.md").write_text(
        "# Validation Rules\n\n- **BR-001**: A payout is positive.\n"
        "- **BR-002**: Unused.\n\nSee BR-003.\n"
    )
    (spec / "entity-model.md").write_text(
        "```mermaid\nerDiagram\nMERCHANT ||--o{ PAYOUT : receives\n```\n"
    )
    codes = {f.code for f in _lint(spec)}
    assert {"TRACE002", "TRACE003", "TRACE004"} <= codes
    assert not REMOVED_CODES & codes
