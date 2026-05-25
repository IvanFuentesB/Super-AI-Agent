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
GUARD_SCRIPT = REPO_ROOT / "03_scripts" / "local_model_output_guard.py"
WORKER_SCRIPT = REPO_ROOT / "03_scripts" / "local_model_worker_lane.py"
LAUNCHER = REPO_ROOT / "03_scripts" / "ghoti_product_launcher.py"


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


def fake_ollama(list_stdout=None):
    list_text = list_stdout or "NAME         ID        SIZE      MODIFIED\ngemma3:4b    a2af6     3.3 GB    now\n"

    def _fake_run(cmd, timeout=10):
        if cmd == ["ollama", "--version"]:
            return FakeCompleted(stdout="ollama version is 0.24.0")
        if cmd == ["ollama", "list"]:
            return FakeCompleted(stdout=list_text)
        if cmd[:2] == ["git", "rev-parse"]:
            return FakeCompleted(stdout="1ddeb0f39d5316e90ee2d0b8caa276b1fec9e4e6\n")
        return FakeCompleted(stdout="")

    return _fake_run


class ConstrainedLocalModelRoutingGuardTests(unittest.TestCase):
    def test_guard_loads_known_bundle_ids(self):
        guard = load_module(GUARD_SCRIPT, "local_model_output_guard")
        catalog = guard.load_repo_catalog()
        self.assertIn("next-milestone", catalog["bundle_ids"])
        self.assertIn("local-model-worker", catalog["bundle_ids"])
        self.assertIn("03_scripts/local_model_worker_lane.py", catalog["file_paths"])

    def test_guard_rejects_invented_bundle_id(self):
        guard = load_module(GUARD_SCRIPT, "local_model_output_guard")
        output = json.dumps({
            "answer": "Use StableLM-DanceDiffusion.",
            "source_metadata": {
                "bundle_ids": ["StableLM-DanceDiffusion"],
                "file_paths": ["14_context/repo_knowledge/generated/task_bundle_next_milestone.md"],
                "local_only": True,
                "live_api_used": False,
            },
        })
        result = guard.validate_model_output(output, task="context-bundle-summary")
        self.assertEqual(result["status"], "reject")
        self.assertIn("invented or unsupported bundle", " ".join(result["reasons"]))

    def test_guard_rejects_unknown_file_source(self):
        guard = load_module(GUARD_SCRIPT, "local_model_output_guard")
        output = json.dumps({
            "answer": "Use a repo file.",
            "source_metadata": {
                "bundle_ids": ["next-milestone"],
                "file_paths": ["docs/DOES_NOT_EXIST.md"],
                "local_only": True,
                "live_api_used": False,
            },
        })
        result = guard.validate_model_output(output, task="status-paragraph")
        self.assertEqual(result["status"], "reject")
        self.assertIn("unknown source file", " ".join(result["reasons"]))

    def test_guard_accepts_valid_source_metadata(self):
        guard = load_module(GUARD_SCRIPT, "local_model_output_guard")
        output = json.dumps({
            "answer": "Use the next milestone bundle and local worker script.",
            "source_metadata": {
                "bundle_ids": ["next-milestone", "local-model-worker"],
                "file_paths": [
                    "14_context/repo_knowledge/generated/task_bundle_next_milestone.md",
                    "03_scripts/local_model_worker_lane.py",
                ],
                "local_only": True,
                "live_api_used": False,
            },
        })
        result = guard.validate_model_output(output, task="context-bundle-summary")
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["local_only"], True)
        self.assertEqual(result["live_api_used"], False)

    def test_route_task_falls_back_when_gemma_hallucinates_bundle(self):
        worker = load_module(WORKER_SCRIPT, "local_model_worker_lane")
        hallucinated = json.dumps({
            "answer": "StableLM-DanceDiffusion is the right bundle.",
            "source_metadata": {
                "bundle_ids": ["StableLM-DanceDiffusion"],
                "file_paths": ["https://github.com/ggerganov/GhoTi/tree/main/StableLM-DanceDiffusion"],
                "local_only": True,
                "live_api_used": False,
            },
        })
        with mock.patch.object(worker, "_run", side_effect=fake_ollama()):
            with mock.patch.object(worker, "_call_ollama_generate", return_value={
                "ok": True,
                "model": "gemma3:4b",
                "text": hallucinated,
                "latency_seconds": 0.01,
                "error": "",
            }):
                payload = worker.route_task("context-bundle-summary", generated_at="2026-05-25T00:00:00Z")

        self.assertEqual(payload["ok"], True)
        self.assertEqual(payload["task"], "context-bundle-summary")
        self.assertEqual(payload["active_route"], "local_demo_fallback")
        self.assertEqual(payload["guard_result"]["status"], "fallback_used")
        self.assertEqual(payload["gemma_attempted"], True)
        self.assertEqual(payload["live_api_used"], False)
        self.assertIn("StableLM-DanceDiffusion", payload["rejected_model_text"])

    def test_safe_task_allowlist_rejects_unsafe_task(self):
        worker = load_module(WORKER_SCRIPT, "local_model_worker_lane")
        payload = worker.route_task("execute-shell-command", generated_at="2026-05-25T00:00:00Z")
        self.assertEqual(payload["ok"], False)
        self.assertEqual(payload["error"], "unsupported routed task")
        self.assertIn("status-paragraph", payload["safe_routed_tasks"])

    def test_routing_demo_writes_expected_files(self):
        worker = load_module(WORKER_SCRIPT, "local_model_worker_lane")
        runtime_tmp = REPO_ROOT / "01_projects" / "dashboard_mvp" / "runtime_data"
        runtime_tmp.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=runtime_tmp) as tmp:
            with mock.patch.object(worker, "_run", side_effect=fake_ollama("NAME    ID    SIZE    MODIFIED\n")):
                result = worker.write_routing_demo(output_root=Path(tmp), generated_at="2026-05-25T00:00:00Z")
            guard_results = json.loads((REPO_ROOT / result["paths"]["03_guard_results.json"]).read_text(encoding="utf-8"))

        self.assertEqual(result["ok"], True)
        self.assertEqual(result["action"], "write-routing-demo")
        expected = {
            "00_routing_manifest.json",
            "01_task_inputs.json",
            "02_gemma_outputs.md",
            "03_guard_results.json",
            "04_fallback_outputs.md",
            "05_final_outputs.md",
            "06_quality_review.md",
            "07_next_steps.md",
        }
        self.assertEqual(set(result["paths"].keys()), expected)
        self.assertTrue(guard_results["local_only"])
        self.assertFalse(guard_results["live_api_used"])

    def test_cli_and_launcher_expose_routing_status(self):
        env = dict(os.environ)
        env["GHOTI_LOCAL_WORKER_FAKE_OLLAMA_VERSION"] = "ollama version is 0.24.0"
        env["GHOTI_LOCAL_WORKER_FAKE_OLLAMA_LIST"] = "NAME    ID    SIZE    MODIFIED\n"
        completed = subprocess.run(
            [sys.executable, str(WORKER_SCRIPT), "--routing-status", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=60,
            env=env,
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr or completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["ok"], True)
        self.assertEqual(payload["guard_enabled"], True)
        self.assertIn("report-to-bullets", payload["safe_routed_tasks"])

        launcher = subprocess.run(
            [sys.executable, str(LAUNCHER), "--local-worker-routing-status", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=60,
            env=env,
        )
        self.assertEqual(launcher.returncode, 0, msg=launcher.stderr or launcher.stdout)
        launcher_payload = json.loads(launcher.stdout)
        self.assertEqual(launcher_payload["ok"], True)
        self.assertEqual(launcher_payload["action"], "local-worker-routing-status")

    def test_dashboard_docs_and_apple_plan_are_present(self):
        index_html = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html").read_text(encoding="utf-8")
        server_js = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js").read_text(encoding="utf-8")
        app_js = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "app.js").read_text(encoding="utf-8")
        launcher_py = LAUNCHER.read_text(encoding="utf-8")

        self.assertIn("Local Model Routing / Guarded Worker", index_html)
        self.assertIn("hallucination guard", index_html.lower())
        self.assertIn("/api/local-model-worker/routing-status", server_js)
        self.assertIn("/api/local-model-worker/route-task", server_js)
        self.assertIn("local-worker-routing-status", app_js)
        self.assertIn("--local-worker-routing-status", launcher_py)
        self.assertNotIn("shell: true", server_js)

        required_docs = [
            "docs/LOCAL_MODEL_ROUTING_GUIDE.md",
            "docs/LOCAL_MODEL_OUTPUT_GUARD.md",
            "docs/LOCAL_WORKER_SAFE_TASKS.md",
            "docs/SAFE_COMPUTER_USE_TEST_PLAN_APPLE_COMPARISON.md",
        ]
        for relpath in required_docs:
            text = (REPO_ROOT / relpath).read_text(encoding="utf-8")
            self.assertIn("no live apis", text.lower())
        apple_plan = (REPO_ROOT / "docs/SAFE_COMPUTER_USE_TEST_PLAN_APPLE_COMPARISON.md").read_text(encoding="utf-8")
        self.assertIn("Chrome in Incognito", apple_plan)
        self.assertIn("observation-only", apple_plan)
        self.assertIn("manual approval", apple_plan)
        self.assertIn("Do not execute", apple_plan)


if __name__ == "__main__":
    unittest.main()
