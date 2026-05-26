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
  activeConsoleView: "overview",
  drawerMode: "",
  handoffTargetPreferences: {
    rememberSelectedCandidates: false,
    sourceCandidateId: "",
    targetCandidateId: "",
  },
};
const HANDOFF_TARGET_PREFERENCES_KEY = "ghoti.handoffTargetPreferences.v1";
const CONSOLE_TAB_STORAGE_KEY = "ghoti.consoleActiveTab.v1";
const CONSOLE_TABS = ["dashboard", "approvals", "pipeline", "control", "tools", "system", "active"];
const CONSOLE_VIEWS = [
  "overview",
  "active-mode",
  "approvals",
  "executor",
  "desktop",
  "browser",
  "artifacts",
  "personal-ops",
  "github",
  "system",
];

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
  return {
    rememberSelectedCandidates: Boolean(uiState.handoffTargetPreferences?.rememberSelectedCandidates),
    sourceCandidateId: String(uiState.handoffTargetPreferences?.sourceCandidateId || ""),
    targetCandidateId: String(uiState.handoffTargetPreferences?.targetCandidateId || ""),
  };
}

function saveHandoffTargetPreferences(preferences) {
  uiState.handoffTargetPreferences = {
    rememberSelectedCandidates: Boolean(preferences?.rememberSelectedCandidates),
    sourceCandidateId: String(preferences?.sourceCandidateId || ""),
    targetCandidateId: String(preferences?.targetCandidateId || ""),
  };
}

function clearHandoffTargetPreferences() {
  uiState.handoffTargetPreferences = {
    rememberSelectedCandidates: false,
    sourceCandidateId: "",
    targetCandidateId: "",
  };
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
  return CONSOLE_TABS.includes(uiState.activeConsoleTab) ? uiState.activeConsoleTab : "";
}

function storeConsoleTab(tabName) {
  uiState.activeConsoleTab = CONSOLE_TABS.includes(tabName) ? tabName : "dashboard";
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

  const mappedView = getConsoleViewForTarget(targetId, element);
  if (mappedView) {
    setActiveConsoleView(mappedView, { focus: false });
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

const TARGET_VIEW_BY_ID = {
  "ghoti-audit-trace-panel": "approvals",
  "ghoti-approval-inbox-panel": "approvals",
  "ghoti-manual-queue-panel": "approvals",
  "pending-approvals-list": "executor",
  "human-needed-list": "executor",
  "waiting-tasks-list": "executor",
  "ready-to-resume-list": "executor",
  "interrupted-tasks-list": "executor",
  "executor-task-list": "executor",
  "desktop-task-list": "desktop",
  "recipe-task-list": "browser",
  "artifacts-output": "artifacts",
  "section-active": "active-mode",
  "section-approvals": "approvals",
  "section-health": "system",
  "section-observer": "system",
  "section-voice": "system",
  "section-youtube": "system",
  "section-runbook": "system",
  "section-about": "system",
};

function getConsoleViewForTarget(targetId, element = null) {
  const mapped = TARGET_VIEW_BY_ID[targetId];
  if (mapped) {
    return mapped;
  }

  const target = element || document.getElementById(targetId);
  if (!target) {
    return "";
  }

  const explicitPanel = target.closest("[data-console-view-panel]");
  if (explicitPanel?.dataset?.consoleViewPanel) {
    return explicitPanel.dataset.consoleViewPanel;
  }

  const currentSection = target.closest(".content-section");
  if (!currentSection) {
    return "";
  }
  return TARGET_VIEW_BY_ID[currentSection.id] || "";
}

function setActiveConsoleView(viewName, options = {}) {
  const nextView = CONSOLE_VIEWS.includes(viewName) ? viewName : "overview";
  uiState.activeConsoleView = nextView;

  document.querySelectorAll(".console-nav-item[data-console-view]").forEach((button) => {
    const isActive = button.dataset.consoleView === nextView;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-current", isActive ? "page" : "false");
  });

  document.querySelectorAll("[data-console-view-panel]").forEach((panel) => {
    const isActive = panel.dataset.consoleViewPanel === nextView;
    panel.hidden = !isActive;
    panel.classList.toggle("is-active", isActive);
  });

  if (options.focus !== false) {
    document.querySelector(`.console-nav-item[data-console-view="${nextView}"]`)?.focus();
  }
}

function updateTopbarMeta(branchText = "", commitText = "") {
  const branchEl = document.getElementById("topbar-branch");
  const commitEl = document.getElementById("topbar-commit");
  if (branchEl && branchText) {
    branchEl.textContent = branchText;
  }
  if (commitEl && commitText) {
    commitEl.textContent = commitText;
  }
}

function closeConsoleDrawer() {
  const drawer = document.getElementById("console-detail-drawer");
  if (!drawer) {
    return;
  }
  drawer.hidden = true;
  drawer.setAttribute("aria-hidden", "true");
  drawer.classList.remove("is-open");
  document.body.classList.remove("drawer-open");
  uiState.drawerMode = "";
  document.querySelectorAll(".console-drawer-panel").forEach((panel) => {
    panel.hidden = true;
  });
}

function openConsoleDrawer(mode, title, kicker = "Details") {
  const drawer = document.getElementById("console-detail-drawer");
  if (!drawer) {
    return;
  }
  uiState.drawerMode = mode;
  document.getElementById("console-drawer-kicker")?.replaceChildren(document.createTextNode(kicker));
  document.getElementById("console-drawer-title")?.replaceChildren(document.createTextNode(title));
  document.querySelectorAll(".console-drawer-panel").forEach((panel) => {
    panel.hidden = panel.id !== `console-drawer-${mode}`;
  });
  drawer.hidden = false;
  drawer.setAttribute("aria-hidden", "false");
  drawer.classList.add("is-open");
  document.body.classList.add("drawer-open");
}

function createConsoleCard(title, description = "", options = {}) {
  const article = document.createElement("section");
  article.className = `console-subcard ${options.className || ""}`.trim();
  if (options.id) {
    article.id = options.id;
  }

  if (title || description) {
    const header = document.createElement("div");
    header.className = "console-subcard-header";

    const copy = document.createElement("div");
    if (title) {
      const heading = document.createElement("h3");
      heading.textContent = title;
      copy.appendChild(heading);
    }
    if (description) {
      const note = document.createElement("p");
      note.textContent = description;
      copy.appendChild(note);
    }
    header.appendChild(copy);
    article.appendChild(header);
  }

  const body = document.createElement("div");
  body.className = `console-subcard-body ${options.bodyClass || ""}`.trim();
  article.appendChild(body);
  return { article, body };
}

function mountNodeById(id, target) {
  const node = document.getElementById(id);
  if (!node || !target) {
    return null;
  }
  target.appendChild(node);
  return node;
}

function mountNodes(ids, target) {
  ids.forEach((id) => {
    mountNodeById(id, target);
  });
}

function appendFieldRows(target, rows) {
  rows.forEach((row) => {
    const nodeIds = Array.isArray(row.ids) ? row.ids : [row.id];
    const present = nodeIds
      .map((id) => document.getElementById(id))
      .filter(Boolean);
    if (!present.length) {
      return;
    }

    const item = document.createElement("div");
    item.className = "console-data-row";
    const label = document.createElement("span");
    label.className = "console-data-label";
    label.textContent = row.label;
    const value = document.createElement("div");
    value.className = "console-data-value";
    present.forEach((node) => value.appendChild(node));
    item.append(label, value);
    target.appendChild(item);
  });
}

function appendDebugDetails(target, title, ids) {
  const details = document.createElement("details");
  details.className = "console-debug-details";
  const summary = document.createElement("summary");
  summary.textContent = title;
  details.appendChild(summary);
  const body = document.createElement("div");
  body.className = "console-debug-body";
  mountNodes(ids, body);
  details.appendChild(body);
  target.appendChild(details);
}

function mountDashboardUxShell() {
  const stagingRoot = document.getElementById("ui-staging-root");
  if (!stagingRoot || stagingRoot.dataset.mounted === "true") {
    return;
  }
  stagingRoot.dataset.mounted = "true";

  mountNodeById("section-overview", document.getElementById("overview-section-slot"));
  mountNodeById("section-active", document.getElementById("active-mode-slot"));
  mountNodeById("section-approvals", document.getElementById("approvals-slot"));
  mountNodeById("section-health", document.getElementById("system-health-slot"));

  const overviewDashboardSlot = document.getElementById("overview-dashboard-slot");
  if (overviewDashboardSlot) {
    const needsActionCard = createConsoleCard("Needs Action Now", "Pending approvals, ready queue items, and operator-required next steps.");
    mountNodeById("ghoti-needs-action-panel", needsActionCard.body);
    overviewDashboardSlot.appendChild(needsActionCard.article);

    const activityCard = createConsoleCard("Recent activity", "Latest local and supervised lifecycle events.");
    mountNodes(["dashboard-activity-note", "dashboard-activity-list"], activityCard.body);
    overviewDashboardSlot.appendChild(activityCard.article);

    const errorCard = createConsoleCard("Recent activity / errors", "Human-readable warnings stay visible. Debug stays in dedicated blocks.");
    mountNodes(["dashboard-errors-note", "dashboard-errors-list"], errorCard.body);
    overviewDashboardSlot.appendChild(errorCard.article);

    const summaryCard = createConsoleCard("Operator summary", "Cross-surface summary text from the existing runtime reads.");
    appendFieldRows(summaryCard.body, [
      { label: "Operator", id: "operator-headline" },
      { label: "Next step", id: "operator-next-step" },
      { label: "Supervisor", id: "supervisor-headline" },
      { label: "Supervisor note", id: "supervisor-quick-note" },
      { label: "Capabilities", id: "capability-headline" },
      { label: "Capability counts", id: "capability-counts" },
      { label: "GitHub", id: "github-headline" },
      { label: "GitHub note", id: "github-quick-note" },
      { label: "Desktop", id: "desktop-headline" },
      { label: "Desktop note", id: "desktop-quick-note" },
    ]);
    overviewDashboardSlot.appendChild(summaryCard.article);
  }

  const overviewPipelineSlot = document.getElementById("overview-pipeline-slot");
  if (overviewPipelineSlot) {
    const stripCard = createConsoleCard("Pipeline strip", "Decision, proposed action, and counts from the supervised control-center state.");
    appendFieldRows(stripCard.body, [
      { label: "Decision", id: "dashboard-strip-decision" },
      { label: "Action", id: "dashboard-strip-action" },
      { label: "Pending", id: "dashboard-strip-pending" },
      { label: "Ready", id: "dashboard-strip-ready" },
      { label: "Status", id: "dashboard-strip-status" },
    ]);
    overviewPipelineSlot.appendChild(stripCard.article);

    const pipelineCard = createConsoleCard("Pipeline state", "Recent pipeline status and visible items.");
    appendFieldRows(pipelineCard.body, [
      { label: "Operator decision", id: "pipeline-operator-decision" },
      { label: "Proposed action", id: "pipeline-proposed-action" },
      { label: "Pending approvals", id: "pipeline-pending-approvals" },
      { label: "Approved", id: "pipeline-approved-count" },
      { label: "Ready", id: "pipeline-ready-items" },
      { label: "Reviewed", id: "pipeline-reviewed-items" },
      { label: "Latest approved", id: "pipeline-latest-approved-id" },
      { label: "Latest ready", id: "pipeline-latest-ready-id" },
    ]);
    mountNodes(["pipeline-state-summary", "pipeline-items-summary", "pipeline-items-list"], pipelineCard.body);
    overviewPipelineSlot.appendChild(pipelineCard.article);
  }

  const executorSupervisorSlot = document.getElementById("executor-supervisor-slot");
  if (executorSupervisorSlot) {
    const supervisorCard = createConsoleCard("Supervisor state", "Legacy stopped-task lifecycle for human-needed queue management.");
    appendFieldRows(supervisorCard.body, [
      { label: "Status", id: "supervisor-status" },
      { label: "Pending approvals", id: "supervisor-pending-count" },
      { label: "Human needed", id: "supervisor-human-needed-count" },
      { label: "Waiting", id: "supervisor-waiting-count" },
      { label: "Ready", id: "supervisor-ready-count" },
      { label: "Interrupted", id: "supervisor-interrupted-count" },
    ]);
    mountNodes(["supervisor-summary", "pending-approvals-list", "human-needed-list", "waiting-tasks-list", "ready-to-resume-list", "interrupted-tasks-list"], supervisorCard.body);
    executorSupervisorSlot.appendChild(supervisorCard.article);
  }

  const executorQueueSlot = document.getElementById("executor-queue-slot");
  if (executorQueueSlot) {
    const queueCard = createConsoleCard("Repo executor queue", "Inline queue form plus dense repo-local task list.");
    mountNodes(["executor-form", "executor-queue-summary", "executor-task-list"], queueCard.body);
    appendDebugDetails(queueCard.body, "Executor raw debug", ["executor-raw"]);
    executorQueueSlot.appendChild(queueCard.article);
  }

  const desktopStatusSlot = document.getElementById("desktop-status-slot");
  if (desktopStatusSlot) {
    const statusCard = createConsoleCard("Desktop bridge", "Status only. Narrow desktop-aware actions only.");
    appendFieldRows(statusCard.body, [
      { label: "Summary", id: "desktop-summary" },
      { label: "PowerShell", id: "desktop-powershell" },
      { label: "Shell command", id: "desktop-shell" },
      { label: "Launcher", id: "desktop-launcher" },
      { label: "Desktop control", id: "desktop-control" },
      { label: "Failsafe", id: "desktop-failsafe" },
      { label: "Terminal windows", id: "desktop-terminal-windows" },
      { label: "PowerShell processes", id: "desktop-powershell-processes" },
      { label: "Node processes", id: "desktop-node-processes" },
      { label: "Python processes", id: "desktop-python-processes" },
      { label: "Ollama", id: "desktop-ollama" },
    ]);
    mountNodes(["desktop-resource-summary", "desktop-available-list", "desktop-missing-list"], statusCard.body);
    desktopStatusSlot.appendChild(statusCard.article);
  }

  const desktopControlsSlot = document.getElementById("desktop-controls-slot");
  if (desktopControlsSlot) {
    const controlsCard = createConsoleCard("Desktop queue controls", "Inline operator-triggered desktop queue controls.");
    mountNodes([
      "queue-desktop-list-windows",
      "queue-desktop-active-window",
      "queue-desktop-focus-terminal",
      "queue-desktop-focus-vscode",
      "queue-desktop-open-terminal",
      "queue-desktop-screenshot",
      "queue-desktop-read-clipboard",
      "queue-desktop-copy-selection",
      "queue-desktop-paste-clipboard",
      "desktop-clipboard-text",
      "queue-desktop-set-clipboard",
      "desktop-hotkey-window",
      "desktop-hotkey-value",
      "queue-desktop-hotkey",
      "desktop-wait-seconds",
      "queue-desktop-wait-seconds",
      "desktop-wait-window",
      "queue-desktop-wait-window",
      "desktop-mouse-window",
      "desktop-mouse-mode",
      "desktop-mouse-x",
      "desktop-mouse-y",
      "queue-desktop-move-mouse",
      "queue-desktop-left-click",
      "queue-desktop-double-click",
      "queue-desktop-right-click",
      "desktop-scroll-delta",
      "queue-desktop-scroll",
      "desktop-action-summary",
      "desktop-task-list",
      "run-desktop-bridge-check",
      "desktop-check-summary",
    ], controlsCard.body);
    appendDebugDetails(controlsCard.body, "Desktop debug output", ["desktop-raw"]);
    desktopControlsSlot.appendChild(controlsCard.article);
  }

  const browserStatusSlot = document.getElementById("browser-status-slot");
  if (browserStatusSlot) {
    const note = document.createElement("p");
    note.className = "console-honest-note";
    note.textContent = "Overlay is browser-based, not a native always-on-top desktop window.";
    browserStatusSlot.appendChild(note);

    const browserCard = createConsoleCard("Browser truth", "Current browser readiness and relay metadata. Scaffold features stay marked as scaffold.");
    appendFieldRows(browserCard.body, [
      { label: "Browser-use installed", id: "ghoti-browser-use-installed" },
      { label: "Browser-use ready", id: "ghoti-browser-use-ready" },
      { label: "Playwright ready", id: "ghoti-playwright-ready" },
      { label: "Browser role", id: "ghoti-browser-role" },
      { label: "Browser action", id: "ghoti-browser-action" },
      { label: "Browser note", id: "ghoti-browser-note" },
      { label: "Relay state", id: "ghoti-relay-state" },
      { label: "Relay step", id: "ghoti-relay-step" },
      { label: "Relay source", id: "ghoti-relay-source" },
      { label: "Relay destination", id: "ghoti-relay-destination" },
      { label: "Relay preset", id: "ghoti-relay-preset" },
      { label: "Relay status", id: "ghoti-relay-status" },
      { label: "Relay reset", id: "ghoti-relay-reset" },
      { label: "Relay note", id: "ghoti-relay-note" },
    ]);
    mountNodes([
      "ghoti-browser-notes",
      "ghoti-relay-notes",
      "run-browser-smoke",
      "browser-smoke-summary",
      "run-browser-visible",
      "browser-visible-summary",
    ], browserCard.body);
    appendDebugDetails(browserCard.body, "Browser debug output", ["browser-smoke-raw", "browser-visible-raw"]);
    browserStatusSlot.appendChild(browserCard.article);
  }

  const browserActionsSlot = document.getElementById("browser-actions-slot");
  if (browserActionsSlot) {
    const recipeCard = createConsoleCard("Operator recipes and handoff", "Existing safe handoff and recipe controls, kept inline.");
    mountNodes([
      "queue-recipe-observe-desktop",
      "queue-recipe-focus-terminal",
      "queue-recipe-copy-focused",
      "queue-recipe-paste-dashboard",
      "queue-recipe-wait-step",
      "handoff-source-window",
      "handoff-target-window",
      "handoff-wait-seconds",
      "handoff-source-candidate",
      "handoff-target-candidate",
      "handoff-use-prepared-clipboard",
      "handoff-allow-send",
      "handoff-remember-targets",
      "handoff-target-summary",
      "handoff-target-memory-note",
      "queue-recipe-codex-handoff",
      "recipe-action-summary",
      "recipe-task-list",
    ], recipeCard.body);
    browserActionsSlot.appendChild(recipeCard.article);
  }

  const artifactsActivitySlot = document.getElementById("artifacts-activity-slot");
  if (artifactsActivitySlot) {
    const actionsCard = createConsoleCard("Recent actions", "Recent actions across the operator console.");
    mountNodeById("recent-actions-output", actionsCard.body);
    artifactsActivitySlot.appendChild(actionsCard.article);
  }

  const artifactsSlot = document.getElementById("artifacts-slot");
  if (artifactsSlot) {
    const artifactsCard = createConsoleCard("Recent artifacts", "Recent artifacts list with preview drawer.");
    mountNodeById("artifacts-output", artifactsCard.body);
    artifactsSlot.appendChild(artifactsCard.article);
  }

  const personalOpsSlot = document.getElementById("personal-ops-slot");
  if (personalOpsSlot) {
    const opsCard = createConsoleCard("Artifact generators", "Personal ops generators stay inline and repo-local.");
    mountNodes([
      "internship-form",
      "internship-summary",
      "showcase-form",
      "showcase-summary",
      "portfolio-form",
      "portfolio-summary",
    ], opsCard.body);
    appendDebugDetails(opsCard.body, "Generator debug output", ["internship-raw", "showcase-raw", "portfolio-raw"]);
    personalOpsSlot.appendChild(opsCard.article);
  }

  const githubSlot = document.getElementById("github-slot");
  if (githubSlot) {
    const githubCard = createConsoleCard("Repository status", "Branch, auth, cleanliness, and recent commits.");
    appendFieldRows(githubCard.body, [
      { label: "Branch", id: "github-branch" },
      { label: "Auth", id: "github-auth" },
      { label: "Remote write", id: "github-remote-write" },
      { label: "Working tree", id: "github-clean" },
      { label: "Summary", id: "github-summary" },
    ]);
    mountNodeById("github-commits", githubCard.body);
    appendDebugDetails(githubCard.body, "GitHub debug output", ["github-raw"]);
    githubSlot.appendChild(githubCard.article);
  }

  const systemCapabilitiesSlot = document.getElementById("system-capabilities-slot");
  if (systemCapabilitiesSlot) {
    const controlCard = createConsoleCard("Ghoti control center", "Honest local status only. No autonomous action planning.");
    appendFieldRows(controlCard.body, [
      { label: "State", id: "ghoti-control-state" },
      { label: "Reason", id: "ghoti-control-reason" },
      { label: "Current task", id: "ghoti-control-current-task" },
      { label: "Current task note", id: "ghoti-control-current-task-note" },
      { label: "Pending", id: "ghoti-control-pending" },
      { label: "Blocked", id: "ghoti-control-blocked" },
      { label: "Actionable", id: "ghoti-control-actionable" },
      { label: "Failures", id: "ghoti-control-failures" },
      { label: "Capabilities", id: "ghoti-control-capabilities" },
      { label: "Artifacts", id: "ghoti-control-artifacts" },
      { label: "Brain provider", id: "ghoti-brain-provider" },
      { label: "Brain model", id: "ghoti-brain-model" },
      { label: "Brain ready", id: "ghoti-brain-ready" },
      { label: "Current task use", id: "ghoti-brain-current-task-use" },
      { label: "Brain note", id: "ghoti-brain-note" },
      { label: "Role", id: "ghoti-role-current" },
      { label: "Role provider", id: "ghoti-role-provider" },
      { label: "Sensitivity", id: "ghoti-role-sensitivity" },
      { label: "Watchdog", id: "ghoti-watchdog-state" },
      { label: "Wrong window", id: "ghoti-watchdog-wrong-window" },
      { label: "Stalled", id: "ghoti-watchdog-stalled" },
      { label: "Did not complete", id: "ghoti-watchdog-did-not-complete" },
      { label: "Watchdog headline", id: "ghoti-watchdog-headline" },
      { label: "Memory ready", id: "ghoti-memory-ready" },
      { label: "Markdown memory", id: "ghoti-memory-markdown-ready" },
      { label: "Memory file count", id: "ghoti-memory-file-count" },
      { label: "Memory note", id: "ghoti-memory-note" },
      { label: "Capabilities available", id: "capability-available-count" },
      { label: "Capabilities blocked", id: "capability-blocked-count" },
    ]);
    mountNodes([
      "ghoti-task-visibility-filter",
      "ghoti-task-limit-filter",
      "ghoti-task-type-filter",
      "ghoti-task-status-filter",
      "ghoti-task-active-only",
      "ghoti-control-filter-note",
      "ghoti-show-approvals",
      "ghoti-show-active-tasks",
      "ghoti-show-artifacts",
      "ghoti-queue-observe-desktop",
      "ghoti-queue-clipboard-read",
      "ghoti-run-runtime-checker",
      "ghoti-run-dashboard-checker",
      "ghoti-queue-handoff",
      "ghoti-quick-clipboard-text",
      "ghoti-queue-clipboard-write",
      "ghoti-quick-focus-window",
      "ghoti-queue-focus-window",
      "ghoti-control-action-summary",
      "ghoti-actionable-task-list",
      "ghoti-failure-task-list",
      "ghoti-brain-notes",
      "ghoti-role-note",
      "ghoti-role-roles",
      "ghoti-watchdog-alerts",
      "ghoti-watchdog-handoff-hint",
      "ghoti-memory-notes",
      "live-now-list",
      "scaffold-only-list",
      "not-implemented-list",
      "capability-list",
      "ghoti-can-do-list",
      "ghoti-next-step-list",
      "ghoti-cli-command-list",
    ], controlCard.body);
    const boundaryNote = document.createElement("p");
    boundaryNote.className = "console-honest-note";
    boundaryNote.textContent = "Ollama reachable ≠ wired to drive operator.";
    controlCard.body.appendChild(boundaryNote);
    mountNodes(["ghoti-control-no-delete-note"], controlCard.body);
    appendDebugDetails(controlCard.body, "Capability debug output", ["capability-raw"]);
    systemCapabilitiesSlot.appendChild(controlCard.article);
  }

  const systemScaffoldsSlot = document.getElementById("system-scaffolds-slot");
  if (systemScaffoldsSlot) {
    mountNodes(["section-observer", "section-voice", "section-youtube", "section-runbook", "section-about"], systemScaffoldsSlot);
  }

  const drawerApprovalSlot = document.getElementById("drawer-approval-slot");
  if (drawerApprovalSlot) {
    const approvalCard = createConsoleCard("Approval detail", "Selected approval detail and operator decision form.");
    appendFieldRows(approvalCard.body, [
      { label: "Approval", id: "approval-detail-id" },
      { label: "Status", id: "approval-detail-status" },
      { label: "Risk", id: "approval-detail-risk" },
      { label: "Task", id: "approval-detail-task-id" },
      { label: "Action", id: "approval-detail-action-label" },
      { label: "Reason", id: "approval-detail-reason" },
      { label: "Scope", id: "approval-detail-scope" },
      { label: "Target paths", id: "approval-detail-target-paths" },
      { label: "Workspace scope", id: "approval-detail-workspace-scope" },
      { label: "Workspace policy", id: "approval-detail-workspace-policy" },
      { label: "Workspace reason", id: "approval-detail-workspace-reason" },
      { label: "Allowed root", id: "approval-detail-allowed-root" },
      { label: "Rollback", id: "approval-detail-rollback" },
      { label: "Requires admin", id: "approval-detail-admin" },
      { label: "Updated", id: "approval-detail-updated-at" },
    ]);
    mountNodes(["approval-detail-summary", "approval-decision-note", "approval-approve", "approval-deny", "approval-defer", "approval-action-result", "approval-history-list"], approvalCard.body);
    appendDebugDetails(approvalCard.body, "Approval debug payload", ["approval-detail-raw"]);
    drawerApprovalSlot.appendChild(approvalCard.article);
  }

  const drawerTaskSlot = document.getElementById("drawer-task-slot");
  if (drawerTaskSlot) {
    const taskCard = createConsoleCard("Task detail", "Selected task detail, review actions, and execution history.");
    appendFieldRows(taskCard.body, [
      { label: "Task", id: "task-detail-id" },
      { label: "Status", id: "task-detail-status" },
      { label: "Risk", id: "task-detail-risk" },
      { label: "Approval state", id: "task-detail-approval-state" },
      { label: "Title", id: "task-detail-title" },
      { label: "Description", id: "task-detail-description" },
      { label: "Executor action", id: "task-detail-executor-action" },
      { label: "Executor target", id: "task-detail-executor-target" },
      { label: "Workspace scope", id: "task-detail-workspace-scope" },
      { label: "Workspace policy", id: "task-detail-workspace-policy" },
      { label: "Workspace reason", id: "task-detail-workspace-reason" },
      { label: "Allowed root", id: "task-detail-allowed-root" },
      { label: "Waiting for", id: "task-detail-waiting-for" },
      { label: "Blocked reason", id: "task-detail-blocked-reason" },
      { label: "Next action", id: "task-detail-next-action" },
      { label: "Last note", id: "task-detail-last-note" },
      { label: "Retry limit", id: "task-detail-retry-limit" },
      { label: "Attempt count", id: "task-detail-last-attempt-count" },
      { label: "Execution status", id: "task-detail-last-execution-status" },
      { label: "Execution summary", id: "task-detail-last-execution-summary" },
      { label: "Last artifact", id: "task-detail-last-artifact-path" },
      { label: "Failure reason", id: "task-detail-last-failure-reason" },
      { label: "Interruption reason", id: "task-detail-last-interruption-reason" },
      { label: "Resource guard", id: "task-detail-last-resource-guard-reason" },
    ]);
    mountNodes([
      "task-detail-summary",
      "task-action-note",
      "task-review",
      "task-resume",
      "task-requeue",
      "task-execute",
      "task-action-result",
      "task-history-list",
      "task-execution-history-list",
      "task-recipe-panel",
    ], taskCard.body);
    appendDebugDetails(taskCard.body, "Task debug payload", ["task-detail-raw", "supervisor-raw"]);
    drawerTaskSlot.appendChild(taskCard.article);
  }

  const drawerArtifactSlot = document.getElementById("drawer-artifact-slot");
  if (drawerArtifactSlot) {
    const artifactCard = createConsoleCard("Artifact preview", "Preview body and debug surface for the selected artifact.");
    mountNodes(["artifact-preview-title", "artifact-preview-meta", "artifact-preview-status", "artifact-preview-body"], artifactCard.body);
    drawerArtifactSlot.appendChild(artifactCard.article);
  }
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

  const firstCommit = typeof commits[0] === "string" ? commits[0].trim().split(/\s+/)[0] : "";
  updateTopbarMeta(summary.branch || "", firstCommit || document.getElementById("topbar-commit")?.textContent || "");

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
    if (!silent) {
      openConsoleDrawer("artifact", result.preview?.name || "Artifact preview", "Artifact");
    }
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
  const navBadge = document.getElementById("console-nav-badge-approvals");
  if (!badge) {
    if (!navBadge) {
      return;
    }
  }
  const attention = summary.attention_summary || {};
  const inbox = summary.approval_inbox_summary || {};
  const queue = summary.manual_queue_summary || {};
  const pending = Number(attention.pending_approvals_count ?? inbox.pending_count ?? 0) || 0;
  const ready = Number(attention.ready_queue_count ?? queue.ready_count ?? 0) || 0;
  const total = pending + ready;
  if (badge) {
    badge.textContent = total > 0 ? String(total) : "";
    badge.title = total > 0 ? `${pending} pending approvals, ${ready} ready manual items` : "";
    badge.hidden = total <= 0;
  }
  if (navBadge) {
    navBadge.textContent = total > 0 ? String(total) : "";
    navBadge.title = total > 0 ? `${pending} pending approvals, ${ready} ready manual items` : "";
    navBadge.hidden = total <= 0;
  }
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
  setText("overview-kpi-pending-value", pendingText);
  setText("overview-kpi-pending-meta", queue.available === false ? "approval inbox unavailable" : "approval inbox");
  setText("overview-kpi-ready-value", String(readyCount));
  setText("overview-kpi-ready-meta", queue.available === false ? "manual queue unavailable" : "manual queue ready");
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
      openConsoleDrawer("approval", approvalId || "Approval detail", "Approval");
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
      openConsoleDrawer("task", taskId || "Task detail", "Task");
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

  setText("overview-kpi-active-value", active ? "1" : "0");
  setText("overview-kpi-active-meta", active ? (state.session_id ? `session ${state.session_id}` : "active") : "idle");
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
let observerSuggestedSessionId = "";
let observerRequestInFlight = false;
const DEFAULT_OBSERVER_PROMPT = "Describe what is visible on screen in 2-4 sentences. Only describe visible UI or objects. Do not guess intent. Do not propose actions.";

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

  setText("overview-kpi-frames-value", String(captureState.frame_count || 0));
  setText("overview-kpi-frames-meta", capturing ? "capture running" : (captureState.frame_count ? "last captured frames" : "capture idle"));
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


function formatObserverStatus(status) {
  switch (String(status || "").trim()) {
    case "ok":
      return "Observation recorded";
    case "no_vision_model_available":
      return "No vision model available";
    case "ollama_unreachable":
      return "Ollama unreachable";
    case "no_frame":
      return "No latest frame";
    case "timeout":
      return "Ollama timed out";
    case "observation_in_flight":
      return "Observation already running";
    case "session_id_required":
      return "Session id required";
    case "invalid_session_id":
      return "Invalid session id";
    case "session_not_found":
      return "Session not found";
    default:
      return status ? String(status) : "Observer idle";
  }
}

function truncateObserverText(value, maxLength = 120) {
  const text = String(value || "").trim();
  if (!text) {
    return "";
  }
  return text.length > maxLength ? `${text.slice(0, maxLength - 1)}…` : text;
}

function syncObserverSessionInput(session) {
  const input = document.getElementById("ghoti-observer-session-id");
  if (!input) {
    return;
  }

  const nextId = session?.session_id || activeCaptureSessionId || "";
  if (nextId && (!input.value || input.value === observerSuggestedSessionId)) {
    input.value = nextId;
    observerSuggestedSessionId = nextId;
    return;
  }

  if (!nextId && input.value === observerSuggestedSessionId) {
    input.value = "";
    observerSuggestedSessionId = "";
  }
}

function getObserverSessionId() {
  const input = document.getElementById("ghoti-observer-session-id");
  return String(input?.value || activeCaptureSessionId || observerSuggestedSessionId || "").trim();
}

function renderObserverVisionStatus(payload, lastObservationAtUtc = null) {
  const availabilityEl = document.getElementById("ghoti-observer-availability");
  const modelEl = document.getElementById("ghoti-observer-model");
  const lastEl = document.getElementById("ghoti-observer-last");
  const noteEl = document.getElementById("ghoti-observer-note");
  if (!availabilityEl || !modelEl || !lastEl || !noteEl) {
    return;
  }

  ACTIVE_PILL_CLASSES.forEach((cls) => availabilityEl.classList.remove(cls));

  const vision = payload?.vision || {};
  if (!payload?.ok) {
    availabilityEl.classList.add("ghoti-active-pill-error");
    availabilityEl.textContent = "Observer unavailable";
    modelEl.textContent = "—";
    lastEl.textContent = lastObservationAtUtc ? formatTimeStamp(lastObservationAtUtc) : "Never";
    noteEl.textContent = "Could not load local Ollama observer status.";
    return;
  }

  if (vision.available) {
    availabilityEl.classList.add("ghoti-active-pill-on");
    availabilityEl.textContent = "Observer ready";
  } else if (vision.reason === "no_vision_model_available") {
    availabilityEl.classList.add("ghoti-active-pill-waiting");
    availabilityEl.textContent = "No vision model";
  } else {
    availabilityEl.classList.add("ghoti-active-pill-off");
    availabilityEl.textContent = "Ollama unavailable";
  }

  modelEl.textContent = vision.model || "None";
  lastEl.textContent = lastObservationAtUtc ? formatTimeStamp(lastObservationAtUtc) : "Never";
  noteEl.textContent = vision.note || "Read-only observer status unavailable.";
}

function renderObserverResult(payload = null, options = {}) {
  const resultEl = document.getElementById("ghoti-observer-result");
  if (!resultEl) {
    return;
  }

  if (options.message && !payload) {
    resultEl.innerHTML = `<div class="result-panel${options.isError ? " is-error" : ""}"><p>${escapeHtml(options.message)}</p></div>`;
    return;
  }

  const observation = payload?.observation || null;
  const status = observation?.status || payload?.error || "idle";
  const headline = observation?.status === "ok"
    ? "Observation recorded"
    : formatObserverStatus(status);
  const model = observation?.model || "none";
  const latencyText = observation?.latency_ms != null ? `${observation.latency_ms} ms` : "—";
  const description = observation?.description || "";
  const errorText = observation?.error || payload?.error || "";
  const hintText = payload?.hint || "";
  const detail = description || errorText || options.message || "No observation has been recorded yet.";
  const resultClass = observation?.status === "ok"
    ? "result-panel is-success"
    : (status === "no_vision_model_available" || status === "no_frame" || status === "session_id_required" || status === "invalid_session_id" || status === "session_not_found" || status === "observation_in_flight")
      ? "result-panel"
      : "result-panel is-error";

  resultEl.innerHTML = `
    <div class="${resultClass}">
      <p><strong>${escapeHtml(headline)}</strong></p>
      <p>${escapeHtml(detail)}</p>
      <p class="ghoti-observer-result-meta">status=${escapeHtml(String(status || "idle"))} · model=${escapeHtml(model)} · latency=${escapeHtml(latencyText)}</p>
      ${hintText ? `<p class="ghoti-observer-result-meta">Hint: ${escapeHtml(hintText)}</p>` : ""}
    </div>
  `;
}

function renderObserverHistory(payload) {
  const empty = document.getElementById("ghoti-observer-history-empty");
  const container = document.getElementById("ghoti-observer-history");
  if (!empty || !container) {
    return;
  }

  const items = Array.isArray(payload?.observations) ? payload.observations.slice(0, 10) : [];
  if (!items.length) {
    empty.hidden = false;
    container.hidden = true;
    container.innerHTML = "";
    empty.textContent = payload?.error === "invalid_session_id"
      ? "The selected session id is invalid for local observations."
      : "No observations recorded yet for the selected session.";
    return;
  }

  empty.hidden = true;
  container.hidden = false;
  container.innerHTML = items.map((item) => {
    const timeLabel = item.completed_at_utc || item.requested_at_utc || null;
    const excerpt = truncateObserverText(item.description || item.error || "No detail recorded.", 120);
    return `
      <article class="ghoti-observer-history-item">
        <div class="ghoti-observer-history-top">
          <strong>${escapeHtml(timeLabel ? formatTimeStamp(timeLabel) : item.id || "Observation")}</strong>
          <span class="state-pill ${item.status === "ok" ? "ghoti-active-pill-on" : item.status === "no_vision_model_available" ? "ghoti-active-pill-waiting" : "ghoti-active-pill-off"}">${escapeHtml(formatObserverStatus(item.status))}</span>
        </div>
        <div class="ghoti-observer-history-meta">${escapeHtml(item.model || "none")} · ${escapeHtml(item.session_id || "no session")}</div>
        <p class="ghoti-observer-history-copy">${escapeHtml(excerpt)}</p>
      </article>
    `;
  }).join("");
}

async function refreshObserverPanel() {
  const sessionId = getObserverSessionId();
  const observationUrl = sessionId
    ? `/api/ghoti/active/observations?session_id=${encodeURIComponent(sessionId)}&limit=10`
    : "/api/ghoti/active/observations?limit=10";

  try {
    const [visionData, observationsData] = await Promise.all([
      requestJson("/api/ghoti/brain/vision-status"),
      requestJson(observationUrl),
    ]);
    const observations = Array.isArray(observationsData?.observations) ? observationsData.observations : [];
    const lastObservationAtUtc = observations[0]?.completed_at_utc || observations[0]?.requested_at_utc || null;
    renderObserverVisionStatus(visionData, lastObservationAtUtc);
    renderObserverHistory(observationsData);
  } catch (error) {
    renderObserverVisionStatus({ ok: false }, null);
    renderObserverHistory({ observations: [] });
    console.warn("Could not load observer panel:", error);
  }
}

async function runFrameObservation() {
  const button = document.getElementById("ghoti-observer-run-btn");
  if (!button || observerRequestInFlight) {
    return;
  }

  const sessionId = getObserverSessionId();
  const promptValue = String(document.getElementById("ghoti-observer-prompt")?.value || "").trim();
  if (!sessionId) {
    renderObserverResult({ ok: false, error: "session_id_required" });
    setActiveFeedback("Provide a session id before requesting an observation.", true);
    return;
  }

  observerRequestInFlight = true;
  const originalLabel = button.textContent;
  button.disabled = true;
  button.textContent = "Observing…";
  renderObserverResult(null, { message: "Waiting for local Ollama to describe the latest frame...", isError: false });

  try {
    const payload = { session_id: sessionId };
    if (promptValue) {
      payload.prompt = promptValue;
    }
    const result = await requestJson("/api/ghoti/active/observe-frame", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    renderObserverResult(result);
    if (result.ok) {
      setActiveFeedback("Latest frame described locally by the read-only observer.", false);
    } else {
      setActiveFeedback(`Observer response: ${formatObserverStatus(result.error)}`, result.error !== "no_vision_model_available" && result.error !== "no_frame");
    }
  } catch (error) {
    renderObserverResult(null, { message: `Observation request failed: ${error.message}`, isError: true });
    setActiveFeedback(`Observation request failed: ${error.message}`, true);
  } finally {
    observerRequestInFlight = false;
    button.disabled = false;
    button.textContent = originalLabel;
    await refreshObserverPanel();
  }
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
    syncObserverSessionInput(currentData.session);
    await refreshObserverPanel();
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
  // Include stored approval_id if operator previously got one for this session
  const storedApprovalId = cleanupArea ? (cleanupArea.dataset.approvalId || "") : "";
  if (resultEl) {
    resultEl.innerHTML = "<p style=\"color:var(--muted);font-size:0.85rem;\">Sending cleanup request...</p>";
  }
  try {
    const reqBody = { session_id: sessionId, confirm: phrase };
    if (storedApprovalId) reqBody.approval_id = storedApprovalId;
    const data = await requestJson("/api/ghoti/active/session/cleanup-confirm", {
      method: "POST",
      body: JSON.stringify(reqBody),
    });
    if (data.ok) {
      const sizeKb = ((data.deleted_bytes || 0) / 1024).toFixed(1);
      const missingNote = data.missing_count ? ` ${escapeHtml(String(data.missing_count))} already missing.` : "";
      if (cleanupArea) cleanupArea.removeAttribute("data-approval-id");
      if (resultEl) {
        resultEl.innerHTML = `<div class="result-panel is-success"><p>Cleanup complete. ${escapeHtml(String(data.deleted_count || 0))} file(s) deleted (${escapeHtml(sizeKb)} KB).${missingNote}</p></div>`;
      }
      await refreshActiveSessionData();
    } else if (data.approval_required) {
      // Store approval id for retry; do not auto-approve
      const apvId = escapeHtml(data.approval_id || "");
      if (cleanupArea && data.approval_id) cleanupArea.dataset.approvalId = data.approval_id;
      if (resultEl) {
        resultEl.innerHTML = `<div class="result-panel"><p>Approval required. Request created: <code>${apvId}</code>. Approve it in the <strong>Approvals panel</strong> (top of Approvals tab), then click Confirm cleanup again.</p></div>`;
      }
      refreshGhotiApprovalQueue();
    } else {
      if (resultEl) {
        resultEl.innerHTML = `<div class="result-panel is-error"><p>Cleanup refused: ${escapeHtml(data.error || "unknown error")}</p></div>`;
      }
    }
  } catch (err) {
    if (resultEl) {
      resultEl.innerHTML = `<div class="result-panel is-error"><p>Cleanup failed: ${escapeHtml(err.message)}</p></div>`;
    }
  }
}

const observerPromptField = document.getElementById("ghoti-observer-prompt");
if (observerPromptField && !observerPromptField.placeholder) {
  observerPromptField.placeholder = DEFAULT_OBSERVER_PROMPT;
}

document.getElementById("ghoti-observer-run-btn")?.addEventListener("click", async () => {
  await runFrameObservation();
});

document.getElementById("ghoti-observer-session-id")?.addEventListener("change", async () => {
  await refreshObserverPanel();
});

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

// Ghoti Approval Queue panel
async function refreshGhotiApprovalQueue() {
  const countEl = document.getElementById("ghoti-approvals-pending-count");
  const pendingListEl = document.getElementById("ghoti-approvals-pending-list");
  const recentListEl = document.getElementById("ghoti-approvals-recent-list");
  const resultEl = document.getElementById("ghoti-approvals-result");
  try {
    const data = await requestJson("/api/ghoti/approvals?status=all");
    if (!data.ok) throw new Error("API error");
    const pending = (data.approvals || []).filter((a) => a.status === "pending");
    const recent = (data.approvals || []).filter((a) => a.status !== "pending").slice(0, 10);
    if (countEl) {
      countEl.textContent = pending.length === 0
        ? "No pending approvals."
        : `${pending.length} pending approval${pending.length !== 1 ? "s" : ""} — operator action required.`;
      countEl.className = "summary-note" + (pending.length > 0 ? " needs-action-urgent" : "");
    }
    if (pendingListEl) {
      if (pending.length === 0) {
        pendingListEl.innerHTML = "<p class=\"empty-state\">No pending approvals.</p>";
      } else {
        pendingListEl.innerHTML = pending.map((a) => `
          <article class="approval-item" data-approval-id="${escapeHtml(a.id)}" style="border-left:3px solid var(--warning,#e6a817);padding:0.6rem 0.75rem;margin-bottom:0.5rem;background:var(--panel-bg,#1c2941);border-radius:4px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem;">
              <div>
                <code style="font-size:0.75rem;opacity:0.7;">${escapeHtml(a.id)}</code>
                <strong style="display:block;margin-top:0.2rem;">${escapeHtml(a.action?.type || "unknown")}</strong>
                <p style="margin:0.25rem 0;font-size:0.85rem;">${escapeHtml(a.reason)}</p>
                <p style="margin:0;font-size:0.75rem;opacity:0.6;">Requested by: ${escapeHtml(a.requested_by)} &mdash; ${escapeHtml(a.requested_at_utc || "")}</p>
              </div>
              <div style="display:flex;gap:0.4rem;flex-shrink:0;">
                <button class="button-secondary ghoti-approve-btn" type="button" data-approval-id="${escapeHtml(a.id)}" style="font-size:0.8rem;padding:4px 10px;">Approve</button>
                <button class="button-danger ghoti-reject-btn" type="button" data-approval-id="${escapeHtml(a.id)}" style="font-size:0.8rem;padding:4px 10px;">Reject</button>
              </div>
            </div>
          </article>`).join("");
      }
    }
    if (recentListEl) {
      if (recent.length === 0) {
        recentListEl.innerHTML = "<p class=\"empty-state\">No recent decisions.</p>";
      } else {
        recentListEl.innerHTML = recent.map((a) => {
          const color = a.status === "approved" ? "var(--success,#2ecc85)" : a.status === "consumed" ? "#6eb2f7" : "var(--danger,#d05050)";
          return `<div style="display:flex;justify-content:space-between;padding:0.35rem 0.5rem;border-bottom:1px solid var(--border,#2d3f5e);font-size:0.82rem;">
            <span>${escapeHtml(a.action?.type || "?")} &mdash; <span style="color:${color};">${escapeHtml(a.status)}</span></span>
            <span style="opacity:0.55;">${escapeHtml((a.decided_at_utc || a.consumed_at_utc || "").slice(0, 19))}</span>
          </div>`;
        }).join("");
      }
    }
    // Update overlay badge via tab badge
    const badge = document.getElementById("tab-badge-approvals");
    if (badge) {
      const total = pending.length + Number(badge.dataset.legacyCount || 0);
      badge.textContent = total > 0 ? String(total) : "";
      badge.hidden = total === 0;
    }
  } catch {
    if (countEl) countEl.textContent = "Approval queue unavailable.";
  }
}

const ghotiApprovalsPanel = document.getElementById("ghoti-approval-queue-panel");
if (ghotiApprovalsPanel) {
  ghotiApprovalsPanel.addEventListener("click", async (e) => {
    const approveBtn = e.target.closest(".ghoti-approve-btn");
    const rejectBtn = e.target.closest(".ghoti-reject-btn");
    const resultEl = document.getElementById("ghoti-approvals-result");
    if (approveBtn) {
      const id = approveBtn.dataset.approvalId;
      approveBtn.disabled = true;
      try {
        const data = await requestJson(`/api/ghoti/approvals/${encodeURIComponent(id)}/approve`, { method: "POST" });
        if (resultEl) resultEl.innerHTML = data.ok ? `<div class="result-panel is-success"><p>Approved: ${escapeHtml(id)}</p></div>` : `<div class="result-panel is-error"><p>${escapeHtml(data.error || "approve failed")}</p></div>`;
      } catch (err) {
        if (resultEl) resultEl.innerHTML = `<div class="result-panel is-error"><p>${escapeHtml(err.message)}</p></div>`;
      } finally {
        approveBtn.disabled = false;
        await refreshGhotiApprovalQueue();
      }
    }
    if (rejectBtn) {
      const id = rejectBtn.dataset.approvalId;
      rejectBtn.disabled = true;
      try {
        const data = await requestJson(`/api/ghoti/approvals/${encodeURIComponent(id)}/reject`, { method: "POST", body: JSON.stringify({ notes: "Rejected by operator." }) });
        if (resultEl) resultEl.innerHTML = data.ok ? `<div class="result-panel"><p>Rejected: ${escapeHtml(id)}</p></div>` : `<div class="result-panel is-error"><p>${escapeHtml(data.error || "reject failed")}</p></div>`;
      } catch (err) {
        if (resultEl) resultEl.innerHTML = `<div class="result-panel is-error"><p>${escapeHtml(err.message)}</p></div>`;
      } finally {
        rejectBtn.disabled = false;
        await refreshGhotiApprovalQueue();
      }
    }
  });

  document.getElementById("ghoti-approvals-refresh")?.addEventListener("click", refreshGhotiApprovalQueue);
}

refreshGhotiApprovalQueue();
setInterval(refreshGhotiApprovalQueue, 3000);

/* ============================================================
   PHASE B — SYSTEM HEALTH POLLER + SIDEBAR HANDLERS
   ============================================================ */

function _chipClass(state) {
  if (state === "ok")       return "chip chip--ok";
  if (state === "warn")     return "chip chip--warn";
  if (state === "err")      return "chip chip--err";
  if (state === "scaffold") return "chip chip--scaffold";
  return "chip chip--idle";
}

function _setChip(id, label, state) {
  const el = document.getElementById(id);
  if (!el) return;
  el.className = _chipClass(state);
  el.textContent = label;
}

function _setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function applyHealthPayload(h) {
  if (!h || !h.ok) return;
  const health = h.health || {};

  // ── Overview chips ──
  const activeMode = health.active_mode || {};
  _setChip("overview-chip-active", activeMode.active ? "Active" : "Idle", activeMode.active ? "ok" : "idle");

  const approvals = health.approvals || {};
  const pendingN = approvals.pending_count || 0;
  _setChip("overview-chip-approvals", pendingN > 0 ? `${pendingN} Pending` : "Clear", pendingN > 0 ? "warn" : "ok");

  const vision = health.vision || {};
  const visionState = vision.available ? "ok" : (vision.reason === "no_vision_model_available" ? "idle" : "warn");
  _setChip("overview-chip-vision", vision.available ? (vision.model || "Ready") : "No Model", visionState);
  _setText("overview-kpi-active-value", activeMode.active ? "1" : "0");
  _setText("overview-kpi-active-meta", activeMode.session_id ? `session ${activeMode.session_id}` : "Active Mode");
  _setText("overview-kpi-pending-value", String(pendingN));
  _setText("overview-kpi-pending-meta", pendingN > 0 ? "operator action required" : "approval inbox clear");
  _setText("overview-kpi-ready-value", String(health.capture?.capturing ? (health.capture?.frame_count || 0) : (health.approvals?.ready_count || 0)));
  _setText("overview-kpi-ready-meta", health.capture?.capturing ? "capture frames" : "manual queue ready");
  _setText("overview-kpi-frames-value", String(health.capture?.frame_count || 0));
  _setText("overview-kpi-frames-meta", health.capture?.capturing ? "capture running" : "capture idle");

  // ── Tab badge (sidebar) ──
  const badge = document.getElementById("tab-badge-approvals");
  if (badge) {
    badge.textContent = pendingN > 0 ? String(pendingN) : "";
    badge.classList.toggle("visible", pendingN > 0);
    badge.hidden = pendingN <= 0;
  }

  // ── Health table rows ──
  // active_mode
  const capState = health.capture || {};
  _setChip("health-chip-active", activeMode.active ? "Active" : "Idle", activeMode.active ? "ok" : "idle");
  _setText("health-detail-active", activeMode.session_id ? `session ${activeMode.session_id}` : "—");

  // capture
  const capturing = Boolean(capState.capturing);
  _setChip("health-chip-capture", capturing ? `Watching (${capState.frame_count || 0} frames)` : "Off", capturing ? "ok" : "idle");
  _setText("health-detail-capture", capState.last_frame_utc ? `Last: ${new Date(capState.last_frame_utc).toLocaleTimeString()}` : "—");

  // ollama
  const ollama = health.ollama || {};
  _setChip("health-chip-ollama", ollama.reachable ? "Reachable" : "Unreachable", ollama.reachable ? "ok" : "err");
  _setText("health-detail-ollama", ollama.host || "127.0.0.1:11434");

  // vision
  _setChip("health-chip-vision", vision.available ? (vision.model || "Ready") : "No Model", visionState);
  _setText("health-detail-vision", vision.all_models?.length ? vision.all_models.join(", ") : (vision.reason || "—"));

  // observer
  const observer = health.observer || {};
  _setChip("health-chip-observer", observer.wired ? (observer.last_observation_utc ? "Active" : "Wired") : "Off", observer.wired ? "ok" : "idle");
  _setText("health-detail-observer", observer.last_observation_utc ? `Last: ${new Date(observer.last_observation_utc).toLocaleTimeString()} · ${observer.observations_total || 0} obs` : `${observer.observations_total || 0} observations`);

  // approvals
  _setChip("health-chip-approvals", pendingN > 0 ? `${pendingN} Pending` : "Clear", pendingN > 0 ? "warn" : "ok");
  _setText("health-detail-approvals", approvals.enforced_on?.length ? `guards: ${approvals.enforced_on.join(", ")}` : "—");

  // voice
  const voiceH = health.voice || {};
  _setChip("health-chip-voice", voiceH.mode === "scaffold" ? "Scaffold" : (voiceH.muted ? "Muted" : "Live"), voiceH.mode === "scaffold" ? "scaffold" : (voiceH.muted ? "idle" : "ok"));
  _setText("health-detail-voice", voiceH.mode === "scaffold" ? "real audio: false" : (voiceH.muted ? "muted" : "unmuted"));

  // youtube
  const yt = health.youtube || {};
  _setChip("health-chip-youtube", yt.status === "scaffold" ? "Scaffold" : "Active", yt.status === "scaffold" ? "scaffold" : "ok");
  _setText("health-detail-youtube", "real: false");

  // overlay
  const overlay = health.overlay || {};
  _setChip("health-chip-overlay", "Browser", "ok");
  _setText("health-detail-overlay", `native always-on-top: ${overlay.native_always_on_top ? "yes" : "no"}`);

  // ── Next actions ──
  const actions = [];
  if (!activeMode.active) actions.push("Start Active Mode to enable Ghoti.");
  if (!ollama.reachable)  actions.push("Start Ollama to enable vision observer.");
  if (!vision.available)  actions.push("Pull a vision model in Ollama (e.g. llava).");
  if (pendingN > 0)       actions.push(`Review ${pendingN} pending approval${pendingN !== 1 ? "s" : ""} in Approvals.`);
  if (!capturing)         actions.push("Start capture to feed frames to the observer.");
  if (actions.length === 0) actions.push("System nominal — no actions required.");

  const listEl = document.getElementById("next-actions-list");
  if (listEl) {
    listEl.innerHTML = actions.map(a => `<li>${escapeHtml(a)}</li>`).join("");
  }

  // ── Sidebar commit info ──
  const srv = h.server || {};
  if (srv.commit) {
    _setText("sidebar-commit-info", `commit ${srv.commit}`);
    _setText("about-commit", srv.commit);
    updateTopbarMeta(srv.branch || document.getElementById("topbar-branch")?.textContent || "", srv.commit);
  }

  // ── Observer no-model banner visibility ──
  const noModelBanner = document.getElementById("observer-no-model-banner");
  if (noModelBanner) noModelBanner.hidden = vision.available;

  // ── Local Brain Truth card (folded from health.models) ──
  const models = health.models || {};
  const ollamaReachable = (health.ollama || {}).reachable;
  _setChip("ghoti-models-ollama", ollamaReachable ? "Reachable" : "Unreachable", ollamaReachable ? "ok" : "err");
  _setText("ghoti-models-count", String(models.all_count ?? "—"));
  _setText("ghoti-models-gemma", models.gemma_available ? (models.selected_text_model || "detected") : "none");
  _setText("ghoti-models-selected", models.selected_text_model || "none");
  _setText("ghoti-models-vision", String(models.all_count > 0 ? "check /api/ghoti/models/status" : "none"));
}

async function refreshProbeHistory() {
  try {
    const data = await requestJson("/api/ghoti/models/probes?limit=5");
    const el = document.getElementById("ghoti-models-probe-history");
    if (!el) return;
    const probes = data.probes || [];
    if (probes.length === 0) { el.innerHTML = "<p class='ghoti-session-empty'>No probes recorded yet.</p>"; return; }
    el.innerHTML = probes.map((p) => {
      const ts = p.completed_at_utc ? new Date(p.completed_at_utc).toLocaleTimeString() : "—";
      const statusClass = p.status === "ok" ? "chip--ok" : "chip--err";
      return `<div class="ghoti-observer-history-item" style="margin-bottom:0.5rem;">
        <span class="chip ${statusClass}" style="font-size:0.7rem;">${escapeHtml(p.status || "?")}</span>
        <span class="mono" style="font-size:0.75rem;margin:0 0.4rem;">${escapeHtml(p.model || "—")}</span>
        <span style="font-size:0.75rem;color:var(--text-dim);">${ts}</span>
        ${p.latency_ms != null ? `<span style="font-size:0.72rem;color:var(--text-dim);margin-left:0.3rem;">${p.latency_ms}ms</span>` : ""}
        ${p.response ? `<p style="font-size:0.78rem;margin:0.2rem 0 0;">${escapeHtml(p.response.slice(0, 300))}</p>` : ""}
        ${p.error ? `<p style="font-size:0.78rem;color:var(--c-warn);margin:0.2rem 0 0;">${escapeHtml(p.error)}</p>` : ""}
      </div>`;
    }).join("");
  } catch { /* silent */ }
}

async function startHealthPoll() {
  async function poll() {
    try {
      const res = await fetch("/api/ghoti/system/health");
      if (res.ok) {
        const data = await res.json();
        applyHealthPayload(data);
      }
    } catch { /* server unreachable — stay silent */ }
  }
  await poll();
  setInterval(poll, 5000);
}

startHealthPoll();
refreshProbeHistory();

document.getElementById("ghoti-models-probe-btn")?.addEventListener("click", async () => {
  const btn = document.getElementById("ghoti-models-probe-btn");
  const result = document.getElementById("ghoti-models-probe-result");
  if (btn) { btn.disabled = true; btn.textContent = "Running…"; }
  if (result) result.textContent = "Running diagnostic probe…";
  try {
    const data = await requestJson("/api/ghoti/models/gemma-probe", { method: "POST", body: "{}", headers: { "Content-Type": "application/json" } });
    if (data.ok) {
      const probe = data.probe || {};
      if (result) result.textContent = probe.response ? `OK (${probe.latency_ms}ms): ${probe.response.slice(0, 400)}` : "Probe returned no response text.";
    } else {
      const errMsg = data.error === "no_gemma_model_available" ? "No Gemma model installed. Install one with: ollama pull gemma3" : (data.error === "ollama_unreachable" ? "Ollama not reachable." : (data.error || "Unknown error"));
      if (result) result.textContent = `Probe failed: ${errMsg}`;
    }
    await refreshProbeHistory();
  } catch (err) {
    if (result) result.textContent = `Error: ${err.message}`;
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = "Run Gemma diagnostic probe"; }
  }
});

// ── Runbook copy buttons ──
document.addEventListener("click", (e) => {
  const btn = e.target.closest(".runbook-copy-btn");
  if (!btn) return;
  const targetId = btn.dataset.copyTarget;
  const source = targetId ? document.getElementById(targetId) : btn.previousElementSibling;
  if (!source) return;
  navigator.clipboard.writeText(source.textContent).then(() => {
    const orig = btn.textContent;
    btn.textContent = "Copied!";
    setTimeout(() => { btn.textContent = orig; }, 1500);
  }).catch(() => {});
});

// ── Voice controls in #section-voice ──
document.getElementById("ghoti-voice-mute-btn")?.addEventListener("click", async () => {
  try {
    const data = await requestJson("/api/ghoti/voice/mute", { method: "POST", body: "{}" });
    if (!data.ok) throw new Error(data.error || "mute failed");
  } catch (err) { console.warn("voice mute:", err.message); }
});

document.getElementById("ghoti-voice-unmute-btn")?.addEventListener("click", async () => {
  try {
    const data = await requestJson("/api/ghoti/voice/unmute", { method: "POST", body: "{}" });
    if (!data.ok) throw new Error(data.error || "unmute failed");
  } catch (err) { console.warn("voice unmute:", err.message); }
});

// ── YouTube queue button in #section-youtube ──
document.getElementById("ghoti-yt-queue-btn")?.addEventListener("click", async () => {
  const url   = document.getElementById("ghoti-yt-url-input")?.value?.trim();
  const goal  = document.getElementById("ghoti-yt-goal-input")?.value?.trim();
  if (!url) { alert("Enter a YouTube URL."); return; }
  try {
    const data = await requestJson("/api/ghoti/youtube-follower/queue", {
      method: "POST",
      body: JSON.stringify({ url, goal: goal || "" }),
    });
    if (!data.ok) throw new Error(data.error || "queue failed");
    const urlEl = document.getElementById("ghoti-yt-url-input");
    if (urlEl) urlEl.value = "";
  } catch (err) { alert(`Queue failed: ${err.message}`); }
});

// ── Sidebar active-link highlight on scroll ──
(function initSidebarHighlight() {
  const sections = document.querySelectorAll(".content-section[id]");
  const navLinks  = document.querySelectorAll(".sidebar-nav a[href^='#']");
  if (!sections.length || !navLinks.length) return;

  const obs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      const link = document.querySelector(`.sidebar-nav a[href='#${entry.target.id}']`);
      if (!link) return;
      if (entry.isIntersecting) link.classList.add("active");
      else link.classList.remove("active");
    });
  }, { rootMargin: "-40% 0px -55% 0px" });

  sections.forEach(s => obs.observe(s));
})();

async function refreshGlobalConsoleView() {
  await Promise.allSettled([
    refreshConsole(),
    refreshActiveModeState(),
    refreshCaptureState(),
    refreshActiveSessionData(),
    refreshObserverPanel(),
    refreshProbeHistory(),
    refreshGhotiApprovalQueue(),
  ]);
}

function initDashboardUxRebuild() {
  mountDashboardUxShell();
  setActiveConsoleView("overview", { focus: false });

  document.querySelectorAll(".console-nav-item[data-console-view]").forEach((button) => {
    button.addEventListener("click", () => {
      setActiveConsoleView(button.dataset.consoleView || "overview", { focus: false });
    });
  });

  document.getElementById("global-refresh-btn")?.addEventListener("click", async (event) => {
    await runRefresh(
      event.currentTarget,
      "Refresh operator console",
      "Refreshing…",
      refreshGlobalConsoleView,
      (error) => {
        console.warn("Global refresh failed:", error);
      },
    );
  });

  document.getElementById("topbar-settings-btn")?.addEventListener("click", () => {
    setActiveConsoleView("system", { focus: false });
  });

  document.getElementById("console-drawer-close")?.addEventListener("click", closeConsoleDrawer);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeConsoleDrawer();
    }
  });

  document.addEventListener("click", (event) => {
    if (event.defaultPrevented) {
      return;
    }
    const interactiveTarget = event.target.closest("button, a, input, textarea, select, label, summary");
    if (interactiveTarget) {
      return;
    }

    const taskRow = event.target.closest("#pending-approvals-list .approval-item, #human-needed-list .approval-item, #waiting-tasks-list .approval-item, #ready-to-resume-list .approval-item, #interrupted-tasks-list .approval-item, #executor-task-list .approval-item, #desktop-task-list .approval-item, #recipe-task-list .approval-item");
    if (taskRow) {
      taskRow.querySelector("[data-task-action='inspect']")?.click();
      return;
    }

    const approvalRow = event.target.closest("#approval-inbox-list .approval-item, #manual-queue-list .approval-item, #pipeline-items-list .approval-item");
    if (approvalRow) {
      approvalRow.querySelector(".view-inbox-trace-btn, .view-queue-trace-btn, .view-trace-btn")?.click();
      return;
    }

    const artifactRow = event.target.closest("#artifacts-output .artifact-item");
    if (artifactRow) {
      artifactRow.querySelector("[data-artifact-action='preview']")?.click();
    }
  });
}


function renderWeeklyReviewCard(payload) {
  var container = document.getElementById('money-review-card');
  if (!container) return;

  if (payload.status === 'zero_state' || !payload.latest_run_id) {
    var warn = payload.warning ? escapeHtml(payload.warning) : 'No weekly review artifacts found yet.';
    container.innerHTML =
      '<h3 class="card-title">Money OS &#8212; Weekly Review</h3>' +
      '<p class="summary-note">' + warn + '</p>' +
      '<p class="summary-note">Generate locally: <code>python 03_scripts/weekly_money_review.py --since-days 30</code></p>';
    return;
  }

  var warnings = Array.isArray(payload.warnings) ? payload.warnings : [];
  var topCandidates = Array.isArray(payload.top_decision_candidates) ? payload.top_decision_candidates : [];
  var nextActions = Array.isArray(payload.next_local_actions) ? payload.next_local_actions : [];
  var artifactPaths = payload.artifact_paths || {};
  var safetyFlags = payload.safety_flags || {};

  var warningsHtml = warnings.length > 0
    ? '<div class="banner banner--warn" style="margin-top:0.5rem;">' + warnings.map(function(w) { return escapeHtml(w); }).join('<br>') + '</div>'
    : '';

  var candidatesHtml = topCandidates.length > 0
    ? topCandidates.map(function(c) {
        return '<div class="approval-item" style="margin-bottom:0.5rem;">' +
          '<strong>' + escapeHtml(c.title || c.experiment_id || '?') + '</strong> ' +
          '<span class="chip">' + escapeHtml(c.category || '?') + '</span> ' +
          '<span class="chip chip--scaffold">confidence: ' + escapeHtml(c.confidence || '?') + '</span> ' +
          '<span class="chip chip--scaffold">risk: ' + escapeHtml(c.risk_level || '?') + '</span>' +
          '<div style="font-size:0.85em;margin-top:0.2rem;">' + escapeHtml(c.next_local_step || '') + '</div>' +
          '<div style="font-size:0.8em;color:#888;">Approval required: ' + (c.approval_required ? 'yes' : 'no') + '</div>' +
          '</div>';
      }).join('')
    : '<p class="empty-state">No decision candidates.</p>';

  var nextActionsHtml = nextActions.length > 0
    ? '<ul class="status-list">' + nextActions.map(function(a) { return '<li>' + escapeHtml(a) + '</li>'; }).join('') + '</ul>'
    : '<p class="empty-state">No next actions listed.</p>';

  var safetyEntries = Object.entries(safetyFlags);
  var safetyFlagsHtml = safetyEntries.length > 0
    ? '<ul class="status-list">' + safetyEntries.map(function(pair) { return '<li><code>' + escapeHtml(pair[0]) + '</code>: ' + escapeHtml(String(pair[1])) + '</li>'; }).join('') + '</ul>'
    : '<p class="empty-state">No safety flags.</p>';

  var artifactEntries = Object.entries(artifactPaths);
  var artifactPathsHtml = artifactEntries.map(function(pair) {
    var name = pair[0], info = pair[1];
    return '<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.25rem;">' +
      '<code style="flex:1;font-size:0.8em;">' + escapeHtml(info.relative || name) + '</code>' +
      (info.exists ? '' : ' <span class="chip chip--warn">missing</span>') +
      '</div>';
  }).join('');

  container.innerHTML =
    '<h3 class="card-title">Money OS &#8212; Weekly Review</h3>' +
    '<p class="summary-note">Latest run: <strong>' + escapeHtml(payload.latest_run_id || '?') + '</strong>' +
    (payload.created_at ? ' &nbsp;<span style="color:#888;">' + escapeHtml(payload.created_at) + '</span>' : '') +
    '</p>' +
    '<p class="summary-note">' +
    'Experiments: <strong>' + (payload.total_experiments != null ? payload.total_experiments : '?') + '</strong> &nbsp;|&nbsp; ' +
    'Money runs: <strong>' + (payload.total_money_runs != null ? payload.total_money_runs : '?') + '</strong> &nbsp;|&nbsp; ' +
    'Candidates: <strong>' + (payload.total_decision_candidates != null ? payload.total_decision_candidates : '?') + '</strong> &nbsp;|&nbsp; ' +
    'Total reviews: <strong>' + (payload.runs_total != null ? payload.runs_total : '?') + '</strong>' +
    '</p>' +
    warningsHtml +
    '<details style="margin-top:0.75rem;"><summary><strong>Top Decision Candidates</strong></summary><div style="margin-top:0.5rem;">' + candidatesHtml + '</div></details>' +
    '<details style="margin-top:0.5rem;"><summary><strong>Next Local Actions</strong></summary><div style="margin-top:0.5rem;">' + nextActionsHtml + '</div></details>' +
    '<details style="margin-top:0.5rem;"><summary><strong>Safety Flags</strong></summary><div style="margin-top:0.5rem;">' + safetyFlagsHtml + '</div></details>' +
    '<details style="margin-top:0.5rem;"><summary><strong>Artifact Paths</strong></summary><div style="margin-top:0.5rem;">' + artifactPathsHtml + '</div></details>';
}

async function refreshWeeklyReview() {
  try {
    var data = await requestJson('/api/ghoti/money/weekly-review/latest');
    renderWeeklyReviewCard(data);
  } catch (err) {
    var container = document.getElementById('money-review-card');
    if (container) {
      container.innerHTML =
        '<h3 class="card-title">Money OS &#8212; Weekly Review</h3>' +
        '<p class="summary-note" style="color:red;">Failed to load: ' + escapeHtml(err.message) + '</p>';
    }
  }
}

function renderManualQueueCard(payload) {
  var container = document.getElementById('manual-queue-card');
  if (!container) return;

  var queuePath = payload.queue_path || '14_context/money_workflows/manual_decision_queue.jsonl';

  if (payload.status === 'zero_state' || payload.status === 'empty' || payload.item_count === 0) {
    var note = (payload.warnings && payload.warnings.length > 0) ? escapeHtml(payload.warnings[0]) : 'No queue items yet.';
    container.innerHTML =
      '<h3 class="card-title">Money OS &#8212; Manual Decision Queue</h3>' +
      '<p class="summary-note">' + note + '</p>' +
      '<p class="summary-note">Queue path (read-only): <code>' + escapeHtml(queuePath) + '</code></p>' +
      '<p class="summary-note">Add item locally: <code>python 03_scripts/manual_decision_queue_new_item.py --latest --dry-run</code></p>';
    return;
  }

  var items = Array.isArray(payload.items) ? payload.items : [];
  var warnings = Array.isArray(payload.warnings) ? payload.warnings : [];
  var safetyFlags = payload.safety_flags || {};
  var statusCounts = payload.status_counts || {};
  var riskCounts = payload.risk_counts || {};

  var warningsHtml = warnings.length > 0
    ? '<div class="banner banner--warn" style="margin-top:0.5rem;">' + warnings.map(function(w) { return escapeHtml(w); }).join('<br>') + '</div>'
    : '';

  var statusCountsHtml = Object.entries(statusCounts).map(function(pair) {
    return '<span class="chip">' + escapeHtml(pair[0]) + ': ' + pair[1] + '</span>';
  }).join(' ');

  var riskCountsHtml = Object.entries(riskCounts).map(function(pair) {
    return '<span class="chip chip--scaffold">risk/' + escapeHtml(pair[0]) + ': ' + pair[1] + '</span>';
  }).join(' ');

  var topItems = items.slice(0, 5);
  var itemsHtml = topItems.map(function(item) {
    var blockedNote = item.blocked_reason ? '<div style="font-size:0.8em;color:#c00;">Blocked: ' + escapeHtml(item.blocked_reason) + '</div>' : '';
    return '<div class="approval-item" style="margin-bottom:0.5rem;">' +
      '<strong>' + escapeHtml(item.title || item.queue_item_id || '?') + '</strong> ' +
      '<span class="chip">' + escapeHtml(item.category || '?') + '</span> ' +
      '<span class="chip chip--scaffold">risk: ' + escapeHtml(item.risk_level || '?') + '</span> ' +
      '<span class="chip">' + escapeHtml(item.status || '?') + '</span>' +
      '<div style="font-size:0.85em;margin-top:0.2rem;">' + escapeHtml(item.next_local_step || '') + '</div>' +
      '<div style="font-size:0.8em;color:#888;">Approval required: ' + (item.approval_required ? 'yes' : 'no') + '</div>' +
      blockedNote +
      '</div>';
  }).join('');

  var safetyEntries = Object.entries(safetyFlags);
  var safetyFlagsHtml = safetyEntries.length > 0
    ? '<ul class="status-list">' + safetyEntries.map(function(pair) { return '<li><code>' + escapeHtml(pair[0]) + '</code>: ' + escapeHtml(String(pair[1])) + '</li>'; }).join('') + '</ul>'
    : '<p class="empty-state">No safety flags.</p>';

  container.innerHTML =
    '<h3 class="card-title">Money OS &#8212; Manual Decision Queue</h3>' +
    '<p class="summary-note">Items: <strong>' + payload.item_count + '</strong> &nbsp;|&nbsp; ' + statusCountsHtml + ' ' + riskCountsHtml + '</p>' +
    '<p class="summary-note">Queue path (copy only): <code>' + escapeHtml(queuePath) + '</code></p>' +
    warningsHtml +
    '<details style="margin-top:0.75rem;"><summary><strong>Queue Items (top 5)</strong></summary><div style="margin-top:0.5rem;">' + (itemsHtml || '<p class="empty-state">No items.</p>') + '</div></details>' +
    '<details style="margin-top:0.5rem;"><summary><strong>Safety Flags</strong></summary><div style="margin-top:0.5rem;">' + safetyFlagsHtml + '</div></details>';
}

async function refreshManualQueue() {
  try {
    var data = await requestJson('/api/ghoti/money/manual-decision-queue');
    renderManualQueueCard(data);
  } catch (err) {
    var container = document.getElementById('manual-queue-card');
    if (container) {
      container.innerHTML =
        '<h3 class="card-title">Money OS &#8212; Manual Decision Queue</h3>' +
        '<p class="summary-note" style="color:red;">Failed to load: ' + escapeHtml(err.message) + '</p>';
    }
  }
}

initDashboardUxRebuild();
refreshWeeklyReview();
refreshManualQueue();

// ─── Local Orchestrator Card (N+3.50A) ────────────────────────────────────────

function renderLocalOrchestratorCard(payload) {
  var container = document.getElementById('local-orchestrator-card');
  if (!container) return;
  if (!payload || !payload.ok) {
    container.innerHTML = '<h3 class="card-title">Local Orchestrator</h3><p class="summary-note" style="color:red;">Status unavailable.</p>';
    return;
  }

  var e = function(s) { return escapeHtml(String(s == null ? '—' : s)); };
  var chip = function(label, cls) { return '<span class="chip ' + (cls || '') + '">' + e(label) + '</span>'; };

  var pb = payload.prompt_bus || {};
  var al = payload.agent_lanes || {};
  var ov = payload.obsidian_vault || {};
  var cm = payload.compact_memory || {};
  var rf = payload.ruflo || {};
  var ol = payload.ollama || {};
  var sf = payload.safety_flags || {};

  var pbHtml =
    '<div class="health-row"><span class="health-label">Outbox files</span>' + chip(pb.outbox_count != null ? pb.outbox_count : '?') + '</div>' +
    '<div class="health-row"><span class="health-label">Latest outbox</span><span class="health-detail mono">' + e(pb.outbox_latest || '(none)') + '</span></div>';

  var alHtml =
    '<div class="health-row"><span class="health-label">Active locks</span>' + chip(al.active_locks_count != null ? al.active_locks_count : '?') + '</div>' +
    '<div class="health-row"><span class="health-label">Status records</span>' + chip(al.status_records_count != null ? al.status_records_count : '?') + '</div>' +
    '<div class="health-row"><span class="health-label">Latest agent</span><span class="health-detail mono">' + e(al.latest_agent) + '</span></div>' +
    '<div class="health-row"><span class="health-label">Latest state</span><span class="health-detail mono">' + e(al.latest_state) + '</span></div>';

  var memHtml =
    '<div class="health-row"><span class="health-label">Obsidian vault</span>' + chip(ov.exists ? 'exists' : 'missing', ov.exists ? 'chip--ok' : 'chip--warn') + '<span class="health-detail mono">' + e(ov.file_count) + ' .md files</span></div>' +
    '<div class="health-row"><span class="health-label">Compact memory</span>' + chip(cm.exists ? 'exists' : 'missing', cm.exists ? 'chip--ok' : 'chip--warn') + '<span class="health-detail mono">' + e(cm.file_count) + ' .md files</span></div>';

  var rufloChip = rf.exists ? 'chip--ok' : 'chip--warn';
  var rfHtml =
    '<div class="health-row"><span class="health-label">Ruflo dir</span>' + chip(rf.exists ? 'exists' : 'missing', rufloChip) + '<span class="health-detail mono">' + e(rf.name) + ' v' + e(rf.version) + '</span></div>' +
    '<div class="health-row"><span class="health-label">node_modules</span>' + chip(rf.node_modules ? 'installed' : 'not installed', rf.node_modules ? 'chip--ok' : 'chip--warn') + '</div>' +
    '<div class="health-row"><span class="health-label">Lifecycle scripts</span>' + chip(rf.lifecycle_scripts && rf.lifecycle_scripts.length ? 'BLOCKED' : 'none (safe)', rf.install_blocked ? 'chip--warn' : 'chip--ok') + '</div>';

  var ollamaChip = ol.found ? 'chip--ok' : 'chip--warn';
  var gemmaChip = ol.gemma_found ? 'chip--ok' : 'chip--warn';
  var olHtml =
    '<div class="health-row"><span class="health-label">Ollama</span>' + chip(ol.found ? 'found' : 'not found', ollamaChip) + '</div>' +
    '<div class="health-row"><span class="health-label">Gemma model</span>' + chip(ol.gemma_found ? 'found' : 'not found', gemmaChip) + '</div>';

  var sfEntries = Object.entries(sf);
  var sfHtml = sfEntries.map(function(pair) {
    return '<div class="health-row"><span class="health-label">' + e(pair[0].replace(/_/g, ' ')) + '</span>' + chip(String(pair[1]), pair[1] ? 'chip--ok' : 'chip--warn') + '</div>';
  }).join('');

  var nextCmd = 'python 03_scripts/ghoti_dashboard.py --json';

  container.innerHTML =
    '<h3 class="card-title">Local Orchestrator <span class="chip chip--ok" style="font-size:0.65rem;">N+3.50A read-only</span></h3>' +
    '<p class="summary-note">Branch: <code>' + e(payload.branch) + '</code> &nbsp;|&nbsp; Generated: ' + e(payload.generated_at) + '</p>' +
    '<p class="summary-note" style="color:var(--text-dim);font-size:0.8rem;">Read-only status card. No live actions. No approve/execute/install buttons.</p>' +
    '<div class="health-table" style="margin-bottom:0.75rem;">' +
    '<p class="ghoti-active-label" style="margin:0.5rem 0 0.25rem;">Prompt Bus</p>' + pbHtml +
    '<p class="ghoti-active-label" style="margin:0.5rem 0 0.25rem;">Agent Lanes</p>' + alHtml +
    '<p class="ghoti-active-label" style="margin:0.5rem 0 0.25rem;">Obsidian / Compact Memory</p>' + memHtml +
    '<p class="ghoti-active-label" style="margin:0.5rem 0 0.25rem;">Ruflo</p>' + rfHtml +
    '<p class="ghoti-active-label" style="margin:0.5rem 0 0.25rem;">Gemma / Ollama</p>' + olHtml +
    '<p class="ghoti-active-label" style="margin:0.5rem 0 0.25rem;">Safety Flags</p>' + sfHtml +
    '</div>' +
    '<p class="ghoti-active-label">Next Recommended Command</p>' +
    '<div class="runbook-code-block"><pre>' + e(nextCmd) + '</pre></div>';
}

async function refreshLocalOrchestrator() {
  try {
    var data = await requestJson('/api/ghoti/local-orchestrator/status');
    renderLocalOrchestratorCard(data);
  } catch (err) {
    var container = document.getElementById('local-orchestrator-card');
    if (container) {
      container.innerHTML =
        '<h3 class="card-title">Local Orchestrator</h3>' +
        '<p class="summary-note" style="color:red;">Failed to load: ' + escapeHtml(err.message) + '</p>';
    }
  }
}

refreshLocalOrchestrator();

// ---------------------------------------------------------------------
// N+4.4B Desktop Operator Action Center (client-side handlers)
// ---------------------------------------------------------------------
(function attachDesktopOperatorActionCenter() {
  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) {
      el.textContent = value || "none";
    }
  }
  function applyLatest(latest) {
    if (!latest) return;
    setText("doa-latest-handoff", latest.handoff_path);
    setText("doa-latest-dry-run", latest.dry_run_plan_path);
    setText("doa-latest-approval", latest.approval_record_path);
    setText("doa-latest-execution", latest.execution_result_path);
    setText("doa-latest-preview", latest.preview_path);
  }
  function applyStatus(status) {
    if (!status) return;
    setText("doa-default-mode", status.default_mode || "unknown");
    if (status.model_adapters) {
      const gemini = status.model_adapters.gemini_cli;
      if (gemini) {
        const txt = gemini.available
          ? ("detected (status-only, quota=" + gemini.quota + ", treated_as_unlimited=" + gemini.treated_as_unlimited + ")")
          : ("missing (quota=" + gemini.quota + ", treated_as_unlimited=" + gemini.treated_as_unlimited + ", live_prompt_executed=" + gemini.live_prompt_executed + ")");
        setText("doa-gemini", txt);
      }
      const ldemo = status.model_adapters.local_demo;
      if (ldemo) {
        setText("doa-local-fallback", ldemo.available ? "available (local_demo)" : "unavailable");
      }
    }
  }
  async function callDoa(endpoint, method, body) {
    const opts = { method: method, headers: { "Content-Type": "application/json" } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(endpoint, opts);
    return await res.json();
  }
  async function refreshDoaStatus() {
    try {
      const data = await callDoa("/api/desktop-operator/status", "GET");
      applyStatus(data && data.status);
      applyLatest(data && data.latest);
    } catch (err) {
      // silent fallback
    }
  }
  function bind(id, fn) {
    const el = document.getElementById(id);
    if (el) { el.addEventListener("click", fn); }
  }
  bind("doa-create-handoff", async () => {
    // Default goal/workflow; no live account, no posting
    const body = {
      goal: "Create a local video-style content package about AI tools for students",
      workflow: "content_studio_demo",
    };
    const data = await callDoa("/api/desktop-operator/create-handoff", "POST", body);
    applyLatest(data && data.latest);
  });
  bind("doa-dry-run", async () => {
    const data = await callDoa("/api/desktop-operator/dry-run", "POST", {});
    applyLatest(data && data.latest);
  });
  bind("doa-approve", async () => {
    // We do NOT capture or display the approval token client-side. The server
    // generates a local random token and stores only its SHA-256 hash.
    const data = await callDoa("/api/desktop-operator/approve", "POST", {});
    applyLatest(data && data.latest);
  });
  bind("doa-execute", async () => {
    const data = await callDoa("/api/desktop-operator/execute-approved", "POST", {});
    applyLatest(data && data.latest);
  });
  bind("doa-open-preview", async () => {
    const latestRes = await callDoa("/api/desktop-operator/latest", "GET");
    const previewPath = latestRes && latestRes.latest && latestRes.latest.preview_path;
    if (!previewPath) {
      // No preview yet; do not navigate anywhere.
      return;
    }
    // Validate locally before requesting preview metadata. We do NOT open
    // arbitrary URLs and do NOT click/type. Just request the safe preview
    // metadata endpoint; the user can choose to follow the link manually.
    const enc = encodeURIComponent(previewPath);
    const meta = await callDoa("/api/desktop-operator/preview?path=" + enc, "GET");
    if (meta && meta.ok && meta.previewPath) {
      setText("doa-latest-preview", meta.previewPath);
    }
  });
  // Initial render
  if (document.getElementById("desktop-operator-action-center")) {
    refreshDoaStatus();
  }
})();

// ---------------------------------------------------------------------
// N+4.4C Desktop Operator Recipe Runner (client-side handlers)
// ---------------------------------------------------------------------
(function attachDesktopOperatorRecipeRunner() {
  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) {
      el.textContent = value || "none";
    }
  }
  function applyRecipeLatest(latest) {
    if (!latest) return;
    setText("dorr-latest-recipe", latest.recipe_id);
    setText("dorr-latest-handoff", latest.handoff_path);
    setText("dorr-latest-dry-run", latest.dry_run_plan_path);
    setText("dorr-latest-approval", latest.approval_record_path);
    setText("dorr-latest-execution", latest.execution_result_path);
    setText("dorr-latest-preview", latest.preview_path);
    setText("dorr-latest-gemini-handoff", latest.handoff_export_path);
  }
  async function callDorr(endpoint, method, body) {
    const opts = { method: method, headers: { "Content-Type": "application/json" } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(endpoint, opts);
    return await res.json();
  }
  async function refreshDorrLatest() {
    try {
      const data = await callDorr("/api/desktop-operator/latest-recipe", "GET");
      applyRecipeLatest(data && data.latest);
    } catch (err) { /* silent */ }
  }
  function selectedRecipeId() {
    const el = document.getElementById("dorr-recipe-select");
    return el ? el.value : null;
  }
  function bind(id, fn) {
    const el = document.getElementById(id);
    if (el) { el.addEventListener("click", fn); }
  }
  bind("dorr-create-handoff", async () => {
    const recipeId = selectedRecipeId();
    if (!recipeId) return;
    const data = await callDorr("/api/desktop-operator/create-recipe-handoff", "POST", { recipe_id: recipeId });
    applyRecipeLatest(data && data.latest);
  });
  bind("dorr-dry-run", async () => {
    const data = await callDorr("/api/desktop-operator/run-recipe-dry-run", "POST", {});
    applyRecipeLatest(data && data.latest);
  });
  bind("dorr-approve", async () => {
    // The client does NOT collect or store the approval token; the server
    // generates a local random token and stores only its SHA-256 hash.
    const data = await callDorr("/api/desktop-operator/approve-recipe", "POST", {});
    applyRecipeLatest(data && data.latest);
  });
  bind("dorr-execute", async () => {
    const data = await callDorr("/api/desktop-operator/execute-approved-recipe", "POST", {});
    applyRecipeLatest(data && data.latest);
  });
  bind("dorr-open-preview", async () => {
    const latestRes = await callDorr("/api/desktop-operator/latest-recipe", "GET");
    const previewPath = latestRes && latestRes.latest && latestRes.latest.preview_path;
    if (!previewPath) return;
    const enc = encodeURIComponent(previewPath);
    const meta = await callDorr("/api/desktop-operator/preview?path=" + enc, "GET");
    if (meta && meta.ok && meta.previewPath) {
      setText("dorr-latest-preview", meta.previewPath);
    }
  });
  // Initial render
  if (document.getElementById("desktop-operator-recipe-runner")) {
    refreshDorrLatest();
  }
})();

// ─── Parallel Agent Relay Truth (N+4.5A) ─────────────────────────────────────
(function () {
  const RELAY_API = "/api/agent-relay/status";

  function relayCard(data) {
    if (!data || !data.ok) {
      return `<p class="empty-state">Parallel Agent Relay status unavailable.</p>`;
    }
    return `
      <h3 class="card-title">Parallel Agent Relay Truth</h3>
      <ul class="status-list">
        <li><strong>Mode:</strong> ${data.relay_mode || "copy_paste_only"}</li>
        <li><strong>Autonomous launch:</strong> ${data.autonomous_launch ? "YES ⚠️" : "NO — human approval required"}</li>
        <li><strong>Claude lane:</strong> /ultraplan + /goal — max planning, Sonnet high execution</li>
        <li><strong>Codex lane:</strong> extra high effort, poll remote refs (ls-remote), no /goal</li>
        <li><strong>Pairs generated:</strong> ${data.pair_count ?? 0}</li>
        <li><strong>Future-compatible:</strong> AEX, Claude Cowork, The Agency, agent-skills-eval</li>
        <li><strong>Relay version:</strong> ${data.relay_version || "—"}</li>
      </ul>`;
  }

  async function refreshRelayStatus() {
    const card = document.getElementById("agent-relay-card");
    if (!card) return;
    try {
      const res = await fetch(RELAY_API);
      const data = await res.json();
      card.innerHTML = relayCard(data);
    } catch (_) {
      card.innerHTML = `<p class="empty-state">Could not load relay status.</p>`;
    }
  }

  if (document.getElementById("section-agent-relay")) {
    refreshRelayStatus();
  }
})();

// ---------------------------------------------------------------------
// N+4.6A Ghoti Product Control Center (client-side handlers)
// ---------------------------------------------------------------------
(function attachProductControlCenter() {
  function esc(value) {
    return escapeHtml(String(value == null ? "" : value));
  }
  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value || "none";
  }
  function setActionResult(text) {
    const el = document.getElementById("product-action-result");
    if (!el) return;
    el.innerHTML = "";
    const p = document.createElement("p");
    p.textContent = text;
    el.appendChild(p);
  }
  async function callProduct(endpoint, method, body) {
    const opts = { method: method, headers: { "Content-Type": "application/json" } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(endpoint, opts);
    return await res.json();
  }
  function renderCapabilities(data) {
    const list = document.getElementById("product-control-capabilities");
    if (!list) return;
    if (!data || !data.ok || !Array.isArray(data.capabilities)) {
      list.innerHTML = '<li class="empty-state">Product status unavailable.</li>';
      return;
    }
    const rows = data.capabilities.map(function (c) {
      const state = c.available ? "available" : "unavailable";
      const mode = c.mode ? " (" + esc(c.mode) + ")" : "";
      return "<li><strong>" + esc(c.label) + ":</strong> " + state + mode +
        " — " + esc(c.how_to_run) + "</li>";
    });
    rows.push("<li><strong>Mode:</strong> local_only=" + esc(data.local_only) +
      ", live_posting=" + esc(data.live_posting) +
      ", live_account_actions=" + esc(data.live_account_actions) +
      ", external_tools=" + esc(data.external_tools) +
      ", approval_gates=" + esc(data.approval_gates) + "</li>");
    list.innerHTML = rows.join("");
  }
  function renderLatest(data) {
    const latest = data && data.latest ? data.latest : {};
    setText("product-latest-content-studio",
      latest.content_studio_run ? latest.content_studio_run.path : "none");
    setText("product-latest-relay-pair",
      latest.relay_pair ? latest.relay_pair.path : "none");
    setText("product-latest-desktop-operator",
      latest.desktop_operator_run
        ? (latest.desktop_operator_run.execution_result_path ||
           latest.desktop_operator_run.handoff_path || "none")
        : "none");
    setText("product-latest-preview", latest.preview_path || "none");
  }
  async function refreshProductStatus() {
    try {
      renderCapabilities(await callProduct("/api/product-control/status", "GET"));
    } catch (err) {
      const list = document.getElementById("product-control-capabilities");
      if (list) list.innerHTML = '<li class="empty-state">Could not load product status.</li>';
    }
    try {
      renderLatest(await callProduct("/api/product-control/latest", "GET"));
    } catch (err) { /* silent — latest is best-effort */ }
  }
  function bind(id, fn) {
    const el = document.getElementById(id);
    if (el) el.addEventListener("click", fn);
  }
  bind("product-refresh-btn", async function () {
    setActionResult("Refreshing product status…");
    await refreshProductStatus();
    setActionResult("Product status refreshed.");
  });
  bind("product-run-content-studio-btn", async function () {
    setActionResult("Running Local Content Studio (dry-run only — no live posting, no external API)…");
    try {
      const data = await callProduct("/api/product-control/run-content-studio-demo", "POST", {});
      if (data && data.ok) {
        setActionResult("Local Content Studio dry-run complete (mode=" + (data.mode || "dry_run") +
          "). No live posting, no external API.");
      } else {
        setActionResult("Local Content Studio reported unavailable: " +
          ((data && data.error) || "unknown") + " (truthful report, no crash).");
      }
      await refreshProductStatus();
    } catch (err) {
      setActionResult("Local Content Studio could not run: " + (err && err.message));
    }
  });
  bind("product-create-relay-pair-btn", async function () {
    setActionResult("Generating Claude + Codex prompt pair (copy-paste only — no agent launch)…");
    try {
      const data = await callProduct("/api/product-control/create-relay-pair", "POST", {});
      if (data && data.ok) {
        setActionResult("Prompt pair generated at " + (data.pair_dir || "(see latest)") +
          ". Copy-paste each prompt manually — nothing was launched automatically.");
      } else {
        setActionResult("Relay pair generation reported unavailable: " +
          ((data && data.error) || "unknown"));
      }
      await refreshProductStatus();
    } catch (err) {
      setActionResult("Relay pair could not be generated: " + (err && err.message));
    }
  });
  bind("product-open-preview-btn", async function () {
    try {
      const data = await callProduct("/api/product-control/latest", "GET");
      const preview = data && data.latest ? data.latest.preview_path : null;
      if (preview) {
        setActionResult("Latest preview is a local repo file: " + preview +
          ". No external browser was opened automatically.");
      } else {
        setActionResult("No local preview available yet. Run a content studio or desktop operator workflow first.");
      }
      renderLatest(data);
    } catch (err) {
      setActionResult("Could not read latest preview: " + (err && err.message));
    }
  });
  if (document.getElementById("section-product-control")) {
    refreshProductStatus();
  }
})();

// ---------------------------------------------------------------------
// N+5.5A Local Memory / Context Pack (client-side handlers)
// ---------------------------------------------------------------------
(function attachLocalMemoryContextPack() {
  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value || "none";
  }
  function setResult(text) {
    const el = document.getElementById("context-pack-action-result");
    if (!el) return;
    el.innerHTML = "";
    const p = document.createElement("p");
    p.textContent = text;
    el.appendChild(p);
  }
  async function callContextPack(endpoint, method) {
    const res = await fetch(endpoint, { method: method || "GET", headers: { "Content-Type": "application/json" } });
    return await res.json();
  }
  function renderStatus(data) {
    if (!data || !data.ok) {
      setText("context-pack-generated-at", "unavailable");
      setText("context-pack-status-short", (data && data.error) || "Context pack status unavailable.");
      return;
    }
    setText("context-pack-generated-at", data.generated_at || "not generated yet");
    setText("context-pack-main-hash", data.main_hash || "origin/main pending");
    setText("context-pack-status-short", data.status_short || "No generated context pack yet.");
    setText("context-pack-latest-path", data.latest_context_pack_path || (data.paths && data.paths["ghoti_current_context_pack.md"]));
    setText("context-pack-prompt-path", data.copy_paste_prompt_path || (data.paths && data.paths["ghoti_codex_next_prompt.md"]));
  }
  async function refreshContextPackStatus() {
    try {
      renderStatus(await callContextPack("/api/local-memory-context-pack/status", "GET"));
    } catch (err) {
      setText("context-pack-status-short", "Could not load context pack status.");
    }
  }
  function bind(id, fn) {
    const el = document.getElementById(id);
    if (el) el.addEventListener("click", fn);
  }
  bind("context-pack-refresh-btn", async function () {
    setResult("Refreshing context pack status...");
    await refreshContextPackStatus();
    setResult("Context pack status refreshed.");
  });
  bind("context-pack-build-btn", async function () {
    setResult("Generating repo-local context pack files...");
    try {
      const data = await callContextPack("/api/local-memory-context-pack/build", "POST");
      renderStatus(data);
      setResult(data && data.ok
        ? "Context pack generated. Copy-paste prompt path is shown above."
        : "Context pack generation reported unavailable: " + ((data && data.error) || "unknown"));
    } catch (err) {
      setResult("Context pack generation failed: " + (err && err.message));
    }
  });
  if (document.getElementById("ghoti-context-pack-card")) {
    refreshContextPackStatus();
  }
})();

// ---------------------------------------------------------------------
// N+5.6A Local Model / Easy Worker Lane (client-side handlers)
// ---------------------------------------------------------------------
(function attachLocalModelEasyWorkerLane() {
  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value || "none";
  }
  function setResult(text) {
    const el = document.getElementById("local-worker-action-result");
    if (!el) return;
    el.innerHTML = "";
    const p = document.createElement("p");
    p.textContent = text;
    el.appendChild(p);
  }
  async function callLocalWorker(endpoint, method) {
    const res = await fetch(endpoint, { method: method || "GET", headers: { "Content-Type": "application/json" } });
    return await res.json();
  }
  function renderStatus(data) {
    if (!data || !data.ok) {
      setText("local-worker-status-line", (data && data.error) || "Local worker status unavailable.");
      setText("local-worker-ollama-status", "unavailable");
      setText("local-worker-gemma-status", "unavailable");
      setText("local-worker-active-mode", "unknown");
      setText("local-worker-readiness", "unknown");
      return;
    }
    const ollama = data.ollama || {};
    const gemma = data.gemma || {};
    setText("local-worker-ollama-status", ollama.available ? "installed" : "not detected");
    setText("local-worker-ollama-version", ollama.version || "unknown");
    setText("local-worker-gemma-status", gemma.installed ? ("installed: " + (gemma.model_name || "gemma")) : "missing, local_demo fallback active");
    setText("local-worker-active-mode", data.active_mode || "local_demo");
    setText("local-worker-readiness", String(data.readiness_percent || 0) + "%");
    setText("local-worker-status-line", data.status_line || "Local worker status loaded.");
    const paths = data.output_paths || data.paths || {};
    setText("local-worker-output-path", paths["local_worker_status.md"] || "14_context/local_worker/generated/");
  }
  async function refreshLocalWorkerStatus() {
    try {
      renderStatus(await callLocalWorker("/api/local-model-worker/status", "GET"));
    } catch (err) {
      setText("local-worker-status-line", "Could not load local worker status.");
    }
  }
  function bind(id, fn) {
    const el = document.getElementById(id);
    if (el) el.addEventListener("click", fn);
  }
  bind("local-worker-refresh-btn", async function () {
    setResult("Refreshing Local Model / Easy Worker Lane status...");
    await refreshLocalWorkerStatus();
    setResult("Local worker status refreshed.");
  });
  bind("local-worker-doctor-btn", async function () {
    setResult("Running local worker doctor...");
    try {
      const data = await callLocalWorker("/api/local-model-worker/doctor", "GET");
      renderStatus(data);
      const checks = Array.isArray(data && data.checks) ? data.checks.length : 0;
      setResult(data && data.ok ? ("Doctor complete: " + checks + " checks. No live APIs, no auto-downloads.") :
        "Doctor reported unavailable: " + ((data && data.error) || "unknown"));
    } catch (err) {
      setResult("Local worker doctor failed: " + (err && err.message));
    }
  });
  bind("local-worker-demo-btn", async function () {
    setResult("Writing deterministic local worker demo outputs...");
    try {
      const data = await callLocalWorker("/api/local-model-worker/write-demo-output", "POST");
      renderStatus(data);
      setResult(data && data.ok
        ? "Local worker demo outputs written under 14_context/local_worker/generated/."
        : "Local worker demo reported unavailable: " + ((data && data.error) || "unknown"));
    } catch (err) {
      setResult("Local worker demo failed: " + (err && err.message));
    }
  });
  if (document.getElementById("ghoti-local-model-worker-card")) {
    refreshLocalWorkerStatus();
  }
})();

// ---------------------------------------------------------------------
// N+6.1A Local Model Routing / Guarded Worker (client-side handlers)
// Launcher flag: --local-worker-routing-status
// ---------------------------------------------------------------------
(function attachLocalModelRoutingGuardedWorker() {
  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value || "none";
  }
  function setResult(text) {
    const el = document.getElementById("local-routing-action-result");
    if (!el) return;
    el.innerHTML = "";
    const p = document.createElement("p");
    p.textContent = text;
    el.appendChild(p);
  }
  async function callRouting(endpoint, method) {
    const res = await fetch(endpoint, { method: method || "GET", headers: { "Content-Type": "application/json" } });
    return await res.json();
  }
  function renderStatus(data) {
    if (!data || !data.ok) {
      setText("local-routing-status-line", (data && data.error) || "Guarded routing status unavailable.");
      setText("local-routing-enabled", "unknown");
      setText("local-routing-guard-enabled", "unknown");
      return;
    }
    const guard = data.guard_result || {};
    setText("local-routing-gemma-installed", data.routing_enabled_for_safe_tasks || data.gemma_attempted ? "yes" : "fallback/local_demo");
    setText("local-routing-active-model", data.active_model || data.active_route_preference || "local_demo");
    setText("local-routing-enabled", data.routing_enabled_for_safe_tasks ? "yes, safe tasks only" : "fallback only");
    setText("local-routing-guard-enabled", data.guard_enabled ? "yes" : "no");
    setText("local-routing-last-guard", guard.status || (Array.isArray(data.guard_statuses) ? data.guard_statuses.join(", ") : "not run"));
    setText("local-routing-bundle-source", data.known_bundle_allowlist_source || "14_context/repo_knowledge/generated/repo_knowledge_map.json");
    setText("local-routing-guard-status", data.guard_enabled ? "enabled; invented bundles/files rejected" : "unavailable");
    setText("local-routing-fallback", data.fallback_used ? "local_demo fallback used" : (data.fallback_available ? "local_demo fallback available" : "unknown"));
    setText("local-routing-run-path", data.latest_routing_run_path || data.run_dir || "14_context/local_worker/routing_runs/");
    setText("local-routing-status-line", data.status_line || ("Guarded routing loaded. Active route: " + (data.active_route || data.active_route_preference || "unknown")));
  }
  async function refreshRoutingStatus() {
    try {
      renderStatus(await callRouting("/api/local-model-worker/routing-status", "GET"));
    } catch (err) {
      setText("local-routing-status-line", "Could not load guarded routing status.");
    }
  }
  function bind(id, fn) {
    const el = document.getElementById(id);
    if (el) el.addEventListener("click", fn);
  }
  bind("local-routing-refresh-btn", async function () {
    setResult("Refreshing guarded routing status...");
    await refreshRoutingStatus();
    setResult("Guarded routing status refreshed.");
  });
  bind("local-routing-route-btn", async function () {
    setResult("Routing status paragraph through guard...");
    try {
      const data = await callRouting("/api/local-model-worker/route-task?task=status-paragraph", "POST");
      renderStatus(data);
      setResult(data && data.ok
        ? "Route complete. Guard result: " + ((data.guard_result && data.guard_result.status) || "unknown") + ". No commands executed from model output."
        : "Route task reported unavailable: " + ((data && data.error) || "unknown"));
    } catch (err) {
      setResult("Route task failed: " + (err && err.message));
    }
  });
  bind("local-routing-demo-btn", async function () {
    setResult("Writing guarded routing demo...");
    try {
      const data = await callRouting("/api/local-model-worker/write-routing-demo", "POST");
      renderStatus(data);
      setResult(data && data.ok
        ? "Guarded routing demo written under 14_context/local_worker/routing_runs/."
        : "Routing demo reported unavailable: " + ((data && data.error) || "unknown"));
    } catch (err) {
      setResult("Routing demo failed: " + (err && err.message));
    }
  });
  if (document.getElementById("ghoti-local-model-routing-card")) {
    refreshRoutingStatus();
  }
})();

// ---------------------------------------------------------------------
// N+5.9A Gemma / Local Model Quality (client-side handlers)
// ---------------------------------------------------------------------
(function attachGemmaReadinessLane() {
  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value || "none";
  }
  function setResult(text) {
    const el = document.getElementById("gemma-action-result");
    if (!el) return;
    el.innerHTML = "";
    const p = document.createElement("p");
    p.textContent = text;
    el.appendChild(p);
  }
  async function callGemma(endpoint, method) {
    const res = await fetch(endpoint, { method: method || "GET", headers: { "Content-Type": "application/json" } });
    return await res.json();
  }
  function renderStatus(data) {
    if (!data || !data.ok) {
      setText("gemma-status-line", (data && data.error) || "Gemma readiness unavailable.");
      setText("gemma-ollama-installed", "unavailable");
      setText("gemma-installed-status", "unavailable");
      setText("gemma-active-mode", "unknown");
      setText("gemma-readiness-percent", "unknown");
      return;
    }
    const paths = data.output_paths || data.paths || {};
    const selected = data.selected_model || "local_demo";
    setText("gemma-ollama-installed", data.ollama_installed ? "yes" : "not detected");
    setText("gemma-ollama-version", data.ollama_version || "unknown");
    setText("gemma-installed-model-count", String(data.installed_models_count || 0));
    setText("gemma-installed-status", data.gemma_installed ? ("yes: " + (data.installed_gemma_models || []).join(", ")) : "Gemma missing");
    setText("gemma-selected-model", selected);
    setText("gemma-active-mode", data.active_worker_mode || "local_demo fallback");
    setText("gemma-readiness-percent", String(data.gemma_readiness_percent || data.readiness_percent || 0) + "%");
    setText("gemma-local-worker-readiness", String(data.local_worker_readiness_percent || 0) + "%");
    setText("gemma-manual-command", data.recommended_manual_command || "ollama pull gemma3:4b");
    setText("gemma-quality-status", data.quality_evaluation_status || "pending/not run");
    setText("gemma-real-eval-status", data.real_local_evaluation_status || data.quality_evaluation_status || "not run");
    setText("gemma-eval-score", data.score_percent !== undefined ? String(data.score_percent) + "%" : (data.latest_eval_score_percent !== null && data.latest_eval_score_percent !== undefined ? String(data.latest_eval_score_percent) + "%" : "not run"));
    setText("gemma-latest-eval-run", data.run_dir || data.latest_eval_run_path || "14_context/local_model_evaluation/runs/");
    setText("gemma-output-path", paths["gemma_readiness_status.md"] || "14_context/local_model_readiness/generated/gemma_readiness_status.md");
    setText("gemma-status-line", data.status_line || "Gemma readiness loaded.");
  }
  async function refreshGemmaStatus() {
    try {
      renderStatus(await callGemma("/api/gemma-readiness/status", "GET"));
    } catch (err) {
      setText("gemma-status-line", "Could not load Gemma readiness.");
    }
  }
  function bind(id, fn) {
    const el = document.getElementById(id);
    if (el) el.addEventListener("click", fn);
  }
  bind("gemma-refresh-btn", async function () {
    setResult("Refreshing Gemma / Local Model Quality status...");
    await refreshGemmaStatus();
    setResult("Gemma readiness refreshed.");
  });
  bind("gemma-doctor-btn", async function () {
    setResult("Running Gemma doctor...");
    try {
      const data = await callGemma("/api/gemma-readiness/doctor", "GET");
      renderStatus(data);
      const checks = Array.isArray(data && data.checks) ? data.checks.length : 0;
      setResult(data && data.ok ? ("Doctor complete: " + checks + " checks. No live APIs, no auto-downloads.") :
        "Gemma doctor reported unavailable: " + ((data && data.error) || "unknown"));
    } catch (err) {
      setResult("Gemma doctor failed: " + (err && err.message));
    }
  });
  bind("gemma-quality-btn", async function () {
    setResult("Loading local task quality plan...");
    try {
      const data = await callGemma("/api/gemma-readiness/quality-plan", "GET");
      renderStatus(data && data.status ? data.status : data);
      const evalData = data && data.quality_evaluation;
      setResult(evalData
        ? "Quality plan loaded: mode " + evalData.mode + ", score " + evalData.score_percent + "%. Production routing remains disabled."
        : "Quality plan loaded.");
    } catch (err) {
      setResult("Gemma quality plan failed: " + (err && err.message));
    }
  });
  bind("gemma-local-eval-btn", async function () {
    setResult("Loading local model evaluation summary...");
    try {
      const data = await callGemma("/api/gemma-readiness/local-model-eval", "GET");
      renderStatus(data && data.status ? Object.assign({}, data.status, data) : data);
      setResult(data && data.ok
        ? "Local eval loaded: mode " + data.mode + ", model " + data.model + ", score " + data.score_percent + "%. Production routing remains disabled."
        : "Local eval reported unavailable: " + ((data && data.error) || "unknown"));
    } catch (err) {
      setResult("Local eval failed: " + (err && err.message));
    }
  });
  bind("gemma-write-btn", async function () {
    setResult("Writing Gemma readiness files...");
    try {
      const data = await callGemma("/api/gemma-readiness/write-readiness", "POST");
      renderStatus(data);
      setResult(data && data.ok
        ? "Gemma readiness files written under 14_context/local_model_readiness/generated/."
        : "Gemma readiness write reported unavailable: " + ((data && data.error) || "unknown"));
    } catch (err) {
      setResult("Gemma readiness write failed: " + (err && err.message));
    }
  });
  if (document.getElementById("ghoti-gemma-readiness-card")) {
    refreshGemmaStatus();
  }
})();

// ---------------------------------------------------------------------
// N+5.7A Repo Knowledge / Graphify Lane (client-side handlers)
// ---------------------------------------------------------------------
(function attachRepoKnowledgeGraphifyLane() {
  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value || "none";
  }
  function setResult(text) {
    const el = document.getElementById("repo-knowledge-action-result");
    if (!el) return;
    el.innerHTML = "";
    const p = document.createElement("p");
    p.textContent = text;
    el.appendChild(p);
  }
  async function callRepoKnowledge(endpoint, method) {
    const res = await fetch(endpoint, { method: method || "GET", headers: { "Content-Type": "application/json" } });
    return await res.json();
  }
  function renderStatus(data) {
    if (!data || !data.ok) {
      setText("repo-knowledge-status-line", (data && data.error) || "Repo knowledge status unavailable.");
      setText("repo-knowledge-readiness", "unknown");
      return;
    }
    const paths = data.output_paths || data.paths || {};
    const bundles = data.task_bundle_paths || {};
    setText("repo-knowledge-status-line", data.status_line || "Repo knowledge status loaded.");
    setText("repo-knowledge-readiness", String(data.readiness_percent || 0) + "%");
    setText("repo-knowledge-map-path", paths["repo_knowledge_map.md"] || data.latest_map_path || "14_context/repo_knowledge/generated/repo_knowledge_map.md");
    setText("repo-knowledge-report-index", paths["latest_reports_index.md"] || data.latest_report_index_path || "14_context/repo_knowledge/generated/latest_reports_index.md");
    setText("repo-knowledge-bundle-path", bundles["next-milestone"] || paths["task_bundle_next_milestone.md"] || "14_context/repo_knowledge/generated/task_bundle_next_milestone.md");
    setText("repo-knowledge-prompt-path", paths["codex_next_prompt_graph_context.md"] || "14_context/repo_knowledge/generated/codex_next_prompt_graph_context.md");
  }
  async function refreshRepoKnowledgeStatus() {
    try {
      renderStatus(await callRepoKnowledge("/api/repo-knowledge/status", "GET"));
    } catch (err) {
      setText("repo-knowledge-status-line", "Could not load repo knowledge status.");
    }
  }
  function bind(id, fn) {
    const el = document.getElementById(id);
    if (el) el.addEventListener("click", fn);
  }
  bind("repo-knowledge-refresh-btn", async function () {
    setResult("Refreshing repo knowledge readiness...");
    await refreshRepoKnowledgeStatus();
    setResult("Repo knowledge status refreshed.");
  });
  bind("repo-knowledge-write-btn", async function () {
    setResult("Generating local repo knowledge map and task bundles...");
    try {
      const data = await callRepoKnowledge("/api/repo-knowledge/write", "POST");
      renderStatus(data);
      setResult(data && data.ok
        ? "Repo knowledge map generated. Latest report index and task bundles are shown above."
        : "Repo knowledge generation reported unavailable: " + ((data && data.error) || "unknown"));
    } catch (err) {
      setResult("Repo knowledge generation failed: " + (err && err.message));
    }
  });
  bind("repo-knowledge-bundle-btn", async function () {
    setResult("Loading next-milestone task bundle...");
    try {
      const data = await callRepoKnowledge("/api/repo-knowledge/bundle?name=next-milestone", "GET");
      setResult(data && data.ok
        ? "Next bundle loaded. Use the generated bundle path for focused Codex/ChatGPT context."
        : "Repo knowledge bundle reported unavailable: " + ((data && data.error) || "unknown"));
    } catch (err) {
      setResult("Repo knowledge bundle failed: " + (err && err.message));
    }
  });
  if (document.getElementById("ghoti-repo-knowledge-card")) {
    refreshRepoKnowledgeStatus();
  }
})();

// ---------------------------------------------------------------------
// N+5.8A Hermes Agent / Manual Bridge (client-side handlers)
// ---------------------------------------------------------------------
(function attachHermesAgentManualBridge() {
  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value || "none";
  }
  function setResult(text) {
    const el = document.getElementById("hermes-bridge-action-result");
    if (!el) return;
    el.innerHTML = "";
    const p = document.createElement("p");
    p.textContent = text;
    el.appendChild(p);
  }
  async function callHermesBridge(endpoint, method) {
    const res = await fetch(endpoint, { method: method || "GET", headers: { "Content-Type": "application/json" } });
    return await res.json();
  }
  function renderStatus(data) {
    if (!data || !data.ok) {
      setText("hermes-bridge-status-line", (data && data.error) || "Hermes bridge status unavailable.");
      setText("hermes-bridge-installed", "unknown");
      setText("hermes-bridge-readiness", "unknown");
      return;
    }
    const paths = data.output_paths || data.paths || {};
    setText("hermes-bridge-installed", data.installed ? "yes" : "not detected");
    setText("hermes-bridge-path", data.path || data.expected_path || "/home/ai_sandbox/.local/bin/hermes");
    setText("hermes-bridge-version", data.version || "unknown");
    setText("hermes-bridge-skills-count", String(data.skills_count || 0));
    setText("hermes-bridge-readiness", String(data.readiness_percent || 0) + "%");
    setText("hermes-bridge-output-path", paths["hermes_workflow_status.md"] || data.latest_status_path || "14_context/hermes_workflow/generated/hermes_workflow_status.md");
    setText("hermes-bridge-status-line", data.status_line || "Hermes bridge status loaded.");
  }
  async function refreshHermesBridgeStatus() {
    try {
      renderStatus(await callHermesBridge("/api/hermes-bridge/status", "GET"));
    } catch (err) {
      setText("hermes-bridge-status-line", "Could not load Hermes bridge status.");
    }
  }
  function bind(id, fn) {
    const el = document.getElementById(id);
    if (el) el.addEventListener("click", fn);
  }
  bind("hermes-bridge-refresh-btn", async function () {
    setResult("Refreshing Hermes Agent / Manual Bridge status...");
    await refreshHermesBridgeStatus();
    setResult("Hermes bridge status refreshed. Safe probes only.");
  });
  bind("hermes-bridge-skills-btn", async function () {
    setResult("Loading Hermes skills index with safe probes only...");
    try {
      const data = await callHermesBridge("/api/hermes-bridge/skills-index", "GET");
      setText("hermes-bridge-skills-count", String((data && data.skills_count) || 0));
      setResult(data && data.ok
        ? "Hermes skills index loaded. Provider setup and Telegram remain manual."
        : "Hermes skills index unavailable: " + ((data && data.error) || "unknown"));
    } catch (err) {
      setResult("Hermes skills index failed: " + (err && err.message));
    }
  });
  bind("hermes-bridge-write-btn", async function () {
    setResult("Writing Hermes readiness files. No live provider setup, tokens, or browser automation...");
    try {
      const data = await callHermesBridge("/api/hermes-bridge/write-readiness", "POST");
      renderStatus(data);
      setResult(data && data.ok
        ? "Hermes readiness files written under 14_context/hermes_workflow/generated/."
        : "Hermes readiness write reported unavailable: " + ((data && data.error) || "unknown"));
    } catch (err) {
      setResult("Hermes readiness write failed: " + (err && err.message));
    }
  });
  if (document.getElementById("ghoti-hermes-bridge-card")) {
    refreshHermesBridgeStatus();
  }
})();

// ---------------------------------------------------------------------
// N+6.2A Hermes Manual Bridge / WSL Guide (client-side handlers)
// ---------------------------------------------------------------------
(function attachHermesManualBridgeWslGuide() {
  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value || "none";
  }
  function setResult(text) {
    const el = document.getElementById("hermes-manual-action-result");
    if (!el) return;
    el.innerHTML = "";
    const p = document.createElement("p");
    p.textContent = text;
    el.appendChild(p);
  }
  async function callHermesManual(endpoint, method) {
    const res = await fetch(endpoint, { method: method || "GET", headers: { "Content-Type": "application/json" } });
    return await res.json();
  }
  function renderStatus(data) {
    if (!data || !data.ok) {
      setText("hermes-manual-status-line", (data && data.error) || "Hermes manual bridge status unavailable.");
      setText("hermes-manual-readiness", "unknown");
      return;
    }
    const wsl = data.wsl_explanation || {};
    const paths = data.paths || {};
    setText("hermes-manual-wsl-map", (wsl.windows_repo_path || "C:\\Users\\ai_sandbox\\Documents\\AI_Managed_Only") +
      " -> " + (wsl.wsl_repo_path || "/mnt/c/Users/ai_sandbox/Documents/AI_Managed_Only"));
    setText("hermes-manual-path", data.path || data.expected_path || "/home/ai_sandbox/.local/bin/hermes");
    setText("hermes-manual-version", data.version || "unknown");
    setText("hermes-manual-skills-count", String(data.skills_count || 0));
    setText("hermes-manual-readiness", String(data.readiness_percent || 0) + "%");
    setText("hermes-manual-guide-path", data.latest_wsl_usage_guide_path || paths["01_wsl_usage_guide.md"] ||
      "14_context/hermes_manual_bridge/generated/01_wsl_usage_guide.md");
    setText("hermes-manual-status-line", data.status_line || "Hermes manual bridge status loaded.");
  }
  async function refreshHermesManualStatus() {
    try {
      renderStatus(await callHermesManual("/api/hermes-manual-bridge/status", "GET"));
    } catch (err) {
      setText("hermes-manual-status-line", "Could not load Hermes manual bridge status.");
    }
  }
  function bind(id, fn) {
    const el = document.getElementById(id);
    if (el) el.addEventListener("click", fn);
  }
  bind("hermes-manual-refresh-btn", async function () {
    setResult("Refreshing Hermes manual bridge status...");
    await refreshHermesManualStatus();
    setResult("Hermes manual bridge status refreshed. Safe probes only.");
  });
  bind("hermes-manual-wsl-btn", async function () {
    setResult("Loading WSL path guide...");
    try {
      const data = await callHermesManual("/api/hermes-manual-bridge/wsl-explain", "GET");
      setResult(data && data.ok
        ? "WSL path guide: " + data.windows_repo_path + " maps to " + data.wsl_repo_path + "."
        : "WSL guide unavailable: " + ((data && data.error) || "unknown"));
    } catch (err) {
      setResult("WSL guide failed: " + (err && err.message));
    }
  });
  bind("hermes-manual-safe-btn", async function () {
    setResult("Loading Hermes safe command list...");
    try {
      const data = await callHermesManual("/api/hermes-manual-bridge/safe-commands", "GET");
      const count = Array.isArray(data && data.safe_commands) ? data.safe_commands.length : 0;
      setResult(data && data.ok
        ? "Safe command list loaded: " + count + " read-only probes. No live provider setup."
        : "Safe commands unavailable: " + ((data && data.error) || "unknown"));
    } catch (err) {
      setResult("Safe commands failed: " + (err && err.message));
    }
  });
  bind("hermes-manual-write-btn", async function () {
    setResult("Writing Hermes manual bridge guide files...");
    try {
      const data = await callHermesManual("/api/hermes-manual-bridge/write-guide", "POST");
      renderStatus(data);
      setResult(data && data.ok
        ? "Hermes manual bridge guide files written under 14_context/hermes_manual_bridge/generated/."
        : "Hermes manual bridge write unavailable: " + ((data && data.error) || "unknown"));
    } catch (err) {
      setResult("Hermes manual bridge write failed: " + (err && err.message));
    }
  });
  if (document.getElementById("ghoti-hermes-manual-card")) {
    refreshHermesManualStatus();
  }
})();

// ---------------------------------------------------------------------
// N+4.8A External Tool Sandbox Truth (client-side handler, read-only)
// ---------------------------------------------------------------------
(function attachExternalToolSandbox() {
  function renderCloneStatus(data) {
    const el = document.getElementById("external-tool-sandbox-clone-status");
    if (!el) return;
    if (!data || !data.ok) {
      el.textContent = "External Tool Sandbox status unavailable.";
      return;
    }
    const repos = Array.isArray(data.repos) ? data.repos : [];
    if (repos.length === 0) {
      el.textContent = "no repos synced yet — static scan only, no install, no runtime wiring";
      return;
    }
    const cloned = repos.filter(function (r) { return r.clone_status === "cloned"; }).length;
    const parts = repos.map(function (r) {
      return (r.name || r.slug || "?") + ": " + (r.clone_status || "unknown");
    });
    el.textContent = cloned + "/" + repos.length + " cloned — " + parts.join("; ") +
      " (static scan only — no install, no runtime wiring, no desktop control, no live APIs)";
  }
  async function refreshExternalToolSandbox() {
    const el = document.getElementById("external-tool-sandbox-clone-status");
    if (!el) return;
    try {
      const res = await fetch("/api/external-tool-sandbox/status");
      renderCloneStatus(await res.json());
    } catch (err) {
      el.textContent = "Could not load External Tool Sandbox status.";
    }
  }
  if (document.getElementById("external-tool-sandbox-truth")) {
    refreshExternalToolSandbox();
  }
})();

// ---------------------------------------------------------------------
// N+4.9A Approved Adapter Execution Truth (client-side handlers)
// ---------------------------------------------------------------------
(function attachApprovedAdapterExecution() {
  function setLatest(text) {
    const el = document.getElementById("adapter-exec-latest");
    if (el) el.textContent = text || "none";
  }
  function setResult(text) {
    const host = document.getElementById("adapter-exec-status");
    if (!host) return;
    let res = document.getElementById("adapter-exec-result");
    if (!res) {
      res = document.createElement("p");
      res.id = "adapter-exec-result";
      host.appendChild(res);
    }
    res.textContent = text;
  }
  async function call(endpoint, method) {
    const res = await fetch(endpoint, {
      method: method, headers: { "Content-Type": "application/json" },
    });
    return await res.json();
  }
  async function refreshLatest() {
    try {
      const data = await call("/api/adapter-execution/latest", "GET");
      const latest = data && data.latest;
      if (latest) {
        setLatest(latest.run_id + " — score " + latest.evaluation_score +
          "/100 (" + latest.evaluation_grade + "), " +
          (latest.artifacts ? latest.artifacts.length : 0) + " local artifacts");
      } else {
        setLatest("none yet — run the safe adapter demo");
      }
    } catch (err) {
      setLatest("unavailable");
    }
  }
  function bind(id, fn) {
    const el = document.getElementById(id);
    if (el) el.addEventListener("click", fn);
  }
  bind("adapter-exec-refresh-btn", async function () {
    setResult("Refreshing adapter status…");
    try {
      const data = await call("/api/adapter-execution/status", "GET");
      setResult("Adapter runner: " + (data && data.ok ? "ok" : "unavailable") +
        " — default adapter " + ((data && data.default_adapter) || "?") +
        ", external_code_executed=" + String(data && data.external_code_executed));
    } catch (err) {
      setResult("Could not load adapter status.");
    }
    await refreshLatest();
  });
  bind("adapter-exec-list-btn", async function () {
    setResult("Listing adapters…");
    try {
      const data = await call("/api/adapter-execution/adapters", "GET");
      const names = ((data && data.adapters) || []).map(function (a) {
        return a.key + (a.execution_approved ? " (approved)" : " (not approved)");
      });
      setResult("Adapters: " + names.join("; "));
    } catch (err) {
      setResult("Could not list adapters.");
    }
  });
  bind("adapter-exec-create-approval-btn", async function () {
    setResult("Creating approval…");
    try {
      const data = await call("/api/adapter-execution/create-approval", "POST");
      if (data && data.ok) {
        // The one-time token is never rendered to the page or returned by GET.
        setResult("Approval created: " + data.approval_id +
          ". A one-time approval token was issued — use it from the CLI for a non-dry-run.");
      } else {
        setResult("Approval creation unavailable: " + ((data && data.error) || "unknown"));
      }
    } catch (err) {
      setResult("Could not create approval.");
    }
  });
  bind("adapter-exec-run-demo-btn", async function () {
    setResult("Running safe adapter demo (dry run — no approval token, no external code)…");
    try {
      const data = await call("/api/adapter-execution/run-demo", "POST");
      if (data && data.ok) {
        setResult("Dry-run demo complete: " + data.run_id + " — score " +
          data.evaluation_score + "/100 (" + data.evaluation_grade + "); " +
          ((data.artifacts || []).length) + " local artifacts written.");
      } else {
        setResult("Demo run unavailable: " + ((data && data.error) || "unknown"));
      }
      await refreshLatest();
    } catch (err) {
      setResult("Could not run adapter demo.");
    }
  });
  if (document.getElementById("approved-adapter-execution-truth")) {
    refreshLatest();
  }
})();

// ---------------------------------------------------------------------
// N+5.0A UI-TARS Observation Truth (client-side handlers, observation-only)
// ---------------------------------------------------------------------
(function attachUiTarsObservation() {
  function setLatest(text) {
    const el = document.getElementById("ui-tars-obs-latest");
    if (el) el.textContent = text || "none";
  }
  function setResult(text) {
    const host = document.getElementById("ui-tars-obs-status");
    if (!host) return;
    let res = document.getElementById("ui-tars-obs-result");
    if (!res) {
      res = document.createElement("p");
      res.id = "ui-tars-obs-result";
      host.appendChild(res);
    }
    res.textContent = text;
  }
  async function call(endpoint, method) {
    const res = await fetch(endpoint, {
      method: method, headers: { "Content-Type": "application/json" },
    });
    return await res.json();
  }
  async function refreshLatest() {
    try {
      const data = await call("/api/ui-tars-observation/latest", "GET");
      const latest = data && data.latest;
      if (latest) {
        setLatest(latest.run_id + " — " + latest.mode + ", screenshot_captured=" +
          String(latest.screenshot_captured) + ", " +
          (latest.artifacts ? latest.artifacts.length : 0) + " local artifacts");
      } else {
        setLatest("none yet — run a dry-run observation");
      }
    } catch (err) {
      setLatest("unavailable");
    }
  }
  function bind(id, fn) {
    const el = document.getElementById(id);
    if (el) el.addEventListener("click", fn);
  }
  bind("ui-tars-obs-refresh-btn", async function () {
    setResult("Refreshing observation status…");
    try {
      const data = await call("/api/ui-tars-observation/status", "GET");
      setResult("Observation adapter: " + (data && data.ok ? "ok" : "unavailable") +
        " — mode " + ((data && data.mode) || "?") +
        ", ui_tars_runtime_started=" + String(data && data.ui_tars_runtime_started) +
        ", desktop_control_enabled=" + String(data && data.desktop_control_enabled));
    } catch (err) {
      setResult("Could not load observation status.");
    }
    await refreshLatest();
  });
  bind("ui-tars-obs-create-approval-btn", async function () {
    setResult("Creating approval…");
    try {
      const data = await call("/api/ui-tars-observation/create-approval", "POST");
      if (data && data.ok) {
        // The one-time token is never rendered to the page or returned by GET.
        setResult("Approval created: " + data.approval_id +
          ". A one-time token was issued — use it from the CLI for an approved screen capture.");
      } else {
        setResult("Approval creation unavailable: " + ((data && data.error) || "unknown"));
      }
    } catch (err) {
      setResult("Could not create approval.");
    }
  });
  bind("ui-tars-obs-dry-run-btn", async function () {
    setResult("Running dry-run observation (no screenshot, no desktop control, no UI-TARS)…");
    try {
      const data = await call("/api/ui-tars-observation/dry-run", "POST");
      if (data && data.ok) {
        setResult("Dry-run observation complete: " + data.run_id + " — " +
          ((data.artifacts || []).length) + " local artifacts; screenshot_captured=" +
          String(data.screenshot_captured) + ".");
      } else {
        setResult("Observation run unavailable: " + ((data && data.error) || "unknown"));
      }
      await refreshLatest();
    } catch (err) {
      setResult("Could not run observation.");
    }
  });
  if (document.getElementById("ui-tars-observation-truth")) {
    refreshLatest();
  }
})();
