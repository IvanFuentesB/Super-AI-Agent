#!/usr/bin/env python3
"""Validate and exchange repo-local Ghoti agent handoff packets.

Commands recorded in packets are audit evidence only. This tool never executes
packet content, starts agents, calls a model, or uses the network.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
MEMORY_ROOT = REPO_ROOT / "14_context" / "memory"
INDEX_PATH = MEMORY_ROOT / "index" / "handoff_index.json"
ALLOWED_AGENTS = ("claude", "codex", "hermes", "chatgpt", "local_models")
MAX_PACKET_BYTES = 65_536
MAX_LIST_ITEMS = 100
MAX_STRING_CHARS = 4_000
MARKDOWN_WORD_BUDGET = 1_200

REQUIRED_FIELDS = (
    "schema_version",
    "packet_id",
    "agent_name",
    "agent_role",
    "branch",
    "task",
    "files_touched",
    "commands_run",
    "tests_passed",
    "tests_failed",
    "blockers",
    "next_recommended_action",
    "generated_at",
    "source_sha256",
    "artifact_sha256",
    "safety",
)
ALLOWED_PACKET_FIELDS = frozenset(REQUIRED_FIELDS)
ALLOWED_SAFETY_FIELDS = frozenset(("contains_secrets", "live_actions_executed", "human_approval_required"))

_PACKET_ID_RE = re.compile(r"^[a-z0-9_]+-[0-9]{8}-[a-z0-9][a-z0-9-]{2,100}$")
_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
_PRIVATE_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+", re.I),
    re.compile(r"/mnt/[a-z]/Users/", re.I),
    re.compile(r"/home/[^/\s]+/", re.I),
)
_SECRET_VALUE_PATTERNS = (
    re.compile(r"\b(?:OPENAI|ANTHROPIC|GEMINI|GOOGLE|TELEGRAM|GITHUB)_?[A-Z_]*(?:KEY|TOKEN|SECRET)\s*=\s*\S+", re.I),
    re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}", re.I),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}", re.I),
    re.compile(r"\bghp_[A-Za-z0-9_]{20,}", re.I),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----", re.I),
)
_NODE_WRITE_SCRIPT = (
    "const fs=require('fs'),p=require('path');"
    "const dest=process.argv[1],data=Buffer.from(process.argv[2],'base64');"
    "fs.mkdirSync(p.dirname(dest),{recursive:true});"
    "fs.writeFileSync(dest,data);"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w.+/-]+\b", text))


def _ascii_text(text: str) -> str:
    replacements = {"\ufeff": "", "\u2013": "-", "\u2014": "-", "\u2192": "->", "\u2194": "<->"}
    for source, replacement in replacements.items():
        text = text.replace(source, replacement)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def _contains_sensitive_value(text: str) -> bool:
    return any(pattern.search(text) for pattern in (*_PRIVATE_PATH_PATTERNS, *_SECRET_VALUE_PATTERNS))


def _repo_relative_path(value: str) -> bool:
    path = Path(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts and not _contains_sensitive_value(value)


def _valid_generated_at(value: Any) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        dt.datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError:
        return False
    return True


def _walk_values(value: Any, errors: list[str], location: str = "packet") -> None:
    if isinstance(value, str):
        if len(value) > MAX_STRING_CHARS:
            errors.append(f"{location} string exceeds {MAX_STRING_CHARS} characters")
        if _contains_sensitive_value(value):
            errors.append(f"{location} contains a private path or secret-like value")
    elif isinstance(value, list):
        if len(value) > MAX_LIST_ITEMS:
            errors.append(f"{location} exceeds {MAX_LIST_ITEMS} items")
        for index, item in enumerate(value):
            _walk_values(item, errors, f"{location}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            _walk_values(key, errors, f"{location}.key")
            _walk_values(item, errors, f"{location}.{key}")


def validate_packet(packet: Any) -> dict:
    errors: list[str] = []
    if not isinstance(packet, dict):
        errors.append("packet must be a JSON object")
        return _validation_result(errors)

    encoded = json.dumps(packet, sort_keys=True, ensure_ascii=True).encode("utf-8")
    if len(encoded) > MAX_PACKET_BYTES:
        errors.append(f"packet exceeds {MAX_PACKET_BYTES} bytes")

    for field in REQUIRED_FIELDS:
        if field not in packet:
            errors.append(f"missing required field: {field}")
    for field in sorted(set(packet) - ALLOWED_PACKET_FIELDS):
        errors.append(f"unknown top-level field: {field}")
    if errors:
        _walk_values(packet, errors)
        return _validation_result(errors)

    agent = packet["agent_name"]
    if agent not in ALLOWED_AGENTS:
        errors.append(f"agent_name must be one of: {', '.join(ALLOWED_AGENTS)}")
    if not isinstance(packet["packet_id"], str) or not _PACKET_ID_RE.fullmatch(packet["packet_id"]):
        errors.append("packet_id has invalid format")
    elif isinstance(agent, str) and not packet["packet_id"].startswith(f"{agent}-"):
        errors.append("packet_id must start with agent_name")

    for field in ("schema_version", "agent_role", "branch", "task", "next_recommended_action"):
        if not isinstance(packet[field], str) or not packet[field].strip():
            errors.append(f"{field} must be a non-empty string")

    for field in ("files_touched", "commands_run", "tests_passed", "tests_failed", "blockers"):
        if not isinstance(packet[field], list) or not all(isinstance(item, str) for item in packet[field]):
            errors.append(f"{field} must be a list of strings")

    for path in packet.get("files_touched", []):
        if isinstance(path, str) and not _repo_relative_path(path):
            errors.append(f"files_touched path must be repo-relative: {path}")

    for field in ("source_sha256", "artifact_sha256"):
        mapping = packet[field]
        if not isinstance(mapping, dict):
            errors.append(f"{field} must be an object")
            continue
        for path, digest in mapping.items():
            if not isinstance(path, str) or not _repo_relative_path(path):
                errors.append(f"{field} path must be repo-relative: {path}")
            if not isinstance(digest, str) or not _SHA256_RE.fullmatch(digest):
                errors.append(f"{field} contains invalid SHA-256 for: {path}")

    if not _valid_generated_at(packet["generated_at"]):
        errors.append("generated_at must be an ISO-8601 UTC timestamp ending in Z")

    safety = packet["safety"]
    if not isinstance(safety, dict):
        errors.append("safety must be an object")
    else:
        for field in sorted(set(safety) - ALLOWED_SAFETY_FIELDS):
            errors.append(f"unknown safety field: {field}")
        if safety.get("contains_secrets") is not False:
            errors.append("safety.contains_secrets must be false")
        if safety.get("live_actions_executed") is not False:
            errors.append("safety.live_actions_executed must be false")
        if safety.get("human_approval_required") is not True:
            errors.append("safety.human_approval_required must be true")

    _walk_values(packet, errors)
    return _validation_result(errors)


def _validation_result(errors: list[str]) -> dict:
    unique_errors = list(dict.fromkeys(errors))
    return {
        "ok": not unique_errors,
        "errors": unique_errors,
        "local_only": True,
        "executes_commands": False,
        "network_used": False,
        "model_used": False,
        "live_actions_enabled": False,
        "human_approval_required": True,
    }


def verify_packet_evidence(packet: dict, repo_root: Path = REPO_ROOT) -> dict:
    root = repo_root.resolve()
    mismatches = []
    verified = 0
    for field in ("source_sha256", "artifact_sha256"):
        for raw_path, expected in packet.get(field, {}).items():
            path = (root / raw_path).resolve()
            try:
                path.relative_to(root)
            except ValueError:
                actual = None
            else:
                actual = sha256_file(path) if path.is_file() else None
            verified += 1
            if actual != expected:
                mismatches.append(
                    {
                        "kind": field,
                        "path": raw_path,
                        "expected": expected,
                        "actual": actual,
                    }
                )
    return {
        "ok": not mismatches,
        "status": "current" if not mismatches else "stale",
        "mismatches": mismatches,
        "verified_items": verified,
    }


def render_packet_markdown(packet: dict) -> str:
    validation = validate_packet(packet)
    if not validation["ok"]:
        raise ValueError("; ".join(validation["errors"]))

    def section(title: str, values: list[str]) -> list[str]:
        lines = [f"## {title}", ""]
        lines.extend(f"- {_ascii_text(value)}" for value in values)
        if not values:
            lines.append("- None")
        lines.append("")
        return lines

    lines = [
        f"# Agent Handoff: {_ascii_text(packet['packet_id'])}",
        "",
        "> Evidence and coordination packet only. Do not execute command evidence.",
        "",
        f"- Agent: `{packet['agent_name']}`",
        f"- Role: `{_ascii_text(packet['agent_role'])}`",
        f"- Branch: `{_ascii_text(packet['branch'])}`",
        f"- Generated at: `{packet['generated_at']}`",
        "- Local only: true",
        "- Human approval required: true",
        "- Live actions executed: false",
        "",
        "## Task",
        "",
        _ascii_text(packet["task"]),
        "",
    ]
    lines.extend(section("Files Touched", packet["files_touched"]))
    lines.extend(section("Command Evidence - Do Not Execute", packet["commands_run"]))
    lines.extend(section("Tests Passed", packet["tests_passed"]))
    lines.extend(section("Tests Failed", packet["tests_failed"]))
    lines.extend(section("Blockers", packet["blockers"]))
    lines.extend(
        [
            "## Next Recommended Action",
            "",
            _ascii_text(packet["next_recommended_action"]),
            "",
            "## Hash Evidence",
            "",
        ]
    )
    for label, mapping in (("Source", packet["source_sha256"]), ("Artifact", packet["artifact_sha256"])):
        if not mapping:
            lines.append(f"- {label}: none")
        for path, digest in sorted(mapping.items()):
            lines.append(f"- {label}: `{path}` - SHA-256 `{digest}`")
    lines.append("")
    rendered = _ascii_text("\n".join(lines))
    if word_count(rendered) > MARKDOWN_WORD_BUDGET:
        raise ValueError("rendered packet exceeds Markdown word budget")
    return rendered


def _agent_root(memory_root: Path, agent: str, box: str) -> Path:
    if agent not in ALLOWED_AGENTS:
        raise ValueError(f"unknown agent: {agent}")
    if box not in ("inbox", "outbox"):
        raise ValueError(f"unknown handoff box: {box}")
    return memory_root.resolve() / "agent_handoffs" / agent / box


def _write_immutable(path: Path, content: str) -> bool:
    expected = content.encode("utf-8")
    if path.exists():
        if path.read_bytes() != expected:
            raise FileExistsError(f"immutable handoff artifact already exists: {path.name}")
        return False
    _safe_write_text(path, content)
    return True


def _safe_write_text(path: Path, content: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        return
    except OSError:
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        result = subprocess.run(
            ["node", "-e", _NODE_WRITE_SCRIPT, str(path), encoded],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise OSError(f"safe data-only write fallback failed for {path.name}: {result.stderr.strip()}")


def write_packet(packet: dict, memory_root: Path = MEMORY_ROOT) -> dict:
    validation = validate_packet(packet)
    if not validation["ok"]:
        raise ValueError("; ".join(validation["errors"]))
    outbox = _agent_root(memory_root, packet["agent_name"], "outbox")
    json_path = outbox / f"{packet['packet_id']}.json"
    markdown_path = outbox / f"{packet['packet_id']}.md"
    json_text = json.dumps(packet, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    markdown_text = render_packet_markdown(packet)
    created = [
        _write_immutable(json_path, json_text),
        _write_immutable(markdown_path, markdown_text),
    ]
    return {
        "ok": True,
        "packet_id": packet["packet_id"],
        "agent_name": packet["agent_name"],
        "written": [str(json_path), str(markdown_path)],
        "idempotent": not any(created),
        "local_only": True,
        "executes_commands": False,
        "live_actions_enabled": False,
    }


def _find_packet(memory_root: Path, packet_id: str) -> Path:
    matches = []
    for agent in ALLOWED_AGENTS:
        candidate = _agent_root(memory_root, agent, "outbox") / f"{packet_id}.json"
        if candidate.is_file():
            matches.append(candidate)
    if not matches:
        raise FileNotFoundError(f"packet not found: {packet_id}")
    if len(matches) > 1:
        raise ValueError(f"packet id is not unique: {packet_id}")
    return matches[0]


def deliver_packet(packet_id: str, recipient_agent: str, memory_root: Path = MEMORY_ROOT) -> dict:
    source = _find_packet(memory_root, packet_id)
    packet = json.loads(source.read_text(encoding="utf-8"))
    validation = validate_packet(packet)
    if not validation["ok"]:
        raise ValueError("source packet is invalid: " + "; ".join(validation["errors"]))
    inbox = _agent_root(memory_root, recipient_agent, "inbox")
    pointer_path = inbox / f"{packet_id}.delivery.json"
    pointer = {
        "schema_version": "1.0",
        "delivery_id": f"{packet_id}-to-{recipient_agent}",
        "packet_id": packet_id,
        "source_agent": packet["agent_name"],
        "recipient_agent": recipient_agent,
        "source_packet_path": source.relative_to(memory_root.resolve()).as_posix(),
        "source_packet_sha256": sha256_file(source),
        "delivered_at": packet["generated_at"],
        "local_only": True,
        "read_only_pointer": True,
        "executes_commands": False,
        "live_actions_enabled": False,
        "human_approval_required": True,
    }
    created = _write_immutable(pointer_path, json.dumps(pointer, indent=2, sort_keys=True) + "\n")
    return {
        "ok": True,
        "packet_id": packet_id,
        "recipient_agent": recipient_agent,
        "written": str(pointer_path),
        "idempotent": not created,
        "local_only": True,
        "executes_commands": False,
        "live_actions_enabled": False,
    }


def build_handoff_index(memory_root: Path = MEMORY_ROOT) -> dict:
    root = memory_root.resolve()
    packets = []
    deliveries = []
    generated_at_values = []
    for agent in ALLOWED_AGENTS:
        outbox = _agent_root(root, agent, "outbox")
        if outbox.is_dir():
            for path in sorted(outbox.glob("*.json")):
                packet = json.loads(path.read_text(encoding="utf-8"))
                validation = validate_packet(packet)
                packets.append(
                    {
                        "packet_id": packet.get("packet_id"),
                        "agent_name": agent,
                        "path": path.relative_to(root).as_posix(),
                        "sha256": sha256_file(path),
                        "generated_at": packet.get("generated_at"),
                        "valid": validation["ok"],
                    }
                )
                if _valid_generated_at(packet.get("generated_at")):
                    generated_at_values.append(packet["generated_at"])
        inbox = _agent_root(root, agent, "inbox")
        if inbox.is_dir():
            for path in sorted(inbox.glob("*.delivery.json")):
                pointer = json.loads(path.read_text(encoding="utf-8"))
                deliveries.append(
                    {
                        "delivery_id": pointer.get("delivery_id"),
                        "packet_id": pointer.get("packet_id"),
                        "recipient_agent": agent,
                        "path": path.relative_to(root).as_posix(),
                        "sha256": sha256_file(path),
                        "source_packet_path": pointer.get("source_packet_path"),
                        "source_packet_sha256": pointer.get("source_packet_sha256"),
                    }
                )
    state_lines = [f"{item['path']}:{item['sha256']}" for item in [*packets, *deliveries]]
    return {
        "schema_version": "1.0",
        "memory_type": "shared_agent_handoff_index",
        "generated_at": max(generated_at_values) if generated_at_values else None,
        "generated_at_source": "newest_packet_timestamp",
        "handoff_state_sha256": hashlib.sha256("\n".join(state_lines).encode("utf-8")).hexdigest(),
        "packet_count": len(packets),
        "delivery_count": len(deliveries),
        "local_only": True,
        "executes_commands": False,
        "live_actions_enabled": False,
        "packets": packets,
        "deliveries": deliveries,
    }


def verify_handoff_index(memory_root: Path, index: dict) -> dict:
    root = memory_root.resolve()
    mismatches = []
    for item in [*index.get("packets", []), *index.get("deliveries", [])]:
        path = root / item["path"]
        actual = sha256_file(path) if path.is_file() else None
        if actual != item["sha256"]:
            mismatches.append({"path": item["path"], "expected": item["sha256"], "actual": actual})
    for delivery in index.get("deliveries", []):
        source = root / delivery["source_packet_path"]
        actual = sha256_file(source) if source.is_file() else None
        if actual != delivery["source_packet_sha256"]:
            mismatches.append(
                {
                    "path": delivery["source_packet_path"],
                    "expected": delivery["source_packet_sha256"],
                    "actual": actual,
                }
            )
    return {"ok": not mismatches, "mismatches": mismatches, "verified_items": len(index.get("packets", [])) + len(index.get("deliveries", []))}


def _repo_local_input(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("input path must be repo-relative")
    resolved = (REPO_ROOT / path).resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise ValueError("input path escapes repo root") from exc
    return resolved


def _write_index(index: dict) -> None:
    _safe_write_text(INDEX_PATH, json.dumps(index, indent=2, sort_keys=True) + "\n")


def check() -> dict:
    example = MEMORY_ROOT / "examples" / "agent_handoff_packet.example.json"
    packet = json.loads(example.read_text(encoding="utf-8"))
    validation = validate_packet(packet)
    evidence = verify_packet_evidence(packet, REPO_ROOT) if validation["ok"] else {"ok": False}
    index = build_handoff_index(MEMORY_ROOT)
    verify = verify_handoff_index(MEMORY_ROOT, index)
    expected_paths = [
        MEMORY_ROOT / "schemas" / "agent_handoff_packet.schema.json",
        MEMORY_ROOT / "index" / "handoff_index.json",
    ]
    for agent in ALLOWED_AGENTS:
        expected_paths.extend((_agent_root(MEMORY_ROOT, agent, "inbox") / ".gitkeep", _agent_root(MEMORY_ROOT, agent, "outbox") / ".gitkeep"))
    missing = [path.relative_to(REPO_ROOT).as_posix() for path in expected_paths if not path.is_file()]
    return {
        "ok": validation["ok"] and evidence["ok"] and verify["ok"] and not missing,
        "milestone": "N+6.42B",
        "agents": list(ALLOWED_AGENTS),
        "packet_count": index["packet_count"],
        "delivery_count": index["delivery_count"],
        "example_valid": validation["ok"],
        "example_evidence_verified": evidence["ok"],
        "index_verified": verify["ok"],
        "missing": missing,
        "local_only": True,
        "executes_commands": False,
        "network_used": False,
        "model_used": False,
        "live_actions_enabled": False,
        "human_approval_required": True,
        "next_milestone": "N+6.42C Obsidian Vault Setup",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="validate the committed shared handoff contract")
    action.add_argument("--validate", metavar="PACKET", help="validate a repo-local packet without writing")
    action.add_argument("--write", metavar="PACKET", help="write a validated packet to its sender outbox")
    action.add_argument("--deliver", metavar="PACKET_ID", help="deliver a read-only packet pointer to an inbox")
    action.add_argument("--reindex", action="store_true", help="write the deterministic handoff index")
    action.add_argument("--verify", action="store_true", help="verify the committed handoff index hashes")
    parser.add_argument("--to-agent", choices=ALLOWED_AGENTS, help="recipient agent for --deliver")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    try:
        if args.check:
            payload = check()
        elif args.validate:
            packet = json.loads(_repo_local_input(args.validate).read_text(encoding="utf-8"))
            payload = validate_packet(packet)
            evidence = verify_packet_evidence(packet, REPO_ROOT) if payload["ok"] else {"ok": False, "status": "invalid", "mismatches": []}
            payload["evidence"] = evidence
            payload["evidence_verified"] = evidence["ok"]
            payload["ok"] = payload["ok"] and evidence["ok"]
        elif args.write:
            packet = json.loads(_repo_local_input(args.write).read_text(encoding="utf-8"))
            evidence = verify_packet_evidence(packet, REPO_ROOT)
            if not evidence["ok"]:
                raise ValueError("packet evidence is stale or missing")
            payload = write_packet(packet, MEMORY_ROOT)
            payload["evidence_verified"] = True
            _write_index(build_handoff_index(MEMORY_ROOT))
        elif args.deliver:
            if not args.to_agent:
                raise ValueError("--deliver requires --to-agent")
            payload = deliver_packet(args.deliver, args.to_agent, MEMORY_ROOT)
            _write_index(build_handoff_index(MEMORY_ROOT))
        elif args.reindex:
            index = build_handoff_index(MEMORY_ROOT)
            _write_index(index)
            payload = {"ok": True, "written": INDEX_PATH.relative_to(REPO_ROOT).as_posix(), **index}
        else:
            payload = verify_handoff_index(MEMORY_ROOT, json.loads(INDEX_PATH.read_text(encoding="utf-8")))
    except (FileNotFoundError, FileExistsError, ValueError, json.JSONDecodeError, OSError) as exc:
        payload = {
            "ok": False,
            "error": str(exc),
            "local_only": True,
            "executes_commands": False,
            "live_actions_enabled": False,
        }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
