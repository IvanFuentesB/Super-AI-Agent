#!/usr/bin/env python3
"""Ghoti Local Orchestrator - stdlib-only, dry-run-first, no external APIs."""
import argparse, datetime, json, pathlib, subprocess, sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
PROMPT_BUS_DIR = REPO_ROOT / "14_context" / "prompt_bus"
CANONICAL_CLAUDE_PROMPT = REPO_ROOT / "14_context" / "ghoti_current_prompt.md"
OUTBOX_DIR = PROMPT_BUS_DIR / "outbox"
AGENT_LANES_DIR = REPO_ROOT / "14_context" / "agent_lanes"
ACTIVE_LOCKS_FILE = AGENT_LANES_DIR / "active_locks.jsonl"
LANE_STATUS_FILE = AGENT_LANES_DIR / "lane_status.jsonl"
OBSIDIAN_VAULT_DIR = REPO_ROOT / "14_context" / "obsidian_vault"
COMPACT_MEMORY_DIR = REPO_ROOT / "14_context" / "compact_memory"
ROUTING_CONFIG = REPO_ROOT / "23_configs" / "local_worker_routing.example.json"
RUFLO_DIR = REPO_ROOT / "21_repos" / "third_party" / "evals" / "ruflo"

def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def _utc_now_display():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

def _run(cmd, cwd=None, timeout=5):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd or REPO_ROOT), timeout=timeout)
        return r.stdout.strip(), r.returncode
    except Exception as e:
        return "ERROR: " + str(e), -1

def _parse_jsonl(p):
    recs, errs = [], []
    if not p.exists() or p.stat().st_size == 0: return recs, errs
    for i, raw in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line: continue
        try: recs.append(json.loads(line))
        except json.JSONDecodeError as e: errs.append((i, str(e)))
    return recs, errs

def cmd_status(args):
    print("=== Ghoti Local Orchestrator Status ===")
    print("Generated: " + _utc_now_display()); print()
    branch, _ = _run(["git", "branch", "--show-current"])
    head, _ = _run(["git", "rev-parse", "--short", "HEAD"])
    ori, rc = _run(["git", "rev-parse", "origin/feat/ghoti-visible-operator-stack"])
    ori_d = ori[:10] if rc == 0 and "ERROR" not in ori else "unavailable"
    print("[Git]"); print("  Branch      : " + branch); print("  HEAD        : " + head); print("  Origin base : " + ori_d); print()
    print("[Prompt Bus]")
    if CANONICAL_CLAUDE_PROMPT.exists():
        sz = CANONICAL_CLAUDE_PROMPT.stat().st_size
        mt = datetime.datetime.fromtimestamp(CANONICAL_CLAUDE_PROMPT.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        print("  Claude prompt : EXISTS (" + str(sz) + "b, modified " + mt + ")")
    else: print("  Claude prompt : MISSING")
    ob = list(OUTBOX_DIR.glob("*.md")) if OUTBOX_DIR.exists() else []
    print("  Outbox files  : " + str(len(ob))); print()
    print("[Local Worker Config]")
    if ROUTING_CONFIG.exists():
        try: json.loads(ROUTING_CONFIG.read_text(encoding="utf-8")); print("  " + ROUTING_CONFIG.name + ": valid JSON")
        except json.JSONDecodeError: print("  " + ROUTING_CONFIG.name + ": INVALID JSON")
    else: print("  " + ROUTING_CONFIG.name + ": MISSING"); print()
    print("[Obsidian Vault]")
    if OBSIDIAN_VAULT_DIR.exists():
        vf = list(OBSIDIAN_VAULT_DIR.glob("*.md"))
        print("  Files: " + str(len(vf)))
        for kf in ["00_Index.md","01_Current_State.md","02_Next_Actions.md","09_Migration_Handoff.md"]:
            print("  " + ("OK" if (OBSIDIAN_VAULT_DIR/kf).exists() else "MISSING") + ": " + kf)
    else: print("  Vault directory MISSING"); print()
    print("[Compact Memory]")
    if COMPACT_MEMORY_DIR.exists():
        mf = list(COMPACT_MEMORY_DIR.glob("*.md"))
        print("  Files: " + str(len(mf)))
        for kf in ["project_state.md","repo_and_tool_index.md","money_os_memory.md","safety_rules.md"]:
            print("  " + ("OK" if (COMPACT_MEMORY_DIR/kf).exists() else "MISSING") + ": " + kf)
    else: print("  Compact memory directory MISSING"); print()
    print("[Agent Lanes]")
    lks,le = _parse_jsonl(ACTIVE_LOCKS_FILE); sts,se = _parse_jsonl(LANE_STATUS_FILE)
    print("  Active locks   : " + str(len(lks)) + (" (parse errors!)" if le else ""))
    print("  Status records : " + str(len(sts)) + (" (parse errors!)" if se else ""))
    if lks: ll = lks[-1]; print("  Latest lock    : " + ll.get("agent_id","?") + " / " + ll.get("task_slug","?"))
    if sts: ls = sts[-1]; print("  Latest status  : " + ls.get("agent_id","?") + " = " + ls.get("current_state","?"))
    print()
    print("[External Tools]")
    print("  Ruflo dir      : " + ("EXISTS" if RUFLO_DIR.exists() else "MISSING"))
    nm = RUFLO_DIR / "node_modules"
    print("  Ruflo npm deps : " + ("INSTALLED" if nm.exists() else "not installed"))
    ov, orc = _run(["ollama", "--version"])
    if orc == 0:
        print("  Ollama         : FOUND - " + ov[:60])
        mo, mrc = _run(["ollama", "list"])
        print("  Gemma model    : " + ("FOUND" if mrc==0 and "gemma" in mo.lower() else "not found"))
    else: print("  Ollama         : not found"); print("  Gemma model    : unavailable")
    print(); print("=== End Status ===")

def cmd_plan_next(args):
    print("=== Ghoti N+3.49A Plan (dry-run) ===")
    print("Generated: " + _utc_now_display()); print()
    print("Current: ~65% | After N+3.50A: ~72%"); print()
    print("[Next Milestones]")
    print("  Claude: N+3.50A - Prompt Bus Dashboard")
    print("  Codex:  N+3.50B - Audit orchestrator purity")
    print("  Gemma:  Compression when Ollama confirmed")
    print("  Python: Archive old outbox files"); print()
    caps = [("Self-inspection","90%"),("Route recommendation","75%"),("Claude prompt gen","80%"),("Codex prompt gen","75%"),("Local Python exec","70%"),("Gemma/Ollama","20%"),("Lane tracking","85%"),("Memory sync","70%"),("Ruflo inspection","60%"),("Human approval gate","100%")]
    for n,p in caps: print("  " + n.ljust(24) + ": " + p)
    print(); print("[Blockers]")
    for b in ["1. Ollama not confirmed","2. Ruflo not installed","3. Prompt bus manual copy-paste","4. No dashboard UI"]: print("  " + b)
    print(); print("[Safety Gates]")
    for g in ["- Live actions require human approval","- Ruflo not wired until safety review","- Gemma download requires user approval"]: print("  " + g)
    print("=== End Plan ===")

def _gen_claude_prompt_n350():
    ts = _utc_now()
    parts = ["# Ghoti Claude Code Prompt - N+3.50A","Generated: " + ts,"Base: feat/ghoti-visible-operator-stack","","## Role","Build 03_scripts/ghoti_dashboard.py with --status, --card --dry-run, --card --apply.","Reads outbox + lane JSONL + compact memory. Writes 14_context/ghoti_dashboard_card.md.","Safety: no live actions, no secret files, no unrelated staging, dry-run-first.","","## Branch: feat/ghoti-agent-claude-n3-50-dashboard-readcard","## Deliverables: A) ghoti_dashboard.py  B) Validation  C) claude_n3_50a_*.md"]
    return chr(10).join(parts) + chr(10)

def _gen_codex_prompt_n350():
    ts = _utc_now()
    parts = ["# Codex Audit - N+3.50B - Orchestrator Purity","Generated: " + ts,"For: Codex audit. DO NOT implement. Audit only.","","Files: ghoti_local_orchestrator.py, prompt_bus.py, local_worker_router.py, JSONL","","Checklist:","- --status: no writes, no external calls","- --plan-next: stdout only","- --write-next-prompts --apply: writes only to 14_context/","- read-only check commands (obsidian/ruflo/gemma-check)","- No Python subprocess shell option","- --write-chatgpt applies to outbox only","- course_cert route forbids impersonation","- ruflo route is research/intake only","- JSONL valid, no path escapes","","Output: 14_context/codex_n3_50b_orchestrator_purity_audit.md","Format: PASS/FAIL per item, APPROVED or NEEDS_FIX verdict."]
    return chr(10).join(parts) + chr(10)

def cmd_write_next_prompts(args):
    cc = _gen_claude_prompt_n350(); ts = _utc_now()
    fn = "codex_n3_50_orchestrator_audit_" + ts + ".md"
    cd = OUTBOX_DIR / fn; dc = _gen_codex_prompt_n350()
    print("[Claude prompt] -> " + str(CANONICAL_CLAUDE_PROMPT.relative_to(REPO_ROOT)) + " (" + str(len(cc)) + " chars)")
    print("[Codex prompt]  -> " + str(cd.relative_to(REPO_ROOT)) + " (" + str(len(dc)) + " chars)"); print()
    if not args.apply:
        print("[DRY RUN] Claude preview:"); print(cc[:400]); print("...")
        print(); print("[DRY RUN] Codex preview:"); print(dc[:300]); print("...")
        print(); print("[DRY RUN] Pass --apply to write."); return
    CANONICAL_CLAUDE_PROMPT.write_text(cc, encoding="utf-8")
    print("Written: " + str(CANONICAL_CLAUDE_PROMPT.relative_to(REPO_ROOT)))
    OUTBOX_DIR.mkdir(parents=True, exist_ok=True); cd.write_text(dc, encoding="utf-8")
    print("Written: " + str(cd.relative_to(REPO_ROOT)))
    print(); print("IMPORTANT: Do NOT run these prompts now. Copy-paste manually when ready.")

def cmd_obsidian_check(args):
    print("=== Obsidian / Compact Memory Check (read-only) ===")
    req = [(OBSIDIAN_VAULT_DIR/"00_Index.md","obsidian"),(OBSIDIAN_VAULT_DIR/"01_Current_State.md","obsidian"),(OBSIDIAN_VAULT_DIR/"02_Next_Actions.md","obsidian"),(OBSIDIAN_VAULT_DIR/"09_Migration_Handoff.md","obsidian"),(COMPACT_MEMORY_DIR/"project_state.md","memory"),(COMPACT_MEMORY_DIR/"repo_and_tool_index.md","memory"),(COMPACT_MEMORY_DIR/"money_os_memory.md","memory"),(COMPACT_MEMORY_DIR/"safety_rules.md","memory")]
    miss = []
    for fp, cat in req:
        rel = fp.relative_to(REPO_ROOT)
        if fp.exists(): print("  OK [" + cat + "]: " + str(rel) + "  (" + str(fp.stat().st_size) + "b)")
        else: print("  MISSING [" + cat + "]: " + str(rel)); miss.append(str(rel))
    print()
    if miss: print("WARNING: " + str(len(miss)) + " missing:"); [print("  - " + m) for m in miss]
    else: print("PASS: all required Obsidian vault and compact memory files present")
    print("=== End Obsidian Check ===")

def cmd_ruflo_check(args):
    print("=== Ruflo Check (read-only) ===")
    print("Path: " + str(RUFLO_DIR.relative_to(REPO_ROOT)) + " | Exists: " + ("YES" if RUFLO_DIR.exists() else "NO")); print()
    if not RUFLO_DIR.exists(): return
    gh, rc = _run(["git", "rev-parse", "--short", "HEAD"], cwd=RUFLO_DIR)
    print("Git HEAD: " + (gh if rc == 0 else "unavailable"))
    pkg = RUFLO_DIR / "package.json"
    if pkg.exists():
        try:
            d = json.loads(pkg.read_text(encoding="utf-8"))
            print("Name: " + d.get("name","?") + " v" + d.get("version","?"))
            sc = d.get("scripts",{})
            print("Scripts: " + str(list(sc.keys())))
            risky = [s for s in sc if s in ("preinstall","postinstall","prepare")]
            if risky: print("WARNING risky lifecycle: " + str(risky))
            else: print("Lifecycle: NONE - safe to install with: npm install --ignore-scripts")
        except: print("package.json: parse error")
    nm = RUFLO_DIR / "node_modules"
    print("node_modules: " + ("INSTALLED" if nm.exists() else "NOT INSTALLED"))
    if not nm.exists():
        lock = RUFLO_DIR / "package-lock.json"
        cmd = "npm ci --ignore-scripts" if lock.exists() else "npm install --ignore-scripts"
        print("Install when ready: " + cmd + " (inside ruflo dir, not global, not wired)")
    print("=== End Ruflo Check ===")

def cmd_gemma_check(args):
    print("=== Gemma / Ollama Check (read-only) ===")
    vo, vrc = _run(["ollama", "--version"])
    if vrc != 0: print("Ollama: NOT FOUND. Install from https://ollama.com"); print("=== End ==="); return
    print("Ollama: FOUND - " + vo)
    lo, lrc = _run(["ollama", "list"])
    if lrc == 0:
        print("Models: " + (lo if lo else "(none)"))
        gl = [l for l in lo.splitlines() if "gemma" in l.lower()]
        if gl: print("Gemma found:"); [print("  " + l) for l in gl]; print("AVAILABLE when user approves.")
        else: print("Gemma: NOT FOUND. Install (user approval required): ollama pull gemma3")
    print("=== End Gemma/Ollama Check ===")

def main():
    p = argparse.ArgumentParser(description="Ghoti Local Orchestrator - stdlib-only, dry-run-first, no external APIs.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--status", action="store_true", help="Print compact system status")
    g.add_argument("--plan-next", action="store_true", help="Print next-step plan (dry-run)")
    g.add_argument("--write-next-prompts", action="store_true", help="Write next Claude+Codex prompts")
    g.add_argument("--obsidian-check", action="store_true", help="Check Obsidian vault + compact memory")
    g.add_argument("--ruflo-check", action="store_true", help="Inspect Ruflo directory (read-only)")
    g.add_argument("--gemma-check", action="store_true", help="Check Ollama + Gemma model")
    p.add_argument("--dry-run", action="store_true", default=True, help="Dry run (default)")
    p.add_argument("--apply", action="store_true", help="Actually write files")
    a = p.parse_args()
    if a.status: cmd_status(a)
    elif a.plan_next: cmd_plan_next(a)
    elif a.write_next_prompts: cmd_write_next_prompts(a)
    elif a.obsidian_check: cmd_obsidian_check(a)
    elif a.ruflo_check: cmd_ruflo_check(a)
    elif a.gemma_check: cmd_gemma_check(a)

if __name__ == "__main__":
    main()
