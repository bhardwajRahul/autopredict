"""Paper/shadow infrastructure and safety-audit helpers for AutoPredict.

The retained ``autopredict.live.trader.LiveTrader`` compatibility target always
raises, and is deliberately not exported from this public package namespace.
"""

from autopredict.core.types import ExecutionReport, Order
from .risk import RiskManager, RiskCheckResult
from .monitor import Monitor, TradeLog, DecisionLog
from .safety_audit import SafetyAuditResult, run_safety_audit

__all__ = [
    "PaperTrader",
    "ExecutionReport",
    "Order",
    "RiskManager",
    "RiskCheckResult",
    "Monitor",
    "TradeLog",
    "DecisionLog",
    "SafetyAuditResult",
    "run_safety_audit",
]


def __getattr__(name: str):
    """Keep legacy trader imports lazy so shadow imports have no live capability."""

    if name == "PaperTrader":
        from .trader import PaperTrader

        return PaperTrader
    raise AttributeError(name)
