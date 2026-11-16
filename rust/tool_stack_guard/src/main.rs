//! tool_stack_guard - deterministic validator/hardener for the Ghoti tool stack.
//!
//! Validates the tool registry, MCP connector templates, and skills registry
//! from Rust so the acceleration layer has a real first-class Rust safety lane.
//! Fails closed on malformed JSON, enforces allowed enums, detects duplicate
//! ids, missing P0 owner/next_action, secret-looking values, private absolute
//! Windows paths, and reject items without a reason. Emits deterministic
//! FNV-1a fingerprints for change detection. No network, no writes.

use serde_json::Value;
use std::{collections::BTreeMap, collections::BTreeSet, env, fs, path::Path, path::PathBuf};

const PRIORITIES: &[&str] = &["P0", "P1", "P2", "defer", "reject"];
const CATEGORIES: &[&str] = &[
    "repo", "mcp", "skill", "business", "local_model", "automation", "design",
    "security", "memory", "analytics", "content", "cad", "infrastructure",
];
const OWNERS: &[&str] = &["claude_code", "codex", "hermes", "chatgpt", "local_model", "human"];
const IMPL: &[&str] = &[
    "inspect_first", "install_adapt", "mcp_connector", "prompt_only",
    "obsidian_memory", "business_research", "future_paid_api", "reject",
];
const RISK: &[&str] = &["low", "medium", "high", "blocked"];
const STATUS: &[&str] = &[
    "candidate", "needs_source", "intake_ready", "inspected", "adopt", "defer", "reject",
];
const REQUIRED: &[&str] = &[
    "id", "name", "category", "priority", "owner", "implementation_type",
    "risk_level", "value", "source_needed", "status", "next_action", "notes",
];
const SECRET_MARKERS: &[&str] = &[
    "api_key=", "apikey=", "password=", "secret=", "sk-ant-", "ghp_", "akia",
    "authorization: bearer", "-----begin",
];
const PRIVATE_PATHS: &[&str] = &["c:\\users\\", "c:/users/"];

// ---- deterministic fingerprint (FNV-1a 64) over canonicalized JSON ----

fn fnv1a64(bytes: &[u8]) -> String {
    let mut hash: u64 = 0xcbf2_9ce4_8422_2325;
    for b in bytes {
        hash ^= *b as u64;
        hash = hash.wrapping_mul(0x0000_0100_0000_01b3);
    }
    format!("{hash:016x}")
}

/// Order-independent canonical string: object keys sorted recursively.
fn canonical(v: &Value) -> String {
    match v {
        Value::Object(map) => {
            let sorted: BTreeMap<&String, &Value> = map.iter().collect();
            let mut s = String::from("{");
            for (i, (k, val)) in sorted.iter().enumerate() {
                if i > 0 {
                    s.push(',');
                }
                s.push_str(&format!("{:?}:{}", k, canonical(val)));
            }
            s.push('}');
            s
        }
        Value::Array(arr) => {
            let mut s = String::from("[");
            for (i, item) in arr.iter().enumerate() {
                if i > 0 {
                    s.push(',');
                }
                s.push_str(&canonical(item));
            }
            s.push(']');
            s
        }
        other => other.to_string(),
    }
}

fn fingerprint(v: &Value) -> String {
    fnv1a64(canonical(v).as_bytes())
}

#[derive(Clone)]
struct Finding {
    severity: String,
    code: String,
    location: String,
    detail: String,
}

fn finding(sev: &str, code: &str, loc: &str, detail: String) -> Finding {
    Finding {
        severity: sev.to_string(),
        code: code.to_string(),
        location: loc.to_string(),
        detail,
    }
}

fn scan_secrets_and_paths(value: &Value, where_: &str, out: &mut Vec<Finding>) {
    match value {
        Value::String(s) => {
            let low = s.to_ascii_lowercase();
            for m in SECRET_MARKERS {
                if low.contains(m) {
                    out.push(finding("blocker", "secret_like_value", where_,
                        format!("matched marker {m}")));
                }
            }
            for p in PRIVATE_PATHS {
                if low.contains(p) {
                    out.push(finding("blocker", "private_absolute_path", where_,
                        format!("matched {p}")));
                }
            }
        }
        Value::Array(a) => a.iter().for_each(|x| scan_secrets_and_paths(x, where_, out)),
        Value::Object(o) => o.iter().for_each(|(_, x)| scan_secrets_and_paths(x, where_, out)),
        _ => {}
    }
}

fn validate_registry(v: &Value, out: &mut Vec<Finding>) {
    let tools = match v.get("tools").and_then(|t| t.as_array()) {
        Some(t) => t,
        None => {
            out.push(finding("blocker", "registry_shape", "tool_registry",
                "missing tools array".to_string()));
            return;
        }
    };
    let mut ids: BTreeSet<String> = BTreeSet::new();
    for (i, t) in tools.iter().enumerate() {
        let loc = format!("tool_registry.tools[{i}]");
        for field in REQUIRED {
            if t.get(*field).is_none() {
                out.push(finding("blocker", "missing_field", &loc,
                    format!("missing {field}")));
            }
        }
        let id = t.get("id").and_then(|x| x.as_str()).unwrap_or("");
        if !id.is_empty() && !ids.insert(id.to_string()) {
            out.push(finding("blocker", "duplicate_id", &loc, format!("duplicate id {id}")));
        }
        check_enum(t, "priority", PRIORITIES, &loc, out);
        check_enum(t, "category", CATEGORIES, &loc, out);
        check_enum(t, "owner", OWNERS, &loc, out);
        check_enum(t, "implementation_type", IMPL, &loc, out);
        check_enum(t, "risk_level", RISK, &loc, out);
        check_enum(t, "status", STATUS, &loc, out);

        let priority = t.get("priority").and_then(|x| x.as_str()).unwrap_or("");
        if priority == "P0" {
            let owner = t.get("owner").and_then(|x| x.as_str()).unwrap_or("");
            let next = t.get("next_action").and_then(|x| x.as_str()).unwrap_or("");
            if owner.is_empty() {
                out.push(finding("blocker", "p0_missing_owner", &loc,
                    format!("P0 {id} has no owner")));
            }
            if next.trim().is_empty() {
                out.push(finding("blocker", "p0_missing_next_action", &loc,
                    format!("P0 {id} has no next_action")));
            }
        }
        if priority == "reject" {
            let notes = t.get("notes").and_then(|x| x.as_str()).unwrap_or("").to_ascii_lowercase();
            if !notes.contains("reason") {
                out.push(finding("blocker", "reject_without_reason", &loc,
                    format!("reject {id} has no reason in notes")));
            }
        }
        scan_secrets_and_paths(t, &loc, out);
    }
}

fn check_enum(obj: &Value, field: &str, allowed: &[&str], loc: &str, out: &mut Vec<Finding>) {
    if let Some(val) = obj.get(field).and_then(|x| x.as_str()) {
        if !allowed.contains(&val) {
            out.push(finding("blocker", "invalid_enum", loc,
                format!("{field}={val} not in allowed set")));
        }
    }
}

fn validate_mcp(v: &Value, out: &mut Vec<Finding>) {
    // Summary index: must assert all_disabled true and list connectors.
    if let Some(false) = v.get("all_disabled").and_then(|x| x.as_bool()) {
        out.push(finding("blocker", "mcp_not_all_disabled", "mcp_connectors",
            "all_disabled must be true".to_string()));
    }
    scan_secrets_and_paths(v, "mcp_connectors", out);
}

fn validate_mcp_template(v: &Value, name: &str, out: &mut Vec<Finding>) {
    if v.get("enabled").and_then(|x| x.as_bool()) != Some(false) {
        out.push(finding("blocker", "mcp_template_enabled", name,
            "template must be enabled:false".to_string()));
    }
    scan_secrets_and_paths(v, name, out);
}

fn validate_skills(v: &Value, out: &mut Vec<Finding>) {
    let agents = match v.get("agents").and_then(|a| a.as_object()) {
        Some(a) => a,
        None => {
            out.push(finding("blocker", "skills_shape", "skills_registry",
                "missing agents object".to_string()));
            return;
        }
    };
    for (agent, items) in agents {
        if let Some(arr) = items.as_array() {
            for (i, item) in arr.iter().enumerate() {
                let loc = format!("skills_registry.{agent}[{i}]");
                if item.get("manual_required").and_then(|x| x.as_bool()).is_none() {
                    out.push(finding("blocker", "skill_missing_field", &loc,
                        "missing manual_required".to_string()));
                }
                if item.get("enabled").and_then(|x| x.as_bool()) != Some(false) {
                    out.push(finding("warning", "skill_enabled", &loc,
                        "skill should be enabled:false until installed".to_string()));
                }
            }
        }
    }
    scan_secrets_and_paths(v, "skills_registry", out);
}

fn load(path: &Path) -> Result<Value, String> {
    let body = fs::read_to_string(path)
        .map_err(|e| format!("cannot read {}: {e}", path.display()))?;
    serde_json::from_str(&body).map_err(|e| format!("malformed JSON in {}: {e}", path.display()))
}

fn arg_value(args: &[String], flag: &str) -> Option<String> {
    args.iter().position(|a| a == flag).and_then(|i| args.get(i + 1)).cloned()
}

fn print_error(msg: String) -> i32 {
    let v = serde_json::json!({
        "ok": false, "checker": "tool_stack_guard", "fail_closed": true, "error": msg,
    });
    println!("{}", serde_json::to_string_pretty(&v).unwrap_or_else(|_| "{}".into()));
    2
}

fn run(args: &[String]) -> i32 {
    let json_out = args.iter().any(|a| a == "--json");
    let mut findings: Vec<Finding> = Vec::new();
    let mut fingerprints: BTreeMap<String, String> = BTreeMap::new();

    // --check is a built-in self-test on the default repo-relative paths.
    let default_check = args.iter().any(|a| a == "--check");
    let registry = arg_value(args, "--registry").or_else(|| {
        default_check.then(|| "14_context/tool_intake/tool_registry.json".to_string())
    });
    let mcp = arg_value(args, "--mcp").or_else(|| {
        default_check.then(|| "14_context/tool_stack/mcp_connectors.json".to_string())
    });
    let mcp_dir = arg_value(args, "--mcp-dir").or_else(|| {
        default_check.then(|| "14_context/mcp_connectors/config_templates".to_string())
    });
    let skills = arg_value(args, "--skills").or_else(|| {
        default_check.then(|| "14_context/tool_stack/skills_registry.json".to_string())
    });

    if registry.is_none() && mcp.is_none() && skills.is_none() && mcp_dir.is_none() {
        return print_error("provide --registry/--mcp/--mcp-dir/--skills or --check".to_string());
    }

    if let Some(p) = &registry {
        match load(Path::new(p)) {
            Ok(v) => {
                validate_registry(&v, &mut findings);
                fingerprints.insert("registry".to_string(), fingerprint(&v));
            }
            Err(e) => return print_error(e), // fail closed on malformed JSON
        }
    }
    if let Some(p) = &mcp {
        if Path::new(p).is_file() {
            match load(Path::new(p)) {
                Ok(v) => {
                    validate_mcp(&v, &mut findings);
                    fingerprints.insert("mcp".to_string(), fingerprint(&v));
                }
                Err(e) => return print_error(e),
            }
        }
    }
    if let Some(dir) = &mcp_dir {
        if Path::new(dir).is_dir() {
            let mut combined = String::new();
            let mut paths: Vec<PathBuf> = fs::read_dir(dir)
                .map(|rd| rd.filter_map(|e| e.ok().map(|e| e.path())).collect())
                .unwrap_or_default();
            paths.sort();
            for path in paths {
                if path.extension().and_then(|e| e.to_str()) == Some("json") {
                    match load(&path) {
                        Ok(v) => {
                            let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("template");
                            validate_mcp_template(&v, name, &mut findings);
                            combined.push_str(&canonical(&v));
                        }
                        Err(e) => return print_error(e),
                    }
                }
            }
            if !combined.is_empty() {
                fingerprints.insert("mcp_templates".to_string(), fnv1a64(combined.as_bytes()));
            }
        }
    }
    if let Some(p) = &skills {
        if Path::new(p).is_file() {
            match load(Path::new(p)) {
                Ok(v) => {
                    validate_skills(&v, &mut findings);
                    fingerprints.insert("skills".to_string(), fingerprint(&v));
                }
                Err(e) => return print_error(e),
            }
        }
    }

    let blockers: Vec<&Finding> = findings.iter().filter(|f| f.severity == "blocker").collect();
    let ok = blockers.is_empty();
    let report = serde_json::json!({
        "ok": ok,
        "checker": "tool_stack_guard",
        "fail_closed": true,
        "blocker_count": blockers.len(),
        "finding_count": findings.len(),
        "findings": findings.iter().map(|f| serde_json::json!({
            "severity": f.severity, "code": f.code, "location": f.location, "detail": f.detail,
        })).collect::<Vec<_>>(),
        "fingerprints": fingerprints,
        "safety": {"network_used": false, "writes_files": false, "default_deny": true},
    });
    if json_out || true {
        println!("{}", serde_json::to_string_pretty(&report).unwrap_or_else(|_| "{}".into()));
    }
    if ok { 0 } else { 1 }
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    std::process::exit(run(&args));
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn good_tool(id: &str, priority: &str) -> Value {
        json!({
            "id": id, "name": "T", "category": "repo", "priority": priority,
            "owner": "claude_code", "implementation_type": "inspect_first",
            "risk_level": "low", "value": "v", "source_needed": true,
            "status": "intake_ready", "next_action": "do x", "notes": "reason: ok"
        })
    }

    #[test]
    fn valid_registry_has_no_blockers() {
        let v = json!({"tools": [good_tool("a", "P0"), good_tool("b", "P1")]});
        let mut out = Vec::new();
        validate_registry(&v, &mut out);
        assert!(out.iter().all(|f| f.severity != "blocker"), "unexpected blocker");
    }

    #[test]
    fn duplicate_ids_detected() {
        let v = json!({"tools": [good_tool("dup", "P1"), good_tool("dup", "P1")]});
        let mut out = Vec::new();
        validate_registry(&v, &mut out);
        assert!(out.iter().any(|f| f.code == "duplicate_id"));
    }

    #[test]
    fn invalid_enum_detected() {
        let mut t = good_tool("x", "P1");
        t["priority"] = json!("URGENT");
        let v = json!({"tools": [t]});
        let mut out = Vec::new();
        validate_registry(&v, &mut out);
        assert!(out.iter().any(|f| f.code == "invalid_enum"));
    }

    #[test]
    fn p0_missing_next_action_detected() {
        let mut t = good_tool("x", "P0");
        t["next_action"] = json!("");
        let v = json!({"tools": [t]});
        let mut out = Vec::new();
        validate_registry(&v, &mut out);
        assert!(out.iter().any(|f| f.code == "p0_missing_next_action"));
    }

    #[test]
    fn reject_without_reason_detected() {
        let mut t = good_tool("x", "reject");
        t["implementation_type"] = json!("reject");
        t["risk_level"] = json!("blocked");
        t["notes"] = json!("no explanation");
        let v = json!({"tools": [t]});
        let mut out = Vec::new();
        validate_registry(&v, &mut out);
        assert!(out.iter().any(|f| f.code == "reject_without_reason"));
    }

    #[test]
    fn secret_like_value_detected() {
        let mut t = good_tool("x", "P1");
        t["notes"] = json!("token ghp_abcdef123456");
        let v = json!({"tools": [t]});
        let mut out = Vec::new();
        validate_registry(&v, &mut out);
        assert!(out.iter().any(|f| f.code == "secret_like_value"));
    }

    #[test]
    fn private_path_detected() {
        let mut t = good_tool("x", "P1");
        t["notes"] = json!("see C:/Users/ivan/secret.txt");
        let v = json!({"tools": [t]});
        let mut out = Vec::new();
        validate_registry(&v, &mut out);
        assert!(out.iter().any(|f| f.code == "private_absolute_path"));
    }

    #[test]
    fn fingerprint_is_deterministic_and_order_independent() {
        let a = json!({"b": 1, "a": [1, 2, {"y": 2, "x": 1}]});
        let b = json!({"a": [1, 2, {"x": 1, "y": 2}], "b": 1});
        assert_eq!(fingerprint(&a), fingerprint(&b));
        // different content -> different fingerprint
        let c = json!({"a": [1, 2, {"x": 1, "y": 3}], "b": 1});
        assert_ne!(fingerprint(&a), fingerprint(&c));
    }

    #[test]
    fn mcp_template_must_be_disabled() {
        let mut out = Vec::new();
        validate_mcp_template(&json!({"enabled": true}), "x.json", &mut out);
        assert!(out.iter().any(|f| f.code == "mcp_template_enabled"));
        let mut out2 = Vec::new();
        validate_mcp_template(&json!({"enabled": false}), "x.json", &mut out2);
        assert!(out2.iter().all(|f| f.code != "mcp_template_enabled"));
    }

    #[test]
    fn skills_registry_shape_validated() {
        let mut out = Vec::new();
        validate_skills(&json!({"agents": {"claude_code": [
            {"id": "s", "manual_required": false, "enabled": false}]}}), &mut out);
        assert!(out.iter().all(|f| f.severity != "blocker"));
    }
}
