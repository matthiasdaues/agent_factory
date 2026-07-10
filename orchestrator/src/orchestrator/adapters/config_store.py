"""TOML-backed ConfigStore adapter (ADR-0017, ST-0042).

Persists operator defaults (`adapter`, `timeout`, `cap`, `auto_approve`) in
the `[defaults]` table of `.orchestrator/config.toml`.

**T-28 (Python-baseline TOML question) resolution**: the project baseline is
Python 3.10+ (pyproject `requires-python = ">=3.10"`), but stdlib `tomllib`
is read-only and only ships from 3.11+. Even on 3.11+, `tomllib` cannot
*write* TOML, so a writer is needed regardless of which reader is chosen.
Rather than add a third-party TOML dependency, this adapter hand-rolls a
reader/writer restricted to the flat `[defaults]` table this store owns —
the "constrained reader" option named in ADR-0017/T-28. This keeps behaviour
identical across the whole 3.10-3.14 support range (no version-conditional
parsing) and needs no new runtime dependency, honouring the stdlib-first
policy (ADR-0006), which requires a follow-up ADR to justify any addition.
The scope is deliberately narrow: string/int/bool scalars in one table, no
arrays, no nested tables, no multi-line strings. Other tables in the same
file (the future adapter registry, ADR-0017/ST-0046) are treated as opaque
text and preserved byte-for-byte across a save() — this store only ever
reads or rewrites its own `[defaults]` table.
"""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path
from typing import Optional

from orchestrator.entities import Config


class ConfigStoreError(Exception):
    """Raised when config.toml is malformed or holds an invalid value (FR-Q6).

    The message always names the offending file and, where identifiable,
    the offending key, so the operator can repair it by hand.
    """


_TABLE_NAME = "defaults"
_TABLE_HEADER_RE = re.compile(r"^\[([A-Za-z0-9_.-]+)\]$")
_KV_RE = re.compile(r"^([A-Za-z0-9_-]+)\s*=\s*(.+)$")
_INT_RE = re.compile(r"^-?\d+$")

_KNOWN_KEYS = {"adapter", "timeout", "cap", "auto_approve"}


class TomlConfigStore:
    """Persists a `Config` in `.orchestrator/config.toml` (`ConfigStore` port)."""

    def __init__(self, orch_dir: Path) -> None:
        self.orch_dir = Path(orch_dir)
        self.config_path = self.orch_dir / "config.toml"

    def load(self) -> Optional[Config]:
        if not self.config_path.exists():
            return None

        text = self.config_path.read_text(encoding="utf-8")
        raw = self._parse_defaults_table(text)
        return Config(
            adapter=raw.get("adapter"),
            timeout=raw.get("timeout"),
            cap=raw.get("cap"),
            auto_approve=raw.get("auto_approve"),
        )

    def save(self, config: Config) -> None:
        self.orch_dir.mkdir(parents=True, exist_ok=True)
        existing_text = (
            self.config_path.read_text(encoding="utf-8")
            if self.config_path.exists()
            else ""
        )
        new_text = self._replace_defaults_table(existing_text, config)

        fd, tmp_name = tempfile.mkstemp(
            dir=self.orch_dir, prefix=".config.toml.", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(new_text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_name, self.config_path)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)

    # --- parsing ----------------------------------------------------------

    def _parse_defaults_table(self, text: str) -> dict:
        raw: dict = {}
        in_defaults = False
        for lineno, raw_line in enumerate(text.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            header_match = _TABLE_HEADER_RE.match(line)
            if header_match:
                in_defaults = header_match.group(1) == _TABLE_NAME
                continue

            if not in_defaults:
                continue

            kv_match = _KV_RE.match(line)
            if not kv_match:
                raise ConfigStoreError(
                    f"{self.config_path}: malformed TOML at line {lineno}: {raw_line!r}"
                )
            key, raw_value = kv_match.group(1), kv_match.group(2).strip()

            if key not in _KNOWN_KEYS:
                raise ConfigStoreError(
                    f"{self.config_path}: unknown key {key!r} in [defaults] "
                    f"(line {lineno})"
                )

            raw[key] = self._parse_value(key, raw_value, lineno)

        self._validate(raw)
        return raw

    def _parse_value(self, key: str, raw_value: str, lineno: int):
        if len(raw_value) >= 2 and raw_value[0] == '"' and raw_value[-1] == '"':
            return raw_value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        if raw_value in ("true", "false"):
            return raw_value == "true"
        if _INT_RE.match(raw_value):
            return int(raw_value)
        raise ConfigStoreError(
            f"{self.config_path}: key {key!r} has an unparsable value "
            f"{raw_value!r} (line {lineno})"
        )

    def _validate(self, raw: dict) -> None:
        if "adapter" in raw and not isinstance(raw["adapter"], str):
            raise ConfigStoreError(
                f"{self.config_path}: key 'adapter' must be a string, "
                f"got {raw['adapter']!r}"
            )
        if "timeout" in raw:
            value = raw["timeout"]
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ConfigStoreError(
                    f"{self.config_path}: key 'timeout' must be a positive "
                    f"integer number of seconds, got {value!r}"
                )
        if "cap" in raw:
            value = raw["cap"]
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise ConfigStoreError(
                    f"{self.config_path}: key 'cap' must be an integer "
                    f"greater than or equal to 1, got {value!r}"
                )
        if "auto_approve" in raw and not isinstance(raw["auto_approve"], bool):
            raise ConfigStoreError(
                f"{self.config_path}: key 'auto_approve' must be a boolean, "
                f"got {raw['auto_approve']!r}"
            )

    # --- serialization ------------------------------------------------------

    def _render_defaults_block(self, config: Config) -> str:
        lines = [f"[{_TABLE_NAME}]"]
        if config.adapter is not None:
            escaped = config.adapter.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'adapter = "{escaped}"')
        if config.timeout is not None:
            lines.append(f"timeout = {int(config.timeout)}")
        if config.cap is not None:
            lines.append(f"cap = {int(config.cap)}")
        if config.auto_approve is not None:
            lines.append(f"auto_approve = {'true' if config.auto_approve else 'false'}")
        return "\n".join(lines) + "\n"

    def _replace_defaults_table(self, existing_text: str, config: Config) -> str:
        new_block = self._render_defaults_block(config)

        if not existing_text.strip():
            return new_block

        lines = existing_text.splitlines()
        header_indices = [
            i for i, line in enumerate(lines) if _TABLE_HEADER_RE.match(line.strip())
        ]

        defaults_start: Optional[int] = None
        defaults_end = len(lines)
        for position, header_idx in enumerate(header_indices):
            name = _TABLE_HEADER_RE.match(lines[header_idx].strip()).group(1)
            if name == _TABLE_NAME:
                defaults_start = header_idx
                defaults_end = (
                    header_indices[position + 1]
                    if position + 1 < len(header_indices)
                    else len(lines)
                )
                break

        if defaults_start is None:
            prefix = existing_text
            if not prefix.endswith("\n"):
                prefix += "\n"
            if prefix.strip():
                prefix += "\n"
            return prefix + new_block

        before = lines[:defaults_start]
        after = lines[defaults_end:]
        rebuilt = before + new_block.splitlines() + after
        return "\n".join(rebuilt) + "\n"
