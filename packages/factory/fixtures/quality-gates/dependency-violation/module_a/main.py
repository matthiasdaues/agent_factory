"""Fixture module with a deliberate forbidden dependency."""

from module_b import VALUE


def read_value() -> str:
    """Return the imported value so the dependency remains observable."""
    return VALUE
