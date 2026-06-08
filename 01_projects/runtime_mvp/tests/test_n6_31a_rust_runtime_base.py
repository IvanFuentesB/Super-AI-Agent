"""
test_n6_31a_rust_runtime_base.py

Structural tests for N+6.31A Rust runtime base scaffold.
Validates that all required files exist, the workspace Cargo.toml is correct,
the runtime_core crate structure is present, no unsafe code was added, no
machine-specific paths are committed, and no AI attribution trailers appear.
Pure stdlib; no network; no shell execution; no installs.
"""

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
RUST = REPO_ROOT / "rust"
RUNTIME_CORE = RUST / "ghoti_runtime_core"
POLICY_CHECKER = RUST / "ghoti_policy_checker"
DOCS = REPO_ROOT / "docs"
CONTEXT = REPO_ROOT / "14_context"


class TestRequiredFilesExist(unittest.TestCase):
    def _check(self, path: Path) -> None:
        self.assertTrue(path.is_file(), msg=f"missing: {path.relative_to(REPO_ROOT)}")

    def test_workspace_cargo_toml(self):
        self._check(RUST / "Cargo.toml")

    def test_runtime_core_cargo_toml(self):
        self._check(RUNTIME_CORE / "Cargo.toml")

    def test_runtime_core_lib(self):
        self._check(RUNTIME_CORE / "src" / "lib.rs")

    def test_runtime_core_policy(self):
        self._check(RUNTIME_CORE / "src" / "policy.rs")

    def test_runtime_core_events(self):
        self._check(RUNTIME_CORE / "src" / "events.rs")

    def test_policy_checker_still_exists(self):
        self._check(POLICY_CHECKER / "Cargo.toml")
        self._check(POLICY_CHECKER / "src" / "main.rs")

    def test_main_doc(self):
        self._check(DOCS / "GHOTI_N6_31A_RUST_RUNTIME_BASE.md")

    def test_context_snapshot(self):
        self._check(CONTEXT / "claude_n6_31a_rust_runtime_base.md")


class TestWorkspaceCargo(unittest.TestCase):
    def setUp(self):
        self.text = (RUST / "Cargo.toml").read_text(encoding="utf-8")

    def test_workspace_section_present(self):
        self.assertIn("[workspace]", self.text)

    def test_policy_checker_is_member(self):
        self.assertIn("ghoti_policy_checker", self.text)

    def test_runtime_core_is_member(self):
        self.assertIn("ghoti_runtime_core", self.text)

    def test_resolver_v2(self):
        self.assertIn('resolver = "2"', self.text)

    def test_no_machine_specific_paths(self):
        forbidden_patterns = [
            r"C:\\Users\\",
            r"/home/[a-z]",
            r"C:/Users/",
        ]
        for pattern in forbidden_patterns:
            self.assertIsNone(
                re.search(pattern, self.text, re.IGNORECASE),
                msg=f"Machine-specific path pattern '{pattern}' found in rust/Cargo.toml",
            )


class TestRuntimeCoreCargo(unittest.TestCase):
    def setUp(self):
        self.text = (RUNTIME_CORE / "Cargo.toml").read_text(encoding="utf-8")

    def test_package_name(self):
        self.assertIn('name = "ghoti_runtime_core"', self.text)

    def test_serde_dependency(self):
        self.assertIn("serde", self.text)

    def test_serde_json_dependency(self):
        self.assertIn("serde_json", self.text)

    def test_no_network_dependencies(self):
        forbidden = ["tokio", "reqwest", "hyper", "axum", "warp", "actix"]
        for dep in forbidden:
            self.assertNotIn(dep, self.text.lower(),
                             msg=f"Network dependency '{dep}' found in runtime_core Cargo.toml")

    def test_no_process_dependencies(self):
        forbidden = ["subprocess", "nix", "libc"]
        for dep in forbidden:
            self.assertNotIn(dep, self.text.lower(),
                             msg=f"Process-level dependency '{dep}' found")


class TestRuntimeCoreSource(unittest.TestCase):
    def _read(self, rel: str) -> str:
        return (RUNTIME_CORE / "src" / rel).read_text(encoding="utf-8")

    def test_lib_declares_policy_module(self):
        self.assertIn("pub mod policy", self._read("lib.rs"))

    def test_lib_declares_events_module(self):
        self.assertIn("pub mod events", self._read("lib.rs"))

    def test_policy_has_policy_verdict(self):
        text = self._read("policy.rs")
        self.assertIn("PolicyVerdict", text)
        self.assertIn("Allow", text)
        self.assertIn("Deny", text)

    def test_policy_has_kill_switch_status(self):
        text = self._read("policy.rs")
        self.assertIn("KillSwitchStatus", text)
        self.assertIn("KillSwitchState", text)

    def test_policy_has_runtime_capability(self):
        text = self._read("policy.rs")
        self.assertIn("RuntimeCapability", text)

    def test_policy_blocked_capabilities_listed(self):
        text = self._read("policy.rs")
        for cap in ["Browser", "ComputerUse", "Mcp", "Account", "Money",
                    "MassMessage", "Secrets", "LiveLaunch", "Docker",
                    "AutoSubmit", "ExternalNav"]:
            self.assertIn(cap, text, msg=f"Blocked capability '{cap}' not in policy.rs")

    def test_events_has_agent_role(self):
        text = self._read("events.rs")
        self.assertIn("AgentRole", text)
        for role in ["Builder", "Auditor", "Planner", "Explorer", "Observer"]:
            self.assertIn(role, text, msg=f"AgentRole::{role} not in events.rs")

    def test_events_has_runtime_event(self):
        text = self._read("events.rs")
        self.assertIn("RuntimeEvent", text)
        self.assertIn("EventKind", text)

    def test_events_dry_run_field_present(self):
        text = self._read("events.rs")
        self.assertIn("dry_run", text)
        self.assertIn("live", text)

    def test_no_unsafe_keyword_as_code(self):
        for fname in ["lib.rs", "policy.rs", "events.rs"]:
            text = self._read(fname)
            lines = text.splitlines()
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if re.match(r"unsafe\s*\{", stripped) or re.match(r"unsafe\s+fn\b", stripped) \
                        or re.match(r"unsafe\s+impl\b", stripped) \
                        or re.match(r"unsafe\s+trait\b", stripped):
                    self.fail(f"unsafe code in {fname}:{i}: {line.rstrip()}")

    def test_no_std_process_command(self):
        for fname in ["lib.rs", "policy.rs", "events.rs"]:
            text = self._read(fname)
            self.assertNotIn("process::Command", text,
                             msg=f"process::Command found in {fname}")

    def test_no_network_use(self):
        network_patterns = ["std::net", "TcpStream", "TcpListener", "UdpSocket",
                            "reqwest", "hyper::", "axum::", "tokio::net"]
        for fname in ["lib.rs", "policy.rs", "events.rs"]:
            text = self._read(fname)
            for pattern in network_patterns:
                self.assertNotIn(pattern, text,
                                 msg=f"Network usage '{pattern}' in {fname}")


class TestPolicyCheckerUnchanged(unittest.TestCase):
    def test_policy_checker_cargo_unchanged(self):
        text = (POLICY_CHECKER / "Cargo.toml").read_text(encoding="utf-8")
        self.assertIn("ghoti_policy_checker", text)
        self.assertIn("serde", text)

    def test_policy_checker_main_unchanged(self):
        text = (POLICY_CHECKER / "src" / "main.rs").read_text(encoding="utf-8")
        self.assertIn("ghoti_policy_checker", text)
        self.assertIn("default_deny", text)
        self.assertIn("live_launch", text)


class TestNoForbiddenContent(unittest.TestCase):
    def _all_new_files(self):
        files = []
        for pattern in [
            "rust/Cargo.toml",
            "rust/ghoti_runtime_core/**/*",
            "docs/GHOTI_N6_31A_*.md",
            "14_context/claude_n6_31a_*.md",
        ]:
            files.extend(REPO_ROOT.glob(pattern))
        return [f for f in files if f.is_file()]

    def test_no_ai_attribution_trailers(self):
        forbidden = [
            "co-authored-by claude",
            "co-authored-by gpt",
            "generated with claude",
            "generated by claude",
            "generated with chatgpt",
        ]
        for fpath in self._all_new_files():
            content = fpath.read_text(encoding="utf-8").lower()
            for phrase in forbidden:
                self.assertNotIn(
                    phrase, content,
                    msg=f"AI attribution in {fpath.name}: '{phrase}'",
                )

    def test_no_machine_paths(self):
        patterns = [r"C:\\Users\\", r"C:/Users/", r"/home/[a-z]"]
        for fpath in self._all_new_files():
            content = fpath.read_text(encoding="utf-8")
            for pattern in patterns:
                self.assertIsNone(
                    re.search(pattern, content, re.IGNORECASE),
                    msg=f"Machine path '{pattern}' in {fpath.name}",
                )

    def test_no_secrets(self):
        secret_patterns = ["api_key =", "token =", "password =", "secret =",
                           "bearer ", ".env"]
        for fpath in self._all_new_files():
            content = fpath.read_text(encoding="utf-8").lower()
            for pattern in secret_patterns:
                if f'"{pattern}' in content or f"'{pattern}" in content:
                    self.fail(f"Possible secret in {fpath.name}: '{pattern}'")


class TestMainDocContent(unittest.TestCase):
    def setUp(self):
        self.doc = (DOCS / "GHOTI_N6_31A_RUST_RUNTIME_BASE.md").read_text(encoding="utf-8")

    def test_doc_references_workspace(self):
        self.assertIn("rust/Cargo.toml", self.doc)

    def test_doc_references_runtime_core(self):
        self.assertIn("ghoti_runtime_core", self.doc)

    def test_doc_references_policy_checker(self):
        self.assertIn("ghoti_policy_checker", self.doc)

    def test_doc_mentions_no_unsafe(self):
        self.assertIn("unsafe", self.doc.lower())

    def test_doc_mentions_kill_switch(self):
        self.assertIn("kill", self.doc.lower())

    def test_doc_lists_all_new_files(self):
        expected = [
            "rust/Cargo.toml",
            "rust/ghoti_runtime_core/Cargo.toml",
            "rust/ghoti_runtime_core/src/lib.rs",
            "rust/ghoti_runtime_core/src/policy.rs",
            "rust/ghoti_runtime_core/src/events.rs",
            "test_n6_31a_rust_runtime_base.py",
            "claude_n6_31a_rust_runtime_base.md",
        ]
        for fname in expected:
            self.assertIn(fname, self.doc, msg=f"Main doc missing '{fname}'")

    def test_computer_use_adapter_untouched_noted(self):
        self.assertIn("not merged", self.doc.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
