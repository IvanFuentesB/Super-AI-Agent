use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AgentRole {
    Builder,
    Auditor,
    Planner,
    Explorer,
    Observer,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EventKind {
    PlanSubmitted,
    PolicyChecked,
    WaveStarted,
    WaveCompleted,
    AgentSpawned,
    AgentDone,
    KillSwitchArmed,
    KillSwitchTriggered,
    ApprovalRequested,
    ApprovalGranted,
    ApprovalDenied,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RuntimeEvent {
    pub kind: EventKind,
    pub plan_id: String,
    pub agent_role: Option<AgentRole>,
    pub wave: Option<u32>,
    pub message: String,
    /// Always true in the current codebase: no live execution is wired.
    pub dry_run: bool,
    /// Always false in the current codebase: no live execution is wired.
    pub live: bool,
}

impl RuntimeEvent {
    pub fn dry(kind: EventKind, plan_id: impl Into<String>, message: impl Into<String>) -> Self {
        RuntimeEvent {
            kind,
            plan_id: plan_id.into(),
            agent_role: None,
            wave: None,
            message: message.into(),
            dry_run: true,
            live: false,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn event_kinds_serialize_snake_case() {
        assert_eq!(
            serde_json::to_string(&EventKind::PlanSubmitted).unwrap(),
            "\"plan_submitted\""
        );
        assert_eq!(
            serde_json::to_string(&EventKind::KillSwitchTriggered).unwrap(),
            "\"kill_switch_triggered\""
        );
        assert_eq!(
            serde_json::to_string(&EventKind::ApprovalRequested).unwrap(),
            "\"approval_requested\""
        );
    }

    #[test]
    fn dry_event_live_is_false() {
        let ev = RuntimeEvent::dry(EventKind::WaveStarted, "p1", "wave 1 starting");
        assert!(ev.dry_run);
        assert!(!ev.live);
    }

    #[test]
    fn all_agent_roles_roundtrip_json() {
        for role in [
            AgentRole::Builder,
            AgentRole::Auditor,
            AgentRole::Planner,
            AgentRole::Explorer,
            AgentRole::Observer,
        ] {
            let json = serde_json::to_string(&role).unwrap();
            let back: AgentRole = serde_json::from_str(&json).unwrap();
            assert_eq!(back, role);
        }
    }

    #[test]
    fn runtime_event_wave_is_optional() {
        let ev = RuntimeEvent::dry(EventKind::PolicyChecked, "p2", "policy ok");
        assert!(ev.wave.is_none());

        let ev_with_wave = RuntimeEvent {
            wave: Some(3),
            ..RuntimeEvent::dry(EventKind::WaveCompleted, "p3", "wave done")
        };
        assert_eq!(ev_with_wave.wave, Some(3));
    }
}
