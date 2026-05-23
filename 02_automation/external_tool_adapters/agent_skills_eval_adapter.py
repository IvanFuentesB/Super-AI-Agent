#!/usr/bin/env python3
"""agent-skills-eval adapter (N+4.9A) — PROMOTED, execution-capable SAFE adapter.

Ghoti-local adapter for agent-skills-eval (darkrishabh/agent-skills-eval).

N+4.8A created this as a static stub. N+4.9A promotes it to an execution-capable
adapter that can run a real LOCAL skill-evaluation workflow and produce useful
artifacts. It is still 100% safe:

  - local-only; standard library only
  - does NOT import or execute any external repo package or code
  - does NOT install dependencies
  - does NOT control the desktop, browser, or any live account/API
  - non-dry-run execution requires a human approval token

The evaluation uses Ghoti's own local skill-quality checklist. The sandboxed
agent-skills-eval repo may be read statically for inspiration only — never run.
"""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

# Marker: a promoted adapter is execution-capable and must NOT be regenerated
# back into a stub by external_tool_sandbox_manager.py --generate-adapters.
ADAPTER_PROMOTED = True

TOOL_KEY = "agent_skills_eval"
TOOL_NAME = "agent-skills-eval"
TOOL_SLUG = "darkrishabh/agent-skills-eval"
REQUIRES_HUMAN_APPROVAL = True

# Ghoti-local skill-quality checklist. Each dimension is detected statically in
# the skill text — no external code runs. (token list, weight, recommendation)
_EVAL_DIMENSIONS = [
    ("clarity", ["purpose", "goal", "summary", "overview"],
     "State a single, clear purpose for the skill."),
    ("safety_boundaries", ["safety", "boundary", "boundaries", "scope", "must not"],
     "Define explicit safety boundaries and out-of-scope behavior."),
    ("allowed_tools", ["allowed tool", "allowed:", "may use", "tools allowed", "permitted tool"],
     "List the exact tools the skill is allowed to use."),
    ("forbidden_actions", ["forbidden", "not allowed", "never", "do not", "prohibited"],
     "List forbidden actions the skill must never take."),
    ("approval_gates", ["approval", "approve", "human review", "sign-off", "gate"],
     "Define which steps require human approval."),
    ("testability", ["test", "validation", "verify", "validate", "check"],
     "Describe how the skill is tested / validated."),
    ("expected_outputs", ["expected output", "output:", "produces", "artifact", "deliverable"],
     "State the expected outputs / artifacts."),
    ("rollback_cleanup", ["rollback", "cleanup", "clean up", "undo", "revert"],
     "Describe rollback and cleanup behavior."),
    ("prompt_quality", [],
     "Improve structure: clear headings, bullet lists, and specific wording."),
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def status() -> dict:
    """Adapter status. Promoted: execution-capable but still approval-gated."""
    return {
        "tool": TOOL_NAME,
        "tool_key": TOOL_KEY,
        "slug": TOOL_SLUG,
        "adapter_kind": "execution_capable_safe_adapter",
        "promoted": True,
        "execution_capable": True,
        "dry_run_default": True,
        "wired": False,
        "runtime_wiring": "local_demo_only",
        "local_only": True,
        "external_code_imported": False,
        "external_code_executed": False,
        "installs_performed": False,
        "desktop_control_enabled": False,
        "live_api_enabled": False,
        "requires_human_approval": REQUIRES_HUMAN_APPROVAL,
    }


def capabilities() -> list:
    """Capabilities this adapter provides locally."""
    return [
        "local agent-skill quality evaluation (Ghoti checklist)",
        "skill clarity / safety-boundary / approval-gate scoring",
        "machine-readable skill score + recommendations",
        "local demo skill generation and evaluation",
    ]


def safety_gates() -> list:
    """Gates that hold for this adapter."""
    return [
        "human_approval_required",
        "sandbox_static_scan_reviewed",
        "no_external_code_execution",
        "no_dependency_install_without_approval",
        "no_desktop_control_without_approval",
        "no_live_api_calls_without_approval",
        "no_live_account_actions",
        "non_dry_run_requires_approval_token",
    ]


# ---------------------------------------------------------------------------
# Demo skill content
# ---------------------------------------------------------------------------

_DEMO_SKILL = """# Skill: Local Repository Markdown Link Auditor

## Purpose
A small supervised Ghoti skill that audits Markdown files in the repository for
broken relative links and reports them locally. It does not fix anything on its
own — it only produces a report for a human to act on.

## Allowed Tools
- Local filesystem read (repo-local Markdown files only)
- Local report writer (writes under 14_context/)

## Forbidden Actions
- No network access; no external API calls
- No file edits or deletes — read-only audit
- No desktop control, no browser automation
- No live account / posting / money actions

## Approval Gates
- The audit runs read-only and needs no approval.
- Any follow-up that edits files requires explicit human approval first.

## Testability
- Validated by a unit test that feeds known-good and known-broken Markdown
  fixtures and checks the reported counts.

## Expected Outputs
- A local Markdown report listing each file and any broken relative links.
- A machine-readable JSON summary with total/broken link counts.

## Rollback & Cleanup
- The skill only writes one report file; cleanup is deleting that report.
- No other state is changed, so rollback is trivial.
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _score_dimension(name: str, tokens: list, text_lower: str, raw_text: str) -> tuple:
    """Return (score_0_to_10, status_str) for one checklist dimension."""
    if name == "prompt_quality":
        headings = raw_text.count("\n#")
        bullets = sum(1 for ln in raw_text.splitlines() if ln.strip().startswith("- "))
        long_enough = len(raw_text) > 400
        if headings >= 3 and bullets >= 5 and long_enough:
            return 10, "pass"
        if headings >= 2 and bullets >= 2:
            return 6, "partial"
        return 0, "fail"
    matched = sum(1 for tok in tokens if tok in text_lower)
    if matched >= 2:
        return 10, "pass"
    if matched == 1:
        return 6, "partial"
    return 0, "fail"


def evaluate_skill_file(skill_path, output_dir, dry_run: bool = True) -> dict:
    """Evaluate a local skill Markdown file against the Ghoti skill checklist.

    Reads only the given local file. Runs no external code. Writes
    01_skill_evaluation.md and 02_skill_evaluation.json under output_dir.
    """
    output_dir = Path(output_dir)
    skill_path = Path(skill_path)
    try:
        raw = skill_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        return {"ok": False, "error": "could not read skill file: %s" % exc}

    text_lower = raw.lower()
    dimensions = []
    recommendations = []
    total = 0
    for name, tokens, rec in _EVAL_DIMENSIONS:
        score, state = _score_dimension(name, tokens, text_lower, raw)
        total += score
        dimensions.append({"dimension": name, "score": score, "max": 10, "status": state})
        if score < 10:
            recommendations.append(rec)

    overall = round(total / (len(_EVAL_DIMENSIONS) * 10) * 100)
    grade = "strong" if overall >= 85 else ("adequate" if overall >= 65 else "needs_work")

    eval_json = {
        "adapter": TOOL_KEY,
        "evaluator": "ghoti_local_skill_checklist",
        "skill_file": os.path.basename(str(skill_path)),
        "dry_run": bool(dry_run),
        "external_code_executed": False,
        "score": overall,
        "grade": grade,
        "dimensions": dimensions,
        "recommendations": recommendations,
        "generated_at": _now(),
    }

    md_lines = [
        "# Skill Evaluation — %s" % os.path.basename(str(skill_path)),
        "",
        "Evaluator: Ghoti local skill checklist (agent-skills-eval adapter).",
        "No external repo code was imported or executed.",
        "",
        "## Overall",
        "",
        "- Score: **%d / 100** (%s)" % (overall, grade),
        "- Dry run: %s" % bool(dry_run),
        "",
        "## Dimension scores",
        "",
        "| Dimension | Score | Status |",
        "| --- | --- | --- |",
    ]
    for d in dimensions:
        md_lines.append("| %s | %d/10 | %s |" % (d["dimension"], d["score"], d["status"]))
    md_lines += ["", "## Recommendations", ""]
    if recommendations:
        for rec in recommendations:
            md_lines.append("- %s" % rec)
    else:
        md_lines.append("- None — the skill meets every checklist dimension.")
    md_lines.append("")

    eval_md_path = output_dir / "01_skill_evaluation.md"
    eval_json_path = output_dir / "02_skill_evaluation.json"
    _write(eval_md_path, "\n".join(md_lines))
    _write(eval_json_path, json.dumps(eval_json, indent=2))

    return {
        "ok": True,
        "score": overall,
        "grade": grade,
        "dimensions": dimensions,
        "recommendations": recommendations,
        "dry_run": bool(dry_run),
        "external_code_executed": False,
        "artifacts": [
            str(eval_md_path).replace(os.sep, "/"),
            str(eval_json_path).replace(os.sep, "/"),
        ],
    }


def execute_demo(output_dir, approval_token=None, dry_run: bool = True, skill_path=None) -> dict:
    """Run the safe local demo: generate (or load) a demo skill, evaluate it,
    write a safety review. Writes 00_demo_skill.md, 01/02 (via
    evaluate_skill_file), and 03_safety_review.md under output_dir.

    If skill_path is given, that local file's content is used as the demo skill
    input; otherwise the adapter's built-in canonical demo skill is used.

    Non-dry-run execution requires a human approval token; the adapter itself
    does not validate the token (the approved_adapter_runner does) but records
    whether one was supplied.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    mode = "dry_run" if dry_run else "approved_execution"

    demo_path = output_dir / "00_demo_skill.md"
    content = _DEMO_SKILL
    if skill_path:
        try:
            loaded = Path(skill_path).read_text(encoding="utf-8", errors="ignore")
            if loaded.strip():
                content = loaded
        except Exception:
            content = _DEMO_SKILL
    _write(demo_path, content)

    evaluation = evaluate_skill_file(demo_path, output_dir, dry_run=dry_run)

    safety_path = output_dir / "03_safety_review.md"
    _write(safety_path, "\n".join([
        "# Adapter Demo Safety Review",
        "",
        "Adapter: %s (%s)" % (TOOL_NAME, TOOL_SLUG),
        "Mode: %s" % mode,
        "",
        "| Safety property | Status |",
        "| --- | --- |",
        "| External repo code imported | NO |",
        "| External repo code executed | NO |",
        "| Dependencies installed | NO |",
        "| Desktop control used | NO |",
        "| Live API / account calls | NO |",
        "| Network access | NO |",
        "| Files outside the run folder modified | NO |",
        "| Approval token supplied | %s |" % ("YES" if approval_token else "NO"),
        "| Non-dry-run requires approval token | YES |",
        "",
        "This demo ran only Ghoti-owned local adapter code over local files.",
        "",
    ]))

    return {
        "ok": bool(evaluation.get("ok")),
        "adapter": TOOL_KEY,
        "mode": mode,
        "dry_run": bool(dry_run),
        "approval_token_supplied": bool(approval_token),
        "score": evaluation.get("score"),
        "grade": evaluation.get("grade"),
        "recommendations": evaluation.get("recommendations", []),
        "external_code_executed": False,
        "external_repo_packages_imported": False,
        "installs_performed": False,
        "desktop_control_enabled": False,
        "live_api_used": False,
        "requires_human_approval": REQUIRES_HUMAN_APPROVAL,
        "artifacts": [
            str(demo_path).replace(os.sep, "/"),
            (evaluation.get("artifacts") or [None, None])[0],
            (evaluation.get("artifacts") or [None, None])[1],
            str(safety_path).replace(os.sep, "/"),
        ],
    }


if __name__ == "__main__":
    print(json.dumps({
        "status": status(),
        "capabilities": capabilities(),
        "safety_gates": safety_gates(),
    }, indent=2))
