"""Bounded planner/executor/critic loop with a shared, inspectable evidence memory.

This is a deterministic control baseline, not an LLM or a live recall monitor.
Free text is displayed as untrusted evidence and never controls tools or decisions.
"""

from __future__ import annotations

import copy
import json
import re
import time
import uuid
from collections import Counter
from typing import Any

from .adapters import EvidenceFederation

SCENARIOS = [
    {"id": "exact", "title": "Exact affected lot", "description": "Match a verified product and lot; distinguish a later lot and a different product.", "expected": "48 units recommended for quarantine"},
    {"id": "ambiguous", "title": "Missing lot + supplier alias", "description": "The critic requests an intake receipt; an exact batch join resolves a missing lot despite a malicious supplier note.", "expected": "30 units resolved through receipt evidence"},
    {"id": "conflict", "title": "Conflicting intake records", "description": "Two receipts disagree about one batch. Abstain and request a physical label check.", "expected": "18 units require human review"},
    {"id": "out_of_scope", "title": "Similar name, different identity", "description": "Do not match by product name. A verified distinct identifier is outside this recall; an unidentified carton remains in review.", "expected": "42 units outside fixture scope; 8 remain unverified"},
]

EXPECTED = {
    "exact": {"INV-E01": "quarantine", "INV-E02": "clear", "INV-E03": "clear"},
    "ambiguous": {"INV-A01": "quarantine", "INV-A02": "clear"},
    "conflict": {"INV-C01": "review", "INV-C02": "quarantine"},
    "out_of_scope": {"INV-N01": "clear", "INV-N02": "review"},
}

SCOPE = (
    "Internal historical triage exercise only. All data is synthetic. Quarantine is "
    "a proposed internal action requiring human review. Clear means no match to this "
    "fixture recall, never safe to eat. No public alert or recall lifecycle status is produced."
)
CONNECTED_SCOPE = (
    "Internal historical triage from caller-supplied connected records. Quarantine "
    "is a proposed internal action requiring human review. Clear means no match to "
    "this supplied recall scope, never safe to eat. No public alert or recall "
    "lifecycle status is produced. Source fetching is independently verified by the caller."
)


def list_scenarios() -> list[dict]:
    return copy.deepcopy(SCENARIOS)


def _token(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    token = value.strip().upper()
    compact = re.sub(r"[\W_]+", "", token)
    placeholders = {"", "UNKNOWN", "UNK", "NA", "NONE", "NULL", "MISSING", "TBD",
                    "NOTAVAILABLE", "NOTAPPLICABLE", "NOTPROVIDED", "NOTKNOWN",
                    "UNVERIFIED", "UNREADABLE", "NOLOT", "NOGTIN", "PENDING"}
    return "" if compact in placeholders else token


def _recall_errors(recall: dict) -> list[str]:
    errors = []
    if not isinstance(recall, dict):
        return ["Recall criteria must be an object"]
    if not _token(recall.get("recall_id")):
        errors.append("Recall identifier is missing")
    for field in ("affected_gtins", "affected_lots"):
        values = recall.get(field)
        if not isinstance(values, list) or not values or any(not _token(value) for value in values):
            errors.append(f"{field} must be a nonempty list of explicit non-placeholder strings")
    gtins = recall.get("affected_gtins")
    if isinstance(gtins, list) and len({_token(value) for value in gtins if _token(value)}) > 1:
        errors.append("MVP supports one distinct product identifier per recall scope; split multi-product notices into verified product-lot scopes")
    lots = recall.get("affected_lots")
    if isinstance(lots, list) and any(not _lot_token(value) for value in lots):
        errors.append("Affected lots must be explicit alphanumeric tokens; ranges, wildcards, and punctuation syntax are unsupported")
    return errors


def _lot_token(value: Any) -> str:
    token = _token(value)
    return token if re.fullmatch(r"[A-Z0-9]{1,64}", token) else ""


class EvidenceMemory:
    def __init__(self):
        self.records: list[dict] = []
        self.keys: set[str] = set()

    def add(self, source: str, record_id: str, field: str, value: Any,
            source_type: str, trust: str = "structured_fixture") -> dict:
        record = {"source": source, "id": record_id, "field": field,
                  "value": value, "source_type": source_type, "trust": trust}
        key = json.dumps(record, sort_keys=True, ensure_ascii=False)
        if key not in self.keys:
            self.records.append(record)
            self.keys.add(key)
        return record


class Trace:
    def __init__(self):
        self.records: list[dict] = []

    def add(self, agent: str, action: str, detail: str, iteration: int,
            status: str = "complete", **extra: Any) -> None:
        self.records.append({"step": len(self.records) + 1, "agent": agent,
                             "action": action, "detail": detail,
                             "iteration": iteration, "status": status, **extra})


def _inventory_evidence(item: dict, memory: EvidenceMemory, source: str = "inventory.json") -> list[dict]:
    fields = ("gtin", "lot", "intake_batch", "supplier_label", "sku", "units", "location")
    result = [memory.add(source, item["item_id"], field, item.get(field), "JSON")
              for field in fields]
    if item.get("supplier_note"):
        # A note can be shown to an operator, but is never parsed as instructions.
        memory.add(source, item["item_id"], "supplier_note",
                   item["supplier_note"], "JSON", "untrusted_free_text")
    return result


def _prepare_inventory(rows: list[dict]) -> list[dict]:
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("Inventory must be a list of record objects")
    normalized = copy.deepcopy(rows)
    ids = [str(row.get("item_id", "")) for row in normalized]
    for index, item in enumerate(normalized):
        errors = []
        item_id = str(item.get("item_id", "")).strip()
        if not item_id:
            errors.append("Missing inventory item identifier")
            item_id = f"INVALID-ITEM-{index + 1}"
        elif ids.count(item_id) > 1:
            errors.append("Duplicate inventory item identifier")
        item["item_id"] = item_id
        units = item.get("units")
        if isinstance(units, bool) or not isinstance(units, int) or units < 0:
            errors.append("Units must be a non-negative integer")
            item["units"] = 0
        item["_input_errors"] = errors
    return normalized


def _decide(item: dict, recall: dict, recall_evidence: list[dict],
            inventory_evidence: list[dict], retrieved: dict | None = None) -> dict:
    evidence = list(recall_evidence) + list(inventory_evidence)
    gtin, lot = _token(item.get("gtin")), _lot_token(item.get("lot"))
    issues = list(item.get("_input_errors", [])) + list(item.get("_transfer_issues", []))
    missing: list[str] = []
    resolved_from = "inventory"
    if retrieved:
        evidence.extend(retrieved["evidence"])
        issues.extend(retrieved["issues"])
        if not issues:
            gtin = gtin or retrieved.get("gtin", "")
            lot = lot or retrieved.get("lot", "")
            resolved_from = "intake_receipt" if retrieved.get("lot") or retrieved.get("gtin") else "inventory"
    recall_errors = _recall_errors(recall)
    affected_gtins = set() if recall_errors else {_token(value) for value in recall["affected_gtins"]}
    affected_lots = set() if recall_errors else {_token(value) for value in recall["affected_lots"]}
    status, basis = "review", "insufficient_evidence"
    if recall_errors:
        reason = "Recall scope is incomplete or unsupported: " + "; ".join(recall_errors) + ". No clear or quarantine recommendation can be made."
        issues.extend(recall_errors)
    elif issues:
        reason = "; ".join(issues) + ". Human inspection is required."
        basis = "conflicting_or_invalid_evidence"
    elif not gtin:
        missing = ["gtin"] + ([] if lot else ["lot"])
        reason = "Product identity is unverified. Similar names cannot establish a recall match or clear this stock."
    elif gtin not in affected_gtins:
        status, basis = "clear", "verified_distinct_product_identifier"
        reason = "The explicit product identifier differs from this supplied recall scope. This is a scope decision, never a safe-to-eat decision."
    elif not lot:
        missing = ["lot"]
        reason = "Product identifier matches, but the lot is missing. Retrieve the exact intake batch before deciding."
    elif lot in affected_lots:
        status, basis = "quarantine", "exact_product_and_affected_lot"
        reason = "Exact product identifier and affected lot match the supplied recall scope. Recommend internal quarantine pending human approval."
    else:
        status, basis = "clear", "verified_product_and_nonmatching_lot"
        reason = "The verified lot is outside the supplied recall's affected lots. This does not establish food safety."
    return {
        "id": f"DEC-{item['item_id']}", "item_id": item["item_id"],
        "product": item.get("product", "Unidentified product"),
        "gtin": gtin or None, "lot": lot or None,
        "location": item.get("location", "Unspecified location"),
        "units": item["units"], "status": status, "reason": reason,
        "decision_basis": basis, "evidence": evidence,
        "missing_evidence": missing, "evidence_issues": issues,
        "resolved_from": resolved_from, "confidence": "abstain" if status == "review" else "exact_structured_evidence",
        "transfers": [], "human_approval_required": status != "clear",
        "scope": "this_provided_recall_only", "safe_to_eat": None,
    }


def _retrieve(item: dict, federation: EvidenceFederation,
              memory: EvidenceMemory, trace: Trace, iteration: int,
              transfer_info: dict) -> dict:
    result: dict = {"gtin": "", "lot": "", "issues": [], "evidence": []}
    alias_rows = federation.supplier(item.get("supplier_label"))
    for alias in alias_rows:
        result["evidence"].append(memory.add(
            federation.sources["aliases"], alias["source_id"], "supplier_id",
            {"alias": alias["alias"], "supplier_id": alias["supplier_id"]}, "CSV"))
    supplier_ids = {row["supplier_id"] for row in alias_rows}
    trace.add("Executor", "resolve_supplier_alias",
              f"{item['item_id']}: exact alias lookup returned {len(supplier_ids)} supplier identifier(s).",
              iteration, item_id=item["item_id"], source=federation.sources["aliases"])
    rows = federation.receipts(item.get("intake_batch"))
    trace.add("Executor", "query_intake_ledger",
              f"Parameterized SELECT by exact intake_batch returned {len(rows)} receipt record(s) for {item['item_id']}.",
              iteration, item_id=item["item_id"], source=federation.sources["ledger"],
              query="SELECT * FROM intake_ledger WHERE intake_batch = ? ORDER BY record_id",
              parameters=[item.get("intake_batch")])
    for row in rows:
        for field in ("intake_batch", "supplier_id", "sku", "gtin", "lot", "units", "document_id"):
            result["evidence"].append(memory.add(
                federation.sources["ledger"], row["record_id"], field, row.get(field), "SQLite"))
    if not rows:
        trace.add("Memory", "retain_unresolved_evidence",
                  f"No receipt found for {item['item_id']}; absence of evidence cannot clear stock.",
                  iteration, "abstain", item_id=item["item_id"])
        return result
    if len(supplier_ids) != 1 or not _token(item.get("sku")):
        result["issues"].append("Receipt join lacks a unique supplier alias and exact SKU")
        return result
    supplier_id = next(iter(supplier_ids))
    if any(row.get("supplier_id") != supplier_id or _token(row.get("sku")) != _token(item.get("sku")) for row in rows):
        result["issues"].append("Receipt supplier or SKU conflicts with inventory")
    if any(_token(item.get("gtin")) and _token(row.get("gtin")) != _token(item["gtin"]) for row in rows):
        result["issues"].append("Receipt product identifier conflicts with inventory")
    if any(_lot_token(item.get("lot")) and _lot_token(row.get("lot")) != _lot_token(item["lot"]) for row in rows):
        result["issues"].append("Receipt lot conflicts with inventory")
    outbound = transfer_info["outbound_units"]
    if outbound is None:
        result["issues"].append("Outgoing transfer quantities are unresolved")
    elif any(row.get("units") != item["units"] + outbound for row in rows):
        result["issues"].append("Receipt quantity does not reconcile to on-hand plus unique direct outbound transfers")
    gtins = {_token(row.get("gtin")) for row in rows}
    lots = {_lot_token(row.get("lot")) for row in rows}
    if len(gtins) != 1 or not next(iter(gtins), ""):
        result["issues"].append("Intake receipts disagree on product identity or omit it")
    if len(lots) != 1 or not next(iter(lots), ""):
        result["issues"].append("Intake receipts disagree on lot or omit it")
    if not result["issues"]:
        result["gtin"], result["lot"] = next(iter(gtins)), next(iter(lots))
        trace.add("Memory", "merge_corroborated_evidence",
                  f"{item['item_id']}: exact batch + supplier + SKU + identifier join; receipt quantity = {item['units']} on hand + {outbound} unique direct outbound units. Resolves lot {result['lot']}.",
                  iteration, item_id=item["item_id"])
    else:
        trace.add("Memory", "retain_conflicting_evidence",
                  f"{item['item_id']}: retain all receipts; do not select the convenient lot. " + "; ".join(result["issues"]),
                  iteration, "abstain", item_id=item["item_id"])
    return result


def _validate(decisions: list[dict], recall: dict, items: list[dict],
              baseline: list[dict], scenario: str, custom_inputs: bool) -> dict:
    quarantine_supported = all(
        d["decision_basis"] == "exact_product_and_affected_lot" and d["gtin"] and d["lot"]
        for d in decisions if d["status"] == "quarantine")
    clear_supported = all(d["decision_basis"] in {
        "verified_distinct_product_identifier", "verified_product_and_nonmatching_lot"}
        for d in decisions if d["status"] == "clear")
    inventory_valid = bool(items) and not any(item["_input_errors"] for item in items)
    scope_complete = not _recall_errors(recall)
    conservation = sum(d["units"] for d in decisions) == sum(item["units"] for item in items)
    checks = [
        {"name": "inventory_present_and_valid", "passed": inventory_valid},
        {"name": "recall_scope_complete", "passed": scope_complete},
        {"name": "no_name_only_definitive_matches", "passed": quarantine_supported and clear_supported},
        {"name": "on_hand_quantity_partition", "passed": conservation},
        {"name": "direct_transfer_quantities_resolved", "passed": all(d.get("transfer_quantity_resolved", True) for d in decisions)},
        {"name": "all_decisions_have_source_record_evidence", "passed": all(bool(d["evidence"]) for d in decisions)},
        {"name": "no_safe_to_eat_claims", "passed": all(d["safe_to_eat"] is None for d in decisions)},
        {"name": "all_external_actions_held", "passed": True},
    ]
    expected = None if custom_inputs else EXPECTED[scenario]
    if expected is not None:
        checks.append({"name": "fixture_expected_outcomes", "passed": all(
            expected.get(d["item_id"]) == d["status"] for d in decisions) and len(decisions) == len(expected)})
    baseline_correct = None if expected is None else sum(expected.get(d["item_id"]) == d["status"] for d in baseline)
    final_correct = None if expected is None else sum(expected.get(d["item_id"]) == d["status"] for d in decisions)
    return {
        "passed": all(check["passed"] for check in checks), "checks": checks,
        "unresolved_items": sum(d["status"] == "review" for d in decisions),
        "fixture_ground_truth_only": True,
        "baseline_correct": baseline_correct, "final_correct": final_correct,
        "baseline_decisions": [{"item_id": d["item_id"], "status": d["status"]} for d in baseline],
        "limitation": "Fixture checks verify this deterministic prototype, not real-world recall accuracy or food safety.",
    }


def _run_pipeline(scenario: str = "ambiguous", mode: str = "fixture", *,
             inventory_override: list[dict] | None = None,
             ledger_override: list[dict] | None = None,
             recall_override: dict | None = None,
             alias_override: list[dict] | None = None,
             transfer_override: list[dict] | None = None,
             connected_provenance: dict | None = None,
             max_iterations: int = 3) -> dict:
    """Run one bounded local exercise without network or external side effects.

    Overrides support adversarial evaluation; they are not a live-data integration.
    A missing source yields review/failed validation, never an inferred all-clear.
    """
    started = time.perf_counter()
    if scenario not in EXPECTED and mode != "connected_records":
        raise ValueError(f"Unknown scenario: {scenario}")
    if mode not in {"fixture", "connected_records"}:
        raise ValueError("Unsupported engine mode")
    if isinstance(max_iterations, bool) or not isinstance(max_iterations, int) or not 1 <= max_iterations <= 4:
        raise ValueError("max_iterations must be an integer from 1 to 4")
    connected = mode == "connected_records"
    scope = CONNECTED_SCOPE if connected else SCOPE
    source_names = None if not connected else {
        "recall": "provided:recall", "inventory": "provided:inventory",
        "aliases": "provided:supplier_aliases", "ledger": "provided:intake_ledger",
        "transfers": "provided:transfers", **(connected_provenance or {}).get("sources", {}),
    }
    federation = EvidenceFederation(ledger_override, alias_rows=alias_override,
                                     transfer_rows=transfer_override, source_names=source_names)
    memory, trace = EvidenceMemory(), Trace()
    try:
        recall = copy.deepcopy(federation.json.read("recall.json") if recall_override is None else recall_override)
        if not isinstance(recall, dict):
            raise ValueError("Recall criteria must be an object")
        source_rows = federation.json.read("inventory.json")[scenario] if inventory_override is None else inventory_override
        items = _prepare_inventory(source_rows)
        trace.add("Planner", "declare_scope",
                  "Plan: read recall and inventory, propose exact-key decisions, critique missing evidence, retrieve only needed receipts, then recompute. " + scope,
                  1)
        trace.add("Executor", "load_structured_sources",
                  f"Loaded {len(items)} inventory row(s) from JSON and recall criteria {recall.get('recall_id', 'MISSING')}.",
                  1, sources=[federation.sources["inventory"], federation.sources["recall"]])
        transfer_info = {item["item_id"]: federation.transfer_evidence(item["item_id"]) for item in items}
        for item in items:
            item["_transfer_issues"] = transfer_info[item["item_id"]]["issues"]
        trace.add("Executor", "read_direct_transfer_receipts",
                  "Read exact item-id transfer records before quantity checks; deduplicate stable IDs and reject ambiguous graphs.",
                  1, source=federation.sources["transfers"])
        recall_evidence = [memory.add(federation.sources["recall"], recall.get("recall_id", "MISSING"), field,
                                      recall.get(field), "JSON")
                           for field in ("affected_gtins", "affected_lots", "as_of")]
        item_evidence = {item["item_id"]: _inventory_evidence(item, memory, federation.sources["inventory"]) for item in items}
        retrieved: dict[str, dict] = {}
        attempts: set[str] = set()
        retrieval_tasks: list[dict] = []
        baseline: list[dict] = []
        iterations = 0
        for iteration in range(1, max_iterations + 1):
            iterations = iteration
            decisions = [_decide(item, recall, recall_evidence, item_evidence[item["item_id"]],
                                 retrieved.get(item["item_id"])) for item in items]
            if iteration == 1:
                baseline = copy.deepcopy(decisions)
            trace.add("Executor", "propose_decisions",
                      ", ".join(f"{d['item_id']} → {d['status']}" for d in decisions) or "No inventory rows; no decision is possible.", iteration)
            needing = [d for d in decisions if d["missing_evidence"] and d["item_id"] not in attempts]
            if not needing:
                trace.add("Critic", "check_evidence_sufficiency",
                          "Every definitive proposal uses exact structured identifiers. Unresolved or conflicting evidence remains in human review.", iteration)
                break
            trace.add("Critic", "request_missing_evidence",
                      "; ".join(f"{d['item_id']} lacks {', '.join(d['missing_evidence'])}" for d in needing)
                      + ". Reject a name-only decision and request exact intake evidence.", iteration, "needs_evidence")
            if iteration == max_iterations:
                trace.add("Planner", "stop_at_iteration_budget", "Iteration budget reached; retain review decisions.", iteration, "abstain")
                break
            trace.add("Planner", "revise_plan", "Retrieve supplier aliases from CSV and exact batch receipts from SQLite; merge evidence and retry the decision.", iteration + 1)
            for decision in needing:
                item = next(item for item in items if item["item_id"] == decision["item_id"])
                attempts.add(item["item_id"])
                retrieved[item["item_id"]] = _retrieve(item, federation, memory, trace, iteration + 1, transfer_info[item["item_id"]])
                retrieval_tasks.append({
                    "id": f"TASK-RETRIEVE-{item['item_id']}", "kind": "retrieve_intake_evidence",
                    "item_id": item["item_id"], "status": "complete",
                    "description": "Read exact intake batch receipts and supplier alias mapping.",
                    "records_found": sum(e["field"] == "document_id" for e in retrieved[item["item_id"]]["evidence"]),
                })
        for decision in decisions:
            info = transfer_info[decision["item_id"]]
            transfers = info["records"]
            decision["transfers"] = transfers
            decision["outbound_units"] = info["outbound_units"]
            decision["transfer_quantity_resolved"] = not bool(info["issues"])
            decision["transfer_scope"] = info["scope"]
            for transfer in transfers:
                ev = memory.add(federation.sources["transfers"], transfer.get("transfer_id", "MISSING"), "transfer", transfer, "CSV")
                decision["evidence"].append(ev)
        trace.add("Executor", "attach_downstream_transfer_evidence",
                  "Attach the direct transfer receipts read earlier. Outbound units are separate from current stock. Explicit multi-hop or conflicting transfer records remain unresolved.",
                  iterations, source=federation.sources["transfers"])
        validation = _validate(decisions, recall, items, baseline, scenario,
                               connected or inventory_override is not None or ledger_override is not None or recall_override is not None)
        validation["fixture_ground_truth_only"] = not connected
        trace.add("Critic", "validate_final_packet",
                  f"Validation {'passed' if validation['passed'] else 'failed'}; {validation['unresolved_items']} item(s) remain in review. All action packets are drafts.",
                  iterations, "complete" if validation["passed"] else "needs_review")
        counts = Counter(d["status"] for d in decisions)
        tasks = retrieval_tasks + [{
            "id": f"TASK-HUMAN-{d['item_id']}", "kind": "inspect_physical_label" if d["status"] == "review" else "approve_internal_quarantine",
            "item_id": d["item_id"], "status": "pending_human",
            "description": d["reason"], "approval_required": True,
        } for d in decisions if d["status"] in {"review", "quarantine"}]
        result = {
            "run_id": f"{mode}-{scenario}-{uuid.uuid4().hex[:10]}", "scenario": scenario,
            "mode": mode, "as_of": recall.get("as_of"), "scope": scope,
            "agent_type": "deterministic_planner_executor_critic_baseline",
            "summary": {
                "affected_units": sum(d["units"] for d in decisions if d["status"] == "quarantine"),
                "review_units": sum(d["units"] for d in decisions if d["status"] == "review"),
                "cleared_units": sum(d["units"] for d in decisions if d["status"] == "clear"),
                "decisions": len(decisions), "total_items": len(items), "iterations": iterations,
                "status_counts": {key: counts[key] for key in ("quarantine", "review", "clear")},
                "transferred_units_under_review": sum(d["outbound_units"] or 0 for d in decisions if d["status"] != "clear"),
                "transfer_quantity_complete": all(d["transfer_quantity_resolved"] for d in decisions),
                "unresolved_transfer_items": sum(not d["transfer_quantity_resolved"] for d in decisions),
            },
            "decisions": decisions, "trace": trace.records,
            "evidence": memory.records, "tasks": tasks, "validation": validation,
            "provenance": {
                "synthetic": (connected_provenance or {}).get("synthetic") if connected else True,
                "pre_event_prototype": True,
                "fixture_snapshot": recall.get("as_of"),
                "record_sources": list(federation.sources.values()),
                "sql_seed": "explicit caller-supplied intake rows" if connected else "data/intake_ledger.csv (synthetic; not an independent second source)",
                "live_integrations_used": [], "network_calls": 0,
                "source_fetching_verified_by_engine": False,
                "caller_provenance": copy.deepcopy(connected_provenance) if connected else None,
            },
            "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        }
        result["action_packet"] = export_action_packet(result)
        return result
    finally:
        federation.close()


def export_action_packet(result: dict) -> dict:
    """Return internal drafts only. This function does not send or mutate anything."""
    actions = []
    for decision in result["decisions"]:
        if decision["status"] == "clear":
            continue
        actions.append({
            "action_id": f"ACTION-{decision['item_id']}",
            "type": "internal_quarantine_review" if decision["status"] == "quarantine" else "physical_label_inspection",
            "item_id": decision["item_id"], "units": decision["units"],
            "location": decision["location"], "reason": decision["reason"],
            "evidence_record_ids": sorted({e["id"] for e in decision["evidence"]}),
            "downstream_transfer_receipts": sorted({t["receipt_id"] for t in decision["transfers"] if t.get("receipt_id")}),
            "transfer_scope": decision.get("transfer_scope", "single_outgoing_hop_only"),
            "outbound_units": decision.get("outbound_units"),
            "approval_required": True, "execution_status": "draft",
            "external_communication_sent": False,
        })
    return {"run_id": result["run_id"], "mode": result["mode"],
            "as_of": result.get("as_of"), "scope": result.get("scope", SCOPE),
            "status": "draft_for_internal_human_review", "actions": actions,
            "external_actions_executed": 0}


def run_case(scenario: str = "ambiguous", mode: str = "fixture", *,
             inventory_override: list[dict] | None = None,
             ledger_override: list[dict] | None = None,
             recall_override: dict | None = None,
             max_iterations: int = 3) -> dict:
    """Run a completely local synthetic case. Never fetches data or sends actions."""
    if mode != "fixture":
        raise ValueError("run_case supports fixture mode only; use run_connected_records for explicit connected inputs")
    return _run_pipeline(scenario, mode, inventory_override=inventory_override,
                         ledger_override=ledger_override, recall_override=recall_override,
                         max_iterations=max_iterations)


def run_connected_records(*, recall: dict, inventory: list[dict],
                          intake_rows: list[dict], supplier_aliases: list[dict],
                          transfers: list[dict], provenance: dict,
                          max_iterations: int = 3) -> dict:
    """Triage explicitly supplied records without fixture fallbacks or network calls.

    A connector must fetch, map, and verify its own records before this call. The
    engine carries caller provenance but does not independently attest live access.
    Empty inputs remain empty and lead to abstention/failed validation as applicable.
    Required intake columns match the fixture schema; alias rows need alias,
    supplier_id, source_id; transfer rows need their fixture schema columns.
    """
    if not isinstance(recall, dict) or not isinstance(provenance, dict):
        raise ValueError("recall and provenance must be explicit dictionaries")
    for name, rows in (("inventory", inventory), ("intake_rows", intake_rows),
                       ("supplier_aliases", supplier_aliases), ("transfers", transfers)):
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError(f"{name} must be an explicit list of record dictionaries")
    return _run_pipeline(
        "connected", "connected_records", inventory_override=inventory,
        ledger_override=intake_rows, recall_override=recall,
        alias_override=supplier_aliases, transfer_override=transfers,
        connected_provenance=provenance, max_iterations=max_iterations,
    )


def run_evaluation() -> dict:
    """Compare the inventory-only baseline with retrieval on declared fixtures.

    This tiny, authored test set measures logic coverage, not generalization.
    """
    cases = []
    baseline_correct = final_correct = total = 0
    for scenario in EXPECTED:
        result = run_case(scenario)
        validation = result["validation"]
        count = result["summary"]["total_items"]
        baseline_correct += validation["baseline_correct"]
        final_correct += validation["final_correct"]
        total += count
        cases.append({"scenario": scenario, "items": count,
                      "baseline_correct": validation["baseline_correct"],
                      "final_correct": validation["final_correct"],
                      "validation_passed": validation["passed"],
                      "iterations": result["summary"]["iterations"]})
    return {"mode": "fixture", "cases": cases, "total_items": total,
            "baseline_correct": baseline_correct, "final_correct": final_correct,
            "baseline_accuracy": round(baseline_correct / total, 4),
            "final_accuracy": round(final_correct / total, 4),
            "limitation": "Nine authored synthetic items; a logic regression check, not a real-world performance claim."}
