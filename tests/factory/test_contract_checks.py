"""Contract tests for module-graph-check and schema-validate.

Both scripts are gates. A gate that cannot read its input must say so with
exit 2 and must not report a clean result (BUG-0055, BUG-0056).
"""

from __future__ import annotations

from pathlib import Path

from conftest import load_script

mgc = load_script("module-graph-check")

DSL_WITH_COMPONENT = """\
workspace "test" {
    model {
        system = softwareSystem "System" {
            core = container "Core" {
                gate = component "gate-script"
            }
        }
    }
}
"""

CONTRACTS_WITH_HEADING = """\
# Interface contracts

## `scripts/gate-script`

| Field | Value |
| ----- | ----- |
| Reads | nothing |
"""

CONTRACTS_WITHOUT_HEADING = "this file holds no contract headings\n"


def _run_module_graph_check(tmp_path: Path, dsl: str, contracts: str) -> int:
    dsl_path = tmp_path / "architecture.dsl"
    contracts_path = tmp_path / "interface-contracts.md"
    entity_path = tmp_path / "entity-model.md"
    dsl_path.write_text(dsl, encoding="utf-8")
    contracts_path.write_text(contracts, encoding="utf-8")
    entity_path.write_text("", encoding="utf-8")
    return mgc.main(
        [
            "--dsl-path",
            str(dsl_path),
            "--interface-contracts",
            str(contracts_path),
            "--entity-model",
            str(entity_path),
            "--story-id",
            "ST-TEST",
            "--report-dir",
            str(tmp_path / "reports"),
        ]
    )


class TestModuleGraphCheckUnreadableInput:
    """BUG-0055: input the script cannot parse must not read as no change."""

    def test_empty_dsl_and_unreadable_contracts_exit_2(self, tmp_path, capsys):
        code = _run_module_graph_check(tmp_path, "", CONTRACTS_WITHOUT_HEADING)

        assert code == 2
        assert "architecture_change=" not in capsys.readouterr().out
        assert not (tmp_path / "reports").exists()

    def test_dsl_without_components_exits_2(self, tmp_path):
        code = _run_module_graph_check(tmp_path, "", CONTRACTS_WITH_HEADING)

        assert code == 2

    def test_contracts_without_headings_exit_2(self, tmp_path):
        code = _run_module_graph_check(
            tmp_path, DSL_WITH_COMPONENT, CONTRACTS_WITHOUT_HEADING
        )

        assert code == 2

    def test_readable_input_still_reports_no_change(self, tmp_path, capsys):
        code = _run_module_graph_check(
            tmp_path, DSL_WITH_COMPONENT, CONTRACTS_WITH_HEADING
        )

        assert code == 0
        assert "architecture_change=false" in capsys.readouterr().out
