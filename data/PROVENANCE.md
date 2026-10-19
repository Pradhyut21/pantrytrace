# Synthetic fixture provenance

All products, identifiers, lots, organizations, inventory, receipts, supplier aliases,
transfers, quantities, timestamps, and the recall in this directory are invented for
this pre-event prototype. They were authored as deterministic test fixtures on
2026-10-19. None is an FDA record or a real supplier record. The fixed historical
exercise snapshot is **2026-09-16T12:00:00Z**. No ongoing recall status is inferred.

The fixture deliberately contains a malicious supplier note, a missing lot, a
supplier alias, contradictory receipts, a similar-name different product, and an
unidentified item. These are test inputs, not commands or assertions of food safety.

`recall.json` and `inventory.json` exercise the JSON adapter.
`supplier_aliases.csv` and `transfers.csv` exercise CSV adapters.
`intake_ledger.csv` seeds an in-memory SQLite database; parameterized SELECTs exercise
the SQL adapter. The seed is not presented as an independent corroborating source.
Source IDs identify fixture records and are carried into every decision's evidence.

All proposed actions are internal human-review drafts. A `clear` decision means only
that explicit identity/lot evidence does not match this one synthetic recall. It is
never a safe-to-eat decision, a public alert, or a statement about recall lifecycle.

Inventory quantities represent current on-hand units. Intake receipt quantities
represent received units; receipt reconciliation adds the item's deduplicated
direct outbound transfers to its current stock. The transfer adapter supports one
outgoing hop only. Explicit parent-linked or multi-hop records, conflicting stable
IDs, and invalid quantities force review and leave outbound totals unresolved.
The system does not claim a complete transfer graph or global stock conservation.

The MVP requires one distinct product identifier per recall scope and an explicit
list of affected alphanumeric lot tokens (1–64 characters). Multiple products,
lot ranges, wildcards, spaces, punctuation, or placeholder values require review.
Even a real hyphenated lot is outside this deliberately narrow parser. Notices
must be manually split into verified product-lot scopes before use; the engine
does not infer a Cartesian product of independent product and lot lists.
