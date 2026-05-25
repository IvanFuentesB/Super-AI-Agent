import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
REPO_MAP = REPO_ROOT / "03_scripts" / "ghoti_repo_knowledge_map.py"
LAUNCHER = REPO_ROOT / "03_scripts" / "ghoti_product_launcher.py"
CONTEXT_PACK = REPO_ROOT / "03_scripts" / "ghoti_context_pack_builder.py"

LAUNCHER_COMMAND = "python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard"
CONTEXT_PACK_COMMAND = "python 03_scripts/ghoti_product_launcher.py --context-pack --json"
REPO_MAP_COMMAND = "python 03_scripts/ghoti_product_launcher.py --repo-map --json"
NEXT_BUNDLE_COMMAND = "python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json"


class GhotiRepoKnowledgeMapTests(unittest.TestCase):
    def _run_map(self, *args, output_dir=None):
        command = [sys.executable, str(REPO_MAP), *args, "--json"]
        if output_dir is not None:
            command.extend(["--output-dir", str(output_dir)])
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=60,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"repo map failed\nstdout={completed.stdout}\nstderr={completed.stderr}",
        )
        return json.loads(completed.stdout)

    def test_status_json_is_local_safe_and_marks_graphify_as_roadmap_only(self):
        payload = self._run_map("--status")

        self.assertEqual(payload["ok"], True)
        self.assertEqual(payload["local_only"], True)
        self.assertEqual(payload["external_api_used"], False)
        self.assertEqual(payload["network_used"], False)
        self.assertEqual(payload["external_repo_runtime"], "not_wired")
        self.assertEqual(payload["graphify_runtime"], "roadmap_only_not_wired")
        self.assertIn("readiness_percent", payload)
        self.assertIsInstance(payload["readiness_percent"], (int, float))
        self.assertGreaterEqual(payload["readiness_percent"], 0)
        self.assertLessEqual(payload["readiness_percent"], 100)
        self.assertIn("Repo knowledge readiness", payload["status_line"])
        self.assertIn("task_bundles", payload)
        self.assertIn("next-milestone", payload["task_bundles"])
        self.assertIn("output_paths", payload)
        self.assertEqual(payload["safety"]["no_live_apis"], True)
        self.assertEqual(payload["safety"]["no_external_repos"], True)

    def test_write_creates_expected_files_and_excludes_unsafe_paths(self):
        runtime_tmp = REPO_ROOT / "01_projects" / "dashboard_mvp" / "runtime_data"
        runtime_tmp.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=runtime_tmp) as tmp:
            output_dir = Path(tmp)
            payload = self._run_map("--write", output_dir=output_dir)

            expected = {
                "repo_knowledge_map.json",
                "repo_knowledge_map.md",
                "latest_reports_index.md",
                "subsystem_index.md",
                "task_bundle_audit_main.md",
                "task_bundle_dashboard.md",
                "task_bundle_local_memory.md",
                "task_bundle_local_model_worker.md",
                "task_bundle_local_model_routing.md",
                "task_bundle_hermes.md",
                "task_bundle_content_workflow.md",
                "task_bundle_safety.md",
                "task_bundle_next_milestone.md",
                "codex_next_prompt_graph_context.md",
                "chatgpt_repo_context_summary.md",
            }
            self.assertEqual(payload["ok"], True)
            self.assertEqual(set(payload["paths"].keys()), expected)
            for filename in expected:
                self.assertTrue((output_dir / filename).exists(), filename)

            map_json = json.loads((output_dir / "repo_knowledge_map.json").read_text(encoding="utf-8"))
            indexed_paths = "\n".join(item["path"] for item in map_json["important_files"])
            self.assertIn("03_scripts/ghoti_product_launcher.py", indexed_paths)
            self.assertIn("03_scripts/ghoti_context_pack_builder.py", indexed_paths)
            self.assertIn("01_projects/dashboard_mvp/public/index.html", indexed_paths)
            self.assertIn("docs/CODEX_ONLY_WORKFLOW.md", indexed_paths)
            self.assertIn("14_context/codex_n5_6b_main_merge_local_model_easy_worker_lane.md", indexed_paths)

            combined = "\n".join(
                path.read_text(encoding="utf-8")
                for path in output_dir.iterdir()
                if path.is_file()
            )
            self.assertIn("latest report index", combined.lower())
            self.assertIn("Graphify runtime: roadmap only/not wired", combined)
            self.assertIn("no external repo runtime", combined)
            self.assertIn("no network", combined)
            self.assertNotIn(".claude/worktrees", indexed_paths)
            self.assertNotIn(".git/", indexed_paths)
            self.assertNotIn("node_modules", indexed_paths)
            self.assertNotRegex(combined, r"\.env(?:\s|$|/)")
            self.assertNotRegex(combined, r"sk-[A-Za-z0-9_-]{20,}")
            self.assertNotRegex(combined, r"ghp_[A-Za-z0-9_]{20,}")
            self.assertNotRegex(combined, r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY")

    def test_task_bundle_contains_required_sections_and_next_prompt(self):
        payload = self._run_map("--bundle", "next-milestone")

        self.assertEqual(payload["ok"], True)
        self.assertEqual(payload["bundle"], "next-milestone")
        text = payload["text"]
        for heading in [
            "## Purpose",
            "## Files To Inspect First",
            "## Current Truth",
            "## Safety Boundaries",
            "## Useful Commands",
            "## Validation Commands",
            "## Known Limitations",
            "## Next Recommended Prompt",
        ]:
            self.assertIn(heading, text)
        self.assertIn("N+5.8A", text)
        self.assertIn("Hermes Agent Workflow", text)
        self.assertIn(REPO_MAP_COMMAND, text)
        self.assertIn("no live APIs", text)
        self.assertIn("no network", text)

    def test_context_pack_launcher_and_dashboard_surface_repo_knowledge_lane(self):
        runtime_tmp = REPO_ROOT / "01_projects" / "dashboard_mvp" / "runtime_data"
        runtime_tmp.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=runtime_tmp) as tmp:
            output_dir = Path(tmp)
            context = subprocess.run(
                [
                    sys.executable,
                    str(CONTEXT_PACK),
                    "--write",
                    "--json",
                    "--output-dir",
                    str(output_dir),
                    "--generated-at",
                    "2026-05-23T00:00:00Z",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                timeout=60,
            )
            self.assertEqual(context.returncode, 0, msg=context.stderr or context.stdout)
            context_pack = (output_dir / "ghoti_current_context_pack.md").read_text(encoding="utf-8")
            self.assertIn("Repo Knowledge / Graphify Lane", context_pack)
            self.assertIn("14_context/repo_knowledge/generated/repo_knowledge_map.md", context_pack)
            self.assertIn("task_bundle_next_milestone.md", context_pack)

        launcher_status = subprocess.run(
            [sys.executable, str(LAUNCHER), "--repo-map", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=60,
        )
        self.assertEqual(launcher_status.returncode, 0, msg=launcher_status.stderr or launcher_status.stdout)
        launcher_payload = json.loads(launcher_status.stdout)
        self.assertEqual(launcher_payload["ok"], True)
        self.assertEqual(launcher_payload["action"], "repo-map")

        launcher_bundle = subprocess.run(
            [sys.executable, str(LAUNCHER), "--repo-bundle", "next-milestone", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=60,
        )
        self.assertEqual(launcher_bundle.returncode, 0, msg=launcher_bundle.stderr or launcher_bundle.stdout)
        bundle_payload = json.loads(launcher_bundle.stdout)
        self.assertEqual(bundle_payload["ok"], True)
        self.assertEqual(bundle_payload["action"], "repo-bundle")

        index_html = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html").read_text(encoding="utf-8")
        server_js = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js").read_text(encoding="utf-8")
        app_js = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "app.js").read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        daily_guide = (REPO_ROOT / "docs" / "DAILY_OPERATOR_GUIDE.md").read_text(encoding="utf-8")
        codex_workflow = (REPO_ROOT / "docs" / "CODEX_ONLY_WORKFLOW.md").read_text(encoding="utf-8")

        self.assertIn("Repo Knowledge / Graphify Lane", index_html)
        self.assertIn("repo knowledge readiness", index_html)
        self.assertIn("task bundles", index_html)
        self.assertIn("latest report index", index_html)
        self.assertIn("Graphify roadmap only", index_html)
        self.assertIn("no external runtime", index_html)
        self.assertIn("no network", index_html)
        self.assertIn("/api/repo-knowledge/status", server_js)
        self.assertIn("/api/repo-knowledge/write", server_js)
        self.assertIn("/api/repo-knowledge/bundle", server_js)
        self.assertIn("/api/repo-knowledge/status", app_js)
        self.assertIn("ghoti_repo_knowledge_map.py", readme)
        self.assertIn("REPO_KNOWLEDGE_MAP_GUIDE.md", readme)
        self.assertIn("GRAPHIFY_REPO_KNOWLEDGE_ROADMAP.md", daily_guide)
        self.assertIn("repo-bundle next-milestone", codex_workflow)
        self.assertNotIn("shell: true", server_js)


if __name__ == "__main__":
    unittest.main()
