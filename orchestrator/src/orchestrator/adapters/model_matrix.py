from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional


class FileModelMatrix:
    """File-backed ModelMatrix adapter for operator-curated model-matrix.conf."""

    def __init__(self, matrix_path: Path) -> None:
        if not matrix_path.exists():
            raise FileNotFoundError(matrix_path)
        self.matrix_path = matrix_path
        self.facts: Dict[str, str] = {}
        self.policy: Dict[str, str] = {}
        self._parse(matrix_path.read_text(encoding="utf-8"))

    def get_tier(self, key: str) -> Optional[str]:
        return self.policy.get(key)

    def get_model(self, cli: str, tier: str) -> Optional[str]:
        return self.facts.get(f"{cli}.{tier}")

    def get_on_missing(self) -> str:
        return self.policy.get("on_missing", "halt")

    def configured_clis(self) -> List[str]:
        return sorted({key.split(".", 1)[0] for key in self.facts})

    def _parse(self, text: str) -> None:
        current: Optional[Dict[str, str]] = None

        for lineno, raw in enumerate(text.splitlines(), start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue

            match = re.match(r"^\[(\w+)\]$", line)
            if match:
                section = match.group(1).lower()
                if section == "facts":
                    current = self.facts
                elif section == "policy":
                    current = self.policy
                else:
                    raise ValueError(
                        f"line {lineno}: unknown section [{match.group(1)}]"
                    )
                continue

            if current is None:
                raise ValueError(f"line {lineno}: content outside a section")

            key_value = re.match(r"^([\w._-]+)\s*=\s*(.+)$", line)
            if not key_value:
                raise ValueError(f"line {lineno}: malformed entry: {line!r}")
            current[key_value.group(1).strip()] = key_value.group(2).strip()

        on_missing = self.policy.get("on_missing", "halt")
        if on_missing not in ("halt", "auto"):
            raise ValueError(
                f"invalid on_missing policy: {on_missing!r} (must be 'halt' or 'auto')"
            )
