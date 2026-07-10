"""SettingsResolver — four-layer precedence for operator defaults (ST-0043).

Precedence (BR-040, VR-034, ADR-0017):

    menu selection > CLI flag > config.toml > built-in default

A ``None`` at any layer means "continue to the next layer," never "stop with
null" — falsy-but-present values (``0``, ``False``, ``""``) are real
selections and win outright; only ``None`` falls through. The same resolver
backs both direct mode and menu mode (FR-Q3, SF-07), so the two entry paths
can never diverge.
"""

from __future__ import annotations

from typing import Any, Optional, Union

from .entities import Config
from .ports import ConfigStore

# Specification table (UC-09, ST-0043 acceptance criteria).
BUILTIN_DEFAULTS: dict[str, Any] = {
    "adapter": "copilot",
    "timeout": 1800,
    "cap": 3,
    "auto_approve": False,
}


class SettingsResolver:
    """Resolves one effective setting through the four-layer precedence chain.

    Accepts either an already-loaded ``Config`` or a ``ConfigStore`` to load
    from (loaded once, at construction time) as the third-layer source. A
    missing store, or a store reporting an absent ``config.toml`` (``load()``
    returning ``None``, BR-037), both mean "no config-layer override" — the
    chain falls through to the built-in default.
    """

    def __init__(self, config_source: Union[Config, ConfigStore, None] = None):
        if config_source is None or isinstance(config_source, Config):
            self._config: Optional[Config] = config_source
        else:
            # Duck-typed ConfigStore: load once so resolve() stays pure.
            self._config = config_source.load()

    def resolve(self, key: str, menu_value: Any = None, cli_flag: Any = None) -> Any:
        """Resolve one setting's effective value.

        Args:
            key: One of ``adapter``, ``timeout``, ``cap``, ``auto_approve``.
            menu_value: The current menu selection, or ``None`` if unset.
            cli_flag: The CLI flag value, or ``None`` if unset.

        Returns:
            The first non-``None`` value found, checked in order: menu
            selection, CLI flag, persisted config, built-in default.

        Raises:
            ValueError: If ``key`` is not one of the four known settings.
        """
        if key not in BUILTIN_DEFAULTS:
            raise ValueError(
                f"Unknown setting {key!r}. Must be one of {sorted(BUILTIN_DEFAULTS)}."
            )

        if menu_value is not None:
            return menu_value
        if cli_flag is not None:
            return cli_flag
        if self._config is not None:
            config_value = getattr(self._config, key)
            if config_value is not None:
                return config_value
        return BUILTIN_DEFAULTS[key]
