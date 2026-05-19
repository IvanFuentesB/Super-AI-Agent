#!/usr/bin/env python3
"""N+5.1A tests: public GitHub readiness + image-backed presentation.

Covers:
- security audit CLI JSON contracts and 100+ checks
- proprietary/all-rights-reserved license posture
- README public-facing safety truth and image/diagram presentation
- .env.example placeholders only
- .gitignore protections for secrets, runtime output, third-party sandboxes, and raw imports
- required public-release docs
- curated image assets only under docs/assets/github
- no newly introduced unsafe shell or public-release blocker hiding
"""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
SCRIPT = REPO_ROOT / "03_scripts" / "public_repo_security_audit.py"
PYTHON = sys.executable

README = REPO_ROOT / "README.md"
LICENSE = REPO_ROOT / "LICENSE"
GITIGNORE = REPO_ROOT / ".gitignore"
ENV_EXAMPLE = REPO_ROOT / ".env.example"
SECURITY = REPO_ROOT / "SECURITY.md"
CONTRIBUTING = REPO_ROOT / "CONTRIBUTING.md"
DOCS = REPO_ROOT / "docs"
ASSETS = DOCS / "assets" / "github"
REPORT = REPO_ROOT / "14_context" / "codex_n5_1a_public_github_readiness_image_backed_presentation.md"

REQUIRED_DOCS = [
    DOCS / "PUBLIC_RELEASE_SECURITY_CHECKLIST.md",
    DOCS / "HUMAN_IMPORTED_STUFF_POLICY.md",
    DOCS / "DIAGRAM_UPDATE_RULE.md",
    DOCS / "FUTURE_MILESTONE_DOCS_CHECKLIST.md",
    DOCS / "GITHUB_PRESENTATION_CHECKLIST.md",
    ASSETS / "README.md",
]

EXPECTED_ENV_KEYS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "GITHUB_TOKEN",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "FIREBASE_API_KEY",
    "DISCORD_TOKEN",
    "TELEGRAM_BOT_TOKEN",
    "LOCAL_ONLY",
]


def run_audit(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(SCRIPT)] + list(args),
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=180,
    )


class TestPublicRepoSecurityAuditCli(unittest.TestCase):
    def test_status_json_valid(self):
        result = run_audit("--status", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("audit"), "public_repo_security_audit")
        self.assertGreaterEqual(data.get("total_checks", 0), 100)

    def test_run_json_valid_and_has_public_decision(self):
        result = run_audit("--run", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data.get("ok"))
        self.assertGreaterEqual(data.get("total_checks", 0), 100)
        self.assertIn("safe_to_make_public", data)
        self.assertIn("human_review_required", data)
        self.assertIn("blocking_findings", data)
        self.assertIn("warning_checks", data)

    def test_write_report_and_latest_json(self):
        written = json.loads(run_audit("--write-report", "--json").stdout)
        self.assertTrue(written.get("ok"))
        self.assertTrue((REPO_ROOT / written["report_dir"]).exists())
        latest = json.loads(run_audit("--latest", "--json").stdout)
        self.assertTrue(latest.get("ok"))
        self.assertEqual(latest.get("report_dir"), written.get("report_dir"))
        self.assertGreaterEqual(latest.get("total_checks", 0), 100)


class TestPublicRepoPresentationFiles(unittest.TestCase):
    def test_required_files_exist(self):
        for path in [README, LICENSE, GITIGNORE, ENV_EXAMPLE, SECURITY, CONTRIBUTING, REPORT] + REQUIRED_DOCS:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), f"missing {path}")

    def test_license_is_proprietary_not_open_source(self):
        text = LICENSE.read_text(encoding="utf-8").lower()
        self.assertIn("all rights reserved", text)
        self.assertIn("not open source", text)
        self.assertIn("public visibility does not equal open-source permission", text)
        for forbidden in ["mit license", "apache license", "gnu general public license", "bsd license"]:
            self.assertNotIn(forbidden, text)

    def test_env_example_placeholders_only(self):
        lines = [
            line.strip()
            for line in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        parsed = dict(line.split("=", 1) for line in lines)
        self.assertEqual(sorted(parsed.keys()), sorted(EXPECTED_ENV_KEYS))
        for key, value in parsed.items():
            if key == "LOCAL_ONLY":
                self.assertEqual(value, "true")
            else:
                self.assertEqual(value, "")

    def test_gitignore_has_public_release_protections(self):
        text = GITIGNORE.read_text(encoding="utf-8")
        required = [
            ".env",
            ".env.*",
            "!.env.example",
            "*.pem",
            "*.key",
            "*.p12",
            "*.pfx",
            "*.crt",
            "*.cer",
            "*.sqlite",
            "*.db",
            "*.log",
            "logs/",
            "05_logs/tmp_*",
            "node_modules/",
            ".venv/",
            "venv/",
            "__pycache__/",
            ".pytest_cache/",
            ".cache/",
            "runtime_data/",
            "output/",
            "*.tmp",
            "*.bak",
            "*.zip",
            "*.7z",
            "*.rar",
            "*.mp4",
            "*.mov",
            "*.webm",
            "21_repos/third_party/*",
            "human imported stuff/",
            "Human Imported Stuff/",
            "human_imported_stuff/",
            "Human_Imported_Stuff/",
            "Human Placed Stuff/",
            "*human*import*stuff*/",
            "*human*placed*stuff*/",
        ]
        for pattern in required:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_readme_public_truth(self):
        text = README.read_text(encoding="utf-8")
        lower = text.lower()
        self.assertIn("# ghoti", lower)
        self.assertIn("source visible for demonstration and review. not open source unless a license change says otherwise.", lower)
        self.assertIn("python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard", text)
        self.assertIn("http://127.0.0.1:3210", text)
        self.assertIn("ui-tars", lower)
        self.assertIn("observation only", lower)
        self.assertIn("no click/type/control", lower)
        self.assertIn("human imported stuff", lower)
        self.assertIn("public repo security", lower)
        self.assertGreaterEqual(text.count("```mermaid"), 8)
        self.assertNotRegex(lower, r"full autonomy|live account automation|autonomous posting|autonomous trading")

    def test_readme_image_links_are_repo_local(self):
        text = README.read_text(encoding="utf-8")
        links = re.findall(r"!\[[^\]]+\]\((docs/assets/github/[^)]+)\)", text)
        self.assertGreaterEqual(len(links), 5)
        for link in links:
            with self.subTest(link=link):
                path = REPO_ROOT / link
                self.assertTrue(path.exists(), f"image link missing: {link}")
                self.assertEqual(path.parent, ASSETS)
                self.assertIn(path.suffix.lower(), [".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"])

    def test_safe_images_only_under_assets(self):
        asset_files = [p for p in ASSETS.iterdir() if p.is_file() and p.name != "README.md"]
        self.assertGreaterEqual(len(asset_files), 5)
        for path in asset_files:
            with self.subTest(path=path.name):
                self.assertEqual(path.parent, ASSETS)
                self.assertRegex(path.name, r"^[a-z0-9][a-z0-9._-]*$")
                self.assertNotRegex(path.name.lower(), r"secret|token|key|password|email|cv|resume|account")


class TestPublicReleaseSafetyNoNewUnsafeClaims(unittest.TestCase):
    def test_new_public_files_do_not_introduce_shell_true_or_download_wrappers(self):
        public_files = [
            README,
            LICENSE,
            SECURITY,
            CONTRIBUTING,
            REPORT,
            *REQUIRED_DOCS,
            SCRIPT,
        ]
        for path in public_files:
            text = path.read_text(encoding="utf-8").lower()
            with self.subTest(path=path.name):
                self.assertNotIn("shell:true", text)
                self.assertNotIn("shell: true", text)
                self.assertNotIn("yt-dlp", text)
                self.assertNotIn("youtube-dl", text)

    def test_no_real_looking_api_keys_in_public_readiness_files(self):
        pattern = re.compile(
            r"(sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}|AKIA[0-9A-Z]{16})"
        )
        public_files = [
            README,
            LICENSE,
            SECURITY,
            CONTRIBUTING,
            ENV_EXAMPLE,
            REPORT,
            *REQUIRED_DOCS,
            SCRIPT,
        ]
        for path in public_files:
            with self.subTest(path=path.name):
                self.assertIsNone(pattern.search(path.read_text(encoding="utf-8")))

    def test_report_does_not_hide_public_release_decision(self):
        text = REPORT.read_text(encoding="utf-8").lower()
        self.assertIn("safe_to_make_public", text)
        self.assertIn("blockers", text)
        self.assertIn("warnings", text)
        self.assertIn("human review", text)


if __name__ == "__main__":
    unittest.main()
