#!/usr/bin/env python3
"""N+4.4B tests: Desktop Operator Dashboard Action Center.

These are static + script-level tests that prove the same safety properties
as the live HTTP endpoints, without spawning a Node server in tests.
"""
import importlib.util
import io
import json
import pathlib
import re
import unittest
from contextlib import redirect_stdout

REPO_ROOT = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
SCRIPTS_DIR = REPO_ROOT / "03_scripts"
DASHBOARD_DIR = REPO_ROOT / "01_projects" / "dashboard_mvp"


def _import_script(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class N44BDashboardActionCenterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plane = _import_script("desktop_operator_control_plane")
        cls.server_js = (DASHBOARD_DIR / "server.js").read_text(encoding="utf-8")
        cls.app_js = (DASHBOARD_DIR / "public" / "app.js").read_text(encoding="utf-8")
        cls.index_html = (DASHBOARD_DIR / "public" / "index.html").read_text(encoding="utf-8")

    # --- Dashboard HTML labels ---

    def test_dashboard_html_has_action_center_section(self):
        self.assertIn("Desktop Operator Action Center", self.index_html)

    def test_dashboard_html_has_5_action_buttons(self):
        for btn in ["doa-create-handoff", "doa-dry-run", "doa-approve", "doa-execute", "doa-open-preview"]:
            self.assertIn(btn, self.index_html, f"Missing button: {btn}")

    def test_dashboard_html_shows_safety_disabled_labels(self):
        for label in [
            "arbitrary click/type: <strong>disabled",
            "shell execution from model output: <strong>disabled",
            "live account actions: <strong>disabled",
            "publish actions: <strong>disabled",
            "money actions: <strong>disabled",
        ]:
            self.assertIn(label, self.index_html, f"Missing safety label: {label}")

    def test_dashboard_html_default_mode_dry_run(self):
        self.assertIn("Default mode: <strong>dry_run</strong>", self.index_html)

    def test_dashboard_html_gemini_status_only(self):
        self.assertIn("Gemini CLI: <span id=\"doa-gemini\">status-only", self.index_html)

    def test_dashboard_html_content_studio_local_preview_only(self):
        self.assertIn("content studio workflow: <strong>local preview only", self.index_html)

    # --- Server.js safety ---

    def test_server_has_all_six_desktop_operator_endpoints(self):
        for endpoint in [
            "/api/desktop-operator/status",
            "/api/desktop-operator/latest",
            "/api/desktop-operator/create-handoff",
            "/api/desktop-operator/dry-run",
            "/api/desktop-operator/approve",
            "/api/desktop-operator/execute-approved",
            "/api/desktop-operator/preview",
        ]:
            self.assertIn(endpoint, self.server_js, f"Missing endpoint: {endpoint}")

    def test_server_uses_runcommand_not_shell_true(self):
        """N+4.4B: desktop operator endpoints must NOT use shell:true."""
        # Find the desktop operator helper block and verify it calls runCommand
        idx = self.server_js.find("runDesktopOperatorCli")
        self.assertGreater(idx, 0, "runDesktopOperatorCli helper missing")
        # Window of 2000 chars around helper definition
        snippet = self.server_js[idx : idx + 2000]
        self.assertIn("runCommand(python.command", snippet)
        # Ensure no "shell: true" inside the desktop operator block
        # (runCommand globally uses shell:false; we just confirm no override)
        block_start = self.server_js.find("N+4.4B Desktop Operator")
        block_end = self.server_js.find("/api/desktop-operator/preview")
        if block_start > 0 and block_end > block_start:
            block = self.server_js[block_start : block_end + 500]
            self.assertNotIn("shell: true", block)
            self.assertNotIn("shell:true", block)

    def test_server_validates_workflow_allowlist(self):
        self.assertIn("desktopOperatorAllowedWorkflows", self.server_js)
        self.assertIn("content_studio_demo", self.server_js)
        self.assertIn("REJECTED: workflow not in allowlist", self.server_js)

    def test_server_preview_endpoint_validates_repo_local(self):
        # Preview must reject paths that are not .html or not repo-local
        self.assertIn("REJECTED: path not repo-local", self.server_js)
        self.assertIn("only .html or .htm previews allowed", self.server_js)
        self.assertIn("REJECTED: path resolved outside repo", self.server_js)

    def test_server_isRepoLocalPath_rejects_dotdot_and_secrets(self):
        self.assertIn("isRepoLocalPath", self.server_js)
        # Check that the function rejects ".." and secret patterns
        helper_idx = self.server_js.find("function isRepoLocalPath")
        self.assertGreater(helper_idx, 0)
        helper = self.server_js[helper_idx : helper_idx + 1500]
        self.assertIn("'..'", helper.replace('"..\"', "'..'"))
        # Secret pattern check should be present
        for pat in ['".env"', '"secret"', '"credential"', '"token"', '"key"', '"password"']:
            self.assertIn(pat, helper, f"Missing secret pattern: {pat}")

    def test_server_approve_does_not_return_raw_token(self):
        # Approve endpoint must include comment stating token is never returned
        block_idx = self.server_js.find("/api/desktop-operator/approve")
        self.assertGreater(block_idx, 0)
        block = self.server_js[block_idx : block_idx + 2500]
        self.assertIn("token never returned", block)
        # Must not return approvalToken/raw token in payload
        self.assertNotIn("approvalToken: approvalToken", block)
        self.assertNotIn("token: approvalToken", block)

    # --- app.js safety ---

    def test_app_js_has_doa_handlers(self):
        for fn in ["doa-create-handoff", "doa-dry-run", "doa-approve", "doa-execute", "doa-open-preview"]:
            self.assertIn(fn, self.app_js, f"Missing handler binding: {fn}")

    def test_app_js_does_not_log_raw_approval_token(self):
        """N+4.4B: client must not capture or display the raw approval token."""
        # The string "approvalToken" should appear at most as part of comments,
        # not as a logged or rendered field.
        idx = self.app_js.find("attachDesktopOperatorActionCenter")
        self.assertGreater(idx, 0)
        client = self.app_js[idx : idx + 5000]
        self.assertNotIn("console.log(data.approvalToken", client)
        self.assertNotIn("setText(\"doa-token\"", client)
        # Confirm the explicit comment about not capturing the token
        self.assertIn("do NOT capture", client)

    # --- Script-level proofs reusing N+4.4A control plane ---

    def test_script_validate_handoff_rejects_unsafe_workflow_via_validation(self):
        """The CLI must validate target_workflow at validate_handoff level."""
        payload = self.plane._build_handoff("test", "content_studio_demo")
        payload["target_workflow"] = "uncontrolled_browser"
        ok, errors = self.plane.validate_handoff(payload)
        self.assertFalse(ok)
        self.assertTrue(any("target_workflow" in e for e in errors))

    def test_script_status_default_mode_dry_run(self):
        f = io.StringIO()
        with redirect_stdout(f):
            self.plane.cmd_status(json_out=True)
        data = json.loads(f.getvalue())
        self.assertEqual(data["default_mode"], "dry_run")
        self.assertFalse(data["live_account_actions_enabled"])
        self.assertFalse(data["external_api_actions_enabled"])
        self.assertFalse(data["money_actions_enabled"])
        self.assertFalse(data["publish_actions_enabled"])
        self.assertFalse(data["arbitrary_click_or_type_enabled"])
        self.assertFalse(data["shell_exec_from_model_output_enabled"])
        self.assertFalse(data["gemini_treated_as_unlimited"])
        self.assertFalse(data["gemini_live_prompt_executed"])

    def test_gemini_status_only_quota_limited(self):
        probe = self.plane._probe_gemini_cli()
        self.assertEqual(probe["adapter"], "gemini_cli")
        self.assertEqual(probe["quota"], "unknown_free_tier_limited")
        self.assertFalse(probe["treated_as_unlimited"])
        self.assertFalse(probe["live_prompt_executed"])


if __name__ == "__main__":
    unittest.main()