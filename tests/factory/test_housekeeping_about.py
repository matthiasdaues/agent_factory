"""Tests for housekeeping-about script."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import load_script

mod = load_script("housekeeping-about")


def _write_install(base: Path, *, version: str = "0.12.0", source: str = "/src", cli: list[str] | None = None) -> None:
    af = base / ".agent-factory"
    af.mkdir(parents=True, exist_ok=True)
    data = {
        "factory_version": version,
        "factory_source": source,
        "cli": cli if cli is not None else ["claude", "copilot"],
    }
    (af / "factory-install.json").write_text(json.dumps(data), encoding="utf-8")


def _write_context(base: Path, *, status: str = "fitted", steps: dict[str, bool] | None = None) -> None:
    cfg = base / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    fitting = {
        "status": status,
        "model_matrix_configured": True,
        "fingerprint_confirmed": True,
        "agent_context_populated": True,
        "test_regime_detected": True,
        "hooks_decided": True,
    }
    if steps:
        fitting.update(steps)
    data = {"fitting": fitting}
    (cfg / "project-context.json").write_text(json.dumps(data), encoding="utf-8")


def _write_usage(base: Path) -> None:
    (base / ".agent-factory" / "usage").mkdir(parents=True, exist_ok=True)


class TestAllSourcesReadable:
    def test_complete_output(self, tmp_path: Path) -> None:
        _write_install(tmp_path)
        _write_context(tmp_path)
        _write_usage(tmp_path)

        out = mod.report(tmp_path)
        assert "Factory version: 0.12.0" in out
        assert "Factory source: /src" in out
        assert "Fitting: 5/5" in out
        assert "model matrix" in out
        assert "CLI integrations: claude, copilot" in out
        assert "Usage pipeline: healthy" in out


class TestMissingInstall:
    def test_version_unknown(self, tmp_path: Path) -> None:
        _write_context(tmp_path)
        _write_usage(tmp_path)

        out = mod.report(tmp_path)
        assert "Factory version: unknown" in out
        assert "FileNotFoundError" in out
        assert "Factory source: unknown" in out
        assert "CLI integrations: unknown" in out

    def test_other_sources_still_work(self, tmp_path: Path) -> None:
        _write_context(tmp_path)
        _write_usage(tmp_path)

        out = mod.report(tmp_path)
        assert "Fitting: 5/5" in out
        assert "Usage pipeline: healthy" in out


class TestMissingContext:
    def test_fitting_unknown(self, tmp_path: Path) -> None:
        _write_install(tmp_path)
        _write_usage(tmp_path)

        out = mod.report(tmp_path)
        assert "Fitting: unknown" in out
        assert "FileNotFoundError" in out

    def test_other_sources_still_work(self, tmp_path: Path) -> None:
        _write_install(tmp_path)
        _write_usage(tmp_path)

        out = mod.report(tmp_path)
        assert "Factory version: 0.12.0" in out
        assert "Usage pipeline: healthy" in out


class TestMissingUsage:
    def test_health_unknown(self, tmp_path: Path) -> None:
        _write_install(tmp_path)
        _write_context(tmp_path)

        out = mod.report(tmp_path)
        assert "Usage pipeline: unknown" in out
        assert "usage directory not found" in out

    def test_other_sources_still_work(self, tmp_path: Path) -> None:
        _write_install(tmp_path)
        _write_context(tmp_path)

        out = mod.report(tmp_path)
        assert "Factory version: 0.12.0" in out
        assert "Fitting: 5/5" in out


class TestAllSourcesMissing:
    def test_no_crash(self, tmp_path: Path) -> None:
        out = mod.report(tmp_path)
        assert "Factory version: unknown" in out
        assert "Fitting: unknown" in out
        assert "Usage pipeline: unknown" in out
        assert "CLI integrations: unknown" in out


class TestPartialFitting:
    def test_three_of_five(self, tmp_path: Path) -> None:
        _write_install(tmp_path)
        _write_usage(tmp_path)
        _write_context(tmp_path, steps={
            "model_matrix_configured": True,
            "fingerprint_confirmed": True,
            "agent_context_populated": True,
            "test_regime_detected": False,
            "hooks_decided": False,
        })

        out = mod.report(tmp_path)
        assert "Fitting: 3/5" in out
        assert "model matrix" in out
        assert "fingerprint" in out
        assert "agent context" in out


class TestNoCli:
    def test_empty_cli_list(self, tmp_path: Path) -> None:
        _write_install(tmp_path, cli=[])
        _write_context(tmp_path)
        _write_usage(tmp_path)

        out = mod.report(tmp_path)
        assert "CLI integrations: none" in out


class TestMainEntrypoint:
    def test_main_runs(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        _write_install(tmp_path)
        _write_context(tmp_path)
        _write_usage(tmp_path)

        mod.main(["--base-dir", str(tmp_path)])
        captured = capsys.readouterr()
        assert "Factory version: 0.12.0" in captured.out
