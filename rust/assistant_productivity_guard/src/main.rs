//! Fail-closed validator for Ghoti assistant productivity configuration.
//!
//! The guard reads JSON only. It never writes files, starts tools, accesses
//! accounts, or performs network calls.

use serde_json::Value;
use std::{
    collections::{BTreeMap, BTreeSet},
    env, fs,
    path::{Path, PathBuf},
};

const DEFAULT_FILES: &[&str] = &[
    "23_configs/assistant_productivity/codex_productivity.example.json",
    "23_configs/assistant_productivity/hermes_productivity.example.json",
    "23_configs/assistant_productivity/claude_code_productivity.example.json",
    "23_configs/assistant_productivity/chatgpt_cowork_productivity.example.json",
    "23_configs/assistant_productivity/routines.example.json",
    "23_configs/assistant_productivity/ruflo_productivity.example.json",
    "23_configs/skills/claude_code_skills.example.json",
    "23_configs/mcp/codex_mcp_strategy.example.json",
    "23_configs/mcp/hermes_mcp_strategy.example.json",
    "23_configs/mcp/chatgpt_cowork_connectors.example.json",
];
const SECRET_MARKERS: &[&str] = &[
    "api_key=", "apikey=", "password=", "secret=", "sk-ant-", "ghp_", "akia",
    "authorization: bearer", "-----begin",
];
const PRIVATE_PATHS: &[&str] = &["c:\\users\\", "c:/users/", "/mnt/c/users/"];
const COMMAND_KEYS: &[&str] = &["command", "shell", "exec", "script"];

#[derive(Clone)]
struct Finding {
    code: String,
    location: String,
    detail: String,
}

fn finding(code: &str, location: &str, detail: impl Into<String>) -> Finding {
    Finding {
        code: code.to_string(),
        location: location.to_string(),
        detail: detail.into(),
    }
}

fn canonical(value: &Value) -> String {
    match value {
        Value::Object(map) => {
            let sorted: BTreeMap<&String, &Value> = map.iter().collect();
            let body = sorted
                .iter()
                .map(|(key, value)| format!("{:?}:{}", key, canonical(value)))
                .collect::<Vec<_>>()
                .join(",");
            format!("{{{body}}}")
        }
        Value::Array(items) => {
            format!(
                "[{}]",
                items.iter().map(canonical).collect::<Vec<_>>().join(",")
            )
        }
        other => other.to_string(),
    }
}

fn fnv1a64(bytes: &[u8]) -> String {
    let mut hash: u64 = 0xcbf2_9ce4_8422_2325;
    for byte in bytes {
        hash ^= *byte as u64;
        hash = hash.wrapping_mul(0x0000_0100_0000_01b3);
    }
    format!("{hash:016x}")
}

fn scan(value: &Value, location: &str, findings: &mut Vec<Finding>, ids: &mut BTreeSet<String>) {
    match value {
        Value::String(text) => {
            let lower = text.to_ascii_lowercase();
            for marker in SECRET_MARKERS {
                if lower.contains(marker) {
                    findings.push(finding("secret_like_value", location, format!("matched {marker}")));
                }
            }
            for marker in PRIVATE_PATHS {
                if lower.contains(marker) {
                    findings.push(finding("private_absolute_path", location, format!("matched {marker}")));
                }
            }
        }
        Value::Array(items) => {
            for (index, item) in items.iter().enumerate() {
                scan(item, &format!("{location}[{index}]"), findings, ids);
            }
        }
        Value::Object(map) => {
            if let Some(id) = map.get("id").and_then(Value::as_str) {
                if !ids.insert(id.to_string()) {
                    findings.push(finding("duplicate_id", location, format!("duplicate id {id}")));
                }
            }
            for (key, item) in map {
                let item_location = format!("{location}.{key}");
                let key_lower = key.to_ascii_lowercase();
                if COMMAND_KEYS.iter().any(|marker| key_lower.contains(marker))
                    && item.as_str().is_some_and(|text| !text.trim().is_empty())
                {
                    findings.push(finding(
                        "arbitrary_command_entry",
                        &item_location,
                        "command-like string entries are not allowed in productivity config",
                    ));
                }
                scan(item, &item_location, findings, ids);
            }
            if map.get("enabled").and_then(Value::as_bool) == Some(true)
                && map.get("credentialed").and_then(Value::as_bool) == Some(true)
            {
                findings.push(finding(
                    "credentialed_connector_enabled",
                    location,
                    "credentialed connectors must remain disabled",
                ));
            }
            if map.get("live_actions").and_then(Value::as_bool) == Some(true) {
                findings.push(finding(
                    "live_action_enabled",
                    location,
                    "productivity routines must not perform live actions",
                ));
            }
        }
        _ => {}
    }
}

fn validate_special(value: &Value, path: &Path, findings: &mut Vec<Finding>) {
    let name = path.file_name().and_then(|item| item.to_str()).unwrap_or("");
    if name == "routines.example.json" {
        for (index, routine) in value
            .get("routines")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
            .enumerate()
        {
            let location = format!("{name}.routines[{index}]");
            if routine.get("enabled").and_then(Value::as_bool) != Some(false) {
                findings.push(finding("routine_not_disabled", &location, "routine enabled must be false"));
            }
            if routine.get("live_actions").and_then(Value::as_bool) != Some(false) {
                findings.push(finding("routine_live_action", &location, "live_actions must be false"));
            }
            if routine.get("mode").and_then(Value::as_str) != Some("prompt_only") {
                findings.push(finding("routine_mode", &location, "mode must be prompt_only"));
            }
        }
    }
    if name == "claude_code_productivity.example.json" {
        let statusline = value.get("statusline").unwrap_or(&Value::Null);
        for field in ["installed", "exact_credits_supported", "claims_exact_credits", "usage_api_enabled"] {
            if statusline.get(field).and_then(Value::as_bool) != Some(false) {
                findings.push(finding(
                    "dishonest_or_live_statusline",
                    &format!("{name}.statusline.{field}"),
                    format!("{field} must be false in committed example config"),
                ));
            }
        }
    }
}

fn load(path: &Path) -> Result<Value, String> {
    let body = fs::read_to_string(path).map_err(|error| format!("cannot read {}: {error}", path.display()))?;
    serde_json::from_str(&body).map_err(|error| format!("malformed JSON in {}: {error}", path.display()))
}

fn run(args: &[String]) -> i32 {
    if !args.iter().any(|arg| arg == "--check") {
        println!("{}", serde_json::json!({
            "ok": false,
            "checker": "assistant_productivity_guard",
            "error": "use --check --json"
        }));
        return 2;
    }
    let root = args
        .iter()
        .position(|arg| arg == "--repo-root")
        .and_then(|index| args.get(index + 1))
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."));
    let mut findings = Vec::new();
    let mut fingerprints = BTreeMap::new();
    for relative in DEFAULT_FILES {
        let path = root.join(relative);
        let value = match load(&path) {
            Ok(value) => value,
            Err(error) => {
                findings.push(finding("missing_or_malformed_config", relative, error));
                continue;
            }
        };
        let mut ids = BTreeSet::new();
        scan(&value, relative, &mut findings, &mut ids);
        validate_special(&value, &path, &mut findings);
        fingerprints.insert(relative.to_string(), fnv1a64(canonical(&value).as_bytes()));
    }
    let report = serde_json::json!({
        "ok": findings.is_empty(),
        "checker": "assistant_productivity_guard",
        "fail_closed": true,
        "validated_file_count": DEFAULT_FILES.len(),
        "blocker_count": findings.len(),
        "findings": findings.iter().map(|item| serde_json::json!({
            "code": item.code,
            "location": item.location,
            "detail": item.detail,
        })).collect::<Vec<_>>(),
        "fingerprints": fingerprints,
        "safety": {
            "network_used": false,
            "writes_files": false,
            "live_actions_allowed": false,
            "credentialed_connectors_enabled": false
        }
    });
    println!("{}", serde_json::to_string_pretty(&report).unwrap_or_else(|_| "{}".to_string()));
    if findings.is_empty() { 0 } else { 1 }
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    std::process::exit(run(&args));
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn fingerprint_is_deterministic() {
        assert_eq!(
            fnv1a64(canonical(&json!({"b": 2, "a": 1})).as_bytes()),
            fnv1a64(canonical(&json!({"a": 1, "b": 2})).as_bytes())
        );
    }

    #[test]
    fn detects_secret_private_path_and_command() {
        let mut findings = Vec::new();
        let mut ids = BTreeSet::new();
        scan(
            &json!({"id": "x", "shell_command": "run me", "note": "C:/Users/example", "other": "ghp_example_value"}),
            "fixture",
            &mut findings,
            &mut ids,
        );
        let codes: BTreeSet<&str> = findings.iter().map(|item| item.code.as_str()).collect();
        assert!(codes.contains("arbitrary_command_entry"));
        assert!(codes.contains("private_absolute_path"));
        assert!(codes.contains("secret_like_value"));
    }

    #[test]
    fn detects_live_routine() {
        let mut findings = Vec::new();
        validate_special(
            &json!({"routines": [{"enabled": true, "live_actions": true, "mode": "execute"}]}),
            Path::new("routines.example.json"),
            &mut findings,
        );
        assert_eq!(findings.len(), 3);
    }
}
