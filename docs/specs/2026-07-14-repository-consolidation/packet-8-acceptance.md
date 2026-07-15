# Packet 8 / issue #11 acceptance mapping

| Acceptance requirement | Implementation | Evidence |
|---|---|---|
| Live remains unavailable | Process-wide guard plus minimized runner | `autopredict/safety.py`, `scripts/run_live.py` |
| Direct Python bypasses fail | Constructor, place, internal submit, adapter mutation, and raw client paths reject | `tests/test_trader.py`, `tests/test_polymarket_adapter.py` |
| Flags and injected adapters cannot bypass | Guard runs before argument/adapter inspection | Parameterized and untouchable-adapter tests |
| Credentials do not imply readiness | Live-config audit is always NO-GO | `tests/test_safety_audit.py` |
| Installed artifact matches source | Wheel installed outside checkout and bypass probes repeated | `.github/workflows/tests.yml` package job |
| Public read-only and shadow remain available | No changes to public scanner or shadow engine | Existing live-scan and shadow suites |
| Evidence is not fabricated | Versioned report explicitly records missing seven-day run and authorization | `docs/live-readiness/v1/` |
| Operations/security are explicit | Threat model, disabled-live runbook, and security policy | `THREAT_MODEL.md`, `RUNBOOK.md`, `SECURITY.md` |

Packet 8 records a **NO-GO** decision. Issue #11 is satisfied only as a safety-boundary
implementation; it does not authorize live enablement.
