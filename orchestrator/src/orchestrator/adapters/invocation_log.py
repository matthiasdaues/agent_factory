"""Append-only JSONL invocation log adapter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from orchestrator.entities import AgentInvocation, AgentRole, GateResult
from orchestrator.ports import LogRecord


class FileInvocationLog:
    """Logger port implementation writing one JSON line per invocation."""

    def __init__(self, log_dir: Path) -> None:
        self.log_dir = log_dir
        self.log_file = self.log_dir / "log.jsonl"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file.touch(exist_ok=True)

    def log(self, record: AgentInvocation, gate: Optional[GateResult] = None) -> None:
        payload = {
            "agent": record.agent,
            "role": record.role.value,
            "adapter": record.adapter,
            "model": record.model,
            "exit_code": record.exit_code,
            "duration_ms": record.duration_ms,
            "timed_out": record.timed_out,
            "auth_error": record.auth_error,
            "config_error": record.config_error,
        }
        if gate is not None:
            payload.update(
                {
                    "passed": gate.passed,
                    "errored": gate.errored,
                    "hook": gate.hook,
                    "error_count": gate.error_count,
                    "gate_timed_out": gate.timed_out,
                }
            )
        with self.log_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def read_entries(self) -> List[LogRecord]:
        """Read-only parse of every logged line, in append order (FR-T5).

        Inverse of ``log()``. Never mutates ``log_file`` (FR-T6).
        """
        records: List[LogRecord] = []
        for line in self.log_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            invocation = AgentInvocation(
                agent=payload["agent"],
                role=AgentRole(payload["role"]),
                adapter=payload["adapter"],
                model=payload.get("model"),
                exit_code=payload["exit_code"],
                duration_ms=payload["duration_ms"],
                timed_out=payload["timed_out"],
                auth_error=payload["auth_error"],
                config_error=payload["config_error"],
            )
            gate: Optional[GateResult] = None
            if "passed" in payload:
                gate = GateResult(
                    passed=payload["passed"],
                    errored=payload["errored"],
                    hook=payload["hook"],
                    error_count=payload["error_count"],
                    timed_out=payload.get("gate_timed_out", False),
                )
            records.append(LogRecord(invocation=invocation, gate=gate))
        return records
