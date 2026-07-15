# Live-readiness decision v1: NO-GO

- Decision date: 2026-07-14
- Decision: **NO-GO**
- Scope: AutoPredict live order submission and venue cancellation
- Evidence manifest schema: `autopredict.live-readiness-evidence.v1`

AutoPredict is not live-ready. This is a product capability decision, not a default
configuration: credentials, confirmation flags, injected adapters, direct imports,
and installed-wheel usage cannot enable live mutations.

## Evidence status

The following prerequisites are missing and must not be inferred from unit tests:

- A continuous seven-day clean shadow run using representative, real point-in-time
  public inputs, with no unresolved breaker, reconciliation, replay-determinism,
  stale-feed, duplicate-intent, partial-fill, or risk-accounting exceptions.
- A separately scoped and human-authorized live-enablement project with named owners,
  independent security and operational review, venue-specific reconciliation design,
  credential lifecycle controls, incident response, and an explicit capital-at-risk
  decision.

No seven-day evidence bundle or human authorization is included in this repository.
Tests demonstrate fail-closed behavior and shadow invariants only; they do not count as
production evidence.

## Enforced release boundary

- No `autopredict-live` installed command.
- `autopredict trade-live` and `scripts/run_live.py` always exit before configuration.
- `autopredict.live.trader.LiveTrader` construction and order paths always raise.
- Polymarket place, submit, cancel, and authenticated-client retrieval always raise
  before credentials or clients are accessed.
- `autopredict safety-audit --config ...` cannot pass a live-mode configuration.
- Public Gamma/CLOB scanning and credential-free shadow execution remain available.

## Reassessment

Do not edit a boolean or weaken a guard to reassess this decision. Create a new,
human-authorized project and a new versioned report. Preserve v1 as historical evidence.
Use the [evidence template](evidence-manifest.template.json),
[threat model](THREAT_MODEL.md), and [runbook](RUNBOOK.md) as minimum inputs.
