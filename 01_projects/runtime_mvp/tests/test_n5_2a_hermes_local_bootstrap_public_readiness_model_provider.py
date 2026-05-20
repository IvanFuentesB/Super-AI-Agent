#!/usr/bin/env python3
"""N+5.2A tests for Hermes local bootstrap and public readiness."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
PYTHON = sys.executable


def run_cmd(*args: str, timeout: int = 180) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def load_json(*args: str) -> dict:
    result = run_cmd(*args)
    if result.returncode != 0:
        raise AssertionError(result.stderr + result.stdout)
    return json.loads(result.stdout)


class TestHermesBootstrap(unittest.TestCase):
    def test_status_json_valid_and_local_only(self):
        data = load_json("03_scripts/hermes_local_bootstrap.py", "--status", "--json")
        self.assertTrue(data["ok"])
        manifest = data["manifest"]
        self.assertTrue(manifest["local_only"])
        self.assertFalse(manifest["paid_vps_required"])
        self.assertFalse(manifest["vps_used"])
        self.assertFalse(manifest["secrets_written"])
        self.assertFalse(manifest["live_api_used"])
        self.assertTrue(manifest["telegram_token_required_from_user"])

    def test_check_prereqs_json_valid(self):
        data = load_json("03_scripts/hermes_local_bootstrap.py", "--check-prereqs", "--json")
        self.assertTrue(data["ok"])
        self.assertIn("curl_exe_found", data["prereqs"])
        self.assertIn("wsl_found", data["prereqs"])
        self.assertIn("git_bash_paths", data["prereqs"])

    def test_print_windows_commands_mentions_safe_shells(self):
        result = subprocess.run(
            [PYTHON, "03_scripts/hermes_local_bootstrap.py", "--print-windows-commands"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        text = result.stdout.lower()
        self.assertIn("curl.exe", text)
        self.assertRegex(text, r"wsl|git bash")


class TestPublicReadinessAndModelCouncil(unittest.TestCase):
    def test_public_repo_security_audit(self):
        data = load_json("03_scripts/public_repo_security_audit.py", "--run", "--json")
        self.assertTrue(data["ok"])
        self.assertGreaterEqual(data["total_checks"], 140)
        self.assertIn("safe_to_make_public", data)
        self.assertIn("blocking_findings", data)

    def test_model_council_registry(self):
        data = load_json("03_scripts/model_council_tool_intake.py", "--scan", "--json")
        self.assertTrue(data["ok"])
        manifest = data["manifest"]
        self.assertTrue(manifest["local_only"])
        self.assertFalse(manifest["external_repos_installed"])
        self.assertFalse(manifest["external_repos_executed"])
        self.assertFalse(manifest["runtime_wiring_enabled"])
        self.assertFalse(manifest["bot_detection_bypass_enabled"])
        registry = {item["slug"]: item for item in data["registry"]}
        for slug in [
            "hermes-agent",
            "codex",
            "gemma/ollama",
            "graphify",
            "vercel-labs/agent-browser",
            "browser-harness",
            "chatgpt/openai",
            "claude-code",
            "supabase",
            "vercel",
            "stripe",
        ]:
            self.assertIn(slug, registry)
        self.assertEqual(registry["cloak/browser bot-detection"]["status"], "BLOCKED")


class TestDocsAndPolicy(unittest.TestCase):
    def test_env_example_placeholders_only(self):
        env_path = REPO_ROOT / ".env.example"
        parsed = {}
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                key, value = line.split("=", 1)
                parsed[key] = value
        for key, value in parsed.items():
            self.assertEqual(value, "true" if key == "LOCAL_ONLY" else "")
        self.assertIn("HERMES_TELEGRAM_BOT_TOKEN", parsed)
        self.assertIn("HERMES_TELEGRAM_CHAT_ID", parsed)

    def test_gitignore_and_license(self):
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        for pattern in ["Human Imported Stuff/", "*human*import*stuff*/", "*human*placed*stuff*/", "21_repos/third_party/*"]:
            self.assertIn(pattern, gitignore)
        license_text = (REPO_ROOT / "LICENSE").read_text(encoding="utf-8").lower()
        self.assertIn("all rights reserved", license_text)
        self.assertIn("not open source", license_text)

    def test_required_docs_exist(self):
        for path in [
            "docs/HERMES_LOCAL_INSTALL_AND_PROVIDER_PLAN.md",
            "docs/HERMES_TELEGRAM_MANUAL_SETUP_PLAN.md",
            "docs/LOCAL_FIRST_NO_VPS_AGENT_STRATEGY.md",
            "docs/GITHUB_PROFILE_AND_REPO_UPGRADE_PLAYBOOK.md",
            "docs/REPO_BRANDING_AND_IMAGE_PLAYBOOK.md",
            "docs/CLAUDE_SKILLS_RECOVERY_PLAN.md",
            "docs/AGENT_BROWSER_BROWSER_HARNESS_INTAKE.md",
            "infra/iac_blueprint.yaml",
        ]:
            self.assertTrue((REPO_ROOT / path).exists(), path)

    def test_readme_truth(self):
        text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        lower = text.lower()
        self.assertIn("hermes local bootstrap", lower)
        self.assertIn("no paid vps currently", lower)
        self.assertIn("telegram setup is later/manual", lower)
        self.assertIn("pending / not verified", lower)
        self.assertIn("not open source unless a license change says otherwise", lower)
        self.assertNotRegex(lower, r"hermes fully installed|telegram connected|vps is running|full autonomy")
        self.assertNotRegex(lower, r"ui-tars (can|will|does) (click|type|control)")

    def test_readme_image_links_valid(self):
        text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        links = re.findall(r"!\[[^\]]+\]\((docs/assets/github/[^)]+)\)", text)
        self.assertGreaterEqual(len(links), 3)
        for link in links:
            self.assertTrue((REPO_ROOT / link).exists(), link)

    def test_no_disallowed_literals_or_api_keys(self):
        bad_shell_a = "shell" + ":" + "true"
        bad_shell_b = "shell" + ": " + "true"
        video_a = "yt" + "-" + "dlp"
        video_b = "youtube" + "-" + "dl"
        key_pattern = re.compile(r"(sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})")
        public_files = [
            REPO_ROOT / "README.md",
            REPO_ROOT / "03_scripts" / "hermes_local_bootstrap.py",
            REPO_ROOT / "03_scripts" / "public_repo_security_audit.py",
            REPO_ROOT / "03_scripts" / "model_council_tool_intake.py",
            REPO_ROOT / "docs" / "BLOCKED_UNSAFE_AUTOMATION.md",
        ]
        for path in public_files:
            text = path.read_text(encoding="utf-8")
            lower = text.lower()
            self.assertNotIn(bad_shell_a, lower)
            self.assertNotIn(bad_shell_b, lower)
            self.assertNotIn(video_a, lower)
            self.assertNotIn(video_b, lower)
            self.assertIsNone(key_pattern.search(text))

    def test_branch_commit_attribution_scan(self):
        result = subprocess.run(
            ["git", "log", "--format=%an <%ae>%n%s%n%b", "origin/main..HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        forbidden = re.compile(r"(co-authored-by|claude|codex|anthropic|openai|assistant|\bbot\b)", re.I)
        self.assertIsNone(forbidden.search(result.stdout))


if __name__ == "__main__":
    unittest.main()
