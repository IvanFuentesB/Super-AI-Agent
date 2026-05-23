import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
BUILDER = REPO_ROOT / "03_scripts" / "ghoti_context_pack_builder.py"
LAUNCHER = "python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard"
DASHBOARD_URL = "http://127.0.0.1:3210"


class GhotiContextPackBuilderTests(unittest.TestCase):
    def _run_builder(self, output_dir: Path):
        command = [
            sys.executable,
            str(BUILDER),
            "--write",
            "--json",
            "--generated-at",
            "2026-05-22T00:00:00Z",
            "--output-dir",
            str(output_dir),
        ]
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=30,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"builder failed\nstdout={completed.stdout}\nstderr={completed.stderr}",
        )
        return json.loads(completed.stdout)

    def test_builder_writes_compact_context_pack_files(self):
        runtime_tmp = REPO_ROOT / "01_projects" / "dashboard_mvp" / "runtime_data"
        runtime_tmp.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=runtime_tmp) as tmp:
            output_dir = Path(tmp)
            payload = self._run_builder(output_dir)

            expected_files = {
                "ghoti_current_context_pack.md",
                "ghoti_current_context_pack.json",
                "ghoti_codex_next_prompt.md",
                "ghoti_chatgpt_migration_summary.md",
                "ghoti_status_short.md",
            }
            self.assertEqual(payload["ok"], True)
            self.assertEqual(payload["local_only"], True)
            self.assertEqual(payload["external_api_used"], False)
            self.assertEqual(set(payload["paths"].keys()), expected_files)

            for filename in expected_files:
                self.assertTrue((output_dir / filename).exists(), filename)

            pack = (output_dir / "ghoti_current_context_pack.md").read_text(encoding="utf-8")
            self.assertIn(LAUNCHER, pack)
            self.assertIn(DASHBOARD_URL, pack)
            self.assertIn("N+5.5B", pack)
            self.assertIn("N+5.6A", pack)
            self.assertIn("N+5.7A", pack)
            self.assertIn("Hermes WSL: installed", pack)
            self.assertIn("/home/ai_sandbox/.local/bin/hermes", pack)
            self.assertIn("v0.14.0", pack)
            self.assertIn("browser/Playwright: degraded/not claimed", pack)
            self.assertIn("Codex provider in Hermes: pending/not proven", pack)
            self.assertIn("Telegram: manual later/no token", pack)
            self.assertIn("No VPS", pack)
            self.assertIn("local_demo fallback active", pack)
            self.assertIn("Obsidian/local memory: present", pack)
            self.assertIn("UI-TARS: observation-only", pack)
            self.assertIn("No bot/captcha/cloak bypass", pack)
            self.assertIn("No autonomous money/trading/legal actions", pack)

            prompt = (output_dir / "ghoti_codex_next_prompt.md").read_text(encoding="utf-8")
            self.assertIn("Use only repo-contained worktrees", prompt)
            self.assertIn("N+5.7A", prompt)
            self.assertIn("no live providers/tokens", prompt)

            summary = (output_dir / "ghoti_chatgpt_migration_summary.md").read_text(encoding="utf-8")
            self.assertIn("ChatGPT migration summary", summary)
            self.assertIn("local-first supervised", summary)

            status = (output_dir / "ghoti_status_short.md").read_text(encoding="utf-8")
            self.assertLessEqual(len(status), 1000)
            self.assertIn(payload["main_hash"][:12], status)

    def test_generated_context_pack_is_secret_safe(self):
        runtime_tmp = REPO_ROOT / "01_projects" / "dashboard_mvp" / "runtime_data"
        runtime_tmp.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=runtime_tmp) as tmp:
            output_dir = Path(tmp)
            self._run_builder(output_dir)

            forbidden_patterns = [
                r"sk-[A-Za-z0-9_-]{20,}",
                r"ghp_[A-Za-z0-9_]{20,}",
                r"xox[baprs]-[A-Za-z0-9-]{20,}",
                r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY",
                r"TELEGRAM_BOT_TOKEN\s*=\s*[^<\s]",
                r"ANTHROPIC_API_KEY\s*=\s*[^<\s]",
                r"OPENAI_API_KEY\s*=\s*[^<\s]",
            ]
            combined = "\n".join(
                path.read_text(encoding="utf-8")
                for path in output_dir.iterdir()
                if path.is_file()
            )
            for pattern in forbidden_patterns:
                self.assertIsNone(re.search(pattern, combined), pattern)

    def test_dashboard_launcher_and_docs_surface_context_pack(self):
        index_html = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html").read_text(encoding="utf-8")
        server_js = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "server.js").read_text(encoding="utf-8")
        app_js = (REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "app.js").read_text(encoding="utf-8")
        launcher_py = (REPO_ROOT / "03_scripts" / "ghoti_product_launcher.py").read_text(encoding="utf-8")
        daily_guide = (REPO_ROOT / "docs" / "DAILY_OPERATOR_GUIDE.md").read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Local Memory / Context Pack", index_html)
        self.assertIn("ghoti-context-pack-card", index_html)
        self.assertIn("ghoti_context_pack_builder.py --write --json", index_html)
        self.assertIn("/api/local-memory-context-pack/status", server_js)
        self.assertIn("/api/local-memory-context-pack/build", server_js)
        self.assertIn("/api/local-memory-context-pack/status", app_js)
        self.assertIn("--context-pack", launcher_py)
        self.assertNotIn("shell: true", server_js)
        self.assertIn("LOCAL_MEMORY_CONTEXT_PACK_GUIDE.md", daily_guide)
        self.assertIn("LOCAL_MEMORY_CONTEXT_PACK_GUIDE.md", readme)


if __name__ == "__main__":
    unittest.main()
