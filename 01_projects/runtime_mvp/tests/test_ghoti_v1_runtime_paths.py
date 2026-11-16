#!/usr/bin/env python3
"""Tests for the Ghoti runtime path layer that keeps generated state out of the repository.

Covers root selection and its fallbacks, the directory getters, idempotent
directory creation, the atomic writers, and the write-access diagnosis that
identifies an operating-system folder protection policy. Every test redirects the
runtime root into a temporary directory and patches ``os.environ`` through
``patch.dict``, so the real environment and the real per-user runtime location are
never touched.
"""

from __future__ import annotations

import contextlib
import importlib.util
import json
import os
import re
import unittest
import tempfile
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_PATHS_PATH = REPO_ROOT / "03_scripts" / "ghoti_runtime" / "paths.py"
RUNTIME_README_PATH = REPO_ROOT / "03_scripts" / "ghoti_runtime" / "README.md"

EXPECTED_ENV_VAR = "GHOTI_RUNTIME_ROOT"
EXPECTED_SOURCES = ("env", "localappdata", "temp")

SAFETY_KEYS = (
    "local_only",
    "network_used",
    "scraping_used",
    "browser_used",
    "account_actions_used",
    "messages_sent",
    "content_posted",
    "payments_or_ad_spend_used",
    "credentials_used",
    "human_review_required",
)

ALLOWED_IMPORTS = {"__future__", "json", "os", "tempfile", "uuid", "pathlib"}

# Nothing in the runtime path layer may reach a network.
NETWORK_MODULES = (
    "smtplib",
    "requests",
    "urllib",
    "urllib.request",
    "http.client",
    "ftplib",
    "socket",
    "ssl",
    "asyncio",
)

# The module may not name any environment variable other than the runtime root.
OTHER_ENV_NAMES = (
    "LOCALAPPDATA",
    "APPDATA",
    "TEMP",
    "TMP",
    "TMPDIR",
    "USERPROFILE",
    "HOMEPATH",
    "HOMEDRIVE",
    "HOME",
    "PATH",
    "PATHEXT",
    "COMSPEC",
    "USERNAME",
)

FORBIDDEN_TEXT_PATTERNS = (
    ("windows_drive_path", re.compile(r"[A-Za-z]:[\\/]")),
    ("unc_path", re.compile(r"\\\\[A-Za-z0-9_.$-]+\\")),
    ("posix_home_path", re.compile(r"/home/[^/\s\"]+/")),
    ("macos_home_path", re.compile(r"/Users/[^/\s\"]+/")),
    ("openai_style_key", re.compile(r"\bsk-[A-Za-z0-9_-]{16,}")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{16,}")),
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
)


def _load_runtime_paths():
    """Load the runtime path module from its file path without installing a package."""
    if not RUNTIME_PATHS_PATH.is_file():
        raise FileNotFoundError("missing 03_scripts/ghoti_runtime/paths.py")
    spec = importlib.util.spec_from_file_location("ghoti_v1_runtime_paths_test", RUNTIME_PATHS_PATH)
    if spec is None or spec.loader is None:
        raise ImportError("paths")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


paths = _load_runtime_paths()
SOURCE = RUNTIME_PATHS_PATH.read_text(encoding="utf-8")

GETTERS = (
    "get_dispatch_runtime_root",
    "get_dispatch_outbox_dir",
    "get_dispatch_artifacts_dir",
    "get_dispatch_evidence_dir",
    "get_logs_dir",
)


@contextlib.contextmanager
def _environment(value: str | None):
    """Run with GHOTI_RUNTIME_ROOT set to ``value`` (or unset). The real env is restored."""
    env = {key: item for key, item in os.environ.items() if key != EXPECTED_ENV_VAR}
    if value is not None:
        env[EXPECTED_ENV_VAR] = value
    with mock.patch.dict(os.environ, env, clear=True):
        yield


def _unwritable(base: Path, name: str = "blocker.txt") -> Path:
    """Return a path that cannot be created: it sits underneath a regular file."""
    blocker = Path(base) / name
    blocker.write_text("this is a file, not a directory\n", encoding="utf-8")
    return blocker / "runtime_root"


class TempCaseMixin:
    """Give every test its own temporary directory."""

    def setUp(self) -> None:  # noqa: D102 - unittest hook
        super().setUp()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)


class RuntimeRootSelectionTests(TempCaseMixin, unittest.TestCase):
    """The first writable candidate wins and every rejection is reported."""

    def test_the_module_declares_the_expected_contract(self) -> None:
        self.assertEqual(paths.RUNTIME_ROOT_ENV_VAR, EXPECTED_ENV_VAR)
        self.assertEqual(tuple(paths.CANDIDATE_SOURCES), EXPECTED_SOURCES)
        self.assertEqual(paths.REPO_ROOT, REPO_ROOT)
        self.assertTrue(RUNTIME_README_PATH.is_file(), "the runtime package must document itself")

    def test_environment_variable_wins_when_set_and_writable(self) -> None:
        wanted = self.tmp / "operator_choice"
        with _environment(str(wanted)):
            selection = paths.select_runtime_root()
            self.assertEqual(paths.get_runtime_root(), wanted)
        self.assertTrue(selection["ok"], selection.get("error"))
        self.assertEqual(selection["selected_source"], "env")
        self.assertEqual(Path(selection["runtime_root"]), wanted)
        self.assertEqual(selection["rejected"], [])
        self.assertTrue(wanted.is_dir(), "the selected root must exist after selection")

    def test_a_blank_environment_variable_is_not_used(self) -> None:
        local_base = self.tmp / "local"
        with _environment("   "), mock.patch.object(
            paths, "_local_app_data_dir", return_value=local_base
        ):
            selection = paths.select_runtime_root()
        self.assertEqual(selection["selected_source"], "localappdata")
        self.assertEqual(
            Path(selection["runtime_root"]),
            local_base / paths.RUNTIME_VENDOR_DIR / paths.RUNTIME_WORKSPACE_DIR,
        )

    def test_an_unset_environment_variable_is_reported_as_a_rejection(self) -> None:
        local_base = self.tmp / "local"
        with _environment(None), mock.patch.object(
            paths, "_local_app_data_dir", return_value=local_base
        ):
            selection = paths.select_runtime_root()
        self.assertEqual(selection["selected_source"], "localappdata")
        self.assertEqual(len(selection["rejected"]), 1)
        rejected = selection["rejected"][0]
        self.assertEqual(rejected["source"], "env")
        self.assertIsNone(rejected["path"])
        self.assertIn(EXPECTED_ENV_VAR, rejected["reason"])

    def test_an_unwritable_environment_root_falls_back_to_local_app_data(self) -> None:
        blocked = _unwritable(self.tmp)
        local_base = self.tmp / "local"
        with _environment(str(blocked)), mock.patch.object(
            paths, "_local_app_data_dir", return_value=local_base
        ):
            selection = paths.select_runtime_root()
            chosen = paths.get_runtime_root()
        self.assertTrue(selection["ok"], selection.get("error"))
        self.assertEqual(selection["selected_source"], "localappdata")
        self.assertEqual(chosen, local_base / paths.RUNTIME_VENDOR_DIR / paths.RUNTIME_WORKSPACE_DIR)
        self.assertNotEqual(chosen, blocked)
        self.assertFalse(blocked.exists(), "an unwritable candidate must not be created")
        self.assertEqual([entry["source"] for entry in selection["rejected"]], ["env"])
        self.assertEqual(Path(selection["rejected"][0]["path"]), blocked)
        self.assertTrue(selection["rejected"][0]["reason"], "a rejection must carry a reason")

    def test_an_unwritable_local_app_data_falls_back_to_temp(self) -> None:
        blocked_env = _unwritable(self.tmp, "env_blocker.txt")
        blocked_local = _unwritable(self.tmp, "local_blocker.txt")
        temp_base = self.tmp / "fallback_temp"
        with _environment(str(blocked_env)), mock.patch.object(
            paths, "_local_app_data_dir", return_value=blocked_local
        ), mock.patch.object(paths, "_temp_dir", return_value=temp_base):
            selection = paths.select_runtime_root()
        self.assertTrue(selection["ok"], selection.get("error"))
        self.assertEqual(selection["selected_source"], "temp")
        self.assertEqual(
            Path(selection["runtime_root"]),
            temp_base / paths.RUNTIME_VENDOR_DIR / paths.RUNTIME_WORKSPACE_DIR,
        )
        self.assertEqual([entry["source"] for entry in selection["rejected"]], ["env", "localappdata"])
        for entry in selection["rejected"]:
            with self.subTest(source=entry["source"]):
                self.assertTrue(entry["reason"])
                self.assertIsNotNone(entry["path"])

    def test_every_candidate_blocked_is_reported_and_never_faked(self) -> None:
        blocked_env = _unwritable(self.tmp, "env_blocker.txt")
        blocked_local = _unwritable(self.tmp, "local_blocker.txt")
        blocked_temp = _unwritable(self.tmp, "temp_blocker.txt")
        with _environment(str(blocked_env)), mock.patch.object(
            paths, "_local_app_data_dir", return_value=blocked_local
        ), mock.patch.object(paths, "_temp_dir", return_value=blocked_temp):
            selection = paths.select_runtime_root()
        self.assertFalse(selection["ok"], "a fully blocked selection must not report success")
        self.assertIsNone(selection["selected_source"])
        self.assertTrue(selection["error"])
        self.assertEqual(
            [entry["source"] for entry in selection["rejected"]], list(EXPECTED_SOURCES)
        )

    def test_an_explicit_root_overrides_the_environment(self) -> None:
        override = self.tmp / "explicit"
        with _environment(str(self.tmp / "from_env")):
            self.assertEqual(paths.get_runtime_root(override), override)
            self.assertEqual(paths.get_runtime_root(str(override)), override)

    def test_selection_probes_instead_of_assuming_and_leaves_no_probe_file(self) -> None:
        wanted = self.tmp / "probe_target"
        with _environment(str(wanted)):
            paths.select_runtime_root()
        self.assertTrue(wanted.is_dir())
        self.assertEqual(
            sorted(path.name for path in wanted.iterdir()), [], "a probe file was left behind"
        )

    def test_the_real_environment_is_never_mutated(self) -> None:
        before = dict(os.environ)
        with _environment(str(self.tmp / "scratch")):
            paths.select_runtime_root()
            paths.ensure_runtime_dirs()
        self.assertEqual(dict(os.environ), before)


class RuntimeDirectoryLayoutTests(TempCaseMixin, unittest.TestCase):
    """Every getter resolves under the runtime root and accepts an override."""

    def test_every_getter_sits_under_the_selected_root(self) -> None:
        root = self.tmp / "runtime"
        with _environment(str(root)):
            self.assertEqual(paths.get_runtime_root(), root)
            for name in GETTERS:
                with self.subTest(getter=name):
                    resolved = getattr(paths, name)()
                    self.assertTrue(
                        resolved.is_relative_to(root), f"{name} escaped the runtime root: {resolved}"
                    )

    def test_every_getter_accepts_an_explicit_root_override(self) -> None:
        override = self.tmp / "override"
        with _environment(str(self.tmp / "ignored")):
            for name in GETTERS:
                with self.subTest(getter=name):
                    resolved = getattr(paths, name)(override)
                    self.assertTrue(resolved.is_relative_to(override), str(resolved))
                    self.assertFalse(resolved.is_relative_to(self.tmp / "ignored"))

    def test_the_dispatch_layout_mirrors_the_repository_layout(self) -> None:
        root = self.tmp / "runtime"
        dispatch = paths.get_dispatch_runtime_root(root)
        self.assertEqual(dispatch, root / "14_context" / "dispatch")
        self.assertEqual(dispatch.relative_to(root).as_posix(), paths.DISPATCH_ROOT_REL)
        self.assertEqual(paths.get_dispatch_outbox_dir(root), dispatch / "outbox")
        self.assertEqual(paths.get_dispatch_artifacts_dir(root), dispatch / "artifacts")
        self.assertEqual(paths.get_dispatch_evidence_dir(root), dispatch / "evidence")
        self.assertEqual(paths.get_logs_dir(root), root / "05_logs")

    def test_no_getter_resolves_inside_the_repository(self) -> None:
        root = self.tmp / "runtime"
        with _environment(str(root)):
            for name in ("get_runtime_root", *GETTERS):
                with self.subTest(getter=name):
                    resolved = getattr(paths, name)()
                    self.assertFalse(
                        resolved.is_relative_to(REPO_ROOT),
                        f"{name} resolved inside the repository: {resolved}",
                    )

    def test_ensure_runtime_dirs_creates_every_directory(self) -> None:
        root = self.tmp / "runtime"
        result = paths.ensure_runtime_dirs(root)
        self.assertTrue(result["ok"], result["failed"])
        self.assertEqual(result["schema"], paths.DIRS_SCHEMA)
        self.assertEqual(Path(result["runtime_root"]), root)
        self.assertEqual(result["failed"], [])
        for name in GETTERS:
            with self.subTest(getter=name):
                self.assertTrue(getattr(paths, name)(root).is_dir())
        self.assertEqual(len(result["created"]), 6)
        self.assertEqual(result["existing"], [])

    def test_ensure_runtime_dirs_is_idempotent(self) -> None:
        root = self.tmp / "runtime"
        first = paths.ensure_runtime_dirs(root)
        second = paths.ensure_runtime_dirs(root)
        third = paths.ensure_runtime_dirs(root)
        self.assertTrue(second["ok"])
        self.assertTrue(third["ok"])
        self.assertEqual(second["created"], [], "a second call must create nothing")
        self.assertEqual(third["created"], [])
        self.assertEqual(sorted(second["existing"]), sorted(first["created"]))
        self.assertEqual(second["existing"], third["existing"])

    def test_ensure_runtime_dirs_reports_a_blocked_root_instead_of_raising(self) -> None:
        blocked = _unwritable(self.tmp)
        result = paths.ensure_runtime_dirs(blocked)
        self.assertFalse(result["ok"], "a blocked root must not report success")
        self.assertTrue(result["failed"])
        self.assertTrue(result["error"])


class AtomicWriteTests(TempCaseMixin, unittest.TestCase):
    """The writers replace a file in one step and never leave a partial one."""

    def test_write_text_atomic_creates_parents_and_writes_utf8(self) -> None:
        target = self.tmp / "deep" / "nested" / "report.md"
        result = paths.write_text_atomic(target, "# report\n\nlocal only\n")
        self.assertTrue(result["ok"], result["error"])
        self.assertEqual(result["schema"], paths.WRITE_SCHEMA)
        self.assertIsNone(result["error"])
        self.assertEqual(target.read_text(encoding="utf-8"), "# report\n\nlocal only\n")
        self.assertEqual(result["byte_count"], len("# report\n\nlocal only\n".encode("utf-8")))

    def test_write_text_atomic_overwrites_cleanly(self) -> None:
        target = self.tmp / "artifact.json"
        paths.write_text_atomic(target, "first" * 200)
        result = paths.write_text_atomic(target, "second\n")
        self.assertTrue(result["ok"], result["error"])
        self.assertEqual(target.read_text(encoding="utf-8"), "second\n")
        self.assertEqual(
            [path.name for path in sorted(self.tmp.iterdir())],
            ["artifact.json"],
            "an overwrite must not leave another file behind",
        )

    def test_write_text_atomic_leaves_no_temporary_file(self) -> None:
        target = self.tmp / "outbox" / "report.md"
        for index in range(3):
            paths.write_text_atomic(target, f"run {index}\n")
        self.assertEqual([path.name for path in sorted(target.parent.iterdir())], ["report.md"])

    def test_a_failed_replace_leaves_no_partial_file(self) -> None:
        target = self.tmp / "outbox" / "report.md"
        # errno 2 is exactly what a Windows folder protection policy surfaces: a
        # phantom FileNotFoundError on a directory that plainly exists.
        with mock.patch("os.replace", side_effect=OSError(2, "blocked by a folder policy")):
            result = paths.write_text_atomic(target, "content that must not survive\n")
        self.assertFalse(result["ok"], "a refused write must not report success")
        self.assertIn("FileNotFoundError", result["error"])
        self.assertFalse(target.exists(), "a failed write left a partial file")
        self.assertEqual(
            [path.name for path in sorted(target.parent.iterdir())],
            [],
            "a failed write left its temporary file behind",
        )

    def test_a_blocked_parent_is_reported_instead_of_raising(self) -> None:
        blocked = _unwritable(self.tmp) / "report.md"
        result = paths.write_text_atomic(blocked, "nothing lands here\n")
        self.assertFalse(result["ok"])
        self.assertTrue(result["error"])
        self.assertEqual(result["byte_count"], 0)
        self.assertFalse(blocked.exists())

    def test_write_text_atomic_refuses_a_non_string_payload(self) -> None:
        target = self.tmp / "report.md"
        result = paths.write_text_atomic(target, {"not": "a string"})
        self.assertFalse(result["ok"])
        self.assertFalse(target.exists())

    def test_write_json_atomic_round_trips_sorted_json(self) -> None:
        target = self.tmp / "evidence" / "2026-03-10.json"
        payload = {"schema": "ghoti_dispatch_evidence/1", "ok": True, "warn_sections": ["gmail"]}
        result = paths.write_json_atomic(target, payload)
        self.assertTrue(result["ok"], result["error"])
        text = target.read_text(encoding="utf-8")
        self.assertEqual(json.loads(text), payload)
        self.assertTrue(text.endswith("\n"))
        self.assertEqual(text, json.dumps(payload, indent=2, sort_keys=True) + "\n")

    def test_write_json_atomic_overwrites_cleanly(self) -> None:
        target = self.tmp / "artifact.latest.json"
        paths.write_json_atomic(target, {"generated_at": "2026-03-10T15:00:00Z"})
        paths.write_json_atomic(target, {"generated_at": "2026-03-11T15:00:00Z"})
        self.assertEqual(
            json.loads(target.read_text(encoding="utf-8")),
            {"generated_at": "2026-03-11T15:00:00Z"},
        )
        self.assertEqual([path.name for path in sorted(self.tmp.iterdir())], ["artifact.latest.json"])

    def test_write_json_atomic_refuses_an_unserializable_payload_and_writes_nothing(self) -> None:
        target = self.tmp / "evidence.json"
        result = paths.write_json_atomic(target, {"handle": object()})
        self.assertFalse(result["ok"], "an unserializable payload must not report success")
        self.assertIn("JSON", result["error"])
        self.assertFalse(target.exists())
        self.assertEqual([path.name for path in sorted(self.tmp.iterdir())], [])

    def test_an_existing_file_survives_a_refused_rewrite(self) -> None:
        target = self.tmp / "artifact.json"
        paths.write_json_atomic(target, {"generated_at": "2026-03-10T15:00:00Z"})
        original = target.read_bytes()
        result = paths.write_json_atomic(target, {"handle": object()})
        self.assertFalse(result["ok"])
        self.assertEqual(target.read_bytes(), original, "a refused rewrite destroyed the old file")


class WriteAccessDiagnosisTests(TempCaseMixin, unittest.TestCase):
    """The diagnosis names where writes work and whether a folder policy blocks the repo."""

    def _diagnose(self, *, repo_root: Path, runtime_root: Path) -> dict:
        with _environment(str(runtime_root)):
            return paths.diagnose_write_access(repo_root=repo_root)

    def test_a_writable_repository_is_not_a_suspected_folder_policy(self) -> None:
        repo = self.tmp / "repo"
        repo.mkdir()
        result = self._diagnose(repo_root=repo, runtime_root=self.tmp / "runtime")
        self.assertTrue(result["ok"], result["error"])
        self.assertIs(result["repo_writable"], True)
        self.assertIs(result["runtime_writable"], True)
        self.assertIs(result["cfa_suspected"], False)
        self.assertEqual(result["selected_source"], "env")

    def test_an_unwritable_repository_with_a_writable_runtime_is_a_suspected_folder_policy(self) -> None:
        blocked_repo = _unwritable(self.tmp, "repo_blocker.txt")
        result = self._diagnose(repo_root=blocked_repo, runtime_root=self.tmp / "runtime")
        self.assertIs(result["repo_writable"], False)
        self.assertIs(result["runtime_writable"], True)
        self.assertIs(result["cfa_suspected"], True)
        self.assertTrue(result["repo_write_reason"])
        self.assertTrue(result["remediation"])
        self.assertTrue(
            any(EXPECTED_ENV_VAR in line for line in result["remediation"]),
            result["remediation"],
        )

    def test_an_unwritable_runtime_root_is_reported_and_never_faked(self) -> None:
        repo = self.tmp / "repo"
        repo.mkdir()
        blocked = _unwritable(self.tmp, "runtime_blocker.txt")
        result = paths.diagnose_write_access(repo_root=repo, runtime_root=blocked)
        self.assertFalse(result["ok"], "a blocked runtime root must not report success")
        self.assertIs(result["runtime_writable"], False)
        self.assertIs(result["cfa_suspected"], False)
        self.assertTrue(result["error"])
        self.assertTrue(result["runtime_write_reason"])
        self.assertTrue(any(EXPECTED_ENV_VAR in line for line in result["remediation"]))

    def test_the_diagnosis_reports_every_documented_field(self) -> None:
        repo = self.tmp / "repo"
        repo.mkdir()
        result = self._diagnose(repo_root=repo, runtime_root=self.tmp / "runtime")
        for field in (
            "ok",
            "schema",
            "runtime_root",
            "repo_writable",
            "runtime_writable",
            "selected_source",
            "rejected",
            "cfa_suspected",
            "remediation",
        ):
            with self.subTest(field=field):
                self.assertIn(field, result)
        self.assertEqual(result["schema"], paths.ACCESS_SCHEMA)
        self.assertIsInstance(result["rejected"], list)
        self.assertIsInstance(result["remediation"], list)
        self.assertTrue(result["remediation"], "remediation must never be empty")
        for line in result["remediation"]:
            self.assertIsInstance(line, str)
            self.assertTrue(line.strip())

    def test_an_explicit_runtime_root_is_reported_as_an_override(self) -> None:
        repo = self.tmp / "repo"
        repo.mkdir()
        override = self.tmp / "explicit_runtime"
        with _environment(str(self.tmp / "ignored")):
            result = paths.diagnose_write_access(repo_root=repo, runtime_root=override)
        self.assertEqual(Path(result["runtime_root"]), override)
        self.assertEqual(result["selected_source"], "override")
        self.assertEqual(result["rejected"], [])

    def test_the_diagnosis_leaves_no_probe_file_behind(self) -> None:
        repo = self.tmp / "repo"
        repo.mkdir()
        runtime = self.tmp / "runtime"
        self._diagnose(repo_root=repo, runtime_root=runtime)
        self.assertEqual([path.name for path in sorted(repo.iterdir())], [])
        self.assertEqual([path.name for path in sorted(runtime.iterdir())], [])

    def test_a_missing_repository_directory_is_never_created(self) -> None:
        missing = self.tmp / "does_not_exist"
        self._diagnose(repo_root=missing, runtime_root=self.tmp / "runtime")
        self.assertFalse(missing.exists(), "diagnosing must never create the repository path")


class RuntimePathsSourceTests(unittest.TestCase):
    """The module stays local, standard-library only and blind to the environment."""

    def test_the_module_reads_no_environment_variable_other_than_the_runtime_root(self) -> None:
        self.assertEqual(SOURCE.count("os.environ"), 1, "exactly one environment read is allowed")
        reads = re.findall(r"os\.environ(?:\.get)?\s*[\(\[]\s*([^,)\]]+)", SOURCE)
        self.assertEqual(reads, ["RUNTIME_ROOT_ENV_VAR"])
        self.assertEqual(paths.RUNTIME_ROOT_ENV_VAR, EXPECTED_ENV_VAR)
        for banned in ("getenv", "environb", "expandvars", "putenv", "os.environ.copy"):
            with self.subTest(token=banned):
                self.assertNotIn(banned, SOURCE)
        for name in OTHER_ENV_NAMES:
            with self.subTest(env_var=name):
                self.assertNotIn(f'"{name}"', SOURCE)
                self.assertNotIn(f"'{name}'", SOURCE)

    def test_the_module_performs_no_network_import(self) -> None:
        for name in NETWORK_MODULES:
            pattern = re.compile(r"\b" + re.escape(name) + r"\b")
            with self.subTest(module=name):
                self.assertIsNone(pattern.search(SOURCE), f"paths.py references {name}")
                self.assertIs(hasattr(paths, name.split(".")[0]), False)

    def test_the_module_imports_only_the_standard_library(self) -> None:
        imported = set(re.findall(r"^\s*(?:from|import)\s+([A-Za-z_][A-Za-z0-9_.]*)", SOURCE, re.M))
        self.assertTrue(imported)
        self.assertTrue(
            imported.issubset(ALLOWED_IMPORTS), f"unexpected imports: {sorted(imported - ALLOWED_IMPORTS)}"
        )

    def test_the_module_spawns_no_process_and_drives_no_browser(self) -> None:
        for token in ("subprocess", "os.system", "os.popen", "webbrowser", "shell=True"):
            with self.subTest(token=token):
                self.assertNotIn(token, SOURCE)

    def test_the_module_hardcodes_no_absolute_user_path_or_secret(self) -> None:
        for label, pattern in FORBIDDEN_TEXT_PATTERNS:
            with self.subTest(pattern=label):
                match = pattern.search(SOURCE)
                self.assertIsNone(match, f"paths.py leaked {label}: {'' if match is None else match.group(0)}")

    def test_the_module_carries_no_ai_attribution(self) -> None:
        lowered = SOURCE.lower()
        for banned in ("generated with claude", "co-authored-by"):
            with self.subTest(marker=banned):
                self.assertNotIn(banned, lowered)
        readme = RUNTIME_README_PATH.read_text(encoding="utf-8").lower()
        for banned in ("generated with claude", "co-authored-by"):
            with self.subTest(marker=banned, file="README.md"):
                self.assertNotIn(banned, readme)


class RuntimePathsSafetyContractTests(TempCaseMixin, unittest.TestCase):
    """Every dict-returning entry point carries the shared safety block."""

    def _payloads(self) -> dict:
        root = self.tmp / "runtime"
        repo = self.tmp / "repo"
        repo.mkdir()
        with _environment(str(root)):
            return {
                "select_runtime_root": paths.select_runtime_root(),
                "ensure_runtime_dirs": paths.ensure_runtime_dirs(),
                "write_text_atomic": paths.write_text_atomic(root / "a.md", "text\n"),
                "write_json_atomic": paths.write_json_atomic(root / "a.json", {"ok": True}),
                "diagnose_write_access": paths.diagnose_write_access(repo_root=repo),
            }

    def test_every_payload_reports_ok_and_a_schema(self) -> None:
        for name, payload in self._payloads().items():
            with self.subTest(function=name):
                self.assertIsInstance(payload["ok"], bool)
                self.assertTrue(payload["schema"].endswith("/1"))
                self.assertTrue(payload["schema"].startswith("ghoti_runtime"))

    def test_every_payload_carries_the_safety_block(self) -> None:
        for name, payload in self._payloads().items():
            with self.subTest(function=name):
                for key in SAFETY_KEYS:
                    self.assertIn(key, payload, f"{name} is missing {key}")
                self.assertIs(payload["local_only"], True)
                self.assertIs(payload["network_used"], False)
                self.assertIs(payload["messages_sent"], False)
                self.assertIs(payload["content_posted"], False)
                self.assertIs(payload["credentials_used"], False)
                self.assertIs(payload["payments_or_ad_spend_used"], False)
                self.assertIs(payload["human_review_required"], True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
