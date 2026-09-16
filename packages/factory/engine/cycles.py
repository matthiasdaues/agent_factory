"""Canonical cycle names — no external dependencies.

Importable from any context (standalone scripts, engine, tests)
without pulling in pyyaml or other heavy dependencies.
"""

REQUIRED_CYCLES = frozenset({"IDEA", "CONCEPT", "ROADMAP", "REFINE", "REALIZE", "DONE"})
