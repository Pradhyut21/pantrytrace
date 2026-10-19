# Architecture and decision contract

PantryTrace separates evidence collection from operational approval. Its current controller uses deterministic tool selection; a future model may suggest a tool or interpretation but cannot invent source rows or change the approval policy.

## Current workflow

1. Load one bounded fixture recall and its stock source. Preserve raw source identifiers and timestamps.
2. Resolve exact product identity or explicitly registered supplier aliases. Similar names alone cannot establish a definitive match.
3. Draft a finding using the available lot scope. The evaluator checks whether the source supports the proposed label.
4. If the lot is missing, retrieve the linked intake evidence and reevaluate. Conflicts remain visible and become human-review findings. Retries have a fixed bound.
5. Join transfer context by stable row identifiers. Draft internal location tasks with evidence; never send notifications or mutate stock.
6. Export the findings, evidence, task drafts, trace and validation information as JSON.

`run_case()` is synthetic fixture mode. `run_connected_records()` accepts explicit caller-supplied records without falling back to fixture sources. Caller-supplied data does not establish live Zetaris integration. A future connected runner must record actual provider execution and data provenance before using that label.

## Evidence and state

Each supported decision references existing source IDs and fields. The trace records selected tools, observations, evaluator feedback and result revisions. It is execution evidence, not hidden model chain of thought. The shared evidence state exists for one investigation; optional Meterless H-MEM can persist selected evidence with provenance between sessions.

The Meterless integration exposes `remember`, `recall`, `audit`, and `feedback` through the official local H-MEM reference engine. Retrieved memory is context, not an authoritative source. A cached memory cannot override a conflicting source record or grant clearance. The Zetaris adapter uses an explicit table allowlist and read-only SQL. An unavailable sponsor does not silently become fixture mode in a claimed live run.

## Decision meanings

| JSON status | UI meaning | Required treatment |
|---|---|---|
| `quarantine` | Propose quarantine for matching stock | Draft internal task, evidence attached, human approval required |
| `review` | Missing, conflicting or insufficient evidence | Explain the unresolved question; no release or definitive scope claim |
| `clear` | Outside this specific recall's demonstrated scope | Record the exclusion evidence; never claim general food safety |

## Operational boundaries

The local HTTP server binds to `127.0.0.1`, serves an explicit static asset allowlist, rejects oversized inputs and cross-origin run requests, and exposes no API keys. UI text uses text nodes so data cannot inject HTML. It has no authentication and is not a production deployment server.

Current fixture evaluation proves regression behavior only. It cannot establish performance on unknown suppliers, arbitrary free-text lot ranges, mixed units, real recalls, or production transfer graphs. Quantity reconciliation and traceability must be validated against the real source schema before a pilot.
