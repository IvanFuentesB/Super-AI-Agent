#!/usr/bin/env python3
"""N+4.4C tests: Desktop Operator Recipe Runner + Preview Polish."""
import importlib.util
import io
import json
import os
import pathlib
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


class N44CRecipeRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plane = _import_script("desktop_operator_control_plane")
        cls.server_js = (DASHBOARD_DIR / "server.js").read_text(encoding="utf-8")
        cls.app_js = (DASHBOARD_DIR / "public" / "app.js").read_text(encoding="utf-8")
        cls.index_html = (DASHBOARD_DIR / "public" / "index.html").read_text(encoding="utf-8")

    # --- Recipe registry ---

    def test_recipes_dict_has_exactly_four_allowlisted(self):
        expected = {
            "content_studio_generate_preview",
            "memory_compress_demo",
            "dashboard_open_preview",
            "gemini_handoff_export",
        }
        self.assertEqual(set(self.plane.RECIPES.keys()), expected)

    def test_recipe_list_cli_emits_valid_json(self):
        f = io.StringIO()
        with redirect_stdout(f):
            rc = self.plane.cmd_recipe_list(json_out=True)
        self.assertEqual(rc, 0)
        data = json.loads(f.getvalue())
        self.assertTrue(data["ok"])
        self.assertEqual(data["recipe_count"], 4)
        self.assertFalse(data["live_account_actions_enabled"])
        self.assertFalse(data["external_api_actions_enabled"])
        self.assertFalse(data["money_actions_enabled"])
        self.assertFalse(data["publish_actions_enabled"])
        self.assertFalse(data["gemini_live_prompt_executed"])
        self.assertFalse(data["gemini_treated_as_unlimited"])

    def test_recipe_execute_rejects_unknown_recipe(self):
        f = io.StringIO()
        with redirect_stdout(f):
            rc = self.plane.cmd_recipe_execute("totally_made_up_recipe", json_out=True)
        self.assertEqual(rc, 1)
        data = json.loads(f.getvalue())
        self.assertFalse(data["ok"])
        self.assertIn("REJECTED", data["error"])

    def test_gemini_handoff_export_writes_md_and_does_not_call_gemini(self):
        f = io.StringIO()
        with redirect_stdout(f):
            rc = self.plane.cmd_recipe_execute("gemini_handoff_export", json_out=True)
        self.assertEqual(rc, 0)
        data = json.loads(f.getvalue())
        self.assertTrue(data["ok"])
        self.assertFalse(data["gemini_live_prompt_executed"])
        self.assertFalse(data["gemini_treated_as_unlimited"])
        self.assertTrue(data["handoff_export_only"])
        self.assertIn("Gemini CLI is quota-limited", data["quota_warning"])
        # File must exist under repo, must be .md
        export_rel = data["handoff_export_path"]
        export_abs = os.path.join(str(REPO_ROOT), export_rel.replace("/", os.sep))
        self.assertTrue(os.path.exists(export_abs))
        self.assertTrue(export_abs.endswith(".md"))
        content = open(export_abs, encoding="utf-8").read()
        self.assertIn("handoff_export_only", content)
        self.assertIn("gemini_live_prompt_executed", content)
        self.assertIn("Gemini CLI is quota-limited", content)

    def test_dashboard_open_preview_recipe_no_browser_spawn(self):
        f = io.StringIO()
        with redirect_stdout(f):
            rc = self.plane.cmd_recipe_execute("dashboard_open_preview", json_out=True)
        self.assertEqual(rc, 0)
        data = json.loads(f.getvalue())
        self.assertTrue(data["ok"])
        self.assertFalse(data["browser_launched"])
        self.assertIn("recorded_repo_local_preview_path_no_spawn", data["actions_executed"])

    # --- Dashboard HTML labels ---

    def test_dashboard_html_has_recipe_runner_section(self):
        self.assertIn("Desktop Operator Recipe Runner", self.index_html)

    def test_dashboard_html_has_recipe_select_and_buttons(self):
        for s in ["dorr-recipe-select", "dorr-create-handoff", "dorr-dry-run", "dorr-approve", "dorr-execute", "dorr-open-preview"]:
            self.assertIn(s, self.index_html)

    def test_dashboard_html_shows_all_four_recipe_options(self):
        for s in ["Run Content Studio Recipe", "Memory Compress Demo Recipe", "Gemini Handoff Export Recipe", "Dashboard Open Preview Recipe"]:
            self.assertIn(s, self.index_html)

    def test_dashboard_html_shows_gemini_disabled_and_handoff_only(self):
        self.assertIn("Gemini live prompt: <strong>disabled", self.index_html)
        self.assertIn("Gemini handoff export only", self.index_html)

    def test_dashboard_html_shows_arbitrary_click_type_disabled(self):
        self.assertIn("arbitrary click/type: <strong>disabled", self.index_html)
        self.assertIn("shell execution: <strong>disabled", self.index_html)
        self.assertIn("live account actions: <strong>disabled", self.index_html)
        self.assertIn("publish/money actions: <strong>disabled", self.index_html)

    # --- Server.js safety ---

    def test_server_has_all_six_recipe_endpoints(self):
        for endpoint in [
            "/api/desktop-operator/recipes",
            "/api/desktop-operator/latest-recipe",
            "/api/desktop-operator/create-recipe-handoff",
            "/api/desktop-operator/run-recipe-dry-run",
            "/api/desktop-operator/approve-recipe",
            "/api/desktop-operator/execute-approved-recipe",
        ]:
            self.assertIn(endpoint, self.server_js)

    def test_server_recipe_block_has_no_shell_true(self):
        block_start = self.server_js.find("N+4.4C Desktop Operator Recipe Runner")
        block_end = self.server_js.find("/api/desktop-operator/execute-approved-recipe")
        self.assertGreater(block_start, 0)
        self.assertGreater(block_end, block_start)
        block = self.server_js[block_start : block_end + 2000]
        self.assertNotIn("shell: true", block)
        self.assertNotIn("shell:true", block)

    def test_server_enforces_recipe_allowlist(self):
        self.assertIn("desktopOperatorAllowedRecipes", self.server_js)
        self.assertIn("REJECTED: recipe_id not in allowlist", self.server_js)

    def test_server_approve_recipe_never_returns_raw_token(self):
        block_idx = self.server_js.find("/api/desktop-operator/approve-recipe")
        block = self.server_js[block_idx : block_idx + 2500]
        self.assertIn("Token never returned", block)
        self.assertNotIn("approvalToken: approvalToken", block)

    # --- app.js safety ---

    def test_app_js_recipe_runner_does_not_log_token(self):
        idx = self.app_js.find("attachDesktopOperatorRecipeRunner")
        self.assertGreater(idx, 0)
        client = self.app_js[idx : idx + 5000]
        self.assertNotIn("console.log(data.approvalToken", client)
        self.assertIn("does NOT collect or store the approval token", client)

    def test_app_js_has_no_arbitrary_shell_or_click_controls(self):
        # Quick check: the new recipe runner block should not expose arbitrary
        # click/type/shell controls
        idx = self.app_js.find("attachDesktopOperatorRecipeRunner")
        self.assertGreater(idx, 0)
        client = self.app_js[idx : idx + 5000]
        for forbidden in ["arbitrary_click", "arbitrary_type", "shell_exec", "send_money", "post_to_youtube"]:
            self.assertNotIn(forbidden, client)


if __name__ == "__main__":
    unittest.main()