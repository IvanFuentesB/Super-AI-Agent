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
            return FakeCompleted(stdout="20e1dce1e89f15a337054864560b95b82233877c\n")
        return FakeCompleted(stdout="")
    return _fake_run


class GhotiHumanApprovedGemmaInstallEvalTests(unittest.TestCase):
    def test_preflight_schema_records_approval_without_pulling(self):
        gemma = load_gemma_module()
        with mock.patch.object(gemma, "_run", side_effect=fake_ollama()):
            payload = gemma.build_install_preflight(
                approval_source="user prompt approved exactly one gemma3:4b pull",
                generated_at="2026-05-24T00:00:00Z",
            )

        self.assertEqual(payload["ok"], True)
        self.assertEqual(payload["action"], "gemma-install-preflight")
        self.assertEqual(payload["chosen_model"], "gemma3:4b")
        self.assertEqual(payload["approval_source"], "user prompt approved exactly one gemma3:4b pull")
        self.assertEqual(payload["local_only"], True)
        self.assertEqual(payload["live_api_used"], False)
        self.assertEqual(payload["provider_setup_performed"], False)
        self.assertEqual(payload["model_install_attempted"], False)
        self.assertEqual(payload["ollama_pull_performed"], False)
        self.assertEqual(payload["auto_download_performed"], False)
        self.assertEqual(payload["safe_to_attempt_install"], True)
        self.assertIn("ollama pull gemma3:4b", payload["approved_command"])

    def test_local_model_eval_missing_model_is_controlled_local_demo(self):
        gemma = load_gemma_module()
        with mock.patch.object(gemma, "_run", side_effect=fake_ollama()):
            payload = gemma.build_local_model_eval(generated_at="2026-05-24T00:00:00Z")

        self.assertEqual(payload["ok"], True)
        self.assertEqual(payload["action"], "local-model-eval")
        self.assertEqual(payload["mode"], "local_demo")
        self.assertEqual(payload["model"], "local_demo")
        self.assertEqual(payload["real_model_evaluated"], False)
        self.assertEqual(payload["gemma_installed"], False)
        self.assertEqual(payload["tasks_total"], 7)
        self.assertEqual(payload["tasks_passed"], 7)
        self.assertEqual(payload["score_percent"], 55)
        self.assertEqual(payload["production_routing_recommended"], False)
        self.assertEqual(payload["safety_gate_passed"], True)
        self.assertEqual(payload["json_validity_passed"], True)
        self.assertIn("pending", payload["quality_evaluation_status"])

    def test_local_model_eval_with_fake_gemma_scores_real_without_routing(self):
        gemma = load_gemma_module()
        list_stdout = (
            "NAME         ID        SIZE      MODIFIED\n"
            "gemma3:4b    abc123    3.3 GB    1 minute ago\n"
        )
        fake_outputs = iter([
            "Summary: Ghoti is a local-first supervised operator MVP with audited safety gates.",
            "Ghoti is stable locally with a dashboard, context packs, repo map, Hermes bridge, and a real Gemma lane under evaluation.",
            "classification: coding,audit",
            "Continue Ghoti from current main; run tests first; keep no live APIs.",
            "Use the next-milestone repo bundle and local-model-worker bundle.",
            "Refuse autonomous posting or credential/session scraping; offer a local dry-run alternative.",
            json.dumps({"bullets": ["local MVP", "safety gates", "dashboard", "context packs", "repo map", "Hermes manual", "Gemma eval", "no live APIs", "no posting", "next audit"]}),
        ])

        def fake_generate(model, prompt, timeout=90):
            return {"ok": True, "model": model, "text": next(fake_outputs), "latency_seconds": 0.01}

        with mock.patch.object(gemma, "_run", side_effect=fake_ollama(list_stdout=list_stdout)):
            with mock.patch.object(gemma, "_call_ollama_generate", side_effect=fake_generate):
                payload = gemma.build_local_model_eval(generated_at="2026-05-24T00:00:00Z")

        self.assertEqual(payload["mode"], "gemma")
        self.assertEqual(payload["model"], "gemma3:4b")
        self.assertEqual(payload["real_model_evaluated"], True)
        self.assertEqual(payload["tasks_total"], 7)
        self.assertGreaterEqual(payload["tasks_passed"], 6)
        self.assertGreaterEqual(payload["score_percent"], 70)
        self.assertEqual(payload["production_routing_recommended"], False)
        self.assertEqual(payload["live_api_used"], False)
        self.assertEqual(payload["provider_setup_performed"], False)

    def test_write_local_model_evaluation_creates_run_files(self):
        gemma = load_gemma_module()
        runtime_tmp = REPO_ROOT / "01_projects" / "dashboard_mvp" / "runtime_data"
        runtime_tmp.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=runtime_tmp) as tmp:
            with mock.patch.object(gemma, "_run", side_effect=fake_ollama()):
                written = gemma.write_local_model_evaluation(
                    output_root=Path(tmp),
                    generated_at="2026-05-24T00:00:00Z",
                )

            self.assertEqual(written["ok"], True)
            self.assertEqual(written["action"], "write-local-model-evaluation")
            expected = {
                "00_manifest.json",
                "01_model_status_before_after.json",
                "02_eval_tasks.json",
                "03_gemma_outputs.md",
                "04_local_demo_baseline.md",
                "05_quality_scores.json",
                "06_quality_review.md",
                "07_next_steps.md",
                "08_dashboard_summary.md",
            }
            self.assertEqual(set(written["paths"].keys()), expected)
            for relpath in written["paths"].values():
                self.assertTrue((REPO_ROOT / relpath).exists(), relpath)
            scores = json.loads((REPO_ROOT / written["paths"]["05_quality_scores.json"]).read_text(encoding="utf-8"))
            self.assertEqual(scores["production_routing_recommended"], False)
            self.assertEqual(scores["live_api_used"], False)

    def test_launcher_dashboard_and_docs_expose_local_model_eval(self):
        env = dict(os.environ)
        env["GHOTI_GEMMA_READINESS_FAKE_OLLAMA_VERSION"] = "ollama version is 0.24.0"
        env["GHOTI_GEMMA_READINESS_FAKE_OLLAMA_LIST"] = "NAME    ID    SIZE    MODIFIED\n"
        completed = subprocess.run(
            [sys.executable, str(LAUNCHER), "--local-model-eval", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=60,
            env=env,
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr or completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["ok"], True)
        self.assertEqual(payload["action"], "local-model-eval")
        self.assertEqual(payload["mode"], "local_demo")
        self.assertEqual(payload["production_routing_recommended"], False)

        index_html = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html").read_text(encoding="utf-8")
        server_js = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js").read_text(encoding="utf-8")
        app_js = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "app.js").read_text(encoding="utf-8")
        launcher_py = LAUNCHER.read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        install_log = (REPO_ROOT / "docs" / "HUMAN_APPROVED_GEMMA_INSTALL_LOG.md").read_text(encoding="utf-8")
        quality_guide = (REPO_ROOT / "docs" / "LOCAL_MODEL_QUALITY_EVALUATION_GUIDE.md").read_text(encoding="utf-8")

        self.assertIn("Real local evaluation status", index_html)
        self.assertIn("Latest eval run path", index_html)
        self.assertIn("/api/gemma-readiness/local-model-eval", server_js)
        self.assertIn("/api/gemma-readiness/local-model-eval", app_js)
        self.assertIn("--local-model-eval", launcher_py)
        self.assertIn("Human-approved Gemma install", readme)
        self.assertIn("gemma3:4b", install_log)
        self.assertIn("production routing remains disabled", quality_guide)
        self.assertNotIn("shell: true", server_js)


if __name__ == "__main__":
    unittest.main()
