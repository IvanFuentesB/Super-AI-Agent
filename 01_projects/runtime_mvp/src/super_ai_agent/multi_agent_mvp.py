"""Native Ghoti multi-agent MVP.

This runner is intentionally small, local, and deterministic. It proves that
Ghoti can schedule several named agents concurrently, write visible artifacts,
and maintain compact shared memory without external services or autonomous
execution.
"""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[4]
RUNS_ROOT = REPO_ROOT / "05_logs" / "multi_agent_runs"
SHARED_MEMORY_PATH = REPO_ROOT / "14_context" / "multi_agent_shared_memory.json"

BLOCKED_TASK_PATTERNS = {
    "external posting/outreach": re.compile(r"\b(post|dm|email|outreach|message)\b", re.I),
    "paid service connection": re.compile(r"\b(paid|billing|subscription|api key|cloud connect)\b", re.I),
    "purchase/trade/money movement": re.compile(r"\b(purchase|buy|sell|trade|invest|payment|wire)\b", re.I),
    "legal/tax filing": re.compile(r"\b(legal filing|tax filing|permit filing|court filing)\b", re.I),
    "cap bypass / usage-limit evasion": re.compile(
        r"\b(cap bypass|quota bypass|usage[- ]limit evasion|fake account|ban evasion)\b",
        re.I,
    ),
    "third-party install/clone/build": re.compile(r"\b(git clone|npm install|pip install|cargo build)\b", re.I),
    "outside repo root": re.compile(r"\b(outside repo|system32|users\\|/etc/|/var/)\b", re.I),
}


@dataclass(slots=True)
class AgentSpec:
    id: str
    role: str
    task: str
    allowed_tools: list[str] = field(default_factory=lambda: ["read_repo_docs", "write_artifact"])
    risk_level: str = "low"
    status: str = "pending"


@dataclass(slots=True)
class AgentResult:
    agent_id: str
    status: str
    summary: str
    artifacts: list[str]
    memory_updates: dict[str, Any]
    errors: list[str]
    started_at: str
    finished_at: str


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_id_now() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def repo_path(relative_path: str) -> Path:
    path = (REPO_ROOT / relative_path).resolve()
    if not path.is_relative_to(REPO_ROOT):
        raise ValueError(f"path escapes repo root: {relative_path}")
    return path


def read_text(relative_path: str, max_chars: int = 16000) -> str:
    path = repo_path(relative_path)
    if not path.exists():
        return f"[missing file: {relative_path}]"
    return path.read_text(encoding="utf-8", errors="replace")[:max_chars]


def compact_lines(text: str, keywords: list[str], limit: int = 8) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or len(line) > 240:
            continue
        if any(keyword.lower() in line.lower() for keyword in keywords):
            lines.append(line)
        if len(lines) >= limit:
            break
    return lines


def default_shared_memory() -> dict[str, Any]:
    return {
        "project_truth": [
            "Ghoti is local-first, supervised, and approval-gated.",
            "External repos/tools are reference-only unless explicitly approved and integrated later.",
            "Observations and model outputs do not authorize actions.",
        ],
        "current_priorities": [
            "Prove native multi-agent coordination with compact memory.",
            "Build ActionIntent and CapabilityAdapter before external adapters.",
        ],
        "blocked_actions": [
            "autonomous posting/outreach",
            "paid service connection",
            "purchases/trades/money movement",
            "legal/tax filings",
            "cap bypass or usage-limit evasion",
            "unapproved third-party clone/install/build",
        ],
        "candidate_tools": {
            "ruflo": "research_only",
            "auto_browser": "best_next_external_browser_candidate",
            "obscura": "research_only_do_not_integrate_now",
            "gemma_ollama": "diagnostic_only_no_model_confirmed",
        },
        "compact_findings": [],
        "last_updated": utc_now(),
    }


def load_shared_memory() -> dict[str, Any]:
    if not SHARED_MEMORY_PATH.exists():
        return default_shared_memory()
    try:
        return json.loads(SHARED_MEMORY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        fallback = default_shared_memory()
        fallback["compact_findings"].append(
            {
                "source": "memory-agent",
                "finding": "Previous shared memory JSON was unreadable; started from safe defaults.",
            }
        )
        return fallback


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp_path.replace(path)


def write_markdown(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = [f"# {title}", "", *lines, ""]
    path.write_text("\n".join(body), encoding="utf-8")


def safety_check(spec: AgentSpec) -> str | None:
    task = f"{spec.role} {spec.task}"
    for reason, pattern in BLOCKED_TASK_PATTERNS.items():
        if pattern.search(task):
            return reason
    return None


async def run_agent(spec: AgentSpec, run_dir: Path, memory: dict[str, Any]) -> AgentResult:
    started_at = utc_now()
    await asyncio.sleep(0)  # Explicit scheduling point so all agents enter the event loop.

    blocked_reason = safety_check(spec)
    artifact_rel = f"05_logs/multi_agent_runs/{run_dir.name}/agents/{spec.id}.md"
    artifact_path = run_dir / "agents" / f"{spec.id}.md"

    if blocked_reason:
        finished_at = utc_now()
        result = AgentResult(
            agent_id=spec.id,
            status="skipped",
            summary=f"Skipped by safety gate: {blocked_reason}.",
            artifacts=[artifact_rel],
            memory_updates={},
            errors=[blocked_reason],
            started_at=started_at,
            finished_at=finished_at,
        )
        write_markdown(
            artifact_path,
            f"{spec.role} ({spec.id})",
            [
                f"- Status: skipped",
                f"- Safety gate: {blocked_reason}",
                f"- Task: {spec.task}",
            ],
        )
        write_json(run_dir / "agents" / f"{spec.id}.json", asdict(result))
        return result

    handlers = {
        "ruflo-review-agent": agent_ruflo_review,
        "browser-candidate-agent": agent_browser_candidate,
        "memory-agent": agent_memory,
        "token-saver-agent": agent_token_saver,
        "implementation-planner-agent": agent_implementation_planner,
    }
    handler = handlers.get(spec.id, agent_generic)

    try:
        summary, markdown_lines, memory_updates = await handler(spec, memory)
        status = "done"
        errors: list[str] = []
    except Exception as exc:  # pragma: no cover - preserved for robust CLI behavior.
        summary = f"Agent failed: {exc}"
        markdown_lines = [f"- Status: failed", f"- Error: {exc}"]
        memory_updates = {}
        status = "failed"
        errors = [str(exc)]

    finished_at = utc_now()
    write_markdown(artifact_path, f"{spec.role} ({spec.id})", markdown_lines)
    result = AgentResult(
        agent_id=spec.id,
        status=status,
        summary=summary,
        artifacts=[artifact_rel],
        memory_updates=memory_updates,
        errors=errors,
        started_at=started_at,
        finished_at=finished_at,
    )
    write_json(run_dir / "agents" / f"{spec.id}.json", asdict(result))
    return result


async def agent_ruflo_review(spec: AgentSpec, memory: dict[str, Any]) -> tuple[str, list[str], dict[str, Any]]:
    audit = read_text("14_context/ruflo_read_only_evaluation.md")
    focused = compact_lines(audit, ["Final Verdict", "research only", "Security", "not_runtime_wired", "API key"], 7)
    summary = "RUFLO remains architecture-reference only; do not install or wire before a source/dependency audit."
    lines = [
        "- Status: done",
        f"- Task: {spec.task}",
        "- Safe next step: keep RUFLO research-only; mine architecture patterns, not runtime behavior.",
        "- Key compact evidence:",
        *[f"  - {line}" for line in focused],
    ]
    return summary, lines, {
        "candidate_tools": {"ruflo": "architecture_reference_research_only"},
        "compact_findings": [
            {
                "source": spec.id,
                "finding": "RUFLO is strategically relevant but too high-risk for runtime wiring without isolated audit.",
            }
        ],
    }


async def agent_browser_candidate(
    spec: AgentSpec, memory: dict[str, Any]
) -> tuple[str, list[str], dict[str, Any]]:
    audit = read_text("14_context/external_operator_candidates_audit.md")
    focused = compact_lines(audit, ["Auto Browser", "Obscura", "Verdict", "approval", "stealth"], 9)
    summary = "Auto Browser is the best future browser candidate; Obscura remains research-only due stealth/scraping posture."
    lines = [
        "- Status: done",
        f"- Task: {spec.task}",
        "- Safe next step: build Ghoti ActionIntent first, then evaluate Auto Browser in isolation if approved.",
        "- Key compact evidence:",
        *[f"  - {line}" for line in focused],
    ]
    return summary, lines, {
        "candidate_tools": {
            "auto_browser": "best_next_external_browser_candidate_after_action_intent",
            "obscura": "research_only_do_not_integrate_now",
        },
        "compact_findings": [
            {
                "source": spec.id,
                "finding": "Auto Browser aligns best with supervised browser control; Obscura should not be first adapter.",
            }
        ],
    }


async def agent_memory(spec: AgentSpec, memory: dict[str, Any]) -> tuple[str, list[str], dict[str, Any]]:
    summary = "Shared memory should stay compact, status-labeled, and limited to durable truths."
    lines = [
        "- Status: done",
        f"- Task: {spec.task}",
        "- Memory update strategy: merge short findings; do not paste giant docs into memory.",
        "- Current durable truth: external tools remain reference-only until explicit approval.",
    ]
    return summary, lines, {
        "project_truth": [
            "Native multi-agent MVP is deterministic and repo-local.",
            "Run artifacts are visible under 05_logs/multi_agent_runs.",
        ],
        "compact_findings": [
            {
                "source": spec.id,
                "finding": "Compact shared memory should carry decisions and pointers, not full transcripts.",
            }
        ],
    }


async def agent_token_saver(spec: AgentSpec, memory: dict[str, Any]) -> tuple[str, list[str], dict[str, Any]]:
    skills = read_text("14_context/ghoti_skills_strategy.md")
    focused = compact_lines(skills, ["token", "handoff", "skill", "memory", "Codex"], 8)
    summary = "Token savings should come from compaction, file references, small agent tasks, and resumable handoffs."
    lines = [
        "- Status: done",
        f"- Task: {spec.task}",
        "- Allowed token-saving patterns: compact memory, checkpoints, short handoffs, file references.",
        "- Forbidden: provider quota/cap bypass, fake accounts, or hidden usage evasion.",
        "- Supporting notes:",
        *[f"  - {line}" for line in focused],
    ]
    return summary, lines, {
        "current_priorities": [
            "Use compact file-based memory instead of repeating giant context.",
            "Keep each agent job narrow and artifact-backed.",
        ],
        "compact_findings": [
            {
                "source": spec.id,
                "finding": "Legal token savings are workflow compaction, not quota evasion.",
            }
        ],
    }


async def agent_implementation_planner(
    spec: AgentSpec, memory: dict[str, Any]
) -> tuple[str, list[str], dict[str, Any]]:
    plan = read_text("14_context/external_operator_implementation_plan.md")
    focused = compact_lines(plan, ["ActionIntent", "CapabilityAdapter", "approval", "audit", "No adapter"], 9)
    summary = "Next coding milestone should add ActionIntent + CapabilityAdapter read model before adapter execution."
    lines = [
        "- Status: done",
        f"- Task: {spec.task}",
        "- Proposed next milestone: native ActionIntent state, approval binding, payload binding, audit trace.",
        "- No external adapter execution yet.",
        "- Supporting notes:",
        *[f"  - {line}" for line in focused],
    ]
    return summary, lines, {
        "current_priorities": [
            "Implement ActionIntent and CapabilityAdapter before external tool integration.",
        ],
        "compact_findings": [
            {
                "source": spec.id,
                "finding": "The safest N+3.1 slice is action-intent plumbing, not Auto Browser execution.",
            }
        ],
    }


async def agent_generic(spec: AgentSpec, memory: dict[str, Any]) -> tuple[str, list[str], dict[str, Any]]:
    summary = "Generic agent completed a local deterministic task."
    lines = ["- Status: done", f"- Task: {spec.task}", "- No external calls were made."]
    return summary, lines, {}


def merge_memory(memory: dict[str, Any], updates: list[dict[str, Any]]) -> dict[str, Any]:
    merged = dict(memory)
    merged.setdefault("project_truth", [])
    merged.setdefault("current_priorities", [])
    merged.setdefault("blocked_actions", [])
    merged.setdefault("candidate_tools", {})
    merged.setdefault("compact_findings", [])

    for update in updates:
        for key in ("project_truth", "current_priorities", "blocked_actions"):
            for item in update.get(key, []):
                if item not in merged[key]:
                    merged[key].append(item)
        merged["candidate_tools"].update(update.get("candidate_tools", {}))
        merged["compact_findings"].extend(update.get("compact_findings", []))

    merged["project_truth"] = dedupe_scalars(merged["project_truth"])[-12:]
    merged["current_priorities"] = dedupe_scalars(merged["current_priorities"])[-10:]
    merged["blocked_actions"] = dedupe_scalars(merged["blocked_actions"])[-12:]
    merged["compact_findings"] = dedupe_findings(merged["compact_findings"])[-25:]
    merged["last_updated"] = utc_now()
    return merged


def dedupe_scalars(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        output.append(item)
    return output


def dedupe_findings(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    output: list[dict[str, Any]] = []
    for item in items:
        key = (str(item.get("source", "")), str(item.get("finding", "")))
        if key in seen:
            continue
        seen.add(key)
        output.append(item)
    return output


def default_agents() -> list[AgentSpec]:
    return [
        AgentSpec(
            id="ruflo-review-agent",
            role="RUFLO Review Agent",
            task="Summarize the current safe next step from RUFLO audit docs.",
            risk_level="low",
        ),
        AgentSpec(
            id="browser-candidate-agent",
            role="Browser Candidate Agent",
            task="Compare Auto Browser and Obscura as safe future browser candidates.",
            risk_level="low",
        ),
        AgentSpec(
            id="memory-agent",
            role="Compact Memory Agent",
            task="Update compact shared memory with durable current truths.",
            risk_level="low",
        ),
        AgentSpec(
            id="token-saver-agent",
            role="Token-Saving Agent",
            task="Propose legal context-saving workflow patterns and provider-limit-evasion boundaries.",
            risk_level="low",
        ),
        AgentSpec(
            id="implementation-planner-agent",
            role="Implementation Planner Agent",
            task="Create the next coding milestone plan for ActionIntent and CapabilityAdapter.",
            risk_level="low",
        ),
    ]


async def run_multi_agent_mvp() -> dict[str, Any]:
    run_id = run_id_now()
    run_dir = RUNS_ROOT / run_id
    agents_dir = run_dir / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    specs = default_agents()
    memory_before = load_shared_memory()

    write_json(run_dir / "shared_memory_before.json", memory_before)
    write_json(
        run_dir / "run_manifest.json",
        {
            "run_id": run_id,
            "status": "running",
            "started_at": utc_now(),
            "repo_root": str(REPO_ROOT),
            "runner": "super_ai_agent.multi_agent_mvp",
            "safety_model": "repo_local_deterministic_no_external_calls",
            "agents": [asdict(spec) for spec in specs],
        },
    )

    tasks = [run_agent(spec, run_dir, memory_before) for spec in specs]
    results = await asyncio.gather(*tasks)
    memory_after = merge_memory(memory_before, [result.memory_updates for result in results])
    write_json(SHARED_MEMORY_PATH, memory_after)
    write_json(run_dir / "shared_memory_after.json", memory_after)

    summary_lines = [
        f"- Run id: `{run_id}`",
        "- Status: completed",
        "- Runtime truth: local deterministic multi-agent MVP; no external services called.",
        "- Safety truth: no autonomous execution, no external adapter integration, no installs/clones/builds.",
        "- Agent results:",
        *[f"  - `{result.agent_id}`: {result.status} — {result.summary}" for result in results],
        "",
        "## Supervisor Recommendation",
        "",
        "Build native `ActionIntent` + `CapabilityAdapter` plumbing next before any external browser or multi-agent adapter execution.",
    ]
    supervisor_path = run_dir / "supervisor_summary.md"
    write_markdown(supervisor_path, "Ghoti Multi-Agent MVP Supervisor Summary", summary_lines)

    manifest = {
        "run_id": run_id,
        "status": "completed",
        "started_at": results[0].started_at if results else utc_now(),
        "finished_at": utc_now(),
        "artifact_dir": f"05_logs/multi_agent_runs/{run_id}",
        "supervisor_summary": f"05_logs/multi_agent_runs/{run_id}/supervisor_summary.md",
        "shared_memory_path": "14_context/multi_agent_shared_memory.json",
        "agents": [asdict(spec) for spec in specs],
        "results": [asdict(result) for result in results],
    }
    write_json(run_dir / "run_manifest.json", manifest)
    return manifest


def main() -> int:
    manifest = asyncio.run(run_multi_agent_mvp())
    print(f"run_id: {manifest['run_id']}")
    print(f"artifact_dir: {manifest['artifact_dir']}")
    print(f"supervisor_summary: {manifest['supervisor_summary']}")
    print("agent_statuses:")
    for result in manifest["results"]:
        print(f"- {result['agent_id']}: {result['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
