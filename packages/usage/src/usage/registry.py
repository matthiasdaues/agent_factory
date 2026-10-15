"""Known CLI identifiers for the usage contract.

This set is not enforced by the contract check gate. It is prepared for
the accounting layer, which maps each CLI to a conservation rule.
Adding a new CLI requires one line here and a conservation rule — no
schema change.
"""

KNOWN_CLIS: frozenset[str] = frozenset(
    {
        "claude-code",
        "pi",
        "codex",
        "copilot",
    }
)
