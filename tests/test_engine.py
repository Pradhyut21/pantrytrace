"""Adversarial logic checks; the small fixture set is not a performance benchmark."""

import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pantrytrace import SCENARIOS, create_demo_database, run_case, run_connected_records, run_evaluation
from pantrytrace.adapters import CsvAdapter, EvidenceFederation, JsonAdapter, SqliteLedgerAdapter


class TriageTests(unittest.TestCase):
    def inventory(self, scenario):
        return JsonAdapter().read("inventory.json")[scenario]

    def test_exact_product_and_lot_are_required(self):
        result = run_case("exact")
        self.assertTrue(result["validation"]["passed"])
        self.assertEqual([d["status"] for d in result["decisions"]], ["quarantine", "clear", "clear"])
        self.assertEqual(result["summary"]["affected_units"], 48)
        self.assertEqual(result["summary"]["cleared_units"], 60)
        self.assertEqual(result["summary"]["iterations"], 1)
        self.assertEqual(result["summary"]["transferred_units_under_review"], 12)

    def test_critic_requests_receipt_then_retries(self):
        result = run_case("ambiguous")
        decision = result["decisions"][0]
        self.assertEqual(decision["status"], "quarantine")
        self.assertEqual(decision["lot"], "NS260902")
        self.assertEqual(decision["resolved_from"], "intake_receipt")
        self.assertEqual(result["summary"]["iterations"], 2)
        actions = [step["action"] for step in result["trace"]]
        self.assertLess(actions.index("request_missing_evidence"), actions.index("query_intake_ledger"))
        self.assertLess(actions.index("query_intake_ledger"), actions.index("merge_corroborated_evidence"))
        self.assertEqual({e["source_type"] for e in result["evidence"]}, {"JSON", "CSV", "SQLite"})
        self.assertIn("LEDGER-A01", {e["id"] for e in decision["evidence"]})
        self.assertIn("ALIAS-02", {e["id"] for e in decision["evidence"]})

    def test_conflicting_receipts_are_preserved_and_abstain(self):
        result = run_case("conflict")
        decision = result["decisions"][0]
        self.assertEqual(decision["status"], "review")
        self.assertEqual(decision["confidence"], "abstain")
        self.assertIsNone(decision["lot"])
        self.assertIn("disagree on lot", decision["reason"])
        evidence_ids = {e["id"] for e in decision["evidence"]}
        self.assertTrue({"LEDGER-C01", "LEDGER-C02"}.issubset(evidence_ids))
        self.assertEqual(result["summary"]["review_units"], 18)
        self.assertTrue(result["validation"]["passed"])

    def test_near_match_does_not_override_verified_distinct_identity(self):
        result = run_case("out_of_scope")
        first, unknown = result["decisions"]
        self.assertEqual(first["status"], "clear")
        self.assertEqual(first["decision_basis"], "verified_distinct_product_identifier")
        self.assertEqual(unknown["status"], "review")
        self.assertIsNone(first["safe_to_eat"])
        self.assertEqual(result["summary"]["review_units"], 8)

    def test_absent_recall_never_becomes_all_clear(self):
        result = run_case("exact", recall_override={})
        self.assertFalse(result["validation"]["passed"])
        self.assertEqual(result["summary"]["cleared_units"], 0)
        self.assertTrue(all(d["status"] == "review" for d in result["decisions"]))

    def test_empty_inventory_fails_validation(self):
        result = run_case(inventory_override=[])
        self.assertFalse(result["validation"]["passed"])
        self.assertEqual(result["decisions"], [])
        self.assertEqual(result["summary"]["cleared_units"], 0)

    def test_missing_ledger_never_infers_lot(self):
        result = run_case("ambiguous", ledger_override=[])
        self.assertEqual(result["decisions"][0]["status"], "review")
        self.assertIsNone(result["decisions"][0]["lot"])

    def test_supplier_note_injection_is_data_and_never_executes(self):
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("No network allowed")), \
             mock.patch("subprocess.run", side_effect=AssertionError("No command allowed")):
            result = run_case("ambiguous")
        self.assertEqual(result["decisions"][0]["status"], "quarantine")
        notes = [e for e in result["evidence"] if e["field"] == "supplier_note"]
        self.assertTrue(any("IGNORE ALL" in e["value"] for e in notes))
        self.assertTrue(all(e["trust"] == "untrusted_free_text" for e in notes))
        self.assertEqual(result["provenance"]["network_calls"], 0)
        self.assertEqual(result["action_packet"]["external_actions_executed"], 0)

    def test_iteration_budget_abstains_without_receipt(self):
        result = run_case("ambiguous", max_iterations=1)
        self.assertEqual(result["decisions"][0]["status"], "review")
        self.assertEqual(result["summary"]["iterations"], 1)
        self.assertNotIn("query_intake_ledger", [step["action"] for step in result["trace"]])

    def test_quantity_mismatch_prevents_receipt_resolution(self):
        inventory = self.inventory("ambiguous")
        inventory[0]["units"] = 29
        result = run_case("ambiguous", inventory_override=inventory)
        self.assertEqual(result["decisions"][0]["status"], "review")
        self.assertIn("quantity", result["decisions"][0]["reason"])

    def test_name_similarity_without_verified_keys_cannot_resolve_identity(self):
        inventory = self.inventory("out_of_scope")[1:]
        inventory[0]["product"] = "Northstar Pantry Chickpeas, 15 oz"
        result = run_case("out_of_scope", inventory_override=inventory)
        self.assertEqual(result["decisions"][0]["status"], "review")

    def test_invalid_quantity_and_duplicate_ids_block_definitive_decisions(self):
        inventory = self.inventory("exact")[:1]
        inventory[0]["units"] = -20
        result = run_case("exact", inventory_override=inventory)
        self.assertFalse(result["validation"]["passed"])
        self.assertEqual(result["decisions"][0]["status"], "review")
        inventory = self.inventory("exact")[:1] * 2
        result = run_case("exact", inventory_override=inventory)
        self.assertFalse(result["validation"]["passed"])
        self.assertTrue(all(d["status"] == "review" for d in result["decisions"]))

    def test_sql_batch_value_is_parameterized(self):
        adapter = SqliteLedgerAdapter()
        try:
            self.assertEqual(adapter.by_intake_batch("IN-ALIAS-01' OR 1=1 --"), [])
            self.assertEqual(len(adapter.by_intake_batch("IN-ALIAS-01")), 1)
            with self.assertRaises(sqlite3.OperationalError):
                adapter.connection.execute("DELETE FROM intake_ledger")
        finally:
            adapter.close()

    def test_action_packet_is_internal_draft_and_has_transfer_receipts(self):
        result = run_case("ambiguous")
        packet = result["action_packet"]
        self.assertEqual(packet["status"], "draft_for_internal_human_review")
        self.assertTrue(all(a["approval_required"] and a["execution_status"] == "draft" for a in packet["actions"]))
        self.assertEqual(packet["actions"][0]["downstream_transfer_receipts"], ["TRANSFER-RECEIPT-A01"])

    def test_json_serializable_and_no_unsupported_live_claim(self):
        self.assertIn('"mode": "fixture"', json.dumps(run_case()))
        with self.assertRaises(ValueError):
            run_case(mode="live")
        with self.assertRaises(ValueError):
            run_case("unknown")

    def test_evaluation_distinguishes_retrieval_from_baseline(self):
        evaluation = run_evaluation()
        self.assertEqual(evaluation["total_items"], 9)
        self.assertEqual(evaluation["baseline_correct"], 8)
        self.assertEqual(evaluation["final_correct"], 9)
        self.assertTrue(all(case["validation_passed"] for case in evaluation["cases"]))

    def test_database_export_is_real_sqlite_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = create_demo_database(Path(directory) / "intake.sqlite")
            connection = sqlite3.connect(path)
            try:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM intake_ledger").fetchone()[0], 4)
            finally:
                connection.close()
            with self.assertRaises(FileExistsError):
                create_demo_database(path)

    def test_connected_records_do_not_read_any_fixture(self):
        recall = JsonAdapter().read("recall.json")
        inventory = self.inventory("ambiguous")[:1]
        ledger = [{"record_id": "LIVE-RECEIPT-1", "intake_batch": "IN-ALIAS-01",
                   "supplier_id": "SUP-NORTHSTAR", "sku": "NCP-15",
                   "gtin": "DEMO-GTIN-NCP15", "lot": "NS260902", "units": 30,
                   "received_at": "2026-09-10", "document_id": "LIVE-DOC-1"}]
        aliases = [{"alias": "North Star Distribution", "supplier_id": "SUP-NORTHSTAR",
                    "source_id": "LIVE-ALIAS-1"}]
        with mock.patch("pantrytrace.adapters.JsonAdapter.read", side_effect=AssertionError("Fixture read")), \
             mock.patch("pantrytrace.adapters.CsvAdapter.read", side_effect=AssertionError("Fixture read")):
            result = run_connected_records(
                recall=recall, inventory=inventory, intake_rows=ledger,
                supplier_aliases=aliases, transfers=[],
                provenance={"synthetic": True, "provider": "test_record_provider",
                            "sources": {"ledger": "test_registered_view"}},
            )
        self.assertEqual(result["mode"], "connected_records")
        self.assertEqual(result["decisions"][0]["status"], "quarantine")
        self.assertEqual(result["decisions"][0]["transfers"], [])
        self.assertFalse(result["provenance"]["source_fetching_verified_by_engine"])
        self.assertIn("test_registered_view", {e["source"] for e in result["evidence"]})
        self.assertNotIn("inventory.json", {e["source"] for e in result["evidence"]})

    def test_connected_empty_records_remain_empty(self):
        result = run_connected_records(recall={}, inventory=[], intake_rows=[],
                                       supplier_aliases=[], transfers=[], provenance={})
        self.assertEqual(result["decisions"], [])
        self.assertFalse(result["validation"]["passed"])
        self.assertIsNone(result["provenance"]["synthetic"])

    def test_connected_requires_explicit_record_lists(self):
        with self.assertRaises(ValueError):
            run_connected_records(recall={}, inventory=[], intake_rows=None,
                                  supplier_aliases=[], transfers=[], provenance={})

    def test_unknown_placeholders_cannot_be_used_to_clear_stock(self):
        for field in ("gtin", "lot"):
            for placeholder in ("UNKNOWN", "unknown", "N/A", "n. a.", "not provided", "--", None, 123):
                with self.subTest(field=field, placeholder=placeholder):
                    item = self.inventory("exact")[0]
                    item[field] = placeholder
                    result = run_case("exact", inventory_override=[item])
                    self.assertEqual(result["decisions"][0]["status"], "review")

    def test_malformed_recall_criteria_fail_closed(self):
        for value in ("DEMO-GTIN-NCP15", [], [None], ["UNKNOWN"], [123], {"x": "y"}, ["DEMO-GTIN-NCP15", ""]):
            for field in ("affected_gtins", "affected_lots"):
                with self.subTest(field=field, value=value):
                    recall = JsonAdapter().read("recall.json")
                    recall[field] = value
                    result = run_case("exact", recall_override=recall)
                    self.assertTrue(all(d["status"] == "review" for d in result["decisions"]))
                    self.assertFalse(result["validation"]["passed"])
                    self.assertEqual(result["summary"]["cleared_units"], 0)

    def connected_ambiguous(self, transfers, ledger_units=36):
        recall = JsonAdapter().read("recall.json")
        inventory = self.inventory("ambiguous")[:1]
        ledger = [row for row in CsvAdapter().read("intake_ledger.csv") if row["record_id"] == "LEDGER-A01"]
        ledger[0]["units"] = ledger_units
        return run_connected_records(
            recall=recall, inventory=inventory, intake_rows=ledger,
            supplier_aliases=CsvAdapter().read("supplier_aliases.csv"),
            transfers=transfers, provenance={"synthetic": True})

    def test_receipt_reconciles_on_hand_plus_unique_direct_outbound(self):
        transfers = [row for row in CsvAdapter().read("transfers.csv") if row["item_id"] == "INV-A01"]
        result = self.connected_ambiguous(transfers + copy.deepcopy(transfers))
        decision = result["decisions"][0]
        self.assertEqual(decision["status"], "quarantine")
        self.assertEqual(decision["outbound_units"], 6)
        self.assertEqual(len(decision["transfers"]), 1)
        self.assertEqual(result["summary"]["affected_units"], 30)
        self.assertEqual(result["summary"]["transferred_units_under_review"], 6)
        bad = self.connected_ambiguous(transfers, ledger_units=30)
        self.assertEqual(bad["decisions"][0]["status"], "review")
        self.assertIn("on-hand plus", bad["decisions"][0]["reason"])

    def test_conflicting_transfer_id_never_gets_a_known_total(self):
        transfers = [row for row in CsvAdapter().read("transfers.csv") if row["item_id"] == "INV-A01"]
        second = {**transfers[0], "units": "7"}
        result = self.connected_ambiguous(transfers + [second])
        decision = result["decisions"][0]
        self.assertEqual(decision["status"], "review")
        self.assertIsNone(decision["outbound_units"])
        self.assertFalse(result["summary"]["transfer_quantity_complete"])
        self.assertFalse(result["validation"]["passed"])
        self.assertEqual(len(decision["transfers"]), 2)

    def test_multi_hop_and_invalid_transfer_quantities_force_review(self):
        base = [row for row in CsvAdapter().read("transfers.csv") if row["item_id"] == "INV-A01"][0]
        for change in ({"parent_transfer_id": "UPSTREAM-1"}, {"hop": 2}, {"units": -6}, {"units": "unknown"}, {"units": True}):
            with self.subTest(change=change):
                result = self.connected_ambiguous([{**base, **change}])
                self.assertEqual(result["decisions"][0]["status"], "review")
                self.assertIsNone(result["decisions"][0]["outbound_units"])
                self.assertFalse(result["summary"]["transfer_quantity_complete"])

    def test_multi_product_recall_cannot_create_cartesian_matches(self):
        recall = JsonAdapter().read("recall.json")
        recall["affected_gtins"].append("DEMO-GTIN-HKC15")
        # A real notice could associate HKC only with a different lot. The MVP
        # cannot represent those pairs and must not invent a Cartesian scope.
        result = run_case("exact", recall_override=recall)
        self.assertTrue(all(d["status"] == "review" for d in result["decisions"]))
        self.assertFalse(result["validation"]["passed"])
        self.assertIn("one distinct product", result["decisions"][0]["reason"])

    def test_unsupported_lot_scope_is_reviewed_instead_of_treated_as_literal(self):
        for unsupported in ("NS260900-NS260999", "NS2609*", "NS260901,NS260902", "NS 260901", "all lots"):
            with self.subTest(unsupported=unsupported):
                recall = JsonAdapter().read("recall.json")
                recall["affected_lots"] = [unsupported]
                result = run_case("exact", recall_override=recall)
                self.assertTrue(all(d["status"] == "review" for d in result["decisions"]))
                self.assertFalse(result["validation"]["passed"])
        item = self.inventory("exact")[0]
        item["lot"] = "NS 260901"
        self.assertEqual(run_case("exact", inventory_override=[item])["decisions"][0]["status"], "review")


if __name__ == "__main__":
    unittest.main()
