"""Cycle Model Loader — loads and validates delivery.yaml.

The engine is a pure domain-logic container. It never writes state,
acquires locks, or imports scripts, configuration, or agent definitions.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

_SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"
_MODEL_SCHEMA_PATH = _SCHEMA_DIR / "cycle-model-v1.schema.json"

from engine.cycles import REQUIRED_CYCLES
EXECUTABLE_PATTERN = re.compile(
    r"(?:^|[\s;|&])"
    r"(?:"
    r"(?:rm|cp|mv|chmod|chown|kill|bash|sh|zsh|python|perl|ruby|node)\s+-"
    r"|/(?:bin|usr|sbin|tmp)/"
    r"|\$\(.*\)"
    r"|`[^`]+`"
    r")",
)


class CycleModelError(Exception):
    pass


@dataclass(frozen=True)
class Cycle:
    name: str
    delegated_attempt_limit: int | None = None
    description: str = ""


@dataclass(frozen=True)
class Route:
    from_cycle: str
    to_cycle: str
    recommend_if: str
    validators: tuple[str, ...] = ()


@dataclass(frozen=True)
class Artifact:
    name: str
    path: str
    description: str = ""
    collection: bool = False


@dataclass(frozen=True)
class Validator:
    name: str
    artifact: str
    description: str = ""


@dataclass(frozen=True)
class DeliveryModel:
    schema_version: int
    cycles: dict[str, Cycle]
    routes: list[Route]
    artifacts: dict[str, Artifact]
    validators: dict[str, Validator]

    @property
    def cycle_names(self) -> frozenset[str]:
        return frozenset(self.cycles.keys())


def load_delivery_model(path: Path) -> DeliveryModel:
    """Load and validate a delivery model from a YAML file.

    Raises CycleModelError with a named fault on any validation failure.
    """
    path = Path(path)
    if not path.exists():
        raise CycleModelError(f"delivery model not found: {path}")

    try:
        raw = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        raise CycleModelError(f"YAML parse error: {exc}") from exc

    if not isinstance(raw, dict):
        raise CycleModelError("delivery model must be a YAML mapping")

    _validate_schema(raw)
    _validate_semantics(raw)

    return _build_model(raw)


def _validate_schema(raw: dict[str, Any]) -> None:
    """Validate against the JSON Schema structurally."""
    try:
        import jsonschema
    except ImportError:
        _validate_schema_manual(raw)
        return

    schema = json.loads(_MODEL_SCHEMA_PATH.read_text())
    try:
        jsonschema.validate(raw, schema, format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as exc:
        raise CycleModelError(f"schema validation failed: {exc.message}") from exc


def _validate_schema_manual(raw: dict[str, Any]) -> None:
    """Fallback structural validation when jsonschema is not installed."""
    for key in ("schema_version", "cycles", "routes", "artifacts", "validators"):
        if key not in raw:
            raise CycleModelError(f"missing required field: {key}")

    cycles = raw.get("cycles", {})
    if not isinstance(cycles, dict):
        raise CycleModelError("'cycles' must be a mapping")
    for name in REQUIRED_CYCLES:
        if name not in cycles:
            raise CycleModelError(f"missing required cycle: {name}")

    for extra in set(cycles.keys()) - REQUIRED_CYCLES:
        raise CycleModelError(f"unknown cycle: {extra}")

    for name in REQUIRED_CYCLES - {"DONE"}:
        cycle_data = cycles[name]
        if not isinstance(cycle_data, dict):
            raise CycleModelError(f"cycle {name} must be a mapping")
        if "delegated_attempt_limit" not in cycle_data:
            raise CycleModelError(
                f"cycle {name} missing required field: delegated_attempt_limit"
            )
        limit = cycle_data["delegated_attempt_limit"]
        if not isinstance(limit, int) or limit < 1:
            raise CycleModelError(
                f"cycle {name}: delegated_attempt_limit must be a positive integer"
            )

    routes = raw.get("routes", [])
    if not isinstance(routes, list) or len(routes) < 1:
        raise CycleModelError("'routes' must be a non-empty list")

    valid_from = {"IDEA", "CONCEPT", "ROADMAP", "REFINE", "REALIZE"}
    valid_to = valid_from | {"DONE"}
    for i, route in enumerate(routes):
        if not isinstance(route, dict):
            raise CycleModelError(f"route {i}: must be a mapping")
        for field_name in ("from", "to", "recommend_if"):
            if field_name not in route:
                raise CycleModelError(f"route {i}: missing required field '{field_name}'")
        if route["from"] not in valid_from:
            raise CycleModelError(f"route {i}: invalid 'from' value: {route['from']}")
        if route["to"] not in valid_to:
            raise CycleModelError(f"route {i}: invalid 'to' value: {route['to']}")


def _validate_semantics(raw: dict[str, Any]) -> None:
    """Validate semantic constraints beyond structural schema."""
    artifact_names = set(raw.get("artifacts", {}).keys())

    validators = raw.get("validators", {})
    for vname, vdata in validators.items():
        if not isinstance(vdata, dict):
            continue
        ref = vdata.get("artifact", "")
        if ref and ref not in artifact_names:
            raise CycleModelError(
                f"validator '{vname}' references unknown artifact: {ref}"
            )
        desc = vdata.get("description", "")
        if desc and EXECUTABLE_PATTERN.search(desc):
            raise CycleModelError(
                f"validator '{vname}' contains executable command in description"
            )

    validator_names = set(raw.get("validators", {}).keys())

    routes = raw.get("routes", [])
    for route in routes:
        if not isinstance(route, dict):
            continue
        for forbidden in ("direction", "classification"):
            if forbidden in route:
                raise CycleModelError(
                    f"rejected: route {route.get('from', '?')}→{route.get('to', '?')} "
                    f"contains forbidden field '{forbidden}'"
                )
        for vref in route.get("validators", []):
            if vref not in validator_names:
                raise CycleModelError(
                    f"route {route.get('from', '?')}→{route.get('to', '?')} "
                    f"references unknown validator: {vref}"
                )


def _build_model(raw: dict[str, Any]) -> DeliveryModel:
    """Build the frozen dataclass model from validated raw data."""
    cycles = {}
    for name, data in raw["cycles"].items():
        if not isinstance(data, dict):
            data = {}
        cycles[name] = Cycle(
            name=name,
            delegated_attempt_limit=data.get("delegated_attempt_limit"),
            description=data.get("description", ""),
        )

    routes = []
    for r in raw["routes"]:
        routes.append(Route(
            from_cycle=r["from"],
            to_cycle=r["to"],
            recommend_if=r["recommend_if"],
            validators=tuple(r.get("validators", ())),
        ))

    artifacts = {}
    for aname, adata in raw["artifacts"].items():
        artifacts[aname] = Artifact(
            name=aname,
            path=adata["path"],
            description=adata.get("description", ""),
            collection=adata.get("collection", False),
        )

    validators = {}
    for vname, vdata in raw["validators"].items():
        validators[vname] = Validator(
            name=vname,
            artifact=vdata["artifact"],
            description=vdata.get("description", ""),
        )

    return DeliveryModel(
        schema_version=raw["schema_version"],
        cycles=cycles,
        routes=routes,
        artifacts=artifacts,
        validators=validators,
    )
