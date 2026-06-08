pub mod events;
pub mod policy;

#[cfg(test)]
mod tests {
    use crate::events::{AgentRole, EventKind, RuntimeEvent};
    use crate::policy::{KillSwitchState, KillSwitchStatus, PolicyDecision, PolicyVerdict};

    #[test]
    fn policy_decision_allow_roundtrips_json() {
        let decision = PolicyDecision {
            verdict: PolicyVerdict::Allow,
            reasons: vec![],
            blocked_capabilities: vec![],
            unknown_capabilities: vec![],
            dry_run: true,
            live_launch: false,
        };
        let json = serde_json::to_string(&decision).unwrap();
        let back: PolicyDecision = serde_json::from_str(&json).unwrap();
        assert_eq!(back.verdict, PolicyVerdict::Allow);
        assert!(back.dry_run);
        assert!(!back.live_launch);
    }

    #[test]
    fn policy_decision_deny_roundtrips_json() {
        let decision = PolicyDecision {
            verdict: PolicyVerdict::Deny,
            reasons: vec!["live_launch_requested".into()],
            blocked_capabilities: vec![],
            unknown_capabilities: vec![],
            dry_run: false,
            live_launch: true,
        };
        let json = serde_json::to_string(&decision).unwrap();
        let back: PolicyDecision = serde_json::from_str(&json).unwrap();
        assert_eq!(back.verdict, PolicyVerdict::Deny);
        assert!(!back.reasons.is_empty());
    }

    #[test]
    fn kill_switch_default_is_inactive() {
        let ks = KillSwitchStatus::default();
        assert_eq!(ks.state, KillSwitchState::Inactive);
        assert!(ks.reason.is_none());
    }

    #[test]
    fn kill_switch_triggered_roundtrips_json() {
        let ks = KillSwitchStatus {
            state: KillSwitchState::Triggered,
            reason: Some("unsafe capability requested".into()),
        };
        let json = serde_json::to_string(&ks).unwrap();
        let back: KillSwitchStatus = serde_json::from_str(&json).unwrap();
        assert_eq!(back.state, KillSwitchState::Triggered);
        assert!(back.reason.is_some());
    }

    #[test]
    fn dry_event_has_no_live_flag() {
        let ev =
            RuntimeEvent::dry(EventKind::PlanSubmitted, "plan-001", "plan submitted for check");
        assert!(ev.dry_run);
        assert!(!ev.live);
        assert_eq!(ev.plan_id, "plan-001");
    }

    #[test]
    fn runtime_event_with_role_roundtrips_json() {
        let ev = RuntimeEvent {
            kind: EventKind::ApprovalRequested,
            plan_id: "plan-002".into(),
            agent_role: Some(AgentRole::Auditor),
            wave: Some(1),
            message: "awaiting human gate".into(),
            dry_run: true,
            live: false,
        };
        let json = serde_json::to_string(&ev).unwrap();
        let back: RuntimeEvent = serde_json::from_str(&json).unwrap();
        assert_eq!(back.agent_role, Some(AgentRole::Auditor));
        assert_eq!(back.wave, Some(1));
    }

    #[test]
    fn agent_roles_serialize_snake_case() {
        assert_eq!(
            serde_json::to_string(&AgentRole::Builder).unwrap(),
            "\"builder\""
        );
        assert_eq!(
            serde_json::to_string(&AgentRole::Explorer).unwrap(),
            "\"explorer\""
        );
    }
}
