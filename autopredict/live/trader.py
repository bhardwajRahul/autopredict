"""Paper execution and a retained, hard-disabled live compatibility class.

Paper trading simulates execution without real capital.
Live order execution is unavailable in this release.
"""

from __future__ import annotations

import random
from datetime import datetime
from typing import Any, Protocol

from autopredict.core.types import ExecutionReport, Order
from autopredict.safety import reject_live_execution


class VenueAdapter(Protocol):
    """Protocol for venue API adapters.

    Defines the interface that venue-specific adapters must implement.
    """

    def submit_order(self, order: Order) -> ExecutionReport:
        """Submit order to venue and get execution report."""
        ...

    def get_order_book(self, market_id: str) -> dict[str, Any]:
        """Get current order book for market."""
        ...

    def get_position(self, market_id: str) -> float:
        """Get current position size for market."""
        ...


class PaperTrader:
    """Simulated trading with no real capital.

    Paper trader simulates order execution using current order book data.
    All fills are simulated - no real money is at risk.

    Example:
        >>> trader = PaperTrader(commission_rate=0.01)
        >>> order = Order(
        ...     market_id="test-market",
        ...     side="buy",
        ...     order_type="market",
        ...     size=100.0
        ... )
        >>> report = trader.place_order(order, current_price=0.55)
        >>> print(f"Filled at {report.fill_price} (paper mode)")
    """

    def __init__(
        self,
        commission_rate: float = 0.01,
        slippage_bps: float = 5.0,
        limit_fill_rate: float = 0.4,
        seed: int | None = 42,
    ):
        """Initialize paper trader.

        Args:
            commission_rate: Commission as decimal (e.g., 0.01 for 1%)
            slippage_bps: Average slippage in basis points for market orders
            limit_fill_rate: Probability of limit order fills (0-1)
            seed: Optional random seed for deterministic paper fills
        """
        self.commission_rate = commission_rate
        self.slippage_bps = slippage_bps
        self.limit_fill_rate = limit_fill_rate
        self.seed = seed
        self._rng = random.Random(seed)
        self.trade_history: list[ExecutionReport] = []
        self.positions: dict[str, float] = {}

    def place_order(
        self,
        order: Order,
        current_price: float,
        order_book: dict[str, Any] | None = None,
    ) -> ExecutionReport:
        """Execute order in paper trading mode.

        Args:
            order: Order to execute
            current_price: Current market price
            order_book: Optional order book for realistic simulation

        Returns:
            Execution report with simulated fill
        """
        order.validate()

        # Simulate market order
        if order.order_type == "market":
            return self._execute_market_order(order, current_price)

        # Simulate limit order
        else:
            return self._execute_limit_order(order, current_price)

    def _execute_market_order(self, order: Order, current_price: float) -> ExecutionReport:
        """Simulate market order execution with slippage."""
        # Add slippage (basis points)
        slippage_factor = self.slippage_bps / 10000.0

        if order.side == "buy":
            # Slippage increases price for buys
            fill_price = current_price * (1 + slippage_factor)
        else:
            # Slippage decreases price for sells
            fill_price = current_price * (1 - slippage_factor)

        # Clamp to valid range for binary markets
        fill_price = max(0.01, min(0.99, fill_price))

        # Calculate commission
        commission = order.size * self.commission_rate

        # Update position tracking
        position_delta = order.size if order.side == "buy" else -order.size
        self.positions[order.market_id] = self.positions.get(order.market_id, 0.0) + position_delta

        report = ExecutionReport(
            order=order,
            filled_size=order.size,
            avg_fill_price=fill_price,
            timestamp=datetime.now(),
            fee_total=commission,
            slippage_bps=self.slippage_bps,
            execution_mode="paper",
        )

        self.trade_history.append(report)
        return report

    def _execute_limit_order(self, order: Order, current_price: float) -> ExecutionReport:
        """Simulate limit order execution with probabilistic fills."""
        # Check if limit order would be immediately executable
        if order.limit_price is None:
            raise ValueError("limit_price required for limit orders")

        is_executable = (order.side == "buy" and order.limit_price >= current_price) or (
            order.side == "sell" and order.limit_price <= current_price
        )

        # Probabilistic fill based on limit_fill_rate
        filled = is_executable or (self._rng.random() < self.limit_fill_rate)

        if not filled:
            return ExecutionReport(
                order=order,
                filled_size=0.0,
                avg_fill_price=None,
                execution_mode="paper",
                metadata={"reason": "limit_not_filled"},
            )

        # Use limit price as fill price (best case)
        fill_price = order.limit_price
        commission = order.size * self.commission_rate

        # Update position tracking
        position_delta = order.size if order.side == "buy" else -order.size
        self.positions[order.market_id] = self.positions.get(order.market_id, 0.0) + position_delta

        report = ExecutionReport(
            order=order,
            filled_size=order.size,
            avg_fill_price=fill_price,
            timestamp=datetime.now(),
            fee_total=commission,
            slippage_bps=0.0,  # No slippage on limit orders
            execution_mode="paper",
        )

        self.trade_history.append(report)
        return report

    def get_position(self, market_id: str) -> float:
        """Get current position for a market."""
        return self.positions.get(market_id, 0.0)

    def get_trade_history(self) -> list[ExecutionReport]:
        """Get complete trade history."""
        return self.trade_history.copy()

    def get_total_commission_paid(self) -> float:
        """Calculate total commission paid across all trades."""
        return sum(trade.fee_total for trade in self.trade_history)


class LiveTrader:
    """Retained import target whose construction and order path always fail closed.

    The parameters remain only to make old callers fail safely. Neither false safety
    flags nor an injected adapter can bypass the process-wide release boundary.
    """

    def __init__(
        self,
        venue_adapter: VenueAdapter,
        safety_checks: bool = True,
        require_confirmation: bool = True,
    ):
        """Reject construction before inspecting the adapter or either flag."""

        del self, venue_adapter, safety_checks, require_confirmation
        reject_live_execution()

    def place_order(self, order: Order) -> ExecutionReport:
        """Reject even if a caller bypassed ``__init__`` with ``__new__``."""

        del self, order
        reject_live_execution()

    def _submit_order(self, order: Order) -> ExecutionReport:
        """Reject direct calls to the former internal mutation helper."""

        del self, order
        reject_live_execution()

    def kill_switch(self, reason: str = "Manual kill switch activated") -> None:
        """Immediately halt all trading activity.

        This is the emergency stop. Once activated, no further orders can be placed.

        Args:
            reason: Reason for kill switch activation
        """
        self.is_active = False
        print("\n" + "=" * 60)
        print("KILL SWITCH ACTIVATED")
        print("=" * 60)
        print(f"Reason: {reason}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("All trading activity has been HALTED")
        print("=" * 60 + "\n")

    def get_trade_history(self) -> list[ExecutionReport]:
        """Get complete trade history."""
        return self.trade_history.copy()

    def is_trading_active(self) -> bool:
        """Check if trading is currently active."""
        return self.is_active
