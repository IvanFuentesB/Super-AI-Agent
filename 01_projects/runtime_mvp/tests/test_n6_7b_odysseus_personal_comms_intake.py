"""Tests for N+6.7B - Odysseus Feature Intake + Personal Communications Roadmap.

These tests lock the safety + contract behavior of the Odysseus / personal-comms
intake so it cannot silently regress. They assert that (1) all seven intake files
exist and the additions JSON is valid, (2) Odysseus and the other required modules
appear and every module is candidate_only - never installed, never runtime_wired,
(3) the email and WhatsApp modules are draft-only with auto-send forbidden, no
account login, and no stored credentials, (4) the 'thinks like me' module never
impersonates without approval and requires human approval for outbound, (5) the AI
video module is local-first with no copyrighted scraping and no automated posting,
(6) the document editor / model cookbook / AI council / deep research modules are
included, and (7) no live browser/computer-use/MCP/Telegram capability is enabled,
with no overclaim and no secret pattern present.
"""

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

TOOL_INTAKE = REPO_ROOT / "14_context" / "tool_intake"
ODYSSEUS = TOOL_INTAKE / "odysseus_feature_intake.md"
COMMS = TOOL_INTAKE / "personal_comms_agent_roadmap.md"
COUNCIL = TOOL_INTAKE / "ai_council_and_model_cookbook_roadmap.md"
ADDITIONS = TOOL_INTAKE / "tool_candidate_registry_additions_n6_7b.json"
DOC = REPO_ROOT / "docs" / "GHOTI_N6_7B_ODYSSEUS_PERSONAL_COMMS_INTAKE.md"
TEST = Path(__file__).resolve()
REPORT = REPO_ROOT / "14_context" / "claude_n6_7b_odysseus_personal_comms_intake.md"

ALL_FILES = [ODYSSEUS, COMMS, COUNCIL, ADDITIONS, DOC, TEST, REPORT]
MARKDOWN_DOCS = [ODYSSEUS, COMMS, COUNCIL, DOC, REPORT]
SECRET_SCAN_FILES = [ODYSSEUS, COMMS, COUNCIL, DOC, REPORT, ADDITIONS]

# Required modules, matched as case-insensitive substrings of module names.
REQUIRED_MODULES = [
    "Odysseus",
    "AI Council",
    "Model Cookbook",
    "Deep Research",
    "Document Editor",
    "Email Triage",
    "WhatsApp",
    "Calendar",
    "Personal Style Memory",
    "AI Video",
]

# Module fields every module must carry (non-empty).
REQUIRED_STR_FIELDS = [
    "value",
    "risk",
    "local_first_path",
    "external_service_path",
    "first_safe_test",
    "implementation_phase",
]
REQUIRED_LIST_FIELDS = ["stop_conditions", "allowed_now", "forbidden_now"]

# Distinctive affirmative overclaims. Phrased so none can be a substring of a
# truthful *negated* sentence (e.g. "Odysseus is not cloned, installed, or run").
FALSE_CLAIMS = [
    "odysseus is installed in ghoti",
    "odysseus was cloned",
    "odysseus is running in ghoti",
    "auto-send is enabled",
    "auto-reply is enabled",
    "messages are sent automatically",
    "credentials are stored in the repo",
    "email login is enabled",
    "whatsapp login is enabled",
    "telegram is enabled for ghoti",
    "mcp is enabled for ghoti",
    "browser-use is enabled for ghoti",
    "computer-use is enabled for ghoti",
]


def read(path):
    return path.read_text(encoding="utf-8")


def norm(text):
    """Lowercase + collapse whitespace so a phrase still matches across wraps."""
    return " ".join(text.lower().split())


def load_additions():
    return json.loads(read(ADDITIONS))


def modules():
    return load_additions()["modules"]


def find_module(needle):
    low = needle.lower()
    for mod in modules():
        if low in mod["name"].lower():
            return mod
    return None


class OdysseusPersonalCommsIntakeTests(unittest.TestCase):
    def test_all_files_exist(self):
        for path in ALL_FILES:
            self.assertTrue(path.is_file(), msg=f"missing file: {path}")

    def test_additions_is_valid_json_with_modules(self):
        data = load_additions()
        self.assertEqual(data.get("milestone"), "N+6.7B")
        self.assertIsInstance(data.get("modules"), list)
        self.assertGreaterEqual(len(data["modules"]), 10)
        self.assertIn("global_safety", data)

    def test_required_modules_present(self):
        names = [m["name"].lower() for m in modules()]
        for needle in REQUIRED_MODULES:
            self.assertTrue(
                any(needle.lower() in name for name in names),
                msg=f"missing required module: {needle!r}",
            )

    def test_odysseus_module_is_candidate_only(self):
        mod = find_module("Odysseus")
        self.assertIsNotNone(mod, msg="Odysseus module not found")
        self.assertEqual(mod["status"], "candidate_only")
        self.assertFalse(mod["installed"])
        self.assertFalse(mod["runtime_wired"])

    def test_all_modules_candidate_only_not_installed_not_wired(self):
        for mod in modules():
            name = mod["name"]
            self.assertEqual(
                mod["status"], "candidate_only", msg=f"{name}: must be candidate_only"
            )
            self.assertIs(mod["installed"], False, msg=f"{name}: must not be installed")
            self.assertIs(
                mod["runtime_wired"], False, msg=f"{name}: must not be runtime_wired"
            )

    def test_every_module_has_required_fields(self):
        for mod in modules():
            name = mod["name"]
            for field in REQUIRED_STR_FIELDS:
                self.assertIsInstance(mod.get(field), str, msg=f"{name}: {field}")
                self.assertTrue(mod.get(field, "").strip(), msg=f"{name}: empty {field}")
            for field in REQUIRED_LIST_FIELDS:
                self.assertIsInstance(mod.get(field), list, msg=f"{name}: {field}")
                self.assertTrue(mod.get(field), msg=f"{name}: empty {field}")

    def test_email_and_whatsapp_are_draft_only(self):
        for needle in ["Email Triage", "WhatsApp"]:
            mod = find_module(needle)
            self.assertIsNotNone(mod, msg=f"{needle} module not found")
            self.assertIs(mod.get("draft_only"), True, msg=f"{needle}: draft_only must be true")
            self.assertIs(mod.get("auto_send"), False, msg=f"{needle}: auto_send must be false")
            self.assertIs(
                mod.get("credentials_stored"), False, msg=f"{needle}: credentials_stored must be false"
            )
            self.assertIs(mod.get("mass_reply"), False, msg=f"{needle}: mass_reply must be false")
            forbidden = norm(" ".join(mod["forbidden_now"]))
            self.assertIn("send", forbidden, msg=f"{needle}: must forbid sending")
            self.assertIn("login", forbidden, msg=f"{needle}: must forbid account login")

    def test_auto_send_is_forbidden_globally(self):
        gs = load_additions()["global_safety"]
        self.assertFalse(gs["auto_send_enabled"], msg="auto_send must be globally disabled")
        self.assertFalse(gs["email_login"], msg="email_login must be disabled")
        self.assertFalse(gs["whatsapp_login"], msg="whatsapp_login must be disabled")

    def test_credentials_and_secrets_forbidden(self):
        gs = load_additions()["global_safety"]
        self.assertFalse(gs["secrets_stored"], msg="secrets_stored must be false")
        self.assertFalse(gs["live_account_action"], msg="live_account_action must be false")
        comms = norm(read(COMMS))
        self.assertIn("credentials", comms)
        self.assertIn("never stored", comms)

    def test_no_runtime_wiring_anywhere(self):
        gs = load_additions()["global_safety"]
        self.assertFalse(gs["runtime_wired"], msg="global runtime_wired must be false")
        self.assertFalse(any(m["runtime_wired"] for m in modules()))

    def test_no_install_or_clone(self):
        gs = load_additions()["global_safety"]
        self.assertFalse(gs["external_repo_cloned"], msg="no external repo may be cloned")
        self.assertFalse(gs["installs_performed"], msg="no install may be performed")
        self.assertFalse(gs["external_code_executed"], msg="no external code may run")

    def test_thinks_like_me_rules(self):
        mod = find_module("Personal Style Memory")
        self.assertIsNotNone(mod, msg="Personal Style Memory module not found")
        self.assertIs(mod.get("impersonation_without_approval"), False)
        self.assertIs(mod.get("outbound_requires_human_approval"), True)
        self.assertIs(mod.get("memory_editable"), True)
        self.assertIs(mod.get("memory_deletable"), True)
        self.assertIs(mod.get("sensitive_profiling"), False)

    def test_ai_video_rules(self):
        mod = find_module("AI Video")
        self.assertIsNotNone(mod, msg="AI Video module not found")
        self.assertIs(mod.get("local_pipeline_first"), True)
        self.assertIs(mod.get("copyrighted_scraping"), False)
        self.assertIs(mod.get("automated_posting"), False)
        self.assertIs(mod.get("approved_assets_only"), True)
        self.assertIs(mod.get("fake_engagement"), False)

    def test_no_live_capabilities_enabled(self):
        gs = load_additions()["global_safety"]
        for flag in [
            "telegram_enabled",
            "mcp_enabled",
            "browser_use_enabled",
            "computer_use_enabled",
            "social_posting_enabled",
        ]:
            self.assertFalse(gs[flag], msg=f"{flag} must be false")

    def test_doc_states_safety_posture(self):
        doc = norm(read(DOC))
        for needle in [
            "candidate_only",
            "draft-only",
            "no auto-send",
            "not installed",
            "not cloned",
            "mcp",
            "browser",
            "computer-use",
            "not enabled",
        ]:
            self.assertIn(needle, doc, msg=f"doc missing: {needle!r}")

    def test_odysseus_doc_documents_features_and_warnings(self):
        text = norm(read(ODYSSEUS))
        for needle in [
            "email triage",
            "deep research",
            "document editor",
            "candidate_only",
            "not cloned",
        ]:
            self.assertIn(needle, text, msg=f"odysseus intake missing: {needle!r}")
        # Odysseus' own security warnings must be carried over.
        self.assertIn("auth", text)
        self.assertTrue("https" in text or "public exposure" in text)

    def test_no_overclaims_across_docs(self):
        combined = "\n".join(norm(read(p)) for p in MARKDOWN_DOCS)
        for claim in FALSE_CLAIMS:
            self.assertNotIn(claim, combined, msg=f"overclaim found: {claim!r}")

    def test_no_secret_patterns(self):
        combined = "\n".join(read(p) for p in SECRET_SCAN_FILES)
        self.assertNotRegex(combined, r"sk-[A-Za-z0-9_-]{20,}")
        self.assertNotRegex(combined, r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY")


if __name__ == "__main__":
    unittest.main()
