import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from pantrytrace.sponsors import MeterlessClient, SponsorError, ZetarisClient, integration_status


class ZetarisTests(unittest.TestCase):
    def client(self, transport=None):
        return ZetarisClient("https://example.test/api/v1.0", "secret-test-key", "42", ["TEAM.inventory"], transport)

    def test_documented_request_and_string_result(self):
        calls = []
        def transport(request, timeout):
            calls.append((request, timeout))
            return {"headers": ["sku", "quantity"], "data": [["ABC", "12"]]}
        rows = self.client(transport).fetch_table("TEAM.inventory", limit=100)
        request, timeout = calls[0]
        self.assertEqual(rows, [{"sku": "ABC", "quantity": "12"}])
        self.assertEqual(request.full_url, "https://example.test/api/v1.0/sql-editor/sqls/run")
        self.assertEqual(request.get_header("Authorization"), "Bearer secret-test-key")
        self.assertEqual(request.get_header("X-org-id"), "42")
        body = json.loads(request.data)
        self.assertEqual(body["source"], "SqlEditor")
        self.assertEqual(body["limit"], 100)
        self.assertEqual(timeout, 30)

    def test_rejects_mutation_cross_table_and_injection_without_network(self):
        with patch("pantrytrace.sponsors._http_json") as http:
            client = self.client()
            for sql in ["DELETE FROM TEAM.inventory", "SELECT * FROM OTHER.inventory",
                        "SELECT * FROM TEAM.inventory; DROP TABLE TEAM.inventory",
                        "SELECT * FROM TEAM.inventory UNION SELECT * FROM SECRET.users",
                        "SELECT * FROM TEAM.inventory WHERE sku='x' OR 1=1",
                        "SELECT * FROM TEAM.inventory JOIN SECRET.users ON 1=1",
                        "SELECT dangerous_udf(sku) FROM TEAM.inventory",
                        "SELECT * FROM TEAM.inventory -- trailing comment"]:
                with self.subTest(sql=sql), self.assertRaises(SponsorError):
                    client.query(sql)
            http.assert_not_called()

    def test_simple_filter_is_permitted(self):
        client = self.client(lambda *_args, **_kwargs: {"headers": ["sku"], "data": []})
        self.assertEqual(client.query("SELECT sku FROM TEAM.inventory WHERE sku='O''Brien' AND quantity>=0"), [])

    def test_malformed_provider_rows_fail_closed(self):
        client = self.client(lambda *_args, **_kwargs: {"headers": ["sku", "quantity"], "data": [["ABC"]]})
        with self.assertRaises(SponsorError):
            client.fetch_table("TEAM.inventory")

    def test_url_must_be_direct_rest_and_have_no_embedded_secret(self):
        for url in ["https://example.test", "https://user:password@example.test/api/v1.0", "https://example.test/api/v1.0?key=secret"]:
            with self.subTest(url=url), self.assertRaises(SponsorError):
                ZetarisClient(url, "key", "1", ["TEAM.inventory"])


class MeterlessTests(unittest.TestCase):
    def test_bridge_calls_official_engine_and_passes_data_on_stdin(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "hmem" / "src").mkdir(parents=True)
            (root / "hmem" / "src" / "index.ts").write_text("export class HMEM {}")
            (root / "cli.mjs").write_text("")
            with patch("pantrytrace.sponsors.shutil.which", return_value="node"):
                client = MeterlessClient(root / "hmem", root / "cli.mjs", root / "state", node="node")
            completed = subprocess.CompletedProcess([], 0, '{"id":"mem-1","source":"FDA:1"}', "")
            with patch("pantrytrace.sponsors.subprocess.run", return_value=completed) as run:
                self.assertEqual(client.remember("Lot ABC recalled", "FDA:1")["id"], "mem-1")
            args, kwargs = run.call_args
            payload = json.loads(kwargs["input"])
            self.assertEqual(payload["operation"], "remember")
            self.assertEqual(payload["source"], "FDA:1")
            self.assertEqual(payload["entry"], str(root / "hmem" / "src" / "index.ts"))
            self.assertIn("memory.add", args[0][-1])
            self.assertIn("memory.query", args[0][-1])
            self.assertNotIn("Lot ABC recalled", args[0][-1])
            self.assertFalse(kwargs.get("shell", False))

    def test_missing_real_engine_is_explicit(self):
        with self.assertRaisesRegex(SponsorError, "Official H-MEM"):
            MeterlessClient("missing-official-engine", "missing-tsx")


class StatusTests(unittest.TestCase):
    def test_status_does_not_call_network_or_claim_verification(self):
        with patch("pantrytrace.sponsors._http_json") as http, patch("pantrytrace.sponsors.subprocess.run") as run:
            status = integration_status({"METERLESS_HMEM_DIR": "missing-official-engine"})
        http.assert_not_called()
        run.assert_not_called()
        self.assertTrue(all(not provider["live_verified"] for provider in status.values()))
        self.assertEqual(status["meterless"]["status"], "dependency_missing")
        self.assertEqual(status["cursor"]["status"], "requires_user_evidence")


if __name__ == "__main__":
    unittest.main()
