# Submission materials

These texts describe the **current declared pre-event prototype**. Update them after the eligible-window build; do not claim pending sponsor work is complete.

## Primary track

**Solving Fragmented Intelligence**. No existing team submission occupies a track, according to the user. The track has not been selected on HackOS by this project.

## Project title

**PantryTrace: Every Recall Decision Needs a Receipt**

## Description (150–2000 characters)

PantryTrace helps food-bank coordinators answer a practical question: which stock and partner locations need investigation after a recall notice?

Donation receipts, inventory sheets and transfer logs often describe the same product differently. PantryTrace links these records while checking product identity separately from lot eligibility. When a lot is missing, its evaluator rejects the unsupported conclusion, requests the intake record and revises the finding. Conflicting records stay in human review. Every decision links to its source evidence.

The working local prototype includes four synthetic scenarios, an inspectable planner/executor/evaluator loop, transfer context, regression evaluation and downloadable internal task drafts. It treats instruction-like supplier notes as untrusted data and performs no external operational actions.

The actual Meterless H-MEM engine persists and retrieves source-linked investigation context with an audit ledger. A documented, tested Zetaris REST adapter and connected-record runner are prepared; live instance validation remains pending. NVIDIA critique is optional and unverified. Actual Cursor development must be documented during the build.

This snapshot was prepared before the event and must be declared as pre-existing. The eligible-window work will add verified federation, substantive agent improvements and fresh evaluation evidence. Results are internal triage support, never a declaration that food is safe.

## Idea proposal (200–300 words)

When a recall arrives, a food-bank coordinator still has to determine whether donated cartons match the affected product, which lots remain on shelves, and which partner agencies received transfers. The evidence lives in donation receipts, stock sheets and movement logs. A missing lot number can turn a simple lookup into a manual investigation.

PantryTrace turns that fragmented evidence into an internal review packet. It checks product identity separately from lot scope, follows documented transfers and attaches source references to each finding. Its planner selects the next source to inspect. An evaluator challenges unsupported conclusions and sends missing evidence back for retrieval. Conflicting receipts produce a specific question for a person instead of a confident guess.

The current prototype demonstrates this loop on four synthetic scenarios, including an ambiguous batch that resolves after receipt retrieval and a contradictory batch that remains in review. It exports draft location tasks without sending messages or changing inventory. Tests cover unknown identifiers, incomplete recall scope and hostile instructions inside supplier notes.

Meterless H-MEM provides real local persistence, retrieval and provenance audit. The eligible build will connect registered sources through Zetaris, document actual Cursor development and evaluate whether NVIDIA model critique improves the investigation. A small inventory-only baseline makes the contribution of additional evidence visible.

The proposed value is less manual evidence assembly for pantry networks with inconsistent records. That value remains a hypothesis until operators test it. Pre-event code, data and media will be declared, and the final demo will distinguish verified sponsor execution from local fixtures. PantryTrace supports accountable decisions while preserving uncertainty wherever the evidence is incomplete.

## Upload fields

| Form field | Prepared asset / required action |
|---|---|
| Team name | HackOS supplies your real team name; no invented name is inserted |
| Track | Solving Fragmented Intelligence, subject to full challenge/rules confirmation |
| Description | Copy the description above after updating completion claims |
| Demo video | `../../video/pantrytrace-walkthrough.mp4` is the preparation walkthrough. Refresh sponsor footage and upload the final 1–4 minute version with judge-accessible permissions |
| GitHub solution | Local repository only. Publish under your own account and paste the real URL |
| Pitch deck | `../../pantrytrace-pitch.pdf` is the preparation deck. Refresh its status slide, then upload if the form accepts PDF or share the deck |
| Pre-existing components | Use `../PREEXISTING.md` and the actual pre-event snapshot commit |

## Pitch and demo sequence

Lead with the missing lot, run the investigation, show the critic's request, inspect the receipt that changes the decision, show a transfer task and export the packet. Then run the conflicting case and show why it remains unresolved. Finish with a real sponsor execution receipt and the benchmark's exact sample size. The 24-second `brag` clip is a separate shareable teaser, shorter than the submission's required walkthrough.
