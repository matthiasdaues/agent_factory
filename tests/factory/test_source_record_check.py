"""Checks of source-record-check.

source-record-check validates the json block of every source record file in a
folder tree against research-source-record.schema.json. The tests run the
script as a subprocess on a temporary folder, because the exit code and the
printed lines are its contract.
"""

from __future__ import annotations

import json
import subprocess
import sys

from conftest import SOURCE_SCRIPTS_DIR

SCRIPT = SOURCE_SCRIPTS_DIR / "source-record-check"

FIELDS = {
    "source_identity": "x",
    "author_or_issuing_body": "x",
    "publisher": "x",
    "publication_date": "2021-07-02T00:00:00Z",
    "relevant_event_date": "2021-07-02",
    "source_family": "Primary",
    "precise_evidence_location": "x",
    "method": "x",
    "limitations": "x",
    "provenance": "x",
}


def _record(fields) -> str:
    return f"# Record\n\n```json\n{json.dumps(fields, indent=2)}\n```\n\n## Evidence\n"


def _run(folder) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(folder)], capture_output=True, text=True
    )


def test_valid_records_pass_and_an_index_is_skipped(tmp_path):
    (tmp_path / "area-1").mkdir()
    (tmp_path / "area-1" / "A1-SR-01-spec.md").write_text(_record(FIELDS))
    (tmp_path / "SR-0002.md").write_text(_record(FIELDS))
    (tmp_path / "area-1-index.md").write_text("# Index\n")
    result = _run(tmp_path)
    assert result.returncode == 0, result.stdout
    assert "2 records checked, 0 failure(s), 1 other file(s) skipped" in result.stdout
    assert "SKIP" in result.stdout and "area-1-index.md" in result.stdout


def test_missing_field_fails(tmp_path):
    fields = dict(FIELDS)
    del fields["provenance"]
    (tmp_path / "A1-SR-01-spec.md").write_text(_record(fields))
    result = _run(tmp_path)
    assert result.returncode == 1
    assert "provenance" in result.stdout


def test_record_without_json_block_fails(tmp_path):
    (tmp_path / "A1-SR-01-spec.md").write_text("# Record\n\nNo block.\n")
    result = _run(tmp_path)
    assert result.returncode == 1
    assert "no json block" in result.stdout


def test_duplicate_record_id_fails(tmp_path):
    (tmp_path / "A1-SR-01-spec.md").write_text(_record(FIELDS))
    (tmp_path / "A1-SR-01-other.md").write_text(_record(FIELDS))
    result = _run(tmp_path)
    assert result.returncode == 1
    assert "already used" in result.stdout


def test_folder_without_records_is_an_operational_error(tmp_path):
    (tmp_path / "index.md").write_text("# Index\n")
    assert _run(tmp_path).returncode == 2
