"""Tests for N+6.14A - Confined Local Browser Sandbox Action Runner.

These tests lock the safety + contract behaviour of the confined local browser
sandbox runner so it cannot silently regress. N+6.14A goes one step past the
N+6.13A in-memory simulation: it performs a real DOM action inside a real but
fully confined local browser (headless, throwaway profile, 127.0.0.1-only
DevTools, standard library only). The tests assert that:

1. every N+6.14A file exists (runner, check, dedicated flags, rules doc, expected
   result, top-level doc, milestone report) plus the shared sandbox target and
   example config;
2. the runner dry-run (default) emits valid JSON, launches no browser, performs
   no DOM action, uses no OS input, touches no live website or account, and asks
   for human approval;
3. the runner rejects URL targets (http/https), targets outside the sandbox
   root, missing targets, and local files that reference external/network
   resources - before launching anything;
4. the optional --allow-local-browser-sandbox mode is safe either way: it either
   performs the DOM action *only* inside the local sandbox page (note/status read
   back GHOTI_OK, no OS input) or returns a safe blocked/unavailable result; the
   test never requires a real browser to be installed;
5. the runner source uses no third-party automation packages (selenium,
   playwright, pyautogui, pynput, browser-use), never opens the default browser,
   never uses a normal user profile, never shells out with shell=True, and never
   uses os.system / os.popen / pip / npm; it does use a temporary profile, a
   headless launch, and a loopback-only DevTools channel;
6. the docs state the safety posture (local sandbox only; no live website; no
   account control; no OS-level input; temporary profile only; feature flags;
   kill switch; inspected-repo attribution; N+6.14B next step) with no overclaim
   and no secret;
7. every risky flag defaults false in both the dedicated flag file and the example
   config, with the dry-run flag true and kill switch engaged in the dedicated
   file;
8. the PowerShell check emits JSON reporting the disabled, explicit-opt-in
   posture.
"""

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

SANDBOX_DIR = REPO_ROOT / "14_context" / "computer_use" / "sandbox"
TARGET_HTML = SANDBOX_DIR / "sandbox_target.html"
FLAGS = SANDBOX_DIR / "feature_flags_confined_browser_sandbox.json"
RULES = SANDBOX_DIR / "CONFINED_BROWSER_SANDBOX_RULES.md"
EXPECTED_RESULT = SANDBOX_DIR / "confined_browser_expected_result.json"

SCRIPT_DIR = REPO_ROOT / "03_scripts" / "computer_use_sandbox"
RUNNER = SCRIPT_DIR / "confined_browser_sandbox_runner.py"
CHECK_PS = SCRIPT_DIR / "check_confined_browser_sandbox.ps1"
SCRIPT_README = SCRIPT_DIR / "README.md"

DOC = REPO_ROOT / "docs" / "GHOTI_N6_14A_CONFINED_BROWSER_SANDBOX_RUNNER.md"
REPORT = REPO_ROOT / "14_context" / "claude_n6_14a_confined_browser_sandbox_runner.md"
EXAMPLE_FLAGS = REPO_ROOT / "23_configs" / "ghoti_feature_flags.example.json"

ALL_FILES = [TARGET_HTML, FLAGS, RULES, EXPECTED_RESULT, RUNNER, CHECK_PS,
             SCRIPT_README, DOC, REPORT, EXAMPLE_FLAGS]

# Genuinely-unsafe tokens. N+6.14A legitimately uses subprocess/socket/urllib/
# struct to launch a confined headless browser and talk to a loopback DevTools
# endpoint, so those are NOT forbidden; third-party automation, default-browser
# opening, normal-profile use, shell=True, os.system/os.popen, and installs are.
SOURCE_FORBIDDEN_TOKENS = [
    "import selenium", "selenium.",
    "import playwright", "playwright.",
    "import pyautogui", "pyautogui.",
    "import pynput", "pynput.",
    "import browser_use", "browser_use.",
    "webbrowser.open",
    "shell=true",
    "os.system", "os.popen",
    "eval(", "exec(",
    "pip install", "npm install",
    "user data",  # the default Chrome profile container; we use a temp profile
]

# Positive safety markers the runner source must contain.
SOURCE_REQUIRED_TOKENS = [
    "tempfile.mkdtemp",     # throwaway profile
    "--user-data-dir",      # isolated profile dir
    "--headless",           # non-intrusive launch
    "127.0.0.1",            # loopback-only DevTools
    "shutil.rmtree",        # profile cleanup
]

# The PowerShell check reads files and runs the dry-run only.
PS_FORBIDDEN_TOKENS = [
    "invoke-expression", "iex(", "iex ", "invoke-webrequest", "invoke-restmethod",
    "downloadstring", "downloadfile", "new-object net.webclient",
]

# Distinctive affirmative overclaims, phrased so they cannot be a substring of a
# truthful negated sentence.
FALSE_CLAIMS = [
    "live browser navigation is enabled",
    "live website automation is enabled",
    "account login is enabled",
    "the desktop was controlled",
    "os-level input was used",
    "a real os click was performed",
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


def run_runner(*args, timeout=120):
    cmd = [sys.executable, str(RUNNER), *args]
    proc = subprocess.run(cmd, capture_output=True, timeout=timeout)
    out = proc.stdout.decode("utf-8", errors="replace").strip()
    err = proc.stderr.decode("utf-8", errors="replace")
    return proc.returncode, out, err


class FilesExistTests(unittest.TestCase):
    def test_all_files_exist(self):
        for path in ALL_FILES:
            self.assertTrue(path.is_file(), msg=f"missing file: {path}")


class DryRunTests(unittest.TestCase):
    def test_dry_run_emits_json_and_does_nothing(self):
        rc, out, err = run_runner("--target", str(TARGET_HTML), "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertTrue(data["ok"])
        self.assertEqual(data["milestone"], "N+6.14A")
        self.assertEqual(data["mode"], "dry_run")
        self.assertIs(data["browser_launched"], False)
        self.assertIs(data["dom_action_performed"], False)
        self.assertIs(data["os_input_used"], False)
        self.assertIs(data["live_website"], False)
        self.assertIs(data["account_context"], False)
        self.assertIs(data["target_is_local"], True)
        self.assertIs(data["target_under_sandbox_root"], True)
        self.assertIs(data["requires_human_approval"], True)
        self.assertIn("next_step", data)

    def test_dry_run_safety_block_all_safe(self):
        rc, out, err = run_runner("--target", str(TARGET_HTML), "--json")
        self.assertEqual(rc, 0, msg=err)
        safety = json.loads(out)["safety"]
        self.assertIs(safety["only_standard_library"], True)
        for flag in ("third_party_automation_packages_used", "os_level_input_used",
                     "live_website_navigated", "account_login_performed",
                     "normal_browser_profile_used", "shell_execution_used",
                     "captcha_or_bot_bypass_used"):
            self.assertIs(safety[flag], False, msg=f"safety.{flag} must be false")


class TargetRejectionTests(unittest.TestCase):
    def test_rejects_http_url(self):
        rc, out, err = run_runner("--target", "http://example.com/x.html", "--json")
        self.assertEqual(rc, 1, msg=err)
        data = json.loads(out)
        self.assertIs(data["ok"], False)
        self.assertIs(data["rejected"], True)
        self.assertIs(data["browser_launched"], False)
        self.assertIn("url", data["rejected_reason"].lower())

    def test_rejects_https_url(self):
        rc, out, err = run_runner("--target", "https://example.com/x.html", "--json")
        self.assertEqual(rc, 1, msg=err)
        data = json.loads(out)
        self.assertIs(data["ok"], False)
        self.assertIs(data["rejected"], True)
        self.assertIs(data["browser_launched"], False)

    def test_rejects_target_outside_sandbox_root(self):
        rc, out, err = run_runner("--target", str(EXAMPLE_FLAGS), "--json")
        self.assertEqual(rc, 1, msg=err)
        data = json.loads(out)
        self.assertIs(data["ok"], False)
        self.assertIs(data["rejected"], True)
        self.assertIn("outside", data["rejected_reason"].lower())

    def test_rejects_missing_target(self):
        missing = SANDBOX_DIR / "_n6_14a_does_not_exist.html"
        rc, out, err = run_runner("--target", str(missing), "--json")
        self.assertEqual(rc, 1, msg=err)
        data = json.loads(out)
        self.assertIs(data["ok"], False)
        self.assertIn("exist", data["rejected_reason"].lower())

    def test_rejects_target_with_external_resources(self):
        probe = SANDBOX_DIR / "_n6_14a_external_probe.html"
        probe.write_text(
            "<!DOCTYPE html><html><head>"
            '<script src="https://cdn.example.com/x.js"></script>'
            "</head><body>probe</body></html>",
            encoding="utf-8",
        )
        self.addCleanup(lambda: probe.unlink(missing_ok=True))
        rc, out, err = run_runner("--target", str(probe), "--json")
        self.assertEqual(rc, 1, msg=err)
        data = json.loads(out)
        self.assertIs(data["ok"], False)
        self.assertIs(data["rejected"], True)
        self.assertIs(data["browser_launched"], False)
        self.assertIn("external", data["rejected_reason"].lower())


class AllowLocalModeTests(unittest.TestCase):
    """The confined action must be safe whether or not a browser is available.

    This test never requires Chrome/Edge to be installed: if no browser or local
    DevTools endpoint is reachable, the runner returns a safe no-action result.
    """

    def test_allow_local_is_confined_or_safely_unavailable(self):
        rc, out, err = run_runner(
            "--target", str(TARGET_HTML),
            "--allow-local-browser-sandbox", "--json", timeout=180)
        data = json.loads(out)
        self.assertEqual(data["mode"], "local_browser_sandbox")
        # Invariants that hold regardless of whether a browser was available.
        self.assertIs(data["os_input_used"], False)
        self.assertIs(data["live_website"], False)
        self.assertIs(data["account_context"], False)
        self.assertIs(data["target_is_local"], True)
        self.assertIs(data["target_under_sandbox_root"], True)
        self.assertIs(data["requires_human_approval"], True)
        self.assertIs(data["safety"]["os_level_input_used"], False)
        self.assertIs(data["safety"]["live_website_navigated"], False)
        self.assertIs(data["safety"]["normal_browser_profile_used"], False)
        if data.get("dom_action_performed"):
            # Real confined action path.
            self.assertEqual(rc, 0, msg=err)
            self.assertIs(data["browser_launched"], True)
            self.assertIs(data["temporary_profile_used"], True)
            self.assertEqual(data["note_value"], "GHOTI_OK")
            self.assertEqual(data["status_output"], "GHOTI_OK")
            self.assertIs(data["goal_satisfied"], True)
        else:
            # Safe blocked/unavailable path.
            self.assertIn("blocked_or_unavailable_reason", data)
            self.assertIn("next_step", data)


class SourceSafetyTests(unittest.TestCase):
    def test_runner_source_has_no_unsafe_tokens(self):
        body = read(RUNNER).lower()
        for token in SOURCE_FORBIDDEN_TOKENS:
            self.assertNotIn(token, body,
                             msg=f"runner contains forbidden token {token!r}")

    def test_runner_source_has_confinement_markers(self):
        body = read(RUNNER)
        for token in SOURCE_REQUIRED_TOKENS:
            self.assertIn(token, body,
                          msg=f"runner missing confinement marker {token!r}")

    def test_powershell_check_has_no_unsafe_tokens(self):
        body = read(CHECK_PS).lower()
        for token in PS_FORBIDDEN_TOKENS:
            self.assertNotIn(token, body,
                             msg=f"check ps1 contains forbidden token {token!r}")


class DocsAndSafetyTests(unittest.TestCase):
    def test_docs_state_safety_posture(self):
        blob = norm("\n".join(read(p) for p in (DOC, RULES, SCRIPT_README)))
        for needle in ("local sandbox", "no live web", "not live web",
                       "temporary profile", "no os-level", "kill switch",
                       "feature flag", "n+6.14b", "loopback"):
            self.assertIn(needle, blob, msg=f"docs missing posture phrase: {needle!r}")

    def test_docs_say_no_account_control(self):
        blob = norm("\n".join(read(p) for p in (DOC, RULES)))
        self.assertIn("account", blob)
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


class FlagsTests(unittest.TestCase):
    def test_dedicated_flags_default_risky_false(self):
        flags = load_json_file(FLAGS)
        self.assertIs(flags.get("global_kill_switch_engaged"), True)
        self.assertIs(flags.get("confined_browser_sandbox_dry_run_enabled"), True)
        self.assertIs(flags.get("strict_confinement_required"), True)
        for risky in ("confined_browser_sandbox_enabled",
                      "confined_browser_cdp_enabled",
                      "confined_browser_dom_action_enabled",
                      "live_browser_navigation_enabled",
                      "os_level_input_enabled"):
            self.assertIs(flags.get(risky), False, msg=f"{risky} must default false")

    def test_example_config_has_confined_flags_disabled(self):
        flags = load_json_file(EXAMPLE_FLAGS)
        for risky in ("confined_browser_sandbox_enabled",
                      "confined_browser_sandbox_dry_run_enabled",
                      "confined_browser_cdp_enabled",
                      "confined_browser_dom_action_enabled",
                      "live_browser_navigation_enabled",
                      "os_level_input_enabled"):
            self.assertIn(risky, flags, msg=f"example config missing {risky!r}")
            self.assertIs(flags[risky], False, msg=f"{risky} must default false")

    def test_example_config_keeps_single_true_flag(self):
        flags = load_json_file(EXAMPLE_FLAGS)
        true_flags = [k for k, v in flags.items() if v is True]
        self.assertEqual(true_flags, ["telegram_status_commands_enabled"])


class PowerShellCheckTests(unittest.TestCase):
    PS = shutil.which("pwsh") or shutil.which("powershell")

    @unittest.skipUnless(PS, "PowerShell not available")
    def test_check_emits_json_disabled_posture(self):
        proc = subprocess.run(
            [self.PS, "-ExecutionPolicy", "Bypass", "-File", str(CHECK_PS)],
            capture_output=True, timeout=180)
        out = proc.stdout.decode("utf-8-sig", errors="replace").strip()
        data = json.loads(out)
        self.assertIs(data["ok"], True)
        self.assertIs(data["dry_run_works"], True)
        self.assertIs(data["local_browser_action_enabled"], False)
        self.assertIs(data["live_navigation_enabled"], False)
        self.assertIs(data["os_input_enabled"], False)
        self.assertIs(data["account_login_enabled"], False)
        self.assertIs(data["captcha_bypass_enabled"], False)
        self.assertIs(data["requires_explicit_allow_flag"], True)
        self.assertIs(data["uses_temp_profile"], True)


if __name__ == "__main__":
    unittest.main()
