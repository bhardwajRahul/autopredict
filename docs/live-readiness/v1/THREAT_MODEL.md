# Live boundary threat model v1

## Assets

- User funds and venue positions
- API credentials and signing keys
- Durable shadow state and evidence integrity
- Operator understanding of whether a capability is approved

## Trust boundaries and threats

| Boundary | Threat | Required v1 control |
|---|---|---|
| CLI/config | A live flag or complete credentials are mistaken for authorization | Every live command/config audit fails closed |
| Direct Python | Callers disable checks, skip confirmation, inject an adapter, or bypass `__init__` | Constructor, public method, and former internal submit helper each reject independently |
| Venue adapter | A caller invokes place/submit/cancel or obtains the raw authenticated client | Reject before credential validation, market lookup, client construction, or injected-client access |
| Packaging | Source behavior differs from an installed wheel | CI installs the wheel outside the checkout and repeats direct-import bypass checks |
| Documentation | Paper/shadow controls are represented as proof of live readiness | Versioned NO-GO report names missing evidence and authorization |
| Shadow runtime | Live capability is imported into the credential-free simulator | Shadow import isolation and no-network mutation tests remain mandatory |

## Out of scope

This version does not design a future live system or claim venue, custody, regulatory,
financial, or operational approval. A later project must produce its own threat model
covering key custody, venue authentication, reconciliation, external monitoring,
manual intervention, incident handling, and capital limits.
