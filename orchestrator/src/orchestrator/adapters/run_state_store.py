"""Run-state persistence and single-run locking adapters."""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from jsonschema import validate

from orchestrator.entities import Run, RunMode, PhaseRecord, PhaseStatus, GateResult

_RUN_STATE_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "RunState",
    "type": "object",
    "required": [
        "run_id",
        "branch",
        "chain",
        "current_phase",
        "iteration",
        "mode",
        "phases",
    ],
    "additionalProperties": False,
    "properties": {
        "run_id": {"type": "string"},
        "branch": {"type": "string"},
        "chain": {"type": "array", "items": {"type": "string"}},
        "current_phase": {"type": "string"},
        "iteration": {"type": "integer", "minimum": 0},
        "mode": {"enum": [mode.value for mode in RunMode]},
        "tooling_version": {"type": ["string", "null"]},
        "phases": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "author", "status"],
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "author": {"type": "string"},
                    "reviewer": {"type": ["string", "null"]},
                    "status": {"enum": [status.value for status in PhaseStatus]},
                    "iteration": {"type": "integer", "minimum": 0},
                    "last_gate": {
                        "type": ["object", "null"],
                        "required": ["passed", "errored", "hook", "error_count"],
                        "additionalProperties": False,
                        "properties": {
                            "passed": {"type": "boolean"},
                            "errored": {"type": "boolean"},
                            "hook": {"type": "string"},
                            "error_count": {"type": "integer", "minimum": 0},
                            "timed_out": {"type": "boolean"},
                        },
                    },
                    "rejection_note": {"type": ["string", "null"]},
                    "last_reviewed_cycle": {"type": ["integer", "null"], "minimum": 0},
                    "halted_from": {
                        "type": ["string", "null"],
                        "enum": [None, *[status.value for status in PhaseStatus]],
                    },
                },
            },
        },
    },
}


class JsonRunStateStore:
    """Atomic JSON-backed RunState store."""

    def __init__(self, orch_dir: Path) -> None:
        self.orch_dir = orch_dir
        self.orch_dir.mkdir(parents=True, exist_ok=True)
        self.run_path = self.orch_dir / "run.json"

    def load(self) -> Optional[Run]:
        if not self.run_path.exists():
            return None

        payload = json.loads(self.run_path.read_text(encoding="utf-8"))
        validate(instance=payload, schema=_RUN_STATE_SCHEMA)
        return self._deserialize_run(payload)

    def save(self, run: Run) -> None:
        payload = self._serialize_run(run)
        validate(instance=payload, schema=_RUN_STATE_SCHEMA)

        temp_path = self.orch_dir / f"{self.run_path.name}.{os.getpid()}.tmp"
        try:
            with temp_path.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, self.run_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def exists(self) -> bool:
        return self.run_path.exists()

    def _serialize_run(self, run: Run) -> dict[str, Any]:
        payload = asdict(run)
        payload["mode"] = run.mode.value
        payload["phases"] = [self._serialize_phase(phase) for phase in run.phases]
        return payload

    def _serialize_phase(self, phase: PhaseRecord) -> dict[str, Any]:
        payload = asdict(phase)
        payload["status"] = phase.status.value
        payload["halted_from"] = (
            phase.halted_from.value if phase.halted_from is not None else None
        )
        payload["last_gate"] = self._serialize_gate(phase.last_gate)
        return payload

    def _serialize_gate(self, gate: Optional[GateResult]) -> Optional[dict[str, Any]]:
        if gate is None:
            return None
        data = asdict(gate)
        data.pop("output", None)  # output is transient, not persisted
        return data

    def _deserialize_run(self, payload: dict[str, Any]) -> Run:
        return Run(
            run_id=payload["run_id"],
            branch=payload["branch"],
            chain=list(payload["chain"]),
            current_phase=payload["current_phase"],
            iteration=payload["iteration"],
            mode=RunMode(payload["mode"]),
            phases=[self._deserialize_phase(phase) for phase in payload["phases"]],
            tooling_version=payload.get("tooling_version"),
        )

    def _deserialize_phase(self, payload: dict[str, Any]) -> PhaseRecord:
        return PhaseRecord(
            name=payload["name"],
            author=payload["author"],
            reviewer=payload.get("reviewer"),
            status=PhaseStatus(payload["status"]),
            iteration=payload.get("iteration", 0),
            last_gate=self._deserialize_gate(payload.get("last_gate")),
            rejection_note=payload.get("rejection_note"),
            # FAGAN-0040: back-compat — pre-existing run.json has no key → None.
            last_reviewed_cycle=payload.get("last_reviewed_cycle"),
            halted_from=PhaseStatus(payload["halted_from"])
            if payload.get("halted_from") is not None
            else None,
        )

    def _deserialize_gate(
        self, payload: Optional[dict[str, Any]]
    ) -> Optional[GateResult]:
        if payload is None:
            return None
        return GateResult(
            passed=payload["passed"],
            errored=payload["errored"],
            hook=payload["hook"],
            error_count=payload["error_count"],
            timed_out=payload.get("timed_out", False),
        )


class FileRunLock:
    """File-backed single-run lock."""

    def __init__(self, orch_dir: Path) -> None:
        self.orch_dir = orch_dir
        self.orch_dir.mkdir(parents=True, exist_ok=True)
        self.lock_path = self.orch_dir / "run.lock"

    def acquire(self, run_id: str) -> None:
        for _attempt in range(2):
            try:
                fd = os.open(
                    str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644
                )
            except FileExistsError:
                current = self._read_lock()
                if current is not None and self._pid_is_alive(current["pid"]):
                    raise RuntimeError(
                        f"run.lock is held by live process {current['pid']} "
                        f"for run {current['run_id']}"
                    )
                self.lock_path.unlink(missing_ok=True)
                continue

            try:
                payload = {
                    "run_id": run_id,
                    "pid": os.getpid(),
                    "started_at": datetime.now(timezone.utc).isoformat(),
                }
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump(payload, handle, indent=2)
                    handle.write("\n")
                    handle.flush()
                    os.fsync(handle.fileno())
            except BaseException:
                self.lock_path.unlink(missing_ok=True)
                raise
            return

        raise RuntimeError("failed to acquire run lock after stale-lock cleanup")

    def release(self) -> None:
        self.lock_path.unlink(missing_ok=True)

    def is_held(self) -> bool:
        data = self._read_lock()
        if data is None:
            return False
        return self._pid_is_alive(data["pid"])

    def is_held_by_other(self) -> bool:
        """Return True if the lock is held by a live process OTHER than this one."""
        data = self._read_lock()
        if data is None:
            return False
        try:
            pid_value = int(data["pid"])
        except (TypeError, ValueError):
            return False
        if pid_value == os.getpid():
            return False
        return self._pid_is_alive(pid_value)

    def _pid_is_alive(self, pid: Any) -> bool:
        try:
            pid_value = int(pid)
            if pid_value <= 0:
                return False
            os.kill(pid_value, 0)
        except (TypeError, ValueError):
            return False
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True

    def _read_lock(self) -> Optional[dict[str, Any]]:
        if not self.lock_path.exists():
            return None
        try:
            payload = json.loads(self.lock_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

        if not isinstance(payload, dict):
            return None
        if {"run_id", "pid", "started_at"} - payload.keys():
            return None
        return payload
