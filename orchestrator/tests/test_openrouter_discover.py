"""Tests for `factory/scripts/openrouter-discover`.

openrouter-discover is an operator aid off the runtime path (ADR-0005): it
curates and validates the `pi.*` OpenRouter rows in model.conf. These tests
exercise the pure catalog helpers and the three command modes against a fixture
catalog served over a `file://` URL — the script's `--url` override — so no
network is touched. The script is extensionless and loaded via importlib.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "factory" / "scripts" / "openrouter-discover"
_loader = SourceFileLoader("openrouter_discover", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("openrouter_discover", _loader)
ord_mod = importlib.util.module_from_spec(_spec)
sys.modules["openrouter_discover"] = ord_mod
_loader.exec_module(ord_mod)


def _model(mid, prompt, ctx=64000, out_modalities=("text",)):
    return {
        "id": mid,
        "pricing": {"prompt": prompt},
        "context_length": ctx,
        "architecture": {"output_modalities": list(out_modalities)},
    }


CATALOG = [
    _model("anthropic/claude-haiku-4.5", "0.0000008"),
    _model("anthropic/claude-sonnet-4.6", "0.000003"),
    _model("anthropic/claude-opus-4.8", "0.000015"),
    _model("some/free-model", "0.0"),
    _model("some/tiny-context", "0.000001", ctx=8000),
    _model("some/image-generator", "0.000002", out_modalities=("image",)),
]


def _catalog_url(tmp_path: Path, data=CATALOG) -> str:
    payload = tmp_path / "catalog.json"
    payload.write_text(json.dumps({"data": data}), encoding="utf-8")
    return payload.as_uri()


class TestCatalogHelpers:
    def test_prompt_price_parses(self):
        assert ord_mod.prompt_price(_model("x", "0.000003")) == 3e-6

    def test_prompt_price_unparseable_is_none(self):
        assert ord_mod.prompt_price({"pricing": {"prompt": "n/a"}}) is None
        assert ord_mod.prompt_price({}) is None

    def test_is_text_chat_excludes_image_only(self):
        assert ord_mod.is_text_chat(_model("x", "1", out_modalities=("text",)))
        assert not ord_mod.is_text_chat(_model("x", "1", out_modalities=("image",)))

    def test_is_text_chat_defaults_true_without_modalities(self):
        assert ord_mod.is_text_chat({"id": "x"})

    def test_usable_applies_context_and_modality_filters(self):
        assert ord_mod.usable(_model("x", "1", ctx=64000), 32000)
        assert not ord_mod.usable(_model("x", "1", ctx=8000), 32000)
        assert not ord_mod.usable(_model("x", "1", out_modalities=("image",)), 32000)

    def test_ranked_sorts_by_price_and_drops_low_context(self):
        rows = ord_mod.ranked(CATALOG, min_context=32000, max_price=None)
        ids = [m["id"] for m in rows]
        # tiny-context (8k) and image-generator are filtered out.
        assert "some/tiny-context" not in ids
        assert "some/image-generator" not in ids
        # sorted ascending by prompt price; free model (0.0) sorts first.
        prices = [ord_mod.prompt_price(m) for m in rows]
        assert prices == sorted(prices)


class TestSuggest:
    def test_suggest_picks_cheapest_median_dearest_priced(self):
        picks = ord_mod.suggest(CATALOG, min_context=32000)
        # free-model (0.0) is excluded from tier picks.
        assert picks["economy"] == "openrouter/anthropic/claude-haiku-4.5"
        assert picks["strong"] == "openrouter/anthropic/claude-opus-4.8"
        assert picks["standard"].startswith("openrouter/")


class TestCheckMode:
    def _conf(self, tmp_path: Path, models: dict[str, str]) -> Path:
        lines = ["[facts]"] + [f"pi.{t} = {m}" for t, m in models.items()]
        lines.append("on_missing = halt")
        conf = tmp_path / "model.conf"
        conf.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return conf

    def test_check_passes_when_all_rows_in_catalog(self, tmp_path, capsys):
        conf = self._conf(
            tmp_path,
            {
                "economy": "openrouter/anthropic/claude-haiku-4.5",
                "standard": "openrouter/anthropic/claude-sonnet-4.6",
                "strong": "openrouter/anthropic/claude-opus-4.8",
            },
        )
        rc = ord_mod.main(
            ["--check", "--model-conf", str(conf), "--url", _catalog_url(tmp_path)]
        )
        assert rc == 0
        assert "ok    pi.economy" in capsys.readouterr().out

    def test_check_reports_drift_and_exits_1(self, tmp_path, capsys):
        conf = self._conf(
            tmp_path,
            {"strong": "openrouter/anthropic/claude-opus-9.9-vaporware"},
        )
        rc = ord_mod.main(
            ["--check", "--model-conf", str(conf), "--url", _catalog_url(tmp_path)]
        )
        assert rc == 1
        assert "DRIFT" in capsys.readouterr().err

    def test_check_no_rows_configured_exits_0(self, tmp_path, capsys):
        conf = tmp_path / "model.conf"
        conf.write_text("[facts]\non_missing = halt\n", encoding="utf-8")
        rc = ord_mod.main(
            ["--check", "--model-conf", str(conf), "--url", _catalog_url(tmp_path)]
        )
        assert rc == 0


class TestListAndSuggestModes:
    def test_list_json_emits_ranked_rows(self, tmp_path, capsys):
        rc = ord_mod.main(["--list", "--json", "--url", _catalog_url(tmp_path)])
        assert rc == 0
        rows = json.loads(capsys.readouterr().out)
        assert rows[0]["id"] == "some/free-model"  # cheapest first
        assert all("prompt_price" in r for r in rows)

    def test_suggest_emits_all_three_tiers(self, tmp_path, capsys):
        rc = ord_mod.main(["--suggest", "--url", _catalog_url(tmp_path)])
        assert rc == 0
        out = capsys.readouterr().out
        assert "pi.economy" in out
        assert "pi.standard" in out
        assert "pi.strong" in out


class TestFetchErrors:
    def test_unreachable_url_exits_2(self, tmp_path, capsys):
        missing = (tmp_path / "does-not-exist.json").as_uri()
        rc = ord_mod.main(["--list", "--url", missing])
        assert rc == 2
        assert "openrouter-discover:" in capsys.readouterr().err
