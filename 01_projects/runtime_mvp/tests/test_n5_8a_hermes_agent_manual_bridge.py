import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
HERMES_BRIDGE = REPO_ROOT / "03_scripts" / "hermes_agent_workflow_bridge.py"
LAUNCHER = REPO_ROOT / "03_scripts" / "ghoti_product_launcher.py"
CONTEXT_PACK = REPO_ROOT / "03_scripts" / "ghoti_context_pack_builder.py"
REPO_MAP = REPO_ROOT / "03_scripts" / "ghoti_repo_knowledge_map.py"

LAUNCHER_COMMAND = "python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard"
HERMES_STATUS_COMMAND = "python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json"
HERMES_WRITE_COMMAND = "python 03_scripts/ghoti_product_launcher.py --hermes-bridge-write --json"


class GhotiHermesAgentManualBridgeTests(unittest.TestCase):
    def _run_bridge(self, *args, output_dir=None):
        command = [sys.executable, str(HERMES_BRIDGE), *args, "--json"]
        if output_dir is not None:
            command.extend(["--output-dir", str(output_dir)])
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=60,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"Hermes bridge failed\nstdout={completed.stdout}\nstderr={completed.stderr}",
        )
        return json.loads(completed.stdout)

    def test_status_json_is_safe_truthful_and_has_readiness(self):
        payload = self._run_bridge("--status")

        self.assertEqual(payload["ok"], True)
        self.assertEqual(payload["local_only"], True)
        self.assertEqual(payload["live_api_used"], False)
        self.assertEqual(payload["provider_setup_run"], False)
        self.assertEqual(payload["telegram_setup_run"], False)
        self.assertEqual(payload["tokens_read"], False)
        self.assertIn("readiness_percent", payload)
        self.assertIsInstance(payload["readiness_percent"], (int, float))
        self.assertGreaterEqual(payload["readiness_percent"], 0)
        self.assertLessEqual(payload["readiness_percent"], 100)
        self.assertIn("Hermes workflow readiness", payload["status_line"])
        self.assertIn("safe_commands", payload)
        self.assertIn("blocked_commands", payload)
        safe_joined = "\n".join(payload["safe_commands"])
        blocked_joined = "\n".join(payload["blocked_commands"])
        self.assertIn("command -v hermes", safe_joined)
        self.assertIn("hermes --version", safe_joined)
        self.assertIn("hermes skills list", safe_joined)
        self.assertIn("hermes setup", blocked_joined)
        self.assertIn("provider config", blocked_joined)
        self.assertIn("Telegram", blocked_joined)
        self.assertEqual(payload["codex_provider_status"], "pending/not proven")
        self.assertEqual(payload["telegram_status"], "manual later/no token")
        self.assertEqual(payload["browser_playwright_status"], "degraded/not claimed")
        self.assertEqual(payload["no_vps"], True)

    def test_doctor_skills_index_and_manual_plan_are_local_only(self):
        doctor = self._run_bridge("--doctor")
        self.assertEqual(doctor["ok"], True)
        self.assertIn("checks", doctor)
        self.assertEqual(doctor["safety"]["no_live_apis"], True)
        self.assertEqual(doctor["safety"]["no_provider_setup"], True)

        skills = self._run_bridge("--skills-index")
        self.assertEqual(skills["ok"], True)
        self.assertIn("skills", skills)
        self.assertIn("important_skills", skills)
        self.assertIn("codex", skills["important_skill_names"])
        self.assertIn("hermes-agent", skills["important_skill_names"])
        self.assertIn("mcp", skills["important_skill_names"])
        self.assertIn(skills["skills_status"], {"visible", "unavailable"})

        plan = self._run_bridge("--manual-plan")
        self.assertEqual(plan["ok"], True)
        self.assertIn("manual_steps", plan)
        self.assertIn("human-approved", "\n".join(plan["manual_steps"]))
        self.assertIn("blocked_until_later", plan)
        self.assertIn("provider setup", "\n".join(plan["blocked_until_later"]))

    def test_write_readiness_creates_expected_safe_files(self):
        runtime_tmp = REPO_ROOT / "01_projects" / "dashboard_mvp" / "runtime_data"
        runtime_tmp.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=runtime_tmp) as tmp:
            output_dir = Path(tmp)
            payload = self._run_bridge("--write-readiness", output_dir=output_dir)

            expected = {
                "hermes_workflow_status.json",
                "hermes_workflow_status.md",
                "hermes_skills_index.json",
                "hermes_skills_index.md",
                "hermes_manual_setup_checklist.md",
                "hermes_safe_next_steps.md",
                "hermes_codex_provider_plan.md",
                "hermes_telegram_manual_plan.md",
                "hermes_browser_playwright_remediation_plan.md",
                "hermes_operator_bridge_packet.md",
            }
            self.assertEqual(payload["ok"], True)
            self.assertEqual(set(payload["paths"].keys()), expected)
            for filename in expected:
                self.assertTrue((output_dir / filename).exists(), filename)

            combined = "\n".join(
                path.read_text(encoding="utf-8")
                for path in output_dir.iterdir()
                if path.is_file()
            )
            self.assertIn(HERMES_STATUS_COMMAND, combined)
            self.assertIn(HERMES_WRITE_COMMAND, combined)
            self.assertIn(LAUNCHER_COMMAND, combined)
            self.assertIn("safe probes only", combined)
            self.assertIn("no live provider setup", combined)
            self.assertIn("Codex provider pending/not proven", combined)
            self.assertIn("Telegram manual later/no token", combined)
            self.assertIn("browser/Playwright degraded/not claimed", combined)
            self.assertNotRegex(combined, r"sk-[A-Za-z0-9_-]{20,}")
            self.assertNotRegex(combined, r"ghp_[A-Za-z0-9_]{20,}")
            self.assertNotRegex(combined, r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY")

    def test_launcher_dashboard_and_docs_surface_hermes_manual_bridge(self):
        status = subprocess.run(
            [sys.executable, str(LAUNCHER), "--hermes-bridge-status", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=60,
        )
        self.assertEqual(status.returncode, 0, msg=status.stderr or status.stdout)
        payload = json.loads(status.stdout)
        self.assertEqual(payload["ok"], True)
        self.assertEqual(payload["action"], "hermes-bridge-status")

        index_html = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html").read_text(encoding="utf-8")
        server_js = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js").read_text(encoding="utf-8")
        app_js = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "app.js").read_text(encoding="utf-8")
        launcher_py = LAUNCHER.read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        daily_guide = (REPO_ROOT / "docs" / "DAILY_OPERATOR_GUIDE.md").read_text(encoding="utf-8")
        hermes_plan = (REPO_ROOT / "docs" / "HERMES_LOCAL_INSTALL_AND_PROVIDER_PLAN.md").read_text(encoding="utf-8")

        self.assertIn("Hermes Agent / Manual Bridge", index_html)
        self.assertIn("readiness percentage", index_html)
        self.assertIn("Codex provider pending/not proven", index_html)
        self.assertIn("Telegram manual", index_html)
        self.assertIn("browser/Playwright degraded", index_html)
        self.assertIn("no live provider setup", index_html)
        self.assertIn("safe probes only", index_html)
        self.assertIn("/api/hermes-bridge/status", server_js)
        self.assertIn("/api/hermes-bridge/skills-index", server_js)
        self.assertIn("/api/hermes-bridge/write-readiness", server_js)
        self.assertIn("/api/hermes-bridge/status", app_js)
        self.assertIn("--hermes-bridge-status", launcher_py)
        self.assertIn("--hermes-bridge-write", launcher_py)
        self.assertNotIn("shell: true", server_js)
        self.assertIn("HERMES_AGENT_WORKFLOW_GUIDE.md", readme)
        self.assertIn("HERMES_MANUAL_PROVIDER_SETUP_CHECKLIST.md", daily_guide)
        self.assertIn("manual bridge", hermes_plan.lower())

    def test_context_pack_and_repo_bundle_reference_hermes_bridge_readiness(self):
        runtime_tmp = REPO_ROOT / "01_projects" / "dashboard_mvp" / "runtime_data"
        runtime_tmp.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=runtime_tmp) as tmp:
            output_dir = Path(tmp)
            context = subprocess.run(
                [
                    sys.executable,
                    str(CONTEXT_PACK),
                    "--write",
                    "--json",
                    "--output-dir",
                    str(output_dir),
                    "--generated-at",
                    "2026-05-23T00:00:00Z",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                timeout=60,
            )
            self.assertEqual(context.returncode, 0, msg=context.stderr or context.stdout)
            pack = (output_dir / "ghoti_current_context_pack.md").read_text(encoding="utf-8")
            self.assertIn("Hermes Agent / Manual Bridge", pack)
            self.assertIn("14_context/hermes_workflow/generated/hermes_workflow_status.md", pack)
            self.assertIn("Hermes setup remains manual later", pack)

        bundle = subprocess.run(
            [sys.executable, str(REPO_MAP), "--bundle", "hermes", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=60,
        )
        self.assertEqual(bundle.returncode, 0, msg=bundle.stderr or bundle.stdout)
        bundle_payload = json.loads(bundle.stdout)
        text = bundle_payload["text"]
        self.assertIn("hermes_agent_workflow_bridge.py", text)
        self.assertIn("HERMES_AGENT_WORKFLOW_GUIDE.md", text)
        self.assertIn("safe probes only", text)
        self.assertIn("provider setup", text)
        self.assertIn("no live APIs", text)


if __name__ == "__main__":
    unittest.main()
