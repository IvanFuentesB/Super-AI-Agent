#!/usr/bin/env python3
"""Pick a writable runtime root outside the repository and write generated Ghoti state there atomically."""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]

# The only environment variable this module is allowed to read. Nothing else in
# this file may consult the process environment, and no value other than the
# runtime root itself is ever reported back.
RUNTIME_ROOT_ENV_VAR = "GHOTI_RUNTIME_ROOT"

RUNTIME_VENDOR_DIR = "Ghoti"
RUNTIME_WORKSPACE_DIR = "AI_Managed_Only"

ROOT_SCHEMA = "ghoti_runtime_root/1"
DIRS_SCHEMA = "ghoti_runtime_dirs/1"
WRITE_SCHEMA = "ghoti_runtime_write/1"
ACCESS_SCHEMA = "ghoti_runtime_write_access/1"

# Generated state mirrors the repository layout so every path reported inside a
# generated file can stay repo-relative.
DISPATCH_REL_PARTS = ("14_context", "dispatch")
LOGS_REL_PARTS = ("05_logs",)
DISPATCH_ROOT_REL = "/".join(DISPATCH_REL_PARTS)

# Root selection order. The first candidate that actually accepts a probe file wins.
CANDIDATE_SOURCES = ("env", "localappdata", "temp")

_PROBE_PREFIX = ".ghoti_write_probe_"
_TEMP_PREFIX = ".ghoti_atomic_"
_TEMP_SUFFIX = ".tmp"


def _safety() -> dict:
    return {
        "local_only": True,
        "network_used": False,
        "scraping_used": False,
        "browser_used": False,
        "account_actions_used": False,
        "messages_sent": False,
        "content_posted": False,
        "payments_or_ad_spend_used": False,
        "credentials_used": False,
        "human_review_required": True,
    }


def _workspace(base: Path) -> Path:
    return Path(base) / RUNTIME_VENDOR_DIR / RUNTIME_WORKSPACE_DIR


def _local_app_data_dir() -> Path:
    """Return the per-user local application data directory without reading the environment."""
    home = Path.home()
    if os.name == "nt":
        return home / "AppData" / "Local"
    return home / ".local" / "share"


def _temp_dir() -> Path:
    """Return the per-user temporary directory without reading the environment."""
    return Path(tempfile.gettempdir())


def _env_runtime_root() -> Path | None:
    """Return the operator-supplied runtime root, or None when it is unset or blank."""
    raw = os.environ.get(RUNTIME_ROOT_ENV_VAR)
    if not isinstance(raw, str) or not raw.strip():
        return None
    return Path(raw.strip()).expanduser()


def _candidates() -> list[tuple[str, Path | None]]:
    return [
        ("env", _env_runtime_root()),
        ("localappdata", _workspace(_local_app_data_dir())),
        ("temp", _workspace(_temp_dir())),
    ]


def _probe_writable(path: Path, *, create: bool = True) -> tuple[bool, str | None]:
    """Prove writability by creating and deleting a probe file. Nothing is assumed."""
    target = Path(path)
    if create:
        try:
            target.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            return False, f"directory could not be created ({type(exc).__name__})"
    elif not target.is_dir():
        return False, "directory does not exist"
    probe = target / f"{_PROBE_PREFIX}{uuid.uuid4().hex}"
    try:
        with open(probe, "wb") as handle:
            handle.write(b"ghoti write probe\n")
    except OSError as exc:
        return False, f"probe file could not be created ({type(exc).__name__})"
    try:
        probe.unlink()
    except OSError:  # the write succeeded, so the location is writable either way
        pass
    return True, None


def select_runtime_root() -> dict:
    """Choose the first writable runtime root and name every candidate that was rejected."""
    rejected: list[dict] = []
    for source, candidate in _candidates():
        if candidate is None:
            rejected.append(
                {
                    "source": source,
                    "path": None,
                    "reason": f"{RUNTIME_ROOT_ENV_VAR} is not set",
                }
            )
            continue
        writable, reason = _probe_writable(candidate)
        if writable:
            return {
                "ok": True,
                "schema": ROOT_SCHEMA,
                "error": None,
                "runtime_root": str(candidate),
                "selected_source": source,
                "rejected": rejected,
                "candidate_sources": list(CANDIDATE_SOURCES),
                **_safety(),
            }
        rejected.append({"source": source, "path": str(candidate), "reason": reason})
    return {
        "ok": False,
        "schema": ROOT_SCHEMA,
        "error": "no candidate runtime root accepted a probe file",
        "runtime_root": str(_workspace(_temp_dir())),
        "selected_source": None,
        "rejected": rejected,
        "candidate_sources": list(CANDIDATE_SOURCES),
        **_safety(),
    }


def get_runtime_root(root: Path | str | None = None) -> Path:
    """Return the runtime root: the explicit override when given, else the first writable candidate."""
    if root is not None:
        return Path(root)
    return Path(select_runtime_root()["runtime_root"])


def get_dispatch_runtime_root(runtime_root: Path | str | None = None) -> Path:
    """Return the dispatch state root, mirroring the repository's dispatch folder name."""
    return get_runtime_root(runtime_root).joinpath(*DISPATCH_REL_PARTS)


def get_dispatch_outbox_dir(runtime_root: Path | str | None = None) -> Path:
    """Return the directory that holds generated Markdown reports."""
    return get_dispatch_runtime_root(runtime_root) / "outbox"


def get_dispatch_artifacts_dir(runtime_root: Path | str | None = None) -> Path:
    """Return the directory that holds generated live artifacts."""
    return get_dispatch_runtime_root(runtime_root) / "artifacts"


def get_dispatch_evidence_dir(runtime_root: Path | str | None = None) -> Path:
    """Return the directory that holds generated evidence records."""
    return get_dispatch_runtime_root(runtime_root) / "evidence"


def get_logs_dir(runtime_root: Path | str | None = None) -> Path:
    """Return the runtime log directory."""
    return get_runtime_root(runtime_root).joinpath(*LOGS_REL_PARTS)


def runtime_directories(runtime_root: Path | str | None = None) -> list[Path]:
    """Return every directory the runtime owns, parents first."""
    root = get_runtime_root(runtime_root)
    return [
        root,
        get_dispatch_runtime_root(root),
        get_dispatch_outbox_dir(root),
        get_dispatch_artifacts_dir(root),
        get_dispatch_evidence_dir(root),
        get_logs_dir(root),
    ]


def ensure_runtime_dirs(runtime_root: Path | str | None = None) -> dict:
    """Create every runtime directory. Calling this twice creates nothing the second time."""
    root = get_runtime_root(runtime_root)
    created: list[str] = []
    existing: list[str] = []
    failed: list[dict] = []
    for target in runtime_directories(root):
        already = target.is_dir()
        try:
            target.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            failed.append({"path": str(target), "reason": f"{type(exc).__name__}"})
            continue
        (existing if already else created).append(str(target))
    return {
        "ok": not failed,
        "schema": DIRS_SCHEMA,
        "error": None if not failed else "one or more runtime directories could not be created",
        "runtime_root": str(root),
        "created": created,
        "existing": existing,
        "failed": failed,
        **_safety(),
    }


def _write_result(ok: bool, path: Path, byte_count: int, error: str | None) -> dict:
    return {
        "ok": ok,
        "schema": WRITE_SCHEMA,
        "error": error,
        "path": str(path),
        "byte_count": byte_count,
        **_safety(),
    }


def write_text_atomic(path: Path | str, content: str) -> dict:
    """Write ``content`` to ``path`` through a same-directory temp file and one ``os.replace``."""
    target = Path(path)
    if not isinstance(content, str):
        return _write_result(False, target, 0, "content must be a string")
    data = content.encode("utf-8")
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return _write_result(False, target, 0, f"parent directory unavailable ({type(exc).__name__})")
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "wb",
            dir=target.parent,
            prefix=_TEMP_PREFIX,
            suffix=_TEMP_SUFFIX,
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, target)
    except OSError as exc:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except OSError:
                pass
        return _write_result(False, target, 0, f"write failed ({type(exc).__name__})")
    return _write_result(True, target, len(data), None)


def write_json_atomic(path: Path | str, payload: object) -> dict:
    """Serialize ``payload`` first, then write it atomically. A bad payload writes nothing."""
    target = Path(path)
    try:
        content = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    except (TypeError, ValueError) as exc:
        return _write_result(False, target, 0, f"payload is not JSON serializable ({type(exc).__name__})")
    return write_text_atomic(target, content)


def _remediation(*, repo_writable: bool, runtime_writable: bool, cfa_suspected: bool) -> list[str]:
    if cfa_suspected:
        return [
            "keep generated state in the runtime root; the repository stays the source of truth for "
            "checked-in files only",
            "to write generated files inside the repository again, allow this python interpreter through "
            "the operating-system folder protection policy",
            f"or set {RUNTIME_ROOT_ENV_VAR} to a folder outside the protected tree",
        ]
    if not runtime_writable:
        return [
            f"set {RUNTIME_ROOT_ENV_VAR} to a folder this account can write to",
            "check the free disk space and the folder permissions of the reported runtime root",
            "no elevated or administrator rights are required or requested",
        ]
    if not repo_writable:
        return [
            "the repository path does not exist or is not a directory; check the repo_root that was passed in",
            "generated state is unaffected: it is written to the runtime root",
        ]
    return ["no action needed; both the repository and the runtime root accept writes"]


def diagnose_write_access(
    *,
    repo_root: Path | str | None = None,
    runtime_root: Path | str | None = None,
) -> dict:
    """Report where generated state can be written and whether a folder policy blocks the repository."""
    repo = Path(repo_root) if repo_root is not None else REPO_ROOT
    if runtime_root is not None:
        root = Path(runtime_root)
        selected_source = "override"
        rejected: list[dict] = []
    else:
        selection = select_runtime_root()
        root = Path(selection["runtime_root"])
        selected_source = selection["selected_source"]
        rejected = selection["rejected"]
    repo_writable, repo_reason = _probe_writable(repo, create=False)
    runtime_writable, runtime_reason = _probe_writable(root)
    # A repository that refuses new files while a sibling location accepts them is the
    # signature of an operating-system folder protection policy, not of a code defect.
    cfa_suspected = bool(runtime_writable and not repo_writable)
    return {
        "ok": bool(runtime_writable),
        "schema": ACCESS_SCHEMA,
        "error": None if runtime_writable else "the runtime root refused a probe file",
        "repo_root": str(repo),
        "runtime_root": str(root),
        "repo_writable": bool(repo_writable),
        "runtime_writable": bool(runtime_writable),
        "repo_write_reason": repo_reason,
        "runtime_write_reason": runtime_reason,
        "selected_source": selected_source,
        "rejected": rejected,
        "cfa_suspected": cfa_suspected,
        "remediation": _remediation(
            repo_writable=repo_writable,
            runtime_writable=runtime_writable,
            cfa_suspected=cfa_suspected,
        ),
        **_safety(),
    }
