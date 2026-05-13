#!/usr/bin/env python3
"""N+4.3A tests: supervised_content_studio_demo.

Tests cover:
- --status JSON has required truth fields
- bare --json works
- --run-demo --json produces all artifacts
- 100 title variants
- 100 thumbnail variants
- safety review says no live posting
- preview HTML exists with required strings
- manifest lists all 8 agents
- output dir outside repo rejected
- secret-pattern output dir rejected
"""
import importlib.util
import io
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

REPO_ROOT = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
SCRIPTS_DIR = REPO_ROOT / "03_scripts"


def _import_script(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class N43AContentStudioTests(unittest.TestCase):
    """Tests for supervised_content_studio_demo."""

    @classmethod
    def setUpClass(cls):
        cls.studio = _import_script("supervised_content_studio_demo")

    def test_studio_has_8_agents(self):
        """N+4.3A: AGENT_NAMES must have exactly 8 agents."""
        self.assertEqual(len(self.studio.AGENT_NAMES), 8)

    def test_script_has_no_bom(self):
        """N+4.3A: script source must not start with UTF-8 BOM."""
        raw = (SCRIPTS_DIR / "supervised_content_studio_demo.py").read_bytes()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))

    def test_status_json_includes_truth_fields(self):
        """N+4.3A: --status --json must include local_only, external_api_used, agent_count."""
        f = io.StringIO()
        with redirect_stdout(f):
            rc = self.studio.cmd_status(json_out=True)
        self.assertEqual(rc, 0)
        data = json.loads(f.getvalue())
        self.assertTrue(data["local_only"])
        self.assertFalse(data["external_api_used"])
        self.assertFalse(data["publish_enabled"])
        self.assertTrue(data["approval_required"])
        self.assertEqual(data["agent_count"], 8)
        self.assertEqual(len(data["agents"]), 8)
        self.assertEqual(data["external_tools_status"], "planning_only")

    def test_outside_repo_output_dir_rejected(self):
        """N+4.3A: --output-dir outside repo must return rc=1."""
        f = io.StringIO()
        with redirect_stdout(f):
            rc = self.studio.cmd_run_demo("test", "C:/Windows/System32", json_out=False)
        self.assertEqual(rc, 1)

    def test_secret_pattern_output_dir_rejected(self):
        """N+4.3A: --output-dir with secret pattern must return rc=1."""
        secret_dir = REPO_ROOT / "14_context" / ".env_runs"
        f = io.StringIO()
        with redirect_stdout(f):
            rc = self.studio.cmd_run_demo("test", str(secret_dir), json_out=False)
        self.assertEqual(rc, 1)

    def test_full_demo_creates_all_artifacts(self):
        """N+4.3A: --run-demo creates a full run folder under a temp dir inside the repo."""
        # Use a subdir inside REPO_ROOT to satisfy _is_inside_repo
        with tempfile.TemporaryDirectory(dir=str(REPO_ROOT / "14_context")) as tmp:
            tmp_path = pathlib.Path(tmp)
            f = io.StringIO()
            with redirect_stdout(f):
                rc = self.studio.cmd_run_demo("AI tools for students and creators", str(tmp_path), json_out=True)
            self.assertEqual(rc, 0)
            status = json.loads(f.getvalue())
            self.assertTrue(status["ok"])
            self.assertEqual(status["agent_count"], 8)
            self.assertEqual(status["title_variant_count"], 100)
            self.assertEqual(status["thumbnail_variant_count"], 100)
            self.assertTrue(status["local_only"])
            self.assertFalse(status["external_api_used"])
            self.assertFalse(status["publish_enabled"])

            # Find the run folder
            run_dirs = [d for d in tmp_path.iterdir() if d.is_dir()]
            self.assertEqual(len(run_dirs), 1)
            run_dir = run_dirs[0]
            expected = [
                "00_manifest.json", "01_agent_trace.md", "02_strategy.md",
                "03_script.md", "04_shotlist.md", "05_titles_100.json",
                "06_thumbnail_variants_100.json", "07_safety_review.md",
                "08_human_approval_packet.md", "09_memory_snapshot.md",
                "10_preview.html", "11_status.json",
            ]
            for name in expected:
                p = run_dir / name
                self.assertTrue(p.exists(), f"Missing artifact: {name}")
                self.assertGreater(p.stat().st_size, 0, f"Empty artifact: {name}")

    def test_manifest_lists_all_8_agents(self):
        with tempfile.TemporaryDirectory(dir=str(REPO_ROOT / "14_context")) as tmp:
            f = io.StringIO()
            with redirect_stdout(f):
                self.studio.cmd_run_demo("agents_test", str(pathlib.Path(tmp)), json_out=True)
            run_dirs = [d for d in pathlib.Path(tmp).iterdir() if d.is_dir()]
            manifest = json.loads((run_dirs[0] / "00_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["agent_count"], 8)
            self.assertEqual(len(manifest["agents"]), 8)
            expected_agents = {
                "strategy_agent", "research_meta_agent", "script_agent",
                "shotlist_agent", "title_thumbnail_agent",
                "safety_compliance_agent", "approval_agent", "memory_agent",
            }
            self.assertEqual(set(manifest["agents"]), expected_agents)
            self.assertFalse(manifest["external_api_used"])
            self.assertFalse(manifest["publish_enabled"])
            self.assertFalse(manifest["external_repo_clone_install_run"])
            self.assertFalse(manifest["live_account_actions_enabled"])

    def test_titles_100_json_has_100_variants(self):
        with tempfile.TemporaryDirectory(dir=str(REPO_ROOT / "14_context")) as tmp:
            f = io.StringIO()
            with redirect_stdout(f):
                self.studio.cmd_run_demo("titles_test", str(pathlib.Path(tmp)), json_out=True)
            run_dirs = [d for d in pathlib.Path(tmp).iterdir() if d.is_dir()]
            titles = json.loads((run_dirs[0] / "05_titles_100.json").read_text(encoding="utf-8"))
            self.assertEqual(titles["count"], 100)
            self.assertEqual(len(titles["titles"]), 100)
            for t in titles["titles"]:
                self.assertFalse(t["autonomous_posting_enabled"])
                self.assertFalse(t["ab_test_runtime_wired"])

    def test_thumbnails_100_json_has_100_variants(self):
        with tempfile.TemporaryDirectory(dir=str(REPO_ROOT / "14_context")) as tmp:
            f = io.StringIO()
            with redirect_stdout(f):
                self.studio.cmd_run_demo("thumbs_test", str(pathlib.Path(tmp)), json_out=True)
            run_dirs = [d for d in pathlib.Path(tmp).iterdir() if d.is_dir()]
            thumbs = json.loads((run_dirs[0] / "06_thumbnail_variants_100.json").read_text(encoding="utf-8"))
            self.assertEqual(thumbs["count"], 100)
            self.assertEqual(len(thumbs["thumbnails"]), 100)
            for t in thumbs["thumbnails"]:
                self.assertFalse(t["uses_copyrighted_media"])
                self.assertFalse(t["uses_real_face"])
                self.assertFalse(t["autonomous_posting_enabled"])
                self.assertEqual(t["asset_source"], "local_mock_only")

    def test_safety_review_blocks_live_posting(self):
        with tempfile.TemporaryDirectory(dir=str(REPO_ROOT / "14_context")) as tmp:
            f = io.StringIO()
            with redirect_stdout(f):
                self.studio.cmd_run_demo("safety_test", str(pathlib.Path(tmp)), json_out=True)
            run_dirs = [d for d in pathlib.Path(tmp).iterdir() if d.is_dir()]
            safety = (run_dirs[0] / "07_safety_review.md").read_text(encoding="utf-8")
            self.assertIn("live_posting_enabled: false", safety)
            self.assertIn("external_apis_enabled: false", safety)
            self.assertIn("external_repo_clone_install_run: false", safety)
            self.assertIn("live_account_actions_enabled: false", safety)
            self.assertIn("autonomous_money_or_trading_actions: false", safety)
            self.assertIn("PASS_LOCAL_ONLY", safety)

    def test_preview_html_has_required_strings(self):
        with tempfile.TemporaryDirectory(dir=str(REPO_ROOT / "14_context")) as tmp:
            f = io.StringIO()
            with redirect_stdout(f):
                self.studio.cmd_run_demo("preview_test", str(pathlib.Path(tmp)), json_out=True)
            run_dirs = [d for d in pathlib.Path(tmp).iterdir() if d.is_dir()]
            html_path = run_dirs[0] / "10_preview.html"
            self.assertTrue(html_path.exists())
            html_text = html_path.read_text(encoding="utf-8")
            self.assertIn("Local preview only", html_text)
            self.assertIn("local_only: true", html_text)
            self.assertIn("external_api_used: false", html_text)
            self.assertIn("publish_enabled: false", html_text)
            self.assertIn("approval_required: true", html_text)
            self.assertIn("Publish (disabled", html_text)
            self.assertIn("aria-disabled=\"true\"", html_text)
            self.assertIn("Supervised Multi-Agent Content Studio", html_text)
            self.assertIn("N+4.3A", html_text)
            self.assertIn("strategy_agent", html_text)
            self.assertIn("title_thumbnail_agent", html_text)

    def test_memory_snapshot_path_approved(self):
        with tempfile.TemporaryDirectory(dir=str(REPO_ROOT / "14_context")) as tmp:
            f = io.StringIO()
            with redirect_stdout(f):
                self.studio.cmd_run_demo("memory_test", str(pathlib.Path(tmp)), json_out=True)
            run_dirs = [d for d in pathlib.Path(tmp).iterdir() if d.is_dir()]
            mem = (run_dirs[0] / "09_memory_snapshot.md").read_text(encoding="utf-8")
            self.assertIn("local_only: true", mem)
            self.assertIn("external_api_used: false", mem)
            self.assertIn("approval_required_for_external_actions: true", mem)

    def test_status_json_field_external_tools_planning_only(self):
        f = io.StringIO()
        with redirect_stdout(f):
            self.studio.cmd_status(json_out=True)
        data = json.loads(f.getvalue())
        self.assertEqual(data["external_tools_status"], "planning_only")

    def test_cli_status_subprocess_emits_valid_json(self):
        """N+4.3A: CLI --status --json emits parseable JSON without prose."""
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "supervised_content_studio_demo.py"), "--status", "--json"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertTrue(data["local_only"])
        self.assertFalse(data["external_api_used"])

    def test_cli_bare_json_emits_valid_json(self):
        """N+4.3A: bare --json emits status JSON (no prose)."""
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "supervised_content_studio_demo.py"), "--json"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["studio"], "supervised_content_studio_demo")


if __name__ == "__main__":
    unittest.main()