use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::BTreeSet;
use std::env;
use std::fs;
use std::path::Path;
use std::process::ExitCode;

const GUARD_VERSION: &str = "agent_os_guard/0.2.0";
const MODES: [&str; 3] = ["simulation", "suggestion", "approved_local"];
const APPROVAL_STATES: [&str; 7] = [
    "draft", "pending", "approved", "rejected", "executed", "failed", "denied",
];
const LEGACY_ACTIONS: [&str; 5] = [
    "automation-plan",
    "business-research-plan",
    "coding-task-plan",
    "content-video-plan",
    "email-draft-plan",
];
const APPROVED_ACTIONS: [&str; 4] = [
    "update_latest_state_note",
    "write_evidence_note",
    "write_handoff_file",
    "write_workflow_plan",
];
const LEGACY_CAPABILITIES: [&str; 7] = [
    "handoff_write",
    "local_policy_check",
    "memory_pointer_read",
    "plan_render",
    "repo_read",
    "repo_write_trial",
    "run_record_write",
];
const APPROVED_CAPABILITIES: [&str; 2] =
    ["agent_os.read_memory", "agent_os.write_repo_local"];
const BLOCKED_CAPABILITIES: [&str; 15] = [
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
    "send",
    "shell",
    "subprocess",
    "trading",
];
const INPUT_ROOTS: [&str; 2] = ["14_context/", "docs/"];
const LEGACY_OUTPUT_ROOTS: [&str; 3] = [
    "14_context/agent_os/handoffs/",
    "14_context/agent_os/runs/",
    "14_context/agent_os/trials/",
];
const APPROVED_OUTPUT_ROOTS: [&str; 3] = [
    "14_context/agent_os/",
    "14_context/memory/agent_handoffs/",
    "14_context/operator_reports/generated/",
];

#[derive(Debug, Clone, Default, Deserialize, Serialize)]
struct ActionRequest {
    #[serde(default)]
    schema: Option<String>,
    #[serde(default)]
    schema_version: Option<String>,
    #[serde(default)]
    request_id: Option<String>,
    #[serde(default)]
    created_at: Option<String>,
    #[serde(default)]
    created_by: Option<String>,
    #[serde(default)]
    workflow_id: Option<String>,
    action_id: String,
    mode: String,
    #[serde(default)]
    approval_state: Option<String>,
    #[serde(default)]
    requested_capabilities: Vec<String>,
    #[serde(default)]
    input_paths: Vec<String>,
    #[serde(default)]
    output_paths: Vec<String>,
    #[serde(default)]
    owned_files: Vec<String>,
    #[serde(default)]
    locked_paths: Vec<String>,
    max_runtime_seconds: u64,
    #[serde(default)]
    approval_token: Option<String>,
    #[serde(default)]
    approval_token_hash: Option<String>,
    #[serde(default)]
    summary: Option<String>,
    #[serde(default)]
    risk_note: Option<String>,
    #[serde(default)]
    payload: Value,
}

#[derive(Debug, Deserialize)]
struct OwnershipInput {
    #[serde(default)]
    owned_files: Vec<String>,
    #[serde(default)]
    locked_paths: Vec<String>,
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
    schema: &'static str,
    allow: bool,
    decision: &'static str,
    reason: String,
    reasons: Vec<String>,
    request_id: Option<String>,
    request_fingerprint: String,
    requested_capabilities: Vec<String>,
    allowed_capabilities: Vec<String>,
    denied_capabilities: Vec<String>,
    approval_required: bool,
    approval_present: bool,
    normalized_input_paths: Vec<String>,
    normalized_output_paths: Vec<String>,
    ownership_conflicts: Vec<String>,
    guard_version: &'static str,
    request_hash_fnv1a64: String,
    max_runtime_seconds: u64,
    safety: SafetyFlags,
}

#[derive(Debug, Serialize)]
struct OwnershipDecision {
    schema: &'static str,
    allow: bool,
    decision: &'static str,
    reason: &'static str,
    normalized_owned_files: Vec<String>,
    normalized_locked_paths: Vec<String>,
    ownership_conflicts: Vec<String>,
    guard_version: &'static str,
}

fn normalize_label(value: &str) -> String {
    value.trim().to_lowercase().replace(['-', ' '], "_")
}

fn normalize_capability(value: &str) -> String {
    value.trim().to_lowercase().replace('-', "_")
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

fn is_valid_hash(value: &str) -> bool {
    value.len() == 64 && value.bytes().all(|byte| byte.is_ascii_hexdigit())
}

fn is_new_contract(request: &ActionRequest) -> bool {
    request.schema.as_deref() == Some("ghoti_action_request/1")
}

fn normalized_conflicts(owned: &[String], locked: &[String]) -> Vec<String> {
    let mut conflicts = BTreeSet::new();
    for owned_path in owned {
        for locked_path in locked {
            if conflicts_with_lock(owned_path, locked_path) {
                conflicts.insert(format!("{owned_path} <> {locked_path}"));
            }
        }
    }
    conflicts.into_iter().collect()
}

fn evaluate(request: &ActionRequest) -> GuardDecision {
    let mut reasons = BTreeSet::new();
    let new_contract = is_new_contract(request);
    let mode = normalize_label(&request.mode);
    let action = request.action_id.trim().to_lowercase();

    if new_contract {
        if request
            .request_id
            .as_deref()
            .is_none_or(|value| value.trim().is_empty())
        {
            reasons.insert("request_id_required".to_string());
        }
        let approval_state = request
            .approval_state
            .as_deref()
            .map(normalize_label)
            .unwrap_or_default();
        if !APPROVAL_STATES.contains(&approval_state.as_str()) {
            reasons.insert("unknown_approval_state".to_string());
        }
        if !APPROVED_ACTIONS.contains(&action.as_str()) {
            reasons.insert("unknown_action".to_string());
        }
    } else {
        if request.schema_version.as_deref() != Some("1.0") {
            reasons.insert("unsupported_schema_version".to_string());
        }
        if !LEGACY_ACTIONS.contains(&action.as_str()) {
            reasons.insert("unknown_action".to_string());
        }
    }
    if !MODES.contains(&mode.as_str()) {
        reasons.insert("unknown_mode".to_string());
    }
    if !(1..=120).contains(&request.max_runtime_seconds) {
        reasons.insert("runtime_limit_invalid".to_string());
    }

    let requested: BTreeSet<String> = request
        .requested_capabilities
        .iter()
        .map(|capability| normalize_capability(capability))
        .collect();
    let allowed_set: &[&str] = if new_contract {
        &APPROVED_CAPABILITIES
    } else {
        &LEGACY_CAPABILITIES
    };
    let allowed: Vec<String> = requested
        .iter()
        .filter(|capability| allowed_set.contains(&capability.as_str()))
        .cloned()
        .collect();
    let denied: Vec<String> = requested
        .iter()
        .filter(|capability| !allowed_set.contains(&capability.as_str()))
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

    let output_roots: &[&str] = if new_contract {
        &APPROVED_OUTPUT_ROOTS
    } else {
        &LEGACY_OUTPUT_ROOTS
    };
    let mut normalized_outputs = Vec::new();
    for path in &request.output_paths {
        match normalize_path(path) {
            Some(normalized) if under_root(&normalized, output_roots) => {
                normalized_outputs.push(normalized);
            }
            _ => {
                reasons.insert("invalid_output_path".to_string());
            }
        }
    }

    let mut normalized_owned = Vec::new();
    for path in &request.owned_files {
        match normalize_path(path) {
            Some(normalized) if under_root(&normalized, output_roots) => {
                normalized_owned.push(normalized);
            }
            _ => {
                reasons.insert("invalid_owned_file".to_string());
            }
        }
    }
    if new_contract
        && normalized_outputs
            .iter()
            .any(|path| !normalized_owned.contains(path))
    {
        reasons.insert("output_not_owned".to_string());
    }

    let normalized_locks: Vec<String> = request
        .locked_paths
        .iter()
        .filter_map(|path| normalize_path(path))
        .collect();
    let ownership_conflicts = normalized_conflicts(&normalized_owned, &normalized_locks);
    let legacy_conflicts = normalized_conflicts(&normalized_outputs, &normalized_locks);
    if !ownership_conflicts.is_empty() || !legacy_conflicts.is_empty() {
        reasons.insert("locked_path_conflict".to_string());
    }
    let mut all_conflicts = ownership_conflicts;
    all_conflicts.extend(legacy_conflicts);
    all_conflicts.sort();
    all_conflicts.dedup();

    let approval_required = mode == "approved_local";
    let approval_present = if new_contract {
        request
            .approval_token_hash
            .as_deref()
            .is_some_and(is_valid_hash)
    } else {
        request
            .approval_token
            .as_deref()
            .is_some_and(|token| !token.trim().is_empty())
    };
    if approval_required && !approval_present {
        if new_contract && request.approval_token_hash.is_some() {
            reasons.insert("approval_token_hash_invalid".to_string());
        } else {
            reasons.insert("approval_required".to_string());
        }
    }

    let fingerprint = stable_hash(request);
    let reasons: Vec<String> = reasons.into_iter().collect();
    let allow = reasons.is_empty();
    GuardDecision {
        schema: "ghoti_guard_decision/1",
        allow,
        decision: if allow { "allowed" } else { "denied" },
        reason: reasons
            .first()
            .cloned()
            .unwrap_or_else(|| "policy_checks_passed".to_string()),
        reasons,
        request_id: request.request_id.clone(),
        request_fingerprint: fingerprint.clone(),
        requested_capabilities: requested.into_iter().collect(),
        allowed_capabilities: allowed,
        denied_capabilities: denied,
        approval_required,
        approval_present,
        normalized_input_paths: normalized_inputs,
        normalized_output_paths: normalized_outputs,
        ownership_conflicts: all_conflicts,
        guard_version: GUARD_VERSION,
        request_hash_fnv1a64: fingerprint,
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

fn ownership_check(input: &OwnershipInput) -> OwnershipDecision {
    let owned: Vec<String> = input
        .owned_files
        .iter()
        .filter_map(|path| normalize_path(path))
        .collect();
    let locked: Vec<String> = input
        .locked_paths
        .iter()
        .filter_map(|path| normalize_path(path))
        .collect();
    let conflicts = normalized_conflicts(&owned, &locked);
    let allow = conflicts.is_empty()
        && owned.len() == input.owned_files.len()
        && locked.len() == input.locked_paths.len();
    OwnershipDecision {
        schema: "ghoti_ownership_decision/1",
        allow,
        decision: if allow { "allowed" } else { "denied" },
        reason: if allow {
            "no_ownership_conflicts"
        } else {
            "ownership_conflict_or_invalid_path"
        },
        normalized_owned_files: owned,
        normalized_locked_paths: locked,
        ownership_conflicts: conflicts,
        guard_version: GUARD_VERSION,
    }
}

fn check_request() -> ActionRequest {
    ActionRequest {
        schema_version: Some("1.0".to_string()),
        action_id: "coding-task-plan".to_string(),
        mode: "simulation".to_string(),
        requested_capabilities: vec!["repo_read".to_string(), "plan_render".to_string()],
        input_paths: vec!["docs/GHOTI_AGENT_OS_GUARD_AND_LOCAL_WORKER_TRIAL.md".to_string()],
        output_paths: vec!["14_context/agent_os/trials/check.md".to_string()],
        max_runtime_seconds: 10,
        ..ActionRequest::default()
    }
}

fn print_json<T: Serialize>(value: &T) -> Result<(), String> {
    let output = serde_json::to_string_pretty(value).map_err(|error| error.to_string())?;
    println!("{output}");
    Ok(())
}

fn argument_value(args: &[String], flag: &str) -> Result<String, String> {
    let index = args
        .iter()
        .position(|arg| arg == flag)
        .ok_or_else(|| format!("{flag} is required"))?;
    args.get(index + 1)
        .cloned()
        .ok_or_else(|| format!("{flag} requires a value"))
}

fn read_request(args: &[String]) -> Result<ActionRequest, String> {
    let request_path = argument_value(args, "--request")?;
    let text = fs::read_to_string(Path::new(&request_path))
        .map_err(|error| format!("could not read request: {error}"))?;
    serde_json::from_str(&text).map_err(|error| format!("invalid request JSON: {error}"))
}

fn validate_repo_root(args: &[String]) -> Result<(), String> {
    if !args.iter().any(|arg| arg == "--repo-root") {
        return Ok(());
    }
    let repo_root = argument_value(args, "--repo-root")?;
    if !Path::new(&repo_root).is_dir() {
        return Err("--repo-root must be an existing directory".to_string());
    }
    Ok(())
}

fn run() -> Result<(), String> {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.iter().any(|arg| arg == "--check") {
        return print_json(&evaluate(&check_request()));
    }
    match args.first().map(String::as_str) {
        Some("validate") | Some("fingerprint") => {
            validate_repo_root(&args)?;
            print_json(&evaluate(&read_request(&args)?))
        }
        Some("ownership-check") => {
            validate_repo_root(&args)?;
            let input_path = argument_value(&args, "--input")?;
            let text = fs::read_to_string(Path::new(&input_path))
                .map_err(|error| format!("could not read ownership input: {error}"))?;
            let input: OwnershipInput = serde_json::from_str(&text)
                .map_err(|error| format!("invalid ownership input JSON: {error}"))?;
            print_json(&ownership_check(&input))
        }
        _ if args.iter().any(|arg| arg == "--request") => {
            print_json(&evaluate(&read_request(&args)?))
        }
        _ => Err(
            "usage: agent_os_guard validate|fingerprint --request <request.json> \
             --repo-root <path> --json"
                .to_string(),
        ),
    }
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

    fn legacy_request() -> ActionRequest {
        ActionRequest {
            schema_version: Some("1.0".to_string()),
            action_id: "content-video-plan".to_string(),
            mode: "suggestion".to_string(),
            requested_capabilities: vec!["repo_read".to_string(), "plan_render".to_string()],
            input_paths: vec!["docs/example.md".to_string()],
            output_paths: vec!["14_context/agent_os/trials/example.md".to_string()],
            max_runtime_seconds: 30,
            ..ActionRequest::default()
        }
    }

    fn approved_request() -> ActionRequest {
        ActionRequest {
            schema: Some("ghoti_action_request/1".to_string()),
            request_id: Some("req-rust-test".to_string()),
            action_id: "write_workflow_plan".to_string(),
            mode: "suggestion".to_string(),
            approval_state: Some("pending".to_string()),
            requested_capabilities: vec![
                "agent_os.read_memory".to_string(),
                "agent_os.write_repo_local".to_string(),
            ],
            output_paths: vec!["14_context/agent_os/workflows/test.md".to_string()],
            owned_files: vec!["14_context/agent_os/workflows/test.md".to_string()],
            max_runtime_seconds: 30,
            ..ActionRequest::default()
        }
    }

    #[test]
    fn legacy_suggestion_remains_allowed() {
        assert!(evaluate(&legacy_request()).allow);
    }

    #[test]
    fn approved_contract_suggestion_is_allowed() {
        assert!(evaluate(&approved_request()).allow);
    }

    #[test]
    fn approved_local_requires_valid_hash() {
        let mut request = approved_request();
        request.mode = "approved_local".to_string();
        request.approval_state = Some("approved".to_string());
        assert!(!evaluate(&request).allow);
        request.approval_token_hash = Some("a".repeat(64));
        assert!(evaluate(&request).allow);
    }

    #[test]
    fn dangerous_and_unknown_capabilities_are_denied() {
        let mut request = approved_request();
        request.requested_capabilities = vec!["browser".to_string(), "future_magic".to_string()];
        assert_eq!(
            evaluate(&request).denied_capabilities,
            vec!["browser".to_string(), "future_magic".to_string()]
        );
    }

    #[test]
    fn output_must_stay_in_approved_roots() {
        let mut request = approved_request();
        request.output_paths = vec!["docs/outside.md".to_string()];
        request.owned_files = request.output_paths.clone();
        assert!(!evaluate(&request).allow);
    }

    #[test]
    fn locked_path_conflict_is_denied() {
        let mut request = approved_request();
        request.locked_paths = vec!["14_context/agent_os/workflows".to_string()];
        assert!(!evaluate(&request).allow);
    }

    #[test]
    fn decision_is_deterministic() {
        let request = approved_request();
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
