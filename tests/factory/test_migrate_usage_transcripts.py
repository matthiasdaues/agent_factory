"""migrate-usage-transcripts turns per-capture copies into chain files (BUG-0142).

Each test builds the layout that usage-capture wrote before BUG-0139: one
record file and one transcript folder per capture, each holding the full
cumulative copy.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import load_script

migrate = load_script("migrate-usage-transcripts")

SESSION = "fe14aa7b"


def _old_capture(project: Path, stamp: str, text: bytes, structured: bytes, **fields):
    """Write one capture the way usage-capture 1.13.0 stored it."""
    usage = project / ".agent-factory" / "usage"
    key = f"{stamp}_claude-code_{SESSION}"
    folder = usage / "transcripts" / key
    folder.mkdir(parents=True)
    record_id = f"{SESSION}-0001"
    plain = folder / f"{record_id}.jsonl"
    plain.write_bytes(text)
    (folder / f"{record_id}.structured.jsonl").write_bytes(structured)
    record = {
        "record_id": record_id,
        "cli": "claude-code",
        "session_id": SESSION,
        "agent": None,
        "recorded_at": stamp,
        "normalized_total": len(text),
        "transcript_ref": {"path": str(plain.resolve()), "span": None},
    }
    record.update(fields)
    (usage / f"{key}.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")


@pytest.fixture
def project(tmp_path):
    project = tmp_path / "project"
    _old_capture(project, "2026-10-16T12-00-01", b"a\n", b"{1}\n")
    _old_capture(project, "2026-10-16T12-00-02", b"a\nb\n", b"{1}\n{2}\n")
    _old_capture(
        project, "2026-10-16T12-00-03", b"child\n", b"{c}\n", agent="Explore"
    )
    _old_capture(project, "2026-10-16T12-00-04", b"a\nb\nc\n", b"{1}\n{2}\n{3}\n")
    _old_capture(project, "2026-10-16T12-00-05", b"", b"")
    return project


def _usage(project: Path) -> Path:
    return project / ".agent-factory" / "usage"


def _slice(path: str, span: dict) -> bytes:
    return Path(path).read_bytes()[span["start"] : span["end"]]


def test_dry_run_changes_nothing(project, capsys):
    before = sorted(p.relative_to(project) for p in project.rglob("*"))

    assert migrate.main([str(project)]) == 0

    assert sorted(p.relative_to(project) for p in project.rglob("*")) == before
    out = capsys.readouterr().out
    assert "Sessions can be migrated: 1" in out
    assert "Records: 5" in out
    assert "Chains: 2, chain files: 4" in out
    assert "Captures without text: 1" in out


def test_apply_writes_one_record_file_and_chain_files(project):
    assert migrate.main([str(project), "--apply"]) == 0

    usage = _usage(project)
    record_files = sorted(p.name for p in usage.glob("*.jsonl"))
    assert record_files == [f"2026-10-16T12-00-01_claude-code_{SESSION}.jsonl"]
    records = [
        json.loads(line)
        for line in (usage / record_files[0]).read_text().splitlines()
    ]
    assert [r["record_id"] for r in records] == [
        f"{SESSION}-000{n}" for n in range(1, 6)
    ]
    assert [r["chain"] for r in records] == [
        SESSION, SESSION, "Explore-1", SESSION, "empty-capture-1"
    ]
    main = [r["transcript_ref"] for r in records if r["chain"] == SESSION]
    assert [ref["byte_range"] for ref in main] == [
        {"start": 0, "end": 2},
        {"start": 2, "end": 4},
        {"start": 4, "end": 6},
    ]
    assert [_slice(ref["path"], ref["byte_range"]) for ref in main] == [
        b"a\n", b"b\n", b"c\n"
    ]
    assert _slice(main[2]["structured_path"], main[2]["structured_byte_range"]) == b"{3}\n"
    assert records[4]["transcript_ref"]["byte_range"] is None

    folders = sorted(p.name for p in (usage / "transcripts").iterdir())
    assert folders == [f"2026-10-16T12-00-01_claude-code_{SESSION}"]
    files = sorted(p.name for p in (usage / "transcripts" / folders[0]).iterdir())
    assert files == [
        ".lock",
        "Explore-1.jsonl",
        "Explore-1.structured.jsonl",
        f"{SESSION}.jsonl",
        f"{SESSION}.structured.jsonl",
    ]


def test_second_run_leaves_migrated_sessions_alone(project, capsys):
    migrate.main([str(project), "--apply"])
    capsys.readouterr()

    assert migrate.main([str(project)]) == 0
    assert "a record already names its chain: 1" in capsys.readouterr().out


def test_child_record_with_the_main_transcript_joins_the_main_chain(tmp_path, capsys):
    """Copilot hands its child hook the main transcript."""
    project = tmp_path / "project"
    _old_capture(project, "2026-10-16T12-00-01", b"a\n", b"{1}\n")
    _old_capture(
        project, "2026-10-16T12-00-02", b"a\nb\n", b"{1}\n{2}\n", agent="Explore"
    )

    assert migrate.main([str(project), "--apply"]) == 0

    out = capsys.readouterr().out
    assert "Sessions with a chain whose records name different agents: 1" in out
    (record_file,) = _usage(project).glob("*.jsonl")
    records = [json.loads(line) for line in record_file.read_text().splitlines()]
    assert [r["chain"] for r in records] == [SESSION, SESSION]
    assert records[1]["transcript_ref"]["byte_range"] == {"start": 2, "end": 4}


def test_rewritten_main_transcript_becomes_a_new_generation(tmp_path):
    project = tmp_path / "project"
    _old_capture(project, "2026-10-16T12-00-01", b"a\n", b"{1}\n")
    _old_capture(project, "2026-10-16T12-00-02", b"summary\n", b"{s}\n")
    _old_capture(project, "2026-10-16T12-00-03", b"summary\nb\n", b"{s}\n{2}\n")

    assert migrate.main([str(project), "--apply"]) == 0

    (record_file,) = _usage(project).glob("*.jsonl")
    records = [json.loads(line) for line in record_file.read_text().splitlines()]
    assert [r["chain"] for r in records] == [SESSION] * 3
    refs = [r["transcript_ref"] for r in records]
    assert Path(refs[0]["path"]).name == f"{SESSION}.jsonl"
    assert Path(refs[1]["path"]).name == f"{SESSION}.2.jsonl"
    assert refs[2]["byte_range"] == {"start": 8, "end": 10}
    assert _slice(refs[2]["path"], refs[2]["byte_range"]) == b"b\n"


def test_apply_refuses_while_captures_are_pending(project):
    pending = _usage(project) / "control" / "pending"
    pending.mkdir(parents=True)
    (pending / "capture-1.pending.json").write_text("{}")

    assert migrate.main([str(project), "--apply"]) == 2
    assert len(list(_usage(project).glob("*.jsonl"))) == 5
