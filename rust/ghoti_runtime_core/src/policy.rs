use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum PolicyVerdict {
    Allow,
    Deny,
}

/// Result of evaluating a swarm plan against the Ghoti policy rules.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyDecision {
    pub verdict: PolicyVerdict,
    pub reasons: Vec<String>,
    pub blocked_capabilities: Vec<String>,
    pub unknown_capabilities: Vec<String>,
    pub dry_run: bool,
    pub live_launch: bool,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum KillSwitchState {
    Inactive,
    Armed,
    Triggered,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KillSwitchStatus {
    pub state: KillSwitchState,
    pub reason: Option<String>,
}

impl Default for KillSwitchStatus {
    fn default() -> Self {
        KillSwitchStatus {
            state: KillSwitchState::Inactive,
            reason: None,
        }
    }
}

/// Capabilities the Ghoti runtime recognises. All variants that name a blocked
/// surface must never appear in an allowed PolicyDecision.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RuntimeCapability {
    // Safe, explicitly allowed
    RepoRead,
    StatusRead,
    PlanRender,
    LocalPolicyCheck,
    FixtureRead,
    // Blocked: none of these may appear in an allowed plan
    Browser,
    ComputerUse,
    Mcp,
    Account,
    Money,
    MassMessage,
    Secrets,
    LiveLaunch,
    Docker,
    AutoSubmit,
    ExternalNav,
}

impl RuntimeCapability {
    pub fn is_blocked(&self) -> bool {
        matches!(
            self,
            RuntimeCapability::Browser
                | RuntimeCapability::ComputerUse
                | RuntimeCapability::Mcp
                | RuntimeCapability::Account
                | RuntimeCapability::Money
                | RuntimeCapability::MassMessage
                | RuntimeCapability::Secrets
                | RuntimeCapability::LiveLaunch
                | RuntimeCapability::Docker
                | RuntimeCapability::AutoSubmit
                | RuntimeCapability::ExternalNav
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn safe_capabilities_are_not_blocked() {
        for cap in [
            RuntimeCapability::RepoRead,
            RuntimeCapability::StatusRead,
            RuntimeCapability::PlanRender,
            RuntimeCapability::LocalPolicyCheck,
            RuntimeCapability::FixtureRead,
        ] {
            assert!(!cap.is_blocked(), "{cap:?} should not be blocked");
        }
    }

    #[test]
    fn dangerous_capabilities_are_blocked() {
        for cap in [
            RuntimeCapability::Browser,
            RuntimeCapability::ComputerUse,
            RuntimeCapability::Mcp,
            RuntimeCapability::Account,
            RuntimeCapability::Money,
            RuntimeCapability::MassMessage,
            RuntimeCapability::Secrets,
            RuntimeCapability::LiveLaunch,
            RuntimeCapability::Docker,
            RuntimeCapability::AutoSubmit,
            RuntimeCapability::ExternalNav,
        ] {
            assert!(cap.is_blocked(), "{cap:?} should be blocked");
        }
    }

    #[test]
    fn verdict_serializes_correctly() {
        assert_eq!(
            serde_json::to_string(&PolicyVerdict::Allow).unwrap(),
            "\"allow\""
        );
        assert_eq!(
            serde_json::to_string(&PolicyVerdict::Deny).unwrap(),
            "\"deny\""
        );
    }

    #[test]
    fn kill_switch_states_serialize_snake_case() {
        assert_eq!(
            serde_json::to_string(&KillSwitchState::Triggered).unwrap(),
            "\"triggered\""
        );
        assert_eq!(
            serde_json::to_string(&KillSwitchState::Armed).unwrap(),
            "\"armed\""
        );
        assert_eq!(
            serde_json::to_string(&KillSwitchState::Inactive).unwrap(),
            "\"inactive\""
        );
    }
}
