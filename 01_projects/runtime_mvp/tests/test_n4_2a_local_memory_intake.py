#!/usr/bin/env python3
"""N+4.2A tests: local_memory_compression_bridge and repo_skill_plugin_intake.

Tests cover:
- Outside-repo path rejected
- Secret path rejected
- local_demo compression works
- snapshot writes expected files
- registry validates (all blocked flags false)
- registry blocks runtime_wiring=true
- registry blocks clone_install_run_enabled=true
- registry blocks live_account_action_enabled=true
- Ollama missing does not crash
- --status JSON includes required truth fields
"""
import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest

# ---------------------------------------------------------------------------
# Helpers to import scripts from 03_scripts/
# ---------------------------------------------------------------------------
REPO_ROOT = pathlib.Path(__file__).parent.parent.parent.parent.resolve()  # tests -> runtime_mvp -> 01_projects -> repo root
SCRIPTS_DIR = REPO_ROOT / "03_scripts"


def _import_script(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class N42ALocalMemoryTests(unittest.TestCase):
    """Tests for local_memory_compression_bridge."""

    @classmethod
    def setUpClass(cls):
        cls.bridge = _import_script("local_memory_compression_bridge")

    # ------------------------------------------------------------------
    # Security / path validation
    # ------------------------------------------------------------------

    def test_outside_repo_path_rejected(self):
        """N+4.2A: --compress-file with path outside repo root must return exit code 1."""
        # We call cmd_compress_file directly with a path outside REPO_ROOT
        rc = self.bridge.cmd_compress_file("C:/Windows/System32/drivers/etc/hosts", write=False, json_out=False)
        self.assertEqual(rc, 1, "Path outside repo root must be rejected with exit code 1")

    def test_secret_path_rejected(self):
        """N+4.2A: --compress-file with a secrets-pattern filename must return exit code 1."""
        # Create a temp file inside repo root but with secret name
        secret_path = REPO_ROOT / "03_scripts" / ".env"
        try:
            secret_path.write_text("SECRET=test", encoding="utf-8")
            rc = self.bridge.cmd_compress_file(str(secret_path), write=False, json_out=False)
            self.assertEqual(rc, 1, "Secret-pattern path must be rejected")
        finally:
            if secret_path.exists():
                secret_path.unlink()

    def test_nonexistent_file_rejected(self):
        """N+4.2A: --compress-file with nonexistent file must return exit code 1."""
        rc = self.bridge.cmd_compress_file(str(REPO_ROOT / "03_scripts" / "definitely_not_real_xyzzy.txt"), write=False, json_out=False)
        self.assertEqual(rc, 1)

    # ------------------------------------------------------------------
    # local_demo compression
    # ------------------------------------------------------------------

    def test_local_demo_compression_works(self):
        """N+4.2A: _compress_local_demo produces non-empty output for demo text."""
        result = self.bridge._compress_local_demo(self.bridge.DEMO_TEXT)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 10, "Demo compression must produce non-empty output")
        self.assertIn("N+4.2A", result, "Demo summary must include N+4.2A marker")

    def test_local_demo_truncates_long_text(self):
        """N+4.2A: _compress_local_demo truncates text beyond 30 lines."""
        long_text = "\n".join([f"line {i}" for i in range(50)])
        result = self.bridge._compress_local_demo(long_text)
        self.assertIn("omitted in local_demo mode", result, "Long text must show omitted note")

    def test_local_demo_short_text_no_truncation(self):
        """N+4.2A: _compress_local_demo does not truncate text <= 30 lines."""
        short_text = "line one\nline two\nline three"
        result = self.bridge._compress_local_demo(short_text)
        self.assertNotIn("omitted", result)

    # ------------------------------------------------------------------
    # Snapshot write
    # ------------------------------------------------------------------

    def test_write_snapshot_creates_files(self):
        """N+4.2A: cmd_compress with write=True creates compact and obsidian files."""
        import io
        from contextlib import redirect_stdout

        # Patch output dirs to tempdir so we don't pollute real dirs
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            orig_compact = self.bridge.COMPACT_MEMORY_DIR
            orig_obsidian = self.bridge.OBSIDIAN_VAULT_DIR
            self.bridge.COMPACT_MEMORY_DIR = tmp_path / "compact"
            self.bridge.OBSIDIAN_VAULT_DIR = tmp_path / "obsidian"
            try:
                f = io.StringIO()
                with redirect_stdout(f):
                    rc = self.bridge.cmd_compress(
                        source_text="test content\nline two",
                        source_files=["test_source"],
                        write=True,
                        json_out=True,
                    )
                self.assertEqual(rc, 0)
                out = json.loads(f.getvalue())
                self.assertTrue(out["written"], "written must be True")
                self.assertIsNotNone(out["compact_path"])
                self.assertIsNotNone(out["obsidian_path"])
                self.assertTrue(out["local_only"])
                self.assertFalse(out["external_api_used"])
                self.assertTrue(out["approval_required_for_external_actions"])
            finally:
                self.bridge.COMPACT_MEMORY_DIR = orig_compact
                self.bridge.OBSIDIAN_VAULT_DIR = orig_obsidian

    def test_write_snapshot_false_does_not_write(self):
        """N+4.2A: cmd_compress with write=False must not write files."""
        import io
        from contextlib import redirect_stdout

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            orig_compact = self.bridge.COMPACT_MEMORY_DIR
            orig_obsidian = self.bridge.OBSIDIAN_VAULT_DIR
            self.bridge.COMPACT_MEMORY_DIR = tmp_path / "compact"
            self.bridge.OBSIDIAN_VAULT_DIR = tmp_path / "obsidian"
            try:
                f = io.StringIO()
                with redirect_stdout(f):
                    rc = self.bridge.cmd_compress(
                        source_text="test content",
                        source_files=["test_source"],
                        write=False,
                        json_out=True,
                    )
                self.assertEqual(rc, 0)
                out = json.loads(f.getvalue())
                self.assertFalse(out["written"])
                # No files should exist
                compact_files = list(tmp_path.glob("**/*.md"))
                self.assertEqual(len(compact_files), 0, "No files should be written when write=False")
            finally:
                self.bridge.COMPACT_MEMORY_DIR = orig_compact
                self.bridge.OBSIDIAN_VAULT_DIR = orig_obsidian

    # ------------------------------------------------------------------
    # Ollama missing must not crash
    # ------------------------------------------------------------------

    def test_probe_ollama_missing_does_not_crash(self):
        """N+4.2A: _probe_ollama must return gracefully if ollama is not found."""
        import unittest.mock as mock
        # Simulate FileNotFoundError for ollama command
        with mock.patch("subprocess.run", side_effect=FileNotFoundError("ollama not found")):
            result = self.bridge._probe_ollama()
        self.assertFalse(result["ollama_available"])
        self.assertEqual(result["fallback_mode"], "local_demo")
        # probe_error will say "NOT_FOUND" or "ollama not found" depending on path hit
        self.assertTrue(
            "NOT_FOUND" in result["probe_error"] or "not found" in result["probe_error"].lower(),
            f"Expected probe_error to indicate missing ollama, got: {result['probe_error']}"
        )

    def test_status_json_includes_truth_fields(self):
        """N+4.2A: --status --json must include required truth fields."""
        import io
        from contextlib import redirect_stdout
        f = io.StringIO()
        with redirect_stdout(f):
            rc = self.bridge.cmd_status(json_out=True)
        self.assertEqual(rc, 0)
        data = json.loads(f.getvalue())
        required_fields = [
            "bridge", "local_only", "external_api_used",
            "ollama_available", "gemma_model_found", "fallback_mode",
            "approval_required_for_external_actions",
        ]
        for field in required_fields:
            self.assertIn(field, data, f"Status JSON missing field: {field}")
        self.assertTrue(data["local_only"])
        self.assertFalse(data["external_api_used"])
        self.assertTrue(data["approval_required_for_external_actions"])


class N42ARepoSkillPluginIntakeTests(unittest.TestCase):
    """Tests for repo_skill_plugin_intake."""

    @classmethod
    def setUpClass(cls):
        cls.intake = _import_script("repo_skill_plugin_intake")

    def test_catalog_has_22_entries(self):
        """N+4.2A: catalog must have exactly 22 entries."""
        self.assertEqual(len(self.intake.CATALOG), 22)

    def test_validate_config_passes_clean(self):
        """N+4.2A: validate_catalog passes for clean catalog (all flags false)."""
        ok, errors = self.intake.validate_catalog(self.intake.CATALOG)
        self.assertTrue(ok, f"Validation must pass for clean catalog. Errors: {errors}")
        self.assertEqual(errors, [])

    def test_validate_blocks_runtime_wiring_true(self):
        """N+4.2A: validate_catalog fails if any entry has current_runtime_wiring=True."""
        bad_catalog = dict(self.intake.CATALOG)
        bad_catalog["__test__"] = {
            "name": "test",
            "current_runtime_wiring": True,
            "clone_install_run_enabled": False,
            "live_account_action_enabled": False,
        }
        ok, errors = self.intake.validate_catalog(bad_catalog)
        self.assertFalse(ok)
        self.assertTrue(any("current_runtime_wiring" in e for e in errors))

    def test_validate_blocks_clone_install_run_true(self):
        """N+4.2A: validate_catalog fails if any entry has clone_install_run_enabled=True."""
        bad_catalog = dict(self.intake.CATALOG)
        bad_catalog["__test__"] = {
            "name": "test",
            "current_runtime_wiring": False,
            "clone_install_run_enabled": True,
            "live_account_action_enabled": False,
        }
        ok, errors = self.intake.validate_catalog(bad_catalog)
        self.assertFalse(ok)
        self.assertTrue(any("clone_install_run_enabled" in e for e in errors))

    def test_validate_blocks_live_account_action_true(self):
        """N+4.2A: validate_catalog fails if any entry has live_account_action_enabled=True."""
        bad_catalog = dict(self.intake.CATALOG)
        bad_catalog["__test__"] = {
            "name": "test",
            "current_runtime_wiring": False,
            "clone_install_run_enabled": False,
            "live_account_action_enabled": True,
        }
        ok, errors = self.intake.validate_catalog(bad_catalog)
        self.assertFalse(ok)
        self.assertTrue(any("live_account_action_enabled" in e for e in errors))

    def test_all_entries_have_required_fields(self):
        """N+4.2A: every catalog entry must have required safety fields."""
        required = [
            "name", "type", "category", "status",
            "current_runtime_wiring", "clone_install_run_enabled", "live_account_action_enabled",
            "allowed_actions", "forbidden_actions", "approval_gate", "risk_level",
        ]
        for tool_id, entry in self.intake.CATALOG.items():
            for field in required:
                self.assertIn(field, entry, f"Entry '{tool_id}' missing field: {field}")

    def test_all_blocked_flags_are_false(self):
        """N+4.2A: all entries have all blocked flags = False."""
        for tool_id, entry in self.intake.CATALOG.items():
            self.assertFalse(entry["current_runtime_wiring"], f"'{tool_id}' has current_runtime_wiring=True")
            self.assertFalse(entry["clone_install_run_enabled"], f"'{tool_id}' has clone_install_run_enabled=True")
            self.assertFalse(entry["live_account_action_enabled"], f"'{tool_id}' has live_account_action_enabled=True")

    def test_metatrader_is_blocked_until_approval(self):
        """N+4.2A: Claude+MetaTrader must be blocked_until_approval (no live trading)."""
        entry = self.intake.CATALOG["claude_metatrader"]
        self.assertEqual(entry["status"], "blocked_until_approval")
        self.assertIn("live_trading", entry["forbidden_actions"])

    def test_ethical_hacking_is_blocked_until_approval(self):
        """N+4.2A: ethical hacking must be blocked_until_approval."""
        entry = self.intake.CATALOG["ethical_hacking"]
        self.assertEqual(entry["status"], "blocked_until_approval")
        self.assertIn("unauthorized_target_attack", entry["forbidden_actions"])

    def test_internship_scraper_is_blocked_until_approval(self):
        """N+4.2A: internship scraper must be blocked_until_approval."""
        entry = self.intake.CATALOG["internship_scraper"]
        self.assertEqual(entry["status"], "blocked_until_approval")
        self.assertIn("autonomous_application_submission", entry["forbidden_actions"])

    def test_status_json_includes_truth_fields(self):
        """N+4.2A: --status --json must include wiring=none and approval_required."""
        import io
        from contextlib import redirect_stdout
        f = io.StringIO()
        with redirect_stdout(f):
            rc = self.intake.cmd_status(json_out=True)
        self.assertEqual(rc, 0)
        data = json.loads(f.getvalue())
        self.assertEqual(data["tool_count"], 22)
        self.assertTrue(data["validation_ok"])
        self.assertFalse(data["current_runtime_wiring_any"])
        self.assertFalse(data["clone_install_run_any"])
        self.assertFalse(data["live_account_action_any"])
        self.assertEqual(data["external_wiring_status"], "none")
        self.assertTrue(data["human_approval_required"])


if __name__ == "__main__":
    unittest.main()