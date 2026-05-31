import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

DOCS = REPO_ROOT / "docs"
SKILLS = REPO_ROOT / "14_context" / "skills"
VAULT = REPO_ROOT / "14_context" / "agent_handoff_vault"

ROADMAP = DOCS / "GHOTI_COMMAND_CENTER_ROADMAP.md"
WRAPPERS_SPEC = DOCS / "GHOTI_N6_6_HERMES_ROUTER_WRAPPERS_SPEC.md"
INTAKE_SPEC = DOCS / "GHOTI_N6_7_TOOL_REPO_INTAKE_SPEC.md"
ANALYTICS_SPEC = DOCS / "GHOTI_N6_8_COMMAND_CENTER_ANALYTICS_SPEC.md"
ORCH_POLICY = DOCS / "GHOTI_N6_9_MULTI_AGENT_ORCHESTRATION_POLICY.md"
WRAPPER_POLICY = SKILLS / "hermes_router_wrapper_policy.md"
BACKLOG = VAULT / "05_Backlog" / "n6_6_7_8_9_command_center_backlog.md"
NEXT_CLAUDE = VAULT / "02_Agent_Handoffs" / "NEXT_CLAUDE_TASK.md"
NEXT_CODEX = VAULT / "02_Agent_Handoffs" / "NEXT_CODEX_AUDIT_PROMPT.md"
ARCH_SUMMARY = VAULT / "04_Logs" / "CLAUDE_COMMAND_CENTER_ARCHITECTURE_SUMMARY.md"

ALL_FILES = [
    ROADMAP,
    WRAPPERS_SPEC,
    INTAKE_SPEC,
    ANALYTICS_SPEC,
    ORCH_POLICY,
    WRAPPER_POLICY,
    BACKLOG,
    NEXT_CLAUDE,
    NEXT_CODEX,
    ARCH_SUMMARY,
]

# Per-file guardrail phrases that must appear (lowercased match). These assert the
# specs carry the safety language and the agreed roles.
REQUIRED = {
    ROADMAP: [
        "chatgpt",
        "hermes is the local coordinator, not the main brain",
        "approved wrappers only",
        "never run arbitrary commands",
        "no secrets",
        "no telegram",
        "no browser/computer-use",
        "no mcp installed",
        "no blind installs",
        "local-first",
    ],
    WRAPPERS_SPEC: [
        "approved wrappers only",
        "never run arbitrary commands",
        "no secrets",
        "no telegram",
        "no browser/computer-use",
        "no mcp installed",
        "dry-run",
    ],
    INTAKE_SPEC: [
        "no blind installs",
        "no secrets",
        "21_repos/third_party",
        "markitdown",
        "understand-anything",
    ],
    ANALYTICS_SPEC: [
        "local-first",
        "no secrets",
        "local-only by default",
        "no external telemetry",
    ],
    ORCH_POLICY: [
        "chatgpt is the main brain",
        "hermes is the local coordinator",
        "no secrets",
        "human_decision",
        "no browser/computer-use",
        "no mcp installed",
    ],
    WRAPPER_POLICY: [
        "guidance-only",
        "approved wrappers only",
        "never run arbitrary commands",
        "no secrets",
        "no telegram",
        "no browser/computer-use",
        "no mcp installed",
    ],
    BACKLOG: [
        "backlog only",
        "no blind installs",
        "local-first",
        "no secrets",
        "no mcp installed",
    ],
    NEXT_CLAUDE: [
        "n+6.6a",
        "approved wrappers only",
        "never run arbitrary commands",
    ],
    NEXT_CODEX: [
        "does not implement",
        "does not merge",
        "clean pass",
        "conditional pass",
        "blocked_validation",
    ],
    ARCH_SUMMARY: [
        "chatgpt thinks",
        "approved wrappers only",
        "never run arbitrary commands",
        "no blind installs",
        "local-first",
    ],
}

# Distinctive affirmative overclaims that must never appear in any planning doc.
FALSE_CLAIMS = [
    "telegram is enabled for ghoti",
    "browser is enabled for ghoti",
    "computer-use is enabled for ghoti",
    "browser click and type is enabled",
    "ghoti is fully autonomous",
    "wrappers run arbitrary commands",
    "agents are launched automatically",
    "mcp is enabled for ghoti",
    "analytics uses external telemetry",
    "blind installs are allowed",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def norm(text: str) -> str:
    """Lowercase and collapse all whitespace so a phrase still matches when the
    Markdown source wrapped it across lines."""
    return " ".join(text.lower().split())


class CommandCenterPlanDocsTests(unittest.TestCase):
    def test_all_planning_files_exist(self):
        for path in ALL_FILES:
            self.assertTrue(path.is_file(), msg=f"missing planning file: {path}")

    def test_required_phrases_present(self):
        for path, needles in REQUIRED.items():
            normalized = norm(read(path))
            for needle in needles:
                self.assertIn(needle, normalized, msg=f"{path.name} missing: {needle!r}")

    def test_no_overclaims_across_plan_docs(self):
        combined = "\n".join(read(p).lower() for p in ALL_FILES)
        for claim in FALSE_CLAIMS:
            self.assertNotIn(claim, combined, msg=f"overclaim found: {claim!r}")

    def test_no_secret_patterns(self):
        combined = "\n".join(read(p) for p in ALL_FILES)
        self.assertNotRegex(combined, r"sk-[A-Za-z0-9_-]{20,}")
        self.assertNotRegex(combined, r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY")

    def test_roadmap_lists_phase_sequence(self):
        lowered = read(ROADMAP).lower()
        for phase in ["n+6.6a", "n+6.6b", "n+6.7a", "n+6.8a", "n+6.9a"]:
            self.assertIn(phase, lowered, msg=f"roadmap missing phase: {phase!r}")


if __name__ == "__main__":
    unittest.main()
