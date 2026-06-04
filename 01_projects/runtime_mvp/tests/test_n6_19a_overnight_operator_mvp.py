import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def run_cmd(args):
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )


class OvernightOperatorFilesTests(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            "docs/GHOTI_N6_19A_OVERNIGHT_OPERATOR_MVP.md",
            "docs/GHOTI_DOCUMENSO_VS_OVERLEAF_PROJECT_DOCS.md",
            "14_context/overnight_operator/README.md",
            "14_context/overnight_operator/operator_status_schema.json",
            "14_context/overnight_operator/queue_examples/claude_runtime_task.json",
            "14_context/overnight_operator/queue_examples/codex_audit_task.json",
            "14_context/overnight_operator/queue_examples/hermes_status_task.json",
            "14_context/overnight_operator/queue_examples/repo_execution_task_markitdown.json",
            "14_context/overnight_operator/queue_examples/repo_execution_task_ecc.json",
            "14_context/overnight_operator/queue_examples/repo_execution_task_gbrain.json",
            "14_context/overnight_operator/allowlists/allowed_repos_n6_19a.json",
            "14_context/overnight_operator/allowlists/allowed_commands_n6_19a.json",
            "14_context/overnight_operator/repo_execution_reports/ecc_n6_19a.md",
            "14_context/overnight_operator/repo_execution_reports/ecc_extraction_plan_n6_19a.md",
            "14_context/overnight_operator/repo_execution_reports/gbrain_n6_19a.md",
            "14_context/overnight_operator/repo_execution_reports/gbrain_memory_extraction_plan_n6_19a.md",
            "14_context/overnight_operator/repo_execution_reports/markitdown_n6_19a.md",
            "14_context/skills/ecc_inspired_agent_setup_n6_19a.md",
            "03_scripts/overnight_operator/ghoti_prompt_packet_builder.py",
            "03_scripts/overnight_operator/ghoti_clipboard_relay.ps1",
            "03_scripts/overnight_operator/ghoti_operator_queue.py",
            "03_scripts/overnight_operator/ghoti_repo_execution_sandbox.py",
            "03_scripts/overnight_operator/ecc_agent_setup_inspector.py",
            "03_scripts/overnight_operator/check_overnight_operator.ps1",
            "23_configs/overnight_operator.example.json",
            "14_context/agent_handoff_vault/02_Agent_Handoffs/NEXT_OVERNIGHT_OPERATOR_TASK.md",
            "14_context/claude_n6_19a_overnight_operator_mvp.md",
            "21_repos/third_party_runtime_sandbox/.gitkeep",
        ]
        missing = [p for p in required if not (REPO_ROOT / p).exists()]
        self.assertEqual([], missing)

    def test_feature_flags_default_false(self):
        flags = json.loads((REPO_ROOT / "23_configs/ghoti_feature_flags.example.json").read_text())
        for name in [
            "overnight_operator_enabled",
            "clipboard_relay_enabled",
            "clipboard_paste_enabled",
            "approved_window_paste_enabled",
            "auto_submit_enabled",
            "external_repo_execution_enabled",
            "ecc_integration_enabled",
            "gbrain_integration_enabled",
            "markitdown_sandbox_enabled",
            "documenso_overleaf_docs_lane_enabled",
            "unattended_mode_enabled",
            "overnight_auto_merge_enabled",
        ]:
            self.assertIs(flags.get(name), False, name)
        enabled = [k for k, v in flags.items() if v is True]
        self.assertEqual(["telegram_status_commands_enabled"], enabled)

    def test_runtime_sandbox_is_gitignored(self):
        gitignore = (REPO_ROOT / ".gitignore").read_text()
        self.assertIn("21_repos/third_party_runtime_sandbox/*", gitignore)
        self.assertIn("!21_repos/third_party_runtime_sandbox/.gitkeep", gitignore)


class OvernightOperatorRuntimeTests(unittest.TestCase):
    def test_repo_sandbox_list_json(self):
        proc = run_cmd([sys.executable, "03_scripts/overnight_operator/ghoti_repo_execution_sandbox.py", "--list", "--json"])
        self.assertEqual(0, proc.returncode, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertTrue(data["ok"])
        names = {repo["name"] for repo in data["repos"]}
        self.assertIn("ECC", names)
        self.assertIn("GBrain", names)
        self.assertIn("MarkItDown", names)
        self.assertFalse(any(repo["runtime_execution_allowed"] for repo in data["repos"]))

    def test_static_scans_are_json_when_repos_present_or_honest(self):
        for repo in ["ECC", "GBrain", "MarkItDown"]:
            proc = run_cmd([sys.executable, "03_scripts/overnight_operator/ghoti_repo_execution_sandbox.py", "--repo", repo, "--static-scan", "--json"])
            self.assertEqual(0, proc.returncode, proc.stderr)
            data = json.loads(proc.stdout)
            self.assertTrue(data["ok"])
            self.assertIn(data["safety_verdict"], {"safe", "needs_review", "blocked", "not_present"})
            self.assertFalse(data["safety"]["runtime_execution_default"])

    def test_ecc_inspector_degrades_or_reports_components(self):
        proc = run_cmd([sys.executable, "03_scripts/overnight_operator/ecc_agent_setup_inspector.py", "--repo", "21_repos/third_party_runtime_sandbox/ecc", "--json"])
        data = json.loads(proc.stdout)
        if data["repo_present"]:
            self.assertEqual(0, proc.returncode, proc.stderr)
            self.assertIn("recommended_ghoti_adaptations", data)
            self.assertFalse(data["safety"]["execution_performed"])
        else:
            self.assertNotEqual(0, proc.returncode)

    def test_prompt_packet_builder_and_queue_are_safe(self):
        task = "14_context/overnight_operator/queue_examples/claude_runtime_task.json"
        proc = run_cmd([sys.executable, "03_scripts/overnight_operator/ghoti_prompt_packet_builder.py", "--task", task, "--json"])
        self.assertEqual(0, proc.returncode, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertTrue(data["ok"])
        self.assertFalse(data["safety"]["auto_submit"])
        self.assertFalse(data["safety"]["clipboard_paste"])
        self.assertIn("manual", data["packet_markdown"].lower())

        blocked = {
            "task_type": "live_app_paste",
            "mission": "try to paste into an app",
        }
        result = subprocess.run(
            [sys.executable, "-c", (
                "import importlib.util,json,pathlib;"
                "p=pathlib.Path('03_scripts/overnight_operator/ghoti_operator_queue.py');"
                "s=importlib.util.spec_from_file_location('q',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
                "print(json.dumps(m.dispatch(%r)))" % blocked
            )],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        queue_data = json.loads(result.stdout)
        self.assertFalse(queue_data["ok"])
        self.assertTrue(queue_data["blocked"])

    def test_clipboard_relay_dry_run_does_not_paste(self):
        packet = REPO_ROOT / "14_context/overnight_operator/outbox/test_fixture_packet.md"
        packet.write_text("# local packet fixture\n", encoding="utf-8")
        try:
            proc = subprocess.run(
                [
                    "powershell",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    "03_scripts/overnight_operator/ghoti_clipboard_relay.ps1",
                    "-InputFile",
                    str(packet),
                    "-DryRun",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(0, proc.returncode, proc.stderr)
            data = json.loads(proc.stdout)
            self.assertTrue(data["ok"])
            self.assertTrue(data["dry_run"])
            self.assertFalse(data["copied_to_clipboard"])
            self.assertFalse(data["pasted_into_app"])
            self.assertFalse(data["auto_submitted"])
        finally:
            packet.unlink(missing_ok=True)


class OvernightOperatorDocsTests(unittest.TestCase):
    def test_documenso_overleaf_classification(self):
        text = (REPO_ROOT / "docs/GHOTI_DOCUMENSO_VS_OVERLEAF_PROJECT_DOCS.md").read_text()
        self.assertIn("Documenso: signing, approval workflow", text)
        self.assertIn("Overleaf: collaborative LaTeX", text)
        self.assertIn("university", text.lower())
        self.assertIn("contracts", text.lower())

    def test_reports_record_actual_external_repo_results(self):
        ecc = (REPO_ROOT / "14_context/overnight_operator/repo_execution_reports/ecc_n6_19a.md").read_text()
        gbrain = (REPO_ROOT / "14_context/overnight_operator/repo_execution_reports/gbrain_n6_19a.md").read_text()
        markitdown = (REPO_ROOT / "14_context/overnight_operator/repo_execution_reports/markitdown_n6_19a.md").read_text()
        self.assertIn("0f84c0e", ecc)
        self.assertIn("agent", ecc.lower())
        self.assertIn("9a0bae8", gbrain)
        self.assertIn("brain", gbrain.lower())
        self.assertIn("e144e0a", markitdown)
        self.assertIn("blocked for runtime execution", markitdown)


if __name__ == "__main__":
    unittest.main()
