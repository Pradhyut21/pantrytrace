# Executed preparation checks

Checked 19 October 2026 on Windows with Python 3.13. These are observed local results, not claims about unexecuted CI platforms or live sponsor accounts.

| Check | Observed result |
|---|---|
| Python regression suite | **44 tests passed**. Includes source-scope ambiguity, placeholders, conflicts, one-hop transfer accounting, SQL parameterization, malicious source notes, provider failures, truncation and memory-policy isolation. |
| Fixture evaluation | Four authored scenarios, **nine development items**. Inventory-only baseline **8/9**; after evidence retrieval **9/9**. Same authored examples used during implementation; no held-out or real-world accuracy claim. |
| Actual Meterless engine | Pinned official H-MEM executed locally. Remember, independent-process recall, audit and feedback passed. A real investigation also persisted and retrieved successfully on repeated runs. No remote API calls. |
| Sponsor adapter tests | Official request contract exercised through mocked transports. No actual Zetaris or NVIDIA account used. |
| Desktop web workflow | Four scenarios passed at 1440 x 1050. Evidence selection and downloaded JSON packet checked. No JavaScript page errors or horizontal overflow. |
| Mobile web workflow | 390 x 844 passed without horizontal overflow. |
| HTTP boundary checks | Unknown scenario, unsupported live mode, cross-origin request, unexpected Host header and non-object JSON returned their expected errors. |
| Source syntax | Python modules compiled; browser JavaScript passed `node --check`. |
| Third-party provenance | All ten vendored H-MEM source hashes match `vendor/meterless-hmem/UPSTREAM.json`. Original license retained. |
| Pitch | Eight landscape pages rendered and visually inspected. The deck distinguishes current proof from pending sponsor work. |

## Reproduce

```powershell
python -m unittest discover -s tests -v
python -m pantrytrace evaluate
npm ci
python -m pantrytrace sponsor-smoke
python -m pantrytrace demo --scenario ambiguous --memory
```

The fixture workbench and regression tests do not require Node or API keys. Node and pinned `tsx` are optional requirements for the actual local Meterless bridge. The pitch-generation helper additionally uses ReportLab, Pillow and the Windows fonts specified in its source; the supplied finished PDF does not require those packages to view.

The GitHub workflow is prepared for Windows/Linux and Python 3.11/3.13, but it has **not been executed on GitHub** because no remote repository was created. Actual Cursor use, live Zetaris federation, NVIDIA inference, target-user validation and production reliability remain unverified.
