const uiState = {
  serverActions: [],
  localActions: [],
  nextLocalActionId: 1,
  selectedArtifactPath: "",
  selectedApprovalId: "",
  selectedTaskId: "",
  controlCenterPayload: null,
  executorTasksPayload: null,
  handoffTargetsPayload: null,
  latestControlCenterSummary: null,
  activeConsoleTab: "dashboard",
};
const HANDOFF_TARGET_PREFERENCES_KEY = "ghoti.handoffTargetPreferences.v1";
const CONSOLE_TAB_STORAGE_KEY = "ghoti.consoleActiveTab.v1";
const CONSOLE_TABS = ["dashboard", "approvals", "pipeline", "control", "tools", "system"];

const desktopActionTypes = new Set([
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
const recipeActionTypes = new Set([
  "run_operator_recipe",
]);

function isDesktopExecutorAction(actionType) {
  return desktopActionTypes.has(String(actionType || "").toLowerCase());
}

function isRecipeExecutorAction(actionType) {
  return recipeActionTypes.has(String(actionType || "").toLowerCase());
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || data.stderr || `Request failed with ${response.status}`);
  }

  return data;
}

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) {
    element.textContent = value;
  }
}

function setValue(id, value) {
  const element = document.getElementById(id);
  if (element) {
    element.value = value;
  }
}

function loadHandoffTargetPreferences() {
  try {
    const raw = window.localStorage.getItem(HANDOFF_TARGET_PREFERENCES_KEY);
    if (!raw) {
      return {
        rememberSelectedCandidates: false,
        sourceCandidateId: "",
        targetCandidateId: "",
      };
    }

    const parsed = JSON.parse(raw);
    return {
      rememberSelectedCandidates: Boolean(parsed?.rememberSelectedCandidates),
      sourceCandidateId: String(parsed?.sourceCandidateId || ""),
      targetCandidateId: String(parsed?.targetCandidateId || ""),
    };
  } catch (error) {
    return {
      rememberSelectedCandidates: false,
      sourceCandidateId: "",
      targetCandidateId: "",
    };
  }
}

function saveHandoffTargetPreferences(preferences) {
  try {
    window.localStorage.setItem(
      HANDOFF_TARGET_PREFERENCES_KEY,
      JSON.stringify({
        rememberSelectedCandidates: Boolean(preferences?.rememberSelectedCandidates),
        sourceCandidateId: String(preferences?.sourceCandidateId || ""),
        targetCandidateId: String(preferences?.targetCandidateId || ""),
      }),
    );
  } catch (error) {
    // Ignore local storage errors and keep the handoff flow usable.
  }
}

function clearHandoffTargetPreferences() {
  try {
    window.localStorage.removeItem(HANDOFF_TARGET_PREFERENCES_KEY);
  } catch (error) {
    // Ignore local storage errors and keep the handoff flow usable.
  }
}

function setSelectOptions(id, options, preferredValue = "") {
  const element = document.getElementById(id);
  if (!element) {
    return;
  }

  const currentValue = preferredValue || String(element.value || "");
  element.innerHTML = options
    .map((item) => `<option value="${escapeHtml(item.value)}">${escapeHtml(item.label)}</option>`)
    .join("");

  const hasPreferredValue = options.some((item) => item.value === currentValue);
  element.value = hasPreferredValue ? currentValue : (options[0]?.value || "");
}

function getInputValue(id) {
  const element = document.getElementById(id);
  return element ? String(element.value || "").trim() : "";
}

function isChecked(id) {
  const element = document.getElementById(id);
  return Boolean(element?.checked);
}

function shouldRememberHandoffTargetSelections() {
  return isChecked("handoff-remember-targets");
}

function persistHandoffTargetPreferences() {
  if (!shouldRememberHandoffTargetSelections()) {
    clearHandoffTargetPreferences();
    return;
  }

  saveHandoffTargetPreferences({
    rememberSelectedCandidates: true,
    sourceCandidateId: getInputValue("handoff-source-candidate"),
    targetCandidateId: getInputValue("handoff-target-candidate"),
  });
}

function updateHandoffTargetPreferenceNote(options = {}) {
  if (!shouldRememberHandoffTargetSelections()) {
    setText(
      "handoff-target-memory-note",
      "Remembered target picks are off. Ghoti will use only the current visible selector values.",
    );
    return;
  }

  const restored = [];
  const cleared = [];
  if (options.restoredSource) {
    restored.push("Codex");
  }
  if (options.restoredTarget) {
    restored.push("ChatGPT");
  }
  if (options.clearedSource) {
    cleared.push("Codex");
  }
  if (options.clearedTarget) {
    cleared.push("ChatGPT");
  }

  let message = "Remembered target picks are on for this browser.";
  if (restored.length > 0) {
    message += ` Restored ${restored.join(" and ")} candidate selection.`;
  }
  if (cleared.length > 0) {
    message += ` Cleared stale ${cleared.join(" and ")} candidate selection because the exact window is no longer visible.`;
  }
  setText("handoff-target-memory-note", message);
}

function getPreferredCandidateValue(selectId, options, rememberedValue = "") {
  const currentValue = getInputValue(selectId);
  const availableValues = new Set(options.map((item) => item.value));
  if (currentValue && availableValues.has(currentValue)) {
    return currentValue;
  }
  if (rememberedValue && availableValues.has(rememberedValue)) {
    return rememberedValue;
  }
  return "";
}

function buildHotkeyTarget() {
  const windowAlias = getInputValue("desktop-hotkey-window");
  const hotkey = getInputValue("desktop-hotkey-value");
  return windowAlias ? `${windowAlias}|${hotkey}` : hotkey;
}

function buildMouseTarget() {
  const windowAlias = getInputValue("desktop-mouse-window");
  const mode = getInputValue("desktop-mouse-mode");
  if (mode === "coordinates") {
    const x = getInputValue("desktop-mouse-x");
    const y = getInputValue("desktop-mouse-y");
    const coordinates = `${x},${y}`;
    return windowAlias ? `${windowAlias}|${coordinates}` : coordinates;
  }
  return windowAlias ? `${windowAlias}|center` : "terminal|center";
}

function buildScrollTarget() {
  const windowAlias = getInputValue("desktop-mouse-window");
  const delta = getInputValue("desktop-scroll-delta");
  return windowAlias ? `${windowAlias}|${delta}` : delta;
}

function buildRecipeQueuePayload(recipeName, options = {}) {
  const payload = {
    actionType: "run_operator_recipe",
    target: recipeName,
  };
  if (Object.keys(options).length > 0) {
    payload.content = JSON.stringify(options);
  }
  return payload;
}

function buildCodexChatGptHandoffOptions() {
  const options = {
    sourceWindow: getInputValue("handoff-source-window") || "codex",
    targetWindow: getInputValue("handoff-target-window") || "chatgpt",
    waitSeconds: Number.parseInt(getInputValue("handoff-wait-seconds") || "1", 10) || 1,
    usePreparedClipboard: isChecked("handoff-use-prepared-clipboard"),
    allowSend: isChecked("handoff-allow-send"),
  };
  const sourceCandidateId = getInputValue("handoff-source-candidate");
  const targetCandidateId = getInputValue("handoff-target-candidate");
  if (sourceCandidateId) {
    options.sourceWindowCandidateId = sourceCandidateId;
  }
  if (targetCandidateId) {
    options.targetWindowCandidateId = targetCandidateId;
  }
  return options;
}

function formatHandoffCandidateLabel(item) {
  const bits = [item.title || item.candidateId || "Visible window"];
  if (item.candidateId) {
    bits.push(item.candidateId);
  }
  if (item.isActive) {
    bits.push("active");
  }
  if (item.isFixture) {
    bits.push("fixture");
  }
  return bits.join(" | ");
}

function renderHandoffTargetCandidates(payload) {
  uiState.handoffTargetsPayload = payload;
  const summary = payload?.summary || {};
  const codexCandidates = Array.isArray(summary.codexCandidates) ? summary.codexCandidates : [];
  const chatgptCandidates = Array.isArray(summary.chatgptCandidates) ? summary.chatgptCandidates : [];
  const currentSourceValue = getInputValue("handoff-source-candidate");
  const currentTargetValue = getInputValue("handoff-target-candidate");
  const sourceOptions = [{ value: "", label: "Auto match" }].concat(
    codexCandidates.map((item) => ({
      value: item.candidateId || "",
      label: formatHandoffCandidateLabel(item),
    })),
  );
  const targetOptions = [{ value: "", label: "Auto match" }].concat(
    chatgptCandidates.map((item) => ({
      value: item.candidateId || "",
      label: formatHandoffCandidateLabel(item),
    })),
  );

  const preferences = loadHandoffTargetPreferences();
  const sourceCandidateAvailable = Boolean(
    preferences.sourceCandidateId && sourceOptions.some((item) => item.value === preferences.sourceCandidateId),
  );
  const targetCandidateAvailable = Boolean(
    preferences.targetCandidateId && targetOptions.some((item) => item.value === preferences.targetCandidateId),
  );
  const sourcePreferredValue = getPreferredCandidateValue(
    "handoff-source-candidate",
    sourceOptions,
    preferences.rememberSelectedCandidates ? preferences.sourceCandidateId : "",
  );
  const targetPreferredValue = getPreferredCandidateValue(
    "handoff-target-candidate",
    targetOptions,
    preferences.rememberSelectedCandidates ? preferences.targetCandidateId : "",
  );

  setSelectOptions("handoff-source-candidate", sourceOptions, sourcePreferredValue);
  setSelectOptions("handoff-target-candidate", targetOptions, targetPreferredValue);
  if (preferences.rememberSelectedCandidates) {
    persistHandoffTargetPreferences();
  }
  updateHandoffTargetPreferenceNote({
    restoredSource:
      preferences.rememberSelectedCandidates
      && Boolean(preferences.sourceCandidateId)
      && sourcePreferredValue === preferences.sourceCandidateId
      && currentSourceValue !== preferences.sourceCandidateId,
    restoredTarget:
      preferences.rememberSelectedCandidates
      && Boolean(preferences.targetCandidateId)
      && targetPreferredValue === preferences.targetCandidateId
      && currentTargetValue !== preferences.targetCandidateId,
    clearedSource: preferences.rememberSelectedCandidates && Boolean(preferences.sourceCandidateId) && !sourceCandidateAvailable,
    clearedTarget: preferences.rememberSelectedCandidates && Boolean(preferences.targetCandidateId) && !targetCandidateAvailable,
  });
  setText(
    "handoff-target-summary",
    summary.headline || "Visible Codex and ChatGPT window candidates are ready for manual selection.",
  );
}

function renderRaw(id, payload) {
  const element = document.getElementById(id);
  if (element) {
    element.textContent = JSON.stringify(payload, null, 2);
  }
}

function normalizeState(status) {
  if (!status) {
    return "neutral";
  }

  const value = String(status).toLowerCase();
  if (["ok", "success", "available", "ready", "yes", "approved", "completed", "succeeded", "ready_to_resume"].includes(value)) {
    return "success";
  }
  if (["blocked", "error", "fail", "failed", "denied", "rejected", "interrupted", "resource_guard_triggered", "blocked_human_needed", "manual_intervention_required", "attention_needed"].includes(value)) {
    return "error";
  }
  if (["pending", "loading", "running", "not_run", "deferred", "waiting", "active", "approval_needed", "queued", "pending_approval", "active_watch"].includes(value)) {
    return "loading";
  }
  return "neutral";
}

const actionableTaskStatuses = new Set([
  "queued",
  "running",
  "waiting",
  "pending_approval",
  "blocked_human_needed",
  "interrupted",
  "ready_to_resume",
  "failed",
]);

function getTaskVisibilityFilter() {
  return document.getElementById("task-visibility-filter")?.value || "actionable";
}

function getTaskRecencyLimit() {
  const value = document.getElementById("task-recency-filter")?.value || "12";
  if (value === "all") {
    return Number.POSITIVE_INFINITY;
  }
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 12;
}

function getGhotiControlCenterFilters() {
  return {
    visibility: document.getElementById("ghoti-task-visibility-filter")?.value || "actionable",
    taskType: document.getElementById("ghoti-task-type-filter")?.value || "all",
    taskStatus: document.getElementById("ghoti-task-status-filter")?.value || "all",
    activeOnly: Boolean(document.getElementById("ghoti-task-active-only")?.checked),
    limit: document.getElementById("ghoti-task-limit-filter")?.value || "6",
  };
}

function readStoredConsoleTab() {
  try {
    const raw = window.localStorage.getItem(CONSOLE_TAB_STORAGE_KEY);
    return CONSOLE_TABS.includes(raw) ? raw : "";
  } catch (_error) {
    return "";
  }
}

function storeConsoleTab(tabName) {
  try {
    window.localStorage.setItem(CONSOLE_TAB_STORAGE_KEY, tabName);
  } catch (_error) {
    // Ignore localStorage write failures.
  }
}

function setActiveConsoleTab(tabName, options = {}) {
  const nextTab = CONSOLE_TABS.includes(tabName) ? tabName : "dashboard";
  uiState.activeConsoleTab = nextTab;

  document.querySelectorAll('.tab-btn[data-tab]').forEach((button) => {
    const isActive = button.dataset.tab === nextTab;
    button.classList.toggle('tab-active', isActive);
    button.setAttribute('aria-selected', isActive ? 'true' : 'false');
    button.tabIndex = isActive ? 0 : -1;
  });

  document.querySelectorAll('[data-tab-panel]').forEach((panel) => {
    const isActive = panel.dataset.tabPanel === nextTab;
    panel.hidden = !isActive;
    panel.setAttribute('aria-hidden', isActive ? 'false' : 'true');
  });

  if (options.persist !== false) {
    storeConsoleTab(nextTab);
  }
}

function initConsoleTabs() {
  const buttons = Array.from(document.querySelectorAll('.tab-btn[data-tab]'));
  if (!buttons.length) {
    return;
  }

  buttons.forEach((button, index) => {
    button.addEventListener('click', () => {
      setActiveConsoleTab(button.dataset.tab || 'dashboard');
    });

    button.addEventListener('keydown', (event) => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) {
        return;
      }
      event.preventDefault();
      let nextIndex = index;
      if (event.key === 'ArrowRight') {
        nextIndex = (index + 1) % buttons.length;
      } else if (event.key === 'ArrowLeft') {
        nextIndex = (index - 1 + buttons.length) % buttons.length;
      } else if (event.key === 'Home') {
        nextIndex = 0;
      } else if (event.key === 'End') {
        nextIndex = buttons.length - 1;
      }
      const nextButton = buttons[nextIndex];
      if (nextButton) {
        setActiveConsoleTab(nextButton.dataset.tab || 'dashboard');
        nextButton.focus();
      }
    });
  });

  const initialTab = readStoredConsoleTab()
    || buttons.find((button) => button.classList.contains('tab-active'))?.dataset.tab
    || 'dashboard';
  setActiveConsoleTab(initialTab, { persist: false });
}

function scrollToElement(targetId) {
  const element = document.getElementById(targetId);
  if (!element) {
    return;
  }

  const panel = element.closest('[data-tab-panel]');
  if (panel?.dataset?.tabPanel) {
    setActiveConsoleTab(panel.dataset.tabPanel);
  }

  let parent = element.parentElement;
  while (parent) {
    if (parent.tagName === 'DETAILS') {
      parent.open = true;
    }
    parent = parent.parentElement;
  }

  window.requestAnimationFrame(() => {
    element.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    });
  });
}

function applyTaskListFilters(items) {
  const allItems = Array.isArray(items) ? items : [];
  const visibility = getTaskVisibilityFilter();
  const recencyLimit = getTaskRecencyLimit();
  const actionableItems = visibility === "actionable"
    ? allItems.filter((item) => actionableTaskStatuses.has(String(item.status || "").toLowerCase()))
    : allItems;
  const visibleItems = Number.isFinite(recencyLimit)
    ? actionableItems.slice(0, recencyLimit)
    : actionableItems;

  return {
    items: visibleItems,
    totalCount: allItems.length,
    actionableCount: actionableItems.length,
    visibility,
    recencyLimit,
  };
}

function buildTaskFilterNotice(label, filtered) {
  if (!filtered.totalCount) {
    return "";
  }

  const limitText = Number.isFinite(filtered.recencyLimit)
    ? `${filtered.items.length} of ${filtered.actionableCount}`
    : `${filtered.items.length}`;
  const scopeText = filtered.visibility === "actionable"
    ? "actionable task(s)"
    : "task(s)";
  const hiddenCount = filtered.totalCount - filtered.items.length;
  const hiddenText = hiddenCount > 0
    ? ` ${hiddenCount} older or completed ${label.toLowerCase()} item(s) are hidden by the current filter.`
    : "";
  return `<p class="list-filter-note">Showing ${limitText} recent ${scopeText} in ${escapeHtml(label)}.${hiddenText}</p>`;
}

function rerenderTaskListsFromState() {
  if (!uiState.executorTasksPayload) {
    return;
  }
  renderExecutorTaskCards(uiState.executorTasksPayload);
  renderRecipeTaskCards(uiState.executorTasksPayload);
  renderDesktopTaskCards(uiState.executorTasksPayload);
}

function renderGhotiState(summary = {}) {
  const stateValue = summary.ghotiState || "idle";
  const normalized = normalizeState(stateValue);
  const reason = summary.ghotiReason && summary.ghotiReason !== "none"
    ? summary.ghotiReason
    : "No active guard or interruption reason right now.";
  const nextStep = summary.operatorNextStep && summary.operatorNextStep !== "none"
    ? summary.operatorNextStep
    : "Queue or review a local task when you want Ghoti to act.";
  const events = summary.resourceGuardEvents || [];
  const eventCount = summary.resourceGuardEventCount ?? events.length ?? 0;

  setText("ghoti-state-label", stateValue.replaceAll("_", " "));
  setText("ghoti-state-reason", reason);
  setText("ghoti-next-step", nextStep);
  setText("ghoti-resource-guard-count", String(eventCount));
  setText("ghoti-indicator-state", stateValue.replaceAll("_", " "));
  setText("ghoti-indicator-note", reason);

  const pill = document.getElementById("ghoti-state-pill");
  if (pill) {
    pill.className = `state-pill state-${normalized}`;
    pill.textContent = stateValue.replaceAll("_", " ");
  }

  const indicator = document.getElementById("ghoti-state-indicator");
  if (indicator) {
    indicator.className = `ghoti-state-indicator is-${normalized}`;
  }

  const panel = document.getElementById("ghoti-state-panel");
  if (panel) {
    panel.className = `ghoti-state-panel ghoti-state-${normalized}`;
  }

  const list = document.getElementById("ghoti-resource-guard-list");
  if (list) {
    list.innerHTML = events.length
      ? events.map((item) => `<article class="log-item"><p>${escapeHtml(item)}</p></article>`).join("")
      : "<p class=\"empty-state\">No recent resource guard events.</p>";
  }
}

function renderGhotiOverlay(summary = {}) {
  const watchdog = summary.watchdog || {};
  const overlayTarget = summary.overlayTarget || watchdog.overlayTarget || {};
  const normalized = normalizeState(watchdog.status || summary.ghotiState || "neutral");
  const alertCount = Array.isArray(watchdog.alerts) ? watchdog.alerts.length : 0;
  const watchdogState = String(watchdog.status || "watching").replaceAll("_", " ");

  const pill = document.getElementById("ghoti-overlay-watchdog-pill");
  if (pill) {
    pill.className = `state-pill state-${normalized}`;
    pill.textContent = watchdogState;
  }

  setText("ghoti-overlay-watchdog-count", `${alertCount} ${alertCount === 1 ? "alert" : "alerts"}`);
  setText(
    "ghoti-overlay-watchdog-summary",
    watchdog.headline || summary.ghotiReason || "No operator watchdog alerts are visible yet.",
  );
  setText("ghoti-overlay-target-label", overlayTarget.label || "No visible target");
  setText(
    "ghoti-overlay-target-detail",
    overlayTarget.detail || "Queue or inspect one narrow task to show Ghoti's next local target.",
  );
  setText(
    "ghoti-overlay-hotkey",
    watchdog.handoffHint || "Ctrl+8 stops the active desktop action or operator recipe immediately.",
  );

  const marker = document.getElementById("ghoti-target-marker");
  if (marker) {
    marker.className = `ghoti-target-marker is-${normalized}`;
  }
  setText("ghoti-target-marker-label", overlayTarget.label || "No visible target");
  setText(
    "ghoti-target-marker-detail",
    overlayTarget.detail || "Ghoti is idle until you queue or inspect a narrow local task.",
  );
}

function renderGhotiWatchdog(summary = {}) {
  const watchdog = summary.watchdog || {};
  setText("ghoti-watchdog-state", String(watchdog.status || "watching").replaceAll("_", " "));
  setText("ghoti-watchdog-wrong-window", String(watchdog.wrongWindowBlockCount ?? 0));
  setText("ghoti-watchdog-stalled", String(watchdog.stalledTaskCount ?? 0));
  setText("ghoti-watchdog-did-not-complete", String(watchdog.didNotCompleteCount ?? 0));
  setText(
    "ghoti-watchdog-headline",
    watchdog.headline || "No operator watchdog summary is available yet.",
  );
  renderStatusList("ghoti-watchdog-alerts", watchdog.alerts || []);
  setText(
    "ghoti-watchdog-handoff-hint",
    watchdog.handoffHint || "Handoff safety hints will appear here when relevant.",
  );
}

function renderGhotiControlTaskList(containerId, items, emptyText, inspectLabel = "Inspect Task") {
  const container = document.getElementById(containerId);
  if (!container) {
    return;
  }

  if (!items || items.length === 0) {
    container.innerHTML = `<p class="empty-state">${escapeHtml(emptyText)}</p>`;
    return;
  }

  container.innerHTML = items
    .map((item) => {
      const state = normalizeState(item.status);
      const isSelected = item.taskId && item.taskId === uiState.selectedTaskId;
      const detailText = [
        item.taskTypeLabel ? `Type: ${item.taskTypeLabel}` : "",
        item.detail && item.detail !== "not_run" ? item.detail : "",
        item.nextAction ? `Next: ${item.nextAction}` : "",
      ].filter(Boolean).join(" | ");
      return `
        <article class="approval-item ${isSelected ? "is-selected" : ""}">
          <div class="approval-topline">
            <strong>${escapeHtml(item.headline || item.taskId || "task")}</strong>
            <span class="state-pill state-${state}">${escapeHtml(item.status || state)}</span>
          </div>
          <div class="approval-summary-grid">
            <p><span>Task</span><strong>${escapeHtml(item.taskId || "none")}</strong></p>
            <p><span>Type</span><strong>${escapeHtml(item.taskTypeLabel || item.taskType || "task")}</strong></p>
            <p><span>Approval</span><strong>${escapeHtml(item.approvalState || "unknown")}</strong></p>
            <p><span>Updated</span><strong>${escapeHtml(item.updatedAt ? formatTimeStamp(item.updatedAt) : "unknown")}</strong></p>
          </div>
          <p class="approval-description"><span>Detail</span>${escapeHtml(detailText || "No recent detail recorded.")}</p>
          <div class="approval-actions">
            <button
              class="button-secondary task-action-button"
              type="button"
              data-task-action="inspect"
              data-task-id="${escapeHtml(item.taskId || "")}"
            >
              ${isSelected ? "Viewing Task" : inspectLabel}
            </button>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderGhotiControlCenter(payload) {
  uiState.controlCenterPayload = payload;
  const summary = payload.summary || {};
  const currentTask = summary.currentTask || null;
  const actionableTasks = summary.recentActionableTasks || [];
  const recentFailures = summary.recentFailures || [];
  const brain = summary.brain || {};
  const specialistRole = summary.specialistRole || {};
  const browser = summary.browser || {};
  const memory = summary.memory || {};
  const relay = summary.relay || {};
  const desktopTruth = summary.desktopActionTruth || {};

  renderGhotiOverlay(summary);
  renderGhotiWatchdog(summary);

  setText("ghoti-control-state", String(summary.ghotiState || "idle").replaceAll("_", " "));
  setText("ghoti-control-reason", summary.ghotiReason || "No current state reason reported.");
  setText("ghoti-control-hotkey", summary.emergencyStopHotkey || "Ctrl+8");
  setText(
    "ghoti-control-hotkey-note",
    "Ctrl+8 stops the current desktop action or operator recipe, marks it interrupted, and requires operator review before any re-queue.",
  );
  setText(
    "ghoti-control-current-task",
    currentTask
      ? `${currentTask.taskId} | ${currentTask.taskTypeLabel || currentTask.taskType || "task"}`
      : "No running task right now.",
  );
  setText(
    "ghoti-control-current-task-note",
    currentTask
      ? [
          currentTask.headline || currentTask.taskId,
          currentTask.detail || currentTask.nextAction || "Inspect the task detail.",
          `desktop_action=${currentTask.desktopAction || desktopTruth.currentAction || "none"}`,
          `desktop_target=${currentTask.desktopTarget || desktopTruth.currentTarget || "none"}`,
          `typing_enabled=${currentTask.typingEnabled || desktopTruth.typingEnabled || "no"}`,
          `desktop_status=${currentTask.desktopStatus || desktopTruth.lastStatus || "not_run"}`,
          `cue_status=${currentTask.cueStatus || desktopTruth.cueStatus || "not_reported"}`,
          `specialist_role=${currentTask.specialistRole || specialistRole.currentRoleId || "supervisor"}`,
        ].join(" | ")
      : "Ghoti is not currently running a task. Queue a narrow local action when you are ready.",
  );

  setText("ghoti-brain-provider", brain.activeProvider || "unknown");
  setText("ghoti-brain-model", brain.activeModel || "none");
  setText("ghoti-brain-ready", brain.inferenceReady ? "yes" : "no");
  setText("ghoti-brain-current-task-use", brain.currentTaskUsedModelInference ? "yes" : "no");
  setText("ghoti-brain-last-call", brain.lastModelCallStatus || "never_called");
  setText(
    "ghoti-brain-current-task-detail",
    currentTask
      ? [
          brain.currentTaskUsedModelInference ? "Current task used model inference." : "Current task is using local rules only right now.",
          `provider=${brain.currentTaskModelProvider || "none"}`,
          `model=${brain.currentTaskModelName || "none"}`,
          `status=${brain.currentTaskModelCallStatus || "not_used"}`,
        ].join(" | ")
      : "No active task is currently claiming model inference.",
  );
  setText(
    "ghoti-brain-note",
    [
      `${brain.activeProvider || "unknown"} / ${brain.activeModel || "none"}`,
      brain.inferenceReady
        ? `ready via ${brain.liveCallPath || "configured local call path"}`
        : `not ready yet via ${brain.liveCallPath || "configured local call path"}`,
      `last=${brain.lastModelCallStatus || "never_called"}`,
    ].join(" | "),
  );

  setText("ghoti-role-current", specialistRole.currentRoleId || "supervisor");
  setText("ghoti-role-provider", specialistRole.currentRoleProvider || "none");
  setText("ghoti-role-sensitivity", specialistRole.currentRoleSensitivity || "unknown");
  setText("ghoti-role-count", String(specialistRole.registryCount ?? 0));
  setText(
    "ghoti-role-note",
    [
      specialistRole.currentRolePurpose || "No current specialist-role purpose was reported.",
      `reason=${specialistRole.currentRoleReason || "none"}`,
    ].join(" | "),
  );

  setText("ghoti-browser-use-installed", browser.browserUseInstalled ? "yes" : "no");
  setText("ghoti-browser-use-ready", browser.browserUseReady ? "yes" : "no");
  setText("ghoti-playwright-ready", browser.playwrightReady ? "yes" : "no");
  setText("ghoti-browser-role", browser.currentBrowserRole || "none");
  setText("ghoti-browser-action", browser.currentBrowserAction || "none");
  setText(
    "ghoti-browser-note",
    [
      `browser_use=${browser.browserUseVersion || "none"}`,
      `playwright=${browser.playwrightVersion || "none"}`,
      `session_support=${browser.browserSessionSupport || "not_available"}`,
      `task_support=${browser.browserTaskSupport || "not_available"}`,
    ].join(" | "),
  );

  setText("ghoti-relay-state", relay.relayState || "idle");
  setText("ghoti-relay-step", relay.currentStep || "idle");
  setText("ghoti-relay-source", relay.sourceTargetAlias || "chatgpt");
  setText("ghoti-relay-destination", relay.destinationTargetAlias || "codex");
  setText("ghoti-relay-preset", `${relay.codexModePreset || "Implementing new feature"} | ${relay.codexReasoningPreset || "Medium"}`);
  setText("ghoti-relay-status", relay.codexExecutionStatus || "unknown");
  setText("ghoti-relay-reset", relay.nextUsageResetAt || "none");
  setText("ghoti-relay-note", [
    `source_status=${relay.sourceTargetStatus || "not_bound"}`,
    `destination_status=${relay.destinationTargetStatus || "not_bound"}`,
    `preset_status=${relay.presetApplicationStatus || "stored_only"}`,
    `payload=${relay.lastPayloadPreview || "none"}`,
    `result=${relay.lastResultPreview || "none"}`,
    `blocked=${relay.blockedReason || "none"}`,
  ].join(" | "));

  setText("ghoti-memory-ready", memory.ready ? "yes" : "no");
  setText("ghoti-memory-markdown-ready", memory.obsidianMarkdownReady ? "yes" : "no");
  setText("ghoti-memory-file-count", String(memory.fileCount ?? 0));
  setText(
    "ghoti-memory-note",
    [
      memory.root || "No compact-memory root reported.",
      `newest=${memory.newestModifiedAt || "none"}`,
    ].join(" | "),
  );

  setText("ghoti-control-pending", String(summary.pendingApprovalCount ?? 0));
  setText("ghoti-control-blocked", String(summary.blockedTaskCount ?? 0));
  setText("ghoti-control-actionable", String(summary.recentActionableCount ?? actionableTasks.length));
  setText("ghoti-control-failures", String(summary.recentFailureCount ?? recentFailures.length));
  setText("ghoti-control-capabilities", String(summary.availableCapabilitiesCount ?? 0));
  setText("ghoti-control-artifacts", String(summary.recentArtifactCount ?? 0));
  setText(
    "ghoti-control-filter-note",
    [
      summary.filters?.visibility === "all" ? "Showing all task statuses." : "Completed tasks stay hidden by default.",
      summary.filters?.activeOnly ? "Active-only filter is on." : "Recent actionable tasks are shown by default.",
      summary.watchdog?.attentionRequired ? "Watchdog alerts are visible below." : "No watchdog alert is currently forcing manual attention.",
      `Limit: ${summary.filters?.limit || 6}.`,
    ].join(" "),
  );
  setText(
    "ghoti-control-next-step-copy",
    summary.operatorNextStep || "Review the next local step from the control center.",
  );
  setText("ghoti-control-no-delete-note", summary.noDeletionPolicy || "No deletion policy summary available.");

  renderGhotiControlTaskList(
    "ghoti-actionable-task-list",
    actionableTasks,
    "No recent actionable tasks match the current Ghoti control-center filter.",
    "Inspect Actionable Task",
  );
  renderGhotiControlTaskList(
    "ghoti-failure-task-list",
    recentFailures,
    "No recent failures are visible in the current executor task history.",
    "Inspect Failure",
  );
  renderStatusList("ghoti-watchdog-alerts", summary.watchdog?.alerts || []);
  renderStatusList("ghoti-brain-notes", brain.notes || []);
  renderStatusList("ghoti-role-roles", specialistRole.roles || []);
  renderStatusList("ghoti-browser-notes", browser.notes || []);
  renderStatusList("ghoti-relay-notes", relay.notes || []);
  renderStatusList("ghoti-memory-notes", memory.notes || []);
  renderStatusList("ghoti-can-do-list", summary.whatGhotiCanDoNow || []);
  renderStatusList("ghoti-next-step-list", summary.whatOperatorShouldDoNext || []);
  renderStatusList("ghoti-cli-command-list", summary.cliCommands || []);
}

function formatTimeStamp(value) {
  if (!value) {
    return "just now";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleString();
}

function localTimeStamp() {
  return new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function createLocalAction(label, summary) {
  const action = {
    id: `local-${uiState.nextLocalActionId++}`,
    label,
    status: "pending",
    summary,
    occurredAt: localTimeStamp(),
    source: "console",
  };

  uiState.localActions = [action, ...uiState.localActions].slice(0, 8);
  renderRecentActionsPanel();
  return action.id;
}

function updateLocalAction(actionId, status, summary) {
  uiState.localActions = uiState.localActions.map((action) =>
    action.id === actionId
      ? {
          ...action,
          status,
          summary,
          occurredAt: localTimeStamp(),
        }
      : action,
  );
  renderRecentActionsPanel();
}

function setResultPanel(targetId, state, headline, detail = "") {
  const element = document.getElementById(targetId);
  if (!element) {
    return;
  }

  const normalizedState = normalizeState(state);
  const detailMarkup = detail ? `<p>${escapeHtml(detail)}</p>` : "";
  element.className = `result-panel is-${normalizedState}`;
  element.innerHTML = `
    <div class="result-topline">
      <strong>${escapeHtml(headline)}</strong>
      <span class="state-pill state-${normalizedState}">${escapeHtml(normalizedState)}</span>
    </div>
    ${detailMarkup}
  `;
}

function withButtonState(button, busyLabel, task) {
  if (!button) {
    return task();
  }

  const originalText = button.textContent;
  const originalDisabled = button.disabled;
  button.disabled = true;
  button.textContent = busyLabel;
  button.classList.add("is-busy");

  return Promise.resolve()
    .then(task)
    .finally(() => {
      button.disabled = originalDisabled;
      button.textContent = originalText;
      button.classList.remove("is-busy");
    });
}

function renderStatusList(id, items) {
  const element = document.getElementById(id);
  if (!element) {
    return;
  }

  element.innerHTML = (items || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
}

function renderOperatorStatus(payload) {
  setText("operator-headline", payload.headline || "Operator status loaded.");
  setText("operator-next-step", payload.nextStep || "No next step reported.");
  renderStatusList("live-now-list", payload.liveNow);
  renderStatusList("scaffold-only-list", payload.scaffoldOnly);
  renderStatusList("not-implemented-list", payload.notImplementedYet);
}

function renderCapabilitySummary(payload) {
  const summary = payload.summary || {};
  const availableCount = summary.availableCount ?? 0;
  const blockedCount = summary.blockedCount ?? 0;

  setText("capability-headline", summary.headline || "Capability summary unavailable.");
  setText("capability-counts", `${availableCount} available / ${blockedCount} blocked`);
  setText("capability-available-count", String(availableCount));
  setText("capability-blocked-count", String(blockedCount));

  const capabilityList = document.getElementById("capability-list");
  const items = summary.capabilities || [];
  if (!capabilityList) {
    return;
  }

  if (items.length === 0) {
    capabilityList.innerHTML = "<p class=\"empty-state\">No capability data returned.</p>";
  } else {
    capabilityList.innerHTML = items
      .map((item) => {
        const state = normalizeState(item.state);
        const blockText =
          item.blockingIssue && item.blockingIssue !== "none"
            ? `Block: ${escapeHtml(item.blockingIssue)}`
            : "Block: none";

        return `
          <article class="capability-item">
            <div class="capability-topline">
              <strong>${escapeHtml(item.capabilityId)}</strong>
              <span class="state-pill state-${state}">${escapeHtml(item.state || state)}</span>
            </div>
            <p>Requires: ${escapeHtml(item.requiredTools || "n/a")}</p>
            <p>${blockText}</p>
          </article>
        `;
      })
      .join("");
  }

  renderRaw("capability-raw", payload);
}

function renderGithubUpdates(payload) {
  const summary = payload.summary || {};
  const clean = summary.clean ? "clean" : "changes present";
  const remoteWrite = summary.remoteWritePossible ? "ready" : "blocked";
  const auth = summary.ghAuthenticated || "unknown";
  const blockedReason = summary.blockingIssue && summary.blockingIssue !== "none" ? summary.blockingIssue : "none";

  setText("github-headline", summary.headline || "GitHub summary unavailable.");
  setText(
    "github-quick-note",
    summary.remoteWritePossible
      ? "Read-only status is live, and approved remote smoke actions are possible."
      : `Read-only status is live. Remote write is blocked: ${blockedReason}.`,
  );
  setText("github-branch", summary.branch || "-");
  setText("github-clean", clean);
  setText("github-remote-write", remoteWrite);
  setText("github-auth", auth);

  const summaryText = [
    `Origin: ${summary.originUrl || "none"}`,
    summary.clean ? "working tree clean" : "local changes present",
    `staged ${summary.stagedChanges ?? 0}`,
    `unstaged ${summary.unstagedChanges ?? 0}`,
    `untracked ${summary.untrackedChanges ?? 0}`,
  ].join(" | ");
  setText("github-summary", summaryText);

  const commitsElement = document.getElementById("github-commits");
  const commits = summary.recentCommits || [];
  if (commitsElement) {
    commitsElement.innerHTML = commits.length
      ? commits.map((item) => `<li>${escapeHtml(item)}</li>`).join("")
      : "<li>No commits reported.</li>";
  }

  renderRaw("github-raw", payload);
}

function renderDesktopBridge(payload) {
  const summary = payload.summary || {};
  setText("desktop-headline", summary.headline || "Desktop bridge summary unavailable.");
  setText(
    "desktop-quick-note",
    summary.desktopControlImplemented
      ? "Desktop control is reported as live."
      : `Narrow desktop-aware actions are available, but arbitrary desktop control is still not implemented. Emergency stop: ${summary.failsafeHotkey || "Ctrl+8"}.`,
  );
  setText("desktop-powershell", summary.powerShellAvailable ? "ready" : "missing");
  setText("desktop-shell", summary.shellCommandCapability ? "ready" : "blocked");
  setText(
    "desktop-launcher",
    summary.launcherCapability === "not_run"
      ? "status only"
      : summary.launcherCapability === "yes"
        ? "ready"
        : "blocked",
  );
  setText("desktop-control", summary.desktopControlImplemented ? "live" : "not yet");
  setText("desktop-failsafe", summary.failsafeHotkey || "Ctrl+8");
  setText(
    "desktop-terminal-windows",
    summary.terminalWindowLimit
      ? `${summary.terminalWindowCount ?? 0}/${summary.terminalWindowLimit}`
      : String(summary.terminalWindowCount ?? 0),
  );
  setText(
    "desktop-powershell-processes",
    summary.terminalProcessLimit
      ? `${summary.powerShellProcessCount ?? 0}/${summary.terminalProcessLimit}`
      : String(summary.powerShellProcessCount ?? 0),
  );
  setText("desktop-node-processes", String(summary.nodeProcessCount ?? 0));
  setText("desktop-python-processes", String(summary.pythonProcessCount ?? 0));
  setText("desktop-ollama", summary.ollamaPresent ? "running" : "not seen");
  setText("desktop-summary", summary.headline || "Desktop bridge status unavailable.");
  const resourceBits = [];
  if (
    Number.isFinite(summary.terminalWindowCount)
    && Number.isFinite(summary.terminalWindowLimit)
    && summary.terminalWindowLimit > 0
    && summary.terminalWindowCount >= summary.terminalWindowLimit
  ) {
    resourceBits.push("Terminal window count is at or above the current soft limit.");
  }
  if (
    Number.isFinite(summary.powerShellProcessCount)
    && Number.isFinite(summary.terminalProcessLimit)
    && summary.terminalProcessLimit > 0
    && summary.powerShellProcessCount >= summary.terminalProcessLimit
  ) {
    resourceBits.push("PowerShell process count is at or above the current soft limit.");
  }
  if (summary.resourceGuardOk) {
    resourceBits.push("Resource guard is ready to stop duplicate terminal spawning.");
  }
  if (summary.clipboardGuardOk) {
    resourceBits.push("Clipboard guard is ready to block checker or recipe labels from landing in the terminal.");
  }
  if (summary.mode === "status" && resourceBits.length === 0) {
    resourceBits.push("Status-only desktop check loaded the current resource picture without running disruptive actions.");
  }
  setText("desktop-resource-summary", resourceBits.join(" ") || "Desktop resource guard details unavailable.");
  renderStatusList("desktop-available-list", summary.availableNow);
  renderStatusList("desktop-missing-list", summary.missingNow);
  renderRaw("desktop-raw", payload);
}

function setApprovalDecisionButtonsDisabled(disabled) {
  ["approval-approve", "approval-deny", "approval-defer"].forEach((id) => {
    const button = document.getElementById(id);
    if (button) {
      button.disabled = disabled;
    }
  });
}

function renderApprovalHistory(items) {
  const element = document.getElementById("approval-history-list");
  if (!element) {
    return;
  }

  if (!items || items.length === 0) {
    element.innerHTML = "<p class=\"empty-state\">No decision history yet for this approval.</p>";
    return;
  }

  element.innerHTML = items
    .map((item) => {
      const state = normalizeState(item.decision);
      const note = item.note && item.note !== "none" ? item.note : "No note recorded.";
      return `
        <article class="approval-history-item">
          <div class="approval-topline">
            <strong>${escapeHtml(item.decision)}</strong>
            <span class="state-pill state-${state}">${escapeHtml(item.decision)}</span>
          </div>
          <p>${escapeHtml(note)}</p>
          <small>${escapeHtml(formatTimeStamp(item.decidedAt))}</small>
        </article>
      `;
    })
    .join("");
}

function renderTaskHistory(items) {
  const element = document.getElementById("task-history-list");
  if (!element) {
    return;
  }

  if (!items || items.length === 0) {
    element.innerHTML = "<p class=\"empty-state\">No task history yet for this item.</p>";
    return;
  }

  element.innerHTML = items
    .map((item) => {
      const state = normalizeState(item.eventType);
      const note = item.note && item.note !== "none" ? item.note : "No note recorded.";
      return `
        <article class="approval-history-item">
          <div class="approval-topline">
            <strong>${escapeHtml(item.eventType)}</strong>
            <span class="state-pill state-${state}">${escapeHtml(item.eventType)}</span>
          </div>
          <p>${escapeHtml(note)}</p>
          <small>${escapeHtml(formatTimeStamp(item.occurredAt))} | ${escapeHtml(item.actor || "system")}</small>
        </article>
      `;
    })
    .join("");
}

function renderExecutionHistory(items) {
  const element = document.getElementById("task-execution-history-list");
  if (!element) {
    return;
  }

  if (!items || items.length === 0) {
    element.innerHTML = "<p class=\"empty-state\">No executor result history yet for this item.</p>";
    return;
  }

  element.innerHTML = items
    .map((item) => {
      const state = normalizeState(item.status);
      const summary = item.summary && item.summary !== "none" ? item.summary : "No execution summary recorded.";
      const artifactLine = item.artifactPath && item.artifactPath !== "none"
        ? `<small>Artifact: ${escapeHtml(item.artifactPath)}</small>`
        : "";
      const reasonLine = item.reason && item.reason !== "none"
        ? `<small>Reason: ${escapeHtml(item.reason)}</small>`
        : "";
      return `
        <article class="approval-history-item">
          <div class="approval-topline">
            <strong>${escapeHtml(item.status)}</strong>
            <span class="state-pill state-${state}">${escapeHtml(item.status)}</span>
          </div>
          <p>${escapeHtml(summary)}</p>
          <small>${escapeHtml(formatTimeStamp(item.startedAt))} -> ${escapeHtml(formatTimeStamp(item.finishedAt))} | ${escapeHtml(item.target || "none")} | attempts=${escapeHtml(String(item.attempts || 1))}</small>
          ${reasonLine}
          ${artifactLine}
        </article>
      `;
    })
    .join("");
}

function renderRecipeStepHistory(items) {
  const element = document.getElementById("task-recipe-step-list");
  if (!element) {
    return;
  }

  if (!items || items.length === 0) {
    element.innerHTML = "<p class=\"empty-state\">No recipe step data loaded yet.</p>";
    return;
  }

  element.innerHTML = items
    .map((item) => {
      const state = normalizeState(item.status);
      const detailBits = [
        item.summary && item.summary !== "none" ? item.summary : "No step summary recorded.",
        item.bridgeTarget && item.bridgeTarget !== "none" ? `Bridge target: ${item.bridgeTarget}` : "",
        item.clipboardPreview && item.clipboardPreview !== "none" ? `Clipboard: ${item.clipboardPreview}` : "",
        item.clipboardClassification && item.clipboardClassification !== "none" ? `Classification: ${item.clipboardClassification}` : "",
        item.windowAlias && item.windowAlias !== "none" ? `Window: ${item.windowAlias}` : "",
        item.windowCandidateId && item.windowCandidateId !== "none" ? `Candidate: ${item.windowCandidateId}` : "",
        item.windowResolutionMode && item.windowResolutionMode !== "none" ? `Resolution: ${item.windowResolutionMode}` : "",
        item.coordinates && item.coordinates !== "none" ? `Coordinates: ${item.coordinates}` : "",
        item.attempts ? `Attempts: ${item.attempts}/${item.maxAttempts || item.attempts}` : "",
        item.required ? `Required: ${item.required}` : "",
      ].filter(Boolean);
      const artifactLine = item.artifactPath && item.artifactPath !== "none"
        ? `<small>Artifact: ${escapeHtml(item.artifactPath)}</small>`
        : "";
      return `
        <article class="approval-history-item">
          <div class="approval-topline">
            <strong>Step ${escapeHtml(String(item.step || "?"))}: ${escapeHtml(item.label || item.actionType || "recipe step")}</strong>
            <span class="state-pill state-${state}">${escapeHtml(item.status || state)}</span>
          </div>
          <p>${escapeHtml(item.actionType || "unknown")} -> ${escapeHtml(item.target || "none")}</p>
          <p>${escapeHtml(detailBits.join(" | "))}</p>
          <small>${escapeHtml(formatTimeStamp(item.startedAt))} -> ${escapeHtml(formatTimeStamp(item.finishedAt))}</small>
          ${artifactLine}
        </article>
      `;
    })
    .join("");
}

function renderRecipeRunHistory(items) {
  const element = document.getElementById("task-recipe-history-list");
  if (!element) {
    return;
  }

  if (!items || items.length === 0) {
    element.innerHTML = "<p class=\"empty-state\">No recipe runs recorded yet.</p>";
    return;
  }

  element.innerHTML = items
    .map((item) => {
      const state = normalizeState(item.status);
      return `
        <article class="approval-history-item">
          <div class="approval-topline">
            <strong>${escapeHtml(item.status || "unknown")}</strong>
            <span class="state-pill state-${state}">${escapeHtml(item.status || state)}</span>
          </div>
          <p>${escapeHtml(item.summary || "No recipe run summary recorded.")}</p>
          <small>${escapeHtml(formatTimeStamp(item.startedAt))} -> ${escapeHtml(formatTimeStamp(item.finishedAt))}</small>
        </article>
      `;
    })
    .join("");
}

function clearApprovalDetail(message) {
  uiState.selectedApprovalId = "";
  setText("approval-detail-id", "-");
  setText("approval-detail-status", "-");
  setText("approval-detail-risk", "-");
  setText("approval-detail-task-id", "-");
  setText("approval-detail-action-label", "-");
  setText("approval-detail-reason", "-");
  setText("approval-detail-scope", "-");
  setText("approval-detail-target-paths", "-");
  setText("approval-detail-workspace-scope", "-");
  setText("approval-detail-workspace-policy", "-");
  setText("approval-detail-workspace-reason", "-");
  setText("approval-detail-allowed-root", "-");
  setText("approval-detail-rollback", "-");
  setText("approval-detail-admin", "-");
  setText("approval-detail-updated-at", "-");
  setText("approval-detail-summary", message);
  setValue("approval-decision-note", "");
  renderApprovalHistory([]);
  renderRaw("approval-detail-raw", { message });
  setResultPanel("approval-action-result", "neutral", "Approval action panel is idle.", "Select a pending approval to inspect it.");
  setApprovalDecisionButtonsDisabled(true);
}

function setTaskActionButtonsDisabled(task = null) {
  const status = String(task?.status || "").toLowerCase();
  const workspaceBlocked = task?.workspacePolicy === "blocked_by_workspace_policy";
  const reviewEnabled = status === "blocked_human_needed" || status === "interrupted";
  const resumeEnabled = status === "waiting";
  const requeueEnabled = status === "ready_to_resume" && !workspaceBlocked;
  const executeEnabled =
    Boolean(task?.executorActionType && task.executorActionType !== "none")
    && status === "queued"
    && !workspaceBlocked
    && ["approved", "not_required"].includes(String(task?.approvalState || "").toLowerCase());

  const buttonStates = {
    "task-review": !reviewEnabled,
    "task-resume": !resumeEnabled,
    "task-requeue": !requeueEnabled,
    "task-execute": !executeEnabled,
  };

  Object.entries(buttonStates).forEach(([id, disabled]) => {
    const button = document.getElementById(id);
    if (button) {
      button.disabled = disabled;
    }
  });
}

function renderApprovalDetail(payload) {
  const summary = payload.summary || {};
  uiState.selectedApprovalId = summary.approvalId || "";
  setText("approval-detail-id", summary.approvalId || "-");
  setText("approval-detail-status", summary.status || "-");
  setText("approval-detail-risk", summary.riskLevel || "-");
  setText("approval-detail-task-id", summary.taskId || "-");
  setText("approval-detail-action-label", summary.actionLabel || "-");
  setText("approval-detail-reason", summary.reason || "-");
  setText("approval-detail-scope", summary.scope || "none");
  setText("approval-detail-target-paths", (summary.targetPaths || []).join(" | ") || "none");
  setText("approval-detail-workspace-scope", summary.workspaceScope || "no_path_detected");
  setText("approval-detail-workspace-policy", summary.workspacePolicy || "allowed");
  setText("approval-detail-workspace-reason", summary.workspaceReason || "none");
  setText("approval-detail-allowed-root", summary.allowedWorkspaceRoot || "unknown");
  setText("approval-detail-rollback", summary.rollbackPlan || "none");
  setText("approval-detail-admin", summary.requiresAdmin ? "yes" : "no");
  setText("approval-detail-updated-at", formatTimeStamp(summary.updatedAt));
  setText("approval-detail-summary", summary.headline || "Approval details loaded.");
  setValue("approval-decision-note", summary.humanNote && summary.humanNote !== "none" ? summary.humanNote : "");
  renderApprovalHistory(summary.decisionHistory || []);
  renderRaw("approval-detail-raw", payload);
  setApprovalDecisionButtonsDisabled(!["pending", "deferred"].includes(String(summary.status || "").toLowerCase()));
}

function clearTaskDetail(message) {
  uiState.selectedTaskId = "";
  const recipePanel = document.getElementById("task-recipe-panel");
  setText("task-detail-id", "-");
  setText("task-detail-status", "-");
  setText("task-detail-risk", "-");
  setText("task-detail-approval-state", "-");
  setText("task-detail-title", "-");
  setText("task-detail-description", "-");
  setText("task-detail-executor-action", "-");
  setText("task-detail-executor-target", "-");
  setText("task-detail-workspace-scope", "-");
  setText("task-detail-workspace-policy", "-");
  setText("task-detail-workspace-reason", "-");
  setText("task-detail-allowed-root", "-");
  setText("task-detail-waiting-for", "-");
  setText("task-detail-blocked-reason", "-");
  setText("task-detail-next-action", "-");
  setText("task-detail-last-note", "-");
  setText("task-detail-retry-limit", "-");
  setText("task-detail-last-attempt-count", "-");
  setText("task-detail-last-execution-status", "-");
  setText("task-detail-last-execution-summary", "-");
  setText("task-detail-last-artifact-path", "-");
  setText("task-detail-last-failure-reason", "-");
  setText("task-detail-last-interruption-reason", "-");
  setText("task-detail-last-resource-guard-reason", "-");
  setText("task-detail-recipe-name", "-");
  setText("task-detail-recipe-status", "-");
  setText("task-detail-recipe-run-count", "-");
  setText("task-detail-recipe-summary", "-");
  setText("task-detail-recipe-last-run", "-");
  setText("task-detail-recipe-source-window", "-");
  setText("task-detail-recipe-target-window", "-");
  setText("task-detail-recipe-clipboard-mode", "-");
  setText("task-detail-recipe-payload-classification", "-");
  setText("task-detail-recipe-payload-preview", "-");
  setText("task-detail-recipe-paste-allowed", "-");
  setText("task-detail-recipe-send-behavior", "-");
  setText("task-detail-recipe-send-allowed", "-");
  setText("task-detail-summary", message);
  setValue("task-action-note", "");
  renderTaskHistory([]);
  renderExecutionHistory([]);
  renderRecipeStepHistory([]);
  renderRecipeRunHistory([]);
  renderRaw("task-detail-raw", { message });
  if (recipePanel) {
    recipePanel.hidden = true;
  }
  setResultPanel("task-action-result", "neutral", "Task action panel is idle.", "Select a stopped task to inspect it.");
  setTaskActionButtonsDisabled(null);
}

function renderTaskDetail(payload) {
  const summary = payload.summary || {};
  const recipePanel = document.getElementById("task-recipe-panel");
  const isRecipe = summary.executorActionType === "run_operator_recipe";
  uiState.selectedTaskId = summary.taskId || "";
  setText("task-detail-id", summary.taskId || "-");
  setText("task-detail-status", summary.status || "-");
  setText("task-detail-risk", summary.riskLevel || "-");
  setText("task-detail-approval-state", summary.approvalState || "-");
  setText("task-detail-title", summary.title || "-");
  setText("task-detail-description", summary.description || "-");
  setText("task-detail-executor-action", summary.executorActionType || "none");
  setText("task-detail-executor-target", summary.executorTarget || "none");
  setText("task-detail-workspace-scope", summary.workspaceScope || "no_path_detected");
  setText("task-detail-workspace-policy", summary.workspacePolicy || "allowed");
  setText("task-detail-workspace-reason", summary.workspaceReason || "none");
  setText("task-detail-allowed-root", summary.allowedWorkspaceRoot || "unknown");
  setText("task-detail-waiting-for", summary.waitingFor || "none");
  setText("task-detail-blocked-reason", summary.blockedReason || "none");
  setText("task-detail-next-action", summary.nextAction || "Review the task state.");
  setText("task-detail-last-note", summary.lastNote || "none");
  setText("task-detail-retry-limit", String(summary.retryLimit ?? 0));
  setText("task-detail-last-attempt-count", String(summary.lastAttemptCount ?? 0));
  setText("task-detail-last-execution-status", summary.lastExecutionStatus || "not_run");
  setText("task-detail-last-execution-summary", summary.lastExecutionSummary || "none");
  setText("task-detail-last-artifact-path", summary.lastArtifactPath || "none");
  setText("task-detail-last-failure-reason", summary.lastFailureReason || "none");
  setText("task-detail-last-interruption-reason", summary.lastInterruptionReason || "none");
  setText("task-detail-last-resource-guard-reason", summary.lastResourceGuardReason || "none");
  setText("task-detail-summary", summary.headline || "Task details loaded.");
  setValue("task-action-note", summary.lastNote && summary.lastNote !== "none" ? summary.lastNote : "");
  renderTaskHistory(summary.history || []);
  renderExecutionHistory(summary.executionHistory || []);
  if (recipePanel) {
    recipePanel.hidden = !isRecipe;
  }
  if (isRecipe) {
    const recipeSteps = (summary.recipeLastRunSteps || []).length > 0
      ? summary.recipeLastRunSteps
      : (summary.recipeSteps || []);
    const lastRunWindow = [
      summary.recipeLastRunStartedAt ? formatTimeStamp(summary.recipeLastRunStartedAt) : "",
      summary.recipeLastRunFinishedAt ? formatTimeStamp(summary.recipeLastRunFinishedAt) : "",
    ].filter(Boolean).join(" -> ");
    setText("task-detail-recipe-name", summary.recipeLabel || summary.recipeName || "-");
    setText("task-detail-recipe-status", summary.recipeStatus || "not_run");
    setText("task-detail-recipe-run-count", String(summary.recipeRunCount ?? 0));
    setText("task-detail-recipe-summary", summary.recipeSummary || "none");
    setText("task-detail-recipe-last-run", lastRunWindow || "No recipe run recorded yet.");
    setText("task-detail-recipe-source-window", summary.recipeSourceWindow || "none");
    setText("task-detail-recipe-target-window", summary.recipeTargetWindow || "none");
    setText("task-detail-recipe-source-selection-mode", summary.handoffSourceSelectionMode || "none");
    setText("task-detail-recipe-target-selection-mode", summary.handoffTargetSelectionMode || "none");
    setText("task-detail-recipe-source-candidate", summary.recipeSourceWindowCandidateId || "none");
    setText("task-detail-recipe-target-candidate", summary.recipeTargetWindowCandidateId || "none");
    setText("task-detail-recipe-clipboard-mode", summary.recipeClipboardMode || "none");
    setText("task-detail-recipe-fallback-denied", summary.handoffFallbackDenied || "none");
    setText("task-detail-recipe-target-resolution", summary.handoffTargetResolutionStatus || "none");
    setText("task-detail-recipe-payload-classification", summary.handoffPayloadClassification || "none");
    setText("task-detail-recipe-payload-preview", summary.handoffPayloadPreview || "none");
    setText("task-detail-recipe-paste-allowed", summary.handoffPasteAllowed || "none");
    setText("task-detail-recipe-send-behavior", summary.handoffSendBehavior || "none");
    setText("task-detail-recipe-send-allowed", summary.handoffSendAllowed || "none");
    setText("task-detail-recipe-source-match", summary.handoffSourceMatch || "none");
    setText("task-detail-recipe-target-match", summary.handoffTargetMatch || "none");
    setText("task-detail-recipe-blocked-payload-repeats", String(summary.handoffBlockedPayloadRepeats ?? 0));
    setText("task-detail-recipe-stop-reason", summary.handoffStopReason || "none");
    renderRecipeStepHistory(recipeSteps);
    renderRecipeRunHistory(summary.recipeRunHistory || []);
  } else {
    setText("task-detail-recipe-name", "-");
    setText("task-detail-recipe-status", "-");
    setText("task-detail-recipe-run-count", "-");
    setText("task-detail-recipe-summary", "-");
    setText("task-detail-recipe-last-run", "-");
    setText("task-detail-recipe-source-window", "-");
    setText("task-detail-recipe-target-window", "-");
    setText("task-detail-recipe-source-selection-mode", "-");
    setText("task-detail-recipe-target-selection-mode", "-");
    setText("task-detail-recipe-source-candidate", "-");
    setText("task-detail-recipe-target-candidate", "-");
    setText("task-detail-recipe-clipboard-mode", "-");
    setText("task-detail-recipe-fallback-denied", "-");
    setText("task-detail-recipe-target-resolution", "-");
    setText("task-detail-recipe-payload-classification", "-");
    setText("task-detail-recipe-payload-preview", "-");
    setText("task-detail-recipe-paste-allowed", "-");
    setText("task-detail-recipe-send-behavior", "-");
    setText("task-detail-recipe-send-allowed", "-");
    setText("task-detail-recipe-source-match", "-");
    setText("task-detail-recipe-target-match", "-");
    setText("task-detail-recipe-blocked-payload-repeats", "-");
    setText("task-detail-recipe-stop-reason", "-");
    renderRecipeStepHistory([]);
    renderRecipeRunHistory([]);
  }
  renderRaw("task-detail-raw", payload);
  setTaskActionButtonsDisabled(summary);
}

function renderApprovalCards(containerId, items, emptyText, options = {}) {
  const container = document.getElementById(containerId);
  if (!container) {
    return;
  }

  if (!items || items.length === 0) {
    container.innerHTML = `<p class="empty-state">${escapeHtml(emptyText)}</p>`;
    return;
  }

  container.innerHTML = items
    .map((item) => {
      const status = normalizeState(item.status);
      const primaryId = item.approvalId || item.taskId || "item";
      const isSelected = options.inspectable && item.approvalId && item.approvalId === uiState.selectedApprovalId;
      const inspectButton = options.inspectable && item.approvalId
        ? `
            <div class="approval-actions">
              <button
                class="button-secondary approval-action-button"
                type="button"
                data-approval-action="inspect"
                data-approval-id="${escapeHtml(item.approvalId)}"
              >
                ${isSelected ? "Viewing Details" : "Inspect Approval"}
              </button>
            </div>
          `
        : "";

      return `
        <article class="approval-item ${isSelected ? "is-selected" : ""}">
          <div class="approval-topline">
            <strong>${escapeHtml(primaryId)}</strong>
            <span class="state-pill state-${status}">${escapeHtml(item.status || status)}</span>
          </div>
          <div class="approval-summary-grid">
            <p><span>Action</span><strong>${escapeHtml(item.actionType || item.detail || "Approval request")}</strong></p>
            <p><span>Target</span><strong>${escapeHtml(item.target || item.taskId || "none")}</strong></p>
            <p><span>Risk</span><strong>${escapeHtml(item.riskLevel || "unknown")}</strong></p>
            <p><span>Task</span><strong>${escapeHtml(item.taskId || "none")}</strong></p>
            <p><span>Workspace</span><strong>${escapeHtml(item.workspaceScope || "no_path_detected")}</strong></p>
            <p><span>Policy</span><strong>${escapeHtml(item.workspacePolicy || "allowed")}</strong></p>
          </div>
          <p class="approval-description"><span>Description</span>${escapeHtml(item.shortDescription || item.detail || "No short description.")}</p>
          ${inspectButton}
        </article>
      `;
    })
    .join("");
}

function renderTaskCards(containerId, items, emptyText) {
  const container = document.getElementById(containerId);
  if (!container) {
    return;
  }

  if (!items || items.length === 0) {
    container.innerHTML = `<p class="empty-state">${escapeHtml(emptyText)}</p>`;
    return;
  }

  container.innerHTML = items
    .map((item) => {
      const status = normalizeState(item.status);
      const isSelected = item.taskId && item.taskId === uiState.selectedTaskId;
      return `
        <article class="approval-item ${isSelected ? "is-selected" : ""}">
          <div class="approval-topline">
            <strong>${escapeHtml(item.taskId || "task")}</strong>
            <span class="state-pill state-${status}">${escapeHtml(item.status || status)}</span>
          </div>
          <div class="approval-summary-grid">
            <p><span>Workspace</span><strong>${escapeHtml(item.workspaceScope || "no_path_detected")}</strong></p>
            <p><span>Policy</span><strong>${escapeHtml(item.workspacePolicy || "allowed")}</strong></p>
            <p><span>Approval</span><strong>${escapeHtml(item.approvalState || "unknown")}</strong></p>
            <p><span>Next</span><strong>${escapeHtml(item.nextAction || "Review the task state.")}</strong></p>
          </div>
          <p class="approval-description"><span>Why stopped</span>${escapeHtml(item.detail || "No detail recorded.")}</p>
          <p class="approval-description"><span>Operator move</span>${escapeHtml(item.nextAction || "Review the task state.")}</p>
          <div class="approval-actions">
            <button
              class="button-secondary task-action-button"
              type="button"
              data-task-action="inspect"
              data-task-id="${escapeHtml(item.taskId || "")}"
            >
              ${isSelected ? "Viewing Task" : "Inspect Task"}
            </button>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderExecutorTaskCards(payload) {
  const container = document.getElementById("executor-task-list");
  if (!container) {
    return;
  }

  const summary = payload.summary || {};
  const allItems = (summary.tasks || []).filter((item) => !isDesktopExecutorAction(item.actionType) && !isRecipeExecutorAction(item.actionType));
  const filtered = applyTaskListFilters(allItems);
  const items = filtered.items;
  if (items.length === 0) {
    const emptyText = filtered.totalCount > 0
      ? "No repo-local executor tasks match the current task filter."
      : "No repo-local executor tasks queued yet.";
    container.innerHTML = `<p class="empty-state">${escapeHtml(emptyText)}</p>`;
    renderRaw("executor-raw", payload);
    return;
  }

  container.innerHTML = buildTaskFilterNotice("Repo Executor", filtered) + items
    .map((item) => {
      const status = normalizeState(item.status);
      const isSelected = item.taskId && item.taskId === uiState.selectedTaskId;
      return `
        <article class="approval-item ${isSelected ? "is-selected" : ""}">
          <div class="approval-topline">
            <strong>${escapeHtml(item.taskId || "task")}</strong>
            <span class="state-pill state-${status}">${escapeHtml(item.status || status)}</span>
          </div>
          <div class="approval-summary-grid">
            <p><span>Action</span><strong>${escapeHtml(item.actionType || "unknown")}</strong></p>
            <p><span>Target</span><strong>${escapeHtml(item.target || "none")}</strong></p>
            <p><span>Approval</span><strong>${escapeHtml(item.approvalState || "unknown")}</strong></p>
            <p><span>Workspace</span><strong>${escapeHtml(item.workspaceScope || "no_path_detected")}</strong></p>
            <p><span>Policy</span><strong>${escapeHtml(item.workspacePolicy || "allowed")}</strong></p>
          </div>
          <p class="approval-description"><span>Last Result</span>${escapeHtml(item.lastSummary || "not_run")}</p>
          <div class="approval-actions">
            <button
              class="button-secondary task-action-button"
              type="button"
              data-task-action="inspect"
              data-task-id="${escapeHtml(item.taskId || "")}"
            >
              ${isSelected ? "Viewing Task" : "Inspect Task"}
            </button>
          </div>
        </article>
      `;
    })
    .join("");

  renderRaw("executor-raw", payload);
}

function renderRecipeTaskCards(payload) {
  const container = document.getElementById("recipe-task-list");
  if (!container) {
    return;
  }

  const summary = payload.summary || {};
  const allItems = (summary.tasks || []).filter((item) => isRecipeExecutorAction(item.actionType));
  const filtered = applyTaskListFilters(allItems);
  const items = filtered.items;
  if (items.length === 0) {
    const emptyText = filtered.totalCount > 0
      ? "No operator recipe tasks match the current task filter."
      : "No operator recipe tasks queued yet.";
    container.innerHTML = `<p class="empty-state">${escapeHtml(emptyText)}</p>`;
    return;
  }

  container.innerHTML = buildTaskFilterNotice("Operator Recipes", filtered) + items
    .map((item) => {
      const status = normalizeState(item.status);
      const isSelected = item.taskId && item.taskId === uiState.selectedTaskId;
      return `
        <article class="approval-item ${isSelected ? "is-selected" : ""}">
          <div class="approval-topline">
            <strong>${escapeHtml(item.taskId || "task")}</strong>
            <span class="state-pill state-${status}">${escapeHtml(item.status || status)}</span>
          </div>
          <div class="approval-summary-grid">
            <p><span>Recipe</span><strong>${escapeHtml(item.target || "unknown_recipe")}</strong></p>
            <p><span>Source</span><strong>${escapeHtml(item.sourceWindow || "none")}</strong></p>
            <p><span>Target</span><strong>${escapeHtml(item.targetWindow || "none")}</strong></p>
            <p><span>Approval</span><strong>${escapeHtml(item.approvalState || "unknown")}</strong></p>
            <p><span>Workspace</span><strong>${escapeHtml(item.workspaceScope || "no_path_detected")}</strong></p>
            <p><span>Policy</span><strong>${escapeHtml(item.workspacePolicy || "allowed")}</strong></p>
            <p><span>Payload</span><strong>${escapeHtml(item.payloadClassification && item.payloadClassification !== "none" ? item.payloadClassification : "not_classified")}</strong></p>
            <p><span>Send</span><strong>${escapeHtml(item.sendBehavior && item.sendBehavior !== "none" ? item.sendBehavior : "not_applicable")}</strong></p>
          </div>
          <p class="approval-description"><span>Last Result</span>${escapeHtml(item.lastSummary || "not_run")}</p>
          <div class="approval-actions">
            <button
              class="button-secondary task-action-button"
              type="button"
              data-task-action="inspect"
              data-task-id="${escapeHtml(item.taskId || "")}"
            >
              ${isSelected ? "Viewing Recipe Task" : "Inspect Recipe Task"}
            </button>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderDesktopTaskCards(payload) {
  const container = document.getElementById("desktop-task-list");
  if (!container) {
    return;
  }

  const summary = payload.summary || {};
  const allItems = (summary.tasks || []).filter((item) => isDesktopExecutorAction(item.actionType));
  const filtered = applyTaskListFilters(allItems);
  const items = filtered.items;
  if (items.length === 0) {
    const emptyText = filtered.totalCount > 0
      ? "No desktop action tasks match the current task filter."
      : "No desktop action tasks queued yet.";
    container.innerHTML = `<p class="empty-state">${escapeHtml(emptyText)}</p>`;
    return;
  }

  container.innerHTML = buildTaskFilterNotice("Desktop Actions", filtered) + items
    .map((item) => {
      const status = normalizeState(item.status);
      const isSelected = item.taskId && item.taskId === uiState.selectedTaskId;
      const approvalNote = ["approved", "not_required"].includes(String(item.approvalState || "").toLowerCase())
        ? "ready to run when queued"
        : "approval still required before run";

      return `
        <article class="approval-item ${isSelected ? "is-selected" : ""}">
          <div class="approval-topline">
            <strong>${escapeHtml(item.taskId || "task")}</strong>
            <span class="state-pill state-${status}">${escapeHtml(item.status || status)}</span>
          </div>
          <div class="approval-summary-grid">
            <p><span>Desktop action</span><strong>${escapeHtml(item.actionType || "unknown")}</strong></p>
            <p><span>Target</span><strong>${escapeHtml(item.target || "none")}</strong></p>
            <p><span>Approval</span><strong>${escapeHtml(item.approvalState || "unknown")}</strong></p>
            <p><span>Workspace</span><strong>${escapeHtml(item.workspaceScope || "no_path_detected")}</strong></p>
            <p><span>Policy</span><strong>${escapeHtml(item.workspacePolicy || "allowed")}</strong></p>
          </div>
          <p class="approval-description"><span>Run state</span>${escapeHtml(approvalNote)}</p>
          <p class="approval-description"><span>Last Result</span>${escapeHtml(item.lastSummary || "not_run")}</p>
          <div class="approval-actions">
            <button
              class="button-secondary task-action-button"
              type="button"
              data-task-action="inspect"
              data-task-id="${escapeHtml(item.taskId || "")}"
            >
              ${isSelected ? "Viewing Task" : "Inspect Desktop Task"}
            </button>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderSupervisorStatus(payload) {
  const summary = payload.summary || {};
  const statusLabel = (summary.status || "unknown").replaceAll("_", " ");
  const workspaceBlocked = (summary.pendingApprovals || []).some((item) => item.workspacePolicy === "blocked_by_workspace_policy")
    || (summary.humanNeededTasks || []).some((item) => item.workspacePolicy === "blocked_by_workspace_policy");
  renderGhotiState(summary);

  setText("supervisor-headline", summary.headline || "Supervisor status unavailable.");
  setText(
    "supervisor-quick-note",
    summary.ghotiState === "resource_guard_triggered"
      ? "Ghoti paused new window-spawning work because the current terminal or process picture looks cluttered."
      : workspaceBlocked
      ? "Some requests are blocked by workspace policy because they target paths outside the allowed workspace."
      : summary.pendingApprovalCount > 0
      ? "Risky or uncertain work is paused until the human approves it."
      : summary.blockedHumanNeededCount > 0
        ? "Some tasks are blocked on a human reply or judgment call."
      : summary.interruptedCount > 0
        ? "Some desktop tasks were interrupted by the failsafe and need operator review before they continue."
      : summary.readyToResumeCount > 0
          ? "Some tasks were reviewed already and can be re-queued manually."
      : "No open approvals right now. The supervisor is only tracking local state.",
  );
  setText("supervisor-status", statusLabel);
  setText("supervisor-pending-count", String(summary.pendingApprovalCount ?? 0));
  setText("supervisor-human-needed-count", String(summary.blockedHumanNeededCount ?? 0));
  setText("supervisor-waiting-count", String(summary.waitingCount ?? 0));
  setText("supervisor-ready-count", String(summary.readyToResumeCount ?? 0));
  setText("supervisor-interrupted-count", String(summary.interruptedCount ?? 0));
  setText(
    "supervisor-summary",
    [summary.headline || "Supervisor status unavailable.", summary.operatorNextStep || ""].filter(Boolean).join(" "),
  );

  renderApprovalCards(
    "pending-approvals-list",
    summary.pendingApprovals || [],
    "No pending approvals right now.",
    { inspectable: true },
  );
  renderTaskCards(
    "human-needed-list",
    summary.humanNeededTasks || [],
    "No human-needed tasks right now.",
  );
  renderTaskCards(
    "interrupted-tasks-list",
    summary.interruptedTasks || [],
    "No interrupted tasks right now.",
  );
  renderTaskCards(
    "waiting-tasks-list",
    summary.waitingTasks || [],
    "No waiting tasks right now.",
  );
  renderTaskCards(
    "ready-to-resume-list",
    summary.readyToResumeTasks || [],
    "No ready-to-resume tasks right now.",
  );
  renderRaw("supervisor-raw", payload);
}

function renderPendingApprovals(payload) {
  const summary = payload.summary || {};
  renderApprovalCards(
    "pending-approvals-list",
    summary.requests || [],
    "No pending approvals right now.",
    { inspectable: true },
  );
}

function renderArtifacts(payload) {
  const container = document.getElementById("artifacts-output");
  const artifacts = payload.artifacts || [];
  if (!container) {
    return;
  }

  if (artifacts.length === 0) {
    container.innerHTML = "<p class=\"empty-state\">No recent artifacts found.</p>";
    return;
  }

  container.innerHTML = artifacts
    .map((artifact) => {
      const groupLabel = String(artifact.group || "artifact").replaceAll("_", " ");
      const previewButton = artifact.previewable
        ? `<button class="button-secondary artifact-action" type="button" data-artifact-action="preview" data-artifact-path="${escapeHtml(artifact.path)}">Preview</button>`
        : `<button class="button-secondary artifact-action" type="button" disabled>Preview unavailable</button>`;

      return `
        <article class="artifact-item">
          <div class="artifact-topline">
            <strong>${escapeHtml(artifact.name)}</strong>
            <span class="artifact-group">${escapeHtml(groupLabel)}</span>
          </div>
          <code class="artifact-path">${escapeHtml(artifact.path)}</code>
          <span class="artifact-meta">${escapeHtml(artifact.modifiedAt)}</span>
          <div class="artifact-actions">
            ${previewButton}
            <button class="button-secondary artifact-action" type="button" data-artifact-action="open" data-artifact-path="${escapeHtml(artifact.path)}">Open</button>
            <button class="button-secondary artifact-action" type="button" data-artifact-action="reveal" data-artifact-path="${escapeHtml(artifact.path)}">Reveal</button>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderRecentActions(payload) {
  uiState.serverActions = payload.actions || [];
  renderRecentActionsPanel();
}

function renderRecentActionsPanel() {
  const container = document.getElementById("recent-actions-output");
  const actions = [...uiState.localActions, ...uiState.serverActions].slice(0, 12);
  if (!container) {
    renderDashboardRecentActivity(uiState.latestControlCenterSummary || {});
    return;
  }

  if (actions.length === 0) {
    container.innerHTML = "<p class=\"empty-state\">No recent actions yet.</p>";
    renderDashboardRecentActivity(uiState.latestControlCenterSummary || {});
    return;
  }

  container.innerHTML = actions
    .map((action) => {
      const state = normalizeState(action.status);
      return `
        <article class="log-item">
          <div class="log-topline">
            <strong>${escapeHtml(action.label || "Action")}</strong>
            <span class="state-pill state-${state}">${escapeHtml(action.status || state)}</span>
          </div>
          <p>${escapeHtml(action.summary || "No summary.")}</p>
          <small>${escapeHtml(formatTimeStamp(action.occurredAt))}</small>
        </article>
      `;
    })
    .join("");

  renderDashboardRecentActivity(uiState.latestControlCenterSummary || {});
}

function renderInlineMarkdown(text) {
  return escapeHtml(text)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");
}

function renderMarkdownPreview(markdown) {
  const lines = String(markdown || "").replace(/\r/g, "").split("\n");
  const parts = [];
  let paragraph = [];
  let listItems = [];
  let codeFence = [];
  let inCodeFence = false;

  function flushParagraph() {
    if (paragraph.length > 0) {
      parts.push(`<p>${renderInlineMarkdown(paragraph.join(" "))}</p>`);
      paragraph = [];
    }
  }

  function flushList() {
    if (listItems.length > 0) {
      parts.push(`<ul>${listItems.map((item) => `<li>${renderInlineMarkdown(item)}</li>`).join("")}</ul>`);
      listItems = [];
    }
  }

  function flushCodeFence() {
    if (codeFence.length > 0) {
      parts.push(`<pre>${escapeHtml(codeFence.join("\n"))}</pre>`);
      codeFence = [];
    }
  }

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();

    if (line.startsWith("```")) {
      flushParagraph();
      flushList();
      if (inCodeFence) {
        flushCodeFence();
        inCodeFence = false;
      } else {
        inCodeFence = true;
      }
      continue;
    }

    if (inCodeFence) {
      codeFence.push(rawLine);
      continue;
    }

    const trimmed = line.trim();
    if (!trimmed) {
      flushParagraph();
      flushList();
      continue;
    }

    const headingMatch = trimmed.match(/^(#{1,6})\s+(.*)$/);
    if (headingMatch) {
      flushParagraph();
      flushList();
      const level = Math.min(headingMatch[1].length, 6);
      parts.push(`<h${level}>${renderInlineMarkdown(headingMatch[2])}</h${level}>`);
      continue;
    }

    if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      flushParagraph();
      listItems.push(trimmed.slice(2));
      continue;
    }

    paragraph.push(trimmed);
  }

  flushParagraph();
  flushList();
  flushCodeFence();

  return parts.join("") || "<p class=\"empty-state\">Preview is empty.</p>";
}

function renderArtifactPreview(preview) {
  uiState.selectedArtifactPath = preview.path;
  setText("artifact-preview-title", preview.name || "Artifact Preview");

  const meta = [
    preview.path || "unknown path",
    preview.format || "text",
    preview.truncated ? "preview truncated" : "full preview",
  ].join(" | ");
  setText("artifact-preview-meta", meta);

  const body = document.getElementById("artifact-preview-body");
  if (!body) {
    return;
  }

  if (preview.format === "markdown") {
    body.innerHTML = `<article class="artifact-preview-rendered">${renderMarkdownPreview(preview.content)}</article>`;
    return;
  }

  body.innerHTML = `<pre class="preview-pre">${escapeHtml(preview.content || "")}</pre>`;
}

function clearArtifactPreview(message) {
  setText("artifact-preview-title", "Artifact Preview");
  setText("artifact-preview-meta", "Select Preview on an artifact to read it here.");
  const body = document.getElementById("artifact-preview-body");
  if (body) {
    body.innerHTML = `<p class="empty-state">${escapeHtml(message)}</p>`;
  }
}

async function previewArtifactPath(artifactPath, options = {}) {
  const { silent = false, button = null } = options;
  const actionId = silent ? null : createLocalAction("Preview artifact", `Loading preview for ${artifactPath}.`);
  if (!silent) {
    setResultPanel("artifact-preview-status", "loading", "Loading artifact preview...", artifactPath);
  }

  try {
    const result = await withButtonState(button, "Working...", () =>
      requestJson("/api/artifacts/preview", {
        method: "POST",
        body: JSON.stringify({ path: artifactPath }),
      }),
    );
    renderArtifactPreview(result.preview);
    setResultPanel("artifact-preview-status", "success", result.summary?.headline || "Preview loaded.", result.preview.path);
    if (actionId) {
      updateLocalAction(actionId, "success", result.summary?.headline || "Artifact preview loaded.");
    }
    await refreshRecentActions();
    return result;
  } catch (error) {
    setResultPanel("artifact-preview-status", "error", "Artifact preview failed.", error.message);
    if (actionId) {
      updateLocalAction(actionId, "error", error.message);
    }
    if (!silent) {
      await refreshRecentActions();
    }
    return null;
  }
}

async function runArtifactFileAction(actionType, artifactPath, button) {
  const labelMap = {
    open: "Open artifact",
    reveal: "Reveal artifact",
  };
  const endpointMap = {
    open: "/api/artifacts/open",
    reveal: "/api/artifacts/reveal",
  };
  const actionLabel = labelMap[actionType] || "Artifact action";
  const actionId = createLocalAction(actionLabel, `${actionLabel} started.`);
  setResultPanel("artifact-preview-status", "loading", `${actionLabel}...`, artifactPath);

  try {
    const result = await withButtonState(button, "Working...", () =>
      requestJson(endpointMap[actionType], {
        method: "POST",
        body: JSON.stringify({ path: artifactPath }),
      }),
    );
    setResultPanel("artifact-preview-status", "success", result.summary?.headline || `${actionLabel} complete.`, result.summary?.outputPath || artifactPath);
    updateLocalAction(actionId, "success", result.summary?.headline || `${actionLabel} complete.`);
    await refreshRecentActions();
    return result;
  } catch (error) {
    setResultPanel("artifact-preview-status", "error", `${actionLabel} failed.`, error.message);
    updateLocalAction(actionId, "error", error.message);
    await refreshRecentActions();
    return null;
  }
}

async function refreshOperatorStatus() {
  const payload = await requestJson("/api/operator-status");
  renderOperatorStatus(payload);
}

async function refreshGhotiControlCenter() {
  const filters = getGhotiControlCenterFilters();
  const query = new URLSearchParams({
    visibility: filters.visibility,
    taskType: filters.taskType,
    taskStatus: filters.taskStatus,
    activeOnly: filters.activeOnly ? "true" : "false",
    limit: String(filters.limit || "6"),
  });
  const payload = await requestJson(`/api/ghoti/control-center?${query.toString()}`);
  renderGhotiControlCenter(payload);
  return payload;
}

async function refreshPipelineState() {
  const payload = await requestJson("/api/ghoti/pipeline-state");
  const s = payload.summary || {};
  const inbox = s.approval_inbox_summary || {};
  const queue = s.manual_queue_summary || {};
  const items = s.latest_items || {};
  const decision = (s.latest_operator_state || {}).decision || "-";
  const proposed = s.latest_proposed_action || "-";

  setText("pipeline-operator-decision", decision);
  setText("pipeline-proposed-action", proposed);
  setText("pipeline-pending-approvals", payload.ok ? (inbox.pending_count ?? "-") : "unavailable");
  setText("pipeline-approved-count", payload.ok ? (inbox.approved_count ?? "-") : "unavailable");
  setText("pipeline-ready-items", payload.ok ? (queue.ready_count ?? "-") : "unavailable");
  setText("pipeline-reviewed-items", payload.ok ? (queue.reviewed_count ?? "-") : "unavailable");
  setText("pipeline-latest-approved-id", items.latest_approved_approval_id || "none");
  setText("pipeline-latest-ready-id", items.latest_ready_item_id || "none");

  const note = payload.ok
    ? `Status: ${s.status || "unknown"} — generated ${s.generated_at_utc || ""}`
    : humanizeGhotiIssue(extractPayloadErrors(payload)[0] || s.reason || "Pipeline state unavailable.");
  setText("pipeline-state-summary", note);
  return payload;
}

async function refreshPipelineItems() {
  const payload = await requestJson("/api/ghoti/pipeline-items");
  const s = payload.summary || {};
  const counts = s.counts || {};
  const items = s.items || [];
  const note = payload.ok
    ? `${counts.total_items ?? 0} items — pending: ${counts.pending_count ?? 0}, approved: ${counts.approved_count ?? 0}, ready: ${counts.ready_count ?? 0}, reviewed: ${counts.reviewed_count ?? 0} — ${s.generated_at_utc || ""}`
    : humanizeGhotiIssue(extractPayloadErrors(payload)[0] || s.reason || "Pipeline items unavailable.");
  setText("pipeline-items-summary", note);
  const container = document.getElementById("pipeline-items-list");
  if (!container) return payload;
  if (!payload.ok) {
    container.innerHTML = renderInlineErrorCard("Pipeline items unavailable", note, payload.detail || payload);
    return payload;
  }
  if (!items.length) {
    container.innerHTML = `<p class="empty-state">No pipeline items found.</p>`;
    return payload;
  }
  container.innerHTML = items.map((item) => {
    const stage = escapeHtml(item.latest_stage || "-");
    const approvalId = escapeHtml((item.approval_id || "").slice(0, 24));
    const action = escapeHtml(item.proposed_action || "-");
    const ts = escapeHtml((item.latest_timestamp_utc || "").replace("T", " ").replace("Z", " UTC"));
    const reviewed = item.reviewed ? "✓ reviewed" : "";
    const stageClass = item.approval_status === "pending" ? "status-pending"
      : item.approval_status === "rejected" ? "status-error"
      : item.latest_stage === "reviewed_by_operator" ? "status-success"
      : item.latest_stage === "ready_for_manual_execution" ? "status-warning"
      : "status-info";
    const rawApprovalId = escapeHtml(item.approval_id || "");
    return `<article class="approval-item">
      <div class="approval-header">
        <span class="approval-id">${approvalId}</span>
        <span class="status-pill ${stageClass}">${stage}</span>
        ${reviewed ? `<span class="status-pill status-success">${reviewed}</span>` : ""}
      </div>
      <div class="approval-body">
        <p><strong>Action:</strong> ${action}</p>
        <p class="approval-meta">${ts}</p>
        ${rawApprovalId ? `<button class="view-trace-btn button-secondary" data-approval-id="${rawApprovalId}" type="button" style="margin-top:6px;">View Trace</button>` : ""}
      </div>
    </article>`;
  }).join("");
  container.querySelectorAll(".view-trace-btn").forEach((btn) => {
    btn.addEventListener("click", () => loadAuditTraceById(btn.dataset.approvalId));
  });
  return payload;
}

async function refreshApprovalInbox() {
  let payload;
  try {
    payload = await requestJson("/api/ghoti/approval-inbox");
  } catch (err) {
    const message = "Approval inbox unavailable: " + err.message;
    setText("approval-inbox-summary", message);
    const container = document.getElementById("approval-inbox-list");
    if (container) {
      container.innerHTML = renderInlineErrorCard("Approval inbox unavailable", message, { error: err.message });
    }
    return;
  }
  const s = payload.summary || {};
  const items = (s.items || []).filter((item) => item.status === "pending");
  const note = payload.ok
    ? `${items.length} pending approval(s) — total in inbox: ${(s.items || []).length}`
    : humanizeGhotiIssue(extractPayloadErrors(payload)[0] || s.reason || "Approval inbox unavailable.");
  setText("approval-inbox-summary", note);
  const container = document.getElementById("approval-inbox-list");
  if (!container) return;
  if (!payload.ok) {
    container.innerHTML = renderInlineErrorCard("Approval inbox unavailable", note, payload.detail || payload);
    return;
  }
  if (!items.length) {
    container.innerHTML = `<p class="empty-state">No pending approvals. All items are approved, rejected, or the inbox is empty.</p>`;
    return;
  }
  container.innerHTML = items.map((item) => {
    const id = escapeHtml(item.id || "");
    const action = escapeHtml(item.proposed_action || "-");
    const ts = escapeHtml((item.timestamp_utc || "").replace("T", " ").replace("Z", " UTC"));
    const reason = escapeHtml(item.reason || "");
    return `<article class="approval-item">
      <div class="approval-header">
        <span class="approval-id">${id.slice(0, 24)}</span>
        <span class="status-pill status-pending">pending</span>
        <span class="console-badge">approval required</span>
      </div>
      <div class="approval-body">
        <p><strong>Action:</strong> ${action}</p>
        ${reason ? `<p><strong>Reason:</strong> ${reason}</p>` : ""}
        <p class="approval-meta">${ts}</p>
        <div style="display:flex;gap:6px;margin-top:6px;flex-wrap:wrap;">
          <button class="approve-inbox-btn" data-approval-id="${id}" type="button">Approve</button>
          <button class="reject-inbox-btn button-danger" data-approval-id="${id}" type="button">Reject…</button>
          <button class="view-inbox-trace-btn button-secondary" data-approval-id="${id}" type="button">View Trace</button>
        </div>
      </div>
    </article>`;
  }).join("");
  container.querySelectorAll(".approve-inbox-btn").forEach((btn) => {
    btn.addEventListener("click", () => approveInboxItem(btn.dataset.approvalId));
  });
  container.querySelectorAll(".reject-inbox-btn").forEach((btn) => {
    btn.addEventListener("click", () => showInboxRejectForm(btn.dataset.approvalId));
  });
  container.querySelectorAll(".view-inbox-trace-btn").forEach((btn) => {
    btn.addEventListener("click", () => loadAuditTraceById(btn.dataset.approvalId));
  });
}

function showInboxRejectForm(approvalId) {
  const form = document.getElementById("approval-inbox-reject-form");
  const idSpan = document.getElementById("approval-inbox-reject-id");
  const textarea = document.getElementById("approval-inbox-reject-reason");
  if (!form || !idSpan || !textarea) return;
  idSpan.textContent = approvalId;
  textarea.value = "";
  form.dataset.pendingId = approvalId;
  form.style.display = "block";
  textarea.focus();
}

async function approveInboxItem(approvalId) {
  const resultEl = document.getElementById("approval-inbox-action-result");
  if (resultEl) resultEl.textContent = `Approving ${approvalId}…`;
  try {
    const result = await requestJson("/api/ghoti/approval/approve", {
      method: "POST",
      body: JSON.stringify({ approval_id: approvalId }),
    });
    if (resultEl) resultEl.textContent = result.summary?.headline || "Approved.";
    await refreshApprovalInbox();
    await refreshManualQueue();
    await refreshPipelineItems();
    await refreshPipelineState();
    await refreshNeedsActionNow();
  } catch (err) {
    if (resultEl) resultEl.textContent = "Approve failed: " + err.message;
  }
}

async function rejectInboxItem(approvalId, reason) {
  const resultEl = document.getElementById("approval-inbox-action-result");
  if (resultEl) resultEl.textContent = `Rejecting ${approvalId}…`;
  try {
    const result = await requestJson("/api/ghoti/approval/reject", {
      method: "POST",
      body: JSON.stringify({ approval_id: approvalId, reason }),
    });
    if (resultEl) resultEl.textContent = result.summary?.headline || "Rejected.";
    await refreshApprovalInbox();
    await refreshPipelineItems();
    await refreshPipelineState();
    await refreshNeedsActionNow();
  } catch (err) {
    if (resultEl) resultEl.textContent = "Reject failed: " + err.message;
  }
}

async function refreshManualQueue() {
  let payload;
  try {
    payload = await requestJson("/api/ghoti/manual-queue");
  } catch (err) {
    const message = "Manual queue unavailable: " + err.message;
    setText("manual-queue-summary", message);
    const container = document.getElementById("manual-queue-list");
    if (container) {
      container.innerHTML = renderInlineErrorCard("Manual queue unavailable", message, { error: err.message });
    }
    return;
  }
  const s = payload.summary || {};
  const items = s.items || [];
  const readyCount = items.filter((i) => i.status === "ready_for_manual_execution").length;
  const reviewedCount = items.filter((i) => i.status === "reviewed_by_operator").length;
  const note = payload.ok
    ? `${items.length} item(s) — ready: ${readyCount}, reviewed: ${reviewedCount}`
    : humanizeGhotiIssue(extractPayloadErrors(payload)[0] || s.reason || "Manual queue unavailable.");
  setText("manual-queue-summary", note);
  const container = document.getElementById("manual-queue-list");
  if (!container) return;
  if (!payload.ok) {
    container.innerHTML = renderInlineErrorCard("Manual queue unavailable", note, payload.detail || payload);
    return;
  }
  if (!items.length) {
    container.innerHTML = `<p class="empty-state">No items in the manual queue.</p>`;
    return;
  }
  container.innerHTML = items.map((item) => {
    const id = escapeHtml(item.id || "");
    const srcApproval = escapeHtml(item.source_approval_id || "-");
    const action = escapeHtml(item.proposed_action || "-");
    const status = escapeHtml(item.status || "-");
    const ts = escapeHtml((item.created_at_utc || "").replace("T", " ").replace("Z", " UTC"));
    const reviewNote = escapeHtml(item.review_note || "");
    const statusClass = status === "reviewed_by_operator" ? "status-success"
      : status === "ready_for_manual_execution" ? "status-warning" : "status-info";
    const isReviewed = status === "reviewed_by_operator";
    return `<article class="approval-item">
      <div class="approval-header">
        <span class="approval-id">${id.slice(0, 24)}</span>
        <span class="status-pill ${statusClass}">${status}</span>
        <span class="console-badge">manual only</span>
        ${isReviewed ? `<span class="status-pill status-success">reviewed by operator</span>` : ""}
      </div>
      <div class="approval-body">
        <p><strong>Action:</strong> ${action}</p>
        <p><strong>Source approval:</strong> ${srcApproval}</p>
        ${reviewNote ? `<p><strong>Review note:</strong> ${reviewNote}</p>` : ""}
        <p class="approval-meta">${ts}</p>
        <div style="display:flex;gap:6px;margin-top:6px;flex-wrap:wrap;">
          ${!isReviewed ? `<button class="review-queue-btn" data-item-id="${id}" type="button">Mark Reviewed…</button>` : ""}
          ${escapeHtml(item.source_approval_id || "") ? `<button class="view-queue-trace-btn button-secondary" data-approval-id="${escapeHtml(item.source_approval_id || "")}" type="button">View Trace</button>` : ""}
        </div>
      </div>
    </article>`;
  }).join("");
  container.querySelectorAll(".review-queue-btn").forEach((btn) => {
    btn.addEventListener("click", () => showQueueReviewForm(btn.dataset.itemId));
  });
  container.querySelectorAll(".view-queue-trace-btn").forEach((btn) => {
    btn.addEventListener("click", () => loadAuditTraceById(btn.dataset.approvalId));
  });
}

function showQueueReviewForm(itemId) {
  const form = document.getElementById("manual-queue-review-form");
  const idSpan = document.getElementById("manual-queue-review-id");
  const textarea = document.getElementById("manual-queue-review-note");
  if (!form || !idSpan || !textarea) return;
  idSpan.textContent = itemId;
  textarea.value = "";
  form.dataset.pendingId = itemId;
  form.style.display = "block";
  textarea.focus();
}

async function submitQueueReview(itemId, note) {
  const resultEl = document.getElementById("manual-queue-action-result");
  if (resultEl) resultEl.textContent = `Marking ${itemId} reviewed…`;
  try {
    const result = await requestJson("/api/ghoti/manual-queue/review", {
      method: "POST",
      body: JSON.stringify({ item_id: itemId, note }),
    });
    if (resultEl) resultEl.textContent = result.summary?.headline || "Marked reviewed.";
    await refreshManualQueue();
    await refreshPipelineItems();
    await refreshPipelineState();
    await refreshNeedsActionNow();
  } catch (err) {
    if (resultEl) resultEl.textContent = "Review failed: " + err.message;
  }
}

async function refreshAuditTrace() {
  const input = document.getElementById("audit-trace-id-input");
  const approvalId = input ? input.value.trim() : "";
  if (!approvalId) {
    setText("audit-trace-summary", "Enter an approval ID above and click Load Trace.");
    return;
  }
  setText("audit-trace-summary", `Loading trace for ${approvalId}…`);
  let payload;
  try {
    payload = await requestJson(`/api/ghoti/audit-trace?approval_id=${encodeURIComponent(approvalId)}`);
  } catch (err) {
    const message = "Audit trace failed: " + err.message;
    setText("audit-trace-summary", message);
    const container = document.getElementById("audit-trace-body");
    if (container) {
      container.innerHTML = renderInlineErrorCard("Audit trace unavailable", message, { error: err.message, approvalId });
    }
    return;
  }
  const s = payload.summary || {};
  const flags = s.lifecycle_flags || {};
  const note = payload.ok
    ? `Trace status: ${s.trace_status || "unknown"} — approval: ${flags.approval_found ? "found" : "missing"}, queue: ${flags.queue_item_found ? "found" : "missing"}`
    : humanizeGhotiIssue(extractPayloadErrors(payload)[0] || s.reason || "Audit trace unavailable.");
  setText("audit-trace-summary", note);
  const container = document.getElementById("audit-trace-body");
  if (!container) return;
  if (!payload.ok || !s.approval_item) {
    container.innerHTML = renderInlineErrorCard("Audit trace unavailable", note, payload.detail || payload);
    return;
  }
  const ai = s.approval_item || {};
  const qi = s.manual_queue_item;
  const timeline = s.timeline || [];
  container.innerHTML = `
    <article class="approval-item">
      <div class="approval-header">
        <span class="approval-id">${escapeHtml((ai.id || "").slice(0, 24))}</span>
        <span class="status-pill ${ai.status === "approved" ? "status-success" : ai.status === "rejected" ? "status-error" : "status-pending"}">${escapeHtml(ai.status || "-")}</span>
      </div>
      <div class="approval-body">
        <p><strong>Action:</strong> ${escapeHtml(ai.proposed_action || "-")}</p>
        <p><strong>Reason:</strong> ${escapeHtml(ai.reason || "-")}</p>
        ${ai.resolved_at_utc ? `<p><strong>Resolved:</strong> ${escapeHtml(ai.resolved_at_utc)}</p>` : ""}
      </div>
    </article>
    ${qi ? `<article class="approval-item">
      <div class="approval-header">
        <span class="approval-id">Queue: ${escapeHtml((qi.id || "").slice(0, 24))}</span>
        <span class="status-pill ${qi.status === "reviewed_by_operator" ? "status-success" : "status-warning"}">${escapeHtml(qi.status || "-")}</span>
        <span class="console-badge">manual only</span>
      </div>
      <div class="approval-body">
        ${qi.review_note ? `<p><strong>Review note:</strong> ${escapeHtml(qi.review_note)}</p>` : ""}
        ${qi.reviewed_at_utc ? `<p><strong>Reviewed at:</strong> ${escapeHtml(qi.reviewed_at_utc)}</p>` : ""}
      </div>
    </article>` : `<p class="empty-state">No manual queue item recorded for this approval.</p>`}
    <div class="timeline-list">
      ${(timeline || []).map((entry) => `
        <article class="log-item">
          <div class="log-topline">
            <strong>${escapeHtml(entry.event || "event")}</strong>
            <span class="console-badge">${escapeHtml(entry.timestamp_utc || "")}</span>
          </div>
          <p>${escapeHtml(entry.note || "")}</p>
        </article>
      `).join("")}
    </div>
  `;
}

function loadAuditTraceById(approvalId) {
  const input = document.getElementById("audit-trace-id-input");
  if (input) input.value = approvalId;
  scrollToElement("ghoti-audit-trace-panel");
  refreshAuditTrace();
}

function extractPayloadErrors(payload = {}) {
  const detailErrors = Array.isArray(payload?.detail?.errors) ? payload.detail.errors : [];
  const summaryReason = payload?.summary?.reason ? [payload.summary.reason] : [];
  const detailReason = payload?.detail?.summary?.reason ? [payload.detail.summary.reason] : [];
  const directError = payload?.error ? [payload.error] : [];
  return [...new Set([...detailErrors, ...summaryReason, ...detailReason, ...directError].filter(Boolean))];
}

function humanizeGhotiIssue(rawMessage) {
  const message = String(rawMessage || "").trim();
  if (!message) {
    return "No fresh supervised data is available right now.";
  }
  if (message.includes(".runtime_data.lock")) {
    return "The live runtime lock file is missing, so this panel is falling back to saved operator state only.";
  }
  if (message.startsWith("approval_inbox_read_failed")) {
    return "The approval inbox could not be read from the local supervised runtime state.";
  }
  if (message.startsWith("manual_queue_read_failed")) {
    return "The manual queue could not be read from the local supervised runtime state.";
  }
  if (message.startsWith("operator_state_read_failed")) {
    return "The latest operator snapshot could not be read from compact memory.";
  }
  if (message.startsWith("operator_state_missing")) {
    return "No operator snapshot has been recorded yet.";
  }
  return message.replaceAll("_", " ");
}

function renderInlineErrorCard(title, message, debugPayload) {
  const debugText = typeof debugPayload === "string"
    ? debugPayload
    : JSON.stringify(debugPayload ?? {}, null, 2);
  return `
    <article class="inline-error-card">
      <div class="inline-error-topline">
        <strong>${escapeHtml(title)}</strong>
        <span class="state-pill state-error">attention</span>
      </div>
      <p>${escapeHtml(message)}</p>
      <details class="details-block">
        <summary>Debug details</summary>
        <pre>${escapeHtml(debugText)}</pre>
      </details>
    </article>
  `;
}

function updateApprovalsTabBadge(summary = {}) {
  const badge = document.getElementById("tab-badge-approvals");
  if (!badge) {
    return;
  }
  const attention = summary.attention_summary || {};
  const inbox = summary.approval_inbox_summary || {};
  const queue = summary.manual_queue_summary || {};
  const pending = Number(attention.pending_approvals_count ?? inbox.pending_count ?? 0) || 0;
  const ready = Number(attention.ready_queue_count ?? queue.ready_count ?? 0) || 0;
  const total = pending + ready;
  badge.textContent = total > 0 ? String(total) : "";
  badge.title = total > 0 ? `${pending} pending approvals, ${ready} ready manual items` : "";
}

function buildDashboardIssues(summary = {}, payload = {}) {
  const issues = [];
  const approvalSummary = summary.approval_inbox_summary || {};
  const queueSummary = summary.manual_queue_summary || {};
  const attention = summary.attention_summary || {};
  const recentItems = Array.isArray(summary.recent_pipeline_items) ? summary.recent_pipeline_items : [];

  if (approvalSummary.available === false && approvalSummary.reason) {
    issues.push(humanizeGhotiIssue(approvalSummary.reason));
  }
  if (queueSummary.available === false && queueSummary.reason) {
    issues.push(humanizeGhotiIssue(queueSummary.reason));
  }
  (attention.action_items || []).forEach((item) => {
    if (item) {
      issues.push(String(item));
    }
  });
  recentItems.forEach((item) => {
    const stage = String(item.latest_stage || "");
    if (["approved_no_queue", "approval_rejected"].includes(stage)) {
      const action = item.proposed_action || item.approval_id || "pipeline item";
      issues.push(`${action}: ${stage.replaceAll("_", " ")}.`);
    }
  });
  extractPayloadErrors(payload).forEach((error) => {
    issues.push(humanizeGhotiIssue(error));
  });

  return [...new Set(issues.filter(Boolean))].slice(0, 6);
}

function renderDashboardStrip(summary = {}, payload = {}) {
  const latest = summary.latest_operator_state || {};
  const attention = summary.attention_summary || {};
  const inbox = summary.approval_inbox_summary || {};
  const queue = summary.manual_queue_summary || {};
  const issues = buildDashboardIssues(summary, payload);

  const pendingText = inbox.available === false
    ? "Unavailable"
    : String(attention.pending_approvals_count ?? inbox.pending_count ?? 0);
  const readyCount = attention.ready_queue_count ?? queue.ready_count ?? 0;
  const readyText = queue.available === false ? "Unavailable" : `${readyCount} ready`;
  const statusText = issues[0]
    || attention.primary_message
    || (summary.status === "ok" ? "Local supervised pipeline is visible." : "Supervised state is partially visible.");

  setText("dashboard-strip-decision", latest.decision || "No decision recorded yet");
  setText("dashboard-strip-action", summary.latest_proposed_action || latest.proposed_next_action || "No action proposed");
  setText("dashboard-strip-pending", pendingText);
  setText("dashboard-strip-ready", readyText);
  setText("dashboard-strip-status", statusText);
}

function renderDashboardRecentActivity(summary = {}) {
  const noteEl = document.getElementById("dashboard-activity-note");
  const listEl = document.getElementById("dashboard-activity-list");
  if (!noteEl || !listEl) {
    return;
  }

  const actions = [...uiState.localActions, ...uiState.serverActions].slice(0, 5);
  if (actions.length) {
    noteEl.textContent = `${actions.length} recent local console event${actions.length === 1 ? "" : "s"}.`;
    listEl.innerHTML = actions
      .map((action) => {
        const state = normalizeState(action.status || "info");
        return `
          <article class="approval-item compact-activity-item">
            <div class="approval-header">
              <strong>${escapeHtml(action.label || "Action")}</strong>
              <span class="state-pill state-${state}">${escapeHtml(action.status || state)}</span>
            </div>
            <div class="approval-body">
              <p>${escapeHtml(action.summary || "No summary.")}</p>
              <p class="approval-meta">${escapeHtml(formatTimeStamp(action.occurredAt))}</p>
            </div>
          </article>
        `;
      })
      .join("");
    return;
  }

  const timeline = Array.isArray(summary.compact_timeline_summary) ? summary.compact_timeline_summary.slice(0, 5) : [];
  if (!timeline.length) {
    noteEl.textContent = "No recent supervised timeline entries are visible yet.";
    listEl.innerHTML = '<p class="empty-state">No recent supervised activity yet.</p>';
    return;
  }

  noteEl.textContent = `${timeline.length} recent supervised lifecycle event${timeline.length === 1 ? "" : "s"}.`;
  listEl.innerHTML = timeline
    .map((entry) => `
      <article class="approval-item compact-activity-item">
        <div class="approval-header">
          <strong>${escapeHtml(String(entry.event || "event").replaceAll("_", " "))}</strong>
          <span class="console-badge">${escapeHtml(entry.source || "runtime")}</span>
        </div>
        <div class="approval-body">
          <p>${escapeHtml(entry.note || "No note recorded.")}</p>
          <p class="approval-meta">${escapeHtml((entry.timestamp_utc || "").replace("T", " ").replace("Z", " UTC"))}</p>
        </div>
      </article>
    `)
    .join("");
}

function renderDashboardErrors(summary = {}, payload = {}) {
  const noteEl = document.getElementById("dashboard-errors-note");
  const listEl = document.getElementById("dashboard-errors-list");
  if (!noteEl || !listEl) {
    return;
  }

  const issues = buildDashboardIssues(summary, payload);
  if (!issues.length) {
    noteEl.textContent = "No operator-facing warnings are visible right now.";
    listEl.innerHTML = '<p class="empty-state">No active errors or watchpoints.</p>';
    return;
  }

  noteEl.textContent = `${issues.length} watchpoint${issues.length === 1 ? "" : "s"} currently visible.`;
  listEl.innerHTML = issues
    .map((issue) => `
      <article class="approval-item compact-activity-item inline-watch-item">
        <div class="approval-header">
          <strong>Watchpoint</strong>
          <span class="state-pill state-error">review</span>
        </div>
        <div class="approval-body">
          <p>${escapeHtml(issue)}</p>
        </div>
      </article>
    `)
    .join("");
}

function renderDashboardFromControlCenter(payload = {}) {
  const summary = payload.summary || {};
  uiState.latestControlCenterSummary = summary;
  renderDashboardStrip(summary, payload);
  renderDashboardRecentActivity(summary);
  renderDashboardErrors(summary, payload);
  updateApprovalsTabBadge(summary);
}

async function refreshNeedsActionNow() {
  let payload;
  try {
    payload = await requestJson("/api/ghoti/control-center-state");
  } catch (err) {
    const message = "Needs-action state unavailable: " + err.message;
    setText("needs-action-message", message);
    renderDashboardStrip({
      attention_summary: { primary_message: message },
      latest_operator_state: uiState.latestControlCenterSummary?.latest_operator_state || {},
      latest_proposed_action: uiState.latestControlCenterSummary?.latest_proposed_action || "",
    });
    renderDashboardErrors({}, { error: err.message });
    return;
  }
  const s = payload.summary || {};
  const attn = s.attention_summary || {};
  const level = attn.attention_level || (payload.ok ? "none" : "warning");
  const banner = document.getElementById("needs-action-banner");
  if (banner) {
    banner.className = `needs-action-banner needs-action-${escapeHtml(level)}`;
  }
  setText("needs-action-message", attn.primary_message || "No attention summary available.");
  setText("needs-action-pending-count", attn.pending_approvals_count ?? "-");
  setText("needs-action-ready-count", attn.ready_queue_count ?? "-");
  const list = document.getElementById("needs-action-items");
  if (list) {
    const items = attn.action_items || [];
    list.innerHTML = items.length
      ? items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")
      : `<li class="empty-state">No action items.</li>`;
  }
  renderDashboardFromControlCenter(payload);
}

async function refreshCapabilities() {
  const payload = await requestJson("/api/capability-summary");
  renderCapabilitySummary(payload);
}

async function refreshGithubUpdates() {
  const payload = await requestJson("/api/github-updates");
  renderGithubUpdates(payload);
}

async function refreshSupervisorStatus() {
  const payload = await requestJson("/api/supervisor/status");
  renderSupervisorStatus(payload);
  const nextApprovalId =
    uiState.selectedApprovalId || payload.summary?.pendingApprovals?.[0]?.approvalId || "";
  const nextTaskId =
    uiState.selectedTaskId
    || payload.summary?.humanNeededTasks?.[0]?.taskId
    || payload.summary?.interruptedTasks?.[0]?.taskId
    || payload.summary?.waitingTasks?.[0]?.taskId
    || payload.summary?.readyToResumeTasks?.[0]?.taskId
    || "";
  if (nextApprovalId) {
    await refreshApprovalDetail(nextApprovalId, { silent: true });
  } else {
    clearApprovalDetail("No approval item selected. Pending requests will appear here when they exist.");
  }
  if (nextTaskId) {
    await refreshTaskDetail(nextTaskId, { silent: true });
  } else {
    clearTaskDetail("No stopped task selected. Human-needed, interrupted, waiting, or ready-to-resume tasks will appear here.");
  }
}

async function refreshExecutorTasks() {
  const payload = await requestJson("/api/executor/tasks");
  uiState.executorTasksPayload = payload;
  renderExecutorTaskCards(payload);
  renderRecipeTaskCards(payload);
  renderDesktopTaskCards(payload);

  const filteredTasks = applyTaskListFilters(payload.summary?.tasks || []).items;

  const nextTaskId =
    uiState.selectedTaskId
    || filteredTasks?.[0]?.taskId
    || payload.summary?.tasks?.[0]?.taskId
    || "";

  if (nextTaskId) {
    await refreshTaskDetail(nextTaskId, { silent: true });
  }

  return payload;
}

async function refreshPendingApprovals() {
  const payload = await requestJson("/api/approvals/pending");
  renderPendingApprovals(payload);
  const hasPendingApproval = (payload.summary?.requests || []).length > 0;
  if (!hasPendingApproval && !uiState.selectedApprovalId) {
    clearApprovalDetail("No pending approvals right now.");
  }
}

async function refreshApprovalDetail(approvalId, options = {}) {
  const { silent = false } = options;
  if (!approvalId) {
    clearApprovalDetail("No approval item selected.");
    return null;
  }

  try {
    const payload = await requestJson(`/api/approvals/item?approvalId=${encodeURIComponent(approvalId)}`);
    renderApprovalDetail(payload);
    if (!silent) {
      setResultPanel("approval-action-result", "success", "Approval details loaded.", approvalId);
    }
    return payload;
  } catch (error) {
    clearApprovalDetail("Approval details could not be loaded.");
    if (!silent) {
      setResultPanel("approval-action-result", "error", "Approval detail lookup failed.", error.message);
    }
    return null;
  }
}

async function refreshTaskDetail(taskId, options = {}) {
  const { silent = false } = options;
  if (!taskId) {
    clearTaskDetail("No task selected.");
    return null;
  }

  try {
    const payload = await requestJson(`/api/tasks/item?taskId=${encodeURIComponent(taskId)}`);
    renderTaskDetail(payload);
    if (!silent) {
      setResultPanel("task-action-result", "success", "Task details loaded.", taskId);
    }
    return payload;
  } catch (error) {
    clearTaskDetail("Task details could not be loaded.");
    if (!silent) {
      setResultPanel("task-action-result", "error", "Task detail lookup failed.", error.message);
    }
    return null;
  }
}

async function submitApprovalDecision(decision, button) {
  const approvalId = uiState.selectedApprovalId;
  if (!approvalId) {
    setResultPanel("approval-action-result", "error", "No approval selected.", "Pick a queue item first.");
    return null;
  }

  const note = document.getElementById("approval-decision-note")?.value || "";
  const actionLabelMap = {
    approve: "Approve approval",
    deny: "Deny approval",
    defer: "Defer approval",
  };
  const actionId = createLocalAction(
    actionLabelMap[decision] || "Update approval",
    `Submitting ${decision} decision for ${approvalId}.`,
  );
  setResultPanel("approval-action-result", "loading", "Submitting approval decision...", `${decision} ${approvalId}`);

  try {
    const result = await withButtonState(button, "Working...", () =>
      requestJson("/api/approvals/decision", {
        method: "POST",
        body: JSON.stringify({
          approvalId,
          decision,
          note,
        }),
      }),
    );

    if (result.approval) {
      renderApprovalDetail({
        summary: result.approval,
        raw: result.approvalRaw,
      });
    }
    setResultPanel(
      "approval-action-result",
      "success",
      result.summary?.headline || "Approval decision saved.",
      result.summary?.approvalId || approvalId,
    );
    updateLocalAction(actionId, "success", result.summary?.headline || "Approval decision saved.");
    await Promise.all([refreshSupervisorStatus(), refreshPendingApprovals(), refreshGhotiControlCenter(), refreshRecentActions()]);
    return result;
  } catch (error) {
    setResultPanel("approval-action-result", "error", "Approval decision failed.", error.message);
    updateLocalAction(actionId, "error", error.message);
    await refreshRecentActions();
    return null;
  }
}

async function submitTaskAction(action, button) {
  const taskId = uiState.selectedTaskId;
  if (!taskId) {
    setResultPanel("task-action-result", "error", "No task selected.", "Pick a stopped task first.");
    return null;
  }

  const note = document.getElementById("task-action-note")?.value || "";
  const actionLabelMap = {
    review: "Review task",
    resume: "Resume waiting task",
    requeue: "Re-queue task",
    execute: "Run allowlisted action",
  };
  const actionId = createLocalAction(
    actionLabelMap[action] || "Update task",
    `Submitting ${action} action for ${taskId}.`,
  );
  setResultPanel("task-action-result", "loading", "Submitting task action...", `${action} ${taskId}`);

  try {
    const result = await withButtonState(button, "Working...", () =>
      requestJson("/api/tasks/action", {
        method: "POST",
        body: JSON.stringify({
          taskId,
          action,
          note,
        }),
      }),
    );

    if (result.task) {
      renderTaskDetail({
        summary: result.task,
        raw: result.taskRaw,
      });
    }
    setResultPanel(
      "task-action-result",
      "success",
      result.summary?.headline || "Task action saved.",
      result.summary?.taskId || taskId,
    );
    updateLocalAction(actionId, "success", result.summary?.headline || "Task action saved.");
    await Promise.all([refreshSupervisorStatus(), refreshExecutorTasks(), refreshArtifacts(), refreshGhotiControlCenter(), refreshRecentActions()]);
    return result;
  } catch (error) {
    setResultPanel("task-action-result", "error", "Task action failed.", error.message);
    updateLocalAction(actionId, "error", error.message);
    await refreshRecentActions();
    return null;
  }
}

async function refreshArtifacts() {
  const payload = await requestJson("/api/artifacts");
  renderArtifacts(payload);

  const artifacts = payload.artifacts || [];
  if (artifacts.length === 0) {
    clearArtifactPreview("No recent artifacts found.");
    return payload;
  }

  const selectedArtifact = artifacts.find((artifact) => artifact.path === uiState.selectedArtifactPath);
  const preferredArtifact = selectedArtifact || artifacts.find((artifact) => artifact.previewable);
  if (preferredArtifact && preferredArtifact.previewable) {
    await previewArtifactPath(preferredArtifact.path, { silent: true });
  } else if (!uiState.selectedArtifactPath) {
    clearArtifactPreview("Recent artifacts exist, but none are previewable yet.");
  }

  return payload;
}

async function refreshRecentActions() {
  const payload = await requestJson("/api/recent-actions");
  renderRecentActions(payload);
}

async function refreshDesktopBridgeStatus() {
  const payload = await requestJson("/api/desktop-bridge/status");
  renderDesktopBridge(payload);
}

async function refreshHandoffTargetCandidates() {
  const payload = await requestJson("/api/desktop-bridge/handoff-targets");
  renderHandoffTargetCandidates(payload);
}

async function refreshConsole() {
  const results = await Promise.allSettled([
    refreshOperatorStatus(),
    refreshGhotiControlCenter(),
    refreshNeedsActionNow(),
    refreshPipelineState(),
    refreshPipelineItems(),
    refreshApprovalInbox(),
    refreshManualQueue(),
    refreshCapabilities(),
    refreshGithubUpdates(),
    refreshSupervisorStatus(),
    refreshPendingApprovals(),
    refreshExecutorTasks(),
    refreshArtifacts(),
    refreshDesktopBridgeStatus(),
    refreshHandoffTargetCandidates(),
    refreshRecentActions(),
  ]);

  const failures = results
    .filter((result) => result.status === "rejected")
    .map((result) => humanizeGhotiIssue(result.reason?.message || result.reason))
    .filter(Boolean);

  if (failures.length) {
    renderDashboardErrors(uiState.latestControlCenterSummary || {}, { error: failures.join(" ") });
  }

  return results;
}

function serializeForm(formId) {
  return Object.fromEntries(new FormData(document.getElementById(formId)).entries());
}

function getFormButton(formId) {
  return document.querySelector(`#${formId} button[type="submit"]`);
}

async function runRefresh(button, label, busyLabel, refreshFn, onError) {
  const actionId = createLocalAction(label, "Running local refresh.");
  try {
    await withButtonState(button, busyLabel, refreshFn);
    updateLocalAction(actionId, "success", `${label} finished successfully.`);
    await refreshRecentActions();
  } catch (error) {
    updateLocalAction(actionId, "error", error.message);
    if (typeof onError === "function") {
      onError(error);
    }
  }
}

async function runScaffold(formId, endpoint, summaryId, rawId, actionLabel, button) {
  const actionId = createLocalAction(actionLabel, "Generating local scaffold.");
  setResultPanel(summaryId, "loading", "Running action...", "Generating a local markdown artifact.");

  try {
    const payload = serializeForm(formId);
    const result = await withButtonState(button, "Working...", () =>
      requestJson(endpoint, {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    );
    const outputPath = result.summary?.outputPath || "Artifact created.";
    setResultPanel(summaryId, "success", result.summary?.headline || "Action complete.", outputPath);
    renderRaw(rawId, result);
    updateLocalAction(actionId, "success", result.summary?.headline || "Scaffold created.");
    await Promise.all([refreshArtifacts(), refreshGhotiControlCenter(), refreshRecentActions()]);
    return result;
  } catch (error) {
    setResultPanel(summaryId, "error", "Action failed.", error.message);
    renderRaw(rawId, { error: error.message });
    updateLocalAction(actionId, "error", error.message);
    await refreshRecentActions();
    return null;
  }
}

async function runExecutorQueue(payload, actionLabel, button, options = {}) {
  const panelId = options.panelId || "executor-queue-summary";
  const actionId = createLocalAction(actionLabel, "Queueing a safe repo-local executor task.");
  setResultPanel(panelId, "loading", "Queueing executor task...", actionLabel);

  try {
    const result = await withButtonState(button, "Working...", () =>
      requestJson("/api/executor/queue", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    );

    if (result.task) {
      renderTaskDetail({
        summary: result.task,
        raw: result.taskRaw,
      });
    }
    setResultPanel(
      panelId,
      "success",
      result.summary?.headline || "Executor task queued.",
      result.summary?.taskId || "task created",
    );
    updateLocalAction(actionId, "success", result.summary?.headline || "Executor task queued.");
    await Promise.all([refreshSupervisorStatus(), refreshExecutorTasks(), refreshArtifacts(), refreshGhotiControlCenter(), refreshRecentActions()]);
    return result;
  } catch (error) {
    setResultPanel(panelId, "error", "Executor task queue failed.", error.message);
    updateLocalAction(actionId, "error", error.message);
    await refreshRecentActions();
    return null;
  }
}

async function runBrowserAction(endpoint, summaryId, rawId, actionLabel, button, payload = {}) {
  const actionId = createLocalAction(actionLabel, "Running browser action.");
  setResultPanel(summaryId, "loading", "Running browser action...", "The local browser demo is starting now.");

  try {
    const result = await withButtonState(button, "Working...", () =>
      requestJson(endpoint, {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    );
    const detail = result.summary?.screenshotPath || result.summary?.outputPath || result.summary?.mode || "";
    setResultPanel(summaryId, "success", result.summary?.headline || "Browser action complete.", detail);
    renderRaw(rawId, result);
    updateLocalAction(actionId, "success", result.summary?.headline || "Browser action completed.");
    await Promise.all([refreshArtifacts(), refreshGhotiControlCenter(), refreshRecentActions()]);
    return result;
  } catch (error) {
    setResultPanel(summaryId, "error", "Browser action failed.", error.message);
    renderRaw(rawId, { error: error.message });
    updateLocalAction(actionId, "error", error.message);
    await refreshRecentActions();
    return null;
  }
}

async function runDesktopBridgeCheck(button) {
  const actionId = createLocalAction("Run desktop bridge check", "Running safe local desktop bridge check.");
  setResultPanel("desktop-check-summary", "loading", "Running desktop bridge check...", "Checking safe local shell and launcher foundations.");

  try {
    const result = await withButtonState(button, "Working...", () =>
      requestJson("/api/desktop-bridge/check", {
        method: "POST",
        body: "{}",
      }),
    );
    renderDesktopBridge(result);
    setResultPanel("desktop-check-summary", "success", result.summary?.headline || "Desktop bridge check completed.", result.summary?.mode || "check");
    updateLocalAction(actionId, "success", result.summary?.headline || "Desktop bridge check completed.");
    await refreshRecentActions();
    return result;
  } catch (error) {
    setResultPanel("desktop-check-summary", "error", "Desktop bridge check failed.", error.message);
    updateLocalAction(actionId, "error", error.message);
    await refreshRecentActions();
    return null;
  }
}

async function runGhotiQuickQueue(payload, actionLabel, button) {
  return runExecutorQueue(payload, actionLabel, button, { panelId: "ghoti-control-action-summary" });
}

document.getElementById("refresh-console").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Refresh console status",
    "Refreshing...",
    refreshConsole,
    (error) => {
      setText("operator-headline", "Console refresh failed.");
      setText("operator-next-step", error.message);
    },
  );
});

document.getElementById("ghoti-refresh-state").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Refresh Ghoti control center",
    "Refreshing...",
    () => Promise.all([refreshGhotiControlCenter(), refreshSupervisorStatus(), refreshExecutorTasks(), refreshArtifacts(), refreshRecentActions()]),
    (error) => {
      setResultPanel("ghoti-control-action-summary", "error", "Ghoti control-center refresh failed.", error.message);
    },
    { panelId: "ghoti-control-action-summary" },
  );
});

document.getElementById("refresh-github").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Refresh GitHub summary",
    "Refreshing...",
    () => Promise.all([refreshGithubUpdates(), refreshRecentActions()]),
    (error) => {
      setText("github-headline", "GitHub refresh failed.");
      setText("github-quick-note", error.message);
    },
  );
});

document.getElementById("refresh-github-panel").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Refresh GitHub panel",
    "Refreshing...",
    () => Promise.all([refreshGithubUpdates(), refreshRecentActions()]),
    (error) => {
      setText("github-headline", "GitHub panel refresh failed.");
      setText("github-quick-note", error.message);
    },
  );
});

document.getElementById("refresh-pipeline-items").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Refresh pipeline items",
    "Refreshing...",
    () => refreshPipelineItems(),
    (error) => {
      setText("pipeline-items-summary", "Pipeline items refresh failed: " + error.message);
    },
  );
});

document.getElementById("refresh-pipeline-state").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Refresh pipeline state",
    "Refreshing...",
    () => refreshPipelineState(),
    (error) => {
      setText("pipeline-state-summary", "Pipeline state refresh failed: " + error.message);
    },
  );
});

document.getElementById("refresh-supervisor").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Refresh supervisor status",
    "Refreshing...",
    () => Promise.all([refreshSupervisorStatus(), refreshPendingApprovals(), refreshGhotiControlCenter(), refreshRecentActions()]),
    (error) => {
      setText("supervisor-headline", "Supervisor refresh failed.");
      setText("supervisor-quick-note", error.message);
    },
  );
});

document.getElementById("refresh-executor-tasks").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Refresh executor tasks",
    "Refreshing...",
    () => Promise.all([refreshExecutorTasks(), refreshGhotiControlCenter(), refreshRecentActions()]),
    () => {
      setResultPanel("executor-queue-summary", "error", "Executor task refresh failed.", "Try the refresh again.");
    },
  );
});

document.getElementById("task-visibility-filter").addEventListener("change", () => {
  rerenderTaskListsFromState();
});

document.getElementById("task-recency-filter").addEventListener("change", () => {
  rerenderTaskListsFromState();
});

[
  "ghoti-task-visibility-filter",
  "ghoti-task-limit-filter",
  "ghoti-task-type-filter",
  "ghoti-task-status-filter",
  "ghoti-task-active-only",
].forEach((id) => {
  document.getElementById(id).addEventListener("change", async () => {
    try {
      await refreshGhotiControlCenter();
    } catch (error) {
      setResultPanel("ghoti-control-action-summary", "error", "Ghoti task filter refresh failed.", error.message);
    }
  });
});

document.getElementById("refresh-capabilities-panel").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Refresh capability summary",
    "Refreshing...",
    () => Promise.all([refreshCapabilities(), refreshRecentActions()]),
    (error) => {
      setText("capability-headline", "Capability refresh failed.");
      setText("capability-counts", error.message);
    },
  );
});

document.getElementById("refresh-desktop-bridge").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Refresh desktop bridge status",
    "Refreshing...",
    () => Promise.all([refreshDesktopBridgeStatus(), refreshRecentActions()]),
    (error) => {
      setText("desktop-headline", "Desktop bridge refresh failed.");
      setText("desktop-quick-note", error.message);
    },
  );
});

document.getElementById("refresh-artifacts").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Refresh recent artifacts",
    "Refreshing...",
    () => Promise.all([refreshArtifacts(), refreshGhotiControlCenter(), refreshRecentActions()]),
    () => {
      clearArtifactPreview("Artifact refresh failed.");
    },
  );
});

document.getElementById("ghoti-show-approvals").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Show pending approvals",
    "Refreshing...",
    async () => {
      await Promise.all([refreshSupervisorStatus(), refreshPendingApprovals(), refreshGhotiControlCenter(), refreshRecentActions()]);
      scrollToElement("pending-approvals-list");
    },
    (error) => {
      setResultPanel("ghoti-control-action-summary", "error", "Pending approval refresh failed.", error.message);
    },
    { panelId: "ghoti-control-action-summary" },
  );
});

document.getElementById("ghoti-show-active-tasks").addEventListener("click", async (event) => {
  document.getElementById("ghoti-task-visibility-filter").value = "actionable";
  document.getElementById("ghoti-task-type-filter").value = "all";
  document.getElementById("ghoti-task-status-filter").value = "all";
  document.getElementById("ghoti-task-limit-filter").value = "12";
  document.getElementById("ghoti-task-active-only").checked = true;
  await runRefresh(
    event.currentTarget,
    "Show active and recent tasks",
    "Refreshing...",
    async () => {
      await Promise.all([refreshGhotiControlCenter(), refreshExecutorTasks(), refreshRecentActions()]);
      scrollToElement("ghoti-actionable-task-list");
    },
    (error) => {
      setResultPanel("ghoti-control-action-summary", "error", "Active task refresh failed.", error.message);
    },
    { panelId: "ghoti-control-action-summary" },
  );
});

document.getElementById("ghoti-show-artifacts").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Show recent artifacts",
    "Refreshing...",
    async () => {
      await Promise.all([refreshArtifacts(), refreshGhotiControlCenter(), refreshRecentActions()]);
      scrollToElement("artifacts-output");
    },
    (error) => {
      setResultPanel("ghoti-control-action-summary", "error", "Artifact refresh failed.", error.message);
    },
    { panelId: "ghoti-control-action-summary" },
  );
});

document.getElementById("ghoti-queue-observe-desktop").addEventListener("click", async (event) => {
  await runGhotiQuickQueue(
    buildRecipeQueuePayload("observe_desktop_state"),
    "Queue desktop observation",
    event.currentTarget,
  );
});

document.getElementById("ghoti-queue-clipboard-read").addEventListener("click", async (event) => {
  await runGhotiQuickQueue(
    { actionType: "get_clipboard_text" },
    "Queue clipboard read",
    event.currentTarget,
  );
});

document.getElementById("ghoti-queue-clipboard-write").addEventListener("click", async (event) => {
  await runGhotiQuickQueue(
    {
      actionType: "set_clipboard_text",
      content: getInputValue("ghoti-quick-clipboard-text"),
    },
    "Queue clipboard write",
    event.currentTarget,
  );
});

document.getElementById("ghoti-queue-focus-window").addEventListener("click", async (event) => {
  await runGhotiQuickQueue(
    {
      actionType: "focus_window",
      target: getInputValue("ghoti-quick-focus-window") || "terminal",
    },
    "Queue focus window",
    event.currentTarget,
  );
});

document.getElementById("ghoti-run-runtime-checker").addEventListener("click", async (event) => {
  await runGhotiQuickQueue(
    { actionType: "run_checker", target: "runtime" },
    "Queue runtime checker",
    event.currentTarget,
  );
});

document.getElementById("ghoti-run-dashboard-checker").addEventListener("click", async (event) => {
  await runGhotiQuickQueue(
    { actionType: "run_checker", target: "dashboard" },
    "Queue dashboard checker",
    event.currentTarget,
  );
});

document.getElementById("ghoti-queue-handoff").addEventListener("click", async (event) => {
  persistHandoffTargetPreferences();
  await runGhotiQuickQueue(
    buildRecipeQueuePayload("codex_to_chatgpt_handoff_mvp", buildCodexChatGptHandoffOptions()),
    "Queue Codex to ChatGPT handoff",
    event.currentTarget,
  );
});

document.getElementById("internship-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  await runScaffold(
    "internship-form",
    "/api/scaffold/internship",
    "internship-summary",
    "internship-raw",
    "Generate internship pack",
    event.submitter || getFormButton("internship-form"),
  );
});

document.getElementById("showcase-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  await runScaffold(
    "showcase-form",
    "/api/scaffold/showcase",
    "showcase-summary",
    "showcase-raw",
    "Generate showcase case study",
    event.submitter || getFormButton("showcase-form"),
  );
});

document.getElementById("portfolio-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  await runScaffold(
    "portfolio-form",
    "/api/scaffold/portfolio",
    "portfolio-summary",
    "portfolio-raw",
    "Generate portfolio project page",
    event.submitter || getFormButton("portfolio-form"),
  );
});

document.getElementById("executor-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = serializeForm("executor-form");
  await runExecutorQueue(
    payload,
    `Queue ${payload.actionType || "executor"} action`,
    event.submitter || getFormButton("executor-form"),
  );
});

document.getElementById("run-browser-smoke").addEventListener("click", async (event) => {
  await runBrowserAction(
    "/api/browser/smoke",
    "browser-smoke-summary",
    "browser-smoke-raw",
    "Run headless browser demo",
    event.currentTarget,
  );
});

document.getElementById("queue-runtime-checker").addEventListener("click", async (event) => {
  await runExecutorQueue(
    { actionType: "run_checker", target: "runtime" },
    "Queue runtime checker",
    event.currentTarget,
  );
});

document.getElementById("queue-dashboard-checker").addEventListener("click", async (event) => {
  await runExecutorQueue(
    { actionType: "run_checker", target: "dashboard" },
    "Queue dashboard checker",
    event.currentTarget,
  );
});

document.getElementById("queue-git-status").addEventListener("click", async (event) => {
  await runExecutorQueue(
    { actionType: "git_status" },
    "Queue git status summary",
    event.currentTarget,
  );
});

document.getElementById("queue-git-diff").addEventListener("click", async (event) => {
  await runExecutorQueue(
    { actionType: "git_diff" },
    "Queue git diff summary",
    event.currentTarget,
  );
});

document.getElementById("queue-desktop-list-windows").addEventListener("click", async (event) => {
  await runExecutorQueue(
    { actionType: "list_windows" },
    "Queue desktop window list",
    event.currentTarget,
    { panelId: "desktop-action-summary" },
  );
});

document.getElementById("queue-desktop-active-window").addEventListener("click", async (event) => {
  await runExecutorQueue(
    { actionType: "get_active_window" },
    "Queue active window check",
    event.currentTarget,
    { panelId: "desktop-action-summary" },
  );
});

document.getElementById("queue-desktop-focus-terminal").addEventListener("click", async (event) => {
  await runExecutorQueue(
    { actionType: "focus_window", target: "terminal" },
    "Queue focus terminal",
    event.currentTarget,
    { panelId: "desktop-action-summary" },
  );
});

document.getElementById("queue-desktop-focus-vscode").addEventListener("click", async (event) => {
  await runExecutorQueue(
    { actionType: "focus_window", target: "vscode" },
    "Queue focus VS Code",
    event.currentTarget,
    { panelId: "desktop-action-summary" },
  );
});

document.getElementById("queue-desktop-open-terminal").addEventListener("click", async (event) => {
  await runExecutorQueue(
    { actionType: "open_allowed_app", target: "terminal" },
    "Queue open terminal",
    event.currentTarget,
    { panelId: "desktop-action-summary" },
  );
});

document.getElementById("queue-desktop-screenshot").addEventListener("click", async (event) => {
  await runExecutorQueue(
    { actionType: "capture_desktop_screenshot" },
    "Queue desktop screenshot",
    event.currentTarget,
    { panelId: "desktop-action-summary" },
  );
});

document.getElementById("queue-desktop-read-clipboard").addEventListener("click", async (event) => {
  await runExecutorQueue(
    { actionType: "get_clipboard_text" },
    "Queue clipboard read",
    event.currentTarget,
    { panelId: "desktop-action-summary" },
  );
});

document.getElementById("queue-desktop-set-clipboard").addEventListener("click", async (event) => {
  await runExecutorQueue(
    {
      actionType: "set_clipboard_text",
      content: getInputValue("desktop-clipboard-text"),
    },
    "Queue clipboard write",
    event.currentTarget,
    { panelId: "desktop-action-summary" },
  );
});

document.getElementById("queue-desktop-copy-selection").addEventListener("click", async (event) => {
  await runExecutorQueue(
    { actionType: "copy_selection" },
    "Queue copy selection",
    event.currentTarget,
    { panelId: "desktop-action-summary" },
  );
});

document.getElementById("queue-desktop-paste-clipboard").addEventListener("click", async (event) => {
  await runExecutorQueue(
    { actionType: "paste_clipboard" },
    "Queue paste clipboard",
    event.currentTarget,
    { panelId: "desktop-action-summary" },
  );
});

document.getElementById("queue-desktop-hotkey").addEventListener("click", async (event) => {
  await runExecutorQueue(
    {
      actionType: "send_hotkey",
      target: buildHotkeyTarget(),
    },
    "Queue allowlisted hotkey",
    event.currentTarget,
    { panelId: "desktop-action-summary" },
  );
});

document.getElementById("queue-desktop-wait-seconds").addEventListener("click", async (event) => {
  await runExecutorQueue(
    {
      actionType: "wait_seconds",
      target: getInputValue("desktop-wait-seconds") || "2",
    },
    "Queue explicit wait",
    event.currentTarget,
    { panelId: "desktop-action-summary" },
  );
});

document.getElementById("queue-desktop-wait-window").addEventListener("click", async (event) => {
  await runExecutorQueue(
    {
      actionType: "wait_for_window",
      target: getInputValue("desktop-wait-window") || "terminal",
    },
    "Queue wait for window",
    event.currentTarget,
    { panelId: "desktop-action-summary" },
  );
});

document.getElementById("queue-desktop-move-mouse").addEventListener("click", async (event) => {
  await runExecutorQueue(
    {
      actionType: "move_mouse",
      target: buildMouseTarget(),
    },
    "Queue mouse move",
    event.currentTarget,
    { panelId: "desktop-action-summary" },
  );
});

document.getElementById("queue-desktop-left-click").addEventListener("click", async (event) => {
  await runExecutorQueue(
    {
      actionType: "left_click",
      target: buildMouseTarget(),
    },
    "Queue left click",
    event.currentTarget,
    { panelId: "desktop-action-summary" },
  );
});

document.getElementById("queue-desktop-double-click").addEventListener("click", async (event) => {
  await runExecutorQueue(
    {
      actionType: "double_click",
      target: buildMouseTarget(),
    },
    "Queue double click",
    event.currentTarget,
    { panelId: "desktop-action-summary" },
  );
});

document.getElementById("queue-desktop-right-click").addEventListener("click", async (event) => {
  await runExecutorQueue(
    {
      actionType: "right_click",
      target: buildMouseTarget(),
    },
    "Queue right click",
    event.currentTarget,
    { panelId: "desktop-action-summary" },
  );
});

document.getElementById("queue-desktop-scroll").addEventListener("click", async (event) => {
  await runExecutorQueue(
    {
      actionType: "scroll_mouse",
      target: buildScrollTarget(),
    },
    "Queue mouse scroll",
    event.currentTarget,
    { panelId: "desktop-action-summary" },
  );
});

document.getElementById("queue-recipe-observe-desktop").addEventListener("click", async (event) => {
  await runExecutorQueue(
    buildRecipeQueuePayload("observe_desktop_state"),
    "Queue observe desktop state recipe",
    event.currentTarget,
    { panelId: "recipe-action-summary" },
  );
});

document.getElementById("queue-recipe-focus-terminal").addEventListener("click", async (event) => {
  await runExecutorQueue(
    buildRecipeQueuePayload("focus_or_reuse_terminal"),
    "Queue focus or reuse terminal recipe",
    event.currentTarget,
    { panelId: "recipe-action-summary" },
  );
});

document.getElementById("queue-recipe-copy-focused").addEventListener("click", async (event) => {
  await runExecutorQueue(
    buildRecipeQueuePayload("copy_from_focused_window"),
    "Queue copy from focused window recipe",
    event.currentTarget,
    { panelId: "recipe-action-summary" },
  );
});

document.getElementById("queue-recipe-paste-dashboard").addEventListener("click", async (event) => {
  await runExecutorQueue(
    buildRecipeQueuePayload("paste_into_target_window", { targetWindow: "dashboard_browser" }),
    "Queue paste into dashboard browser recipe",
    event.currentTarget,
    { panelId: "recipe-action-summary" },
  );
});

document.getElementById("queue-recipe-wait-step").addEventListener("click", async (event) => {
  await runExecutorQueue(
    buildRecipeQueuePayload("wait_and_resume_operator_step", { waitSeconds: 2 }),
    "Queue wait and resume operator step recipe",
    event.currentTarget,
    { panelId: "recipe-action-summary" },
  );
});

document.getElementById("queue-recipe-codex-handoff").addEventListener("click", async (event) => {
  persistHandoffTargetPreferences();
  await runExecutorQueue(
    buildRecipeQueuePayload("codex_to_chatgpt_handoff_mvp", buildCodexChatGptHandoffOptions()),
    "Queue Codex to ChatGPT handoff recipe",
    event.currentTarget,
    { panelId: "recipe-action-summary" },
  );
});

document.getElementById("refresh-handoff-targets").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Refresh handoff target candidates",
    "Refreshing visible Codex and ChatGPT targets...",
    () => refreshHandoffTargetCandidates(),
    (error) => {
      setText("handoff-target-summary", error.message);
    },
    { panelId: "recipe-action-summary" },
  );
});

document.getElementById("handoff-remember-targets").addEventListener("change", () => {
  persistHandoffTargetPreferences();
  updateHandoffTargetPreferenceNote();
});

document.getElementById("handoff-source-candidate").addEventListener("change", () => {
  if (shouldRememberHandoffTargetSelections()) {
    persistHandoffTargetPreferences();
    updateHandoffTargetPreferenceNote();
  }
});

document.getElementById("handoff-target-candidate").addEventListener("change", () => {
  if (shouldRememberHandoffTargetSelections()) {
    persistHandoffTargetPreferences();
    updateHandoffTargetPreferenceNote();
  }
});

document.getElementById("run-browser-visible").addEventListener("click", async (event) => {
  await runBrowserAction(
    "/api/browser/visible",
    "browser-visible-summary",
    "browser-visible-raw",
    "Run visible browser demo",
    event.currentTarget,
  );
});

document.getElementById("run-desktop-bridge-check").addEventListener("click", async (event) => {
  await runDesktopBridgeCheck(event.currentTarget);
});

document.getElementById("quick-internship").addEventListener("click", async (event) => {
  await runScaffold(
    "internship-form",
    "/api/scaffold/internship",
    "internship-summary",
    "internship-raw",
    "Generate internship pack",
    event.currentTarget,
  );
});

document.getElementById("quick-showcase").addEventListener("click", async (event) => {
  await runScaffold(
    "showcase-form",
    "/api/scaffold/showcase",
    "showcase-summary",
    "showcase-raw",
    "Generate showcase case study",
    event.currentTarget,
  );
});

document.getElementById("quick-portfolio").addEventListener("click", async (event) => {
  await runScaffold(
    "portfolio-form",
    "/api/scaffold/portfolio",
    "portfolio-summary",
    "portfolio-raw",
    "Generate portfolio project page",
    event.currentTarget,
  );
});

document.getElementById("quick-browser-smoke").addEventListener("click", async (event) => {
  await runBrowserAction(
    "/api/browser/smoke",
    "browser-smoke-summary",
    "browser-smoke-raw",
    "Run headless browser demo",
    event.currentTarget,
  );
});

document.getElementById("quick-browser-visible").addEventListener("click", async (event) => {
  await runBrowserAction(
    "/api/browser/visible",
    "browser-visible-summary",
    "browser-visible-raw",
    "Run visible browser demo",
    event.currentTarget,
  );
});

document.getElementById("quick-desktop-check").addEventListener("click", async (event) => {
  await runDesktopBridgeCheck(event.currentTarget);
});

document.getElementById("refresh-needs-action").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Refresh needs-action panel",
    "Refreshing...",
    () => refreshNeedsActionNow(),
    (error) => {
      setText("needs-action-message", "Needs-action refresh failed: " + error.message);
    },
  );
});

document.getElementById("needs-action-goto-approvals").addEventListener("click", () => {
  scrollToElement("ghoti-approval-inbox-panel");
});

document.getElementById("needs-action-goto-queue").addEventListener("click", () => {
  scrollToElement("ghoti-manual-queue-panel");
});

document.getElementById("refresh-approval-inbox").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Refresh approval inbox",
    "Refreshing...",
    () => refreshApprovalInbox(),
    (error) => {
      setText("approval-inbox-summary", "Approval inbox refresh failed: " + error.message);
    },
  );
});

document.getElementById("approval-inbox-reject-confirm").addEventListener("click", async () => {
  const form = document.getElementById("approval-inbox-reject-form");
  const approvalId = form ? form.dataset.pendingId : "";
  const reason = document.getElementById("approval-inbox-reject-reason").value.trim();
  if (!approvalId) return;
  if (!reason) {
    const resultEl = document.getElementById("approval-inbox-action-result");
    if (resultEl) resultEl.textContent = "Reason is required to reject.";
    return;
  }
  if (form) form.style.display = "none";
  await rejectInboxItem(approvalId, reason);
});

document.getElementById("approval-inbox-reject-cancel").addEventListener("click", () => {
  const form = document.getElementById("approval-inbox-reject-form");
  if (form) form.style.display = "none";
});

document.getElementById("refresh-manual-queue").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Refresh manual queue",
    "Refreshing...",
    () => refreshManualQueue(),
    (error) => {
      setText("manual-queue-summary", "Manual queue refresh failed: " + error.message);
    },
  );
});

document.getElementById("manual-queue-review-confirm").addEventListener("click", async () => {
  const form = document.getElementById("manual-queue-review-form");
  const itemId = form ? form.dataset.pendingId : "";
  const note = document.getElementById("manual-queue-review-note").value.trim();
  if (!itemId) return;
  if (!note) {
    const resultEl = document.getElementById("manual-queue-action-result");
    if (resultEl) resultEl.textContent = "Operator note is required to mark reviewed.";
    return;
  }
  if (form) form.style.display = "none";
  await submitQueueReview(itemId, note);
});

document.getElementById("manual-queue-review-cancel").addEventListener("click", () => {
  const form = document.getElementById("manual-queue-review-form");
  if (form) form.style.display = "none";
});

document.getElementById("refresh-audit-trace").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Load audit trace",
    "Loading...",
    () => refreshAuditTrace(),
    (error) => {
      setText("audit-trace-summary", "Audit trace failed: " + error.message);
    },
  );
});

document.getElementById("artifacts-output").addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-artifact-action]");
  if (!button) {
    return;
  }

  const artifactAction = button.getAttribute("data-artifact-action");
  const artifactPath = button.getAttribute("data-artifact-path");
  if (!artifactPath) {
    return;
  }

  if (artifactAction === "preview") {
    await previewArtifactPath(artifactPath, { button });
    return;
  }

  if (artifactAction === "open" || artifactAction === "reveal") {
    await runArtifactFileAction(artifactAction, artifactPath, button);
  }
});

document.getElementById("pending-approvals-list").addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-approval-action='inspect']");
  if (!button) {
    return;
  }

  const approvalId = button.getAttribute("data-approval-id");
  if (!approvalId) {
    return;
  }

  const actionId = createLocalAction("Inspect approval", `Loading details for ${approvalId}.`);
  setResultPanel("approval-action-result", "loading", "Loading approval details...", approvalId);
  const result = await withButtonState(button, "Loading...", () => refreshApprovalDetail(approvalId));
  if (result) {
    updateLocalAction(actionId, "success", `Loaded approval details for ${approvalId}.`);
  } else {
    updateLocalAction(actionId, "error", `Approval detail lookup failed for ${approvalId}.`);
  }
  await refreshRecentActions();
});

[
  "human-needed-list",
  "interrupted-tasks-list",
  "waiting-tasks-list",
  "ready-to-resume-list",
  "ghoti-actionable-task-list",
  "ghoti-failure-task-list",
].forEach((containerId) => {
  document.getElementById(containerId).addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-task-action='inspect']");
    if (!button) {
      return;
    }

    const taskId = button.getAttribute("data-task-id");
    if (!taskId) {
      return;
    }

    const actionId = createLocalAction("Inspect task", `Loading details for ${taskId}.`);
    setResultPanel("task-action-result", "loading", "Loading task details...", taskId);
    const result = await withButtonState(button, "Loading...", () => refreshTaskDetail(taskId));
    if (result) {
      updateLocalAction(actionId, "success", `Loaded task details for ${taskId}.`);
    } else {
      updateLocalAction(actionId, "error", `Task detail lookup failed for ${taskId}.`);
    }
    await refreshRecentActions();
  });
});

document.getElementById("executor-task-list").addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-task-action='inspect']");
  if (!button) {
    return;
  }

  const taskId = button.getAttribute("data-task-id");
  if (!taskId) {
    return;
  }

  const actionId = createLocalAction("Inspect executor task", `Loading details for ${taskId}.`);
  setResultPanel("task-action-result", "loading", "Loading task details...", taskId);
  const result = await withButtonState(button, "Loading...", () => refreshTaskDetail(taskId));
  if (result) {
    updateLocalAction(actionId, "success", `Loaded executor task ${taskId}.`);
  } else {
    updateLocalAction(actionId, "error", `Executor task detail lookup failed for ${taskId}.`);
  }
  await refreshRecentActions();
});

document.getElementById("desktop-task-list").addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-task-action='inspect']");
  if (!button) {
    return;
  }

  const taskId = button.getAttribute("data-task-id");
  if (!taskId) {
    return;
  }

  const actionId = createLocalAction("Inspect desktop task", `Loading details for ${taskId}.`);
  setResultPanel("task-action-result", "loading", "Loading task details...", taskId);
  const result = await withButtonState(button, "Loading...", () => refreshTaskDetail(taskId));
  if (result) {
    updateLocalAction(actionId, "success", `Loaded desktop task ${taskId}.`);
  } else {
    updateLocalAction(actionId, "error", `Desktop task detail lookup failed for ${taskId}.`);
  }
  await refreshRecentActions();
});

document.getElementById("recipe-task-list").addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-task-action='inspect']");
  if (!button) {
    return;
  }

  const taskId = button.getAttribute("data-task-id");
  if (!taskId) {
    return;
  }

  const actionId = createLocalAction("Inspect recipe task", `Loading details for ${taskId}.`);
  setResultPanel("task-action-result", "loading", "Loading task details...", taskId);
  const result = await withButtonState(button, "Loading...", () => refreshTaskDetail(taskId));
  if (result) {
    updateLocalAction(actionId, "success", `Loaded recipe task ${taskId}.`);
  } else {
    updateLocalAction(actionId, "error", `Recipe task detail lookup failed for ${taskId}.`);
  }
  await refreshRecentActions();
});

document.getElementById("approval-approve").addEventListener("click", async (event) => {
  await submitApprovalDecision("approve", event.currentTarget);
});

document.getElementById("approval-deny").addEventListener("click", async (event) => {
  await submitApprovalDecision("deny", event.currentTarget);
});

document.getElementById("approval-defer").addEventListener("click", async (event) => {
  await submitApprovalDecision("defer", event.currentTarget);
});

document.getElementById("task-review").addEventListener("click", async (event) => {
  await submitTaskAction("review", event.currentTarget);
});

document.getElementById("task-resume").addEventListener("click", async (event) => {
  await submitTaskAction("resume", event.currentTarget);
});

document.getElementById("task-requeue").addEventListener("click", async (event) => {
  await submitTaskAction("requeue", event.currentTarget);
});

document.getElementById("task-execute").addEventListener("click", async (event) => {
  await submitTaskAction("execute", event.currentTarget);
});

clearApprovalDetail("Select a pending approval to inspect it.");
clearTaskDetail("Select a stopped, interrupted, or executor task to inspect it.");
document.getElementById("handoff-remember-targets").checked = loadHandoffTargetPreferences().rememberSelectedCandidates;
updateHandoffTargetPreferenceNote();
initConsoleTabs();
renderDashboardRecentActivity({});
renderDashboardErrors({}, {});

refreshConsole().catch((error) => {
  setText("operator-headline", "Console load failed.");
  setText("operator-next-step", error.message);
  renderDashboardStrip({
    attention_summary: { primary_message: error.message },
    latest_operator_state: {},
    latest_proposed_action: "",
  }, { error: error.message });
  renderDashboardErrors({}, { error: error.message });
});

// --- Ghoti Active Mode ---

const ACTIVE_PILL_CLASSES = ["ghoti-active-pill-off","ghoti-active-pill-on","ghoti-active-pill-listening","ghoti-active-pill-processing","ghoti-active-pill-waiting","ghoti-active-pill-error"];

function renderActiveModeState(state) {
  if (!state) return;
  const pill = document.getElementById("ghoti-active-pill");
  const rail = document.getElementById("ghoti-active-mode-rail");
  const railLabel = document.getElementById("ghoti-active-rail-label");
  const lastEvent = document.getElementById("ghoti-active-last-event");
  const snapshotPreview = document.getElementById("ghoti-active-snapshot-preview");
  const snapshotLink = document.getElementById("ghoti-active-snapshot-link");

  const mode = (state.mode || "idle").toLowerCase();
  const active = Boolean(state.active);

  // pill label + class
  const modeLabels = { idle: "OFF — idle", active: "ACTIVE — screen view on", listening: "LISTENING", processing: "PROCESSING", waiting_for_approval: "WAITING — approval needed", stopped: "STOPPED", error: "ERROR" };
  const modeClasses = { idle: "ghoti-active-pill-off", active: "ghoti-active-pill-on", listening: "ghoti-active-pill-listening", processing: "ghoti-active-pill-processing", waiting_for_approval: "ghoti-active-pill-waiting", stopped: "ghoti-active-pill-off", error: "ghoti-active-pill-error" };
  if (pill) {
    ACTIVE_PILL_CLASSES.forEach(c => pill.classList.remove(c));
    pill.classList.add(modeClasses[mode] || "ghoti-active-pill-off");
    pill.textContent = modeLabels[mode] || mode.toUpperCase();
  }

  // top rail
  if (rail && railLabel) {
    rail.classList.toggle("is-active", active);
    railLabel.textContent = active ? "Ghoti active — screen view on" : "Ghoti idle";
  }

  // last event timestamp
  if (lastEvent && state.last_event_utc) {
    try { lastEvent.textContent = new Date(state.last_event_utc).toLocaleTimeString(); } catch { lastEvent.textContent = state.last_event_utc; }
  }

  // snapshot preview
  if (snapshotPreview && snapshotLink && state.last_snapshot_path) {
    snapshotPreview.hidden = false;
    snapshotLink.textContent = state.last_snapshot_path;
    snapshotLink.href = "/" + state.last_snapshot_path;
  } else if (snapshotPreview) {
    snapshotPreview.hidden = true;
  }

  if (state.error) {
    setActiveFeedback("Error: " + state.error, true);
  }
}

function setActiveFeedback(msg, isError) {
  const el = document.getElementById("ghoti-active-feedback");
  if (!el) return;
  el.textContent = msg;
  el.style.color = isError ? "#c0392b" : "#1a7f4b";
}

async function refreshActiveModeState() {
  try {
    const data = await requestJson("/api/ghoti/active-state");
    renderActiveModeState(data.state);
  } catch (err) {
    setActiveFeedback("Could not load active state: " + err.message, true);
  }
}

async function activeModePost(endpoint, body) {
  try {
    const resp = await fetch(endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: body ? JSON.stringify(body) : undefined });
    const data = await resp.json();
    renderActiveModeState(data.state);
    return data;
  } catch (err) {
    setActiveFeedback("Request failed: " + err.message, true);
    return null;
  }
}

document.getElementById("ghoti-active-start-btn").addEventListener("click", async () => {
  setActiveFeedback("Starting Ghoti Active Mode...", false);
  const data = await activeModePost("/api/ghoti/active/start");
  if (data && data.ok) {
    setActiveFeedback("Ghoti Active Mode started. Visible indicator is now shown.", false);
    refreshActiveSessionData();
  }
});

document.getElementById("ghoti-active-stop-btn").addEventListener("click", async () => {
  setActiveFeedback("Stopping Ghoti Active Mode...", false);
  const data = await activeModePost("/api/ghoti/active/stop");
  if (data && data.ok) {
    setActiveFeedback("Ghoti Active Mode stopped.", false);
    refreshActiveSessionData();
  }
});

document.getElementById("ghoti-active-snapshot-btn").addEventListener("click", async () => {
  setActiveFeedback("Capturing screenshot...", false);
  const data = await activeModePost("/api/ghoti/active/snapshot");
  if (data && data.ok) setActiveFeedback("Screenshot captured: " + data.snapshotPath, false);
  else if (data && data.error) setActiveFeedback("Snapshot failed: " + data.error, true);
});

document.getElementById("ghoti-active-send-btn").addEventListener("click", async () => {
  const input = document.getElementById("ghoti-active-msg-input");
  const msg = input ? input.value.trim() : "";
  if (!msg) { setActiveFeedback("Enter an instruction before sending.", true); return; }
  setActiveFeedback("Sending instruction...", false);
  const data = await activeModePost("/api/ghoti/active/message", { message: msg });
  if (data && data.ok) {
    setActiveFeedback("Instruction received. " + (data.note || ""), false);
    if (input) input.value = "";
  } else if (data && data.error) {
    setActiveFeedback("Failed: " + data.error, true);
  }
});

// Poll active state every 6 seconds
refreshActiveModeState();
setInterval(refreshActiveModeState, 6000);

// --- Continuous Screen Capture UI ---

let activeCaptureSessionId = null;

function buildSessionLatestFrameUrl(sessionId) {
  if (!sessionId) return "/api/ghoti/active/latest-frame";
  return `/api/ghoti/active/latest-frame?session_id=${encodeURIComponent(sessionId)}`;
}

function buildSessionFrameUrl(sessionId, frameName) {
  if (!sessionId || !frameName) return "";
  return `/api/ghoti/active/frame?name=${encodeURIComponent(frameName)}&session_id=${encodeURIComponent(sessionId)}`;
}

const CAPTURE_PILL_CLASSES = ["ghoti-capture-pill-off", "ghoti-capture-pill-on", "ghoti-capture-pill-error"];

function renderCaptureState(captureState) {
  if (!captureState) return;
  activeCaptureSessionId = captureState.session_id || null;
  const pill = document.getElementById("ghoti-capture-pill");
  const meta = document.getElementById("ghoti-capture-meta");
  const fpsEl = document.getElementById("ghoti-capture-fps");
  const countEl = document.getElementById("ghoti-capture-count");
  const timeEl = document.getElementById("ghoti-capture-time");
  const previewRow = document.getElementById("ghoti-capture-preview-row");
  const latestLink = document.getElementById("ghoti-capture-latest-link");
  const latestImg = document.getElementById("ghoti-capture-latest-img");
  const errorEl = document.getElementById("ghoti-capture-error");

  const capturing = Boolean(captureState.capturing);

  if (pill) {
    CAPTURE_PILL_CLASSES.forEach(c => pill.classList.remove(c));
    if (captureState.error && !capturing) {
      pill.classList.add("ghoti-capture-pill-error");
      pill.textContent = "ERROR";
    } else if (capturing) {
      pill.classList.add("ghoti-capture-pill-on");
      pill.textContent = "CAPTURING";
    } else {
      pill.classList.add("ghoti-capture-pill-off");
      pill.textContent = "OFF";
    }
  }

  if (meta) meta.hidden = !capturing && !captureState.frame_count;
  if (fpsEl) fpsEl.textContent = `FPS target: ${captureState.fps_target || 1}`;
  if (countEl) countEl.textContent = `Frames: ${captureState.frame_count || 0}`;
  if (timeEl && captureState.latest_frame_utc) {
    try { timeEl.textContent = `Last: ${new Date(captureState.latest_frame_utc).toLocaleTimeString()}`; }
    catch { timeEl.textContent = captureState.latest_frame_utc; }
  }

  const hasFrames = captureState.frame_count > 0;
  if (previewRow) {
    previewRow.hidden = !hasFrames;
  }
  if (hasFrames && latestLink && latestImg) {
    const latestBase = buildSessionLatestFrameUrl(captureState.session_id);
    const frameUrl = latestBase + (latestBase.includes("?") ? "&" : "?") + "t=" + Date.now();
    latestLink.href = latestBase;
    latestLink.textContent = capturing ? "Capture running — Latest frame" : "Capture stopped — Latest frame";
    latestImg.src = frameUrl;
    latestImg.hidden = false;
    latestImg.alt = capturing ? "Live screen preview" : "Last captured frame";
  } else if (latestImg) {
    latestImg.hidden = true;
  }

  if (errorEl) {
    if (captureState.error) {
      errorEl.textContent = "Capture error: " + captureState.error;
      errorEl.hidden = false;
    } else {
      errorEl.hidden = true;
    }
  }
}

function getActiveSessionReviewStatus(session) {
  return session?.reviewed ? "Reviewed" : "Pending";
}

function getActiveSessionRetentionStatus(session) {
  switch (String(session?.retention_status || "default").toLowerCase()) {
    case "kept":
      return "Kept";
    case "discarded":
      return "Discarded";
    default:
      return "Default";
  }
}

function renderCurrentActiveSession(session) {
  const empty = document.getElementById("ghoti-session-empty");
  const current = document.getElementById("ghoti-session-current");
  const badge = document.getElementById("ghoti-session-status-badge");
  if (!empty || !current || !badge) {
    return;
  }

  ACTIVE_PILL_CLASSES.forEach((cls) => badge.classList.remove(cls));

  if (!session || !session.session_id) {
    empty.hidden = false;
    current.hidden = true;
    badge.classList.add("ghoti-active-pill-off");
    badge.textContent = "IDLE";
    setText("ghoti-session-reviewed", "Pending");
    setText("ghoti-session-retention", "Default");
    setText("ghoti-session-note", "Capture stays local-only and only starts when you explicitly press Start Screen Capture.");
    return;
  }

  empty.hidden = true;
  current.hidden = false;
  const statusLabel = session.status === "stopped"
    ? "STOPPED"
    : session.capture_running ? "ACTIVE + CAPTURE" : "ACTIVE";
  badge.classList.add(
    session.status === "stopped"
      ? "ghoti-active-pill-off"
      : session.capture_running ? "ghoti-active-pill-on" : "ghoti-active-pill-waiting"
  );
  badge.textContent = statusLabel;

  setText("ghoti-session-id", session.session_id);
  setText("ghoti-session-started", session.started_at_utc ? formatTimeStamp(session.started_at_utc) : "—");
  setText("ghoti-session-stopped", session.stopped_at_utc ? formatTimeStamp(session.stopped_at_utc) : "—");
  setText("ghoti-session-frame-count", String(session.frame_count || 0));
  setText("ghoti-session-reviewed", session.reviewed_at_utc ? `${getActiveSessionReviewStatus(session)} · ${formatTimeStamp(session.reviewed_at_utc)}` : getActiveSessionReviewStatus(session));
  setText("ghoti-session-retention", getActiveSessionRetentionStatus(session));

  const baseNote = session.capture_running
    ? "Capture is currently running locally. Stop Screen Capture to freeze the latest gallery."
    : session.status === "stopped"
      ? "This session is closed. The gallery below shows the most recent locally retained frames from it."
      : "Ghoti is active, but capture is still off until the operator explicitly starts it.";
  const reviewNote = session.review_note ? `Review note: ${session.review_note}` : "";
  const retentionNote = session.retention_status === "discarded"
    ? "Discard only affects the local archive label. It does not delete capture files."
    : session.retention_status === "kept"
      ? "This session is explicitly marked to keep in the local archive."
      : "Retention is still on the default local setting.";
  setText("ghoti-session-note", [baseNote, retentionNote, reviewNote].filter(Boolean).join(" "));
}

function renderRecentActiveSessions(sessions) {
  const empty = document.getElementById("ghoti-session-history-empty");
  const container = document.getElementById("ghoti-session-history");
  if (!empty || !container) {
    return;
  }

  const items = Array.isArray(sessions) ? sessions : [];
  if (!items.length) {
    empty.hidden = false;
    container.hidden = true;
    container.innerHTML = "";
    return;
  }

  empty.hidden = true;
  container.hidden = false;
  container.innerHTML = items.map((session) => {
    const statusText = session.status === "stopped"
      ? "Stopped"
      : session.capture_running ? "Active + capture" : "Active";
    const badgeClass = session.status === "stopped"
      ? "ghoti-active-pill-off"
      : session.capture_running ? "ghoti-active-pill-on" : "ghoti-active-pill-waiting";
    const reviewStatus = session.reviewed_at_utc
      ? `${getActiveSessionReviewStatus(session)} · ${formatTimeStamp(session.reviewed_at_utc)}`
      : getActiveSessionReviewStatus(session);
    const retentionStatus = getActiveSessionRetentionStatus(session);
    const reviewLabel = session.reviewed ? "Update review" : "Mark reviewed";
    const reviewPlaceholder = session.reviewed
      ? "Update the local review note for this session"
      : "Optional local review note for this session";

    const cleanupStatus = session.cleanup_status === "cleaned" ? "Cleaned" : (session.retention_status === "discarded" ? "Pending" : "—");
    const cleanupDetail = session.cleanup_status === "cleaned" && session.cleaned_file_count != null
      ? ` · ${escapeHtml(String(session.cleaned_file_count))} file(s), ${escapeHtml(((session.cleaned_bytes || 0) / 1024).toFixed(1))} KB`
      : "";
    const approxSizeHint = session.frame_count ? ` · ~${escapeHtml(String(session.frame_count))} frame(s)` : "";

    const showCleanupBtn = session.status === "stopped"
      && session.retention_status === "discarded"
      && session.cleanup_status !== "cleaned";

    const isLegacySession = !session.frame_dir && (session.frame_count > 0 || session.capture_method);
    const legacyNote = isLegacySession
      ? `<p class="summary-note" style="font-size:0.81rem;margin-bottom:0.4rem;">Legacy capture session — captured before per-session folder isolation. Cleanup may have zero files or may be unavailable.</p>`
      : "";

    return `
      <article class="ghoti-session-history-item" data-session-id="${escapeHtml(session.session_id || "")}">
        <div class="ghoti-session-history-top">
          <strong class="ghoti-session-history-id">${escapeHtml((session.session_id || "session").slice(0, 28))}</strong>
          <span class="state-pill ${badgeClass}">${escapeHtml(statusText)}</span>
        </div>
        <div class="ghoti-session-history-meta">
          <span>Started <strong>${escapeHtml(session.started_at_utc ? formatTimeStamp(session.started_at_utc) : "—")}</strong></span>
          <span>Stopped <strong>${escapeHtml(session.stopped_at_utc ? formatTimeStamp(session.stopped_at_utc) : "—")}</strong></span>
          <span>Frames <strong>${escapeHtml(String(session.frame_count || 0))}${approxSizeHint}</strong></span>
          <span>Reviewed <strong>${escapeHtml(reviewStatus)}</strong></span>
          <span>Retention <strong>${escapeHtml(retentionStatus)}</strong></span>
          <span>Cleanup <strong>${escapeHtml(cleanupStatus)}${cleanupDetail}</strong></span>
        </div>
        <label class="ghoti-session-review-field">
          <span>Review note</span>
          <textarea class="ghoti-session-review-note" data-session-id="${escapeHtml(session.session_id || "")}" rows="2" placeholder="${escapeHtml(reviewPlaceholder)}">${escapeHtml(session.review_note || "")}</textarea>
        </label>
        ${legacyNote}
        <div class="ghoti-session-history-actions">
          <button class="button-secondary ghoti-session-action-btn" type="button" data-active-session-action="review" data-session-id="${escapeHtml(session.session_id || "")}">${escapeHtml(reviewLabel)}</button>
          <button class="button-secondary ghoti-session-action-btn" type="button" data-active-session-action="keep" data-session-id="${escapeHtml(session.session_id || "")}">Keep session</button>
          <button class="button-secondary ghoti-session-action-btn" type="button" data-active-session-action="discard" data-session-id="${escapeHtml(session.session_id || "")}">Discard metadata</button>
          ${showCleanupBtn ? `<button class="button-secondary ghoti-session-action-btn" type="button" data-active-session-action="cleanup-preview" data-session-id="${escapeHtml(session.session_id || "")}">Preview cleanup</button>` : ""}
        </div>
        <p class="ghoti-session-retention-copy">
          <strong>Discard</strong> = metadata status only — no files deleted.
          <strong>Preview cleanup</strong> = shows what would be deleted (only after Discard).
          <strong>Confirm cleanup</strong> = requires typing <code>DELETE_CAPTURE_FRAMES</code> — deletes only <code>frame-XXXXXX.png</code> files in this session's folder. <code>latest.png</code> is preserved. Other sessions are untouched. Cleanup never runs automatically.
        </p>
        <div class="ghoti-session-cleanup-area" data-session-id="${escapeHtml(session.session_id || "")}" style="margin-top:0.6rem;" hidden></div>
      </article>
    `;
  }).join("");
}

function renderActiveSessionFrames(payload) {
  const empty = document.getElementById("ghoti-capture-gallery-empty");
  const gallery = document.getElementById("ghoti-capture-gallery");
  if (!empty || !gallery) {
    return;
  }

  const frames = Array.isArray(payload?.frames) ? payload.frames : [];
  if (!frames.length) {
    empty.hidden = false;
    gallery.hidden = true;
    gallery.innerHTML = "";
    return;
  }

  const cacheBust = Date.now();
  const gallerySessionId = payload.session_id || null;
  const isLegacy = payload.session?.legacy_capture;

  empty.hidden = true;
  gallery.hidden = false;

  const legacyNote = isLegacy
    ? `<p class="summary-note" style="font-size:0.82rem;margin-bottom:0.5rem;">Legacy capture session; frame URLs may not be available after per-session isolation.</p>`
    : "";

  gallery.innerHTML = legacyNote + frames.map((frame) => {
    let baseUrl = gallerySessionId && frame.filename
      ? buildSessionFrameUrl(gallerySessionId, frame.filename)
      : String(frame.image_url || frame.url || "");
    const imageUrl = baseUrl ? `${baseUrl}${baseUrl.includes("?") ? "&" : "?"}t=${cacheBust}` : "";
    const label = frame.captured_at_utc ? formatTimeStamp(frame.captured_at_utc) : (frame.filename || "Captured frame");
    return `
      <a class="ghoti-capture-gallery-item" href="${escapeHtml(baseUrl || "#")}" target="_blank" rel="noopener">
        <img src="${escapeHtml(imageUrl)}" alt="${escapeHtml(frame.filename || "Captured frame")}" loading="lazy" />
        <span>${escapeHtml(label)}</span>
      </a>
    `;
  }).join("");
}

async function updateActiveSessionArchive(action, sessionId, reviewNote = "") {
  const normalizedId = String(sessionId || "").trim();
  if (!normalizedId) {
    setActiveFeedback("Session action failed: session id is missing.", true);
    return;
  }

  const routeMap = {
    review: "/api/ghoti/active/session/review",
    keep: "/api/ghoti/active/session/keep",
    discard: "/api/ghoti/active/session/discard",
  };
  const route = routeMap[action];
  if (!route) {
    return;
  }

  const payload = { session_id: normalizedId };
  if (action === "review") {
    payload.review_note = String(reviewNote || "");
  }

  const pendingMessage = action === "review"
    ? "Saving local session review..."
    : action === "keep"
      ? "Marking session kept locally..."
      : "Marking session discarded in local metadata...";
  setActiveFeedback(pendingMessage, false);

  try {
    const data = await requestJson(route, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    if (!data?.ok) {
      throw new Error(data?.error || "Session archive update failed.");
    }
    const successMessage = action === "review"
      ? "Session review saved locally."
      : action === "keep"
        ? "Session marked kept locally."
        : "Session marked discarded in metadata. No files were deleted.";
    setActiveFeedback(successMessage, false);
    await refreshActiveSessionData();
  } catch (error) {
    setActiveFeedback(`Session action failed: ${error.message}`, true);
  }
}

async function refreshActiveSessionData() {
  try {
    const [currentData, sessionsData, framesData] = await Promise.all([
      requestJson("/api/ghoti/active/session"),
      requestJson("/api/ghoti/active/sessions"),
      requestJson("/api/ghoti/active/frames"),
    ]);
    renderCurrentActiveSession(currentData.session);
    renderRecentActiveSessions(sessionsData.sessions);
    renderActiveSessionFrames(framesData);
  } catch (err) {
    console.warn("Could not load active session data:", err);
  }
}

async function refreshCaptureState() {
  try {
    const data = await requestJson("/api/ghoti/active/capture-state");
    renderCaptureState(data.captureState);
  } catch { /* silent */ }
}

async function handleCleanupPreview(sessionId) {
  const container = document.querySelector(`.ghoti-session-cleanup-area[data-session-id="${CSS.escape(sessionId)}"]`);
  if (!container) {
    return;
  }
  container.hidden = false;
  container.innerHTML = "<p style=\"color:var(--muted);font-size:0.85rem;\">Loading cleanup preview...</p>";
  try {
    const data = await requestJson(`/api/ghoti/active/session/cleanup-preview?session_id=${encodeURIComponent(sessionId)}`);
    if (!data.deletion_allowed) {
      container.innerHTML = `<div class="result-panel is-error"><p>${escapeHtml(data.reason || "Cleanup not allowed.")}</p></div>`;
      return;
    }
    const filesSample = (data.files || []).slice(0, 5).map((f) => escapeHtml(f)).join(", ");
    const moreCount = (data.files || []).length > 5 ? ` and ${(data.files || []).length - 5} more` : "";
    const sizeKb = ((data.total_bytes || 0) / 1024).toFixed(1);
    container.innerHTML = `
      <div class="result-panel">
        <p><strong>Cleanup preview</strong> — ${escapeHtml(String(data.file_count || 0))} frame file(s) · ${escapeHtml(sizeKb)} KB total</p>
        ${data.file_count > 0 ? `<p style="font-size:0.82rem;color:var(--muted);">Files: ${filesSample}${moreCount}</p>` : "<p style=\"font-size:0.82rem;color:var(--muted);\">No frame files found in capture folder.</p>"}
        <p style="font-size:0.81rem;color:var(--muted);">Safety root: ${escapeHtml(data.safety_root || "")}</p>
        <p class="summary-note" style="margin-top:0.6rem;font-size:0.82rem;">
          Cleanup deletes only <code>frame-XXXXXX.png</code> files from this session's folder. <code>latest.png</code> is preserved. Other session folders are not affected. Cleanup never runs automatically.
        </p>
        <div style="display:grid;gap:0.55rem;margin-top:0.75rem;">
          <label style="display:grid;gap:0.3rem;font-weight:600;font-size:0.85rem;">
            <span>Type <code>DELETE_CAPTURE_FRAMES</code> to confirm</span>
            <input type="text" class="ghoti-cleanup-confirm-input" placeholder="DELETE_CAPTURE_FRAMES" autocomplete="off" />
          </label>
          <button class="button-danger ghoti-session-action-btn" type="button" data-active-session-action="cleanup-confirm" data-session-id="${escapeHtml(sessionId)}">Confirm cleanup</button>
        </div>
        <div class="ghoti-cleanup-result" aria-live="polite" style="margin-top:0.5rem;"></div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="result-panel is-error"><p>Preview failed: ${escapeHtml(err.message)}</p></div>`;
  }
}

async function handleCleanupConfirm(sessionId, articleEl) {
  const cleanupArea = articleEl ? articleEl.querySelector(".ghoti-session-cleanup-area") : null;
  const confirmInput = cleanupArea ? cleanupArea.querySelector(".ghoti-cleanup-confirm-input") : null;
  const resultEl = cleanupArea ? cleanupArea.querySelector(".ghoti-cleanup-result") : null;
  const phrase = confirmInput ? confirmInput.value.trim() : "";
  if (resultEl) {
    resultEl.innerHTML = "<p style=\"color:var(--muted);font-size:0.85rem;\">Sending cleanup request...</p>";
  }
  try {
    const data = await requestJson("/api/ghoti/active/session/cleanup-confirm", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, confirm: phrase }),
    });
    if (data.ok) {
      const sizeKb = ((data.deleted_bytes || 0) / 1024).toFixed(1);
      const missingNote = data.missing_count ? ` ${escapeHtml(String(data.missing_count))} already missing.` : "";
      if (resultEl) {
        resultEl.innerHTML = `<div class="result-panel is-success"><p>Cleanup complete. ${escapeHtml(String(data.deleted_count || 0))} file(s) deleted (${escapeHtml(sizeKb)} KB).${missingNote}</p></div>`;
      }
      await refreshActiveSessionData();
    }
  } catch (err) {
    if (resultEl) {
      resultEl.innerHTML = `<div class="result-panel is-error"><p>Cleanup failed: ${escapeHtml(err.message)}</p></div>`;
    }
  }
}

const ghotiSessionHistory = document.getElementById("ghoti-session-history");
if (ghotiSessionHistory) {
  ghotiSessionHistory.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-active-session-action]");
    if (!button) {
      return;
    }

    const action = String(button.dataset.activeSessionAction || "").trim();
    const sessionId = String(button.dataset.sessionId || button.closest("[data-session-id]")?.dataset.sessionId || "").trim();
    const sessionCard = button.closest("[data-session-id]");
    const noteField = sessionCard?.querySelector(".ghoti-session-review-note");
    const reviewNote = noteField ? noteField.value : "";

    if (action === "cleanup-preview") {
      await handleCleanupPreview(sessionId);
      return;
    }
    if (action === "cleanup-confirm") {
      await handleCleanupConfirm(sessionId, sessionCard);
      return;
    }
    await updateActiveSessionArchive(action, sessionId, reviewNote);
  });
}

document.getElementById("ghoti-capture-start-btn").addEventListener("click", async () => {
  setActiveFeedback("Starting continuous screen capture...", false);
  try {
    const resp = await fetch("/api/ghoti/active/capture/start", { method: "POST", headers: { "Content-Type": "application/json" } });
    const data = await resp.json();
    if (data.ok) {
      setActiveFeedback("Screen capture started.", false);
      renderCaptureState(data.captureState);
      refreshActiveSessionData();
    } else {
      setActiveFeedback("Cannot start capture: " + (data.error || "unknown error"), true);
    }
  } catch (err) {
    setActiveFeedback("Request failed: " + err.message, true);
  }
});

document.getElementById("ghoti-capture-stop-btn").addEventListener("click", async () => {
  setActiveFeedback("Stopping screen capture...", false);
  try {
    const resp = await fetch("/api/ghoti/active/capture/stop", { method: "POST", headers: { "Content-Type": "application/json" } });
    const data = await resp.json();
    if (data.ok) {
      setActiveFeedback("Screen capture stopped.", false);
      renderCaptureState(data.captureState);
      refreshActiveSessionData();
    } else {
      setActiveFeedback("Stop failed: " + (data.error || "unknown"), true);
    }
  } catch (err) {
    setActiveFeedback("Request failed: " + err.message, true);
  }
});

refreshCaptureState();
refreshActiveSessionData();
setInterval(refreshCaptureState, 4000);
setInterval(refreshActiveSessionData, 4000);

setInterval(() => {
  const img = document.getElementById("ghoti-capture-latest-img");
  if (img && !img.hidden) {
    const base = buildSessionLatestFrameUrl(activeCaptureSessionId);
    img.src = base + (base.includes("?") ? "&" : "?") + "t=" + Date.now();
  }
}, 2000);

