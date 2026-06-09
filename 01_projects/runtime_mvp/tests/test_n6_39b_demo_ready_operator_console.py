#!/usr/bin/env python3
"""N+6.39B tests: Demo-Ready Operator Console.

Covers:
- Fix A: badge/card overflow (overflow-x hidden, word-break on badges)
- Fix B: overlay default-collapsed on first visit
- Fix C: hero section with 3 bullets and 4 status chips
- Fix D: Real Use Today 5-card demo flow
- Fix E: Investor Demo Mode panel (30-second pitch, 90-second flow, what's real,
         what's not live yet, why it matters)
- Fix F: Why blocked is good explanation
- Fix G: Roadmap with 5 items
- Fix H: Approvals page static friendly card
- Fix I: GitHub page plain-language static card
- Fix J: Show me what command to run (copyable area)
- No new AI attribution
- No new provider key references
- Context snapshot file exists
"""
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
INDEX_HTML = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "index.html"
APP_JS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "app.js"
STYLES_CSS = REPO_ROOT / "01_projects" / "dashboard_mvp" / "public" / "styles.css"
CONTEXT_SNAPSHOT = REPO_ROOT / "14_context" / "claude_n6_39b_demo_ready_operator_console.md"
DOCS_FILE = REPO_ROOT / "docs" / "GHOTI_N6_39B_DEMO_READY_OPERATOR_CONSOLE.md"


class TestOverflowFix(unittest.TestCase):
    def setUp(self):
        self.css = STYLES_CSS.read_text(encoding="utf-8")

    def test_body_overflow_hidden(self):
        self.assertIn("overflow-x: hidden", self.css)

    def test_badge_word_break_fix(self):
        # Badges must have word-break to prevent horizontal overflow.
        self.assertIn("word-break", self.css)
        # The N+6.39B section adds it for .cap-badge.
        n39b_section = self.css.split("N+6.39B", 1)[-1] if "N+6.39B" in self.css else ""
        self.assertIn("word-break", n39b_section, "word-break must appear in N+6.39B section")


class TestOverlayDefaultCollapsed(unittest.TestCase):
    def setUp(self):
        self.app = APP_JS.read_text(encoding="utf-8")

    def test_overlay_collapsed_by_default_first_visit(self):
        # The initOverlayControls must default collapsed=true when no stored preference.
        self.assertIn("stored === null ? true", self.app)

    def test_overlay_collapse_default_comment(self):
        # The default collapsed behaviour is documented inline.
        self.assertIn("default: collapsed on first visit", self.app)


class TestHeroSection(unittest.TestCase):
    def setUp(self):
        self.html = INDEX_HTML.read_text(encoding="utf-8")

    def test_hero_what_is_ghoti_present(self):
        self.assertIn("What is Ghoti?", self.html)

    def test_hero_three_bullets_present(self):
        hero_block = self.html.split("What is Ghoti?", 1)[-1].split("What can Ghoti do now?", 1)[0]
        bullet_count = hero_block.count("<li>")
        self.assertGreaterEqual(bullet_count, 3, "hero section must have at least 3 bullets")

    def test_hero_four_status_chips(self):
        for chip in ["Local-only", "Supervised", "Dry-run-first", "No live account actions"]:
            self.assertIn(chip, self.html, "hero chip missing: %s" % chip)


class TestRealUseTodayDemoFlow(unittest.TestCase):
    def setUp(self):
        self.html = INDEX_HTML.read_text(encoding="utf-8")

    def test_real_use_today_demo_flow_present(self):
        self.assertIn("Real Use Today - Demo Flow", self.html)

    def test_demo_card_run_safe_check(self):
        self.assertIn("Run Safe Check", self.html)

    def test_demo_card_repo_map(self):
        self.assertIn("Show Repo Map", self.html)

    def test_demo_card_fixture_replay(self):
        self.assertIn("Run Fixture Replay", self.html)

    def test_demo_card_handoff_packet(self):
        self.assertIn("Prepare Handoff Packet", self.html)

    def test_demo_card_local_model(self):
        self.assertIn("Check Local Model Lane", self.html)


class TestInvestorDemoPanel(unittest.TestCase):
    def setUp(self):
        self.html = INDEX_HTML.read_text(encoding="utf-8")

    def test_investor_demo_panel_present(self):
        self.assertIn("Investor Demo Mode", self.html)

    def test_investor_demo_30_second_pitch(self):
        self.assertIn("30-second pitch", self.html)

    def test_investor_demo_90_second_flow(self):
        self.assertIn("90-second", self.html)

    def test_investor_demo_what_is_real_today(self):
        self.assertIn("What is real today", self.html)

    def test_investor_demo_what_is_not_live_yet(self):
        self.assertIn("What is not live yet", self.html)

    def test_investor_demo_why_it_matters(self):
        self.assertIn("Why it matters", self.html)


class TestWhyBlockedIsGood(unittest.TestCase):
    def setUp(self):
        self.html = INDEX_HTML.read_text(encoding="utf-8")

    def test_why_blocked_is_good_present(self):
        self.assertIn("Why blocked is good", self.html)

    def test_blocked_is_feature_not_failure(self):
        self.assertIn("feature", self.html.split("Why blocked is good", 1)[-1].split("</section>", 1)[0])


class TestRoadmap(unittest.TestCase):
    def setUp(self):
        self.html = INDEX_HTML.read_text(encoding="utf-8")

    def test_roadmap_section_present(self):
        self.assertIn("Roadmap", self.html)

    def test_roadmap_5_items_present(self):
        for item in [
            "Obsidian Memory Bridge",
            "Telegram notification bridge",
            "Live agent with approval gate",
            "Real computer-use lane",
            "Hermes Codex provider integration",
        ]:
            self.assertIn(item, self.html, "roadmap item missing: %s" % item)


class TestApprovalsStaticCard(unittest.TestCase):
    def setUp(self):
        self.html = INDEX_HTML.read_text(encoding="utf-8")

    def test_approvals_has_friendly_static_card(self):
        self.assertIn("approvals-static-card", self.html)

    def test_approvals_no_private_paths(self):
        approvals_block = self.html.split('data-console-view-panel="approvals"', 1)[-1].split(
            'data-console-view-panel=', 1)[0]
        for bad in ["C:\\Users\\", "C:/Users/", "\\AppData\\", "/home/ai_sandbox"]:
            self.assertNotIn(bad, approvals_block, "private path in approvals panel: %r" % bad)

    def test_approvals_no_action_needed_message(self):
        self.assertIn("No action needed if you are not running any agents", self.html)


class TestGitHubStaticCard(unittest.TestCase):
    def setUp(self):
        self.html = INDEX_HTML.read_text(encoding="utf-8")

    def test_github_static_card_present(self):
        self.assertIn("github-static-card", self.html)

    def test_github_does_not_modify_claim(self):
        github_block = self.html.split('data-console-view-panel="github"', 1)[-1].split(
            'data-console-view-panel=', 1)[0]
        self.assertIn("does not push, merge, or modify", github_block)

    def test_github_read_only_note(self):
        github_block = self.html.split('data-console-view-panel="github"', 1)[-1].split(
            'data-console-view-panel=', 1)[0]
        self.assertIn("read-only", github_block)


class TestShowCommandArea(unittest.TestCase):
    def setUp(self):
        self.html = INDEX_HTML.read_text(encoding="utf-8")
        self.app = APP_JS.read_text(encoding="utf-8")

    def test_show_command_section_present(self):
        self.assertIn("cap-show-command", self.html)

    def test_show_cmd_text_element_present(self):
        self.assertIn("cap-show-cmd-text", self.html)

    def test_show_cmd_copy_button_present(self):
        self.assertIn("cap-show-cmd-copy", self.html)

    def test_show_cmd_copy_handler_in_app_js(self):
        self.assertIn("capShowCmdCopy", self.app)


class TestNoUnsafeAdditions(unittest.TestCase):
    def setUp(self):
        self.html = INDEX_HTML.read_text(encoding="utf-8")
        self.app = APP_JS.read_text(encoding="utf-8")
        self.css = STYLES_CSS.read_text(encoding="utf-8")

    def test_no_new_ai_attribution(self):
        blob = (self.html + self.app + self.css).lower()
        for phrase in ["co-authored-by claude", "generated with claude",
                       "generated by claude", "written by claude",
                       "claude-sonnet", "claude-opus"]:
            self.assertNotIn(phrase, blob, "AI attribution found: %r" % phrase)

    def test_no_new_provider_keys(self):
        for token in ["sk-ant-", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"]:
            self.assertNotIn(token, self.html, "provider key ref in html: %s" % token)
            self.assertNotIn(token, self.css, "provider key ref in css: %s" % token)

    def test_context_snapshot_file_exists(self):
        self.assertTrue(CONTEXT_SNAPSHOT.exists(),
                        "context snapshot missing: %s" % CONTEXT_SNAPSHOT)

    def test_docs_file_exists(self):
        self.assertTrue(DOCS_FILE.exists(), "docs file missing: %s" % DOCS_FILE)


if __name__ == "__main__":
    unittest.main()
