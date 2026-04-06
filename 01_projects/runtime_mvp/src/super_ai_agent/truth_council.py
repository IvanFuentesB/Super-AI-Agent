from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TruthCouncilResult:
    question: str
    lead_answer: str
    dissent: str
    consensus_level: str
    confidence_score: float
    evidence_quality_notes: str
    notes: list[str]


def _normalize_level(value: str, default: str = "medium") -> str:
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in {"low", "medium", "high"}:
        return normalized
    return default


def _confidence_score(evidence_quality: str, disagreement_level: str, source_count: int) -> float:
    quality_weights = {"low": 0.25, "medium": 0.55, "high": 0.8}
    disagreement_adjustment = {"low": 0.1, "medium": 0.0, "high": -0.2}
    sources_bonus = min(max(source_count, 0), 5) * 0.03

    score = quality_weights[evidence_quality] + disagreement_adjustment[disagreement_level] + sources_bonus
    return round(min(max(score, 0.05), 0.95), 2)


def _consensus_level(evidence_quality: str, disagreement_level: str, source_count: int) -> str:
    if disagreement_level == "high":
        return "contested"
    if evidence_quality == "high" and source_count >= 3:
        return "strong"
    if evidence_quality in {"medium", "high"}:
        return "moderate"
    return "weak"


def build_truth_council_result(
    question: str,
    proposer_summary: str,
    challenger_summary: str,
    evidence_summary: str,
    evidence_quality: str,
    disagreement_level: str,
    source_count: int,
) -> TruthCouncilResult:
    quality = _normalize_level(evidence_quality)
    disagreement = _normalize_level(disagreement_level)
    bounded_sources = max(source_count, 0)

    notes: list[str] = []
    if bounded_sources < 2:
        notes.append("Source coverage is still thin.")
    if quality == "low":
        notes.append("Treat the current answer as provisional.")
    if disagreement == "high":
        notes.append("High disagreement means the dissent should stay visible.")

    evidence_notes = (
        f"Evidence quality is {quality}; disagreement is {disagreement}; "
        f"source count is {bounded_sources}. {evidence_summary.strip()}"
    )

    return TruthCouncilResult(
        question=question.strip(),
        lead_answer=proposer_summary.strip(),
        dissent=challenger_summary.strip() or "No challenger objections provided.",
        consensus_level=_consensus_level(quality, disagreement, bounded_sources),
        confidence_score=_confidence_score(quality, disagreement, bounded_sources),
        evidence_quality_notes=evidence_notes.strip(),
        notes=notes,
    )
