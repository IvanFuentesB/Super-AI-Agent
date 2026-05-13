#!/usr/bin/env python3
"""N+4.4A tests: desktop_operator_control_plane."""
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


class N44ADesktopOperatorControlPlaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plane = _import_script("desktop_operator_control_plane")

    def test_script_has_no_bom(self):
        raw = (SCRIPTS_DIR / "desktop_operator_control_plane.py").read_bytes()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))

    def test_status_json_returns_local_only(self):
        f = io.StringIO()
        with redirect_stdout(f):
            rc = self.plane.cmd_status(json_out=True)
        self.assertEqual(rc, 0)
        data = json.loads(f.getvalue())
        self.assertEqual(data["default_mode"], "dry_run")
        self.assertTrue(data["local_only"])
        self.assertFalse(data["live_account_actions_enabled"])
        self.assertFalse(data["external_api_actions_enabled"])
        self.assertFalse(data["money_actions_enabled"])
        self.assertFalse(data["publish_actions_enabled"])
        self.assertFalse(data["arbitrary_click_or_type_enabled"])
        self.assertFalse(data["shell_exec_from_model_output_enabled"])
        self.assertFalse(data["gemini_treated_as_unlimited"])
        self.assertFalse(data["gemini_live_prompt_executed"])
        self.assertEqual(data["external_tools_status"], "planning_only")

    def test_cli_bare_json_emits_status(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "desktop_operator_control_plane.py"), "--json"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["control_plane"], "desktop_operator_control_plane")
        self.assertEqual(data["default_mode"], "dry_run")

    def test_build_handoff_valid_schema(self):
        payload = self.plane._build_handoff("test goal", "content_studio_demo")
        ok, errors = self.plane.validate_handoff(payload)
        self.assertTrue(ok, f"Validation failed: {errors}")

    def test_validate_rejects_live_account_actions(self):
        payload = self.plane._build_handoff("test goal", "content_studio_demo")
        payload["live_account_actions_enabled"] = True
        ok, errors = self.plane.validate_handoff(payload)
        self.assertFalse(ok)
        self.assertTrue(any("live_account_actions_enabled" in e for e in errors))

    def test_validate_rejects_publish_actions(self):
        payload = self.plane._build_handoff("test goal", "content_studio_demo")
        payload["publish_actions_enabled"] = True
        ok, errors = self.plane.validate_handoff(payload)
        self.assertFalse(ok)
        self.assertTrue(any("publish_actions_enabled" in e for e in errors))

    def test_validate_rejects_money_actions(self):
        payload = self.plane._build_handoff("test goal", "content_studio_demo")
        payload["money_actions_enabled"] = True
        ok, errors = self.plane.validate_handoff(payload)
        self.assertFalse(ok)
        self.assertTrue(any("money_actions_enabled" in e for e in errors))

    def test_validate_rejects_external_api_actions(self):
        payload = self.plane._build_handoff("test goal", "content_studio_demo")
        payload["external_api_actions_enabled"] = True
        ok, errors = self.plane.validate_handoff(payload)
        self.assertFalse(ok)
        self.assertTrue(any("external_api_actions_enabled" in e for e in errors))

    def test_validate_rejects_forbidden_action_in_allowed(self):
        payload = self.plane._build_handoff("test goal", "content_studio_demo")
        payload["allowed_actions"].append("arbitrary_click")
        ok, errors = self.plane.validate_handoff(payload)
        self.assertFalse(ok)
        self.assertTrue(any("arbitrary_click" in e for e in errors))

    def test_validate_rejects_ui_tars_runtime_wired(self):
        payload = self.plane._build_handoff("test goal", "content_studio_demo")
        payload["ui_tars_runtime_wired"] = True
        ok, errors = self.plane.validate_handoff(payload)
        self.assertFalse(ok)
        self.assertTrue(any("ui_tars_runtime_wired" in e for e in errors))

    def test_validate_rejects_external_repo_runtime(self):
        payload = self.plane._build_handoff("test goal", "content_studio_demo")
        payload["external_repo_clone_install_run_enabled"] = True
        ok, errors = self.plane.validate_handoff(payload)
        self.assertFalse(ok)

    def test_create_handoff_writes_artifacts(self):
        with tempfile.TemporaryDirectory(dir=str(REPO_ROOT / "14_context")) as tmp:
            tmp_path = pathlib.Path(tmp)
            orig = self.plane.RUNS_DIR
            self.plane.RUNS_DIR = tmp_path
            try:
                f = io.StringIO()
                with redirect_stdout(f):
                    rc = self.plane.cmd_create_handoff("test goal local", "content_studio_demo", json_out=True)
                self.assertEqual(rc, 0)
                result = json.loads(f.getvalue())
                self.assertTrue(result["ok"])
                self.assertTrue(result["approval_required"])
            finally:
                self.plane.RUNS_DIR = orig

    def test_dry_run_no_execution(self):
        with tempfile.TemporaryDirectory(dir=str(REPO_ROOT)) as tmp:
            tmp_path = pathlib.Path(tmp)
            orig = self.plane.RUNS_DIR
            self.plane.RUNS_DIR = tmp_path
            try:
                f = io.StringIO()
                with redirect_stdout(f):
                    self.plane.cmd_create_handoff("plan goal", "content_studio_demo", json_out=True)
                rd = [d for d in tmp_path.iterdir() if d.is_dir()][0]
                handoff = rd / "00_handoff_payload.json"
                f2 = io.StringIO()
                with redirect_stdout(f2):
                    rc = self.plane.cmd_dry_run(str(handoff), json_out=True)
                self.assertEqual(rc, 0)
                result = json.loads(f2.getvalue())
                self.assertTrue(result["ok"])
                self.assertEqual(result["actions_executed"], 0)
                self.assertTrue(result["approval_required_next"])
                self.assertFalse(result["model_status_brief"]["gemini_treated_as_unlimited"])
                self.assertFalse(result["model_status_brief"]["gemini_live_prompt_executed"])
            finally:
                self.plane.RUNS_DIR = orig



    def test_execute_approved_fails_no_approval(self):
        import os as _os
        with tempfile.TemporaryDirectory(dir=str(REPO_ROOT)) as tmp:
            tmp_path = pathlib.Path(tmp)
            orig = self.plane.RUNS_DIR
            self.plane.RUNS_DIR = tmp_path
            try:
                f = io.StringIO()
                with redirect_stdout(f):
                    self.plane.cmd_create_handoff("noapproval", "content_studio_demo", json_out=True)
                rd = [d for d in tmp_path.iterdir() if d.is_dir()][0]
                handoff = _os.path.join(str(rd), "00_handoff_payload.json")
                f2 = io.StringIO()
                with redirect_stdout(f2):
                    rc = self.plane.cmd_execute_approved(handoff, json_out=True)
                self.assertEqual(rc, 1)
                result = json.loads(f2.getvalue())
                self.assertFalse(result["ok"])
            finally:
                self.plane.RUNS_DIR = orig

    def test_approve_requires_token(self):
        import os as _os
        with tempfile.TemporaryDirectory(dir=str(REPO_ROOT)) as tmp:
            tmp_path = pathlib.Path(tmp)
            orig = self.plane.RUNS_DIR
            self.plane.RUNS_DIR = tmp_path
            try:
                f = io.StringIO()
                with redirect_stdout(f):
                    self.plane.cmd_create_handoff("g", "content_studio_demo", json_out=True)
                rd = [d for d in tmp_path.iterdir() if d.is_dir()][0]
                handoff = _os.path.join(str(rd), "00_handoff_payload.json")
                f2 = io.StringIO()
                with redirect_stdout(f2):
                    rc = self.plane.cmd_approve(handoff, "", json_out=True)
                self.assertEqual(rc, 1)
                result = json.loads(f2.getvalue())
                self.assertFalse(result["ok"])
            finally:
                self.plane.RUNS_DIR = orig

    def test_full_approve_then_execute_pipeline(self):
        import os as _os
        with tempfile.TemporaryDirectory(dir=str(REPO_ROOT)) as tmp:
            tmp_path = pathlib.Path(tmp)
            orig = self.plane.RUNS_DIR
            self.plane.RUNS_DIR = tmp_path
            try:
                f = io.StringIO()
                with redirect_stdout(f):
                    self.plane.cmd_create_handoff("full pipe", "content_studio_demo", json_out=True)
                rd = [d for d in tmp_path.iterdir() if d.is_dir()][0]
                handoff = _os.path.join(str(rd), "00_handoff_payload.json")
                f2 = io.StringIO()
                with redirect_stdout(f2):
                    self.plane.cmd_approve(handoff, "valid-token-aaaa", json_out=True)
                approval_path = _os.path.join(str(rd), "04_approval_record.json")
                self.assertTrue(_os.path.exists(approval_path))
                f3 = io.StringIO()
                with redirect_stdout(f3):
                    rc = self.plane.cmd_execute_approved(handoff, json_out=True)
                self.assertEqual(rc, 0)
                exec_result = json.loads(f3.getvalue())
                self.assertTrue(exec_result["ok"])
                self.assertFalse(exec_result["arbitrary_click_or_type_executed"])
                self.assertFalse(exec_result["shell_exec_from_model_output_executed"])
                self.assertFalse(exec_result["live_account_actions_executed"])
                self.assertFalse(exec_result["posting_executed"])
                self.assertFalse(exec_result["external_repo_clone_install_run_executed"])
                exec_path = _os.path.join(str(rd), "05_execution_result.json")
                self.assertTrue(_os.path.exists(exec_path))
            finally:
                self.plane.RUNS_DIR = orig

    def test_outside_repo_handoff_path_rejected(self):
        import os as _os
        bogus = _os.path.join(_os.path.expanduser("~"), "definitely_not_in_repo_xyz.json")
        f = io.StringIO()
        with redirect_stdout(f):
            rc = self.plane.cmd_validate_handoff(bogus, json_out=True)
        self.assertEqual(rc, 1)

    def test_gemini_status_safe(self):
        probe = self.plane._probe_gemini_cli()
        self.assertEqual(probe["adapter"], "gemini_cli")
        self.assertFalse(probe["treated_as_unlimited"])
        self.assertFalse(probe["live_prompt_executed"])
        self.assertEqual(probe["quota"], "unknown_free_tier_limited")

    def test_local_demo_always_available(self):
        p = self.plane._probe_local_demo()
        self.assertTrue(p["available"])
        self.assertFalse(p["live_prompt_executed"])

    def test_content_studio_link_visible(self):
        ops = self.plane._probe_operator_adapters()
        self.assertIn("content_studio_demo_present", ops)


if __name__ == "__main__":
    unittest.main()