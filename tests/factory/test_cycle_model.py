"""Contract tests for the cycle model loader.

Owned contracts:
  - Model loads from tracked source (standard risk)
  - Unknown artifact reference fails validation (standard risk)
  - Validator with executable command rejected (standard risk)
  - Route with direction field rejected (standard risk)
  - Engine package imports nothing from scripts, config, agents, skills, or orchestrator
"""

from __future__ import annotations

import copy
import importlib
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGES_DIR = REPO_ROOT / "packages" / "factory"

if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from engine.cycle_model import CycleModelError, load_delivery_model

DELIVERY_YAML = PACKAGES_DIR / "engine" / "models" / "delivery.yaml"


class TestValidModelLoads:
    def test_loads_five_cycles_and_done(self):
        model = load_delivery_model(DELIVERY_YAML)
        assert set(model.cycle_names) == {
            "IDEA", "CONCEPT", "ROADMAP", "REFINE", "REALIZE", "DONE",
        }

    def test_every_route_has_required_fields(self):
        model = load_delivery_model(DELIVERY_YAML)
        for route in model.routes:
            assert route.from_cycle, "route missing 'from'"
            assert route.to_cycle, "route missing 'to'"
            assert route.recommend_if, "route missing 'recommend_if'"

    def test_no_route_has_direction_or_classification(self):
        model = load_delivery_model(DELIVERY_YAML)
        raw = yaml.safe_load(DELIVERY_YAML.read_text())
        for route in raw["routes"]:
            assert "direction" not in route
            assert "classification" not in route

    def test_cycles_have_attempt_limits(self):
        model = load_delivery_model(DELIVERY_YAML)
        for name in ("IDEA", "CONCEPT", "ROADMAP", "REFINE", "REALIZE"):
            cycle = model.cycles[name]
            assert cycle.delegated_attempt_limit >= 1

    def test_done_has_no_attempt_limit(self):
        model = load_delivery_model(DELIVERY_YAML)
        assert model.cycles["DONE"].delegated_attempt_limit is None

    def test_artifacts_declared(self):
        model = load_delivery_model(DELIVERY_YAML)
        assert len(model.artifacts) > 0

    def test_validators_declared(self):
        model = load_delivery_model(DELIVERY_YAML)
        assert len(model.validators) > 0

    def test_schema_version(self):
        model = load_delivery_model(DELIVERY_YAML)
        assert model.schema_version == 1


class TestMissingRouteField:
    def test_missing_from_raises(self, tmp_path):
        raw = yaml.safe_load(DELIVERY_YAML.read_text())
        del raw["routes"][0]["from"]
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.dump(raw))
        with pytest.raises(CycleModelError, match="from"):
            load_delivery_model(bad)

    def test_missing_to_raises(self, tmp_path):
        raw = yaml.safe_load(DELIVERY_YAML.read_text())
        del raw["routes"][0]["to"]
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.dump(raw))
        with pytest.raises(CycleModelError, match="to"):
            load_delivery_model(bad)

    def test_missing_recommend_if_raises(self, tmp_path):
        raw = yaml.safe_load(DELIVERY_YAML.read_text())
        del raw["routes"][0]["recommend_if"]
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.dump(raw))
        with pytest.raises(CycleModelError, match="recommend_if"):
            load_delivery_model(bad)


class TestMissingCycle:
    def test_missing_required_cycle_raises(self, tmp_path):
        raw = yaml.safe_load(DELIVERY_YAML.read_text())
        del raw["cycles"]["ROADMAP"]
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.dump(raw))
        with pytest.raises(CycleModelError, match="ROADMAP"):
            load_delivery_model(bad)


class TestUnknownArtifactReference:
    def test_validator_referencing_unknown_artifact_raises(self, tmp_path):
        raw = yaml.safe_load(DELIVERY_YAML.read_text())
        raw["validators"]["bad_lint"] = {
            "artifact": "nonexistent_artifact",
            "description": "references nothing",
        }
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.dump(raw))
        with pytest.raises(CycleModelError, match="nonexistent_artifact"):
            load_delivery_model(bad)


class TestExecutableCommandRejected:
    @pytest.mark.parametrize("command", [
        "rm -rf /",
        "$(whoami)",
        "`id`",
        "bash -c 'echo pwned'",
        "/bin/sh -c test",
    ])
    def test_executable_in_validator_description_rejected(self, tmp_path, command):
        raw = yaml.safe_load(DELIVERY_YAML.read_text())
        raw["validators"]["evil_lint"] = {
            "artifact": "proposal",
            "description": command,
        }
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.dump(raw))
        with pytest.raises(CycleModelError, match="executable"):
            load_delivery_model(bad)


class TestRouteValidatorReference:
    def test_unknown_validator_on_route_rejected(self, tmp_path):
        raw = yaml.safe_load(DELIVERY_YAML.read_text())
        raw["routes"][0]["validators"] = ["nonexistent_validator"]
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.dump(raw))
        with pytest.raises(CycleModelError, match="nonexistent_validator"):
            load_delivery_model(bad)

    def test_valid_validator_on_route_accepted(self):
        model = load_delivery_model(DELIVERY_YAML)
        route = model.routes[0]
        assert len(route.validators) > 0
        for vname in route.validators:
            assert vname in model.validators


class TestDirectionFieldRejected:
    def test_direction_on_route_rejected(self, tmp_path):
        raw = yaml.safe_load(DELIVERY_YAML.read_text())
        raw["routes"][0]["direction"] = "forward"
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.dump(raw))
        with pytest.raises(CycleModelError, match="direction"):
            load_delivery_model(bad)

    def test_classification_on_route_rejected(self, tmp_path):
        raw = yaml.safe_load(DELIVERY_YAML.read_text())
        raw["routes"][0]["classification"] = "progression"
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.dump(raw))
        with pytest.raises(CycleModelError, match="classification"):
            load_delivery_model(bad)


class TestDependencyBoundary:
    """The engine package must not import from scripts, config, agents, skills, or orchestrator."""

    FORBIDDEN_PREFIXES = (
        "factory.scripts",
        "factory.config",
        "factory.agents",
        "factory.skills",
        "factory.playbooks",
    )

    def test_engine_imports_no_forbidden_modules(self):
        engine_mod = importlib.import_module("engine.cycle_model")
        transitive = set()
        _collect_imports(engine_mod, transitive, set())
        for mod_name in transitive:
            for prefix in self.FORBIDDEN_PREFIXES:
                assert not mod_name.startswith(prefix), (
                    f"engine.cycle_model transitively imports {mod_name}"
                )


def _collect_imports(module, collected: set, visited: set):
    name = getattr(module, "__name__", "")
    if name in visited:
        return
    visited.add(name)
    collected.add(name)
    for attr_name in dir(module):
        attr = getattr(module, attr_name, None)
        if hasattr(attr, "__module__") and attr.__module__:
            collected.add(attr.__module__)
