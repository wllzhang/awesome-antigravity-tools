"""
Verification tests for generated docs/ site bundle, RSS/XML feeds, and HTML/CSS invariants.
"""

from __future__ import annotations

import json
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import build_site
import export_catalog
import generate_badges


class TestSiteArtifacts(unittest.TestCase):
    def test_bundle_matches_catalog_count_and_has_summary(self):
        catalog = json.loads((REPO_ROOT / "data" / "tools.json").read_text(encoding="utf-8"))
        bundle = json.loads((DOCS_DIR / "catalog-bundle.json").read_text(encoding="utf-8"))
        self.assertEqual(len(bundle["tools"]), len(catalog["tools"]))
        self.assertEqual(bundle["summary"]["total_tools"], len(catalog["tools"]))
        self.assertGreater(bundle["summary"]["total_stars"], 0)

    def test_rss_and_sitemap_are_valid_xml(self):
        rss_root = ET.fromstring((DOCS_DIR / "feed.xml").read_text(encoding="utf-8"))
        self.assertEqual(rss_root.tag, "rss")
        items = rss_root.findall("./channel/item")
        catalog = json.loads((REPO_ROOT / "data" / "tools.json").read_text(encoding="utf-8"))
        self.assertEqual(len(items), len(catalog["tools"]))

        sitemap_root = ET.fromstring((DOCS_DIR / "sitemap.xml").read_text(encoding="utf-8"))
        self.assertTrue(sitemap_root.tag.endswith("urlset"))

    def test_html_and_css_modern_accessibility_invariants(self):
        html = (DOCS_DIR / "index.html").read_text(encoding="utf-8")
        css = (DOCS_DIR / "styles.css").read_text(encoding="utf-8")

        self.assertIn('<meta name="color-scheme" content="light dark">', html)
        self.assertIn('closedby="any"', html)
        self.assertIn('aria-live="polite"', html)
        self.assertIn('class="skip-link"', html)
        self.assertTrue((DOCS_DIR / "styles.css").exists())
        self.assertTrue((DOCS_DIR / "app.js").exists())
        self.assertTrue((DOCS_DIR / "insights.js").exists())
        self.assertTrue((DOCS_DIR / ".nojekyll").exists())

        self.assertIn('meta[name="color-scheme"][content="dark"]', css)
        self.assertIn("overscroll-behavior: contain", css)
        self.assertIn("container-type: inline-size", css)

    def test_build_site_check_mode_passes(self):
        old_argv = sys.argv
        try:
            sys.argv = ["build_site.py", "--check"]
            self.assertEqual(build_site.main(), 0)
        finally:
            sys.argv = old_argv

    def test_exports_check_mode_and_jsonld_integrity(self):
        old_argv = sys.argv
        try:
            sys.argv = ["export_catalog.py", "--check"]
            self.assertEqual(export_catalog.main(), 0)
        finally:
            sys.argv = old_argv

        catalog = json.loads((REPO_ROOT / "data" / "tools.json").read_text(encoding="utf-8"))
        jsonld = json.loads((REPO_ROOT / "data" / "exports" / "catalog.jsonld").read_text(encoding="utf-8"))
        self.assertEqual(jsonld["@type"], "ItemList")
        self.assertEqual(jsonld["numberOfItems"], len(catalog["tools"]))
        self.assertEqual(len(jsonld["itemListElement"]), len(catalog["tools"]))

        csv_lines = (REPO_ROOT / "data" / "exports" / "tools.csv").read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(csv_lines), len(catalog["tools"]) + 1)

    def test_dom_ids_and_i18n_keys_complete(self):
        html = (DOCS_DIR / "index.html").read_text(encoding="utf-8")
        app = (DOCS_DIR / "app.js").read_text(encoding="utf-8")

        html_ids = set(re.findall(r'\bid="([^"]+)"', html))
        js_ids = set(re.findall(r'getElementById\("([^"]+)"\)', app))
        self.assertEqual(js_ids - html_ids, set(), f"Missing HTML IDs: {js_ids - html_ids}")

        i18n_attrs = set(re.findall(r'data-i18n="([^"]+)"', html))
        en_block = re.search(r"en:\s*\{([\s\S]*?)\},\s*zh:", app)
        zh_block = re.search(r"zh:\s*\{([\s\S]*?)\}\s*,?\s*\};", app)
        assert en_block and zh_block
        en_keys = set(re.findall(r"^\s*([A-Za-z0-9_]+):", en_block.group(1), flags=re.MULTILINE))
        zh_keys = set(re.findall(r"^\s*([A-Za-z0-9_]+):", zh_block.group(1), flags=re.MULTILINE))
        self.assertEqual(i18n_attrs - en_keys, set(), f"Missing I18N.en keys: {i18n_attrs - en_keys}")
        self.assertEqual(i18n_attrs - zh_keys, set(), f"Missing I18N.zh keys: {i18n_attrs - zh_keys}")

    def test_badges_check_mode_passes(self):
        old_argv = sys.argv
        try:
            sys.argv = ["generate_badges.py", "--check"]
            self.assertEqual(generate_badges.main(), 0)
        finally:
            sys.argv = old_argv

    def test_native_plugin_manifest_and_skill(self):
        manifest = json.loads((REPO_ROOT / "plugin.json").read_text(encoding="utf-8"))
        allowed_keys = {
            "name",
            "displayName",
            "description",
            "logo",
            "version",
            "author",
            "homepage",
            "repository",
            "suggestedPrompts",
            "disabled",
        }
        self.assertTrue(set(manifest.keys()).issubset(allowed_keys))
        self.assertEqual(manifest["name"], "awesome-antigravity-tools")
        self.assertTrue((REPO_ROOT / manifest["logo"]).exists())
        self.assertTrue((REPO_ROOT / "skills" / "antigravity-tools-advisor" / "SKILL.md").exists())

        mcp_cfg = json.loads((REPO_ROOT / "mcp_config.json").read_text(encoding="utf-8"))
        srv = mcp_cfg.get("mcpServers", {}).get("awesome-antigravity-tools")
        self.assertIsInstance(srv, dict)
        self.assertEqual(srv.get("args"), ["scripts/mcp_server.py"])
        self.assertTrue((REPO_ROOT / "scripts" / "mcp_server.py").exists())

    def test_llms_txt_and_logo_svg_integrity(self):
        llms_path = DOCS_DIR / "llms.txt"
        self.assertTrue(llms_path.exists())
        llms_text = llms_path.read_text(encoding="utf-8")
        catalog = json.loads((REPO_ROOT / "data" / "tools.json").read_text(encoding="utf-8"))
        for tool in catalog["tools"]:
            self.assertIn(tool["name"], llms_text)
            self.assertIn(tool["url"], llms_text)

        src_logo = (REPO_ROOT / "assets" / "logo.svg").read_text(encoding="utf-8").replace("\r\n", "\n")
        dst_logo = (DOCS_DIR / "logo.svg").read_text(encoding="utf-8").replace("\r\n", "\n")
        self.assertEqual(src_logo, dst_logo)

    def test_rss_guids_use_query_tool_deeplinks(self):
        rss_root = ET.fromstring((DOCS_DIR / "feed.xml").read_text(encoding="utf-8"))
        guids = rss_root.findall("./channel/item/guid")
        self.assertGreater(len(guids), 0)
        for guid in guids:
            self.assertEqual(guid.attrib.get("isPermaLink"), "true")
            self.assertIn("?tool=", guid.text or "")
            self.assertNotIn("#tool=", guid.text or "")

    def test_health_check_workflow_stages_all_generated_docs(self):
        wf_text = (REPO_ROOT / ".github" / "workflows" / "health-check.yml").read_text(encoding="utf-8")
        for expected in (
            "docs/catalog-bundle.json",
            "docs/feed.xml",
            "docs/sitemap.xml",
            "docs/robots.txt",
            "docs/llms.txt",
            "docs/logo.svg",
            "docs/.nojekyll",
        ):
            self.assertIn(expected, wf_text)

    def test_discovery_radar_workflow_is_read_only_and_safe(self):
        wf_path = REPO_ROOT / ".github" / "workflows" / "discovery-radar.yml"
        self.assertTrue(wf_path.exists())
        wf_text = wf_path.read_text(encoding="utf-8")
        self.assertIn("contents: read", wf_text)
        self.assertNotIn("contents: write", wf_text)
        self.assertNotIn("issues: write", wf_text)
        self.assertNotIn("pull-requests: write", wf_text)
        for expected in (
            "scripts/discover_candidates.py",
            "discovery_radar.md",
            "discovery_commands.sh",
            "GITHUB_STEP_SUMMARY",
            "actions/upload-artifact@v4",
            "retention-days: 14",
        ):
            self.assertIn(expected, wf_text)
        for line in wf_text.splitlines():
            if "${{ inputs." in line:
                self.assertRegex(line, r"^\s*[A-Z0-9_]+:\s*\$\{\{\s*inputs\.")


if __name__ == "__main__":
    unittest.main()
