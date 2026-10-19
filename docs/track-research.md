# PantryTrace: research and track selection

Research checked 19 October 2026. Recommended primary track: **Solving Fragmented Intelligence**. Working project name: **PantryTrace**. The recommendation concerns project fit and achievable execution; public research cannot establish how many entrants will select a track, prove zero competition, or predict a win.

## Eligibility and selection context

The supplied Hackathon Overview, FAQ, and APPROACH guide say that work committed before **22 October 2026, 00:00 UTC** is ineligible except clearly declared pre-existing components. That is **22 October, 05:30 IST**. Prepared data also needs declaration. The stated submission cutoff is **27 October, 23:45 UTC / 28 October, 05:15 IST**. Treat current work as declared preparation; build during the window unless the official rules explicitly permit otherwise. The supplied text calls this a 144-hour event, although the published endpoints are 143 hours 45 minutes apart.

Every submission must integrate Zetaris and Meterless and use Cursor as its development environment. NVIDIA belongs where it adds value. The supplied rubric is Impact 30, Technical 20, Innovation 15, Demo 15, Product/UX 10, Sponsor Tech 10. A usable internal investigation packet with visible correction and recovery fits this rubric better than a broad recall-search chatbot. The supplied written guides require a slide deck even though the pasted submission form labels it optional; prepare one and check the final official requirements.

### Six ideas compared

These are analyst judgments about scope and evidence, not entrant counts or measured market saturation.

| Candidate | Primary track | Accessible foundation / existing capability | Judgment for a 144-hour build |
|---|---|---|---|
| **Pantry recall-to-stock and agency-transfer reconciliation** | Fragmented Intelligence | FDA notices and historical enforcement records, synthetic donor manifests, stock CSVs and transfer ledger; [Primarius](https://help.primarius.app/Home/Detail/Food-Rescue) documents real donor-to-agency workflows | **Best fit.** Three small sources can disagree visibly. Produces a bounded task packet, supports exact fixture evaluation, and naturally demonstrates data federation. Domain review is still needed. |
| Thrift-store recalled-product intake triage | Fragmented Intelligence | [CPSC public recall API](https://www.cpsc.gov/Recalls/CPSC-Recalls-Application-Program-Interface-API-Information?language=en); resale intake records | Strong runner-up. Public structured recall data exists, but image/model identification is harder and product condition is outside what the data can establish. |
| Public procurement milestone/payment explanation | Explain Why | [OCDS](https://www.open-contracting.org/data-standard/) connects contracting stages; OCP publishes [73 risk indicators](https://www.open-contracting.org/resources/red-flags-in-public-procurement-a-guide-to-using-data-to-detect-and-mitigate-risks/) | Worthwhile but implementation records may be incomplete. Requires careful distinction between missing data, accounting timing, and actual wrongdoing. |
| Explain whether an SBOM dependency finding applies to this release | Explain Why | Package manifests, advisories, build flags and dependency evidence; extensive existing scanner ecosystem | Fast data access and clear output, but a crowded category and correct reachability analysis is difficult. Avoid claiming vulnerability absence from a model answer. |
| Pantry donation pickup replanning after a failed route | Reasoning Architecture | Synthetic pickup/agency demand/time-window inputs; [OR-Tools](https://github.com/google/or-tools) already solves constrained routing | Clear measurable actions. Hard to show the agent adds value beyond the optimizer without expanding integration scope. Better as a future PantryTrace extension. |
| Pantry allocation replanning after a recalled lot becomes unavailable | Reasoning Architecture | Same synthetic stock plus explicit capacity, reservation and priority policies | Good alternate track if the build concentrates on stateful decisions. For this event, it adds scheduling/fairness work before the core evidence reconciliation is solved. |

## 1. Idea breakdown and problem statement

**One-sentence problem:** We are building an agent that helps a food-bank operations coordinator reconcile a recall notice with inconsistent donation, inventory, and agency-transfer records, producing an evidence-linked internal review packet and draft quarantine tasks.

The user supplies or selects one bounded notice. The system discovers relevant sources, resolves product aliases, separates product identity from lot eligibility, follows transfers to partner locations, and asks for review when evidence is missing or conflicting. Its output is an inventory investigation packet: affected or possibly affected rows, quantities, locations, evidence, unresolved questions, and internal tasks requiring a coordinator's approval.

This workflow is grounded in actual operations. A January 2026 [Foodbank of Southeastern Virginia and the Eastern Shore partner manual](https://foodbankonline.org/wp-content/uploads/2026/01/PAM-Jan-2026.pdf), recall section, instructs agencies to inspect inventory and quarantine recalled product. The [Global FoodBanking Network](https://www.foodbanking.org/blogs/how-food-banks-keep-donated-food-safe-to-eat/) describes receiving inspections, inventory control, and traceability in food-bank safety programs.

The difficult subproblems are inconsistent names, reused supplier SKUs, free-text lot/date expressions, incomplete lot fields, split shipments, quantity units, duplicate transfers, and contradictory documents. The narrow MVP handles three tabular sources and text notices; barcode scanning, OCR, live public notification, route optimization, and automatic stock release are outside the first version.

**Data boundary:** The [openFDA food enforcement overview](https://open.fda.gov/apis/food/enforcement/) describes weekly historical/classified recall data, warns against using it for public alerts or recall lifecycle tracking, and explains that statuses can remain stale. Use this endpoint for historical demonstrations and reconciliation context. A live notice workflow should start from an original FDA public announcement, preserve its retrieval time, and require operator verification. FDA also says [its announcement list is incomplete](https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts). No result means insufficient evidence about this query, never proof that stock is safe.

## 2. Prior art and existing products

| Tool | What it already does | Similarity and defensible opportunity |
|---|---|---|
| [Trustwell / FoodLogiQ](https://www.trustwell.com/platform/manage-quality/) | Connects food quality, suppliers, product/location/batch context, traceability and recall readiness | Direct commercial overlap. PantryTrace should be a small CSV-first investigation layer for fragmented pantry records; do not claim to invent traceability or recall management. |
| [Recall InfoLink](https://www-origin.recallinfolink.com/why-recall-infolink) | Recall communication, documentation, status and response workflows across suppliers, distributors and points of sale | Direct workflow overlap. The proposed demo emphasizes uncertainty in entity/lot reconciliation and reproducible evidence; feature gaps and pricing have not been independently established. |
| [Primarius Food Rescue](https://help.primarius.app/Home/Detail/Food-Rescue) | Donor pickups, receiving inventory, route quantities and agency dropoffs | Strong domain incumbent/possible source system. Integrate exported records rather than propose replacing a food-bank ERP. No claim is made that Primarius lacks recall functionality. |
| [Beanstalk](https://github.com/jacobrakaiFoundation/beanstalk) | Free FDA/FSIS search, source fields, watchlists and clearly separated announcement/history handling | Open-source adjacent competitor. Recall search alone is insufficient differentiation. Our proposed work links private-style synthetic inventory and transfers into an operational packet. |
| [RecallBridge](https://github.com/gokul-debugger/recallbridge) | CPSC/openFDA recall search, deterministic explainable product matching and private browser watchlists | **Name collision and close prior art.** Avoid this name. The proposal must demonstrate lot scope, agency transfer lineage, adversarial review and task artifacts beyond search/matching. |

Exact-name web searches for “PantryTrace” and “LotLighthouse” returned no results during this research. This is a limited search observation, not name availability or trademark clearance.

## 3. GitHub repository research

Metadata below was retrieved from the public GitHub repository API on 19 October 2026. Stars and push times change; a recent push does not itself establish maintenance quality. Do not copy code without checking its actual file license and attribution requirements.

| Repository | Stars at check | Main stack | Last pushed (UTC) / license | Relevance and recommendation |
|---|---:|---|---|---|
| [LangGraph](https://github.com/langchain-ai/langgraph) | 43,520 | Python; JS counterpart available | 2026-10-19 / MIT | Optional state-machine orchestration, shared state, critique branches, checkpointing. Use only if already comfortable; a small custom typed orchestrator is also viable. |
| [dedupe](https://github.com/dedupeio/dedupe) | 4,518 | Python | 2025-07-29 / MIT | Active-learning entity resolution. Useful reference for labeled pair adjudication; interactive labeling and sparse domain examples make it less attractive as the initial MVP dependency. |
| [RapidFuzz](https://github.com/rapidfuzz/RapidFuzz) | 4,172 | Python/C++ | 2026-10-19 / MIT | Best simple baseline/candidate generator. Similarity proposes records for inspection; it must not decide lot eligibility or imply a probability of recall. |
| [Splink](https://github.com/moj-analytical-services/splink) | 2,494 | Python/SQL backends | 2026-10-19 / MIT | Probabilistic linkage across records lacking stable identifiers. Useful after enough representative pairs exist. Too much calibration work for the smallest fixture. |
| [Ditto](https://github.com/megagonlabs/ditto) | 321 | Python/Transformers | 2024-04-17 / Apache-2.0 | Research reference for pairwise entity matching; older repository. Avoid training or deploying it merely to add technical weight. |
| [Beanstalk](https://github.com/jacobrakaiFoundation/beanstalk) | 1 | TypeScript, web/native components | 2026-10-13 / no detected repository license | Inspect as prior art only. GitHub's missing detected license means no assumed reuse permission. |
| [RecallBridge](https://github.com/gokul-debugger/recallbridge) | 1 | Python/FastAPI plus React/TypeScript | 2026-08-25 / MIT | Closest naming/category collision. Inspect for competitive comparison; build the actual differentiated inventory workflow independently. |

**Starter choice:** create a small original typed service during the eligible window; use RapidFuzz for a transparent baseline, a typed schema validator, bounded model calls, and test fixtures. Libraries are building blocks, not the project's novelty. There is no requirement to import a large starter repository.

## 4. Papers and academic work

| Paper | Authors / date | What it contributes to this design |
|---|---|---|
| [Deep Entity Matching with Pre-Trained Language Models](https://arxiv.org/abs/2004.00584) | Yuliang Li, Jinfeng Li, Yoshihiko Suhara, AnHai Doan, Wang-Chiew Tan; 2020 preprint, VLDB 2021 | Ditto treats entity matching as sequence-pair classification and injects domain cues. Supports keeping brand/size/identifier fields distinct. Its benchmark results do not establish performance on recalls or pantry lots. |
| [WDC Products: A Multi-Dimensional Entity Matching Benchmark](https://arxiv.org/abs/2301.09521) | Ralph Peeters, Reng Chiz Der, Christian Bizer; 2023 preprint, EDBT 2024 | Tests corner cases, unseen entities and development-set size; finds unseen entities difficult. Motivates held-out brands, hard negative near-neighbor products and no leakage from fixtures into prompts. |
| [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) | Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao; 2022 preprint, ICLR 2023 | Interleaves tool actions and plan adjustment. Inspiration for selecting an invoice or alias source after a conflict, rather than always running a fixed chain. No need to expose private model reasoning; log tool decisions, evidence and outcomes. |
| [Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection](https://arxiv.org/abs/2310.11511) | Akari Asai, Zeqiu Wu, Yizhong Wang, Avirup Sil, Hannaneh Hajishirzi; 2023 | Adaptive retrieval and critique address unsupported generation. The MVP borrows an evidence-checking pattern; it does not reproduce the trained Self-RAG method or claim its results. |
| [Towards a more efficient use of process and product traceability data for continuous improvement of industrial performances](https://arxiv.org/abs/1810.13141) | Thierno Diallo, Sébastien Henry, Yacine Ouzrout; 2018 | Domain prior art connecting traceability data to recall procedures. Shows that exploiting lineage for recall is established, not a new scientific contribution. |

The unresolved research questions for this MVP are calibrated abstention on incomplete lot data, preserving conflict instead of silently merging it, evaluating correct quantities after transfer splits, and measuring whether critique improves decisions over simple rules. No paper reviewed establishes the proposed pantry-specific system's real-world accuracy or health impact.

## 5. Technology stack analysis

Use one typed application stack and keep the agent's decisions inspectable. Python/FastAPI plus a small web UI is a reasonable candidate; a TypeScript implementation is equally acceptable if it is faster for the builder. Model choice is secondary to strict tool schemas, reproducible inputs and bounded state transitions.

| Layer | Proposed responsibility |
|---|---|
| Zetaris | Query the recall snapshot, inventory export and transfer/source-document tables through federated views. The demo must show actual execution evidence; a local sample adapter must be labeled sample mode. |
| Meterless | Use the official local H-MEM engine for persistent evidence context, retrieval and provenance audit. The implementation research subsequently verified and executed this engine. It is not a hosted model inference API; optional model critique is a separate integration. |
| Matching | Exact identifiers first; explicit supplier alias mapping; fuzzy matching only to generate candidates; separate product identity and recall lot/date scope. |
| Decision checks | Typed enums, source-reference validation, immutable raw fields, quantity/unit consistency, transfer deduplication, and a bounded critic/retrieval retry. |
| Storage | Small relational tables or JSON fixtures; append-only investigation events. A graph database is unnecessary for tens of transfer edges. |
| NVIDIA | Optional validated endpoint for a useful model or reranker if available. Measure latency/quality contribution before adding it. |
| Output | Reviewable JSON/CSV plus readable internal task packet; task drafts contain quantity, location, evidence and uncertainty. |

The [GS1 traceability standard](https://www.gs1.org/standards/gs1-global-traceability-standard/current-standard) organizes traceability around events and their key data elements. [EPCIS](https://ref.gs1.org/epcis/) supplies a relevant event-sharing model. Borrow the concepts of object/lot identity, location, time and movement, but do not claim EPCIS conformance without validation.

### Minimal schema and behavior

- `notice`: ID, source URL/kind, publication and retrieval times, raw text/hash, product description, raw lot/date expression.
- `stock`: row ID, original product/brand/supplier SKU, GTIN if known, raw lot/date values, quantity and unit, location, source document ID.
- `transfer`: stable ID, linked stock/lot, from/to locations, quantity/unit, event time, source document ID.
- `finding`: stock/notice IDs, identity evidence, lot-scope evidence, transfer path, uncertainty, evidence IDs, decision enum.
- `task_draft`: review status, location, quantity, suggested internal action, required verification and source links.

Recommended decision labels are `MATCHED`, `POSSIBLE`, `NOT_MATCHED`, `INSUFFICIENT_EVIDENCE`. `NOT_MATCHED` describes a bounded comparison, not a declaration that food is safe. Missing lot data must remain unresolved. An LLM may propose parsed expressions, but deterministic checks must validate numbers, dates, citations and units before they drive an action draft.

Planner selects sources → analyst proposes a match → critic finds an alias/lot/quantity conflict → planner chooses an additional document → analyst revises or abstains → exporter writes the internal review packet. Add a maximum revision count and a documented timeout fallback. Labels in the trace must reflect actual calls and observations, not theatrical agents.

## 6. Community, ecosystem and datasets

**Domain resources:** the [Global FoodBanking Network food-safety explanation](https://www.foodbanking.org/blogs/how-food-banks-keep-donated-food-safe-to-eat/), the cited partner-agency manual, [Primarius food rescue documentation](https://help.primarius.app/Home/Detail/Food-Rescue), and GS1/EPCIS specifications are useful discovery material. An operations coordinator or food-safety lead should validate the task packet before any real pilot. This research did not interview one.

**Technical community:** official GitHub discussions/issues for the selected matching/orchestration library; database research venues VLDB and EDBT for entity matching; GS1's public standards materials for traceability. The names attached to the cited papers are a better starting point than unsupported influencer lists. HackOS sponsor Help channels and mentor hours are the event-specific place to resolve integrations.

**Available data:**

| Source | Use and limitation |
|---|---|
| [openFDA food enforcement API](https://open.fda.gov/apis/food/enforcement/example-api-queries/) | Small historical recall snapshots. Preserve source dates and raw lot text; no assertion of live alert completeness. |
| [FDA recall announcements](https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts) | Original public-notice URLs for selected cases. The list is incomplete and old notices can move to archives. |
| [USDA FSIS recall API](https://www.fsis.usda.gov/science-data/developer-resources/recall-api) | JSON recalls/public-health alerts for a later meat/poultry extension. Defer from the minimum FDA-only build. |
| Synthetic pantry records | Explicitly fictional manifests, stock and transfer logs with documented ground truth. No beneficiary names, real addresses or confidential supplier records. |
| [WDC Products paper/data reference](https://arxiv.org/abs/2301.09521) | General entity-matching research benchmark. Not a substitute for domain-specific lot/transfer tests; large downloads are unnecessary. |

[openFDA's licensing page](https://open.fda.gov/license/) generally dedicates its own content/data/code to CC0 unless otherwise noted and forbids implying endorsement. Record source, retrieval date, subset size and transformations in a data ledger. Check third-party notice content separately; link rather than copy full articles. Any data prepared before the build opens must be declared under the supplied event guidance.

## 7. Market landscape and viability

There is demonstrated operational need and substantial existing competition. Commercial traceability/recall vendors validate the category; free recall-search projects narrow the space for another search interface. The plausible niche is a lightweight investigation layer for small pantry networks with imperfect exports, limited identifiers and no desire to migrate their inventory software. That niche is a hypothesis, not verified unmet demand.

A credible distinction is the combination of: source discovery across inconsistent tables; separate identity and lot-scope judgments; partner-transfer lineage; explicit uncertainty; a critic that changes the plan; and a concrete task artifact with an auditable benchmark. Neither entity resolution, multi-agent critique, nor recall management is scientifically novel by itself.

Potential sustainability models include open-source self-hosting, sponsored nonprofit hosting, or support contracts through a network. No current willingness-to-pay, market size, cost savings or adoption figure was validated. A top-down TAM estimate would add false precision. Real value requires a user study comparing investigation time and error rates with the existing process.

## 8. Recommended next steps and measurable evaluation

### Validate before building

1. Inspect 5–10 FDA notice examples with different lot expressions; create a small provenance ledger and proposed ground truth. Mark all synthetic records and pre-window preparation explicitly.
2. Have one target-domain operator review the input/export fields and the proposed internal task. Ask which source they trust, what prevents a confident decision, and who approves the action. If no operator is available, state that validation remains outstanding.
3. Confirm actual Zetaris query access, Meterless engine setup and Cursor use. Then implement the narrow eligible-window build and produce evidence from real sponsor calls. A mock adapter cannot substantiate sponsor completion.

### Proposed benchmark — targets, not results

Create 60–100 labeled comparisons grouped by scenario; hold out at least one brand and one lot-expression family. Ground truth includes product identity, lot eligibility, unresolved fields, affected locations, quantity bounds and expected task status. Keep development and evaluation cases separate.

| Measure | How to report it honestly |
|---|---|
| Match precision/recall | Compare labeled affected inventory rows, separating exact-match cases from ambiguous cases. Report numerator/denominator and sample size. |
| Abstention quality | Measure whether missing/conflicting evidence is marked unresolved; report how many true matches are deferred and how many unresolved rows are overclassified. |
| Unsupported clearance | Count any output that calls an item safe or releases stock without required evidence. Target zero; do not claim this proves deployment safety. |
| Transfer/quantity correctness | Compare final location set and quantities with fixture truth; include split transfers, duplicates, returns and mixed units. |
| Evidence coverage | Check that each match claim, quantity and task references existing source rows/documents. Human review checks whether references actually support the conclusion. |
| Critique contribution | Evaluate exact string baseline, fuzzy-only baseline, full system without critic, and full system. Show both improvements and regressions. |
| Recovery and reproducibility | Test unavailable external source, malformed model output, timeout, stale snapshot, contradictory documents and clean installation. Capture bounded retries and final state. |
| Efficiency | Report median and worst-case duration on the published fixture with machine/model/mode noted. Treat manual time savings as unproven until measured with users. |

Suggested development gates: core deterministic evidence checks first; one genuine critique-and-retrieval branch; three contrasting end-to-end scenarios; sponsor integration traces; then clean-run validation, README, deck and a 1–4 minute demo. Keep a reliable sample mode with frozen inputs and clearly labeled provenance; do not present sample-mode execution as live federation or inference.

The strongest demo contrast is one record that matches exactly, one alias resolved through an invoice and a transfer, and one missing-lot case that remains unresolved. Show a real correction in the trace, the resulting partner-location task draft, and the source evidence beside it. The claim is **less manual evidence assembly with explicit uncertainty**; accuracy and impact claims must come from the executed benchmark and later user validation.
