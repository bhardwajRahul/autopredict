"""Process-wide product safety boundaries.

This module intentionally has no configuration, credential, client, or network imports.
Callers can therefore reject disabled capabilities before touching sensitive state.
"""

from __future__ import annotations

LIVE_EXECUTION_ENABLED = False
LIVE_EXECUTION_DISABLED_MESSAGE = (
    "Live order execution is disabled in this AutoPredict release. Credentials, "
    "confirmation flags, injected adapters, and configuration cannot enable it. "
    "Use the credential-free shadow runner or read-only public market scanner."
)


class LiveExecutionDisabledError(RuntimeError):
    """Raised before any live-order capability can access credentials or a client."""


def reject_live_execution() -> None:
    """Fail closed at every retained Python mutation boundary."""

    raise LiveExecutionDisabledError(LIVE_EXECUTION_DISABLED_MESSAGE)
