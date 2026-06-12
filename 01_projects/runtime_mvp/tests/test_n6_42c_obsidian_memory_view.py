"""N+6.42C deterministic Obsidian memory view contract tests."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "03_scripts" / "context_memory" / "ghoti_obsidian_memory_view.py"
MEMORY_MAP = REPO_ROOT / "03_scripts" / "context_memory" / "ghoti_context_memory_map.py"
MEMORY_ROOT = REPO_ROOT / "14_context" / "memory"


def load_module():
    spec = importlib.util.spec_from_file_location("ghoti_obsidian_memory_view", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Obsidian memory view module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestObsidianMemoryViewContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obsidian = load_module()

    def test_expected_views_and_source_indexes_are_declared(self):
        self.assertEqual(
            tuple(self.obsidian.VIEW_NAMES),
            (
                "START_HERE.md",
                "CURRENT_STATE.md",
                "NEXT_ACTIONS.md",
                "SAFETY_GATES.md",
                "AGENT_HANDOFFS.md",
            ),
        )
        self.assertEqual(
            tuple(self.obsidian.SOURCE_INDEX_PATHS),
            (
                "14_context/memory/index/raw_index.json",
                "14_context/memory/index/handoff_index.json",
            ),
        )

    def test_view_index_is_local_pointer_layer_with_current_source_hashes(self):
        index = self.obsidian.build_view_index(REPO_ROOT)
        self.assertTrue(index["local_only"])
        self.assertFalse(index["canonical_truth"])
        self.assertFalse(index["network_used"])
        self.assertFalse(index["model_used"])
        self.assertFalse(index["live_actions_enabled"])
        self.assertEqual(index["hash_mode"], "sha256_canonical_text_lf_binary_raw")
        self.assertEqual(index["view_count"], len(self.obsidian.VIEW_NAMES))
        for source in index["source_indexes"]:
            path = REPO_ROOT / source["path"]
            self.assertTrue(path.is_file())
            self.assertEqual(source["sha256"], self.obsidian.sha256_file(path))

    def test_views_are_deterministic_ascii_and_token_bounded(self):
        first = self.obsidian.render_views(REPO_ROOT)
        second = self.obsidian.render_views(REPO_ROOT)
        self.assertEqual(first, second)
        for name, text in first.items():
            self.assertTrue(text.isascii(), name)
            self.assertLessEqual(
                self.obsidian.word_count(text),
                self.obsidian.VIEW_WORD_BUDGETS[name],
                name,
            )

    def test_views_are_explicitly_noncanonical_and_source_linked(self):
        views = self.obsidian.render_views(REPO_ROOT)
        for name, text in views.items():
            self.assertIn("not canonical truth", text.lower(), name)
            self.assertIn("source", text.lower(), name)
        self.assertIn("../generated/latest_state.md", views["CURRENT_STATE.md"])
        self.assertIn("../generated/context_map.md", views["CURRENT_STATE.md"])
        self.assertIn("../index/handoff_index.json", views["AGENT_HANDOFFS.md"])
        self.assertIn("Human approval remains required", views["SAFETY_GATES.md"])

    def test_all_generated_markdown_links_resolve_without_network(self):
        result = self.obsidian.verify_rendered_links(REPO_ROOT, self.obsidian.render_views(REPO_ROOT))
        self.assertTrue(result["ok"], result)
        self.assertGreater(result["checked_links"], 10)
        self.assertFalse(result["network_links_allowed"])

    def test_write_scope_is_only_obsidian_views_and_view_index(self):
        source_before = {
            path: self.obsidian.sha256_file(REPO_ROOT / path)
            for path in self.obsidian.SOURCE_INDEX_PATHS
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            written = self.obsidian.write_views(REPO_ROOT, root, root)
            relative = sorted(path.relative_to(root.resolve()).as_posix() for path in written)
            self.assertEqual(
                relative,
                sorted(
                    [
                        *(f"obsidian/{name}" for name in self.obsidian.VIEW_NAMES),
                        "index/obsidian_view_index.json",
                    ]
                ),
            )
        source_after = {
            path: self.obsidian.sha256_file(REPO_ROOT / path)
            for path in self.obsidian.SOURCE_INDEX_PATHS
        }
        self.assertEqual(source_before, source_after)

    def test_output_path_must_stay_inside_memory_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(ValueError):
                self.obsidian.write_views(REPO_ROOT, root)
            with self.assertRaises(ValueError):
                self.obsidian.write_views(REPO_ROOT, root / ".." / "escape", root)

    def test_verify_detects_tampered_view(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.obsidian.write_views(REPO_ROOT, root, root)
            index = json.loads((root / "index" / "obsidian_view_index.json").read_text(encoding="utf-8"))
            self.assertTrue(self.obsidian.verify_view_index(root, index)["ok"])
            (root / "obsidian" / "CURRENT_STATE.md").write_text("changed\n", encoding="utf-8")
            self.assertFalse(self.obsidian.verify_view_index(root, index)["ok"])

    def test_committed_views_readme_and_index_exist(self):
        expected = [
            *(f"14_context/memory/obsidian/{name}" for name in self.obsidian.VIEW_NAMES),
            "14_context/memory/index/obsidian_view_index.json",
            "14_context/memory/README.md",
        ]
        for path in expected:
            self.assertTrue((REPO_ROOT / path).is_file(), path)
        readme = (MEMORY_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("obsidian/START_HERE.md", readme)
        self.assertIn("not canonical truth", readme.lower())

    def test_no_private_obsidian_workspace_state_is_declared_or_written(self):
        declared = json.dumps(
            {
                "views": self.obsidian.VIEW_NAMES,
                "sources": self.obsidian.SOURCE_INDEX_PATHS,
                "outputs": self.obsidian.expected_output_paths(),
            }
        )
        for forbidden in [".obsidian", "workspace.json", "community-plugins.json", "plugins/"]:
            self.assertNotIn(forbidden, declared)

    def test_cli_check_write_and_verify_are_safe_json(self):
        for command in ("--check", "--write", "--verify"):
            result = subprocess.run(
                [sys.executable, str(SCRIPT), command, "--json"],
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

    def test_context_map_surfaces_obsidian_entry_point(self):
        result = subprocess.run(
            [sys.executable, str(MEMORY_MAP), "--write", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        context_map = (MEMORY_ROOT / "generated" / "context_map.md").read_text(encoding="utf-8")
        latest_state = (MEMORY_ROOT / "generated" / "latest_state.md").read_text(encoding="utf-8")
        self.assertIn("obsidian/START_HERE.md", context_map)
        self.assertIn("obsidian_view_index.json", context_map)
        self.assertIn("Obsidian memory view", latest_state)

    def test_script_has_no_network_model_launch_or_command_execution(self):
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
            "obsidian://",
            "subprocess.Popen",
            "subprocess.call",
            "subprocess.check_",
        ]
        for needle in forbidden:
            self.assertNotIn(needle, text)

    def test_data_only_write_fallback_has_no_command_surface(self):
        helper = self.obsidian._NODE_WRITE_SCRIPT
        self.assertIn("writeFileSync", helper)
        self.assertIn("Buffer.from", helper)
        for forbidden in ["child_process", "exec", "spawn", "eval", "shell"]:
            self.assertNotIn(forbidden, helper)
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('["node", "-e", _NODE_WRITE_SCRIPT', text)


if __name__ == "__main__":
    unittest.main()
