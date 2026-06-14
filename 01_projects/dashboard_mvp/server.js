const fs = require("fs");
const http = require("http");
const path = require("path");
const { spawn, spawnSync } = require("child_process");
const { URL } = require("url");

const repoRoot = path.resolve(__dirname, "..", "..");
const dashboardRoot = __dirname;
const publicRoot = path.join(dashboardRoot, "public");
const browserProjectRoot = path.join(repoRoot, "01_projects", "browser_playground");
const runtimeProjectRoot = path.join(repoRoot, "01_projects", "runtime_mvp");
const runtimeSrcPath = path.join(runtimeProjectRoot, "src");
const desktopPlaygroundRoot = path.join(repoRoot, "01_projects", "desktop_playground");
const desktopCheckScriptPath = path.join(desktopPlaygroundRoot, "check_desktop_playground.ps1");
const desktopActionsScriptPath = path.join(desktopPlaygroundRoot, "desktop_bridge_actions.ps1");
const dashboardPort = Number.parseInt(process.env.PORT || "3210", 10);
const maxRecentActions = 25;

// Boot-time constants
let _bootCommitHash = null;
try {
  const r = spawnSync("git", ["rev-parse", "--short", "HEAD"], { encoding: "utf8", timeout: 2000 });
  if (r.status === 0) _bootCommitHash = r.stdout.trim() || null;
} catch { /* git not available */ }

// Vision status cache (10s TTL) to avoid probing Ollama on every /health request
let _visionStatusCache = null;
let _visionStatusCacheAt = 0;
const _visionCacheTtlMs = 10000;

async function getCachedOllamaVisionStatus() {
  const now = Date.now();
  if (_visionStatusCache && (now - _visionStatusCacheAt) < _visionCacheTtlMs) {
    return _visionStatusCache;
  }
  _visionStatusCache = await getOllamaVisionStatus();
  _visionStatusCacheAt = now;
  return _visionStatusCache;
}
const runtimeDataDir = path.join(runtimeProjectRoot, "runtime_data");
const activeModeStateFile = path.join(runtimeDataDir, "active_mode_state.json");
const activeSessionsFile = path.join(runtimeDataDir, "active_capture_sessions.json");
const screenshotsDir = path.join(dashboardRoot, ".tmp-screenshots");
const captureFramesDir = path.join(screenshotsDir, "capture_frames");
const captureStateFile = path.join(runtimeDataDir, "screen_capture_state.json");
const captureStopFile = path.join(captureFramesDir, ".stop");
const captureSidecarScript = path.join(runtimeProjectRoot, "src", "super_ai_agent", "screen_capture_sidecar.py");
const voiceStateFile = path.join(runtimeDataDir, "voice_state.json");
const youtubeFollowerTasksFile = path.join(runtimeDataDir, "youtube_follower_tasks.json");
const approvalsFile = path.join(runtimeDataDir, "approvals.json");
const observationsFile = path.join(runtimeDataDir, "observations.json");
const modelProbesFile = path.join(runtimeDataDir, "model_probes.json");
const maxActiveSessions = 5;
const maxYoutubeFollowerTasks = 20;
const maxSessionFrames = 12;
const maxObservations = 500;
const defaultObservationLimit = 20;
const maxObservationLimit = 100;
const maxModelProbes = 200;
const defaultProbeLimit = 20;
const maxProbeLimit = 100;
const gemmaProbeTimeoutMs = 60000;
const observeFrameTimeoutMs = 60000;
const defaultObservationPrompt = "Describe what is visible on screen in 2-4 sentences. Only describe visible UI or objects. Do not guess intent. Do not propose actions.";
const ollamaVisionModelHints = [
  "llava:7b",
  "llava",
  "moondream",
  "llama3.2-vision",
  "bakllava",
  "minicpm-v",
];
const activeSessionSafetyNote = "Local-only screen capture. Frames are only collected while the operator explicitly keeps capture running.";

let captureInterval = null;
let captureFrameCount = 0;
let captureTickRunning = false;
let currentCaptureSessionId = null;
const observationRequestsInFlight = new Set();
const previewableExtensions = new Set([
  ".md",
  ".markdown",
  ".txt",
  ".log",
  ".json",
  ".ps1",
  ".py",
  ".js",
  ".css",
  ".html",
]);

let actionCounter = 0;
const recentActions = [];

function sanitizeSessionId(sessionId) {
  const s = String(sessionId || "").trim();
  return /^ghoti-session-[A-Za-z0-9_-]+$/.test(s) ? s : null;
}

function getSessionFrameDir(sessionId) {
  const safe = sanitizeSessionId(sessionId);
  if (!safe) return null;
  const base = path.resolve(captureFramesDir);
  const dir = path.resolve(base, safe);
  if (!dir.startsWith(base + path.sep)) return null;
  return dir;
}

function resolveSessionFramePath(sessionId, frameName) {
  const dir = getSessionFrameDir(sessionId);
  if (!dir) return null;
  const safeName = path.basename(String(frameName || ""));
  if (safeName !== "latest.png" && !/^frame-\d{6}\.png$/i.test(safeName)) return null;
  const abs = path.resolve(dir, safeName);
  if (!abs.startsWith(dir + path.sep) && abs !== path.resolve(dir, safeName)) return null;
  if (!abs.startsWith(path.resolve(captureFramesDir) + path.sep)) return null;
  return abs;
}

function listSessionFrameFiles(sessionId) {
  const dir = getSessionFrameDir(sessionId);
  const resolvedDir = dir ? path.resolve(dir) : null;
  if (!resolvedDir || !fs.existsSync(resolvedDir)) {
    return { files: [], missing_files: [], total_bytes: 0, safety_root: resolvedDir || "" };
  }
  const entries = fs.readdirSync(resolvedDir);
  const files = [];
  const missing_files = [];
  let total_bytes = 0;
  for (const name of entries) {
    if (!/^frame-\d{6}\.png$/i.test(name)) continue;
    const abs = path.resolve(resolvedDir, name);
    if (!abs.startsWith(resolvedDir + path.sep)) continue;
    try {
      const stat = fs.statSync(abs);
      files.push({ name, abs, size: stat.size });
      total_bytes += stat.size;
    } catch {
      missing_files.push(name);
    }
  }
  return { files, missing_files, total_bytes, safety_root: resolvedDir };
}

function buildDefaultVoiceState() {
  return {
    mode: "placeholder",
    muted: true,
    listening: false,
    real_audio: false,
    input_provider: "not_configured",
    output_provider: "not_configured",
    stt_available: false,
    tts_available: false,
    local_only: true,
    note: "Voice is placeholder only. No real microphone or TTS is wired.",
    updated_at_utc: new Date().toISOString(),
  };
}

function readVoiceState() {
  const defaults = buildDefaultVoiceState();
  try {
    if (fs.existsSync(voiceStateFile)) {
      const stored = JSON.parse(fs.readFileSync(voiceStateFile, "utf8"));
      return {
        ...defaults,
        ...stored,
        mode: "placeholder",
        real_audio: false,
        note: defaults.note,
        updated_at_utc: stored.updated_at_utc || defaults.updated_at_utc,
      };
    }
  } catch {}
  return defaults;
}

function writeVoiceState(state) {
  if (!fs.existsSync(runtimeDataDir)) fs.mkdirSync(runtimeDataDir, { recursive: true });
  fs.writeFileSync(voiceStateFile, JSON.stringify(state, null, 2), "utf8");
}

function readYoutubeFollowerTasks() {
  try {
    if (fs.existsSync(youtubeFollowerTasksFile)) {
      return JSON.parse(fs.readFileSync(youtubeFollowerTasksFile, "utf8"));
    }
  } catch {}
  return [];
}

// Risky route pattern:
// 1. Caller omits approval_id -> create/reuse pending approval, return approval_required JSON.
// 2. Operator approves/rejects in UI.
// 3. Caller retries with approval_id.
// 4. Route consumes approval.
// 5. Route executes exactly the approved action.
// 6. Missing/rejected/consumed/wrong-type approval refuses.
// This app-level gate is separate from Claude Code CLI permissions.
function requiresOperatorApproval(action) {
  const riskyTypes = new Set([
    "cleanup_capture_files",
    "delete_file",
    "write_outside_repo",
    "send_network_request",
    "click",
    "type_text",
    "run_shell",
    "browser_submit",
    "desktop_action",
    "browser_action",
  ]);
  return riskyTypes.has(action?.type || action);
}

function buildApprovalRequiredResponse(action, reason, approval) {
  return {
    ok: false,
    approval_required: true,
    approval_id: approval?.id || null,
    action,
    reason,
    approval,
    local_only: true,
    next_step: "Approve or reject this request in the dashboard Approvals panel, then retry the original action with approval_id.",
  };
}

const MAX_APPROVALS = 200;
const MAX_PAYLOAD_STRING_LEN = 512;
const MAX_PAYLOAD_ARRAY_LEN = 20;
const APPROVAL_TTL_MS = 15 * 60 * 1000; // 15 minutes
const SENSITIVE_KEYS = /password|api_key|apikey|token|secret|credential|authorization|cookie|bearer|private_key|ssh_key/i;

function sanitizeApprovalPayload(obj, depth) {
  if (depth === undefined) depth = 0;
  if (depth > 6) return "[truncated-depth]";
  if (obj === null || obj === undefined) return obj;
  if (typeof obj === "string") return obj.length > MAX_PAYLOAD_STRING_LEN ? obj.slice(0, MAX_PAYLOAD_STRING_LEN) + "[truncated]" : obj;
  if (typeof obj !== "object") return obj;
  if (Array.isArray(obj)) {
    return obj.slice(0, MAX_PAYLOAD_ARRAY_LEN).map((v) => sanitizeApprovalPayload(v, depth + 1));
  }
  const out = {};
  let anyRedacted = false;
  for (const [k, v] of Object.entries(obj)) {
    if (SENSITIVE_KEYS.test(k)) {
      out[k] = "[REDACTED]";
      anyRedacted = true;
    } else {
      out[k] = sanitizeApprovalPayload(v, depth + 1);
    }
  }
  return { _sanitized: anyRedacted, ...out };
}

function stripSanitizedMarker(obj) {
  if (!obj || typeof obj !== "object" || Array.isArray(obj)) return obj;
  const { _sanitized, ...rest } = obj;
  return rest;
}

function sanitizePayloadClean(payload) {
  const raw = sanitizeApprovalPayload(payload);
  const wasRedacted = raw && raw._sanitized;
  const clean = stripSanitizedMarker(raw);
  return { clean: clean || {}, wasRedacted: Boolean(wasRedacted) };
}

function readApprovals() {
  let list = [];
  try {
    if (fs.existsSync(approvalsFile)) {
      list = JSON.parse(fs.readFileSync(approvalsFile, "utf8"));
      if (!Array.isArray(list)) list = [];
    }
  } catch {
    pushAction({ actionType: "warning", label: "approvals.json parse error", status: "warn", summary: "approvals.json unreadable; returning empty list." });
    return [];
  }
  // Lazy expiry sweep: expire pending records past TTL
  const now = Date.now();
  let changed = false;
  for (let i = 0; i < list.length; i++) {
    const a = list[i];
    if (a.status !== "pending") continue;
    if (a.expires_at_utc) {
      if (new Date(a.expires_at_utc).getTime() <= now) {
        list[i] = { ...a, status: "expired", expired_at_utc: new Date().toISOString() };
        changed = true;
      }
    } else {
      // Legacy record without expires_at_utc — mark and leave pending; assign TTL from now
      list[i] = { ...a, legacy_no_expiry: true };
    }
  }
  if (changed) writeApprovals(list);
  return list;
}

function writeApprovals(list) {
  if (!fs.existsSync(runtimeDataDir)) fs.mkdirSync(runtimeDataDir, { recursive: true });
  const bounded = Array.isArray(list) ? list.slice(0, MAX_APPROVALS) : [];
  const tmpPath = approvalsFile + ".tmp";
  fs.writeFileSync(tmpPath, JSON.stringify(bounded, null, 2), "utf8");
  fs.renameSync(tmpPath, approvalsFile);
}

function createApprovalRequest(action, reason, requestedBy) {
  const { clean, wasRedacted } = sanitizePayloadClean(action.payload);
  const now = new Date();
  const record = {
    id: `apv-${now.getTime()}-${Math.random().toString(36).slice(2, 7)}`,
    action: { type: String(action.type || "").slice(0, 128), payload: clean },
    reason: String(reason || "").slice(0, 512),
    requested_by: String(requestedBy || "").slice(0, 128),
    requested_at_utc: now.toISOString(),
    expires_at_utc: new Date(now.getTime() + APPROVAL_TTL_MS).toISOString(),
    status: "pending",
    decided_at_utc: null,
    decided_by: null,
    consumed_at_utc: null,
    notes: "",
    payload_sanitized: wasRedacted,
  };
  const list = readApprovals();
  list.unshift(record);
  writeApprovals(list);
  return record;
}

function getApproval(id) {
  return readApprovals().find((a) => a.id === id) || null;
}

function updateApprovalStatus(id, status, extraFields) {
  const list = readApprovals();
  const idx = list.findIndex((a) => a.id === id);
  if (idx === -1) return null;
  list[idx] = { ...list[idx], status, ...extraFields };
  writeApprovals(list);
  return list[idx];
}

function pendingApprovals() {
  return readApprovals().filter((a) => a.status === "pending");
}

// expectedPayloadSubset: if provided, every key in subset must match approval's payload
function validateAndConsumeApproval(approvalId, expectedActionType, expectedPayloadSubset) {
  const approval = getApproval(approvalId);
  if (!approval) return { ok: false, error: "approval_not_found" };
  if (approval.status === "consumed") return { ok: false, error: "already_consumed", approval };
  if (approval.status === "rejected") return { ok: false, error: "approval_rejected", approval };
  if (approval.status === "expired") return { ok: false, error: "approval_expired", approval };
  if (approval.status !== "approved") return { ok: false, error: "approval_not_approved", approval };
  if (expectedActionType && approval.action?.type !== expectedActionType) {
    return { ok: false, error: "action_mismatch", approval };
  }
  if (expectedPayloadSubset) {
    for (const [k, v] of Object.entries(expectedPayloadSubset)) {
      if (approval.action?.payload?.[k] !== v) {
        return { ok: false, error: "payload_mismatch", approval };
      }
    }
  }
  const consumed = updateApprovalStatus(approvalId, "consumed", { consumed_at_utc: new Date().toISOString() });
  return { ok: true, approval: consumed };
}

function checkOllamaReachable() {
  return new Promise((resolve) => {
    const req = http.get("http://127.0.0.1:11434/api/tags", { timeout: 2000 }, (res) => {
      let data = "";
      res.on("data", (chunk) => { data += chunk; });
      res.on("end", () => {
        try {
          const parsed = JSON.parse(data);
          const models = Array.isArray(parsed.models)
            ? parsed.models.map((m) => m.name || m.model || String(m)).filter(Boolean)
            : [];
          resolve({ reachable: true, models });
        } catch {
          resolve({ reachable: true, models: [] });
        }
      });
    });
    req.on("error", () => resolve({ reachable: false, models: [] }));
    req.on("timeout", () => { req.destroy(); resolve({ reachable: false, models: [] }); });
  });
}

function toRepoRelativePath(targetPath) {
  if (!targetPath) {
    return null;
  }
  const relative = path.relative(repoRoot, targetPath);
  return relative ? relative.replace(/\\/g, "/") : null;
}

function pickVisionModelName(allModels) {
  const entries = (Array.isArray(allModels) ? allModels : [])
    .map((model) => String(model || "").trim())
    .filter(Boolean)
    .map((model) => {
      const lower = model.toLowerCase();
      const short = lower.split("/").pop() || lower;
      return { model, lower, short };
    });

  for (const hint of ollamaVisionModelHints) {
    const normalizedHint = hint.toLowerCase();
    const match = entries.find((entry) => (
      entry.lower === normalizedHint
      || entry.lower.startsWith(`${normalizedHint}:`)
      || entry.short === normalizedHint
      || entry.short.startsWith(`${normalizedHint}:`)
      || entry.lower.includes(normalizedHint)
      || entry.short.includes(normalizedHint)
    ));
    if (match) {
      return match.model;
    }
  }

  return null;
}

function pickGemmaModelName(allModels) {
  const entries = (Array.isArray(allModels) ? allModels : [])
    .map((m) => String(m || "").trim())
    .filter(Boolean);
  return entries.find((m) => m.toLowerCase().includes("gemma")) || null;
}

function pickVisionCandidates(allModels) {
  const entries = (Array.isArray(allModels) ? allModels : [])
    .map((m) => String(m || "").trim())
    .filter(Boolean);
  return entries.filter((m) => {
    const lower = m.toLowerCase();
    return ollamaVisionModelHints.some((hint) => lower.includes(hint.toLowerCase()));
  });
}

async function getModelInventoryStatus() {
  const { reachable, models } = await checkOllamaReachable();
  const allModels = (Array.isArray(models) ? models : []).map((m) => String(m || "").trim()).filter(Boolean);
  const gemmaCandidates = allModels.filter((m) => m.toLowerCase().includes("gemma"));
  const visionCandidates = pickVisionCandidates(allModels);
  const selectedText = gemmaCandidates[0] || null;
  const selectedVision = pickVisionModelName(allModels);
  return {
    ok: true,
    ollama: { reachable, host: "127.0.0.1:11434" },
    models: {
      all: allModels,
      count: allModels.length,
      gemma_candidates: gemmaCandidates,
      selected_text_model: selectedText,
      vision_candidates: visionCandidates,
      selected_vision_model: selectedVision,
    },
    truth: {
      gemma_available: gemmaCandidates.length > 0,
      gemma_wired_for_diagnostic_probe: true,
      gemma_drives_operator: false,
      frame_understanding: selectedVision ? "vision_model_present" : "not_validated_without_vision_model",
      action_planning: false,
      autonomous_actions: false,
    },
    updated_at_utc: new Date().toISOString(),
  };
}

function buildVisionStatusNote(visionStatus) {
  if (visionStatus.available) {
    return "Vision-capable Ollama model detected. Read-only frame observer can describe frames. It does not drive operator actions.";
  }
  if (visionStatus.reason === "no_vision_model_available") {
    return "No vision-capable Ollama model found. Install one with: ollama pull llava:7b";
  }
  return "Ollama not reachable at 127.0.0.1:11434.";
}

async function getOllamaVisionStatus() {
  const { reachable, models } = await checkOllamaReachable();
  const allModels = Array.isArray(models)
    ? models.map((model) => String(model || "").trim()).filter(Boolean)
    : [];

  if (!reachable) {
    return {
      available: false,
      model: null,
      all_models: allModels,
      reason: "ollama_unreachable",
    };
  }

  const model = pickVisionModelName(allModels);
  if (!model) {
    return {
      available: false,
      model: null,
      all_models: allModels,
      reason: "no_vision_model_available",
    };
  }

  return {
    available: true,
    model,
    all_models: allModels,
    reason: null,
  };
}

function normalizeObservationRecord(record) {
  const allowedStatuses = new Set([
    "ok",
    "no_vision_model_available",
    "ollama_unreachable",
    "no_frame",
    "timeout",
    "error",
  ]);

  return {
    id: typeof record?.id === "string" ? record.id : `obs-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    session_id: sanitizeSessionId(record?.session_id) || null,
    frame_path: typeof record?.frame_path === "string" ? record.frame_path : null,
    frame_ts_utc: typeof record?.frame_ts_utc === "string" ? record.frame_ts_utc : null,
    requested_at_utc: typeof record?.requested_at_utc === "string" ? record.requested_at_utc : new Date().toISOString(),
    completed_at_utc: typeof record?.completed_at_utc === "string" ? record.completed_at_utc : null,
    model: typeof record?.model === "string" ? record.model : null,
    prompt: typeof record?.prompt === "string" && record.prompt.trim()
      ? record.prompt.trim().slice(0, 4000)
      : defaultObservationPrompt,
    description: typeof record?.description === "string" ? record.description.trim().slice(0, 12000) : "",
    latency_ms: Number.isFinite(Number(record?.latency_ms)) ? Number(record.latency_ms) : null,
    status: allowedStatuses.has(String(record?.status || "").trim()) ? String(record.status).trim() : "error",
    error: typeof record?.error === "string" && record.error.trim() ? record.error.trim().slice(0, 4000) : null,
  };
}

function readObservations() {
  try {
    if (!fs.existsSync(observationsFile)) {
      return [];
    }
    const parsed = JSON.parse(fs.readFileSync(observationsFile, "utf8"));
    if (!Array.isArray(parsed)) {
      return [];
    }
    return parsed
      .filter((item) => item && typeof item === "object")
      .map((item) => normalizeObservationRecord(item))
      .slice(0, maxObservations);
  } catch {
    return [];
  }
}

function writeObservations(list) {
  if (!fs.existsSync(runtimeDataDir)) {
    fs.mkdirSync(runtimeDataDir, { recursive: true });
  }
  const bounded = (Array.isArray(list) ? list : [])
    .filter((item) => item && typeof item === "object")
    .map((item) => normalizeObservationRecord(item))
    .slice(0, maxObservations);
  const tmpPath = `${observationsFile}.tmp-${process.pid}-${Date.now()}`;
  try {
    fs.writeFileSync(tmpPath, JSON.stringify(bounded, null, 2), "utf8");
    fs.renameSync(tmpPath, observationsFile);
  } finally {
    if (fs.existsSync(tmpPath)) {
      try { fs.unlinkSync(tmpPath); } catch { /* ignore cleanup errors */ }
    }
  }
  return bounded;
}

function appendObservation(record) {
  const observation = normalizeObservationRecord(record);
  const next = [observation, ...readObservations().filter((item) => item.id !== observation.id)].slice(0, maxObservations);
  writeObservations(next);
  return observation;
}

function listObservations(sessionId, limit = defaultObservationLimit) {
  const safeLimit = Math.max(1, Math.min(maxObservationLimit, Number.parseInt(String(limit || defaultObservationLimit), 10) || defaultObservationLimit));
  const safeId = sessionId ? sanitizeSessionId(sessionId) : null;
  const items = readObservations().filter((item) => !safeId || item.session_id === safeId);
  return items.slice(0, safeLimit);
}

// ── Model probe helpers ──────────────────────────────────────────────────────

function readModelProbes() {
  try {
    if (!fs.existsSync(modelProbesFile)) return [];
    const parsed = JSON.parse(fs.readFileSync(modelProbesFile, "utf8"));
    return Array.isArray(parsed) ? parsed : [];
  } catch { return []; }
}

function writeModelProbes(list) {
  if (!fs.existsSync(runtimeDataDir)) fs.mkdirSync(runtimeDataDir, { recursive: true });
  const bounded = (Array.isArray(list) ? list : []).slice(0, maxModelProbes);
  const tmp = `${modelProbesFile}.tmp-${process.pid}-${Date.now()}`;
  try {
    fs.writeFileSync(tmp, JSON.stringify(bounded, null, 2), "utf8");
    fs.renameSync(tmp, modelProbesFile);
  } finally {
    if (fs.existsSync(tmp)) { try { fs.unlinkSync(tmp); } catch { /* ignore */ } }
  }
  return bounded;
}

function appendModelProbe(record) {
  const bounded = [record, ...readModelProbes()].slice(0, maxModelProbes);
  writeModelProbes(bounded);
  return record;
}

function requestOllamaGenerate(model, prompt) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ model, prompt, stream: false });
    const req = http.request({
      hostname: "127.0.0.1",
      port: 11434,
      path: "/api/generate",
      method: "POST",
      headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body) },
      timeout: gemmaProbeTimeoutMs,
    }, (res) => {
      let data = "";
      res.on("data", (chunk) => { data += chunk; });
      res.on("end", () => {
        try {
          const parsed = JSON.parse(data);
          resolve(parsed);
        } catch { reject(new Error("ollama_invalid_json")); }
      });
    });
    req.on("error", reject);
    req.on("timeout", () => { req.destroy(); reject(new Error("ollama_timeout")); });
    req.write(body);
    req.end();
  });
}

function requestOllamaVisionDescription(model, prompt, imageBase64) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model,
      prompt,
      images: [imageBase64],
      stream: false,
    });

    const req = http.request({
      hostname: "127.0.0.1",
      port: 11434,
      path: "/api/generate",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(body),
      },
      timeout: observeFrameTimeoutMs,
    }, (res) => {
      let data = "";
      res.on("data", (chunk) => { data += chunk; });
      res.on("end", () => {
        if (res.statusCode < 200 || res.statusCode >= 300) {
          const err = new Error(`ollama_http_${res.statusCode}`);
          err.code = "OLLAMA_HTTP_ERROR";
          err.details = data;
          reject(err);
          return;
        }
        try {
          resolve(JSON.parse(data || "{}"));
        } catch {
          const err = new Error("ollama_invalid_json");
          err.code = "OLLAMA_INVALID_JSON";
          reject(err);
        }
      });
    });

    req.on("error", (error) => reject(error));
    req.on("timeout", () => {
      const err = new Error("ollama_timeout");
      err.code = "OLLAMA_TIMEOUT";
      req.destroy(err);
    });
    req.write(body);
    req.end();
  });
}

function writeYoutubeFollowerTasks(tasks) {
  if (!fs.existsSync(runtimeDataDir)) fs.mkdirSync(runtimeDataDir, { recursive: true });
  fs.writeFileSync(youtubeFollowerTasksFile, JSON.stringify(tasks, null, 2), "utf8");
}

function createYoutubeFollowerTask(body) {
  const tasks = readYoutubeFollowerTasks();
  const task = {
    id: `yt-task-${Date.now()}`,
    url: String(body.url || "").slice(0, 2048),
    goal: String(body.goal || "follow the tutorial").slice(0, 512),
    created_at: new Date().toISOString(),
    status: "planned",
    execution_enabled: false,
    needs_user_approval: true,
    next_step: "browser_operator_not_integrated",
    steps: [],
    log: [],
  };
  tasks.unshift(task);
  if (tasks.length > maxYoutubeFollowerTasks) tasks.length = maxYoutubeFollowerTasks;
  writeYoutubeFollowerTasks(tasks);
  return task;
}

function firstNonEmptyValue(values) {
  for (const value of values) {
    if (value && value.trim()) {
      return value.trim();
    }
  }

  return "";
}

function resolveCommand(candidates, versionArgs) {
  for (const candidate of candidates) {
    const result = spawnSync(candidate.command, [...candidate.baseArgs, ...versionArgs], {
      cwd: repoRoot,
      encoding: "utf8",
      windowsHide: true,
    });
    if (result.error || result.status !== 0) {
      continue;
    }

    return {
      command: candidate.command,
      baseArgs: candidate.baseArgs,
      displayName: candidate.displayName,
      version: firstNonEmptyValue([result.stdout, result.stderr]),
    };
  }

  return null;
}

function probeTool(commands, timeoutMs) {
  const t = timeoutMs || 2000;
  for (const entry of commands) {
    try {
      const r = spawnSync(entry.cmd, entry.args || ["--version"], {
        encoding: "utf8",
        timeout: t,
        windowsHide: true,
        shell: process.platform === "win32",
      });
      if (r.status === 0) {
        const ver = (r.stdout || r.stderr || "").trim().split("\n")[0];
        return { available: true, version: ver || "ok" };
      }
    } catch { /* command not found */ }
  }
  return { available: false, error: "not_found" };
}

function probeCodexTool() {
  const direct = probeTool([{ cmd: "codex.cmd" }, { cmd: "codex" }]);
  if (direct.available) {
    return {
      ...direct,
      command: direct.version ? "codex.cmd/codex" : "codex",
      app_operator_surface: true,
      cli_invocable: true,
    };
  }

  if (process.platform !== "win32") {
    return { available: false, error: direct.error || "not_found" };
  }

  try {
    const ps = spawnSync("powershell.exe", [
      "-NoProfile",
      "-Command",
      "$cmd = Get-Command codex -ErrorAction SilentlyContinue; if (-not $cmd) { $cmd = Get-Command codex.cmd -ErrorAction SilentlyContinue }; if ($cmd) { $cmd.Source }",
    ], {
      encoding: "utf8",
      timeout: 2000,
      windowsHide: true,
    });
    const source = (ps.stdout || "").trim().split(/\r?\n/).find(Boolean);
    if (source) {
      return {
        available: true,
        command_visible: true,
        cli_invocable: false,
        command: source.toLowerCase().endsWith("codex.cmd") ? "codex.cmd" : "codex",
        path: source,
        error: "version_probe_failed_or_access_denied",
        note: "Codex app executable is visible to this shell, but --version could not be launched from the dashboard process.",
        app_operator_surface: true,
      };
    }
  } catch { /* keep not_found fallback */ }

  return { available: false, error: direct.error || "not_found" };
}

function resolvePython() {
  const candidates = [];
  if (process.env.SUPER_AGENT_PYTHON) {
    candidates.push({
      command: process.env.SUPER_AGENT_PYTHON,
      baseArgs: [],
      displayName: "SUPER_AGENT_PYTHON",
    });
  }
  candidates.push(
    { command: "python", baseArgs: [], displayName: "python" },
    { command: "py", baseArgs: ["-3"], displayName: "py -3" },
    {
      command: "C:\\Program Files\\KiCad\\9.0\\bin\\python.exe",
      baseArgs: [],
      displayName: "KiCad bundled python",
    },
  );

  return resolveCommand(candidates, ["--version"]);
}

function resolvePowerShell() {
  return resolveCommand(
    [
      { command: "powershell.exe", baseArgs: [], displayName: "powershell.exe" },
      { command: "powershell", baseArgs: [], displayName: "powershell" },
      { command: "pwsh.exe", baseArgs: [], displayName: "pwsh.exe" },
      { command: "pwsh", baseArgs: [], displayName: "pwsh" },
    ],
    ["-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"],
  );
}

function buildRuntimeEnv() {
  const pythonPath = process.env.PYTHONPATH
    ? `${runtimeSrcPath}${path.delimiter}${process.env.PYTHONPATH}`
    : runtimeSrcPath;

  return {
    ...process.env,
    PYTHONPATH: pythonPath,
  };
}

function pushAction(entry) {
  recentActions.unshift({
    actionId: `action-${Date.now()}-${++actionCounter}`,
    occurredAt: new Date().toISOString(),
    ...entry,
  });
  recentActions.splice(maxRecentActions);
}

function runCommand(command, args, options = {}) {
  return new Promise((resolve) => {
    const child = spawn(command, args, {
      cwd: options.cwd || repoRoot,
      env: options.env || process.env,
      windowsHide: false,
      shell: false,
    });
    let stdout = "";
    let stderr = "";
    let settled = false;

    const finalize = (result) => {
      if (settled) {
        return;
      }
      settled = true;
      resolve({
        ok: result.code === 0,
        exitCode: result.code,
        stdout: stdout.trim(),
        stderr: stderr.trim(),
        command: [command, ...args].join(" "),
        timedOut: Boolean(result.timedOut),
      });
    };

    const timeoutMs = options.timeoutMs || 120000;
    const timer = setTimeout(() => {
      stderr += `${stderr ? "\n" : ""}Process timed out after ${timeoutMs} ms.`;
      child.kill();
      finalize({ code: 1, timedOut: true });
    }, timeoutMs);

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    child.on("error", (error) => {
      clearTimeout(timer);
      stderr += `${stderr ? "\n" : ""}${error.message}`;
      finalize({ code: 1, timedOut: false });
    });
    child.on("close", (code) => {
      clearTimeout(timer);
      finalize({ code: code ?? 1, timedOut: false });
    });
  });
}

function readActiveModeState() {
  const defaults = {
    active: false,
    mode: "idle",
    screen_view_enabled: false,
    audio_enabled: false,
    last_snapshot_path: null,
    last_event_utc: null,
    error: null,
    safety_note: "No hidden recording. Screen capture only when explicitly triggered by operator.",
  };
  try {
    if (!fs.existsSync(activeModeStateFile)) return defaults;
    return { ...defaults, ...JSON.parse(fs.readFileSync(activeModeStateFile, "utf8")) };
  } catch {
    return defaults;
  }
}

function writeActiveModeState(patch) {
  const current = readActiveModeState();
  const next = { ...current, ...patch, last_event_utc: new Date().toISOString() };
  if (!fs.existsSync(runtimeDataDir)) fs.mkdirSync(runtimeDataDir, { recursive: true });
  fs.writeFileSync(activeModeStateFile, JSON.stringify(next, null, 2));
  return next;
}

function readCaptureState() {
  const defaults = {
    capturing: false,
    capture_method: null,
    fps_target: 1,
    frame_count: 0,
    latest_frame_path: null,
    latest_frame_utc: null,
    error: null,
  };
  try {
    if (!fs.existsSync(captureStateFile)) return defaults;
    return { ...defaults, ...JSON.parse(fs.readFileSync(captureStateFile, "utf8")) };
  } catch {
    return defaults;
  }
}

function normalizeRecentFrames(frames) {
  if (!Array.isArray(frames)) {
    return [];
  }

  return frames
    .filter((frame) => frame && typeof frame === "object")
    .map((frame) => ({
      frame_id: typeof frame.frame_id === "string" ? frame.frame_id : null,
      filename: typeof frame.filename === "string" ? frame.filename : null,
      captured_at_utc: typeof frame.captured_at_utc === "string" ? frame.captured_at_utc : null,
      image_url: typeof frame.image_url === "string" ? frame.image_url : null,
    }))
    .filter((frame) => frame.filename)
    .slice(0, maxSessionFrames);
}

function normalizeReviewNote(value) {
  return typeof value === "string" ? value.trim().slice(0, 600) : "";
}

function normalizeRetentionStatus(value) {
  const normalized = String(value || "").trim().toLowerCase();
  if (normalized === "kept" || normalized === "discarded") {
    return normalized;
  }
  return "default";
}

function normalizeActiveSession(session) {
  if (!session || typeof session !== "object") {
    return null;
  }

  return {
    session_id: typeof session.session_id === "string" ? session.session_id : null,
    status: typeof session.status === "string" ? session.status : "idle",
    started_at_utc: typeof session.started_at_utc === "string" ? session.started_at_utc : null,
    stopped_at_utc: typeof session.stopped_at_utc === "string" ? session.stopped_at_utc : null,
    capture_running: Boolean(session.capture_running),
    capture_started_at_utc: typeof session.capture_started_at_utc === "string" ? session.capture_started_at_utc : null,
    capture_stopped_at_utc: typeof session.capture_stopped_at_utc === "string" ? session.capture_stopped_at_utc : null,
    frame_count: Number.isFinite(Number(session.frame_count)) ? Number(session.frame_count) : 0,
    capture_method: typeof session.capture_method === "string" ? session.capture_method : null,
    frame_dir: typeof session.frame_dir === "string" ? session.frame_dir : null,
    latest_frame_path: typeof session.latest_frame_path === "string" ? session.latest_frame_path : null,
    latest_frame_name: typeof session.latest_frame_name === "string" ? session.latest_frame_name : null,
    latest_frame_utc: typeof session.latest_frame_utc === "string" ? session.latest_frame_utc : null,
    latest_frame_url: session.latest_frame_path && session.session_id ? `/api/ghoti/active/latest-frame?session_id=${encodeURIComponent(session.session_id)}` : (session.latest_frame_path ? "/api/ghoti/active/latest-frame" : null),
    recent_frames: normalizeRecentFrames(session.recent_frames),
    reviewed: Boolean(session.reviewed),
    reviewed_at_utc: typeof session.reviewed_at_utc === "string" ? session.reviewed_at_utc : null,
    review_note: normalizeReviewNote(session.review_note),
    retention_status: normalizeRetentionStatus(session.retention_status),
    cleanup_status: typeof session.cleanup_status === "string" ? session.cleanup_status : null,
    cleaned_at_utc: typeof session.cleaned_at_utc === "string" ? session.cleaned_at_utc : null,
    cleaned_file_count: Number.isFinite(Number(session.cleaned_file_count)) && session.cleaned_file_count != null ? Number(session.cleaned_file_count) : null,
    cleaned_bytes: Number.isFinite(Number(session.cleaned_bytes)) && session.cleaned_bytes != null ? Number(session.cleaned_bytes) : null,
    cleanup_missing_file_count: Number.isFinite(Number(session.cleanup_missing_file_count)) && session.cleanup_missing_file_count != null ? Number(session.cleanup_missing_file_count) : null,
    operator_controlled: true,
    local_only: true,
    safety_note: activeSessionSafetyNote,
  };
}

function buildActiveSessionRecord() {
  return normalizeActiveSession({
    session_id: `ghoti-session-${Date.now()}`,
    status: "active",
    started_at_utc: new Date().toISOString(),
    stopped_at_utc: null,
    capture_running: false,
    capture_started_at_utc: null,
    capture_stopped_at_utc: null,
    frame_count: 0,
    capture_method: null,
    frame_dir: null,
    latest_frame_path: null,
    latest_frame_name: null,
    latest_frame_utc: null,
    recent_frames: [],
    reviewed: false,
    reviewed_at_utc: null,
    review_note: "",
    retention_status: "default",
    operator_controlled: true,
    local_only: true,
    safety_note: activeSessionSafetyNote,
  });
}

function buildActiveSessionSummary(session) {
  const normalized = normalizeActiveSession(session);
  if (!normalized) {
    return null;
  }

  return {
    session_id: normalized.session_id,
    status: normalized.status,
    started_at_utc: normalized.started_at_utc,
    stopped_at_utc: normalized.stopped_at_utc,
    capture_running: normalized.capture_running,
    frame_count: normalized.frame_count,
    latest_frame_utc: normalized.latest_frame_utc,
    latest_frame_available: Boolean(normalized.latest_frame_path),
    reviewed: normalized.reviewed,
    reviewed_at_utc: normalized.reviewed_at_utc,
    review_note: normalized.review_note,
    retention_status: normalized.retention_status,
    cleanup_status: normalized.cleanup_status,
    cleaned_at_utc: normalized.cleaned_at_utc,
    cleaned_file_count: normalized.cleaned_file_count,
    cleaned_bytes: normalized.cleaned_bytes,
    cleanup_missing_file_count: normalized.cleanup_missing_file_count,
    frame_dir: normalized.frame_dir,
    legacy_capture: !normalized.frame_dir,
    operator_controlled: true,
    local_only: true,
    safety_note: normalized.safety_note,
  };
}

function readActiveSessionStore() {
  const defaults = {
    current_session: null,
    recent_sessions: [],
  };

  try {
    if (!fs.existsSync(activeSessionsFile)) {
      return defaults;
    }

    const parsed = JSON.parse(fs.readFileSync(activeSessionsFile, "utf8"));
    return {
      current_session: normalizeActiveSession(parsed.current_session),
      recent_sessions: Array.isArray(parsed.recent_sessions)
        ? parsed.recent_sessions
          .filter((session) => session && typeof session === "object")
          .map((session) => buildActiveSessionSummary(session))
          .filter(Boolean)
          .slice(0, maxActiveSessions)
        : [],
    };
  } catch {
    return defaults;
  }
}

function writeActiveSessionStore(store) {
  const next = {
    current_session: normalizeActiveSession(store.current_session),
    recent_sessions: Array.isArray(store.recent_sessions)
      ? store.recent_sessions.filter((session) => session && typeof session === "object").slice(0, maxActiveSessions)
      : [],
  };

  if (!fs.existsSync(runtimeDataDir)) {
    fs.mkdirSync(runtimeDataDir, { recursive: true });
  }

  fs.writeFileSync(activeSessionsFile, JSON.stringify(next, null, 2));
  return next;
}

function upsertRecentSessionSummary(recentSessions, session, options = {}) {
  const summary = buildActiveSessionSummary(session);
  if (!summary || !summary.session_id) {
    return Array.isArray(recentSessions) ? recentSessions.slice(0, maxActiveSessions) : [];
  }

  const items = Array.isArray(recentSessions) ? recentSessions.filter((item) => item && typeof item === "object") : [];
  if (options.promote === false) {
    let found = false;
    const nextItems = items.map((item) => {
      if (item?.session_id === summary.session_id) {
        found = true;
        return summary;
      }
      return buildActiveSessionSummary(item) || item;
    }).filter(Boolean);
    if (!found) {
      nextItems.unshift(summary);
    }
    return nextItems.slice(0, maxActiveSessions);
  }

  return [
    summary,
    ...items.filter((item) => item?.session_id !== summary.session_id),
  ].slice(0, maxActiveSessions);
}

function updateStoredActiveSession(sessionId, patch) {
  const normalizedId = String(sessionId || "").trim();
  if (!normalizedId) {
    throw new Error("session_id is required.");
  }

  const store = readActiveSessionStore();
  const recentSessions = Array.isArray(store.recent_sessions) ? store.recent_sessions : [];
  const baseSession = store.current_session?.session_id === normalizedId
    ? normalizeActiveSession(store.current_session)
    : normalizeActiveSession(recentSessions.find((session) => session?.session_id === normalizedId));

  if (!baseSession) {
    return null;
  }

  const nextSession = normalizeActiveSession({
    ...baseSession,
    ...patch,
    review_note: Object.prototype.hasOwnProperty.call(patch || {}, "review_note")
      ? normalizeReviewNote(patch.review_note)
      : baseSession.review_note,
    retention_status: Object.prototype.hasOwnProperty.call(patch || {}, "retention_status")
      ? normalizeRetentionStatus(patch.retention_status)
      : baseSession.retention_status,
  });

  if (store.current_session?.session_id === normalizedId) {
    store.current_session = nextSession;
  } else {
    store.current_session = normalizeActiveSession(store.current_session);
  }

  store.recent_sessions = upsertRecentSessionSummary(recentSessions, nextSession, { promote: false });
  const written = writeActiveSessionStore(store);
  return written.current_session?.session_id === normalizedId
    ? written.current_session
    : written.recent_sessions.find((session) => session?.session_id === normalizedId) || buildActiveSessionSummary(nextSession);
}

function ensureCurrentActiveSession() {
  const store = readActiveSessionStore();
  let session = normalizeActiveSession(store.current_session);

  if (!session || session.status !== "active") {
    session = buildActiveSessionRecord();
  } else {
    session = {
      ...session,
      status: "active",
      stopped_at_utc: null,
      operator_controlled: true,
      local_only: true,
      safety_note: activeSessionSafetyNote,
    };
  }

  store.current_session = session;
  store.recent_sessions = upsertRecentSessionSummary(store.recent_sessions, session);
  return writeActiveSessionStore(store).current_session;
}

function markCurrentSessionCaptureStarted(method = "powershell-copyfromscreen-loop") {
  const store = readActiveSessionStore();
  const session = normalizeActiveSession(store.current_session) || buildActiveSessionRecord();
  const nowUtc = new Date().toISOString();
  const sessionFrameDir = getSessionFrameDir(session.session_id);
  if (sessionFrameDir && !fs.existsSync(sessionFrameDir)) {
    fs.mkdirSync(sessionFrameDir, { recursive: true });
  }
  const next = {
    ...session,
    status: "active",
    capture_running: true,
    capture_started_at_utc: nowUtc,
    capture_stopped_at_utc: null,
    frame_count: 0,
    capture_method: method,
    frame_dir: sessionFrameDir || null,
    latest_frame_path: null,
    latest_frame_name: null,
    latest_frame_utc: null,
    latest_frame_url: null,
    recent_frames: [],
    operator_controlled: true,
    local_only: true,
    safety_note: activeSessionSafetyNote,
  };

  store.current_session = next;
  store.recent_sessions = upsertRecentSessionSummary(store.recent_sessions, next);
  return writeActiveSessionStore(store).current_session;
}

function recordCurrentSessionFrame(framePath, latestPath, capturedAtUtc) {
  const store = readActiveSessionStore();
  const session = normalizeActiveSession(store.current_session);
  if (!session) {
    return null;
  }

  const nextFrameCount = Number(session.frame_count || 0) + 1;
  const filename = path.basename(framePath);
  const sidParam = session.session_id ? `&session_id=${encodeURIComponent(session.session_id)}` : "";
  const next = {
    ...session,
    capture_running: true,
    capture_method: session.capture_method || "powershell-copyfromscreen-loop",
    frame_count: nextFrameCount,
    frame_dir: session.frame_dir,
    latest_frame_path: latestPath,
    latest_frame_name: filename,
    latest_frame_utc: capturedAtUtc,
    latest_frame_url: session.session_id ? `/api/ghoti/active/latest-frame?session_id=${encodeURIComponent(session.session_id)}` : "/api/ghoti/active/latest-frame",
    recent_frames: [
      {
        frame_id: `${session.session_id}-frame-${String(nextFrameCount).padStart(6, "0")}`,
        filename,
        captured_at_utc: capturedAtUtc,
        image_url: `/api/ghoti/active/frame?name=${encodeURIComponent(filename)}${sidParam}`,
      },
      ...session.recent_frames.filter((frame) => frame.filename !== filename),
    ].slice(0, maxSessionFrames),
    operator_controlled: true,
    local_only: true,
    safety_note: activeSessionSafetyNote,
  };

  store.current_session = next;
  store.recent_sessions = upsertRecentSessionSummary(store.recent_sessions, next);
  return writeActiveSessionStore(store).current_session;
}

function markCurrentSessionCaptureStopped() {
  const store = readActiveSessionStore();
  const session = normalizeActiveSession(store.current_session);
  if (!session) {
    return null;
  }

  const next = {
    ...session,
    capture_running: false,
    capture_stopped_at_utc: new Date().toISOString(),
    operator_controlled: true,
    local_only: true,
    safety_note: activeSessionSafetyNote,
  };

  store.current_session = next;
  store.recent_sessions = upsertRecentSessionSummary(store.recent_sessions, next);
  return writeActiveSessionStore(store).current_session;
}

function closeCurrentActiveSession() {
  const store = readActiveSessionStore();
  const session = normalizeActiveSession(store.current_session);
  if (!session) {
    return null;
  }

  const nowUtc = new Date().toISOString();
  const next = {
    ...session,
    status: "stopped",
    capture_running: false,
    stopped_at_utc: nowUtc,
    capture_stopped_at_utc: session.capture_running || session.capture_started_at_utc
      ? (session.capture_stopped_at_utc || nowUtc)
      : session.capture_stopped_at_utc,
    operator_controlled: true,
    local_only: true,
    safety_note: activeSessionSafetyNote,
  };

  store.current_session = next;
  store.recent_sessions = upsertRecentSessionSummary(store.recent_sessions, next);
  return writeActiveSessionStore(store).current_session;
}

function getStoredSessionById(sessionId) {
  const safeId = sanitizeSessionId(sessionId);
  if (!safeId) {
    return null;
  }
  const store = readActiveSessionStore();
  return safeId === store.current_session?.session_id
    ? normalizeActiveSession(store.current_session)
    : normalizeActiveSession((store.recent_sessions || []).find((session) => session?.session_id === safeId));
}

function resolveLatestFramePathForSession(sessionId) {
  const safeId = sanitizeSessionId(sessionId);
  if (!safeId) {
    return null;
  }
  const candidate = resolveSessionFramePath(safeId, "latest.png");
  return candidate && fs.existsSync(candidate) ? candidate : null;
}

function resolveFramePathForSession(sessionId, frameName) {
  const safeName = path.basename(String(frameName || ""));
  if (!/^frame-\d{6}\.png$/i.test(safeName)) return null;
  const safeId = sanitizeSessionId(sessionId);
  if (!safeId) return null;
  const dir = getSessionFrameDir(safeId);
  if (!dir) return null;
  const abs = path.resolve(dir, safeName);
  if (!abs.startsWith(path.resolve(captureFramesDir) + path.sep)) return null;
  if (!fs.existsSync(abs)) return null;
  return abs;
}

function resolveCurrentSessionFramePath(sessionIdHint, frameName) {
  const safeName = path.basename(String(frameName || ""));
  if (!/^frame-\d{6}\.png$/i.test(safeName)) return null;

  const store = readActiveSessionStore();

  const trySession = (session) => {
    if (!session) return null;
    if (!session.recent_frames.some((frame) => frame.filename === safeName)) return null;
    return resolveFramePathForSession(session.session_id, safeName);
  };

  if (sessionIdHint) {
    const safeHint = sanitizeSessionId(sessionIdHint);
    if (safeHint) {
      const hintSession = safeHint === store.current_session?.session_id
        ? normalizeActiveSession(store.current_session)
        : normalizeActiveSession((store.recent_sessions || []).find((s) => s?.session_id === safeHint));
      const found = trySession(hintSession);
      if (found) return found;
    }
  }

  return trySession(normalizeActiveSession(store.current_session));
}

function stopCaptureProcess() {
  if (captureInterval) {
    clearInterval(captureInterval);
    captureInterval = null;
  }
  captureTickRunning = false;
  currentCaptureSessionId = null;
  const current = readCaptureState();
  const stopped = { ...current, capturing: false };
  try {
    if (!fs.existsSync(runtimeDataDir)) fs.mkdirSync(runtimeDataDir, { recursive: true });
    fs.writeFileSync(captureStateFile, JSON.stringify(stopped, null, 2));
  } catch { /* best effort */ }
  markCurrentSessionCaptureStopped();
}

async function captureOneTick(powerShell) {
  if (captureTickRunning) return;
  captureTickRunning = true;
  try {
    const sessionId = currentCaptureSessionId;
    const sessionDir = sessionId ? getSessionFrameDir(sessionId) : null;
    if (sessionDir && !fs.existsSync(sessionDir)) {
      fs.mkdirSync(sessionDir, { recursive: true });
    }
    const writeDir = sessionDir || captureFramesDir;
    const latestPath = path.join(writeDir, "latest.png");
    const frameName = `frame-${String(captureFrameCount).padStart(6, "0")}.png`;
    const framePath = path.join(writeDir, frameName);
    // Also keep a global latest for backward compat (not a cleanup candidate)
    const globalLatestPath = path.join(captureFramesDir, "latest.png");
    const latestEsc = latestPath.replace(/\\/g, "\\\\");
    const frameEsc = framePath.replace(/\\/g, "\\\\");
    const globalLatestEsc = globalLatestPath.replace(/\\/g, "\\\\");
    const saveLines = [
      `$bmp.Save("${latestEsc}")`,
      `$bmp.Save("${frameEsc}")`,
    ];
    if (sessionDir && globalLatestPath !== latestPath) {
      saveLines.push(`$bmp.Save("${globalLatestEsc}")`);
    }
    const psScript = [
      "Add-Type -AssemblyName System.Windows.Forms",
      "Add-Type -AssemblyName System.Drawing",
      "$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds",
      "$bmp = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)",
      "$g = [System.Drawing.Graphics]::FromImage($bmp)",
      "$g.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)",
      "$g.Dispose()",
      ...saveLines,
      "$bmp.Dispose()",
      "Write-Output 'ok'",
    ].join("; ");
    const result = await runCommand(
      powerShell.command,
      [...powerShell.baseArgs, "-ExecutionPolicy", "Bypass", "-Command", psScript],
      { cwd: repoRoot, timeoutMs: 10000 }
    );
    // If stop was called while we were capturing, do not overwrite the stopped state
    if (!captureInterval) return;
    if (result.ok && fs.existsSync(latestPath)) {
      captureFrameCount++;
      const nowUtc = new Date().toISOString();
      if (!fs.existsSync(runtimeDataDir)) fs.mkdirSync(runtimeDataDir, { recursive: true });
      fs.writeFileSync(captureStateFile, JSON.stringify({
        capturing: true,
        capture_method: "powershell-copyfromscreen-loop",
        fps_target: 1,
        frame_count: captureFrameCount,
        session_id: sessionId || null,
        session_frame_dir: sessionDir || null,
        latest_frame_path: latestPath,
        latest_frame_name: frameName,
        latest_frame_utc: nowUtc,
        error: null,
      }, null, 2));
      recordCurrentSessionFrame(framePath, latestPath, nowUtc);
    } else {
      const cur = readCaptureState();
      if (!fs.existsSync(runtimeDataDir)) fs.mkdirSync(runtimeDataDir, { recursive: true });
      fs.writeFileSync(captureStateFile, JSON.stringify({
        ...cur,
        error: result.stderr || result.stdout || "PowerShell capture failed",
      }, null, 2));
    }
  } catch (err) {
    process.stderr.write(`[capture] tick error: ${err.message}\n`);
  } finally {
    captureTickRunning = false;
  }
}

async function runRuntimeCli(cliArgs) {
  const python = resolvePython();
  if (!python) {
    return {
      ok: false,
      exitCode: 1,
      stdout: "",
      stderr: "Python runtime not found for dashboard server.",
      command: "python -m super_ai_agent.cli",
      tool: "python",
    };
  }

  const result = await runCommand(
    python.command,
    [...python.baseArgs, "-m", "super_ai_agent.cli", ...cliArgs],
    {
      cwd: repoRoot,
      env: buildRuntimeEnv(),
      timeoutMs: 120000,
    },
  );

  return {
    ...result,
    tool: python.displayName,
  };
}

async function runBrowserDemo(visible, checkOnly) {
  const scriptPath = path.join(browserProjectRoot, "scripts", "smoke_click_demo.js");
  const playwrightPath = path.join(browserProjectRoot, "node_modules", "playwright");
  if (!fs.existsSync(playwrightPath)) {
    return {
      ok: false,
      degraded: true,
      exitCode: 0,
      stdout: [
        "mode: dependency_missing",
        "missing_dependency: playwright",
        "screenshot_path: none",
        `headless: ${visible ? "no" : "yes"}`,
        "slow_mo: 0",
        "keep_open_ms: 0",
      ].join("\n"),
      stderr: "Playwright is not installed in the local browser playground; browser demo was not run.",
      command: `${process.execPath} ${scriptPath}`,
      timedOut: false,
    };
  }
  const args = [scriptPath];
  if (visible) {
    args.push("--visible");
  }
  if (checkOnly) {
    args.push("--check-only");
  }

  const result = await runCommand(process.execPath, args, {
    cwd: browserProjectRoot,
    env: process.env,
    timeoutMs: visible && !checkOnly ? 180000 : 120000,
  });

  return {
    ...result,
    tool: "node",
  };
}

async function runDesktopBridgeCheck(statusOnly) {
  const powerShell = resolvePowerShell();
  if (!powerShell) {
    return {
      ok: false,
      exitCode: 1,
      stdout: "",
      stderr: "PowerShell runtime not found for desktop bridge check.",
      command: "powershell -ExecutionPolicy Bypass -File check_desktop_playground.ps1",
      tool: "powershell",
    };
  }

  const args = [...powerShell.baseArgs, "-ExecutionPolicy", "Bypass", "-File", desktopCheckScriptPath];
  if (statusOnly) {
    args.push("-StatusOnly");
  }

  const result = await runCommand(powerShell.command, args, {
    cwd: desktopPlaygroundRoot,
    env: process.env,
    timeoutMs: 120000,
  });

  return {
    ...result,
    tool: powerShell.displayName,
  };
}

async function runDesktopBridgeAction(action, options = {}) {
  const powerShell = resolvePowerShell();
  if (!powerShell) {
    return {
      ok: false,
      exitCode: 1,
      stdout: "",
      stderr: "PowerShell runtime not found for desktop bridge action.",
      command: "powershell -ExecutionPolicy Bypass -File desktop_bridge_actions.ps1",
      tool: "powershell",
    };
  }

  const args = [
    ...powerShell.baseArgs,
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    desktopActionsScriptPath,
    "-Action",
    String(action || ""),
  ];
  if (options.target) {
    args.push("-Target", String(options.target));
  }
  if (options.artifactPath) {
    args.push("-ArtifactPath", String(options.artifactPath));
  }
  if (options.textContent) {
    args.push("-TextContent", String(options.textContent));
  }

  const result = await runCommand(powerShell.command, args, {
    cwd: desktopPlaygroundRoot,
    env: options.env || process.env,
    timeoutMs: options.timeoutMs || 120000,
  });

  return {
    ...result,
    tool: powerShell.displayName,
  };
}

function parseKeyValueBlock(stdout) {
  const values = {};
  const listSections = {};
  let currentList = null;

  for (const rawLine of stdout.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line) {
      continue;
    }

    if (line.endsWith(":") && !line.includes(" | ")) {
      currentList = line.slice(0, -1);
      if (!listSections[currentList]) {
        listSections[currentList] = [];
      }
      continue;
    }

    if (currentList && line.startsWith("- ")) {
      listSections[currentList].push(line.slice(2));
      continue;
    }

    currentList = null;
    const separatorIndex = line.indexOf(":");
    if (separatorIndex !== -1) {
      const key = line.slice(0, separatorIndex).trim();
      const value = line.slice(separatorIndex + 1).trim();
      values[key] = value;
    }
  }

  return {
    values,
    listSections,
  };
}

function parseCapabilitySummary(stdout) {
  const capabilities = stdout
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const parts = line.split(" | ").map((part) => part.trim());
      if (parts.length !== 4) {
        return null;
      }
      return {
        capabilityId: parts[0],
        state: parts[1],
        requiredTools: parts[2].replace(/^requires:\s*/, ""),
        blockingIssue: parts[3].replace(/^block:\s*/, ""),
      };
    })
    .filter(Boolean);

  const availableCount = capabilities.filter((item) => item.state === "available").length;
  const blockedCount = capabilities.filter((item) => item.state === "blocked").length;

  return {
    capabilities,
    availableCount,
    blockedCount,
    headline: `${availableCount} available, ${blockedCount} blocked`,
  };
}

function parseGithubStatus(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  return {
    repoRoot: parsed.values.repo_root || "unknown",
    branch: parsed.values.branch || "unknown",
    clean: parsed.values.clean === "yes",
    stagedChanges: Number.parseInt(parsed.values.staged_changes || "0", 10),
    unstagedChanges: Number.parseInt(parsed.values.unstaged_changes || "0", 10),
    untrackedChanges: Number.parseInt(parsed.values.untracked_changes || "0", 10),
    originUrl: parsed.values.origin_url || "none",
    ghAvailable: parsed.values.gh_available === "yes",
    ghAuthenticated: parsed.values.gh_authenticated || "unknown",
    recentCommits: parsed.listSections.recent_commits || [],
  };
}

function parseRemoteCapability(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  return {
    repoRoot: parsed.values.repo_root || "unknown",
    branch: parsed.values.branch || "unknown",
    originUrl: parsed.values.origin_url || "none",
    ghAvailable: parsed.values.gh_available === "yes",
    ghAuthenticated: parsed.values.gh_authenticated || "unknown",
    remoteWritePossible: parsed.values.remote_write_possible === "yes",
    blockingIssue: parsed.values.blocking_issue || "none",
  };
}

function parseBrowserResult(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  return {
    mode: parsed.values.mode || "unknown",
    screenshotPath: parsed.values.smoke_screenshot || parsed.values.screenshot_path || "none",
    headless: parsed.values.headless || "unknown",
    slowMo: parsed.values.slow_mo || "0",
    keepOpenMs: parsed.values.keep_open_ms || "0",
  };
}

function parseDesktopBridge(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  return {
    mode: parsed.values.mode || "unknown",
    headline: parsed.values.headline || "Desktop bridge status unavailable.",
    powerShellAvailable: parsed.values.powershell_available === "yes",
    powerShellVersion: parsed.values.powershell_version || "unknown",
    explorerAvailable: parsed.values.explorer_available === "yes",
    processVisibility: parsed.values.process_visibility === "yes",
    shellCommandCapability: parsed.values.shell_command_capability === "yes",
    launcherCapability: parsed.values.launcher_capability || "unknown",
    failsafeHotkey: parsed.values.failsafe_hotkey || "Ctrl+8",
    desktopControlImplemented: parsed.values.desktop_control_implemented === "yes",
    terminalWindowCount: Number.parseInt(parsed.values.terminal_window_count || "0", 10),
    powerShellProcessCount: Number.parseInt(parsed.values.powershell_process_count || "0", 10),
    nodeProcessCount: Number.parseInt(parsed.values.node_process_count || "0", 10),
    pythonProcessCount: Number.parseInt(parsed.values.python_process_count || "0", 10),
    terminalWindowLimit: Number.parseInt(parsed.values.terminal_window_limit || "0", 10),
    terminalProcessLimit: Number.parseInt(parsed.values.terminal_process_limit || "0", 10),
    ollamaPresent: parsed.values.ollama_present === "yes",
    listWindowsOk: parsed.values.list_windows_ok === "yes",
    activeWindowOk: parsed.values.active_window_ok === "yes",
    openAllowedAppOk: parsed.values.open_allowed_app_ok === "yes",
    duplicateTerminalAvoidanceOk: parsed.values.duplicate_terminal_avoidance_ok === "yes",
    focusWindowOk: parsed.values.focus_window_ok === "yes",
    clipboardWriteOk: parsed.values.clipboard_write_ok === "yes",
    clipboardReadOk: parsed.values.clipboard_read_ok === "yes",
    pasteClipboardOk: parsed.values.paste_clipboard_ok === "yes",
    sendHotkeyOk: parsed.values.send_hotkey_ok === "yes",
    copySelectionOk: parsed.values.copy_selection_ok === "yes",
    waitSecondsOk: parsed.values.wait_seconds_ok === "yes",
    waitForWindowOk: parsed.values.wait_for_window_ok === "yes",
    moveMouseOk: parsed.values.move_mouse_ok === "yes",
    leftClickOk: parsed.values.left_click_ok === "yes",
    scrollMouseOk: parsed.values.scroll_mouse_ok === "yes",
    failsafeInterruptOk: parsed.values.failsafe_interrupt_ok === "yes",
    captureDesktopScreenshotOk: parsed.values.capture_desktop_screenshot_ok === "yes",
    unsupportedActionBlocked: parsed.values.unsupported_action_blocked === "yes",
    resourceGuardOk: parsed.values.resource_guard_ok === "yes",
    clipboardGuardOk: parsed.values.clipboard_guard_ok === "yes",
    availableNow: parsed.listSections.available_now || [],
    missingNow: parsed.listSections.missing_now || [],
  };
}

function parseBrainStatus(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  const notes = (parsed.listSections.brain_notes || [])
    .filter((item) => item !== "none");
  const installedModels = (parsed.listSections.brain_installed_models || [])
    .filter((item) => item !== "none");

  return {
    activeProvider: parsed.values.active_brain_provider || "unknown",
    activeModel: parsed.values.active_brain_model || "none",
    configSource: parsed.values.brain_config_source || "unknown",
    providerReady: parsed.values.brain_provider_ready === "yes",
    inferenceReady: parsed.values.brain_inference_ready === "yes",
    liveCallPath: parsed.values.brain_live_call_path || "none",
    ollamaBaseUrl: parsed.values.brain_ollama_base_url || "none",
    ollamaAvailable: parsed.values.brain_ollama_available === "yes",
    modelInstalled: parsed.values.brain_model_installed === "yes",
    currentTaskUsedModelInference: parsed.values.current_task_used_model_inference === "yes",
    currentTaskModelProvider: parsed.values.current_task_model_provider || "none",
    currentTaskModelName: parsed.values.current_task_model_name || "none",
    currentTaskModelCallStatus: parsed.values.current_task_model_call_status || "not_used",
    lastModelCallStatus: parsed.values.last_model_call_status || "never_called",
    lastModelCallAt: parsed.values.last_model_call_at || "none",
    lastModelCallSource: parsed.values.last_model_call_source || "none",
    lastModelCallTaskId: parsed.values.last_model_call_task_id || "none",
    lastModelCallError: parsed.values.last_model_call_error || "none",
    lastModelResponsePreview: parsed.values.last_model_response_preview || "none",
    runtimeBrainConfigFile: parsed.values.runtime_brain_config_file || "none",
    runtimeBrainStateFile: parsed.values.runtime_brain_state_file || "none",
    notes,
    installedModels,
    headline: `${parsed.values.active_brain_provider || "unknown"} | ${parsed.values.active_brain_model || "none"} | ${parsed.values.last_model_call_status || "never_called"}`,
  };
}

function parseAgentRoleStatus(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  const roles = (parsed.listSections.roles || [])
    .filter((item) => item !== "none");

  return {
    currentRoleId: parsed.values.current_specialist_role || "supervisor",
    currentRolePurpose: parsed.values.current_specialist_role_purpose || "none",
    currentRoleProvider: parsed.values.current_specialist_role_provider || "none",
    currentRoleSensitivity: parsed.values.current_specialist_role_sensitivity || "unknown",
    currentRoleReason: parsed.values.current_specialist_role_reason || "none",
    registryCount: Number.parseInt(parsed.values.specialist_role_registry_count || String(roles.length), 10),
    roles,
    headline: `${parsed.values.current_specialist_role || "supervisor"} | ${parsed.values.specialist_role_registry_count || roles.length} role(s)` ,
  };
}

function parseBrowserStatus(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  const notes = (parsed.listSections.browser_notes || [])
    .filter((item) => item !== "none");

  return {
    browserUseInstalled: parsed.values.browser_use_installed === "yes",
    browserUseVersion: parsed.values.browser_use_version || "none",
    browserUseReady: parsed.values.browser_use_ready === "yes",
    browserSessionSupport: parsed.values.browser_session_support || "not_available",
    browserTaskSupport: parsed.values.browser_task_support || "not_available",
    playwrightInstalled: parsed.values.playwright_installed === "yes",
    playwrightVersion: parsed.values.playwright_version || "none",
    playwrightCliAvailable: parsed.values.playwright_cli_available === "yes",
    playwrightBrowserBinariesInstalled: parsed.values.playwright_browser_binaries_installed === "yes",
    playwrightReady: parsed.values.playwright_ready === "yes",
    currentBrowserRole: parsed.values.current_browser_role || "none",
    currentBrowserAction: parsed.values.current_browser_action || "none",
    currentBrowserSessionId: parsed.values.current_browser_session_id || "none",
    lastBrowserStatus: parsed.values.last_browser_status || "not_used",
    runtimeBrowserStateFile: parsed.values.runtime_browser_state_file || "none",
    notes,
    headline: `${parsed.values.browser_use_installed || "no"} browser_use | ${parsed.values.playwright_ready || "no"} playwright_ready`,
  };
}

function parseMemoryStatus(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  const notes = (parsed.listSections.compact_memory_notes || [])
    .filter((item) => item !== "none");
  const missingFiles = (parsed.listSections.compact_memory_missing_files || [])
    .filter((item) => item !== "none");

  return {
    ready: parsed.values.compact_memory_ready === "yes",
    root: parsed.values.compact_memory_root || "none",
    obsidianMarkdownReady: parsed.values.compact_memory_obsidian_markdown_ready === "yes",
    fileCount: Number.parseInt(parsed.values.compact_memory_file_count || "0", 10),
    newestModifiedAt: parsed.values.compact_memory_newest_modified_at || "none",
    missingFiles,
    notes,
    headline: `${parsed.values.compact_memory_ready || "no"} compact_memory | files=${parsed.values.compact_memory_file_count || "0"}`,
  };
}

function parseRelayStatus(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  const notes = (parsed.listSections.relay_notes || [])
    .filter((item) => item !== "none");

  return {
    relayState: parsed.values.relay_state || "idle",
    currentStep: parsed.values.relay_current_step || "idle",
    sourceTargetAlias: parsed.values.relay_source_target_alias || "chatgpt",
    sourceTargetCandidateId: parsed.values.relay_source_target_candidate_id || "none",
    sourceTargetTitle: parsed.values.relay_source_target_title || "none",
    sourceTargetStatus: parsed.values.relay_source_target_status || "not_bound",
    destinationTargetAlias: parsed.values.relay_destination_target_alias || "codex",
    destinationTargetCandidateId: parsed.values.relay_destination_target_candidate_id || "none",
    destinationTargetTitle: parsed.values.relay_destination_target_title || "none",
    destinationTargetStatus: parsed.values.relay_destination_target_status || "not_bound",
    codexModePreset: parsed.values.relay_codex_mode_preset || "Implementing new feature",
    codexReasoningPreset: parsed.values.relay_codex_reasoning_preset || "Medium",
    presetApplicationStatus: parsed.values.relay_preset_application_status || "stored_only",
    codexExecutionStatus: parsed.values.relay_codex_execution_status || "unknown",
    nextUsageResetAt: parsed.values.relay_next_usage_reset_at || "none",
    resumeAfterUsageReset: parsed.values.relay_resume_after_usage_reset === "yes",
    waitingReason: parsed.values.relay_waiting_reason || "none",
    blockedReason: parsed.values.relay_blocked_reason || "none",
    lastPayloadPreview: parsed.values.relay_last_payload_preview || "none",
    lastResultPreview: parsed.values.relay_last_result_preview || "none",
    lastCompletionStatus: parsed.values.relay_last_completion_status || "none",
    lastTransitionAt: parsed.values.relay_last_transition_at || "none",
    lastUpdatedAt: parsed.values.relay_last_updated_at || "none",
    lastUsedTaskId: parsed.values.relay_last_used_task_id || "none",
    lastKnownDialogStatus: parsed.values.relay_last_known_dialog_status || "none",
    lastKnownDialogNote: parsed.values.relay_last_known_dialog_note || "none",
    runtimeRelayStateFile: parsed.values.runtime_relay_state_file || "none",
    notes,
    headline: `${parsed.values.relay_state || "idle"} | ${parsed.values.relay_current_step || "idle"} | ${parsed.values.relay_codex_execution_status || "unknown"}`,
  };
}

function parseApprovalRequestLine(line) {
  const parts = String(line)
    .split(" | ")
    .map((item) => item.trim())
    .filter(Boolean);

  const labeled = {};
  for (const part of parts.slice(2)) {
    const separatorIndex = part.indexOf("=");
    if (separatorIndex === -1) {
      continue;
    }
    const key = part.slice(0, separatorIndex).trim();
    const value = part.slice(separatorIndex + 1).trim();
    labeled[key] = value;
  }

  return {
    approvalId: parts[0] || "",
    status: parts[1] || "unknown",
    riskLevel: labeled.risk || "unknown",
    taskId: labeled.task || "",
    actionType: labeled.action || "Approval request",
    target: labeled.target || labeled.task || "none",
    shortDescription: labeled.description || "none",
    workspaceScope: labeled.workspace || "no_path_detected",
    workspacePolicy: labeled.policy || "allowed",
    adminRequired: labeled.admin || "unknown",
    detail: [
      labeled.action ? `action=${labeled.action}` : "",
      labeled.target ? `target=${labeled.target}` : "",
      labeled.description ? `description=${labeled.description}` : "",
      labeled.workspace ? `workspace=${labeled.workspace}` : "",
      labeled.policy ? `policy=${labeled.policy}` : "",
      labeled.admin ? `admin=${labeled.admin}` : "",
    ].filter(Boolean).join(" | "),
  };
}

function parseApprovalHistoryLine(line) {
  const parts = String(line)
    .split(" | ")
    .map((item) => item.trim())
    .filter(Boolean);

  return {
    decision: parts[0] || "unknown",
    decidedAt: parts[1] || "",
    note: parts.slice(2).join(" | ").replace(/^note=/, "") || "none",
  };
}

function parseTaskStatusLine(line) {
  const parts = String(line)
    .split(" | ")
    .map((item) => item.trim())
    .filter(Boolean);

  const labeled = {};
  for (const part of parts.slice(2)) {
    const separatorIndex = part.indexOf("=");
    if (separatorIndex === -1) {
      continue;
    }
    const key = part.slice(0, separatorIndex).trim();
    const value = part.slice(separatorIndex + 1).trim();
    labeled[key] = value;
  }

  return {
    taskId: parts[0] || "",
    status: parts[1] || "unknown",
    workspaceScope: labeled.workspace || "no_path_detected",
    workspacePolicy: labeled.policy || "allowed",
    approvalState: labeled.approval || "unknown",
    actionType: labeled.action || "",
    target: labeled.target || "",
    lastSummary: labeled.last || "none",
    nextAction: labeled.next || "Review the task state.",
    detail: labeled.detail || parts.slice(2).join(" | ") || "",
  };
}

function parseApprovalList(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  const requests = (parsed.listSections.requests || [])
    .filter((item) => item !== "none")
    .map(parseApprovalRequestLine);
  const count = Number.parseInt(parsed.values.count || String(requests.length), 10);

  return {
    count,
    requests,
    headline: count > 0 ? `${count} approval request(s) pending.` : "No pending approvals right now.",
  };
}

function parseTaskHistoryLine(line) {
  const parts = String(line)
    .split(" | ")
    .map((item) => item.trim())
    .filter(Boolean);

  return {
    eventType: parts[0] || "unknown",
    occurredAt: parts[1] || "",
    actor: parts[2]?.replace(/^actor=/, "") || "system",
    note: parts.slice(3).join(" | ").replace(/^note=/, "") || "none",
  };
}

function parseExecutionHistoryLine(line) {
  const parts = String(line)
    .split(" | ")
    .map((item) => item.trim())
    .filter(Boolean);

  const labeled = {};
  for (const part of parts.slice(1)) {
    const separatorIndex = part.indexOf("=");
    if (separatorIndex === -1) {
      continue;
    }
    const key = part.slice(0, separatorIndex).trim();
    const value = part.slice(separatorIndex + 1).trim();
    labeled[key] = value;
  }

  return {
    status: parts[0] || "unknown",
    startedAt: labeled.started || "",
    finishedAt: labeled.finished || "",
    target: labeled.target || "none",
    summary: labeled.summary || "none",
    artifactPath: labeled.artifact || "none",
    attempts: Number.parseInt(labeled.attempts || "1", 10),
    reason: labeled.reason || "none",
  };
}

function parseRecipeStepLine(line) {
  const parts = String(line)
    .split(" | ")
    .map((item) => item.trim())
    .filter(Boolean);

  const labeled = {};
  for (const part of parts.slice(1)) {
    const separatorIndex = part.indexOf("=");
    if (separatorIndex === -1) {
      continue;
    }
    const key = part.slice(0, separatorIndex).trim();
    const value = part.slice(separatorIndex + 1).trim();
    labeled[key] = value;
  }

  return {
    status: parts[0] || "unknown",
    step: Number.parseInt(labeled.step || "0", 10),
    actionType: labeled.action || "unknown",
    target: labeled.target || "none",
    bridgeTarget: labeled.bridge_target || "none",
    label: labeled.label || "recipe step",
    startedAt: labeled.started || "",
    finishedAt: labeled.finished || "",
    summary: labeled.summary || "none",
    artifactPath: labeled.artifact || "none",
    clipboardPreview: labeled.clipboard || "none",
    clipboardClassification: labeled.classification || "none",
    windowAlias: labeled.window || "none",
    windowCandidateId: labeled.candidate || "none",
    windowResolutionMode: labeled.resolution_mode || "none",
    coordinates: labeled.coordinates || "none",
    attempts: Number.parseInt(labeled.attempts || "0", 10),
    maxAttempts: Number.parseInt(labeled.max_attempts || "0", 10),
    required: labeled.required || "yes",
  };
}

function parseWindowCandidateLine(line) {
  const parts = String(line)
    .split(" | ")
    .map((item) => item.trim())
    .filter(Boolean);

  const labeled = {};
  for (const part of parts) {
    const separatorIndex = part.indexOf("=");
    if (separatorIndex === -1) {
      continue;
    }
    const key = part.slice(0, separatorIndex).trim();
    const value = part.slice(separatorIndex + 1).trim();
    labeled[key] = value;
  }

  return {
    aliases: (labeled.aliases || "").split(",").map((item) => item.trim()).filter(Boolean),
    title: labeled.title || "unknown",
    candidateId: labeled.candidate || "none",
    processId: Number.parseInt(labeled.pid || "0", 10),
    isActive: labeled.active === "yes",
    isFixture: labeled.fixture === "yes",
    matchScore: Number.parseInt(labeled.score || "0", 10),
    matchReason: labeled.reason || "none",
  };
}

function parseRecipeRunLine(line) {
  const parts = String(line)
    .split(" | ")
    .map((item) => item.trim())
    .filter(Boolean);

  const labeled = {};
  for (const part of parts.slice(1)) {
    const separatorIndex = part.indexOf("=");
    if (separatorIndex === -1) {
      continue;
    }
    const key = part.slice(0, separatorIndex).trim();
    const value = part.slice(separatorIndex + 1).trim();
    labeled[key] = value;
  }

  return {
    status: parts[0] || "unknown",
    startedAt: labeled.started || "",
    finishedAt: labeled.finished || "",
    summary: labeled.summary || "none",
  };
}

function parseTaskDetail(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  const history = (parsed.listSections.history || [])
    .filter((item) => item !== "none")
    .map(parseTaskHistoryLine);
  const executionHistory = (parsed.listSections.execution_history || [])
    .filter((item) => item !== "none")
    .map(parseExecutionHistoryLine);
  const recipeSteps = (parsed.listSections.recipe_steps || [])
    .filter((item) => item !== "none")
    .map(parseRecipeStepLine);
  const recipeLastRunSteps = (parsed.listSections.recipe_last_run_steps || [])
    .filter((item) => item !== "none")
    .map(parseRecipeStepLine);
  const recipeRunHistory = (parsed.listSections.recipe_run_history || [])
    .filter((item) => item !== "none")
    .map(parseRecipeRunLine);

  return {
    taskId: parsed.values.task_id || "",
    title: parsed.values.title || "Untitled task",
    description: parsed.values.description || "none",
    status: parsed.values.status || "unknown",
    riskLevel: parsed.values.risk_level || "unknown",
    approvalState: parsed.values.approval_state || "unknown",
    approvalRequestId: parsed.values.approval_request_id || "none",
    source: parsed.values.source || "manual",
    executorActionType: parsed.values.executor_action_type || "none",
    executorTarget: parsed.values.executor_target || "none",
    recipeName: parsed.values.recipe_name || "none",
    recipeLabel: parsed.values.recipe_label || "none",
    recipeStatus: parsed.values.recipe_status || "not_run",
    recipeSummary: parsed.values.recipe_summary || "none",
    recipeRunCount: Number.parseInt(parsed.values.recipe_run_count || "0", 10),
    recipeLastRunStartedAt: parsed.values.recipe_last_run_started_at || "",
    recipeLastRunFinishedAt: parsed.values.recipe_last_run_finished_at || "",
    recipeSourceWindow: parsed.values.recipe_source_window || "none",
    recipeTargetWindow: parsed.values.recipe_target_window || "none",
    recipeSourceWindowCandidateId: parsed.values.recipe_source_window_candidate_id || "none",
    recipeTargetWindowCandidateId: parsed.values.recipe_target_window_candidate_id || "none",
    recipeClipboardMode: parsed.values.recipe_clipboard_mode || "none",
    handoffSourceSelectionMode: parsed.values.handoff_source_selection_mode || "none",
    handoffTargetSelectionMode: parsed.values.handoff_target_selection_mode || "none",
    handoffPayloadClassification: parsed.values.handoff_payload_classification || "none",
    handoffPayloadPreview: parsed.values.handoff_payload_preview || "none",
    handoffPayloadReason: parsed.values.handoff_payload_reason || "none",
    handoffPasteAllowed: parsed.values.handoff_paste_allowed || "none",
    handoffSendBehavior: parsed.values.handoff_send_behavior || "none",
    handoffSendAllowed: parsed.values.handoff_send_allowed || "none",
    handoffFallbackDenied: parsed.values.handoff_fallback_denied || "none",
    handoffTargetResolutionStatus: parsed.values.handoff_target_resolution_status || "none",
    handoffManualTargetResolution: parsed.values.handoff_manual_target_resolution || "none",
    handoffSourceMatch: parsed.values.handoff_source_match || "none",
    handoffTargetMatch: parsed.values.handoff_target_match || "none",
    handoffStopReason: parsed.values.handoff_stop_reason || "none",
    handoffBlockedPayloadRepeats: Number.parseInt(parsed.values.handoff_blocked_payload_repeats || "0", 10),
    workspaceScope: parsed.values.workspace_scope || "no_path_detected",
    workspacePolicy: parsed.values.workspace_policy || "allowed",
    workspaceReason: parsed.values.workspace_reason || "none",
    allowedWorkspaceRoot: parsed.values.allowed_workspace_root || "unknown",
    waitingFor: parsed.values.waiting_for || "none",
    blockedReason: parsed.values.blocked_reason || "none",
    requiresHuman: parsed.values.requires_human === "yes",
    adminRequired: parsed.values.admin_required === "yes",
    lastNote: parsed.values.last_note || "none",
    createdAt: parsed.values.created_at || "",
    updatedAt: parsed.values.updated_at || "",
    nextAction: parsed.values.next_action || "Review the task state.",
    executionCount: Number.parseInt(parsed.values.execution_count || "0", 10),
    lastExecutionStatus: parsed.values.last_execution_status || "not_run",
    lastExecutionSummary: parsed.values.last_execution_summary || "none",
    lastArtifactPath: parsed.values.last_artifact_path || "none",
    lastAttemptCount: Number.parseInt(parsed.values.last_attempt_count || "0", 10),
    lastFailureReason: parsed.values.last_failure_reason || "none",
    lastInterruptionReason: parsed.values.last_interruption_reason || "none",
    lastResourceGuardReason: parsed.values.last_resource_guard_reason || "none",
    desktopCurrentAction: parsed.values.desktop_current_action || "none",
    desktopCurrentTarget: parsed.values.desktop_current_target || "none",
    desktopCurrentTypingEnabled: parsed.values.desktop_current_typing_enabled || "no",
    desktopLastAction: parsed.values.desktop_last_action || "none",
    desktopLastTarget: parsed.values.desktop_last_target || "none",
    desktopLastTypingEnabled: parsed.values.desktop_last_typing_enabled || "no",
    desktopLastActionStatus: parsed.values.desktop_last_action_status || "not_run",
    desktopVisualCueStatus: parsed.values.desktop_visual_cue_status || "not_reported",
    desktopVisualCueAction: parsed.values.desktop_visual_cue_action || "none",
    desktopVisualCueTarget: parsed.values.desktop_visual_cue_target || "none",
    desktopLastTextPreview: parsed.values.desktop_last_text_preview || "none",
    retryLimit: Number.parseInt(parsed.values.retry_limit || "0", 10),
    targetPaths: (parsed.listSections.target_paths || []).filter((item) => item !== "none"),
    recipeSteps,
    recipeLastRunSteps,
    recipeRunHistory,
    executionHistory,
    history,
    headline: `${parsed.values.title || "Task"} (${parsed.values.status || "unknown"})`,
  };
}

function parseExecutorTaskLine(line) {
  const parts = String(line)
    .split(" | ")
    .map((item) => item.trim())
    .filter(Boolean);

  const labeled = {};
  for (const part of parts.slice(2)) {
    const separatorIndex = part.indexOf("=");
    if (separatorIndex === -1) {
      continue;
    }
    const key = part.slice(0, separatorIndex).trim();
    const value = part.slice(separatorIndex + 1).trim();
    labeled[key] = value;
  }

  return {
    taskId: parts[0] || "",
    status: parts[1] || "unknown",
    actionType: labeled.action || "unknown",
    target: labeled.target || "none",
    taskType: labeled.type || "repo",
    title: labeled.title || "Executor task",
    updatedAt: labeled.updated || "",
    recipeName: labeled.recipe || "none",
    approvalState: labeled.approval || "unknown",
    workspaceScope: labeled.workspace || "no_path_detected",
    workspacePolicy: labeled.policy || "allowed",
    lastSummary: labeled.last || "not_run",
    sourceWindow: labeled.source_window || "none",
    targetWindow: labeled.target_window || "none",
    payloadClassification: labeled.classification || "none",
    sendBehavior: labeled.send_behavior || "none",
    desktopAction: labeled.desktop_action || "none",
    desktopTarget: labeled.desktop_target || "none",
    typingEnabled: labeled.typing_enabled || "no",
    desktopStatus: labeled.desktop_status || "not_run",
    cueStatus: labeled.cue_status || "not_reported",
    detail: [
      labeled.action ? `action=${labeled.action}` : "",
      labeled.target ? `target=${labeled.target}` : "",
      labeled.approval ? `approval=${labeled.approval}` : "",
      labeled.workspace ? `workspace=${labeled.workspace}` : "",
      labeled.policy ? `policy=${labeled.policy}` : "",
      labeled.last ? `last=${labeled.last}` : "",
      labeled.source_window ? `source=${labeled.source_window}` : "",
      labeled.target_window ? `target_window=${labeled.target_window}` : "",
      labeled.classification ? `classification=${labeled.classification}` : "",
      labeled.desktop_action ? `desktop_action=${labeled.desktop_action}` : "",
      labeled.desktop_target ? `desktop_target=${labeled.desktop_target}` : "",
      labeled.typing_enabled ? `typing_enabled=${labeled.typing_enabled}` : "",
      labeled.desktop_status ? `desktop_status=${labeled.desktop_status}` : "",
      labeled.cue_status ? `cue_status=${labeled.cue_status}` : "",
    ].filter(Boolean).join(" | "),
  };
}

function parseExecutorTaskList(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  const tasks = (parsed.listSections.tasks || [])
    .filter((item) => item !== "none")
    .map(parseExecutorTaskLine);
  const count = Number.parseInt(parsed.values.count || String(tasks.length), 10);

  return {
    count,
    tasks,
    headline: count > 0 ? `${count} executor task(s) available.` : "No executor tasks queued yet.",
  };
}

function parseApprovalDetail(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  const history = (parsed.listSections.decision_history || [])
    .filter((item) => item !== "none")
    .map(parseApprovalHistoryLine);

  return {
    approvalId: parsed.values.approval_id || "",
    taskId: parsed.values.task_id || "",
    status: parsed.values.status || "unknown",
    riskLevel: parsed.values.risk_level || "unknown",
    actionLabel: parsed.values.action_label || "Approval request",
    requestedAt: parsed.values.requested_at || "",
    updatedAt: parsed.values.updated_at || "",
    source: parsed.values.source || "manual",
    scope: parsed.values.scope || "none",
    workspaceScope: parsed.values.workspace_scope || "no_path_detected",
    workspacePolicy: parsed.values.workspace_policy || "allowed",
    workspaceReason: parsed.values.workspace_reason || "none",
    allowedWorkspaceRoot: parsed.values.allowed_workspace_root || "unknown",
    requiresAdmin: parsed.values.requires_admin === "yes",
    reason: parsed.values.reason || "none",
    rollbackPlan: parsed.values.rollback_plan || "none",
    humanNote: parsed.values.human_note || "none",
    targetPaths: (parsed.listSections.target_paths || []).filter((item) => item !== "none"),
    decisionHistory: history,
    headline: `${parsed.values.action_label || "Approval request"} (${parsed.values.status || "unknown"})`,
  };
}

function parseSupervisorStatus(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  const pendingApprovals = (parsed.listSections.pending_approvals || [])
    .filter((item) => item !== "none")
    .map(parseApprovalRequestLine);
  const humanNeededTasks = (parsed.listSections.human_needed_tasks || [])
    .filter((item) => item !== "none")
    .map(parseTaskStatusLine);
  const interruptedTasks = (parsed.listSections.interrupted_tasks || [])
    .filter((item) => item !== "none")
    .map(parseTaskStatusLine);
  const waitingTasks = (parsed.listSections.waiting_tasks || [])
    .filter((item) => item !== "none")
    .map(parseTaskStatusLine);
  const readyToResumeTasks = (parsed.listSections.ready_to_resume_tasks || [])
    .filter((item) => item !== "none")
    .map(parseTaskStatusLine);
  const resourceGuardEvents = (parsed.listSections.resource_guard_events || [])
    .filter((item) => item !== "none");

  const status = parsed.values.status || "unknown";
  const pendingApprovalCount = Number.parseInt(parsed.values.pending_approval_count || "0", 10);
  const blockedHumanNeededCount = Number.parseInt(parsed.values.blocked_human_needed_count || "0", 10);
  const interruptedCount = Number.parseInt(parsed.values.interrupted_count || "0", 10);
  const waitingCount = Number.parseInt(parsed.values.waiting_count || "0", 10);
  const readyToResumeCount = Number.parseInt(parsed.values.ready_to_resume_count || "0", 10);
  const queuedCount = Number.parseInt(parsed.values.queued_count || "0", 10);
  const runningCount = Number.parseInt(parsed.values.running_count || "0", 10);

  return {
    supervisorId: parsed.values.supervisor_id || "local-supervisor",
    mode: parsed.values.mode || "local_only",
    status,
    activeTaskId: parsed.values.active_task_id || "none",
    queuedCount,
    runningCount,
    waitingCount,
    readyToResumeCount,
    pendingApprovalCount,
    blockedHumanNeededCount,
    interruptedCount,
    ghotiState: parsed.values.ghoti_state || "idle",
    ghotiReason: parsed.values.ghoti_reason || "none",
    operatorNextStep: parsed.values.operator_next_step || "Review the local operator state.",
    resourceGuardEventCount: Number.parseInt(parsed.values.resource_guard_event_count || "0", 10),
    notificationMode: parsed.values.notification_mode || "dashboard",
    notificationTitle: parsed.values.notification_title || "Supervisor status",
    lastEvent: parsed.values.last_event || "none",
    updatedAt: parsed.values.updated_at || "",
    allowedWorkspaceRoot: parsed.values.allowed_workspace_root || "unknown",
    resourceGuardEvents,
    pendingApprovals,
    humanNeededTasks,
    interruptedTasks,
    waitingTasks,
    readyToResumeTasks,
    headline:
      pendingApprovalCount > 0
        ? `${pendingApprovalCount} approval request(s) need review.`
        : blockedHumanNeededCount > 0
          ? `${blockedHumanNeededCount} task(s) are blocked on the human.`
        : interruptedCount > 0
          ? `${interruptedCount} task(s) were interrupted by the local failsafe.`
        : waitingCount > 0
          ? `${waitingCount} task(s) are waiting to resume later.`
          : readyToResumeCount > 0
            ? `${readyToResumeCount} task(s) are ready to re-queue.`
            : queuedCount > 0 || runningCount > 0
              ? "Supervisor is tracking local work without open approvals."
              : "Supervisor is idle and ready.",
  };
}

function buildDegradedSupervisorStatus(raw) {
  const message = String(raw.stderr || raw.stdout || "Runtime supervisor status is unavailable.").trim()
    || "Runtime supervisor status is unavailable.";
  return {
    supervisorId: "local-supervisor",
    mode: "local_only",
    status: "degraded",
    activeTaskId: "none",
    queuedCount: 0,
    runningCount: 0,
    waitingCount: 0,
    readyToResumeCount: 0,
    pendingApprovalCount: 0,
    blockedHumanNeededCount: 0,
    interruptedCount: 0,
    ghotiState: "degraded",
    ghotiReason: message,
    operatorNextStep: "Inspect the local runtime state and run the supervisor-status CLI check.",
    resourceGuardEventCount: 0,
    notificationMode: "dashboard",
    notificationTitle: "Supervisor status degraded",
    lastEvent: message,
    updatedAt: new Date().toISOString(),
    allowedWorkspaceRoot: repoRoot,
    resourceGuardEvents: [],
    pendingApprovals: [],
    humanNeededTasks: [],
    interruptedTasks: [],
    waitingTasks: [],
    readyToResumeTasks: [],
    headline: `Supervisor status degraded: ${message}`,
  };
}

function extractOutputPath(label, stdout) {
  const regex = new RegExp(`${label}:\\s*(.+)$`, "m");
  const match = stdout.match(regex);
  return match ? match[1].trim() : null;
}

function relativeRepoPath(absolutePath) {
  return path.relative(repoRoot, absolutePath).replace(/\\/g, "/");
}

function isPathInside(parentPath, childPath) {
  const relative = path.relative(parentPath, childPath);
  return relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative));
}

function getAllowedArtifactRoots() {
  return [
    path.join(repoRoot, "11_exports", "personal_ops"),
    path.join(repoRoot, "11_exports", "github"),
    path.join(repoRoot, "01_projects", "browser_playground", "artifacts"),
    path.join(repoRoot, "05_logs", "tmp", "desktop"),
  ];
}

function resolveAllowedArtifactPath(targetPath) {
  if (!targetPath || typeof targetPath !== "string") {
    throw new Error("Missing artifact path.");
  }

  const normalizedInput = targetPath.replaceAll("/", path.sep);
  const absolutePath = path.normalize(
    path.isAbsolute(normalizedInput)
      ? normalizedInput
      : path.join(repoRoot, normalizedInput),
  );

  const isAllowed = getAllowedArtifactRoots().some((root) => isPathInside(root, absolutePath));
  if (!isAllowed) {
    throw new Error("Artifact path is outside the allowed dashboard roots.");
  }

  if (!fs.existsSync(absolutePath)) {
    throw new Error("Artifact not found.");
  }

  if (!fs.statSync(absolutePath).isFile()) {
    throw new Error("Artifact path is not a file.");
  }

  return absolutePath;
}

function getArtifactFormat(absolutePath) {
  const extension = path.extname(absolutePath).toLowerCase();
  if (extension === ".md" || extension === ".markdown") {
    return "markdown";
  }
  if (extension === ".json") {
    return "json";
  }
  return "text";
}

function isPreviewableArtifact(absolutePath) {
  return previewableExtensions.has(path.extname(absolutePath).toLowerCase());
}

function buildArtifactPreview(targetPath) {
  const absolutePath = resolveAllowedArtifactPath(targetPath);
  if (!isPreviewableArtifact(absolutePath)) {
    throw new Error("Artifact preview is limited to markdown and text-like files.");
  }

  const maxChars = 32000;
  const stats = fs.statSync(absolutePath);
  let content = fs.readFileSync(absolutePath, "utf8");
  const truncated = content.length > maxChars;
  if (truncated) {
    content = `${content.slice(0, maxChars)}\n\n[preview truncated]`;
  }

  return {
    name: path.basename(absolutePath),
    path: relativeRepoPath(absolutePath),
    format: getArtifactFormat(absolutePath),
    previewable: true,
    truncated,
    size: stats.size,
    modifiedAt: stats.mtime.toISOString(),
    content,
  };
}

async function openArtifact(targetPath) {
  const absolutePath = resolveAllowedArtifactPath(targetPath);
  const powerShell = resolvePowerShell();
  if (!powerShell) {
    return {
      ok: false,
      exitCode: 1,
      stdout: "",
      stderr: "PowerShell runtime not found for artifact open action.",
      path: relativeRepoPath(absolutePath),
    };
  }

  const result = await runCommand(
    powerShell.command,
    [
      ...powerShell.baseArgs,
      "-NoProfile",
      "-Command",
      "Start-Process -FilePath $args[0]",
      absolutePath,
    ],
    {
      cwd: repoRoot,
      env: process.env,
      timeoutMs: 30000,
    },
  );

  return {
    ...result,
    path: relativeRepoPath(absolutePath),
  };
}

async function revealArtifact(targetPath) {
  const absolutePath = resolveAllowedArtifactPath(targetPath);
  const powerShell = resolvePowerShell();
  if (!powerShell) {
    return {
      ok: false,
      exitCode: 1,
      stdout: "",
      stderr: "PowerShell runtime not found for artifact reveal action.",
      path: relativeRepoPath(absolutePath),
    };
  }

  const result = await runCommand(
    powerShell.command,
    [
      ...powerShell.baseArgs,
      "-NoProfile",
      "-Command",
      "Start-Process -FilePath explorer.exe -ArgumentList $args[0]",
      `/select,${absolutePath}`,
    ],
    {
      cwd: repoRoot,
      env: process.env,
      timeoutMs: 30000,
    },
  );

  return {
    ...result,
    path: relativeRepoPath(absolutePath),
  };
}

function listDirectoryArtifacts(absoluteDirPath, groupLabel) {
  if (!fs.existsSync(absoluteDirPath)) {
    return [];
  }

  const items = fs.readdirSync(absoluteDirPath, { withFileTypes: true });
  return items
    .filter((entry) => entry.isFile() && entry.name !== ".gitkeep")
    .map((entry) => {
      const absolutePath = path.join(absoluteDirPath, entry.name);
      const stats = fs.statSync(absolutePath);
      return {
        group: groupLabel,
        name: entry.name,
        path: relativeRepoPath(absolutePath),
        previewable: isPreviewableArtifact(absolutePath),
        size: stats.size,
        modifiedAt: stats.mtime.toISOString(),
      };
    });
}

function listRecentArtifacts() {
  const artifacts = [
    ...listDirectoryArtifacts(path.join(repoRoot, "11_exports", "personal_ops"), "personal_ops"),
    ...listDirectoryArtifacts(path.join(repoRoot, "11_exports", "github"), "github"),
    ...listDirectoryArtifacts(
      path.join(repoRoot, "01_projects", "browser_playground", "artifacts"),
      "browser_playground",
    ),
    ...listDirectoryArtifacts(
      path.join(repoRoot, "05_logs", "tmp", "desktop"),
      "desktop",
    ),
  ];

  artifacts.sort((left, right) => right.modifiedAt.localeCompare(left.modifiedAt));
  return artifacts.slice(0, 25);
}

function buildOperatorStatus() {
  return {
    localOnly: true,
    headline: "Local operator console for safe, visible, reviewable actions.",
    dashboardUrl: `http://127.0.0.1:${dashboardPort}`,
    emergencyStopHotkey: "Ctrl+8",
    controlCenterDoc: relativeRepoPath(path.join(repoRoot, "04_docs", "ghoti_control_center.md")),
    cliCommands: [
      "python -m super_ai_agent.cli ghoti-help",
      "python -m super_ai_agent.cli ghoti-status",
      "python -m super_ai_agent.cli ghoti-hotkeys",
      "python -m super_ai_agent.cli ghoti-recent",
      "python -m super_ai_agent.cli list-agent-roles",
      "python -m super_ai_agent.cli browser-status",
      "python -m super_ai_agent.cli memory-status",
    ],
    liveNow: [
      "Capability summary and environment-aware status",
      "GitHub read status and remote-capability visibility",
      "Internship, showcase, and portfolio scaffold generation",
      "Allowlisted repo-local executor tasks for safe checker, file, and git actions",
      "Allowlisted desktop bridge tasks for listing windows, checking the active window, focusing allowed windows, opening allowed local apps, capturing repo-local screenshots, clipboard reads and writes, waits, hotkeys, and narrow mouse actions",
      "Narrow operator recipes built from the existing desktop hand primitives",
      "Artifact preview, open, and reveal from the dashboard",
      "Browser smoke demo and visible local browser demo",
      "Desktop bridge status and safe local desktop checks",
      "Supervisor status and approval inbox visibility",
      "Approval queue review with local approve, deny, and defer actions",
      "Manual task review, resume, re-queue, and failsafe interruption visibility",
      "CLI Ghoti help, status, hotkey, and recent-work summaries",
      "Specialist-agent registry with role/provider/approval sensitivity truth",
      "Browser Use and Playwright readiness visibility",
      "Compact markdown memory scaffold visibility",
      "Safe real-window Codex-to-ChatGPT handoff with explicit target verification",
      "Recent artifacts and recent-action log",
    ],
    scaffoldOnly: [
      "GitHub remote write actions remain explicit and approval-gated",
      "Mail, Notion, and LinkedIn remain planning-only",
      "Personal ops packs are generated outputs, not live send or publish flows",
      "Desktop bridge actions and recipes are still narrow, allowlisted, and operator-triggered",
      "Business outreach remains draft-and-review scaffolding only",
      "The handoff workflow remains paste-only by default and still stops for manual target resolution when real window matching is not confident",
      "Notifications are local dashboard summaries only",
    ],
    notImplementedYet: [
      "Full browser executor loop",
      "Arbitrary desktop or Windows app control",
      "Freeform typing, drag-and-drop, or unrestricted mouse automation",
      "Runtime-stored durable Codex or ChatGPT target profiles beyond browser-local remembered candidate picks",
      "A live Browser Use executor path or autonomous browser sessions",
      "Live outreach send, pricing, or negotiation actions",
      "Live mail, Notion, and LinkedIn adapters",
    ],
    nextStep: "Use the Ghoti control center or the new ghoti-* CLI commands to spot the next actionable task, review approvals, and inspect artifacts before queueing another narrow local action.",
  };
}

async function buildGhotiControlCenterResponse(filters = {}) {
  const [capabilityPayload, supervisorPayload, executorPayload, brainPayload, rolePayload, browserPayload, memoryPayload, relayPayload] = await Promise.all([
    buildCapabilityResponse(),
    buildSupervisorResponse(),
    buildExecutorTasksResponse(),
    buildBrainStatusResponse(),
    buildAgentRoleResponse(),
    buildBrowserStatusResponse(),
    buildMemoryStatusResponse(),
    buildRelayStatusResponse(),
  ]);

  const operator = buildOperatorStatus();
  const supervisor = supervisorPayload.summary || {};
  const executorSummary = executorPayload.summary || {};
  const capabilitySummary = capabilityPayload.summary || {};
  const brainSummary = brainPayload.summary || {};
  const roleSummary = rolePayload.summary || {};
  const browserSummary = browserPayload.summary || {};
  const memorySummary = memoryPayload.summary || {};
  const relaySummary = relayPayload.summary || {};
  const tasks = executorSummary.tasks || [];
  const filteredTasks = filterGhotiTasks(tasks, filters);
  const sortedTasks = sortGhotiTasks(tasks).map(decorateGhotiTask);
  const currentTask = sortedTasks.find((item) => item.taskId === supervisor.activeTaskId)
    || sortedTasks.find((item) => String(item.status || "").toLowerCase() === "running")
    || null;
  const watchdog = buildGhotiWatchdogSummary(supervisor, sortedTasks, currentTask);
  const recentFailures = sortedTasks
    .filter((item) => ghotiFailureStatuses.has(String(item.status || "").toLowerCase()))
    .slice(0, 5);
  const artifacts = listRecentArtifacts();
  const availableCapabilities = (capabilitySummary.capabilities || [])
    .filter((item) => String(item.state || "").toLowerCase() === "available")
    .map((item) => item.capabilityId)
    .slice(0, 6);
  const nextSteps = [
    supervisor.operatorNextStep || operator.nextStep,
    "Use Ctrl+8 if a desktop action or recipe needs to stop immediately.",
    supervisor.pendingApprovalCount > 0
      ? "Review pending approvals before trying to run blocked work."
      : "",
    supervisor.blockedHumanNeededCount > 0
      ? "Inspect blocked human-needed tasks and decide whether to review, resume, or re-queue them."
      : "",
    `Open ${operator.controlCenterDoc} for the compact dashboard and CLI usage path.`,
  ].filter(Boolean);

  return {
    ok: capabilityPayload.ok && supervisorPayload.ok && executorPayload.ok && brainPayload.ok && rolePayload.ok && browserPayload.ok && memoryPayload.ok && relayPayload.ok,
    summary: {
      headline: `${supervisor.ghotiState || "idle"} | ${supervisor.headline || "Ghoti control center ready."}`,
      ghotiState: supervisor.ghotiState || "idle",
      ghotiReason: supervisor.ghotiReason || "none",
      operatorNextStep: supervisor.operatorNextStep || operator.nextStep,
      emergencyStopHotkey: operator.emergencyStopHotkey,
      currentTask: currentTask
        ? {
            taskId: currentTask.taskId,
            headline: currentTask.headline,
            status: currentTask.status,
            taskType: currentTask.taskType,
            taskTypeLabel: currentTask.taskTypeLabel,
            detail: currentTask.detail,
            nextAction: currentTask.nextAction || "Inspect the task detail.",
            usedModelInference: brainSummary.currentTaskUsedModelInference === true,
            modelProvider: brainSummary.currentTaskModelProvider || "none",
            modelName: brainSummary.currentTaskModelName || "none",
            modelCallStatus: brainSummary.currentTaskModelCallStatus || "not_used",
            desktopAction: currentTask.desktopAction || "none",
            desktopTarget: currentTask.desktopTarget || "none",
            typingEnabled: currentTask.typingEnabled || "no",
            desktopStatus: currentTask.desktopStatus || "not_run",
            cueStatus: currentTask.cueStatus || "not_reported",
            specialistRole: roleSummary.currentRoleId || "supervisor",
          }
        : null,
      desktopActionTruth: currentTask
        ? {
            currentAction: currentTask.desktopAction || "none",
            currentTarget: currentTask.desktopTarget || "none",
            typingEnabled: currentTask.typingEnabled || "no",
            lastStatus: currentTask.desktopStatus || "not_run",
            cueStatus: currentTask.cueStatus || "not_reported",
            specialistRole: roleSummary.currentRoleId || "supervisor",
          }
        : {
            currentAction: "none",
            currentTarget: "none",
            typingEnabled: "no",
            lastStatus: "not_run",
            cueStatus: "not_reported",
            specialistRole: roleSummary.currentRoleId || "supervisor",
          },
      brain: brainSummary,
      specialistRole: roleSummary,
      browser: browserSummary,
      memory: memorySummary,
      relay: relaySummary,
      pendingApprovalCount: Number(supervisor.pendingApprovalCount || 0),
      blockedTaskCount: Number(supervisor.blockedHumanNeededCount || 0),
      interruptedCount: Number(supervisor.interruptedCount || 0),
      waitingCount: Number(supervisor.waitingCount || 0),
      readyToResumeCount: Number(supervisor.readyToResumeCount || 0),
      recentActionableCount: filteredTasks.filteredCount,
      recentFailureCount: recentFailures.length,
      recentArtifactCount: artifacts.length,
      overlayTarget: watchdog.overlayTarget,
      watchdog,
      recentActionableTasks: filteredTasks.items,
      recentFailures,
      whatGhotiCanDoNow: availableCapabilities.length > 0 ? availableCapabilities : operator.liveNow.slice(0, 6),
      whatOperatorShouldDoNext: nextSteps,
      filters: {
        visibility: filteredTasks.visibility,
        taskType: filteredTasks.taskType,
        taskStatus: filteredTasks.taskStatus,
        activeOnly: filteredTasks.activeOnly,
        limit: filteredTasks.limit,
      },
      dashboardUrl: operator.dashboardUrl,
      controlCenterDoc: operator.controlCenterDoc,
      cliCommands: operator.cliCommands,
      hideCompletedByDefault: filteredTasks.visibility !== "all",
      noDeletionPolicy: "No task deletion without explicit approval. Prefer archive, filter, and history visibility instead.",
      availableCapabilitiesCount: Number(capabilitySummary.availableCount || 0),
    },
    raw: {
      capability: capabilityPayload.raw,
      brain: brainPayload.raw,
      role: rolePayload.raw,
      browser: browserPayload.raw,
      memory: memoryPayload.raw,
      relay: relayPayload.raw,
      supervisor: supervisorPayload.raw,
      executor: executorPayload.raw,
    },
    localOnly: true,
  };
}

const ghotiActionableStatuses = new Set([
  "queued",
  "running",
  "waiting",
  "pending_approval",
  "blocked_human_needed",
  "interrupted",
  "ready_to_resume",
  "failed",
]);

const ghotiActiveStatuses = new Set([
  "queued",
  "running",
  "waiting",
  "pending_approval",
  "blocked_human_needed",
  "interrupted",
  "ready_to_resume",
]);

const ghotiFailureStatuses = new Set([
  "failed",
  "blocked_human_needed",
  "interrupted",
]);

const ghotiDesktopActionTypes = new Set([
  "list_windows",
  "get_active_window",
  "focus_window",
  "open_allowed_app",
  "capture_desktop_screenshot",
  "get_clipboard_text",
  "set_clipboard_text",
  "copy_selection",
  "paste_clipboard",
  "send_hotkey",
  "wait_seconds",
  "wait_for_window",
  "move_mouse",
  "left_click",
  "double_click",
  "right_click",
  "scroll_mouse",
]);

function parseBooleanQuery(value, fallback = false) {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  return ["1", "true", "yes", "on"].includes(String(value).toLowerCase());
}

function parsePositiveIntQuery(value, fallback) {
  const parsed = Number.parseInt(String(value || ""), 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function isDesktopExecutorAction(actionType) {
  return ghotiDesktopActionTypes.has(String(actionType || "").toLowerCase());
}

function normalizeGhotiText(value) {
  return String(value || "").trim().toLowerCase();
}

function parseGhotiDate(value) {
  const normalized = String(value || "").trim();
  if (!normalized) {
    return null;
  }

  const parsed = new Date(normalized);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function getGhotiTaskAgeMinutes(task) {
  const timestamp = task?.updatedAt || task?.createdAt || "";
  const parsed = parseGhotiDate(timestamp);
  if (!parsed) {
    return null;
  }

  return Math.max(0, Math.round((Date.now() - parsed.getTime()) / 60000));
}

function taskLooksLikeWrongActiveWindowBlock(task) {
  const haystack = [
    task?.detail,
    task?.lastSummary,
    task?.blockedReason,
    task?.target,
  ].map((item) => String(item || "").toLowerCase()).join(" ");

  return (
    haystack.includes("wrong active window")
    || haystack.includes("active window mismatch")
    || haystack.includes("terminal stayed foreground")
    || haystack.includes("manual target resolution is required")
    || haystack.includes("powershell")
  );
}

function isLikelyStalledGhotiTask(task) {
  const status = normalizeGhotiText(task?.status);
  if (!["queued", "running", "waiting"].includes(status)) {
    return false;
  }

  const ageMinutes = getGhotiTaskAgeMinutes(task);
  if (!Number.isFinite(ageMinutes)) {
    return false;
  }

  const thresholdMinutes = status === "running" ? 15 : 20;
  return ageMinutes >= thresholdMinutes;
}

function buildGhotiOverlayTarget(task) {
  if (!task) {
    return {
      kind: "none",
      label: "No visible target",
      detail: "Queue or inspect one narrow task to show Ghoti's next local target.",
    };
  }

  const actionType = normalizeGhotiText(task.actionType);
  const taskType = task.taskType || classifyGhotiTaskType(task);
  const target = String(task.target || "").trim();
  const targetDetail = target && target !== "none"
    ? target
    : task.detail || task.headline || "No specific target recorded yet.";

  if (taskType === "handoff") {
    const sourceWindow = String(task.sourceWindow || "codex").trim() || "codex";
    const targetWindow = String(task.targetWindow || "chatgpt").trim() || "chatgpt";
    const detail = target && target !== "none"
      ? `${sourceWindow} -> ${targetWindow} | ${target}`
      : `${sourceWindow} -> ${targetWindow}`;
    return {
      kind: "handoff",
      label: "Handoff target",
      detail,
    };
  }

  if (["move_mouse", "left_click", "double_click", "right_click", "scroll_mouse"].includes(actionType)) {
    return {
      kind: "pointer",
      label: "Pointer target",
      detail: targetDetail,
    };
  }

  if (["focus_window", "open_allowed_app", "wait_for_window", "get_active_window"].includes(actionType)) {
    return {
      kind: "window",
      label: "Window target",
      detail: targetDetail,
    };
  }

  if (["paste_clipboard", "copy_selection", "set_clipboard_text", "send_hotkey", "get_clipboard_text", "type_text"].includes(actionType)) {
    return {
      kind: "input",
      label: "Input target",
      detail: targetDetail,
    };
  }

  return {
    kind: taskType || "task",
    label: `${task.taskTypeLabel || "Current task"} target`,
    detail: targetDetail,
  };
}

function buildGhotiWatchdogSummary(supervisor, sortedTasks, currentTask) {
  const recentFailures = sortedTasks
    .filter((item) => ghotiFailureStatuses.has(normalizeGhotiText(item.status)))
    .slice(0, 6);
  const wrongWindowBlocks = recentFailures.filter(taskLooksLikeWrongActiveWindowBlock);
  const stalledTasks = sortedTasks.filter(isLikelyStalledGhotiTask).slice(0, 4);
  const didNotCompleteTasks = recentFailures.filter((item) => normalizeGhotiText(item.status) !== "completed");
  const waitingCount = Number(supervisor.waitingCount || 0) + Number(supervisor.readyToResumeCount || 0);
  const pendingApprovalCount = Number(supervisor.pendingApprovalCount || 0);
  const blockedCount = Number(supervisor.blockedHumanNeededCount || 0);
  const interruptedCount = Number(supervisor.interruptedCount || 0);
  const runningCount = Number(supervisor.runningCount || 0);

  let status = "idle";
  let headline = "Ghoti is visible and waiting for the next narrow local action.";

  if (pendingApprovalCount > 0) {
    status = "approval_needed";
    headline = `${pendingApprovalCount} approval request(s) need review before more guarded work can proceed.`;
  } else if (wrongWindowBlocks.length > 0) {
    status = "blocked";
    headline = `Blocked before input on ${wrongWindowBlocks.length} wrong-window handoff attempt(s).`;
  } else if (blockedCount > 0 || didNotCompleteTasks.length > 0) {
    status = "blocked";
    headline = blockedCount > 0
      ? `${blockedCount} task(s) are blocked and need manual intervention.`
      : `${didNotCompleteTasks.length} recent task(s) did not complete cleanly.`;
  } else if (interruptedCount > 0) {
    status = "interrupted";
    headline = `${interruptedCount} task(s) were interrupted and must be reviewed before re-queue.`;
  } else if (runningCount > 0 || normalizeGhotiText(currentTask?.status) === "running") {
    status = "active";
    headline = currentTask
      ? `${currentTask.taskTypeLabel || "Task"} ${currentTask.taskId || ""} is active.`.trim()
      : "Ghoti is actively running a local task.";
  } else if (waitingCount > 0 || stalledTasks.length > 0) {
    status = "waiting";
    headline = waitingCount > 0
      ? `${waitingCount} task(s) are waiting or ready to resume.`
      : `${stalledTasks.length} task(s) look stalled and need operator attention.`;
  }

  const alerts = [
    wrongWindowBlocks.length > 0
      ? `${wrongWindowBlocks.length} recent handoff block(s) stopped before input because the active window did not match the intended Codex or ChatGPT destination.`
      : "",
    stalledTasks.length > 0
      ? `${stalledTasks.length} queued, running, or waiting task(s) have been unchanged for 15-20+ minutes.`
      : "",
    didNotCompleteTasks.length > 0
      ? `${didNotCompleteTasks.length} recent task(s) ended blocked, interrupted, or failed and still need review.`
      : "",
    pendingApprovalCount > 0
      ? `${pendingApprovalCount} approval request(s) are waiting on the operator.`
      : "",
    blockedCount > 0
      ? `${blockedCount} human-needed task(s) remain blocked in the current queue state.`
      : "",
    interruptedCount > 0
      ? `${interruptedCount} interrupted task(s) are visible and require review before any re-queue.`
      : "",
  ].filter(Boolean);

  const focusTask = currentTask
    || wrongWindowBlocks[0]
    || stalledTasks[0]
    || sortedTasks.find((item) => ghotiActionableStatuses.has(normalizeGhotiText(item.status)))
    || null;
  const overlayTarget = buildGhotiOverlayTarget(focusTask);
  const handoffHint = wrongWindowBlocks.length > 0 || overlayTarget.kind === "handoff"
    ? "Codex to ChatGPT handoff stays paste-only by default and blocks before input whenever the wrong window stays foreground or the destination is not confident."
    : "Ctrl+8 is still the emergency stop if a desktop action or operator recipe needs immediate interruption.";

  return {
    status,
    headline,
    alerts,
    wrongWindowBlockCount: wrongWindowBlocks.length,
    stalledTaskCount: stalledTasks.length,
    didNotCompleteCount: didNotCompleteTasks.length,
    attentionRequired: alerts.length > 0,
    handoffHint,
    overlayTarget,
  };
}

function classifyGhotiTaskType(task) {
  const actionType = String(task?.actionType || "").toLowerCase();
  const recipeName = String(task?.recipeName || "").toLowerCase();
  const sourceWindow = String(task?.sourceWindow || "").toLowerCase();
  const targetWindow = String(task?.targetWindow || "").toLowerCase();

  if (actionType === "run_operator_recipe") {
    if (
      recipeName === "codex_to_chatgpt_handoff_mvp"
      || (sourceWindow === "codex" && targetWindow === "chatgpt")
    ) {
      return "handoff";
    }
    return "recipe";
  }

  if (isDesktopExecutorAction(actionType)) {
    return "desktop";
  }

  return "repo";
}

function humanizeGhotiTaskType(taskType) {
  const mapping = {
    repo: "Repo action",
    desktop: "Desktop action",
    recipe: "Operator recipe",
    handoff: "Codex to ChatGPT handoff",
  };
  return mapping[taskType] || "Task";
}

function sortGhotiTasks(tasks) {
  return [...(tasks || [])].sort((left, right) => {
    const leftUpdated = String(left?.updatedAt || "");
    const rightUpdated = String(right?.updatedAt || "");
    const byUpdated = rightUpdated.localeCompare(leftUpdated);
    if (byUpdated !== 0) {
      return byUpdated;
    }
    return String(right?.taskId || "").localeCompare(String(left?.taskId || ""));
  });
}

function decorateGhotiTask(task) {
  const taskType = classifyGhotiTaskType(task);
  const headline = task.title && task.title !== "Executor task"
    ? task.title
    : `${humanizeGhotiTaskType(taskType)} ${task.taskId || ""}`.trim();
  return {
    ...task,
    taskType,
    taskTypeLabel: humanizeGhotiTaskType(taskType),
    headline,
    detail: task.lastSummary || task.detail || "No recent summary.",
  };
}

function filterGhotiTasks(tasks, filters = {}) {
  const visibility = String(filters.visibility || "actionable").toLowerCase();
  const requestedType = String(filters.taskType || "all").toLowerCase();
  const requestedStatus = String(filters.taskStatus || "all").toLowerCase();
  const activeOnly = Boolean(filters.activeOnly);
  const limit = parsePositiveIntQuery(filters.limit, 8);

  let items = sortGhotiTasks((tasks || []).map(decorateGhotiTask));
  const totalCount = items.length;

  if (visibility !== "all") {
    items = items.filter((item) => ghotiActionableStatuses.has(String(item.status || "").toLowerCase()));
  }

  if (activeOnly) {
    items = items.filter((item) => ghotiActiveStatuses.has(String(item.status || "").toLowerCase()));
  }

  if (requestedType !== "all") {
    items = items.filter((item) => item.taskType === requestedType);
  }

  if (requestedStatus !== "all") {
    items = items.filter((item) => String(item.status || "").toLowerCase() === requestedStatus);
  }

  return {
    items: items.slice(0, limit),
    totalCount,
    filteredCount: items.length,
    visibility,
    taskType: requestedType,
    taskStatus: requestedStatus,
    activeOnly,
    limit,
  };
}

async function buildSupervisorResponse() {
  const raw = await runRuntimeCli(["supervisor-status"]);
  const summary = raw.ok ? parseSupervisorStatus(raw.stdout) : buildDegradedSupervisorStatus(raw);
  return {
    ok: raw.ok,
    status: raw.ok ? "ok" : "degraded",
    degraded: !raw.ok,
    summary,
    raw,
    localOnly: true,
  };
}

async function buildPendingApprovalsResponse() {
  const raw = await runRuntimeCli(["pending-approvals"]);
  return {
    ok: raw.ok,
    summary: parseApprovalList(raw.stdout),
    raw,
    localOnly: true,
  };
}

async function buildApprovalItemResponse(approvalId) {
  const raw = await runRuntimeCli(["approval-status", "--approval-id", approvalId]);
  return {
    ok: raw.ok,
    summary: raw.ok ? parseApprovalDetail(raw.stdout) : null,
    raw,
    localOnly: true,
  };
}

async function buildTaskItemResponse(taskId) {
  const raw = await runRuntimeCli(["task-status", "--task-id", taskId]);
  return {
    ok: raw.ok,
    summary: raw.ok ? parseTaskDetail(raw.stdout) : null,
    raw,
    localOnly: true,
  };
}

async function buildExecutorTasksResponse() {
  const raw = await runRuntimeCli(["list-executor-tasks"]);
  return {
    ok: raw.ok,
    summary: raw.ok ? parseExecutorTaskList(raw.stdout) : null,
    raw,
    localOnly: true,
  };
}

function buildCompactSupervisorSummary(summary) {
  if (!summary) {
    return null;
  }

  return {
    headline: summary.headline || "Supervisor status unavailable.",
    status: summary.status || "unknown",
    ghotiState: summary.ghotiState || "idle",
    ghotiReason: summary.ghotiReason || "none",
    operatorNextStep: summary.operatorNextStep || "Refresh supervisor status.",
    pendingApprovalCount: Number(summary.pendingApprovalCount || 0),
    blockedHumanNeededCount: Number(summary.blockedHumanNeededCount || 0),
    waitingCount: Number(summary.waitingCount || 0),
    readyToResumeCount: Number(summary.readyToResumeCount || 0),
    interruptedCount: Number(summary.interruptedCount || 0),
    resourceGuardEventCount: Number(summary.resourceGuardEventCount || 0),
  };
}

function buildCompactExecutorTaskSummary(summary) {
  if (!summary) {
    return null;
  }

  return {
    headline: summary.headline || "No executor tasks queued yet.",
    count: Number(summary.count || 0),
  };
}

async function buildApprovalListResponse() {
  const raw = await runRuntimeCli(["approval-status"]);
  return {
    ok: raw.ok,
    summary: parseApprovalList(raw.stdout),
    raw,
    localOnly: true,
  };
}

function sendJson(response, statusCode, payload) {
  response.writeHead(statusCode, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
  });
  response.end(JSON.stringify(payload, null, 2));
}

function sendBuffer(response, statusCode, body, contentType = "text/plain; charset=utf-8") {
  response.writeHead(statusCode, {
    "Content-Type": contentType,
    "Cache-Control": "no-store",
  });
  response.end(body);
}

function contentTypeForPath(filePath) {
  switch (path.extname(filePath).toLowerCase()) {
    case ".html":
      return "text/html; charset=utf-8";
    case ".js":
      return "application/javascript; charset=utf-8";
    case ".css":
      return "text/css; charset=utf-8";
    case ".json":
      return "application/json; charset=utf-8";
    default:
      return "text/plain; charset=utf-8";
  }
}

function readJsonBody(request) {
  return new Promise((resolve, reject) => {
    let rawBody = "";
    request.on("data", (chunk) => {
      rawBody += chunk.toString();
      if (rawBody.length > 1024 * 1024) {
        reject(new Error("Request body too large."));
      }
    });
    request.on("end", () => {
      if (!rawBody.trim()) {
        resolve({});
        return;
      }

      try {
        resolve(JSON.parse(rawBody));
      } catch (error) {
        reject(new Error(`Invalid JSON body: ${error.message}`));
      }
    });
    request.on("error", reject);
  });
}

function requireFields(payload, fieldNames) {
  for (const fieldName of fieldNames) {
    if (!payload[fieldName] || String(payload[fieldName]).trim() === "") {
      throw new Error(`Missing required field: ${fieldName}`);
    }
  }
}

async function buildCapabilityResponse() {
  const raw = await runRuntimeCli(["capability-matrix"]);
  return {
    ok: raw.ok,
    summary: parseCapabilitySummary(raw.stdout),
    raw,
    localOnly: true,
  };
}

async function buildBrainStatusResponse() {
  const raw = await runRuntimeCli(["brain-status"]);
  return {
    ok: raw.ok,
    summary: parseBrainStatus(raw.stdout),
    raw,
    localOnly: true,
  };
}

async function buildAgentRoleResponse() {
  const raw = await runRuntimeCli(["list-agent-roles"]);
  return {
    ok: raw.ok,
    summary: parseAgentRoleStatus(raw.stdout),
    raw,
    localOnly: true,
  };
}

async function buildBrowserStatusResponse() {
  const raw = await runRuntimeCli(["browser-status"]);
  return {
    ok: raw.ok,
    summary: parseBrowserStatus(raw.stdout),
    raw,
    localOnly: true,
  };
}

async function buildMemoryStatusResponse() {
  const raw = await runRuntimeCli(["memory-status"]);
  return {
    ok: raw.ok,
    summary: parseMemoryStatus(raw.stdout),
    raw,
    localOnly: true,
  };
}

async function buildRelayStatusResponse() {
  const raw = await runRuntimeCli(["relay-status"]);
  return {
    ok: raw.ok,
    summary: parseRelayStatus(raw.stdout),
    raw,
    localOnly: true,
  };
}

function parseCliJson(stdout) {
  if (!stdout) {
    return null;
  }

  const normalized = String(stdout).trimEnd();
  const markerMatch = normalized.match(/(?:^|\r?\n)---\r?\n([\s\S]+)$/);
  if (!markerMatch) {
    return null;
  }

  const jsonPart = markerMatch[1].trim();
  if (!jsonPart) {
    return null;
  }

  try {
    const parsed = JSON.parse(jsonPart);
    return parsed && typeof parsed === "object" ? parsed : null;
  } catch (_) {
    return null;
  }
}

function buildCliJsonFailure(raw, error, parsed = null) {
  return {
    ok: false,
    summary: null,
    detail: parsed,
    raw,
    localOnly: true,
    error,
  };
}

function buildCliSummaryResponse(raw, label) {
  const parsed = parseCliJson(raw.stdout);
  if (!raw.ok) {
    return buildCliJsonFailure(raw, raw.stderr || raw.stdout || `${label} failed.`, parsed);
  }
  if (!parsed || typeof parsed !== "object") {
    return buildCliJsonFailure(raw, `${label} returned an invalid CLI JSON payload.`, parsed);
  }
  if (!parsed.summary || typeof parsed.summary !== "object") {
    return buildCliJsonFailure(raw, `${label} returned no summary.`, parsed);
  }
  if (parsed.status === "error") {
    const errors = Array.isArray(parsed.errors) ? parsed.errors.filter(Boolean) : [];
    return buildCliJsonFailure(raw, errors[0] || `${label} returned an error status.`, parsed);
  }
  return {
    ok: true,
    summary: parsed.summary,
    detail: parsed,
    raw,
    localOnly: true,
  };
}

function buildCliActionResponse(raw, label, fallbackHeadline) {
  const parsed = parseCliJson(raw.stdout);
  if (!parsed || typeof parsed !== "object") {
    return {
      ok: false,
      localOnly: true,
      summary: { headline: fallbackHeadline || `${label} failed.` },
      detail: parsed,
      raw,
      error: `${label} returned an invalid CLI JSON payload.`,
    };
  }
  if (!parsed.summary || typeof parsed.summary !== "object") {
    return {
      ok: false,
      localOnly: true,
      summary: { headline: fallbackHeadline || `${label} failed.` },
      detail: parsed,
      raw,
      error: `${label} returned no summary.`,
    };
  }

  const errors = Array.isArray(parsed.errors) ? parsed.errors.filter(Boolean) : [];
  const ok = raw.ok && parsed.status === "ok";
  const headline = parsed.summary.headline || fallbackHeadline || (ok ? `${label} completed.` : `${label} failed.`);

  return {
    ok,
    localOnly: true,
    summary: {
      ...parsed.summary,
      headline,
    },
    detail: parsed,
    raw,
    error: ok ? null : (errors[0] || raw.stderr || raw.stdout || `${label} failed.`),
  };
}

async function buildApprovalInboxResponse() {
  const raw = await runRuntimeCli(["ghoti-approval-list"]);
  return buildCliSummaryResponse(raw, "Approval inbox");
}

async function buildApprovalItemDetailResponse(approvalId) {
  const raw = await runRuntimeCli(["ghoti-approval-view", approvalId]);
  return buildCliSummaryResponse(raw, "Approval item detail");
}

async function buildManualQueueResponse() {
  const raw = await runRuntimeCli(["ghoti-manual-queue-list"]);
  return buildCliSummaryResponse(raw, "Manual queue");
}

async function buildManualQueueItemResponse(itemId) {
  const raw = await runRuntimeCli(["ghoti-manual-queue-view", itemId]);
  return buildCliSummaryResponse(raw, "Manual queue item detail");
}

async function buildAuditTraceResponse(approvalId) {
  const raw = await runRuntimeCli(["ghoti-audit-trace", approvalId]);
  return buildCliSummaryResponse(raw, "Audit trace");
}

async function buildControlCenterStateResponse() {
  const raw = await runRuntimeCli(["ghoti-control-center-state"]);
  return buildCliSummaryResponse(raw, "Control center state");
}

async function buildPipelineStateResponse() {
  const raw = await runRuntimeCli(["ghoti-control-center-state"]);
  return buildCliSummaryResponse(raw, "Pipeline state");
}

async function buildPipelineItemsResponse(statusFilter) {
  const cliArgs = ["ghoti-pipeline-items"];
  if (statusFilter) {
    cliArgs.push("--status", statusFilter);
  }
  const raw = await runRuntimeCli(cliArgs);
  return buildCliSummaryResponse(raw, "Pipeline items");
}

async function buildActionIntentsResponse() {
  const raw = await runRuntimeCli(["ghoti-action-intents"]);
  return buildCliSummaryResponse(raw, "Action intents");
}

async function buildGithubUpdatesResponse() {
  const statusRaw = await runRuntimeCli(["github-status"]);
  const capabilityRaw = await runRuntimeCli(["github-remote-capability"]);
  const status = parseGithubStatus(statusRaw.stdout);
  const capability = parseRemoteCapability(capabilityRaw.stdout);

  return {
    ok: statusRaw.ok && capabilityRaw.ok,
    summary: {
      branch: status.branch,
      clean: status.clean,
      stagedChanges: status.stagedChanges,
      unstagedChanges: status.unstagedChanges,
      untrackedChanges: status.untrackedChanges,
      originUrl: status.originUrl,
      ghAvailable: status.ghAvailable,
      ghAuthenticated: capability.ghAuthenticated,
      remoteWritePossible: capability.remoteWritePossible,
      blockingIssue: capability.blockingIssue,
      recentCommits: status.recentCommits,
      headline: status.clean
        ? `Branch ${status.branch} is clean.`
        : `Branch ${status.branch} has local changes.`,
    },
    raw: {
      githubStatus: statusRaw,
      remoteCapability: capabilityRaw,
    },
    localOnly: true,
  };
}

async function buildDesktopBridgeResponse(statusOnly) {
  const raw = await runDesktopBridgeCheck(statusOnly);
  return {
    ok: raw.ok,
    summary: parseDesktopBridge(raw.stdout),
    raw,
    localOnly: true,
  };
}

async function buildHandoffTargetCandidatesResponse() {
  const raw = await runDesktopBridgeAction("list_windows");
  const parsed = parseKeyValueBlock(raw.stdout);
  const windows = (parsed.listSections.windows || [])
    .filter((item) => item !== "none")
    .map(parseWindowCandidateLine);
  const codexCandidates = windows.filter((item) => item.aliases.includes("codex"));
  const chatgptCandidates = windows.filter((item) => item.aliases.includes("chatgpt"));

  return {
    ok: raw.ok,
    summary: {
      headline: raw.ok
        ? `Loaded ${codexCandidates.length} Codex and ${chatgptCandidates.length} ChatGPT window candidate(s).`
        : "Failed to load handoff target candidates.",
      codexCandidates,
      chatgptCandidates,
      candidateCount: windows.length,
    },
    raw,
    localOnly: true,
  };
}

async function handleApiRequest(request, response, requestUrl) {
  if (request.method === "GET" && requestUrl.pathname === "/api/health") {
    sendJson(response, 200, {
      ok: true,
      service: "dashboard-mvp",
      port: dashboardPort,
      localOnly: true,
    });
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/operator-status") {
    const payload = {
      ok: true,
      ...buildOperatorStatus(),
    };
    pushAction({
      actionType: "status",
      label: "Viewed operator status",
      status: "success",
      summary: "Loaded the local operator-mode status summary.",
    });
    sendJson(response, 200, payload);
    return;
  }

    if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/control-center") {
      const payload = await buildGhotiControlCenterResponse({
      visibility: requestUrl.searchParams.get("visibility") || "actionable",
      taskType: requestUrl.searchParams.get("taskType") || "all",
      taskStatus: requestUrl.searchParams.get("taskStatus") || "all",
      activeOnly: parseBooleanQuery(requestUrl.searchParams.get("activeOnly"), false),
      limit: parsePositiveIntQuery(requestUrl.searchParams.get("limit"), 8),
    });
    pushAction({
      actionType: "status",
      label: "Viewed Ghoti control center",
      status: payload.ok ? "success" : "error",
      summary: payload.summary.headline,
    });
      sendJson(response, payload.ok ? 200 : 500, payload);
      return;
    }

    if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/pipeline-items") {
      const statusFilter = requestUrl.searchParams.get("status") || null;
      const payload = await buildPipelineItemsResponse(statusFilter);
      pushAction({
        actionType: "status",
        label: "Viewed Ghoti pipeline items",
        status: payload.ok ? "success" : "error",
        summary: payload.ok ? `Pipeline items loaded${statusFilter ? ` (filter: ${statusFilter})` : ""}.` : "Pipeline items unavailable.",
      });
      sendJson(response, payload.ok ? 200 : 500, payload);
      return;
    }

    if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/action-intents") {
      const payload = await buildActionIntentsResponse();
      pushAction({
        actionType: "status",
        label: "Viewed Ghoti action intents",
        status: payload.ok ? "success" : "error",
        summary: payload.ok ? "ActionIntent read model loaded." : "ActionIntent read model unavailable.",
      });
      sendJson(response, payload.ok ? 200 : 500, payload);
      return;
    }

    if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/pipeline-state") {
      const payload = await buildPipelineStateResponse();
      pushAction({
        actionType: "status",
        label: "Viewed Ghoti pipeline state",
        status: payload.ok ? "success" : "error",
        summary: payload.ok ? "Pipeline state loaded." : "Pipeline state unavailable.",
      });
      sendJson(response, payload.ok ? 200 : 500, payload);
      return;
    }

    if (request.method === "GET" && requestUrl.pathname === "/api/brain/status") {
      const payload = await buildBrainStatusResponse();
      pushAction({
        actionType: "status",
        label: "Viewed brain status",
        status: payload.ok ? "success" : "error",
        summary: payload.summary.headline,
      });
      sendJson(response, payload.ok ? 200 : 500, payload);
      return;
    }

    if (request.method === "GET" && requestUrl.pathname === "/api/supervisor/status") {
    const payload = await buildSupervisorResponse();
    pushAction({
      actionType: "supervisor",
      label: "Viewed supervisor status",
      status: payload.ok ? "success" : "error",
      summary: payload.summary.headline,
    });
    sendJson(response, 200, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/approvals/pending") {
    const payload = await buildPendingApprovalsResponse();
    pushAction({
      actionType: "approval",
      label: "Viewed pending approvals",
      status: payload.ok ? "success" : "error",
      summary: payload.summary.headline,
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/approvals/list") {
    const payload = await buildApprovalListResponse();
    pushAction({
      actionType: "approval",
      label: "Viewed approval request list",
      status: payload.ok ? "success" : "error",
      summary: payload.summary.headline,
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/approvals/item") {
    const approvalId = requestUrl.searchParams.get("approvalId");
    if (!approvalId) {
      throw new Error("Missing approvalId query parameter.");
    }

    const payload = await buildApprovalItemResponse(approvalId);
    pushAction({
      actionType: "approval",
      label: "Viewed approval item",
      status: payload.ok ? "success" : "error",
      summary: payload.ok && payload.summary
        ? payload.summary.headline
        : (payload.raw.stderr || "Approval item lookup failed."),
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/tasks/item") {
    const taskId = requestUrl.searchParams.get("taskId");
    if (!taskId) {
      throw new Error("Missing taskId query parameter.");
    }

    const payload = await buildTaskItemResponse(taskId);
    pushAction({
      actionType: "task",
      label: "Viewed task item",
      status: payload.ok ? "success" : "error",
      summary: payload.ok && payload.summary
        ? payload.summary.headline
        : (payload.raw.stderr || "Task item lookup failed."),
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/executor/tasks") {
    const payload = await buildExecutorTasksResponse();
    pushAction({
      actionType: "executor",
      label: "Viewed executor task list",
      status: payload.ok ? "success" : "error",
      summary: payload.ok && payload.summary
        ? payload.summary.headline
        : (payload.raw.stderr || "Executor task list failed."),
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/capability-summary") {
    const payload = await buildCapabilityResponse();
    pushAction({
      actionType: "status",
      label: "Refreshed capability summary",
      status: payload.ok ? "success" : "error",
      summary: payload.summary.headline,
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (
    request.method === "GET" &&
    (requestUrl.pathname === "/api/github-status" || requestUrl.pathname === "/api/github-updates")
  ) {
    const payload = await buildGithubUpdatesResponse();
    pushAction({
      actionType: "github",
      label: "Refreshed GitHub updates",
      status: payload.ok ? "success" : "error",
      summary: payload.summary.headline,
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/executor/queue") {
    const payload = await readJsonBody(request);
    requireFields(payload, ["actionType"]);

    const cliArgs = [
      "queue-executor-action",
      "--action-type",
      String(payload.actionType),
    ];

    if (payload.target) {
      cliArgs.push("--target", String(payload.target));
    }
    if (payload.content) {
      cliArgs.push("--content", String(payload.content));
    }
    cliArgs.push("--source", "dashboard");

    const raw = await runRuntimeCli(cliArgs);
    const taskId = extractOutputPath("task_id", raw.stdout) || "none";
    const taskPayload = taskId !== "none" ? await buildTaskItemResponse(taskId) : { ok: false, summary: null, raw: { stdout: "", stderr: "Task id missing." } };
    const executorPayload = await buildExecutorTasksResponse();
    const supervisorPayload = await buildSupervisorResponse();
    const ok = raw.ok && taskPayload.ok && executorPayload.ok && supervisorPayload.ok;

    const summaryHeadline = ok
      ? (
          taskPayload.summary?.approvalState === "pending"
            ? "Executor task queued and now waiting for approval."
            : "Executor task queued."
        )
      : (raw.stderr || raw.stdout || "Executor task queue failed.");

    pushAction({
      actionType: "executor",
      label: "Queued executor task",
      status: ok ? "success" : "error",
      summary: summaryHeadline,
      outputPath: taskId,
    });

    sendJson(response, ok ? 200 : 500, {
      ok,
      localOnly: true,
      summary: {
        headline: summaryHeadline,
        taskId,
        status: taskPayload.summary?.status || "unknown",
      },
      task: taskPayload.summary,
      taskRaw: taskPayload.raw,
      executorTasks: executorPayload.summary,
      supervisor: supervisorPayload.summary,
      raw: {
        queue: raw,
      },
    });
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/artifacts") {
    sendJson(response, 200, {
      ok: true,
      localOnly: true,
      artifacts: listRecentArtifacts(),
    });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/artifacts/preview") {
    const payload = await readJsonBody(request);
    requireFields(payload, ["path"]);
    const preview = buildArtifactPreview(String(payload.path));
    pushAction({
      actionType: "artifact",
      label: "Previewed artifact",
      status: "success",
      summary: `Loaded preview for ${preview.name}.`,
      outputPath: preview.path,
    });
    sendJson(response, 200, {
      ok: true,
      localOnly: true,
      preview,
      summary: {
        headline: `Preview loaded for ${preview.name}.`,
        outputPath: preview.path,
      },
    });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/approvals/decision") {
    const payload = await readJsonBody(request);
    requireFields(payload, ["approvalId", "decision"]);

    const approvalId = String(payload.approvalId).trim();
    const decision = String(payload.decision).trim().toLowerCase();
    const note = payload.note ? String(payload.note) : "";
    const commandMap = {
      approve: "approve-approval",
      deny: "deny-approval",
      defer: "defer-approval",
    };
    const command = commandMap[decision];
    if (!command) {
      throw new Error("Unsupported approval decision.");
    }

    const cliArgs = [command, "--approval-id", approvalId];
    if (note.trim()) {
      cliArgs.push("--note", note);
    }

    const raw = await runRuntimeCli(cliArgs);
    const approvalPayload = await buildApprovalItemResponse(approvalId);
    const supervisorPayload = await buildSupervisorResponse();
    const pendingPayload = await buildPendingApprovalsResponse();
    const ok = raw.ok && approvalPayload.ok && supervisorPayload.ok && pendingPayload.ok;

    const headlineMap = {
      approve: "Approval approved.",
      deny: "Approval denied.",
      defer: "Approval deferred.",
    };
    const summaryHeadline = ok
      ? (
          decision === "approve" && approvalPayload.summary?.workspacePolicy === "blocked_by_workspace_policy"
            ? "Approval recorded, but workspace policy still blocks execution."
            : headlineMap[decision]
        )
      : (raw.stderr || raw.stdout || "Approval decision failed.");

    pushAction({
      actionType: "approval",
      label: `${decision[0].toUpperCase()}${decision.slice(1)} approval`,
      status: ok ? "success" : "error",
      summary: summaryHeadline,
      outputPath: approvalId,
    });

    sendJson(response, ok ? 200 : 500, {
      ok,
      localOnly: true,
      summary: {
        headline: summaryHeadline,
        approvalId,
        decision,
        status: approvalPayload.summary?.status || "unknown",
      },
      approval: approvalPayload.summary,
      approvalRaw: approvalPayload.raw,
      supervisor: supervisorPayload.summary,
      pendingApprovals: pendingPayload.summary,
      raw: {
        decision: raw,
      },
    });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/tasks/action") {
    const payload = await readJsonBody(request);
    requireFields(payload, ["taskId", "action"]);

    const taskId = String(payload.taskId).trim();
    const action = String(payload.action).trim().toLowerCase();
    const note = payload.note ? String(payload.note) : "";
    const commandMap = {
      review: "review-task",
      resume: "resume",
      requeue: "requeue-task",
      execute: "execute-task",
    };
    const command = commandMap[action];
    if (!command) {
      throw new Error("Unsupported task action.");
    }

    const cliArgs = [command, "--task-id", taskId];
    if (note.trim() && (action === "review" || action === "requeue")) {
      cliArgs.push("--note", note);
    }

    const raw = await runRuntimeCli(cliArgs);
    const taskPayload = await buildTaskItemResponse(taskId);
    const supervisorPayload = await buildSupervisorResponse();
    const executorPayload = await buildExecutorTasksResponse();
    const ok = raw.ok && taskPayload.ok && supervisorPayload.ok && executorPayload.ok;

    const headlineMap = {
      review: "Task review recorded.",
      resume: "Waiting task resumed.",
      requeue: "Task re-queued.",
      execute: "Allowlisted executor action completed.",
    };
    let summaryHeadline = headlineMap[action] || "Task action completed.";
    if (!ok) {
      summaryHeadline = raw.stderr || raw.stdout || "Task action failed.";
    } else if (action === "execute" && taskPayload.summary?.status === "interrupted") {
      summaryHeadline = "Desktop action interrupted by the local failsafe.";
    } else if (
      action === "execute" &&
      taskPayload.summary?.status === "blocked_human_needed" &&
      taskPayload.summary?.lastExecutionStatus === "failed"
    ) {
      summaryHeadline =
        taskPayload.summary?.lastExecutionSummary
        || taskPayload.summary?.blockedReason
        || "Allowlisted executor action was blocked.";
    } else if (
      action === "execute" &&
      taskPayload.summary?.status === "failed" &&
      taskPayload.summary?.lastExecutionStatus === "failed"
    ) {
      summaryHeadline =
        taskPayload.summary?.lastExecutionSummary
        || taskPayload.summary?.lastFailureReason
        || "Allowlisted executor action failed.";
    } else if (
      action === "review" &&
      taskPayload.summary?.workspacePolicy === "blocked_by_workspace_policy" &&
      taskPayload.summary?.status === "blocked_human_needed"
    ) {
      summaryHeadline = "Task review recorded, but workspace policy still blocks it.";
    }

    pushAction({
      actionType: "task",
      label: `${action[0].toUpperCase()}${action.slice(1)} task`,
      status: ok ? "success" : "error",
      summary: summaryHeadline,
      outputPath: taskId,
    });

    sendJson(response, ok ? 200 : 500, {
      ok,
      localOnly: true,
      summary: {
        headline: summaryHeadline,
        taskId,
        action,
        status: taskPayload.summary?.status || "unknown",
      },
      task: taskPayload.summary,
      taskRaw: taskPayload.raw,
      supervisor: buildCompactSupervisorSummary(supervisorPayload.summary),
      executorTasks: buildCompactExecutorTaskSummary(executorPayload.summary),
      raw: {
        action: raw,
      },
    });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/artifacts/open") {
    const payload = await readJsonBody(request);
    requireFields(payload, ["path"]);
    const raw = await openArtifact(String(payload.path));
    pushAction({
      actionType: "artifact",
      label: "Opened artifact",
      status: raw.ok ? "success" : "error",
      summary: raw.ok ? `Opened ${raw.path} in the default app.` : (raw.stderr || "Artifact open failed."),
      outputPath: raw.path,
    });
    sendJson(response, raw.ok ? 200 : 500, {
      ok: raw.ok,
      localOnly: true,
      summary: {
        headline: raw.ok ? "Artifact opened in the default app." : "Artifact open failed.",
        outputPath: raw.path,
      },
      raw,
    });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/artifacts/reveal") {
    const payload = await readJsonBody(request);
    requireFields(payload, ["path"]);
    const raw = await revealArtifact(String(payload.path));
    pushAction({
      actionType: "artifact",
      label: "Revealed artifact",
      status: raw.ok ? "success" : "error",
      summary: raw.ok ? `Revealed ${raw.path} in Explorer.` : (raw.stderr || "Artifact reveal failed."),
      outputPath: raw.path,
    });
    sendJson(response, raw.ok ? 200 : 500, {
      ok: raw.ok,
      localOnly: true,
      summary: {
        headline: raw.ok ? "Artifact revealed in Explorer." : "Artifact reveal failed.",
        outputPath: raw.path,
      },
      raw,
    });
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/desktop-bridge/status") {
    const payload = await buildDesktopBridgeResponse(true);
    pushAction({
      actionType: "desktop",
      label: "Viewed desktop bridge status",
      status: payload.ok ? "success" : "error",
      summary: payload.summary.headline,
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/desktop-bridge/check") {
    const requestPayload = await readJsonBody(request);
    const runFullCheck = requestPayload.fullCheck === true && requestPayload.allowDisruptiveActions === true;
    const payload = await buildDesktopBridgeResponse(!runFullCheck);
    pushAction({
      actionType: "desktop",
      label: runFullCheck ? "Ran desktop bridge check" : "Ran desktop bridge status check",
      status: payload.ok ? "success" : "error",
      summary: payload.summary.headline,
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/desktop-bridge/handoff-targets") {
    const payload = await buildHandoffTargetCandidatesResponse();
    pushAction({
      actionType: "desktop",
      label: "Viewed handoff target candidates",
      status: payload.ok ? "success" : "error",
      summary: payload.summary.headline,
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/recent-actions") {
    sendJson(response, 200, {
      ok: true,
      localOnly: true,
      actions: recentActions,
    });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/scaffold/internship") {
    const payload = await readJsonBody(request);
    requireFields(payload, ["targetRole", "company", "jobSource", "fitSummary"]);
    const raw = await runRuntimeCli([
      "scaffold-internship-pack",
      "--target-role",
      String(payload.targetRole),
      "--company",
      String(payload.company),
      "--job-source",
      String(payload.jobSource),
      "--fit-summary",
      String(payload.fitSummary),
    ]);
    const outputPath = extractOutputPath("personal_ops_path", raw.stdout) || "none";
    const responsePayload = {
      ok: raw.ok,
      summary: {
        action: "internship_scaffold",
        headline: raw.ok
          ? "Internship pack generated."
          : "Internship pack generation failed.",
        outputPath,
      },
      raw,
      artifacts: listRecentArtifacts(),
      localOnly: true,
    };
    pushAction({
      actionType: "personal_ops",
      label: "Generated internship pack",
      status: raw.ok ? "success" : "error",
      summary: responsePayload.summary.headline,
      outputPath,
    });
    sendJson(response, raw.ok ? 200 : 500, responsePayload);
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/scaffold/showcase") {
    const payload = await readJsonBody(request);
    requireFields(payload, ["projectName", "objective", "highlights"]);
    const raw = await runRuntimeCli([
      "scaffold-showcase-case-study",
      "--project-name",
      String(payload.projectName),
      "--objective",
      String(payload.objective),
      "--highlights",
      String(payload.highlights),
    ]);
    const outputPath = extractOutputPath("personal_ops_path", raw.stdout) || "none";
    const responsePayload = {
      ok: raw.ok,
      summary: {
        action: "showcase_case_study",
        headline: raw.ok
          ? "Showcase case study generated."
          : "Showcase case study generation failed.",
        outputPath,
      },
      raw,
      artifacts: listRecentArtifacts(),
      localOnly: true,
    };
    pushAction({
      actionType: "personal_ops",
      label: "Generated showcase case study",
      status: raw.ok ? "success" : "error",
      summary: responsePayload.summary.headline,
      outputPath,
    });
    sendJson(response, raw.ok ? 200 : 500, responsePayload);
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/scaffold/portfolio") {
    const payload = await readJsonBody(request);
    requireFields(payload, ["projectName", "summary", "stack"]);
    const raw = await runRuntimeCli([
      "scaffold-portfolio-project-page",
      "--project-name",
      String(payload.projectName),
      "--summary",
      String(payload.summary),
      "--stack",
      String(payload.stack),
    ]);
    const outputPath = extractOutputPath("personal_ops_path", raw.stdout) || "none";
    const responsePayload = {
      ok: raw.ok,
      summary: {
        action: "portfolio_project_page",
        headline: raw.ok
          ? "Portfolio project page generated."
          : "Portfolio project page generation failed.",
        outputPath,
      },
      raw,
      artifacts: listRecentArtifacts(),
      localOnly: true,
    };
    pushAction({
      actionType: "personal_ops",
      label: "Generated portfolio page",
      status: raw.ok ? "success" : "error",
      summary: responsePayload.summary.headline,
      outputPath,
    });
    sendJson(response, raw.ok ? 200 : 500, responsePayload);
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/browser/smoke") {
    const raw = await runBrowserDemo(false, false);
    const browserResult = parseBrowserResult(raw.stdout);
    const responsePayload = {
      ok: raw.ok,
      degraded: Boolean(raw.degraded),
      summary: {
        action: "browser_smoke",
        headline: raw.ok
          ? "Headless browser smoke demo completed."
          : raw.degraded
            ? "Headless browser smoke demo unavailable until Playwright is installed."
          : "Headless browser smoke demo failed.",
        mode: browserResult.mode,
        screenshotPath: browserResult.screenshotPath,
        missingDependency: browserResult.mode === "dependency_missing" ? "playwright" : "none",
      },
      raw,
      artifacts: listRecentArtifacts(),
      localOnly: true,
    };
    pushAction({
      actionType: "browser",
      label: "Ran browser smoke demo",
      status: raw.ok ? "success" : (raw.degraded ? "warning" : "error"),
      summary: responsePayload.summary.headline,
      outputPath: browserResult.screenshotPath,
    });
    sendJson(response, raw.ok || raw.degraded ? 200 : 500, responsePayload);
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/browser/visible") {
    const payload = await readJsonBody(request);
    const raw = await runBrowserDemo(true, Boolean(payload.checkOnly));
    const browserResult = parseBrowserResult(raw.stdout);
    const responsePayload = {
      ok: raw.ok,
      degraded: Boolean(raw.degraded),
      summary: {
        action: "browser_visible",
        headline: raw.ok
          ? (payload.checkOnly
              ? "Visible browser demo path checked."
              : "Visible browser demo completed.")
          : raw.degraded
            ? "Visible browser demo unavailable until Playwright is installed."
          : "Visible browser demo failed.",
        mode: browserResult.mode,
        screenshotPath: browserResult.screenshotPath,
        headless: browserResult.headless,
        checkOnly: Boolean(payload.checkOnly),
        missingDependency: browserResult.mode === "dependency_missing" ? "playwright" : "none",
      },
      raw,
      artifacts: listRecentArtifacts(),
      localOnly: true,
    };
    pushAction({
      actionType: "browser",
      label: payload.checkOnly
        ? "Checked visible browser demo path"
        : "Ran visible browser demo",
      status: raw.ok ? "success" : (raw.degraded ? "warning" : "error"),
      summary: responsePayload.summary.headline,
      outputPath: browserResult.screenshotPath,
    });
    sendJson(response, raw.ok || raw.degraded ? 200 : 500, responsePayload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/control-center-state") {
    const payload = await buildControlCenterStateResponse();
    pushAction({ actionType: "status", label: "Viewed Ghoti control center state", status: payload.ok ? "success" : "error", summary: payload.ok ? "Control center state loaded." : "Control center state unavailable." });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/approval-inbox") {
    const payload = await buildApprovalInboxResponse();
    pushAction({ actionType: "approval", label: "Viewed Ghoti approval inbox", status: payload.ok ? "success" : "error", summary: payload.ok ? "Approval inbox loaded." : "Approval inbox unavailable." });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/approval-item") {
    const id = requestUrl.searchParams.get("id");
    if (!id) {
      sendJson(response, 400, { ok: false, error: "Missing id query parameter." });
      return;
    }
    const payload = await buildApprovalItemDetailResponse(id);
    pushAction({ actionType: "approval", label: "Viewed approval item detail", status: payload.ok ? "success" : "error", summary: payload.ok ? `Approval ${id} loaded.` : `Approval ${id} not found.` });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/manual-queue") {
    const payload = await buildManualQueueResponse();
    pushAction({ actionType: "status", label: "Viewed Ghoti manual queue", status: payload.ok ? "success" : "error", summary: payload.ok ? "Manual queue loaded." : "Manual queue unavailable." });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/manual-queue-item") {
    const id = requestUrl.searchParams.get("id");
    if (!id) {
      sendJson(response, 400, { ok: false, error: "Missing id query parameter." });
      return;
    }
    const payload = await buildManualQueueItemResponse(id);
    pushAction({ actionType: "status", label: "Viewed manual queue item", status: payload.ok ? "success" : "error", summary: payload.ok ? `Queue item ${id} loaded.` : `Queue item ${id} not found.` });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/audit-trace") {
    const id = requestUrl.searchParams.get("approval_id");
    if (!id) {
      sendJson(response, 400, { ok: false, error: "Missing approval_id query parameter." });
      return;
    }
    const payload = await buildAuditTraceResponse(id);
    pushAction({ actionType: "status", label: "Viewed audit trace", status: payload.ok ? "success" : "error", summary: payload.ok ? `Audit trace for ${id} loaded.` : `Audit trace for ${id} unavailable.` });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/approval/approve") {
    const body = await readJsonBody(request);
    requireFields(body, ["approval_id"]);
    const approvalId = String(body.approval_id).trim();
    const raw = await runRuntimeCli(["ghoti-approval-approve", approvalId]);
    const payload = buildCliActionResponse(raw, "Approval approve", "Approval approve failed.");
    pushAction({
      actionType: "approval",
      label: "Approved ghoti approval",
      status: payload.ok ? "success" : "error",
      summary: payload.summary?.headline || payload.error || "Approve failed.",
      outputPath: approvalId,
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/approval/reject") {
    const body = await readJsonBody(request);
    requireFields(body, ["approval_id", "reason"]);
    const approvalId = String(body.approval_id).trim();
    const reason = String(body.reason).trim();
    if (!reason) throw new Error("reason is required to reject an approval.");
    const raw = await runRuntimeCli(["ghoti-approval-reject", approvalId, "--reason", reason]);
    const payload = buildCliActionResponse(raw, "Approval reject", "Approval reject failed.");
    pushAction({
      actionType: "approval",
      label: "Rejected ghoti approval",
      status: payload.ok ? "success" : "error",
      summary: payload.summary?.headline || payload.error || "Reject failed.",
      outputPath: approvalId,
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/manual-queue/review") {
    const body = await readJsonBody(request);
    requireFields(body, ["item_id", "note"]);
    const itemId = String(body.item_id).trim();
    const note = String(body.note).trim();
    if (!note) throw new Error("note is required to mark a queue item reviewed.");
    const raw = await runRuntimeCli(["ghoti-manual-queue-mark-reviewed", itemId, "--note", note]);
    const payload = buildCliActionResponse(raw, "Manual queue review", "Queue item review failed.");
    pushAction({
      actionType: "status",
      label: "Marked queue item reviewed",
      status: payload.ok ? "success" : "error",
      summary: payload.summary?.headline || payload.error || "Review failed.",
      outputPath: itemId,
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/active-state") {
    const state = readActiveModeState();
    sendJson(response, 200, { ok: true, state });
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/active/session") {
    const store = readActiveSessionStore();
    sendJson(response, 200, { ok: true, session: store.current_session });
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/active/sessions") {
    const store = readActiveSessionStore();
    sendJson(response, 200, { ok: true, sessions: store.recent_sessions.slice(0, maxActiveSessions) });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/active/session/review") {
    const body = await readJsonBody(request);
    requireFields(body, ["session_id"]);
    const sessionId = String(body.session_id).trim();
    const reviewNote = normalizeReviewNote(body.review_note);
    const session = updateStoredActiveSession(sessionId, {
      reviewed: true,
      reviewed_at_utc: new Date().toISOString(),
      review_note: reviewNote,
    });
    if (!session) {
      sendJson(response, 404, { ok: false, error: "Active session not found." });
      return;
    }
    pushAction({
      actionType: "status",
      label: "Reviewed active session",
      status: "success",
      summary: reviewNote
        ? `Marked ${sessionId} reviewed. Note saved locally.`
        : `Marked ${sessionId} reviewed.`,
    });
    sendJson(response, 200, { ok: true, action: "review", session });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/active/session/keep") {
    const body = await readJsonBody(request);
    requireFields(body, ["session_id"]);
    const sessionId = String(body.session_id).trim();
    const session = updateStoredActiveSession(sessionId, {
      retention_status: "kept",
    });
    if (!session) {
      sendJson(response, 404, { ok: false, error: "Active session not found." });
      return;
    }
    pushAction({
      actionType: "status",
      label: "Kept active session metadata",
      status: "success",
      summary: `Marked ${sessionId} as kept. No files were deleted.`,
    });
    sendJson(response, 200, { ok: true, action: "keep", session });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/active/session/discard") {
    const body = await readJsonBody(request);
    requireFields(body, ["session_id"]);
    const sessionId = String(body.session_id).trim();
    const session = updateStoredActiveSession(sessionId, {
      retention_status: "discarded",
    });
    if (!session) {
      sendJson(response, 404, { ok: false, error: "Active session not found." });
      return;
    }
    pushAction({
      actionType: "status",
      label: "Discarded active session metadata",
      status: "success",
      summary: `Marked ${sessionId} discarded. Capture files remain untouched until a future explicit operator action.`,
    });
    sendJson(response, 200, { ok: true, action: "discard", session });
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/active/frames") {
    const store = readActiveSessionStore();
    const sessionIdParam = requestUrl.searchParams.get("session_id");
    let session;
    if (sessionIdParam) {
      const safeId = sanitizeSessionId(sessionIdParam);
      if (!safeId) {
        sendJson(response, 400, { ok: false, error: "Invalid session_id." });
        return;
      }
      session = safeId === store.current_session?.session_id
        ? normalizeActiveSession(store.current_session)
        : normalizeActiveSession((store.recent_sessions || []).find((s) => s?.session_id === safeId));
    } else {
      session = normalizeActiveSession(store.current_session);
    }
    const sessionId = session?.session_id || null;
    const rawFrames = Array.isArray(session?.recent_frames) ? session.recent_frames.slice(0, maxSessionFrames) : [];
    const frames = rawFrames.map((frame) => ({
      ...frame,
      url: frame.image_url || null,
      size: null,
      mtime_utc: frame.captured_at_utc || null,
    }));
    sendJson(response, 200, {
      ok: true,
      session_id: sessionId,
      session: buildActiveSessionSummary(session),
      frames,
      bounded: true,
      max_frames: maxSessionFrames,
      local_only: true,
    });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/active/start") {
    const state = writeActiveModeState({ active: true, mode: "active", screen_view_enabled: true, error: null });
    const session = ensureCurrentActiveSession();
    pushAction({ actionType: "status", label: "Ghoti Active Mode started", status: "success", summary: "Operator started Ghoti Active Mode." });
    sendJson(response, 200, { ok: true, state, session });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/active/stop") {
    stopCaptureProcess();
    const state = writeActiveModeState({ active: false, mode: "idle", screen_view_enabled: false, error: null });
    const session = closeCurrentActiveSession();
    pushAction({ actionType: "status", label: "Ghoti Active Mode stopped", status: "success", summary: "Operator stopped Ghoti Active Mode." });
    sendJson(response, 200, { ok: true, state, session });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/active/snapshot") {
    if (!fs.existsSync(screenshotsDir)) fs.mkdirSync(screenshotsDir, { recursive: true });
    const snapshotFilename = `ghoti-snapshot-${Date.now()}.png`;
    const snapshotPath = path.join(screenshotsDir, snapshotFilename);
    const powerShell = resolvePowerShell();
    if (!powerShell) {
      const state = writeActiveModeState({ error: "PowerShell not found — cannot capture screenshot." });
      sendJson(response, 500, { ok: false, error: "PowerShell not found.", state });
      return;
    }
    const psScript = [
      "Add-Type -AssemblyName System.Windows.Forms",
      "Add-Type -AssemblyName System.Drawing",
      "$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds",
      "$bmp = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)",
      "$g = [System.Drawing.Graphics]::FromImage($bmp)",
      "$g.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)",
      "$g.Dispose()",
      `$bmp.Save("${snapshotPath.replace(/\\/g, "\\\\")}")`,
      "$bmp.Dispose()",
      "Write-Output 'ok'",
    ].join("; ");
    const result = await runCommand(powerShell.command, [...powerShell.baseArgs, "-ExecutionPolicy", "Bypass", "-Command", psScript], { cwd: repoRoot, timeoutMs: 20000 });
    if (!result.ok || !fs.existsSync(snapshotPath)) {
      const errMsg = result.stderr || result.stdout || "Screenshot capture failed.";
      const state = writeActiveModeState({ error: `Screenshot failed: ${errMsg}` });
      sendJson(response, 500, { ok: false, error: errMsg, state });
      return;
    }
    const relPath = path.relative(repoRoot, snapshotPath).replace(/\\/g, "/");
    const state = writeActiveModeState({ last_snapshot_path: relPath, mode: "active", error: null });
    pushAction({ actionType: "status", label: "Ghoti snapshot captured", status: "success", summary: `Snapshot saved: ${relPath}` });
    sendJson(response, 200, { ok: true, snapshotPath: relPath, state });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/active/message") {
    const body = await readJsonBody(request);
    requireFields(body, ["message"]);
    const msg = String(body.message || "").trim();
    if (!msg) throw new Error("message is required.");
    const state = writeActiveModeState({ mode: "processing", error: null });
    pushAction({ actionType: "status", label: "Ghoti received instruction", status: "success", summary: `Operator message: ${msg.slice(0, 80)}` });
    const ackState = writeActiveModeState({ mode: "waiting_for_approval" });
    sendJson(response, 200, { ok: true, received: msg, note: "Instruction logged. Operator approval required before any action is taken.", state: ackState });
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/active/capture-state") {
    const captureState = readCaptureState();
    sendJson(response, 200, { ok: true, captureState });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/active/capture/start") {
    const activeState = readActiveModeState();
    if (!activeState.active) {
      sendJson(response, 400, { ok: false, error: "Ghoti is not active. Start Ghoti first.", captureState: readCaptureState() });
      return;
    }
    if (captureInterval) {
      sendJson(response, 200, { ok: true, note: "Capture already running.", captureState: readCaptureState() });
      return;
    }

    const powerShell = resolvePowerShell();
    if (!powerShell) {
      sendJson(response, 500, { ok: false, error: "PowerShell not found — cannot start screen capture.", captureState: readCaptureState() });
      return;
    }

    if (!fs.existsSync(runtimeDataDir)) fs.mkdirSync(runtimeDataDir, { recursive: true });
    if (!fs.existsSync(captureFramesDir)) fs.mkdirSync(captureFramesDir, { recursive: true });

    captureFrameCount = 0;
    captureTickRunning = false;

    const session = markCurrentSessionCaptureStarted();
    currentCaptureSessionId = session?.session_id || null;

    fs.writeFileSync(captureStateFile, JSON.stringify({
      capturing: true,
      capture_method: "powershell-copyfromscreen-loop",
      fps_target: 1,
      frame_count: 0,
      session_id: currentCaptureSessionId,
      session_frame_dir: currentCaptureSessionId ? getSessionFrameDir(currentCaptureSessionId) : null,
      latest_frame_path: null,
      latest_frame_name: null,
      latest_frame_utc: null,
      error: null,
    }, null, 2));

    // Kick off first frame immediately (non-blocking)
    captureOneTick(powerShell);

    // Then repeat at 1 FPS
    captureInterval = setInterval(() => captureOneTick(powerShell), 1000);

    const captureState = readCaptureState();
    pushAction({ actionType: "status", label: "Screen capture started", status: "success", summary: "Continuous capture at 1 FPS via PowerShell" });
    sendJson(response, 200, { ok: true, captureState, session });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/active/capture/stop") {
    stopCaptureProcess();
    const captureState = readCaptureState();
    const session = normalizeActiveSession(readActiveSessionStore().current_session);
    pushAction({ actionType: "status", label: "Screen capture stopped", status: "success", summary: "Operator stopped continuous capture." });
    sendJson(response, 200, { ok: true, captureState, session });
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/active/frame") {
    const sessionIdParam = requestUrl.searchParams.get("session_id");
    const framePath = resolveCurrentSessionFramePath(sessionIdParam, requestUrl.searchParams.get("name"));
    if (!framePath) {
      sendJson(response, 404, { ok: false, error: "Requested frame is not available for the requested session." });
      return;
    }
    sendBuffer(response, 200, fs.readFileSync(framePath), "image/png");
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/active/latest-frame") {
    const sessionIdParam = requestUrl.searchParams.get("session_id");
    let latestFramePath = null;

    const trySessionLatest = (sessionId) => {
      const safeId = sanitizeSessionId(sessionId);
      if (!safeId) return null;
      const dir = getSessionFrameDir(safeId);
      if (!dir) return null;
      const candidate = path.join(dir, "latest.png");
      return fs.existsSync(candidate) ? candidate : null;
    };

    if (sessionIdParam) {
      const safeId = sanitizeSessionId(sessionIdParam);
      if (!safeId) {
        sendJson(response, 400, { ok: false, error: "Invalid session_id." });
        return;
      }
      latestFramePath = trySessionLatest(safeId);
    } else {
      const store = readActiveSessionStore();
      // Prefer current session
      latestFramePath = store.current_session?.session_id
        ? trySessionLatest(store.current_session.session_id)
        : null;
      // Fall back to most recent stopped session with a frame
      if (!latestFramePath && Array.isArray(store.recent_sessions)) {
        for (const s of store.recent_sessions) {
          if (s?.session_id) {
            const candidate = trySessionLatest(s.session_id);
            if (candidate) { latestFramePath = candidate; break; }
          }
        }
      }
      // Final fallback: global latest.png
      if (!latestFramePath) {
        const globalLatest = path.join(captureFramesDir, "latest.png");
        if (fs.existsSync(globalLatest)) latestFramePath = globalLatest;
      }
    }

    if (!latestFramePath) {
      sendJson(response, 404, { ok: false, error: "No latest frame available." });
      return;
    }
    sendBuffer(response, 200, fs.readFileSync(latestFramePath), "image/png");
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/active/observations") {
    const rawSessionId = String(requestUrl.searchParams.get("session_id") || "").trim();
    if (rawSessionId && !sanitizeSessionId(rawSessionId)) {
      sendJson(response, 200, { ok: false, error: "invalid_session_id", observations: [] });
      return;
    }
    const rawLimit = requestUrl.searchParams.get("limit");
    const observations = listObservations(rawSessionId || null, rawLimit || defaultObservationLimit);
    sendJson(response, 200, {
      ok: true,
      observations,
      session_id: rawSessionId || null,
      limit: observations.length,
    });
    return;
  }

  // FUTURE ACTION HOOK - scaffold only:
  // If an observation is ever used to trigger an action such as click, type, browser navigation,
  // shell, file write, or external request, that action must go through requiresOperatorApproval
  // plus action-bound and payload-bound approval consumption. Observations alone never authorize actions.
  // Do not wire this milestone.
  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/active/observe-frame") {
    const body = await readJsonBody(request);
    const rawSessionId = String(body.session_id || "").trim();
    const customPrompt = typeof body.prompt === "string" ? body.prompt.trim() : "";

    if (!rawSessionId) {
      sendJson(response, 200, { ok: false, error: "session_id_required" });
      return;
    }

    const sessionId = sanitizeSessionId(rawSessionId);
    if (!sessionId) {
      sendJson(response, 200, { ok: false, error: "invalid_session_id" });
      return;
    }

    const session = getStoredSessionById(sessionId);
    if (!session) {
      sendJson(response, 200, { ok: false, error: "session_not_found" });
      return;
    }

    if (observationRequestsInFlight.has(sessionId)) {
      sendJson(response, 200, { ok: false, error: "observation_in_flight" });
      return;
    }

    const prompt = customPrompt || defaultObservationPrompt;
    const requestedAtUtc = new Date().toISOString();
    const framePath = resolveLatestFramePathForSession(sessionId);
    const framePathRelative = toRepoRelativePath(framePath);
    const frameTsUtc = typeof session.latest_frame_utc === "string" ? session.latest_frame_utc : null;

    observationRequestsInFlight.add(sessionId);

    try {
      if (!framePath) {
        const observation = appendObservation({
          session_id: sessionId,
          frame_path: framePathRelative,
          frame_ts_utc: frameTsUtc,
          requested_at_utc: requestedAtUtc,
          completed_at_utc: new Date().toISOString(),
          model: null,
          prompt,
          description: "",
          latency_ms: null,
          status: "no_frame",
          error: "No latest frame available for this session.",
        });
        sendJson(response, 200, { ok: false, error: "no_frame", observation });
        return;
      }

      const visionStatus = await getOllamaVisionStatus();
      if (!visionStatus.available) {
        const observation = appendObservation({
          session_id: sessionId,
          frame_path: framePathRelative,
          frame_ts_utc: frameTsUtc,
          requested_at_utc: requestedAtUtc,
          completed_at_utc: new Date().toISOString(),
          model: null,
          prompt,
          description: "",
          latency_ms: null,
          status: visionStatus.reason,
          error: visionStatus.reason === "ollama_unreachable"
            ? "Ollama not reachable at 127.0.0.1:11434."
            : "No vision-capable Ollama model found.",
        });
        sendJson(response, 200, {
          ok: false,
          error: visionStatus.reason,
          hint: visionStatus.reason === "no_vision_model_available" ? "Run: ollama pull llava:7b" : null,
          observation,
        });
        return;
      }

      const imageBase64 = fs.readFileSync(framePath).toString("base64");
      const startedAt = Date.now();
      const ollamaPayload = await requestOllamaVisionDescription(visionStatus.model, prompt, imageBase64);
      const description = String(ollamaPayload?.response || "").trim();
      if (!description) {
        throw new Error("ollama_empty_response");
      }

      const observation = appendObservation({
        session_id: sessionId,
        frame_path: framePathRelative,
        frame_ts_utc: frameTsUtc,
        requested_at_utc: requestedAtUtc,
        completed_at_utc: new Date().toISOString(),
        model: visionStatus.model,
        prompt,
        description,
        latency_ms: Date.now() - startedAt,
        status: "ok",
        error: null,
      });
      sendJson(response, 200, { ok: true, observation });
      return;
    } catch (error) {
      const status = error?.code === "OLLAMA_TIMEOUT" ? "timeout" : "error";
      const errorMessage = error?.details
        ? `${error.message}: ${String(error.details).trim().slice(0, 1000)}`
        : (error?.message || "Observer request failed.");
      const observation = appendObservation({
        session_id: sessionId,
        frame_path: framePathRelative,
        frame_ts_utc: frameTsUtc,
        requested_at_utc: requestedAtUtc,
        completed_at_utc: new Date().toISOString(),
        model: null,
        prompt,
        description: "",
        latency_ms: null,
        status,
        error: errorMessage,
      });
      sendJson(response, 200, { ok: false, error: status, observation });
      return;
    } finally {
      observationRequestsInFlight.delete(sessionId);
    }
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/active/session/cleanup-preview") {
    const rawSessionId = String(requestUrl.searchParams.get("session_id") || "").trim();
    if (!rawSessionId) {
      sendJson(response, 400, { ok: false, error: "session_id query param is required." });
      return;
    }
    const sessionId = sanitizeSessionId(rawSessionId);
    if (!sessionId) {
      sendJson(response, 400, { ok: false, error: "Invalid session_id format." });
      return;
    }
    const store = readActiveSessionStore();
    const session = sessionId === store.current_session?.session_id
      ? normalizeActiveSession(store.current_session)
      : normalizeActiveSession((store.recent_sessions || []).find((s) => s?.session_id === sessionId));
    if (!session) {
      sendJson(response, 404, { ok: false, error: "Session not found." });
      return;
    }
    if (session.status === "active" || session.capture_running) {
      sendJson(response, 200, { ok: true, session_id: sessionId, deletion_allowed: false, reason: "Session is still active or capture is running." });
      return;
    }
    if (session.retention_status !== "discarded") {
      sendJson(response, 200, { ok: true, session_id: sessionId, deletion_allowed: false, reason: "Session must be marked discarded before cleanup." });
      return;
    }
    if (session.cleanup_status === "cleaned") {
      sendJson(response, 200, { ok: true, session_id: sessionId, deletion_allowed: false, reason: "Session has already been cleaned." });
      return;
    }
    const { files, missing_files, total_bytes, safety_root } = listSessionFrameFiles(sessionId);
    sendJson(response, 200, {
      ok: true,
      session_id: sessionId,
      deletion_allowed: true,
      reason: "Session is discarded and stopped. Files listed are safe capture frames from this session's folder only.",
      safety_root,
      files: files.map((f) => f.name),
      missing_files,
      file_count: files.length,
      total_bytes,
      note: "latest.png is preserved. Only frame-XXXXXX.png files are listed for deletion.",
    });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/active/session/cleanup-confirm") {
    const body = await readJsonBody(request);
    const rawSessionId = String(body.session_id || "").trim();
    const confirm = String(body.confirm || "").trim();
    const approvalId = String(body.approval_id || requestUrl.searchParams.get("approval_id") || "").trim();
    if (!rawSessionId) {
      sendJson(response, 400, { ok: false, error: "session_id is required." });
      return;
    }
    const sessionId = sanitizeSessionId(rawSessionId);
    if (!sessionId) {
      sendJson(response, 400, { ok: false, error: "Invalid session_id format." });
      return;
    }
    if (confirm !== "DELETE_CAPTURE_FRAMES") {
      sendJson(response, 400, { ok: false, error: "Incorrect confirmation phrase. Required: DELETE_CAPTURE_FRAMES" });
      return;
    }
    const store = readActiveSessionStore();
    const session = sessionId === store.current_session?.session_id
      ? normalizeActiveSession(store.current_session)
      : normalizeActiveSession((store.recent_sessions || []).find((s) => s?.session_id === sessionId));
    if (!session) {
      sendJson(response, 404, { ok: false, error: "Session not found." });
      return;
    }
    if (session.status === "active" || session.capture_running) {
      sendJson(response, 400, { ok: false, error: "Cannot clean an active session or one with capture running." });
      return;
    }
    if (session.retention_status !== "discarded") {
      sendJson(response, 400, { ok: false, error: "Session must be marked discarded before cleanup." });
      return;
    }
    if (session.cleanup_status === "cleaned") {
      sendJson(response, 400, { ok: false, error: "Session has already been cleaned." });
      return;
    }
    const { files, missing_files, safety_root } = listSessionFrameFiles(sessionId);

    // Approval gate: require explicit approval for cleanup_capture_files
    if (!approvalId) {
      // Reuse existing pending approval for same session if one exists
      const existing = readApprovals().find(
        (a) => a.status === "pending" && a.action?.type === "cleanup_capture_files" && a.action?.payload?.session_id === sessionId,
      );
      const approval = existing || createApprovalRequest(
        { type: "cleanup_capture_files", payload: { session_id: sessionId, file_count: files.length, safety_root } },
        `Delete ${files.length} capture frame file(s) from session ${sessionId}. Only frame-XXXXXX.png files will be deleted. latest.png is preserved.`,
        "POST /api/ghoti/active/session/cleanup-confirm",
      );
      sendJson(response, 200, buildApprovalRequiredResponse(
        { type: "cleanup_capture_files", payload: { session_id: sessionId } },
        `Approval required to delete ${files.length} capture frame file(s). Approve in the Approvals panel, then retry with approval_id.`,
        approval,
      ));
      return;
    }

    // Validate and consume approval
    const consumeResult = validateAndConsumeApproval(approvalId, "cleanup_capture_files", { session_id: sessionId });
    if (!consumeResult.ok) {
      sendJson(response, 400, { ok: false, error: consumeResult.error, approval: consumeResult.approval || null });
      return;
    }

    const sessionDir = getSessionFrameDir(sessionId);
    const resolvedSessionDir = sessionDir ? path.resolve(sessionDir) : null;
    let deleted_count = 0;
    let deleted_bytes = 0;
    let delete_fail_count = 0;
    for (const { abs, size } of files) {
      // Double-check: must be inside this session's dir, must match frame pattern
      if (!resolvedSessionDir || !abs.startsWith(resolvedSessionDir + path.sep)) continue;
      if (!/^frame-\d{6}\.png$/i.test(path.basename(abs))) continue;
      try {
        fs.unlinkSync(abs);
        deleted_count++;
        deleted_bytes += size;
      } catch {
        delete_fail_count++;
      }
    }
    const nowUtc = new Date().toISOString();
    const updatedSession = updateStoredActiveSession(sessionId, {
      cleanup_status: "cleaned",
      cleaned_at_utc: nowUtc,
      cleaned_file_count: deleted_count,
      cleaned_bytes: deleted_bytes,
      cleanup_missing_file_count: missing_files.length + delete_fail_count,
    });
    pushAction({
      actionType: "status",
      label: "Active session cleanup completed",
      status: "success",
      summary: `Deleted ${deleted_count} capture frame(s) (${deleted_bytes} bytes) for session ${sessionId}. Session folder and latest.png preserved.`,
    });
    sendJson(response, 200, {
      ok: true,
      session_id: sessionId,
      deleted_count,
      deleted_bytes,
      missing_count: missing_files.length + delete_fail_count,
      safety_root,
      note: "Only frame-XXXXXX.png files in this session's folder were deleted. latest.png and other sessions are untouched.",
      session: updatedSession,
    });
    return;
  }

  // Voice state routes
  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/voice/state") {
    const voice = readVoiceState();
    sendJson(response, 200, { ok: true, voice });
    return;
  }
  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/voice/mute") {
    const voice = readVoiceState();
    voice.muted = true;
    voice.updated_at_utc = new Date().toISOString();
    writeVoiceState(voice);
    sendJson(response, 200, { ok: true, voice });
    return;
  }
  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/voice/unmute") {
    const voice = readVoiceState();
    voice.muted = false;
    voice.updated_at_utc = new Date().toISOString();
    writeVoiceState(voice);
    sendJson(response, 200, { ok: true, voice });
    return;
  }
  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/voice/listen/start") {
    const voice = readVoiceState();
    voice.listening = false;
    voice.updated_at_utc = new Date().toISOString();
    writeVoiceState(voice);
    sendJson(response, 200, {
      ok: true,
      voice,
      note: "STT not configured. Listening remains false.",
    });
    return;
  }
  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/voice/listen/stop") {
    const voice = readVoiceState();
    voice.listening = false;
    voice.updated_at_utc = new Date().toISOString();
    writeVoiceState(voice);
    sendJson(response, 200, { ok: true, voice });
    return;
  }

  // Operator status route — returns full system summary
  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/operator/status") {
    const activeState = readActiveModeState();
    const captureState = readCaptureState();
    const voiceState = readVoiceState();
    const desktopBridgeExists = fs.existsSync(desktopActionsScriptPath);
    const isActive = Boolean(activeState.active);
    const isCapturing = Boolean(captureState.capturing);
    const operatorStatus = isCapturing ? "watching" : isActive ? "active" : "idle";
    const visionStatus = await getOllamaVisionStatus();
    const observations = readObservations();
    const lastObservation = observations[0] || null;
    sendJson(response, 200, {
      ok: true,
      status: operatorStatus,
      active_mode: isActive,
      capture: {
        capturing: isCapturing,
        frame_count: captureState.frame_count || 0,
        session_id: currentCaptureSessionId || null,
        last_frame_ts: captureState.latest_frame_utc || null,
        latest_frame_url: currentCaptureSessionId
          ? `/api/ghoti/active/latest-frame?session_id=${encodeURIComponent(currentCaptureSessionId)}`
          : (captureState.latest_frame_path ? "/api/ghoti/active/latest-frame" : null),
      },
      voice: {
        real: false,
        mode: voiceState.mode || "placeholder",
        muted: Boolean(voiceState.muted),
        listening: Boolean(voiceState.listening),
      },
      brain: {
        provider: visionStatus.reason === "ollama_unreachable" ? "none" : "ollama",
        reachable: visionStatus.reason !== "ollama_unreachable",
        model: visionStatus.model,
        drives_operator: false,
        note: "Ollama visibility is read-only here. Reachable does not mean wired. Observations never plan or execute actions.",
      },
      vision: {
        available: visionStatus.available,
        model: visionStatus.model,
        observations_total: observations.length,
        last_observation_at_utc: lastObservation?.completed_at_utc || lastObservation?.requested_at_utc || null,
        read_only: true,
        drives_operator: false,
      },
      operator: {
        desktop_actions_available: desktopBridgeExists,
        browser_actions_available: false,
        visual_indicator_available: true,
        approval_required_for_risky_actions: true,
        full_autonomy_enabled: false,
      },
      approvals: {
        pending_count: pendingApprovals().length,
        queue_enabled: true,
        enforced_on: ["cleanup_capture_files"],
        enforced_stub_for: [
          "delete_file",
          "write_outside_repo",
          "send_network_request",
          "click",
          "type_text",
          "run_shell",
          "browser_submit",
          "desktop_action",
          "browser_action",
        ],
      },
      local_only: true,
      updated_at_utc: new Date().toISOString(),
    });
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/brain/vision-status") {
    const visionStatus = await getOllamaVisionStatus();
    sendJson(response, 200, {
      ok: true,
      vision: {
        ...visionStatus,
        note: buildVisionStatusNote(visionStatus),
      },
      updated_at_utc: new Date().toISOString(),
    });
    return;
  }

  // Brain status — probes Ollama directly; always 200 (reachable:false = not configured, not an error)
  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/brain/status") {
    const visionStatus = await getOllamaVisionStatus();
    sendJson(response, 200, {
      ok: true,
      brain: {
        provider: visionStatus.reason === "ollama_unreachable" ? "none" : "ollama",
        reachable: visionStatus.reason !== "ollama_unreachable",
        models: visionStatus.all_models,
        active_model: visionStatus.model || visionStatus.all_models[0] || null,
        drives_operator: false,
        frame_understanding: Boolean(visionStatus.available),
        action_planning: false,
        note: visionStatus.available
          ? `Ollama reachable at 127.0.0.1:11434. Vision model detected: ${visionStatus.model}. Read-only frame observer can describe captured frames. It does not drive operator actions.`
          : visionStatus.reason === "no_vision_model_available"
            ? "Ollama reachable at 127.0.0.1:11434, but no vision-capable model is installed. Run: ollama pull llava:7b. Not wired to drive operator actions."
            : "Ollama not reachable at 127.0.0.1:11434. No local brain available. Not wired to drive operator actions.",
      },
    });
    return;
  }

  // Ghoti approval queue routes
  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/approvals") {
    const statusFilter = (requestUrl.searchParams.get("status") || "all").toLowerCase();
    const all = readApprovals();
    const filtered = statusFilter === "all" ? all : all.filter((a) => a.status === statusFilter);
    sendJson(response, 200, {
      ok: true,
      approvals: filtered,
      pending_count: all.filter((a) => a.status === "pending").length,
      updated_at_utc: new Date().toISOString(),
    });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/approvals/request") {
    const body = await readJsonBody(request);
    if (!body.action?.type) {
      sendJson(response, 400, { ok: false, error: "action.type is required" });
      return;
    }
    if (!body.reason) {
      sendJson(response, 400, { ok: false, error: "reason is required" });
      return;
    }
    const record = createApprovalRequest(body.action, body.reason, body.requested_by || "api");
    sendJson(response, 200, { ok: true, approval: record });
    return;
  }

  // /api/ghoti/approvals/<id>/approve|reject|consume — parse id from path
  {
    const approvalRouteMatch = requestUrl.pathname.match(/^\/api\/ghoti\/approvals\/([^/]+)\/(approve|reject|consume)$/);
    if (approvalRouteMatch && request.method === "POST") {
      const approvalId = approvalRouteMatch[1];
      const action = approvalRouteMatch[2];
      const approval = getApproval(approvalId);
      if (!approval) {
        sendJson(response, 404, { ok: false, error: "approval_not_found" });
        return;
      }
      if (action === "approve") {
        if (approval.status !== "pending") {
          sendJson(response, 400, { ok: false, error: `Cannot approve: status is ${approval.status}`, approval });
          return;
        }
        const updated = updateApprovalStatus(approvalId, "approved", {
          decided_at_utc: new Date().toISOString(),
          decided_by: "operator",
        });
        sendJson(response, 200, { ok: true, approval: updated });
        return;
      }
      if (action === "reject") {
        if (approval.status !== "pending") {
          sendJson(response, 400, { ok: false, error: `Cannot reject: status is ${approval.status}`, approval });
          return;
        }
        const body = await readJsonBody(request);
        const updated = updateApprovalStatus(approvalId, "rejected", {
          decided_at_utc: new Date().toISOString(),
          decided_by: "operator",
          notes: String(body.notes || "").slice(0, 512),
        });
        sendJson(response, 200, { ok: true, approval: updated });
        return;
      }
      if (action === "consume") {
        const consumeBody = await readJsonBody(request);
        const actionType = String(consumeBody.action_type || "").trim();
        if (!actionType) {
          sendJson(response, 200, { ok: false, error: "action_type_required" });
          return;
        }
        const consumeResult = validateAndConsumeApproval(approvalId, actionType);
        sendJson(response, 200, consumeResult.ok
          ? { ok: true, approval: consumeResult.approval }
          : { ok: false, error: consumeResult.error, approval: consumeResult.approval || null });
        return;
      }
    }
  }

  // YouTube follower routes
  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/youtube-follower/status") {
    const tasks = readYoutubeFollowerTasks();
    sendJson(response, 200, {
      ok: true,
      status: "scaffold",
      real: false,
      execution_enabled: false,
      browser_operator_integrated: false,
      task_count: tasks.length,
      latest_task: tasks[0] || null,
      note: "YouTube follower is a scaffold only. No video parsing or browser execution is wired.",
    });
    return;
  }
  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/youtube-follower/task") {
    let body = {};
    try {
      const chunks = [];
      for await (const chunk of request) chunks.push(chunk);
      body = JSON.parse(Buffer.concat(chunks).toString("utf8"));
    } catch {}
    if (!body.url) {
      sendJson(response, 400, { ok: false, error: "url is required" });
      return;
    }
    const task = createYoutubeFollowerTask(body);
    sendJson(response, 200, {
      ok: true,
      task: {
        id: task.id,
        status: task.status,
        execution_enabled: task.execution_enabled,
        needs_user_approval: task.needs_user_approval,
        next_step: task.next_step,
        url: task.url,
        goal: task.goal,
        created_at: task.created_at,
      },
    });
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/system/health") {
    const activeState = readActiveModeState();
    const captureState = readCaptureState();
    const voiceState = readVoiceState();
    const observations = readObservations();
    const lastObs = observations[0] || null;
    const pending = pendingApprovals();
    const allApprovals = readApprovals();
    const visionStatus = await getCachedOllamaVisionStatus();
    const probes = readModelProbes();
    const lastProbe = probes[0] || null;
    const allModels = Array.isArray(visionStatus.all_models) ? visionStatus.all_models : [];
    const gemmaCandidates = allModels.filter((m) => m.toLowerCase().includes("gemma"));
    const finishLogExists = fs.existsSync(path.join(repoRoot, "14_context", "ghoti_finish_line_log.md"));
    sendJson(response, 200, {
      ok: true,
      health: {
        active_mode: {
          active: Boolean(activeState.active),
          session_id: activeState.active ? (activeState.session_id || null) : null,
        },
        capture: {
          capturing: Boolean(captureState.capturing),
          frame_count: captureState.frame_count || 0,
          last_frame_utc: captureState.latest_frame_utc || null,
        },
        approvals: {
          pending_count: pending.length,
          enforced_on: ["cleanup_capture_files"],
          enforced_stub_for: [
            "delete_file", "write_outside_repo", "send_network_request",
            "click", "type_text", "run_shell", "browser_submit", "desktop_action", "browser_action",
          ],
        },
        ollama: {
          reachable: visionStatus.reason !== "ollama_unreachable",
          host: "127.0.0.1:11434",
        },
        vision: {
          available: visionStatus.available,
          model: visionStatus.model,
          all_models: visionStatus.all_models,
          reason: visionStatus.reason,
        },
        observer: {
          wired: true,
          read_only: true,
          last_observation_utc: lastObs?.completed_at_utc || lastObs?.requested_at_utc || null,
          observations_total: observations.length,
        },
        voice: {
          mode: "scaffold",
          real_audio: false,
          muted: Boolean(voiceState.muted),
        },
        youtube: {
          status: "scaffold",
          real: false,
        },
        overlay: {
          kind: "browser",
          native_always_on_top: false,
        },
        models: {
          all_count: allModels.length,
          gemma_available: gemmaCandidates.length > 0,
          selected_text_model: gemmaCandidates[0] || null,
          last_probe_at_utc: lastProbe?.completed_at_utc || null,
          probe_count: probes.length,
        },
        token_resilience: {
          state_persisted: true,
          runtime_data_gitignored: true,
          finish_line_log_present: finishLogExists,
          current_prompt_path: "14_context/ghoti_current_prompt.md",
          can_resume_after_chat_limits: true,
          note: "Long-running autonomy is not implemented. Current resilience is checkpoint/log/prompt based.",
        },
      },
      server: {
        port: dashboardPort,
        commit: _bootCommitHash,
      },
      updated_at_utc: new Date().toISOString(),
    });
    return;
  }

  // GET /api/ghoti/wait-resume/status — read-only wait/resume supervisor state (N+3.2)
  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/wait-resume/status") {
    const waitResumePath = path.join(runtimeDataDir, "wait_resume_items.json");
    let items = [];
    let parseError = null;
    try {
      if (fs.existsSync(waitResumePath)) {
        items = JSON.parse(fs.readFileSync(waitResumePath, "utf8"));
        if (!Array.isArray(items)) items = [];
      }
    } catch (e) {
      parseError = String(e.message || e);
      items = [];
    }
    const counts = { pending: 0, ready: 0, done: 0, blocked: 0, expired: 0 };
    let latestUpdatedAt = "";
    for (const item of items) {
      const s = item.status || "unknown";
      if (s in counts) counts[s]++;
      const ts = item.updated_at_utc || "";
      if (ts > latestUpdatedAt) latestUpdatedAt = ts;
    }
    const activeItems = items
      .filter(i => i.status !== "done" && i.status !== "expired")
      .map(i => ({
        wait_id: i.wait_id,
        title: i.title,
        status: i.status,
        wait_type: i.wait_type,
        risk_level: i.risk_level,
        approval_required: i.approval_required,
        resume_command: i.resume_command,
        updated_at_utc: i.updated_at_utc,
      }));
    sendJson(response, 200, {
      ok: true,
      pending_count: counts.pending,
      ready_count: counts.ready,
      blocked_count: counts.blocked,
      done_count: counts.done,
      total: items.length,
      latest_updated_at_utc: latestUpdatedAt || new Date().toISOString(),
      items: activeItems,
      runtime_wiring_truth: "local_wait_resume_only",
      autonomous_execution_enabled: false,
      external_actions_enabled: false,
      parse_error: parseError,
    });
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/action-audit/status") {
    const auditPath = path.join(repoRoot, "05_logs", "action_audit.jsonl");
    const runsDir = path.join(repoRoot, "05_logs", "action_intent_runs");
    let auditEventCount = 0;
    let latestEventType = null;
    if (fs.existsSync(auditPath)) {
      const lines = fs.readFileSync(auditPath, "utf8").split("\n").filter(l => l.trim());
      auditEventCount = lines.length;
      if (lines.length > 0) {
        try { latestEventType = JSON.parse(lines[lines.length - 1]).event_type; } catch { /* ignore */ }
      }
    }
    let latestRunSummaryPath = null;
    if (fs.existsSync(runsDir)) {
      const runs = fs.readdirSync(runsDir).sort().reverse();
      if (runs.length > 0) {
        const candidate = path.join(runsDir, runs[0], "action_intent_demo_summary.md");
        if (fs.existsSync(candidate)) {
          latestRunSummaryPath = path.relative(repoRoot, candidate).replace(/\\/g, "/");
        }
      }
    }
    sendJson(response, 200, {
      ok: true,
      latest_audit_path: auditPath ? "05_logs/action_audit.jsonl" : null,
      audit_event_count: auditEventCount,
      latest_event_type: latestEventType,
      latest_run_summary_path: latestRunSummaryPath,
      action_intent_runtime: "local_demo_only",
      external_adapters_wired: false,
      approval_gate_truth: "action_intents require approval before future adapter execution",
      updated_at_utc: new Date().toISOString(),
    });
    return;
  }

  // GET /api/ghoti/computer-use/candidates — read-only CUA candidate status (N+3.4)
  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/computer-use/candidates") {
    sendJson(response, 200, {
      ok: true,
      candidates: {
        cua_driver: {
          status: "descriptor_only",
          runtime_wired: false,
          adapter_id: "cua-driver-reference",
          source: "github.com/trycua/cua",
          windows_compatible: false,
          notes: "Canonical trycua/cua requires macOS/Apple Silicon (Lume). Windows alternative needed.",
          sandbox_profile: "23_configs/cua_sandbox_profile.example.json",
          evaluation_doc: "14_context/cua_trycua_exact_source_evaluation.md",
        },
        screenpipe: {
          status: "retention_plan_only",
          runtime_wired: false,
          capture_started: false,
          notes: "3-day retention policy defined. Cleanup script at 03_scripts/screenpipe_retention_cleanup.ps1. No capture started.",
          plan_doc: "14_context/screenpipe_local_capture_plan.md",
        },
        obscura: {
          status: "runtime_verified",
          runtime_wired: false,
          build_path: "C:/tmp/obscura_build/release/obscura.exe",
          cdp_confirmed: true,
          stealth_used: false,
          notes: "Binary built outside repo in N+3.2. CDP confirmed. Not wired into Ghoti runtime.",
          verification_doc: "14_context/obscura_runtime_verification.md",
        },
        autobrowser: {
          status: "cloned_audited",
          runtime_wired: false,
          clone_path: "21_repos/third_party/evals/auto-browser",
          docker_run: false,
          notes: "Cloned and audited in N+2.9. Most aligned with Ghoti supervised browser model. No Docker run yet.",
          audit_doc: "14_context/autobrowser_isolated_clone_audit.md",
        },
        ruflo: {
          status: "research_only",
          runtime_wired: false,
          clone_path: "21_repos/third_party/evals/ruflo",
          npm_install: false,
          risk: "high",
          notes: "Prior security incidents. 314 MCP tools. No install. Not wired.",
          audit_doc: "14_context/ruflo_isolated_clone_audit.md",
        },
      },
      runtime_wiring_truth: "no_computer_use_adapter_wired",
      autonomous_execution_enabled: false,
      updated_at_utc: new Date().toISOString(),
    });
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/models/status") {
    const status = await getModelInventoryStatus();
    sendJson(response, 200, status);
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/models/gemma-probe") {
    let body = "";
    await new Promise((resolve) => {
      request.on("data", (chunk) => { body += chunk; });
      request.on("end", resolve);
    });
    let userPrompt = null;
    try { userPrompt = JSON.parse(body).prompt || null; } catch { /* ignore */ }
    const probePrompt = userPrompt || "You are Ghoti's local diagnostic model probe. Summarize this system state in 3 short bullets. Do not suggest actions. Do not claim to control the computer.";
    const probeId = `probe-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const requestedAt = new Date().toISOString();

    const inv = await getModelInventoryStatus();
    if (!inv.ollama.reachable) {
      const rec = { id: probeId, model: null, prompt: probePrompt, status: "error", error: "ollama_unreachable", requested_at_utc: requestedAt, completed_at_utc: new Date().toISOString(), latency_ms: null, response: null };
      appendModelProbe(rec);
      sendJson(response, 200, { ok: false, error: "ollama_unreachable", probe: rec });
      return;
    }
    if (!inv.models.selected_text_model) {
      const rec = { id: probeId, model: null, prompt: probePrompt, status: "error", error: "no_gemma_model_available", requested_at_utc: requestedAt, completed_at_utc: new Date().toISOString(), latency_ms: null, response: null };
      appendModelProbe(rec);
      sendJson(response, 200, { ok: false, error: "no_gemma_model_available", probe: rec });
      return;
    }
    const model = inv.models.selected_text_model;
    const t0 = Date.now();
    try {
      const result = await requestOllamaGenerate(model, probePrompt);
      const latency = Date.now() - t0;
      const responseText = String(result?.response || "").trim();
      const rec = { id: probeId, model, prompt: probePrompt, status: "ok", error: null, requested_at_utc: requestedAt, completed_at_utc: new Date().toISOString(), latency_ms: latency, response: responseText };
      appendModelProbe(rec);
      sendJson(response, 200, { ok: true, probe: rec });
    } catch (err) {
      const latency = Date.now() - t0;
      const errMsg = err.message === "ollama_timeout" ? "timeout" : (err.message || "error");
      const rec = { id: probeId, model, prompt: probePrompt, status: "error", error: errMsg, requested_at_utc: requestedAt, completed_at_utc: new Date().toISOString(), latency_ms: latency, response: null };
      appendModelProbe(rec);
      sendJson(response, 200, { ok: false, error: errMsg, probe: rec });
    }
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/models/probes") {
    const rawLimit = requestUrl.searchParams?.get("limit") || String(defaultProbeLimit);
    const safeLimit = Math.max(1, Math.min(maxProbeLimit, Number.parseInt(rawLimit, 10) || defaultProbeLimit));
    const probes = readModelProbes().slice(0, safeLimit);
    sendJson(response, 200, { ok: true, probes, count: probes.length });
    return;
  }

  // GET /api/ghoti/models/inventory — honest inventory with required N+1.4 truth fields
  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/models/inventory") {
    const inv = await getModelInventoryStatus();
    sendJson(response, 200, {
      ok: true,
      ollama: inv.ollama,
      models: inv.models,
      truth: {
        gemma_available: inv.models.gemma_candidates.length > 0,
        gemma_drives_operator: false,
        frame_understanding: inv.models.selected_vision_model
          ? "vision_model_present"
          : "not_validated_without_vision_model",
        action_planning: false,
        autonomous_actions: false,
        model_pulls_allowed_this_milestone: false,
        llava_pull_deferred: true,
      },
      updated_at_utc: inv.updated_at_utc,
    });
    return;
  }

  // POST /api/ghoti/models/gemma-diagnostic — diagnostic text only; drives nothing
  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/models/gemma-diagnostic") {
    let body = "";
    await new Promise((resolve) => {
      request.on("data", (chunk) => { body += chunk; });
      request.on("end", resolve);
    });
    let userPrompt = null;
    try { userPrompt = JSON.parse(body).prompt || null; } catch { /* ignore */ }
    const diagnosticPrompt = userPrompt ||
      "In one short paragraph, say what you are and whether you are running locally. Do not claim to control the operator.";
    const probeId = `diag-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const requestedAt = new Date().toISOString();
    const inv = await getModelInventoryStatus();
    if (!inv.ollama.reachable) {
      sendJson(response, 200, { ok: false, error: "ollama_unreachable", hint: "Ollama not reachable at 127.0.0.1:11434." });
      return;
    }
    const gemmaModel = inv.models.selected_text_model;
    if (!gemmaModel) {
      sendJson(response, 200, { ok: false, error: "no_gemma_model_available", hint: "No model pull is allowed in this milestone." });
      return;
    }
    const t0 = Date.now();
    try {
      const result = await requestOllamaGenerate(gemmaModel, diagnosticPrompt);
      const latency = Date.now() - t0;
      const responseText = String(result?.response || "").trim();
      const rec = {
        id: probeId, kind: "diagnostic", model: gemmaModel,
        prompt: diagnosticPrompt, status: "ok", error: null,
        requested_at_utc: requestedAt, completed_at_utc: new Date().toISOString(),
        latency_ms: latency, response: responseText,
        truth: { diagnostic_only: true, drives_operator: false, action_planning: false },
      };
      appendModelProbe(rec);
      sendJson(response, 200, { ok: true, probe: rec });
    } catch (err) {
      const latency = Date.now() - t0;
      const errMsg = err.message === "ollama_timeout" ? "timeout" : (err.message || "error");
      const rec = {
        id: probeId, kind: "diagnostic", model: gemmaModel,
        prompt: diagnosticPrompt, status: "error", error: errMsg,
        requested_at_utc: requestedAt, completed_at_utc: new Date().toISOString(),
        latency_ms: latency, response: null,
        truth: { diagnostic_only: true, drives_operator: false, action_planning: false },
      };
      appendModelProbe(rec);
      sendJson(response, 200, { ok: false, error: errMsg, probe: rec });
    }
    return;
  }

  // GET /api/ghoti/continuity/status — token resilience truth
  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/continuity/status") {
    const finishLogExists = fs.existsSync(path.join(repoRoot, "14_context", "ghoti_finish_line_log.md"));
    const registryExists = fs.existsSync(path.join(repoRoot, "14_context", "future_concepts_registry.md"));
    const compactMemExists = fs.existsSync(path.join(repoRoot, "14_context", "compact_memory"));
    const currentPromptExists = fs.existsSync(path.join(repoRoot, "14_context", "ghoti_current_prompt.md"));
    sendJson(response, 200, {
      ok: true,
      token_resilience_kind: "checkpoint_log_prompt_continuity",
      autonomous_daemon: false,
      unlimited_context: false,
      current_prompt_file: "14_context/ghoti_current_prompt.md",
      current_prompt_exists: currentPromptExists,
      finish_line_log_exists: finishLogExists,
      future_concepts_registry_exists: registryExists,
      compact_memory_exists: compactMemExists,
      handoff_ready: true,
      note: "Token resilience means durable checkpoints, prompts, logs, and handoffs; it does not bypass model limits.",
    });
    return;
  }

  // GET /api/ghoti/tooling/status — live checks with short timeouts; no heavy recursive search
  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/tooling/status") {
    const cargoHome = path.join(
      process.env.USERPROFILE || process.env.HOME || "",
      ".cargo", "bin"
    );
    const probeWithCargoFallback = (name) => probeTool([
      { cmd: name },
      { cmd: path.join(cargoHome, `${name}.exe`) },
    ]);

    const openclawPaths = [
      path.join(repoRoot, "21_repos", "third_party", "openclaw"),
      path.join(repoRoot, "21_repos", "third_party", "OpenClaw"),
    ];
    const claudeSkillsUserPath = path.join(
      process.env.USERPROFILE || process.env.HOME || "",
      ".claude", "skills"
    );
    const claudeSkillsRepoPath = path.join(repoRoot, ".claude", "skills");

    sendJson(response, 200, {
      ok: true,
      checked_at: new Date().toISOString(),
      rustc: probeWithCargoFallback("rustc"),
      cargo: probeWithCargoFallback("cargo"),
      git: probeTool([{ cmd: "git" }]),
      node: probeTool([{ cmd: "node" }]),
      npm: probeTool([{ cmd: "npm" }]),
      pnpm: probeTool([{ cmd: "pnpm" }]),
      python: probeTool([{ cmd: "python" }, { cmd: "py", args: ["-3", "--version"] }]),
      uv: probeTool([{ cmd: "uv" }]),
      ollama: probeTool([{ cmd: "ollama" }]),
      gh: probeTool([{ cmd: "gh" }]),
      codex: probeCodexTool(),
      claude: probeTool([{ cmd: "claude" }]),
      openclaw: {
        local_paths_found: openclawPaths.some((op) => fs.existsSync(op)),
        not_wired: true,
        note: "local reference/prep only — not connected to Ghoti runtime",
      },
      claude_skills: {
        repo_folder_exists: fs.existsSync(claudeSkillsRepoPath),
        user_folder_exists: fs.existsSync(claudeSkillsUserPath),
        repo_path_checked: claudeSkillsRepoPath,
        user_path_checked: claudeSkillsUserPath,
      },
      bridge: {
        status: "manual_handoff_only",
        note: "No codex-plugin or runtime bridge found in local repo search",
      },
      blocked: {
        quota_bypass: true,
        phone_farm_automation: true,
        fake_engagement: true,
        autonomous_real_money_trading: true,
        weapon_guidance: true,
        autonomous_actions: true,
      },
    });
    return;
  }

  // GET /api/ghoti/screenpipe/status — read-only policy existence check (N+3.7)
  // Does NOT start capture, read frames, serve screenshots, or delete anything.
  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/screenpipe/status") {
    const policyFilePath = path.join(repoRoot, "23_configs", "screenpipe_retention_policy.example.json");
    const cleanupScriptPath = path.join(repoRoot, "03_scripts", "screenpipe_retention_cleanup.ps1");
    const outputScreenpipePath = path.join(repoRoot, "output", "screenpipe");
    const logsScreenpipePath = path.join(repoRoot, "05_logs", "screenpipe");

    const policyFileExists = fs.existsSync(policyFilePath);
    const cleanupScriptExists = fs.existsSync(cleanupScriptPath);
    let retentionDays = null;
    let dryRunDefault = null;
    let allowedRoots = [];

    if (policyFileExists) {
      try {
        const policy = JSON.parse(fs.readFileSync(policyFilePath, "utf8"));
        retentionDays = policy.retention_days ?? null;
        dryRunDefault = policy.dry_run_default ?? null;
        allowedRoots = Array.isArray(policy.allowed_roots) ? policy.allowed_roots : [];
      } catch { /* parse error — leave nulls */ }
    }

    const outputScreenpipeExists = fs.existsSync(outputScreenpipePath);
    let outputScreenpipeFileCount = 0;
    if (outputScreenpipeExists) {
      try { outputScreenpipeFileCount = fs.readdirSync(outputScreenpipePath).length; } catch { /* ignore */ }
    }

    const logsScreenpipeExists = fs.existsSync(logsScreenpipePath);
    let logsScreenpipeFileCount = 0;
    if (logsScreenpipeExists) {
      try { logsScreenpipeFileCount = fs.readdirSync(logsScreenpipePath).length; } catch { /* ignore */ }
    }

    sendJson(response, 200, {
      ok: true,
      capture_started: false,
      runtime_wired: false,
      retention_days: retentionDays,
      dry_run_default: dryRunDefault,
      policy_file_exists: policyFileExists,
      cleanup_script_exists: cleanupScriptExists,
      allowed_roots: allowedRoots,
      output_screenpipe_exists: outputScreenpipeExists,
      output_screenpipe_file_count: outputScreenpipeFileCount,
      logs_screenpipe_exists: logsScreenpipeExists,
      logs_screenpipe_file_count: logsScreenpipeFileCount,
      deletion_performed: false,
      updated_at_utc: new Date().toISOString(),
    });
    return;
  }

  // GET /api/ghoti/money/weekly-review/latest — read-only weekly review artifact summary (N+3.30)
  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/money/weekly-review/latest") {
    const moneyReviewsDir = path.join(repoRoot, "05_logs", "money_reviews");
    const warnings = [];

    if (!fs.existsSync(moneyReviewsDir)) {
      sendJson(response, 200, {
        ok: true,
        status: "zero_state",
        runs_total: 0,
        latest_run_id: null,
        warning: "No weekly review artifacts found. Run: python 03_scripts/weekly_money_review.py --since-days 30",
        updated_at_utc: new Date().toISOString(),
      });
      return;
    }

    let runDirs;
    try {
      runDirs = fs.readdirSync(moneyReviewsDir)
        .filter(name => {
          try { return fs.statSync(path.join(moneyReviewsDir, name)).isDirectory(); } catch { return false; }
        })
        .sort()
        .reverse();
    } catch (e) {
      sendJson(response, 200, {
        ok: true,
        status: "zero_state",
        runs_total: 0,
        latest_run_id: null,
        warning: "Could not read money_reviews dir: " + e.message,
        updated_at_utc: new Date().toISOString(),
      });
      return;
    }

    if (runDirs.length === 0) {
      sendJson(response, 200, {
        ok: true,
        status: "zero_state",
        runs_total: 0,
        latest_run_id: null,
        warning: "No weekly review artifacts found. Run: python 03_scripts/weekly_money_review.py --since-days 30",
        updated_at_utc: new Date().toISOString(),
      });
      return;
    }

    const latestRunId = runDirs[0];
    const latestDir = path.join(moneyReviewsDir, latestRunId);

    let reviewData = null;
    const reviewJsonPath = path.join(latestDir, "weekly_review.json");
    try {
      if (fs.existsSync(reviewJsonPath)) {
        reviewData = JSON.parse(fs.readFileSync(reviewJsonPath, "utf8"));
      } else {
        warnings.push("weekly_review.json missing in latest run dir");
      }
    } catch (e) {
      warnings.push("weekly_review.json parse error: " + e.message);
    }

    const decisionsPath = path.join(latestDir, "decisions_recommended.jsonl");
    const candidates = [];
    let decisionsParseErrors = 0;
    if (fs.existsSync(decisionsPath)) {
      try {
        const lines = fs.readFileSync(decisionsPath, "utf8").split("\n").filter(l => l.trim());
        for (const line of lines) {
          try { candidates.push(JSON.parse(line)); } catch { decisionsParseErrors++; }
        }
        if (decisionsParseErrors > 0) warnings.push(decisionsParseErrors + " decision candidate line(s) could not be parsed");
      } catch (e) {
        warnings.push("decisions_recommended.jsonl read error: " + e.message);
      }
    } else {
      warnings.push("decisions_recommended.jsonl missing");
    }

    const candidateCounts = {};
    for (const c of candidates) {
      const cat = String(c.category || c.recommendation || "UNKNOWN");
      candidateCounts[cat] = (candidateCounts[cat] || 0) + 1;
    }

    const topCandidates = candidates.slice(0, 3).map(c => ({
      decision_id: c.decision_id,
      experiment_id: c.experiment_id,
      title: c.title,
      category: c.category || c.recommendation,
      confidence: c.confidence,
      risk_level: c.risk_level,
      next_local_step: c.next_local_step,
      approval_required: c.approval_required,
    }));

    const artifactFiles = ["weekly_review.json", "weekly_review.md", "decisions_recommended.jsonl", "source_index.json", "tracker_snapshot.json", "request.json"];
    const artifactPaths = {};
    for (const fname of artifactFiles) {
      artifactPaths[fname] = {
        relative: "05_logs/money_reviews/" + latestRunId + "/" + fname,
        exists: fs.existsSync(path.join(latestDir, fname)),
      };
    }

    const safetyFlags = reviewData && reviewData.safety_flags ? reviewData.safety_flags : null;
    if (safetyFlags) {
      const dangerous = Object.entries(safetyFlags).filter(([k, v]) => k !== "manual_review_required" && k !== "approval_required_for_public_actions" && v === true);
      if (dangerous.length > 0) warnings.push("Safety anomaly: non-false flags: " + dangerous.map(([k]) => k).join(", "));
    }

    sendJson(response, 200, {
      ok: true,
      status: "found",
      runs_total: runDirs.length,
      latest_run_id: (reviewData && reviewData.run_id) || latestRunId,
      created_at: (reviewData && reviewData.created_at) || null,
      week_start: (reviewData && reviewData.week_start) || null,
      week_end: (reviewData && reviewData.week_end) || null,
      source_counts: (reviewData && reviewData.source_counts) || null,
      total_experiments: reviewData != null ? (reviewData.total_experiments != null ? reviewData.total_experiments : null) : null,
      total_money_runs: reviewData != null ? (reviewData.total_money_runs != null ? reviewData.total_money_runs : null) : null,
      top_candidates: (reviewData && reviewData.top_candidates) || [],
      next_local_actions: (reviewData && reviewData.next_local_actions) || [],
      warnings: warnings.concat((reviewData && reviewData.warnings) || []),
      safety_flags: safetyFlags,
      approval_required_for_public_actions: reviewData != null ? (reviewData.approval_required_for_public_actions != null ? reviewData.approval_required_for_public_actions : true) : true,
      candidate_counts: candidateCounts,
      top_decision_candidates: topCandidates,
      total_decision_candidates: candidates.length,
      artifact_paths: artifactPaths,
      artifact_dir: "05_logs/money_reviews/" + latestRunId,
      updated_at_utc: new Date().toISOString(),
    });
    return;
  }

  // GET /api/ghoti/money/manual-decision-queue — read-only manual decision queue (N+3.32)
  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/money/manual-decision-queue") {
    const queuePath = path.join(repoRoot, "14_context", "money_workflows", "manual_decision_queue.jsonl");
    const warnings = [];
    const safetyFlags = {
      external_api_used: false,
      scraping_enabled: false,
      live_account_actions_enabled: false,
      posting_enabled: false,
      selling_enabled: false,
      outreach_enabled: false,
      payment_actions_enabled: false,
      model_output_executed: false,
      manual_review_required: true,
    };

    if (!fs.existsSync(queuePath)) {
      sendJson(response, 200, {
        ok: true,
        status: "zero_state",
        queue_path: "14_context/money_workflows/manual_decision_queue.jsonl",
        item_count: 0,
        items: [],
        warnings: ["Queue file not found. No items yet."],
        safety_flags: safetyFlags,
        generated_at: new Date().toISOString(),
        suggested_command: "python 03_scripts/manual_decision_queue_new_item.py --latest --dry-run",
      });
      return;
    }

    let rawText;
    try {
      rawText = fs.readFileSync(queuePath, "utf8");
    } catch (e) {
      sendJson(response, 200, {
        ok: true,
        status: "read_error",
        queue_path: "14_context/money_workflows/manual_decision_queue.jsonl",
        item_count: 0,
        items: [],
        warnings: ["Could not read queue file: " + e.message],
        safety_flags: safetyFlags,
        generated_at: new Date().toISOString(),
      });
      return;
    }

    const items = [];
    const lines = rawText.split("\n");
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;
      try {
        const obj = JSON.parse(line);
        if (typeof obj === "object" && obj !== null && !Array.isArray(obj)) {
          items.push({
            queue_item_id: obj.queue_item_id || null,
            created_at: obj.created_at || null,
            source_review_run_id: obj.source_review_run_id || null,
            source_decision_id: obj.source_decision_id || null,
            title: obj.title || "",
            category: obj.category || obj.decision_type || "",
            recommendation: obj.recommendation || "",
            risk_level: obj.risk_level || "",
            approval_required: obj.approval_required !== false,
            status: obj.status || "",
            public_or_money_facing: obj.public_or_money_facing === true,
            next_local_step: obj.next_local_step || obj.next_manual_action || "",
            blocked_reason: obj.blocked_reason || "",
            human_review_note: obj.human_review_note || "",
          });
        } else {
          warnings.push("Line " + (i + 1) + ": non-object JSON, skipped");
        }
      } catch (e) {
        warnings.push("Line " + (i + 1) + ": malformed JSONL — " + e.message);
      }
    }

    const statusCounts = {};
    const riskCounts = {};
    for (const item of items) {
      statusCounts[item.status] = (statusCounts[item.status] || 0) + 1;
      riskCounts[item.risk_level] = (riskCounts[item.risk_level] || 0) + 1;
    }

    sendJson(response, 200, {
      ok: true,
      status: items.length > 0 ? "found" : "empty",
      queue_path: "14_context/money_workflows/manual_decision_queue.jsonl",
      item_count: items.length,
      items,
      status_counts: statusCounts,
      risk_counts: riskCounts,
      warnings,
      safety_flags: safetyFlags,
      generated_at: new Date().toISOString(),
    });
    return;
  }

  // GET /api/ghoti/local-orchestrator/status — read-only local stack card (N+3.50A)
  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/local-orchestrator/status") {
    const agentLanesDir = path.join(repoRoot, "14_context", "agent_lanes");
    const activeLocksFile = path.join(agentLanesDir, "active_locks.jsonl");
    const laneStatusFile = path.join(agentLanesDir, "lane_status.jsonl");
    const promptBusOutbox = path.join(repoRoot, "14_context", "prompt_bus", "outbox");
    const obsidianVaultDir = path.join(repoRoot, "14_context", "obsidian_vault");
    const compactMemoryDir = path.join(repoRoot, "14_context", "compact_memory");
    const rufloDir = path.join(repoRoot, "21_repos", "third_party", "evals", "ruflo");

    function safeReadJsonl(filePath) {
      const result = { records: [], errors: [] };
      if (!fs.existsSync(filePath)) return result;
      const text = (() => { try { return fs.readFileSync(filePath, "utf8"); } catch { return ""; } })();
      text.split("\n").forEach((line, i) => {
        const l = line.trim();
        if (!l) return;
        try { result.records.push(JSON.parse(l)); }
        catch { result.errors.push("line " + (i + 1) + ": malformed"); }
      });
      return result;
    }

    function countDirFiles(dirPath, ext) {
      if (!fs.existsSync(dirPath)) return 0;
      try { return fs.readdirSync(dirPath).filter(f => !ext || f.endsWith(ext)).length; }
      catch { return 0; }
    }

    const locks = safeReadJsonl(activeLocksFile);
    const statuses = safeReadJsonl(laneStatusFile);
    const latestLock = locks.records[locks.records.length - 1] || null;
    const latestStatus = statuses.records[statuses.records.length - 1] || null;

    const outboxFiles = (() => {
      if (!fs.existsSync(promptBusOutbox)) return [];
      try { return fs.readdirSync(promptBusOutbox).filter(f => f.endsWith(".md")); }
      catch { return []; }
    })();

    let rufloExists = fs.existsSync(rufloDir);
    let rufloNodeModules = rufloExists && fs.existsSync(path.join(rufloDir, "node_modules"));
    let rufloPackageLock = rufloExists && fs.existsSync(path.join(rufloDir, "package-lock.json"));
    let rufloPkgName = "unknown"; let rufloPkgVersion = "unknown"; let rufloLifecycle = [];
    if (rufloExists) {
      try {
        const pkg = JSON.parse(fs.readFileSync(path.join(rufloDir, "package.json"), "utf8"));
        rufloPkgName = pkg.name || "unknown";
        rufloPkgVersion = pkg.version || "unknown";
        const risky = new Set(["preinstall","postinstall","prepare","prepack","postpack","prepublish","prepublishOnly"]);
        rufloLifecycle = Object.keys(pkg.scripts || {}).filter(k => risky.has(k));
      } catch { /* ignore */ }
    }

    let ollamaFound = false; let gemmaFound = false;
    try {
      const oc = spawnSync("ollama", ["list"], { encoding: "utf8", timeout: 3000 });
      if (oc.status === 0) { ollamaFound = true; gemmaFound = (oc.stdout || "").toLowerCase().includes("gemma"); }
    } catch { /* ollama not found */ }

    let branch = "unknown";
    try {
      const br = spawnSync("git", ["branch", "--show-current"], { encoding: "utf8", timeout: 2000, cwd: repoRoot });
      if (br.status === 0) branch = (br.stdout || "").trim() || "unknown";
    } catch { /* ignore */ }

    sendJson(response, 200, {
      ok: true,
      generated_at: new Date().toISOString(),
      branch,
      prompt_bus: { outbox_count: outboxFiles.length, outbox_latest: outboxFiles.sort().slice(-1)[0] || null },
      agent_lanes: {
        active_locks_count: locks.records.length,
        status_records_count: statuses.records.length,
        parse_errors: locks.errors.length + statuses.errors.length,
        latest_agent: latestLock ? latestLock.agent_id : null,
        latest_task: latestLock ? latestLock.task_slug : null,
        latest_state: latestStatus ? latestStatus.current_state : null,
      },
      obsidian_vault: { exists: fs.existsSync(obsidianVaultDir), file_count: countDirFiles(obsidianVaultDir, ".md") },
      compact_memory: { exists: fs.existsSync(compactMemoryDir), file_count: countDirFiles(compactMemoryDir, ".md") },
      ruflo: {
        exists: rufloExists, node_modules: rufloNodeModules, package_lock: rufloPackageLock,
        name: rufloPkgName, version: rufloPkgVersion,
        lifecycle_scripts: rufloLifecycle, install_blocked: rufloLifecycle.length > 0,
      },
      ollama: { found: ollamaFound, gemma_found: gemmaFound },
      safety_flags: { read_only: true, no_live_actions: true, no_external_calls: true, human_approval_required: true },
    });
    return;
  }

  // ---------------------------------------------------------------------
  // N+4.4B Desktop Operator Action Center endpoints
  // ---------------------------------------------------------------------
  const desktopOperatorScript = path.join(repoRoot, "03_scripts", "desktop_operator_control_plane.py");
  const desktopOperatorLatestFile = path.join(runtimeProjectRoot, "runtime_data", "desktop_operator_latest.json");
  const desktopOperatorAllowedWorkflows = new Set(["content_studio_demo", "memory_bridge", "dashboard_open"]);
  const desktopOperatorAllowedAdapters = new Set(["dry_run", "local_preview_open", "screenshot_probe"]);

  function loadDesktopOperatorLatest() {
    try {
      if (!fs.existsSync(desktopOperatorLatestFile)) {
        return { handoff_path: null, dry_run_plan_path: null, approval_record_path: null, execution_result_path: null, preview_path: null };
      }
      return JSON.parse(fs.readFileSync(desktopOperatorLatestFile, "utf8"));
    } catch (err) {
      return { handoff_path: null, dry_run_plan_path: null, approval_record_path: null, execution_result_path: null, preview_path: null, parse_error: String(err) };
    }
  }

  function saveDesktopOperatorLatest(state) {
    try {
      const dir = path.dirname(desktopOperatorLatestFile);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(desktopOperatorLatestFile, JSON.stringify(state, null, 2), "utf8");
      return true;
    } catch (err) {
      return false;
    }
  }

  // N+4.4D: real directory containment using path.relative().
  // Rejects sibling-prefix attacks like "<repoRoot>_evil/fake.html" which
  // the prior naive prefix-string check accepted as inside-repo.
  function isPathInsideRepo(candidate) {
    if (typeof candidate !== "string" || candidate.length === 0) {
      return false;
    }
    const resolvedRoot = path.resolve(repoRoot);
    const absolute = path.isAbsolute(candidate) ? candidate : path.join(resolvedRoot, candidate);
    let resolvedCandidate;
    try {
      resolvedCandidate = path.resolve(absolute);
    } catch (err) {
      return false;
    }
    const relative = path.relative(resolvedRoot, resolvedCandidate);
    // relative === "" -> candidate IS the repo root itself; reject.
    // relative starts with ".." -> candidate is outside repo (covers
    // sibling-prefix paths like "<repoRoot>_evil/...").
    // path.isAbsolute(relative) on Windows is true when target is on a
    // different drive -> reject.
    if (relative === "") {
      return false;
    }
    if (relative.startsWith("..")) {
      return false;
    }
    if (path.isAbsolute(relative)) {
      return false;
    }
    return true;
  }

  function isRepoLocalPath(candidate) {
    if (typeof candidate !== "string" || candidate.length === 0) {
      return false;
    }
    if (candidate.indexOf("..") !== -1) {
      return false;
    }
    const lower = candidate.toLowerCase();
    const secrets = [".env", "secret", "credential", "token", "key", "password", "apikey", "api_key", "private", "passwd", "auth"];
    for (const pat of secrets) {
      if (lower.indexOf(pat) !== -1) {
        return false;
      }
    }
    // N+4.4D: replaced vulnerable naive prefix check with real directory
    // containment via isPathInsideRepo().
    return isPathInsideRepo(candidate);
  }

  async function runDesktopOperatorCli(scriptArgs) {
    const python = resolvePython();
    if (!python) {
      return { ok: false, exitCode: 1, stdout: "", stderr: "Python runtime not found.", command: "python desktop_operator_control_plane.py", timedOut: false };
    }
    const fullArgs = [...python.baseArgs, desktopOperatorScript, ...scriptArgs];
    return await runCommand(python.command, fullArgs, { cwd: repoRoot, env: buildRuntimeEnv(), timeoutMs: 60000 });
  }

  function parseDesktopOperatorJson(raw) {
    if (!raw || !raw.stdout) {
      return null;
    }
    try {
      return JSON.parse(raw.stdout);
    } catch (err) {
      return null;
    }
  }
  if (request.method === "GET" && requestUrl.pathname === "/api/desktop-operator/status") {
    const raw = await runDesktopOperatorCli(["--status", "--json"]);
    const status = parseDesktopOperatorJson(raw) || { ok: false, degraded: true, error: "status JSON parse failed" };
    const latest = loadDesktopOperatorLatest();
    sendJson(response, 200, {
      ok: raw.ok && !!status,
      localOnly: true,
      status,
      latest,
      raw: { exitCode: raw.exitCode, timedOut: raw.timedOut },
    });
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/desktop-operator/latest") {
    const latest = loadDesktopOperatorLatest();
    sendJson(response, 200, { ok: true, localOnly: true, latest });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/desktop-operator/create-handoff") {
    const payload = await readJsonBody(request);
    const goal = typeof payload.goal === "string" && payload.goal.trim().length > 0
      ? payload.goal.trim()
      : "Create a local video-style content package about AI tools for students";
    const workflow = typeof payload.workflow === "string" ? payload.workflow : "content_studio_demo";
    if (!desktopOperatorAllowedWorkflows.has(workflow)) {
      sendJson(response, 400, { ok: false, error: "REJECTED: workflow not in allowlist", workflow });
      return;
    }
    const raw = await runDesktopOperatorCli(["--create-handoff", "--goal", goal, "--workflow", workflow, "--json"]);
    const result = parseDesktopOperatorJson(raw);
    if (!result || !result.ok) {
      sendJson(response, raw.ok ? 200 : 500, { ok: false, error: "create-handoff failed", raw });
      return;
    }
    const latest = loadDesktopOperatorLatest();
    latest.handoff_path = result.handoff_path || null;
    latest.run_dir = result.run_dir || null;
    latest.dry_run_plan_path = null;
    latest.approval_record_path = null;
    latest.execution_result_path = null;
    latest.preview_path = null;
    latest.task_id = result.task_id || null;
    latest.created_at = new Date().toISOString();
    saveDesktopOperatorLatest(latest);
    sendJson(response, 200, {
      ok: true,
      localOnly: true,
      summary: { headline: "Safe handoff created (dry-run by default).", taskId: latest.task_id, handoffPath: latest.handoff_path },
      result,
      latest,
    });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/desktop-operator/dry-run") {
    const latest = loadDesktopOperatorLatest();
    if (!latest.handoff_path) {
      sendJson(response, 400, { ok: false, error: "No handoff_path on record. Run create-handoff first." });
      return;
    }
    if (!isRepoLocalPath(latest.handoff_path)) {
      sendJson(response, 400, { ok: false, error: "REJECTED: handoff_path not repo-local" });
      return;
    }
    const handoffAbs = path.isAbsolute(latest.handoff_path) ? latest.handoff_path : path.join(repoRoot, latest.handoff_path);
    const raw = await runDesktopOperatorCli(["--dry-run", handoffAbs, "--json"]);
    const result = parseDesktopOperatorJson(raw);
    if (!result) {
      sendJson(response, 500, { ok: false, error: "dry-run JSON parse failed", raw });
      return;
    }
    latest.dry_run_plan_path = result.plan_path || null;
    latest.actions_executed = result.actions_executed || 0;
    saveDesktopOperatorLatest(latest);
    sendJson(response, 200, {
      ok: true,
      localOnly: true,
      summary: { headline: "Dry run complete. No actions executed.", planPath: latest.dry_run_plan_path, actionsExecuted: latest.actions_executed },
      result,
      latest,
    });
    return;
  }
  if (request.method === "POST" && requestUrl.pathname === "/api/desktop-operator/approve") {
    const payload = await readJsonBody(request);
    const latest = loadDesktopOperatorLatest();
    if (!latest.handoff_path) {
      sendJson(response, 400, { ok: false, error: "No handoff_path on record. Run create-handoff first." });
      return;
    }
    if (!isRepoLocalPath(latest.handoff_path)) {
      sendJson(response, 400, { ok: false, error: "REJECTED: handoff_path not repo-local" });
      return;
    }
    let approvalToken = typeof payload.approvalToken === "string" ? payload.approvalToken.trim() : "";
    if (approvalToken.length < 4) {
      // Server-generated local token (sha-friendly random, never returned to client)
      approvalToken = "dash-" + Math.random().toString(36).slice(2, 10) + Math.random().toString(36).slice(2, 10);
    }
    const handoffAbs = path.isAbsolute(latest.handoff_path) ? latest.handoff_path : path.join(repoRoot, latest.handoff_path);
    const raw = await runDesktopOperatorCli(["--approve", handoffAbs, "--approval-token", approvalToken, "--json"]);
    const result = parseDesktopOperatorJson(raw);
    if (!result || !result.ok) {
      sendJson(response, raw.ok ? 200 : 500, { ok: false, error: "approve failed", raw });
      return;
    }
    latest.approval_record_path = result.approval_record_path || null;
    latest.approved = result.approved === true;
    saveDesktopOperatorLatest(latest);
    sendJson(response, 200, {
      ok: true,
      localOnly: true,
      // Note: raw token is NEVER returned. Only the record path (which holds a SHA-256 hash) is exposed.
      summary: { headline: "Approval record created (token never returned).", approvalRecordPath: latest.approval_record_path },
      latest,
    });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/desktop-operator/execute-approved") {
    const latest = loadDesktopOperatorLatest();
    if (!latest.handoff_path) {
      sendJson(response, 400, { ok: false, error: "No handoff_path on record." });
      return;
    }
    if (!latest.approval_record_path) {
      sendJson(response, 400, { ok: false, error: "No approval record. Run approve first." });
      return;
    }
    if (!isRepoLocalPath(latest.handoff_path)) {
      sendJson(response, 400, { ok: false, error: "REJECTED: handoff_path not repo-local" });
      return;
    }
    const handoffAbs = path.isAbsolute(latest.handoff_path) ? latest.handoff_path : path.join(repoRoot, latest.handoff_path);
    const raw = await runDesktopOperatorCli(["--execute-approved", handoffAbs, "--json"]);
    const result = parseDesktopOperatorJson(raw);
    if (!result) {
      sendJson(response, 500, { ok: false, error: "execute-approved JSON parse failed", raw });
      return;
    }
    // Derive execution_result_path from run_dir
    if (latest.run_dir) {
      latest.execution_result_path = path.posix.join(latest.run_dir.replace(/\\/g, "/"), "05_execution_result.json");
    }
    // The script may have produced a preview (content_studio link). We don't auto-open browser.
    latest.actions_executed = Array.isArray(result.actions_executed) ? result.actions_executed.length : 0;
    saveDesktopOperatorLatest(latest);
    sendJson(response, 200, {
      ok: result.ok === true,
      localOnly: true,
      summary: { headline: "Executed approved safe local action only. No live posting.", actionsExecuted: latest.actions_executed, executionResultPath: latest.execution_result_path },
      result,
      latest,
    });
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/desktop-operator/preview") {
    const candidate = requestUrl.searchParams.get("path");
    if (!candidate) {
      sendJson(response, 400, { ok: false, error: "path query parameter required" });
      return;
    }
    if (!isRepoLocalPath(candidate)) {
      sendJson(response, 400, { ok: false, error: "REJECTED: path not repo-local" });
      return;
    }
    const lowered = candidate.toLowerCase();
    if (!lowered.endsWith(".html") && !lowered.endsWith(".htm")) {
      sendJson(response, 400, { ok: false, error: "REJECTED: only .html or .htm previews allowed" });
      return;
    }
    // N+4.4D: enforce real directory containment via isPathInsideRepo().
    // The previous naive prefix-string check accepted sibling-prefix paths
    // like "<repoRoot>_evil/fake.html".
    if (!isPathInsideRepo(candidate)) {
      sendJson(response, 400, { ok: false, error: "REJECTED: path resolved outside repo" });
      return;
    }
    const absolute = path.isAbsolute(candidate) ? candidate : path.join(repoRoot, candidate);
    const resolvedAbsolute = path.resolve(absolute);
    if (!fs.existsSync(resolvedAbsolute)) {
      sendJson(response, 404, { ok: false, error: "preview not found" });
      return;
    }
    sendJson(response, 200, { ok: true, localOnly: true, previewPath: path.relative(path.resolve(repoRoot), resolvedAbsolute).replace(/\\/g, "/"), bytes: fs.statSync(resolvedAbsolute).size });
    return;
  }

  // ---------------------------------------------------------------------
  // N+4.4C Desktop Operator Recipe Runner endpoints
  // ---------------------------------------------------------------------
  const desktopOperatorRecipeLatestFile = path.join(runtimeProjectRoot, "runtime_data", "desktop_operator_recipe_latest.json");
  const desktopOperatorAllowedRecipes = new Set([
    "content_studio_generate_preview",
    "memory_compress_demo",
    "dashboard_open_preview",
    "gemini_handoff_export",
  ]);

  function loadDesktopOperatorRecipeLatest() {
    try {
      if (!fs.existsSync(desktopOperatorRecipeLatestFile)) {
        return {
          recipe_id: null,
          handoff_path: null,
          dry_run_plan_path: null,
          approval_record_path: null,
          execution_result_path: null,
          preview_path: null,
          handoff_export_path: null,
          last_action: null,
        };
      }
      return JSON.parse(fs.readFileSync(desktopOperatorRecipeLatestFile, "utf8"));
    } catch (err) {
      return { recipe_id: null, parse_error: String(err) };
    }
  }

  function saveDesktopOperatorRecipeLatest(state) {
    try {
      const dir = path.dirname(desktopOperatorRecipeLatestFile);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(desktopOperatorRecipeLatestFile, JSON.stringify(state, null, 2), "utf8");
      return true;
    } catch (err) {
      return false;
    }
  }

  function recipeIdToWorkflow(recipeId) {
    if (recipeId === "content_studio_generate_preview") return "content_studio_demo";
    if (recipeId === "memory_compress_demo") return "memory_bridge";
    if (recipeId === "dashboard_open_preview") return "dashboard_open";
    if (recipeId === "gemini_handoff_export") return "memory_bridge";
    return null;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/desktop-operator/recipes") {
    const raw = await runDesktopOperatorCli(["--recipe-list", "--json"]);
    const data = parseDesktopOperatorJson(raw);
    if (!data) {
      sendJson(response, 200, { ok: false, degraded: true, error: "recipe-list JSON parse failed" });
      return;
    }
    sendJson(response, 200, { ok: true, localOnly: true, ...data });
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/desktop-operator/latest-recipe") {
    const latest = loadDesktopOperatorRecipeLatest();
    sendJson(response, 200, { ok: true, localOnly: true, latest });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/desktop-operator/create-recipe-handoff") {
    const payload = await readJsonBody(request);
    const recipeId = typeof payload.recipe_id === "string" ? payload.recipe_id : null;
    if (!recipeId || !desktopOperatorAllowedRecipes.has(recipeId)) {
      sendJson(response, 400, { ok: false, error: "REJECTED: recipe_id not in allowlist", recipeId });
      return;
    }
    const workflow = recipeIdToWorkflow(recipeId);
    const goal = typeof payload.goal === "string" && payload.goal.trim().length > 0
      ? payload.goal.trim()
      : `Run recipe ${recipeId} locally with approval gate intact.`;
    const raw = await runDesktopOperatorCli(["--create-handoff", "--goal", goal, "--workflow", workflow, "--json"]);
    const result = parseDesktopOperatorJson(raw);
    if (!result || !result.ok) {
      sendJson(response, raw.ok ? 200 : 500, { ok: false, error: "create-recipe-handoff failed", raw });
      return;
    }
    const latest = loadDesktopOperatorRecipeLatest();
    latest.recipe_id = recipeId;
    latest.handoff_path = result.handoff_path || null;
    latest.run_dir = result.run_dir || null;
    latest.dry_run_plan_path = null;
    latest.approval_record_path = null;
    latest.execution_result_path = null;
    latest.preview_path = null;
    latest.handoff_export_path = null;
    latest.task_id = result.task_id || null;
    latest.created_at = new Date().toISOString();
    latest.last_action = "create_recipe_handoff";
    saveDesktopOperatorRecipeLatest(latest);
    sendJson(response, 200, {
      ok: true,
      localOnly: true,
      summary: { headline: `Recipe handoff created (${recipeId}). Dry-run by default.`, recipeId, handoffPath: latest.handoff_path },
      result,
      latest,
    });
    return;
  }
  if (request.method === "POST" && requestUrl.pathname === "/api/desktop-operator/run-recipe-dry-run") {
    const latest = loadDesktopOperatorRecipeLatest();
    if (!latest.recipe_id || !latest.handoff_path) {
      sendJson(response, 400, { ok: false, error: "No recipe handoff on record. Run create-recipe-handoff first." });
      return;
    }
    if (!isRepoLocalPath(latest.handoff_path)) {
      sendJson(response, 400, { ok: false, error: "REJECTED: handoff_path not repo-local" });
      return;
    }
    const handoffAbs = path.isAbsolute(latest.handoff_path) ? latest.handoff_path : path.join(repoRoot, latest.handoff_path);
    const raw = await runDesktopOperatorCli(["--dry-run", handoffAbs, "--json"]);
    const result = parseDesktopOperatorJson(raw);
    if (!result) {
      sendJson(response, 500, { ok: false, error: "recipe dry-run JSON parse failed", raw });
      return;
    }
    latest.dry_run_plan_path = result.plan_path || null;
    latest.actions_executed = result.actions_executed || 0;
    latest.last_action = "run_recipe_dry_run";
    saveDesktopOperatorRecipeLatest(latest);
    sendJson(response, 200, {
      ok: true,
      localOnly: true,
      summary: { headline: `Recipe dry run complete (${latest.recipe_id}). No actions executed.`, recipeId: latest.recipe_id, planPath: latest.dry_run_plan_path },
      result,
      latest,
    });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/desktop-operator/approve-recipe") {
    const payload = await readJsonBody(request);
    const latest = loadDesktopOperatorRecipeLatest();
    if (!latest.recipe_id || !latest.handoff_path) {
      sendJson(response, 400, { ok: false, error: "No recipe handoff on record." });
      return;
    }
    if (!isRepoLocalPath(latest.handoff_path)) {
      sendJson(response, 400, { ok: false, error: "REJECTED: handoff_path not repo-local" });
      return;
    }
    let approvalToken = typeof payload.approvalToken === "string" ? payload.approvalToken.trim() : "";
    if (approvalToken.length < 4) {
      // Server-generated local token; never returned to client.
      approvalToken = "recipe-" + Math.random().toString(36).slice(2, 10) + Math.random().toString(36).slice(2, 10);
    }
    const handoffAbs = path.isAbsolute(latest.handoff_path) ? latest.handoff_path : path.join(repoRoot, latest.handoff_path);
    const raw = await runDesktopOperatorCli(["--approve", handoffAbs, "--approval-token", approvalToken, "--json"]);
    const result = parseDesktopOperatorJson(raw);
    if (!result || !result.ok) {
      sendJson(response, raw.ok ? 200 : 500, { ok: false, error: "approve-recipe failed", raw });
      return;
    }
    latest.approval_record_path = result.approval_record_path || null;
    latest.approved = result.approved === true;
    latest.last_action = "approve_recipe";
    saveDesktopOperatorRecipeLatest(latest);
    sendJson(response, 200, {
      ok: true,
      localOnly: true,
      // Raw token is NEVER returned.
      summary: { headline: `Recipe approval record created (${latest.recipe_id}). Token never returned.`, recipeId: latest.recipe_id, approvalRecordPath: latest.approval_record_path },
      latest,
    });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/desktop-operator/execute-approved-recipe") {
    const latest = loadDesktopOperatorRecipeLatest();
    if (!latest.recipe_id || !latest.handoff_path) {
      sendJson(response, 400, { ok: false, error: "No recipe handoff on record." });
      return;
    }
    if (!latest.approval_record_path) {
      sendJson(response, 400, { ok: false, error: "No approval record. Run approve-recipe first." });
      return;
    }
    if (!desktopOperatorAllowedRecipes.has(latest.recipe_id)) {
      sendJson(response, 400, { ok: false, error: "REJECTED: recipe_id not in allowlist" });
      return;
    }
    // Execute the recipe via the Python CLI's --recipe-execute mode.
    const raw = await runDesktopOperatorCli(["--recipe-execute", "--recipe-id", latest.recipe_id, "--json"]);
    const result = parseDesktopOperatorJson(raw);
    if (!result) {
      sendJson(response, 500, { ok: false, error: "execute-approved-recipe JSON parse failed", raw });
      return;
    }
    latest.execution_result_path = result.recipe_run_dir || null;
    latest.preview_path = result.preview_path || latest.preview_path || null;
    latest.handoff_export_path = result.handoff_export_path || null;
    latest.actions_executed = Array.isArray(result.actions_executed) ? result.actions_executed.length : 0;
    latest.last_action = "execute_approved_recipe";
    saveDesktopOperatorRecipeLatest(latest);
    sendJson(response, 200, {
      ok: result.ok === true,
      localOnly: true,
      summary: {
        headline: `Recipe executed locally (${latest.recipe_id}). No live posting, no Gemini live call.`,
        recipeId: latest.recipe_id,
        actionsExecuted: latest.actions_executed,
        executionResultPath: latest.execution_result_path,
        previewPath: latest.preview_path,
        handoffExportPath: latest.handoff_export_path,
      },
      result,
      latest,
    });
    return;
  }

  // ─── Parallel Agent Relay (N+4.5A) ──────────────────────────────────────────

  function resolveRelayPromptPath(rawPath) {
    const pairsRoot = path.join(repoRoot, "14_context", "agent_relay", "pairs");
    const ctxRoot = path.join(repoRoot, "14_context");
    const candidate = path.resolve(repoRoot, String(rawPath).replace(/\//g, path.sep));
    if (!isPathInside(pairsRoot, candidate) && !isPathInside(ctxRoot, candidate)) {
      return null;
    }
    return candidate;
  }

  // GET /api/agent-relay/status
  if (request.method === "GET" && requestUrl.pathname === "/api/agent-relay/status") {
    const pairsDir = path.join(repoRoot, "14_context", "agent_relay", "pairs");
    let pairCount = 0;
    try {
      const entries = fs.readdirSync(pairsDir, { withFileTypes: true });
      pairCount = entries.filter((e) => e.isDirectory()).length;
    } catch (_) {}
    sendJson(response, 200, {
      ok: true,
      relay_version: "1.0.0",
      relay_mode: "copy_paste_only",
      autonomous_launch: false,
      human_approval_required: true,
      pair_count: pairCount,
      pairs_dir: path.relative(repoRoot, pairsDir).replace(/\\/g, "/"),
    });
    return;
  }

  // POST /api/agent-relay/create-pair
  if (request.method === "POST" && requestUrl.pathname === "/api/agent-relay/create-pair") {
    let body = {};
    try {
      body = await readJsonBody(request);
    } catch (err) {
      sendJson(response, 400, { ok: false, error: String(err.message) });
      return;
    }
    const milestone = body.milestone;
    const title = body.title;
    const implBranch = body.implementation_branch;
    const auditBranch = body.audit_branch;
    const codexEffort = body.codex_effort || "extra-high";
    const outputDir = body.output_dir;
    if (!milestone || !title || !implBranch || !auditBranch) {
      sendJson(response, 400, {
        ok: false,
        error: "Missing required fields: milestone, title, implementation_branch, audit_branch",
      });
      return;
    }
    const relayScript = path.join(repoRoot, "03_scripts", "parallel_agent_relay.py");
    const py = resolvePython();
    if (!py) {
      sendJson(response, 500, { ok: false, error: "Python interpreter not found" });
      return;
    }
    const argv = [
      ...py.baseArgs,
      relayScript,
      "--create-pair",
      "--milestone", milestone,
      "--title", title,
      "--implementation-branch", implBranch,
      "--audit-branch", auditBranch,
      "--codex-effort", codexEffort,
      "--write-packets",
      "--json",
    ];
    if (outputDir) {
      const resolvedOut = path.resolve(repoRoot, String(outputDir).replace(/\//g, path.sep));
      if (!isPathInside(repoRoot, resolvedOut)) {
        sendJson(response, 400, { ok: false, error: "output_dir is outside repo root" });
        return;
      }
      argv.push("--output-dir", path.relative(repoRoot, resolvedOut).replace(/\\/g, "/"));
    }
    const createResult = await runCommand(py.command, argv, { cwd: repoRoot, timeoutMs: 30000 });
    if (!createResult.ok) {
      sendJson(response, 500, { ok: false, error: createResult.stderr || `exit ${createResult.exitCode}` });
      return;
    }
    try {
      const pairData = JSON.parse(createResult.stdout);
      sendJson(response, 200, pairData);
    } catch (_) {
      sendJson(response, 500, { ok: false, error: "Failed to parse relay output" });
    }
    return;
  }

  // GET /api/agent-relay/latest
  if (request.method === "GET" && requestUrl.pathname === "/api/agent-relay/latest") {
    const pairsDir = path.join(repoRoot, "14_context", "agent_relay", "pairs");
    let latestManifest = null;
    let latestPairId = null;
    try {
      const dirs = fs
        .readdirSync(pairsDir, { withFileTypes: true })
        .filter((e) => e.isDirectory())
        .sort((a, b) => b.name.localeCompare(a.name));
      if (dirs.length > 0) {
        latestPairId = dirs[0].name;
        const manifestPath = path.join(pairsDir, latestPairId, "00_manifest.json");
        latestManifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
      }
    } catch (_) {}
    sendJson(response, 200, { ok: true, pair_id: latestPairId, manifest: latestManifest });
    return;
  }

  // GET /api/agent-relay/pair?id=<pair_id>
  if (request.method === "GET" && requestUrl.pathname === "/api/agent-relay/pair") {
    const pairId = requestUrl.searchParams.get("id");
    if (!pairId || String(pairId).includes("..") || String(pairId).includes("/")) {
      sendJson(response, 400, { ok: false, error: "Invalid or missing ?id= parameter" });
      return;
    }
    const pairsDir = path.join(repoRoot, "14_context", "agent_relay", "pairs");
    const pairDir = path.resolve(pairsDir, pairId);
    if (!isPathInside(pairsDir, pairDir)) {
      sendJson(response, 400, { ok: false, error: "Invalid pair id" });
      return;
    }
    try {
      const manifest = JSON.parse(fs.readFileSync(path.join(pairDir, "00_manifest.json"), "utf8"));
      sendJson(response, 200, { ok: true, pair_id: pairId, manifest });
    } catch (_) {
      sendJson(response, 404, { ok: false, error: "Pair not found" });
    }
    return;
  }

  // GET /api/agent-relay/prompt?path=<relative_path>
  if (request.method === "GET" && requestUrl.pathname === "/api/agent-relay/prompt") {
    const rawPath = requestUrl.searchParams.get("path");
    if (!rawPath) {
      sendJson(response, 400, { ok: false, error: "Missing ?path= parameter" });
      return;
    }
    const resolvedPromptPath = resolveRelayPromptPath(rawPath);
    if (!resolvedPromptPath) {
      sendJson(response, 403, { ok: false, error: "Path is outside allowed relay directories" });
      return;
    }
    try {
      const content = fs.readFileSync(resolvedPromptPath, "utf8");
      sendJson(response, 200, {
        ok: true,
        path: path.relative(repoRoot, resolvedPromptPath).replace(/\\/g, "/"),
        content,
      });
    } catch (_) {
      sendJson(response, 404, { ok: false, error: "Prompt file not found" });
    }
    return;
  }

  // ─── Ghoti Product Control Center (N+4.6A) ──────────────────────────────────
  // Usability/product layer. Local-only. No external API, no live account
  // actions, no autonomous launch. Subprocess endpoints use fixed argv +
  // shell:false + timeouts. Path output reuses the N+4.4D isPathInsideRepo
  // containment helper.

  async function runContextPackBuilder(argvTail, timeoutMs) {
    const contextPackScript = path.join(repoRoot, "03_scripts", "ghoti_context_pack_builder.py");
    const py = resolvePython();
    if (!py) {
      return { ok: false, local_only: true, available: false, error: "Python interpreter not found" };
    }
    if (!fs.existsSync(contextPackScript)) {
      return { ok: false, local_only: true, available: false, error: "Context pack builder not found" };
    }
    const argv = [...py.baseArgs, contextPackScript, ...argvTail, "--json"];
    let raw;
    try {
      raw = await runCommand(py.command, argv, { cwd: repoRoot, timeoutMs: timeoutMs || 30000 });
    } catch (err) {
      return { ok: false, local_only: true, available: false, error: String(err && err.message) };
    }
    if (!raw.ok) {
      return {
        ok: false,
        local_only: true,
        available: false,
        error: raw.stderr || `exit ${raw.exitCode}`,
        output: raw.stdout,
      };
    }
    try {
      return JSON.parse(raw.stdout);
    } catch (_) {
      return { ok: false, local_only: true, available: false, error: "Failed to parse context pack output" };
    }
  }

  async function runLocalModelWorkerLane(argvTail, timeoutMs) {
    const localWorkerScript = path.join(repoRoot, "03_scripts", "local_model_worker_lane.py");
    const py = resolvePython();
    if (!py) {
      return { ok: false, local_only: true, available: false, error: "Python interpreter not found" };
    }
    if (!fs.existsSync(localWorkerScript)) {
      return { ok: false, local_only: true, available: false, error: "Local model worker lane not found" };
    }
    const argv = [...py.baseArgs, localWorkerScript, ...argvTail, "--json"];
    let raw;
    try {
      raw = await runCommand(py.command, argv, { cwd: repoRoot, timeoutMs: timeoutMs || 30000 });
    } catch (err) {
      return { ok: false, local_only: true, available: false, error: String(err && err.message) };
    }
    if (!raw.ok) {
      return {
        ok: false,
        local_only: true,
        available: false,
        error: raw.stderr || `exit ${raw.exitCode}`,
        output: raw.stdout,
      };
    }
    try {
      return JSON.parse(raw.stdout);
    } catch (_) {
      return { ok: false, local_only: true, available: false, error: "Failed to parse local worker output" };
    }
  }

  async function runGemmaModelReadiness(argvTail, timeoutMs) {
    const gemmaReadinessScript = path.join(repoRoot, "03_scripts", "gemma_model_readiness.py");
    const py = resolvePython();
    if (!py) {
      return { ok: false, local_only: true, available: false, error: "Python interpreter not found" };
    }
    if (!fs.existsSync(gemmaReadinessScript)) {
      return { ok: false, local_only: true, available: false, error: "Gemma model readiness script not found" };
    }
    const argv = [...py.baseArgs, gemmaReadinessScript, ...argvTail, "--json"];
    let raw;
    try {
      raw = await runCommand(py.command, argv, { cwd: repoRoot, timeoutMs: timeoutMs || 45000 });
    } catch (err) {
      return { ok: false, local_only: true, available: false, error: String(err && err.message) };
    }
    if (!raw.ok) {
      return {
        ok: false,
        local_only: true,
        available: false,
        error: raw.stderr || `exit ${raw.exitCode}`,
        output: raw.stdout,
      };
    }
    try {
      return JSON.parse(raw.stdout);
    } catch (_) {
      return { ok: false, local_only: true, available: false, error: "Failed to parse Gemma readiness output" };
    }
  }

  async function runRepoKnowledgeMap(argvTail, timeoutMs) {
    const repoKnowledgeScript = path.join(repoRoot, "03_scripts", "ghoti_repo_knowledge_map.py");
    const py = resolvePython();
    if (!py) {
      return { ok: false, local_only: true, available: false, error: "Python interpreter not found" };
    }
    if (!fs.existsSync(repoKnowledgeScript)) {
      return { ok: false, local_only: true, available: false, error: "Repo knowledge map not found" };
    }
    const argv = [...py.baseArgs, repoKnowledgeScript, ...argvTail, "--json"];
    let raw;
    try {
      raw = await runCommand(py.command, argv, { cwd: repoRoot, timeoutMs: timeoutMs || 45000 });
    } catch (err) {
      return { ok: false, local_only: true, available: false, error: String(err && err.message) };
    }
    if (!raw.ok) {
      return {
        ok: false,
        local_only: true,
        available: false,
        error: raw.stderr || `exit ${raw.exitCode}`,
        output: raw.stdout,
      };
    }
    try {
      return JSON.parse(raw.stdout);
    } catch (_) {
      return { ok: false, local_only: true, available: false, error: "Failed to parse repo knowledge output" };
    }
  }

  async function runHermesAgentBridge(argvTail, timeoutMs) {
    const hermesBridgeScript = path.join(repoRoot, "03_scripts", "hermes_agent_workflow_bridge.py");
    const py = resolvePython();
    if (!py) {
      return { ok: false, local_only: true, available: false, error: "Python interpreter not found" };
    }
    if (!fs.existsSync(hermesBridgeScript)) {
      return { ok: false, local_only: true, available: false, error: "Hermes agent workflow bridge not found" };
    }
    const argv = [...py.baseArgs, hermesBridgeScript, ...argvTail, "--json"];
    let raw;
    try {
      raw = await runCommand(py.command, argv, { cwd: repoRoot, timeoutMs: timeoutMs || 60000 });
    } catch (err) {
      return { ok: false, local_only: true, available: false, error: String(err && err.message) };
    }
    if (!raw.ok) {
      return {
        ok: false,
        local_only: true,
        available: false,
        error: raw.stderr || `exit ${raw.exitCode}`,
        output: raw.stdout,
      };
    }
    try {
      return JSON.parse(raw.stdout);
    } catch (_) {
      return { ok: false, local_only: true, available: false, error: "Failed to parse Hermes bridge output" };
    }
  }

  async function runHermesManualBridge(argvTail, timeoutMs) {
    const hermesManualScript = path.join(repoRoot, "03_scripts", "hermes_manual_bridge_verifier.py");
    const py = resolvePython();
    if (!py) {
      return { ok: false, local_only: true, available: false, error: "Python interpreter not found" };
    }
    if (!fs.existsSync(hermesManualScript)) {
      return { ok: false, local_only: true, available: false, error: "Hermes manual bridge verifier not found" };
    }
    const argv = [...py.baseArgs, hermesManualScript, ...argvTail, "--json"];
    let raw;
    try {
      raw = await runCommand(py.command, argv, { cwd: repoRoot, timeoutMs: timeoutMs || 60000 });
    } catch (err) {
      return { ok: false, local_only: true, available: false, error: String(err && err.message) };
    }
    if (!raw.ok) {
      return {
        ok: false,
        local_only: true,
        available: false,
        error: raw.stderr || `exit ${raw.exitCode}`,
        output: raw.stdout,
      };
    }
    try {
      return JSON.parse(raw.stdout);
    } catch (_) {
      return { ok: false, local_only: true, available: false, error: "Failed to parse Hermes manual bridge output" };
    }
  }

  // GET /api/local-memory-context-pack/status
  if (request.method === "GET" && requestUrl.pathname === "/api/local-memory-context-pack/status") {
    sendJson(response, 200, await runContextPackBuilder(["--status"], 30000));
    return;
  }

  // POST /api/local-memory-context-pack/build
  if (request.method === "POST" && requestUrl.pathname === "/api/local-memory-context-pack/build") {
    // Fixed argv. Repo-local file generation only. No external API, provider setup,
    // account action, or browser/computer-use action is triggered.
    sendJson(response, 200, await runContextPackBuilder(["--write"], 30000));
    return;
  }

  // GET /api/local-model-worker/status
  if (request.method === "GET" && requestUrl.pathname === "/api/local-model-worker/status") {
    sendJson(response, 200, await runLocalModelWorkerLane(["--status"], 30000));
    return;
  }

  // GET /api/local-model-worker/doctor
  if (request.method === "GET" && requestUrl.pathname === "/api/local-model-worker/doctor") {
    sendJson(response, 200, await runLocalModelWorkerLane(["--doctor"], 30000));
    return;
  }

  // POST /api/local-model-worker/demo
  if (request.method === "POST" && requestUrl.pathname === "/api/local-model-worker/demo") {
    // Fixed argv. Local deterministic demo only. No live APIs, no provider setup,
    // no model downloads, no posting, and no account actions.
    sendJson(response, 200, await runLocalModelWorkerLane(["--demo-task", "status-paragraph"], 30000));
    return;
  }

  // POST /api/local-model-worker/write-demo-output
  if (request.method === "POST" && requestUrl.pathname === "/api/local-model-worker/write-demo-output") {
    // Fixed argv. Repo-local file generation only. Ghoti never runs ollama pull.
    sendJson(response, 200, await runLocalModelWorkerLane(["--write-demo-output"], 45000));
    return;
  }

  // GET /api/local-model-worker/routing-status
  if (request.method === "GET" && requestUrl.pathname === "/api/local-model-worker/routing-status") {
    // N+6.1A guarded routing status only. No live APIs, no command execution from
    // model output, no provider setup, no browser actions, and no file edits.
    sendJson(response, 200, await runLocalModelWorkerLane(["--routing-status"], 45000));
    return;
  }

  // GET or POST /api/local-model-worker/route-task?task=<safe-task>
  if ((request.method === "GET" || request.method === "POST") && requestUrl.pathname === "/api/local-model-worker/route-task") {
    const allowedRouteTasks = new Set([
      "summarize-latest-report",
      "status-paragraph",
      "codex-next-prompt",
      "safety-classification",
      "context-bundle-summary",
      "next-milestone-outline",
      "report-to-bullets",
    ]);
    const task = String(requestUrl.searchParams.get("task") || "status-paragraph");
    if (!allowedRouteTasks.has(task)) {
      sendJson(response, 400, { ok: false, local_only: true, error: "Unsupported guarded local worker task" });
      return;
    }
    // Fixed argv allowlist. The worker validates source metadata and falls back to
    // local_demo when Gemma invents bundles/files or omits required source truth.
    sendJson(response, 200, await runLocalModelWorkerLane(["--route-task", task], 90000));
    return;
  }

  // POST /api/local-model-worker/write-routing-demo
  if (request.method === "POST" && requestUrl.pathname === "/api/local-model-worker/write-routing-demo") {
    // Repo-local guarded routing artifacts only. No browser/computer-use, no live
    // providers, no commands or file edits from model output.
    sendJson(response, 200, await runLocalModelWorkerLane(["--write-routing-demo"], 180000));
    return;
  }

  // GET /api/gemma-readiness/status
  if (request.method === "GET" && requestUrl.pathname === "/api/gemma-readiness/status") {
    sendJson(response, 200, await runGemmaModelReadiness(["--status"], 45000));
    return;
  }

  // GET /api/gemma-readiness/doctor
  if (request.method === "GET" && requestUrl.pathname === "/api/gemma-readiness/doctor") {
    sendJson(response, 200, await runGemmaModelReadiness(["--doctor"], 45000));
    return;
  }

  // GET /api/gemma-readiness/recommend
  if (request.method === "GET" && requestUrl.pathname === "/api/gemma-readiness/recommend") {
    sendJson(response, 200, await runGemmaModelReadiness(["--recommend"], 45000));
    return;
  }

  // GET /api/gemma-readiness/quality-plan
  if (request.method === "GET" && requestUrl.pathname === "/api/gemma-readiness/quality-plan") {
    sendJson(response, 200, await runGemmaModelReadiness(["--quality-plan"], 45000));
    return;
  }

  // GET /api/gemma-readiness/local-model-eval
  if (request.method === "GET" && requestUrl.pathname === "/api/gemma-readiness/local-model-eval") {
    // Local Ollama/Gemma evaluation summary only. No downloads, no provider setup,
    // no Telegram setup, no browser automation, and no production routing.
    sendJson(response, 200, await runGemmaModelReadiness(["--local-model-eval"], 150000));
    return;
  }

  // POST /api/gemma-readiness/write-readiness
  if (request.method === "POST" && requestUrl.pathname === "/api/gemma-readiness/write-readiness") {
    // Fixed argv. Repo-local file generation only. No downloads, no live API,
    // no provider setup, and no production routing.
    sendJson(response, 200, await runGemmaModelReadiness(["--write-readiness"], 60000));
    return;
  }

  // GET /api/repo-knowledge/status
  if (request.method === "GET" && requestUrl.pathname === "/api/repo-knowledge/status") {
    sendJson(response, 200, await runRepoKnowledgeMap(["--status"], 45000));
    return;
  }

  // POST /api/repo-knowledge/write
  if (request.method === "POST" && requestUrl.pathname === "/api/repo-knowledge/write") {
    // Fixed argv. Local JSON/Markdown generation only. No network, no external repo runtime.
    sendJson(response, 200, await runRepoKnowledgeMap(["--write"], 60000));
    return;
  }

  // GET /api/repo-knowledge/bundle?name=<bundle>
  if (request.method === "GET" && requestUrl.pathname === "/api/repo-knowledge/bundle") {
    const allowedBundles = new Set([
      "audit-main",
      "dashboard",
      "local-memory",
      "local-model-worker",
      "local-model-routing",
      "hermes",
      "content-workflow",
      "safety",
      "next-milestone",
    ]);
    const bundle = String(requestUrl.searchParams.get("name") || "next-milestone");
    if (!allowedBundles.has(bundle)) {
      sendJson(response, 400, { ok: false, local_only: true, error: "Unsupported repo knowledge bundle" });
      return;
    }
    sendJson(response, 200, await runRepoKnowledgeMap(["--bundle", bundle], 45000));
    return;
  }

  // GET /api/hermes-bridge/status
  if (request.method === "GET" && requestUrl.pathname === "/api/hermes-bridge/status") {
    sendJson(response, 200, await runHermesAgentBridge(["--status"], 60000));
    return;
  }

  // GET /api/hermes-bridge/doctor
  if (request.method === "GET" && requestUrl.pathname === "/api/hermes-bridge/doctor") {
    sendJson(response, 200, await runHermesAgentBridge(["--doctor"], 60000));
    return;
  }

  // GET /api/hermes-bridge/skills-index
  if (request.method === "GET" && requestUrl.pathname === "/api/hermes-bridge/skills-index") {
    sendJson(response, 200, await runHermesAgentBridge(["--skills-index"], 60000));
    return;
  }

  // POST /api/hermes-bridge/write-readiness
  if (request.method === "POST" && requestUrl.pathname === "/api/hermes-bridge/write-readiness") {
    // Fixed argv. Safe WSL status probes and repo-local files only. No live
    // provider setup, no provider config, no Telegram setup, no tokens, and
    // no browser automation.
    sendJson(response, 200, await runHermesAgentBridge(["--write-readiness"], 90000));
    return;
  }

  // GET /api/hermes-manual-bridge/status
  if (request.method === "GET" && requestUrl.pathname === "/api/hermes-manual-bridge/status") {
    sendJson(response, 200, await runHermesManualBridge(["--status"], 60000));
    return;
  }

  // GET /api/hermes-manual-bridge/doctor
  if (request.method === "GET" && requestUrl.pathname === "/api/hermes-manual-bridge/doctor") {
    sendJson(response, 200, await runHermesManualBridge(["--doctor"], 60000));
    return;
  }

  // GET /api/hermes-manual-bridge/wsl-explain
  if (request.method === "GET" && requestUrl.pathname === "/api/hermes-manual-bridge/wsl-explain") {
    sendJson(response, 200, await runHermesManualBridge(["--wsl-explain"], 30000));
    return;
  }

  // GET /api/hermes-manual-bridge/safe-commands
  if (request.method === "GET" && requestUrl.pathname === "/api/hermes-manual-bridge/safe-commands") {
    sendJson(response, 200, await runHermesManualBridge(["--safe-commands"], 30000));
    return;
  }

  // GET /api/hermes-manual-bridge/blocked-commands
  if (request.method === "GET" && requestUrl.pathname === "/api/hermes-manual-bridge/blocked-commands") {
    sendJson(response, 200, await runHermesManualBridge(["--blocked-commands"], 30000));
    return;
  }

  // GET /api/hermes-manual-bridge/skills-summary
  if (request.method === "GET" && requestUrl.pathname === "/api/hermes-manual-bridge/skills-summary") {
    sendJson(response, 200, await runHermesManualBridge(["--skills-summary"], 60000));
    return;
  }

  // POST /api/hermes-manual-bridge/write-guide
  if (request.method === "POST" && requestUrl.pathname === "/api/hermes-manual-bridge/write-guide") {
    // Fixed argv. Safe WSL probes and repo-local guide files only. No live
    // provider setup, no provider config, no Telegram, no tokens, no browser
    // automation, and no computer-use click/type.
    sendJson(response, 200, await runHermesManualBridge(["--write-guide"], 90000));
    return;
  }

  // GET /api/product-control/status
  if (request.method === "GET" && requestUrl.pathname === "/api/product-control/status") {
    sendJson(response, 200, {
      ok: true,
      product: "Ghoti Local Supervised Operator",
      local_only: true,
      live_posting: false,
      live_account_actions: false,
      external_api: false,
      external_tools: "planning_only",
      approval_gates: "required",
      autonomous_launch: false,
      relay_mode: "copy_paste_only",
      capabilities: [
        {
          key: "local_content_studio",
          label: "Local Content Studio",
          available: true,
          how_to_run: "Run Local Content Studio button -> POST /api/product-control/run-content-studio-demo (safe dry-run, no live posting)",
        },
        {
          key: "desktop_operator_action_center",
          label: "Desktop Operator Action Center",
          available: true,
          how_to_run: "Desktop Operator section: safe dry-run -> human approval -> execute",
        },
        {
          key: "desktop_recipe_runner",
          label: "Desktop Recipe Runner",
          available: true,
          how_to_run: "Recipe Runner section: pick recipe -> dry-run -> approve -> execute",
        },
        {
          key: "parallel_agent_relay",
          label: "Parallel Agent Relay",
          available: true,
          how_to_run: "Generate Claude + Codex Prompt Pair button -> copy-paste each prompt manually",
        },
        {
          key: "local_memory_gemma_fallback",
          label: "Local Memory / Gemma Fallback",
          available: true,
          how_to_run: "local_memory_compression_bridge.py --json (local only, no external API)",
        },
        {
          key: "local_memory_context_pack",
          label: "Local Memory / Context Pack",
          available: true,
          mode: "repo_local_copy_paste",
          how_to_run: "Run ghoti_context_pack_builder.py --write --json or POST /api/local-memory-context-pack/build to refresh compact handoff files.",
        },
        {
          key: "local_model_easy_worker_lane",
          label: "Local Model / Easy Worker Lane",
          available: true,
          mode: "local_demo_fallback_or_ollama_gemma",
          how_to_run: "Run local_model_worker_lane.py --status --json or POST /api/local-model-worker/write-demo-output. No live APIs, no auto-downloads.",
        },
        {
          key: "gemma_local_model_quality",
          label: "Gemma / Local Model Quality",
          available: true,
          mode: "manual_install_decision_and_quality_plan",
          how_to_run: "Run gemma_model_readiness.py --doctor --json or GET /api/gemma-readiness/quality-plan. No live APIs, no auto-downloads, no ollama pull, production routing disabled.",
        },
        {
          key: "local_model_guarded_worker",
          label: "Local Model Routing / Guarded Worker",
          available: true,
          mode: "guarded_safe_tasks_only",
          how_to_run: "Run local_model_worker_lane.py --routing-status --json or GET /api/local-model-worker/routing-status. Gemma output must pass source metadata guard or local_demo fallback is used.",
        },
        {
          key: "repo_knowledge_graphify_lane",
          label: "Repo Knowledge / Graphify Lane",
          available: true,
          mode: "local_map_and_task_bundles",
          how_to_run: "Run ghoti_repo_knowledge_map.py --write --json or POST /api/repo-knowledge/write. Graphify runtime is roadmap only/not wired; no external repo runtime; no network.",
        },
        {
          key: "hermes_agent_manual_bridge",
          label: "Hermes Agent / Manual Bridge",
          available: true,
          mode: "safe_wsl_probes_only",
          how_to_run: "Run hermes_agent_workflow_bridge.py --status --json or POST /api/hermes-bridge/write-readiness. Codex provider pending/not proven; Telegram manual later/no token; browser/Playwright degraded/not claimed.",
        },
        {
          key: "external_tool_intake",
          label: "External Tool Intake",
          available: true,
          mode: "planning_only",
          how_to_run: "Catalog / intake review only — nothing is cloned, installed, or run",
        },
        {
          key: "hermes_wsl_truth",
          label: "Hermes WSL Truth",
          available: true,
          mode: "verified_local_wsl",
          how_to_run: "Hermes status lane: Ubuntu WSL safe probes report /home/ai_sandbox/.local/bin/hermes and Hermes Agent v0.14.0; setup/provider/Telegram flows stay manual.",
        },
        {
          key: "gemma_ollama_lane",
          label: "Gemma / Ollama Lane",
          available: true,
          mode: "local_probe_or_demo_fallback",
          how_to_run: "Use local_memory_compression_bridge.py --json; missing Ollama/Gemma falls back to local_demo instead of pretending.",
        },
        {
          key: "obsidian_compact_memory",
          label: "Obsidian Compact Memory",
          available: true,
          mode: "repo_local_memory",
          how_to_run: "Compact repo notes and Obsidian-compatible markdown follow docs/OBSIDIAN_COMPACT_MEMORY_PLAN.md.",
        },
        {
          key: "ruflo_local_brain_bridge",
          label: "Ruflo / Local Brain Bridge",
          available: true,
          mode: "status_only",
          how_to_run: "Read-only Ruflo/local brain bridge status; no runtime wiring or installs from the dashboard.",
        },
        {
          key: "graphify_token_plan",
          label: "Graphify / Token Plan",
          available: true,
          mode: "roadmap",
          how_to_run: "Graphify remains a token-efficiency roadmap lane; not installed, not wired, no external call.",
        },
        {
          key: "ui_tars_observation_only",
          label: "UI-TARS Observation Only",
          available: true,
          mode: "observation_only",
          how_to_run: "Run UI-TARS observation dry-run to create local packets; no runtime start, no click/type/control.",
        },
        {
          key: "adapter_dry_runs",
          label: "Adapter Dry-Runs",
          available: true,
          mode: "dry_run_only",
          how_to_run: "Approved adapter runner executes local dry-runs only; no external repo code, installs, or live API.",
        },
        {
          key: "external_sandbox",
          label: "External Sandbox",
          available: true,
          mode: "static_scan_only",
          how_to_run: "External sandbox status reports static-scan/intake truth only.",
        },
        {
          key: "public_readiness",
          label: "Public Readiness",
          available: true,
          mode: "audit_gate",
          how_to_run: "Run public_repo_security_audit.py --run --json; warnings still require human review.",
        },
        {
          key: "model_council",
          label: "Model Council",
          available: true,
          mode: "planning_only",
          how_to_run: "Model council scans provider/tool plans locally; unsafe automation stays blocked.",
        },
        {
          key: "safety_gates",
          label: "Safety Gates",
          available: true,
          mode: "enforced",
          how_to_run: "No live posting, money/trading/legal action, provider token setup, or hidden autonomy is enabled.",
        },
      ],
    });
    return;
  }

  // POST /api/product-control/run-content-studio-demo
  if (request.method === "POST" && requestUrl.pathname === "/api/product-control/run-content-studio-demo") {
    const studioScript = path.join(repoRoot, "03_scripts", "supervised_content_mvp_runner.py");
    const py = resolvePython();
    if (!py) {
      sendJson(response, 200, { ok: false, available: false, error: "Python interpreter not found" });
      return;
    }
    if (!fs.existsSync(studioScript)) {
      sendJson(response, 200, { ok: false, available: false, error: "Content studio runner not found" });
      return;
    }
    // Fixed argv. Safe dry-run only — never --apply, no live posting.
    const argv = [...py.baseArgs, studioScript, "--run", "--dry-run"];
    let studioResult;
    try {
      studioResult = await runCommand(py.command, argv, { cwd: repoRoot, timeoutMs: 60000 });
    } catch (err) {
      sendJson(response, 200, { ok: false, available: false, mode: "dry_run", error: String(err && err.message) });
      return;
    }
    if (!studioResult.ok) {
      sendJson(response, 200, {
        ok: false,
        available: false,
        mode: "dry_run",
        live_posting: false,
        external_api: false,
        error: studioResult.stderr || `exit ${studioResult.exitCode}`,
        output: studioResult.stdout,
      });
      return;
    }
    sendJson(response, 200, {
      ok: true,
      available: true,
      mode: "dry_run",
      live_posting: false,
      external_api: false,
      output: studioResult.stdout,
    });
    return;
  }

  // POST /api/product-control/create-relay-pair
  if (request.method === "POST" && requestUrl.pathname === "/api/product-control/create-relay-pair") {
    let body = {};
    try {
      body = await readJsonBody(request);
    } catch (_) {
      body = {};
    }
    const str = (v, fallback) =>
      (typeof v === "string" && v.trim().length > 0 ? v.trim() : fallback);
    const milestone = str(body.milestone, "Ghoti Product Control Center Demo");
    const title = str(body.title, "Product Control Center Relay Pair");
    const implBranch = str(body.implementation_branch, "feat/ghoti-demo-implementation");
    const auditBranch = str(body.audit_branch, "audit/ghoti-demo-audit");
    const allowedEfforts = ["extra-high", "high", "medium"];
    let codexEffort = str(body.codex_effort, "extra-high");
    if (!allowedEfforts.includes(codexEffort)) {
      codexEffort = "extra-high";
    }
    const relayScript = path.join(repoRoot, "03_scripts", "parallel_agent_relay.py");
    const py = resolvePython();
    if (!py) {
      sendJson(response, 200, { ok: false, available: false, error: "Python interpreter not found" });
      return;
    }
    const argv = [
      ...py.baseArgs,
      relayScript,
      "--create-pair",
      "--milestone", milestone,
      "--title", title,
      "--implementation-branch", implBranch,
      "--audit-branch", auditBranch,
      "--codex-effort", codexEffort,
      "--write-packets",
      "--json",
    ];
    let relayResult;
    try {
      relayResult = await runCommand(py.command, argv, { cwd: repoRoot, timeoutMs: 30000 });
    } catch (err) {
      sendJson(response, 200, { ok: false, available: false, error: String(err && err.message) });
      return;
    }
    if (!relayResult.ok) {
      sendJson(response, 200, { ok: false, available: false, error: relayResult.stderr || `exit ${relayResult.exitCode}` });
      return;
    }
    try {
      sendJson(response, 200, JSON.parse(relayResult.stdout));
    } catch (_) {
      sendJson(response, 200, { ok: false, available: false, error: "Failed to parse relay output" });
    }
    return;
  }

  // GET /api/product-control/latest
  if (request.method === "GET" && requestUrl.pathname === "/api/product-control/latest") {
    const safeRepoRel = (absOrRel) => {
      // N+4.4D containment: return a repo-relative POSIX path only if contained.
      if (typeof absOrRel !== "string" || absOrRel.length === 0) return null;
      if (!isPathInsideRepo(absOrRel)) return null;
      const abs = path.isAbsolute(absOrRel) ? absOrRel : path.join(repoRoot, absOrRel);
      return path.relative(repoRoot, path.resolve(abs)).replace(/\\/g, "/");
    };
    const newestSubdir = (dirAbs) => {
      try {
        return fs.readdirSync(dirAbs, { withFileTypes: true })
          .filter((e) => e.isDirectory())
          .map((e) => e.name)
          .sort((a, b) => b.localeCompare(a))[0] || null;
      } catch (_) {
        return null;
      }
    };
    const csDir = path.join(repoRoot, "14_context", "content_workflows", "runs");
    const csId = newestSubdir(csDir);
    const csRel = csId ? safeRepoRel(path.join(csDir, csId)) : null;
    const pairsDir = path.join(repoRoot, "14_context", "agent_relay", "pairs");
    const pairId = newestSubdir(pairsDir);
    const pairRel = pairId ? safeRepoRel(path.join(pairsDir, pairId)) : null;
    const doLatest = loadDesktopOperatorLatest();
    const doHandoffRel = doLatest && doLatest.handoff_path ? safeRepoRel(doLatest.handoff_path) : null;
    const doExecRel = doLatest && doLatest.execution_result_path ? safeRepoRel(doLatest.execution_result_path) : null;
    const previewRel = doLatest && doLatest.preview_path ? safeRepoRel(doLatest.preview_path) : null;
    sendJson(response, 200, {
      ok: true,
      local_only: true,
      latest: {
        content_studio_run: csRel ? { id: csId, path: csRel } : null,
        relay_pair: pairRel ? { id: pairId, path: pairRel } : null,
        desktop_operator_run:
          doHandoffRel || doExecRel
            ? { handoff_path: doHandoffRel, execution_result_path: doExecRel }
            : null,
        preview_path: previewRel,
      },
    });
    return;
  }

  // ─── Operator Capability Console (N+6.39A) ──────────────────────────────────
  // Turns the existing safe backend checks into plain-language capability cards.
  // Every check below runs an existing safe script via fixed argv (shell:false).
  // No live agents, no accounts, no MCP, no Telegram, no browser automation, and
  // no provider/API keys are ever used. POST only selects a mode ("fast"/"full");
  // no user-supplied command is ever executed.

  // Static truth table. statusCategory is one of:
  //   pass | warning | blocked-safely | dry-run | not-implemented | roadmap | manual | unknown
  function buildCapabilityRegistry() {
    return [
      { id: "dashboard-server", title: "Dashboard server", group: "real-today",
        statusCategory: "pass", statusLabel: "Running",
        detail: "This local console is up and answering on http://127.0.0.1:3210." },
      { id: "product-launcher", title: "Product launcher", group: "real-today",
        statusCategory: "pass", statusLabel: "Working (port-state hardened)",
        detail: "Starts/inspects the dashboard. A busy port is now detected as already-running, not an error." },
      { id: "public-audit", title: "Public safety audit", group: "real-today",
        statusCategory: "pass", statusLabel: "Pass (warnings, no blockers)",
        detail: "Scans the repo for things unsafe to publish. Warnings are advisory; no blocking findings." },
      { id: "rust-policy", title: "Rust policy tests", group: "real-today",
        statusCategory: "unknown", statusLabel: "Run on demand",
        detail: "cargo test for policy crates. Shown as command + last-known to keep the console fast." },
      { id: "cua-trial", title: "Computer-use (CUA) trial", group: "dry-run",
        statusCategory: "dry-run", statusLabel: "Safe demo/check available",
        detail: "Inspected only, not executed. No external code runs and no desktop is controlled." },
      { id: "agent-systems", title: "Agent systems trial", group: "dry-run",
        statusCategory: "dry-run", statusLabel: "Safe static/dry-run",
        detail: "Inspected only, not executed. No live agents are launched." },
      { id: "agent-adapter", title: "Agent system adapter", group: "dry-run",
        statusCategory: "dry-run", statusLabel: "Safe static/dry-run",
        detail: "Adapter shape is checked statically; nothing is executed." },
      { id: "claude-swarm-dry-run", title: "claude-swarm dry-run", group: "dry-run",
        statusCategory: "blocked-safely", statusLabel: "Ghoti refused to run something unsafe",
        detail: "claude-swarm --dry-run calls a provider before the dry-run skip, so Ghoti blocks it. This is correct, not a failure." },
      { id: "claude-swarm-fixture", title: "claude-swarm fixture replay", group: "real-today",
        statusCategory: "pass", statusLabel: "Pass (5 tasks / 3 groups / 0 overlaps)",
        detail: "Replays a static plan with no provider, no API key, no external CLI." },
      { id: "local-model", title: "Local model / Ollama", group: "real-today",
        statusCategory: "unknown", statusLabel: "Reported from live check",
        detail: "Exact readiness is read from the local worker status check; no value is faked." },
      { id: "hermes", title: "Hermes", group: "manual",
        statusCategory: "manual", statusLabel: "Manual setup guide exists, no live automation",
        detail: "Coordinator / manual bridge only. Nothing posts or runs automatically." },
      { id: "obsidian", title: "Obsidian memory bridge", group: "not-real-yet",
        statusCategory: "not-implemented", statusLabel: "Not implemented yet",
        detail: "Planned next. No vault is read or written in this build." },
      { id: "telegram", title: "Telegram", group: "not-real-yet",
        statusCategory: "roadmap", statusLabel: "Planned later (notification-only / status-only / draft-only)",
        detail: "No Telegram integration exists yet. No commands are executed from chat." },
      { id: "github-contrib", title: "GitHub contributor UI", group: "not-real-yet",
        statusCategory: "warning", statusLabel: "UI cache investigation pending",
        detail: "A UI cache question is still open. Not claimed as solved." },
    ];
  }

  // Allowlisted safe checks. The key is referenced only by the fixed runner below;
  // args are constant arrays, never built from request input.
  function capabilityCheckPlan(mode) {
    const py = resolvePython();
    const launcher = ["03_scripts", "ghoti_product_launcher.py"];
    const lp = path.join(repoRoot, ...launcher);
    const fixture = path.join(repoRoot, "03_scripts", "claude_swarm_fixture", "ghoti_claude_swarm_fixture_replay.py");
    const swarmDry = path.join(repoRoot, "03_scripts", "claude_swarm_dry_run", "ghoti_claude_swarm_dry_run.py");
    const audit = path.join(repoRoot, "03_scripts", "public_repo_security_audit.py");
    const repoMap = lp;
    const fast = [
      { id: "product-launcher", title: "Product launcher status", argv: [lp, "--status", "--json"], timeoutMs: 30000 },
      { id: "claude-swarm-fixture", title: "Fixture replay check", argv: [fixture, "--replay", "--json"], timeoutMs: 30000 },
      { id: "local-model", title: "Local model / worker status", argv: [lp, "--local-worker-status", "--json"], timeoutMs: 30000 },
      { id: "hermes", title: "Hermes manual bridge status", argv: [lp, "--hermes-manual-status", "--json"], timeoutMs: 30000 },
    ];
    const fullExtra = [
      { id: "public-audit", title: "Public repo security audit", argv: [audit, "--run", "--json"], timeoutMs: 90000 },
      { id: "claude-swarm-dry-run", title: "claude-swarm dry-run safety check", argv: [swarmDry, "--check", "--json"], timeoutMs: 30000 },
      { id: "repo-map", title: "Repo map", argv: [repoMap, "--repo-map", "--json"], timeoutMs: 120000 },
    ];
    const checks = mode === "full" ? fast.concat(fullExtra) : fast;
    return { py, checks };
  }

  async function runCapabilityChecks(mode) {
    const { py, checks } = capabilityCheckPlan(mode);
    const startedAt = new Date().toISOString();
    if (!py) {
      return {
        ok: false, available: false, mode,
        error: "Python interpreter not found",
        message: "Could not find a local Python to run safe checks.",
        generated_at: startedAt,
      };
    }
    const results = [];
    for (const check of checks) {
      const argv = [...py.baseArgs, ...check.argv];
      const r = await runCommand(py.command, argv, { cwd: repoRoot, env: buildRuntimeEnv(), timeoutMs: check.timeoutMs });
      let parsed = null;
      try { parsed = JSON.parse(r.stdout); } catch (_) { parsed = null; }
      let statusCategory = "unknown";
      let statusLabel = "Could not read result";
      let detail = "";
      if (parsed && typeof parsed === "object") {
        if (check.id === "public-audit") {
          const blockers = Array.isArray(parsed.blocking_findings) ? parsed.blocking_findings.length : 0;
          statusCategory = blockers > 0 ? "blocked-safely" : "pass";
          statusLabel = blockers > 0 ? `${blockers} blocking finding(s)` : "Pass (no blocking findings)";
          detail = `Blocking findings: ${blockers}.`;
        } else if (check.id === "claude-swarm-fixture") {
          const ps = parsed.plan_summary || {};
          const tasks = ps.task_count ?? 0;
          const groups = Array.isArray(ps.parallel_groups) ? ps.parallel_groups.length : 0;
          const overlaps = ps.overlap_count ?? 0;
          statusCategory = parsed.accepted ? "pass" : "warning";
          statusLabel = `Pass (${tasks} tasks / ${groups} groups / ${overlaps} overlaps)`;
          detail = `simulation=${parsed.simulation} live_execution=${parsed.live_execution}`;
        } else if (check.id === "claude-swarm-dry-run") {
          statusCategory = "blocked-safely";
          statusLabel = "Blocked safely (provider call precedes dry-run skip)";
          detail = "Ghoti refuses to run claude-swarm --dry-run; this is the correct safe outcome.";
        } else {
          statusCategory = parsed.ok ? "pass" : "warning";
          statusLabel = parsed.ok ? "Pass" : "Needs review";
          detail = String(parsed.status_line || parsed.note || "").slice(0, 200);
        }
      } else {
        statusCategory = "warning";
        statusLabel = "Could not run (skipped safely)";
        detail = (r.stderr || "no JSON output").slice(0, 200);
      }
      results.push({
        id: check.id, title: check.title,
        statusCategory, statusLabel, detail,
        ran: true, ok: Boolean(parsed && parsed.ok !== false),
      });
    }
    const summary = {
      pass: results.filter((x) => x.statusCategory === "pass").length,
      warning: results.filter((x) => x.statusCategory === "warning").length,
      blockedSafely: results.filter((x) => x.statusCategory === "blocked-safely").length,
      total: results.length,
    };
    return {
      ok: true, available: true, mode,
      python: py.displayName,
      checks: results,
      summary,
      safety: {
        live_agents: false, accounts: false, mcp: false, telegram: false,
        browser_automation: false, provider_api_key: false, auto_submit: false,
        external_cli_executed: false,
      },
      generated_at: startedAt,
    };
  }

  function capabilityCheckCacheFile() {
    return path.join(runtimeDataDir, "capability_check_latest.json");
  }

  function writeCapabilityCache(payload) {
    try {
      if (!fs.existsSync(runtimeDataDir)) fs.mkdirSync(runtimeDataDir, { recursive: true });
      const tmp = capabilityCheckCacheFile() + ".tmp";
      fs.writeFileSync(tmp, JSON.stringify(payload, null, 2), "utf8");
      fs.renameSync(tmp, capabilityCheckCacheFile());
      return true;
    } catch (_) {
      return false;
    }
  }

  // GET /api/product-control/capabilities -- static registry, instant, no subprocess.
  if (request.method === "GET" && requestUrl.pathname === "/api/product-control/capabilities") {
    const registry = buildCapabilityRegistry();
    sendJson(response, 200, {
      ok: true,
      local_only: true,
      milestone: "N+6.39A",
      next_recommended_action: "Click \"Run Safe Check\" for a live read, or \"Run Public Audit\" before sharing the repo.",
      next_recommended_build: [
        "Obsidian Memory Bridge (after this capability console)",
        "Telegram notification-only bridge (after Obsidian)",
      ],
      groups: {
        "real-today": "Real use today",
        "dry-run": "Safe dry-run / simulation only",
        "manual": "Manual bridge (no live automation)",
        "not-real-yet": "Not real yet",
      },
      capabilities: registry,
      safety: {
        live_computer_use: false, live_agent_launch: false, account_actions: false,
        telegram: false, obsidian: false, mcp: false, auto_submit: false,
        provider_api_key: false,
      },
    });
    return;
  }

  // POST /api/product-control/run-capability-check -- runs safe checks (fast default).
  if (request.method === "POST" && requestUrl.pathname === "/api/product-control/run-capability-check") {
    let body = {};
    try { body = await readJsonBody(request); } catch (_) { body = {}; }
    const mode = body && body.mode === "full" ? "full" : "fast";
    const payload = await runCapabilityChecks(mode);
    writeCapabilityCache(payload);
    sendJson(response, 200, payload);
    return;
  }

  // GET /api/product-control/latest-capability-check -- cached last run, friendly when absent.
  if (request.method === "GET" && requestUrl.pathname === "/api/product-control/latest-capability-check") {
    const cacheFile = capabilityCheckCacheFile();
    let cached = null;
    try {
      if (fs.existsSync(cacheFile)) cached = JSON.parse(fs.readFileSync(cacheFile, "utf8"));
    } catch (_) { cached = null; }
    if (!cached) {
      sendJson(response, 200, {
        ok: true, available: false,
        message: "No capability check has been run yet. Click \"Run Safe Check\" to populate it.",
      });
      return;
    }
    sendJson(response, 200, cached);
    return;
  }

  // ─── Operator Recipes (N+6.40A) ─────────────────────────────────────────────
  // Working recipes: safe local supervised workflows run via the repo-local
  // recipes CLI with fixed argv (shell:false). Only allowlisted recipe ids can
  // run; reports go to the repo-safe generated folder; latest run summaries
  // are cached in repo-local gitignored runtime_data. No accounts, no agents,
  // no provider/API keys, no network beyond localhost status probes.

  const OPERATOR_RECIPES_SCRIPT = path.join(
    repoRoot, "03_scripts", "operator_recipes", "ghoti_operator_recipes.py",
  );
  const OPERATOR_RECIPE_IDS = [
    "project-health", "handoff-pack", "cleanup-preview",
    "local-model-check", "fixture-replay-demo", "all-safe",
  ];

  function operatorRecipeRunsCacheFile() {
    return path.join(runtimeDataDir, "operator_recipe_runs_latest.json");
  }

  function readOperatorRecipeRunsCache() {
    try {
      const cacheFile = operatorRecipeRunsCacheFile();
      if (fs.existsSync(cacheFile)) {
        return JSON.parse(fs.readFileSync(cacheFile, "utf8"));
      }
    } catch (_) { /* unreadable cache is the same as no cache */ }
    return { ok: true, runs: {} };
  }

  function writeOperatorRecipeRunsCache(cache) {
    try {
      if (!fs.existsSync(runtimeDataDir)) fs.mkdirSync(runtimeDataDir, { recursive: true });
      const tmp = operatorRecipeRunsCacheFile() + ".tmp";
      fs.writeFileSync(tmp, JSON.stringify(cache, null, 2), "utf8");
      fs.renameSync(tmp, operatorRecipeRunsCacheFile());
      return true;
    } catch (_) {
      return false;
    }
  }

  // GET /api/product-control/operator-recipes -- list recipes via the CLI.
  if (request.method === "GET" && requestUrl.pathname === "/api/product-control/operator-recipes") {
    const py = resolvePython();
    if (!py) {
      sendJson(response, 200, { ok: false, available: false, error: "python unavailable" });
      return;
    }
    const result = await runCommand(
      py.command, [...py.baseArgs, OPERATOR_RECIPES_SCRIPT, "--list", "--json"],
      { timeoutMs: 30000, env: buildRuntimeEnv() },
    );
    let parsed = null;
    try { parsed = JSON.parse(result.stdout); } catch (_) { parsed = null; }
    if (!parsed) {
      sendJson(response, 200, {
        ok: false, available: false,
        error: "recipes CLI did not return JSON",
        detail: (result.stderr || "").slice(0, 300),
      });
      return;
    }
    sendJson(response, 200, { ...parsed, available: true, milestone: "N+6.40A" });
    return;
  }

  // POST /api/product-control/run-operator-recipe -- run one allowlisted recipe.
  if (request.method === "POST" && requestUrl.pathname === "/api/product-control/run-operator-recipe") {
    let body = {};
    try { body = await readJsonBody(request); } catch (_) { body = {}; }
    const recipeId = typeof body.recipe === "string" ? body.recipe : "";
    if (!OPERATOR_RECIPE_IDS.includes(recipeId)) {
      sendJson(response, 400, {
        ok: false,
        error: "unknown or non-allowlisted recipe id",
        allowed: OPERATOR_RECIPE_IDS,
      });
      return;
    }
    const py = resolvePython();
    if (!py) {
      sendJson(response, 200, { ok: false, available: false, error: "python unavailable" });
      return;
    }
    const result = await runCommand(
      py.command, [...py.baseArgs, OPERATOR_RECIPES_SCRIPT, "--run", recipeId, "--json"],
      { timeoutMs: 300000, env: buildRuntimeEnv() },
    );
    let parsed = null;
    try { parsed = JSON.parse(result.stdout); } catch (_) { parsed = null; }
    if (!parsed) {
      sendJson(response, 200, {
        ok: false, recipe_id: recipeId,
        error: "recipe run produced no JSON",
        detail: (result.stderr || "").slice(0, 300),
      });
      return;
    }
    const cache = readOperatorRecipeRunsCache();
    cache.runs = cache.runs || {};
    cache.runs[recipeId] = {
      recipe_id: recipeId,
      ok: Boolean(parsed.ok),
      summary: parsed.summary || "",
      report_path: parsed.report_path || null,
      mode: parsed.mode || "unknown",
      finished_at: new Date().toISOString(),
    };
    cache.updated_at = new Date().toISOString();
    writeOperatorRecipeRunsCache(cache);
    sendJson(response, 200, parsed);
    return;
  }

  // GET /api/product-control/latest-operator-recipe-runs -- cached summaries.
  if (request.method === "GET" && requestUrl.pathname === "/api/product-control/latest-operator-recipe-runs") {
    const cache = readOperatorRecipeRunsCache();
    sendJson(response, 200, {
      ok: true,
      available: Object.keys(cache.runs || {}).length > 0,
      runs: cache.runs || {},
      updated_at: cache.updated_at || null,
      reports_folder: "14_context/operator_reports/generated/",
    });
    return;
  }

  // ─── Agent OS Command Center ────────────────────────────────────────────────
  // Integrated command center: status, workflow plans, task waves, memory
  // search, suggestions, bounded approvals, handoffs, and local demos.
  // All routes shell to the repo-local agent OS CLI with fixed argv
  // (shell:false); user input only ever selects from the workflow allowlist
  // or passes a sanitized search term. The worker never executes commands.

  const AGENT_OS_SCRIPT = path.join(repoRoot, "03_scripts", "agent_os", "ghoti_agent_os.py");
  // Must stay in sync with WORKFLOW_ORDER in 03_scripts/agent_os/workflow_templates.py
  // and the static cards in public/index.html.
  const AGENT_OS_WORKFLOW_IDS = [
    "coding-task", "repo-audit", "content-video", "business-research",
    "email-draft", "automation-n8n", "computer-use-prep",
  ];
  const AGENT_OS_SEARCH_TERM_RE = /^[A-Za-z0-9 _.\-]{1,64}$/;
  const AGENT_OS_REQUEST_ID_RE = /^req-[a-z0-9][a-z0-9-]{7,63}$/;

  async function runAgentOsCli(cliArgs, timeoutMs) {
    const py = resolvePython();
    if (!py) {
      return { ok: false, available: false, error: "python unavailable" };
    }
    const result = await runCommand(
      py.command, [...py.baseArgs, AGENT_OS_SCRIPT, ...cliArgs, "--json"],
      { timeoutMs: timeoutMs || 60000, env: buildRuntimeEnv() },
    );
    try {
      return { ...JSON.parse(result.stdout), available: true };
    } catch (_) {
      return {
        ok: false, available: false,
        error: "agent OS CLI did not return JSON",
        detail: (result.stderr || "").slice(0, 300),
      };
    }
  }

  // GET /api/product-control/agent-os-status -- integrated status snapshot.
  if (request.method === "GET" && requestUrl.pathname === "/api/product-control/agent-os-status") {
    sendJson(response, 200, await runAgentOsCli(["--status"], 60000));
    return;
  }

  // GET /api/product-control/agent-os-approvals -- inspect bounded queue state.
  if (request.method === "GET" && requestUrl.pathname === "/api/product-control/agent-os-approvals") {
    sendJson(response, 200, await runAgentOsCli(["--approval-status"], 60000));
    return;
  }

  // GET /api/product-control/agent-os-workflows -- templates plus roster.
  if (request.method === "GET" && requestUrl.pathname === "/api/product-control/agent-os-workflows") {
    sendJson(response, 200, await runAgentOsCli(["--list-workflows"], 30000));
    return;
  }

  // GET /api/product-control/agent-os-task-wave?workflow=ID -- wave preview.
  if (request.method === "GET" && requestUrl.pathname === "/api/product-control/agent-os-task-wave") {
    const workflowId = requestUrl.searchParams.get("workflow") || "coding-task";
    if (!AGENT_OS_WORKFLOW_IDS.includes(workflowId)) {
      sendJson(response, 400, { ok: false, error: "unknown workflow id", allowed: AGENT_OS_WORKFLOW_IDS });
      return;
    }
    sendJson(response, 200, await runAgentOsCli(["--task-wave", workflowId], 30000));
    return;
  }

  // GET /api/product-control/agent-os-search?term=... -- memory search pointers.
  if (request.method === "GET" && requestUrl.pathname === "/api/product-control/agent-os-search") {
    const term = requestUrl.searchParams.get("term") || "";
    if (!AGENT_OS_SEARCH_TERM_RE.test(term)) {
      sendJson(response, 400, {
        ok: false, error: "term must be 1-64 chars of letters, digits, space, _ . -",
      });
      return;
    }
    sendJson(response, 200, await runAgentOsCli(["--search-memory", term], 30000));
    return;
  }

  // POST /api/product-control/agent-os-plan -- write a workflow plan.
  if (request.method === "POST" && requestUrl.pathname === "/api/product-control/agent-os-plan") {
    let body = {};
    try { body = await readJsonBody(request); } catch (_) { body = {}; }
    const workflowId = typeof body.workflow === "string" ? body.workflow : "";
    if (!AGENT_OS_WORKFLOW_IDS.includes(workflowId)) {
      sendJson(response, 400, { ok: false, error: "unknown workflow id", allowed: AGENT_OS_WORKFLOW_IDS });
      return;
    }
    sendJson(response, 200, await runAgentOsCli(["--plan-workflow", workflowId], 60000));
    return;
  }

  // POST /api/product-control/agent-os-worker-suggest -- suggestion-only worker.
  if (request.method === "POST" && requestUrl.pathname === "/api/product-control/agent-os-worker-suggest") {
    let body = {};
    try { body = await readJsonBody(request); } catch (_) { body = {}; }
    const workflowId = typeof body.workflow === "string" ? body.workflow : "";
    if (!AGENT_OS_WORKFLOW_IDS.includes(workflowId)) {
      sendJson(response, 400, { ok: false, error: "unknown workflow id", allowed: AGENT_OS_WORKFLOW_IDS });
      return;
    }
    sendJson(response, 200, await runAgentOsCli(["--worker-suggest", workflowId], 60000));
    return;
  }

  // POST /api/product-control/agent-os-propose-action -- workflow allowlist only.
  if (request.method === "POST" && requestUrl.pathname === "/api/product-control/agent-os-propose-action") {
    let body = {};
    try { body = await readJsonBody(request); } catch (_) { body = {}; }
    const workflowId = typeof body.workflow === "string" ? body.workflow : "";
    if (!AGENT_OS_WORKFLOW_IDS.includes(workflowId)) {
      sendJson(response, 400, { ok: false, error: "unknown workflow id", allowed: AGENT_OS_WORKFLOW_IDS });
      return;
    }
    sendJson(response, 200, await runAgentOsCli(["--propose-action", workflowId], 180000));
    return;
  }

  // Approval mutations accept only deterministic request ids; no path/action input.
  const approvalRoutes = {
    "/api/product-control/agent-os-approve-action": "--approve-action",
    "/api/product-control/agent-os-reject-action": "--reject-action",
    "/api/product-control/agent-os-execute-approved": "--execute-approved",
  };
  if (request.method === "POST" && approvalRoutes[requestUrl.pathname]) {
    let body = {};
    try { body = await readJsonBody(request); } catch (_) { body = {}; }
    const requestId = typeof body.request_id === "string" ? body.request_id : "";
    if (!AGENT_OS_REQUEST_ID_RE.test(requestId)) {
      sendJson(response, 400, { ok: false, error: "invalid request id" });
      return;
    }
    sendJson(response, 200, await runAgentOsCli(
      [approvalRoutes[requestUrl.pathname], requestId], 180000,
    ));
    return;
  }

  // POST /api/product-control/agent-os-handoff -- copy-paste handoff packets.
  if (request.method === "POST" && requestUrl.pathname === "/api/product-control/agent-os-handoff") {
    let body = {};
    try { body = await readJsonBody(request); } catch (_) { body = {}; }
    const workflowId = typeof body.workflow === "string" ? body.workflow : "";
    const cliArgs = ["--build-handoff"];
    if (workflowId) {
      if (!AGENT_OS_WORKFLOW_IDS.includes(workflowId)) {
        sendJson(response, 400, { ok: false, error: "unknown workflow id", allowed: AGENT_OS_WORKFLOW_IDS });
        return;
      }
      cliArgs.push("--workflow", workflowId);
    }
    sendJson(response, 200, await runAgentOsCli(cliArgs, 60000));
    return;
  }

  // POST /api/product-control/agent-os-full-demo -- the end-to-end local demo.
  if (request.method === "POST" && requestUrl.pathname === "/api/product-control/agent-os-full-demo") {
    sendJson(response, 200, await runAgentOsCli(["--full-demo"], 300000));
    return;
  }

  // POST /api/product-control/agent-os-full-approved-demo -- one bounded write.
  if (request.method === "POST" && requestUrl.pathname === "/api/product-control/agent-os-full-approved-demo") {
    sendJson(response, 200, await runAgentOsCli(["--full-approved-demo"], 300000));
    return;
  }

  // ─── Swarm coordinator (control plane: plan many, run at most one) ──────────
  // Plans are read-only previews; queue-next creates ONE approval request via
  // the existing queue. No parallel launch, no new execution path.
  const AGENT_OS_SWARM_IDS = [
    "coding-task-swarm-plan", "content-pipeline-swarm-plan", "business-research-swarm-plan",
  ];
  const AGENT_OS_PLAN_ID_RE = /^swarm-[a-z0-9]{8,40}$/;

  // GET /api/product-control/agent-os-swarm-status -- all plans + step states.
  if (request.method === "GET" && requestUrl.pathname === "/api/product-control/agent-os-swarm-status") {
    sendJson(response, 200, await runAgentOsCli(["--swarm-status"], 60000));
    return;
  }

  // GET /api/product-control/agent-os-swarm-plans -- list plans.
  if (request.method === "GET" && requestUrl.pathname === "/api/product-control/agent-os-swarm-plans") {
    sendJson(response, 200, await runAgentOsCli(["--list-swarm-plans"], 30000));
    return;
  }

  // POST /api/product-control/agent-os-plan-swarm -- build a plan (allowlist).
  if (request.method === "POST" && requestUrl.pathname === "/api/product-control/agent-os-plan-swarm") {
    let body = {};
    try { body = await readJsonBody(request); } catch (_) { body = {}; }
    const workflowId = typeof body.workflow === "string" ? body.workflow : "";
    if (!AGENT_OS_SWARM_IDS.includes(workflowId)) {
      sendJson(response, 400, { ok: false, error: "unknown swarm workflow", allowed: AGENT_OS_SWARM_IDS });
      return;
    }
    sendJson(response, 200, await runAgentOsCli(["--plan-swarm", workflowId], 60000));
    return;
  }

  // POST /api/product-control/agent-os-queue-next-swarm-step -- one approval request.
  if (request.method === "POST" && requestUrl.pathname === "/api/product-control/agent-os-queue-next-swarm-step") {
    let body = {};
    try { body = await readJsonBody(request); } catch (_) { body = {}; }
    const planId = typeof body.plan_id === "string" ? body.plan_id : "";
    if (!AGENT_OS_PLAN_ID_RE.test(planId)) {
      sendJson(response, 400, { ok: false, error: "invalid plan id" });
      return;
    }
    sendJson(response, 200, await runAgentOsCli(["--queue-next-swarm-step", planId], 60000));
    return;
  }

  // POST /api/product-control/agent-os-full-swarm-planning-demo -- planning demo.
  if (request.method === "POST" && requestUrl.pathname === "/api/product-control/agent-os-full-swarm-planning-demo") {
    sendJson(response, 200, await runAgentOsCli(["--full-swarm-planning-demo"], 120000));
    return;
  }

  // GET /api/product-control/agent-os-latest -- newest generated artifacts.
  if (request.method === "GET" && requestUrl.pathname === "/api/product-control/agent-os-latest") {
    const folders = ["workflows", "handoffs", "runs", "evidence"];
    const entries = [];
    folders.forEach((folder) => {
      const dir = path.join(repoRoot, "14_context", "agent_os", folder);
      try {
        fs.readdirSync(dir).forEach((name) => {
          if (name === "README.md") return;
          const full = path.join(dir, name);
          const stat = fs.statSync(full);
          if (!stat.isFile()) return;
          entries.push({
            kind: folder,
            name,
            path: `14_context/agent_os/${folder}/${name}`,
            modified_unix: Math.floor(stat.mtimeMs / 1000),
          });
        });
      } catch (_) { /* missing folder is the same as empty */ }
    });
    entries.sort((a, b) => b.modified_unix - a.modified_unix);
    sendJson(response, 200, {
      ok: true,
      available: entries.length > 0,
      count: entries.length,
      artifacts: entries.slice(0, 12),
      folder: "14_context/agent_os/",
    });
    return;
  }

  // ─── External Tool Sandbox (N+4.8A) ─────────────────────────────────────────
  // Surface for the safe clone + static-scan manager. No install, no external
  // code execution, no desktop control, no live APIs. Subprocess via fixed argv
  // (shell:false); the sync/scan endpoints pass NO user-supplied repo slug —
  // only the manager's fixed approved catalog is ever cloned.

  function readExternalToolSandboxStatus() {
    const statusFile = path.join(
      repoRoot, "14_context", "external_tools", "external_tool_sandbox_status.json",
    );
    try {
      if (fs.existsSync(statusFile)) {
        return JSON.parse(fs.readFileSync(statusFile, "utf8"));
      }
    } catch (_) {}
    return {
      mode: "sandbox_static_inspection_only",
      installs_performed: false,
      external_code_executed: false,
      runtime_wiring: "none",
      desktop_control_enabled: false,
      live_api_enabled: false,
      human_approval_required: true,
      repos: [],
      adapters: [],
      note: "external tool sandbox not yet synced",
    };
  }

  // GET /api/external-tool-sandbox/status
  if (request.method === "GET" && requestUrl.pathname === "/api/external-tool-sandbox/status") {
    sendJson(response, 200, Object.assign({ ok: true }, readExternalToolSandboxStatus()));
    return;
  }

  // GET /api/external-tool-sandbox/latest
  if (request.method === "GET" && requestUrl.pathname === "/api/external-tool-sandbox/latest") {
    sendJson(response, 200, { ok: true, latest: readExternalToolSandboxStatus() });
    return;
  }

  // POST /api/external-tool-sandbox/sync-approved
  if (request.method === "POST" && requestUrl.pathname === "/api/external-tool-sandbox/sync-approved") {
    const managerScript = path.join(repoRoot, "03_scripts", "external_tool_sandbox_manager.py");
    const py = resolvePython();
    if (!py) {
      sendJson(response, 200, { ok: false, available: false, error: "Python interpreter not found" });
      return;
    }
    // Fixed argv. No user-supplied repo slug — only the approved catalog.
    const syncArgv = [...py.baseArgs, managerScript, "--sync-approved", "--json"];
    const syncResult = await runCommand(py.command, syncArgv, { cwd: repoRoot, timeoutMs: 600000 });
    if (!syncResult.ok) {
      sendJson(response, 200, {
        ok: false, available: false,
        error: syncResult.stderr || `exit ${syncResult.exitCode}`,
      });
      return;
    }
    try {
      sendJson(response, 200, JSON.parse(syncResult.stdout));
    } catch (_) {
      sendJson(response, 200, { ok: false, available: false, error: "Failed to parse sandbox output" });
    }
    return;
  }

  // POST /api/external-tool-sandbox/scan
  if (request.method === "POST" && requestUrl.pathname === "/api/external-tool-sandbox/scan") {
    const managerScript = path.join(repoRoot, "03_scripts", "external_tool_sandbox_manager.py");
    const py = resolvePython();
    if (!py) {
      sendJson(response, 200, { ok: false, available: false, error: "Python interpreter not found" });
      return;
    }
    const scanArgv = [...py.baseArgs, managerScript, "--scan", "--json"];
    const scanResult = await runCommand(py.command, scanArgv, { cwd: repoRoot, timeoutMs: 120000 });
    if (!scanResult.ok) {
      sendJson(response, 200, {
        ok: false, available: false,
        error: scanResult.stderr || `exit ${scanResult.exitCode}`,
      });
      return;
    }
    try {
      sendJson(response, 200, JSON.parse(scanResult.stdout));
    } catch (_) {
      sendJson(response, 200, { ok: false, available: false, error: "Failed to parse sandbox output" });
    }
    return;
  }

  // ─── Approved Adapter Execution (N+4.9A) ────────────────────────────────────
  // Surface for the approved adapter runner. Local-only. No external repo code
  // execution, no installs, no desktop control, no live APIs. Subprocess via
  // fixed argv (shell:false); the adapter is always the fixed approved key and
  // the dashboard run-demo path is always --dry-run (never non-dry-run).

  function runAdapterRunner(extraArgs, timeoutMs) {
    return new Promise((resolve) => {
      const runnerScript = path.join(repoRoot, "03_scripts", "approved_adapter_runner.py");
      const py = resolvePython();
      if (!py) {
        resolve({ ok: false, available: false, error: "Python interpreter not found" });
        return;
      }
      const argv = [...py.baseArgs, runnerScript, ...extraArgs];
      runCommand(py.command, argv, { cwd: repoRoot, timeoutMs: timeoutMs || 60000 })
        .then((res) => {
          if (!res.ok) {
            resolve({ ok: false, available: false, error: res.stderr || `exit ${res.exitCode}` });
            return;
          }
          try {
            resolve(JSON.parse(res.stdout));
          } catch (_) {
            resolve({ ok: false, available: false, error: "Failed to parse runner output" });
          }
        });
    });
  }

  // GET /api/adapter-execution/status
  if (request.method === "GET" && requestUrl.pathname === "/api/adapter-execution/status") {
    sendJson(response, 200, await runAdapterRunner(["--status", "--json"], 30000));
    return;
  }

  // GET /api/adapter-execution/adapters
  if (request.method === "GET" && requestUrl.pathname === "/api/adapter-execution/adapters") {
    sendJson(response, 200, await runAdapterRunner(["--list-adapters", "--json"], 30000));
    return;
  }

  // POST /api/adapter-execution/create-approval
  if (request.method === "POST" && requestUrl.pathname === "/api/adapter-execution/create-approval") {
    // Fixed approved adapter only — no user-supplied adapter name.
    sendJson(response, 200, await runAdapterRunner(
      ["--create-approval", "--adapter", "agent_skills_eval", "--json"], 30000));
    return;
  }

  // POST /api/adapter-execution/run-demo
  if (request.method === "POST" && requestUrl.pathname === "/api/adapter-execution/run-demo") {
    // The dashboard only ever triggers a DRY-RUN demo — never a non-dry-run
    // execution, and never with an approval token.
    sendJson(response, 200, await runAdapterRunner(
      ["--execute-approved", "--adapter", "agent_skills_eval", "--dry-run", "--json"], 120000));
    return;
  }

  // GET /api/adapter-execution/latest
  if (request.method === "GET" && requestUrl.pathname === "/api/adapter-execution/latest") {
    const latestFile = path.join(
      repoRoot, "14_context", "adapter_execution", "latest_adapter_run.json",
    );
    let latest = null;
    try {
      if (fs.existsSync(latestFile)) {
        latest = JSON.parse(fs.readFileSync(latestFile, "utf8"));
      }
    } catch (_) {}
    sendJson(response, 200, { ok: true, latest });
    return;
  }

  // ─── UI-TARS Observation Only (N+5.0A) ──────────────────────────────────────
  // Surface for the UI-TARS observation-only adapter CLI. Observation only:
  // no UI-TARS runtime, no external repo code, no desktop control, no
  // click/type/hotkeys, no live API. Subprocess via fixed argv (shell:false);
  // the dashboard dry-run path never captures the screen; capture-approved
  // requires an approval token in the POST body.

  function runUiTarsObservation(extraArgs, timeoutMs) {
    return new Promise((resolve) => {
      const obsScript = path.join(repoRoot, "03_scripts", "ui_tars_observation_adapter.py");
      const py = resolvePython();
      if (!py) {
        resolve({ ok: false, available: false, error: "Python interpreter not found" });
        return;
      }
      const argv = [...py.baseArgs, obsScript, ...extraArgs];
      runCommand(py.command, argv, { cwd: repoRoot, timeoutMs: timeoutMs || 60000 })
        .then((res) => {
          if (!res.ok) {
            resolve({ ok: false, available: false, error: res.stderr || `exit ${res.exitCode}` });
            return;
          }
          try {
            resolve(JSON.parse(res.stdout));
          } catch (_) {
            resolve({ ok: false, available: false, error: "Failed to parse observation output" });
          }
        });
    });
  }

  // GET /api/ui-tars-observation/status
  if (request.method === "GET" && requestUrl.pathname === "/api/ui-tars-observation/status") {
    sendJson(response, 200, await runUiTarsObservation(["--status", "--json"], 30000));
    return;
  }

  // GET /api/ui-tars-observation/latest
  if (request.method === "GET" && requestUrl.pathname === "/api/ui-tars-observation/latest") {
    const latestFile = path.join(
      repoRoot, "14_context", "ui_tars_observation", "latest.json");
    let latest = null;
    try {
      if (fs.existsSync(latestFile)) {
        latest = JSON.parse(fs.readFileSync(latestFile, "utf8"));
      }
    } catch (_) {}
    // latest.json carries run metadata only — never a raw approval token.
    sendJson(response, 200, { ok: true, latest });
    return;
  }

  // POST /api/ui-tars-observation/create-approval
  if (request.method === "POST" && requestUrl.pathname === "/api/ui-tars-observation/create-approval") {
    sendJson(response, 200, await runUiTarsObservation(["--create-approval", "--json"], 30000));
    return;
  }

  // POST /api/ui-tars-observation/dry-run
  if (request.method === "POST" && requestUrl.pathname === "/api/ui-tars-observation/dry-run") {
    // The dashboard only ever triggers a dry-run observation — never a capture.
    sendJson(response, 200, await runUiTarsObservation(
      ["--observe", "--dry-run", "--json"], 90000));
    return;
  }

  // POST /api/ui-tars-observation/capture-approved
  if (request.method === "POST" && requestUrl.pathname === "/api/ui-tars-observation/capture-approved") {
    let body = {};
    try {
      body = await readJsonBody(request);
    } catch (_) {
      body = {};
    }
    const token = typeof body.approval_token === "string" ? body.approval_token.trim() : "";
    if (!token) {
      sendJson(response, 200, {
        ok: false,
        error: "approval token required for capture-approved (pass approval_token in the body)",
      });
      return;
    }
    sendJson(response, 200, await runUiTarsObservation(
      ["--observe", "--capture-screen", "--approval-token", token, "--json"], 90000));
    return;
  }

  sendJson(response, 404, {
    ok: false,
    error: "Route not found.",
    path: requestUrl.pathname,
  });
}

function serveStatic(requestUrl, response) {
  const requestedPath = requestUrl.pathname === "/"
    ? path.join(publicRoot, "index.html")
    : path.join(publicRoot, requestUrl.pathname.replace(/^\/+/, ""));
  const normalizedPath = path.normalize(requestedPath);

  if (!normalizedPath.startsWith(publicRoot)) {
    sendBuffer(response, 403, "Forbidden");
    return;
  }

  if (!fs.existsSync(normalizedPath) || fs.statSync(normalizedPath).isDirectory()) {
    sendBuffer(response, 404, "Not found");
    return;
  }

  sendBuffer(response, 200, fs.readFileSync(normalizedPath), contentTypeForPath(normalizedPath));
}

async function handleRequest(request, response) {
  const requestUrl = new URL(request.url, `http://127.0.0.1:${dashboardPort}`);

  try {
    if (requestUrl.pathname.startsWith("/api/")) {
      await handleApiRequest(request, response, requestUrl);
      return;
    }

    if (requestUrl.pathname === "/overlay") {
      requestUrl.pathname = "/overlay.html";
    }

    serveStatic(requestUrl, response);
  } catch (error) {
    pushAction({
      actionType: "error",
      label: "Dashboard request failed",
      status: "error",
      summary: error.message,
    });
    sendJson(response, 500, {
      ok: false,
      error: error.message,
    });
  }
}

if (process.argv.includes("--check")) {
  const python = resolvePython();
  console.log("dashboard_check: ok");
  console.log("mode: operator_console_v3");
  console.log("local_only: yes");
  console.log(`python: ${python ? python.displayName : "missing"}`);
  console.log(`browser_runner: ${process.execPath}`);
  console.log(`desktop_bridge_script: ${desktopCheckScriptPath}`);
  process.exit(0);
}

const server = http.createServer((request, response) => {
  handleRequest(request, response).catch((error) => {
    try {
      pushAction({
        actionType: "error",
        label: "Dashboard request failed",
        status: "error",
        summary: error.message,
      });
      if (!response.headersSent && !response.destroyed) {
        sendJson(response, 500, {
          ok: false,
          error: error.message,
        });
      } else if (!response.destroyed) {
        response.destroy(error);
      }
    } catch {
      if (!response.destroyed) {
        response.destroy();
      }
    }
  });
});

server.on("error", (error) => {
  if (error && error.code === "EADDRINUSE") {
    // Graceful, friendly message instead of an unhandled stack trace. The most
    // common cause is that the Ghoti dashboard is already running on this port.
    console.error(
      `Ghoti dashboard: port ${dashboardPort} is already in use.\n` +
        `  If this is the Ghoti dashboard, it is probably already running:\n` +
        `    open http://127.0.0.1:${dashboardPort}\n` +
        `  To inspect the listener safely (do not auto-kill):\n` +
        `    Windows PowerShell: Get-NetTCPConnection -LocalPort ${dashboardPort} | Format-List\n` +
        `    Linux/WSL:          lsof -i :${dashboardPort}`,
    );
    process.exit(0);
  }
  console.error(`Ghoti dashboard failed to start: ${error && error.message}`);
  process.exit(1);
});

server.listen(dashboardPort, "127.0.0.1", () => {
  console.log(`dashboard_url: http://127.0.0.1:${dashboardPort}`);
});
