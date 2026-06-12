use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;
use std::env;
use std::fs;
use std::path::Path;
use std::process::ExitCode;

const GUARD_VERSION: &str = "agent_os_guard/0.1.0";
const MODES: [&str; 3] = ["simulation", "suggestion", "approved_local"];
const ACTIONS: [&str; 5] = [
    "automation-plan",
    "business-research-plan",
    "coding-task-plan",
    "content-video-plan",
    "email-draft-plan",
];
const ALLOWED_CAPABILITIES: [&str; 7] = [
    "handoff_write",
    "local_policy_check",
    "memory_pointer_read",
    "plan_render",
    "repo_read",
    "repo_write_trial",
    "run_record_write",
];
const BLOCKED_CAPABILITIES: [&str; 11] = [
    "account",
    "browser",
    "computer_use",
    "external_write",
    "mass_message",
    "mcp",
    "money",
    "payment",
    "posting",
    "purchase",
    "secrets",
];
const INPUT_ROOTS: [&str; 2] = ["14_context/", "docs/"];
const OUTPUT_ROOTS: [&str; 3] = [
    "14_context/agent_os/handoffs/",
    "14_context/agent_os/runs/",
    "14_context/agent_os/trials/",
];

#[derive(Debug, Clone, Deserialize, Serialize)]
struct ActionRequest {
    schema_version: String,
    action_id: String,
    mode: String,
    #[serde(default)]
    requested_capabilities: Vec<String>,
    #[serde(default)]
    input_paths: Vec<String>,
    #[serde(default)]
    output_paths: Vec<String>,
    #[serde(default)]
    locked_paths: Vec<String>,
    max_runtime_seconds: u64,
    approval_token: Option<String>,
}

#[derive(Debug, Serialize)]
struct SafetyFlags {
    default_deny: bool,
    launches_processes: bool,
    network_used: bool,
    writes_files: bool,
    live_execution: bool,
}

#[derive(Debug, Serialize)]
struct GuardDecision {
    allow: bool,
    decision: &'static str,
    reason: String,
    reasons: Vec<String>,
    requested_capabilities: Vec<String>,
    allowed_capabilities: Vec<String>,
    denied_capabilities: Vec<String>,
    approval_required: bool,
    approval_present: bool,
    normalized_input_paths: Vec<String>,
    normalized_output_paths: Vec<String>,
    guard_version: &'static str,
    request_hash_fnv1a64: String,
    max_runtime_seconds: u64,
    safety: SafetyFlags,
}

fn normalize_label(value: &str) -> String {
    value.trim().to_lowercase().replace(['-', ' '], "_")
}

fn normalize_path(value: &str) -> Option<String> {
    let normalized = value.trim().replace('\\', "/");
    if normalized.is_empty()
        || normalized.starts_with('/')
        || normalized.contains(':')
        || normalized
            .split('/')
            .any(|part| part == ".." || part == ".")
    {
        return None;
    }
    Some(
        normalized
            .split('/')
            .filter(|part| !part.is_empty())
            .collect::<Vec<_>>()
            .join("/"),
    )
}

fn under_root(path: &str, roots: &[&str]) -> bool {
    roots.iter().any(|root| path.starts_with(root))
}

fn conflicts_with_lock(output: &str, locked: &str) -> bool {
    output == locked
        || output.starts_with(&format!("{locked}/"))
        || locked.starts_with(&format!("{output}/"))
}

fn stable_hash(request: &ActionRequest) -> String {
    let bytes = serde_json::to_vec(request).expect("serializing ActionRequest cannot fail");
    let mut hash: u64 = 0xcbf29ce484222325;
    for byte in bytes {
        hash ^= u64::from(byte);
        hash = hash.wrapping_mul(0x100000001b3);
    }
    format!("{hash:016x}")
}

fn evaluate(request: &ActionRequest) -> GuardDecision {
    let mut reasons = BTreeSet::new();
    let mode = normalize_label(&request.mode);
    let action = request.action_id.trim().to_lowercase();

    if request.schema_version != "1.0" {
        reasons.insert("unsupported_schema_version".to_string());
    }
    if !MODES.contains(&mode.as_str()) {
        reasons.insert("unknown_mode".to_string());
    }
    if !ACTIONS.contains(&action.as_str()) {
        reasons.insert("unknown_action".to_string());
    }
    if !(1..=120).contains(&request.max_runtime_seconds) {
        reasons.insert("runtime_limit_invalid".to_string());
    }

    let requested: BTreeSet<String> = request
        .requested_capabilities
        .iter()
        .map(|capability| normalize_label(capability))
        .collect();
    let allowed: Vec<String> = requested
        .iter()
        .filter(|capability| ALLOWED_CAPABILITIES.contains(&capability.as_str()))
        .cloned()
        .collect();
    let denied: Vec<String> = requested
        .iter()
        .filter(|capability| !ALLOWED_CAPABILITIES.contains(&capability.as_str()))
        .cloned()
        .collect();
    if denied
        .iter()
        .any(|capability| BLOCKED_CAPABILITIES.contains(&capability.as_str()))
    {
        reasons.insert("blocked_capability".to_string());
    }
    if denied
        .iter()
        .any(|capability| !BLOCKED_CAPABILITIES.contains(&capability.as_str()))
    {
        reasons.insert("unknown_capability".to_string());
    }

    let mut normalized_inputs = Vec::new();
    for path in &request.input_paths {
        match normalize_path(path) {
            Some(normalized) if under_root(&normalized, &INPUT_ROOTS) => {
                normalized_inputs.push(normalized);
            }
            _ => {
                reasons.insert("invalid_input_path".to_string());
            }
        }
    }

    let mut normalized_outputs = Vec::new();
    for path in &request.output_paths {
        match normalize_path(path) {
            Some(normalized) if under_root(&normalized, &OUTPUT_ROOTS) => {
                normalized_outputs.push(normalized);
            }
            _ => {
                reasons.insert("invalid_output_path".to_string());
            }
        }
    }

    let normalized_locks: Vec<String> = request
        .locked_paths
        .iter()
        .filter_map(|path| normalize_path(path))
        .collect();
    if normalized_outputs.iter().any(|output| {
        normalized_locks
            .iter()
            .any(|locked| conflicts_with_lock(output, locked))
    }) {
        reasons.insert("locked_path_conflict".to_string());
    }

    let approval_required = mode == "approved_local";
    let approval_present = request
        .approval_token
        .as_deref()
        .is_some_and(|token| !token.trim().is_empty());
    if approval_required && !approval_present {
        reasons.insert("approval_required".to_string());
    }

    let reasons: Vec<String> = reasons.into_iter().collect();
    let allow = reasons.is_empty();
    GuardDecision {
        allow,
        decision: if allow { "allowed" } else { "denied" },
        reason: reasons
            .first()
            .cloned()
            .unwrap_or_else(|| "policy_checks_passed".to_string()),
        reasons,
        requested_capabilities: requested.into_iter().collect(),
        allowed_capabilities: allowed,
        denied_capabilities: denied,
        approval_required,
        approval_present,
        normalized_input_paths: normalized_inputs,
        normalized_output_paths: normalized_outputs,
        guard_version: GUARD_VERSION,
        request_hash_fnv1a64: stable_hash(request),
        max_runtime_seconds: request.max_runtime_seconds,
        safety: SafetyFlags {
            default_deny: true,
            launches_processes: false,
            network_used: false,
            writes_files: false,
            live_execution: false,
        },
    }
}

fn check_request() -> ActionRequest {
    ActionRequest {
        schema_version: "1.0".to_string(),
        action_id: "coding-task-plan".to_string(),
        mode: "simulation".to_string(),
        requested_capabilities: vec!["repo_read".to_string(), "plan_render".to_string()],
        input_paths: vec!["docs/GHOTI_AGENT_OS_GUARD_AND_LOCAL_WORKER_TRIAL.md".to_string()],
        output_paths: vec!["14_context/agent_os/trials/check.md".to_string()],
        locked_paths: Vec::new(),
        max_runtime_seconds: 10,
        approval_token: None,
    }
}

fn print_json(decision: &GuardDecision) -> Result<(), String> {
    let output = serde_json::to_string_pretty(decision).map_err(|error| error.to_string())?;
    println!("{output}");
    Ok(())
}

fn run() -> Result<(), String> {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.iter().any(|arg| arg == "--check") {
        return print_json(&evaluate(&check_request()));
    }
    let request_index = args
        .iter()
        .position(|arg| arg == "--request")
        .ok_or_else(|| "usage: agent_os_guard --request <request.json> --json".to_string())?;
    let request_path = args
        .get(request_index + 1)
        .ok_or_else(|| "--request requires a JSON file path".to_string())?;
    let text = fs::read_to_string(Path::new(request_path))
        .map_err(|error| format!("could not read request: {error}"))?;
    let request: ActionRequest =
        serde_json::from_str(&text).map_err(|error| format!("invalid request JSON: {error}"))?;
    print_json(&evaluate(&request))
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("{error}");
            ExitCode::from(2)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn safe_request() -> ActionRequest {
        ActionRequest {
            schema_version: "1.0".to_string(),
            action_id: "content-video-plan".to_string(),
            mode: "suggestion".to_string(),
            requested_capabilities: vec!["repo_read".to_string(), "plan_render".to_string()],
            input_paths: vec!["docs/example.md".to_string()],
            output_paths: vec!["14_context/agent_os/trials/example.md".to_string()],
            locked_paths: Vec::new(),
            max_runtime_seconds: 30,
            approval_token: None,
        }
    }

    #[test]
    fn safe_suggestion_is_allowed() {
        assert!(evaluate(&safe_request()).allow);
    }

    #[test]
    fn dangerous_and_unknown_capabilities_are_denied() {
        let mut request = safe_request();
        request.requested_capabilities = vec!["browser".to_string(), "future_magic".to_string()];
        assert_eq!(
            evaluate(&request).denied_capabilities,
            vec!["browser".to_string(), "future_magic".to_string()]
        );
    }

    #[test]
    fn approved_local_requires_approval() {
        let mut request = safe_request();
        request.mode = "approved_local".to_string();
        assert!(!evaluate(&request).allow);
        request.approval_token = Some("present".to_string());
        assert!(evaluate(&request).allow);
    }

    #[test]
    fn output_must_stay_in_agent_os_roots() {
        let mut request = safe_request();
        request.output_paths = vec!["docs/outside.md".to_string()];
        assert!(!evaluate(&request).allow);
    }

    #[test]
    fn locked_path_conflict_is_denied() {
        let mut request = safe_request();
        request.locked_paths = vec!["14_context/agent_os/trials".to_string()];
        assert!(!evaluate(&request).allow);
    }

    #[test]
    fn decision_is_deterministic() {
        let request = safe_request();
        assert_eq!(
            serde_json::to_string(&evaluate(&request)).unwrap(),
            serde_json::to_string(&evaluate(&request)).unwrap()
        );
    }

    #[test]
    fn built_in_check_request_is_allowed() {
        assert!(evaluate(&check_request()).allow);
    }
}
