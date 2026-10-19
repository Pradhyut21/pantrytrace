"""Optional real Meterless memory around an evidence-checked investigation."""
from __future__ import annotations

import hashlib
import json

from .sponsors import MeterlessClient, SponsorError


def consult_memory(scenario: str, client: MeterlessClient | None = None) -> tuple[MeterlessClient, dict]:
    """Retrieve prior context without treating it as authoritative inventory data."""
    client = client or MeterlessClient.from_env()
    found = client.recall(f"PantryTrace investigation {scenario}", top_n=5)
    if not isinstance(found, dict) or not isinstance(found.get("memories"), list):
        raise SponsorError("H-MEM recall result has an unexpected shape.")
    return client, found


def retain_investigation(result: dict, client: MeterlessClient,
                         prior: dict | None = None) -> dict:
    """Persist actual source-backed findings and verify retrieval in a new process.

    The current policy always refreshes source evidence. Prior memory can explain
    context to a reviewer, but it cannot clear stock or override a fresh receipt.
    """
    findings = [{"item_id": d["item_id"], "status": d["status"], "lot": d["lot"],
                 "units": d["units"], "source_records": sorted({str(e["id"]) for e in d["evidence"]})}
                for d in result["decisions"]]
    content = json.dumps({"project": "PantryTrace", "scenario": result["scenario"],
                          "as_of": result.get("as_of"), "mode": result["mode"],
                          "findings": findings, "policy": "source refresh required; draft actions only"},
                         sort_keys=True)
    digest = hashlib.sha256(content.encode()).hexdigest()
    source = f"investigation:{result['run_id']}:{digest[:12]}"
    record = client.remember(content, source=source, tags=["project:pantrytrace", "scenario:" + result["scenario"]])
    memory_id = record.get("id") if isinstance(record, dict) else None
    if not isinstance(memory_id, str):
        raise SponsorError("H-MEM did not return a persisted memory identifier.")
    # The reference ranks content, not the source label. Verify by the actual
    # stored content so unrelated source-UUID terms cannot suppress a match.
    check = client.recall(content[:3900], top_n=20)
    hits = check.get("memories") if isinstance(check, dict) else None
    if not isinstance(hits, list) or not any(isinstance(hit, dict) and isinstance(hit.get("memory"), dict) and hit["memory"].get("id") == memory_id for hit in hits):
        raise SponsorError("Stored investigation was not retrieved from actual H-MEM.")
    audit = client.audit(memory_id)
    if not isinstance(audit, list) or any(not isinstance(event, dict) for event in audit):
        raise SponsorError("H-MEM audit result has an unexpected shape.")
    actions = [event.get("action") for event in audit]
    if not {"create", "read"}.issubset(actions):
        raise SponsorError("H-MEM ledger did not confirm investigation persistence and retrieval.")
    result["meterless"] = {"engine": "official local H-MEM", "verified": True,
                           "memory_id": memory_id, "source": source,
                           "content_sha256": digest, "ledger_actions": actions,
                           "prior_hits": len((prior or {}).get("memories", [])),
                           "policy": "fresh source evidence always required; memory cannot authorize decisions",
                           "remote_api_calls": 0}
    first = {"agent": "Planner", "action": "consult_meterless_memory",
             "detail": f"Retrieved {result['meterless']['prior_hits']} prior context record(s) from official H-MEM; refresh source evidence before any finding.",
             "iteration": 1, "status": "complete"}
    last = {"agent": "Memory", "action": "persist_and_audit_meterless",
            "detail": f"Stored source-linked findings as {memory_id}; independent engine calls verified retrieval and provenance ledger.",
            "iteration": result["summary"]["iterations"], "status": "verified"}
    result["trace"] = [first, *result["trace"], last]
    for index, event in enumerate(result["trace"], 1):
        event["step"] = index
    return result
