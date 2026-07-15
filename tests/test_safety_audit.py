"""Tests for production safety audit checks."""

from __future__ import annotations

from pathlib import Path

import pytest

from autopredict.cli import main as cli_main
from autopredict.live.safety_audit import run_safety_audit


def test_safety_audit_passes_without_live_config() -> None:
    result = run_safety_audit()

    assert result.passed is True
    assert result.checks["explicit_data_required"] is True
    assert result.checks["default_domain_models_are_no_edge"] is True
    assert result.checks["live_execution_request_allowed"] is True
    assert result.metadata["live_execution_capability_enabled"] is False


def test_installed_live_entrypoint_is_not_published() -> None:
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"

    assert "autopredict-live" not in pyproject.read_text(encoding="utf-8")


def test_primary_cli_live_trade_command_remains_disabled(monkeypatch) -> None:
    def unexpected_defaults_load():
        raise AssertionError("disabled live command loaded configuration")

    monkeypatch.setattr("autopredict.cli._load_defaults", unexpected_defaults_load)
    monkeypatch.setattr("sys.argv", ["autopredict", "trade-live"])

    with pytest.raises(SystemExit, match="trade-live is disabled"):
        cli_main()


def test_safety_audit_blocks_live_config_with_missing_env(
    tmp_path: Path,
    monkeypatch,
) -> None:
    for env_name in (
        "POLYMARKET_API_KEY",
        "POLYMARKET_API_SECRET",
        "POLYMARKET_API_PASSPHRASE",
        "POLYMARKET_PRIVATE_KEY",
        "POLYMARKET_FUNDER",
    ):
        monkeypatch.delenv(env_name, raising=False)
    config = tmp_path / "live.yaml"
    config.write_text(
        "venue:\n" "  mode: live\n" "  api_key: ${POLYMARKET_API_KEY}\n",
        encoding="utf-8",
    )

    result = run_safety_audit(config)

    assert result.passed is False
    assert result.checks["live_credentials_present"] is False
    assert result.metadata["missing_env_vars"] == [
        "POLYMARKET_API_KEY",
        "POLYMARKET_API_PASSPHRASE",
        "POLYMARKET_API_SECRET",
        "POLYMARKET_FUNDER",
        "POLYMARKET_PRIVATE_KEY",
    ]


def test_safety_audit_requires_all_polymarket_trading_credentials(
    tmp_path: Path,
    monkeypatch,
) -> None:
    for env_name in (
        "POLYMARKET_API_KEY",
        "POLYMARKET_API_SECRET",
        "POLYMARKET_API_PASSPHRASE",
        "POLYMARKET_PRIVATE_KEY",
        "POLYMARKET_FUNDER",
    ):
        monkeypatch.delenv(env_name, raising=False)
    config = tmp_path / "live.yaml"
    config.write_text(
        "venue:\n"
        "  name: polymarket\n"
        "  mode: live\n"
        "  api_key: ${POLYMARKET_API_KEY}\n"
        "  api_secret: ${POLYMARKET_API_SECRET}\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("POLYMARKET_API_KEY", "key")
    monkeypatch.setenv("POLYMARKET_API_SECRET", "secret")

    result = run_safety_audit(config)

    assert result.passed is False
    assert result.metadata["missing_env_vars"] == [
        "POLYMARKET_API_PASSPHRASE",
        "POLYMARKET_FUNDER",
        "POLYMARKET_PRIVATE_KEY",
    ]


def test_safety_audit_rejects_live_config_even_when_credentials_are_present(
    tmp_path: Path,
    monkeypatch,
) -> None:
    for env_name in (
        "POLYMARKET_API_KEY",
        "POLYMARKET_API_SECRET",
        "POLYMARKET_API_PASSPHRASE",
        "POLYMARKET_PRIVATE_KEY",
        "POLYMARKET_FUNDER",
    ):
        monkeypatch.delenv(env_name, raising=False)
    config = tmp_path / "live.yaml"
    config.write_text(
        "venue:\n"
        "  name: polymarket\n"
        "  mode: live\n"
        "  api_key: ${POLYMARKET_API_KEY}\n"
        "  api_secret: ${POLYMARKET_API_SECRET}\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("POLYMARKET_API_KEY", "key")
    monkeypatch.setenv("POLYMARKET_API_SECRET", "secret")
    monkeypatch.setenv("POLYMARKET_API_PASSPHRASE", "passphrase")
    monkeypatch.setenv("POLYMARKET_PRIVATE_KEY", "private-key")
    monkeypatch.setenv("POLYMARKET_FUNDER", "0xfunder")

    result = run_safety_audit(config)

    assert result.passed is False
    assert result.checks["live_credentials_present"] is True
    assert result.checks["live_execution_request_allowed"] is False
    assert result.metadata["live_execution_capability_enabled"] is False
    assert result.metadata["missing_env_vars"] == []
    assert any(
        "credentials and configuration cannot make it ready" in item for item in result.findings
    )
