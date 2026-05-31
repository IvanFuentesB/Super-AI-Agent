"""Tests for N+6.7A - Tool/Repo Intake Static Registry.

These tests lock the safety + contract behavior of the static intake registry so
it cannot silently regress. They assert that (1) the registry JSON and its
companion files exist and the registry is valid JSON, (2) the CLI loads the
registry and emits a JSON summary, lists candidates, and shows one candidate,
exiting non-zero on a missing candidate or an invalid registry, (3) every
candidate is planning-only - status candidate_only|blocked, never installed,
never runtime_wired, (4) the required HIGH candidates are present and carry a
first_safe_test plus stop_conditions, (5) the blocked tier names the dangerous
boundaries (social posting, live browser/desktop, money, account login, unknown
binary, OSINT/Kali), (6) the script itself contains no network/install/clone/exec
tokens, and (7) the docs state "no blind installs" and that MCP/browser/
computer-use are not enabled, with no overclaim and no secret pattern present.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

TOOL_INTAKE = REPO_ROOT / "14_context" / "tool_intake"
REGISTRY = TOOL_INTAKE / "tool_candidate_registry.json"
DECISION_LOG = TOOL_INTAKE / "tool_intake_decision_log.md"
README = TOOL_INTAKE / "README_TOOL_INTAKE.md"
SCRIPT = REPO_ROOT / "03_scripts" / "tool_intake_static_registry.py"
DOC = REPO_ROOT / "docs" / "GHOTI_N6_7A_TOOL_INTAKE_STATIC_REGISTRY.md"

# Required HIGH-tier candidates (matched as case-insensitive substrings of names).
REQUIRED_HIGH = [
    "Understand-Anything",
    "MarkItDown",
    "Graphify",
    "UI-TARS",
    "Browser Harness",
    "21st.dev",
    "Graph MCP",
    "Security Checklists",
]

# The script must never reach the network, install, clone, or execute anything.
FORBIDDEN_SCRIPT_TOKENS = [
    "requests",
    "httpx",
    "urllib",
    "socket",
    "subprocess",
    "os.system",
    "git clone",
    "pip install",
    "npm install",
    "winget",
    "invoke-webrequest",
    "invoke-expression",
]

# Distinctive affirmative overclaims. Phrased so they cannot be a substring of a
# truthful *negated* sentence (e.g. "MCP ... are not enabled").
FALSE_CLAIMS = [
    "candidates are installed and wired",
    "the registry installs tools",
    "external repos are cloned and run",
    "mcp is enabled for ghoti",
    "browser-use is enabled for ghoti",
    "computer-use is enabled for ghoti",
    "telegram is enabled for ghoti",
    "ghoti is fully autonomous",
    "tools were installed for this milestone",
]

MARKDOWN_DOCS = [DOC, README, DECISION_LOG]
SECRET_SCAN_FILES = [DOC, README, DECISION_LOG, REGISTRY, SCRIPT]


def read(path):
    return path.read_text(encoding="utf-8")


def norm(text):
    """Lowercase and collapse whitespace so a phrase still matches when Markdown
    wrapped it across lines."""
    return " ".join(text.lower().split())


def load_registry():
    return json.loads(read(REGISTRY))


def run_cli(*args):
    """Run the CLI and return (returncode, stdout_text, stderr_text)."""
    cmd = [sys.executable, str(SCRIPT), *args]
    proc = subprocess.run(cmd, capture_output=True, timeout=60)
    out = proc.stdout.decode("utf-8", errors="replace").strip()
    err = proc.stderr.decode("utf-8", errors="replace")
    return proc.returncode, out, err


def run_cli_with_registry(reg_obj):
    """Write reg_obj to a temp file, run the CLI against it, return (rc, out, err)."""
    handle = tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    )
    try:
        json.dump(reg_obj, handle)
        handle.close()
        return run_cli("--registry", handle.name, "--json")
    finally:
        os.unlink(handle.name)


class ToolIntakeRegistryTests(unittest.TestCase):
    def test_intake_files_exist(self):
        for path in [REGISTRY, DECISION_LOG, README, SCRIPT, DOC]:
            self.assertTrue(path.is_file(), msg=f"missing file: {path}")

    def test_registry_is_valid_json_with_candidates(self):
        reg = load_registry()
        self.assertIsInstance(reg, dict)
        self.assertIsInstance(reg.get("candidates"), list)
        self.assertTrue(reg["candidates"], msg="candidates list is empty")

    def test_cli_summary_returns_json(self):
        rc, out, err = run_cli("--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertTrue(data["ok"])
        self.assertEqual(data["candidate_count"], len(load_registry()["candidates"]))
        self.assertFalse(data["any_installed"], msg="no candidate may be installed")
        self.assertFalse(data["any_runtime_wired"], msg="no candidate may be wired")
        self.assertIn("by_priority", data)
        self.assertIn("by_risk", data)
        self.assertIn("by_status", data)

    def test_cli_list_runs(self):
        rc, out, err = run_cli("--list")
        self.assertEqual(rc, 0, msg=err)
        self.assertIn("MarkItDown", out)
        self.assertIn("blocked", out)

    def test_cli_candidate_lookup_is_case_insensitive(self):
        rc, out, err = run_cli("--candidate", "markitdown", "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertEqual(data["name"], "MarkItDown")
        self.assertEqual(data["status"], "candidate_only")
        self.assertFalse(data["installed"])
        self.assertFalse(data["runtime_wired"])

    def test_cli_missing_candidate_is_nonzero(self):
        rc, out, err = run_cli("--candidate", "NoSuchTool", "--json")
        self.assertNotEqual(rc, 0, msg="missing candidate must exit non-zero")

    def test_cli_invalid_json_registry_is_nonzero(self):
        handle = tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        )
        try:
            handle.write("{ this is not valid json")
            handle.close()
            rc, out, err = run_cli("--registry", handle.name, "--json")
            self.assertNotEqual(rc, 0, msg="invalid JSON must exit non-zero")
        finally:
            os.unlink(handle.name)

    def test_cli_rejects_installed_candidate(self):
        reg = load_registry()
        reg["candidates"][0]["installed"] = True
        rc, out, err = run_cli_with_registry(reg)
        self.assertNotEqual(rc, 0, msg="an installed candidate must be rejected")

    def test_cli_rejects_runtime_wired_candidate(self):
        reg = load_registry()
        reg["candidates"][0]["runtime_wired"] = True
        rc, out, err = run_cli_with_registry(reg)
        self.assertNotEqual(rc, 0, msg="a runtime_wired candidate must be rejected")

    def test_required_high_candidates_present(self):
        names = [c["name"].lower() for c in load_registry()["candidates"]]
        for needle in REQUIRED_HIGH:
            self.assertTrue(
                any(needle.lower() in name for name in names),
                msg=f"missing required HIGH candidate: {needle!r}",
            )

    def test_all_candidates_are_planning_only(self):
        for cand in load_registry()["candidates"]:
            name = cand["name"]
            self.assertIn(
                cand["status"],
                {"candidate_only", "blocked"},
                msg=f"{name}: status must be candidate_only or blocked",
            )
            self.assertIs(cand["installed"], False, msg=f"{name}: must not be installed")
            self.assertIs(
                cand["runtime_wired"], False, msg=f"{name}: must not be runtime_wired"
            )

    def test_no_candidate_is_runtime_wired(self):
        self.assertFalse(
            any(c["runtime_wired"] for c in load_registry()["candidates"]),
            msg="no candidate may declare runtime_wired: true",
        )

    def test_high_candidates_have_first_safe_test_and_stop_conditions(self):
        high = [c for c in load_registry()["candidates"] if c["priority"] == "high"]
        self.assertTrue(high, msg="there must be HIGH-priority candidates")
        for cand in high:
            name = cand["name"]
            self.assertIsInstance(cand["first_safe_test"], str)
            self.assertTrue(cand["first_safe_test"].strip(), msg=f"{name}: empty first_safe_test")
            self.assertIsInstance(cand["stop_conditions"], list)
            self.assertTrue(cand["stop_conditions"], msg=f"{name}: empty stop_conditions")

    def test_blocked_tier_names_dangerous_boundaries(self):
        blocked = [c for c in load_registry()["candidates"] if c["priority"] == "blocked"]
        self.assertGreaterEqual(len(blocked), 6, msg="expected the 6 blocked boundaries")
        for cand in blocked:
            self.assertEqual(cand["status"], "blocked")
            self.assertEqual(cand["risk_level"], "blocked")
        blob = norm(json.dumps(blocked))
        for needle in [
            "social",
            "browser",
            "desktop",
            "money",
            "account",
            "login",
            "unknown binary",
            "osint",
            "kali",
        ]:
            self.assertIn(needle, blob, msg=f"blocked tier missing boundary: {needle!r}")

    def test_script_has_no_network_install_or_exec_tokens(self):
        body = read(SCRIPT).lower()
        for token in FORBIDDEN_SCRIPT_TOKENS:
            self.assertNotIn(token, body, msg=f"script contains forbidden token {token!r}")
        self.assertIsNone(re.search(r"\biex\b", body), msg="script uses the iex alias")

    def test_doc_states_safety_posture(self):
        doc = norm(read(DOC))
        for needle in [
            "no blind installs",
            "candidate_only",
            "not installed",
            "mcp",
            "browser",
            "computer-use",
            "not enabled",
        ]:
            self.assertIn(needle, doc, msg=f"doc missing: {needle!r}")

    def test_readme_states_no_blind_installs(self):
        readme = norm(read(README))
        self.assertIn("no blind installs", readme)
        self.assertIn("candidate", readme)

    def test_no_overclaims_across_docs(self):
        combined = "\n".join(norm(read(p)) for p in MARKDOWN_DOCS)
        for claim in FALSE_CLAIMS:
            self.assertNotIn(claim, combined, msg=f"overclaim found: {claim!r}")

    def test_no_secret_patterns(self):
        combined = "\n".join(read(p) for p in SECRET_SCAN_FILES)
        self.assertNotRegex(combined, r"sk-[A-Za-z0-9_-]{20,}")
        self.assertNotRegex(combined, r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY")


if __name__ == "__main__":
    unittest.main()
