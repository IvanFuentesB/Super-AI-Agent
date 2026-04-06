from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .storage import get_project_root

REPO_ROOT = get_project_root().parents[1]
IGNORED_DIR_NAMES = {".git", "__pycache__", ".venv", "venv", "node_modules"}
TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".py", ".ps1", ".cfg", ".ini"}
SECRET_PATTERNS = {
    "github_token": re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    "openai_style_key": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private_key_header": re.compile(r"BEGIN (?:RSA )?PRIVATE KEY"),
}


@dataclass
class PublishabilityFinding:
    category: str
    path: str
    detail: str


@dataclass
class PublishabilityReport:
    scanned_files: int
    findings: list[PublishabilityFinding]

    @property
    def finding_count(self) -> int:
        return len(self.findings)

    def category_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for finding in self.findings:
            counts[finding.category] = counts.get(finding.category, 0) + 1
        return counts


def _relative_path(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _is_runtime_artifact(relative_path: str) -> bool:
    if not relative_path.startswith("01_projects/runtime_mvp/runtime_data/"):
        return False
    return not relative_path.endswith(".gitkeep")


def _is_report_export(relative_path: str) -> bool:
    return relative_path.startswith("11_exports/reports/") and relative_path.endswith(".md")


def _iter_repo_files() -> list[Path]:
    files: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIR_NAMES for part in path.parts):
            continue
        files.append(path)
    return files


def _scan_secret_like_content(path: Path, findings: list[PublishabilityFinding]) -> None:
    if ".example." in path.name:
        return
    if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {".env", ".env.example"}:
        return
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return
    sample = text[:200000]
    for label, pattern in SECRET_PATTERNS.items():
        if pattern.search(sample):
            findings.append(
                PublishabilityFinding(
                    category="secret_like_content",
                    path=_relative_path(path),
                    detail=f"Matched {label} pattern.",
                )
            )
            break


def scan_publishability() -> PublishabilityReport:
    findings: list[PublishabilityFinding] = []
    files = _iter_repo_files()

    for path in files:
        relative_path = _relative_path(path)
        lower_name = path.name.lower()

        if lower_name == ".env" or lower_name.startswith(".env."):
            findings.append(
                PublishabilityFinding(
                    category="env_file",
                    path=relative_path,
                    detail="Environment file should stay private.",
                )
            )

        if path.suffix.lower() in {".pem", ".key"}:
            findings.append(
                PublishabilityFinding(
                    category="key_file",
                    path=relative_path,
                    detail="Key material should not be public.",
                )
            )

        if _is_runtime_artifact(relative_path):
            findings.append(
                PublishabilityFinding(
                    category="runtime_artifact",
                    path=relative_path,
                    detail="Runtime data should be reviewed before publication.",
                )
            )

        if _is_report_export(relative_path):
            findings.append(
                PublishabilityFinding(
                    category="report_export",
                    path=relative_path,
                    detail="Generated export should be reviewed before publication.",
                )
            )

        _scan_secret_like_content(path, findings)

    return PublishabilityReport(scanned_files=len(files), findings=findings)
