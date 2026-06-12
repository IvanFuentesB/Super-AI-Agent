#!/usr/bin/env python3
"""N+6.40A tests: Working MVP Runtime Recipes.

Proves the operator recipes layer actually works and stays safe:
- recipes CLI exists, lists >= 5 recipes, every recipe runs and writes a
  Markdown report with the honest six-section structure
- all-safe runs everything with zero live actions
- deny-by-default policy (Rust checker bridge + Python mirror + manifest)
- no provider keys, no agent launches, no deletes, no moves, no writes
  outside the repo-safe generated folder by default
- dashboard Working Recipes section, endpoints, artifacts reference
- UI fixes: vertical titles, badge overflow, calm idle overlay, collapsed debug
- previous milestone suites still pass; public audit has no blockers
- PowerShell checker is ASCII-safe and structurally safe
"""
import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
RECIPES_SCRIPT = REPO_ROOT / "03_scripts" / "operator_recipes" / "ghoti_operator_recipes.py"
RECIPES_PS1 = REPO_ROOT / "03_scripts" / "operator_recipes" / "check_operator_recipes.ps1"
POLICY_MANIFEST = REPO_ROOT / "23_configs" / "operator_recipe_policy.example.json"
RUST_MAIN = REPO_ROOT / "rust" / "ghoti_policy_checker" / "src" / "main.rs"
SERVER_JS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js"
INDEX_HTML = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html"
APP_JS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "app.js"
STYLES_CSS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "styles.css"
TESTS_DIR = REPO_ROOT / "01_projects" / "runtime_mvp" / "tests"
PYTHON = sys.executable

# Repo-local, gitignored output dir so test runs never pollute tracked paths.
TEST_OUTPUT_DIR = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "runtime_data"
                   / "recipe_test_output")

RECIPE_IDS = ["project-health", "handoff-pack", "cleanup-preview",
              "local-model-check", "fixture-replay-demo"]

_ALL_SAFE_RESULT: dict = {}


def _run_cli(args, timeout=420):
    proc = subprocess.run(
        [PYTHON, str(RECIPES_SCRIPT)] + args,
        capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=timeout,
    )
    return proc


def setUpModule():
    """Run all-safe once into a repo-local gitignored dir; share the results."""
    global _ALL_SAFE_RESULT
    proc = _run_cli(["--run", "all-safe", "--json",
                     "--output-dir", str(TEST_OUTPUT_DIR)])
    _ALL_SAFE_RESULT = json.loads(proc.stdout)


def _result_for(recipe_id: str) -> dict:
    for result in _ALL_SAFE_RESULT.get("results", []):
        if result.get("recipe_id") == recipe_id:
            return result
    raise AssertionError("no all-safe result for %s" % recipe_id)


# ===========================================================================
# 1-2. CLI existence and listing
# ===========================================================================

class TestRecipesCliBasics(unittest.TestCase):
    def test_01_recipes_script_exists(self):
        self.assertTrue(RECIPES_SCRIPT.is_file())

    def test_02_list_returns_at_least_5_recipes(self):
        proc = _run_cli(["--list", "--json"], timeout=60)
        data = json.loads(proc.stdout)
        self.assertTrue(data.get("ok"))
        self.assertGreaterEqual(len(data.get("recipes", [])), 5)
        listed = {r["id"] for r in data["recipes"]}
        for rid in RECIPE_IDS:
            self.assertIn(rid, listed)


# ===========================================================================
# 3-8, 14-18. Every recipe runs, writes honest Markdown, with safe flags
# ===========================================================================

class TestRecipeRuns(unittest.TestCase):
    def _assert_recipe_report(self, recipe_id):
        result = _result_for(recipe_id)
        self.assertTrue(result.get("ok"), "%s did not run ok" % recipe_id)
        report_path = result.get("report_path")
        self.assertTrue(report_path, "%s wrote no report" % recipe_id)
        report = Path(report_path)
        if not report.is_absolute():
            report = REPO_ROOT / report_path
        self.assertTrue(report.is_file(), "report missing on disk: %s" % report)
        self.assertEqual(report.suffix, ".md")
        body = report.read_text(encoding="utf-8")
        self.assertIn("What happened", body)
        self.assertIn("Next action", body)
        self.assertIn("What Ghoti refused to do", body)
        self.assertIn("What remains disabled", body)
        return result

    def test_03_project_health_writes_markdown_report(self):
        self._assert_recipe_report("project-health")

    def test_04_handoff_pack_writes_markdown_report(self):
        self._assert_recipe_report("handoff-pack")

    def test_05_cleanup_preview_is_preview_only(self):
        result = self._assert_recipe_report("cleanup-preview")
        details = result.get("details", {})
        self.assertTrue(details.get("preview_only"))
        self.assertEqual(details.get("files_deleted"), 0)
        self.assertEqual(details.get("files_moved"), 0)

    def test_06_local_model_check_runs_even_without_ollama(self):
        # The environment may or may not have Ollama; the recipe must be ok
        # either way and must report the truth.
        result = self._assert_recipe_report("local-model-check")
        details = result.get("details", {})
        self.assertIn("ollama_command_found", details)
        self.assertIs(details.get("auto_pull"), False)

    def test_07_fixture_replay_demo_runs_or_reports_gracefully(self):
        result = _result_for("fixture-replay-demo")
        self.assertTrue(result.get("ok"))
        details = result.get("details", {})
        if details.get("available"):
            self.assertEqual(details.get("task_count"), 5)
            self.assertEqual(details.get("parallel_group_count"), 3)
            self.assertEqual(details.get("overlap_count"), 0)
        else:
            self.assertIn("fixture replay wrapper unavailable",
                          " ".join(result.get("warnings", [])))

    def test_08_all_safe_runs_without_live_actions(self):
        self.assertTrue(_ALL_SAFE_RESULT.get("ok"))
        self.assertEqual(len(_ALL_SAFE_RESULT.get("results", [])), 5)
        flags = _ALL_SAFE_RESULT.get("safety_flags", {})
        self.assertIs(flags.get("no_live_actions"), True)

    def test_14_reports_contain_what_happened(self):
        for rid in RECIPE_IDS:
            result = _result_for(rid)
            report = Path(result["report_path"])
            if not report.is_absolute():
                report = REPO_ROOT / result["report_path"]
            self.assertIn("What happened", report.read_text(encoding="utf-8"))

    def test_15_reports_contain_next_action(self):
        for rid in RECIPE_IDS:
            result = _result_for(rid)
            report = Path(result["report_path"])
            if not report.is_absolute():
                report = REPO_ROOT / result["report_path"]
            self.assertIn("Next action", report.read_text(encoding="utf-8"))

    def test_16_17_18_safety_flags_honest(self):
        for rid in RECIPE_IDS:
            flags = _result_for(rid).get("safety_flags", {})
            self.assertIs(flags.get("no_live_actions"), True, rid)
            self.assertIs(flags.get("provider_api_used"), False, rid)
            self.assertIs(flags.get("agents_launched"), False, rid)
            self.assertIs(flags.get("files_deleted"), False, rid)
            self.assertIs(flags.get("files_moved"), False, rid)


# ===========================================================================
# 9-13. Source-level safety: no keys, no agents, no deletes/moves, repo-only
# ===========================================================================

class TestRecipeSourceSafety(unittest.TestCase):
    def setUp(self):
        self.src = RECIPES_SCRIPT.read_text(encoding="utf-8")

    def test_09_no_provider_api_key_usage(self):
        # Needles assembled from fragments so this test never self-triggers.
        for needle in ["sk-" + "ant-", "ANTHROPIC" + "_API_KEY", "OPENAI" + "_API_KEY",
                       "api." + "anthropic.com", "api." + "openai.com"]:
            self.assertNotIn(needle, self.src, "provider reference: %s" % needle)

    def test_10_no_agent_launch_primitives(self):
        for needle in ["claude" + "-swarm run", "agent" + ".launch", "spawn" + "_agent"]:
            self.assertNotIn(needle, self.src)
        # subprocess is used only with fixed argv and shell=False semantics.
        self.assertNotIn("shell=" + "True", self.src)

    def test_11_no_delete_primitives(self):
        for needle in ["os." + "remove", "os." + "unlink", "shutil." + "rmtree",
                       ".unlink" + "(", "send2" + "trash"]:
            self.assertNotIn(needle, self.src, "delete primitive: %s" % needle)

    def test_12_no_move_primitives(self):
        for needle in ["shutil." + "move", "os." + "rename", "os." + "replace",
                       ".rename" + "("]:
            self.assertNotIn(needle, self.src, "move primitive: %s" % needle)

    def test_13_no_writes_outside_repo_by_default(self):
        # Default run wrote into the repo-local dir.
        for rid in RECIPE_IDS:
            report_path = _result_for(rid)["report_path"]
            resolved = Path(report_path)
            if not resolved.is_absolute():
                resolved = REPO_ROOT / report_path
            resolved.resolve().relative_to(REPO_ROOT)  # raises if outside
        # An explicit outside-repo output dir is preview-only: nothing written.
        outside = Path("/tmp/ghoti_n640a_outside_check" if sys.platform != "win32"
                       else "C:/Temp/ghoti_n640a_outside_check")
        proc = _run_cli(["--run", "local-model-check", "--json",
                         "--output-dir", str(outside)], timeout=120)
        data = json.loads(proc.stdout)
        self.assertEqual(data.get("mode"), "preview_only")
        self.assertIsNone(data.get("report_path"))
        self.assertFalse(outside.exists(), "outside-repo dir must never be created")

    def test_localhost_only_network(self):
        self.assertIn("127.0.0.1", self.src)
        urls = re.findall(r"https?://[\w\.\-:]+", self.src)
        for url in urls:
            self.assertTrue(
                url.startswith("http://127.0.0.1") or url.startswith("http://localhost")
                or url.startswith("https://ollama.com"),  # docs-only install hint text
                "non-localhost URL in recipes: %s" % url)


# ===========================================================================
# 19. Policy: manifest exists; Rust integration explicit; deny-by-default mirror
# ===========================================================================

class TestPolicyIntegration(unittest.TestCase):
    def test_19_policy_manifest_exists_and_is_deny_by_default(self):
        self.assertTrue(POLICY_MANIFEST.is_file())
        manifest = json.loads(POLICY_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest.get("default_decision"), "deny")
        self.assertIn("report_write_repo_local", manifest.get("allowed_capabilities", []))
        for blocked in ["account", "mcp", "provider_api", "agent_launch",
                        "file_delete", "file_move", "telegram"]:
            self.assertIn(blocked, manifest.get("blocked_capabilities", []))

    def test_rust_checker_capabilities_match_manifest(self):
        rust_src = RUST_MAIN.read_text(encoding="utf-8")
        for cap in ["report_write_repo_local", "local_model_status_read",
                    "repo_read", "status_read", "fixture_read"]:
            self.assertIn('"%s"' % cap, rust_src,
                          "Rust checker missing capability: %s" % cap)

    def test_recipe_runs_declare_policy_status_explicitly(self):
        result = _result_for("project-health")
        policy = result.get("policy", {})
        for field in ["requested_capabilities", "allowed_capabilities",
                      "denied_capabilities", "rust_checker_available",
                      "rust_checker_used", "policy_check_passed"]:
            self.assertIn(field, policy, "policy field missing: %s" % field)
        self.assertTrue(policy["policy_check_passed"])
        self.assertEqual(policy["denied_capabilities"], [])

    def test_python_mirror_denies_unknown_and_blocked(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("ghoti_recipes_n640a",
                                                      str(RECIPES_SCRIPT))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        denied = module._python_policy_check("test", ["external_write"])
        self.assertEqual(denied["decision"], "deny")
        blocked = module._python_policy_check("test", ["mcp"])
        self.assertEqual(blocked["decision"], "deny")
        self.assertIn("mcp", blocked["blocked_capabilities"])
        allowed = module._python_policy_check(
            "test", ["repo_read", "report_write_repo_local"])
        self.assertEqual(allowed["decision"], "allow")


# ===========================================================================
# 20-23. Dashboard: Working Recipes section, endpoints, artifacts reference
# ===========================================================================

class TestDashboardRecipes(unittest.TestCase):
    def setUp(self):
        self.html = INDEX_HTML.read_text(encoding="utf-8")
        self.server = SERVER_JS.read_text(encoding="utf-8")
        self.app = APP_JS.read_text(encoding="utf-8")

    def test_20_dashboard_contains_working_recipes(self):
        self.assertIn("Working Recipes", self.html)
        self.assertIn("Start here: run a useful local recipe.", self.html)

    def test_21_dashboard_has_cards_for_all_recipes(self):
        for rid in RECIPE_IDS + ["all-safe"]:
            self.assertIn('data-recipe-run="%s"' % rid, self.html,
                          "missing recipe button: %s" % rid)
            self.assertIn('data-recipe-result="%s"' % rid, self.html,
                          "missing recipe result slot: %s" % rid)

    def test_21b_cards_state_what_why_wont(self):
        recipes_block = self.html.split("Working Recipes", 1)[-1].split("cap-hero", 1)[0]
        self.assertGreaterEqual(recipes_block.count("What it does:"), 6)
        self.assertGreaterEqual(recipes_block.count("Why it matters:"), 6)
        self.assertGreaterEqual(recipes_block.count("It will not:"), 6)

    def test_22_operator_recipe_endpoints_registered(self):
        for route in ["/api/product-control/operator-recipes",
                      "/api/product-control/run-operator-recipe",
                      "/api/product-control/latest-operator-recipe-runs"]:
            self.assertIn(route, self.server, "missing endpoint: %s" % route)
            self.assertIn(route, self.app, "frontend missing call to: %s" % route)

    def test_22b_run_endpoint_is_allowlisted(self):
        self.assertIn("OPERATOR_RECIPE_IDS", self.server)
        self.assertIn("non-allowlisted recipe id", self.server)

    def test_23_artifacts_page_references_operator_reports(self):
        self.assertIn("artifacts-operator-reports", self.html)
        self.assertIn("14_context/operator_reports/generated/", self.html)


# ===========================================================================
# 24-27. UI fixes
# ===========================================================================

class TestUiFixes(unittest.TestCase):
    def setUp(self):
        self.css = STYLES_CSS.read_text(encoding="utf-8")
        self.app = APP_JS.read_text(encoding="utf-8")
        self.html = INDEX_HTML.read_text(encoding="utf-8")

    def test_24_vertical_title_wrapping_fixed(self):
        self.assertIn("No vertical title text", self.css)
        self.assertIn("word-break: keep-all", self.css)

    def test_25_badge_overflow_fixed(self):
        self.assertIn("overflow-x: hidden", self.css)
        n39b_and_later = self.css.split("N+6.39B", 1)[-1]
        self.assertIn("word-break", n39b_and_later)

    def test_26_overlay_idle_not_degraded_by_default(self):
        self.assertIn("Idle is normal, not degraded", self.app)
        self.assertIn("default: collapsed on first visit", self.app)

    def test_27_raw_debug_collapsed_by_default(self):
        # Debug blocks are <details> without an open attribute.
        for needle in ["<summary>Debug details</summary>"]:
            self.assertIn(needle, self.html)
        self.assertNotIn("<details class=\"cap-debug\" open", self.html)


# ===========================================================================
# 28-33. Nothing unsafe added anywhere in this milestone's files
# ===========================================================================

class TestNoUnsafeAdditions(unittest.TestCase):
    def setUp(self):
        self.blob = "\n".join([
            RECIPES_SCRIPT.read_text(encoding="utf-8"),
            RECIPES_PS1.read_text(encoding="utf-8"),
            POLICY_MANIFEST.read_text(encoding="utf-8"),
        ])

    def test_28_no_mcp(self):
        self.assertNotIn("mcp." + "connect", self.blob)
        self.assertNotIn("Model Context Protocol server", self.blob)

    def test_29_no_telegram_commands(self):
        low = self.blob.lower()
        for needle in ["telegram" + ".send", "telegram" + "bot", "bot" + ".sendmessage",
                       "api.telegram" + ".org"]:
            self.assertNotIn(needle, low)

    def test_30_no_obsidian_bridge(self):
        low = self.blob.lower()
        for needle in ["obsidian" + "://", ".obsidian" + "/", "obsidian" + "_vault"]:
            self.assertNotIn(needle, low)

    def test_31_no_account_actions(self):
        low = self.blob.lower()
        for needle in ["login(", "oauth", "set-cookie", "authorization: bearer"]:
            self.assertNotIn(needle, low)

    def test_32_no_secrets(self):
        for needle in ["sk-" + "ant-", "ghp" + "_", "AKIA" + "IOSFODNN",
                       "BEGIN RSA " + "PRIVATE KEY"]:
            # The PS1 scans reports for these patterns, so check only the
            # python/manifest sources here.
            src = RECIPES_SCRIPT.read_text(encoding="utf-8") + \
                  POLICY_MANIFEST.read_text(encoding="utf-8")
            self.assertNotIn(needle, src)

    def test_33_no_ai_attribution(self):
        low = self.blob.lower()
        for phrase in ["co-authored-by: claude", "generated with claude",
                       "generated by claude", "written by claude",
                       "claude-sonnet", "claude-opus", "claude-fable"]:
            self.assertNotIn(phrase, low, "AI attribution: %r" % phrase)


# ===========================================================================
# 34-36. Previous suites still pass; public audit clean
# ===========================================================================

class TestRegression(unittest.TestCase):
    def _run_suite(self, pattern):
        proc = subprocess.run(
            [PYTHON, "-m", "unittest", "discover",
             "-s", str(TESTS_DIR), "-p", pattern],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=600,
        )
        return proc

    def test_34_n6_39b_tests_still_pass(self):
        if not list(TESTS_DIR.glob("test_n6_39b_*.py")):
            self.skipTest("n6_39b tests not present")
        proc = self._run_suite("test_n6_39b_*.py")
        self.assertEqual(proc.returncode, 0, proc.stderr[-2000:])

    def test_35_n6_39a_tests_still_pass(self):
        if not list(TESTS_DIR.glob("test_n6_39a_*.py")):
            self.skipTest("n6_39a tests not present")
        proc = self._run_suite("test_n6_39a_*.py")
        self.assertEqual(proc.returncode, 0, proc.stderr[-2000:])

    def test_36_public_audit_no_blockers(self):
        audit = REPO_ROOT / "03_scripts" / "public_repo_security_audit.py"
        proc = subprocess.run(
            [PYTHON, str(audit), "--run", "--json"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=300,
        )
        data = json.loads(proc.stdout)
        self.assertEqual(data.get("blocking_findings", []), [])


# ===========================================================================
# 37-38. PowerShell checker
# ===========================================================================

class TestPowerShellChecker(unittest.TestCase):
    def setUp(self):
        self.raw = RECIPES_PS1.read_bytes()
        self.text = RECIPES_PS1.read_text(encoding="ascii")  # raises if non-ASCII

    def test_37_ps1_is_ascii_safe(self):
        bad = [i for i, b in enumerate(self.raw) if b > 127]
        self.assertEqual(bad, [], "PS1 checker must stay ASCII-safe")

    def test_37b_ps1_is_structurally_safe(self):
        self.assertIn("Set-StrictMode -Version Latest", self.text)
        for forbidden in ["Invoke-" + "Expression", "Start-" + "Process",
                          "iex " , "DownloadString"]:
            self.assertNotIn(forbidden, self.text,
                             "forbidden PS primitive: %s" % forbidden)
        # Pipeline outputs wrapped before .Count under StrictMode.
        self.assertIn("@(", self.text)

    def test_38_ps1_passes_when_powershell_available(self):
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if not shell:
            self.skipTest("PowerShell not available in this environment - "
                          "execution reported as not available, not passed")
        proc = subprocess.run(
            [shell, "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-File", str(RECIPES_PS1)],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=600,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout[-2000:])
        self.assertIn("RESULT: PASS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
