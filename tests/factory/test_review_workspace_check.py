"""Contract tests for the review-mode pre-dispatch gate."""

from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path


def load_source_script(name: str):
    path = Path(__file__).resolve().parents[2] / "packages" / "factory" / "scripts" / name
    module_name = f"source_{name.replace('-', '_')}"
    loader = SourceFileLoader(module_name, str(path))
    spec = importlib.util.spec_from_loader(module_name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    loader.exec_module(module)
    return module


workspace_check = load_source_script("review-workspace-check")


def test_reads_canonical_test_all_before_compatibility_command(tmp_path):
    testing_yaml = tmp_path / "testing.yaml"
    testing_yaml.write_text(
        'test_all: "python -m pytest"\n'
        'test_command: "legacy test command"\n',
        encoding="utf-8",
    )

    assert workspace_check.read_test_command(testing_yaml) == "python -m pytest"
