#!/usr/bin/env python3
"""Retained command name for a live runtime that is not shipped.

This module intentionally imports no package, configuration, credential, venue, or
trading code. It remains standalone so it fails safely from a source checkout even
when no AutoPredict distribution is installed.
"""

from __future__ import annotations

LIVE_EXECUTION_DISABLED_MESSAGE = (
    "Live order execution through supported commands is disabled in this "
    "AutoPredict release. Credentials, confirmation flags, injected adapters, "
    "and configuration cannot enable it. Use the credential-free shadow runner "
    "or read-only public market scanner."
)


def main() -> None:
    """Fail before configuration, environment, client, or adapter access."""

    raise SystemExit(LIVE_EXECUTION_DISABLED_MESSAGE)


if __name__ == "__main__":
    main()
