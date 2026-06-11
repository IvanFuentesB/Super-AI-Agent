"""N+6.43A optional local memory search trial contract tests."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "03_scripts" / "context_memory" / "ghoti_local_memory_search.py"
MEMORY_MAP = REPO_ROOT / "03_scripts" / "context_memory" / "ghoti_context_memory_map.py"
MEMORY_ROOT = REPO_ROOT / "14_context" / "memory"
RAW_INDEX = MEMORY_ROOT / "index" / "raw_index.json"
SEARCH_INDEX = MEMORY_ROOT / "search" / "generated" / "local_search_index.json"
EVALUATION = MEMORY_ROOT / "search" / "generated" / "evaluation_result.json"
FIXTURE = MEMORY_ROOT / "search" / "fixtures" / "sanitized_search_eval.json"


def load_module():
    spec = importlib.util.spec_from_file_location("ghoti_local_memory_search", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load local memory search module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestLocalMemorySearchTrial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.search = load_module()

    def test_expected_trial_files_exist(self):
        expected = [
            "docs/GHOTI_N6_43A_LOCAL_MEMORY_SEARCH_TRIAL.md",
            "03_scripts/context_memory/ghoti_local_memory_search.py",
            "23_configs/context_memory_search.example.json",
            "14_context/memory/search/README.md",
            "14_context/memory/search/fixtures/sanitized_search_eval.json",
            "14_context/memory/search/generated/local_search_index.json",
            "14_context/memory/search/generated/evaluation_result.json",
        ]
        for path in expected:
            self.assertTrue((REPO_ROOT / path).is_file(), path)

    def test_index_is_disposable_local_noncanonical_and_model_free(self):
        index = self.search.build_search_index(REPO_ROOT)
        self.assertTrue(index["local_only"])
        self.assertTrue(index["read_only_sources"])
        self.assertTrue(index["disposable"])
        self.assertFalse(index["canonical_truth"])
        self.assertFalse(index["network_used"])
        self.assertFalse(index["model_used"])
        self.assertFalse(index["remote_embedding_used"])
        self.assertFalse(index["live_actions_enabled"])
        self.assertEqual(index["engine"], "deterministic_local_feature_hash_v1")
        self.assertEqual(index["vector_dimensions"], 256)
        self.assertGreater(index["source_count"], 0)

    def test_only_reviewed_summary_safe_sources_enter_index(self):
        raw = json.loads(RAW_INDEX.read_text(encoding="utf-8"))
        allowed = {item["path"]: item for item in raw["sources"] if item["summary_safe"]}
        index = self.search.build_search_index(REPO_ROOT)
        self.assertEqual({item["path"] for item in index["sources"]}, set(allowed))
        for item in index["sources"]:
            self.assertEqual(item["source_sha256"], allowed[item["path"]]["sha256"])
            self.assertNotIn("raw_text", item)
            self.assertNotIn("content", item)
            self.assertTrue(item["vector"])

    def test_search_results_are_source_linked_current_and_never_truth_claims(self):
        index = self.search.build_search_index(REPO_ROOT)
        payload = self.search.search("coordinator planner memory writer", index, REPO_ROOT, limit=3)
        self.assertTrue(payload["ok"], payload)
        self.assertFalse(payload["canonical_truth"])
        self.assertTrue(payload["verification_required"])
        self.assertGreater(len(payload["results"]), 0)
        first = payload["results"][0]
        self.assertEqual(first["source_path"], "14_context/agent_handoff_vault/AGENT_RULES.md")
        self.assertEqual(first["source_sha256"], first["current_sha256"])
        self.assertTrue(first["hash_verified"])
        self.assertFalse(first["canonical_truth"])

    def test_query_rejects_secrets_private_paths_and_oversized_input(self):
        unsafe = [
            "OPENAI_API_KEY=not-allowed",
            "C:\\Users\\private-user\\notes.md",
            "/mnt/c/Users/private-user/notes.md",
            "sk-ant-" + ("x" * 30),
            "x" * 501,
        ]
        for query in unsafe:
            with self.assertRaises(ValueError, msg=query[:40]):
                self.search.validate_query(query)

    def test_stale_index_fails_closed(self):
        index = self.search.build_search_index(REPO_ROOT)
        index["sources"][0]["source_sha256"] = "0" * 64
        verification = self.search.verify_search_index(index, REPO_ROOT)
        self.assertFalse(verification["ok"])
        payload = self.search.search("current task", index, REPO_ROOT, limit=3)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"], "stale_search_index")
        self.assertTrue(payload["stale_entries"])

    def test_direct_scan_without_saved_index_still_finds_sources(self):
        payload = self.search.direct_search("bind exact targets relay paste send", REPO_ROOT, limit=3)
        self.assertTrue(payload["ok"], payload)
        self.assertFalse(payload["index_used"])
        self.assertEqual(payload["mode"], "direct_scan_fallback")
        self.assertEqual(
            payload["results"][0]["source_path"],
            "14_context/compact_memory/next_exact_step.md",
        )

    def test_evaluation_proves_content_search_improves_over_path_only(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        evaluation = self.search.evaluate_fixture(fixture, REPO_ROOT)
        self.assertTrue(evaluation["ok"], evaluation)
        self.assertTrue(evaluation["measurable_improvement"])
        self.assertGreater(
            evaluation["content_search"]["top_k_hit_rate"],
            evaluation["path_only_baseline"]["top_k_hit_rate"],
        )
        self.assertGreaterEqual(
            evaluation["content_search"]["top_k_hit_rate"],
            fixture["minimum_content_top_k_hit_rate"],
        )

    def test_written_index_and_evaluation_verify(self):
        index = json.loads(SEARCH_INDEX.read_text(encoding="utf-8"))
        verification = self.search.verify_search_index(index, REPO_ROOT)
        self.assertTrue(verification["ok"], verification)
        evaluation = json.loads(EVALUATION.read_text(encoding="utf-8"))
        self.assertTrue(evaluation["ok"])
        self.assertTrue(evaluation["measurable_improvement"])

    def test_saved_index_is_bounded_and_does_not_store_source_text(self):
        config = json.loads(
            (REPO_ROOT / "23_configs" / "context_memory_search.example.json").read_text(encoding="utf-8")
        )
        self.assertLessEqual(SEARCH_INDEX.stat().st_size, config["max_index_bytes"])
        check = self.search.check(REPO_ROOT)
        self.assertTrue(check["index_within_budget"])
        self.assertLessEqual(check["index_bytes"], check["max_index_bytes"])
        text = SEARCH_INDEX.read_text(encoding="utf-8")
        self.assertLessEqual(len(text.splitlines()), 2)
        self.assertNotIn("Hermes/Alfred: coordinator", text)
        self.assertNotIn("Bind exact ChatGPT and Codex targets", text)

    def test_write_scope_is_only_search_generated_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            written = self.search.write_trial_outputs(REPO_ROOT, root, root)
            relative = sorted(path.relative_to(root.resolve()).as_posix() for path in written)
            self.assertEqual(
                relative,
                [
                    "evaluation_result.json",
                    "local_search_index.json",
                ],
            )

    def test_output_path_must_stay_inside_allowed_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(ValueError):
                self.search.write_trial_outputs(REPO_ROOT, root)
            with self.assertRaises(ValueError):
                self.search.write_trial_outputs(REPO_ROOT, root / ".." / "escape", root)

    def test_cli_contract_is_json_local_only_and_safe(self):
        commands = [
            ["--check", "--json"],
            ["--build", "--json"],
            ["--verify", "--json"],
            ["--evaluate", "--json"],
            ["--search", "coordinator planner memory writer", "--json"],
            ["--search", "bind exact targets relay paste send", "--no-index", "--json"],
        ]
        for arguments in commands:
            result = subprocess.run(
                [sys.executable, str(SCRIPT), *arguments],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"], payload)
            self.assertTrue(payload["local_only"])
            self.assertFalse(payload["network_used"])
            self.assertFalse(payload["model_used"])
            self.assertFalse(payload["live_actions_enabled"])

    def test_base_memory_remains_usable_without_search_index(self):
        result = subprocess.run(
            [sys.executable, str(MEMORY_MAP), "--check", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertNotIn("local_search_index", json.dumps(payload))

    def test_script_has_no_network_model_provider_or_unsafe_command_execution(self):
        text = SCRIPT.read_text(encoding="utf-8")
        forbidden = [
            "import requests",
            "import urllib",
            "import socket",
            "os.system(",
            "shell=True",
            "shell = True",
            "Invoke-Expression",
            "Start-Process",
            "ollama",
            "openai",
            "anthropic",
            "chromadb",
            "faiss",
            "sqlite",
            "exec(",
            "eval(",
        ]
        for needle in forbidden:
            self.assertNotIn(needle, text)

    def test_data_only_write_fallback_has_no_query_or_command_surface(self):
        helper = self.search._NODE_WRITE_SCRIPT
        self.assertIn("writeFileSync", helper)
        self.assertIn("process.stdin", helper)
        for forbidden in ["child_process", "exec", "spawn", "eval", "shell"]:
            self.assertNotIn(forbidden, helper)
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('["node", "-e", _NODE_WRITE_SCRIPT', text)

    def test_config_disables_remote_and_live_capabilities(self):
        config = json.loads(
            (REPO_ROOT / "23_configs" / "context_memory_search.example.json").read_text(encoding="utf-8")
        )
        self.assertTrue(config["local_only"])
        self.assertTrue(config["disposable_index"])
        self.assertFalse(config["remote_embedding_enabled"])
        self.assertFalse(config["provider_enabled"])
        self.assertFalse(config["live_actions_enabled"])
        self.assertFalse(config["automatic_truth_promotion"])
        self.assertLessEqual(config["max_results"], 5)


if __name__ == "__main__":
    unittest.main()
