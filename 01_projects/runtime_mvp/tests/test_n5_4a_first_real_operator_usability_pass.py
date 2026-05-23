#!/usr/bin/env python3
"""N+5.4A tests: first real daily operator usability pass."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
PYTHON = sys.executable

INDEX_HTML = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html"
LAUNCHER = REPO_ROOT / "03_scripts" / "ghoti_product_launcher.py"
README = REPO_ROOT / "README.md"
DAILY_GUIDE = REPO_ROOT / "docs" / "DAILY_OPERATOR_GUIDE.md"
CODEX_WORKFLOW = REPO_ROOT / "docs" / "CODEX_ONLY_WORKFLOW.md"


def run_launcher(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(LAUNCHER), *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )


class TestDailyOperatorDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_HTML.read_text(encoding="utf-8", errors="replace")

    def test_daily_operator_cards_are_visible(self):
        required = [
            'id="ghoti-daily-operator-card"',
            "Start Here / Daily Operator",
            "Launch dashboard -> Check status truth -> Run smoke/demo -> Review report -> Stop dashboard",
            "python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard",
            "python 03_scripts/ghoti_product_launcher.py --status --json",
            "python 03_scripts/ghoti_product_launcher.py --stop-dashboard",
        ]
        for label in required:
            with self.subTest(label=label):
                self.assertIn(label, self.html)

    def test_status_truth_is_explicit_and_current(self):
        required = [
            'id="ghoti-status-truth-card"',
            "N+5.6B clean/local-model-easy-worker-lane on main",
            "origin/main = c9413108006d920e0110413d3d5e195b504489c1",
            "/home/ai_sandbox/.local/bin/hermes",
            "Hermes Agent v0.14.0",
            "browser/Playwright: degraded/not claimed",
            "Codex provider in Hermes: pending/not proven",
            "Telegram: manual later/no token",
            "No VPS",
            "Ollama available v0.24.0",
            "Gemma model missing/local_demo fallback active",
            "Local Model / Easy Worker Lane reports readiness percentage",
            "Obsidian/local memory present",
            "Public audit: 0 blockers / 7 warnings",
            "Readiness score: 100",
        ]
        for label in required:
            with self.subTest(label=label):
                self.assertIn(label, self.html)

    def test_works_remains_safety_and_codex_prompts_are_visible(self):
        required = [
            'id="ghoti-works-now-card"',
            'id="ghoti-remains-card"',
            'id="ghoti-safety-locks-card"',
            'id="ghoti-ask-codex-next-card"',
            "8 agents / 100 titles / 100 thumbnails / local preview / no posting",
            "Reports under 14_context",
            "Future audited computer-use click/type",
            "No bot/captcha/cloak bypass",
            "No autonomous money/trading/legal actions",
            "Audit current main",
            "Run product smoke test",
            "Build N+5.8A Hermes Agent Workflow",
        ]
        for label in required:
            with self.subTest(label=label):
                self.assertIn(label, self.html)


class TestDailyOperatorLauncher(unittest.TestCase):
    def test_status_json_surfaces_daily_operator_commands(self):
        result = run_launcher("--status", "--json")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        data = json.loads(result.stdout)
        commands = data.get("daily_operator_commands")
        self.assertIsInstance(commands, list)
        rendered = "\n".join(commands)
        for command in [
            "python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard",
            "python 03_scripts/ghoti_product_launcher.py --status --json",
            "python 03_scripts/ghoti_product_launcher.py --smoke --json",
            "python 03_scripts/ghoti_product_launcher.py --local-worker-status --json",
            "python 03_scripts/ghoti_product_launcher.py --local-worker-demo --json",
            "python 03_scripts/ghoti_product_launcher.py --repo-map --json",
            "python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json",
            "python 03_scripts/ghoti_product_launcher.py --stop-dashboard",
        ]:
            with self.subTest(command=command):
                self.assertIn(command, rendered)

    def test_help_mentions_daily_operator_sequence(self):
        result = run_launcher("--help")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("Daily operator sequence", result.stdout)
        self.assertIn("--start-dashboard --open-dashboard", result.stdout)
        self.assertIn("--smoke --json", result.stdout)
        self.assertIn("--stop-dashboard", result.stdout)


class TestDailyOperatorDocs(unittest.TestCase):
    def test_daily_operator_guide_exists_and_covers_safe_use(self):
        self.assertTrue(DAILY_GUIDE.exists())
        text = DAILY_GUIDE.read_text(encoding="utf-8", errors="replace")
        required = [
            "What Ghoti is",
            "python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard",
            "http://127.0.0.1:3210",
            "local_demo fallback",
            "Hermes is currently allowed",
            "UI-TARS is currently allowed",
            "What must remain manual",
            "What not to do",
            "dashboard won't start",
            "port busy",
            "WSL/Hermes not found",
            "Ollama/Gemma missing",
            "public audit warnings",
            "generated residue",
            "launcher PID stale",
        ]
        for label in required:
            with self.subTest(label=label):
                self.assertIn(label, text)

    def test_readme_and_codex_workflow_show_current_baseline(self):
        readme = README.read_text(encoding="utf-8", errors="replace")
        codex = CODEX_WORKFLOW.read_text(encoding="utf-8", errors="replace")
        for text in [readme, codex]:
            with self.subTest(path="baseline"):
                self.assertIn("N+5.6B", text)
                self.assertIn("c9413108006d920e0110413d3d5e195b504489c1", text)
                self.assertIn("python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard", text)
                self.assertIn("no primary worktree mutation", text.lower())
                self.assertIn("no live providers/tokens", text.lower())


class TestNoNewFalseClaims(unittest.TestCase):
    def test_new_usability_copy_does_not_overclaim_autonomy(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in [INDEX_HTML, README, CODEX_WORKFLOW]
        ).lower()
        forbidden = [
            "autonomous operator works",
            "browser control works",
            "gemma is active",
            "codex provider supported",
            "telegram connected",
        ]
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, combined)
