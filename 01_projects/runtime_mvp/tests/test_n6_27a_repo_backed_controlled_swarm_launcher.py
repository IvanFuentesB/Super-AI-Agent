"""Tests for N+6.27A - Repo-Backed Controlled Swarm Launcher (Dry Run).

These tests lock the safety and behavior of the dry-run swarm launcher. They assert
(1) every committed file exists, (2) the launcher source uses no subprocess/shell/os.system
and its --check reports a no-process-spawn, no-file-write, dry-run-only posture with
live_launch_enabled false and approval + kill switch required, (3) a basic task yields a
dry_run_ready plan with dependency waves, placeholder worktrees, the five roles, and the
default agents, (4) an overlapping task is blocked (one owner per path), a parallel-safe
task yields multiple waves, and an out-of-scope path is blocked, (5) the schemas/examples/
manifest are valid and the attribution manifest commits no third-party code and needs no
Rust, and (6) no secret, token, chat-id, video-downloader token, bot-bypass phrase, or real
local path / username is committed. Flagged literals are assembled at runtime.
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

SL_DIR = REPO_ROOT / "03_scripts" / "swarm_launcher"
SCRIPT = SL_DIR / "ghoti_swarm_launcher.py"
CHECK_PS = SL_DIR / "check_swarm_launcher.ps1"

CTX = REPO_ROOT / "14_context" / "swarm_launcher"
TASK_SCHEMA = CTX / "swarm_task_schema.json"
PLAN_SCHEMA = CTX / "swarm_plan_schema.json"
EX_BASIC = CTX / "examples" / "basic_two_agent_task.json"
EX_PARALLEL = CTX / "examples" / "parallel_safe_task.json"
EX_BLOCKED = CTX / "examples" / "blocked_overlap_task.json"
MANIFEST = CTX / "repo_inspiration_manifest_n6_27a.json"
INSP_REPORT = CTX / "repo_inspiration_report_n6_27a.md"
README = CTX / "README.md"

DOC = REPO_ROOT / "docs" / "GHOTI_N6_27A_REPO_BACKED_CONTROLLED_SWARM_LAUNCHER.md"
HANDOFF = (REPO_ROOT / "14_context" / "agent_handoff_vault" / "02_Agent_Handoffs"
           / "NEXT_CONTROLLED_SWARM_TASK.md")
REPORT = REPO_ROOT / "14_context" / "claude_n6_27a_repo_backed_controlled_swarm_launcher.md"

ALL_FILES = [SCRIPT, CHECK_PS, TASK_SCHEMA, PLAN_SCHEMA, EX_BASIC, EX_PARALLEL, EX_BLOCKED,
             MANIFEST, INSP_REPORT, README, DOC, HANDOFF, REPORT]
TEXT_FILES = ALL_FILES

ROLES = ["planner", "builder", "auditor", "summarizer", "human_approver"]
DEFAULT_AGENT_NAMES = ["ChatGPT strategy", "Claude builder", "Codex auditor",
                       "Hermes coordinator", "local model summarizer"]

CHAT_ID_RE = re.compile(r"\b\d{8,12}\b")
TOKEN_RE = re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")


def read(path):
    return path.read_text(encoding="utf-8")


def norm(text):
    return " ".join(text.lower().split())


def run_py(*args, timeout=60):
    proc = subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


class FilesExistTests(unittest.TestCase):
    def test_all_files_exist(self):
        for path in ALL_FILES:
            self.assertTrue(path.is_file(), msg=f"missing file: {path}")


class SourceSafetyTests(unittest.TestCase):
    def setUp(self):
        self.src = read(SCRIPT)

    def test_no_subprocess_import(self):
        self.assertNotIn("import subprocess", self.src)
        self.assertNotIn("subprocess.run(", self.src)

    def test_no_shell_or_system(self):
        self.assertNotIn("shell=True", self.src)
        self.assertNotIn("os.system(", self.src)

    def test_no_popen_call(self):
        # A real Popen( / os.popen( / os.exec call must not exist (the regex strings in the
        # launcher's own self-check are not calls).
        self.assertIsNone(re.search(r"Popen\s*\(|os\.popen\s*\(|os\.exec", self.src))

    def test_no_file_write_call(self):
        self.assertIsNone(re.search(r"\.write_text\s*\(|\.write_bytes\s*\(|\.mkdir\s*\(", self.src))


class CheckCliTests(unittest.TestCase):
    def test_check_ok(self):
        rc, out, err = run_py("--check", "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertTrue(data["ok"], msg=f"check not ok: {data}")
        for key in ["no_subprocess", "no_shell_true", "no_os_exec_or_popen",
                    "no_process_spawn", "no_file_writes", "no_worktree_creation",
                    "roles_complete", "approval_required", "kill_switch_required"]:
            self.assertTrue(data[key], msg=f"check.{key} must be true")
        self.assertFalse(data["live_launch_enabled"])
        self.assertEqual(data["default_agents_count"], 6)


class BasicPlanTests(unittest.TestCase):
    def setUp(self):
        rc, out, err = run_py("--task", str(EX_BASIC), "--dry-run", "--json")
        self.assertEqual(rc, 0, msg=err)
        self.data = json.loads(out)

    def test_dry_run_ready(self):
        self.assertEqual(self.data["status"], "dry_run_ready")
        self.assertEqual(self.data["mode"], "dry_run")

    def test_gates(self):
        gates = self.data["gates"]
        self.assertFalse(gates["live_launch_enabled"])
        self.assertTrue(gates["approval_required"])
        self.assertTrue(gates["kill_switch_required"])
        self.assertEqual(gates["main_merge"], "codex_gate_only")

    def test_roles_and_agents(self):
        self.assertEqual(self.data["roles"], ROLES)
        names = [a["name"] for a in self.data["default_agents"]]
        for needed in DEFAULT_AGENT_NAMES:
            self.assertIn(needed, names, msg=f"missing default agent {needed}")

    def test_waves_and_placeholder_worktrees(self):
        self.assertEqual(self.data["waves"], [["build_feature"], ["audit_feature"]])
        for a in self.data["assignments"]:
            self.assertTrue(a["proposed_worktree"].startswith("<repo>/.claude/worktrees/"))
            self.assertFalse(a["executed"])

    def test_refused_live_actions(self):
        joined = " ".join(self.data["refused_live_actions"]).lower()
        self.assertIn("live agent launch", joined)
        self.assertIn("browser", joined)
        self.assertIn("auto-submit", joined)

    def test_arena_status_safe(self):
        arena = self.data["arena_status"]
        self.assertTrue(arena["simulation"])
        self.assertFalse(arena["live_execution"])


class BlockedAndParallelTests(unittest.TestCase):
    def test_blocked_overlap(self):
        rc, out, err = run_py("--task", str(EX_BLOCKED), "--dry-run", "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertEqual(data["status"], "blocked")
        self.assertFalse(data["overlap"]["one_owner_per_path"])
        self.assertTrue(data["overlap"]["conflicts"])

    def test_parallel_safe_waves(self):
        rc, out, err = run_py("--task", str(EX_PARALLEL), "--dry-run", "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertEqual(data["status"], "dry_run_ready")
        self.assertEqual(len(data["waves"]), 3)

    def test_out_of_scope_blocked(self):
        spec = {
            "title": "scope violation",
            "scope": {"allowed_paths": ["03_scripts/example/"]},
            "tasks": [{"id": "t1", "role": "builder", "files": ["../../etc/passwd"], "depends_on": []}],
        }
        fd, tmp = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        self.addCleanup(lambda: os.path.exists(tmp) and os.remove(tmp))
        Path(tmp).write_text(json.dumps(spec), encoding="utf-8")
        rc, out, err = run_py("--task", tmp, "--dry-run", "--json")
        self.assertEqual(rc, 0, msg=err)
        data = json.loads(out)
        self.assertEqual(data["status"], "blocked")
        self.assertTrue(data["scope"]["violations"])


class SchemaAndManifestTests(unittest.TestCase):
    def test_schemas_valid(self):
        task_schema = json.loads(read(TASK_SCHEMA))
        plan_schema = json.loads(read(PLAN_SCHEMA))
        self.assertEqual(task_schema["type"], "object")
        self.assertFalse(plan_schema["x_safety"]["live_launch_enabled"])
        self.assertTrue(plan_schema["x_safety"]["approval_required"])

    def test_examples_valid(self):
        for ex in [EX_BASIC, EX_PARALLEL, EX_BLOCKED]:
            data = json.loads(read(ex))
            self.assertIn("tasks", data)

    def test_manifest_no_vendored_code_no_rust(self):
        man = json.loads(read(MANIFEST))
        self.assertTrue(man["no_third_party_code_committed"])
        self.assertTrue(man["no_code_copied"])
        self.assertFalse(man["rust_toolchain"]["required_by_inspected_repos"])
        self.assertFalse(man["rust_toolchain"]["installed"])
        repos = " ".join(r["repo"] for r in man["repos"]).lower()
        for needed in ["am-will/swarms", "hkuds/clawteam", "affaan-m/claude-swarm", "affaan-m/ecc"]:
            self.assertIn(needed, repos)


class DocsTests(unittest.TestCase):
    def test_doc_mentions_dry_run_and_deferral(self):
        body = norm(read(DOC))
        self.assertIn("dry-run", body)
        self.assertIn("repo-backed", body)
        self.assertIn("deferred to a later", body)

    def test_handoff_controlled_launcher(self):
        self.assertIn("real launch", norm(read(HANDOFF)))

    def test_report_verdict(self):
        self.assertIn("IMPLEMENTED_AND_PUSHED", read(REPORT))


class SecretAndFlaggedTokenTests(unittest.TestCase):
    def test_no_token_or_chat_id(self):
        for path in TEXT_FILES:
            text = read(path)
            self.assertIsNone(TOKEN_RE.search(text), msg=f"token-like pattern in {path.name}")
            self.assertIsNone(CHAT_ID_RE.search(text), msg=f"chat-id-like value in {path.name}")

    def test_no_secret_blobs(self):
        combined = "\n".join(read(p) for p in TEXT_FILES)
        self.assertNotRegex(combined, r"sk-[A-Za-z0-9]{20,}")
        self.assertNotRegex(combined, r"-----BEGIN [A-Z ]+-----")

    def test_no_video_downloader_token(self):
        combined = "\n".join(read(p) for p in TEXT_FILES)
        self.assertNotIn("yt" + "-" + "dlp", combined)
        self.assertNotIn("youtube" + "-" + "dl", combined)

    def test_json_has_no_bot_bypass_phrases(self):
        body = read(MANIFEST).lower()
        for phrase in ["captcha" + " bypass", "bot detection" + " bypass",
                       "cloak browser" + " bypass", "anti-bot" + " bypass"]:
            self.assertNotIn(phrase, body)


class NoLocalPathLeakTests(unittest.TestCase):
    """Committed N+6.27A files must carry no real local path / username. Forbidden tokens
    are assembled at runtime so this file never contains them literally."""

    def test_no_real_local_path_leak(self):
        bslash = chr(92)
        forbidden = [
            "ai" + "_sandbox",
            "Nav" + "if",
            "C:" + bslash + "Users" + bslash,
            "C:" + "/Users/",
            "/mnt/" + "c/Users/",
            "Documents" + bslash + "AI_Managed_Only",
        ]
        for path in TEXT_FILES:
            text = read(path)
            for token in forbidden:
                self.assertNotIn(token, text, msg=f"local path/username leak in {path.name}")


if __name__ == "__main__":
    unittest.main()
