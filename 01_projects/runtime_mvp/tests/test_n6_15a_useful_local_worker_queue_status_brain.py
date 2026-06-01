"""Tests for N+6.15A - Useful Local Worker Queue + Ghoti Status Brain.

These tests lock the safety + contract behaviour of the first genuinely useful
day-to-day local workflow so it cannot silently regress. They assert that:

1. every N+6.15A file exists (schema, three queue examples, both READMEs, the two
   scripts, the PowerShell check, the doc, the seed handoff) plus the example
   feature-flags config;
2. the queue example JSON files and the status schema are valid JSON with the
   expected task types;
3. the status brain --json emits every required packet field, with ok true and the
   six safety flags false;
4. --write-handoff writes the expected markdown handoff note (and the test cleans
   it up so it leaves no residue);
5. the optional --use-gemma-if-available path never fails whether or not a local
   Ollama/Gemma model is installed (exactly one of gemma_used/fallback is true);
6. --include-computer-use-sandbox runs the confined sandbox dry-run only: no
   browser launch, no DOM action, no OS input, no live website;
7. the queue runs the three supported task types and blocks every blocked task
   type and any unrecognized type by default-deny;
8. the script sources never use a shell string, os.system/os.popen, eval/exec, a
   network/external-API import, webbrowser, or an --allow flag, and the PowerShell
   check uses no Invoke-Expression / web download; no secrets anywhere;
9. the six N+6.15A feature flags default false in the example config, which keeps a
   single enabled flag (telegram_status_commands_enabled);
10. the docs explain the safety posture (no live autonomy, no external API, no
    account; Gemma optional + local; Hermes can read the handoff later; Telegram
    can expose the status later) with no overclaim;
11. the PowerShell check emits JSON reporting the disabled, local-only posture.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

LWQ_DIR = REPO_ROOT / "14_context" / "local_worker_queue"
SCHEMA = LWQ_DIR / "status_schema_n6_15a.json"
EXAMPLES_DIR = LWQ_DIR / "queue_examples"
STATUS_TASK = EXAMPLES_DIR / "status_summary_task.json"
CUS_TASK = EXAMPLES_DIR / "computer_use_sandbox_status_task.json"
INTAKE_TASK = EXAMPLES_DIR / "repo_intake_summary_task.json"
LWQ_README = LWQ_DIR / "README.md"

SCRIPT_DIR = REPO_ROOT / "03_scripts" / "local_worker_queue"
STATUS_BRAIN = SCRIPT_DIR / "ghoti_status_brain.py"
QUEUE = SCRIPT_DIR / "ghoti_local_worker_queue.py"
CHECK_PS = SCRIPT_DIR / "check_local_worker_queue.ps1"
SCRIPT_README = SCRIPT_DIR / "README.md"

DOC = REPO_ROOT / "docs" / "GHOTI_N6_15A_USEFUL_LOCAL_WORKER_QUEUE_STATUS_BRAIN.md"
SEED_HANDOFF = (
    REPO_ROOT / "14_context" / "agent_handoff_vault" / "02_Agent_Handoffs"
    / "NEXT_LOCAL_WORKER_QUEUE_TASK.md"
)
EXAMPLE_FLAGS = REPO_ROOT / "23_configs" / "ghoti_feature_flags.example.json"
HANDOFF_LOG = (
    REPO_ROOT / "14_context" / "agent_handoff_vault" / "04_Logs"
    / "GHOTI_STATUS_BRAIN_LAST_RUN.md"
)

ALL_FILES = [
    SCHEMA, STATUS_TASK, CUS_TASK, INTAKE_TASK, LWQ_README,
    STATUS_BRAIN, QUEUE, CHECK_PS, SCRIPT_README,
    DOC, SEED_HANDOFF, EXAMPLE_FLAGS,
]

REQUIRED_PACKET_FIELDS = [
    "ok", "repo_root", "origin_main_short", "current_branch",
    "latest_main_commits", "n6_test_count_known_or_null", "latest_codex_report",
    "latest_claude_report", "latest_tool_intake_summary",
    "computer_use_sandbox_status", "telegram_runtime_status",
    "hermes_integration_status", "repo_visibility_unknown_or_public_private",
    "next_recommended_action", "handoff_written", "handoff_path", "gemma_used",
    "fallback_summary_used", "safety",
]

SAFETY_FALSE_FIELDS = [
    "live_browser_used", "os_input_used", "external_api_used",
    "telegram_control_used", "mcp_used", "auto_send_used",
]

SUPPORTED_TASK_TYPES = (
    "status_summary", "computer_use_sandbox_status", "repo_intake_summary",
)

BLOCKED_TASK_TYPES = (
    "launch_claude", "launch_codex", "browser_live", "computer_use_live",
    "telegram_send", "email_send", "whatsapp_send", "mcp_write", "shell_exec",
    "install_repo", "docker_run",
)

N6_15A_FLAGS = (
    "local_worker_queue_enabled", "local_status_brain_enabled",
    "local_gemma_summary_enabled", "auto_schedule_worker_enabled",
    "telegram_status_bridge_enabled", "hermes_memory_writer_enabled",
)

# subprocess is legitimate here (git read-only + optional local ollama), so it is
# NOT forbidden; shell strings, os.system/os.popen, eval/exec, network/external
# imports, webbrowser, installs, and any --allow flag are.
SOURCE_FORBIDDEN_TOKENS = [
    "shell=true", "shell = true",
    "os.system", "os.popen",
    "eval(", "exec(",
    "import requests", "import urllib", "urllib.request", "import http",
    "http.client", "import socket", "socket.socket",
    "webbrowser",
    "pip install", "npm install",
    "--allow-",
]

PS_FORBIDDEN_TOKENS = [
    "invoke-expression", "iex(", "iex ", "invoke-webrequest", "invoke-restmethod",
    "downloadstring", "downloadfile", "new-object net.webclient", "start-process",
]

FALSE_CLAIMS = [
    "ghoti is fully autonomous",
    "live autonomy is enabled",
    "live website automation is enabled",
    "the desktop was controlled",
    "os-level input was used",
    "a real os click was performed",
    "telegram messages were sent",
    "an email was sent",
    "an account was logged in",
]

TEXT_FILES = [DOC, LWQ_README, SCRIPT_README, SEED_HANDOFF]


def read(path):
    return path.read_text(encoding="utf-8")


def norm(text):
    return " ".join(text.lower().split())


def load_json_file(path):
    return json.loads(read(path))


def run_py(script, *args, timeout=120):
    cmd = [sys.executable, str(script), *args]
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, timeout=timeout)
    out = proc.stdout.decode("utf-8", errors="replace").strip()
    err = proc.stderr.decode("utf-8", errors="replace")
    return proc.returncode, out, err


def run_queue_with(task_obj, timeout=120):
    """Write a temp task file, run the queue against it, return parsed result."""
    fd, tmp_name = tempfile.mkstemp(suffix=".json")
    os.close(fd)  # close the descriptor so Windows can unlink it afterwards
    tmp = Path(tmp_name)
    try:
        tmp.write_text(json.dumps(task_obj), encoding="utf-8")
        rc, out, err = run_py(QUEUE, "--task", str(tmp), "--json", timeout=timeout)
        return rc, json.loads(out), err
    finally:
        tmp.unlink(missing_ok=True)


class FilesExistTests(unittest.TestCase):
    def test_all_files_exist(self):
        for path in ALL_FILES:
            self.assertTrue(path.is_file(), msg=f"missing file: {path}")


class SchemaAndExamplesTests(unittest.TestCase):
    def test_schema_is_valid_json(self):
        data = load_json_file(SCHEMA)
        self.assertIsInstance(data, dict)
        self.assertIn("fields", data)
        for field in REQUIRED_PACKET_FIELDS:
            self.assertIn(field, data["fields"], msg=f"schema missing {field}")

    def test_examples_are_valid_json_with_expected_types(self):
        cases = {
            STATUS_TASK: "status_summary",
            CUS_TASK: "computer_use_sandbox_status",
            INTAKE_TASK: "repo_intake_summary",
        }
        for path, expected_type in cases.items():
            data = load_json_file(path)
            self.assertIsInstance(data, dict)
            self.assertEqual(data.get("task_type"), expected_type)

    def test_sandbox_example_is_dry_run_only(self):
        data = load_json_file(CUS_TASK)
        self.assertIs(data.get("dry_run_only"), True)
        self.assertIs(data.get("never_allow_live"), True)

    def test_intake_example_lists_candidates(self):
        data = load_json_file(INTAKE_TASK)
        candidates = data.get("include_candidates")
        self.assertIsInstance(candidates, list)
        for name in ("Ruflo", "TryCUA / CUA", "Browser Harness",
                     "Vercel agent-browser", "UI-TARS"):
            self.assertIn(name, candidates)


class StatusBrainTests(unittest.TestCase):
    def test_json_has_all_required_fields(self):
        rc, out, err = run_py(STATUS_BRAIN, "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertIs(data["ok"], True)
        for field in REQUIRED_PACKET_FIELDS:
            self.assertIn(field, data, msg=f"packet missing {field}")
        self.assertIsInstance(data["latest_main_commits"], list)
        self.assertIsInstance(data["repo_visibility_unknown_or_public_private"], str)
        self.assertIsInstance(data["next_recommended_action"], str)

    def test_safety_flags_all_false(self):
        rc, out, err = run_py(STATUS_BRAIN, "--json")
        self.assertEqual(rc, 0, msg=err)
        safety = json.loads(out)["safety"]
        for field in SAFETY_FALSE_FIELDS:
            self.assertIs(safety[field], False, msg=f"safety.{field} must be false")

    def test_gemma_and_fallback_are_exclusive(self):
        rc, out, err = run_py(STATUS_BRAIN, "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertNotEqual(data["gemma_used"], data["fallback_summary_used"])
        # No gemma flag => deterministic fallback only.
        self.assertIs(data["gemma_used"], False)
        self.assertIs(data["fallback_summary_used"], True)

    def test_write_handoff_writes_markdown(self):
        existed_before = HANDOFF_LOG.exists()
        if not existed_before:
            self.addCleanup(lambda: HANDOFF_LOG.unlink(missing_ok=True))
        rc, out, err = run_py(STATUS_BRAIN, "--write-handoff", "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertIs(data["handoff_written"], True)
        self.assertTrue(str(data["handoff_path"]).endswith("GHOTI_STATUS_BRAIN_LAST_RUN.md"))
        self.assertTrue(HANDOFF_LOG.is_file())
        text = norm(read(HANDOFF_LOG))
        for section in ("current status", "useful capabilities",
                        "pending branches", "safety disabled", "next action"):
            self.assertIn(section, text, msg=f"handoff missing section: {section}")

    def test_gemma_optional_path_never_fails(self):
        # Passes whether or not a local Ollama/Gemma model is installed.
        rc, out, err = run_py(STATUS_BRAIN, "--use-gemma-if-available", "--json",
                              timeout=200)
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertIs(data["ok"], True)
        self.assertNotEqual(data["gemma_used"], data["fallback_summary_used"])

    def test_include_computer_use_sandbox_is_dry_run_only(self):
        rc, out, err = run_py(STATUS_BRAIN, "--include-computer-use-sandbox", "--json")
        self.assertEqual(rc, 0, msg=err)
        cus = json.loads(out)["computer_use_sandbox_status"]
        self.assertIs(cus["browser_launched"], False)
        self.assertIs(cus["dom_action_performed"], False)
        self.assertIs(cus["os_input_used"], False)
        self.assertIs(cus["live_website"], False)


class QueueTests(unittest.TestCase):
    def test_status_summary_supported(self):
        rc, out, err = run_py(QUEUE, "--task", str(STATUS_TASK), "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertIs(data["ok"], True)
        self.assertIs(data["supported"], True)
        self.assertIs(data["blocked"], False)
        self.assertEqual(data["task_type"], "status_summary")
        self.assertIn("ok", data["result"])

    def test_computer_use_sandbox_status_supported_dry_run(self):
        rc, out, err = run_py(QUEUE, "--task", str(CUS_TASK), "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertIs(data["supported"], True)
        result = data["result"]
        self.assertIs(result["dry_run_only"], True)
        self.assertIs(result["computer_use_sandbox_status"]["browser_launched"], False)

    def test_repo_intake_summary_supported(self):
        rc, out, err = run_py(QUEUE, "--task", str(INTAKE_TASK), "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertIs(data["supported"], True)
        candidates = data["result"]["candidates"]
        self.assertEqual(len(candidates), 5)
        for entry in candidates:
            self.assertIn("statically_inspected", entry)

    def test_blocked_task_types_are_blocked(self):
        for task_type in BLOCKED_TASK_TYPES:
            rc, data, err = run_queue_with({"task_type": task_type})
            self.assertIs(data["blocked"], True, msg=f"{task_type} not blocked")
            self.assertIs(data["supported"], False, msg=f"{task_type} marked supported")

    def test_unknown_task_type_blocked_by_default(self):
        rc, data, err = run_queue_with({"task_type": "totally_unknown_kind"})
        self.assertIs(data["blocked"], True)
        self.assertIs(data["supported"], False)

    def test_queue_result_safety_flags_false(self):
        rc, out, err = run_py(QUEUE, "--task", str(STATUS_TASK), "--json")
        self.assertEqual(rc, 0, msg=err)
        safety = json.loads(out)["safety"]
        for field in SAFETY_FALSE_FIELDS:
            self.assertIs(safety[field], False, msg=f"safety.{field} must be false")


class SourceSafetyTests(unittest.TestCase):
    def test_python_sources_have_no_unsafe_tokens(self):
        for path in (STATUS_BRAIN, QUEUE):
            low = read(path).lower()
            for token in SOURCE_FORBIDDEN_TOKENS:
                self.assertNotIn(token, low, msg=f"{path.name} contains {token!r}")

    def test_powershell_check_has_no_unsafe_tokens(self):
        low = read(CHECK_PS).lower()
        for token in PS_FORBIDDEN_TOKENS:
            self.assertNotIn(token, low, msg=f"check ps1 contains {token!r}")

    def test_queue_lists_all_blocked_types(self):
        src = read(QUEUE)
        for task_type in BLOCKED_TASK_TYPES:
            self.assertIn(task_type, src, msg=f"queue source missing {task_type}")

    def test_no_secret_patterns(self):
        combined = "\n".join(read(p) for p in ALL_FILES)
        self.assertNotRegex(combined, r"sk-[A-Za-z0-9_-]{20,}")
        self.assertNotRegex(combined, r"AIza[0-9A-Za-z_-]{30,}")
        self.assertNotRegex(combined, r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY")


class FlagsTests(unittest.TestCase):
    def test_example_config_has_n6_15a_flags_false(self):
        flags = load_json_file(EXAMPLE_FLAGS)
        for flag in N6_15A_FLAGS:
            self.assertIn(flag, flags, msg=f"example config missing {flag!r}")
            self.assertIs(flags[flag], False, msg=f"{flag} must default false")

    def test_example_config_keeps_single_true_flag(self):
        flags = load_json_file(EXAMPLE_FLAGS)
        true_flags = [k for k, v in flags.items() if v is True]
        self.assertEqual(true_flags, ["telegram_status_commands_enabled"])


class DocsTests(unittest.TestCase):
    def test_docs_explain_required_points(self):
        combined = norm("\n".join(read(p) for p in (DOC, LWQ_README, SCRIPT_README)))
        for phrase in ("hermes", "handoff", "telegram", "gemma", "live autonomy",
                       "external api", "account", "repo-intake"):
            self.assertIn(phrase, combined, msg=f"docs missing point: {phrase}")

    def test_docs_say_hermes_reads_handoff_and_telegram_later(self):
        combined = norm("\n".join(read(p) for p in (DOC, LWQ_README, SCRIPT_README,
                                                    SEED_HANDOFF)))
        self.assertIn("hermes can", combined)
        self.assertIn("later", combined)

    def test_docs_have_no_overclaim(self):
        combined = norm("\n".join(read(p) for p in TEXT_FILES))
        for claim in FALSE_CLAIMS:
            self.assertNotIn(claim, combined, msg=f"overclaim present: {claim!r}")


class PowerShellCheckTests(unittest.TestCase):
    PS = shutil.which("pwsh") or shutil.which("powershell")

    @unittest.skipUnless(PS, "PowerShell not available")
    def test_check_emits_json_local_posture(self):
        proc = subprocess.run(
            [self.PS, "-ExecutionPolicy", "Bypass", "-File", str(CHECK_PS)],
            capture_output=True, timeout=180)
        out = proc.stdout.decode("utf-8-sig", errors="replace").strip()
        data = json.loads(out)
        self.assertIs(data["ok"], True)
        self.assertIs(data["status_brain_exists"], True)
        self.assertIs(data["queue_script_exists"], True)
        self.assertIs(data["queue_examples_exist"], True)
        self.assertIs(data["handoff_dir_exists"], True)
        self.assertIs(data["local_only"], True)
        self.assertIs(data["risky_flags_default_false"], True)
        for field in SAFETY_FALSE_FIELDS:
            self.assertIs(data[field], False, msg=f"{field} must be false")


if __name__ == "__main__":
    unittest.main()
