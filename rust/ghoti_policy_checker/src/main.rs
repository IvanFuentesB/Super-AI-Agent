use serde::{Deserialize, Serialize};
use std::{env, fs, path::Path};

const ALLOWED_CAPABILITIES: &[&str] = &[
    "fixture_read",
    "local_policy_check",
    "plan_render",
    "repo_read",
    "status_read",
];

const BLOCKED_CAPABILITIES: &[&str] = &[
    "account",
    "browser",
    "computer_use",
    "mass_message",
    "mcp",
    "money",
    "secrets",
];

#[derive(Debug, Default, Deserialize)]
struct SwarmPlan {
    #[serde(default)]
    plan_id: String,
    #[serde(default)]
    dry_run: bool,
    #[serde(default)]
    live_launch: bool,
    #[serde(default)]
    requires_human_approval: bool,
    #[serde(default)]
    capabilities: Vec<String>,
}

#[derive(Debug, Serialize)]
struct Safety {
    default_deny: bool,
    launches_agents: bool,
    network_used: bool,
    writes_files: bool,
}

#[derive(Debug, Serialize)]
struct PolicyDecision {
    ok: bool,
    checker: &'static str,
    policy_version: &'static str,
    plan_id: String,
    allowed: bool,
    decision: &'static str,
    dry_run: bool,
    live_launch: bool,
    requires_human_approval: bool,
    reasons: Vec<String>,
    blocked_capabilities: Vec<String>,
    unknown_capabilities: Vec<String>,
    safety: Safety,
}

#[derive(Debug, Serialize)]
struct CliError {
    ok: bool,
    error: String,
    safety: Safety,
}

fn normalize_capability(value: &str) -> String {
    value.trim().to_ascii_lowercase().replace([' ', '-'], "_")
}

fn evaluate(plan: SwarmPlan) -> PolicyDecision {
    let mut reasons = Vec::new();
    let mut blocked_capabilities = Vec::new();
    let mut unknown_capabilities = Vec::new();

    if !plan.dry_run {
        reasons.push("dry_run_required".to_string());
    }
    if plan.live_launch {
        reasons.push("live_launch_requested".to_string());
    }
    if !plan.requires_human_approval {
        reasons.push("human_approval_not_required_by_plan".to_string());
    }

    for capability in &plan.capabilities {
        let normalized = normalize_capability(capability);
        if BLOCKED_CAPABILITIES.contains(&normalized.as_str()) {
            blocked_capabilities.push(normalized);
        } else if !ALLOWED_CAPABILITIES.contains(&normalized.as_str()) {
            unknown_capabilities.push(normalized);
        }
    }

    blocked_capabilities.sort();
    blocked_capabilities.dedup();
    unknown_capabilities.sort();
    unknown_capabilities.dedup();

    if !blocked_capabilities.is_empty() {
        reasons.push("blocked_capability_requested".to_string());
    }
    if !unknown_capabilities.is_empty() {
        reasons.push("unknown_capability_requested".to_string());
    }

    let allowed = reasons.is_empty();
    PolicyDecision {
        ok: true,
        checker: "ghoti_policy_checker",
        policy_version: "n6.28a-prototype-v1",
        plan_id: plan.plan_id,
        allowed,
        decision: if allowed { "allow" } else { "deny" },
        dry_run: plan.dry_run,
        live_launch: plan.live_launch,
        requires_human_approval: plan.requires_human_approval,
        reasons,
        blocked_capabilities,
        unknown_capabilities,
        safety: Safety {
            default_deny: true,
            launches_agents: false,
            network_used: false,
            writes_files: false,
        },
    }
}

fn print_json<T: Serialize>(value: &T) -> Result<(), String> {
    let rendered = serde_json::to_string_pretty(value).map_err(|error| error.to_string())?;
    println!("{rendered}");
    Ok(())
}

fn print_error(message: impl Into<String>) -> i32 {
    let error = CliError {
        ok: false,
        error: message.into(),
        safety: Safety {
            default_deny: true,
            launches_agents: false,
            network_used: false,
            writes_files: false,
        },
    };
    let _ = print_json(&error);
    2
}

fn load_plan(path: &Path) -> Result<SwarmPlan, String> {
    let body = fs::read_to_string(path)
        .map_err(|error| format!("cannot read input {}: {error}", path.display()))?;
    serde_json::from_str(&body).map_err(|error| format!("invalid plan JSON: {error}"))
}

fn run(args: &[String]) -> i32 {
    match args {
        [flag] if flag == "--check" => {
            let plan = SwarmPlan {
                plan_id: "built-in-default-deny-check".to_string(),
                ..SwarmPlan::default()
            };
            print_json(&evaluate(plan)).map_or_else(print_error, |_| 0)
        }
        [flag, path] if flag == "--input" => match load_plan(Path::new(path)) {
            Ok(plan) => print_json(&evaluate(plan)).map_or_else(print_error, |_| 0),
            Err(error) => print_error(error),
        },
        _ => print_error("usage: ghoti_policy_checker --check | --input <plan.json>"),
    }
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    std::process::exit(run(&args));
}

#[cfg(test)]
mod tests {
    use super::*;

    fn safe_plan() -> SwarmPlan {
        SwarmPlan {
            plan_id: "safe".to_string(),
            dry_run: true,
            live_launch: false,
            requires_human_approval: true,
            capabilities: vec!["repo_read".to_string(), "plan_render".to_string()],
        }
    }

    #[test]
    fn default_plan_is_denied() {
        let decision = evaluate(SwarmPlan::default());
        assert!(!decision.allowed);
        assert_eq!(decision.decision, "deny");
    }

    #[test]
    fn safe_dry_run_plan_is_allowed() {
        let decision = evaluate(safe_plan());
        assert!(decision.allowed);
        assert_eq!(decision.decision, "allow");
    }

    #[test]
    fn blocked_and_unknown_capabilities_are_denied() {
        let mut plan = safe_plan();
        plan.capabilities = vec!["money".to_string(), "future_magic".to_string()];
        let decision = evaluate(plan);
        assert!(!decision.allowed);
        assert_eq!(decision.blocked_capabilities, vec!["money"]);
        assert_eq!(decision.unknown_capabilities, vec!["future_magic"]);
    }

    #[test]
    fn live_launch_is_denied() {
        let mut plan = safe_plan();
        plan.live_launch = true;
        let decision = evaluate(plan);
        assert!(!decision.allowed);
        assert!(
            decision
                .reasons
                .contains(&"live_launch_requested".to_string())
        );
    }
}
