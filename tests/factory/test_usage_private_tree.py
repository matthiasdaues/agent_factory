"""The usage tree repair keeps the execute bits of installed programs (BUG-0140).

`initialize_usage_lifecycle` makes every file under `.agent-factory/usage/`
private. The usage analysis environment lives inside that tree, so the
repair must keep its programs runnable.
"""

from __future__ import annotations

import stat
from pathlib import Path

import pytest

from conftest import load_script


def _mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


@pytest.fixture(scope="module")
def init_factory():
    return load_script("init-factory")


def test_repair_keeps_execute_bit_and_makes_files_private(tmp_path, init_factory):
    usage = tmp_path / "usage"
    program = usage / "analysis" / ".venv" / "bin" / "usage-query"
    data = usage / "analysis" / ".venv" / "bin" / "activate"
    program.parent.mkdir(parents=True)
    program.write_text("#!/bin/sh\necho ok\n", encoding="utf-8")
    data.write_text("# activate\n", encoding="utf-8")
    program.chmod(0o755)
    data.chmod(0o644)

    init_factory._repair_private_tree(usage)

    assert _mode(program) == 0o700
    assert _mode(data) == 0o600


def test_second_lifecycle_initialization_keeps_programs_runnable(
    tmp_path, init_factory
):
    program = (
        tmp_path / ".agent-factory" / "usage" / "analysis" / ".venv" / "bin" / "usage-query"
    )
    program.parent.mkdir(parents=True)
    program.write_text("#!/bin/sh\necho ok\n", encoding="utf-8")
    program.chmod(0o755)

    init_factory.initialize_usage_lifecycle(tmp_path, [])
    init_factory.initialize_usage_lifecycle(tmp_path, [])

    assert _mode(program) == 0o700
