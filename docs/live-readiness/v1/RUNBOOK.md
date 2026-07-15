# Disabled-live operator runbook v1

## Supported operations

Use only credential-free surfaces:

```bash
autopredict scan-live --limit 20 --top 5
autopredict shadow run --config /path/to/shadow.yaml
autopredict shadow status --state /path/to/autopredict.db
autopredict safety-audit --config /path/to/config.yaml
```

For a shadow incident, stop the process and latch the simulated cancel-all breaker:

```bash
autopredict shadow cancel-all \
  --state /path/to/autopredict.db \
  --reason "operator stop: describe the incident"
```

Preserve the SQLite state, capture manifest, logs, configuration, package version, and
command output before investigation. Reset only after reconciliation succeeds and the
public feed is fresh.

## If a live path appears reachable

1. Do not add credentials and do not test against a real or testnet account.
2. Stop the process and preserve the exact command/import path and package hash.
3. Confirm that the expected result is `LiveExecutionDisabledError` or a fail-closed
   CLI exit.
4. Report the bypass privately as described in `SECURITY.md`.
5. Do not weaken another boundary as a workaround.

There is no AutoPredict live-order emergency runbook because there is no approved live
runtime. Any real venue account must be managed through the venue's independently
authorized operator procedures, outside AutoPredict.
