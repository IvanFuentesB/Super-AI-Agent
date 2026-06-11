#!/usr/bin/env python3
"""Run Ghoti's optional, disposable, local memory search trial.

The trial builds a deterministic feature-hash vector from sources already
approved by the raw memory index. It does not call a model or provider, store
source text, establish truth, or execute actions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import unicodedata
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MEMORY_ROOT = REPO_ROOT / "14_context" / "memory"
RAW_INDEX_PATH = MEMORY_ROOT / "index" / "raw_index.json"
SEARCH_ROOT = MEMORY_ROOT / "search"
SEARCH_INDEX_PATH = SEARCH_ROOT / "generated" / "local_search_index.json"
EVALUATION_PATH = SEARCH_ROOT / "generated" / "evaluation_result.json"
FIXTURE_PATH = SEARCH_ROOT / "fixtures" / "sanitized_search_eval.json"
ENGINE = "deterministic_local_feature_hash_v1"
VECTOR_DIMENSIONS = 256
MAX_QUERY_CHARS = 500
MAX_RESULTS = 5
MAX_INDEX_BYTES = 100000
HASH_MODE = "sha256_canonical_text_lf_binary_raw"
TEXT_HASH_SUFFIXES = frozenset(
    (".css", ".html", ".js", ".json", ".md", ".ps1", ".py", ".toml", ".txt", ".yaml", ".yml")
)
STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "in",
        "is",
        "it",
        "no",
        "not",
        "of",
        "on",
        "or",
        "the",
        "this",
        "to",
        "with",
    }
)
PRIVATE_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+", re.I),
    re.compile(r"/mnt/[a-z]/Users/", re.I),
    re.compile(r"/home/[^/\s]+/", re.I),
)
SECRET_VALUE_PATTERNS = (
    re.compile(r"\b(?:OPENAI|ANTHROPIC|GEMINI|GOOGLE|TELEGRAM|GITHUB)_?[A-Z_]*(?:KEY|TOKEN|SECRET)\s*=\s*\S+", re.I),
    re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}", re.I),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}", re.I),
    re.compile(r"\bghp_[A-Za-z0-9_]{20,}", re.I),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----", re.I),
)
_NODE_WRITE_SCRIPT = (
    "const fs=require('fs'),p=require('path'),chunks=[];"
    "const dest=process.argv[1];"
    "process.stdin.on('data',chunk=>chunks.push(chunk));"
    "process.stdin.on('end',()=>{"
    "fs.mkdirSync(p.dirname(dest),{recursive:true});"
    "fs.writeFileSync(dest,Buffer.concat(chunks));"
    "});"
)


def safety_flags() -> dict:
    return {
        "local_only": True,
        "read_only_sources": True,
        "canonical_truth": False,
        "disposable": True,
        "network_used": False,
        "model_used": False,
        "remote_embedding_used": False,
        "live_actions_enabled": False,
        "automatic_truth_promotion": False,
    }


def canonical_file_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_HASH_SUFFIXES:
        return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return data


def sha256_file(path: Path) -> str:
    return hashlib.sha256(canonical_file_bytes(path)).hexdigest()


def _repo_relative_path(repo_root: Path, raw_path: str) -> Path:
    relative = Path(raw_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"path must be repo-relative: {raw_path}")
    resolved = (repo_root.resolve() / relative).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(f"path escapes repo root: {raw_path}") from exc
    return resolved


def validate_query(query: str) -> str:
    cleaned = query.strip()
    if not cleaned:
        raise ValueError("query must not be empty")
    if len(cleaned) > MAX_QUERY_CHARS:
        raise ValueError(f"query exceeds {MAX_QUERY_CHARS} characters")
    if any(pattern.search(cleaned) for pattern in (*PRIVATE_PATH_PATTERNS, *SECRET_VALUE_PATTERNS)):
        raise ValueError("query contains a private path or secret-like value")
    return cleaned


def _ascii_lower(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower()


def tokenize(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9]+", _ascii_lower(text))
        if len(token) >= 2 and token not in STOP_WORDS
    ]


def _feature_id(term: str) -> int:
    return int.from_bytes(hashlib.sha256(term.encode("utf-8")).digest()[:4], "big") % VECTOR_DIMENSIONS


def _term_hashes(text: str) -> list[str]:
    return sorted({hashlib.sha256(term.encode("utf-8")).hexdigest()[:16] for term in tokenize(text)})


def feature_vector(text: str) -> list[list[float | int]]:
    counts = Counter(_feature_id(term) for term in tokenize(text))
    magnitude = math.sqrt(sum(value * value for value in counts.values()))
    if not magnitude:
        return []
    return [[feature, round(value / magnitude, 10)] for feature, value in sorted(counts.items())]


def _vector_dict(vector: list[list[float | int]]) -> dict[int, float]:
    return {int(feature): float(weight) for feature, weight in vector}


def _cosine(left: list[list[float | int]], right: list[list[float | int]]) -> float:
    left_map = _vector_dict(left)
    right_map = _vector_dict(right)
    return sum(weight * right_map.get(feature, 0.0) for feature, weight in left_map.items())


def _load_raw_index(repo_root: Path) -> dict:
    path = repo_root / RAW_INDEX_PATH.relative_to(REPO_ROOT)
    if not path.is_file():
        raise FileNotFoundError("raw memory index missing")
    index = json.loads(path.read_text(encoding="utf-8"))
    for source in index.get("sources", []):
        source_path = _repo_relative_path(repo_root, source["path"])
        if not source_path.is_file() or sha256_file(source_path) != source["sha256"]:
            raise ValueError(f"raw memory index is stale: {source['path']}")
    return index


def build_search_index(repo_root: Path = REPO_ROOT) -> dict:
    raw = _load_raw_index(repo_root.resolve())
    sources = []
    for source in raw["sources"]:
        if not source.get("summary_safe"):
            continue
        source_path = _repo_relative_path(repo_root.resolve(), source["path"])
        text = source_path.read_text(encoding="utf-8", errors="replace")
        if any(pattern.search(text) for pattern in (*PRIVATE_PATH_PATTERNS, *SECRET_VALUE_PATTERNS)):
            continue
        weighted_text = " ".join(
            [
                source.get("title", ""),
                source.get("title", ""),
                source.get("category", ""),
                source.get("category", ""),
                Path(source["path"]).stem,
                text,
            ]
        )
        sources.append(
            {
                "path": source["path"],
                "source_sha256": source["sha256"],
                "category": source["category"],
                "priority": source["priority"],
                "title": source.get("title", Path(source["path"]).name),
                "term_hashes": _term_hashes(weighted_text),
                "vector": feature_vector(weighted_text),
            }
        )
    return {
        "schema_version": "1.0",
        "milestone": "N+6.43A",
        "memory_type": "disposable_local_search_aid",
        "engine": ENGINE,
        "vector_dimensions": VECTOR_DIMENSIONS,
        "hash_mode": HASH_MODE,
        "source_state_sha256": raw["source_state_sha256"],
        "source_count": len(sources),
        "sources": sorted(sources, key=lambda item: item["path"]),
        **safety_flags(),
    }


def verify_search_index(index: dict, repo_root: Path = REPO_ROOT) -> dict:
    stale_entries = []
    try:
        raw = _load_raw_index(repo_root.resolve())
    except (FileNotFoundError, ValueError) as exc:
        return {"ok": False, "stale_entries": [{"path": "raw_index.json", "reason": str(exc)}]}
    if index.get("engine") != ENGINE:
        stale_entries.append({"path": "search_index", "reason": "unexpected_engine"})
    if index.get("source_state_sha256") != raw.get("source_state_sha256"):
        stale_entries.append({"path": "raw_index.json", "reason": "source_state_hash_mismatch"})
    for source in index.get("sources", []):
        try:
            path = _repo_relative_path(repo_root.resolve(), source["path"])
            actual = sha256_file(path) if path.is_file() else None
        except ValueError:
            actual = None
        if actual != source.get("source_sha256"):
            stale_entries.append(
                {
                    "path": source.get("path"),
                    "expected": source.get("source_sha256"),
                    "actual": actual,
                }
            )
    return {
        "ok": not stale_entries,
        "verified_sources": len(index.get("sources", [])),
        "stale_entries": stale_entries,
    }


def search(query: str, index: dict, repo_root: Path = REPO_ROOT, limit: int = MAX_RESULTS) -> dict:
    cleaned = validate_query(query)
    verification = verify_search_index(index, repo_root)
    base = {
        "query": cleaned,
        "engine": ENGINE,
        "mode": "saved_disposable_index",
        "index_used": True,
        "verification_required": True,
        "search_aid_only": True,
        **safety_flags(),
    }
    if not verification["ok"]:
        return {
            "ok": False,
            "error": "stale_search_index",
            "stale_entries": verification["stale_entries"],
            "results": [],
            **base,
        }
    query_vector = feature_vector(cleaned)
    query_hashes = set(_term_hashes(cleaned))
    scored = []
    for source in index["sources"]:
        exact_fraction = (
            len(query_hashes.intersection(source["term_hashes"])) / len(query_hashes)
            if query_hashes
            else 0.0
        )
        score = (exact_fraction * 2.0) + _cosine(query_vector, source["vector"])
        if score <= 0:
            continue
        path = _repo_relative_path(repo_root.resolve(), source["path"])
        current_sha256 = sha256_file(path)
        scored.append(
            {
                "source_path": source["path"],
                "source_sha256": source["source_sha256"],
                "current_sha256": current_sha256,
                "hash_verified": current_sha256 == source["source_sha256"],
                "title": source["title"],
                "category": source["category"],
                "priority": source["priority"],
                "score": round(score, 8),
                "exact_term_fraction": round(exact_fraction, 8),
                "canonical_truth": False,
            }
        )
    scored.sort(key=lambda item: (-item["score"], item["priority"], item["source_path"]))
    results = scored[: max(1, min(int(limit), MAX_RESULTS))]
    for rank, result in enumerate(results, start=1):
        result["rank"] = rank
    return {"ok": True, "results": results, **base}


def direct_search(query: str, repo_root: Path = REPO_ROOT, limit: int = MAX_RESULTS) -> dict:
    payload = search(query, build_search_index(repo_root), repo_root, limit)
    payload["mode"] = "direct_scan_fallback"
    payload["index_used"] = False
    return payload


def _path_only_results(query: str, raw_index: dict, limit: int) -> list[str]:
    terms = tokenize(query)
    scored = []
    for source in raw_index["sources"]:
        path_text = _ascii_lower(source["path"])
        score = sum(1 for term in terms if term in path_text)
        if score:
            scored.append((score, source["path"]))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [path for _, path in scored[:limit]]


def evaluate_fixture(fixture: dict, repo_root: Path = REPO_ROOT) -> dict:
    index = build_search_index(repo_root)
    raw = _load_raw_index(repo_root)
    top_k = max(1, min(int(fixture.get("top_k", 3)), MAX_RESULTS))
    rows = []
    content_hits = 0
    baseline_hits = 0
    for case in fixture["queries"]:
        query = validate_query(case["query"])
        expected = set(case["expected_paths"])
        content_paths = [item["source_path"] for item in search(query, index, repo_root, top_k)["results"]]
        baseline_paths = _path_only_results(query, raw, top_k)
        content_hit = bool(expected.intersection(content_paths))
        baseline_hit = bool(expected.intersection(baseline_paths))
        content_hits += int(content_hit)
        baseline_hits += int(baseline_hit)
        rows.append(
            {
                "id": case["id"],
                "query": query,
                "expected_paths": sorted(expected),
                "content_paths": content_paths,
                "path_only_paths": baseline_paths,
                "content_hit": content_hit,
                "path_only_hit": baseline_hit,
            }
        )
    count = len(rows)
    content_rate = round(content_hits / count, 4) if count else 0.0
    baseline_rate = round(baseline_hits / count, 4) if count else 0.0
    improvement = round(content_rate - baseline_rate, 4)
    minimum = float(fixture["minimum_content_top_k_hit_rate"])
    measurable = content_rate >= minimum and improvement > 0
    return {
        "ok": measurable,
        "milestone": "N+6.43A",
        "fixture_id": fixture["fixture_id"],
        "query_count": count,
        "top_k": top_k,
        "content_search": {"hits": content_hits, "top_k_hit_rate": content_rate},
        "path_only_baseline": {"hits": baseline_hits, "top_k_hit_rate": baseline_rate},
        "improvement": improvement,
        "measurable_improvement": measurable,
        "results": rows,
        "semantic_embedding_claim": False,
        **safety_flags(),
    }


def _safe_output_root(output_root: Path, allowed_root: Path) -> Path:
    if ".." in output_root.parts:
        raise ValueError("output path may not contain parent traversal")
    resolved = output_root.resolve(strict=False)
    try:
        resolved.relative_to(allowed_root.resolve(strict=False))
    except ValueError as exc:
        raise ValueError("output path must stay inside the allowed search output root") from exc
    return resolved


def _json_text(payload: dict, compact: bool = False) -> str:
    if compact:
        return json.dumps(payload, separators=(",", ":"), sort_keys=True) + "\n"
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _write_json(path: Path, payload: dict, compact: bool = False) -> None:
    content = _json_text(payload, compact)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        return
    except OSError:
        result = subprocess.run(
            ["node", "-e", _NODE_WRITE_SCRIPT, str(path)],
            input=content,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise OSError(f"safe data-only write fallback failed for {path.name}: {result.stderr.strip()}")


def _json_size(payload: dict, compact: bool = False) -> int:
    return len(_json_text(payload, compact).encode("utf-8"))


def write_trial_outputs(
    repo_root: Path = REPO_ROOT,
    output_root: Path = SEARCH_INDEX_PATH.parent,
    allowed_root: Path | None = None,
) -> list[Path]:
    allowed = allowed_root or SEARCH_INDEX_PATH.parent
    root = _safe_output_root(output_root, allowed)
    fixture = json.loads((repo_root / FIXTURE_PATH.relative_to(REPO_ROOT)).read_text(encoding="utf-8"))
    index = build_search_index(repo_root)
    if _json_size(index, compact=True) > MAX_INDEX_BYTES:
        raise ValueError("search index exceeds configured size budget")
    evaluation = evaluate_fixture(fixture, repo_root)
    paths = [root / "local_search_index.json", root / "evaluation_result.json"]
    _write_json(paths[0], index, compact=True)
    _write_json(paths[1], evaluation)
    return paths


def check(repo_root: Path = REPO_ROOT) -> dict:
    fixture = json.loads((repo_root / FIXTURE_PATH.relative_to(REPO_ROOT)).read_text(encoding="utf-8"))
    index = build_search_index(repo_root)
    evaluation = evaluate_fixture(fixture, repo_root)
    index_bytes = _json_size(index, compact=True)
    within_budget = index_bytes <= MAX_INDEX_BYTES
    return {
        "ok": evaluation["ok"] and within_budget,
        "milestone": "N+6.43A",
        "engine": ENGINE,
        "source_count": index["source_count"],
        "query_count": evaluation["query_count"],
        "content_top_k_hit_rate": evaluation["content_search"]["top_k_hit_rate"],
        "path_only_top_k_hit_rate": evaluation["path_only_baseline"]["top_k_hit_rate"],
        "measurable_improvement": evaluation["measurable_improvement"],
        "index_bytes": index_bytes,
        "max_index_bytes": MAX_INDEX_BYTES,
        "index_within_budget": within_budget,
        "next_milestone": "N+6.43B Local Search Integration And Review Gate",
        **safety_flags(),
    }


def _load_saved_index() -> dict:
    if not SEARCH_INDEX_PATH.is_file():
        raise FileNotFoundError("saved search index missing; run --build or use --no-index")
    return json.loads(SEARCH_INDEX_PATH.read_text(encoding="utf-8"))


def _with_flags(payload: dict) -> dict:
    return {**payload, **safety_flags()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--build", action="store_true")
    action.add_argument("--verify", action="store_true")
    action.add_argument("--evaluate", action="store_true")
    action.add_argument("--search", metavar="QUERY")
    parser.add_argument("--no-index", action="store_true", help="search by direct safe-source scan without saved index")
    parser.add_argument("--limit", type=int, default=MAX_RESULTS)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.check:
            payload = check()
        elif args.build:
            written = write_trial_outputs()
            payload = _with_flags(
                {
                    "ok": True,
                    "written": [path.relative_to(REPO_ROOT).as_posix() for path in written],
                    "engine": ENGINE,
                }
            )
        elif args.verify:
            payload = _with_flags(verify_search_index(_load_saved_index(), REPO_ROOT))
        elif args.evaluate:
            fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
            payload = evaluate_fixture(fixture, REPO_ROOT)
        elif args.no_index:
            payload = direct_search(args.search, REPO_ROOT, args.limit)
        else:
            payload = search(args.search, _load_saved_index(), REPO_ROOT, args.limit)
    except (FileNotFoundError, ValueError, KeyError, json.JSONDecodeError) as exc:
        payload = _with_flags({"ok": False, "error": str(exc)})

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
