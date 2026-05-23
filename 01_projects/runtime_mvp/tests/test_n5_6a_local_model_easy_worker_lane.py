import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
LOCAL_WORKER = REPO_ROOT / "03_scripts" / "local_model_worker_lane.py"
LAUNCHER_COMMAND = "python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard"
CONTEXT_PACK_COMMAND = "python 03_scripts/ghoti_product_launcher.py --context-pack --json"
WORKER_STATUS_COMMAND = "python 03_scripts/ghoti_product_launcher.py --local-worker-status --json"
WORKER_DEMO_COMMAND = "python 03_scripts/ghoti_product_launcher.py --local-worker-demo --json"


class GhotiLocalModelEasyWorkerLaneTests(unittest.TestCase):
    def _run_worker(self, *args, output_dir=None):
        command = [sys.executable, str(LOCAL_WORKER), *args, "--json"]
        if output_dir is not None:
            command.extend(["--output-dir", str(output_dir)])
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=45,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"local worker failed\nstdout={completed.stdout}\nstderr={completed.stderr}",
        )
        return json.loads(completed.stdout)

    def test_status_json_is_truthful_safe_and_has_readiness(self):
        payload = self._run_worker("--status")

        self.assertEqual(payload["ok"], True)
        self.assertEqual(payload["local_only"], True)
        self.assertEqual(payload["live_api_used"], False)
        self.assertEqual(payload["external_api_used"], False)
        self.assertEqual(payload["auto_downloads_enabled"], False)
        self.assertEqual(payload["ollama_pull_run"], False)
        self.assertIn("readiness_percent", payload)
        self.assertIsInstance(payload["readiness_percent"], (int, float))
        self.assertGreaterEqual(payload["readiness_percent"], 0)
        self.assertLessEqual(payload["readiness_percent"], 100)
        self.assertIn(payload["active_mode"], {"local_demo", "ollama_gemma"})
        self.assertIn("ollama", payload)
        self.assertIn("gemma", payload)
        self.assertIn("safe_demo_tasks", payload)
        self.assertIn("status-paragraph", payload["safe_demo_tasks"])
        self.assertIn("summarize-latest-report", payload["safe_demo_tasks"])
        self.assertIn("codex-next-prompt", payload["safe_demo_tasks"])

        if not payload["gemma"]["installed"]:
            self.assertEqual(payload["active_mode"], "local_demo")
            self.assertIn("local_demo fallback", payload["status_line"])

    def test_doctor_and_demo_tasks_return_compact_local_outputs(self):
        doctor = self._run_worker("--doctor")
        self.assertEqual(doctor["ok"], True)
        self.assertEqual(doctor["local_only"], True)
        self.assertIn("checks", doctor)
        self.assertIn("manual_next_commands", doctor)
        self.assertIn("ollama list", "\n".join(doctor["manual_next_commands"]))
        self.assertIn("ollama pull", "\n".join(doctor["manual_next_commands"]))

        status_demo = self._run_worker("--demo-task", "status-paragraph")
        self.assertEqual(status_demo["ok"], True)
        self.assertEqual(status_demo["task"], "status-paragraph")
        self.assertIn("Local worker readiness", status_demo["text"])
        self.assertIn(LAUNCHER_COMMAND, status_demo["text"])
        self.assertLessEqual(len(status_demo["text"]), 1200)

        prompt_demo = self._run_worker("--demo-task", "codex-next-prompt")
        self.assertEqual(prompt_demo["ok"], True)
        self.assertIn("Use only repo-contained worktrees", prompt_demo["text"])
        self.assertIn(CONTEXT_PACK_COMMAND, prompt_demo["text"])

    def test_write_demo_output_creates_expected_safe_files(self):
        runtime_tmp = REPO_ROOT / "01_projects" / "dashboard_mvp" / "runtime_data"
        runtime_tmp.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=runtime_tmp) as tmp:
            output_dir = Path(tmp)
            payload = self._run_worker("--write-demo-output", output_dir=output_dir)

            expected_files = {
                "local_worker_status.json",
                "local_worker_status.md",
                "latest_report_summary.md",
                "status_paragraph.md",
                "codex_next_prompt_from_context.md",
            }
            self.assertEqual(payload["ok"], True)
            self.assertEqual(set(payload["paths"].keys()), expected_files)
            for filename in expected_files:
                self.assertTrue((output_dir / filename).exists(), filename)

            combined = "\n".join(
                path.read_text(encoding="utf-8")
                for path in output_dir.iterdir()
                if path.is_file()
            )
            self.assertIn(WORKER_STATUS_COMMAND, combined)
            self.assertIn(WORKER_DEMO_COMMAND, combined)
            self.assertIn(LAUNCHER_COMMAND, combined)
            self.assertIn(CONTEXT_PACK_COMMAND, combined)
            self.assertIn("no live APIs", combined)
            self.assertIn("no auto-downloads", combined)
            self.assertNotRegex(combined, r"sk-[A-Za-z0-9_-]{20,}")
            self.assertNotRegex(combined, r"ghp_[A-Za-z0-9_]{20,}")
            self.assertNotRegex(combined, r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY")

    def test_dashboard_launcher_and_docs_surface_easy_worker_lane(self):
        index_html = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html").read_text(encoding="utf-8")
        server_js = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js").read_text(encoding="utf-8")
        app_js = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "app.js").read_text(encoding="utf-8")
        launcher_py = (REPO_ROOT / "03_scripts" / "ghoti_product_launcher.py").read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        daily_guide = (REPO_ROOT / "docs" / "DAILY_OPERATOR_GUIDE.md").read_text(encoding="utf-8")
        codex_workflow = (REPO_ROOT / "docs" / "CODEX_ONLY_WORKFLOW.md").read_text(encoding="utf-8")

        self.assertIn("Local Model / Easy Worker Lane", index_html)
        self.assertIn("local_demo fallback", index_html)
        self.assertIn("readiness percentage", index_html)
        self.assertIn("no live APIs", index_html)
        self.assertIn("no auto-downloads", index_html)
        self.assertIn("/api/local-model-worker/status", server_js)
        self.assertIn("/api/local-model-worker/doctor", server_js)
        self.assertIn("/api/local-model-worker/demo", server_js)
        self.assertIn("/api/local-model-worker/write-demo-output", server_js)
        self.assertIn("local_model_easy_worker_lane", server_js)
        self.assertIn("/api/local-model-worker/status", app_js)
        self.assertIn("--local-worker-status", launcher_py)
        self.assertIn("--local-worker-demo", launcher_py)
        self.assertNotIn("shell: true", server_js)
        self.assertIn("LOCAL_MODEL_GEMMA_SETUP_GUIDE.md", readme)
        self.assertIn("EASY_WORKER_LANE_GUIDE.md", readme)
        self.assertIn("LOCAL_MODEL_GEMMA_SETUP_GUIDE.md", daily_guide)
        self.assertIn("EASY_WORKER_LANE_GUIDE.md", codex_workflow)


if __name__ == "__main__":
    unittest.main()
