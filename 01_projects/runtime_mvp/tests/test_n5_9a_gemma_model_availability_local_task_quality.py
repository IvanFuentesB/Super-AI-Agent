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
GEMMA_READINESS = REPO_ROOT / "03_scripts" / "gemma_model_readiness.py"
LAUNCHER = REPO_ROOT / "03_scripts" / "ghoti_product_launcher.py"
CONTEXT_PACK = REPO_ROOT / "03_scripts" / "ghoti_context_pack_builder.py"


class FakeCompleted:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def load_gemma_module():
    spec = importlib.util.spec_from_file_location("gemma_model_readiness", GEMMA_READINESS)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def fake_ollama(version_stdout="ollama version is 0.24.0", list_stdout="NAME    ID    SIZE    MODIFIED\n"):
    def _fake_run(cmd, timeout=10):
        if cmd == ["ollama", "--version"]:
            return FakeCompleted(stdout=version_stdout)
        if cmd == ["ollama", "list"]:
            return FakeCompleted(stdout=list_stdout)
        if cmd[:2] == ["git", "rev-parse"]:
            return FakeCompleted(stdout="6d1a9238d2caa4355e475904c6433310e6cb568b\n")
        return FakeCompleted(stdout="")
    return _fake_run


class GhotiGemmaModelReadinessTests(unittest.TestCase):
    def test_ollama_missing_degrades_safely(self):
        gemma = load_gemma_module()

        def missing_ollama(cmd, timeout=10):
            if cmd == ["ollama", "--version"]:
                raise FileNotFoundError("ollama")
            return FakeCompleted(stdout="")

        with mock.patch.object(gemma, "_run", side_effect=missing_ollama):
            payload = gemma.build_status(generated_at="2026-05-24T00:00:00Z")

        self.assertEqual(payload["ok"], True)
        self.assertEqual(payload["local_only"], True)
        self.assertEqual(payload["live_api_used"], False)
        self.assertEqual(payload["auto_download_performed"], False)
        self.assertEqual(payload["ollama_pull_performed"], False)
        self.assertEqual(payload["ollama_installed"], False)
        self.assertEqual(payload["ollama_reachable"], False)
        self.assertEqual(payload["gemma_installed"], False)
        self.assertEqual(payload["active_worker_mode"], "local_demo")
        self.assertEqual(payload["production_routing_enabled"], False)
        self.assertIn("Install or start Ollama manually", payload["recommendation"])

    def test_gemma_missing_uses_local_demo_and_keeps_manual_command(self):
        gemma = load_gemma_module()
        with mock.patch.object(gemma, "_run", side_effect=fake_ollama()):
            payload = gemma.build_status(generated_at="2026-05-24T00:00:00Z")

        self.assertEqual(payload["ollama_installed"], True)
        self.assertEqual(payload["ollama_version"], "ollama version is 0.24.0")
        self.assertEqual(payload["ollama_reachable"], True)
        self.assertEqual(payload["installed_models_count"], 0)
        self.assertEqual(payload["gemma_installed"], False)
        self.assertEqual(payload["installed_gemma_models"], [])
        self.assertEqual(payload["preferred_model"], "gemma3:4b")
        self.assertEqual(payload["preferred_model_installed"], False)
        self.assertEqual(payload["fallback_models_installed"], [])
        self.assertEqual(payload["active_worker_mode"], "local_demo")
        self.assertIn("ollama pull gemma3:4b", "\n".join(payload["manual_commands"]))
        self.assertIn("manual approval required", payload["manual_approval_required_reason"])
        self.assertIn("local_demo fallback", payload["status_line"])

    def test_preferred_and_lighter_gemma_models_are_detected(self):
        gemma = load_gemma_module()
        list_4b = (
            "NAME         ID        SIZE      MODIFIED\n"
            "gemma3:4b    abc123    3.3 GB    1 hour ago\n"
        )
        with mock.patch.object(gemma, "_run", side_effect=fake_ollama(list_stdout=list_4b)):
            preferred = gemma.build_status(generated_at="2026-05-24T00:00:00Z")
        self.assertEqual(preferred["gemma_installed"], True)
        self.assertEqual(preferred["preferred_model_installed"], True)
        self.assertEqual(preferred["active_worker_mode"], "ollama_gemma")
        self.assertGreaterEqual(preferred["gemma_readiness_percent"], 70)

        list_1b = (
            "NAME         ID        SIZE      MODIFIED\n"
            "gemma3:1b    def456    815 MB    1 hour ago\n"
        )
        with mock.patch.object(gemma, "_run", side_effect=fake_ollama(list_stdout=list_1b)):
            fallback = gemma.build_status(generated_at="2026-05-24T00:00:00Z")
        self.assertEqual(fallback["gemma_installed"], True)
        self.assertEqual(fallback["preferred_model_installed"], False)
        self.assertEqual(fallback["fallback_models_installed"], ["gemma3:1b"])
        self.assertIn("lighter Gemma", fallback["recommendation"])

    def test_invalid_ollama_list_output_does_not_fake_model_presence(self):
        gemma = load_gemma_module()
        with mock.patch.object(gemma, "_run", side_effect=fake_ollama(list_stdout="this is not ollama list output\n")):
            payload = gemma.build_status(generated_at="2026-05-24T00:00:00Z")

        self.assertEqual(payload["ollama_installed"], True)
        self.assertEqual(payload["ollama_reachable"], False)
        self.assertEqual(payload["model_list_parse_ok"], False)
        self.assertEqual(payload["gemma_installed"], False)
        self.assertEqual(payload["active_worker_mode"], "local_demo")

    def test_recommendation_install_plan_never_pulls_by_default(self):
        gemma = load_gemma_module()
        with mock.patch.object(gemma, "_run", side_effect=fake_ollama()):
            plan = gemma.build_recommendation(generated_at="2026-05-24T00:00:00Z")

        self.assertEqual(plan["ok"], True)
        self.assertEqual(plan["action"], "recommend")
        self.assertEqual(plan["auto_download_performed"], False)
        self.assertEqual(plan["ollama_pull_performed"], False)
        self.assertEqual(plan["human_approval_required"], True)
        self.assertIn("ollama pull gemma3:4b", plan["recommended_manual_commands"])
        self.assertIn("ollama pull gemma3:1b", plan["lighter_alternative_commands"])
        self.assertIn("3.3GB", plan["model_options"]["gemma3:4b"]["disk_size_note"])

    def test_quality_plan_and_write_readiness_create_safe_outputs(self):
        gemma = load_gemma_module()
        runtime_tmp = REPO_ROOT / "01_projects" / "dashboard_mvp" / "runtime_data"
        runtime_tmp.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=runtime_tmp) as tmp:
            output_dir = Path(tmp)
            with mock.patch.object(gemma, "_run", side_effect=fake_ollama()):
                quality = gemma.build_quality_plan(generated_at="2026-05-24T00:00:00Z")
                written = gemma.write_readiness(output_dir=output_dir, generated_at="2026-05-24T00:00:00Z")

            self.assertEqual(quality["ok"], True)
            self.assertEqual(quality["quality_evaluation"]["mode"], "local_demo")
            self.assertEqual(quality["quality_evaluation"]["production_routing_recommended"], False)
            self.assertEqual(quality["quality_evaluation"]["tasks_total"], 7)
            self.assertEqual(quality["quality_evaluation"]["safety_gate_passed"], True)
            self.assertEqual(quality["quality_evaluation"]["json_validity_passed"], True)

            expected = {
                "gemma_readiness_status.json",
                "gemma_readiness_status.md",
                "gemma_install_decision.md",
                "gemma_manual_commands.md",
                "local_task_quality_plan.md",
                "local_task_quality_rubric.json",
                "local_worker_next_steps.md",
                "local_demo_quality_eval.json",
                "local_demo_quality_eval.md",
            }
            self.assertEqual(set(written["paths"].keys()), expected)
            for filename in expected:
                self.assertTrue((output_dir / filename).exists(), filename)

            rubric = json.loads((output_dir / "local_task_quality_rubric.json").read_text(encoding="utf-8"))
            self.assertEqual(rubric["tasks_total"], 7)
            combined = "\n".join(path.read_text(encoding="utf-8") for path in output_dir.iterdir() if path.is_file())
            self.assertIn("manual approval required", combined)
            self.assertIn("ollama pull gemma3:4b", combined)
            self.assertIn("local_demo fallback", combined)
            self.assertIn("No live APIs", combined)
            self.assertNotRegex(combined, r"sk-[A-Za-z0-9_-]{20,}")
            self.assertNotRegex(combined, r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY")

    def test_launcher_dashboard_context_pack_and_docs_surface_gemma_readiness(self):
        env = dict(os.environ)
        env["GHOTI_GEMMA_READINESS_FAKE_OLLAMA_VERSION"] = "ollama version is 0.24.0"
        env["GHOTI_GEMMA_READINESS_FAKE_OLLAMA_LIST"] = "NAME    ID    SIZE    MODIFIED\n"
        completed = subprocess.run(
            [sys.executable, str(LAUNCHER), "--gemma-status", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=45,
            env=env,
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr or completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["ok"], True)
        self.assertEqual(payload["action"], "gemma-status")
        self.assertEqual(payload["gemma_installed"], False)
        self.assertEqual(payload["active_worker_mode"], "local_demo")

        index_html = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html").read_text(encoding="utf-8")
        server_js = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js").read_text(encoding="utf-8")
        app_js = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "app.js").read_text(encoding="utf-8")
        launcher_py = LAUNCHER.read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        daily_guide = (REPO_ROOT / "docs" / "DAILY_OPERATOR_GUIDE.md").read_text(encoding="utf-8")
        gemma_decision = (REPO_ROOT / "docs" / "GEMMA_MODEL_INSTALL_DECISION.md").read_text(encoding="utf-8")
        quality_guide = (REPO_ROOT / "docs" / "LOCAL_MODEL_QUALITY_EVALUATION_GUIDE.md").read_text(encoding="utf-8")

        self.assertIn("Gemma / Local Model Quality", index_html)
        self.assertIn("manual approval required before model download", index_html)
        self.assertIn("no auto-downloads", index_html)
        self.assertIn("/api/gemma-readiness/status", server_js)
        self.assertIn("/api/gemma-readiness/quality-plan", server_js)
        self.assertIn("/api/gemma-readiness/status", app_js)
        self.assertIn("--gemma-status", launcher_py)
        self.assertIn("--gemma-doctor", launcher_py)
        self.assertIn("--gemma-quality-plan", launcher_py)
        self.assertNotIn("shell: true", server_js)
        self.assertIn("Gemma readiness", readme)
        self.assertIn("GEMMA_MODEL_INSTALL_DECISION.md", daily_guide)
        self.assertIn("ollama pull gemma3:4b", gemma_decision)
        self.assertIn("production routing remains disabled", quality_guide)

        context = subprocess.run(
            [
                sys.executable,
                str(CONTEXT_PACK),
                "--write",
                "--json",
                "--output-dir",
                str(REPO_ROOT / "01_projects" / "dashboard_mvp" / "runtime_data" / "gemma-context-test"),
                "--generated-at",
                "2026-05-24T00:00:00Z",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=60,
            env=env,
        )
        self.assertEqual(context.returncode, 0, msg=context.stderr or context.stdout)
        pack_path = REPO_ROOT / "01_projects" / "dashboard_mvp" / "runtime_data" / "gemma-context-test" / "ghoti_current_context_pack.md"
        pack = pack_path.read_text(encoding="utf-8")
        self.assertIn("Gemma / Local Model Quality", pack)
        self.assertIn("14_context/local_model_readiness/generated/gemma_readiness_status.md", pack)
        self.assertIn("quality evaluation", pack)


if __name__ == "__main__":
    unittest.main()
