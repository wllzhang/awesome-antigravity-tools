"""
Comprehensive offline unit & integration test suite for awesome-antigravity-tools.

Run with:
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import copy
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import aat_cli
import discover_candidates
import generate_badges
import generate_docs
import parse_submission
import validate_catalog


def _load_health_check():
    spec = importlib.util.spec_from_file_location("health_check", SCRIPTS_DIR / "health-check.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


health_check = _load_health_check()


def make_sample_catalog() -> dict:
    return {
        "schema_version": "1.0.0",
        "repository": "wllzhang/awesome-antigravity-tools",
        "categories": [
            {
                "id": "ide-extensions-cockpits",
                "icon": "🖥️",
                "name_en": "IDE Extensions & Cockpits",
                "name_zh": "IDE 扩展与专属控制台",
                "description_en": "Extensions built exclusively for Antigravity.",
                "description_zh": "专为 Antigravity 打造的扩展。",
            }
        ],
        "tools": [
            {
                "id": "alpha-tool",
                "name": "AlphaTool",
                "repo": "acme/alpha-tool",
                "url": "https://github.com/acme/alpha-tool",
                "category": "ide-extensions-cockpits",
                "description_en": "Monitors Antigravity model quotas in real time.",
                "description_zh": "实时监控 Antigravity 模型配额。",
                "exclusivity_reason_en": "Connects directly to Antigravity local language server.",
                "exclusivity_reason_zh": "直接连接 Antigravity 本地语言服务器。",
                "platforms": ["VS Code", "Windows"],
                "tags": ["VS Code", "Quota"],
                "install_hint": "Install VSIX from releases",
                "added_at": "2026-11-18",
            },
            {
                "id": "beta-tool",
                "name": "BetaTool",
                "repo": "acme/beta-tool",
                "url": "https://github.com/acme/beta-tool",
                "category": "ide-extensions-cockpits",
                "description_en": "Switches Antigravity IDE profiles cleanly.",
                "description_zh": "一键切换 Antigravity IDE 配置文件。",
                "exclusivity_reason_en": "Manages Antigravity local profile stores natively.",
                "exclusivity_reason_zh": "原生管理 Antigravity 本地配置存储。",
                "platforms": ["Cross-Platform"],
                "tags": ["Rust", "Desktop"],
                "added_at": "2026-11-18",
            },
        ],
    }


class TestCatalogValidator(unittest.TestCase):
    def test_real_catalog_passes_strictly(self):
        real = json.loads((REPO_ROOT / "data" / "tools.json").read_text(encoding="utf-8"))
        errors, warnings = validate_catalog.validate_catalog_data(real)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        ok_tpl, _ = validate_catalog.validate_issue_template_categories(real)
        self.assertTrue(ok_tpl)

    def test_issue_template_category_drift_and_auto_sync(self):
        with tempfile.TemporaryDirectory() as tmp:
            tpl = Path(tmp) / "submit_tool.yml"
            tpl.write_text(
                (REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "submit_tool.yml").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            sample = make_sample_catalog()
            ok_before, _ = validate_catalog.validate_issue_template_categories(sample, tpl)
            self.assertFalse(ok_before)
            self.assertTrue(validate_catalog.sync_issue_template_categories(sample, tpl))
            ok_after, _ = validate_catalog.validate_issue_template_categories(sample, tpl)
            self.assertTrue(ok_after)

    def test_rejects_duplicate_repo_and_self_reference(self):
        cat = make_sample_catalog()
        dup = copy.deepcopy(cat["tools"][0])
        dup["id"] = "alpha-dup"
        dup["name"] = "AlphaDup"
        cat["tools"].append(dup)
        errors, _ = validate_catalog.validate_catalog_data(cat)
        self.assertTrue(any("duplicate repository" in e for e in errors))

        cat2 = make_sample_catalog()
        cat2["tools"][0]["repo"] = "wllzhang/awesome-antigravity-tools"
        cat2["tools"][0]["url"] = "https://github.com/wllzhang/awesome-antigravity-tools"
        errors2, _ = validate_catalog.validate_catalog_data(cat2)
        self.assertTrue(any("must not reference itself" in e for e in errors2))

    def test_rejects_bad_punctuation_and_invalid_platform(self):
        cat = make_sample_catalog()
        cat["tools"][0]["description_en"] = "lowercase description without period"
        cat["tools"][0]["description_zh"] = "这是一个缺少中文句号的测试描述"
        cat["tools"][0]["platforms"] = ["Solaris"]
        errors, _ = validate_catalog.validate_catalog_data(cat)
        self.assertTrue(any("start with a capital letter" in e for e in errors))
        self.assertTrue(any("end with a period" in e for e in errors))
        self.assertTrue(any("end with '。'" in e for e in errors))
        self.assertTrue(any("invalid platforms" in e for e in errors))

    def test_warns_on_hyperbole_and_unsorted_order(self):
        cat = make_sample_catalog()
        cat["tools"][0]["description_en"] = "The best revolutionary quota monitor for Antigravity."
        cat["tools"].reverse()
        errors, warnings = validate_catalog.validate_catalog_data(cat)
        self.assertEqual(errors, [])
        self.assertTrue(any("promotional language" in w for w in warnings))
        self.assertTrue(any("alphabetically sorted" in w for w in warnings))


class TestDocsGenerator(unittest.TestCase):
    def test_renders_bilingual_with_archived_tag_and_accurate_badge(self):
        cat = make_sample_catalog()
        snap = {
            "generated_at": "2026-11-18T00:00:00Z",
            "repositories": [
                {"full_name": "acme/alpha-tool", "status": "HEALTHY", "stars": 1500, "health_score": 92},
                {"full_name": "acme/beta-tool", "status": "ARCHIVED", "stars": 300, "health_score": 25},
            ],
        }
        en = generate_docs.render_readme_en(cat, snap)
        zh = generate_docs.render_readme_zh(cat, snap)
        self.assertIn("`[Archived]` Switches Antigravity IDE profiles cleanly.", en)
        self.assertIn("`[Archived]` 一键切换 Antigravity IDE 配置文件。", zh)
        self.assertIn("1/2%20Active%20%2850%25%29", en)
        self.assertIn("1.8k", en)
        self.assertIn("CONTRIBUTING.zh-CN.md", zh)

    def test_real_readmes_are_in_sync(self):
        real_cat = json.loads((REPO_ROOT / "data" / "tools.json").read_text(encoding="utf-8"))
        snap = generate_docs.load_json(REPO_ROOT / "data" / "health_snapshot.json")
        self.assertTrue(
            generate_docs.write_or_check(
                REPO_ROOT / "README.md", generate_docs.render_readme_en(real_cat, snap), check_only=True
            )
        )
        self.assertTrue(
            generate_docs.write_or_check(
                REPO_ROOT / "README.zh-CN.md", generate_docs.render_readme_zh(real_cat, snap), check_only=True
            )
        )

    def test_github_anchors_match_all_readme_headings(self):
        import re

        self.assertEqual(generate_docs.github_anchor("🖥️ IDE Extensions & Cockpits"), "\ufe0f-ide-extensions--cockpits")
        self.assertEqual(generate_docs.github_anchor("🏷️ Badge"), "\ufe0f-badge")
        for fname in ("README.md", "README.zh-CN.md"):
            text = (REPO_ROOT / fname).read_text(encoding="utf-8")
            valid_anchors = {
                f"#{generate_docs.github_anchor(m.group(1))}" for m in re.finditer(r"^##+\s+(.+)$", text, flags=re.MULTILINE)
            }
            for link in re.findall(r"\]\((#[^)]+)\)", text):
                self.assertIn(link, valid_anchors, f"Broken TOC anchor {link!r} in {fname}")


class TestHealthEngineV2(unittest.TestCase):
    def test_health_score_bounds_and_penalties(self):
        high = health_check.compute_health_score("HEALTHY", 2, 5000, 120, "MIT", True, 5, True)
        self.assertEqual(high, 100)

        stale = health_check.compute_health_score("STALE", 250, 100, 10, "Apache-2.0", True, 2, False)
        self.assertLess(stale, high)
        self.assertGreater(stale, 40)

        archived = health_check.compute_health_score("ARCHIVED", 5, 10000, 500, "MIT", True, 4, True)
        self.assertLessEqual(archived, 25)

        dead = health_check.compute_health_score("DEAD", 0, 0, 0, None, False, 0, False)
        self.assertEqual(dead, 0)

    def test_audit_mocked_http_and_history_retention(self):
        repos = [
            {
                "id": "a",
                "title": "Alpha",
                "url": "https://github.com/acme/alpha",
                "owner": "acme",
                "repo": "alpha",
                "full_name": "acme/alpha",
                "section": "IDE",
                "section_zh": "IDE",
            },
            {
                "id": "b",
                "title": "Gone",
                "url": "https://github.com/acme/gone",
                "owner": "acme",
                "repo": "gone",
                "full_name": "acme/gone",
                "section": "IDE",
                "section_zh": "IDE",
            },
        ]

        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        def fake_repo(owner, repo, token="", retries=3):
            if repo == "alpha":
                return 200, {
                    "archived": False,
                    "disabled": False,
                    "stargazers_count": 600,
                    "forks_count": 40,
                    "open_issues_count": 3,
                    "language": "Rust",
                    "license": {"spdx_id": "MIT"},
                    "default_branch": "main",
                    "pushed_at": now_iso,
                    "topics": ["antigravity"],
                    "description": "Antigravity tool",
                }
            return 404, {"error": "Not found"}

        with mock.patch.object(health_check, "query_github_repo", side_effect=fake_repo), mock.patch.object(
            health_check, "query_latest_release", return_value=("v1.2.0", now_iso)
        ):
            results = health_check.audit_repositories(repos, fetch_releases=True)

        self.assertEqual(results[0]["status"], "HEALTHY")
        self.assertEqual(results[0]["latest_release"], "v1.2.0")
        self.assertEqual(results[1]["status"], "DEAD")
        self.assertEqual(results[1]["health_score"], 0)

        snap = health_check.build_snapshot_payload(results, datetime(2026, 11, 18, 2, 0, tzinfo=timezone.utc))
        prev = {
            "repositories": [
                {"full_name": "acme/alpha", "status": "HEALTHY", "stars": 590},
                {"full_name": "acme/gone", "status": "HEALTHY", "stars": 10},
            ]
        }
        changes = health_check.detect_status_changes(snap, prev)
        self.assertEqual(changes, [{"repo": "acme/gone", "from": "HEALTHY", "to": "DEAD"}])

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            hist_path = tmp_path / "history.json"
            health_check.update_health_history(hist_path, snap, status_changes=changes, max_days=30)
            # Second update same day should deduplicate
            health_check.update_health_history(hist_path, snap, status_changes=changes, max_days=30)
            hist = json.loads(hist_path.read_text(encoding="utf-8"))
            self.assertEqual(len(hist["entries"]), 1)

            rep_en = tmp_path / "report.md"
            issue_md = tmp_path / "issue.md"
            _, action_count = health_check.generate_report_en(
                snap, rep_en, issue_file=issue_md, previous_snapshot=prev, status_changes=changes
            )
            self.assertEqual(action_count, 1)
            self.assertTrue(issue_md.exists())
            self.assertIn("(+10)", rep_en.read_text(encoding="utf-8"))
            self.assertIn("Status Transitions Since Last Audit", rep_en.read_text(encoding="utf-8"))

            rep_zh = tmp_path / "report.zh.md"
            health_check.generate_report_zh(snap, rep_zh, previous_snapshot=prev, status_changes=changes)
            zh_txt = rep_zh.read_text(encoding="utf-8")
            self.assertIn("(+10)", zh_txt)
            self.assertIn("上次巡检以来的状态变更", zh_txt)
            self.assertIn("需维护者处理的仓库", zh_txt)


class TestBadgesAndDiscovery(unittest.TestCase):
    def test_badge_payloads(self):
        cat = make_sample_catalog()
        snap = {
            "summary": {
                "total": 2,
                "healthy": 2,
                "health_ratio_pct": 100.0,
                "total_stars": 12450,
                "average_health_score": 88.5,
            }
        }
        badges = generate_badges.build_badges(cat, snap)
        self.assertEqual(badges["stars.json"]["message"], "12.4k")
        self.assertEqual(badges["health.json"]["color"], "brightgreen")
        self.assertEqual(badges["score.json"]["message"], "88.5/100")

    def test_discovery_scoring_separates_native_vs_generic_noise(self):
        native = {
            "name": "antigravity-quota-hud",
            "description": "Real-time Antigravity IDE quota HUD using local language server.",
            "language": "TypeScript",
            "stargazers_count": 320,
            "license": {"spdx_id": "MIT"},
        }
        generic = {
            "name": "awesome-ai-prompts",
            "description": "Prompt collection and skill pack for Claude Code, Codex, Cursor, Windsurf, Copilot, and Antigravity.",
            "language": None,
            "stargazers_count": 5000,
            "license": {"spdx_id": "MIT"},
        }
        native_score, _ = discover_candidates.score_candidate(native)
        generic_score, _ = discover_candidates.score_candidate(generic)
        self.assertGreaterEqual(native_score, 80)
        self.assertLess(generic_score, 30)


class TestCliAndSubmissionParser(unittest.TestCase):
    def test_cli_search_stats_and_add(self):
        with tempfile.TemporaryDirectory() as tmp:
            cat_path = Path(tmp) / "tools.json"
            cat_path.write_text(json.dumps(make_sample_catalog()), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = aat_cli.main(["--catalog", str(cat_path), "search", "quota", "--json"])
            self.assertEqual(rc, 0)
            items = json.loads(buf.getvalue())
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0]["id"], "alpha-tool")

            rc_add = aat_cli.main(
                [
                    "--catalog",
                    str(cat_path),
                    "add",
                    "--repo",
                    "acme/gamma-acp",
                    "--category",
                    "ide-extensions-cockpits",
                    "--desc-en",
                    "Streams Antigravity ACP events into a local inspector.",
                    "--desc-zh",
                    "将 Antigravity ACP 事件流式输出到本地检查器。",
                    "--reason-en",
                    "Built specifically for Antigravity agy acp protocol inspection.",
                    "--reason-zh",
                    "专为 Antigravity agy acp 协议调试而设计。",
                    "--platforms",
                    "Cross-Platform",
                    "--tags",
                    "ACP,CLI",
                ]
            )
            self.assertEqual(rc_add, 0)
            updated = json.loads(cat_path.read_text(encoding="utf-8"))
            self.assertEqual(len(updated["tools"]), 3)

    def test_submission_parser_valid_and_duplicate(self):
        cat = make_sample_catalog()
        valid_body = """
### Tool Name

GammaBridge

### Repository / Project URL

https://github.com/acme/gamma-bridge

### Category

IDE Extensions & Cockpits

### One-line Description (English)

Bridges Antigravity IDE session events to local webhooks.

### Antigravity Exclusivity Rationale

Hooks directly into Antigravity IDE SessionStart and Stop lifecycle events.

### Platforms

Windows, macOS

### Tags

CLI, Hooks
"""
        entry, errors = parse_submission.build_candidate_entry(parse_submission.parse_issue_form(valid_body), cat)
        self.assertEqual(errors, [])
        self.assertEqual(entry["repo"], "acme/gamma-bridge")
        self.assertEqual(entry["category"], "ide-extensions-cockpits")
        comment = parse_submission.render_triage_comment(entry, errors)
        self.assertIn("<!-- aat-submission-triage -->", comment)

        dup_body = valid_body.replace("acme/gamma-bridge", "acme/alpha-tool")
        _, dup_errors = parse_submission.build_candidate_entry(parse_submission.parse_issue_form(dup_body), cat)
        self.assertTrue(any("Duplicate submission" in e for e in dup_errors))

    def test_cli_recommend_and_compare(self):
        real_cat = REPO_ROOT / "data" / "tools.json"
        real_snap = REPO_ROOT / "data" / "health_snapshot.json"

        buf_en = io.StringIO()
        with redirect_stdout(buf_en):
            rc_en = aat_cli.main(
                ["--catalog", str(real_cat), "--snapshot", str(real_snap), "recommend", "windows proxy", "--json"]
            )
        self.assertEqual(rc_en, 0)
        recs_en = json.loads(buf_en.getvalue())
        self.assertGreaterEqual(len(recs_en), 1)
        self.assertEqual(recs_en[0]["id"], "antigravity-proxy")
        self.assertGreater(recs_en[0]["match_score"], 0)

        buf_zh = io.StringIO()
        with redirect_stdout(buf_zh):
            rc_zh = aat_cli.main(
                ["--catalog", str(real_cat), "--snapshot", str(real_snap), "recommend", "硬链接", "--lang", "zh", "--json"]
            )
        self.assertEqual(rc_zh, 0)
        recs_zh = json.loads(buf_zh.getvalue())
        self.assertEqual(recs_zh[0]["id"], "antigravity-junction-skill-fix")

        buf_cmp = io.StringIO()
        with redirect_stdout(buf_cmp):
            rc_cmp = aat_cli.main(
                ["--catalog", str(real_cat), "--snapshot", str(real_snap), "compare", "liftgate", "agy-gyro", "--markdown"]
            )
        self.assertEqual(rc_cmp, 0)
        md_out = buf_cmp.getvalue()
        self.assertIn("liftgate", md_out)
        self.assertIn("agy-gyro", md_out)

        rc_bad = aat_cli.main(["--catalog", str(real_cat), "--snapshot", str(real_snap), "compare", "liftgate"])
        self.assertEqual(rc_bad, 1)


if __name__ == "__main__":
    unittest.main()
