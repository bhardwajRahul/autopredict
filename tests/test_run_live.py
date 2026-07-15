"""Regression tests for the minimized fail-closed live runner."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parent.parent
_RUN_LIVE_SPEC = importlib.util.spec_from_file_location(
    "autopredict_run_live_script",
    ROOT / "scripts" / "run_live.py",
)
assert _RUN_LIVE_SPEC is not None and _RUN_LIVE_SPEC.loader is not None
run_live = importlib.util.module_from_spec(_RUN_LIVE_SPEC)
sys.modules[_RUN_LIVE_SPEC.name] = run_live
_RUN_LIVE_SPEC.loader.exec_module(run_live)


def test_main_fails_closed() -> None:
    with pytest.raises(SystemExit, match="disabled in this AutoPredict release"):
        run_live.main()


def test_runner_has_no_live_runtime_imports() -> None:
    source = (ROOT / "scripts" / "run_live.py").read_text(encoding="utf-8")

    forbidden = (
        "load_config",
        "PolymarketAdapter",
        "LiveTrader",
        "py_clob_client",
        "POLYMARKET_API_KEY",
    )
    assert not any(name in source for name in forbidden)
