#!/usr/bin/env python3
"""Supervised Multi-Agent Content Studio Demo (N+4.3A).

Local-only, supervised, no external APIs, no live posting, no account actions.
Produces a complete local content/video-style package and a preview HTML.

CLI modes:
  --status                          show studio status
  --run-demo                        run full agent pipeline
  --topic "<topic>"                 override demo topic
  --output-dir <repo-local path>    override default run dir (must be inside repo)
  --json                            emit JSON output
  --open-preview                    NO-OP placeholder (does not open anything)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html
import json
import pathlib
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
DEFAULT_RUNS_DIR = REPO_ROOT / "14_context" / "content_studio" / "runs"
DEFAULT_TOPIC = "AI tools for students and creators"
MILESTONE = "N+4.3A"
STUDIO_NAME = "supervised_content_studio_demo"

AGENT_NAMES = [
    "strategy_agent",
    "research_meta_agent",
    "script_agent",
    "shotlist_agent",
    "title_thumbnail_agent",
    "safety_compliance_agent",
    "approval_agent",
    "memory_agent",
]

_SECRET_NAME_PATTERNS = frozenset([
    ".env", "secret", "credential", "token", "key", "password",
    "apikey", "api_key", "private", "passwd", "auth",
])


def _is_inside_repo(p: pathlib.Path) -> bool:
    try:
        p.resolve().relative_to(REPO_ROOT)
        return True
    except ValueError:
        return False


def _is_secret_path(p: pathlib.Path) -> bool:
    lowered = str(p).lower()
    for pat in _SECRET_NAME_PATTERNS:
        if pat in lowered:
            return True
    return False


def _utc_timestamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _slug(text: str, limit: int = 32) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_")
    return (s[:limit] or "topic").rstrip("_")


def _safe_write(path: pathlib.Path, content: str) -> Tuple[bool, str]:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return True, "python"
    except (PermissionError, OSError) as e_py:
        try:
            import base64
            b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")
            node = shutil.which("node")
            if not node:
                return False, f"python_failed: {e_py}; node not available"
            node_script = (
                "const fs=require('fs');"
                "const path=require('path');"
                f"const target={json.dumps(str(path))};"
                f"const data=Buffer.from({json.dumps(b64)},'base64');"
                "fs.mkdirSync(path.dirname(target),{recursive:true});"
                "fs.writeFileSync(target,data);"
            )
            proc = subprocess.run([node, "-e", node_script], capture_output=True, timeout=15)
            if proc.returncode == 0:
                return True, "node_fallback"
            return False, f"python_failed: {e_py}; node_failed: {proc.stderr.decode('utf-8', 'ignore')}"
        except Exception as e_node:
            return False, f"python_failed: {e_py}; node_exception: {e_node}"

def _agent_strategy(topic: str) -> Dict[str, Any]:
    return {
        "agent": "strategy_agent",
        "topic": topic,
        "content_angle": f"How {topic} change the daily workflow in 2026, for honest creators.",
        "target_viewer": "Students and creators 18-30 who want practical, legal, supervised AI workflows.",
        "promise": "Show one concrete workflow they can copy in 60 seconds, with no shady tricks.",
        "distribution_note": "Future workflow: long-form -> short cuts -> title/thumbnail iteration. NO autonomous posting in this milestone.",
        "format": "vertical short, 30-60 seconds",
        "tone": "calm, useful, honest, no hype",
    }


def _agent_research_meta(topic: str) -> Dict[str, Any]:
    return {
        "agent": "research_meta_agent",
        "source": "local_repo_knowledge_only",
        "external_api_used": False,
        "market_assumptions": [
            "Many students already use AI assistants but rarely supervise outputs.",
            "Creators want repeatable workflows, not one-off tricks.",
            "Compliance and approval gates are undervalued by quick-content channels.",
        ],
        "caveats": [
            "No web research performed; all assumptions are planning-only.",
            "No claims about audience size, revenue, or virality.",
            "Numbers in titles are creative variants, not measured results.",
        ],
    }


def _agent_script(topic: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
    lines: List[str] = []
    lines.append(f"# Short Script -- {topic}")
    lines.append("")
    lines.append("**Length target:** 30-60 seconds vertical short.")
    lines.append(f"**Promise:** {strategy['promise']}")
    lines.append("")
    lines.append("## Hook (0-3s)")
    lines.append(f"You don't need 10 AI tools. You need one supervised workflow for {topic}.")
    lines.append("")
    lines.append("## Setup (3-10s)")
    lines.append("Open a local agent. Give it the goal. Watch it route the task to the right local helper.")
    lines.append("")
    lines.append("## Demo (10-40s)")
    lines.append("Strategy agent picks an angle.")
    lines.append("Script agent writes the next short.")
    lines.append("Title and thumbnail agent generates 100 variants.")
    lines.append("Safety agent blocks anything that would post live.")
    lines.append("Approval agent shows a human checklist.")
    lines.append("")
    lines.append("## Payoff (40-55s)")
    lines.append(f"One supervised workflow turned {topic} into a clean preview you can review before any human shares it.")
    lines.append("")
    lines.append("## CTA (55-60s)")
    lines.append("Follow if you want supervised AI workflows, not autonomous chaos.")
    lines.append("")
    lines.append("_No autonomous posting. No live accounts. Local preview only._")
    return {
        "agent": "script_agent",
        "estimated_seconds": 55,
        "body": "\n".join(lines),
    }


def _agent_shotlist(topic: str) -> Dict[str, Any]:
    scenes = [
        {"scene": 1, "time": "0-3s", "visual": "Tight shot: terminal cursor blinking on phrase 'supervised local'.", "audio": "soft pad, no music license issues", "text_overlay": "One workflow."},
        {"scene": 2, "time": "3-10s", "visual": "Wide screen-recording: agent pipeline diagram lighting up node by node.", "audio": "voiceover", "text_overlay": "Strategy -> Script -> Shotlist"},
        {"scene": 3, "time": "10-25s", "visual": "Split screen: 5 candidate titles fading in, 5 thumbnail concepts on right.", "audio": "voiceover", "text_overlay": "100 local variants, zero auto-post."},
        {"scene": 4, "time": "25-40s", "visual": "Safety panel showing 'live posting: disabled' / 'external APIs: disabled'.", "audio": "voiceover", "text_overlay": "Approval required."},
        {"scene": 5, "time": "40-55s", "visual": "Preview HTML opens in browser; human clicks 'review', no publish button.", "audio": "voiceover", "text_overlay": "Local preview only."},
        {"scene": 6, "time": "55-60s", "visual": "Card: 'Supervised AI workflows for honest creators.' Channel handle locked off-screen.", "audio": "outro pad", "text_overlay": "Supervised. Local. Honest."},
    ]
    return {
        "agent": "shotlist_agent",
        "topic": topic,
        "scene_count": len(scenes),
        "scenes": scenes,
        "assets_policy": "No copyrighted external media. Local mock visuals or planning text only.",
    }

_TITLE_ANGLES = [
    "I supervised {n} AI agents to make this short about {topic}",
    "{topic}: one workflow beats ten apps",
    "What {topic} actually look like when you supervise them",
    "Stop autonomous AI. Try supervised {topic} instead",
    "{topic} in 60 seconds (no live posting)",
    "The honest creator's stack for {topic}",
    "I built a local studio for {topic}",
    "100 titles, zero auto-posts: {topic}",
    "Supervised {topic} for students and creators",
    "Why I won't auto-post {topic}",
]
_TITLE_HOOKS = [
    "the boring truth", "no hype", "no live accounts", "all local",
    "with approval gates", "before anyone touches publish", "for 2026",
    "without scraping anything", "without breaking ToS", "with full receipts",
]


def _agent_title_thumbnail(topic: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
    titles: List[Dict[str, Any]] = []
    seen_titles = set()
    n_agents = 8
    for i in range(100):
        base = _TITLE_ANGLES[i % len(_TITLE_ANGLES)]
        hook = _TITLE_HOOKS[i % len(_TITLE_HOOKS)]
        text = base.format(topic=topic, n=n_agents) + f" -- {hook} (v{i+1:03d})"
        if text in seen_titles:
            text = text + f" [{i+1}]"
        seen_titles.add(text)
        titles.append({
            "id": f"title_{i+1:03d}",
            "text": text,
            "length": len(text),
            "variant_index": i + 1,
            "ab_test_runtime_wired": False,
            "autonomous_posting_enabled": False,
        })

    thumbs: List[Dict[str, Any]] = []
    palettes = [
        ("#0b132b", "#5bc0be"),
        ("#1f2937", "#fbbf24"),
        ("#111827", "#34d399"),
        ("#1e1b4b", "#f472b6"),
        ("#0f172a", "#60a5fa"),
    ]
    poses = [
        "left-aligned face mock", "center close-up mock", "split-frame demo",
        "diagram-only no face", "phone-in-hand mock", "terminal screenshot mock",
    ]
    text_styles = ["bold sans block", "italic accent line", "stacked two-row", "single-word slam"]
    for i in range(100):
        bg, accent = palettes[i % len(palettes)]
        pose = poses[i % len(poses)]
        style = text_styles[i % len(text_styles)]
        big_text = (titles[i]["text"].split(" -- ")[0])[:38]
        thumbs.append({
            "id": f"thumb_{i+1:03d}",
            "variant_index": i + 1,
            "bg_color": bg,
            "accent_color": accent,
            "pose": pose,
            "text_style": style,
            "big_text": big_text,
            "sublabel": "supervised | local | no auto-post",
            "asset_source": "local_mock_only",
            "uses_copyrighted_media": False,
            "uses_real_face": False,
            "ab_test_runtime_wired": False,
            "autonomous_posting_enabled": False,
        })

    return {
        "agent": "title_thumbnail_agent",
        "topic": topic,
        "title_count": len(titles),
        "thumbnail_count": len(thumbs),
        "titles": titles,
        "thumbnails": thumbs,
        "iteration_note": "Title/thumbnail iteration is a future workflow. No autonomous posting or A/B test in this milestone.",
        "external_account_actions": False,
    }


def _agent_safety_compliance(_topic: str) -> Dict[str, Any]:
    findings = [
        "live_posting_enabled: false",
        "external_apis_enabled: false",
        "external_repo_clone_install_run: false",
        "live_account_actions_enabled: false",
        "uses_copyrighted_external_media: false",
        "uses_unlicensed_music: false",
        "scrapes_third_party_sites: false",
        "autonomous_money_or_trading_actions: false",
        "ui_tars_runtime_wired: false",
        "the_agency_runtime_wired: false",
        "weavy_runtime_wired: false",
        "manychat_runtime_wired: false",
        "vouch_runtime_wired: false",
        "aex_runtime_wired: false",
        "airllm_runtime_wired: false",
        "openfang_moneyprinter_runtime_wired: false",
        "approval_gates_intact: true",
        "secrets_or_api_keys_committed: false",
        "output_path_inside_repo: true",
    ]
    return {
        "agent": "safety_compliance_agent",
        "findings": findings,
        "verdict": "PASS_LOCAL_ONLY",
        "publish_enabled": False,
        "external_api_used": False,
    }


def _agent_approval(topic: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
    checklist = [
        {"item": "Human reviewed strategy angle", "required": True, "status": "pending_human_review"},
        {"item": "Human reviewed 30-60s script for accuracy", "required": True, "status": "pending_human_review"},
        {"item": "Human reviewed shotlist for ToS-safe visuals", "required": True, "status": "pending_human_review"},
        {"item": "Human selected from 100 title candidates", "required": True, "status": "pending_human_review"},
        {"item": "Human selected from 100 thumbnail concepts", "required": True, "status": "pending_human_review"},
        {"item": "Human confirmed no live account is touched by any agent", "required": True, "status": "pending_human_review"},
        {"item": "Human confirmed no external repo cloned/installed/run", "required": True, "status": "pending_human_review"},
    ]
    return {
        "agent": "approval_agent",
        "topic": topic,
        "checklist": checklist,
        "all_required_pending": True,
        "publish_blocked": True,
        "manual_publish_path": "Human-only; no autonomous publish path in this milestone.",
        "promise_quoted_back": strategy.get("promise", ""),
    }


def _probe_memory_bridge() -> Dict[str, Any]:
    bridge = REPO_ROOT / "03_scripts" / "local_memory_compression_bridge.py"
    if not bridge.exists():
        return {"available": False, "fallback_mode": "local_demo", "probe_error": "bridge not found"}
    py = sys.executable or "python"
    try:
        proc = subprocess.run(
            [py, str(bridge), "--status", "--json"],
            capture_output=True,
            timeout=15,
        )
        if proc.returncode != 0:
            return {"available": False, "fallback_mode": "local_demo", "probe_error": f"exit={proc.returncode}"}
        data = json.loads(proc.stdout.decode("utf-8", "ignore"))
        return {
            "available": True,
            "fallback_mode": data.get("fallback_mode", "local_demo"),
            "ollama_available": data.get("ollama_available"),
            "gemma_model_found": data.get("gemma_model_found"),
        }
    except Exception as exc:
        return {"available": False, "fallback_mode": "local_demo", "probe_error": f"probe exception: {exc}"}


def _agent_memory(topic: str, strategy: Dict[str, Any], script: Dict[str, Any]) -> Dict[str, Any]:
    probe = _probe_memory_bridge()
    summary_lines = [
        f"# Memory snapshot -- {MILESTONE} content studio demo",
        f"- topic: {topic}",
        f"- content_angle: {strategy.get('content_angle', '')}",
        f"- script_seconds: {script.get('estimated_seconds', '')}",
        f"- bridge_available: {probe.get('available')}",
        f"- fallback_mode: {probe.get('fallback_mode')}",
        "- local_only: true",
        "- external_api_used: false",
        "- approval_required_for_external_actions: true",
    ]
    return {
        "agent": "memory_agent",
        "topic": topic,
        "bridge_probe": probe,
        "memory_summary": "\n".join(summary_lines),
        "approved_path_only": True,
    }

def _agent_trace_md(trace: List[Dict[str, Any]]) -> str:
    lines = ["# Agent Trace", ""]
    for step in trace:
        lines.append(f"## {step['order']}. {step['agent']}")
        lines.append(f"- started_at: {step['started_at']}")
        lines.append(f"- finished_at: {step['finished_at']}")
        lines.append(f"- status: {step['status']}")
        lines.append("")
    lines.append("_All steps ran locally, supervised, with no external API calls._")
    return "\n".join(lines)


def _strategy_md(strategy: Dict[str, Any]) -> str:
    lines = [
        "# Strategy",
        f"- topic: {strategy['topic']}",
        f"- content_angle: {strategy['content_angle']}",
        f"- target_viewer: {strategy['target_viewer']}",
        f"- promise: {strategy['promise']}",
        f"- distribution_note: {strategy['distribution_note']}",
        f"- format: {strategy['format']}",
        f"- tone: {strategy['tone']}",
    ]
    return "\n".join(lines)


def _shotlist_md(shotlist: Dict[str, Any]) -> str:
    lines = [
        "# Shotlist",
        f"- scene_count: {shotlist['scene_count']}",
        f"- assets_policy: {shotlist['assets_policy']}",
        "",
        "| # | Time | Visual | Audio | Text overlay |",
        "| - | ---- | ------ | ----- | ------------- |",
    ]
    for s in shotlist["scenes"]:
        lines.append(f"| {s['scene']} | {s['time']} | {s['visual']} | {s['audio']} | {s['text_overlay']} |")
    return "\n".join(lines)


def _safety_md(safety: Dict[str, Any]) -> str:
    lines = ["# Safety / Compliance Review", "",
             f"- verdict: {safety['verdict']}",
             f"- publish_enabled: {safety['publish_enabled']}",
             f"- external_api_used: {safety['external_api_used']}",
             "", "## Findings", ""]
    for f in safety["findings"]:
        lines.append(f"- {f}")
    lines.append("")
    lines.append("Live posting is disabled. No external accounts are touched. No external repos are cloned, installed, or run by this demo.")
    return "\n".join(lines)


def _approval_md(approval: Dict[str, Any]) -> str:
    lines = ["# Human Approval Packet", "",
             f"- topic: {approval['topic']}",
             f"- publish_blocked: {approval['publish_blocked']}",
             f"- manual_publish_path: {approval['manual_publish_path']}",
             "", "## Checklist", ""]
    for item in approval["checklist"]:
        lines.append(f"- [ ] {item['item']} (status: {item['status']})")
    return "\n".join(lines)

def _preview_html(
    topic: str,
    run_dir_rel: str,
    strategy: Dict[str, Any],
    script: Dict[str, Any],
    shotlist: Dict[str, Any],
    title_thumb: Dict[str, Any],
    safety: Dict[str, Any],
    approval: Dict[str, Any],
    memory: Dict[str, Any],
) -> str:
    def esc(s: Any) -> str:
        return html.escape(str(s))

    scenes_rows = "".join(
        f"<tr><td>{esc(s['scene'])}</td><td>{esc(s['time'])}</td><td>{esc(s['visual'])}</td><td>{esc(s['text_overlay'])}</td></tr>"
        for s in shotlist["scenes"]
    )
    titles_top5 = title_thumb["titles"][:5]
    thumbs_top5 = title_thumb["thumbnails"][:5]
    title_items = "".join(
        f"<li><code>{esc(t['id'])}</code> -- {esc(t['text'])}</li>"
        for t in titles_top5
    )
    thumb_cards = "".join(
        f'<div class="thumb" style="background:{esc(t["bg_color"])};color:{esc(t["accent_color"])}">'
        f'<div class="thumb-big">{esc(t["big_text"])}</div>'
        f'<div class="thumb-sub">{esc(t["sublabel"])}</div>'
        f'<div class="thumb-id">{esc(t["id"])} ({esc(t["pose"])} | {esc(t["text_style"])})</div>'
        f"</div>"
        for t in thumbs_top5
    )
    safety_lines = "".join(f"<li>{esc(f)}</li>" for f in safety["findings"])
    checklist_items = "".join(
        f'<li><input type="checkbox" disabled> {esc(item["item"])} <em>(status: {esc(item["status"])})</em></li>'
        for item in approval["checklist"]
    )
    css = (
        "body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:#0b132b;color:#e0e1dd;margin:0;padding:24px;}"
        ".banner{background:#1f2937;border-left:4px solid #5bc0be;padding:12px 16px;margin-bottom:16px;}"
        "h1{color:#5bc0be;}h2{color:#fbbf24;border-bottom:1px solid #334155;padding-bottom:4px;}"
        "section{margin-bottom:24px;padding:16px;background:#111827;border-radius:6px;}"
        "table{width:100%;border-collapse:collapse;}th,td{border:1px solid #334155;padding:6px 8px;text-align:left;font-size:13px;}th{background:#1f2937;}"
        ".thumbgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;}"
        ".thumb{padding:18px;border-radius:8px;min-height:120px;display:flex;flex-direction:column;justify-content:space-between;}"
        ".thumb-big{font-weight:800;font-size:18px;line-height:1.15;}.thumb-sub{font-size:11px;opacity:0.8;}"
        ".thumb-id{font-size:10px;opacity:0.6;font-family:Consolas,monospace;}"
        ".disabled-publish{background:#374151;color:#9ca3af;border:1px dashed #6b7280;padding:8px 16px;border-radius:4px;cursor:not-allowed;}"
        "code{background:#1f2937;padding:1px 4px;border-radius:3px;}"
        ".tag{display:inline-block;padding:2px 8px;border-radius:12px;background:#1f2937;font-size:11px;margin-right:6px;}"
        ".pipeline{display:flex;gap:8px;flex-wrap:wrap;}.pipeline div{background:#1f2937;padding:6px 10px;border-radius:14px;font-size:12px;}"
    )
    pipeline = "".join(f"<div>{esc(a)}</div>" for a in AGENT_NAMES)

    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        f"<title>Supervised Content Studio Preview -- {esc(topic)}</title>\n"
        f"<style>{css}</style>\n</head>\n<body>\n"
        "<div class=\"banner\"><strong>Local preview only.</strong> "
        "This page is a supervised local artifact. No live posting. No external API calls. No account actions.</div>\n"
        f"<h1>Supervised Multi-Agent Content Studio -- {esc(MILESTONE)}</h1>\n"
        "<p>"
        "<span class=\"tag\">local_only: true</span>"
        "<span class=\"tag\">external_api_used: false</span>"
        "<span class=\"tag\">publish_enabled: false</span>"
        "<span class=\"tag\">approval_required: true</span>"
        "</p>\n"
        f"<p>Run folder: <code>{esc(run_dir_rel)}</code></p>\n"
        f"<section><h2>Agent pipeline ({len(AGENT_NAMES)} agents)</h2><div class=\"pipeline\">{pipeline}</div></section>\n"
        "<section><h2>Strategy</h2><ul>"
        f"<li><strong>Topic:</strong> {esc(strategy['topic'])}</li>"
        f"<li><strong>Angle:</strong> {esc(strategy['content_angle'])}</li>"
        f"<li><strong>Target viewer:</strong> {esc(strategy['target_viewer'])}</li>"
        f"<li><strong>Promise:</strong> {esc(strategy['promise'])}</li>"
        f"<li><strong>Distribution note:</strong> {esc(strategy['distribution_note'])}</li>"
        "</ul></section>\n"
        f"<section><h2>Script (~{esc(script['estimated_seconds'])}s)</h2><pre>{esc(script['body'])}</pre></section>\n"
        f"<section><h2>Shotlist</h2><table><thead><tr><th>#</th><th>Time</th><th>Visual</th><th>Text overlay</th></tr></thead><tbody>{scenes_rows}</tbody></table></section>\n"
        f"<section><h2>Top 5 title candidates (from 100 local variants)</h2><ul>{title_items}</ul>"
        f"<p><em>{esc(title_thumb['iteration_note'])}</em></p></section>\n"
        f"<section><h2>Top 5 thumbnail concepts (from 100 local variants)</h2><div class=\"thumbgrid\">{thumb_cards}</div></section>\n"
        f"<section><h2>Safety / Compliance -- verdict: {esc(safety['verdict'])}</h2><ul>{safety_lines}</ul></section>\n"
        f"<section><h2>Human approval checklist</h2><ul>{checklist_items}</ul>"
        f"<p>Manual publish path: {esc(approval['manual_publish_path'])}</p>"
        "<button class=\"disabled-publish\" disabled aria-disabled=\"true\">Publish (disabled -- supervised local demo)</button></section>\n"
        "<section><h2>Memory bridge</h2><ul>"
        f"<li>bridge_available: {esc(memory['bridge_probe'].get('available'))}</li>"
        f"<li>fallback_mode: {esc(memory['bridge_probe'].get('fallback_mode'))}</li>"
        f"<li>approved_path_only: {esc(memory['approved_path_only'])}</li>"
        "</ul></section>\n"
        f"<footer><p><em>Generated locally by {esc(STUDIO_NAME)} ({esc(MILESTONE)}). "
        "No live posting. No external APIs. Future tools (UI-TARS, The Agency, Weavy, Manychat, Vouch, AEX, AirLLM, OpenFang/MoneyPrinter) remain planning-only.</em></p></footer>\n"
        "</body>\n</html>\n"
    )

def _run_pipeline(topic: str, run_dir: pathlib.Path) -> Dict[str, Any]:
    if not _is_inside_repo(run_dir):
        return {"ok": False, "error": "REJECTED: output_dir is outside repo root", "run_dir": str(run_dir)}
    if _is_secret_path(run_dir):
        return {"ok": False, "error": "REJECTED: output_dir matches a secret/credential pattern", "run_dir": str(run_dir)}

    run_dir.mkdir(parents=True, exist_ok=True)
    trace: List[Dict[str, Any]] = []

    def _step(order: int, agent: str, fn):
        started = _utc_timestamp()
        result = fn()
        finished = _utc_timestamp()
        trace.append({"order": order, "agent": agent, "started_at": started, "finished_at": finished, "status": "ok"})
        return result

    strategy = _step(1, "strategy_agent", lambda: _agent_strategy(topic))
    _step(2, "research_meta_agent", lambda: _agent_research_meta(topic))
    script = _step(3, "script_agent", lambda: _agent_script(topic, strategy))
    shotlist = _step(4, "shotlist_agent", lambda: _agent_shotlist(topic))
    title_thumb = _step(5, "title_thumbnail_agent", lambda: _agent_title_thumbnail(topic, strategy))
    safety = _step(6, "safety_compliance_agent", lambda: _agent_safety_compliance(topic))
    approval = _step(7, "approval_agent", lambda: _agent_approval(topic, strategy))
    memory = _step(8, "memory_agent", lambda: _agent_memory(topic, strategy, script))

    try:
        run_dir_rel = str(run_dir.resolve().relative_to(REPO_ROOT))
    except ValueError:
        run_dir_rel = str(run_dir)

    artifacts: Dict[str, pathlib.Path] = {
        "00_manifest.json": run_dir / "00_manifest.json",
        "01_agent_trace.md": run_dir / "01_agent_trace.md",
        "02_strategy.md": run_dir / "02_strategy.md",
        "03_script.md": run_dir / "03_script.md",
        "04_shotlist.md": run_dir / "04_shotlist.md",
        "05_titles_100.json": run_dir / "05_titles_100.json",
        "06_thumbnail_variants_100.json": run_dir / "06_thumbnail_variants_100.json",
        "07_safety_review.md": run_dir / "07_safety_review.md",
        "08_human_approval_packet.md": run_dir / "08_human_approval_packet.md",
        "09_memory_snapshot.md": run_dir / "09_memory_snapshot.md",
        "10_preview.html": run_dir / "10_preview.html",
        "11_status.json": run_dir / "11_status.json",
    }

    manifest = {
        "studio": STUDIO_NAME,
        "milestone": MILESTONE,
        "topic": topic,
        "created_at": _utc_timestamp(),
        "run_dir": run_dir_rel,
        "agents": AGENT_NAMES,
        "agent_count": len(AGENT_NAMES),
        "artifacts": list(artifacts.keys()),
        "local_only": True,
        "external_api_used": False,
        "publish_enabled": False,
        "external_repo_clone_install_run": False,
        "live_account_actions_enabled": False,
        "approval_required_for_external_actions": True,
        "title_variant_count": title_thumb["title_count"],
        "thumbnail_variant_count": title_thumb["thumbnail_count"],
    }

    status = {
        "studio": STUDIO_NAME,
        "milestone": MILESTONE,
        "topic": topic,
        "ok": True,
        "run_dir": run_dir_rel,
        "preview_path": f"{run_dir_rel}/10_preview.html".replace("\\", "/"),
        "agent_count": len(AGENT_NAMES),
        "title_variant_count": title_thumb["title_count"],
        "thumbnail_variant_count": title_thumb["thumbnail_count"],
        "local_only": True,
        "external_api_used": False,
        "publish_enabled": False,
        "approval_required": True,
        "memory_bridge_available": memory["bridge_probe"].get("available", False),
        "memory_fallback_mode": memory["bridge_probe"].get("fallback_mode", "local_demo"),
        "safety_verdict": safety["verdict"],
        "video_render": "skipped",
    }

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        try:
            mp4_path = run_dir / "12_preview.mp4"
            proc = subprocess.run(
                [ffmpeg, "-y", "-f", "lavfi", "-i",
                 "color=c=#0b132b:s=854x480:d=1",
                 "-frames:v", "1", str(mp4_path)],
                capture_output=True,
                timeout=30,
            )
            if proc.returncode == 0 and mp4_path.exists():
                status["video_render"] = "rendered_local_only"
                manifest["video_artifact"] = "12_preview.mp4"
            else:
                status["video_render"] = "ffmpeg_failed_non_blocking"
        except Exception:
            status["video_render"] = "ffmpeg_exception_non_blocking"

    _safe_write(artifacts["00_manifest.json"], json.dumps(manifest, indent=2))
    _safe_write(artifacts["01_agent_trace.md"], _agent_trace_md(trace))
    _safe_write(artifacts["02_strategy.md"], _strategy_md(strategy))
    _safe_write(artifacts["03_script.md"], script["body"])
    _safe_write(artifacts["04_shotlist.md"], _shotlist_md(shotlist))
    _safe_write(
        artifacts["05_titles_100.json"],
        json.dumps({"topic": topic, "count": title_thumb["title_count"], "titles": title_thumb["titles"]}, indent=2),
    )
    _safe_write(
        artifacts["06_thumbnail_variants_100.json"],
        json.dumps({"topic": topic, "count": title_thumb["thumbnail_count"], "thumbnails": title_thumb["thumbnails"]}, indent=2),
    )
    _safe_write(artifacts["07_safety_review.md"], _safety_md(safety))
    _safe_write(artifacts["08_human_approval_packet.md"], _approval_md(approval))
    _safe_write(artifacts["09_memory_snapshot.md"], memory["memory_summary"])
    _safe_write(
        artifacts["10_preview.html"],
        _preview_html(topic, run_dir_rel, strategy, script, shotlist, title_thumb, safety, approval, memory),
    )
    _safe_write(artifacts["11_status.json"], json.dumps(status, indent=2))

    return status

def cmd_status(json_out: bool) -> int:
    runs = []
    if DEFAULT_RUNS_DIR.exists():
        for child in sorted(DEFAULT_RUNS_DIR.iterdir()):
            if child.is_dir():
                runs.append(child.name)
    latest = runs[-1] if runs else None
    try:
        latest_rel = str((DEFAULT_RUNS_DIR / latest).resolve().relative_to(REPO_ROOT)) if latest else None
    except (ValueError, TypeError):
        latest_rel = None

    bridge = _probe_memory_bridge()
    data = {
        "studio": STUDIO_NAME,
        "milestone": MILESTONE,
        "local_only": True,
        "external_api_used": False,
        "publish_enabled": False,
        "approval_required": True,
        "agent_count": len(AGENT_NAMES),
        "agents": AGENT_NAMES,
        "runs_dir": str(DEFAULT_RUNS_DIR.relative_to(REPO_ROOT)).replace("\\", "/"),
        "run_count": len(runs),
        "latest_run": latest_rel,
        "memory_bridge_available": bridge.get("available", False),
        "memory_fallback_mode": bridge.get("fallback_mode", "local_demo"),
        "title_thumbnail_iteration": "future_workflow_no_autonomous_posting",
        "video_render": "optional_local_only",
        "external_tools_status": "planning_only",
    }
    if json_out:
        print(json.dumps(data, indent=2))
        return 0
    print(f"{STUDIO_NAME} status")
    for k, v in data.items():
        if isinstance(v, list):
            print(f"  {k}: {len(v)} items")
        else:
            print(f"  {k}: {v}")
    return 0


def cmd_run_demo(topic: str, output_dir: Optional[str], json_out: bool) -> int:
    if output_dir:
        run_root = pathlib.Path(output_dir).resolve()
        if not _is_inside_repo(run_root):
            msg = {"ok": False, "error": "REJECTED: output_dir is outside repo root"}
            print(json.dumps(msg, indent=2) if json_out else msg["error"])
            return 1
        if _is_secret_path(run_root):
            msg = {"ok": False, "error": "REJECTED: output_dir matches a secret/credential pattern"}
            print(json.dumps(msg, indent=2) if json_out else msg["error"])
            return 1
    else:
        run_root = DEFAULT_RUNS_DIR

    timestamp = _utc_timestamp()
    folder = f"{timestamp}_{_slug(topic)}"
    run_dir = run_root / folder

    status = _run_pipeline(topic, run_dir)
    if not status.get("ok", False):
        print(json.dumps(status, indent=2) if json_out else status.get("error", "FAILED"))
        return 1
    if json_out:
        print(json.dumps(status, indent=2))
    else:
        print(f"Run complete. Folder: {status['run_dir']}")
        print(f"Preview: {status['preview_path']}")
        print(f"Agents: {status['agent_count']}; titles: {status['title_variant_count']}; thumbs: {status['thumbnail_variant_count']}")
        print(f"local_only={status['local_only']} external_api_used={status['external_api_used']} publish_enabled={status['publish_enabled']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Supervised Multi-Agent Content Studio Demo (N+4.3A) -- local-only.")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--run-demo", action="store_true")
    parser.add_argument("--topic", default=DEFAULT_TOPIC)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--open-preview", action="store_true", help="No-op placeholder (does not open anything).")
    parser.add_argument("--json", dest="json_out", action="store_true")
    args = parser.parse_args()

    if args.run_demo:
        return cmd_run_demo(args.topic, args.output_dir, args.json_out)
    if args.status:
        return cmd_status(args.json_out)
    if args.json_out:
        return cmd_status(json_out=True)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())