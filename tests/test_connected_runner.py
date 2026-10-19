"""Connected orchestration with real fixture-shaped records, mocked providers.

These tests prove mapping/failure behavior, never actual sponsor connectivity.
"""
import copy
import csv
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pantrytrace.sponsors import SponsorError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("pantrytrace_connected_test", ROOT / "scripts" / "run_connected.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def provided_rows():
    recall = json.loads((ROOT / "data" / "recall.json").read_text(encoding="utf-8"))
    recall["affected_gtins"] = json.dumps(recall["affected_gtins"])
    recall["affected_lots"] = json.dumps(recall["affected_lots"])
    inventory = json.loads((ROOT / "data" / "inventory.json").read_text(encoding="utf-8"))["ambiguous"]
    for row in inventory:
        row["units"] = str(row["units"])
    rows = {"TEAM.recall": [recall], "TEAM.inventory": inventory}
    for alias, filename in (("intake", "intake_ledger.csv"), ("aliases", "supplier_aliases.csv"), ("transfers", "transfers.csv")):
        with (ROOT / "data" / filename).open(newline="", encoding="utf-8") as stream:
            rows["TEAM." + alias] = list(csv.DictReader(stream))
    return rows


class FakeMemory:
    def remember(self, content, source, tags):
        self.content = content
        return {"id": "mem-1", "source": source}

    def recall(self, query, top_n=5):
        return {"memories": [{"memory": {"id": "mem-1", "content": self.content}}]}

    def audit(self, memory_id):
        return [{"action": "create"}, {"action": "read"}]


class ConnectedRunnerTests(unittest.TestCase):
    def invoke(self, rows, output, side_effect=None):
        argv = ["run_connected.py"]
        for name in ("recall", "inventory", "intake", "aliases", "transfers"):
            argv += ["--" + name + "-view", "TEAM." + name]
        argv += ["--output", str(output)]
        calls = []
        def fetch(view, limit):
            calls.append((view, limit))
            if side_effect:
                raise side_effect
            return copy.deepcopy(rows[view])
        with patch.object(runner.ZetarisClient, "from_env") as factory, \
                patch.object(runner, "consult_memory", return_value=(FakeMemory(), {"memories": []})) as consult, \
                patch("pantrytrace.adapters.JsonAdapter.read", side_effect=AssertionError("connected path must not read fixture JSON")), \
                patch("pantrytrace.adapters.CsvAdapter.read", side_effect=AssertionError("connected path must not read fixture CSV")), \
                patch("sys.argv", argv), patch("sys.stdout", io.StringIO()):
            factory.return_value.fetch_table.side_effect = fetch
            runner.main()
        return calls, consult

    def test_schema_mapping_executes_real_engine_without_fixture_fallback(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "connected.json"
            calls, _ = self.invoke(provided_rows(), output)
            result = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(len(calls), 5)
        self.assertTrue(all(limit == 5000 for _, limit in calls))
        self.assertEqual(result["mode"], "connected_records")
        self.assertEqual(result["decisions"][0]["status"], "quarantine")
        self.assertEqual(result["decisions"][0]["lot"], "NS260902")
        self.assertEqual(result["summary"]["affected_units"], 30)
        self.assertEqual(result["summary"]["transferred_units_under_review"], 6)
        self.assertTrue(result["zetaris"]["verified"])
        self.assertEqual(len(result["zetaris"]["receipts"]), 5)
        self.assertFalse(result["provenance"]["source_fetching_verified_by_engine"])
        self.assertEqual(result["action_packet"]["external_actions_executed"], 0)

    def test_provider_error_does_not_create_success_artifact(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "connected.json"
            with self.assertRaises(SponsorError):
                self.invoke(provided_rows(), output, SponsorError("provider unavailable"))
            self.assertFalse(output.exists())

    def test_possible_truncation_and_invalid_quantity_fail_before_memory(self):
        for kind in ("truncated", "invalid_units", "multiple_recalls"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary:
                rows, output = provided_rows(), Path(temporary) / "connected.json"
                if kind == "truncated":
                    rows["TEAM.inventory"] = rows["TEAM.inventory"][:1] * 5000
                elif kind == "invalid_units":
                    rows["TEAM.inventory"][0]["units"] = "30.5"
                else:
                    rows["TEAM.recall"] *= 2
                with self.assertRaises(SponsorError):
                    self.invoke(rows, output)
                self.assertFalse(output.exists())

    def test_missing_memory_cannot_be_reported_as_connected_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "connected.json"
            # Wrap the real guard with a deterministic local failure. All five
            # read results can succeed, yet no complete output should be saved.
            with patch.object(runner, "retain_investigation", side_effect=SponsorError("memory unavailable")):
                with self.assertRaises(SponsorError):
                    self.invoke(provided_rows(), output)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
