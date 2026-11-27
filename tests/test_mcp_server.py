"""
Offline unit & stdio subprocess integration tests for scripts/mcp_server.py.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import mcp_server


class TestMcpServer(unittest.TestCase):
    def setUp(self) -> None:
        self.server = mcp_server.McpCatalogServer(
            env_probe={
                "os": "Windows",
                "agy_in_path": True,
                "proxy_configured": True,
                "proxy_vars": ["HTTPS_PROXY"],
                "windows_junction_risk": True,
                "junction_paths": [r"C:\Users\demo\.gemini\config\skills\demo"],
            }
        )

    def test_initialize_ping_and_notification(self):
        for proto, expected in (
            ("2024-11-05", "2024-11-05"),
            ("2025-03-26", "2025-03-26"),
            ("2025-06-18", "2025-06-18"),
            ("1999-01-01", "2024-11-05"),
        ):
            init = self.server.handle_request(
                {"jsonrpc": "2.0", "id": f"init-{proto}", "method": "initialize", "params": {"protocolVersion": proto}}
            )
            assert init is not None
            self.assertEqual(init["result"]["protocolVersion"], expected)
            self.assertEqual(init["result"]["serverInfo"]["name"], "awesome-antigravity-tools")
            self.assertIn("tools", init["result"]["capabilities"])
            self.assertIn("resources", init["result"]["capabilities"])

        notif = self.server.handle_request({"jsonrpc": "2.0", "method": "notifications/initialized"})
        self.assertIsNone(notif)
        self.assertIsNone(self.server.handle_line("   \n"))

        ping = self.server.handle_request({"jsonrpc": "2.0", "id": 2, "method": "ping"})
        assert ping is not None
        self.assertEqual(ping["result"], {})

    def test_tools_list_and_all_six_tools_call(self):
        listed = self.server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        assert listed is not None
        tool_names = [t["name"] for t in listed["result"]["tools"]]
        self.assertEqual(
            tool_names,
            ["aat_recommend", "aat_search", "aat_compare", "aat_info", "aat_stats", "aat_doctor"],
        )

        rec = self.server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "aat_recommend", "arguments": {"intent": "windows proxy", "limit": 3, "lang": "zh"}},
            }
        )
        assert rec is not None
        self.assertFalse(rec["result"]["isError"])
        self.assertEqual(rec["result"]["structuredContent"]["tools"][0]["id"], "antigravity-proxy")
        self.assertIn("https://github.com/yuaotian/antigravity-proxy", rec["result"]["content"][0]["text"])
        self.assertIn("代理", rec["result"]["content"][0]["text"])

        srch = self.server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "aat_search", "arguments": {"query": "acp", "tag": "Rust"}},
            }
        )
        assert srch is not None
        self.assertFalse(srch["result"]["isError"])
        self.assertGreaterEqual(srch["result"]["structuredContent"]["count"], 1)
        self.assertIn("/100", srch["result"]["content"][0]["text"])

        cmp_res = self.server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "aat_compare", "arguments": {"tools": ["liftgate", "agy-gyro"], "lang": "zh"}},
            }
        )
        assert cmp_res is not None
        self.assertFalse(cmp_res["result"]["isError"])
        self.assertIn("专有性依据", cmp_res["result"]["content"][0]["text"])

        cmp_json = self.server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 40,
                "method": "tools/call",
                "params": {"name": "aat_compare", "arguments": {"tools": ["liftgate", "agy-gyro"], "format": "json"}},
            }
        )
        assert cmp_json is not None
        self.assertEqual(len(json.loads(cmp_json["result"]["content"][0]["text"])["tools"]), 2)

        info = self.server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {"name": "aat_info", "arguments": {"tool": "liftgate"}},
            }
        )
        assert info is not None
        self.assertEqual(info["result"]["structuredContent"]["repo"], "acking-you/liftgate")

        stats = self.server.handle_request(
            {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "aat_stats", "arguments": {}}}
        )
        assert stats is not None
        self.assertGreaterEqual(stats["result"]["structuredContent"]["total_tools"], 37)

        doc = self.server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {"name": "aat_doctor", "arguments": {"os": "windows", "lang": "zh"}},
            }
        )
        assert doc is not None
        self.assertIn("环境体检", doc["result"]["content"][0]["text"])
        rec_ids = {t["id"] for t in doc["result"]["structuredContent"]["recommended_tools"]}
        self.assertIn("antigravity-junction-skill-fix", rec_ids)

    def test_protocol_validation_and_error_codes(self):
        bad_json = self.server.handle_line("{not-json")
        assert bad_json is not None
        self.assertEqual(bad_json["error"]["code"], -32700)

        for invalid_req in (
            [],
            {"jsonrpc": "1.0", "id": 1, "method": "ping"},
            {"jsonrpc": "2.0", "id": None, "method": "ping"},
            {"jsonrpc": "2.0", "id": True, "method": "ping"},
            {"jsonrpc": "2.0", "id": [1], "method": "ping"},
        ):
            resp = self.server.handle_request(invalid_req)
            assert resp is not None
            self.assertEqual(resp["error"]["code"], -32600)
            self.assertIsNone(resp["id"])

        empty_method = self.server.handle_request({"jsonrpc": "2.0", "id": 1, "method": ""})
        assert empty_method is not None
        self.assertEqual(empty_method["error"]["code"], -32600)
        self.assertEqual(empty_method["id"], 1)

        bad_params = self.server.handle_request({"jsonrpc": "2.0", "id": 9, "method": "ping", "params": "nope"})
        assert bad_params is not None
        self.assertEqual(bad_params["error"]["code"], -32602)

        unknown_method = self.server.handle_request({"jsonrpc": "2.0", "id": 10, "method": "prompts/list"})
        assert unknown_method is not None
        self.assertEqual(unknown_method["error"]["code"], -32601)

        unknown_tool = self.server.handle_request(
            {"jsonrpc": "2.0", "id": 11, "method": "tools/call", "params": {"name": "nope", "arguments": {}}}
        )
        assert unknown_tool is not None
        self.assertEqual(unknown_tool["error"]["code"], -32602)

        bad_args_type = self.server.handle_request(
            {"jsonrpc": "2.0", "id": 110, "method": "tools/call", "params": {"name": "aat_stats", "arguments": [1, 2]}}
        )
        assert bad_args_type is not None
        self.assertEqual(bad_args_type["error"]["code"], -32602)

        for bad_call in (
            {"name": "aat_recommend", "arguments": {"intent": "proxy", "limit": True}},
            {"name": "aat_recommend", "arguments": {"intent": "proxy", "lang": ""}},
            {"name": "aat_recommend", "arguments": {"intent": "proxy", "platform": 123}},
            {"name": "aat_compare", "arguments": {"tools": ["liftgate"]}},
            {"name": "aat_info", "arguments": {"tool": "missing-tool"}},
            {"name": "aat_doctor", "arguments": {"os": ""}},
        ):
            res = self.server.handle_request({"jsonrpc": "2.0", "id": 12, "method": "tools/call", "params": bad_call})
            assert res is not None
            self.assertTrue(res["result"]["isError"], f"Expected isError=True for {bad_call}")

    def test_resources_and_io_error_handling(self):
        res_list = self.server.handle_request({"jsonrpc": "2.0", "id": 13, "method": "resources/list"})
        assert res_list is not None
        uris = [r["uri"] for r in res_list["result"]["resources"]]
        self.assertEqual(uris, ["aat://catalog", "aat://llms.txt"])

        cat_res = self.server.handle_request(
            {"jsonrpc": "2.0", "id": 14, "method": "resources/read", "params": {"uri": "aat://catalog"}}
        )
        assert cat_res is not None
        parsed_cat = json.loads(cat_res["result"]["contents"][0]["text"])
        self.assertGreaterEqual(len(parsed_cat["tools"]), 37)

        llms_res = self.server.handle_request(
            {"jsonrpc": "2.0", "id": 15, "method": "resources/read", "params": {"uri": "aat://llms.txt"}}
        )
        assert llms_res is not None
        self.assertIn("Awesome Antigravity Tools", llms_res["result"]["contents"][0]["text"])

        bad_uri = self.server.handle_request(
            {"jsonrpc": "2.0", "id": 16, "method": "resources/read", "params": {"uri": "aat://missing"}}
        )
        assert bad_uri is not None
        self.assertEqual(bad_uri["error"]["code"], -32602)

        with tempfile.TemporaryDirectory() as tmp:
            broken_srv = mcp_server.McpCatalogServer(
                catalog_path=Path(tmp) / "missing.json",
                llms_path=Path(tmp) / "missing.txt",
            )
            missing_res = broken_srv.handle_request(
                {"jsonrpc": "2.0", "id": 17, "method": "resources/read", "params": {"uri": "aat://catalog"}}
            )
            assert missing_res is not None
            self.assertEqual(missing_res["error"]["code"], -32603)

    def test_stdio_subprocess_lf_roundtrip_and_self_test(self):
        payload = (
            "\n".join(
                [
                    json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}}),
                    json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": 2,
                            "method": "tools/call",
                            "params": {"name": "aat_recommend", "arguments": {"intent": "硬链接", "lang": "zh"}},
                        }
                    ),
                ]
            )
            + "\n"
        ).encode("utf-8")

        proc = subprocess.run(
            [sys.executable, "-m", "scripts.mcp_server"],
            cwd=str(REPO_ROOT),
            input=payload,
            capture_output=True,
            timeout=10,
            check=True,
        )
        self.assertNotIn(b"\r\n", proc.stdout)
        lines = [json.loads(line.decode("utf-8")) for line in proc.stdout.strip().splitlines() if line.strip()]
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0]["id"], 1)
        self.assertEqual(lines[1]["id"], 2)
        self.assertEqual(lines[1]["result"]["structuredContent"]["tools"][0]["id"], "antigravity-junction-skill-fix")

        self.assertEqual(mcp_server.main(["--self-test"]), 0)


if __name__ == "__main__":
    unittest.main()
