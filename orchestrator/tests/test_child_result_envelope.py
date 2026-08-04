"""End-to-end contract tests for bounded Pi child-result envelopes (ST-0067)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_INIT = _ROOT / "factory/scripts/init-factory"
_FIELDS = {"disposition", "finding_counts", "artifact_paths", "next_action"}
_VERBOSE_DETAIL = "VERBOSE_CHILD_REASONING_MUST_STAY_IN_THE_TRACKED_REPORT"


def _git(repo: Path, *args: str) -> str:
    """Run one deterministic Git operation in a disposable consumer."""
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, text=True, capture_output=True
    ).stdout.strip()


def _consumer(tmp_path: Path) -> tuple[Path, str]:
    """Install Factory into a Git repository with canonical result artifacts."""
    target = tmp_path / "consumer"
    target.mkdir()
    result = subprocess.run(
        [
            str(_INIT),
            "--target",
            str(target),
            "--source",
            str(_ROOT),
            "--project-name",
            "Envelope Test",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr

    typebox = target / "node_modules/typebox"
    typebox.mkdir(parents=True)
    (typebox / "package.json").write_text(
        json.dumps({"name": "typebox", "type": "module", "exports": "./index.js"})
    )
    (typebox / "index.js").write_text(
        "export const Type = new Proxy({}, {get: () => (...args) => ({args})});\n"
    )

    report = target / "docs/reviews/child-result.md"
    finding = target / "docs/findings/ENV-001.md"
    report.parent.mkdir(parents=True)
    finding.parent.mkdir(parents=True)
    report.write_text(f"# Complete child result\n\n{_VERBOSE_DETAIL}\n")
    finding.write_text("# ENV-001\n\nFull per-finding remediation detail.\n")

    _git(target, "init", "-b", "main")
    _git(target, "add", ".")
    _git(
        target,
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=Test",
        "commit",
        "-m",
        "test: seed envelope consumer",
    )
    return target, _git(target, "rev-parse", "HEAD")


def _envelope(*, artifact_paths: list[str] | None = None) -> dict[str, object]:
    """Return one exact four-field child-result envelope."""
    return {
        "disposition": "pass",
        "finding_counts": {"critical": 0, "major": 1, "minor": 0},
        "artifact_paths": artifact_paths
        or ["docs/reviews/child-result.md", "docs/findings/ENV-001.md"],
        "next_action": "Read the complete report, then resolve the major finding.",
    }


def _pi_stub(target: Path, envelope: dict[str, object]) -> dict[str, str]:
    """Install a fake Pi that returns an envelope in its final JSONL event."""
    bin_dir = target / "test-bin"
    bin_dir.mkdir(exist_ok=True)
    pi = bin_dir / "pi"
    event = {
        "type": "message_end",
        "message": {
            "role": "assistant",
            "content": [{"type": "text", "text": json.dumps(envelope)}],
            "usage": {"input": 11, "output": 5},
        },
    }
    pi.write_text(f"#!/bin/sh\nprintf '%s\\n' {json.dumps(json.dumps(event))}\n")
    pi.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    for name in (
        "PI_AGENT_FACTORY_SESSION_ID",
        "PI_AGENT_FACTORY_USAGE_ROOT",
        "PI_RUN_AGENT_DEPTH",
    ):
        env.pop(name, None)
    return env


def _execute(
    target: Path,
    extension: str,
    params: dict[str, object],
    env: dict[str, str],
) -> dict[str, object]:
    """Invoke an installed Pi tool and decode its complete returned value."""
    script = target / f"exercise-{extension}.mjs"
    script.write_text(
        f"""
import extension from {json.dumps((target / ".pi/extensions" / extension).as_uri())};
let tool;
extension({{registerTool(value) {{ tool = value; }}}});
const result = await tool.execute(
  'call-envelope',
  {json.dumps(params)},
  undefined,
  undefined,
  {{cwd:{json.dumps(str(target))},sessionManager:{{getSessionFile() {{ return undefined; }}}}}},
);
process.stdout.write(JSON.stringify(result));
"""
    )
    result = subprocess.run(
        ["node", "--experimental-strip-types", str(script)],
        cwd=target,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _content_envelope(result: dict[str, object]) -> dict[str, object]:
    """Decode the sole parent-visible envelope from a Pi tool result."""
    content = result["content"]
    assert isinstance(content, list) and len(content) == 1
    return json.loads(content[0]["text"])


def test_report_convention_defines_exact_bounded_json_envelope():
    """The canonical convention names the serialization and forbidden detail."""
    text = (_ROOT / "factory/rulebooks/conventions/report-format.md").read_text()
    assert "exactly these four fields" in text
    for field in _FIELDS:
        assert f"`{field}`" in text
    assert "verbatim finding detail" in text
    assert "full reasoning" in text
    assert "JSON" in text


def test_run_agent_returns_only_envelope_and_keeps_runtime_metadata_outside(tmp_path):
    """Verbose detail remains reachable without entering parent-visible content."""
    target, _ = _consumer(tmp_path)
    expected = _envelope()
    result = _execute(
        target,
        "run-agent.ts",
        {"agent": "developer-agent", "task": "review", "model": "test/model"},
        _pi_stub(target, expected),
    )

    actual = _content_envelope(result)
    assert actual == expected
    assert set(actual) == _FIELDS
    assert _VERBOSE_DETAIL not in json.dumps(result["content"])
    persisted = "\n".join(
        (target / path).read_text() for path in actual["artifact_paths"]
    )
    assert _VERBOSE_DETAIL in persisted
    assert result["details"]["usage"] == {"input": 11, "output": 5}
    assert result["details"]["exitCode"] == 0
    assert "usage" not in actual and "exitCode" not in actual


@pytest.mark.parametrize(
    ("paths", "reason"),
    [
        (["docs/reviews/missing.md"], "does not exist"),
        (["untracked-result.md"], "not tracked by Git"),
        (["../outside.md"], "canonical repository-relative"),
    ],
)
def test_run_agent_rejects_exit_zero_without_canonical_tracked_artifacts(
    tmp_path, paths, reason
):
    """Exit zero cannot bypass the durable result-artifact obligation."""
    target, _ = _consumer(tmp_path)
    (target / "untracked-result.md").write_text(_VERBOSE_DETAIL)
    result = _execute(
        target,
        "run-agent.ts",
        {"agent": "developer-agent", "task": "review", "model": "test/model"},
        _pi_stub(target, _envelope(artifact_paths=paths)),
    )

    assert result["details"]["error"] is True
    assert reason in result["details"]["reason"]
    assert _VERBOSE_DETAIL not in json.dumps(result)


def test_dispatch_wave_returns_aggregate_envelope_and_item_runtime_metadata(tmp_path):
    """Wave content is one bounded envelope; per-child telemetry stays in details."""
    target, base = _consumer(tmp_path)
    expected = _envelope()
    result = _execute(
        target,
        "dispatch-wave.ts",
        {
            "target": "main",
            "merge": False,
            "items": [
                {
                    "task": "review",
                    "branch": "test/envelope-wave",
                    "base": base,
                    "agent": "developer-agent",
                    "model": "test/model",
                }
            ],
        },
        _pi_stub(target, expected),
    )

    actual = _content_envelope(result)
    assert actual == expected
    assert set(actual) == _FIELDS
    assert _VERBOSE_DETAIL not in json.dumps(result["content"])
    item = result["details"]["items"][0]
    assert item["usage"] == {"input": 11, "output": 5}
    assert item["exitCode"] == 0
    assert "usage" not in actual and "exitCode" not in actual


def test_dispatch_wave_blocks_exit_zero_child_without_persisted_result(tmp_path):
    """An invalid child envelope cannot advance to premerge or merge."""
    target, base = _consumer(tmp_path)
    result = _execute(
        target,
        "dispatch-wave.ts",
        {
            "target": "main",
            "items": [
                {
                    "task": "review",
                    "branch": "test/missing-wave-result",
                    "base": base,
                    "agent": "developer-agent",
                    "model": "test/model",
                }
            ],
        },
        _pi_stub(target, _envelope(artifact_paths=["docs/reviews/missing.md"])),
    )

    actual = _content_envelope(result)
    assert actual["disposition"] == "block"
    assert actual["artifact_paths"] == []
    assert result["details"]["items"][0]["error"]
    assert result["details"]["items"][0]["premergeExit"] is None
