#!/usr/bin/env python3
"""N+5.3A tests: finished local-first supervised operator MVP."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
PYTHON = sys.executable

INDEX_HTML = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html"
SERVER_JS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js"
LAUNCHER = REPO_ROOT / "03_scripts" / "ghoti_product_launcher.py"

CONTROL_CENTER_LABELS = [
    "Product Control Center",
    "Hermes WSL Truth",
    "Gemma / Ollama Lane",
    "Obsidian Compact Memory",
    "Ruflo / Local Brain Bridge",
    "Graphify / Token Plan",
    "UI-TARS Observation Only",
    "Adapter Dry-Runs",
    "External Sandbox",
    "Public Readiness",
    "Model Council",
    "Safety Gates",
]

REQUIRED_DOCS = [
    "docs/CODEX_ONLY_WORKFLOW.md",
    "docs/HERMES_LOCAL_INSTALL_AND_PROVIDER_PLAN.md",
    "docs/OBSIDIAN_COMPACT_MEMORY_PLAN.md",
    "docs/TOKEN_EFFICIENT_COMPUTER_USE_ROADMAP.md",
    "docs/COMPUTER_USE_ROADMAP.md",
    "docs/GITHUB_PROFILE_AND_REPO_UPGRADE_PLAYBOOK.md",
    "docs/REPO_BRANDING_AND_IMAGE_PLAYBOOK.md",
    "docs/BLOCKED_UNSAFE_AUTOMATION.md",
    "infra/README.md",
    "infra/iac_blueprint.yaml",
    "README.md",
    "LICENSE",
    ".env.example",
    ".gitignore",
    "SECURITY.md",
    "CONTRIBUTING.md",
]


def run_py(*args: str, timeout: int = 180) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def load_json(*args: str, timeout: int = 180) -> dict:
    result = run_py(*args, timeout=timeout)
    if result.returncode != 0:
        raise AssertionError(result.stderr + result.stdout)
    return json.loads(result.stdout)


class TestProductControlCenterContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_HTML.read_text(encoding="utf-8", errors="replace")
        cls.server = SERVER_JS.read_text(encoding="utf-8", errors="replace")

    def test_dashboard_static_labels_present(self):
        for label in CONTROL_CENTER_LABELS:
            with self.subTest(label=label):
                self.assertIn(label, self.html)

    def test_product_lanes_are_in_visible_overview_shell(self):
        overview = self.html.find('data-console-view-panel="overview"')
        legacy = self.html.find('id="legacy-compat"')
        self.assertGreater(overview, -1)
        self.assertGreater(legacy, overview)
        self.assertIn('id="overview-product-control-center"', self.html[overview:legacy])
        for label in CONTROL_CENTER_LABELS:
            with self.subTest(label=label):
                self.assertIn(label, self.html[overview:legacy])

    def test_server_status_surfaces_same_lanes(self):
        for label in CONTROL_CENTER_LABELS[1:]:
            with self.subTest(label=label):
                self.assertIn(label, self.server)

    def test_launcher_status_surfaces_same_lanes(self):
        data = load_json("03_scripts/ghoti_product_launcher.py", "--status", "--json")
        self.assertEqual(data["dashboard_url"], "http://127.0.0.1:3210")
        self.assertTrue(data["localhost_only"])
        self.assertFalse(data["external_api"])
        self.assertFalse(data["live_account_actions"])
        self.assertFalse(data["live_posting"])
        labels = [lane["label"] for lane in data.get("control_center_lanes", [])]
        for label in CONTROL_CENTER_LABELS[1:]:
            with self.subTest(label=label):
                self.assertIn(label, labels)

    def test_launcher_command_contract_is_visible(self):
        text = LAUNCHER.read_text(encoding="utf-8")
        self.assertIn("--start-dashboard", text)
        self.assertIn("--open-dashboard", text)
        self.assertIn("http://127.0.0.1", text)
        self.assertNotIn("shell=True", text)
        self.assertNotIn("shell = True", text)


class TestContentDemoMvpContract(unittest.TestCase):
    def test_content_demo_counts_and_local_safety(self):
        data = load_json(
            "03_scripts/supervised_content_studio_demo.py",
            "--run-demo",
            "--topic",
            "N+5.3A local operator control center",
            "--json",
            timeout=240,
        )
        self.assertTrue(data["ok"])
        self.assertEqual(data["agent_count"], 8)
        self.assertEqual(data["title_variant_count"], 100)
        self.assertEqual(data["thumbnail_variant_count"], 100)
        self.assertTrue(data["local_only"])
        self.assertFalse(data["external_api_used"])
        self.assertFalse(data["publish_enabled"])
        self.assertIn("local_preview_path", data)


class TestDocsAndPublicPolish(unittest.TestCase):
    def test_required_docs_and_public_files_exist(self):
        for path in REQUIRED_DOCS:
            with self.subTest(path=path):
                self.assertTrue((REPO_ROOT / path).exists(), path)

    def test_required_docs_explain_local_first_status(self):
        for path in REQUIRED_DOCS[:8]:
            with self.subTest(path=path):
                text = (REPO_ROOT / path).read_text(encoding="utf-8", errors="replace").lower()
                self.assertRegex(text, r"local|manual|approval|blocked|read-only|observation")

    def test_license_env_and_gitignore_are_hardened(self):
        license_text = (REPO_ROOT / "LICENSE").read_text(encoding="utf-8").lower()
        self.assertIn("all rights reserved", license_text)
        self.assertIn("not open source", license_text)

        env_lines = (REPO_ROOT / ".env.example").read_text(encoding="utf-8").splitlines()
        parsed = {
            key: value
            for key, value in (line.split("=", 1) for line in env_lines if line and not line.startswith("#"))
        }
        for key, value in parsed.items():
            with self.subTest(key=key):
                self.assertEqual(value, "true" if key == "LOCAL_ONLY" else "")

        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        for pattern in [".env", ".env.*", "21_repos/third_party/*", "14_context/security/public_repo_audits/*", ".claude/worktrees/"]:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, gitignore)

    def test_readme_branding_and_diagrams(self):
        text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        lower = text.lower()
        self.assertIn("ghoti", lower)
        self.assertRegex(lower, r"fish|supervised operator|local-first")
        image_links = re.findall(r"!\[[^\]]+\]\((docs/assets/github/[^)]+)\)", text)
        self.assertGreaterEqual(len(image_links), 3)
        for link in image_links:
            with self.subTest(link=link):
                self.assertTrue((REPO_ROOT / link).exists(), link)

    def test_unsafe_automation_doc_keeps_bypass_blocked(self):
        text = (REPO_ROOT / "docs" / "BLOCKED_UNSAFE_AUTOMATION.md").read_text(encoding="utf-8").lower()
        for term in ["captcha", "cloak", "fake engagement", "unauthorized desktop control"]:
            with self.subTest(term=term):
                self.assertIn(term, text)
        self.assertGreaterEqual(text.count("blocked"), 2)


class TestCurrentTruthSurfaces(unittest.TestCase):
    def test_hermes_status_truth(self):
        data = load_json("03_scripts/hermes_local_bootstrap.py", "--status", "--json")
        manifest = data["manifest"]
        self.assertTrue(manifest["local_only"])
        self.assertFalse(manifest["paid_vps_required"])
        self.assertFalse(manifest["vps_used"])
        self.assertTrue(manifest["telegram_token_required_from_user"])
        self.assertIn("pending", manifest["codex_provider_truth"])

    def test_model_council_and_adapter_safety(self):
        council = load_json("03_scripts/model_council_tool_intake.py", "--scan", "--json")
        registry = {item["slug"]: item for item in council["registry"]}
        self.assertIn("gemma/ollama", registry)
        self.assertIn("graphify", registry)
        self.assertFalse(council["manifest"]["runtime_wiring_enabled"])
        self.assertFalse(council["manifest"]["bot_detection_bypass_enabled"])
        self.assertEqual(registry["cloak/browser bot-detection"]["status"], "BLOCKED")

        ui_tars = load_json("03_scripts/ui_tars_observation_adapter.py", "--observe", "--dry-run", "--json")
        self.assertTrue(ui_tars["ok"])
        self.assertTrue(ui_tars["dry_run"])
        self.assertFalse(ui_tars["desktop_control"])
        self.assertFalse(ui_tars["external_repo_code_executed"])

        adapter = load_json(
            "03_scripts/approved_adapter_runner.py",
            "--execute-approved",
            "--adapter",
            "agent_skills_eval",
            "--dry-run",
            "--json",
        )
        self.assertTrue(adapter["ok"])
        self.assertTrue(adapter["dry_run"])
        self.assertFalse(adapter["external_code_executed"])
        self.assertFalse(adapter["live_api"])


if __name__ == "__main__":
    unittest.main()
