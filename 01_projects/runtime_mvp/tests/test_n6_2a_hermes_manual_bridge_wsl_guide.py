import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[3]
VERIFIER = REPO_ROOT / "03_scripts" / "hermes_manual_bridge_verifier.py"
LAUNCHER = REPO_ROOT / "03_scripts" / "ghoti_product_launcher.py"
CONTEXT_PACK = REPO_ROOT / "03_scripts" / "ghoti_context_pack_builder.py"
REPO_MAP = REPO_ROOT / "03_scripts" / "ghoti_repo_knowledge_map.py"


class FakeCompleted:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def fake_wsl_run(cmd, timeout=12):
    joined = " ".join(cmd)
    if "pwd" in joined:
        return FakeCompleted(stdout="/mnt/c/Users/ai_sandbox/Documents/AI_Managed_Only\n")
    if "command -v hermes" in joined:
        return FakeCompleted(stdout="/home/ai_sandbox/.local/bin/hermes\n")
    if "hermes --version" in joined:
        return FakeCompleted(stdout="Hermes Agent v0.14.0 (2026.5.16)\n")
    if "hermes skills list" in joined:
        return FakeCompleted(
            stdout=(
                "codex\nclaude-code\nhermes-agent\nmcp\nmemory\nobsidian\n"
                "github\nplan\ntest-driven-development\nbrowser\ncomputer-use\n"
            )
        )
    if "hermes --help" in joined:
        return FakeCompleted(stdout="Usage: hermes [OPTIONS] COMMAND\nCommands: skills status doctor\n")
    if cmd[:2] == ["git", "rev-parse"]:
        return FakeCompleted(stdout="39daf4d81f8a5dc123c9949ce6d7c3ea49763978\n")
    return FakeCompleted(stdout="")


class HermesManualBridgeWslGuideTests(unittest.TestCase):
    def test_status_json_and_wsl_explanation_are_safe(self):
        verifier = load_module(VERIFIER, "hermes_manual_bridge_verifier")
        with mock.patch.object(verifier, "_run", side_effect=fake_wsl_run):
            payload = verifier.build_status(generated_at="2026-05-25T00:00:00Z")
            wsl = verifier.build_wsl_explain(generated_at="2026-05-25T00:00:00Z")

        self.assertEqual(payload["ok"], True)
        self.assertEqual(payload["local_only"], True)
        self.assertEqual(payload["live_api_used"], False)
        self.assertEqual(payload["provider_setup_run"], False)
        self.assertEqual(payload["telegram_setup_run"], False)
        self.assertEqual(payload["tokens_read"], False)
        self.assertEqual(payload["browser_automation_run"], False)
        self.assertEqual(payload["computer_use_run"], False)
        self.assertIn("readiness_percent", payload)
        self.assertIsInstance(payload["readiness_percent"], (int, float))
        self.assertIn("Hermes manual bridge readiness", payload["status_line"])
        self.assertIn("/home/ai_sandbox/.local/bin/hermes", payload["path"])
        self.assertIn("v0.14.0", payload["version"])
        self.assertGreaterEqual(payload["skills_count"], 1)
        self.assertEqual(payload["codex_provider_status"], "pending/not proven")
        self.assertEqual(payload["telegram_status"], "manual later/no token")
        self.assertEqual(payload["browser_playwright_status"], "degraded/not claimed")
        self.assertEqual(payload["no_vps"], True)

        self.assertIn("/mnt/c/Users/ai_sandbox/Documents/AI_Managed_Only", wsl["wsl_repo_path"])
        self.assertIn("C:\\Users\\ai_sandbox\\Documents\\AI_Managed_Only", wsl["windows_repo_path"])
        self.assertIn("ai_sandbox@Ivan-G14:/mnt/c/Users/ai_sandbox$", wsl["prompt_example"])

    def test_safe_and_blocked_commands_are_explicit(self):
        verifier = load_module(VERIFIER, "hermes_manual_bridge_verifier")
        safe = verifier.build_safe_commands(generated_at="2026-05-25T00:00:00Z")
        blocked = verifier.build_blocked_commands(generated_at="2026-05-25T00:00:00Z")

        safe_text = "\n".join(item["command"] for item in safe["safe_commands"])
        blocked_text = "\n".join(item["command"] for item in blocked["blocked_commands"])
        self.assertIn("command -v hermes", safe_text)
        self.assertIn("hermes --version", safe_text)
        self.assertIn("hermes skills list", safe_text)
        self.assertIn("hermes --help", safe_text)
        self.assertIn("hermes setup", blocked_text)
        self.assertIn("hermes login", blocked_text)
        self.assertIn("hermes telegram", blocked_text)
        self.assertIn("hermes browser", blocked_text)
        self.assertTrue(safe["safe_probes_only"])
        self.assertTrue(blocked["provider_setup_blocked"])

    def test_write_guide_creates_expected_files(self):
        verifier = load_module(VERIFIER, "hermes_manual_bridge_verifier")
        runtime_tmp = REPO_ROOT / "01_projects" / "dashboard_mvp" / "runtime_data"
        runtime_tmp.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=runtime_tmp) as tmp:
            with mock.patch.object(verifier, "_run", side_effect=fake_wsl_run):
                result = verifier.write_guide(Path(tmp), generated_at="2026-05-25T00:00:00Z")
            expected = {
                "00_hermes_manual_bridge_status.json",
                "01_wsl_usage_guide.md",
                "02_hermes_safe_commands.md",
                "03_hermes_blocked_commands.md",
                "04_hermes_skills_summary.md",
                "05_hermes_agent_bridge_next_steps.md",
                "06_computer_use_roadmap_note.md",
                "07_apple_comparison_manual_bridge_plan.md",
            }
            self.assertEqual(result["ok"], True)
            self.assertEqual(set(result["paths"].keys()), expected)
            combined = "\n".join((Path(tmp) / name).read_text(encoding="utf-8") for name in expected)

        self.assertIn("C:\\Users\\ai_sandbox\\Documents\\AI_Managed_Only", combined)
        self.assertIn("/mnt/c/Users/ai_sandbox/Documents/AI_Managed_Only", combined)
        self.assertIn("safe probes only", combined)
        self.assertIn("no live provider setup", combined)
        self.assertIn("manual approval", combined)
        self.assertNotRegex(combined, r"sk-[A-Za-z0-9_-]{20,}")
        self.assertNotRegex(combined, r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY")

    def test_launcher_dashboard_docs_context_and_repo_map_surface_manual_bridge(self):
        status = subprocess.run(
            [sys.executable, str(LAUNCHER), "--hermes-manual-status", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=60,
        )
        self.assertEqual(status.returncode, 0, msg=status.stderr or status.stdout)
        payload = json.loads(status.stdout)
        self.assertEqual(payload["ok"], True)
        self.assertEqual(payload["action"], "hermes-manual-status")
        self.assertEqual(payload["local_only"], True)

        index_html = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html").read_text(encoding="utf-8")
        server_js = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js").read_text(encoding="utf-8")
        app_js = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "app.js").read_text(encoding="utf-8")
        launcher_py = LAUNCHER.read_text(encoding="utf-8")

        self.assertIn("Hermes Manual Bridge / WSL Guide", index_html)
        self.assertIn("WSL path mapping", index_html)
        self.assertIn("no live provider setup", index_html)
        self.assertIn("/api/hermes-manual-bridge/status", server_js)
        self.assertIn("/api/hermes-manual-bridge/wsl-explain", server_js)
        self.assertIn("/api/hermes-manual-bridge/safe-commands", server_js)
        self.assertIn("hermes-manual-status", app_js)
        self.assertIn("--hermes-manual-status", launcher_py)
        self.assertIn("--hermes-wsl-guide", launcher_py)
        self.assertIn("--hermes-safe-commands", launcher_py)
        self.assertNotIn("shell: true", server_js)

        required_docs = [
            "docs/WSL_USAGE_GUIDE_FOR_GHOTI.md",
            "docs/HERMES_MANUAL_BRIDGE_VERIFICATION.md",
            "docs/HERMES_SAFE_COMMANDS.md",
            "docs/HERMES_BLOCKED_COMMANDS.md",
            "docs/HERMES_TO_COMPUTER_USE_ROADMAP.md",
            "docs/SAFE_COMPUTER_USE_TEST_PLAN_APPLE_COMPARISON.md",
        ]
        for relpath in required_docs:
            text = (REPO_ROOT / relpath).read_text(encoding="utf-8").lower()
            self.assertIn("no live api", text)

        apple_plan = (REPO_ROOT / "docs" / "SAFE_COMPUTER_USE_TEST_PLAN_APPLE_COMPARISON.md").read_text(encoding="utf-8")
        self.assertIn("Chrome in Incognito", apple_plan)
        self.assertIn("observation-only", apple_plan)
        self.assertIn("manual approval", apple_plan)
        self.assertIn("Do not execute", apple_plan)

        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "01_projects" / "dashboard_mvp" / "runtime_data") as tmp:
            context = subprocess.run(
                [
                    sys.executable,
                    str(CONTEXT_PACK),
                    "--write",
                    "--json",
                    "--output-dir",
                    str(tmp),
                    "--generated-at",
                    "2026-05-25T00:00:00Z",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                timeout=60,
            )
            self.assertEqual(context.returncode, 0, msg=context.stderr or context.stdout)
            pack = (Path(tmp) / "ghoti_current_context_pack.md").read_text(encoding="utf-8")
        self.assertIn("Hermes Manual Bridge / WSL Guide", pack)
        self.assertIn("14_context/hermes_manual_bridge/generated/01_wsl_usage_guide.md", pack)

        bundle = subprocess.run(
            [sys.executable, str(REPO_MAP), "--bundle", "hermes", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=60,
        )
        self.assertEqual(bundle.returncode, 0, msg=bundle.stderr or bundle.stdout)
        bundle_text = json.loads(bundle.stdout)["text"]
        self.assertIn("hermes_manual_bridge_verifier.py", bundle_text)
        self.assertIn("WSL_USAGE_GUIDE_FOR_GHOTI.md", bundle_text)
        self.assertIn("SAFE_COMPUTER_USE_TEST_PLAN_APPLE_COMPARISON.md", bundle_text)


if __name__ == "__main__":
    unittest.main()
