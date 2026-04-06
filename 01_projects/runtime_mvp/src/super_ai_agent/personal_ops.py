from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .storage import _ensure_directory, _write_text, get_project_root

CATALOG_PATH = get_project_root().parents[1] / "23_configs" / "personal_workflow_catalog.example.json"
PERSONAL_OPS_DIR = get_project_root().parents[1] / "11_exports" / "personal_ops"


@dataclass
class PersonalWorkflow:
    workflow_id: str
    title: str
    purpose: str
    inputs: list[str]
    outputs: list[str]
    approval_points: list[str]
    notes: str

    @classmethod
    def from_dict(cls, data: dict) -> "PersonalWorkflow":
        return cls(**data)


def _load_catalog_payload() -> dict:
    with CATALOG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return slug.strip("-") or "pack"


def _write_pack(filename: str, lines: list[str]) -> Path:
    _ensure_directory(PERSONAL_OPS_DIR)
    output_path = PERSONAL_OPS_DIR / filename
    _write_text(output_path, "\n".join(lines) + "\n")
    return output_path


def list_personal_workflows() -> list[PersonalWorkflow]:
    payload = _load_catalog_payload()
    return [PersonalWorkflow.from_dict(item) for item in payload.get("workflows", [])]


def get_personal_workflow(workflow_id: str) -> PersonalWorkflow:
    for workflow in list_personal_workflows():
        if workflow.workflow_id == workflow_id:
            return workflow
    raise ValueError(f"Personal workflow not found: {workflow_id}")


def scaffold_inbox_triage_pack(account_label: str, goal: str) -> Path:
    filename = f"{_slugify(account_label)}-inbox-triage-pack.md"
    return _write_pack(
        filename,
        [
            "# Inbox Triage Runbook",
            "",
            f"## Account Label",
            account_label,
            "",
            "## Inbox Goal",
            goal,
            "",
            "## Current Context",
            "- to be filled in",
            "",
            "## Categories",
            "- urgent",
            "- waiting",
            "- archive",
            "",
            "## Priority Messages",
            "- to be filled in",
            "",
            "## Draft Responses Needed",
            "- to be filled in",
            "",
            "## Follow-Ups",
            "- to be filled in",
            "",
            "## Risks",
            "- sending still requires approval",
            "",
            "## Next Step",
            "- review the pack before any outbound action",
        ],
    )


def scaffold_linkedin_pack(profile_label: str, target_role: str, focus: str) -> Path:
    filename = f"{_slugify(profile_label)}-linkedin-update-pack.md"
    return _write_pack(
        filename,
        [
            "# LinkedIn Update Pack",
            "",
            "## Profile Goal",
            f"Refresh {profile_label} toward {target_role}",
            "",
            "## Target Audience",
            target_role,
            "",
            "## Headline Draft",
            f"{target_role} | {focus}",
            "",
            "## About Draft",
            f"Draft direction focused on {focus}.",
            "",
            "## Featured Ideas",
            "- to be filled in",
            "",
            "## Content Angle Ideas",
            f"- {focus}",
            "",
            "## Approval Points",
            "- editing profile text",
            "- publishing posts",
            "",
            "## Next Step",
            "- review before making any live profile changes",
        ],
    )


def scaffold_cv_pack(target_role: str, summary: str) -> Path:
    filename = f"{_slugify(target_role)}-cv-update-pack.md"
    return _write_pack(
        filename,
        [
            "# CV Update Pack",
            "",
            "## Target Role",
            target_role,
            "",
            "## Current Strengths",
            "- to be filled in",
            "",
            "## Gaps",
            "- to be filled in",
            "",
            "## Summary Draft",
            summary,
            "",
            "## Experience Bullets To Revise",
            "- to be filled in",
            "",
            "## Project Highlights",
            "- to be filled in",
            "",
            "## Approval Points",
            "- exporting final resume",
            "- sharing externally",
            "",
            "## Next Step",
            "- review and revise before final export",
        ],
    )


def scaffold_outreach_draft(recipient_label: str, purpose: str, notes: str = "") -> Path:
    filename = f"{_slugify(recipient_label)}-outreach-draft.md"
    context_notes = notes if notes else "No extra notes provided."
    return _write_pack(
        filename,
        [
            "# Outreach Draft",
            "",
            "## Recipient Label",
            recipient_label,
            "",
            "## Objective",
            purpose,
            "",
            "## Context",
            context_notes,
            "",
            "## Draft Message",
            "Draft pending review.",
            "",
            "## Tone Notes",
            "- keep it direct and legitimate",
            "",
            "## Approval Status",
            "Pending",
            "",
            "## Next Step",
            "- review before any send action",
        ],
    )


def scaffold_internship_application_pack(
    target_role: str,
    company: str,
    job_source: str,
    fit_summary: str,
) -> Path:
    filename = f"{_slugify(company)}-{_slugify(target_role)}-internship-application-pack.md"
    return _write_pack(
        filename,
        [
            "# Internship Application Pack",
            "",
            "## Target Role",
            target_role,
            "",
            "## Company",
            company,
            "",
            "## Job Link / Source",
            job_source,
            "",
            "## Why It Fits",
            fit_summary,
            "",
            "## CV Changes Needed",
            "- tailor summary and project emphasis",
            "",
            "## LinkedIn / Profile Changes Needed",
            "- align headline, featured work, and profile framing",
            "",
            "## Portfolio / Case-Study Assets Needed",
            "- identify the most relevant proof or case study",
            "",
            "## Approval Points",
            "- review assets before sharing externally",
            "- submit application only after human review",
            "- send follow-up messages only after approval",
            "",
            "## Next Step",
            "- review the pack before any external action",
        ],
    )


def scaffold_showcase_case_study(project_name: str, objective: str, highlights: str) -> Path:
    filename = f"{_slugify(project_name)}-showcase-case-study.md"
    return _write_pack(
        filename,
        [
            "# Project Showcase Case Study",
            "",
            "## Project Objective",
            objective,
            "",
            "## Starting Point",
            "Execution-first AI operating framework foundation with runtime, GitHub workflow, and personal-ops scaffolding.",
            "",
            "## Architecture Summary",
            "Compact file-backed runtime with approval-aware workflow layers, durable handoff context, and reference-only repo intake.",
            "",
            "## Major Capabilities",
            f"- {highlights}",
            "- approval-aware runtime and GitHub workflow utilities",
            "- internship and personal-ops scaffold generation",
            "",
            "## What Is Live vs Scaffold-Only",
            "- live: runtime CLI, checker, GitHub read-only and approval-gated command surface",
            "- scaffold-only: many downstream integrations and showcase publishing outputs",
            "",
            "## Risks / Limits",
            "- browser and app execution are not implemented yet",
            "- third-party repos remain reference-only",
            "",
            "## Internship Relevance",
            "Shows practical AI workflow design, explicit approval control, and inspectable runtime behavior.",
            "",
            "## Next Step",
            "- prepare one short live demo and tighten recruiter-facing outputs",
        ],
    )


def scaffold_portfolio_project_page(project_name: str, summary: str, stack: str) -> Path:
    filename = f"{_slugify(project_name)}-portfolio-project-page.md"
    return _write_pack(
        filename,
        [
            "# Portfolio Project Page",
            "",
            "## Project Summary",
            summary,
            "",
            "## Problem",
            "AI workflow systems often look impressive in docs but are hard to inspect or control in practice.",
            "",
            "## Solution",
            f"{project_name} uses a small execution-first runtime with approval-aware workflow layers and reviewable outputs.",
            "",
            "## Stack",
            stack,
            "",
            "## Notable Capabilities",
            "- approval-aware task and GitHub workflow scaffolding",
            "- durable handoff and context files",
            "- personal-ops and showcase artifact generation",
            "",
            "## Screenshots / Demo Ideas",
            "- runtime checker pass",
            "- GitHub capability output",
            "- internship or showcase pack generation",
            "",
            "## Lessons",
            "- start with controllable outputs before deeper automation",
            "",
            "## Next Milestone",
            "- choose one browser-control path and one tighter live demo",
        ],
    )
