"use strict";

const POLL_MS = 2500;

let isActive = false;

const dock = document.getElementById("operator-dock");
const emptyState = document.getElementById("dock-empty-state");
const dockStatus = document.getElementById("dock-status");
const dockStatusValue = document.getElementById("dock-status-value");
const dockTargetValue = document.getElementById("dock-target-value");
const dockAlertsValue = document.getElementById("dock-alerts-value");
const dockApprovalsValue = document.getElementById("dock-approvals-value");
const dockNextValue = document.getElementById("dock-next-value");
const dockStartBtn = document.getElementById("dock-start-btn");
const dockDiagBtn = document.getElementById("dock-diag-btn");
const dockCaptureRow = document.getElementById("dock-capture-row");
const dockCaptureLabel = document.getElementById("dock-capture-label");

const diagDrawer = document.getElementById("diag-drawer");
const diagCloseBtn = document.getElementById("diag-close-btn");
const diagRoutesEl = document.getElementById("diag-routes");
const diagBuildEl = document.getElementById("diag-build");
const diagBrainEl = document.getElementById("diag-brain");
const diagRawStateEl = document.getElementById("diag-raw-state");
const diagVoiceEl = document.getElementById("diag-voice");

let lastRawState = {};

async function safeFetch(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) return { _status: res.status, _url: url, ok: false };
    return await res.json();
  } catch {
    return { _error: "unreachable", _url: url, ok: false };
  }
}

function setDockEmptyState() {
  if (emptyState) emptyState.hidden = false;
  if (dockStatus) dockStatus.hidden = true;
  if (dock) dock.dataset.status = "Idle";
}

function setDockActiveState() {
  if (emptyState) emptyState.hidden = true;
  if (dockStatus) dockStatus.hidden = false;
}

async function fetchState() {
  const [activeData, operatorData, approvalsData] = await Promise.all([
    safeFetch("/api/ghoti/active-state"),
    safeFetch("/api/ghoti/operator/status"),
    safeFetch("/api/ghoti/approvals?status=pending"),
  ]);

  lastRawState = { activeData, operatorData, approvalsData };

  isActive = Boolean(activeData?.state?.active);
  const watchdog = operatorData?.operator?.watchdog || operatorData?.watchdog || {};
  const overlayTarget = operatorData?.operator?.overlayTarget || operatorData?.overlayTarget || watchdog.overlayTarget || {};
  const alertCount = Array.isArray(watchdog.alerts) ? watchdog.alerts.length : 0;
  const pendingApprovals = approvalsData?.pending_count ?? 0;
  const targetLabel = overlayTarget.label || null;

  // Show empty state when Ghoti is idle, no target, no alerts
  if (!isActive && !targetLabel && alertCount === 0) {
    setDockEmptyState();
  } else {
    setDockActiveState();

    const statusLabel = isActive ? "Running" : (alertCount > 0 ? "Alert" : "Idle");
    if (dockStatusValue) {
      dockStatusValue.textContent = statusLabel;
      dockStatusValue.className = "dock-value " + (isActive ? "dock-value-active" : "dock-value-idle");
    }

    if (dockTargetValue) {
      dockTargetValue.textContent = targetLabel || "No target selected";
    }

    if (dockAlertsValue) {
      dockAlertsValue.textContent = String(alertCount);
    }

    if (dockApprovalsValue) {
      dockApprovalsValue.textContent = pendingApprovals > 0
        ? `${pendingApprovals} pending — action needed`
        : "0 pending";
    }

    if (dockNextValue) {
      if (pendingApprovals > 0) {
        dockNextValue.textContent = "Open Approvals in dashboard to unblock";
      } else if (isActive) {
        dockNextValue.textContent = "Task running — watch for alerts";
      } else if (alertCount > 0) {
        dockNextValue.textContent = "Review alerts in dashboard";
      } else {
        dockNextValue.textContent = "Queue a task from the dashboard";
      }
    }
  }

  if (dock) dock.dataset.status = isActive ? "Running" : "Idle";

  if (dockStartBtn) {
    dockStartBtn.textContent = isActive ? "Stop Ghoti" : "Start Ghoti";
    dockStartBtn.classList.toggle("btn-stop", isActive);
  }
}

async function fetchCaptureState() {
  const data = await safeFetch("/api/ghoti/active/capture-state");
  const capturing = Boolean(data?.captureState?.capturing);
  if (dockCaptureRow) dockCaptureRow.hidden = !capturing;
  if (capturing && dockCaptureLabel) {
    const count = data.captureState.frame_count || 0;
    dockCaptureLabel.textContent = `Watching — ${count} frame${count !== 1 ? "s" : ""}`;
  }
}

async function openDiagnostics() {
  if (!diagDrawer) return;
  diagDrawer.hidden = false;
  diagDrawer.removeAttribute("aria-hidden");

  // Route health check
  const routeTargets = [
    "/api/ghoti/active-state",
    "/api/ghoti/models/status",
    "/api/ghoti/brain/status",
    "/api/ghoti/active/capture-state",
    "/api/operator-status",
  ];

  const routeResults = await Promise.all(
    routeTargets.map(async (url) => {
      try {
        const res = await fetch(url);
        return `${res.status}  ${url}`;
      } catch {
        return `ERR  ${url}`;
      }
    }),
  );

  if (diagRoutesEl) diagRoutesEl.textContent = routeResults.join("\n");

  // Build / model truth
  const modelStatus = await safeFetch("/api/ghoti/models/status");
  if (diagBuildEl) {
    if (modelStatus?.ok) {
      const t = modelStatus.truth || {};
      const m = modelStatus.models || {};
      diagBuildEl.textContent = [
        `Port:                  3210 (default) or $PORT`,
        `Ollama reachable:      ${modelStatus.ollama?.reachable ?? "?"}`,
        `Models found:          ${m.count ?? 0}`,
        `Gemma candidates:      ${(m.gemma_candidates || []).join(", ") || "none"}`,
        `Selected text model:   ${m.selected_text_model || "none"}`,
        `Gemma drives operator: ${t.gemma_drives_operator ?? false}`,
        `Action planning wired: ${t.action_planning ?? false}`,
        `Autonomous actions:    ${t.autonomous_actions ?? false}`,
        `Updated:               ${modelStatus.updated_at_utc || "?"}`,
      ].join("\n");
    } else {
      diagBuildEl.textContent = "Could not reach /api/ghoti/models/status";
    }
  }

  // Brain state
  const brainData = await safeFetch("/api/ghoti/brain/status");
  if (diagBrainEl) diagBrainEl.textContent = JSON.stringify(brainData, null, 2);

  // Raw operator state
  if (diagRawStateEl) diagRawStateEl.textContent = JSON.stringify(lastRawState, null, 2);

  // Voice state
  const voiceData = await safeFetch("/api/ghoti/voice/state");
  if (diagVoiceEl) diagVoiceEl.textContent = JSON.stringify(voiceData, null, 2);
}

function closeDiagnostics() {
  if (!diagDrawer) return;
  diagDrawer.hidden = true;
  diagDrawer.setAttribute("aria-hidden", "true");
}

// ── Event listeners ───────────────────────────────────────────

if (dockStartBtn) {
  dockStartBtn.addEventListener("click", async () => {
    dockStartBtn.disabled = true;
    try {
      const route = isActive ? "/api/ghoti/active/stop" : "/api/ghoti/active/start";
      await fetch(route, { method: "POST", headers: { "Content-Type": "application/json" } });
      await fetchState();
    } catch { /* ignore */ } finally {
      dockStartBtn.disabled = false;
    }
  });
}

if (dockDiagBtn) {
  dockDiagBtn.addEventListener("click", openDiagnostics);
}

if (diagCloseBtn) {
  diagCloseBtn.addEventListener("click", closeDiagnostics);
}

// Responsive collapse for narrow viewports
if (window.innerWidth < 600 && dock) {
  dock.classList.add("is-collapsed");
  dock.addEventListener("click", () => {
    dock.classList.toggle("is-collapsed");
  });
}

// ── Initial load + polling ────────────────────────────────────

fetchState();
fetchCaptureState();
setInterval(fetchState, POLL_MS);
setInterval(fetchCaptureState, POLL_MS);
