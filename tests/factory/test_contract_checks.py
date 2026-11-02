"""Contract tests for module-graph-check and schema-validate.

Both scripts are gates. A gate that cannot read its input must say so with
exit 2 and must not report a clean result (BUG-0055, BUG-0056).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import SOURCE_SCRIPTS_DIR, load_script

mgc = load_script("module-graph-check")
sv = load_script("schema-validate")

USAGE_RECORD_SCHEMA = (
    SOURCE_SCRIPTS_DIR.parent / "contracts" / "usage-record" / "v1.schema.json"
)

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

CONTRACTS_WITH_DRIFTED_HEADINGS = """\
# Interface contracts

## UserRepository

| Field | Value |
| ----- | ----- |
| Reads | users |
"""

READS_TABLE = "| Field | Value |\n| ----- | ----- |\n| Reads | users |\n"

CONTRACTS_DECLARING_NONE = """\
# Interface contracts

This feature adds no interfaces.
"""


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
        code = _run_module_graph_check(
            tmp_path, "", CONTRACTS_WITH_DRIFTED_HEADINGS
        )

        assert code == 2
        assert "architecture_change=" not in capsys.readouterr().out
        assert not (tmp_path / "reports").exists()

    def test_dsl_without_components_exits_2(self, tmp_path):
        code = _run_module_graph_check(tmp_path, "", CONTRACTS_WITH_HEADING)

        assert code == 2

    def test_contracts_with_drifted_headings_exit_2(self, tmp_path):
        code = _run_module_graph_check(
            tmp_path, DSL_WITH_COMPONENT, CONTRACTS_WITH_DRIFTED_HEADINGS
        )

        assert code == 2
        assert not (tmp_path / "reports").exists()

    def test_contracts_declaring_none_warn_and_report_no_change(
        self, tmp_path, capsys
    ):
        code = _run_module_graph_check(
            tmp_path, DSL_WITH_COMPONENT, CONTRACTS_DECLARING_NONE
        )

        captured = capsys.readouterr()
        assert code == 0
        assert "architecture_change=false" in captured.out
        assert "warning" in captured.err
        assert (tmp_path / "reports" / "ST-TEST.json").is_file()

    @pytest.mark.parametrize(
        "heading",
        [
            pytest.param("### `scripts/new-tool`", id="level-three"),
            pytest.param("##`scripts/new-tool`", id="no-space"),
            pytest.param("   ## `scripts/new-tool`", id="indented"),
            pytest.param("# `scripts/new-tool`", id="level-one"),
            pytest.param("﻿## `scripts/new-tool`", id="byte-order-mark"),
        ],
    )
    def test_contract_shaped_heading_out_of_form_exits_2(
        self, tmp_path, capsys, heading
    ):
        contracts = (
            f"{heading}\n\n| Field | Value |\n| ----- | ----- |\n| Reads | users |\n"
        )

        code = _run_module_graph_check(tmp_path, DSL_WITH_COMPONENT, contracts)

        assert code == 2
        assert "architecture_change=" not in capsys.readouterr().out
        assert not (tmp_path / "reports").exists()

    def test_fenced_contract_shaped_heading_still_declares_none(
        self, tmp_path, capsys
    ):
        contracts = "# Interface contracts\n\n```md\n### `scripts/new-tool`\n```\n"

        code = _run_module_graph_check(tmp_path, DSL_WITH_COMPONENT, contracts)

        assert code == 0
        assert "warning" in capsys.readouterr().err

    @pytest.mark.parametrize(
        "contracts",
        [
            pytest.param(
                "# C\n\n### Script `scripts/new-tool`\n\n" + READS_TABLE,
                id="backtick-not-first",
            ),
            pytest.param(
                "# C\n\n`scripts/new-tool`\n---\n\n" + READS_TABLE,
                id="setext-heading",
            ),
            pytest.param(
                "# C\n\n### scripts/new-tool\n\n" + READS_TABLE,
                id="no-backticks",
            ),
            pytest.param(
                "# C\n\n```\nstray\n\n### `scripts/new-tool`\n\n" + READS_TABLE,
                id="unclosed-fence",
            ),
            pytest.param(
                "# C\n\n### scripts/new-tool\n\n| Writes | users |\n",
                id="writes-row",
            ),
        ],
    )
    def test_reads_or_writes_row_without_parsed_contract_exits_2(
        self, tmp_path, capsys, contracts
    ):
        code = _run_module_graph_check(tmp_path, DSL_WITH_COMPONENT, contracts)

        assert code == 2
        assert "architecture_change=" not in capsys.readouterr().out
        assert not (tmp_path / "reports").exists()

    def test_contract_shaped_heading_without_rows_exits_2(self, tmp_path):
        contracts = "# C\n\n### `scripts/new-tool`\n\nA tool with no reads.\n"

        code = _run_module_graph_check(tmp_path, DSL_WITH_COMPONENT, contracts)

        assert code == 2

    def test_fenced_reads_row_still_declares_none(self, tmp_path, capsys):
        contracts = "# C\n\nUse this form:\n\n```md\n### `x`\n" + READS_TABLE + "```\n"

        code = _run_module_graph_check(tmp_path, DSL_WITH_COMPONENT, contracts)

        assert code == 0
        assert "warning" in capsys.readouterr().err

    def test_plain_table_without_reads_or_writes_declares_none(
        self, tmp_path, capsys
    ):
        contracts = (
            "# Interface contracts\n\n## Notes\n\nThis feature adds no interfaces.\n\n"
            "| Field | Value |\n| ----- | ----- |\n| Owner | team-a |\n"
        )

        code = _run_module_graph_check(tmp_path, DSL_WITH_COMPONENT, contracts)

        captured = capsys.readouterr()
        assert code == 0
        assert "architecture_change=false" in captured.out
        assert "warning" in captured.err

    def test_readable_input_still_reports_no_change(self, tmp_path, capsys):
        code = _run_module_graph_check(
            tmp_path, DSL_WITH_COMPONENT, CONTRACTS_WITH_HEADING
        )

        assert code == 0
        assert "architecture_change=false" in capsys.readouterr().out


GRAPH_PROJECT_DSL = """\
workspace "graph-project" {
    model {
        system = softwareSystem "System" {
            api = container "api" {
                apiServer = component "api-server"
            }
            db = container "db" {
                dbStore = component "db-store"
            }
        }
        apiServer -> dbStore "reads"
    }
}
"""

GRAPH_PROJECT_CONTRACTS = """\
# Interface contracts

## `src/api/api-server`

| Field | Value |
| ----- | ----- |
| Reads | `db-store` |

## `src/db/db-store`

| Field | Value |
| ----- | ----- |
| Reads | nothing |
"""

GRAPH_PROJECT_ENTITY_MODEL = """\
# Entity model

```mermaid
erDiagram
    ORDER {
        int id
    }
```
"""

UNNAMED_MODULE_CONTRACT = """
## `src/billing/billing-service`

| Field | Value |
| ----- | ----- |
| Reads | nothing |
"""


def _graph_project(root: Path, contracts: str = GRAPH_PROJECT_CONTRACTS) -> Path:
    """Build the migrated fixture `graph-project`: the core sits in docs/spec/."""
    spec = root / "docs" / "spec"
    spec.mkdir(parents=True)
    (spec / "architecture.dsl").write_text(GRAPH_PROJECT_DSL, encoding="utf-8")
    (spec / "interface-contracts.md").write_text(contracts, encoding="utf-8")
    (spec / "entity-model.md").write_text(
        GRAPH_PROJECT_ENTITY_MODEL, encoding="utf-8"
    )
    for module in ("api", "db"):
        (root / "src" / module).mkdir(parents=True)
    return root


class TestModuleGraphCheckDefaultPaths:
    """ST-0341: with no path arguments the check reads the core in docs/spec/."""

    def test_consistent_migrated_project_exits_0(
        self, tmp_path, monkeypatch, capsys
    ):
        monkeypatch.chdir(_graph_project(tmp_path))

        code = mgc.main(["--story-id", "ST-TEST"])

        assert code == 0
        assert "architecture_change=false" in capsys.readouterr().out
        assert (tmp_path / ".current-work/module-graph-check/ST-TEST.json").is_file()

    def test_module_the_dsl_does_not_name_is_reported(
        self, tmp_path, monkeypatch, capsys
    ):
        contracts = GRAPH_PROJECT_CONTRACTS + UNNAMED_MODULE_CONTRACT
        monkeypatch.chdir(_graph_project(tmp_path, contracts))

        code = mgc.main(["--story-id", "ST-TEST"])

        out = capsys.readouterr().out
        assert code == 0
        assert "architecture_change=true" in out
        assert "new_modules=billing-service" in out


class TestSchemaValidateTypeKeywords:
    """BUG-0056: union types, null, and minimum."""

    UNION = {"type": ["string", "null"]}

    @pytest.mark.parametrize("value", ["text", None])
    def test_union_type_accepts_each_member(self, value):
        assert sv.validate(value, self.UNION) == []

    def test_union_type_rejects_other_types(self):
        errors = sv.validate(3, self.UNION)

        assert len(errors) == 1
        assert "string" in errors[0] and "null" in errors[0]

    def test_null_type_rejects_string(self):
        assert sv.validate("text", {"type": "null"}) != []

    def test_null_type_accepts_null(self):
        assert sv.validate(None, {"type": "null"}) == []

    def test_minimum_rejects_smaller_number(self):
        errors = sv.validate(-1, {"type": "integer", "minimum": 0})

        assert len(errors) == 1
        assert "minimum" in errors[0]

    def test_minimum_accepts_boundary(self):
        assert sv.validate(0, {"type": "integer", "minimum": 0}) == []

    def test_minimum_skips_null_in_union(self):
        assert sv.validate(None, {"type": ["integer", "null"], "minimum": 0}) == []


def _usage_record(**overrides):
    record = {
        "record_id": "r-1",
        "project_id": "p-1",
        "project_name": "demo",
        "normalized_input": 10,
        "normalized_output": 5,
        "normalized_total": 15,
        "cli": "claude",
        "session_id": None,
        "parent_session_id": None,
        "depth": 0,
        "recorded_at": "2026-10-15T00:00:00Z",
        "agent": None,
        "model": "m",
        "provider": None,
        "reported_input": None,
        "reported_output": 3,
        "reported_cache_read": None,
        "reported_cache_write": None,
        "usage_granularity": None,
        "usage_capability": None,
        "cache_miss_turns": None,
        "cache_miss_input_tokens": None,
        "late_early_input_ratio": 0.5,
        "exit_status": None,
        "branch": None,
        "commit_id": None,
        "transcript_ref": None,
    }
    record.update(overrides)
    return record


class TestSchemaValidateUsageRecord:
    """The shipped usage-record schema uses union types and minimum."""

    def _main(self, tmp_path, record):
        artifact = tmp_path / "record.json"
        artifact.write_text(json.dumps(record), encoding="utf-8")
        return sv.main([str(artifact), str(USAGE_RECORD_SCHEMA)])

    def test_conforming_record_exits_0(self, tmp_path):
        assert self._main(tmp_path, _usage_record()) == 0

    def test_negative_count_exits_1(self, tmp_path, capsys):
        code = self._main(tmp_path, _usage_record(depth=-1))

        assert code == 1
        assert "$.depth" in capsys.readouterr().out
