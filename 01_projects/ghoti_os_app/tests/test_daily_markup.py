"""Scoped daily-shell markup/accessibility checks; no browser or runtime side effects."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

STATIC = Path(__file__).resolve().parents[1] / "dashboard_app/static"


class DailyMarkup(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.elements = []
        self.legacy = False
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id") == "legacy-dashboard":
            self.legacy = True
            assert "hidden" in attrs and "inert" in attrs
        if not self.legacy:
            self.elements.append((tag, attrs))


class DailyMarkupTests(unittest.TestCase):
    def setUp(self):
        self.html = (STATIC / "index.html").read_text(encoding="utf-8")
        self.markup = DailyMarkup(self.html)

    def test_default_chat_and_seven_navigation_destinations_are_unambiguous(self):
        elements = self.markup.elements
        counts = Counter(a["id"] for _, a in elements if "id" in a)
        self.assertTrue(all(n == 1 for n in counts.values()))
        nav = [a["data-daily-view"] for _, a in elements if "data-daily-view" in a]
        self.assertEqual(nav, ["chat", "computer", "projects", "agents", "memory", "tools", "settings"])
        panels = {a["data-daily-panel"]: a for _, a in elements if "data-daily-panel" in a}
        self.assertEqual(set(nav), set(panels))
        self.assertNotIn("hidden", panels["chat"])
        self.assertTrue(all("hidden" in panels[k] for k in panels if k != "chat"))

    def test_inputs_are_labelled_and_initial_write_controls_are_disabled(self):
        labels = {a.get("for") for tag, a in self.markup.elements if tag == "label"}
        for tag, attrs in self.markup.elements:
            if tag in {"input", "textarea", "select"}:
                self.assertIn(attrs.get("id"), labels)
            if attrs.get("id") in {"daily-send", "daily-run", "daily-cancel", "daily-new"}:
                self.assertIn("disabled", attrs)
        self.assertTrue(any(a.get("class") == "skip-link" for _, a in self.markup.elements))
        self.assertTrue(any(a.get("role") == "log" for _, a in self.markup.elements))

    def test_mobile_menu_diagnostics_and_quiet_conversation_have_explicit_semantics(self):
        ids = {a["id"]: a for _, a in self.markup.elements if "id" in a}
        self.assertEqual(ids["daily-menu"]["aria-controls"], "daily-navigation")
        self.assertEqual(ids["daily-menu"]["aria-expanded"], "false")
        self.assertNotIn("open", ids["daily-developer"])
        self.assertEqual(ids["daily-conversation"]["aria-live"], "off")
        self.assertEqual(ids["daily-chat-state"]["role"], "status")
        self.assertEqual(ids["daily-prompt"]["maxlength"], "12000")
        self.assertIn("prefers-reduced-motion", (STATIC / "daily.css").read_text(encoding="utf-8"))

    def test_only_daily_scripts_load_and_no_unsafe_sinks_or_demo_data_are_shipped(self):
        scripts = [a.get("src") for tag, a in self.markup.elements if tag == "script"]
        self.assertEqual(scripts, ["/static/local-session.js", "/static/chat.js", "/static/daily.js", "/static/computer.js"])
        ids = {a["id"]: a for _, a in self.markup.elements if "id" in a}
        for name in ("computer-start", "computer-stop", "computer-approve", "computer-deny"):
            self.assertIn("disabled", ids[name])
        self.assertIn("hidden", ids["computer-image"])
        self.assertIn("hidden", ids["computer-approval"])
        self.assertIn("daily-chat-mode", ids)
        for name in ("chat.js", "daily.js", "computer.js", "local-session.js"):
            source = (STATIC / name).read_text(encoding="utf-8")
            for forbidden in ("innerHTML", "outerHTML", "insertAdjacentHTML", "localStorage", "sessionStorage", "fixture-browser", "eval("):
                self.assertNotIn(forbidden, source)
        for _, attrs in self.markup.elements:
            self.assertFalse(any(key.startswith("on") for key in attrs))

    def test_skip_link_target_is_at_least_44px_at_default_size(self):
        css = (STATIC / "daily.css").read_text(encoding="utf-8")
        rule = re.search(r"^\.skip-link\s*\{([^}]*)\}", css, re.M).group(1)
        min_height = re.search(r"(?:^|;)\s*min-height:\s*(\d+)px", rule)
        self.assertIsNotNone(min_height, rule)
        self.assertGreaterEqual(int(min_height.group(1)), 44)
        self.assertNotRegex(rule, r"(?:^|;)\s*display:\s*inline\s*;")

    def test_palette_text_contrast_meets_wcag_aa(self):
        css = (STATIC / "daily.css").read_text(encoding="utf-8")
        colors = dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-f]{6});", css))

        def luminance(color):
            channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in channels]
            return sum(c * w for c, w in zip(linear, (.2126, .7152, .0722)))

        pairs = [(colors["ink"], colors["canvas"]), (colors["muted"], colors["canvas"]),
                 (colors["muted"], colors["nav"]), ("#ffffff", colors["accent"]),
                 (colors["warn"], colors["warn-soft"]), (colors["red"], colors["surface"])]
        for foreground, background in pairs:
            high, low = sorted([luminance(foreground), luminance(background)], reverse=True)
            self.assertGreaterEqual((high + .05) / (low + .05), 4.5, (foreground, background))


if __name__ == "__main__":
    unittest.main()
