"""TOML-backed AdapterRegistry adapter (ADR-0017, ST-0046).

Persists the registered-adapter inventory and each adapter's model
dictionary in `.orchestrator/config.toml` — the same file `TomlConfigStore`
(ST-0042) uses for the `[defaults]` table. Table-name coordination between
the two stores:

- `TomlConfigStore` owns exactly one table: `[defaults]`.
- `TomlAdapterRegistry` (this module) owns two kinds of tables:
  - `[adapters]` — one flat table; each key is a registered adapter's
    logical name, each value its quoted binary path. This mirrors the
    `[adapters]` shape `TomlConfigStore`'s own test suite
    (`test_save_preserves_unrelated_toml_sections`,
    tests/test_toml_config_store.py) already assumes as the foreign table it
    must leave byte-for-byte untouched.
  - `[models.<name>]` — one table per adapter that has at least one tier
    mapping, keyed by tier (`economy`/`standard`/`strong`) with a quoted
    model_id value. An adapter with an empty dictionary has no `[models.*]`
    table at all (nothing to render).

Neither store ever recognizes the other's table names, so a `save()` on one
port is a no-op with respect to the other's data: each adapter's writer
identifies the *other* store's tables purely as opaque foreign text (matched
by table-header line, never by content) and reproduces them byte-for-byte.

Same T-28 resolution as `TomlConfigStore` (see adapters/config_store.py):
stdlib `tomllib` can't write, so this module hand-rolls a reader/writer
constrained to the tables it owns — flat string-valued key/value pairs only,
no arrays, no multi-line strings. This needs no new runtime dependency,
honouring the stdlib-first policy (ADR-0006).
"""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from orchestrator.entities import AdapterEntry, ModelDictionary

_ADAPTERS_TABLE = "adapters"
_TABLE_HEADER_RE = re.compile(r"^\[([A-Za-z0-9_.-]+)\]$")
_MODELS_TABLE_RE = re.compile(r"^models\.([^.]+)$")
_KV_RE = re.compile(r"^([A-Za-z0-9_-]+)\s*=\s*(.+)$")
_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")


class TomlAdapterRegistry:
    """Persists an `AdapterRegistry` in `.orchestrator/config.toml`.

    Every mutating method (`register`, `unregister`, `set_model`,
    `remove_model`) re-reads the file, validates the requested change against
    that freshly-loaded state, and only then writes — mutation never touches
    the file until validation has fully passed, so a failed validation raises
    before any write is attempted and a failed write (e.g. a disk error) never
    reaches `os.replace`, leaving the last committed file byte-for-byte
    intact (BR-048, mirrors VR-032's write-temp-then-rename guarantee used by
    `TomlConfigStore`).
    """

    def __init__(self, orch_dir: Path) -> None:
        self.orch_dir = Path(orch_dir)
        self.config_path = self.orch_dir / "config.toml"

    # --- AdapterRegistry: reads -------------------------------------------

    def list_adapters(self) -> List[AdapterEntry]:
        adapters, _ = self._load()
        return [
            AdapterEntry(name=name, binary_path=path)
            for name, path in sorted(adapters.items())
        ]

    def get_adapter(self, name: str) -> AdapterEntry:
        adapters, _ = self._load()
        if name not in adapters:
            raise KeyError(f"adapter {name!r} is not registered")
        return AdapterEntry(name=name, binary_path=adapters[name])

    def get_model(self, adapter: str, tier: str) -> Optional[str]:
        adapters, models = self._load()
        if adapter not in adapters:
            raise KeyError(f"adapter {adapter!r} is not registered")
        return models.get(adapter, ModelDictionary()).get_model(tier)

    def list_models(self, adapter: str) -> List[Tuple[str, str]]:
        adapters, models = self._load()
        if adapter not in adapters:
            raise KeyError(f"adapter {adapter!r} is not registered")
        return models.get(adapter, ModelDictionary()).list_models()

    # --- AdapterRegistry: writes -------------------------------------------

    def register(self, name: str, binary_path: str) -> None:
        """Register `name` -> `binary_path` (BR-042, BR-043).

        Validates the binary path resolves to an executable file, the name
        is not already registered, and the same path is not registered under
        a different name — all before any write is attempted.
        """
        if not _NAME_RE.match(name):
            raise ValueError(
                f"adapter name {name!r} must match {_NAME_RE.pattern} "
                "(letters, digits, underscore, hyphen)"
            )

        adapters, models = self._load()

        if name in adapters:
            raise ValueError(f"adapter name {name!r} is already registered")
        if binary_path in adapters.values():
            raise ValueError(
                f"binary path {binary_path!r} is already registered under another name"
            )

        path = Path(binary_path)
        if not path.is_file() or not os.access(path, os.X_OK):
            raise ValueError(
                f"binary path {binary_path!r} does not resolve to an executable file"
            )

        adapters[name] = binary_path
        models[name] = ModelDictionary()
        self._save(adapters, models)

    def unregister(self, name: str) -> None:
        """Remove `name` and its model dictionary in one write (BR-044)."""
        adapters, models = self._load()
        if name not in adapters:
            raise KeyError(f"adapter {name!r} is not registered")

        del adapters[name]
        models.pop(name, None)
        self._save(adapters, models)

    def set_model(self, adapter: str, tier: str, model_id: str) -> None:
        adapters, models = self._load()
        if adapter not in adapters:
            raise KeyError(f"adapter {adapter!r} is not registered")

        dictionary = models.setdefault(adapter, ModelDictionary())
        dictionary.set_model(tier, model_id)  # raises ValueError before any write
        self._save(adapters, models)

    def remove_model(self, adapter: str, tier: str) -> None:
        adapters, models = self._load()
        if adapter not in adapters:
            raise KeyError(f"adapter {adapter!r} is not registered")

        dictionary = models.setdefault(adapter, ModelDictionary())
        dictionary.remove_model(tier)  # raises ValueError before any write
        self._save(adapters, models)

    # --- persistence --------------------------------------------------------

    def _load(self) -> Tuple[Dict[str, str], Dict[str, ModelDictionary]]:
        if not self.config_path.exists():
            return {}, {}
        text = self.config_path.read_text(encoding="utf-8")
        return self._parse(text)

    def _save(
        self, adapters: Dict[str, str], models: Dict[str, ModelDictionary]
    ) -> None:
        self.orch_dir.mkdir(parents=True, exist_ok=True)
        existing_text = (
            self.config_path.read_text(encoding="utf-8")
            if self.config_path.exists()
            else ""
        )
        new_text = self._splice(existing_text, adapters, models)

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

    # --- parsing --------------------------------------------------------

    def _parse(self, text: str) -> Tuple[Dict[str, str], Dict[str, ModelDictionary]]:
        adapters: Dict[str, str] = {}
        models: Dict[str, ModelDictionary] = {}

        for name, start, end, lines in self._segments(text):
            body = lines[start + 1 : end]
            if name == _ADAPTERS_TABLE:
                for key, raw_value in self._body_kv(body):
                    adapters[key] = self._parse_string(raw_value)
                continue

            models_match = _MODELS_TABLE_RE.match(name)
            if models_match:
                adapter_name = models_match.group(1)
                dictionary = models.setdefault(adapter_name, ModelDictionary())
                for key, raw_value in self._body_kv(body):
                    dictionary.set_model(key, self._parse_string(raw_value))

        return adapters, models

    def _body_kv(self, body_lines: List[str]):
        for line in body_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            match = _KV_RE.match(stripped)
            if not match:
                raise ValueError(
                    f"{self.config_path}: malformed TOML line {stripped!r}"
                )
            yield match.group(1), match.group(2).strip()

    def _parse_string(self, raw_value: str) -> str:
        if len(raw_value) >= 2 and raw_value[0] == '"' and raw_value[-1] == '"':
            return raw_value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        raise ValueError(
            f"{self.config_path}: expected a quoted string value, got {raw_value!r}"
        )

    def _segments(self, text: str):
        """Yield (table_name, header_line_index, end_line_index, all_lines)."""
        lines = text.splitlines()
        header_indices = [
            i for i, line in enumerate(lines) if _TABLE_HEADER_RE.match(line.strip())
        ]
        for position, header_idx in enumerate(header_indices):
            name = _TABLE_HEADER_RE.match(lines[header_idx].strip()).group(1)
            end = (
                header_indices[position + 1]
                if position + 1 < len(header_indices)
                else len(lines)
            )
            yield name, header_idx, end, lines

    # --- serialization ------------------------------------------------------

    def _escape(self, value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')

    def _render_block(
        self, adapters: Dict[str, str], models: Dict[str, ModelDictionary]
    ) -> str:
        blocks: List[str] = []

        if adapters:
            lines = [f"[{_ADAPTERS_TABLE}]"]
            for name in sorted(adapters.keys()):
                lines.append(f'{name} = "{self._escape(adapters[name])}"')
            blocks.append("\n".join(lines))

        for name in sorted(adapters.keys()):
            dictionary = models.get(name)
            if not dictionary:
                continue
            pairs = dictionary.list_models()
            if not pairs:
                continue
            lines = [f"[models.{name}]"]
            for tier, model_id in sorted(pairs):
                lines.append(f'{tier} = "{self._escape(model_id)}"')
            blocks.append("\n".join(lines))

        return ("\n\n".join(blocks) + "\n") if blocks else ""

    def _splice(
        self,
        existing_text: str,
        adapters: Dict[str, str],
        models: Dict[str, ModelDictionary],
    ) -> str:
        new_block = self._render_block(adapters, models)

        lines = existing_text.splitlines()
        header_indices = [
            i for i, line in enumerate(lines) if _TABLE_HEADER_RE.match(line.strip())
        ]

        def is_ours(name: str) -> bool:
            return name == _ADAPTERS_TABLE or bool(_MODELS_TABLE_RE.match(name))

        segments = []
        for position, header_idx in enumerate(header_indices):
            name = _TABLE_HEADER_RE.match(lines[header_idx].strip()).group(1)
            end = (
                header_indices[position + 1]
                if position + 1 < len(header_indices)
                else len(lines)
            )
            segments.append((header_idx, end, is_ours(name)))

        result_lines: List[str] = []
        insert_at: Optional[int] = None
        cursor = 0
        for start, end, ours in segments:
            if cursor < start:
                result_lines.extend(lines[cursor:start])
            if ours:
                if insert_at is None:
                    insert_at = len(result_lines)
            else:
                result_lines.extend(lines[start:end])
            cursor = end
        if cursor < len(lines):
            result_lines.extend(lines[cursor:])

        if not new_block:
            new_lines = result_lines
        elif insert_at is None:
            if result_lines and result_lines[-1].strip():
                result_lines.append("")
            new_lines = result_lines + new_block.splitlines()
        else:
            new_lines = (
                result_lines[:insert_at]
                + new_block.splitlines()
                + result_lines[insert_at:]
            )

        text = "\n".join(new_lines)
        if text and not text.endswith("\n"):
            text += "\n"
        return text
