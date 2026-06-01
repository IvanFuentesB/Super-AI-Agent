"""Tests for N+6.13A - Sandboxed Computer-Use Action Harness.

These tests lock the safety + contract behaviour of the local sandbox computer-use
harness so it cannot silently regress. They assert that:

1. every harness file exists (sandbox target, fixture, expected plan, rules, flags,
   planner, runner, check, script README, milestone doc, final report);
2. the sandbox HTML is offline (no external scripts/styles/resources/network) and
   the fixture is local_only with live_website false and no account context;
3. the planner emits valid JSON: target sandbox_only, requires_human_approval true,
   dry_run_default true, live_website false, an all-safe safety block, and a
   blocked_actions list covering real websites, account login, captcha, stealth,
   proxy, arbitrary shell, and money/payment; its actions match the committed
   expected action plan;
4. the runner dry-run emits valid JSON with action_performed false; the optional
   --allow-sandbox-action mode performs no real action (action_performed false),
   keeps the action simulated with reason "strict confinement not yet guaranteed",
   satisfies the goal in simulation, and records a clear N+6.13B next step;
5. the planner/runner sources contain no execution / dynamic-import / live
   browser-desktop / network / install tokens, and no shell=True; the PowerShell
   check contains no Invoke-Expression / web-download tokens;
6. the docs state the safety posture (sandbox only; no live browser; no live
   computer-use; dry-run; human approval; feature flags; kill switch; attribution;
   reused statically inspected repo patterns) with no overclaim and no secret;
7. every risky feature flag defaults false (in both the sandbox flag file and the
   example config) and the dry-run flag defaults true with the kill switch engaged;
8. the PowerShell check emits JSON reporting the disabled posture.
"""

import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

SANDBOX_DIR = REPO_ROOT / "14_context" / "computer_use" / "sandbox"
TARGET_HTML = SANDBOX_DIR / "sandbox_target.html"
FIXTURE = SANDBOX_DIR / "sandbox_observation_fixture.json"
EXPECTED_PLAN = SANDBOX_DIR / "sandbox_expected_action_plan.json"
FLAGS = SANDBOX_DIR / "feature_flags_sandbox_computer_use.json"
RULES = SANDBOX_DIR / "SANDBOX_COMPUTER_USE_RULES.md"

SCRIPT_DIR = REPO_ROOT / "03_scripts" / "computer_use_sandbox"
PLANNER = SCRIPT_DIR / "sandbox_action_planner.py"
RUNNER = SCRIPT_DIR / "sandbox_action_runner.py"
CHECK_PS = SCRIPT_DIR / "check_sandbox_computer_use.ps1"
SCRIPT_README = SCRIPT_DIR / "README.md"

DOC = REPO_ROOT / "docs" / "GHOTI_N6_13A_SANDBOX_COMPUTER_USE_ACTION_HARNESS.md"
REPORT = REPO_ROOT / "14_context" / "claude_n6_13a_sandbox_computer_use_action_harness.md"
EXAMPLE_FLAGS = REPO_ROOT / "23_configs" / "ghoti_feature_flags.example.json"

ALL_FILES = [TARGET_HTML, FIXTURE, EXPECTED_PLAN, FLAGS, RULES, PLANNER, RUNNER,
             CHECK_PS, SCRIPT_README, DOC, REPORT, EXAMPLE_FLAGS]

# Patterns that would indicate an EXTERNAL resource in the sandbox HTML. Inline
# <script>/<style> are allowed (offline); only external references are forbidden.
HTML_EXTERNAL_TOKENS = [
    "http://", "https://", "src=", "<link", "//cdn", "integrity=",
    "crossorigin", "url(", "@import",
]

# The planner/runner are pure stdlib local tools. Forbid execution / dynamic-import
# / live-control / network / install patterns (call/import forms, not bare words -
# the blocked_actions labels deliberately contain descriptive words as data).
SOURCE_FORBIDDEN_TOKENS = [
    "subprocess", "os.system", "os.popen", "popen(", "__import__", "importlib",
    "eval(", "exec(", "check_output", "check_call",
    "import requests", "import httpx", "import urllib", "import socket",
    "import selenium", "import playwright", "import pyautogui", "import pynput",
    "import webbrowser", "import browser_use",
    "requests.get", "requests.post", "httpx.", "urllib.request",
    "webbrowser.open", "page.goto", ".goto(", "pyautogui.", "pynput.",
    "selenium.", "playwright.", "browser_use.",
    "pip install", "npm install", "shell=true",
]

# The PowerShell check reads files only - no shelling out, no web download.
PS_FORBIDDEN_TOKENS = [
    "invoke-expression", "iex(", "iex ", "invoke-webrequest", "invoke-restmethod",
    "downloadstring", "downloadfile", "start-process", "new-object net.webclient",
]

# Distinctive affirmative overclaims, phrased so they cannot be a substring of a
# truthful negated sentence (e.g. "real click stays disabled").
FALSE_CLAIMS = [
    "sandbox computer-use is enabled for ghoti",
    "real click is enabled",
    "real typing is enabled",
    "live browser control is enabled",
    "the desktop was controlled",
    "a real os action was performed",
    "captcha solving is enabled",
    "ghoti is fully autonomous",
]

TEXT_FILES = [DOC, RULES, SCRIPT_README, REPORT]


def read(path):
    return path.read_text(encoding="utf-8")


def norm(text):
    """Lowercase + collapse whitespace so a phrase still matches across wraps."""
    return " ".join(text.lower().split())


def load_json_file(path):
    return json.loads(read(path))


def run_py(script_path, *args, timeout=120):
    cmd = [sys.executable, str(script_path), *args]
    proc = subprocess.run(cmd, capture_output=True, timeout=timeout)
    out = proc.stdout.decode("utf-8", errors="replace").strip()
    err = proc.stderr.decode("utf-8", errors="replace")
    return proc.returncode, out, err


class FilesExistTests(unittest.TestCase):
    def test_all_harness_files_exist(self):
        for path in ALL_FILES:
            self.assertTrue(path.is_file(), msg=f"missing file: {path}")


class SandboxFixtureTests(unittest.TestCase):
    def test_sandbox_html_has_no_external_resources(self):
        body = read(TARGET_HTML).lower()
        for token in HTML_EXTERNAL_TOKENS:
            self.assertNotIn(token, body,
                             msg=f"sandbox HTML references external resource {token!r}")
        for needed in ('id="status-button"', 'id="note-input"', 'id="status-output"',
                       "ghoti sandbox target"):
            self.assertIn(needed, body, msg=f"sandbox HTML missing {needed!r}")

    def test_fixture_is_local_only(self):
        fixture = load_json_file(FIXTURE)
        self.assertIs(fixture.get("local_only"), True)
        self.assertIs(fixture.get("live_website"), False)
        self.assertIs(fixture.get("account_context"), False)
        ids = {el.get("id") for el in fixture.get("elements", [])}
        self.assertEqual(ids, {"note-input", "status-button", "status-output"})

    def test_sandbox_flags_default_risky_false(self):
        flags = load_json_file(FLAGS)
        self.assertIs(flags.get("global_kill_switch_engaged"), True)
        self.assertIs(flags.get("sandbox_computer_use_dry_run_enabled"), True)
        self.assertIs(flags.get("strict_sandbox_confinement_guaranteed"), False)
        for risky in ("sandbox_computer_use_enabled",
                      "sandbox_computer_use_real_click_enabled",
                      "sandbox_computer_use_real_type_enabled",
                      "live_browser_computer_use_enabled",
                      "captcha_bypass_enabled",
                      "account_login_automation_enabled"):
            self.assertIs(flags.get(risky), False, msg=f"{risky} must default false")


class PlannerCliTests(unittest.TestCase):
    def test_planner_emits_valid_json_plan(self):
        rc, out, err = run_py(PLANNER, "--fixture", str(FIXTURE), "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertTrue(data["ok"])
        self.assertEqual(data["target"], "sandbox_only")
        self.assertIs(data["requires_human_approval"], True)
        self.assertIs(data["dry_run_default"], True)
        self.assertIs(data["live_website"], False)
        self.assertIs(data["local_only"], True)
        safety = data["safety"]
        for flag in ("external_repo_code_executed", "installs_performed",
                     "network_used", "live_website", "desktop_control_enabled",
                     "real_click_enabled", "real_type_enabled"):
            self.assertIs(safety[flag], False, msg=f"safety.{flag} must be false")
        self.assertIs(safety["only_standard_library"], True)

    def test_planner_blocked_actions_cover_required_categories(self):
        rc, out, err = run_py(PLANNER, "--fixture", str(FIXTURE), "--json")
        self.assertEqual(rc, 0, msg=err)
        blocked = " ".join(json.loads(out)["blocked_actions"]).lower()
        for needle in ("real_website", "account_login", "captcha", "stealth",
                       "proxy", "arbitrary_shell", "money", "payment"):
            self.assertIn(needle, blocked, msg=f"blocked_actions missing {needle!r}")

    def test_planner_actions_match_committed_expected_plan(self):
        rc, out, err = run_py(PLANNER, "--fixture", str(FIXTURE), "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        expected = load_json_file(EXPECTED_PLAN)
        self.assertEqual(data["actions"], expected["actions"])
        self.assertEqual(data["expected_outcome"], expected["expected_outcome"])
        self.assertEqual([a["action"] for a in data["actions"]],
                         ["type_text", "click"])


class RunnerCliTests(unittest.TestCase):
    def test_runner_dry_run_performs_nothing(self):
        rc, out, err = run_py(RUNNER, "--fixture", str(FIXTURE), "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertTrue(data["ok"])
        self.assertEqual(data["mode"], "dry_run")
        self.assertIs(data["dry_run"], True)
        self.assertIs(data["action_performed"], False)
        self.assertIs(data["simulated_action_performed"], False)
        self.assertIs(data["requires_human_approval"], True)
        self.assertIs(data["real_click_performed"], False)
        self.assertIs(data["real_type_performed"], False)
        self.assertIs(data["os_input_used"], False)

    def test_runner_allow_sandbox_action_is_simulated_only(self):
        rc, out, err = run_py(RUNNER, "--fixture", str(FIXTURE),
                              "--allow-sandbox-action", "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertEqual(data["mode"], "allow_sandbox_action")
        self.assertIs(data["action_performed"], False)
        self.assertIs(data["real_click_performed"], False)
        self.assertIs(data["real_type_performed"], False)
        self.assertIs(data["os_input_used"], False)
        self.assertIs(data["simulated_action_performed"], True)
        self.assertEqual(data["sandbox_action_not_performed_reason"],
                         "strict confinement not yet guaranteed")
        sim = data["simulation"]
        self.assertIs(sim["goal_satisfied_in_simulation"], True)
        self.assertEqual(sim["final_state"]["status-output"]["text"], "GHOTI_OK")
        self.assertIn("N+6.13B", data["next_step_n6_13b"])


class SourceSafetyTests(unittest.TestCase):
    def test_python_sources_have_no_unsafe_tokens(self):
        for script in (PLANNER, RUNNER):
            body = read(script).lower()
            for token in SOURCE_FORBIDDEN_TOKENS:
                self.assertNotIn(token, body,
                                 msg=f"{script.name} contains forbidden token {token!r}")

    def test_powershell_check_has_no_unsafe_tokens(self):
        body = read(CHECK_PS).lower()
        for token in PS_FORBIDDEN_TOKENS:
            self.assertNotIn(token, body,
                             msg=f"check ps1 contains forbidden token {token!r}")

    def test_no_network_calls_in_html_or_python(self):
        for path in (TARGET_HTML, PLANNER, RUNNER):
            body = read(path).lower()
            for token in ("http://", "https://", "requests.get", "urllib.request",
                          "socket.socket"):
                self.assertNotIn(token, body,
                                 msg=f"{path.name} contains network token {token!r}")


class DocsAndSafetyTests(unittest.TestCase):
    def test_docs_state_safety_posture(self):
        blob = norm("\n".join(read(p) for p in (DOC, RULES, SCRIPT_README)))
        for needle in ("sandbox only", "no live browser", "no live computer-use",
                       "dry-run", "human approval", "feature flag", "kill switch",
                       "attribution", "static", "no third-party code", "n+6.13b"):
            self.assertIn(needle, blob, msg=f"docs missing posture phrase: {needle!r}")

    def test_docs_mention_inspected_repo_patterns(self):
        blob = norm("\n".join(read(p) for p in (DOC, RULES, SCRIPT_README)))
        for repo in ("trycua", "browser harness", "agent-browser", "ruflo"):
            self.assertIn(repo, blob, msg=f"docs missing inspected repo: {repo!r}")

    def test_no_overclaims(self):
        combined = "\n".join(norm(read(p)) for p in TEXT_FILES)
        for claim in FALSE_CLAIMS:
            self.assertNotIn(claim, combined, msg=f"overclaim found: {claim!r}")

    def test_no_secret_patterns(self):
        combined = "\n".join(read(p) for p in ALL_FILES)
        self.assertNotRegex(combined, r"sk-[A-Za-z0-9_-]{20,}")
        self.assertNotRegex(combined, r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY")


class ExampleFlagsTests(unittest.TestCase):
    def test_example_config_has_sandbox_flags_disabled(self):
        flags = load_json_file(EXAMPLE_FLAGS)
        for risky in ("sandbox_computer_use_enabled",
                      "sandbox_computer_use_dry_run_enabled",
                      "sandbox_computer_use_real_click_enabled",
                      "sandbox_computer_use_real_type_enabled",
                      "live_browser_computer_use_enabled",
                      "captcha_bypass_enabled",
                      "account_login_automation_enabled"):
            self.assertIn(risky, flags, msg=f"example config missing {risky!r}")
            self.assertIs(flags[risky], False, msg=f"{risky} must default false")


class PowerShellCheckTests(unittest.TestCase):
    PS = shutil.which("pwsh") or shutil.which("powershell")

    @unittest.skipUnless(PS, "PowerShell not available")
    def test_check_emits_json_disabled_posture(self):
        proc = subprocess.run(
            [self.PS, "-ExecutionPolicy", "Bypass", "-File", str(CHECK_PS)],
            capture_output=True, timeout=120)
        out = proc.stdout.decode("utf-8-sig", errors="replace").strip()
        data = json.loads(out)
        self.assertIs(data["ok"], True)
        self.assertIs(data["dry_run_enabled"], True)
        self.assertIs(data["live_browser_enabled"], False)
        self.assertIs(data["account_login_enabled"], False)
        self.assertIs(data["captcha_bypass_enabled"], False)
        self.assertIs(data["real_click_enabled"], False)
        self.assertIs(data["real_type_enabled"], False)
        self.assertIs(data["global_kill_switch"], True)


if __name__ == "__main__":
    unittest.main()
