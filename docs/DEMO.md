# PantryTrace demo guide

A short path through the working prototype for judges and reviewers. Run `python -m pantrytrace serve` from the repository and open **http://127.0.0.1:8765**.

This guide and the recorded footage describe the **19-20 October pre-event preparation snapshot**, using invented records. Live Zetaris federation, Nemotron inference and actual Cursor development evidence remain pending; the [readiness checklist](SUBMISSION_READINESS.md) is the current submission gate.

## A 90-second walkthrough

| Time | Show | Point to make |
| --- | --- | --- |
| 0:00-0:10 | The recall workbench and its fixture labels. | A notice alone does not identify which donated stock and partner locations need attention. |
| 0:10-0:35 | Select **Missing lot - retrieve intake record**, then **Investigate recall**. Inspect the decision register and evidence panel. | The inventory line lacks a lot. The evaluator requests the intake receipt; the second pass resolves 30 on-hand units using structured product and lot evidence. |
| 0:35-0:50 | Read the investigation trace and source references. | The retry is an actual deterministic execution trace. It records the missing evidence, retrieval and revised finding. Six transferred units remain visible as transfer context. |
| 0:50-1:10 | Select **Conflicting records - escalate** and run again. | Conflicting receipts keep 18 units in human review. The system asks for better evidence instead of forcing a definitive finding. |
| 1:10-1:25 | Click **Export evidence packet** and inspect the JSON. | This is a reviewable work product: source-linked findings, execution trace and internal task drafts. A person approves operational actions. |
| 1:25-1:30 | State the tested scope. | The prototype uses synthetic fixtures; local Meterless memory is verified separately through its CLI. Live sponsor integration and eligible-window work are still to come. |

The sequence can be extended to the submission's final 1-4 minute demo after connected-source and runtime proof are available.

## Other cases to inspect

| UI case | CLI scenario | Expected fixture behavior |
| --- | --- | --- |
| Exact lot - direct match | `exact` | 48 units proposed for quarantine; explicit identity and lot checks establish exclusions. |
| Missing lot - retrieve intake record | `ambiguous` | Two evaluation passes; 30 on-hand units resolved, 12 outside this recall, six transferred units under review. |
| Conflicting records - escalate | `conflict` | Two passes; 18 units remain in human review. |
| Similar product - different scope | `out_of_scope` | 42 units outside this fixture's recall scope; eight remain unverified. |

These outcomes are fixture expectations, not findings about actual food or suppliers. The JSON status `clear` is retained for compatibility and means **outside this specific recall's demonstrated scope**.

## Verify the supporting evidence

From the project directory:

```sh
python -m pantrytrace evaluate
python -m pantrytrace demo --scenario ambiguous --output artifacts/ambiguous.json --packet artifacts/action-packet.json
```

The evaluation contains nine authored development items: inventory-only baseline **8/9**, retrieval loop **9/9**. It is not held-out validation. See the checked-in [evaluation](../artifacts/evaluation.json) and [validation notes](validation.md).

To verify actual local Meterless behavior separately, install Node.js, then run:

```sh
npm ci
python -m pantrytrace sponsor-smoke
python -m pantrytrace demo --scenario ambiguous --memory
```

That path exercises the vendored official H-MEM engine; the standard web demo does not silently invoke it. The [smoke receipt](../artifacts/meterless-smoke.json) describes local persistence, cross-process recall, audit and feedback, with zero remote API calls.

## Recorded assets

- [1:56 preparation walkthrough on Google Drive](https://drive.google.com/file/d/1A3MebeBEs_cJHzJBYgj1wZ6Pcby7npV8/view?usp=drivesdk), also available as a [repository MP4](media/pantrytrace-walkthrough.mp4).
- [24-second brag teaser](media/pantrytrace-brag.mp4).
- [Pitch deck PDF](pitch/pantrytrace-pitch.pdf).
- [Music, assets and licensing credits](media/MEDIA-CREDITS.md).

The Drive walkthrough has been verified as viewable by anyone with the link. The teaser is separate from the full submission walkthrough. Both recordings need fresh connected-source, runtime and eligible-window evidence before they represent the final entry.

For live-source setup, use [CONNECTED.md](CONNECTED.md). For the event disclosure and new-work plan, read [PREEXISTING.md](../PREEXISTING.md) and [SUBMISSION_READINESS.md](SUBMISSION_READINESS.md).
