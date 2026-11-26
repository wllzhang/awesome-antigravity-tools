"""
Offline unit & stdio subprocess integration tests for scripts/mcp_server.py.
"""

from __future__ import annotations

import json
import subprocess
import sys
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
        init = self.server.handle_request(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}}
        )
        assert init is not None
        self.assertEqual(init["result"]["protocolVersion"], "2024-11-05")
        self.assertEqual(init["result"]["serverInfo"]["name"], "awesome-antigravity-tools")
        self.assertIn("tools", init["result"]["capabilities"])
        self.assertIn("resources", init["result"]["capabilities"])

        notif = self.server.handle_request({"jsonrpc": "2.0", "method": "notifications/initialized"})
        self.assertIsNone(notif)

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
                "params": {"name": "aat_recommend", "arguments": {"intent": "windows proxy", "limit": 3}},
            }
        )
        assert rec is not None
        self.assertFalse(rec["result"]["isError"])
        self.assertEqual(rec["result"]["structuredContent"]["tools"][0]["id"], "antigravity-proxy")

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
                "params": {"name": "aat_doctor", "arguments": {"os": "windows"}},
            }
        )
        assert doc is not None
        rec_ids = {t["id"] for t in doc["result"]["structuredContent"]["recommended_tools"]}
        self.assertIn("antigravity-junction-skill-fix", rec_ids)

    def test_error_handling_and_resources(self):
        bad_json = self.server.handle_line("{not-json")
        assert bad_json is not None
        self.assertEqual(bad_json["error"]["code"], -32700)

        unknown_method = self.server.handle_request({"jsonrpc": "2.0", "id": 10, "method": "prompts/list"})
        assert unknown_method is not None
        self.assertEqual(unknown_method["error"]["code"], -32601)

        bad_tool = self.server.handle_request(
            {"jsonrpc": "2.0", "id": 11, "method": "tools/call", "params": {"name": "nope", "arguments": {}}}
        )
        assert bad_tool is not None
        self.assertTrue(bad_tool["result"]["isError"])

        bad_cmp = self.server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 12,
                "method": "tools/call",
                "params": {"name": "aat_compare", "arguments": {"tools": ["liftgate"]}},
            }
        )
        assert bad_cmp is not None
        self.assertTrue(bad_cmp["result"]["isError"])

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

    def test_stdio_subprocess_roundtrip(self):
        payload = "\n".join(
            [
                json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}}),
                json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
                json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "aat_recommend", "arguments": {"intent": "硬链接", "lang": "zh"}}}),
            ]
        ) + "\n"
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "mcp_server.py")],
            input=payload,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            check=True,
        )
        lines = [json.loads(line) for line in proc.stdout.strip().splitlines() if line.strip()]
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0]["id"], 1)
        self.assertEqual(lines[1]["id"], 2)
        self.assertEqual(lines[1]["result"]["structuredContent"]["tools"][0]["id"], "antigravity-junction-skill-fix")


if __name__ == "__main__":
    unittest.main()
