"""Acceptance tests for ST-0068 session-end retrospective signals.

The pure derivation seam exercises BR-042 without depending on a provider
runtime.  A record-serialization check and canonical guidance checks complete
the vertical slice from native turn evidence to retrospective consumption.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import uuid
from importlib.machinery import SourceFileLoader
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "factory" / "scripts" / "usage-capture"


def _load_usage_capture():
    loader = SourceFileLoader("session_usage_capture", str(_SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


usage_capture = _load_usage_capture()


def _write_jsonl(path, records):
    path.write_text(
        "".join(f"{json.dumps(record)}\n" for record in records),
        encoding="utf-8",
    )


def _turn(input_tokens, cache_read_tokens):
    return usage_capture.ProviderUsageTurn(
        input_tokens=input_tokens,
        cache_read_tokens=cache_read_tokens,
    )


def _signals(turns):
    return usage_capture.derive_session_usage_signals(
        turns,
        cli="pi",
        provider="openrouter",
    )


def test_UC_11_BR_042_full_cache_derives_all_signals():
    signals = _signals([_turn(100, 0), _turn(120, 20), _turn(300, 0), _turn(400, 40)])

    assert signals.cli == "pi"
    assert signals.provider == "openrouter"
    assert signals.usage_capability == "full-cache"
    assert signals.cache_miss_turns == 2
    assert signals.cache_miss_input_tokens == 400
    assert signals.late_early_input_ratio == 4.0


def test_UC_11_BR_042_input_only_derives_ratio_independently():
    signals = _signals([_turn(100, None), _turn(200, None), _turn(300, None)])

    assert signals.usage_capability == "input-only"
    assert signals.cache_miss_turns is None
    assert signals.cache_miss_input_tokens is None
    assert signals.late_early_input_ratio == 3.0


def test_UC_11_BR_042_unavailable_when_no_eligible_turns():
    signals = _signals([])

    assert signals.usage_capability == "unavailable"
    assert signals.cache_miss_turns is None
    assert signals.cache_miss_input_tokens is None
    assert signals.late_early_input_ratio is None


def test_UC_11_BR_042_missing_input_nulls_every_signal():
    signals = _signals([_turn(100, 10), _turn(None, 0), _turn(300, 30)])

    assert signals.usage_capability == "unavailable"
    assert signals.cache_miss_turns is None
    assert signals.cache_miss_input_tokens is None
    assert signals.late_early_input_ratio is None


def test_UC_11_BR_042_no_cache_miss_stores_numeric_zeros():
    signals = _signals([_turn(100, 10), _turn(200, 20)])

    assert signals.cache_miss_turns == 0
    assert signals.cache_miss_input_tokens == 0
    assert signals.late_early_input_ratio == 2.0


def test_UC_11_BR_042_fewer_than_two_turns_nulls_only_ratio():
    signals = _signals([_turn(100, 0)])

    assert signals.usage_capability == "full-cache"
    assert signals.cache_miss_turns == 1
    assert signals.cache_miss_input_tokens == 100
    assert signals.late_early_input_ratio is None


def test_UC_11_BR_042_zero_early_denominator_nulls_only_ratio():
    signals = _signals([_turn(0, 0), _turn(200, 0)])

    assert signals.usage_capability == "full-cache"
    assert signals.cache_miss_turns == 1
    assert signals.cache_miss_input_tokens == 200
    assert signals.late_early_input_ratio is None


def test_UC_11_BR_042_usage_record_stores_provider_qualified_signals():
    signals = _signals([_turn(100, 0), _turn(200, 20)])
    record = usage_capture.UsageRecord(
        record_id="session-0001",
        project_id=str(uuid.uuid4()),
        project_name="fixture",
        normalized_input=1,
        normalized_output=1,
        **signals.to_record_fields(),
    ).to_dict()

    assert record["cli"] == "pi"
    assert record["provider"] == "openrouter"
    assert record["usage_capability"] == "full-cache"
    assert record["cache_miss_turns"] == 1
    assert record["cache_miss_input_tokens"] == 100
    assert record["late_early_input_ratio"] == 2.0


def test_UC_11_BR_042_capture_derives_and_persists_session_signals(
    tmp_path, monkeypatch
):
    config = tmp_path / "config"
    config.mkdir()
    (config / "project.json").write_text(
        json.dumps(
            {
                "project_id": str(uuid.uuid4()),
                "project_name": "fixture",
            }
        ),
        encoding="utf-8",
    )
    transcript = tmp_path / "claude.jsonl"
    _write_jsonl(
        transcript,
        [
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": "one",
                    "usage": {
                        "input_tokens": 100,
                        "cache_read_input_tokens": 0,
                    },
                },
            },
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": "two",
                    "usage": {
                        "input_tokens": 200,
                        "cache_read_input_tokens": 20,
                    },
                },
            },
        ],
    )
    args = usage_capture._build_arg_parser().parse_args(
        [
            "--cli",
            "claude-code",
            "--provider",
            "anthropic",
            "--transcript",
            str(transcript),
            "--session",
            "session-signals",
        ]
    )
    monkeypatch.setattr(usage_capture, "count_tokens", lambda text: len(text))

    assert usage_capture._capture(args, tmp_path)

    record = json.loads(
        (tmp_path / ".agent-factory/usage/claude-code_session-signals.jsonl").read_text(
            encoding="utf-8"
        )
    )
    assert record["cli"] == "claude-code"
    assert record["provider"] == "anthropic"
    assert record["usage_capability"] == "full-cache"
    assert record["cache_miss_turns"] == 1
    assert record["cache_miss_input_tokens"] == 100
    assert record["late_early_input_ratio"] == 2.0


def test_UC_11_BR_042_claude_normalizer_keeps_eligible_turn_nullability(tmp_path):
    transcript = tmp_path / "claude.jsonl"
    _write_jsonl(
        transcript,
        [
            {"type": "progress", "usage": {"input_tokens": 999}},
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": "one",
                    "usage": {
                        "input_tokens": 100,
                        "cache_read_input_tokens": 0,
                    },
                },
            },
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": "two",
                    "usage": {"cache_read_input_tokens": 10},
                },
            },
            {
                "type": "assistant",
                "isSidechain": True,
                "message": {
                    "role": "assistant",
                    "content": "child",
                    "usage": {
                        "input_tokens": 500,
                        "cache_read_input_tokens": 0,
                    },
                },
            },
        ],
    )

    normalized = usage_capture.get_normalizer("claude-code").parse(transcript)

    assert normalized.eligible_turns == [_turn(100, 0), _turn(None, 10)]
    assert _signals(normalized.eligible_turns).usage_capability == "unavailable"


def test_UC_11_BR_042_codex_excludes_synthetic_aggregate_usage(tmp_path):
    transcript = tmp_path / "codex.jsonl"
    _write_jsonl(
        transcript,
        [
            {
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {
                        "total_token_usage": {
                            "input_tokens": 999,
                            "cached_input_tokens": 999,
                        }
                    },
                },
            },
            {
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {
                        "total_token_usage": {
                            "input_tokens": 1099,
                            "cached_input_tokens": 999,
                        },
                        "last_token_usage": {
                            "input_tokens": 100,
                            "cached_input_tokens": 0,
                        },
                    },
                },
            },
        ],
    )

    normalized = usage_capture.get_normalizer("codex").parse(transcript)

    assert normalized.eligible_turns == [_turn(100, 0)]


def test_UC_11_FR_K5_cache_hygiene_is_bounded_and_measurement_first():
    convention = (_ROOT / "factory/rulebooks/conventions/cache-hygiene.md").read_text(
        encoding="utf-8"
    )

    assert "bounded" in convention
    assert "on demand" in convention
    assert "provider" in convention
    assert "prose-only" in convention
    assert "restabilisation" in convention


def test_UC_11_FR_K7_retrospective_consumes_signals_only_as_friction_evidence():
    guidance = (_ROOT / "factory/skills/retrospective/SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "Caused Friction" in guidance
    assert "cache_miss_turns" in guidance
    assert "cache_miss_input_tokens" in guidance
    assert "late_early_input_ratio" in guidance
    assert "live budget gate" in guidance
