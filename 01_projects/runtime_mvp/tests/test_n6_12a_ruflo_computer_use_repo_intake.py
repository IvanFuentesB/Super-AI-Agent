"""Tests for N+6.12A - Ruflo + Computer-Use Repo Static Clone/Inspect/Extract.

These tests lock the safety + contract behaviour of the external-repo static
intake so it cannot silently regress. They assert that:

1. the manifest, the static inspector, both adapter contracts, the adapters
   README, the milestone doc, the per-repo reports, and the static-clone .gitkeep
   all exist, and the manifest is valid JSON with candidates;
2. Ruflo is present and carries MIT + reuse + an attribution-based extraction;
3. the computer-use members are present (UI-TARS, Browser Harness, Vercel
   agent-browser, TryCUA/CUA, Browser-use) plus the umbrella;
4. EVERY candidate is safe_to_run: false and runtime_wired: false;
5. the inspector CLI loads the manifest and emits a JSON report whose safety
   block proves no execution / no import / no install / no network, inspects all
   candidates, filters to one candidate, and exits non-zero on a missing manifest;
6. the inspector source contains no execution/install/dynamic-import tokens (its
   network-keyword *data* and the bare word "install" are deliberately allowed -
   it is a scanner - so only call/exec/two-word-install tokens are forbidden);
7. both adapter contracts contain no live browser/desktop/network call or import,
   and their --status output reports every capability disabled with the global
   kill switch engaged and no code copied;
8. the docs state the safety posture (no live computer-use yet; static-inspected,
   not blindly run; reuse with attribution/license awareness; feature flags and
   kill switches), with no overclaim and no secret pattern;
9. no third-party clone files (including any nested .git) are committed.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

MANIFEST = (REPO_ROOT / "14_context" / "tool_intake" / "repo_intake_manifests"
            / "n6_12a_ruflo_computer_use_manifest.json")
INTAKE_SCRIPT = REPO_ROOT / "03_scripts" / "external_repo_static_intake.py"
ADAPTERS_DIR = REPO_ROOT / "03_scripts" / "external_adapters"
RUFLO_ADAPTER = ADAPTERS_DIR / "ruflo_adapter_contract.py"
CU_ADAPTER = ADAPTERS_DIR / "computer_use_adapter_contract.py"
ADAPTERS_README = ADAPTERS_DIR / "README.md"
DOC = REPO_ROOT / "docs" / "GHOTI_N6_12A_RUFLO_COMPUTER_USE_REPO_INTAKE.md"

REPORTS_DIR = REPO_ROOT / "14_context" / "tool_intake" / "repo_intake_reports"
REPORT_FILES = [
    REPORTS_DIR / "n6_12a_overview.md",
    REPORTS_DIR / "ruflo_n6_12a.md",
    REPORTS_DIR / "computer_use_stack_n6_12a.md",
    REPORTS_DIR / "ui_tars_n6_12a.md",
    REPORTS_DIR / "browser_harness_n6_12a.md",
    REPORTS_DIR / "vercel_agent_browser_n6_12a.md",
    REPORTS_DIR / "trycua_cua_driver_n6_12a.md",
]

GITIGNORE = REPO_ROOT / ".gitignore"
STATIC_CLONE_KEEP = REPO_ROOT / "21_repos" / "third_party_static" / ".gitkeep"
STATIC_CLONE_REL = "21_repos/third_party_static"

# The inspector is a security scanner, so it legitimately contains network/keyword
# *strings* (e.g. "requests.get") and the bare word "install" as detection DATA.
# We therefore forbid only execution / dependency-install / dynamic-import patterns
# that would prove it actually runs or installs third-party code.
INTAKE_FORBIDDEN_TOKENS = [
    "subprocess",
    "os.system",
    "os.popen",
    "popen(",
    "__import__",
    "importlib",
    "eval(",
    "exec(",
    "check_output",
    "check_call",
    "pip install",
    "npm install",
    "pnpm install",
    "git clone",
]

# The adapter contracts expose disabled capability FLAGS named click_enabled /
# type_enabled / network_enabled / live_browser_enabled, so we cannot forbid the
# bare words. Instead we forbid the import/call patterns that would mean a live
# browser/desktop/network is actually driven.
ADAPTER_FORBIDDEN_TOKENS = [
    "subprocess",
    "os.system",
    "os.popen",
    "popen(",
    "__import__",
    "importlib",
    "eval(",
    "exec(",
    "import requests",
    "import httpx",
    "import urllib",
    "import socket",
    "import selenium",
    "import playwright",
    "import pyautogui",
    "import pynput",
    "import webbrowser",
    "requests.get",
    "requests.post",
    "httpx.",
    "urllib.request",
    "webbrowser.open",
    "page.goto",
    ".goto(",
    "pyautogui.",
    "pynput.",
    "pip install",
    "npm install",
]

# Distinctive affirmative overclaims, phrased so they cannot be a substring of a
# truthful negated sentence (e.g. "computer-use ... stays disabled").
FALSE_CLAIMS = [
    "computer-use is enabled for ghoti",
    "ruflo is enabled for ghoti",
    "browser-use is enabled for ghoti",
    "ghoti is fully autonomous",
    "third-party code was executed",
    "dependencies were installed",
    "desktop control is enabled",
    "ruflo source is vendored",
]

ALL_TEXT_FILES = [DOC, ADAPTERS_README, RUFLO_ADAPTER, CU_ADAPTER,
                  INTAKE_SCRIPT, MANIFEST] + REPORT_FILES


def read(path):
    return path.read_text(encoding="utf-8")


def norm(text):
    """Lowercase + collapse whitespace so a phrase still matches across wraps."""
    return " ".join(text.lower().split())


def load_manifest():
    return json.loads(read(MANIFEST))


def run_py(script_path, *args, timeout=180):
    cmd = [sys.executable, str(script_path), *args]
    proc = subprocess.run(cmd, capture_output=True, timeout=timeout)
    out = proc.stdout.decode("utf-8", errors="replace").strip()
    err = proc.stderr.decode("utf-8", errors="replace")
    return proc.returncode, out, err


class FilesAndManifestTests(unittest.TestCase):
    def test_core_files_exist(self):
        for path in ([MANIFEST, INTAKE_SCRIPT, RUFLO_ADAPTER, CU_ADAPTER,
                      ADAPTERS_README, DOC, STATIC_CLONE_KEEP, GITIGNORE]
                     + REPORT_FILES):
            self.assertTrue(path.is_file(), msg=f"missing file: {path}")

    def test_manifest_is_valid_json_with_candidates(self):
        man = load_manifest()
        self.assertIsInstance(man, dict)
        self.assertTrue(man.get("static_inspection_only"))
        cands = man.get("candidates")
        self.assertIsInstance(cands, list)
        self.assertGreaterEqual(len(cands), 7, msg="expected at least 7 candidates")

    def test_ruflo_present_with_attribution(self):
        ruflo = self._candidate_named("Ruflo")
        self.assertIsNotNone(ruflo, msg="Ruflo candidate missing")
        self.assertEqual(ruflo["license_detected"], "MIT")
        self.assertIs(ruflo["license_allows_reuse"], True)
        self.assertIn("ruvnet/ruflo", ruflo["source_url"])
        self.assertIn("attribution", ruflo["extraction_status"].lower())

    def test_computer_use_members_present(self):
        haystack = norm(json.dumps([
            [c.get("name", "")] + list(c.get("aliases", []))
            for c in load_manifest()["candidates"]
        ]))
        for needle in ["ui-tars", "browser harness", "agent-browser", "cua",
                       "browser-use", "computer-use"]:
            self.assertIn(needle, haystack, msg=f"missing computer-use member: {needle!r}")

    def test_every_candidate_is_not_runtime_wired_and_not_safe_to_run(self):
        for cand in load_manifest()["candidates"]:
            name = cand.get("name", "?")
            self.assertIs(cand.get("safe_to_run"), False,
                          msg=f"{name}: safe_to_run must be false")
            self.assertIs(cand.get("runtime_wired"), False,
                          msg=f"{name}: runtime_wired must be false")

    def _candidate_named(self, name):
        for cand in load_manifest()["candidates"]:
            if cand.get("name", "").lower() == name.lower():
                return cand
        return None


class InspectorCliTests(unittest.TestCase):
    def test_cli_json_report_safety_block(self):
        rc, out, err = run_py(INTAKE_SCRIPT, "--manifest", str(MANIFEST), "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertTrue(data["static_inspection_only"])
        self.assertEqual(data["candidates_inspected"],
                         len(load_manifest()["candidates"]))
        safety = data["safety"]
        self.assertFalse(safety["executed_third_party_code"])
        self.assertFalse(safety["imported_third_party_modules"])
        self.assertFalse(safety["installed_dependencies"])
        self.assertFalse(safety["network_used"])
        self.assertTrue(safety["only_standard_library"])
        self.assertTrue(safety["read_only"])
        for rep in data["reports"]:
            self.assertFalse(rep["safe_to_run"])
            self.assertFalse(rep["runtime_wired"])

    def test_cli_candidate_filter_selects_one(self):
        rc, out, err = run_py(INTAKE_SCRIPT, "--manifest", str(MANIFEST),
                              "--candidate", "Ruflo", "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertEqual(data["candidates_inspected"], 1)
        self.assertIn("ruflo", data["reports"][0]["name"].lower())

    def test_cli_missing_manifest_is_nonzero(self):
        missing = REPO_ROOT / "14_context" / "no_such_manifest_n6_12a.json"
        rc, out, err = run_py(INTAKE_SCRIPT, "--manifest", str(missing), "--json")
        self.assertNotEqual(rc, 0, msg="missing manifest must exit non-zero")


class InspectorSourceTests(unittest.TestCase):
    def test_inspector_has_no_exec_install_or_dynamic_import_tokens(self):
        body = read(INTAKE_SCRIPT).lower()
        for token in INTAKE_FORBIDDEN_TOKENS:
            self.assertNotIn(token, body,
                             msg=f"inspector contains forbidden token {token!r}")


class AdapterContractTests(unittest.TestCase):
    def test_adapters_have_no_live_control_tokens(self):
        for adapter in (RUFLO_ADAPTER, CU_ADAPTER):
            body = read(adapter).lower()
            for token in ADAPTER_FORBIDDEN_TOKENS:
                self.assertNotIn(token, body,
                                 msg=f"{adapter.name} contains forbidden token {token!r}")

    def test_ruflo_adapter_status_is_disabled(self):
        rc, out, err = run_py(RUFLO_ADAPTER, "--status", "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertFalse(data["ruflo_swarm_enabled"])
        self.assertTrue(data["global_kill_switch_engaged"])
        self.assertFalse(data["runtime_wired"])
        self.assertFalse(data["safe_to_run"])
        self.assertFalse(data["code_copied_from_source"])
        self.assertTrue(data["re_expressed_from_scratch"])
        self.assertFalse(data["network_used"])
        self.assertFalse(data["installs_performed"])

    def test_computer_use_adapter_status_is_disabled(self):
        rc, out, err = run_py(CU_ADAPTER, "--status", "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertFalse(data["runtime_wired"])
        self.assertFalse(data["safe_to_run"])
        self.assertFalse(data["code_copied_from_source"])
        self.assertTrue(data["global_kill_switch_engaged"])
        caps = data["capabilities"]
        self.assertTrue(caps, msg="capabilities block is empty")
        for flag, value in caps.items():
            self.assertIs(value, False, msg=f"capability {flag!r} must default false")
        for refused in ("stealth", "captcha_solving", "proxy_rotation"):
            self.assertIn(refused, data["permanently_refused_capabilities"])


class DocsAndSafetyTests(unittest.TestCase):
    def test_docs_state_safety_posture(self):
        blob = norm("\n".join(read(p) for p in [DOC, ADAPTERS_README,
                                                 REPORT_FILES[0]]))
        for needle in ["no live computer-use", "static-inspected", "not blindly run",
                       "attribution", "license", "feature flag", "kill switch"]:
            self.assertIn(needle, blob, msg=f"docs missing posture phrase: {needle!r}")

    def test_no_overclaims_across_docs_and_reports(self):
        combined = "\n".join(norm(read(p)) for p in [DOC, ADAPTERS_README] + REPORT_FILES)
        for claim in FALSE_CLAIMS:
            self.assertNotIn(claim, combined, msg=f"overclaim found: {claim!r}")

    def test_no_secret_patterns(self):
        combined = "\n".join(read(p) for p in ALL_TEXT_FILES)
        self.assertNotRegex(combined, r"sk-[A-Za-z0-9_-]{20,}")
        self.assertNotRegex(combined, r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY")


class CloneHygieneTests(unittest.TestCase):
    def test_gitignore_ignores_static_clones(self):
        body = read(GITIGNORE)
        self.assertIn(f"{STATIC_CLONE_REL}/*", body,
                      msg="static-clone root is not git-ignored")
        self.assertIn(f"!{STATIC_CLONE_REL}/.gitkeep", body,
                      msg=".gitkeep is not re-included")

    def test_no_thirdparty_clone_files_committed(self):
        try:
            proc = subprocess.run(
                ["git", "ls-files", STATIC_CLONE_REL],
                cwd=str(REPO_ROOT), capture_output=True, timeout=60)
        except (OSError, subprocess.SubprocessError):
            self.skipTest("git not available")
        tracked = [line for line in proc.stdout.decode("utf-8", "replace").splitlines()
                   if line.strip()]
        for path in tracked:
            self.assertTrue(path.endswith(".gitkeep"),
                            msg=f"third-party clone file is committed: {path}")


if __name__ == "__main__":
    unittest.main()
