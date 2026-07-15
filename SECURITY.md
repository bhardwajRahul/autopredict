# Security policy

## Supported security boundary

AutoPredict supports credential-free offline evaluation, public read-only market
scanning, recording/replay, and shadow execution. Live order submission and venue
cancellation are not supported and are hard-disabled at command, direct Python, and
Polymarket adapter boundaries.

Do not provision trading credentials to AutoPredict. Credential presence is never a
readiness signal. A live-mode safety audit must return NO-GO even when all expected
environment variables are populated.

## Report a vulnerability

Report any path that reaches an authenticated client, submits/cancels an order, or
causes the safety audit to pass a live configuration as a security vulnerability.
Avoid including private keys, API secrets, real account identifiers, or production
captures in an issue. Use GitHub's private vulnerability reporting channel when it is
enabled for the repository; otherwise contact the maintainers privately before public
disclosure.

The current decision and scope are documented in
[docs/live-readiness/v1/NO_GO.md](docs/live-readiness/v1/NO_GO.md).
