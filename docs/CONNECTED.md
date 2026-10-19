# Connect actual sponsor data

The web workbench intentionally runs synthetic fixtures. The connected CLI is a separate, explicit execution path and has not been run against a real Zetaris instance.

## Required setup

1. Obtain the assigned instance URL, numeric organization ID, bearer API key, team namespace and view permissions from HackOS. Keep secrets in your shell or local secret manager. The application does not read `.env` automatically.
2. Follow the official [Zetaris connection guide](https://github.com/zetaris/getting-started/blob/main/docs/connections/README.md). Register the independent sources through supported connectors and expose read-only, investigation-scoped views. The exact source registration and federation view syntax depends on the assigned instance; verify it in its current OpenAPI documentation and sponsor resources.
3. Preserve the field names below. Each view must contain only the bounded investigation under review. The prototype supports one product identifier per notice and explicit alphanumeric lot tokens; it does not parse arbitrary notice prose or lot ranges.
4. Install the local Meterless runtime with `npm ci`. The vendored official engine is pinned and attributed. Keep one CLI writer per memory directory; the reference's JSON persistence is not a concurrent database.

## View schemas

| View | Required fields |
|---|---|
| Recall | Exactly one row: `recall_id`, `affected_gtins`, `affected_lots`; include `as_of`, `source_id`, original notice URL and provenance. The two affected columns must be actual arrays or JSON array strings, never comma-separated prose. |
| Inventory | `item_id`, `product`, `gtin`, `lot`, `units`, `location`, `intake_batch`, `supplier_label`, `sku`; optional untrusted `supplier_note` |
| Intake | `record_id`, `intake_batch`, `supplier_id`, `sku`, `gtin`, `lot`, `units`, `document_id` |
| Aliases | `source_id`, `alias`, `supplier_id` |
| Transfers | `transfer_id`, `item_id`, `destination`, `units`, `transferred_at`, `receipt_id`; only one outgoing hop is supported |

`units` is an explicit whole-number quantity in the same unit across the relevant records. The runner converts only integer strings; it does not infer cases-to-cans conversions. Inventory quantities mean on hand. Intake quantity must reconcile with on-hand stock plus deduplicated direct outbound transfers. Empty rows are not replaced by sample data.

## Run

In PowerShell, set the actual `ZETARIS_REST_URL`, `ZETARIS_API_KEY`, `ZETARIS_ORG_ID` and comma-separated `ZETARIS_ALLOWED_TABLES` environment variables. Do not paste keys into documentation, screenshots or commits. The names below are placeholders for views you registered:

```powershell
python scripts/run_connected.py --recall-view TEAM.recall --inventory-view TEAM.inventory --intake-view TEAM.intake_ledger --aliases-view TEAM.supplier_aliases --transfers-view TEAM.transfers --output artifacts/local-connected.json
```

The command executes actual read-only Zetaris queries, records view names/counts/retrieval times, and supplies explicit data to the engine. It stops on errors or a potentially truncated result. It uses the real Meterless engine to consult context, persist source-linked findings and verify the audit ledger. No output claims successful sponsor execution until those calls actually complete.

The current runner eagerly fetches the scoped views, then performs dynamic record retrieval from the resulting local SQL/CSV adapters. It does not yet push every critic-requested lookup back to Zetaris. That deeper federation and source-selection work is a concrete eligible-window improvement. A successful fetch does not establish that the registered views themselves span independent sources; capture their actual source mapping and query plan as additional evidence.

`--nvidia-critique` explicitly sends the decision evidence to the configured NVIDIA endpoint. Only use it with data you are authorized to send. Its output is advisory and cannot change the deterministic scope checks. No authenticated NVIDIA call has been executed for this preparation package.

## Evidence for the final demo

Capture the registered-source mapping, a real query receipt with secrets removed, the connected investigation trace, Meterless memory/audit records, and the generated task draft. Report the exact model and actual Cursor changes. Do not present mocked adapter tests, local SQLite, or caller-supplied records as proof of live federation.
