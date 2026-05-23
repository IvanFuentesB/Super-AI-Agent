#!/usr/bin/env python3
"""Approved Adapter Runner (N+4.9A) — first approved adapter execution demo.

Moves Ghoti from "static sandbox/adapter stubs exist" to "one safe adapter can
execute a real LOCAL demo workflow and produce a useful artifact."

It runs ONLY Ghoti-owned adapter code, over local files, to produce local
reports. It NEVER: installs dependencies, imports/executes external repo code,
controls the desktop, calls a live API, or performs any live account action.

Approval model:
  - --dry-run executes the demo with no approval token (artifacts marked dry_run)
  - --execute-approved without --dry-run REQUIRES a valid --approval-token
  - --create-approval issues a one-time token (only its SHA-256 hash is stored)
"""
import argparse
import hashlib
import importlib.util
import json
import os
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
ADAPTERS_DIR = REPO_ROOT / "02_automation" / "external_tool_adapters"
EXEC_DIR = REPO_ROOT / "14_context" / "adapter_execution"
APPROVALS_DIR = EXEC_DIR / "approvals"
RUNS_DIR = EXEC_DIR / "runs"
LATEST_FILE = EXEC_DIR / "latest_adapter_run.json"

RUNNER_VERSION = "1.0.0"
MILESTONE = "N+4.9A"
DEFAULT_ADAPTER = "agent_skills_eval"

# Approved adapter catalog. Only agent_skills_eval is execution-approved now;
# the others are listed but NOT executable (each needs its own approval step).
ADAPTER_CATALOG = [
    {
        "key": "agent_skills_eval",
        "name": "agent-skills-eval",
        "adapter_file": "agent_skills_eval_adapter.py",
        "execution_approved": True,
        "reason": "Safe local skill evaluation — no desktop control, no external code, no live API.",
    },
    {
        "key": "the_agency",
        "name": "TheAgency",
        "adapter_file": "the_agency_adapter.py",
        "execution_approved": False,
        "reason": "Multi-agent orchestration — not yet approved for execution.",
    },
    {
        "key": "vouch",
        "name": "Vouch Protocol",
        "adapter_file": "vouch_adapter.py",
        "execution_approved": False,
        "reason": "Identity / attestation protocol — not yet approved for execution.",
    },
    {
        "key": "ui_tars_model",
        "name": "UI-TARS Model",
        "adapter_file": "ui_tars_model_adapter.py",
        "execution_approved": False,
        "reason": "GUI model — not yet approved for execution.",
    },
    {
        "key": "ui_tars_desktop",
        "name": "UI-TARS Desktop",
        "adapter_file": "ui_tars_desktop_adapter.py",
        "execution_approved": False,
        "reason": "Desktop click/type/screenshot control — explicitly NOT approved for execution.",
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _is_repo_local(target) -> bool:
    try:
        resolved = Path(str(target)).resolve()
        repo = REPO_ROOT.resolve()
        return resolved == repo or repo in resolved.parents
    except Exception:
        return False


def _repo_rel(target) -> str:
    try:
        return str(Path(target).resolve().relative_to(REPO_ROOT.resolve())).replace(os.sep, "/")
    except Exception:
        return str(target)


def _catalog_for(key: str):
    for entry in ADAPTER_CATALOG:
        if entry["key"] == key:
            return entry
    return None


def _load_adapter(adapter_file: str):
    """Import a Ghoti-owned adapter module by file path. Adapters are Ghoti
    code; no external repo package is imported."""
    path = ADAPTERS_DIR / adapter_file
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location("ghoti_adapter_" + adapter_file[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _latest_run() -> dict:
    return _read_json(LATEST_FILE)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_status() -> dict:
    return {
        "ok": True,
        "runner": "approved_adapter_runner",
        "runner_version": RUNNER_VERSION,
        "milestone": MILESTONE,
        "execution_mode": "approval_gated_local_only",
        "default_adapter": DEFAULT_ADAPTER,
        "external_code_executed": False,
        "external_repo_packages_imported": False,
        "installs_performed": False,
        "desktop_control_enabled": False,
        "live_api_enabled": False,
        "human_approval_required": True,
        "non_dry_run_requires_approval_token": True,
        "approvals_dir": _repo_rel(APPROVALS_DIR),
        "runs_dir": _repo_rel(RUNS_DIR),
        "adapters": [
            {"key": e["key"], "name": e["name"], "execution_approved": e["execution_approved"]}
            for e in ADAPTER_CATALOG
        ],
        "latest_run": _latest_run() or None,
        "generated_at": _now(),
    }


def cmd_list_adapters() -> dict:
    adapters = []
    for entry in ADAPTER_CATALOG:
        item = {
            "key": entry["key"],
            "name": entry["name"],
            "adapter_file": _repo_rel(ADAPTERS_DIR / entry["adapter_file"]),
            "execution_approved": entry["execution_approved"],
            "reason": entry["reason"],
        }
        mod = None
        try:
            mod = _load_adapter(entry["adapter_file"])
        except Exception:
            mod = None
        if mod is not None and hasattr(mod, "status"):
            try:
                st = mod.status()
                item["adapter_status"] = {
                    "execution_capable": bool(st.get("execution_capable", False)),
                    "requires_human_approval": bool(st.get("requires_human_approval", True)),
                    "wired": bool(st.get("wired", False)),
                }
            except Exception:
                item["adapter_status"] = None
        adapters.append(item)
    return {
        "ok": True,
        "action": "list-adapters",
        "default_adapter": DEFAULT_ADAPTER,
        "adapters": adapters,
        "generated_at": _now(),
    }


def cmd_create_approval(adapter_key: str) -> dict:
    entry = _catalog_for(adapter_key)
    if entry is None:
        return {"ok": False, "error": "adapter '%s' is not in the approved catalog" % adapter_key}
    if not entry["execution_approved"]:
        return {"ok": False, "error": "adapter '%s' is not execution-approved" % adapter_key}
    if not _is_repo_local(APPROVALS_DIR):
        return {"ok": False, "error": "approvals dir is outside the repo root"}
    APPROVALS_DIR.mkdir(parents=True, exist_ok=True)

    token = secrets.token_hex(16)
    ts = _now()
    approval_id = "approval-" + secrets.token_hex(6)
    record = {
        "approval_id": approval_id,
        "adapter": adapter_key,
        "status": "approved",
        "token_hash": _token_hash(token),
        "token_algo": "sha256",
        "created_at": ts,
        "note": "Single-use local approval. Only the SHA-256 hash of the token is stored.",
    }
    record_path = APPROVALS_DIR / ("%s_%s.json" % (ts, adapter_key))
    record_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "action": "create-approval",
        "approval_id": approval_id,
        "adapter": adapter_key,
        "approval_record": _repo_rel(record_path),
        # The raw token is shown ONCE here; only its hash is persisted.
        "approval_token": token,
        "token_note": "Store this token now — it is not recoverable and is required for non-dry-run execution.",
        "generated_at": ts,
    }


def _verify_token(adapter_key: str, token: str) -> bool:
    if not token:
        return False
    wanted = _token_hash(token)
    try:
        for rec_path in APPROVALS_DIR.glob("*.json"):
            rec = _read_json(rec_path)
            if (
                rec.get("adapter") == adapter_key
                and rec.get("status") == "approved"
                and rec.get("token_hash") == wanted
            ):
                return True
    except Exception:
        return False
    return False


def cmd_execute_approved(adapter_key, dry_run, approval_token, demo_skill, output_dir) -> dict:
    entry = _catalog_for(adapter_key)
    if entry is None:
        return {"ok": False, "error": "adapter '%s' is not in the approved catalog" % adapter_key}
    if not entry["execution_approved"]:
        return {"ok": False, "error": "adapter '%s' is not execution-approved" % adapter_key}

    approval_verified = False
    if not dry_run:
        approval_verified = _verify_token(adapter_key, approval_token or "")
        if not approval_verified:
            return {
                "ok": False,
                "action": "execute-approved",
                "adapter": adapter_key,
                "error": "approval token required for non-dry-run execution "
                         "(supply --approval-token from --create-approval, or use --dry-run)",
                "dry_run": False,
                "generated_at": _now(),
            }

    adapter = _load_adapter(entry["adapter_file"])
    if adapter is None or not hasattr(adapter, "execute_demo"):
        return {"ok": False, "error": "adapter %s does not expose execute_demo()" % adapter_key}

    # Resolve an optional caller-supplied skill file (must be repo-local).
    skill_path = None
    if demo_skill:
        candidate = Path(str(demo_skill).replace("/", os.sep))
        if not candidate.is_absolute():
            candidate = REPO_ROOT / candidate
        if _is_repo_local(candidate) and candidate.is_file():
            skill_path = str(candidate)

    # Resolve the run folder (always repo-local).
    base_runs = RUNS_DIR
    if output_dir:
        cand = Path(str(output_dir).replace("/", os.sep))
        if not cand.is_absolute():
            cand = REPO_ROOT / cand
        if _is_repo_local(cand):
            base_runs = cand
    ts = _now()
    run_id = "%s_%s" % (ts, adapter_key)
    run_dir = base_runs / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = adapter.execute_demo(
            str(run_dir), approval_token=approval_token, dry_run=dry_run, skill_path=skill_path,
        )
    except Exception as exc:
        return {"ok": False, "error": "adapter execution error: %s" % exc, "run_id": run_id}

    mode = "dry_run" if dry_run else "approved_execution"
    artifacts = [a for a in (result.get("artifacts") or []) if a]

    manifest = {
        "milestone": MILESTONE,
        "runner": "approved_adapter_runner",
        "adapter": adapter_key,
        "run_id": run_id,
        "run_dir": _repo_rel(run_dir),
        "mode": mode,
        "dry_run": bool(dry_run),
        "approval_token_supplied": bool(approval_token),
        "approval_verified": bool(approval_verified),
        "external_code_executed": False,
        "external_repo_packages_imported": False,
        "installs_performed": False,
        "desktop_control_enabled": False,
        "live_api_used": False,
        "evaluation_score": result.get("score"),
        "evaluation_grade": result.get("grade"),
        "artifacts": [_repo_rel(a) for a in artifacts],
        "generated_at": ts,
    }
    manifest_path = run_dir / "04_execution_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    next_steps_path = run_dir / "05_human_next_steps.md"
    next_steps_path.write_text("\n".join([
        "# Human Next Steps — %s adapter run" % adapter_key,
        "",
        "Run: `%s`  (mode: %s)" % (run_id, mode),
        "Evaluation score: %s / 100 (%s)" % (result.get("score"), result.get("grade")),
        "",
        "## What happened",
        "",
        "- The %s adapter ran a LOCAL skill evaluation and wrote artifacts below." % adapter_key,
        "- No external repo code ran. No installs. No desktop control. No live API.",
        "",
        "## Artifacts",
        "",
    ] + ["- `%s`" % _repo_rel(a) for a in artifacts] + [
        "- `%s`" % _repo_rel(manifest_path),
        "",
        "## Decide",
        "",
        "- [ ] Review `01_skill_evaluation.md` and the recommendations.",
        "- [ ] If you want a non-dry-run execution, run `--create-approval` and",
        "      re-run with `--execute-approved --approval-token <token>`.",
        "- [ ] No external tool is runtime-wired until you explicitly approve it.",
        "",
    ]), encoding="utf-8")

    full_artifacts = [_repo_rel(a) for a in artifacts] + [
        _repo_rel(manifest_path), _repo_rel(next_steps_path),
    ]

    latest = {
        "adapter": adapter_key,
        "run_id": run_id,
        "run_dir": _repo_rel(run_dir),
        "mode": mode,
        "evaluation_score": result.get("score"),
        "evaluation_grade": result.get("grade"),
        "artifacts": full_artifacts,
        "generated_at": ts,
    }
    try:
        EXEC_DIR.mkdir(parents=True, exist_ok=True)
        LATEST_FILE.write_text(json.dumps(latest, indent=2), encoding="utf-8")
    except Exception:
        pass

    return {
        "ok": bool(result.get("ok")),
        "action": "execute-approved",
        "adapter": adapter_key,
        "run_id": run_id,
        "run_dir": _repo_rel(run_dir),
        "mode": mode,
        "dry_run": bool(dry_run),
        "approval_verified": bool(approval_verified),
        "evaluation_score": result.get("score"),
        "evaluation_grade": result.get("grade"),
        "recommendations": result.get("recommendations", []),
        "external_code_executed": False,
        "installs_performed": False,
        "desktop_control_enabled": False,
        "desktop_control": False,
        "live_api_used": False,
        "live_api": False,
        "artifacts": full_artifacts,
        "generated_at": ts,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Approved Adapter Runner (N+4.9A) — safe local adapter execution.",
    )
    parser.add_argument("--status", action="store_true", help="show runner status")
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    parser.add_argument("--list-adapters", action="store_true", help="list the approved adapter catalog")
    parser.add_argument("--create-approval", action="store_true", help="issue a one-time approval token")
    parser.add_argument("--execute-approved", action="store_true", help="execute the adapter demo")
    parser.add_argument("--adapter", default=DEFAULT_ADAPTER, help="adapter key (default agent_skills_eval)")
    parser.add_argument("--demo-skill", default=None, help="optional repo-local skill file to evaluate")
    parser.add_argument("--output-dir", default=None, help="optional repo-local run output dir")
    parser.add_argument("--approval-token", default=None, help="approval token (required for non-dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="dry-run execution (no token required)")
    parser.add_argument("--no-external-code", action="store_true", default=True,
                        help="never run external repo code (always enforced)")
    args = parser.parse_args(argv)

    try:
        if args.create_approval:
            result = cmd_create_approval(args.adapter)
        elif args.execute_approved:
            result = cmd_execute_approved(
                args.adapter, args.dry_run, args.approval_token, args.demo_skill, args.output_dir,
            )
        elif args.list_adapters:
            result = cmd_list_adapters()
        else:
            result = cmd_status()
    except Exception as exc:
        result = {"ok": False, "error": "runner error: %s" % exc, "generated_at": _now()}

    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
