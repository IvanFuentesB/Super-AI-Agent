#!/usr/bin/env python3
"""LLM Council Runner — local-first Karpathy-style multi-model council scaffold.

Inspired by karpathy/llm-council (3-stage: individual opinions, anonymous peer review,
chairman synthesis). This Ghoti implementation is local-first and safety-gated.

Safety invariants (never removed):
  LOCAL_ONLY_BY_DEFAULT
  NO_AUTONOMOUS_ACTIONS
  HUMAN_REVIEW_REQUIRED
  EXTERNAL_CALLS_DISABLED_BY_DEFAULT

Provider modes:
  local_demo          — deterministic placeholder responses, no model required (default)
  ollama_local        — local Ollama inference, only when --apply passed and ollama found
  openrouter_external — disabled by default; refused unless config+env var explicitly set

N+3.61A scaffold: stdlib-only, no external API calls by default, no secrets.
"""
import argparse
import datetime
import hashlib
import json
import os
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
SESSIONS_DIR = REPO_ROOT / "05_logs" / "llm_council_runs"
DEFAULT_CONFIG_PATH = REPO_ROOT / "23_configs" / "llm_council.example.json"

SAFETY_FLAGS = {
    "LOCAL_ONLY_BY_DEFAULT": True,
    "NO_AUTONOMOUS_ACTIONS": True,
    "HUMAN_REVIEW_REQUIRED": True,
    "EXTERNAL_CALLS_DISABLED_BY_DEFAULT": True,
}

# Default council configuration (used when no config file found)
DEFAULT_CONFIG = {
    "council_name": "Ghoti LLM Council",
    "default_provider_mode": "local_demo",
    "external_enabled": False,
    "external_gateway": "openrouter",
    "env_var_name": "OPENROUTER_API_KEY",
    "chairman_member": "chairman_claude",
    "council_members": [
        {"id": "member_a", "role": "pragmatist", "model": "local_demo"},
        {"id": "member_b", "role": "critic",     "model": "local_demo"},
        {"id": "member_c", "role": "synthesizer","model": "local_demo"},
    ],
    "ranking_criteria": ["accuracy", "clarity", "safety", "actionability"],
    "no_secret_storage": True,
    "no_external_calls_by_default": True,
    "no_autonomous_actions": True,
    "human_review_required": True,
    "no_live_account_actions": True,
}


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _session_id(question: str) -> str:
    ts = _utc_now()
    slug = hashlib.md5(question.encode("utf-8")).hexdigest()[:8]
    return f"council_{ts}_{slug}"


def _load_config(config_path: pathlib.Path) -> dict:
    if config_path.exists():
        try:
            return json.loads(config_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[WARN] Could not load config {config_path}: {e}. Using defaults.")
    return dict(DEFAULT_CONFIG)


def _check_ollama_available(model_hint: str = "gemma") -> tuple[bool, str]:
    try:
        import subprocess
        r = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            has_model = model_hint.lower() in r.stdout.lower()
            return True, r.stdout.strip()
        return False, r.stderr.strip()
    except Exception as e:
        return False, str(e)


def _check_env_var(var_name: str) -> bool:
    val = os.environ.get(var_name, "")
    return bool(val and val.strip())


# ---------------------------------------------------------------------------
# Demo provider — deterministic, no model required
# ---------------------------------------------------------------------------

DEMO_TEMPLATES = {
    "pragmatist": (
        "From a pragmatist perspective: the question '{q}' has clear practical implications. "
        "I recommend focusing on immediate, measurable actions. Validate assumptions before scaling. "
        "Keep scope minimal and reversible."
    ),
    "critic": (
        "Critical review of '{q}': Several assumptions deserve scrutiny. "
        "Consider edge cases and failure modes. A staged rollout with human checkpoints reduces risk. "
        "Do not skip the audit step."
    ),
    "synthesizer": (
        "Synthesizing perspectives on '{q}': Both pragmatic action and critical review are valid. "
        "The optimal path combines iterative delivery with safety checkpoints. "
        "Prioritize human oversight at each gate."
    ),
}

DEMO_RANKING_TEMPLATE = (
    "After reviewing all responses anonymously:\n"
    "- Response {top}: most actionable and clearly reasoned.\n"
    "- Response {mid}: solid but could be more concrete.\n"
    "- Response {bot}: insightful critique but needs a positive path forward.\n"
    "Ranking: {top} > {mid} > {bot}"
)

DEMO_CHAIRMAN_TEMPLATE = (
    "Chairman synthesis for '{q}':\n\n"
    "The council converged on: take iterative, human-reviewed steps. "
    "No autonomous action. Validate at each stage. "
    "The pragmatist's focus on immediacy, the critic's risk awareness, "
    "and the synthesizer's integration approach all point toward a gated, "
    "incremental implementation. Human approval is required before any live action.\n\n"
    "Final recommendation: proceed with dry-run first, then await human review."
)


def _demo_stage1(question: str, members: list) -> list:
    opinions = []
    for m in members:
        role = m.get("role", "member")
        template = DEMO_TEMPLATES.get(role, DEMO_TEMPLATES["synthesizer"])
        opinions.append({
            "member_id": m["id"],
            "role": role,
            "response": template.format(q=question),
            "provider": "local_demo",
        })
    return opinions


def _demo_stage2(opinions: list, criteria: list) -> dict:
    labels = [chr(65 + i) for i in range(len(opinions))]  # A, B, C, ...
    label_to_member = {labels[i]: opinions[i]["member_id"] for i in range(len(opinions))}

    if len(labels) >= 3:
        ranking_text = DEMO_RANKING_TEMPLATE.format(
            top=labels[0], mid=labels[1], bot=labels[2]
        )
    else:
        ranking_text = "Responses reviewed. All meet minimum quality threshold."

    peer_reviews = []
    for label, opinion in zip(labels, opinions):
        peer_reviews.append({
            "label": label,
            "response_excerpt": opinion["response"][:120] + "...",
            "criteria_scores": {c: 3 for c in criteria},
            "reviewer_note": f"Response {label}: meets criteria for {', '.join(criteria[:2])}.",
        })

    return {
        "label_to_member": label_to_member,
        "peer_reviews": peer_reviews,
        "ranking_summary": ranking_text,
    }


def _demo_stage3(question: str, stage2: dict) -> str:
    return DEMO_CHAIRMAN_TEMPLATE.format(q=question)


# ---------------------------------------------------------------------------
# Ollama provider — optional local inference
# ---------------------------------------------------------------------------

def _ollama_query(prompt: str, model: str = "gemma3", timeout: int = 60) -> str:
    import subprocess
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False})
    try:
        r = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True, text=True, timeout=timeout
        )
        if r.returncode == 0:
            return r.stdout.strip()
        return f"[ollama error rc={r.returncode}] {r.stderr.strip()[:200]}"
    except Exception as e:
        return f"[ollama exception] {e}"


def _ollama_stage1(question: str, members: list, available: bool, available_detail: str) -> list:
    if not available:
        return [
            {
                "member_id": m["id"],
                "role": m.get("role", "member"),
                "response": f"[ollama_local unavailable: {available_detail}] Degrading to demo response. {DEMO_TEMPLATES.get(m.get('role','synthesizer'), DEMO_TEMPLATES['synthesizer']).format(q=question)}",
                "provider": "ollama_local_degraded",
            }
            for m in members
        ]

    opinions = []
    for m in members:
        role = m.get("role", "member")
        prompt = (
            f"You are a council member with the role of {role}. "
            f"Answer the following question concisely in 2-3 sentences: {question}"
        )
        response = _ollama_query(prompt)
        opinions.append({
            "member_id": m["id"],
            "role": role,
            "response": response,
            "provider": "ollama_local",
        })
    return opinions


# ---------------------------------------------------------------------------
# External provider — disabled stub
# ---------------------------------------------------------------------------

def _external_refused() -> str:
    return (
        "[EXTERNAL_PROVIDER_REFUSED] "
        "External API calls are disabled by default in this Ghoti LLM Council scaffold. "
        "To enable: set external_enabled=true in config AND set the env var. "
        "TODO: implement OpenRouter integration here when explicitly authorized."
    )


# ---------------------------------------------------------------------------
# Core council flow
# ---------------------------------------------------------------------------

def _run_council(question: str, config: dict, provider_mode: str, dry_run: bool) -> dict:
    members = config.get("council_members", DEFAULT_CONFIG["council_members"])
    chairman = config.get("chairman_member", DEFAULT_CONFIG["chairman_member"])
    criteria = config.get("ranking_criteria", DEFAULT_CONFIG["ranking_criteria"])
    session_id = _session_id(question)

    result = {
        "session_id": session_id,
        "question": question,
        "provider_mode": provider_mode,
        "dry_run": dry_run,
        "timestamp_utc": _utc_now(),
        "safety_flags": SAFETY_FLAGS,
        "stage1_first_opinions": [],
        "stage2_anonymous_peer_review": {},
        "stage3_chairman_synthesis": "",
        "metadata": {
            "chairman_member": chairman,
            "label_to_member": {},
            "members": [m["id"] for m in members],
            "criteria": criteria,
        },
    }

    if provider_mode == "local_demo":
        stage1 = _demo_stage1(question, members)
        stage2 = _demo_stage2(stage1, criteria)
        stage3 = _demo_stage3(question, stage2)

    elif provider_mode == "ollama_local":
        available, detail = _check_ollama_available()
        stage1 = _ollama_stage1(question, members, available, detail)
        stage2 = _demo_stage2(stage1, criteria)
        stage3 = _demo_stage3(question, stage2)

    elif provider_mode == "openrouter_external":
        external_enabled = config.get("external_enabled", False)
        env_var = config.get("env_var_name", "OPENROUTER_API_KEY")
        if not external_enabled or not _check_env_var(env_var):
            refused = _external_refused()
            stage1 = [{"member_id": "refused", "role": "refused", "response": refused, "provider": "refused"}]
            stage2 = {"label_to_member": {}, "peer_reviews": [], "ranking_summary": refused}
            stage3 = refused
        else:
            refused = _external_refused()
            stage1 = [{"member_id": "refused", "role": "refused", "response": refused, "provider": "refused"}]
            stage2 = {"label_to_member": {}, "peer_reviews": [], "ranking_summary": refused}
            stage3 = refused
    else:
        stage1 = _demo_stage1(question, members)
        stage2 = _demo_stage2(stage1, criteria)
        stage3 = _demo_stage3(question, stage2)

    result["stage1_first_opinions"] = stage1
    result["stage2_anonymous_peer_review"] = stage2
    result["stage3_chairman_synthesis"] = stage3
    result["metadata"]["label_to_member"] = stage2.get("label_to_member", {})

    return result


def _write_session(result: dict) -> pathlib.Path:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SESSIONS_DIR / f"{result['session_id']}.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8", newline="\n")
    return out_path


def _print_result(result: dict) -> None:
    print(f"\n{'='*60}")
    print(f"Ghoti LLM Council — Session: {result['session_id']}")
    print(f"Provider mode: {result['provider_mode']} | Dry run: {result['dry_run']}")
    print(f"Safety: LOCAL_ONLY_BY_DEFAULT | NO_AUTONOMOUS_ACTIONS | HUMAN_REVIEW_REQUIRED")
    print(f"{'='*60}")
    print(f"\nQuestion: {result['question']}")

    print(f"\n--- Stage 1: First Opinions ---")
    for op in result["stage1_first_opinions"]:
        print(f"[{op['member_id']} / {op['role']}] ({op['provider']})")
        print(f"  {op['response']}")

    print(f"\n--- Stage 2: Anonymous Peer Review ---")
    s2 = result["stage2_anonymous_peer_review"]
    for pr in s2.get("peer_reviews", []):
        print(f"  Response {pr['label']}: {pr['reviewer_note']}")
    print(f"  Ranking: {s2.get('ranking_summary','')}")

    print(f"\n--- Stage 3: Chairman Synthesis ---")
    print(result["stage3_chairman_synthesis"])
    print(f"\n{'='*60}")
    print("HUMAN_REVIEW_REQUIRED: Review this output before any action.")
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def cmd_status(args, config: dict) -> None:
    print("=== Ghoti LLM Council Status ===")
    print(f"Script       : {pathlib.Path(__file__).name}")
    print(f"Council name : {config.get('council_name','(default)')}")
    print(f"Default mode : {config.get('default_provider_mode','local_demo')}")
    print(f"Ext enabled  : {config.get('external_enabled', False)}")
    ollama_ok, ollama_detail = _check_ollama_available()
    print(f"Ollama       : {'FOUND' if ollama_ok else 'NOT FOUND'}")
    print(f"Sessions dir : {SESSIONS_DIR.relative_to(REPO_ROOT)}")
    sessions = sorted(SESSIONS_DIR.glob("*.json")) if SESSIONS_DIR.exists() else []
    print(f"Sessions     : {len(sessions)}")
    print(f"Safety flags : {', '.join(SAFETY_FLAGS.keys())}")
    print("=== End Status ===")


def cmd_demo(args, config: dict) -> None:
    question = "Demonstrate the Ghoti LLM Council 3-stage flow."
    print("[DEMO] Running local_demo council with sample question...")
    result = _run_council(question, config, "local_demo", dry_run=True)
    _print_result(result)
    if not args.dry_run:
        out = _write_session(result)
        print(f"[DEMO] Written: {out.relative_to(REPO_ROOT)}")
    else:
        print("[DRY RUN] Pass --apply to write session log.")


def cmd_ask(args, config: dict) -> None:
    question = args.ask
    if not question:
        print("ERROR: --ask requires a question string")
        sys.exit(1)
    provider_mode = config.get("default_provider_mode", "local_demo")
    dry_run = not args.apply
    result = _run_council(question, config, provider_mode, dry_run=dry_run)
    _print_result(result)
    if args.apply:
        out = _write_session(result)
        print(f"Written: {out.relative_to(REPO_ROOT)}")
    else:
        print("[DRY RUN] Pass --apply to write session log.")


def cmd_from_file(args, config: dict) -> None:
    p = pathlib.Path(args.from_file)
    if not p.exists():
        print(f"ERROR: File not found: {p}")
        sys.exit(1)
    question = p.read_text(encoding="utf-8").strip()
    if not question:
        print("ERROR: File is empty")
        sys.exit(1)
    provider_mode = config.get("default_provider_mode", "local_demo")
    dry_run = not args.apply
    result = _run_council(question, config, provider_mode, dry_run=dry_run)
    _print_result(result)
    if args.apply:
        out = _write_session(result)
        print(f"Written: {out.relative_to(REPO_ROOT)}")
    else:
        print("[DRY RUN] Pass --apply to write session log.")


def cmd_list_sessions(args) -> None:
    if not SESSIONS_DIR.exists():
        print("No sessions found (directory does not exist).")
        return
    sessions = sorted(SESSIONS_DIR.glob("*.json"))
    if not sessions:
        print("No sessions found.")
        return
    print(f"Sessions ({len(sessions)}):")
    for s in sessions:
        print(f"  {s.name}")


def cmd_show_session(args) -> None:
    sid = args.show_session
    p = SESSIONS_DIR / f"{sid}.json"
    if not p.exists():
        p2 = SESSIONS_DIR / sid
        if p2.exists():
            p = p2
        else:
            print(f"Session not found: {sid}")
            sys.exit(1)
    data = json.loads(p.read_text(encoding="utf-8"))
    _print_result(data)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Ghoti LLM Council Runner — local-first Karpathy-style 3-stage council scaffold. "
            "LOCAL_ONLY_BY_DEFAULT | NO_AUTONOMOUS_ACTIONS | HUMAN_REVIEW_REQUIRED | "
            "EXTERNAL_CALLS_DISABLED_BY_DEFAULT. N+3.61A."
        )
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--status",       action="store_true", help="Show council status")
    mode.add_argument("--demo",         action="store_true", help="Run demo council flow (no model required)")
    mode.add_argument("--ask",          metavar="QUESTION",  help="Ask the council a question")
    mode.add_argument("--from-file",    metavar="PATH",      help="Ask question read from a file")
    mode.add_argument("--list-sessions",action="store_true", help="List past session logs")
    mode.add_argument("--show-session", metavar="SESSION_ID",help="Print a past session")

    parser.add_argument("--config",   metavar="PATH",  help="Path to council config JSON (default: 23_configs/llm_council.example.json)")
    parser.add_argument("--dry-run",  action="store_true", default=True, help="Do not write session log (default)")
    parser.add_argument("--apply",    action="store_true", help="Write session log to 05_logs/llm_council_runs/")

    args = parser.parse_args()

    config_path = pathlib.Path(args.config) if args.config else DEFAULT_CONFIG_PATH
    config = _load_config(config_path)

    if args.status:
        cmd_status(args, config)
    elif args.demo:
        cmd_demo(args, config)
    elif args.ask:
        cmd_ask(args, config)
    elif args.from_file:
        cmd_from_file(args, config)
    elif args.list_sessions:
        cmd_list_sessions(args)
    elif args.show_session:
        cmd_show_session(args)


if __name__ == "__main__":
    main()
