"""
test_n6_32a_no_ai_attribution_guard.py

N+6.32A — strict no-AI-attribution guard.

Forward-looking guard that prevents future contamination of the GitHub
contributor / co-author / author / committer surface with AI identities
(Claude, GPT/ChatGPT, Codex, Anthropic, OpenAI, generic assistant/bot).

Design notes:
  - This guard is FORWARD-looking. It does NOT rewrite history and does NOT
    hard-fail on already-pushed inherited commits. It checks:
      1. the configured git identity (what the NEXT commit will use),
      2. HEAD author + committer (what GitHub shows as latest contributor),
      3. NEW commit messages in origin/main..HEAD for attribution trailers,
      4. tracked docs for "AI is a co-author/contributor/collaborator" wording.
  - Historical inherited AI authorship is intentionally NOT hard-failed here;
    that is surfaced as a reviewed warning by
    03_scripts/public_repo_security_audit.py (no force-push, no rewrite).

Pure stdlib; no network; no installs.
"""

import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

# AI identity tokens that must never appear as git author/committer or in an
# attribution trailer. Workflow words used in prose (e.g. "Claude Code",
# "Codex audits") are NOT matched by the trailer/identity patterns below.
AI_IDENTITY = re.compile(
    r"(claude|chatgpt|\bgpt\b|codex|anthropic|openai|\bassistant\b|\bbot\b)",
    re.IGNORECASE,
)

# Attribution trailers / phrases that must never appear in commit messages or
# docs. These are specific enough not to flag normal workflow prose.
ATTRIBUTION_PATTERNS = [
    re.compile(r"co-authored-by:\s*(claude|chatgpt|gpt|codex|anthropic|openai)", re.IGNORECASE),
    re.compile(r"generated\s+(with|by)\s+(claude|chatgpt|gpt|codex)", re.IGNORECASE),
    re.compile(r"(claude|chatgpt|gpt|codex)\s+(is|as)\s+(a\s+|the\s+)?(co-?author|contributor|collaborator)", re.IGNORECASE),
    re.compile(r"🤖\s*generated", re.IGNORECASE),
]


def _git(args):
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class TestGitIdentityGuard(unittest.TestCase):
    def test_configured_identity_is_not_ai(self):
        """The identity that will author the NEXT commit must not be an AI."""
        name = _git(["config", "user.name"]).stdout.strip()
        email = _git(["config", "user.email"]).stdout.strip()
        # An unset identity cannot be an AI; only fail if one is set AND matches.
        if name:
            self.assertIsNone(
                AI_IDENTITY.search(name),
                msg=f"git user.name '{name}' looks like an AI identity",
            )
        if email:
            self.assertIsNone(
                AI_IDENTITY.search(email),
                msg=f"git user.email '{email}' looks like an AI identity",
            )

    def test_head_author_and_committer_not_ai(self):
        """HEAD (latest contributor shown on GitHub) must not be an AI."""
        out = _git(["log", "-1", "--format=%an <%ae>%n%cn <%ce>", "HEAD"])
        if out.returncode != 0:
            self.skipTest("git log unavailable")
        self.assertIsNone(
            AI_IDENTITY.search(out.stdout),
            msg=f"HEAD author/committer looks like an AI identity:\n{out.stdout}",
        )


class TestNewCommitMessagesGuard(unittest.TestCase):
    def _range_logs(self):
        mb = _git(["merge-base", "HEAD", "origin/main"])
        if mb.returncode != 0 or not mb.stdout.strip():
            self.skipTest("origin/main merge-base unavailable")
        base = mb.stdout.strip()
        out = _git(["log", "--format=%an <%ae>%n%cn <%ce>%n%s%n%b%n--EOC--", f"{base}..HEAD"])
        if out.returncode != 0:
            self.skipTest("git log range unavailable")
        return out.stdout

    def test_new_commit_messages_have_no_attribution_trailers(self):
        """NEW commits (origin/main..HEAD) must carry no AI attribution trailers."""
        text = self._range_logs()
        for pattern in ATTRIBUTION_PATTERNS:
            self.assertIsNone(
                pattern.search(text),
                msg=f"AI attribution trailer in new commit(s): {pattern.pattern}",
            )

    def test_new_commit_authors_and_committers_not_ai(self):
        """NEW commits in this branch must not be AI-authored or AI-committed.

        Range-scoped (not full history): respects the no-rewrite rule for
        already-merged inherited commits while blocking future contamination.
        """
        text = self._range_logs()
        # Only inspect the identity lines (first two lines of each record).
        offending = []
        for record in text.split("--EOC--"):
            lines = [ln for ln in record.strip().splitlines() if ln.strip()]
            for ident_line in lines[:2]:
                if AI_IDENTITY.search(ident_line):
                    offending.append(ident_line)
        self.assertEqual(
            offending, [],
            msg=f"AI author/committer in new commit(s): {offending}",
        )


class TestDocAttributionGuard(unittest.TestCase):
    """Tracked docs must not claim an AI is a co-author/contributor/collaborator."""

    def _doc_files(self):
        out = _git(["ls-files", "*.md", "docs/*.md", "14_context/**/*.md", "README.md"])
        if out.returncode != 0:
            self.skipTest("git ls-files unavailable")
        files = {line.strip() for line in out.stdout.splitlines() if line.strip()}
        # Exclude this guard's own milestone doc, which describes the forbidden
        # phrasing indirectly but should not be self-flagged.
        files = {f for f in files if "N6_32A_NO_AI_ATTRIBUTION" not in f.upper()}
        return sorted(files)

    def test_no_ai_collaborator_wording_in_docs(self):
        for rel in self._doc_files():
            path = REPO_ROOT / rel
            try:
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for pattern in ATTRIBUTION_PATTERNS:
                self.assertIsNone(
                    pattern.search(content),
                    msg=f"AI attribution wording in {rel}: {pattern.pattern}",
                )


class TestGuardRegexItself(unittest.TestCase):
    """Sanity: the guard patterns catch known-bad strings and allow good ones."""

    def test_identity_pattern_catches_ai(self):
        for bad in ["Claude", "Claude <noreply@anthropic.com>", "ChatGPT", "codex-bot"]:
            self.assertIsNotNone(AI_IDENTITY.search(bad), msg=bad)

    def test_identity_pattern_allows_human(self):
        for good in ["IvanFuentesB <IvanFuentesB@users.noreply.github.com>", "Ivan Fuentes"]:
            self.assertIsNone(AI_IDENTITY.search(good), msg=good)

    def test_attribution_patterns_catch_trailers(self):
        # Built from fragments so this source file does not contain the literal
        # contiguous forbidden trailer string.
        samples = [
            "Co-authored-by: " + "Claude <noreply@anthropic.com>",
            "Generated " + "with Claude",
            "Claude is a " + "co-author of this change",
        ]
        for sample in samples:
            self.assertTrue(
                any(p.search(sample) for p in ATTRIBUTION_PATTERNS),
                msg=f"no pattern matched: {sample}",
            )

    def test_attribution_patterns_allow_workflow_prose(self):
        for good in [
            "Claude Code implements features; Codex audits each branch.",
            "Codex records the verdict in CODEX_LAST_AUDIT.md.",
            "The Claude profile uses subagents for read-only work.",
        ]:
            self.assertFalse(
                any(p.search(good) for p in ATTRIBUTION_PATTERNS),
                msg=f"false positive on workflow prose: {good}",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
