"""N+6.42A deterministic, source-linked context memory map tests."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "03_scripts" / "context_memory" / "ghoti_context_memory_map.py"


def load_module():
    spec = importlib.util.spec_from_file_location("ghoti_context_memory_map", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load context memory map module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestContextMemoryMapContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.memory = load_module()

    def test_reviewed_source_registry_is_repo_relative_and_present(self):
        self.assertGreaterEqual(len(self.memory.SOURCE_SPECS), 8)
        for spec in self.memory.SOURCE_SPECS:
            path = Path(spec["path"])
            self.assertFalse(path.is_absolute(), spec["path"])
            self.assertNotIn("..", path.parts)
            self.assertTrue((REPO_ROOT / path).is_file(), spec["path"])

    def test_index_contains_current_sha256_and_no_absolute_paths(self):
        index = self.memory.build_raw_index(REPO_ROOT)
        self.assertTrue(index["local_only"])
        self.assertTrue(index["read_only_sources"])
        self.assertFalse(index["live_actions_enabled"])
        self.assertGreaterEqual(len(index["sources"]), 8)
        for source in index["sources"]:
            self.assertEqual(source["sha256"], sha256(REPO_ROOT / source["path"]))
            self.assertFalse(Path(source["path"]).is_absolute())
            self.assertNotIn(str(REPO_ROOT), json.dumps(source))

    def test_sensitive_source_is_indexed_but_never_summarized(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "notes.md"
            source.write_text(
                "# Unsafe\n\nOPENAI_API_KEY=example-secret-value\n"
                "C:\\Users\\private-user\\secret.md\n",
                encoding="utf-8",
            )
            specs = [{"path": "notes.md", "category": "test", "priority": 1}]
            index = self.memory.build_raw_index(root, specs)
            self.assertFalse(index["sources"][0]["summary_safe"])
            outputs = self.memory.render_outputs(index)
            combined = "\n".join(outputs.values())
            self.assertNotIn("example-secret-value", combined)
            self.assertNotIn("C:\\Users\\private-user", combined)

    def test_rendering_is_deterministic_and_token_budgeted(self):
        index = self.memory.build_raw_index(REPO_ROOT)
        first = self.memory.render_outputs(index)
        second = self.memory.render_outputs(index)
        self.assertEqual(first, second)
        self.assertLessEqual(
            self.memory.word_count(first["context_map.md"]),
            self.memory.CONTEXT_MAP_WORD_BUDGET,
        )
        self.assertLessEqual(
            self.memory.word_count(first["latest_state.md"]),
            self.memory.LATEST_STATE_WORD_BUDGET,
        )

    def test_generated_markdown_links_to_sources_and_hashes(self):
        index = self.memory.build_raw_index(REPO_ROOT)
        outputs = self.memory.render_outputs(index)
        context_map = outputs["context_map.md"]
        latest_state = outputs["latest_state.md"]
        for source in index["sources"]:
            self.assertIn(source["path"], context_map)
            self.assertIn(source["sha256"], context_map)
        self.assertIn("Source-linked highlights", latest_state)
        self.assertIn("not canonical truth", latest_state)
        self.assertIn("review-required excerpts", latest_state)

    def test_generated_outputs_are_ascii_safe(self):
        index = self.memory.build_raw_index(REPO_ROOT)
        outputs = self.memory.render_outputs(index)
        for name, content in outputs.items():
            self.assertTrue(content.isascii(), name)

    def test_write_outputs_never_modifies_sources(self):
        index = self.memory.build_raw_index(REPO_ROOT)
        before = {item["path"]: sha256(REPO_ROOT / item["path"]) for item in index["sources"]}
        with tempfile.TemporaryDirectory() as temp:
            written = self.memory.write_outputs(index, Path(temp), Path(temp))
            self.assertEqual(
                sorted(path.name for path in written),
                ["context_map.md", "latest_state.md", "raw_index.json"],
            )
        after = {item["path"]: sha256(REPO_ROOT / item["path"]) for item in index["sources"]}
        self.assertEqual(before, after)

    def test_output_path_must_stay_inside_memory_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            index = self.memory.build_raw_index(REPO_ROOT)
            with self.assertRaises(ValueError):
                self.memory.write_outputs(index, root)
            with self.assertRaises(ValueError):
                self.memory.write_outputs(index, root / ".." / "escape", root)

    def test_source_danger_scan_blocks_private_paths_and_secret_values(self):
        unsafe = [
            "C:\\Users\\somebody\\file.md",
            "C:/Users/somebody/file.md",
            "/mnt/c/Users/somebody/file.md",
            "OPENAI_API_KEY=real-value",
            "sk-ant-" + ("x" * 30),
        ]
        for text in unsafe:
            self.assertFalse(self.memory.is_summary_safe(text), text)
        self.assertTrue(self.memory.is_summary_safe("Reviewed local-only memory with no credentials."))

    def test_cli_check_returns_safe_json_without_writes(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--check", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["local_only"])
        self.assertTrue(payload["read_only_sources"])
        self.assertFalse(payload["network_used"])
        self.assertFalse(payload["model_used"])
        self.assertFalse(payload["live_actions_enabled"])

    def test_cli_write_and_verify_use_safe_repo_local_outputs(self):
        write = subprocess.run(
            [sys.executable, str(SCRIPT), "--write", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(write.returncode, 0, write.stderr)
        payload = json.loads(write.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(len(payload["written"]), 3)
        for raw_path in payload["written"]:
            path = REPO_ROOT / raw_path
            self.assertTrue(path.is_file(), raw_path)
            self.assertTrue(path.resolve().is_relative_to((REPO_ROOT / "14_context" / "memory").resolve()))

        verify = subprocess.run(
            [sys.executable, str(SCRIPT), "--verify", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(verify.returncode, 0, verify.stderr)
        self.assertTrue(json.loads(verify.stdout)["ok"])

    def test_expected_docs_schema_and_blueprint_exist(self):
        expected = [
            "14_context/memory/README.md",
            "14_context/memory/schemas/raw_index.schema.json",
            "14_context/operator_reports/generated/codex_context_memory_sync_blueprint.md",
        ]
        for path in expected:
            self.assertTrue((REPO_ROOT / path).is_file(), path)

    def test_script_has_no_network_model_or_unsafe_command_execution(self):
        text = SCRIPT.read_text(encoding="utf-8")
        forbidden = [
            "import requests",
            "import urllib",
            "import socket",
            "os.system(",
            "shell=True",
            "shell = True",
            "Invoke-Expression",
            "ollama",
        ]
        for needle in forbidden:
            self.assertNotIn(needle, text)


if __name__ == "__main__":
    unittest.main()
