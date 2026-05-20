#!/usr/bin/env python3
"""UI-TARS Observation-Only adapter (N+5.0A) — SAFE, observation-only.

This is the first UI-TARS-related adapter. It is strictly OBSERVATION ONLY:

  - it does NOT run UI-TARS or import any UI-TARS package
  - it does NOT execute any external repo code
  - it does NOT click, type, move the mouse, or press hotkeys
  - it does NOT control the desktop or call any live API
  - it produces a local "observation packet" of Ghoti-owned artifacts

The only optional desktop interaction is a single read-only screen capture,
and only when: a valid human approval token is supplied AND it is not a
dry run. The capture uses built-in Windows PowerShell/.NET (no external
screenshot library). If capture is unavailable it degrades truthfully and
the observation packet is still produced.

local-only; standard library only; no external repo imports.
"""
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ADAPTER_PROMOTED = True

ADAPTER_KEY = "ui_tars_observation_only"
ADAPTER_NAME = "UI-TARS Observation Only"
REQUIRES_HUMAN_APPROVAL = True

REPO_ROOT = Path(__file__).parent.parent.parent.resolve()
SANDBOX_DIR = REPO_ROOT / "21_repos" / "third_party" / "sandboxed"

# Sandboxed UI-TARS repos to read STATIC metadata from (never run).
_UI_TARS_SANDBOX = [
    ("ui_tars_desktop", "UI-TARS Desktop"),
    ("ui_tars_model", "UI-TARS Model"),
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def status() -> dict:
    """Adapter status — observation-only; not wired; no desktop control."""
    return {
        "adapter": ADAPTER_NAME,
        "adapter_key": ADAPTER_KEY,
        "adapter_kind": "observation_only",
        "promoted": True,
        "wired": False,
        "runtime_wiring": "observation_only",
        "local_only": True,
        "ui_tars_runtime_started": False,
        "external_code_imported": False,
        "external_code_executed": False,
        "installs_performed": False,
        "desktop_control_enabled": False,
        "click_enabled": False,
        "type_enabled": False,
        "hotkeys_enabled": False,
        "live_api_enabled": False,
        "approval_required_for_capture": True,
        "requires_human_approval": REQUIRES_HUMAN_APPROVAL,
    }


def capabilities() -> list:
    """What this observation-only adapter can do locally."""
    return [
        "generate a local UI-TARS observation packet (Ghoti-owned artifacts)",
        "dry-run observation with no screenshot and no approval token",
        "read static metadata from sandboxed UI-TARS repos (never run them)",
        "optional approval-gated read-only screen capture (local PNG only)",
    ]


def safety_gates() -> list:
    """Gates that hold for this adapter."""
    return [
        "human_approval_required",
        "observation_only_no_desktop_control",
        "no_click_no_type_no_hotkeys",
        "no_ui_tars_runtime",
        "no_external_repo_code_execution",
        "no_dependency_install",
        "no_live_api_calls",
        "screenshot_capture_requires_approval_token",
        "non_dry_run_requires_approval_token",
    ]


def _ui_tars_static_context() -> dict:
    """Read STATIC metadata from sandboxed UI-TARS repos. Never runs them."""
    repos = []
    for key, name in _UI_TARS_SANDBOX:
        repo_dir = SANDBOX_DIR / key
        entry = {"key": key, "name": name, "sandbox_present": repo_dir.is_dir()}
        if repo_dir.is_dir():
            readme_excerpt = None
            try:
                for child in sorted(repo_dir.iterdir()):
                    if child.is_file() and child.name.lower().startswith("readme"):
                        readme_excerpt = child.read_text(
                            encoding="utf-8", errors="ignore")[:1200]
                        break
            except Exception:
                readme_excerpt = None
            entry["readme_excerpt_present"] = readme_excerpt is not None
            entry["readme_excerpt"] = readme_excerpt
        repos.append(entry)
    return {
        "sandbox_dir_present": SANDBOX_DIR.is_dir(),
        "repos": repos,
    }


def _capture_screenshot(dest_png: Path) -> dict:
    """Read-only screen capture via built-in Windows PowerShell/.NET.

    Captures pixels only — no click, type, or mouse action. Degrades
    truthfully if a desktop session / capture is unavailable. Never raises.
    """
    result = {"screenshot_captured": False, "screenshot_path": None,
              "screenshot_skipped_reason": None}
    script = (
        "try {\n"
        "  Add-Type -AssemblyName System.Windows.Forms\n"
        "  Add-Type -AssemblyName System.Drawing\n"
        "  $b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds\n"
        "  $bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height\n"
        "  $g = [System.Drawing.Graphics]::FromImage($bmp)\n"
        "  $g.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size)\n"
        "  $bmp.Save('%s', [System.Drawing.Imaging.ImageFormat]::Png)\n"
        "  $g.Dispose(); $bmp.Dispose()\n"
        "  Write-Output 'CAPTURE_OK'\n"
        "} catch { Write-Output ('CAPTURE_FAILED: ' + $_.Exception.Message) }\n"
        % str(dest_png).replace("\\", "\\\\").replace("'", "''")
    )
    script_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ps1", delete=False, encoding="utf-8") as fh:
            fh.write(script)
            script_path = fh.name
        proc = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-NoProfile", "-File", script_path],
            capture_output=True, text=True, timeout=40, shell=False,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        if dest_png.exists() and dest_png.stat().st_size > 100 and "CAPTURE_OK" in out:
            result["screenshot_captured"] = True
            result["screenshot_path"] = str(dest_png)
        else:
            result["screenshot_skipped_reason"] = (
                "screen capture unavailable: " + out.strip()[:300]
                if out.strip() else "screen capture produced no image")
    except subprocess.TimeoutExpired:
        result["screenshot_skipped_reason"] = "screen capture timed out"
    except FileNotFoundError:
        result["screenshot_skipped_reason"] = "powershell not available"
    except Exception as exc:
        result["screenshot_skipped_reason"] = "screen capture error: %s" % exc
    finally:
        if script_path:
            try:
                os.unlink(script_path)
            except OSError:
                pass
    return result


def create_observation_packet(output_dir, dry_run=True, capture_screen=False,
                               approval_token=None) -> dict:
    """Produce a local UI-TARS observation packet under output_dir.

    Writes 00-05 + 10_preview.html. A read-only screen capture is attempted
    only when capture_screen is True, it is not a dry run, and an approval
    token was supplied — otherwise it is skipped truthfully.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    mode = "dry_run" if dry_run else "approved_observation"
    ts = _now()

    static_context = _ui_tars_static_context()

    # Decide whether a screen capture is permitted.
    capture = {"screenshot_captured": False, "screenshot_path": None,
               "screenshot_skipped_reason": None}
    if capture_screen and not dry_run and approval_token:
        capture = _capture_screenshot(output_dir / "screen_capture.png")
    elif capture_screen and dry_run:
        capture["screenshot_skipped_reason"] = "dry run never captures the screen"
    elif capture_screen and not approval_token:
        capture["screenshot_skipped_reason"] = "screen capture requires an approval token"

    observation = {
        "adapter_name": ADAPTER_KEY,
        "mode": mode,
        "dry_run": bool(dry_run),
        "local_only": True,
        "external_repo_code_executed": False,
        "installs_performed": False,
        "ui_tars_runtime_started": False,
        "desktop_control_enabled": False,
        "click_enabled": False,
        "type_enabled": False,
        "hotkeys_enabled": False,
        "live_api_used": False,
        "approval_required_for_capture": True,
        "approval_token_supplied": bool(approval_token),
        "capture_requested": bool(capture_screen),
        "screenshot_captured": capture["screenshot_captured"],
        "screenshot_path": (
            os.path.relpath(capture["screenshot_path"], str(REPO_ROOT)).replace(os.sep, "/")
            if capture["screenshot_path"] else None),
        "screenshot_skipped_reason": capture["screenshot_skipped_reason"],
        "ui_tars_sandbox": static_context,
        "next_safe_step_recommendations": [
            "Review this observation packet with a human.",
            "Approve an explicit screenshot capture only if a visual snapshot is needed.",
            "Do NOT enable UI-TARS runtime, desktop control, click, or type without "
            "a dedicated approved milestone.",
        ],
        "generated_at": ts,
    }

    # 00 manifest — full observation manifest contract (N+5.0B):
    # local_only / click_enabled / type_enabled are required contract fields.
    _write(output_dir / "00_observation_manifest.json", json.dumps({
        "adapter": ADAPTER_KEY,
        "mode": mode,
        "dry_run": bool(dry_run),
        "local_only": True,
        "capture_requested": bool(capture_screen),
        "screenshot_captured": capture["screenshot_captured"],
        "external_repo_code_executed": False,
        "installs_performed": False,
        "ui_tars_runtime_started": False,
        "desktop_control_enabled": False,
        "click_enabled": False,
        "type_enabled": False,
        "live_api_used": False,
        "generated_at": ts,
    }, indent=2))

    # 01 static context
    ctx_lines = ["# UI-TARS Static Context", "",
                 "Static metadata only — the sandboxed UI-TARS repos are read,",
                 "never imported and never run.", ""]
    for repo in static_context["repos"]:
        ctx_lines.append("## %s" % repo["name"])
        ctx_lines.append("")
        ctx_lines.append("- sandbox present: %s" % repo["sandbox_present"])
        if repo.get("readme_excerpt"):
            ctx_lines.append("- README excerpt (static, truncated):")
            ctx_lines.append("")
            ctx_lines.append("```")
            ctx_lines.append(repo["readme_excerpt"].strip()[:900])
            ctx_lines.append("```")
        ctx_lines.append("")
    _write(output_dir / "01_ui_tars_static_context.md", "\n".join(ctx_lines))

    # 02 observation report
    _write(output_dir / "02_observation_report.md", "\n".join([
        "# UI-TARS Observation Report",
        "",
        "Mode: %s" % mode,
        "Generated: %s" % ts,
        "",
        "## What this run did",
        "",
        "- Produced a local observation packet (Ghoti-owned artifacts).",
        "- Read static UI-TARS sandbox metadata: sandbox present = %s."
        % static_context["sandbox_dir_present"],
        "- Screenshot captured: %s." % capture["screenshot_captured"],
        ("- Screenshot skipped: %s." % capture["screenshot_skipped_reason"]
         if capture["screenshot_skipped_reason"] else "- Screenshot: included."),
        "",
        "## What this run did NOT do",
        "",
        "- Did not run UI-TARS or any external repo code.",
        "- Did not install anything.",
        "- Did not click, type, use hotkeys, or control the desktop.",
        "- Did not call any live API or account.",
        "",
    ]))

    # 03 observation json
    _write(output_dir / "03_observation.json", json.dumps(observation, indent=2))

    # 04 safety review
    _write(output_dir / "04_safety_review.md", "\n".join([
        "# UI-TARS Observation Safety Review",
        "",
        "| Safety property | Status |",
        "| --- | --- |",
        "| UI-TARS runtime started | NO |",
        "| External repo code imported | NO |",
        "| External repo code executed | NO |",
        "| Dependencies installed | NO |",
        "| Desktop control enabled | NO |",
        "| Click / type / hotkeys | NO |",
        "| Live API / account calls | NO |",
        "| Screen capture | %s |" % (
            "captured (approval token supplied, local PNG only)"
            if capture["screenshot_captured"] else "not captured"),
        "| Approval required for capture | YES |",
        "",
        "Observation-only. Any future desktop control needs its own approved milestone.",
        "",
    ]))

    # 05 human next steps
    _write(output_dir / "05_human_next_steps.md", "\n".join([
        "# Human Next Steps — UI-TARS observation",
        "",
        "Mode: %s" % mode,
        "",
        "- [ ] Review `02_observation_report.md` and `03_observation.json`.",
        "- [ ] To capture a real screenshot, create an approval token and re-run",
        "      with `--observe --capture-screen --approval-token <token>`.",
        "- [ ] UI-TARS runtime / desktop control remains OUT OF SCOPE until a",
        "      dedicated approved milestone.",
        "",
    ]))

    # 10 preview
    _write(output_dir / "10_preview.html", "\n".join([
        "<!doctype html>",
        "<html><head><meta charset='utf-8'><title>UI-TARS Observation</title></head>",
        "<body style='font-family:system-ui;margin:2rem;max-width:48rem'>",
        "<h1>UI-TARS Observation Packet</h1>",
        "<p>Mode: <strong>%s</strong> &middot; generated %s</p>" % (mode, ts),
        "<ul>",
        "<li>ui_tars_runtime_started: false</li>",
        "<li>desktop_control_enabled: false</li>",
        "<li>click / type / hotkeys: false</li>",
        "<li>external repo code executed: false</li>",
        "<li>screenshot_captured: %s</li>" % str(capture["screenshot_captured"]).lower(),
        "</ul>",
        "<p>Observation-only. No UI-TARS runtime, no desktop control.</p>",
        "</body></html>",
    ]))

    artifacts = [
        "00_observation_manifest.json", "01_ui_tars_static_context.md",
        "02_observation_report.md", "03_observation.json", "04_safety_review.md",
        "05_human_next_steps.md", "10_preview.html",
    ]
    if capture["screenshot_captured"]:
        artifacts.append("screen_capture.png")

    return {
        "ok": True,
        "adapter": ADAPTER_KEY,
        "mode": mode,
        "dry_run": bool(dry_run),
        "screenshot_captured": capture["screenshot_captured"],
        "screenshot_path": observation["screenshot_path"],
        "screenshot_skipped_reason": capture["screenshot_skipped_reason"],
        "external_repo_code_executed": False,
        "installs_performed": False,
        "ui_tars_runtime_started": False,
        "desktop_control_enabled": False,
        "live_api_used": False,
        "artifacts": [str(output_dir / a).replace(os.sep, "/") for a in artifacts],
    }


if __name__ == "__main__":
    print(json.dumps({
        "status": status(),
        "capabilities": capabilities(),
        "safety_gates": safety_gates(),
    }, indent=2))
