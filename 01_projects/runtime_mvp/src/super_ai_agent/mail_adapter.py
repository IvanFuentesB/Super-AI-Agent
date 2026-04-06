from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MailPlan:
    account_label: str
    objective: str
    mode: str
    steps: list[str]
    outputs: list[str]
    approval_points: list[str]


def get_mail_adapter_mode() -> str:
    return "planning_only"


def build_inbox_triage_plan(account_label: str, goal: str) -> MailPlan:
    return MailPlan(
        account_label=account_label,
        objective=goal,
        mode=get_mail_adapter_mode(),
        steps=[
            "gather inbox context",
            "group messages by urgency and category",
            "prepare draft response needs and follow-up notes",
            "hold all outbound actions behind approval",
        ],
        outputs=[
            "triage summary",
            "priority message list",
            "draft response plan",
        ],
        approval_points=[
            "sending replies",
            "changing live mailbox state",
        ],
    )


def build_reply_draft_plan(account_label: str, objective: str) -> MailPlan:
    return MailPlan(
        account_label=account_label,
        objective=objective,
        mode=get_mail_adapter_mode(),
        steps=[
            "capture recipient and thread context",
            "draft a reply outline",
            "check tone and legitimacy",
            "hold send behind approval",
        ],
        outputs=[
            "reply draft pack",
            "tone notes",
            "review checklist",
        ],
        approval_points=[
            "sending the message",
        ],
    )
