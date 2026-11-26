#!/usr/bin/env python3
"""
Zero-dependency stdio MCP (Model Context Protocol) server for awesome-antigravity-tools.

Exposes catalog search, bilingual intent recommendation, side-by-side comparison,
tool telemetry lookup, ecosystem statistics, local environment diagnostics, and
machine-readable catalog resources over newline-delimited JSON-RPC 2.0.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable, TextIO


SCRIPT_DIR = Path(__file__).resolve().parent


def _resolve_repo_root() -> Path:
    candidate = SCRIPT_DIR.parent
    if (candidate / "data" / "tools.json").exists():
        return candidate
    cwd_candidate = Path.cwd()
    if (cwd_candidate / "data" / "tools.json").exists():
        return cwd_candidate
    return candidate


REPO_ROOT = _resolve_repo_root()
DEFAULT_CATALOG = REPO_ROOT / "data" / "tools.json"
DEFAULT_SNAPSHOT = REPO_ROOT / "data" / "health_snapshot.json"
DEFAULT_LLMS = REPO_ROOT / "docs" / "llms.txt"

try:
    from . import aat_cli
except ImportError:
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    import aat_cli


SERVER_INFO = {
    "name": "awesome-antigravity-tools",
    "version": "2.1.0",
}
SUPPORTED_PROTOCOLS = {"2024-11-05", "2025-03-26", "2025-06-18"}

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "aat_recommend",
        "description": "Recommend 100% Google Antigravity-exclusive tools matching a natural-language goal, workflow, or bug symptom (English or Chinese).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "intent": {"type": "string", "description": "Problem, workflow, or capability query (EN/ZH)."},
                "platform": {"type": "string", "description": "Optional platform filter (Windows, macOS, Linux, VS Code, Antigravity IDE, Cross-Platform, Mobile, Web)."},
                "limit": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
                "lang": {"type": "string", "enum": ["en", "zh"], "default": "en"},
            },
            "required": ["intent"],
        },
    },
    {
        "name": "aat_search",
        "description": "Filter and sort curated Antigravity-exclusive tools by keyword, category, platform, tag, or health status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "default": "", "description": "Space-separated search keywords."},
                "category": {"type": "string", "default": ""},
                "platform": {"type": "string", "default": ""},
                "tag": {"type": "string", "default": ""},
                "status": {"type": "string", "default": ""},
                "sort": {"type": "string", "enum": ["stars", "score", "name", "recent"], "default": "stars"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
            },
        },
    },
    {
        "name": "aat_compare",
        "description": "Compare 2 to 4 Antigravity-exclusive tools side by side on health score, stars, platforms, tags, exclusivity rationale, and install instructions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tools": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                    "maxItems": 4,
                    "description": "2 to 4 tool IDs, names, or owner/repo slugs.",
                },
                "lang": {"type": "string", "enum": ["en", "zh"], "default": "en"},
                "format": {"type": "string", "enum": ["markdown", "json"], "default": "markdown"},
            },
            "required": ["tools"],
        },
    },
    {
        "name": "aat_info",
        "description": "Fetch full metadata, exclusivity rationale, install hint, and live GitHub telemetry for a single curated tool.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tool": {"type": "string", "description": "Tool ID, display name, or owner/repo slug."},
            },
            "required": ["tool"],
        },
    },
    {
        "name": "aat_stats",
        "description": "Return aggregate ecosystem metrics (total tools, combined stars, average health score, category/language/status breakdowns).",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "aat_doctor",
        "description": "Run read-only local Antigravity environment diagnostics (OS, agy CLI, proxy variables, Windows NTFS junctions) and suggest matching catalog fixes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "os": {"type": "string", "enum": ["windows", "macos", "linux"], "description": "Optional OS override."},
                "lang": {"type": "string", "enum": ["en", "zh"], "default": "en"},
            },
        },
    },
]

KNOWN_TOOLS = {t["name"] for t in TOOL_DEFINITIONS}

RESOURCE_DEFINITIONS: list[dict[str, Any]] = [
    {
        "uri": "aat://catalog",
        "name": "Canonical Antigravity Tools Catalog",
        "description": "Single-source-of-truth JSON catalog of all curated 100% Antigravity-exclusive tools.",
        "mimeType": "application/json",
    },
    {
        "uri": "aat://llms.txt",
        "name": "Compact LLMs.txt Directory Index",
        "description": "Concise markdown index of curated Antigravity tools with live stars, health scores, and install hints.",
        "mimeType": "text/plain",
    },
]


class ToolArgumentError(ValueError):
    """Raised when an MCP tool call supplies invalid field values."""


class UnknownResourceError(ValueError):
    """Raised when resources/read requests an unknown URI."""


def _opt_str(args: dict[str, Any], key: str, default: str = "") -> str:
    if key not in args or args[key] is None:
        return default
    val = args[key]
    if not isinstance(val, str):
        raise ToolArgumentError(f"`{key}` must be a string.")
    return val


def _opt_enum(args: dict[str, Any], key: str, allowed: tuple[str, ...], default: str) -> str:
    if key not in args or args[key] is None:
        return default
    val = args[key]
    if not isinstance(val, str) or val not in allowed:
        raise ToolArgumentError(f"`{key}` must be one of: {', '.join(allowed)}.")
    return val


def _opt_int(args: dict[str, Any], key: str, min_val: int, max_val: int, default: int) -> int:
    if key not in args or args[key] is None:
        return default
    val = args[key]
    if isinstance(val, bool) or not isinstance(val, int) or not (min_val <= val <= max_val):
        raise ToolArgumentError(f"`{key}` must be an integer between {min_val} and {max_val}.")
    return val


def _is_valid_jsonrpc_id(req_id: Any) -> bool:
    return isinstance(req_id, str) or (isinstance(req_id, int) and not isinstance(req_id, bool))


class McpCatalogServer:
    """In-process and stdio JSON-RPC 2.0 handler for awesome-antigravity-tools."""

    def __init__(
        self,
        catalog_path: Path = DEFAULT_CATALOG,
        snapshot_path: Path = DEFAULT_SNAPSHOT,
        llms_path: Path = DEFAULT_LLMS,
        *,
        env_probe: dict[str, Any] | Callable[[], dict[str, Any]] | None = None,
    ) -> None:
        self.catalog_path = Path(catalog_path)
        self.snapshot_path = Path(snapshot_path)
        self.llms_path = Path(llms_path)
        self.env_probe = env_probe

    def _load(self) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, dict[str, Any]], list[dict[str, Any]]]:
        return aat_cli.load_enriched_catalog(self.catalog_path, self.snapshot_path)

    @staticmethod
    def _jsonrpc_ok(req_id: Any, result: Any) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    @staticmethod
    def _jsonrpc_err(req_id: Any, code: int, message: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}

    @staticmethod
    def _tool_ok(text: str, structured: Any = None) -> dict[str, Any]:
        res: dict[str, Any] = {
            "content": [{"type": "text", "text": text}],
            "isError": False,
        }
        if structured is not None:
            res["structuredContent"] = structured
        return res

    @staticmethod
    def _tool_err(message: str) -> dict[str, Any]:
        return {
            "content": [{"type": "text", "text": message}],
            "isError": True,
        }

    def _call_tool(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        catalog, health_map, cat_map, enriched = self._load()

        if name == "aat_recommend":
            intent = args.get("intent")
            if not isinstance(intent, str) or not intent.strip():
                raise ToolArgumentError("`intent` must be a non-empty string.")
            platform = _opt_str(args, "platform", "")
            lang = _opt_enum(args, "lang", ("en", "zh"), "en")
            limit = _opt_int(args, "limit", 1, 20, 5)
            recs = aat_cli.recommend_tools(enriched, intent, platform=platform, limit=limit)
            blocks: list[str] = []
            for idx, t in enumerate(recs, 1):
                desc = t["description_zh"] if lang == "zh" else t["description_en"]
                score_s = f"{t['health_score']}/100" if t.get("health_score") is not None else "N/A"
                line = (
                    f"{idx}. {t['name']} ({t['repo']}) | ★{t.get('stars', 0):,} | "
                    f"{t.get('status')} ({score_s}) | match={t['match_score']}\n"
                    f"   {desc}\n"
                    f"   URL: {t['url']}"
                )
                if t.get("install_hint"):
                    line += f"\n   Install: {t['install_hint']}"
                blocks.append(line)
            empty_msg = "未找到匹配的 Antigravity 专有工具。" if lang == "zh" else "No matching Antigravity-exclusive tools found."
            return self._tool_ok("\n".join(blocks) if blocks else empty_msg, {"tools": recs, "count": len(recs)})

        if name == "aat_search":
            query = _opt_str(args, "query", "")
            category = _opt_str(args, "category", "")
            platform = _opt_str(args, "platform", "")
            tag = _opt_str(args, "tag", "")
            status = _opt_str(args, "status", "")
            sort_by = _opt_enum(args, "sort", ("stars", "score", "name", "recent"), "stars")
            limit = _opt_int(args, "limit", 1, 100, 20)
            matched = aat_cli.filter_and_sort_tools(
                enriched,
                query=query,
                category=category,
                platform=platform,
                tag=tag,
                status=status,
                sort_by=sort_by,
            )[:limit]
            lines = [
                f"{idx}. {t['name']} ({t['repo']}) | ★{t.get('stars', 0):,} | "
                f"{t.get('status')} ({t.get('health_score')}/100) | {t['url']}\n   {t['description_en']}"
                for idx, t in enumerate(matched, 1)
            ]
            return self._tool_ok(
                "\n".join(lines) if lines else "No matching tools found.",
                {"tools": matched, "count": len(matched)},
            )

        if name == "aat_compare":
            idents = args.get("tools")
            if not isinstance(idents, list) or not (2 <= len(idents) <= 4) or not all(isinstance(x, str) and x.strip() for x in idents):
                raise ToolArgumentError("`tools` must be an array of 2 to 4 non-empty tool identifiers.")
            lang = _opt_enum(args, "lang", ("en", "zh"), "en")
            fmt = _opt_enum(args, "format", ("markdown", "json"), "markdown")

            resolved: list[dict[str, Any]] = []
            seen_ids: set[str] = set()
            for ident in idents:
                found = aat_cli.find_tool(catalog, health_map, cat_map, ident)
                if not found:
                    raise ToolArgumentError(f"Tool not found: {ident}")
                if found["id"] in seen_ids:
                    raise ToolArgumentError(f"Duplicate tool specified: {found['id']}")
                seen_ids.add(found["id"])
                resolved.append(found)

            text = (
                json.dumps({"tools": resolved}, indent=2, ensure_ascii=False)
                if fmt == "json"
                else aat_cli.render_comparison_markdown(resolved, lang=lang)
            )
            return self._tool_ok(text, {"tools": resolved})

        if name == "aat_info":
            ident = args.get("tool")
            if not isinstance(ident, str) or not ident.strip():
                raise ToolArgumentError("`tool` must be a non-empty string.")
            found = aat_cli.find_tool(catalog, health_map, cat_map, ident)
            if not found:
                raise ToolArgumentError(f"Tool not found: {ident}")
            return self._tool_ok(json.dumps(found, indent=2, ensure_ascii=False), found)

        if name == "aat_stats":
            by_cat = Counter(t["category"] for t in enriched)
            by_lang = Counter(t["language"] or "Unspecified" for t in enriched)
            by_status = Counter(t["status"] for t in enriched)
            scores = [t["health_score"] for t in enriched if isinstance(t["health_score"], (int, float))]
            payload = {
                "total_tools": len(enriched),
                "total_categories": len(catalog.get("categories", [])),
                "total_stars": sum(t.get("stars", 0) for t in enriched),
                "average_health_score": round(sum(scores) / len(scores), 1) if scores else None,
                "by_category": dict(by_cat),
                "by_status": dict(by_status),
                "by_language": dict(by_lang.most_common()),
            }
            return self._tool_ok(json.dumps(payload, indent=2, ensure_ascii=False), payload)

        if name == "aat_doctor":
            raw_os = ""
            if "os" in args and args["os"] is not None:
                raw_os = _opt_enum(args, "os", ("windows", "macos", "linux"), "")
            lang = _opt_enum(args, "lang", ("en", "zh"), "en")
            probe = self.env_probe() if callable(self.env_probe) else self.env_probe
            report = aat_cli.run_doctor(enriched, env_probe=probe, os_override=raw_os)
            env = report["environment"]
            header = (
                f"Antigravity 环境体检 ({env['os']}) | agy CLI: {'是' if env.get('agy_in_path') else '否'}"
                if lang == "zh"
                else f"Antigravity Environment Doctor ({env['os']}) | agy CLI: {'Yes' if env.get('agy_in_path') else 'No'}"
            )
            lines = [header]
            for chk in report["checks"]:
                title = chk["title_zh"] if lang == "zh" else chk["title_en"]
                detail = chk["detail_zh"] if lang == "zh" else chk["detail_en"]
                tool_names = ", ".join(t["name"] for t in chk["tools"])
                lines.append(f"- [{chk['severity'].upper()}] {title}: {detail} -> {tool_names}")
            return self._tool_ok("\n".join(lines), report)

        raise ToolArgumentError(f"Unknown tool: {name}")

    def _read_resource(self, uri: str) -> dict[str, Any]:
        if uri == "aat://catalog":
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": self.catalog_path.read_text(encoding="utf-8"),
                    }
                ]
            }
        if uri == "aat://llms.txt":
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "text/plain",
                        "text": self.llms_path.read_text(encoding="utf-8"),
                    }
                ]
            }
        raise UnknownResourceError(f"Unknown resource URI: {uri}")

    def handle_request(self, req: Any) -> dict[str, Any] | None:
        if not isinstance(req, dict) or req.get("jsonrpc") != "2.0":
            return self._jsonrpc_err(None, -32600, "Invalid Request")

        has_id = "id" in req
        req_id = req.get("id")
        if has_id and not _is_valid_jsonrpc_id(req_id):
            return self._jsonrpc_err(None, -32600, "Invalid Request: `id` must be a string or integer.")

        method = req.get("method")
        if not isinstance(method, str) or not method:
            return self._jsonrpc_err(req_id if has_id else None, -32600, "Invalid Request")

        if not has_id:
            return None

        params = req.get("params")
        if "params" in req and params is not None and not isinstance(params, dict):
            return self._jsonrpc_err(req_id, -32602, "Invalid params: expected JSON object.")

        if method == "initialize":
            req_proto = params.get("protocolVersion") if isinstance(params, dict) else None
            proto = req_proto if isinstance(req_proto, str) and req_proto in SUPPORTED_PROTOCOLS else "2024-11-05"
            return self._jsonrpc_ok(
                req_id,
                {
                    "protocolVersion": proto,
                    "capabilities": {"tools": {}, "resources": {}},
                    "serverInfo": SERVER_INFO,
                },
            )

        if method == "ping":
            return self._jsonrpc_ok(req_id, {})

        if method == "tools/list":
            return self._jsonrpc_ok(req_id, {"tools": TOOL_DEFINITIONS})

        if method == "tools/call":
            if not isinstance(params, dict) or not isinstance(params.get("name"), str) or not params["name"]:
                return self._jsonrpc_err(req_id, -32602, "Invalid params: expected `{name, arguments}`.")
            tool_name = params["name"]
            if tool_name not in KNOWN_TOOLS:
                return self._jsonrpc_err(req_id, -32602, f"Unknown tool: {tool_name}")
            if "arguments" in params and params["arguments"] is not None and not isinstance(params["arguments"], dict):
                return self._jsonrpc_err(req_id, -32602, "Invalid params: `arguments` must be an object.")
            tool_args = params.get("arguments") or {}
            try:
                return self._jsonrpc_ok(req_id, self._call_tool(tool_name, tool_args))
            except ToolArgumentError as exc:
                return self._jsonrpc_ok(req_id, self._tool_err(str(exc)))
            except Exception as exc:
                return self._jsonrpc_ok(req_id, self._tool_err(f"Internal error executing {tool_name}: {exc}"))

        if method == "resources/list":
            return self._jsonrpc_ok(req_id, {"resources": RESOURCE_DEFINITIONS})

        if method == "resources/read":
            if not isinstance(params, dict) or not isinstance(params.get("uri"), str) or not params["uri"]:
                return self._jsonrpc_err(req_id, -32602, "Invalid params: expected `{uri}`.")
            try:
                return self._jsonrpc_ok(req_id, self._read_resource(params["uri"]))
            except UnknownResourceError as exc:
                return self._jsonrpc_err(req_id, -32602, str(exc))
            except (OSError, UnicodeError) as exc:
                return self._jsonrpc_err(req_id, -32603, f"Internal error reading resource: {exc}")

        return self._jsonrpc_err(req_id, -32601, f"Method not found: {method}")

    def handle_line(self, line: str) -> dict[str, Any] | None:
        stripped = line.strip()
        if not stripped:
            return None
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            return self._jsonrpc_err(None, -32700, f"Parse error: {exc}")
        return self.handle_request(payload)

    def serve_streams(self, stdin_stream: TextIO, stdout_stream: TextIO) -> int:
        for line in stdin_stream:
            resp = self.handle_line(line)
            if resp is not None:
                stdout_stream.write(json.dumps(resp, ensure_ascii=False) + "\n")
                stdout_stream.flush()
        return 0


def run_self_test(server: McpCatalogServer) -> int:
    probes = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "aat_stats", "arguments": {}}},
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "aat_recommend", "arguments": {"intent": "windows proxy", "limit": 2}},
        },
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "aat_compare", "arguments": {"tools": ["liftgate", "agy-gyro"]}},
        },
        {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "aat_doctor", "arguments": {"os": "windows"}}},
        {"jsonrpc": "2.0", "id": 7, "method": "resources/list"},
        {"jsonrpc": "2.0", "id": 8, "method": "resources/read", "params": {"uri": "aat://llms.txt"}},
    ]
    for req in probes:
        resp = server.handle_request(req)
        assert resp is not None and "result" in resp, f"MCP self-test failed on {req['method']}: {resp}"
        if req["method"] == "tools/call":
            assert not resp["result"].get("isError"), f"Tool call failed: {resp}"
    print(f"[OK] MCP self-test passed ({len(probes)} JSON-RPC checks, 6 tools, 2 resources).")
    return 0


def _reconfigure_utf8(stream: TextIO, *, newline: str | None = None) -> None:
    reconfig = getattr(stream, "reconfigure", None)
    if callable(reconfig):
        try:
            kwargs: dict[str, Any] = {"encoding": "utf-8", "errors": "replace"}
            if newline is not None:
                kwargs["newline"] = newline
            reconfig(**kwargs)
        except Exception:
            pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Zero-dependency stdio MCP server for awesome-antigravity-tools.")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--llms", type=Path, default=DEFAULT_LLMS)
    parser.add_argument("--self-test", action="store_true", help="Run offline JSON-RPC self-test and exit")
    args = parser.parse_args(argv)

    _reconfigure_utf8(sys.stdin)
    _reconfigure_utf8(sys.stdout, newline="\n")
    _reconfigure_utf8(sys.stderr)

    server = McpCatalogServer(catalog_path=args.catalog, snapshot_path=args.snapshot, llms_path=args.llms)
    if args.self_test:
        return run_self_test(server)
    return server.serve_streams(sys.stdin, sys.stdout)


if __name__ == "__main__":
    raise SystemExit(main())
