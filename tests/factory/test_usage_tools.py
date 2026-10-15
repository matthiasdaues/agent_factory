"""Regression tests for the Pi bootstrap and the usage tools (ST-0302)."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import SOURCE_SCRIPTS_DIR

NODE = shutil.which("node")


def _pi_registration(tmp_path: Path, *, staged_source: str | None = None) -> dict[str, Path]:
    """Lay out one Pi registration as pi-usage.ts leaves it for the bootstrap."""
    root = (tmp_path / "project").resolve()
    control = root / ".agent-factory" / "usage" / "control"
    pending = control / "pending"
    scratch = root / ".agent-factory" / "usage" / ".capture"
    pending.mkdir(parents=True)
    scratch.mkdir(parents=True)
    (control / "state.json").write_text(
        json.dumps({"generation": "g1", "mode": "active"}), encoding="utf-8"
    )
    source = scratch / "session-1.jsonl"
    source.write_text("{}\n", encoding="utf-8")
    marker = pending / "session-1.pending.json"
    marker.write_text(
        json.dumps({"generation": "g1", "staged_source": staged_source or str(source)}),
        encoding="utf-8",
    )
    return {
        "root": root,
        "control": control,
        "marker": marker,
        "source": source,
        "status": control / "session-1.completion.json",
        "handshake": control / "session-1.accepted.json",
    }


def _run_bootstrap(paths: dict[str, Path], *extra: str, launcher: str) -> None:
    subprocess.run(
        [
            NODE,
            str(SOURCE_SCRIPTS_DIR / "pi-capture-bootstrap.mjs"),
            "--root", str(paths["root"]),
            "--marker", str(paths["marker"]),
            "--source", str(paths["source"]),
            "--status", str(paths["status"]),
            "--handshake", str(paths["handshake"]),
            "--generation", "g1",
            *extra,
            "--supervisor-command", launcher,
        ],
        check=True,
        timeout=30,
    )


@pytest.mark.skipif(NODE is None, reason="node is not installed")
@pytest.mark.parametrize(
    ("extra", "launcher_kind"),
    [
        pytest.param((), "wrong", id="wrong-launcher"),
        pytest.param(("--accept-timeout-ms", "0"), "right", id="invalid-timeout"),
    ],
)
def test_pi_bootstrap_cleans_up_a_validated_marker_it_rejects(
    tmp_path: Path, extra: tuple[str, ...], launcher_kind: str
) -> None:
    """BUG-0068: a rejected launch removes the marker and transcript copy."""
    paths = _pi_registration(tmp_path)
    right = paths["root"] / ".agent-factory" / "factory" / "scripts" / "usage-capture-runtime"
    launcher = str(right) if launcher_kind == "right" else "/elsewhere/usage-capture-runtime"

    _run_bootstrap(paths, *extra, launcher=launcher)

    assert not paths["marker"].exists()
    assert not paths["source"].exists()
    diagnostics = list((paths["control"] / "diagnostics").glob("bootstrap-*.json"))
    assert len(diagnostics) == 1


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_pi_bootstrap_keeps_files_whose_registration_does_not_match(tmp_path: Path) -> None:
    """BUG-0068: an untrusted registration is never cleanup authority."""
    paths = _pi_registration(tmp_path, staged_source="/elsewhere/session-1.jsonl")

    _run_bootstrap(paths, launcher="/elsewhere/usage-capture-runtime")

    assert paths["marker"].exists()
    assert paths["source"].exists()

