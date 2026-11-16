"use strict";

const APP_VERSION = "2026.08.01.4";
const GHOTI_FISH_URL = `/assets/ghoti_fish_original.png?v=${APP_VERSION}`;
const APP_UPDATE_MESSAGE = "If Windows/iPhone installed icon is still old, uninstall and reinstall the Ghoti PWA.";
const PAIRING_HEADER = "X-Ghoti-Pairing";
const OPTIONAL_STATUS_COMMAND_IDS = new Set([
  "ghoti_chat_freeform_status", "voice_status", "app_update_status",
  "pwa_icon_refresh_help", "full_computer_use_status", "connector_setup_status",
  "orchestration_status", "paperclip_status", "ruflo_status", "ghoti_full_status",
  "orchestration_profile_status", "orchestration_scan_modules",
  "desktop_operator_status", "desktop_operator_list_apps",
  "desktop_operator_list_actions",
  "agent_status", "agent_capabilities", "agent_last_result",
  "agent_supervised_status", "agent_observe_screen",
  "agent_icon_status", "agent_icon_reset_help", "agent_voice_status",
  "unified_agent_status", "obsidian_sync_status", "github_sync_status",
  "github_local_summary", "github_remote_status", "paperclip_agent_status",
  "ruflo_agent_status", "ghoti_os_status", "ghoti_os_memory_status",
  "ghoti_os_project_status", "ghoti_os_swarm_status", "ghoti_os_routine_status",
  "ghoti_os_connector_status", "ghoti_os_content_status", "ghoti_os_live_approval_status",
  "computer_use_status", "computer_use_observe", "computer_use_stop",
  "computer_use_reset_stop", "computer_use_last_screenshot", "computer_use_demo_safe",
]);
const CLIENT_COMMAND_IDS = new Set([
  "auto_fixture_blocked", "auto_fixture_safe", "clipper_render_latest", "clipper_status",
  "app_update_status", "connector_setup_status", "full_computer_use_status",
  "blocked_live_test", "ghoti_full_status", "orchestration_status",
  "orchestration_local_demo", "orchestration_profile_status",
  "orchestration_sandbox_demo", "orchestration_scan_modules",
  "desktop_operator_status", "desktop_operator_list_apps",
  "desktop_operator_list_actions", "desktop_open_dashboard",
  "desktop_open_obsidian", "desktop_open_vscode", "desktop_open_repo_folder",
  "desktop_open_clipper_input", "desktop_open_proof_videos",
  "desktop_run_local_status", "desktop_run_orchestration_demo",
  "desktop_blocked_live_test",
  "agent_status", "agent_capabilities", "agent_last_result",
  "agent_supervised_status", "agent_observe_screen",
  "agent_overlay_listening", "agent_overlay_thinking", "agent_overlay_working",
  "agent_overlay_done", "agent_overlay_error", "agent_voice_status",
  "agent_icon_status", "agent_icon_reset_help", "agent_open_dashboard",
  "agent_open_obsidian", "agent_open_vscode", "agent_open_repo",
  "agent_open_clipper_input", "agent_open_clips", "agent_run_status",
  "agent_run_local_demo", "agent_stop",
  "unified_agent_status", "obsidian_sync_status", "obsidian_update_status",
  "obsidian_open_live_status", "github_sync_status", "github_local_summary",
  "github_remote_status", "github_push_current_branch", "paperclip_agent_status",
  "ruflo_agent_status",
  "ghoti_os_status", "ghoti_os_memory_status", "ghoti_os_project_status",
  "ghoti_os_swarm_status", "ghoti_os_routine_status", "ghoti_os_connector_status",
  "ghoti_os_content_status", "ghoti_os_live_approval_status",
  "computer_use_status", "computer_use_observe", "computer_use_stop",
  "computer_use_reset_stop", "computer_use_last_screenshot", "computer_use_demo_safe",
  "paperclip_sandbox_demo", "paperclip_setup_check", "paperclip_status",
  "ruflo_sandbox_demo", "ruflo_setup_check", "ruflo_status",
  "ghoti_chat_freeform_status", "ghoti_chat_status", "ghoti_chat_summary",
  "ghoti_self_evolve_list", "pwa_icon_refresh_help", "voice_status",
  "ghoti_self_evolve_propose", "ghoti_self_evolve_status",
  "local_ai_status", "post_export_manual", "post_queue_status", "real_cu_blocked_action_test",
  "real_cu_full_local_demo", "real_cu_local_fixture", "real_cu_scan_repos", "real_cu_status",
  "run_everything_local", "system_status",
]);
const COMPUTER_USE_ACTIVE_STATES = new Set(["observing", "planning", "awaiting_confirmation", "controlling"]);
const COMPUTER_USE_POLL_MS = 1500;

const state = {
  status: null, evidence: [], logs: [], logFiles: [], proofs: [], packages: [], safety: null,
  mobile: null, pairingValue: "", pairingPromise: null, pairingResolve: null,
  availableCommands: new Set(), installPrompt: null, chatMessages: [],
  evolveQueue: [], backendEvolveStatus: null, backendEvolveProposals: [],
  recognition: null, latestGhotiMessage: "", voiceListening: false,
  freeformStatus: null, voiceStatus: null, fullComputerStatus: null, connectorStatus: null,
  orchestrationStatus: null, paperclipStatus: null, rufloStatus: null,
  ghotiFullStatus: null, systemMap: null, systemMapFilter: "ALL",
  dashboardModules: null, profileStatus: null, moduleScan: null,
  desktopOperatorStatus: null, desktopApps: [], desktopActions: [],
  agentStatus: null, agentCapabilities: null, agentSupervisedStatus: null, agentState: "idle",
  pendingConfirmation: null, agentRequestController: null,
  unifiedAgentStatus: null, obsidianStatus: null, githubStatus: null,
  githubLocalSummary: null, githubRemoteStatus: null,
  osStatus: null, osMemoryStatus: null, osProjectStatus: null, osSwarmStatus: null,
  osRoutineStatus: null, osConnectorStatus: null, osContentStatus: null,
  osLiveApprovalStatus: null, osMemoryQuery: "",
  selectedModelProvider: "ollama", selectedModel: "gemma3:4b",
  computerUseSession: null, computerUsePanelManuallyHidden: false,
  computerUsePollTimer: null, computerUsePollBusy: false,
  speechSpeaking: false,
};

const VIEW_ALIASES = Object.freeze({ chat: "home" });

const AGENT_API_PATHS = Object.freeze({
  status: "/api/agent/status",
  message: "/api/agent/message",
  confirm: "/api/agent/confirm",
  cancel: "/api/agent/cancel",
});
const AGENT_OVERLAY_COMMANDS = Object.freeze({
  listening: "agent_overlay_listening",
  thinking: "agent_overlay_thinking",
  observing: "agent_overlay_working",
  planning: "agent_overlay_thinking",
  "needs-confirmation": "agent_overlay_thinking",
  "awaiting-confirmation": "agent_overlay_thinking",
  working: "agent_overlay_working",
  controlling: "agent_overlay_working",
  done: "agent_overlay_done",
  error: "agent_overlay_error",
  stopped: "agent_overlay_error",
});
const AGENT_STATE_COPY = Object.freeze({
  idle: "Ready for a local conversation or supervised task.",
  listening: "Listening in this browser. Audio is not uploaded or stored.",
  thinking: "Ghoti is thinking locally.",
  observing: "Ghoti is observing your local screen.",
  planning: "Ghoti is preparing one supervised local action.",
  "needs-confirmation": "Plan ready. Review the exact action and target, then confirm or cancel.",
  "awaiting-confirmation": "Plan ready. Review the exact action and target, then confirm or cancel.",
  working: "Ghoti is working through the requested local tool.",
  controlling: "Ghoti is controlling your PC for one confirmed local action.",
  done: "Done. Review the result and evidence below.",
  error: "Stopped safely. Review the structured error below.",
  stopped: "Stopped. Ctrl+8 / STOP_AGENT prevents further desktop control until reset.",
});

function setAgentState(nextState, detail = "", notifyOverlay = true) {
  if (!Object.prototype.hasOwnProperty.call(AGENT_STATE_COPY, nextState)) {
    nextState = "error";
  }
  state.agentState = nextState;
  document.body.dataset.agentState = nextState;
  const shell = document.getElementById("agent-shell");
  if (shell) shell.dataset.agentState = nextState;
  for (const id of ["agent-state-pill", "global-agent-state"]) {
    const pill = document.getElementById(id);
    if (pill) {
      pill.dataset.state = nextState;
      pill.textContent = nextState.toUpperCase();
    }
  }
  text("agent-state-copy", detail || AGENT_STATE_COPY[nextState]);
  text("agent-fish-bubble", detail || AGENT_STATE_COPY[nextState]);
  if (notifyOverlay && AGENT_OVERLAY_COMMANDS[nextState]) {
    void runAgentOverlay(AGENT_OVERLAY_COMMANDS[nextState]);
  }
}

function inferredAgentTool(message) {
  const value = String(message || "").toLowerCase();
  const matches = [
    [["project"], "Project planner"],
    [["swarm", "worker"], "Swarm planner"],
    [["clip", "video", "youtube", "tiktok"], "Rights-gated content planner"],
    [["obsidian", "memory"], "Shared memory"],
    [["github", "git"], "GitHub status"],
    [["paperclip"], "Paperclip sandbox status"],
    [["ruflo"], "Ruflo sandbox status"],
    [["observe", "screen", "computer use", "click", "type ", "hotkey", "mouse"], "Computer Use"],
  ];
  const found = matches.find(([terms]) => terms.some(term => value.includes(term)));
  return found ? found[1] : "Local assistant";
}

function setAgentActivity(stage, message = "") {
  const activity = document.getElementById("agent-activity");
  const root = document.getElementById("agent-conversation");
  if (!activity || !root) return;
  const stageIndex = { thinking: 0, observing: 1, planning: 0, working: 1, controlling: 1, evidence: 2, done: 3 }[stage] ?? 0;
  const labels = {
    thinking: "Ghoti is thinking",
    observing: "Ghoti is observing your screen",
    planning: "Ghoti is planning one supervised action",
    working: `Ghoti is using ${inferredAgentTool(message)}`,
    controlling: "Ghoti is controlling your PC for one confirmed action",
    evidence: "Ghoti is preparing the result and evidence",
    done: "Done",
  };
  activity.hidden = false;
  activity.dataset.stage = stage;
  text("agent-activity-badge", stage === "evidence" ? "FINISHING" : stage.toUpperCase());
  const activityText = document.getElementById("agent-activity-text");
  if (activityText) {
    activityText.replaceChildren(document.createTextNode(labels[stage] || labels.thinking));
    if (stage !== "done") {
      const dots = document.createElement("span");
      dots.className = "typing-dots";
      dots.setAttribute("aria-hidden", "true");
      for (let i = 0; i < 3; i += 1) {
        const dot = document.createElement("span");
        dot.textContent = ".";
        dots.append(dot);
      }
      activityText.append(dots);
    }
  }
  document.querySelectorAll("#agent-progress-steps li").forEach((item, index) => {
    item.dataset.state = index < stageIndex ? "done" : (index === stageIndex ? "active" : "pending");
  });
  root.append(activity);
  root.scrollTop = root.scrollHeight;
}

function hideAgentActivity() {
  const activity = document.getElementById("agent-activity");
  if (activity) activity.hidden = true;
}

function computerUseCommandAvailable(command = null) {
  if (command) return CLIENT_COMMAND_IDS.has(command) && state.availableCommands.has(command);
  return computerUseCommandAvailable("computer_use_status");
}

function isComputerUseMessage(message) {
  return /\b(observe screen|computer use|desktop control|click at|type |press |hotkey|move (?:the )?mouse|mouse to)\b/i
    .test(String(message || ""));
}

function computerUsePayload(result = {}) {
  return result && typeof result.json === "object" ? result.json : result;
}

function reconcileComputerUseStatus(observationResult = {}, statusResult = {}) {
  const observation = computerUsePayload(observationResult);
  const status = computerUsePayload(statusResult);
  return {
    ...observation,
    computer_use_session: observation.computer_use_session || observation.session_id || status.computer_use_session,
    computer_use_state: status.computer_use_state || observation.computer_use_state || observation.state,
    current_window: observation.current_window || observation.active_window || status.current_window || status.active_window,
    mouse_position: observation.mouse_position || status.mouse_position,
    screenshot_path: observation.screenshot_path || observation.last_screenshot || status.screenshot_path || status.last_screenshot,
    active_control: status.active_control === true,
    stopped: status.stopped === true,
    stopped_by_ctrl8: status.stopped_by_ctrl8 === true,
    last_action_result: observation.last_action_result || status.last_action_result,
    evidence_path: observation.evidence_path || status.evidence_path,
  };
}

function normalizeComputerUseState(value) {
  return String(value || "").trim().toLowerCase().replaceAll(" ", "_").replaceAll("-", "_");
}

function computerUseSummary(result = {}) {
  const payload = computerUsePayload(result);
  const detail = payload.detail && typeof payload.detail === "object" ? payload.detail : {};
  const session = payload.computer_use_session && typeof payload.computer_use_session === "object" ?
    payload.computer_use_session :
    (detail.computer_use_session && typeof detail.computer_use_session === "object" ? detail.computer_use_session : {});
  const reportedFlag = key => {
    for (const source of [payload, session, detail]) {
      if (Object.prototype.hasOwnProperty.call(source, key)) return source[key] === true;
    }
    return false;
  };
  const sessionId = typeof payload.computer_use_session === "string" ? payload.computer_use_session :
    (payload.session_id || session.session_id || detail.session_id ||
      (typeof detail.computer_use_session === "string" ? detail.computer_use_session : null));
  const mouse = payload.mouse_position || session.mouse_position || detail.mouse_position || {};
  const mousePoint = Array.isArray(mouse) ? { x: mouse[0], y: mouse[1] } : mouse;
  const plan = payload.plan && typeof payload.plan === "object" ? payload.plan : {};
  const steps = Array.isArray(plan.steps) ? plan.steps :
    (Array.isArray(payload.planned_actions) ? payload.planned_actions : []);
  const firstStep = steps[0] || {};
  const screenshot = payload.last_screenshot || payload.screenshot_path || session.last_screenshot ||
    detail.last_screenshot || detail.screenshot_url || detail.screenshot_path || null;
  const explicitState = payload.computer_use_state || payload.state || session.state ||
    detail.computer_use_state || detail.state || null;
  const normalizedState = normalizeComputerUseState(explicitState ||
    (payload.needs_confirmation ? "awaiting_confirmation" : payload.outcome || "ready"));
  const lastActionValue = payload.last_action_result || payload.last_action || session.last_action ||
    detail.last_action_result || detail.last_action || null;
  const stateIsRelevant = ["observing", "planning", "awaiting_confirmation", "controlling", "stopped", "error"]
    .includes(normalizedState);
  const relevant = Boolean(
    payload.needs_confirmation || sessionId || stateIsRelevant || screenshot || payload.screenshot_status ||
    ["click", "type_text", "hotkey", "move_mouse", "observe_screen"].includes(firstStep.type)
  );
  return {
    relevant,
    hasExplicitState: Boolean(explicitState),
    state: normalizedState || "ready",
    sessionId: sessionId || "Not started",
    activeWindow: payload.current_window || payload.active_window || session.active_window || detail.active_window || "Not reported",
    mouse: mousePoint && (mousePoint.x != null || mousePoint.y != null) ?
      `x=${mousePoint.x ?? "?"}, y=${mousePoint.y ?? "?"}` : "Not reported",
    lastAction: lastActionValue && typeof lastActionValue === "object" ? formatAgentItem(lastActionValue) :
      (lastActionValue || (firstStep.type ? formatAgentItem(firstStep) : "None this session")),
    evidence: payload.evidence_path || session.evidence_path || detail.evidence_path || "none reported",
    screenshot,
    screenshotReason: payload.screenshot_skip_reason || detail.screenshot_skip_reason || null,
    activeControl: reportedFlag("active_control"),
    stoppedByCtrl8: reportedFlag("stopped_by_ctrl8"),
    stopped: reportedFlag("stopped"),
  };
}

function safeComputerUseScreenshotPath(value) {
  const path = String(value || "");
  return /^\/(?:api|assets|static|icons)\/[A-Za-z0-9._~!$&'()*+,;=:@%/-]+$/.test(path) &&
    !path.includes("..") && !path.includes("//");
}

function stopComputerUsePolling() {
  if (state.computerUsePollTimer) clearTimeout(state.computerUsePollTimer);
  state.computerUsePollTimer = null;
}

function scheduleComputerUsePolling(computerState) {
  stopComputerUsePolling();
  if (!COMPUTER_USE_ACTIVE_STATES.has(normalizeComputerUseState(computerState)) ||
      !computerUseCommandAvailable("computer_use_status")) return;
  state.computerUsePollTimer = setTimeout(() => {
    state.computerUsePollTimer = null;
    void pollComputerUseStatus();
  }, COMPUTER_USE_POLL_MS);
}

function updateComputerUseBanner(summary) {
  const banner = document.getElementById("computer-use-control-banner");
  if (!banner) return;
  const stopped = summary.stoppedByCtrl8 || summary.stopped;
  const controlling = summary.activeControl || summary.state === "controlling";
  banner.hidden = !stopped && !controlling;
  banner.classList.toggle("stopped", stopped);
  if (stopped) {
    text("computer-use-control-banner-title", "Stopped by Ctrl+8 / STOP_AGENT");
    text("computer-use-control-banner-copy", "Desktop control is blocked until Reset stop is confirmed by the backend.");
  } else if (controlling) {
    text("computer-use-control-banner-title", "Ghoti is controlling your PC");
    text("computer-use-control-banner-copy", "One confirmed local action is active. Press Ctrl+8 anytime to stop Ghoti.");
  }
}

function applyComputerUseAgentState(summary) {
  if (!summary.hasExplicitState) return;
  if (summary.state === "awaiting_confirmation" && !state.pendingConfirmation) return;
  const uiState = {
    observing: "observing",
    planning: "planning",
    awaiting_confirmation: "needs-confirmation",
    controlling: "controlling",
    stopped: "stopped",
    error: "error",
    done: "done",
  }[summary.state];
  if (uiState) setAgentState(uiState, AGENT_STATE_COPY[uiState], false);
}

function updateComputerUsePanel(result = {}, requestedMessage = "") {
  const panel = document.getElementById("computer-use-panel");
  const shell = document.getElementById("agent-shell");
  if (!panel || !shell) return;
  const payload = computerUsePayload(result);
  const summary = computerUseSummary(payload);
  const requested = isComputerUseMessage(requestedMessage);
  if (!summary.relevant && !requested) return;
  const orphanedPending = summary.state === "awaiting_confirmation" &&
    !state.pendingConfirmation && payload.needs_confirmation !== true;
  const activeState = COMPUTER_USE_ACTIVE_STATES.has(summary.state) || summary.activeControl ||
    summary.stoppedByCtrl8 || summary.stopped || payload.needs_confirmation;
  if (panel.hidden && !requested && !activeState) {
    state.computerUseSession = { ...summary, requestedMessage };
    updateComputerUseBanner(summary);
    if (summary.hasExplicitState) scheduleComputerUsePolling(summary.state);
    return;
  }
  state.computerUsePanelManuallyHidden = false;
  state.computerUseSession = { ...summary, requestedMessage };
  panel.hidden = false;
  shell.classList.add("computer-use-active");
  const normalizedState = orphanedPending ? "PENDING PLAN NOT LOADED" :
    String(summary.state || "ready").toUpperCase().replaceAll("_", " ");
  const status = document.getElementById("computer-use-panel-state");
  if (status) {
    status.textContent = normalizedState;
    status.className = `tool-status ${/STOP|BLOCK|ERROR|DENIED/.test(normalizedState) ? "blocked" :
      (/CONFIRM|PENDING|REVIEW/.test(normalizedState) ? "needs-ivan" : "ready")}`;
  }
  text("computer-use-panel-copy", orphanedPending ?
    "A backend session reports a pending plan, but its exact action is not loaded. Start a fresh demo or press STOP; confirmation stays unavailable." :
    (payload.needs_confirmation || summary.state === "awaiting_confirmation" ?
    "Waiting for confirmation. Nothing touches the mouse or keyboard until Confirm once is pressed." :
    (summary.activeControl || summary.state === "controlling" ? "Ghoti is controlling your PC for one confirmed local action." :
      (summary.state === "observing" ? "Ghoti is observing your local screen." :
        (summary.state === "planning" ? "Ghoti is planning one supervised local action." :
          (summary.stoppedByCtrl8 || summary.stopped ? "Stopped by Ctrl+8 / STOP_AGENT." :
            "Computer Use is visible and remains supervised by local safety gates."))))));
  text("computer-use-session-id", summary.sessionId);
  text("computer-use-active-window", summary.activeWindow);
  text("computer-use-mouse", summary.mouse);
  text("computer-use-last-action", summary.lastAction);
  text("computer-use-evidence", summary.evidence);
  text("computer-use-active-control", summary.activeControl ? "YES" : "NO");
  text("computer-use-stopped-by-ctrl8", summary.stoppedByCtrl8 ? "YES" : "NO");
  const screenshot = document.getElementById("computer-use-screenshot");
  const screenshotEmpty = document.getElementById("computer-use-screenshot-empty");
  const hasSafeScreenshot = safeComputerUseScreenshotPath(summary.screenshot);
  if (screenshot) {
    screenshot.hidden = !hasSafeScreenshot;
    if (hasSafeScreenshot) screenshot.src = summary.screenshot;
    else screenshot.removeAttribute("src");
  }
  if (screenshotEmpty) {
    screenshotEmpty.hidden = hasSafeScreenshot;
    screenshotEmpty.textContent = summary.screenshotReason ? `Screenshot unavailable: ${summary.screenshotReason}` :
      (summary.screenshot ?
      "Screenshot evidence exists but is not exposed as a safe same-origin browser asset." :
      "No safe browser-renderable screenshot available.");
  }
  updateComputerUseBanner(summary);
  applyComputerUseAgentState(summary);
  if (summary.hasExplicitState && !orphanedPending) scheduleComputerUsePolling(summary.state);
  text("computer-use-backend-note", computerUseCommandAvailable() ?
    "Fixed computer-use session IDs are advertised by this backend." :
    "Computer-use session endpoint pending. Basic supervised Confirm/Cancel still available.");
}

function hideComputerUsePanel() {
  state.computerUsePanelManuallyHidden = true;
  const panel = document.getElementById("computer-use-panel");
  const shell = document.getElementById("agent-shell");
  if (panel) panel.hidden = true;
  if (shell) shell.classList.remove("computer-use-active");
}

function renderComputerUseFeatureDetection() {
  const sessionReady = computerUseCommandAvailable();
  text("tool-status-computer-use", sessionReady ? "SESSION READY" : "SUPERVISED");
  document.querySelectorAll("[data-computer-use-command]").forEach(button => {
    const command = button.dataset.computerUseCommand;
    button.disabled = !computerUseCommandAvailable(command);
    button.title = button.disabled ? `Backend unavailable: ${command}` : "";
  });
  const note = document.getElementById("computer-use-backend-note");
  if (note) note.textContent = sessionReady ?
    "Fixed computer-use session IDs are advertised by this backend." :
    "Computer-use session endpoint pending. Basic supervised Confirm/Cancel still available.";
}

async function pollComputerUseStatus() {
  if (state.computerUsePollBusy || !computerUseCommandAvailable("computer_use_status")) return null;
  state.computerUsePollBusy = true;
  try {
    const payload = await optionalStatusPayload("computer_use_status");
    updateComputerUsePanel(payload);
    return payload;
  } catch (error) {
    stopComputerUsePolling();
    text("computer-use-backend-note", `Backend unavailable: ${error.message}`);
    return null;
  } finally {
    state.computerUsePollBusy = false;
  }
}

async function readLatestComputerUseStatus() {
  if (!computerUseCommandAvailable("computer_use_status")) return null;
  try {
    return await optionalStatusPayload("computer_use_status");
  } catch (_error) {
    return null;
  }
}

function computerUseObservationReply(summary) {
  if (summary.screenshotReason) {
    return `Observation finished locally. Screenshot was skipped honestly: ${summary.screenshotReason}`;
  }
  return `Observation finished locally. Active window: ${summary.activeWindow}; mouse: ${summary.mouse}.`;
}

async function resetComputerUseStop(button = null) {
  if (!computerUseCommandAvailable("computer_use_reset_stop")) {
    updateComputerUsePanel({}, "computer use");
    text("computer-use-backend-note", "Backend unavailable: computer_use_reset_stop is not advertised.");
    return null;
  }
  if (button) button.disabled = true;
  try {
    const payload = await optionalStatusPayload("computer_use_reset_stop");
    const resetConfirmed = payload?.outcome === "OK" && payload?.stopped === false;
    if (!resetConfirmed) {
      text("computer-use-backend-note", "Reset was not confirmed by the backend; stopped mode remains visible.");
      return payload;
    }
    stopComputerUsePolling();
    updateComputerUsePanel({
      outcome: "OK",
      computer_use_session: state.computerUseSession?.sessionId,
      computer_use_state: "idle",
      active_control: false,
      stopped: false,
      stopped_by_ctrl8: false,
      last_action_result: payload.note || "Emergency stop reset",
      evidence_path: state.computerUseSession?.evidence,
    }, "computer use");
    appendChatMessage("ghoti", payload.note || "Emergency stop reset. Supervised actions can be confirmed again.");
    setAgentState("idle", "Emergency stop reset. Supervised actions require confirmation.", false);
    return payload;
  } catch (error) {
    text("computer-use-backend-note", `Reset blocked or unavailable: ${error.message}`);
    return null;
  } finally {
    if (button) button.disabled = !computerUseCommandAvailable("computer_use_reset_stop");
  }
}

async function runComputerUseControl(button) {
  const command = button?.dataset.computerUseCommand;
  if (!computerUseCommandAvailable(command)) {
    updateComputerUsePanel({}, "computer use");
    text("computer-use-backend-note", `Backend unavailable: ${command || "unknown fixed command"}.`);
    return null;
  }
  if (command === "computer_use_stop") return stopAgent();
  if (command === "computer_use_reset_stop") return resetComputerUseStop(button);
  if (command === "computer_use_demo_safe") {
    button.disabled = true;
    try {
      return await sendAgentMessage("computer use demo", "computer-use-control");
    } finally {
      button.disabled = !computerUseCommandAvailable(command);
    }
  }
  button.disabled = true;
  if (command === "computer_use_observe") {
    appendChatMessage("user", "observe screen", { badge: "COMPUTER USE" });
    setAgentState("observing", AGENT_STATE_COPY.observing, false);
    setAgentActivity("observing", "observe screen");
    updateComputerUsePanel({ computer_use_state: "observing" }, "observe screen");
  }
  try {
    const payload = await optionalStatusPayload(command);
    const summary = computerUseSummary(payload);
    updateComputerUsePanel(payload, command === "computer_use_observe" ? "observe screen" : "computer use");
    if (command === "computer_use_observe") {
      const reply = computerUseObservationReply(summary);
      const rendered = renderAgentResult({ ...payload, reply, computer_use_session: summary.sessionId,
        computer_use_state: summary.state });
      appendChatMessage("ghoti", reply, rendered.meta);
      hideAgentActivity();
      const statusPayload = await readLatestComputerUseStatus();
      const reconciled = statusPayload ? reconcileComputerUseStatus(payload, statusPayload) : payload;
      if (statusPayload) updateComputerUsePanel(reconciled, "observe screen");
      const finalSummary = computerUseSummary(reconciled);
      setAgentState(finalSummary.stoppedByCtrl8 || finalSummary.stopped ? "stopped" : "done");
    }
    return payload;
  } catch (error) {
    hideAgentActivity();
    text("computer-use-backend-note", `Backend unavailable: ${error.message}`);
    setAgentState("error", `Computer Use failed safely: ${error.message}`, false);
    return null;
  } finally {
    button.disabled = !computerUseCommandAvailable(command);
  }
}

function updateStarterVisibility() {
  const starters = document.querySelector(".assistant-examples");
  if (starters) starters.hidden = state.chatMessages.some(item => item.role === "user");
}

async function runAgentOverlay(command) {
  if (!CLIENT_COMMAND_IDS.has(command) || !state.availableCommands.has(command)) return null;
  try {
    return await api(`/api/run/${command}`, { method: "POST" });
  } catch (_error) {
    // A missing or SKIPPED desktop overlay must never block the web UI.
    return null;
  }
}

function assertInternalApiPath(path) {
  if (typeof path !== "string" || !/^\/api\/[a-z0-9_/-]+$/.test(path) ||
      path.includes("..") || path.includes("//")) {
    throw new Error("Only fixed same-origin API paths are allowed.");
  }
}

function waitForPairing() {
  showPairing();
  if (!state.pairingPromise) {
    state.pairingPromise = new Promise(resolve => { state.pairingResolve = resolve; });
  }
  return state.pairingPromise;
}

async function api(path, options = {}, retryOnUnauthorized = true) {
  assertInternalApiPath(path);
  const headers = new Headers(options.headers || {});
  if (state.pairingValue) headers.set(PAIRING_HEADER, state.pairingValue);
  const response = await fetch(path, { cache: "no-store", ...options, headers });
  const data = await response.json();
  if (response.status === 401 && retryOnUnauthorized) {
    state.pairingValue = "";
    if (state.mobile) {
      state.mobile = { ...state.mobile, paired: false };
      renderMobileConfig();
    }
    await waitForPairing();
    return api(path, options, false);
  }
  if (!response.ok) throw new Error(data.reason || `Request failed (${response.status})`);
  return data;
}

function text(id, value) {
  const node = document.getElementById(id);
  if (node) node.textContent = value == null ? "--" : String(value);
}

function safeString(value) {
  return value == null ? "--" : typeof value === "object" ? JSON.stringify(value) : String(value);
}

function row(label, value, tone = "") {
  const item = document.createElement("div");
  item.className = "row";
  const name = document.createElement("span");
  name.textContent = label;
  const data = document.createElement("strong");
  data.textContent = safeString(value);
  if (tone) data.className = tone;
  item.append(name, data);
  return item;
}

function renderRows(id, values) {
  const root = document.getElementById(id);
  if (!root) return;
  root.replaceChildren();
  Object.entries(values).forEach(([key, value]) => root.append(row(key, value,
    String(value).includes("BLOCKED") ? "bad" : String(value).includes("WARN") ? "caution" :
      String(value).includes("PASS") || value === true ? "good" : "")));
}

function renderDailyCards(cards) {
  const root = document.getElementById("daily-cards");
  if (!root) return;
  root.replaceChildren();
  cards.forEach(card => {
    const article = document.createElement("article");
    article.className = `status-card ${String(card.status).toLowerCase()}`;
    const badge = document.createElement("span");
    badge.className = "status-pill";
    badge.textContent = card.status;
    const heading = document.createElement("h3");
    heading.textContent = card.title;
    const value = document.createElement("strong");
    value.textContent = card.value;
    const detail = document.createElement("p");
    detail.textContent = card.detail;
    article.append(badge, heading, value, detail);
    root.append(article);
  });
}

function renderNextAction(nextAction) {
  const root = document.getElementById("next-action");
  root.replaceChildren();
  const badge = document.createElement("span");
  badge.className = "status-pill warn";
  badge.textContent = nextAction.stage || "CHECK";
  const primary = document.createElement("p");
  primary.className = "next-primary";
  primary.textContent = nextAction.primary || "Refresh status to calculate the next action.";
  root.append(badge, primary);
  (nextAction.commands || []).forEach(command => {
    const code = document.createElement("code");
    code.textContent = command;
    root.append(code);
  });
  const packageNote = document.createElement("p");
  packageNote.textContent = nextAction.manual_package_path ?
    `Manual export: ${nextAction.manual_package_path}` : nextAction.manual_package_note;
  const blocked = document.createElement("p");
  blocked.className = "blocked-reason";
  blocked.textContent = `Live post blocked: ${nextAction.live_post_reason || "No audited posting adapter exists."}`;
  const action = document.createElement("button");
  action.className = "button primary next-action-cta";
  action.type = "button";
  if (nextAction.stage === "NEEDS FOOTAGE") {
    action.textContent = "Open Clipper and add owned footage";
    action.addEventListener("click", () => openView("clipper"));
  } else if (nextAction.manual_package_path) {
    action.textContent = "Open manual package queue";
    action.addEventListener("click", () => openView("queue"));
  } else {
    action.textContent = "Check clipper readiness";
    action.addEventListener("click", () => openView("clipper"));
  }
  root.append(packageNote, action, blocked);
}

function renderModelRouting(id, items) {
  const root = document.getElementById(id);
  if (!root) return;
  root.replaceChildren();
  items.forEach(item => {
    const entry = document.createElement("div");
    entry.className = "routing-item";
    const label = document.createElement("strong");
    label.textContent = item.model;
    const lane = document.createElement("span");
    lane.textContent = item.lane;
    const cost = document.createElement("small");
    cost.textContent = item.cost;
    entry.append(label, lane, cost);
    root.append(entry);
  });
}

const SITE_DATA = [
  { name: "YouTube / Shorts", status: "MOCK_MANUAL", works: "Clip prep + manual upload package", blocked: "Live upload, OAuth, channel writes", needs: "Channel + YouTube Data API docs + 3 env creds", pkg: "manual + mock" },
  { name: "TikTok", status: "MOCK_MANUAL", works: "Clip prep + manual publish package", blocked: "Live publish, login, tokens", needs: "TikTok business account + Content Posting API docs + 3 env creds", pkg: "manual + mock" },
  { name: "Instagram / Meta", status: "MOCK_MANUAL", works: "Reel prep + mock ad package", blocked: "Publish, ad spend, campaigns, login", needs: "IG/FB business + Meta ad account + Marketing API docs + 4 env creds", pkg: "manual + mock" },
  { name: "Shopify", status: "MOCK_ONLY", works: "Product/catalog/order mock package", blocked: "Store writes, publish, orders", needs: "Shopify store + Admin API docs + 2 env creds", pkg: "mock" },
  { name: "Google Ads", status: "MOCK_ONLY", works: "Ad + budget plan (no spend) mock", blocked: "Ad spend, campaigns, login", needs: "Ads account + MCC + developer token + 5 env creds", pkg: "mock" },
  { name: "Pinterest Ads", status: "MOCK_ONLY", works: "Pin / ad plan mock", blocked: "Ad spend, publish, login", needs: "Business + ad account + API docs + 4 env creds", pkg: "mock" },
  { name: "Google Drive / Sheets", status: "MOCK_ONLY", works: "Local CSV/JSON export packages", blocked: "Drive/Sheets writes, login", needs: "Google account + Drive/Sheets API docs + 3 env creds", pkg: "mock + manual import" },
  { name: "Obsidian", status: "LOCAL_WORKS", works: "Local vault status writes", blocked: "Cloud sync, plugins, network", needs: "Nothing — local vault", pkg: "live (local)" },
  { name: "Ollama (local AI)", status: "LOCAL_WORKS", works: "Captions / hooks / titles (no credits)", blocked: "Cloud/paid model, network", needs: "Nothing — local models present", pkg: "live (local)" },
  { name: "Higgsfield (AI video)", status: "BLOCKED", works: "Nothing (interim = local ffmpeg)", blocked: "Activation, login, credits", needs: "Exact official CLI/API/MCP docs link", pkg: "blocked" },
];

const CONNECTOR_SETUP_DATA = [
  { name: "YouTube", target: "Channel + manual upload workflow", docs: "Official YouTube API and policy docs" },
  { name: "TikTok", target: "Business profile + manual publish workflow", docs: "Official Content Posting API and policy docs" },
  { name: "Instagram / Meta", target: "Business profile + ad account sandbox", docs: "Official Graph and Marketing API docs" },
  { name: "Shopify", target: "Development store or test profile", docs: "Official Admin API docs" },
  { name: "Google Ads", target: "Test account + manager scope", docs: "Official Google Ads API docs" },
  { name: "Pinterest", target: "Business profile + ad sandbox", docs: "Official Pinterest API docs" },
  { name: "Higgsfield", target: "Exact official product surface", docs: "Official CLI, API, or integration docs still required" },
  { name: "Drive / Sheets", target: "Test folder and spreadsheet only", docs: "Official Drive and Sheets API docs" },
];

const CONNECTOR_REQUIRED_INPUTS = [
  "account selected by the human",
  "official docs / API surface",
  "credentials outside the repo",
  "hard budget cap",
  "sandbox or test profile",
  "explicit allowed actions",
];

const ROUTINE_DATA = [
  { id: "daily_operator_check", time: "09:00 daily", title: "Operator check", what: "Read the whole local OS health and next action." },
  { id: "daily_clipping_sprint", time: "14:00 daily", title: "Clipping sprint", what: "Plan and render from owned footage; stop before upload." },
  { id: "daily_obsidian_memory_sync", time: "20:00 daily", title: "Obsidian memory sync", what: "Mirror today's memory and report any pending vault write." },
  { id: "weekly_github_status", time: "Mon 10:00", title: "GitHub status", what: "Review branch, tests, remote, and guarded sync readiness." },
  { id: "weekly_connector_review", time: "Wed 10:00", title: "Connector review", what: "Review setup gaps without logging in or storing credentials." },
  { id: "project_swarm_check", time: "Fri 16:00", title: "Project swarm check", what: "Review worker packets and stale supervised handoffs." },
];

const QUEST_DATA = [
  { time: "01", title: "Run status", what: "Refresh fixed local checks and read the next action.", view: "actions" },
  { time: "02", title: "Add footage", what: "Open the owned-media input folder before a clipping sprint.", view: "actions" },
  { time: "03", title: "Review clips", what: "Check local proof videos and manual packages.", view: "actions" },
  { time: "04", title: "Ask Ghoti", what: "Ask for local status, safety, or the next supervised step.", view: "chat" },
  { time: "05", title: "Review safety", what: "Confirm external control and live actions remain blocked.", view: "computer" },
];

const AGENT_ACTIONS = [
  { command: "agent_open_dashboard", appId: "ghoti_dashboard", title: "Open Dashboard", detail: "Local loopback browser" },
  { command: "agent_open_obsidian", appId: "obsidian_vault", title: "Open Obsidian", detail: "Ghoti local vault" },
  { command: "agent_open_vscode", appId: "vscode_repo", title: "Open VS Code", detail: "Current repo only" },
  { command: "agent_open_repo", appId: "file_explorer_repo", title: "Open Repo", detail: "Local File Explorer" },
  { command: "agent_open_clipper_input", appId: "ghoti_clipper_input_folder", title: "Add Footage", detail: "Owned-media input" },
  { command: "agent_open_clips", appId: "ghoti_proof_videos_folder", title: "Show Clips", detail: "Rendered local clips" },
  { command: "agent_run_status", actionId: "local_status", title: "Run Status", detail: "Read-only local check" },
  { command: "agent_run_local_demo", actionId: "orchestration_local_demo", title: "Run Local Demo", detail: "Bounded local workflow" },
  { command: "agent_stop", actionId: "stop", title: "Stop Agent", detail: "Cancel pending agent plans" },
];

const HOME_LAUNCHER_COMMANDS = [
  "agent_open_obsidian",
  "agent_open_vscode",
  "agent_open_repo",
  "agent_open_clipper_input",
];

const EVOLVE_PROPOSALS = [
  { id: "dashboard-clarity", area: "Dashboard", title: "Sharper daily priority signal", detail: "Rank the next safe local action from current status and evidence." },
  { id: "clipper-batch", area: "Clipper", title: "Batch-ready clip planning", detail: "Propose a bounded queue for owned footage without posting or scraping." },
  { id: "business-review", area: "Business", title: "Local business review packet", detail: "Summarize manual packages, mocks, and blockers without spend or store writes." },
  { id: "computer-use-proof", area: "Computer-use", title: "Stronger fixture evidence", detail: "Expand local fixture coverage while real OS input remains blocked." },
  { id: "connector-readiness", area: "Connectors", title: "Connector readiness checklist", detail: "Track official docs, required human inputs, and blocked live permissions." },
  { id: "routine-closeout", area: "Routines", title: "Reliable closeout packet", detail: "Propose a local end-of-day status and Obsidian handoff format." },
  { id: "obsidian-live-update", area: "Memory", title: "Live Obsidian status update command", detail: "Propose a fixed allowlisted command that writes a reviewed status note; do not write every chat message." },
];

const TOOL_DATA = [
  { name: "Clipper (ffmpeg)", status: "IMPLEMENTED" },
  { name: "Post manager (manual export)", status: "IMPLEMENTED" },
  { name: "Real computer-use (fixtures)", status: "IMPLEMENTED" },
  { name: "Rust guard", status: "IMPLEMENTED" },
  { name: "Local AI / Ollama", status: "IMPLEMENTED" },
  { name: "Operator dashboard (this app)", status: "IMPLEMENTED" },
  { name: "Business / site connectors", status: "MOCK_ONLY" },
  { name: "python-mss (screen observe)", status: "INSPECT_FIRST" },
  { name: "Playwright (local fixture)", status: "INSPECT_FIRST" },
  { name: "browser-use / stagehand / openhands / windows-use", status: "BLOCKED" },
  { name: "Higgsfield (AI video)", status: "NEEDS_EXACT_LINK" },
  { name: "Ruflo (claude-flow)", status: "BLOCKED" },
];

function statusTone(value) {
  const s = String(value).toUpperCase();
  if (/PASS|READY|IMPLEMENTED|LOCAL_WORKS|LIVE \(LOCAL\)/.test(s)) return "good";
  if (/BLOCK|NEEDS_EXACT_LINK/.test(s)) return "bad";
  return "caution";
}

function makeCard(fields, statusValue) {
  const article = document.createElement("article");
  article.className = `info-card ${statusTone(statusValue)}`;
  const pill = document.createElement("span");
  pill.className = "status-pill";
  pill.textContent = statusValue;
  const h3 = document.createElement("h3");
  h3.textContent = fields.title;
  article.append(pill, h3);
  (fields.rows || []).forEach(([label, value]) => {
    const p = document.createElement("p");
    const b = document.createElement("strong");
    b.textContent = `${label}: `;
    p.append(b, document.createTextNode(value));
    article.append(p);
  });
  return article;
}

function renderSites() {
  const root = document.getElementById("site-cards");
  if (!root) return;
  root.replaceChildren();
  SITE_DATA.forEach(s => {
    const card = makeCard({
      title: s.name,
      rows: [["Works now", s.works], ["Blocked", s.blocked], ["Needs from you", s.needs], ["Package", s.pkg]],
    }, s.status);
    const readiness = s.status === "LOCAL_WORKS" ? 100 :
      s.status === "MOCK_MANUAL" ? 45 : s.status === "MOCK_ONLY" ? 30 : 5;
    card.append(progressBar(readiness, "readiness"));
    root.append(card);
  });
}

function renderRoutines() {
  const root = document.getElementById("routine-cards");
  if (!root) return;
  root.replaceChildren();
  const reported = state.osRoutineStatus?.routines || {};
  ROUTINE_DATA.forEach(routine => {
    const backend = reported[routine.id] || {};
    const card = document.createElement("article");
    card.className = "routine-os-card";
    const time = document.createElement("span");
    time.className = "os-eyebrow";
    time.textContent = routine.time;
    const title = document.createElement("h3");
    title.textContent = routine.title;
    const detail = document.createElement("p");
    detail.textContent = routine.what;
    const status = document.createElement("small");
    status.className = "routine-last-run";
    status.textContent = backend.last_run ? `Last run: ${backend.last_run}` :
      `${backend.tier || "LOCAL_SAFE"} / not run this session`;
    const action = document.createElement("button");
    action.type = "button";
    action.className = "button tiny secondary";
    action.textContent = "Prepare in Ghoti";
    action.addEventListener("click", () => {
      openView("home");
      insertToolIntent(routine.title === "Clipping sprint" ?
        "make a clip from owned video" : routine.title.toLowerCase());
    });
    card.append(time, title, detail, status, action);
    root.append(card);
  });
}

function renderTools() {
  const root = document.getElementById("tool-cards");
  if (!root) return;
  root.replaceChildren();
  TOOL_DATA.forEach(t => root.append(makeCard({ title: t.name, rows: [] }, t.status)));
}

function osRoots(payload) {
  if (!payload || typeof payload !== "object") return [];
  return [payload, payload.data, payload.status, payload.result]
    .filter(value => value && typeof value === "object" && !Array.isArray(value));
}

function osValue(payload, keys, fallback = null) {
  for (const root of osRoots(payload)) {
    for (const key of keys) {
      if (root[key] !== undefined && root[key] !== null) return root[key];
    }
  }
  return fallback;
}

function osArray(payload, keys) {
  const value = osValue(payload, keys, []);
  if (Array.isArray(value)) return value;
  if (value && typeof value === "object") return Object.values(value);
  return [];
}

function osItemText(item, fallback = "Local record") {
  if (typeof item === "string") return item;
  if (!item || typeof item !== "object") return fallback;
  return item.title || item.name || item.summary || item.description || item.task ||
    item.action || item.path || item.id || item.project_id || item.mission_id || fallback;
}

function renderOsDetails(id, value, emptyText) {
  text(id, value && typeof value === "object" ? JSON.stringify(value, null, 2) : emptyText);
}

function renderOsItemList(id, items, emptyText, className = "os-list-item") {
  const root = document.getElementById(id);
  if (!root) return;
  root.replaceChildren();
  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = emptyText;
    root.append(empty);
    return;
  }
  items.forEach(value => {
    const item = value && typeof value === "object" ? value : { title: String(value) };
    const entry = document.createElement("article");
    entry.className = className;
    const heading = document.createElement("strong");
    heading.textContent = osItemText(item);
    const status = document.createElement("span");
    status.textContent = item.status || item.state || item.outcome || item.type || "LOCAL";
    const detail = document.createElement("small");
    detail.textContent = item.next_action || item.detail || item.note || item.path ||
      item.updated_at || item.generated_at || "Repo-local record";
    entry.append(heading, status, detail);
    root.append(entry);
  });
}

function renderSidebarProjects(projects) {
  const root = document.getElementById("os-sidebar-projects");
  if (!root) return;
  root.replaceChildren();
  if (!projects.length) {
    const empty = document.createElement("p");
    empty.textContent = state.availableCommands.has("ghoti_os_project_status") ?
      "No active projects reported." : "Project backend pending.";
    root.append(empty);
    return;
  }
  projects.slice(0, 3).forEach(project => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "sidebar-project-item";
    button.textContent = osItemText(project, "Local project");
    button.addEventListener("click", () => openView("projects"));
    root.append(button);
  });
}

function renderOsProjects() {
  const payload = state.osProjectStatus || state.osStatus;
  const projects = osArray(payload, ["projects", "project_list", "items"]);
  const mission = osValue(payload, ["latest_mission", "active_mission", "mission"], {});
  const tasks = osArray(payload, ["tasks", "active_tasks"]);
  const missionTasks = tasks.length ? tasks : (mission && typeof mission === "object" && Array.isArray(mission.tasks) ? mission.tasks : []);
  const evidence = osArray(payload, ["evidence", "artifacts", "evidence_paths"]);
  renderSidebarProjects(projects);
  renderOsItemList("os-project-list", projects, "No local projects reported.");
  renderOsItemList("os-project-tasks", missionTasks, "No project tasks reported.", "check-item");
  renderOsItemList("os-project-evidence", evidence, "No project evidence reported.", "artifact-item");
  text("os-project-count", `${projects.length} PROJECT${projects.length === 1 ? "" : "S"}`);
  renderRows("os-latest-mission", mission && typeof mission === "object" && Object.keys(mission).length ? {
    "Mission ID": mission.mission_id || mission.id || "not reported",
    Status: mission.status || mission.state || "LOCAL",
    "Next action": mission.next_action || mission.summary || "Review with Ghoti",
  } : { Status: "No mission reported" });
  const projectCommandReady = state.availableCommands.has("ghoti_os_project_status");
  const projectState = document.getElementById("os-projects-state");
  if (projectState) {
    projectState.textContent = projectCommandReady ? "LOCAL READY" : "BACKEND PENDING";
    projectState.className = `status-pill ${projectCommandReady ? "" : "warn"}`;
  }
  renderOsDetails("os-project-details", {
    project_status: state.osProjectStatus,
    swarm_status: state.osSwarmStatus,
  }, "Project and swarm status commands are not loaded yet.");
}

function renderOsSwarms() {
  const payload = state.osSwarmStatus || state.osProjectStatus || state.osStatus;
  const swarm = osValue(payload, ["latest_swarm", "active_swarm", "swarm"], {});
  const roles = osArray(payload, ["worker_roles", "roles", "workers"]);
  const liveExecution = osValue(payload, ["live_execution", "live_launch_enabled", "live_swarm_runtime"], false) === true;
  renderRows("os-swarm-status", {
    "Swarm ID": swarm?.swarm_id || swarm?.id || "not launched",
    Status: swarm?.status || (state.availableCommands.has("ghoti_os_swarm_status") ? "READY FOR PLAN" : "BACKEND PENDING"),
    "Worker roles": roles.length || 8,
    "Live swarm launch": liveExecution ? "REVIEW REQUIRED" : "BLOCKED",
    "Human approval": "REQUIRED",
  });
  const badge = document.getElementById("os-swarm-state");
  if (badge) {
    badge.textContent = liveExecution ? "REVIEW" : "SUPERVISED";
    badge.className = `status-pill ${liveExecution ? "bad" : "warn"}`;
  }
}

function memorySearchText(item) {
  if (typeof item === "string") return item;
  if (!item || typeof item !== "object") return "";
  return [item.title, item.name, item.summary, item.description, item.path, item.type,
    item.mission_id, item.project_id].filter(Boolean).join(" ");
}

function renderOsMemory() {
  const payload = state.osMemoryStatus || state.osStatus;
  const reportedMemories = osArray(payload, ["recent_memories", "memories", "items"]);
  const counts = osValue(payload, ["counts"], {});
  const allMemories = reportedMemories.length ? reportedMemories :
    Object.entries(counts && typeof counts === "object" ? counts : {}).map(([name, count]) => ({
      title: `${count} ${name.replaceAll("_", " ")}`,
      status: "INDEXED",
      detail: "Local SQLite and Markdown mirror count; contents stay repo-local.",
    }));
  const query = state.osMemoryQuery.trim().toLowerCase();
  const memories = query ? allMemories.filter(item => memorySearchText(item).toLowerCase().includes(query)) : allMemories;
  const events = osArray(payload, ["mission_events", "events", "recent_events"]);
  renderOsItemList("os-memory-results", memories, query ? "No local memory matched this search." : "No local memory records reported.");
  renderOsItemList("os-mission-events", events, "No mission events reported.", "timeline-item");
  text("os-memory-result-count", `${memories.length} ITEM${memories.length === 1 ? "" : "S"}`);
  const obsidian = state.obsidianStatus || {};
  renderRows("os-memory-obsidian", {
    Vault: obsidian.vault_found === true ? "DETECTED" : "NOT WRITABLE / PENDING",
    "Pending mirror": obsidian.mirror_dir || "obsidian_sync/pending/",
    "Live status note": obsidian.live_status_note || obsidian.notes?.live_status?.rel || "not reported",
    "Secrets stored": "NO",
  });
  const badge = document.getElementById("os-memory-state");
  if (badge) {
    const ready = state.availableCommands.has("ghoti_os_memory_status");
    badge.textContent = ready ? "LOCAL READY" : "LOCAL / BACKEND PENDING";
    badge.className = `status-pill ${ready ? "" : "warn"}`;
  }
  renderOsDetails("os-memory-details", state.osMemoryStatus, "Memory status command is not loaded yet.");
}

function renderOsContent() {
  const payload = state.osContentStatus || state.osStatus;
  const plan = osArray(payload, ["content_plans", "content_plan", "plan", "steps"]);
  renderOsItemList("os-content-plan", plan, "Ask Ghoti to make a clip plan from owned video.", "check-item");
  const packagePath = osValue(payload, ["manual_package_path", "latest_package", "package_path"], "clipper/output/latest_package.json");
  const liveApproved = osValue(state.osLiveApprovalStatus || payload, ["live_approved", "enabled"], false) === true;
  renderRows("os-content-package", {
    "Latest path": packagePath,
    "Auto-upload": liveApproved ? "SEPARATE APPROVAL REQUIRED" : "BLOCKED",
  });
  renderRows("os-content-schedule", {
    Mode: osValue(payload, ["schedule_mode", "mode"], "LOCAL PLAN"),
    Publishing: liveApproved ? "LIVE-GATED" : "MANUAL",
  });
  text("os-content-live-state", liveApproved ? "GATE PRESENT / NOT AUTO-RUN" : "NO");
  const connectors = state.osConnectorStatus?.connectors || {};
  text("os-youtube-state", connectors.youtube?.manual_package_mode === true ? "MANUAL PACKAGE / LIVE-GATED" : "BLOCKED");
  text("os-tiktok-state", connectors.tiktok?.manual_package_mode === true ? "MANUAL PACKAGE / LIVE-GATED" : "BLOCKED");
  const badge = document.getElementById("os-content-state");
  if (badge) badge.textContent = liveApproved ? "LIVE-GATED" : "MANUAL PUBLISH";
  renderOsDetails("clipper-output", state.osContentStatus, "No clipper or content status command run.");
}

function renderOsRoutines() {
  const payload = state.osRoutineStatus || state.osStatus;
  const scheduler = osArray(payload, ["task_scheduler_commands", "scheduler_commands", "copy_commands"]);
  const values = scheduler.length ? Object.fromEntries(scheduler.slice(0, 4).map((value, index) => [
    `Command ${index + 1}`, typeof value === "string" ? value : osItemText(value),
  ])) : { Commands: "Not advertised" };
  renderRows("os-routine-scheduler", values);
  renderRoutines();
  const badge = document.getElementById("os-routine-state");
  if (badge) badge.textContent = state.availableCommands.has("ghoti_os_routine_status") ? "LOCAL READY" : "RUN ONCE";
  renderOsDetails("os-routine-details", state.osRoutineStatus, "Routine status command is not loaded yet.");
}

function makeOsToolCard(item) {
  const card = document.createElement("article");
  card.className = "os-tool-card";
  const heading = document.createElement("div");
  heading.className = "os-panel-heading";
  const title = document.createElement("h3");
  title.textContent = item.name;
  const badge = document.createElement("span");
  badge.className = `tool-status ${item.tone || "needs-ivan"}`;
  badge.textContent = item.status;
  heading.append(title, badge);
  const works = document.createElement("p");
  works.textContent = item.works;
  const boundary = document.createElement("small");
  boundary.textContent = item.boundary;
  card.append(heading, works, boundary);
  return card;
}

function renderOsTools() {
  const agentReady = state.agentStatus?.outcome === "OK";
  const supervisedReady = state.agentSupervisedStatus?.outcome === "OK";
  const githubReady = state.githubStatus?.remote_configured === true;
  const obsidianReady = state.obsidianStatus?.vault_writable === true;
  const tools = [
    { name: "Desktop Computer Use", status: agentReady ? "READY" : "CHECK", tone: agentReady ? "ready" : "needs-ivan", works: "Allowlisted local apps, folders, and status actions.", boundary: "No raw shell text." },
    { name: "Supervised Click / Type", status: supervisedReady ? "READY" : "CHECK", tone: supervisedReady ? "ready" : "needs-ivan", works: "One bounded mouse or keyboard action after confirmation.", boundary: "Confirm once; evidence logged." },
    { name: "Browser Control", status: "LIVE-GATED", tone: "needs-ivan", works: "Local fixtures and supervised planning.", boundary: "External sites and accounts remain blocked." },
    { name: "Paperclip", status: "SANDBOX", tone: "sandbox", works: "Status and plan-only company coordination.", boundary: "No live company or agents launched." },
    { name: "Ruflo", status: "SANDBOX", tone: "sandbox", works: "Simulated swarm profiles and status.", boundary: "No live swarm launch." },
    { name: "GitHub", status: githubReady ? "READY" : "NEEDS_IVAN", tone: githubReady ? "ready" : "needs-ivan", works: "Local status and guarded branch sync.", boundary: "No remote creation or force push." },
    { name: "Obsidian", status: obsidianReady ? "READY" : "PENDING MIRROR", tone: obsidianReady ? "ready" : "needs-ivan", works: "Local memory status and pending notes.", boundary: "No fake vault write claim." },
    { name: "YouTube / TikTok", status: "LIVE-GATED", tone: "blocked", works: "Content plans and manual upload packages.", boundary: "No login, upload, or posting." },
  ];
  const root = document.getElementById("os-tool-cards");
  if (root) {
    root.replaceChildren();
    tools.forEach(item => root.append(makeOsToolCard(item)));
  }
  renderOsItemList("os-local-now", [
    "local chat and Ollama fallback", "allowlisted desktop control", "confirmed click/type/hotkey/move",
    "shared repo-local memory", "project and swarm task planning", "owned-media clipping and manual packages",
    "run-once routines",
  ], "No local capabilities reported.", "check-item");
  renderOsItemList("os-needs-live", [
    "live account login", "posting or uploading", "payments and ad spend",
    "official API credentials", "external site automation",
  ], "No live gates reported.", "check-item blocked-check");
  renderOsDetails("os-tools-details", {
    connector_status: state.osConnectorStatus,
    live_approval_status: state.osLiveApprovalStatus,
  }, "Connector and live-approval status commands are not loaded yet.");
}

function renderGhotiOs() {
  renderOsProjects();
  renderOsSwarms();
  renderOsMemory();
  renderOsContent();
  renderOsRoutines();
  renderOsTools();
  const model = state.agentStatus?.model?.selected || state.status?.local_ai?.model_selected || "local fallback";
  text("os-mode-model", String(model).toUpperCase());
  const liveApproved = osValue(state.osLiveApprovalStatus || state.osStatus, ["live_approved_any", "enabled"], false) === true;
  text("os-mode-live", liveApproved ? "LIVE APPROVAL GATE PRESENT" : "LIVE EXTERNAL BLOCKED");
}

function activateView(view, sourceTab = null) {
  view = VIEW_ALIASES[view] || view;
  const panel = document.querySelector(`.view[data-panel="${view}"]`);
  if (!panel) return false;
  const directTab = sourceTab || document.querySelector(`.tab[data-view="${view}"]`);
  const activeTab = directTab || null;
  document.querySelectorAll(".tab").forEach(item =>
    item.classList.toggle("active", item === activeTab));
  document.querySelectorAll(".view").forEach(item =>
    item.classList.toggle("active", item === panel));
  const advanced = document.getElementById("advanced-navigation");
  if (advanced && directTab?.classList.contains("advanced-tab")) advanced.open = true;
  text("page-title", view === "home" ? "Ghoti" :
    (directTab?.textContent || panel.querySelector("h2")?.textContent || "Advanced"));
  if (view === "evolve") loadBackendEvolve();
  if (view === "home") loadAgentCapabilities();
  if (view === "actions") loadDesktopOperatorCapabilities();
  if (["projects", "memory", "clipper", "routines", "tools"].includes(view)) loadGhotiOsStatus();
  if (view === "computer") {
    loadComputerCapabilities();
    loadAgentCapabilities();
  }
  if (["command", "paperclip", "ruflo"].includes(view)) loadOrchestrationCapabilities();
  if (view === "system-map") renderSystemMap();
  return true;
}

function openView(view) {
  activateView(view);
}

function openToolDestination(button) {
  insertToolIntent(button.dataset.toolIntent);
  if (["desktop", "computer-use", "browser"].includes(button.dataset.tool)) {
    updateComputerUsePanel({}, button.dataset.toolIntent || "computer use");
  }
}

function prepareAgentIntent(button) {
  openView("home");
  insertToolIntent(button.dataset.intent);
}

function renderDailyQuests() {
  const root = document.getElementById("daily-quests");
  if (!root) return;
  root.replaceChildren();
  QUEST_DATA.forEach((quest, index) => {
    const item = document.createElement("article");
    item.className = "quest-item";
    const order = document.createElement("span");
    order.className = "quest-order";
    order.textContent = String(index + 1).padStart(2, "0");
    const body = document.createElement("div");
    const time = document.createElement("strong");
    time.textContent = quest.time;
    const title = document.createElement("h3");
    title.textContent = quest.title;
    const detail = document.createElement("p");
    detail.textContent = quest.what;
    const action = document.createElement("button");
    action.className = "button tiny secondary";
    action.type = "button";
    action.textContent = "Open";
    action.addEventListener("click", () => openView(quest.view));
    body.append(time, title, detail, action);
    item.append(order, body);
    root.append(item);
  });
}

function renderObsidian() {
  const root = document.getElementById("obsidian-info");
  if (!root) return;
  const obsidian = state.obsidianStatus || {};
  const vault = obsidian.vault_path || obsidian.vault || "Not reported by backend";
  const liveNote = obsidian.live_status_note || obsidian.notes?.live_status?.rel || "Not reported";
  renderRows("obsidian-info", {
    "Vault (local)": vault,
    "Live status note": liveNote,
    "Last update time": obsidian.last_updated || obsidian.updated_at || "not reported",
    "Update behavior": firstAvailableCommand(["obsidian_update_status"]) ? "fixed reviewed command" : "not advertised by backend",
    "Live dashboard write command": firstAvailableCommand(["obsidian_update_status"]) || "not available",
    "Cloud sync": "disabled (local only)",
  });
  const code = document.getElementById("obsidian-path");
  if (code) code.textContent = vault;
  const copy = document.getElementById("obsidian-copy");
  if (copy) copy.dataset.copy = vault;
}

function progressBar(value, label) {
  const wrapper = document.createElement("div");
  wrapper.className = "progress-wrap";
  const caption = document.createElement("span");
  caption.textContent = `${label}: ${Math.max(0, Math.min(100, value))}%`;
  const track = document.createElement("div");
  track.className = "progress-track";
  const fill = document.createElement("span");
  fill.style.width = `${Math.max(0, Math.min(100, value))}%`;
  track.append(fill);
  wrapper.append(caption, track);
  return wrapper;
}

function renderSimsCards(status) {
  const root = document.getElementById("sims-cards");
  if (!root) return;
  const system = status.system || {}, clipper = status.clipper || {}, summary = status.operator_summary || {};
  const clips = clipper.rendered_clips?.length ?? 0;
  const owned = clipper.owned_footage_files?.length ?? 0;
  const cards = [
    { key: "EN", title: "Energy", status: system.guard_binary_built ? "PASS" : "WARN", value: `${summary.readiness_percent ?? 0}% ready`, progress: summary.readiness_percent ?? 0, next: "Run everything local to refresh.", command: "run_everything_local", action: "Refresh local core" },
    { key: "CO", title: "Content", status: clips ? "PASS" : clipper.ffmpeg_present ? "WARN" : "BLOCKER", value: `${clips} clips`, progress: clips ? 85 : clipper.ffmpeg_present ? 55 : 10, next: owned ? "Render a clip." : "Add owned footage to clipper/input/.", command: "clipper_status", action: "Check clipper" },
    { key: "MO", title: "Money", status: "WARN", value: "mock / manual", progress: 20, next: "Ads, sales, and store writes remain mock or manual." },
    { key: "SA", title: "Safety", status: "PASS", value: "live actions blocked", progress: 100, next: "Accounts, external control, and posting stay blocked.", command: "real_cu_blocked_action_test", action: "Prove blocks" },
    { key: "AU", title: "Autonomy", status: "WARN", value: "one local fixture", progress: 25, next: "Supervised fixture only; no external autonomy.", command: "real_cu_local_fixture", action: "Run fixture" },
  ];
  root.replaceChildren();
  cards.forEach(c => {
    const article = document.createElement("article");
    article.className = `sims-card ${String(c.status).toLowerCase()}`;
    const icon = document.createElement("span");
    icon.className = "sims-icon";
    icon.textContent = c.key;
    const pill = document.createElement("span");
    pill.className = "status-pill";
    pill.textContent = c.status;
    const h3 = document.createElement("h3");
    h3.textContent = c.title;
    const value = document.createElement("strong");
    value.textContent = c.value;
    const next = document.createElement("p");
    next.textContent = c.next;
    article.append(icon, pill, h3, value, progressBar(c.progress, "level"), next);
    if (c.command) {
      const action = document.createElement("button");
      action.className = "button tiny secondary";
      action.type = "button";
      action.dataset.command = c.command;
      action.dataset.output = "operator-command-output";
      action.textContent = c.action;
      action.addEventListener("click", () => runCommand(action));
      article.append(action);
    } else if (c.view) {
      const action = document.createElement("button");
      action.className = "button tiny secondary";
      action.type = "button";
      action.textContent = c.action;
      action.addEventListener("click", () => openView(c.view));
      article.append(action);
    }
    root.append(article);
  });
}

function renderDesktopOperator() {
  const status = state.desktopOperatorStatus || {};
  const appsById = new Map(state.desktopApps.map(item => [item.id, item]));
  const launcherRoot = document.getElementById("desktop-launcher-cards");
  if (launcherRoot) {
    launcherRoot.replaceChildren();
    HOME_LAUNCHER_COMMANDS.forEach(command => {
      const definition = AGENT_ACTIONS.find(item => item.command === command);
      if (!definition) return;
      const app = appsById.get(definition.appId) || {};
      const card = makeCard({
        title: definition.title,
        rows: [
          ["Target", app.label || definition.detail],
          ["Scope", app.description || "Fixed local launcher"],
        ],
      }, state.availableCommands.has(command) ? "READY" : "CHECK");
      const action = document.createElement("button");
      action.className = "button primary";
      action.type = "button";
      action.dataset.command = command;
      action.dataset.output = "operator-command-output";
      action.textContent = definition.title;
      action.disabled = !state.availableCommands.has(command);
      action.addEventListener("click", () => runCommand(action));
      card.append(action);
      launcherRoot.append(card);
    });
  }
  renderRows("desktop-operator-status", {
    "Mode": status.component || "ghoti_desktop_operator",
    "Apps / folders": status.apps_count ?? state.desktopApps.length,
    "Read-only actions": status.actions_count ?? state.desktopActions.length,
    "Dry-run supported": status.dry_run_supported ?? true,
    "Arbitrary command": status.arbitrary_command ?? false,
    "Network used": status.network_used ?? false,
    "Live execution": status.live_execution ?? false,
  });
  renderRows("desktop-operator-summary", {
    "Agent action cards": AGENT_ACTIONS.length,
    "Open commands": AGENT_ACTIONS.filter(item => item.appId).length,
    "Status / stop commands": AGENT_ACTIONS.filter(item => item.actionId).length,
    "Raw shell / arguments": "BLOCKED",
    "Accounts / posting / payment": "BLOCKED",
  });
}

async function loadDesktopOperatorCapabilities() {
  try {
    const [status, appsResult, actionsResult] = await Promise.all([
      optionalStatusPayload("desktop_operator_status"),
      optionalStatusPayload("desktop_operator_list_apps"),
      optionalStatusPayload("desktop_operator_list_actions"),
    ]);
    state.desktopOperatorStatus = status;
    state.desktopApps = appsResult?.apps || [];
    state.desktopActions = actionsResult?.actions || [];
    renderDesktopOperator();
  } catch (error) {
    text("desktop-output", `BLOCKED or failed safely: ${error.message}`);
    text("operator-command-output", `Desktop operator unavailable: ${error.message}`);
  }
}

function renderFullComputerUse(status) {
  const real = status.real_cu || {};
  const full = state.ghotiFullStatus || {};
  const agent = state.agentStatus || {};
  const input = agent.input_backend || {};
  const inputReady = Object.values(input).some(value => value === true || value === "AVAILABLE");
  const root = document.getElementById("full-cu-cards");
  if (!root) return;
  root.replaceChildren();
  const cards = [
    { title: "LOCAL_AGENT_SAFE", status: agent.outcome === "OK" ? "READY" : "CHECK", value: "Local talk + allowlisted actions", detail: "Open or focus local apps and folders, run local status/demo, use the local model, take screenshots, and show the glow overlay." },
    { title: "LOCAL_DESKTOP_SUPERVISED", status: inputReady ? "READY" : "CHECK", value: inputReady ? "One-shot input backend available" : "Confirmation gates ready; input backend missing", detail: "Click, type, hotkey, and mouse move require a separate confirmation, are capped, evidence-logged, and stopped by the emergency gate." },
    { title: "LOCAL FIXTURE", status: (full.local_fixture || real.mode) ? "READY" : "CHECK", value: full.local_fixture || real.mode || "not reported", detail: "Rust-gated local fixture remains available for proof." },
    { title: "LIVE_SITE_APPROVED", status: "NOT CONFIGURED", value: "External targets unavailable", detail: "No external site, account, login, upload, purchase, payment, or posting approval exists." },
  ];
  cards.forEach(card => root.append(makeCard({
    title: card.title,
    rows: [["State", card.value], ["Meaning", card.detail]],
  }, card.status)));
  renderRows("full-cu-works-now", {
    "Talk with Ghoti": "READY",
    "Voice and read-aloud": "READY WHEN BROWSER SUPPORTS IT",
    "Glow overlay": "READY",
    "Open apps / folders": "READY / FIXED ALLOWLIST",
    "Run local status / demo": "READY",
    "Update Obsidian": firstAvailableCommand(["obsidian_update_status"]) ? "READY / FIXED COMMAND" : "NEEDS BACKEND COMMAND",
    "GitHub status / sync": firstAvailableCommand(["github_sync_status", "github_local_summary"]) ? "READY / FIXED COMMANDS" : "NEEDS BACKEND COMMAND",
    "Paperclip / Ruflo status": firstAvailableCommand(["paperclip_agent_status", "paperclip_status"]) && firstAvailableCommand(["ruflo_agent_status", "ruflo_status"]) ? "SANDBOX STATUS READY" : "CHECK",
    "Click / type / hotkey / move": inputReady ? "READY / CONFIRM EACH ACTION" : "CHECK",
  });
  renderRows("full-cu-not-configured", {
    "Live websites / accounts": "NOT CONFIGURED",
    "Posting / uploading": "BLOCKED",
    "Login / password entry": "BLOCKED",
    "Payments / ad spend": "BLOCKED",
  });
  renderRows("real-cu-status", {
    "Local safe agent": agent.outcome === "OK" ? "READY" : "CHECK",
    "Supervised local input": inputReady ? "READY / CONFIRM EACH ACTION" : "CHECK",
    "Screenshot / observation": agent.screen?.available === false ? "CHECK" : "READY",
    "Live external site": "NOT CONFIGURED",
    "Accounts / login / upload / payment / posting": "BLOCKED",
    "Emergency sentinel": state.agentSupervisedStatus?.emergency_stop_file || "desktop_agent/STOP_AGENT",
  });
  renderRows("full-cu-inputs", {
    "Account": "human-selected test account later",
    "Docs / API": "official source required",
    "Credentials": "outside repo only; none entered here",
    "Budget cap": "hard human-set limit required",
    "Sandbox / test profile": "required before live integration",
    "Allowed actions": "explicit allowlist required",
  });
  renderRows("full-cu-evidence", {
    "Adapter evidence": "real_computer_use/evidence/",
    "Fixed command log": "app_backend/logs/runner_log.jsonl",
    "Guard log": "logs/guard_log.jsonl",
    "Agent plans": "desktop_agent/logs/plans.json",
    "Agent evidence": "desktop_agent/evidence/",
    "Live approved": full.live_approved ?? false,
    "Why LIVE_APPROVED = 0": "No audited external connector has explicit human approval, bounded credentials, budget cap, and test profile.",
    "Simulation": full.simulation ?? true,
    "Live execution": full.live_execution ?? false,
  });
}

function renderConnectorSetup() {
  const root = document.getElementById("connector-setup-cards");
  if (!root) return;
  root.replaceChildren();
  CONNECTOR_SETUP_DATA.forEach(connector => {
    const card = makeCard({
      title: connector.name,
      rows: [
        ["Target", connector.target],
        ["Docs", connector.docs],
        ["Required", CONNECTOR_REQUIRED_INPUTS.join("; ")],
        ["Current action", "requirements review only"],
      ],
    }, "BLOCKED");
    root.append(card);
  });
}

function systemMapItem(id) {
  return systemModules().find(item => item.id === id) || null;
}

function systemModules() {
  const details = new Map((state.systemMap?.subsystems || []).map(item => [item.id, item]));
  const pages = state.dashboardModules?.pages || {};
  const mapped = [];
  Object.entries(pages).forEach(([dashboardPage, entries]) => {
    (entries || []).forEach(entry => {
      const detail = details.get(entry.id) || {};
      mapped.push({
        ...detail,
        ...entry,
        dashboard_page: dashboardPage,
        requires_ivan: detail.requires_ivan || "not reported",
        next_command: entry.next_command || detail.next_command || "n/a",
      });
    });
  });
  return mapped.length ? mapped : (state.systemMap?.subsystems || []);
}

function profileCounts() {
  if (state.profileStatus?.counts) return state.profileStatus.counts;
  const counts = {
    LOCAL_READY: 0, SANDBOX_READY: 0, LIVE_APPROVED: 0, NEEDS_IVAN: 0, BLOCKED: 0,
  };
  systemModules().forEach(item => {
    if (Object.hasOwn(counts, item.activation_profile)) counts[item.activation_profile] += 1;
  });
  return counts;
}

function renderActivationProfiles() {
  const root = document.getElementById("activation-profile-cards");
  if (!root) return;
  const profiles = state.systemMap?.activation_profiles || {};
  const counts = profileCounts();
  const details = [
    {
      profile: "LOCAL_READY",
      meaning: profiles.LOCAL_READY || "Fixed local commands and status reads.",
      runnable: "Yes, within existing local allowlists.",
    },
    {
      profile: "SANDBOX_READY",
      meaning: profiles.SANDBOX_READY || "Simulation and local fixtures only.",
      runnable: "Yes, but never as a live external action.",
    },
    {
      profile: "NEEDS_IVAN",
      meaning: profiles.NEEDS_IVAN || "Requires a human choice or bounded input.",
      runnable: "No, until Ivan supplies the listed input or approval.",
    },
    {
      profile: "BLOCKED",
      meaning: profiles.BLOCKED || "Unavailable by policy or missing an audited integration.",
      runnable: "No. The blocked card stays visible.",
    },
    {
      profile: "LIVE_APPROVED",
      meaning: profiles.LIVE_APPROVED || "Future audited live connectors only.",
      runnable: counts.LIVE_APPROVED ? "Only with explicit human approval." : "No live subsystem is approved.",
    },
  ];
  root.replaceChildren();
  details.forEach(item => root.append(makeCard({
    title: item.profile,
    rows: [
      ["Systems", String(counts[item.profile] || 0)],
      ["Scope", item.meaning],
      ["Runnable now", item.runnable],
    ],
  }, item.profile === "LIVE_APPROVED" ? "BLOCKED" : item.profile)));
}

function renderOrchestrationModules() {
  const root = document.getElementById("orchestration-modules");
  if (!root) return;
  const modules = state.moduleScan?.modules || [];
  root.replaceChildren();
  modules.forEach(item => root.append(makeCard({
    title: item.module.replaceAll("_", " "),
    rows: [
      ["State", item.state || "not reported"],
      ["Repository detected", item.repo_detected ?? "n/a"],
      ["Runtime enabled", item.runtime_enabled ?? false],
      ["Live execution", item.live_execution ?? false],
      ["Summary", item.summary || "--"],
    ],
  }, item.activation_profile || "WARN")));
  if (!modules.length) {
    const empty = document.createElement("p");
    empty.className = "operator-note";
    empty.textContent = "Module scan not loaded. Open Command Center or press Scan modules.";
    root.append(empty);
  }
}

function renderOrchestrationStatus() {
  const payload = state.orchestrationStatus || {};
  const counts = state.profileStatus?.counts || payload.profile_counts || profileCounts();
  renderRows("orchestration-status", {
    "Mode": payload.state || "LOCAL_READY",
    "Simulation": payload.simulation ?? true,
    "Live execution": payload.live_execution ?? false,
    "Processes started": payload.process_started ?? false,
    "Network used": payload.network_used ?? false,
    "LOCAL_READY systems": counts.LOCAL_READY ?? 0,
    "SANDBOX_READY systems": counts.SANDBOX_READY ?? 0,
    "NEEDS_IVAN systems": counts.NEEDS_IVAN ?? 0,
    "BLOCKED systems": counts.BLOCKED ?? 0,
    "LIVE_APPROVED systems": counts.LIVE_APPROVED ?? 0,
  });
  const runnable = payload.runnable_now || [
    "fixed dashboard status commands",
    "local content and clipping pipeline",
    "Rust-gated local computer-use fixture",
    "Paperclip and Ruflo plan previews",
  ];
  const needs = payload.needs_ivan || [
    "choose one target connector",
    "choose a sandbox/test profile",
    "define explicit allowed actions",
    "set a hard budget cap before any future spend",
  ];
  renderRows("command-center-runnable",
    Object.fromEntries(runnable.map((item, index) => [`${index + 1}`, item])));
  renderRows("command-center-needs",
    Object.fromEntries(needs.map((item, index) => [`${index + 1}`, item])));
  renderActivationProfiles();
  renderOrchestrationModules();
}

function renderPaperclipStatus() {
  const payload = state.paperclipStatus || {};
  const mapped = systemMapItem("paperclip") || {};
  const scanned = (state.moduleScan?.modules || [])
    .find(item => item.module === "paperclip") || {};
  renderRows("paperclip-status", {
    "Activation profile": payload.activation_profile || mapped.activation_profile || "SANDBOX_READY",
    "Detected state": payload.state || mapped.status || "SANDBOX_READY",
    "Repository detected": payload.repo_detected ?? scanned.repo_detected ?? "not scanned",
    "Installed": payload.installed ?? false,
    "Runtime enabled": payload.runtime_enabled ?? false,
    "Live execution": payload.live_execution ?? false,
    "Works now": payload.works_now || mapped.what_works || "Status and plan preview only",
    "Integration role": payload.integration_role || "Future supervised task coordination",
    "Next action": payload.next_step || mapped.next_action || "Static intake before any install",
  });
}

function renderRufloStatus() {
  const payload = state.rufloStatus || {};
  const mapped = systemMapItem("ruflo") || {};
  const scanned = (state.moduleScan?.modules || [])
    .find(item => item.module === "ruflo") || {};
  renderRows("ruflo-status", {
    "Activation profile": payload.activation_profile || mapped.activation_profile || "SANDBOX_READY",
    "Detected state": payload.state || mapped.status || "SANDBOX_READY",
    "Repository detected": payload.repo_detected ?? scanned.repo_detected ?? "not scanned",
    "Installed": payload.installed ?? false,
    "Runtime enabled": payload.runtime_enabled ?? false,
    "Live execution": payload.live_execution ?? false,
    "Works now": payload.works_now || mapped.what_works || "Swarm profile simulation only",
    "Integration role": payload.integration_role || "Future supervised swarm coordination",
    "Next action": payload.next_step || mapped.next_action || "Static intake before any install",
  });
  const profiles = payload.swarm_profiles || [
    "solo-planner", "two-agent-review", "content-planning-team",
  ];
  renderRows("ruflo-profiles",
    Object.fromEntries(profiles.map((item, index) => [`Profile ${index + 1}`, `${item} (simulation only)`])));
}

function renderSystemMap(filter = state.systemMapFilter) {
  const root = document.getElementById("system-map-cards");
  if (!root) return;
  const all = systemModules();
  const items = filter === "ALL" ? all :
    all.filter(item => item.activation_profile === filter);
  state.systemMapFilter = filter;
  root.replaceChildren();
  const grouped = new Map();
  items.forEach(item => {
    const page = item.dashboard_page || "Unassigned";
    if (!grouped.has(page)) grouped.set(page, []);
    grouped.get(page).push(item);
  });
  grouped.forEach((entries, page) => {
    const group = document.createElement("section");
    group.className = "system-map-group";
    const heading = document.createElement("h3");
    heading.textContent = page;
    const grid = document.createElement("div");
    grid.className = "card-grid system-map-grid";
    entries.forEach(item => grid.append(makeCard({
      title: item.name,
      rows: [
        ["Status", item.status || "--"],
        ["Command ID", item.command_id || "n/a"],
        ["Dashboard page", item.dashboard_page || page],
        ["What works", item.what_works || item.summary || "--"],
        ["Requires Ivan", item.requires_ivan || "none"],
        ["Next command", item.next_command || "n/a"],
      ],
    }, item.activation_profile)));
    group.append(heading, grid);
    root.append(group);
  });
  if (!items.length) {
    const empty = document.createElement("div");
    empty.className = "operator-note";
    empty.textContent = filter === "LIVE_APPROVED" ?
      "No subsystem is LIVE_APPROVED. Live actions remain blocked." :
      "No subsystem matches this filter.";
    root.append(empty);
  }
  text("system-map-count", `${items.length} / ${all.length} SYSTEMS`);
  const counts = profileCounts();
  renderRows("system-map-summary", {
    "System source": state.systemMap?.source || "integration_registry/GHOTI_SYSTEM_MAP.json",
    "Page grouping": state.dashboardModules?.source || "integration_registry/DASHBOARD_MODULES.json",
    "LOCAL_READY": counts.LOCAL_READY,
    "SANDBOX_READY": counts.SANDBOX_READY,
    "LIVE_APPROVED": counts.LIVE_APPROVED,
    "NEEDS_IVAN": counts.NEEDS_IVAN,
    "BLOCKED": counts.BLOCKED,
  });
  document.querySelectorAll(".system-filter").forEach(button => {
    const active = button.dataset.filter === filter;
    button.classList.toggle("primary", active);
    button.classList.toggle("secondary", !active);
  });
}

function resultCardTone(status) {
  const value = String(status || "").toUpperCase();
  if (/BLOCKED|DENIED|REFUSED|FAILED|REQUIRED/.test(value)) return "blocked";
  if (/READY|OK|DONE|EXECUTED|UPDATED|SYNCED|AVAILABLE/.test(value)) return "ready";
  return "review";
}

function appendResultCards(root, cards = []) {
  if (!root || !Array.isArray(cards) || !cards.length) return;
  const grid = document.createElement("div");
  grid.className = "chat-result-cards";
  cards.forEach(card => {
    const article = document.createElement("article");
    article.className = `chat-result-card ${resultCardTone(card.status)}`;
    article.dataset.resultKind = card.kind || "status";
    const header = document.createElement("header");
    const title = document.createElement("strong");
    title.textContent = card.title || "Result";
    const status = document.createElement("span");
    status.textContent = card.status || "REVIEW";
    header.append(title, status);
    article.append(header);
    if (Array.isArray(card.facts) && card.facts.length) {
      const facts = document.createElement("dl");
      card.facts.forEach(fact => {
        if (!fact || fact.value == null || fact.value === "") return;
        const row = document.createElement("div");
        const label = document.createElement("dt");
        const value = document.createElement("dd");
        label.textContent = fact.label || "Status";
        value.textContent = String(fact.value);
        row.append(label, value);
        facts.append(row);
      });
      if (facts.childElementCount) article.append(facts);
    }
    if (card.note) {
      const note = document.createElement("p");
      note.textContent = String(card.note);
      article.append(note);
    }
    grid.append(article);
  });
  if (grid.childElementCount) root.append(grid);
}

function appendChatMessage(role, message, meta = {}) {
  state.chatMessages.push({ role, message, meta });
  updateStarterVisibility();
  if (role === "ghoti") state.latestGhotiMessage = message;
  const root = document.getElementById("agent-conversation");
  if (!root) return;
  const item = document.createElement("article");
  item.className = `conversation-message ${role === "ghoti" ? "assistant-message" : "user-message"}`;
  const avatar = document.createElement(role === "ghoti" ? "img" : "span");
  avatar.className = "message-avatar";
  if (role === "ghoti") {
    avatar.src = GHOTI_FISH_URL;
    avatar.alt = "Ghoti";
  } else {
    avatar.textContent = "YOU";
    avatar.setAttribute("aria-hidden", "true");
  }
  const column = document.createElement("div");
  column.className = "message-column";
  const content = document.createElement("div");
  content.className = "message-body";
  const heading = document.createElement("div");
  heading.className = "message-heading";
  const label = document.createElement("strong");
  label.textContent = role === "ghoti" ? "Ghoti" : "You";
  heading.append(label);
  if (meta.badge) {
    const badge = document.createElement("span");
    badge.className = "message-badge";
    badge.textContent = String(meta.badge);
    heading.append(badge);
  }
  const textNode = document.createElement("p");
  textNode.textContent = message;
  content.append(heading, textNode);
  const metaItems = [
    meta.action,
    meta.model,
    meta.projectId ? `project ${meta.projectId}` : null,
    meta.missionId ? `mission ${meta.missionId}` : null,
    meta.swarmId ? `swarm ${meta.swarmId}` : null,
    meta.nextAction ? `next: ${meta.nextAction}` : null,
    meta.liveApproval ? `live: ${meta.liveApproval}` : null,
    meta.evidence,
  ].filter(Boolean);
  if (metaItems.length) {
    const details = document.createElement("div");
    details.className = "message-meta";
    metaItems.forEach(value => {
      const chip = document.createElement("span");
      chip.textContent = String(value);
      details.append(chip);
    });
    content.append(details);
  }
  column.append(content);
  appendResultCards(column, meta.cards);
  item.append(avatar, column);
  root.append(item);
  root.scrollTop = root.scrollHeight;
}

function localSafetyReply() {
  return "Safety boundary: confirmed one-shot local input is available; unconfirmed input, live posting, external websites, accounts, uploads, payments, scraping, Telegram, MCP, live Ruflo, Higgsfield, and cloud APIs remain blocked.";
}

function selectedLocalModel(payload = {}) {
  return payload.model_used || payload.model || state.status?.local_ai?.model_selected || "fallback";
}

function renderModelProviderStatus() {
  const providerSelect = document.getElementById("agent-model-provider");
  const modelSelect = document.getElementById("agent-model-choice");
  if (!providerSelect || !modelSelect) return;
  state.selectedModelProvider = providerSelect.value;
  state.selectedModel = modelSelect.value;
  const providers = state.agentStatus?.providers || {};
  const provider = providers[state.selectedModelProvider] || {};
  let label = "Fallback ready";
  let status = "ready";
  if (state.selectedModelProvider === "ollama") {
    const models = Array.isArray(provider.models) ? provider.models : (state.agentStatus?.model?.models || []);
    const connected = provider.available === true || state.agentStatus?.model?.ollama_present === true;
    const selectedPresent = models.includes(state.selectedModel);
    label = connected && selectedPresent ? `Ollama connected - ${state.selectedModel}` :
      (connected ? `${state.selectedModel} unavailable - fallback ready` : "Ollama unavailable - fallback ready");
    status = connected && selectedPresent ? "ready" : "warn";
    modelSelect.disabled = false;
  } else if (state.selectedModelProvider === "openai-compatible") {
    label = provider.configured === true ? "OpenAI-compatible configured; runtime remains disabled" :
      "OpenAI-compatible provider not configured";
    status = "warn";
    modelSelect.disabled = true;
  } else {
    label = "Deterministic fallback ready";
    status = "ready";
    modelSelect.disabled = true;
  }
  const chip = document.getElementById("agent-provider-status");
  if (chip) {
    chip.textContent = label;
    chip.dataset.status = status;
  }
}

function formatAgentItem(item) {
  if (item == null) return "not reported";
  if (typeof item === "string") return item;
  if (typeof item !== "object") return String(item);
  const action = item.step || item.type || item.action || item.action_id || item.kind || item.intent || "action";
  const target = item.target || item.app || item.path || item.operator_id || "";
  const outcome = item.outcome || item.status || "";
  return [action, target, outcome].filter(Boolean).join(" - ");
}

function renderAgentItems(id, items, emptyText) {
  const root = document.getElementById(id);
  if (!root) return;
  root.replaceChildren();
  const values = Array.isArray(items) ? items : [];
  if (!values.length) {
    const item = document.createElement("li");
    item.textContent = emptyText;
    root.append(item);
    return;
  }
  values.forEach(value => {
    const item = document.createElement("li");
    item.textContent = formatAgentItem(value);
    root.append(item);
  });
}

function confirmationTarget(step = {}, plan = {}) {
  const params = step.params && typeof step.params === "object" ? step.params : {};
  const type = step.type || step.step || plan.action_type || "local action";
  if (type === "click" || type === "move_mouse") {
    return `x=${params.x ?? "?"}, y=${params.y ?? "?"}`;
  }
  if (type === "type_text") {
    const value = String(params.text || "").replace(/\s+/g, " ").trim();
    const preview = value.length > 80 ? `${value.slice(0, 77)}...` : value;
    return preview ? `text: "${preview}"` : "text input";
  }
  if (type === "hotkey") {
    return Array.isArray(params.keys) ? params.keys.join(" + ") : "local hotkey";
  }
  return step.target || params.target || plan.target || "local desktop";
}

function setConfirmationButtonsDisabled(disabled) {
  for (const id of ["agent-confirm", "agent-cancel"]) {
    const button = document.getElementById(id);
    if (button) button.disabled = disabled;
  }
}

function renderConfirmation(plan = {}, visible = false, currentWindow = "not reported") {
  const steps = Array.isArray(plan.steps) ? plan.steps : [];
  const firstStep = steps[0] || {};
  const planId = plan.plan_id || "not reported";
  const action = firstStep.type || firstStep.step || plan.action_type || "not reported";
  const target = confirmationTarget(firstStep, plan);
  for (const [id, value] of [
    ["agent-confirm-plan-id", planId],
    ["agent-confirm-action", action],
    ["agent-confirm-target", target],
    ["agent-confirm-window", currentWindow || "not reported"],
  ]) {
    text(id, value);
  }
  text("agent-confirm-safety", visible ?
    "One action only. Explicit approval, bounds checks, blocked target terms, and evidence logging remain active." :
    "One action, explicit approval, evidence logged.");
  for (const id of ["agent-confirmation"]) {
    const confirmation = document.getElementById(id);
    if (confirmation) {
      confirmation.hidden = !visible;
      if (visible) {
        const conversation = document.getElementById("agent-conversation");
        if (conversation) {
          conversation.append(confirmation);
          conversation.scrollTop = conversation.scrollHeight;
        }
      }
    }
  }
  setConfirmationButtonsDisabled(!visible);
  if (visible) updateComputerUsePanel({ needs_confirmation: true, plan, current_window: currentWindow });
}

function renderAgentSafetyFlags(flags = {}) {
  const values = flags && typeof flags === "object" ? flags : {};
  const display = {};
  Object.entries(values).forEach(([key, value]) => {
    display[key.replaceAll("_", " ")] = value === false ? "BLOCKED / FALSE" : value;
  });
  if (!Object.keys(display).length) display.Status = "No safety flags reported.";
  renderRows("agent-safety-flags", display);
}

function agentActionLabel(plan = {}, payload = {}) {
  const steps = Array.isArray(plan.steps) ? plan.steps : [];
  const first = steps[0] || {};
  return first.type || first.step || plan.action_type || payload.action || "conversation";
}

function agentResultCards(payload = {}, context = {}) {
  const detail = payload.detail && typeof payload.detail === "object" ? payload.detail : {};
  const intent = `${payload.intent || ""} ${payload.subsystem || ""} ${payload.action || ""}`.toLowerCase();
  const computerUse = computerUseSummary(payload);
  const cards = [];
  const add = (kind, title, status, facts = [], note = "") => {
    cards.push({ kind, title, status, facts, note });
  };
  if (context.projectId) {
    add("project", "Project", detail.status || payload.outcome || "READY", [
      { label: "ID", value: context.projectId },
      { label: "Goal", value: detail.goal || payload.project?.goal },
      { label: "Next", value: context.nextAction },
    ], "Project state is local and evidence-backed.");
  }
  if (context.missionId) {
    add("mission", "Mission", detail.status || payload.outcome || "READY", [
      { label: "ID", value: context.missionId },
      { label: "Task", value: detail.task || detail.goal || payload.mission?.task },
      { label: "Next", value: context.nextAction },
    ]);
  }
  if (context.swarmId) {
    const workerCount = detail.worker_count ?? (Array.isArray(detail.workers) ? detail.workers.length : null);
    add("swarm", "Swarm plan", payload.outcome || "READY", [
      { label: "ID", value: context.swarmId },
      { label: "Profile", value: detail.profile || payload.swarm?.profile || "MANUAL" },
      { label: "Workers", value: workerCount },
      { label: "Live agents", value: detail.live_agents_started === true ? "REVIEW" : "NO" },
    ], "Task orchestration only; no uncontrolled agents are launched.");
  }
  if (/content|clip|video/.test(intent)) {
    const connectors = detail.connectors && typeof detail.connectors === "object" ? detail.connectors : {};
    add("content", "Content workflow", payload.outcome || "REVIEW", [
      { label: "Plan", value: detail.plan_id || detail.content_plan_id || context.missionId },
      { label: "Source", value: detail.source || detail.source_url || detail.source_expected_at },
      { label: "Rights", value: detail.rights || detail.rights_status || "REQUIRED" },
      { label: "Clip plan", value: detail.clip_plan || (detail.plan_id ? "READY" : "NOT CREATED") },
      { label: "Package", value: detail.manual_package_path || detail.package_path || detail.export_path },
      { label: "TikTok", value: connectors.tiktok || detail.tiktok_connector || "BLOCKED / NOT CONFIGURED" },
      { label: "YouTube", value: connectors.youtube || detail.youtube_connector || "BLOCKED / NOT CONFIGURED" },
      { label: "Next", value: context.nextAction },
    ], detail.rights_status === "MISSING" ?
      "Declare owned, permitted, or self-recorded rights before Ghoti creates a plan. No media was downloaded." :
      "Owned or permitted media only. Uploading requires a LIVE_APPROVED connector; manual packaging remains available.");
  }
  if (/routine/.test(intent)) {
    add("routine", "Routine", payload.outcome || "READY", [
      { label: "Name", value: detail.name || detail.routine_id || payload.action },
      { label: "Schedule", value: detail.schedule || detail.cadence },
      { label: "Next", value: context.nextAction },
    ], "Run-once or local schedule plan; no account action is implied.");
  }
  for (const tool of ["paperclip", "ruflo"]) {
    if (intent.includes(tool)) {
      const runtime = detail.runtime_enabled === true || detail.live_execution === true;
      add("tool", tool === "paperclip" ? "Paperclip" : "Ruflo", detail.state || detail.activation_profile || "SANDBOX", [
        { label: "Profile", value: detail.activation_profile || "SANDBOX" },
        { label: "Runtime", value: runtime ? "REVIEW" : "NOT STARTED" },
        { label: "Next", value: detail.next_step || context.nextAction },
      ], runtime ? "Runtime activity was reported; review before continuing." : "Status and sandbox planning only.");
    }
  }
  if (computerUse.relevant) {
    add("computer-use", "Computer Use", computerUse.state, [
      { label: "Active window", value: computerUse.activeWindow },
      { label: "Mouse", value: computerUse.mouse },
      { label: "Last action", value: computerUse.lastAction },
      { label: "Evidence", value: computerUse.evidence },
    ], payload.needs_confirmation ?
      "Waiting for Confirm once. Press Ctrl+8 anytime to stop Ghoti." :
      "Supervised local computer use only; external sites and account actions remain blocked.");
  }
  if (intent.includes("obsidian") || payload.obsidian_updated === true) {
    const mirrorPath = detail.mirror_dir || detail.pending_path || "obsidian_sync/pending/";
    const obsidianStatus = payload.obsidian_updated === true ? "UPDATED" :
      (detail.vault_writable === false || payload.outcome === "BLOCKED" ? "BLOCKED / MIRRORED" : "PENDING / CHECK");
    add("obsidian", "Obsidian memory", obsidianStatus, [
      { label: "Vault", value: detail.vault_name || detail.vault_status || detail.status },
      { label: "Write", value: detail.vault_writable === true ? "WRITABLE" : (detail.vault_writable === false ? "BLOCKED" : null) },
      { label: "Pending", value: mirrorPath },
      { label: "Evidence", value: payload.evidence_path },
    ], payload.obsidian_updated === true ? "The backend reported a completed local update." :
      `Vault write blocked; mirrored to ${mirrorPath}. No vault update is claimed.`);
  }
  if (intent.includes("github") || payload.github_status != null) {
    const github = payload.github_status && typeof payload.github_status === "object" ? payload.github_status : detail;
    const dirty = github.dirty === true || github.clean_tree === false;
    const clean = github.dirty === false || github.clean_tree === true;
    const dirtyCount = Array.isArray(github.dirty_files) ? github.dirty_files.length : 0;
    const pushStatus = github.push_possible === true ? "READY / CONFIRM" :
      (github.push_possible === false ? "BLOCKED" : (github.status || payload.outcome || "CHECK"));
    add("github", "GitHub", pushStatus, [
      { label: "Branch", value: github.branch },
      { label: "Working tree", value: dirty ? `DIRTY${dirtyCount ? ` (${dirtyCount} files)` : ""}` : (clean ? "CLEAN" : null) },
      { label: "Remote", value: github.remote || github.remote_status || (github.remote_configured === true ? "CONFIGURED" : (github.remote_configured === false ? "NOT CONFIGURED" : null)) },
      { label: "Push", value: github.push_state || github.push_reason || github.blocker || (github.push_possible === true ? "REQUIRES CONFIRMATION" : null) },
    ], "Status only. No push is inferred from this card.");
  }
  if (context.executed.length) {
    add("execution", "Local execution", "EXECUTED", [
      { label: "Actions", value: context.executed.length },
      { label: "Last", value: formatAgentItem(context.executed.at(-1)) },
      { label: "Evidence", value: payload.evidence_path },
    ], "Only backend-reported, allowlisted local actions appear here.");
  }
  if (Array.isArray(payload.memory_events) && payload.memory_events.length) {
    add("memory", "Shared memory", "UPDATED", [
      { label: "Events", value: payload.memory_events.length },
      { label: "Latest", value: formatAgentItem(payload.memory_events.at(-1)) },
    ], "Repo-local memory only; secrets are not displayed.");
  }
  if (payload.live_approval_needed === true) {
    add("approval", "Live approval", "REQUIRED / NOT CONFIGURED", [
      { label: "Next", value: context.nextAction },
    ], "External sites, accounts, posting, uploads, and payments stay blocked.");
  }
  return cards;
}

function renderAgentResult(payload = {}) {
  const plan = payload.plan && typeof payload.plan === "object" ? payload.plan : {};
  const reply = payload.reply || payload.response || payload.reason || "Ghoti returned no reply.";
  const model = selectedLocalModel(payload);
  const steps = Array.isArray(plan.steps) ? plan.steps :
    (Array.isArray(payload.plan_steps) ? payload.plan_steps : []);
  const executed = Array.isArray(payload.executed_actions) ? payload.executed_actions : [];
  const planId = plan.plan_id || payload.plan_id || null;
  const projectId = payload.project_id || plan.project_id || payload.project?.project_id || payload.project?.id || null;
  const missionId = payload.mission_id || plan.mission_id || payload.mission?.mission_id || payload.mission?.id || null;
  const swarmId = payload.swarm_id || plan.swarm_id || payload.swarm?.swarm_id || payload.swarm?.id || null;
  const nextAction = payload.next_action || plan.next_action || payload.project?.next_action || payload.mission?.next_action || null;
  const liveApproval = payload.live_approval_needed === true ? "REQUIRED / NOT CONFIGURED" :
    (payload.live_approval_status || payload.approval_state ||
      (payload.safety_flags?.live_execution === true ? "REVIEW" : "LIVE EXTERNAL BLOCKED"));
  state.pendingConfirmation = payload.needs_confirmation && planId ? planId : null;
  state.latestGhotiMessage = String(reply);
  text("agent-reply", reply);
  text("agent-model", model);
  text("agent-evidence-path", payload.evidence_path || "none reported");
  text("operator-command-output", JSON.stringify(payload, null, 2));
  renderAgentSafetyFlags(payload.safety_flags || state.agentStatus?.safety_flags || {});
  const emptyPlanText = state.pendingConfirmation
    ? `Plan ${planId} is waiting for confirmation.`
    : (planId ? `No executable action needed (${planId}).` : "No action plan required.");
  renderAgentItems("agent-plan", steps, emptyPlanText);
  renderAgentItems("agent-executed", executed, "No action executed.");
  const computerUse = computerUseSummary(payload);
  renderConfirmation(plan, Boolean(state.pendingConfirmation), computerUse.activeWindow);
  if (computerUse.relevant) updateComputerUsePanel(payload);
  const safety = payload.safety_flags || {};
  const unsafeTrue = Object.entries(safety).some(([key, value]) => key !== "message_text_as_command" && value === true);
  text("agent-safety-badge", unsafeTrue ? "REVIEW" : "LOCAL ONLY");
  return {
    reply: String(reply),
    executed,
    needsConfirmation: Boolean(state.pendingConfirmation),
    meta: {
      badge: state.pendingConfirmation ? "CONFIRM" : (payload.outcome || "OK"),
      action: agentActionLabel(plan, payload),
      model,
      projectId,
      missionId,
      swarmId,
      nextAction,
      liveApproval,
      evidence: payload.evidence_path || null,
      cards: agentResultCards(payload, {
        projectId,
        missionId,
        swarmId,
        nextAction,
        executed,
      }),
    },
  };
}

async function postAgentApi(path, payload, controller = null) {
  if (!Object.values(AGENT_API_PATHS).includes(path)) {
    throw new Error("Unknown Agent API path.");
  }
  return api(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {}),
    ...(controller ? { signal: controller.signal } : {}),
  });
}

function computerUseInterruptKind(message) {
  const normalized = String(message || "").trim().toLowerCase().replace(/[.!?]+$/g, "");
  if (/^(?:please )?stop(?: now)?$/.test(normalized)) return "stop";
  if (/^(?:please )?cancel(?: that| it)?$/.test(normalized)) return "cancel";
  if (/^(?:please )?wait(?: a moment)?$/.test(normalized)) return "wait";
  return null;
}

async function requestFixedComputerUseStop() {
  let backendStop = null;
  let computerUseStop = null;
  if (computerUseCommandAvailable("agent_stop")) {
    try {
      backendStop = await api("/api/run/agent_stop", { method: "POST" });
    } catch (_error) {
      // The independent computer-use stop remains available when the overlay stop is absent.
    }
  }
  if (computerUseCommandAvailable("computer_use_stop")) {
    try {
      computerUseStop = await api("/api/run/computer_use_stop", { method: "POST" });
    } catch (_error) {
      // The cancelled plan and browser-side abort still fail closed.
    }
  }
  return { backendStop, computerUseStop };
}

async function prepareComputerUseInterrupt(kind) {
  if (!kind) return false;
  let pendingCancelled = false;
  if (state.pendingConfirmation) {
    try {
      await postAgentApi(AGENT_API_PATHS.cancel, { plan_id: state.pendingConfirmation });
      pendingCancelled = true;
    } catch (_error) {
      // Continue to the stronger stop path when cancellation is unavailable.
    }
    state.pendingConfirmation = null;
    renderConfirmation({}, false);
  }
  const activeControl = state.computerUseSession?.activeControl === true;
  const shouldStop = kind === "stop" || kind === "wait" || (kind === "cancel" && activeControl);
  if (shouldStop) await requestFixedComputerUseStop();
  appendChatMessage("ghoti", "Interrupt sent.", { badge: "INTERRUPT" });
  if (shouldStop) {
    stopComputerUsePolling();
    updateComputerUsePanel({
      computer_use_session: state.computerUseSession?.sessionId,
      computer_use_state: "stopped",
      stopped: true,
      active_control: false,
      last_action_result: `${kind} interrupt sent`,
      evidence_path: state.computerUseSession?.evidence,
    }, "computer use");
    setAgentState("stopped", "Interrupt sent. Desktop control is stopped until reset.", false);
  } else if (pendingCancelled) {
    updateComputerUsePanel({ computer_use_state: "done", active_control: false,
      last_action_result: "Pending action cancelled" }, "computer use");
  }
  return true;
}

async function sendAgentMessage(message, source = "home") {
  const clean = String(message || "").trim();
  if (!clean) return null;
  if (state.agentRequestController) state.agentRequestController.abort();
  const interruptKind = computerUseInterruptKind(clean);
  const interruptStopsControl = interruptKind === "stop" || interruptKind === "wait" ||
    (interruptKind === "cancel" && state.computerUseSession?.activeControl === true);
  appendChatMessage("user", clean, { badge: source === "chat" ? "CHAT" : "REQUEST" });
  if (interruptKind) await prepareComputerUseInterrupt(interruptKind);
  const controller = new AbortController();
  state.agentRequestController = controller;
  const initialState = interruptStopsControl ? "stopped" : (interruptKind ? "thinking" :
    (/\bobserve screen\b/i.test(clean) ? "observing" : (isComputerUseMessage(clean) ? "planning" : "thinking")));
  setAgentState(initialState, interruptStopsControl ? "Interrupt sent. Desktop control remains stopped until reset." :
    (interruptKind ? "Interrupt sent. Ghoti is confirming the cancelled state." : ""), false);
  if (isComputerUseMessage(clean)) updateComputerUsePanel({}, clean);
  setAgentActivity(initialState, clean);
  const workingTimer = setTimeout(() => {
    if (interruptStopsControl) return;
    if (["thinking", "observing", "planning"].includes(state.agentState)) {
      setAgentState("working");
      setAgentActivity("working", clean);
    }
  }, 220);
  try {
    const payload = await postAgentApi(AGENT_API_PATHS.message, {
      message: clean,
      model_provider: state.selectedModelProvider,
      model: state.selectedModel,
    }, controller);
    clearTimeout(workingTimer);
    if (!interruptStopsControl && !isComputerUseMessage(clean) && state.agentState !== "working") setAgentState("working");
    setAgentActivity("evidence", clean);
    const rendered = renderAgentResult(payload);
    appendChatMessage("ghoti", rendered.reply, rendered.meta);
    hideAgentActivity();
    let computerUse = computerUseSummary(payload);
    if (isComputerUseMessage(clean) && !rendered.needsConfirmation) {
      const statusPayload = await readLatestComputerUseStatus();
      if (statusPayload) {
        const reconciled = reconcileComputerUseStatus(payload, statusPayload);
        updateComputerUsePanel(reconciled, clean);
        computerUse = computerUseSummary(reconciled);
      }
    }
    if (interruptStopsControl) {
      setAgentState("stopped", "Interrupt sent. Desktop control remains stopped until reset.", false);
    } else if (rendered.needsConfirmation) {
      setAgentState("needs-confirmation", "Plan ready. Review the exact mouse or keyboard action, then confirm or cancel.");
    } else if (computerUse.hasExplicitState && COMPUTER_USE_ACTIVE_STATES.has(computerUse.state)) {
      applyComputerUseAgentState(computerUse);
    } else if (computerUse.stoppedByCtrl8 || computerUse.stopped || computerUse.state === "stopped") {
      setAgentState("stopped", "Desktop control is stopped until reset.", false);
    } else {
      setAgentState("done");
    }
    return payload;
  } catch (error) {
    clearTimeout(workingTimer);
    hideAgentActivity();
    if (error.name === "AbortError") {
      setAgentState("done", "Request stopped locally.", false);
      return null;
    }
    renderAgentResult({ outcome: "BLOCKED", reason: error.message, executed_actions: [] });
    appendChatMessage("ghoti", `Stopped safely: ${error.message}`);
    setAgentState("error", `Stopped safely: ${error.message}`);
    return null;
  } finally {
    if (state.agentRequestController === controller) state.agentRequestController = null;
  }
}

async function resolveAgentConfirmation(confirm) {
  const planId = state.pendingConfirmation;
  if (!planId) return;
  setConfirmationButtonsDisabled(true);
  setAgentState(confirm ? "controlling" : "thinking",
    confirm ? "Ghoti is controlling your PC for one confirmed local action." : "Cancelling the pending plan.");
  if (confirm) {
    setAgentActivity("controlling", "computer use");
    updateComputerUsePanel({ computer_use_state: "CONTROLLING", plan: { plan_id: planId } }, "computer use");
    await new Promise(resolve => setTimeout(resolve, 250));
    if (state.pendingConfirmation !== planId || state.agentState === "stopped") return;
  }
  try {
    const path = confirm ? AGENT_API_PATHS.confirm : AGENT_API_PATHS.cancel;
    const payload = await postAgentApi(path, { plan_id: planId });
    const reply = payload.reply || payload.reason || (confirm ? "Plan confirmed." : "Plan cancelled.");
    renderAgentResult({ ...payload, reply });
    appendChatMessage("ghoti", reply);
    hideAgentActivity();
    state.pendingConfirmation = null;
    renderConfirmation({}, false);
    updateComputerUsePanel({
      computer_use_state: confirm ? "DONE" : "CANCELLED",
      last_action: confirm ? "Confirmed plan completed under backend policy" : "Pending plan cancelled",
      evidence_path: payload.evidence_path,
    }, "computer use");
    setAgentState("done", confirm ? "Confirmed plan finished or is ready under backend policy." : "Plan cancelled.");
  } catch (error) {
    hideAgentActivity();
    setConfirmationButtonsDisabled(false);
    setAgentState("error", `Confirmation failed safely: ${error.message}`);
  }
}

async function stopAgent(options = {}) {
  const source = options.source || "button";
  if (state.agentRequestController) state.agentRequestController.abort();
  if (state.recognition) state.recognition.abort();
  if ("speechSynthesis" in window) window.speechSynthesis.cancel();
  state.speechSpeaking = false;
  updateVoiceControls();
  if (state.pendingConfirmation) {
    try {
      await postAgentApi(AGENT_API_PATHS.cancel, { plan_id: state.pendingConfirmation });
    } catch (_error) {
      // Continue to the independent emergency-stop command.
    }
  }
  state.pendingConfirmation = null;
  hideAgentActivity();
  renderConfirmation({}, false);
  const { backendStop, computerUseStop } = await requestFixedComputerUseStop();
  const emergencyStopPath = "desktop_agent\\STOP_AGENT";
  const stopMessage = "Stopped. Ctrl+8 / STOP_AGENT prevents further desktop control until reset.";
  state.latestGhotiMessage = stopMessage;
  text("agent-reply", stopMessage);
  text("operator-command-output", JSON.stringify({
    outcome: "STOPPED",
    pending_plan_cancelled: true,
    backend_stop: backendStop?.json || backendStop || "optional command unavailable",
    computer_use_stop: computerUseStop?.json || computerUseStop || "optional command unavailable",
    emergency_stop_file: emergencyStopPath,
  }, null, 2));
  appendChatMessage("ghoti", stopMessage);
  stopComputerUsePolling();
  updateComputerUsePanel({ computer_use_state: "stopped", stopped: true,
    stopped_by_ctrl8: source === "ctrl8", active_control: false,
    last_action: source === "ctrl8" ? "Ctrl+8 emergency stop requested" : "STOP_AGENT requested" }, "computer use");
  setAgentState("stopped", stopMessage, false);
}

async function loadAgentCapabilities() {
  try {
    state.agentStatus = await api(AGENT_API_PATHS.status);
    [state.agentCapabilities, state.agentSupervisedStatus] = await Promise.all([
      optionalStatusPayload("agent_capabilities"),
      optionalStatusPayload("agent_supervised_status"),
    ]);
    const model = state.agentStatus?.model?.selected || "deterministic-fallback";
    text("agent-model", model);
    renderModelProviderStatus();
    renderComputerUseFeatureDetection();
    renderAgentSafetyFlags(state.agentStatus?.safety_flags || state.agentSupervisedStatus?.safety_flags || {});
    setAgentState("idle", `Ready. Local model: ${model}.`, false);
    await pollComputerUseStatus();
    renderChatStatus();
    renderFullComputerUse(state.status || {});
    renderUnifiedTools();
  } catch (error) {
    state.agentStatus = { outcome: "UNAVAILABLE", reason: error.message };
    setAgentState("error", `Desktop agent unavailable: ${error.message}`, false);
  }
}

async function optionalStatusPayload(command) {
  if (!OPTIONAL_STATUS_COMMAND_IDS.has(command) || !CLIENT_COMMAND_IDS.has(command) ||
      !state.availableCommands.has(command)) {
    return null;
  }
  const result = await api(`/api/run/${command}`, { method: "POST" });
  return result.json || result;
}

async function runOptionalStatus(command, outputId) {
  if (!state.availableCommands.has(command)) {
    text(outputId, `WARN: optional fixed command ${command} is not available in this backend build.`);
    return null;
  }
  try {
    const payload = await optionalStatusPayload(command);
    text(outputId, JSON.stringify(payload, null, 2));
    return payload;
  } catch (error) {
    text(outputId, `BLOCKED or failed: ${error.message}`);
    return null;
  }
}

function firstAvailableCommand(commands) {
  return commands.find(command => CLIENT_COMMAND_IDS.has(command) && state.availableCommands.has(command)) || null;
}

async function optionalStatusSafe(commands) {
  const command = firstAvailableCommand(commands);
  if (!command) return { command: null, payload: null, error: null };
  try {
    return { command, payload: await optionalStatusPayload(command), error: null };
  } catch (error) {
    return { command, payload: null, error: error.message };
  }
}

const GHOTI_OS_STATE_KEYS = Object.freeze({
  ghoti_os_status: "osStatus",
  ghoti_os_memory_status: "osMemoryStatus",
  ghoti_os_project_status: "osProjectStatus",
  ghoti_os_swarm_status: "osSwarmStatus",
  ghoti_os_routine_status: "osRoutineStatus",
  ghoti_os_connector_status: "osConnectorStatus",
  ghoti_os_content_status: "osContentStatus",
  ghoti_os_live_approval_status: "osLiveApprovalStatus",
});

async function loadGhotiOsStatus() {
  const commands = Object.keys(GHOTI_OS_STATE_KEYS);
  const results = await Promise.all(commands.map(command => optionalStatusSafe([command])));
  results.forEach((result, index) => {
    if (result.payload) state[GHOTI_OS_STATE_KEYS[commands[index]]] = result.payload;
  });
  renderGhotiOs();
  return results;
}

async function runGhotiOsCommand(button) {
  const command = button.dataset.osCommand;
  const outputId = button.dataset.osOutput || "os-tools-details";
  if (!Object.prototype.hasOwnProperty.call(GHOTI_OS_STATE_KEYS, command) ||
      !CLIENT_COMMAND_IDS.has(command) || !state.availableCommands.has(command)) {
    text(outputId, `WARN: fixed command ${command || "unknown"} is not advertised by this backend build.`);
    renderGhotiOs();
    return null;
  }
  button.disabled = true;
  text(outputId, `Reading ${command}...`);
  try {
    const payload = await optionalStatusPayload(command);
    state[GHOTI_OS_STATE_KEYS[command]] = payload;
    text(outputId, JSON.stringify(payload, null, 2));
    renderGhotiOs();
    return payload;
  } catch (error) {
    text(outputId, `BLOCKED or unavailable: ${error.message}`);
    return null;
  } finally {
    button.disabled = false;
  }
}

function setUnifiedToolState(tool, status) {
  const normalized = ["READY", "LOCAL", "SUPERVISED", "RUN ONCE", "MANUAL", "LIVE-GATED",
    "SESSION READY", "TASK PACKETS", "SANDBOX", "NEEDS_IVAN", "BLOCKED"].includes(status) ? status : "NEEDS_IVAN";
  text(`tool-status-${tool}`, normalized);
  const cardState = document.getElementById(`${tool}-tool-state`);
  if (cardState) {
    cardState.textContent = normalized;
    cardState.className = `tool-status ${normalized.toLowerCase().replaceAll("_", "-").replaceAll(" ", "-")}`;
  }
}

function renderUnifiedTools() {
  const obsidianCommand = firstAvailableCommand(["obsidian_sync_status"]);
  const obsidian = state.obsidianStatus || {};
  const vaultReady = obsidian.vault_found === true;
  setUnifiedToolState("desktop", state.agentStatus?.outcome === "OK" ? "READY" : "NEEDS_IVAN");
  setUnifiedToolState("computer-use", computerUseCommandAvailable() ? "SESSION READY" : "SUPERVISED");
  setUnifiedToolState("browser", state.agentSupervisedStatus?.outcome === "OK" ? "SUPERVISED" : "LIVE-GATED");
  setUnifiedToolState("obsidian", obsidianCommand && vaultReady && obsidian.vault_writable !== false ? "READY" : "NEEDS_IVAN");
  setUnifiedToolState("github", firstAvailableCommand(["github_sync_status", "github_local_summary"]) && state.githubStatus?.remote_configured === true ? "READY" : "NEEDS_IVAN");
  setUnifiedToolState("paperclip", firstAvailableCommand(["paperclip_agent_status", "paperclip_status"]) ? "SANDBOX" : "NEEDS_IVAN");
  setUnifiedToolState("ruflo", firstAvailableCommand(["ruflo_agent_status", "ruflo_status"]) ? "SANDBOX" : "NEEDS_IVAN");
  setUnifiedToolState("clips", state.availableCommands.has("agent_open_clips") ? "READY" : "NEEDS_IVAN");
  setUnifiedToolState("projects", state.availableCommands.has("ghoti_os_project_status") ? "LOCAL" : "NEEDS_IVAN");
  setUnifiedToolState("swarms", state.availableCommands.has("ghoti_os_swarm_status") ? "TASK PACKETS" : "SANDBOX");
  setUnifiedToolState("memory", state.availableCommands.has("ghoti_os_memory_status") || obsidianCommand ? "LOCAL" : "NEEDS_IVAN");
  setUnifiedToolState("routines", state.availableCommands.has("ghoti_os_routine_status") ? "RUN ONCE" : "NEEDS_IVAN");
  setUnifiedToolState("youtube", "MANUAL");
  setUnifiedToolState("tiktok", "MANUAL");

  text("obsidian-tool-vault", obsidian.vault_path || obsidian.vault || "Not reported by backend");
  text("obsidian-tool-note", obsidian.live_status_note || obsidian.notes?.live_status?.rel || "Not reported");
  text("obsidian-tool-updated", obsidian.last_updated || obsidian.updated_at || "Not reported");
  const pendingDir = obsidian.mirror_dir || "obsidian_sync/pending";
  text("obsidian-tool-pending", pendingDir.endsWith("/") ? pendingDir : `${pendingDir}/`);
  const obsidianWarning = !obsidianCommand ?
    "The dedicated Obsidian status command is not advertised by this backend build. No update is claimed." :
    (vaultReady ?
      (obsidian.vault_writable === false ?
        "Vault write blocked by Windows Controlled Folder Access. Pending notes are safely mirrored to obsidian_sync/pending/. To fully sync, allow Python/agent runtime in Windows Security or copy pending notes manually." :
        "Vault detected. Updates still run only through the fixed reviewed command.") :
      "The backend did not detect a live Obsidian vault. No update is claimed.");
  text("obsidian-tool-warning", obsidianWarning);
  const obsidianUpdate = document.getElementById("obsidian-tool-update");
  const obsidianOpen = document.getElementById("obsidian-tool-open");
  if (obsidianUpdate) obsidianUpdate.disabled = !firstAvailableCommand(["obsidian_update_status"]);
  if (obsidianOpen) obsidianOpen.disabled = !firstAvailableCommand(["obsidian_open_live_status"]);

  const github = { ...(state.githubStatus || {}), ...(state.githubLocalSummary || {}), ...(state.githubRemoteStatus || {}) };
  text("github-tool-branch", github.current_branch || github.branch || "Not reported");
  const cleanTree = github.clean_tree ?? github.clean;
  text("github-tool-clean", cleanTree === true ? "clean" : cleanTree === false ? "dirty" : (github.worktree_status || "Not reported"));
  text("github-tool-commit", github.last_commit || github.latest_commit || github.head || github.commit || "Not reported");
  const remoteLabel = github.remote_configured === true ? "YES" :
    github.remote_configured === false ? "NO" : "Not checked";
  text("github-tool-remote", remoteLabel);
  const githubAvailable = Boolean(firstAvailableCommand(["github_sync_status", "github_local_summary"]));
  const marker = github.test_marker || {};
  const pushSafe = github.push_safe === true || github.can_push === true || github.safe_to_push === true ||
    (github.push_possible === true && marker.present === true && marker.passed === true && marker.fresh === true);
  state.githubPushSafe = githubAvailable && pushSafe;
  const pushBlockers = [];
  if (github.remote_configured === false) pushBlockers.push("Add GitHub remote first.");
  if (cleanTree === false) pushBlockers.push("Working tree is dirty.");
  if (marker.present === false) pushBlockers.push("No recent passing test marker is recorded.");
  const pushReason = pushSafe ? "Backend reports the current branch is safe to push." :
    (pushBlockers.join(" ") || github.push_blocked_reason || github.blocker || github.reason ||
      "Push is disabled until the tree is clean, a remote exists, and a recent passing test marker is present.");
  text("github-tool-push-state", pushSafe ? "YES" : "NO");
  text("github-tool-reason", pushReason);
  text("github-tool-warning", githubAvailable ?
    (pushSafe ? "Backend reports the current branch is safe to push. Force push is never exposed." :
      pushReason) :
    "GitHub status commands are not advertised by this backend build. Push stays disabled.");
  const branch = github.current_branch || github.branch || "<CURRENT_BRANCH>";
  const remoteTemplate = "git remote add origin <YOUR_REPO_URL>";
  const pushTemplate = `git push -u origin ${branch}`;
  text("github-remote-template", remoteTemplate);
  text("github-push-template", pushTemplate);
  const remoteCopy = document.getElementById("github-remote-copy");
  const pushCopy = document.getElementById("github-push-copy");
  if (remoteCopy) remoteCopy.dataset.copy = remoteTemplate;
  if (pushCopy) pushCopy.dataset.copy = pushTemplate;
  const setupHelp = document.getElementById("github-setup-help");
  if (setupHelp) setupHelp.hidden = github.remote_configured !== false;
  const githubCheck = document.getElementById("github-tool-check");
  const githubPush = document.getElementById("github-tool-push");
  if (githubCheck) githubCheck.disabled = !githubAvailable;
  if (githubPush) githubPush.disabled = !state.githubPushSafe || !firstAvailableCommand(["github_push_current_branch"]);
  renderReleaseReadiness();
  renderGhotiOs();
}

function renderReleaseReadiness() {
  const agentReady = state.agentStatus?.outcome === "OK";
  const supervisedReady = state.agentSupervisedStatus?.outcome === "OK";
  text("release-version", APP_VERSION);
  text("release-dashboard-url", window.location.origin);
  text("release-agent-api", agentReady ? "WIRED" : "CHECK REQUIRED");
  text("release-supervised", supervisedReady ? "READY / CONFIRM ONCE" : "CHECK REQUIRED");
  const releaseState = document.getElementById("release-system-state");
  if (releaseState) {
    const ready = agentReady && supervisedReady;
    releaseState.textContent = ready ? "LOCAL READY" : "CHECK REQUIRED";
    releaseState.className = `tool-status ${ready ? "ready" : "needs-ivan"}`;
  }
}

async function loadUnifiedToolStatus() {
  const [unified, obsidian, githubStatus, githubLocal, githubRemote, paperclip, ruflo] = await Promise.all([
    optionalStatusSafe(["unified_agent_status"]),
    optionalStatusSafe(["obsidian_sync_status"]),
    optionalStatusSafe(["github_sync_status"]),
    optionalStatusSafe(["github_local_summary"]),
    optionalStatusSafe(["github_remote_status"]),
    optionalStatusSafe(["paperclip_agent_status", "paperclip_status"]),
    optionalStatusSafe(["ruflo_agent_status", "ruflo_status"]),
  ]);
  state.unifiedAgentStatus = unified.payload;
  state.obsidianStatus = obsidian.payload;
  state.githubStatus = githubStatus.payload;
  state.githubLocalSummary = githubLocal.payload;
  state.githubRemoteStatus = githubRemote.payload;
  if (paperclip.payload) state.paperclipStatus = paperclip.payload;
  if (ruflo.payload) state.rufloStatus = ruflo.payload;
  renderUnifiedTools();
  renderObsidian();
  renderFullComputerUse(state.status || {});
}

async function runFixedToolCommand(commands, outputId, reload = true) {
  const command = firstAvailableCommand(commands);
  if (!command) {
    text(outputId, `BLOCKED: none of the fixed command IDs are advertised (${commands.join(", ")}).`);
    renderUnifiedTools();
    return null;
  }
  try {
    const result = await api(`/api/run/${command}`, { method: "POST" });
    text(outputId, JSON.stringify(result, null, 2));
    if (reload) await loadUnifiedToolStatus();
    return result.json || result;
  } catch (error) {
    text(outputId, `BLOCKED or failed safely: ${error.message}`);
    return null;
  }
}

function insertToolIntent(value) {
  const input = document.getElementById("operator-command-input");
  if (!input) return;
  input.value = String(value || "").slice(0, 600);
  input.focus();
}

async function startNewSession() {
  if (state.pendingConfirmation) {
    try {
      await postAgentApi(AGENT_API_PATHS.cancel, { plan_id: state.pendingConfirmation });
    } catch (error) {
      setAgentState("error", `New session blocked until the pending plan is cancelled: ${error.message}`, false);
      return;
    }
  }
  state.pendingConfirmation = null;
  state.chatMessages = [];
  renderConfirmation({}, false);
  hideComputerUsePanel();
  state.computerUsePanelManuallyHidden = false;
  const root = document.getElementById("agent-conversation");
  if (root) root.replaceChildren();
  appendChatMessage("ghoti", "New local session ready. Ask what I can do or choose an available tool.", { badge: "READY" });
  const input = document.getElementById("operator-command-input");
  if (input) input.value = "";
  setAgentState("idle", "New session ready. No conversation data is persisted in the browser.", false);
}

async function loadChatCapabilities() {
  try {
    const [freeform, voice] = await Promise.all([
      optionalStatusPayload("ghoti_chat_freeform_status"),
      optionalStatusPayload("agent_voice_status"),
    ]);
    state.freeformStatus = freeform;
    state.voiceStatus = voice;
  } catch (error) {
    state.freeformStatus = { problem: error.message };
  }
  renderChatStatus();
}

async function loadComputerCapabilities() {
  try {
    const [fullComputer, connectors, ghotiFull] = await Promise.all([
      optionalStatusPayload("full_computer_use_status"),
      optionalStatusPayload("connector_setup_status"),
      optionalStatusPayload("ghoti_full_status"),
    ]);
    state.fullComputerStatus = fullComputer;
    state.connectorStatus = connectors;
    state.ghotiFullStatus = ghotiFull;
    renderFullComputerUse(state.status || {});
    renderConnectorSetup();
    text("computer-output", fullComputer ?
      JSON.stringify(fullComputer, null, 2) :
      "WARN: optional full_computer_use_status is unavailable; existing local fixture status remains authoritative.");
    text("connector-setup-output", connectors ?
      JSON.stringify({
        connectors: Object.keys(connectors.connectors || {}),
        credentials_stored: connectors.credentials_stored,
        live_action_enabled: connectors.live_action_enabled,
      }, null, 2) :
      "WARN: optional connector_setup_status is unavailable; setup cards remain planning-only.");
  } catch (error) {
    text("computer-output", `BLOCKED or failed safely: ${error.message}`);
  }
}

async function loadOrchestrationCapabilities(preserveOutput = false) {
  try {
    const [orchestration, profiles, modules, paperclip, ruflo] = await Promise.all([
      optionalStatusPayload("orchestration_status"),
      optionalStatusPayload("orchestration_profile_status"),
      optionalStatusPayload("orchestration_scan_modules"),
      optionalStatusPayload("paperclip_status"),
      optionalStatusPayload("ruflo_status"),
    ]);
    state.orchestrationStatus = orchestration;
    state.profileStatus = profiles;
    state.moduleScan = modules;
    state.paperclipStatus = paperclip;
    state.rufloStatus = ruflo;
    renderOrchestrationStatus();
    renderPaperclipStatus();
    renderRufloStatus();
    if (orchestration && !preserveOutput) {
      text("command-center-output", JSON.stringify(orchestration, null, 2));
    }
  } catch (error) {
    text("command-center-output", `BLOCKED or failed safely: ${error.message}`);
  }
}

function speechRecognitionConstructor() {
  return window.SpeechRecognition || window.webkitSpeechRecognition || null;
}

function updateVoiceControls() {
  const inputButton = document.getElementById("agent-voice-input");
  const outputButton = document.getElementById("agent-read-output");
  const recognitionAvailable = Boolean(speechRecognitionConstructor());
  const synthesisAvailable = "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;
  if (inputButton) inputButton.disabled = !recognitionAvailable;
  if (inputButton) inputButton.classList.toggle("is-active", state.voiceListening);
  if (outputButton) {
    outputButton.disabled = !synthesisAvailable;
    outputButton.classList.toggle("is-active", state.speechSpeaking);
    outputButton.textContent = state.speechSpeaking ? "Stop reading" : "Read";
  }
  text("voice-ui-status", recognitionAvailable ?
    "Voice input is available in this browser. Review the transcript and press Send; audio is never sent to Ghoti." :
    "Voice input is unavailable in this browser. Typed input still works; no audio is recorded or sent.");
}

function startVoiceInput(targetInputId = "operator-command-input") {
  const Recognition = speechRecognitionConstructor();
  if (!Recognition) {
    updateVoiceControls();
    setAgentState("error", "Browser speech input is unavailable. Typed input still works.", false);
    return;
  }
  if (state.voiceListening && state.recognition) {
    state.recognition.abort();
    return;
  }
  const recognition = new Recognition();
  state.recognition = recognition;
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  recognition.lang = document.documentElement.lang || navigator.language || "en-US";
  recognition.onstart = () => {
    state.voiceListening = true;
    setAgentState("listening");
    text("voice-ui-status", "Listening in the browser. Nothing is sent to Ghoti until you review the transcript and press Send.");
    const homeMic = document.getElementById("agent-voice-input");
    if (homeMic) {
      homeMic.textContent = "Listening";
      homeMic.classList.add("is-active");
    }
  };
  recognition.onresult = event => {
    const transcript = event.results?.[0]?.[0]?.transcript || "";
    const input = document.getElementById(targetInputId);
    if (input) {
      input.value = transcript.slice(0, 600);
      input.focus();
    }
    text("voice-ui-status", "Transcript ready in the message box. Review it, then press Send.");
    setAgentState("idle", "Transcript ready. Review it, then press Send.", false);
  };
  recognition.onerror = event => {
    text("voice-ui-status", `Voice input stopped safely: ${event.error || "browser error"}. Typed input still works.`);
    setAgentState("error", `Voice stopped safely: ${event.error || "browser error"}.`, false);
  };
  recognition.onend = () => {
    state.voiceListening = false;
    state.recognition = null;
    const homeMic = document.getElementById("agent-voice-input");
    if (homeMic) {
      homeMic.textContent = "Mic";
      homeMic.classList.remove("is-active");
    }
    if (state.agentState === "listening") setAgentState("idle", "", false);
  };
  recognition.start();
}

function readLatestGhotiReply() {
  if (!("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) {
    text("voice-ui-status", "Read-aloud is unavailable in this browser. The reply remains visible as text.");
    return;
  }
  if (state.speechSpeaking || window.speechSynthesis.speaking) {
    window.speechSynthesis.cancel();
    state.speechSpeaking = false;
    updateVoiceControls();
    text("voice-ui-status", "Read-aloud stopped. The text reply is unchanged.");
    return;
  }
  const utterance = new SpeechSynthesisUtterance(state.latestGhotiMessage || "Ghoti has no reply to read yet.");
  utterance.onstart = () => {
    state.speechSpeaking = true;
    updateVoiceControls();
    text("voice-ui-status", "Reading the latest Ghoti reply with browser speech synthesis.");
  };
  utterance.onend = () => {
    state.speechSpeaking = false;
    updateVoiceControls();
  };
  utterance.onerror = () => {
    state.speechSpeaking = false;
    updateVoiceControls();
    text("voice-ui-status", "Read-aloud stopped safely. The text reply is unchanged.");
  };
  window.speechSynthesis.speak(utterance);
}

function renderChatStatus() {
  const ai = state.status?.local_ai || {};
  const mobile = state.mobile || {};
  const agentAvailable = state.agentStatus?.outcome === "OK";
  const voiceBackendAvailable = state.availableCommands.has("agent_voice_status");
  const model = state.agentStatus?.model?.selected ||
    state.freeformStatus?.model || ai.model_selected || "deterministic-fallback";
  renderRows("chat-status", {
    "Typed chat": agentAvailable ? "READY / AGENT API" : "CHECK",
    "Local freeform engine": agentAvailable ? "READY / LOCAL" : "UNAVAILABLE",
    "Dashboard message bridge": agentAvailable ? "/api/agent/message" : "NOT AVAILABLE",
    "Message storage": "browser memory only",
    "Cloud API": "BLOCKED",
    "Ollama": ai.ollama_installed ? "AVAILABLE" : "CHECK / FALLBACK",
    "Model used": model,
    "Model routing": "gemma3:4b / deterministic fallback",
    "Desktop actions": "FIXED AGENT ALLOWLIST",
    "Browser voice": speechRecognitionConstructor() ? "AVAILABLE" : "TYPED FALLBACK",
    "Voice backend status": voiceBackendAvailable ?
      (state.voiceStatus?.microphone_access_from_backend === false ? "SAFE / NO BACKEND MIC" : "AVAILABLE") :
      "NOT INSTALLED",
    "Pairing": mobile.pairing_required ? (mobile.paired ? "PAIRED" : "REQUIRED") : "loopback",
    "Posting / accounts": "BLOCKED",
  });
  text("chat-mode", agentAvailable ? "LOCAL DESKTOP AGENT" : "LOCAL FALLBACK");
  text("freeform-warning", agentAvailable ?
    `Ghoti is connected to the dedicated local Agent API using ${model}. Messages are planned locally and never become raw shell commands.` :
    "Desktop Agent API unavailable in this build. No message will be sent to the command runner.");
  updateVoiceControls();
}

function renderEvolveProposals() {
  const root = document.getElementById("evolve-proposals");
  if (!root) return;
  root.replaceChildren();
  EVOLVE_PROPOSALS.forEach(proposal => {
    const card = document.createElement("article");
    card.className = "proposal-card";
    const area = document.createElement("span");
    area.className = "status-pill warn";
    area.textContent = proposal.area;
    const title = document.createElement("h3");
    title.textContent = proposal.title;
    const detail = document.createElement("p");
    detail.textContent = proposal.detail;
    const queue = document.createElement("button");
    queue.className = "button tiny secondary";
    queue.type = "button";
    queue.dataset.proposal = proposal.id;
    queue.textContent = state.evolveQueue.includes(proposal.id) ? "Queued" : "Queue proposal";
    queue.disabled = state.evolveQueue.includes(proposal.id);
    queue.addEventListener("click", () => queueEvolveProposal(proposal.id));
    card.append(area, title, detail, queue);
    root.append(card);
  });
}

function queueEvolveProposal(id) {
  if (!EVOLVE_PROPOSALS.some(item => item.id === id)) return false;
  if (!state.evolveQueue.includes(id)) state.evolveQueue.push(id);
  renderEvolveProposals();
  renderEvolveQueue();
  return true;
}

function renderEvolveQueue() {
  const root = document.getElementById("evolve-queue");
  if (!root) return;
  root.replaceChildren();
  if (!state.evolveQueue.length) {
    root.append(row("Queue", "No proposals selected"));
    return;
  }
  state.evolveQueue.forEach(id => {
    const proposal = EVOLVE_PROPOSALS.find(item => item.id === id);
    if (proposal) root.append(row(proposal.area, proposal.title, "caution"));
  });
}

function exportEvolvePrompt() {
  const selected = state.evolveQueue
    .map(id => EVOLVE_PROPOSALS.find(item => item.id === id))
    .filter(Boolean);
  if (!selected.length) {
    text("evolve-prompt", "Queue one or more proposals first.");
    return;
  }
  const lines = [
    "Ghoti supervised improvement handoff",
    "",
    "Review and implement only after inspecting the current repo and safety gates.",
    "Do not enable live posting, accounts, external browser control, Telegram, MCP, Ruflo, Higgsfield, or cloud API keys.",
    "",
    "Selected proposals:",
    ...selected.map(item => `- ${item.area}: ${item.title} - ${item.detail}`),
    "",
    "Required outcome: a small reviewed change, focused tests, and an honest PASS/WARN/BLOCKER report.",
  ];
  text("evolve-prompt", lines.join("\n"));
}

function renderBackendEvolve() {
  const status = state.backendEvolveStatus || {};
  renderRows("evolve-backend-status", {
    "Saved proposals": status.total ?? 0,
    "By status": status.by_status || {},
    "Automatic code edits": status.applies_code_automatically === true ? "BLOCKED" : false,
    "Implementation": "Claude / Codex after human review",
  });
  const root = document.getElementById("evolve-backend-list");
  root.replaceChildren();
  if (!state.backendEvolveProposals.length) {
    root.append(row("Saved queue", "No saved proposals"));
    return;
  }
  state.backendEvolveProposals.slice(-8).reverse().forEach(proposal => {
    root.append(row(`#${proposal.id} ${proposal.area}`, `${proposal.status}: ${proposal.title}`, "caution"));
  });
}

async function loadBackendEvolve() {
  const allowed = ["ghoti_self_evolve_status", "ghoti_self_evolve_list"];
  if (!allowed.every(command => CLIENT_COMMAND_IDS.has(command) && state.availableCommands.has(command))) {
    text("evolve-backend-output", "BLOCKED: saved proposal queue commands are not allowlisted.");
    return;
  }
  try {
    const [statusResult, listResult] = await Promise.all(allowed.map(command =>
      api(`/api/run/${command}`, { method: "POST" })));
    state.backendEvolveStatus = statusResult.json || {};
    state.backendEvolveProposals = listResult.json?.proposals || [];
    renderBackendEvolve();
    text("evolve-backend-output", JSON.stringify({
      outcome: "OK",
      commands: allowed,
      saved_proposals: state.backendEvolveProposals.length,
      automatic_code_edits: false,
    }, null, 2));
  } catch (error) {
    text("evolve-backend-output", `BLOCKED or failed: ${error.message}`);
  }
}

async function proposeDashboardBackend(button) {
  const command = "ghoti_self_evolve_propose";
  if (!CLIENT_COMMAND_IDS.has(command) || !state.availableCommands.has(command)) {
    text("evolve-backend-output", "BLOCKED: fixed dashboard proposal command is not allowlisted.");
    return;
  }
  button.disabled = true;
  text("evolve-backend-output", "Queueing one fixed dashboard proposal...");
  try {
    const result = await api(`/api/run/${command}`, { method: "POST" });
    text("evolve-backend-output", JSON.stringify(result, null, 2));
    await loadBackendEvolve();
  } catch (error) {
    text("evolve-backend-output", `BLOCKED or failed: ${error.message}`);
  } finally {
    button.disabled = false;
  }
}

function renderStatus() {
  const status = state.status || {};
  const system = status.system || {};
  const real = status.real_cu || {};
  const clipper = status.clipper || {};
  const queue = status.post_queue || {};
  const ai = status.local_ai || {};
  const summary = status.operator_summary || {};
  const guardReady = Boolean(system.guard_binary_built);
  text("last-updated", `Local refresh ${new Date().toLocaleTimeString()}`);
  text("readiness-percent", `${summary.readiness_percent ?? 0}%`);
  text("readiness-scope", summary.readiness_scope || "supervised local checks");
  text("tests-summary", summary.tests || "--");
  text("full-auto-summary", summary.full_auto_local || "CHECK");
  text("live-post-summary", summary.live_post || "BLOCKED");
  renderDailyCards(status.daily_cards || []);
  renderSimsCards(status);
  renderFullComputerUse(status);
  renderNextAction(status.next_action || {});
  renderModelRouting("model-routing", status.model_routing || []);
  renderModelRouting("model-routing-full", status.model_routing || []);
  renderRows("queue-summary", {
    "Core plans": system.queue?.total ?? 0,
    "Manual packages": queue.packages?.length ?? 0,
    "Live gate": queue.live_post_gate?.status || "BLOCKED",
  });
  renderRows("clipper-status", {
    "FFmpeg": clipper.ffmpeg_present ? "READY" : "MISSING",
    "Owned footage": clipper.owned_footage_files?.length ?? 0,
    "Dummy fixture": clipper.dummy_source_present,
    "Rendered clips": clipper.rendered_clips?.length ?? 0,
    "Input": "clipper/input/",
    "Output": "clipper/output/",
    "Latest package": "clipper/output/latest_package.json",
  });
  renderRows("automation-status", {
    "Rust guard": guardReady ? "PASS" : "CHECK",
    "Max local action": 1,
    "Live execution": false,
    "Evidence files": system.evidence_files ?? 0,
  });
  renderRows("real-cu-status", {
    "Mode": real.mode || "--",
    "Rust required": real.rust_guard_required,
    "Allowed local actions": real.allowed_actions?.length ?? 0,
    "Real OS input": real.real_os_input || "BLOCKED",
    "External actions": real.live_external_actions || "BLOCKED",
  });
  renderRows("local-ai-status", {
    "Ollama": ai.ollama_installed ? "READY" : "SKIPPED",
    "Model": ai.model_selected || "none",
    "No paid API": true,
    "Tasks": ai.tasks?.length ?? 0,
    "Available helpers": (ai.tasks || []).join(", ") || "none",
  });
  renderChatStatus();
}

function renderEvidence() {
  const summary = document.getElementById("evidence-summary");
  if (summary) {
    summary.replaceChildren();
    state.evidence.slice(0, 5).forEach(item =>
      summary.append(row(item.path, item.data?.outcome || "record")));
  }
  const evidenceFiles = document.getElementById("evidence-files");
  if (evidenceFiles) {
    evidenceFiles.replaceChildren();
    state.evidence.slice(0, 8).forEach(item =>
      evidenceFiles.append(row(item.path, item.data?.outcome || "record")));
  }
  const logFiles = document.getElementById("log-files");
  if (logFiles) {
    logFiles.replaceChildren();
    state.logFiles.slice(0, 8).forEach(item =>
      logFiles.append(row(item.path, `${item.entries} entries`)));
  }
  text("evidence-log", JSON.stringify(state.evidence.slice(0, 12), null, 2));
  text("run-log", JSON.stringify(state.logs.slice(-20), null, 2));
}

function renderPackages() {
  const root = document.getElementById("manual-packages");
  root.replaceChildren();
  state.packages.forEach(item => {
    const article = document.createElement("article");
    article.className = "package-item";
    const heading = document.createElement("div");
    heading.className = "package-heading";
    const title = document.createElement("h3");
    title.textContent = item.title || "Untitled package";
    const mode = document.createElement("span");
    mode.className = "status-pill";
    mode.textContent = "MANUAL ONLY";
    heading.append(title, mode);
    const details = document.createElement("div");
    details.className = "rows";
    details.append(row("Platform", item.platform || "--"));
    details.append(row("Package", item.path));
    details.append(row("Video", item.video_path || "--"));
    details.append(row("Caption file", item.caption_path || "--"));
    details.append(row("Rights", item.rights_note || "--"));
    if (item.caption_preview) details.append(row("Caption", item.caption_preview));
    article.append(heading, details);
    root.append(article);
  });
  if (!state.packages.length) {
    const empty = document.createElement("p");
    empty.textContent = "No manual packages yet.";
    root.append(empty);
  }
}

function renderProofs() {
  const root = document.getElementById("proof-list");
  root.replaceChildren();
  state.proofs.forEach(item => {
    const article = document.createElement("article");
    article.className = "proof-item";
    const heading = document.createElement("h3");
    heading.textContent = `Item ${String(item.item_id).padStart(3, "0")}`;
    const title = document.createElement("p");
    title.textContent = item.metadata?.title || "Local proof video";
    const path = document.createElement("code");
    path.textContent = item.video;
    const meta = document.createElement("small");
    meta.textContent = `${item.metadata?.resolution || "--"} | ${item.metadata?.duration_seconds || "--"}s | ${item.video_exists ? "ready" : "missing"}`;
    article.append(heading, title, path, meta);
    root.append(article);
  });
}

function renderSafety() {
  const root = document.getElementById("safety-status");
  root.replaceChildren();
  Object.entries(state.safety || {}).filter(([key]) => key !== "outcome").forEach(([key, value]) => {
    root.append(row(key.replaceAll("_", " "), value,
      String(value).includes("BLOCKED") || String(value).includes("disabled") ? "bad" : "good"));
  });
}

function renderMobileConfig() {
  const mobile = state.mobile || {};
  const advertised = Array.isArray(mobile.available_command_ids) ? mobile.available_command_ids : [];
  state.availableCommands = new Set(advertised.filter(command => CLIENT_COMMAND_IDS.has(command)));
  text("connection-mode", mobile.mode === "trusted_lan" ? "Trusted LAN / paired API" : "127.0.0.1 local only");
  text("live-post-summary", mobile.live_post || "BLOCKED");
  renderRows("mobile-status", {
    "Connection mode": mobile.mode || "--",
    "Pairing required": mobile.pairing_required === true,
    "This client paired": mobile.paired === true,
    "Pairing storage": mobile.pairing_storage || "not used",
    "Transport": mobile.transport || "local HTTP",
    "API cache": mobile.api_cache || "disabled",
    "Live post": mobile.live_post || "BLOCKED",
    "Available command IDs": advertised.join(", ") || "none",
    "Blocked actions": (mobile.blocked_actions || []).join(", ") || "none",
  });
  renderComputerUseFeatureDetection();
  renderChatStatus();
  renderDesktopOperator();
}

function showPairing() {
  const dialog = document.getElementById("pairing-dialog");
  if (!dialog.open) {
    if (typeof dialog.showModal === "function") dialog.showModal();
    else dialog.setAttribute("open", "");
  }
}

function showAppUpdateNotice() {
  const notice = document.getElementById("notice");
  const settingsMessage = document.getElementById("app-update-message");
  notice.textContent = APP_UPDATE_MESSAGE;
  notice.classList.add("update-notice");
  notice.hidden = false;
  settingsMessage.hidden = false;
}

async function updateApp(button) {
  document.querySelectorAll(".update-app").forEach(item => { item.disabled = true; });
  button.textContent = "Updating...";
  showAppUpdateNotice();
  try {
    if ("serviceWorker" in navigator) {
      const registrations = await navigator.serviceWorker.getRegistrations();
      await Promise.all(registrations.map(registration => registration.unregister()));
    }
    if ("caches" in window) {
      const keys = await caches.keys();
      await Promise.all(keys
        .filter(key => key.startsWith("ghoti-static-shell-"))
        .map(key => caches.delete(key)));
    }
  } finally {
    setTimeout(() => {
      window.location.replace(`/?app_updated=${encodeURIComponent(APP_VERSION)}&cache_bust=${Date.now()}`);
    }, 1200);
  }
}

function showUpdateResultFromUrl() {
  const params = new URLSearchParams(window.location.search);
  if (!params.has("app_updated")) return;
  showAppUpdateNotice();
  window.history.replaceState({}, "", "/");
}

async function refreshAll() {
  const notice = document.getElementById("notice");
  notice.hidden = true;
  try {
    const [status, evidence, logs, proofs, packages, safety, systemMap, dashboardModules] = await Promise.all([
      api("/api/status"), api("/api/evidence"), api("/api/logs"), api("/api/proofs"),
      api("/api/manual-packages"), api("/api/safety"), api("/api/system-map"),
      api("/api/dashboard-modules"),
    ]);
    state.status = status;
    state.evidence = evidence.items || [];
    state.logs = logs.items || [];
    state.logFiles = logs.files || [];
    state.proofs = proofs.items || [];
    state.packages = packages.items || [];
    state.safety = safety;
    state.systemMap = systemMap;
    state.dashboardModules = dashboardModules;
    renderStatus(); renderEvidence(); renderPackages(); renderProofs(); renderSafety();
    renderSystemMap();
    renderOrchestrationStatus();
    renderPaperclipStatus();
    renderRufloStatus();
  } catch (error) {
    notice.textContent = error.message;
    notice.hidden = false;
  }
}

async function loadMobileConfig() {
  state.mobile = await api("/api/mobile-config");
  renderMobileConfig();
  return state.mobile;
}

function outputFor(command) {
  if (command.startsWith("ghoti_os_")) return "os-tools-details";
  if (command.startsWith("agent_")) return "operator-command-output";
  if (command.startsWith("desktop_")) return "desktop-output";
  if (command.startsWith("real_cu")) return "computer-output";
  if (command === "ghoti_full_status" || command === "blocked_live_test") return "computer-output";
  if (command.startsWith("paperclip")) return "paperclip-output";
  if (command.startsWith("ruflo")) return "ruflo-output";
  if (command.startsWith("orchestration_")) return "command-center-output";
  if (command.startsWith("clipper")) return "clipper-output";
  if (command.startsWith("post_")) return "queue-output";
  if (command === "local_ai_status") return "ai-output";
  return "operator-command-output";
}

async function runCommand(button) {
  const command = button.dataset.command;
  const output = button.dataset.output || outputFor(command);
  if (!CLIENT_COMMAND_IDS.has(command) || !state.availableCommands.has(command)) {
    text(output, "BLOCKED: command ID is not allowlisted by this app and backend.");
    return;
  }
  if (command === "agent_stop") {
    button.disabled = true;
    await stopAgent();
    button.disabled = false;
    return;
  }
  const isAgentAction = command.startsWith("agent_");
  button.disabled = true;
  if (isAgentAction) setAgentState("working", `Running fixed local action: ${command}.`);
  text(output, `Running ${command}...`);
  try {
    const result = await api(`/api/run/${command}`, { method: "POST" });
    text(output, JSON.stringify(result, null, 2));
    const payload = result.json || result;
    if (isAgentAction && (payload.reply || payload.plan || payload.executed_actions)) {
      const rendered = renderAgentResult(payload);
      appendChatMessage("ghoti", rendered.reply);
    }
    await refreshAll();
    if (/^(orchestration_|paperclip_|ruflo_)/.test(command)) {
      await loadOrchestrationCapabilities(true);
    }
    if (command.startsWith("desktop_")) {
      await loadDesktopOperatorCapabilities();
    }
    if (command === "ghoti_full_status" || command === "blocked_live_test") {
      await loadComputerCapabilities();
    }
    if (isAgentAction) {
      await loadAgentCapabilities();
      setAgentState("done");
    }
  } catch (error) {
    text(output, `BLOCKED or failed: ${error.message}`);
    if (isAgentAction) setAgentState("error", `Action stopped safely: ${error.message}`);
  } finally {
    button.disabled = false;
  }
}

document.querySelectorAll(".tab").forEach(button => button.addEventListener("click", () =>
  activateView(button.dataset.view, button)));
document.querySelectorAll(".command").forEach(button => button.addEventListener("click", () => runCommand(button)));
document.querySelectorAll(".os-command").forEach(button => button.addEventListener("click", () => runGhotiOsCommand(button)));
document.querySelectorAll(".agent-intent").forEach(button => button.addEventListener("click", () => prepareAgentIntent(button)));
document.querySelectorAll("[data-computer-use-command]").forEach(button => button.addEventListener("click", () => runComputerUseControl(button)));
document.querySelectorAll(".sidebar-context-item").forEach(button => button.addEventListener("click", () => openView(button.dataset.viewTarget)));
document.addEventListener("click", event => {
  const button = event.target.closest(".copy");
  if (!button) return;
  const value = button.dataset.copy || "";
  const restore = button.textContent;
  const done = () => { button.textContent = "Copied"; setTimeout(() => { button.textContent = restore; }, 1200); };
  if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(value).then(done).catch(() => {});
  else done();
});
renderSites();
renderConnectorSetup();
renderRoutines();
renderDailyQuests();
renderTools();
renderObsidian();
renderEvolveProposals();
renderEvolveQueue();
renderDesktopOperator();
document.getElementById("refresh").addEventListener("click", async () => {
  await refreshAll();
  await loadUnifiedToolStatus();
  await loadGhotiOsStatus();
});
document.querySelectorAll(".open-view").forEach(button => button.addEventListener("click", () => openView(button.dataset.openView)));
document.getElementById("operator-command-form").addEventListener("submit", async event => {
  event.preventDefault();
  const input = document.getElementById("operator-command-input");
  const message = input.value.trim();
  if (!message) return;
  input.value = "";
  await sendAgentMessage(message, "home");
});
document.querySelectorAll(".intent-example").forEach(button => button.addEventListener("click", async () => {
  await sendAgentMessage(button.dataset.intent, "home");
}));
document.querySelectorAll(".tool-chip").forEach(button => button.addEventListener("click", () =>
  openToolDestination(button)));
document.getElementById("os-memory-search-form").addEventListener("submit", event => {
  event.preventDefault();
  state.osMemoryQuery = document.getElementById("os-memory-query").value;
  renderOsMemory();
});
document.getElementById("operator-command-input").addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    document.getElementById("operator-command-form").requestSubmit();
  }
});
document.addEventListener("keydown", event => {
  if (event.ctrlKey && !event.altKey && !event.metaKey && (event.code === "Digit8" || event.key === "8")) {
    event.preventDefault();
    void stopAgent({ source: "ctrl8" });
  }
});
document.getElementById("new-agent-session").addEventListener("click", startNewSession);
document.getElementById("refresh-desktop-status").addEventListener("click", loadDesktopOperatorCapabilities);
document.querySelectorAll(".system-filter").forEach(button => button.addEventListener("click", () =>
  renderSystemMap(button.dataset.filter)));
document.getElementById("agent-voice-input").addEventListener("click", () => startVoiceInput("operator-command-input"));
document.getElementById("agent-read-output").addEventListener("click", readLatestGhotiReply);
document.getElementById("agent-stop").addEventListener("click", stopAgent);
document.getElementById("agent-model-provider").addEventListener("change", renderModelProviderStatus);
document.getElementById("agent-model-choice").addEventListener("change", renderModelProviderStatus);
document.getElementById("agent-stop-top").addEventListener("click", stopAgent);
document.getElementById("computer-use-panel-close").addEventListener("click", hideComputerUsePanel);
document.getElementById("agent-confirm").addEventListener("click", () => resolveAgentConfirmation(true));
document.getElementById("agent-cancel").addEventListener("click", () => resolveAgentConfirmation(false));
document.getElementById("obsidian-tool-update").addEventListener("click", () =>
  runFixedToolCommand(["obsidian_update_status"], "obsidian-tool-output"));
document.getElementById("obsidian-tool-open").addEventListener("click", () =>
  runFixedToolCommand(["obsidian_open_live_status"], "obsidian-tool-output", false));
document.getElementById("github-tool-check").addEventListener("click", () =>
  runFixedToolCommand(["github_sync_status", "github_local_summary"], "github-tool-output"));
document.getElementById("github-tool-push").addEventListener("click", async () => {
  if (!state.githubPushSafe) {
    text("github-tool-output", "BLOCKED: backend has not explicitly marked the current branch safe to push.");
    return;
  }
  await runFixedToolCommand(["github_push_current_branch"], "github-tool-output");
});
document.getElementById("full-cu-backend-check").addEventListener("click", () =>
  runOptionalStatus("full_computer_use_status", "computer-output"));
document.getElementById("connector-setup-check").addEventListener("click", () =>
  runOptionalStatus("connector_setup_status", "connector-setup-output"));
document.getElementById("app-update-status-check").addEventListener("click", () =>
  runOptionalStatus("agent_icon_status", "app-support-output"));
document.getElementById("pwa-icon-help-check").addEventListener("click", () =>
  runOptionalStatus("agent_icon_reset_help", "app-support-output"));
document.getElementById("home-agent-icon-status").addEventListener("click", () =>
  runOptionalStatus("agent_icon_status", "home-icon-output"));
document.getElementById("home-agent-icon-help").addEventListener("click", () =>
  runOptionalStatus("agent_icon_reset_help", "home-icon-output"));
document.getElementById("request-obsidian-live-update").addEventListener("click", () => {
  queueEvolveProposal("obsidian-live-update");
  openView("evolve");
  text("evolve-prompt", "Queued: Live Obsidian status update command. Export the proposal for Claude or Codex; this dashboard does not edit the vault automatically.");
});
document.getElementById("export-evolve-prompt").addEventListener("click", exportEvolvePrompt);
document.getElementById("refresh-evolve-backend").addEventListener("click", loadBackendEvolve);
document.getElementById("propose-dashboard-backend").addEventListener("click", event => proposeDashboardBackend(event.currentTarget));
document.querySelectorAll(".update-app").forEach(button => button.addEventListener("click", () => updateApp(button)));
document.getElementById("pairing-form").addEventListener("submit", async event => {
  event.preventDefault();
  const input = document.getElementById("pairing-input");
  const error = document.getElementById("pairing-error");
  state.pairingValue = input.value.trim();
  input.value = "";
  try {
    const config = await loadMobileConfig();
    if (!config.paired) throw new Error("Pairing value was not accepted.");
    error.textContent = "";
    document.getElementById("pairing-dialog").close();
    const resolvePairing = state.pairingResolve;
    state.pairingPromise = null;
    state.pairingResolve = null;
    if (resolvePairing) resolvePairing();
    else {
      await refreshAll();
      await loadDesktopOperatorCapabilities();
      await loadAgentCapabilities();
      await loadUnifiedToolStatus();
      await loadGhotiOsStatus();
    }
  } catch (problem) {
    state.pairingValue = "";
    error.textContent = problem.message;
  }
});

document.getElementById("pairing-dialog").addEventListener("cancel", event => {
  if (state.pairingPromise || (state.mobile?.pairing_required && !state.mobile?.paired)) {
    event.preventDefault();
  }
});

window.addEventListener("beforeinstallprompt", event => {
  event.preventDefault();
  state.installPrompt = event;
  document.getElementById("install-app").hidden = false;
});

document.getElementById("install-app").addEventListener("click", async () => {
  if (!state.installPrompt) return;
  state.installPrompt.prompt();
  await state.installPrompt.userChoice;
  state.installPrompt = null;
  document.getElementById("install-app").hidden = true;
});

async function bootstrap() {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register(`/service-worker.js?v=${APP_VERSION}`).catch(() => {});
  }
  try {
    text("app-version", APP_VERSION);
    const config = await loadMobileConfig();
    if (config.pairing_required && !config.paired) showPairing();
    else if (config.integrated_runtime) {
      openView("command");
      text("connection-mode", "Deployed local runtime");
      document.querySelectorAll(".command").forEach(button => { button.disabled = true; });
      // Legacy panels describe a different execution surface, disabled in this release.
      document.querySelectorAll('[data-panel="command"] > :not(#integrated-runtime)').forEach(node => { node.style.display = "none"; });
      document.querySelectorAll('[data-view]:not([data-view="command"]), [data-view-target], #new-agent-session').forEach(button => { button.disabled = true; });
      document.querySelectorAll('#agent-stop-top, .emergency-stop-hint, .update-app, #refresh, #install-app').forEach(node => { node.style.display = "none"; });
      document.dispatchEvent(new Event("ghoti-runtime-ready"));
    }
    else {
      await refreshAll();
      await loadDesktopOperatorCapabilities();
      await loadAgentCapabilities();
      await loadUnifiedToolStatus();
      await loadGhotiOsStatus();
    }
    showUpdateResultFromUrl();
  } catch (problem) {
    const notice = document.getElementById("notice");
    notice.textContent = problem.message;
    notice.hidden = false;
  } finally {
    const loading = document.getElementById("app-loading");
    loading.classList.add("done");
    setTimeout(() => { loading.hidden = true; }, 180);
  }
}

bootstrap();
