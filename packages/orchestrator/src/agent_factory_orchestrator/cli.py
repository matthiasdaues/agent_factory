"""run-playbook — step-at-a-time FSM runner.

Replaces you pressing "enter" between agent sessions.
Reads the marker, resolves the current state's agent, dispatches via
trigger, waits, checks the out-gate via phase advance, and self-chains
on success. Stops at human gates, final states, and halt conditions.

Pure delegation: all sequencing decisions go to phase advance, all
iteration-cap enforcement to phase retry, all dispatch to trigger.
This script holds no logic of its own (ADR-0001).

Usage:
  run-playbook [--playbook NAME] [--cli claude|copilot] [--from-state STATE]
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

MARKER_PATH = Path(".current-work/playbook-state.yml")
AUDIT_LOG = Path(".current-work/audit.log")
PLAYBOOKS_DIR = Path("factory/playbooks")
PHASE_SCRIPT = Path("factory/scripts/phase")
TRIGGER_SCRIPT = Path("factory/scripts/trigger")


def _provision_session_log() -> None:
    """Export AF_SESSION_LOG so every subprocess writes to the same audit log.

    This is the single provisioning point for the session log env var.
    factory/scripts/_session_log.py reads it on each gate run: set → log,
    unset → no-op. By exporting it here, the orchestrator ensures that
    phase advance, phase retry, trigger, and any gate script they invoke
    all write to .current-work/audit.log alongside the orchestrator's own
    entries — one file, one timeline, no configuration drift.
    """
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    os.environ["AF_SESSION_LOG"] = str(AUDIT_LOG.resolve())


def read_marker(marker_path: Path) -> dict[str, str]:
    """Parse the YAML marker into a flat dict."""
    if not marker_path.exists():
        return {}
    result = {}
    for line in marker_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, val = line.partition(":")
        if sep:
            result[key.strip()] = val.strip()
    return result


def read_fsm_state(playbook: str, state: str) -> dict:
    """Read a state's definition from the FSM file."""
    fsm_path = PLAYBOOKS_DIR / f"{playbook}.fsm.yml"
    if not fsm_path.exists():
        return {}

    # Minimal extraction: find agent and final fields for a named state.
    text = fsm_path.read_text(encoding="utf-8")
    in_state = False
    indent = 0
    agent = None
    final = False

    for line in text.splitlines():
        stripped = line.lstrip()
        current_indent = len(line) - len(stripped)

        if stripped == f"{state}:":
            in_state = True
            indent = current_indent
            continue

        if in_state:
            if current_indent <= indent and stripped and not stripped.startswith("#"):
                break
            if stripped.startswith("agent:"):
                val = stripped.partition(":")[2].strip()
                agent = None if val in ("null", "~", "") else val
            if stripped.startswith("final:"):
                val = stripped.partition(":")[2].strip()
                final = val in ("true", "True")

    return {"agent": agent, "final": final}


def write_audit(entry: dict) -> None:
    """Append one JSON-lines entry to the audit log."""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def run_phase_advance(dry_run: bool = False, playbook: str | None = None) -> int:
    """Call phase advance. Returns exit code."""
    cmd = [sys.executable, str(PHASE_SCRIPT), "advance"]
    if dry_run:
        cmd.append("--dry-run")
    if playbook:
        cmd.extend(["--playbook", playbook])
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


def run_phase_retry() -> int:
    """Call phase retry. Returns exit code."""
    cmd = [sys.executable, str(PHASE_SCRIPT), "retry"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


def run_trigger(agent: str, cli: str) -> tuple[int, str]:
    """Call trigger. Returns (exit_code, stderr)."""
    cmd = [
        sys.executable,
        str(TRIGGER_SCRIPT),
        "agent",
        agent,
        "--background",
        "--cli",
        cli,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.stdout.strip():
        print(result.stdout.strip())
    return result.returncode, result.stderr


def bootstrap_marker(playbook: str, state: str) -> None:
    """Create a fresh marker at the given state."""
    MARKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    fields = {
        "playbook": playbook,
        "state": state,
        "gate": "null",
        "result": "null",
        "open_findings": "0",
        "next": "null",
        "iteration": "1",
        "recorded_by": "run-playbook",
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    lines = [f"{k}: {v}" for k, v in fields.items()]
    MARKER_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--playbook",
        default=None,
        help="FSM to follow (default: read from marker, or greenfield-development)",
    )
    ap.add_argument(
        "--cli",
        default="claude",
        choices=["claude", "copilot"],
        help="AI CLI to dispatch through",
    )
    ap.add_argument(
        "--from-state",
        default=None,
        help="Bootstrap marker at this state (first run only)",
    )
    args = ap.parse_args(argv)

    _provision_session_log()

    # Bootstrap if needed
    marker = read_marker(MARKER_PATH)
    if not marker and args.from_state:
        playbook = args.playbook or "greenfield-development"
        bootstrap_marker(playbook, args.from_state)
        print(f"Bootstrapped marker at {args.from_state} ({playbook})")
        marker = read_marker(MARKER_PATH)
    elif not marker:
        print("No marker found. Use --from-state to bootstrap.", file=sys.stderr)
        return 1

    playbook = args.playbook or marker.get("playbook", "greenfield-development")

    # Main loop
    while True:
        marker = read_marker(MARKER_PATH)
        state = marker.get("state")
        if not state:
            print("Marker has no state field.", file=sys.stderr)
            return 1

        state_def = read_fsm_state(playbook, state)
        iteration = int(marker.get("iteration", "1"))

        # Final state → done
        if state_def.get("final"):
            print(f"\n✓ Playbook '{playbook}' complete (state: {state}).")
            write_audit(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "playbook": playbook,
                    "state": state,
                    "agent": None,
                    "action": "done",
                    "trigger_exit": None,
                    "phase_advance_exit": None,
                    "phase_retry_exit": None,
                    "iteration": iteration,
                    "duration_seconds": 0,
                }
            )
            return 0

        agent = state_def.get("agent")

        # Human gate → stop
        if agent is None:
            print(f"\n⏸ Human gate at '{state}': {playbook}")
            print("  Perform the required action, then re-invoke run-playbook.")
            write_audit(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "playbook": playbook,
                    "state": state,
                    "agent": None,
                    "action": "human-gate",
                    "trigger_exit": None,
                    "phase_advance_exit": None,
                    "phase_retry_exit": None,
                    "iteration": iteration,
                    "duration_seconds": 0,
                }
            )
            # Try dry-run in case human already acted
            if run_phase_advance(dry_run=True, playbook=playbook) == 0:
                print("  Out-gate already satisfied — advancing.")
                run_phase_advance(playbook=playbook)
                continue
            return 0

        # Can we already advance? (outputs from a prior run)
        if run_phase_advance(dry_run=True, playbook=playbook) == 0:
            print(f"  [{state}] Out-gate already satisfied — advancing.")
            run_phase_advance(playbook=playbook)
            continue

        # Dispatch
        print(f"\n▶ [{state}] Dispatching: {agent} (via {args.cli})")
        t0 = time.monotonic()
        trigger_exit, trigger_stderr = run_trigger(agent, args.cli)
        duration = time.monotonic() - t0

        # Config error → immediate halt
        if trigger_exit == 2:
            print(f"\n✗ Config error dispatching {agent}: {trigger_stderr.strip()}")
            write_audit(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "playbook": playbook,
                    "state": state,
                    "agent": agent,
                    "action": "halt",
                    "trigger_exit": 2,
                    "phase_advance_exit": None,
                    "phase_retry_exit": None,
                    "iteration": iteration,
                    "duration_seconds": round(duration, 1),
                }
            )
            return 2

        # Check out-gate
        advance_exit = run_phase_advance(playbook=playbook)
        if advance_exit == 0:
            print(f"  ✓ Gate passed — advanced past {state}.")
            write_audit(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "playbook": playbook,
                    "state": state,
                    "agent": agent,
                    "action": "advance",
                    "trigger_exit": trigger_exit,
                    "phase_advance_exit": 0,
                    "phase_retry_exit": None,
                    "iteration": iteration,
                    "duration_seconds": round(duration, 1),
                }
            )
            continue

        # Out-gate failed → retry?
        retry_exit = run_phase_retry()
        if retry_exit != 0:
            print(
                f"\n✗ Halt: iteration cap reached at '{state}' (iteration {iteration})."
            )
            write_audit(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "playbook": playbook,
                    "state": state,
                    "agent": agent,
                    "action": "halt",
                    "trigger_exit": trigger_exit,
                    "phase_advance_exit": advance_exit,
                    "phase_retry_exit": retry_exit,
                    "iteration": iteration,
                    "duration_seconds": round(duration, 1),
                }
            )
            return 1

        print(f"  ↻ Gate not yet satisfied — retrying {agent}.")
        write_audit(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "playbook": playbook,
                "state": state,
                "agent": agent,
                "action": "retry",
                "trigger_exit": trigger_exit,
                "phase_advance_exit": advance_exit,
                "phase_retry_exit": 0,
                "iteration": iteration,
                "duration_seconds": round(duration, 1),
            }
        )
        # Loop continues → re-dispatch


if __name__ == "__main__":
    sys.exit(main())
