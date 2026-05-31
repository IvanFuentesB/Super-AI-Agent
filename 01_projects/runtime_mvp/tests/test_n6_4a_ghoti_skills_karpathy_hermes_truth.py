import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

TRUTH = REPO_ROOT / "14_context" / "ghoti_current_truth.md"
HERMES_DOC = REPO_ROOT / "docs" / "HERMES_LOCAL_SETUP_CURRENT_TRUTH.md"
WORKFLOW_DOC = REPO_ROOT / "docs" / "GHOTI_SKILLS_AND_AGENT_WORKFLOW.md"
CLAUDE_POLICY = REPO_ROOT / "docs" / "CLAUDE_CODE_SKILLS_POLICY.md"
CODEX_WORKFLOW = REPO_ROOT / "docs" / "CODEX_AUDIT_WORKFLOW.md"
SKILL_REGISTRY = REPO_ROOT / "14_context" / "skills" / "ghoti_skill_registry.md"
KARPATHY_INTAKE = REPO_ROOT / "14_context" / "skills" / "karpathy_guidelines_intake.md"
SKILL_LOG = REPO_ROOT / "14_context" / "skills" / "claude_code_skill_install_log.md"
CODEX_RULES = REPO_ROOT / "14_context" / "skills" / "codex_working_rules.md"
BACKLOG = (
    REPO_ROOT
    / "14_context"
    / "agent_handoff_vault"
    / "05_Backlog"
    / "dashboard_performance_and_local_analytics.md"
)
VAULT_RULES = REPO_ROOT / "14_context" / "agent_handoff_vault" / "AGENT_RULES.md"
VAULT_TASK = (
    REPO_ROOT / "14_context" / "agent_handoff_vault" / "02_Agent_Handoffs" / "CURRENT_TASK.md"
)
VAULT_START = REPO_ROOT / "14_context" / "agent_handoff_vault" / "00_Inbox" / "START_HERE.md"

ALL_FILES = [
    TRUTH,
    HERMES_DOC,
    WORKFLOW_DOC,
    CLAUDE_POLICY,
    CODEX_WORKFLOW,
    SKILL_REGISTRY,
    KARPATHY_INTAKE,
    SKILL_LOG,
    CODEX_RULES,
    BACKLOG,
    VAULT_RULES,
    VAULT_TASK,
    VAULT_START,
]

# Distinctive affirmative false-claim phrases that must never appear in the
# registered truth/skills docs. These assert the milestone does not overclaim.
FALSE_CLAIMS = [
    "telegram is enabled for ghoti",
    "browser is enabled for ghoti",
    "computer-use is enabled for ghoti",
    "browser click and type is enabled",
    "ghoti is fully autonomous",
    "claude code is fully wired into hermes",
    "codex is fully wired into hermes",
    "production analytics is implemented and live",
    "external telemetry is enabled by default",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class GhotiTruthAndSkillFilesTests(unittest.TestCase):
    def test_all_required_files_exist(self):
        for path in ALL_FILES:
            self.assertTrue(path.is_file(), msg=f"missing required file: {path}")

    def test_truth_registers_agent_roles_and_hermes_setup(self):
        text = read(TRUTH)
        for needle in [
            "ChatGPT",
            "Hermes",
            "Obsidian",
            "Claude Code",
            "Codex",
            "gemma3:4b",
            "llama3.1:8b",
            "Git",
            "Human",
            "v0.14.0",
            "http://127.0.0.1:11434/v1",
            "ai_sandbox",
            "WSL",
            "qwen was removed",
            r"14_context\agent_handoff_vault",
        ]:
            self.assertIn(needle, text, msg=f"truth missing: {needle!r}")

    def test_truth_states_what_is_not_enabled(self):
        lowered = read(TRUTH).lower()
        self.assertIn("telegram is not configured", lowered)
        self.assertIn("not approved and not enabled", lowered)
        self.assertIn("supervised, not autonomous", lowered)
        self.assertIn("manual", lowered)

    def test_no_overclaims_across_truth_and_skill_docs(self):
        scanned = [
            TRUTH,
            HERMES_DOC,
            WORKFLOW_DOC,
            CLAUDE_POLICY,
            CODEX_WORKFLOW,
            SKILL_REGISTRY,
            KARPATHY_INTAKE,
            SKILL_LOG,
            CODEX_RULES,
            BACKLOG,
        ]
        combined = "\n".join(read(p).lower() for p in scanned)
        for claim in FALSE_CLAIMS:
            self.assertNotIn(claim, combined, msg=f"overclaim found: {claim!r}")

    def test_hermes_doc_is_factual_and_local_only(self):
        text = read(HERMES_DOC)
        for needle in [
            "v0.14.0",
            "llama3.1:8b",
            "gemma3:4b",
            "http://127.0.0.1:11434/v1",
            "loopback",
            "qwen was removed",
        ]:
            self.assertIn(needle, text, msg=f"hermes doc missing: {needle!r}")
        lowered = text.lower()
        self.assertIn("telegram", lowered)
        self.assertIn("not configured", lowered)
        self.assertIn("not approved and not enabled", lowered)

    def test_skill_registry_marks_unsafe_tools_not_enabled(self):
        lowered = read(SKILL_REGISTRY).lower()
        for tool in ["browser", "computer-use", "mcp"]:
            self.assertIn(tool, lowered, msg=f"registry missing tool row: {tool!r}")
        self.assertIn("not enabled", lowered)
        self.assertIn("guidance-only", lowered)
        self.assertIn("manual", lowered)
        for skill in ["goal", "ultraplan", "ghoti-status", "prompt-bus", "karpathy-guidelines"]:
            self.assertIn(skill, lowered, msg=f"registry missing skill: {skill!r}")

    def test_karpathy_intake_records_four_principles(self):
        text = read(KARPATHY_INTAKE)
        for principle in [
            "Think Before Coding",
            "Simplicity First",
            "Surgical Changes",
            "Goal-Driven Execution",
        ]:
            self.assertIn(principle, text, msg=f"karpathy intake missing: {principle!r}")
        self.assertIn("guidance-only", read(KARPATHY_INTAKE).lower())

    def test_skill_install_log_has_no_runtime_wired_skill(self):
        lowered = read(SKILL_LOG).lower()
        self.assertIn("guidance-only", lowered)
        # The status key may define "runtime-wired", but the log must assert none
        # are wired in today.
        self.assertIn("no entry above is runtime-wired", lowered)

    def test_codex_rules_are_audit_only(self):
        text = read(CODEX_RULES)
        lowered = text.lower()
        self.assertIn("does not implement", lowered)
        self.assertIn("does not merge", lowered)
        for verdict in ["CLEAN PASS", "CONDITIONAL PASS", "BLOCKED_VALIDATION"]:
            self.assertIn(verdict, text, msg=f"codex rules missing verdict: {verdict!r}")

    def test_codex_audit_workflow_defines_checks_and_verdicts(self):
        text = read(CODEX_WORKFLOW)
        for verdict in ["CLEAN PASS", "CONDITIONAL PASS", "BLOCKED_VALIDATION"]:
            self.assertIn(verdict, text, msg=f"codex workflow missing verdict: {verdict!r}")
        lowered = text.lower()
        self.assertIn("does not merge", lowered)
        self.assertIn("overclaim", lowered)

    def test_backlog_note_is_local_first_and_not_built(self):
        text = read(BACKLOG)
        lowered = text.lower()
        self.assertIn("backlog only", lowered)
        self.assertIn("not built", lowered)
        self.assertIn("no external tracking by default", lowered)
        self.assertIn("no user secrets", lowered)
        self.assertIn("no invasive telemetry", lowered)
        self.assertIn("explicit human approval", lowered)
        for metric in [
            "transition",
            "feature usage",
            "command usage",
            "task completion",
            "task failure",
            "latency",
            "error counts",
            "reliability",
        ]:
            self.assertIn(metric, lowered, msg=f"backlog missing metric: {metric!r}")

    def test_vault_was_imported(self):
        self.assertTrue(VAULT_RULES.is_file())
        self.assertTrue(VAULT_TASK.is_file())
        self.assertTrue(VAULT_START.is_file())
        self.assertIn("Claude Code", read(VAULT_RULES))


if __name__ == "__main__":
    unittest.main()
