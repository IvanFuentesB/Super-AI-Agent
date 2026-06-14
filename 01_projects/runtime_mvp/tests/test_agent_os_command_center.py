"""Integrated Ghoti Agent OS command center tests.

Proves the vertical slice end to end: CLI status/check/list, workflow
plans, the suggestion-only worker, memory search pointers, ownership
overlap detection, handoff packets, full demo evidence, generated-file
hygiene, and the dashboard/launcher wiring (static assertions, same
convention as the n6.39/n6.40 dashboard tests).
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "03_scripts" / "agent_os"))
import data_only_writer  # noqa: E402

AGENT_OS = REPO_ROOT / "03_scripts" / "agent_os" / "ghoti_agent_os.py"
LOCAL_WORKER = REPO_ROOT / "03_scripts" / "agent_os" / "local_worker.py"
CHECKER = REPO_ROOT / "03_scripts" / "agent_os" / "check_agent_os.py"
LAUNCHER = REPO_ROOT / "03_scripts" / "ghoti_product_launcher.py"
SERVER_JS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js"
INDEX_HTML = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html"
APP_JS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "app.js"
RUNS_DIR = REPO_ROOT / "14_context" / "agent_os" / "runs"
RUST_BINARIES = [
    REPO_ROOT / "rust" / "target" / "release" / "ghoti_policy_checker.exe",
    REPO_ROOT / "rust" / "target" / "release" / "ghoti_policy_checker",
    REPO_ROOT / "rust" / "target" / "debug" / "ghoti_policy_checker.exe",
    REPO_ROOT / "rust" / "target" / "debug" / "ghoti_policy_checker",
]

WORKFLOW_IDS = ["coding-task", "repo-audit", "content-video", "business-research",
                "email-draft", "automation-n8n", "computer-use-prep"]

SECRET_PATTERNS = ["api_key=", "apikey=", "password=", "secret=", "bearer ",
                   "ghp_", "sk-ant-", "AKIA"]


def run_cli(*args: str) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(AGENT_OS), *args, "--json"],
        capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=180, shell=False,
    )
    try:
        return proc.returncode, json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise AssertionError("CLI emitted no JSON for %s:\nstdout=%s\nstderr=%s"
                             % (args, proc.stdout[:500], proc.stderr[:500]))


class TestStatusAndCheck(unittest.TestCase):
    def test_status_returns_json_with_core_sections(self):
        code, payload = run_cli("--status")
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        for key in ("repo", "recipes", "memory", "handoffs", "lanes",
                    "local_model", "worker", "workflows", "safety_flags"):
            self.assertIn(key, payload)
        self.assertEqual(payload["worker"]["mode"], "suggestion_only")
        self.assertEqual(payload["safety_flags"]["relay_mode"], "copy_paste_only")

    def test_self_check_all_pass(self):
        code, payload = run_cli("--check")
        self.assertEqual(code, 0, "self-check failed: %s"
                         % [c for c in payload["checks"] if not c["ok"]])
        self.assertEqual(payload["passed"], payload["total"])

    def test_standalone_checker_exits_zero(self):
        proc = subprocess.run([sys.executable, str(CHECKER), "--json"],
                              capture_output=True, text=True, cwd=str(REPO_ROOT),
                              timeout=180, shell=False)
        self.assertEqual(proc.returncode, 0, proc.stdout[:500])


class TestWorkflowTemplates(unittest.TestCase):
    def test_seven_workflows_exist(self):
        code, payload = run_cli("--list-workflows")
        self.assertEqual(code, 0)
        self.assertEqual([w["id"] for w in payload["workflows"]], WORKFLOW_IDS)
        self.assertEqual(len(payload["roster"]), 6)

    def test_template_fingerprint_is_stable(self):
        _, first = run_cli("--list-workflows")
        _, second = run_cli("--list-workflows")
        self.assertEqual(first["template_fingerprint"], second["template_fingerprint"])

    def test_plan_workflow_writes_repo_local_ascii(self):
        code, payload = run_cli("--plan-workflow", "coding-task")
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        plan_path = REPO_ROOT / payload["plan_path"]
        self.assertTrue(plan_path.is_file())
        plan_path.resolve().relative_to(REPO_ROOT)  # raises if it escaped
        content = plan_path.read_text(encoding="utf-8")
        self.assertTrue(all(ord(c) < 128 for c in content), "plan is not ASCII")
        self.assertIn("copy_paste_only", content)

    def test_task_wave_is_deterministic_simulation(self):
        _, first = run_cli("--task-wave", "content-video")
        _, second = run_cli("--task-wave", "content-video")
        self.assertTrue(first["ok"])
        self.assertTrue(first["simulation_only"])
        self.assertEqual(first["waves"], second["waves"])


class TestLocalWorker(unittest.TestCase):
    def test_worker_source_has_no_execution_primitives(self):
        source = LOCAL_WORKER.read_text(encoding="utf-8")
        for marker in ("import subprocess", "from subprocess", "os.system(",
                       "os.popen(", "os.exec", "urllib.request"):
            self.assertNotIn(marker, source, "worker must stay inert: " + marker)

    def test_worker_suggest_writes_handoff_only(self):
        code, payload = run_cli("--worker-suggest", "content-video")
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["mode"], "suggestion_only")
        self.assertEqual(payload["executed_commands"], [])
        suggestion = REPO_ROOT / payload["suggestion_path"]
        self.assertTrue(suggestion.is_file())
        self.assertIn("14_context/agent_os/handoffs", payload["suggestion_path"])
        self.assertIn("no command was executed",
                      suggestion.read_text(encoding="utf-8").lower())

    def test_handoff_packets_are_copy_paste_only(self):
        code, payload = run_cli("--build-handoff", "--workflow", "coding-task")
        self.assertEqual(code, 0)
        self.assertEqual(sorted(payload["packets"]), ["claude", "codex", "hermes"])
        for packet_rel in payload["packets"].values():
            text = (REPO_ROOT / packet_rel).read_text(encoding="utf-8")
            self.assertIn("Human copy-paste required: YES", text)
            self.assertIn("relay_mode: copy_paste_only", text)


class TestMemorySearch(unittest.TestCase):
    def test_search_returns_compact_repo_relative_pointers(self):
        code, payload = run_cli("--search-memory", "ghoti")
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertGreater(payload["hit_count"], 0)
        for hit in payload["hits"]:
            self.assertNotIn(":\\", hit["path"], "absolute path leaked")
            self.assertFalse(hit["path"].startswith("/"))
            self.assertIsInstance(hit["line"], int)
            self.assertLessEqual(len(hit["snippet"]), 160)

    def test_bad_search_term_is_rejected(self):
        code, payload = run_cli("--search-memory", ";rm -rf /!!")
        self.assertEqual(code, 1)
        self.assertFalse(payload["ok"])


class TestOwnershipCheck(unittest.TestCase):
    def test_default_wave_has_no_overlap(self):
        code, payload = run_cli("--ownership-check")
        self.assertEqual(code, 0)
        self.assertTrue(payload["allowed"])
        self.assertEqual(payload["overlap_count"], 0)

    def test_overlap_fixture_is_caught(self):
        RUNS_DIR.mkdir(parents=True, exist_ok=True)
        fixture = RUNS_DIR / "test_overlap_wave.json"
        data_only_writer.write_text(
            fixture,
            json.dumps({"assignments": [
                {"agent": "coder", "files": ["03_scripts/x.py"]},
                {"agent": "auditor", "files": ["03_scripts\\X.py"]},
            ]}),
        )
        code, payload = run_cli("--ownership-check", "--wave-input",
                                str(fixture.relative_to(REPO_ROOT)))
        self.assertFalse(payload["allowed"])
        self.assertEqual(payload["overlap_count"], 1)
        self.assertEqual(payload["overlaps"][0]["agents"], ["auditor", "coder"])

    def test_checker_identity_matches_binary_presence(self):
        binary_exists = any(b.is_file() for b in RUST_BINARIES)
        _, payload = run_cli("--ownership-check")
        self.assertEqual(payload["rust_checker_used"], binary_exists)
        expected = "ghoti_policy_checker" if binary_exists \
            else "python_mirror_of_ghoti_policy_checker"
        self.assertEqual(payload["checker"], expected)


class TestFullDemoAndHygiene(unittest.TestCase):
    def test_full_demo_creates_evidence_and_clean_artifacts(self):
        code, payload = run_cli("--full-demo")
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(all(step["ok"] for step in payload["steps"]))
        evidence_md = REPO_ROOT / payload["evidence_path"]
        evidence_json = REPO_ROOT / payload["evidence_json_path"]
        self.assertTrue(evidence_md.is_file())
        self.assertTrue(evidence_json.is_file())
        # Hygiene over everything this demo generated: no absolute private
        # paths, no secret-looking strings, ASCII only.
        for rel in [payload["evidence_path"]] + payload["artifacts"]:
            text = (REPO_ROOT / rel).read_text(encoding="utf-8")
            lower = text.lower()
            self.assertNotIn("c:\\users", lower, rel)
            self.assertNotIn("c:/users", lower, rel)
            for pattern in SECRET_PATTERNS:
                self.assertNotIn(pattern.lower(), lower, "%s in %s" % (pattern, rel))
            self.assertTrue(all(ord(c) < 128 for c in text), "%s not ASCII" % rel)


class TestLauncherIntegration(unittest.TestCase):
    def test_launcher_agent_os_status_flag_works(self):
        proc = subprocess.run(
            [sys.executable, str(LAUNCHER), "--agent-os-status", "--json"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=120, shell=False)
        self.assertEqual(proc.returncode, 0, proc.stderr[:300])
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["action"], "agent-os-status")

    def test_launcher_lists_agent_os_lane(self):
        source = LAUNCHER.read_text(encoding="utf-8")
        self.assertIn("agent_os_command_center", source)
        self.assertIn("Agent OS Command Center", source)


class TestDashboardWiring(unittest.TestCase):
    def setUp(self):
        self.index = INDEX_HTML.read_text(encoding="utf-8")
        self.app = APP_JS.read_text(encoding="utf-8")
        self.server = SERVER_JS.read_text(encoding="utf-8")

    def test_nav_and_panel_present(self):
        self.assertIn('data-console-view="agent-os"', self.index)
        self.assertIn('data-console-view-panel="agent-os"', self.index)
        self.assertIn('id="agentos-full-demo"', self.index)
        self.assertIn('id="agentos-search-term"', self.index)

    def test_console_views_gate_includes_agent_os(self):
        self.assertIn('"agent-os",', self.app)
        self.assertIn("function initAgentOs()", self.app)
        self.assertIn("initAgentOs();", self.app)

    def test_server_endpoints_and_allowlist(self):
        for route in ("agent-os-status", "agent-os-workflows", "agent-os-plan",
                      "agent-os-worker-suggest", "agent-os-handoff",
                      "agent-os-task-wave", "agent-os-search",
                      "agent-os-full-demo", "agent-os-latest"):
            self.assertIn("/api/product-control/%s" % route, self.server)
        self.assertIn("AGENT_OS_WORKFLOW_IDS", self.server)
        for workflow_id in WORKFLOW_IDS:
            self.assertIn('"%s"' % workflow_id, self.server)

    def test_honesty_labels_present(self):
        self.assertIn("suggestion-only", self.index)
        self.assertIn("simulation", self.index)
        self.assertIn("Human copy-paste required", self.index)


if __name__ == "__main__":
    unittest.main()
