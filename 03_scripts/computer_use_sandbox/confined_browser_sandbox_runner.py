#!/usr/bin/env python3
"""N+6.14A Confined Local Browser Sandbox Action Runner.

Standard library only. This runner performs a DOM-level action against a LOCAL,
offline sandbox HTML file using a headless Chromium-family browser (Chrome or
Edge) that is launched with a TEMPORARY, isolated user-data directory and driven
over a 127.0.0.1-only DevTools (CDP) endpoint.

It is deliberately confined:

- It never navigates to a website; http/https targets are rejected.
- It only accepts a local file under 14_context/computer_use/sandbox/.
- It uses a throwaway temporary profile, never a normal user profile.
- It uses no OS-level mouse/keyboard input.
- It uses no third-party automation packages (only the standard library).
- Dry-run is the default. A real local browser is launched only with the
  explicit --allow-local-browser-sandbox flag, and only when confinement holds.
- If a browser/CDP endpoint is unavailable, it returns a safe no-action result.

This is NOT live web automation, account automation, desktop control, or any
form of bot/stealth/proxy automation.
"""

import argparse
import base64
import json
import os
import re
import shutil
import socket
import struct
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

REPO_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = (REPO_ROOT / "14_context" / "computer_use" / "sandbox").resolve()
DEFAULT_TARGET = SANDBOX_ROOT / "sandbox_target.html"
FLAGS_PATH = SANDBOX_ROOT / "feature_flags_confined_browser_sandbox.json"

NOTE_VALUE = "GHOTI_OK"
NOTE_ID = "note-input"
BUTTON_ID = "status-button"
OUTPUT_ID = "status-output"

NEXT_STEP_N6_14B = (
    "N+6.14B / N+6.15: harden the confined CDP utility (or a local Gemma-worker "
    "driver) under separate audit before any non-sandbox target is considered; "
    "the harness stays local-sandbox-only until then."
)

# Capabilities that stay blocked this milestone. Descriptive underscore-joined
# names keep posture data from being mistaken for real implementations.
BLOCKED_ACTIONS = (
    "live_website_navigation",
    "http_or_https_target",
    "account_login_automation",
    "captcha_or_bot_bypass",
    "stealth_or_proxy_automation",
    "os_level_mouse_or_keyboard_input",
    "arbitrary_window_control",
    "arbitrary_shell_execution",
    "third_party_repo_code_execution",
    "dependency_install",
    "normal_user_browser_profile",
)

DEFAULT_FLAGS = {
    "global_kill_switch_engaged": True,
    "confined_browser_sandbox_enabled": False,
    "confined_browser_sandbox_dry_run_enabled": True,
    "confined_browser_cdp_enabled": False,
    "confined_browser_dom_action_enabled": False,
    "live_browser_navigation_enabled": False,
    "os_level_input_enabled": False,
    "strict_confinement_required": True,
}

ATTRIBUTION = {
    "note": "design inspiration only; no third-party code copied or vendored",
    "patterns_adapted": [
        "TryCUA / CUA Driver (MIT) - capability/policy separation; sandbox isolation",
        "Browser Harness (MIT) - thin observe-then-act loop",
        "Vercel agent-browser (Apache-2.0) - discrete explicit commands over a devtools channel",
        "Ruflo / claude-flow (MIT) - coordinator/worker hand-off with local memory",
    ],
}

# External / network resource indicators. A sandbox file that references any of
# these is refused, because the action must run against a fully offline target.
EXTERNAL_RESOURCE_PATTERNS = (
    re.compile(r"<\s*script[^>]*\bsrc\s*=", re.I),
    re.compile(r"<\s*link[^>]*\bhref\s*=", re.I),
    re.compile(r"<\s*img[^>]*\bsrc\s*=", re.I),
    re.compile(r"<\s*iframe[^>]*\bsrc\s*=", re.I),
    re.compile(r"https?://", re.I),
    re.compile(r"\bsrc\s*=\s*[\"']//", re.I),
    re.compile(r"@import", re.I),
)


def load_flags():
    """Load the dedicated confined-browser flag file, falling back to defaults."""
    try:
        data = json.loads(FLAGS_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            merged = dict(DEFAULT_FLAGS)
            merged.update(data)
            return merged
    except (OSError, json.JSONDecodeError):
        pass
    return dict(DEFAULT_FLAGS)


def _safety_block():
    return {
        "only_standard_library": True,
        "third_party_automation_packages_used": False,
        "os_level_input_used": False,
        "live_website_navigated": False,
        "account_login_performed": False,
        "normal_browser_profile_used": False,
        "network_used_beyond_loopback_cdp": False,
        "shell_execution_used": False,
        "captcha_or_bot_bypass_used": False,
    }


def scan_external_resources(html_text):
    """Return the list of external-resource indicators found (empty == clean)."""
    hits = []
    for pat in EXTERNAL_RESOURCE_PATTERNS:
        if pat.search(html_text):
            hits.append(pat.pattern)
    return hits


def validate_target(target_str):
    """Validate the requested target path.

    Returns (ok, info, reject_reason). Rejects URL schemes (http/https/etc.),
    paths outside the sandbox root, missing files, and non-HTML files.
    """
    info = {
        "requested_target": target_str,
        "is_url": False,
        "target_is_local": False,
        "target_under_sandbox_root": False,
        "target_exists": False,
    }
    lowered = target_str.strip().lower()
    if "://" in lowered or lowered.startswith("http:") or lowered.startswith("https:"):
        info["is_url"] = True
        return False, info, "rejected: remote or URL targets are not allowed (local sandbox file only)"
    raw = Path(target_str)
    if not raw.is_absolute():
        raw = REPO_ROOT / raw
    try:
        resolved = raw.resolve()
    except OSError:
        return False, info, "rejected: target path could not be resolved"
    info["resolved_target"] = str(resolved)
    try:
        resolved.relative_to(SANDBOX_ROOT)
    except ValueError:
        return False, info, "rejected: target is outside the sandbox root"
    info["target_under_sandbox_root"] = True
    info["target_is_local"] = True
    if not resolved.is_file():
        return False, info, "rejected: target file does not exist"
    info["target_exists"] = True
    if resolved.suffix.lower() not in (".html", ".htm"):
        return False, info, "rejected: target is not a local HTML sandbox file"
    info["resolved_path_obj"] = resolved
    return True, info, None


def _result_skeleton(mode, info, flags):
    return {
        "ok": True,
        "milestone": "N+6.14A",
        "tool": "confined_browser_sandbox_runner",
        "mode": mode,
        "target": info.get("requested_target"),
        "resolved_target": info.get("resolved_target"),
        "target_is_local": True,
        "target_under_sandbox_root": True,
        "target_exists": True,
        "live_website": False,
        "account_context": False,
        "os_input_used": False,
        "browser_launched": False,
        "dom_action_performed": False,
        "requires_human_approval": True,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "feature_flags": flags,
        "global_kill_switch_engaged": flags.get("global_kill_switch_engaged", True),
        "attribution": ATTRIBUTION,
        "safety": _safety_block(),
    }


def _rejection_result(mode, info, flags, reason):
    return {
        "ok": False,
        "milestone": "N+6.14A",
        "tool": "confined_browser_sandbox_runner",
        "mode": mode,
        "target": info.get("requested_target"),
        "resolved_target": info.get("resolved_target"),
        "rejected": True,
        "rejected_reason": reason,
        "is_url": info.get("is_url", False),
        "target_is_local": info.get("target_is_local", False),
        "target_under_sandbox_root": info.get("target_under_sandbox_root", False),
        "target_exists": info.get("target_exists", False),
        "live_website": False,
        "account_context": False,
        "os_input_used": False,
        "browser_launched": False,
        "dom_action_performed": False,
        "requires_human_approval": True,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "feature_flags": flags,
        "safety": _safety_block(),
    }


# ---------------------------------------------------------------------------
# Browser discovery (standard install locations + PATH lookup; no secrets).
# ---------------------------------------------------------------------------
def _browser_candidates():
    candidates = []
    bases = [Path(r"C:\Program Files"), Path(r"C:\Program Files (x86)")]
    rels = [
        Path("Google/Chrome/Application/chrome.exe"),
        Path("Microsoft/Edge/Application/msedge.exe"),
        Path("Chromium/Application/chrome.exe"),
    ]
    for base in bases:
        for rel in rels:
            candidates.append(base / rel)
    home = Path.home()
    candidates.append(home / "AppData/Local/Google/Chrome/Application/chrome.exe")
    candidates.append(home / "AppData/Local/Microsoft/Edge/Application/msedge.exe")
    for name in ("chrome", "chrome.exe", "msedge", "msedge.exe", "chromium", "chromium-browser", "google-chrome"):
        found = shutil.which(name)
        if found:
            candidates.append(Path(found))
    seen, ordered = set(), []
    for cand in candidates:
        key = str(cand).lower()
        if key not in seen:
            seen.add(key)
            ordered.append(cand)
    return ordered


def find_browser():
    for cand in _browser_candidates():
        try:
            if cand.is_file():
                return cand
        except OSError:
            continue
    return None


# ---------------------------------------------------------------------------
# Minimal RFC 6455 WebSocket client (text frames) over a blocking socket. Used
# only to talk to the local 127.0.0.1 DevTools endpoint.
# ---------------------------------------------------------------------------
def _recv_exact(sock, count):
    chunks, got = [], 0
    while got < count:
        chunk = sock.recv(count - got)
        if not chunk:
            raise ConnectionError("socket closed")
        chunks.append(chunk)
        got += len(chunk)
    return b"".join(chunks)


def _recv_until(sock, marker):
    data = b""
    while marker not in data:
        chunk = sock.recv(1)
        if not chunk:
            break
        data += chunk
        if len(data) > 65536:
            break
    return data


class _WebSocket:
    def __init__(self, host, port, path, timeout=6.0):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        handshake = (
            "GET %s HTTP/1.1\r\n"
            "Host: %s:%d\r\n"
            "Origin: http://%s:%d\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Key: %s\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        ) % (path, host, port, host, port, key)
        self.sock.sendall(handshake.encode("ascii"))
        resp = _recv_until(self.sock, b"\r\n\r\n")
        status_line = resp.split(b"\r\n", 1)[0]
        if b"101" not in status_line:
            raise ConnectionError("websocket upgrade rejected")

    def send_text(self, text):
        payload = text.encode("utf-8")
        n = len(payload)
        header = bytearray([0x81])  # FIN + text opcode
        if n < 126:
            header.append(0x80 | n)
        elif n < 65536:
            header.append(0x80 | 126)
            header += struct.pack(">H", n)
        else:
            header.append(0x80 | 127)
            header += struct.pack(">Q", n)
        mask = os.urandom(4)
        header += mask
        masked = bytes(payload[i] ^ mask[i % 4] for i in range(n))
        self.sock.sendall(bytes(header) + masked)

    def recv_text(self):
        b0 = _recv_exact(self.sock, 1)[0]
        opcode = b0 & 0x0F
        b1 = _recv_exact(self.sock, 1)[0]
        masked = bool(b1 & 0x80)
        length = b1 & 0x7F
        if length == 126:
            length = struct.unpack(">H", _recv_exact(self.sock, 2))[0]
        elif length == 127:
            length = struct.unpack(">Q", _recv_exact(self.sock, 8))[0]
        mask = _recv_exact(self.sock, 4) if masked else None
        data = _recv_exact(self.sock, length) if length else b""
        if mask:
            data = bytes(data[i] ^ mask[i % 4] for i in range(len(data)))
        if opcode == 0x8:
            raise ConnectionError("websocket closed by peer")
        if opcode in (0x9, 0xA):  # ping/pong -> read the next frame
            return self.recv_text()
        return data.decode("utf-8", errors="replace")

    def close(self):
        try:
            self.sock.sendall(bytes([0x88, 0x80]) + os.urandom(4))
        except OSError:
            pass
        try:
            self.sock.close()
        except OSError:
            pass


def _cdp_call(ws, msg_id, method, params, deadline):
    ws.send_text(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
    while True:
        if time.time() > deadline:
            raise TimeoutError("cdp response timeout")
        try:
            data = json.loads(ws.recv_text())
        except json.JSONDecodeError:
            continue
        if data.get("id") == msg_id:
            return data


def _build_dom_js():
    return (
        "(function(){"
        "var n=document.getElementById(%s);"
        "var b=document.getElementById(%s);"
        "var o=document.getElementById(%s);"
        "if(!n||!b||!o){return JSON.stringify({ok:false,reason:'missing_element'});}"
        "n.value=%s;"
        "b.click();"
        "return JSON.stringify({ok:true,note:n.value,status:o.textContent});"
        "})()"
    ) % (json.dumps(NOTE_ID), json.dumps(BUTTON_ID), json.dumps(OUTPUT_ID), json.dumps(NOTE_VALUE))


def _http_get_json(url, timeout=1.5):
    with urlopen(url, timeout=timeout) as resp:  # 127.0.0.1 loopback only
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def _free_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]
    finally:
        sock.close()


def perform_local_browser_action(target_path, result):
    """Launch a confined headless browser and run the sandbox DOM action.

    Always returns the (mutated) result dict. On any failure it records a
    blocked_or_unavailable_reason and performs no action.
    """
    browser = find_browser()
    result["browser_executable_found"] = browser is not None
    if browser is None:
        result["blocked_or_unavailable_reason"] = "no local Chromium-family browser found in standard locations"
        return result

    port = _free_port()
    profile_dir = tempfile.mkdtemp(prefix="ghoti_confined_browser_")
    result["temporary_profile_used"] = True
    args = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        "--disable-background-networking",
        "--remote-allow-origins=*",
        "--remote-debugging-port=%d" % port,
        "--user-data-dir=%s" % profile_dir,
        target_path.as_uri(),
    ]
    proc = None
    ws = None
    try:
        proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        version = None
        deadline = time.time() + 10.0
        while time.time() < deadline:
            if proc.poll() is not None:
                break
            try:
                version = _http_get_json("http://127.0.0.1:%d/json/version" % port, timeout=1.0)
                break
            except (URLError, ConnectionError, OSError, ValueError):
                time.sleep(0.2)
        if version is None:
            result["blocked_or_unavailable_reason"] = "local CDP endpoint did not become available"
            return result
        result["browser_launched"] = True

        ws_url = None
        deadline2 = time.time() + 6.0
        while time.time() < deadline2 and not ws_url:
            try:
                targets = _http_get_json("http://127.0.0.1:%d/json" % port, timeout=1.0)
            except (URLError, ConnectionError, OSError, ValueError):
                time.sleep(0.2)
                continue
            for tgt in targets:
                if tgt.get("type") == "page" and str(tgt.get("url", "")).lower().startswith("file:"):
                    ws_url = tgt.get("webSocketDebuggerUrl")
                    break
            if not ws_url:
                for tgt in targets:
                    if tgt.get("type") == "page" and tgt.get("webSocketDebuggerUrl"):
                        ws_url = tgt.get("webSocketDebuggerUrl")
                        break
            if not ws_url:
                time.sleep(0.2)
        if not ws_url:
            result["blocked_or_unavailable_reason"] = "no local page target exposed by CDP"
            return result

        match = re.match(r"ws://([^:/]+):(\d+)(/.*)$", ws_url)
        if not match:
            result["blocked_or_unavailable_reason"] = "unexpected CDP websocket url"
            return result
        host, ws_port, ws_path = match.group(1), int(match.group(2)), match.group(3)
        if host not in ("127.0.0.1", "localhost"):
            result["blocked_or_unavailable_reason"] = "refused non-loopback CDP host"
            return result

        ws = _WebSocket(host, ws_port, ws_path, timeout=6.0)
        call_deadline = time.time() + 8.0
        _cdp_call(ws, 1, "Runtime.enable", {}, call_deadline)
        action = None
        for attempt in range(2):
            resp = _cdp_call(
                ws, 2 + attempt, "Runtime.evaluate",
                {"expression": _build_dom_js(), "returnByValue": True},
                call_deadline,
            )
            value = (((resp or {}).get("result") or {}).get("result") or {}).get("value")
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                except json.JSONDecodeError:
                    parsed = None
                if parsed and parsed.get("ok"):
                    action = parsed
                    break
            time.sleep(0.25)
        if not action:
            result["blocked_or_unavailable_reason"] = "DOM action did not complete in the sandbox page"
            return result

        result["dom_action_performed"] = True
        result["note_value"] = action.get("note")
        result["status_output"] = action.get("status")
        result["goal_satisfied"] = action.get("note") == NOTE_VALUE and action.get("status") == NOTE_VALUE
        result["cdp_browser"] = version.get("Browser") if isinstance(version, dict) else None
        return result
    except (OSError, ConnectionError, TimeoutError, ValueError) as exc:
        result["blocked_or_unavailable_reason"] = "confined browser action error: %s" % type(exc).__name__
        return result
    finally:
        if ws is not None:
            ws.close()
        if proc is not None:
            try:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)
            except OSError:
                pass
        shutil.rmtree(profile_dir, ignore_errors=True)
        result["temporary_profile_cleaned"] = not os.path.isdir(profile_dir)


def run(target_str, allow_local=False):
    flags = load_flags()
    mode = "local_browser_sandbox" if allow_local else "dry_run"
    ok, info, reject_reason = validate_target(target_str)
    if not ok:
        return _rejection_result(mode, info, flags, reject_reason)

    html_text = info["resolved_path_obj"].read_text(encoding="utf-8", errors="replace")
    external = scan_external_resources(html_text)
    if external:
        result = _rejection_result(mode, info, flags,
                                   "rejected: sandbox file references external or network resources")
        result["target_has_external_resources"] = True
        return result

    result = _result_skeleton(mode, info, flags)
    result["target_has_external_resources"] = False

    if not allow_local:
        result["next_step"] = (
            "Pass --allow-local-browser-sandbox to perform the confined DOM action in a "
            "temporary, isolated local browser profile. " + NEXT_STEP_N6_14B
        )
        return result

    result = perform_local_browser_action(info["resolved_path_obj"], result)
    if not result.get("dom_action_performed"):
        result.setdefault("blocked_or_unavailable_reason", "confined browser action unavailable")
        result["next_step"] = NEXT_STEP_N6_14B
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="N+6.14A confined local browser sandbox action runner (stdlib only)")
    parser.add_argument("--target", default=str(DEFAULT_TARGET),
                        help="local sandbox HTML file under 14_context/computer_use/sandbox/")
    parser.add_argument("--allow-local-browser-sandbox", action="store_true",
                        help="launch a temporary, isolated local browser to perform the confined DOM action")
    parser.add_argument("--json", action="store_true", help="emit JSON (default output is JSON)")
    args = parser.parse_args(argv)
    result = run(args.target, allow_local=args.allow_local_browser_sandbox)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
