const uiState = {
  serverActions: [],
  localActions: [],
  nextLocalActionId: 1,
  selectedArtifactPath: "",
  selectedApprovalId: "",
};

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
  if (["ok", "success", "available", "ready", "yes"].includes(value)) {
    return "success";
  }
  if (["blocked", "error", "fail", "failed", "no"].includes(value)) {
    return "error";
  }
  if (["pending", "loading", "running", "not_run"].includes(value)) {
    return "loading";
  }
  return "neutral";
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
      : "Safe local checks are available, but real desktop control is still not implemented.",
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
  setText("desktop-summary", summary.headline || "Desktop bridge status unavailable.");
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

function clearApprovalDetail(message) {
  uiState.selectedApprovalId = "";
  setText("approval-detail-id", "-");
  setText("approval-detail-status", "-");
  setText("approval-detail-risk", "-");
  setText("approval-detail-task-id", "-");
  setText("approval-detail-action-label", "-");
  setText("approval-detail-reason", "-");
  setText("approval-detail-scope", "-");
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
  setText("approval-detail-rollback", summary.rollbackPlan || "none");
  setText("approval-detail-admin", summary.requiresAdmin ? "yes" : "no");
  setText("approval-detail-updated-at", formatTimeStamp(summary.updatedAt));
  setText("approval-detail-summary", summary.headline || "Approval details loaded.");
  setValue("approval-decision-note", summary.humanNote && summary.humanNote !== "none" ? summary.humanNote : "");
  renderApprovalHistory(summary.decisionHistory || []);
  renderRaw("approval-detail-raw", payload);
  setApprovalDecisionButtonsDisabled(!["pending", "deferred"].includes(String(summary.status || "").toLowerCase()));
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
          </div>
          <p class="approval-description"><span>Description</span>${escapeHtml(item.shortDescription || item.detail || "No short description.")}</p>
          ${inspectButton}
        </article>
      `;
    })
    .join("");
}

function renderSupervisorStatus(payload) {
  const summary = payload.summary || {};
  const statusLabel = (summary.status || "unknown").replaceAll("_", " ");

  setText("supervisor-headline", summary.headline || "Supervisor status unavailable.");
  setText(
    "supervisor-quick-note",
    summary.pendingApprovalCount > 0
      ? "Risky or uncertain work is paused until the human approves it."
      : summary.blockedHumanNeededCount > 0
        ? "Some tasks are blocked on a human reply or judgment call."
        : "No open approvals right now. The supervisor is only tracking local state.",
  );
  setText("supervisor-status", statusLabel);
  setText("supervisor-pending-count", String(summary.pendingApprovalCount ?? 0));
  setText("supervisor-human-needed-count", String(summary.blockedHumanNeededCount ?? 0));
  setText("supervisor-waiting-count", String(summary.waitingCount ?? 0));
  setText("supervisor-summary", summary.headline || "Supervisor status unavailable.");

  renderApprovalCards(
    "pending-approvals-list",
    summary.pendingApprovals || [],
    "No pending approvals right now.",
    { inspectable: true },
  );
  renderApprovalCards(
    "human-needed-list",
    summary.humanNeededTasks || [],
    "No human-needed tasks right now.",
  );
  renderApprovalCards(
    "waiting-tasks-list",
    summary.waitingTasks || [],
    "No waiting tasks right now.",
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
      const previewButton = artifact.previewable
        ? `<button class="button-secondary artifact-action" type="button" data-artifact-action="preview" data-artifact-path="${escapeHtml(artifact.path)}">Preview</button>`
        : `<button class="button-secondary artifact-action" type="button" disabled>Preview unavailable</button>`;

      return `
        <article class="artifact-item">
          <div class="artifact-topline">
            <strong>${escapeHtml(artifact.name)}</strong>
            <span class="artifact-group">${escapeHtml(artifact.group)}</span>
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
  if (!container) {
    return;
  }

  const actions = [...uiState.localActions, ...uiState.serverActions].slice(0, 12);
  if (actions.length === 0) {
    container.innerHTML = "<p class=\"empty-state\">No recent actions yet.</p>";
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
  if (nextApprovalId) {
    await refreshApprovalDetail(nextApprovalId, { silent: true });
  } else {
    clearApprovalDetail("No approval item selected. Pending requests will appear here when they exist.");
  }
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
    await Promise.all([refreshSupervisorStatus(), refreshPendingApprovals(), refreshRecentActions()]);
    return result;
  } catch (error) {
    setResultPanel("approval-action-result", "error", "Approval decision failed.", error.message);
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

async function refreshConsole() {
  await Promise.all([
    refreshOperatorStatus(),
    refreshCapabilities(),
    refreshGithubUpdates(),
    refreshSupervisorStatus(),
    refreshPendingApprovals(),
    refreshArtifacts(),
    refreshDesktopBridgeStatus(),
    refreshRecentActions(),
  ]);
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
    await Promise.all([refreshArtifacts(), refreshRecentActions()]);
    return result;
  } catch (error) {
    setResultPanel(summaryId, "error", "Action failed.", error.message);
    renderRaw(rawId, { error: error.message });
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
    await Promise.all([refreshArtifacts(), refreshRecentActions()]);
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

document.getElementById("refresh-supervisor").addEventListener("click", async (event) => {
  await runRefresh(
    event.currentTarget,
    "Refresh supervisor status",
    "Refreshing...",
    () => Promise.all([refreshSupervisorStatus(), refreshPendingApprovals(), refreshRecentActions()]),
    (error) => {
      setText("supervisor-headline", "Supervisor refresh failed.");
      setText("supervisor-quick-note", error.message);
    },
  );
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
    () => Promise.all([refreshArtifacts(), refreshRecentActions()]),
    () => {
      clearArtifactPreview("Artifact refresh failed.");
    },
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

document.getElementById("run-browser-smoke").addEventListener("click", async (event) => {
  await runBrowserAction(
    "/api/browser/smoke",
    "browser-smoke-summary",
    "browser-smoke-raw",
    "Run headless browser demo",
    event.currentTarget,
  );
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

document.getElementById("approval-approve").addEventListener("click", async (event) => {
  await submitApprovalDecision("approve", event.currentTarget);
});

document.getElementById("approval-deny").addEventListener("click", async (event) => {
  await submitApprovalDecision("deny", event.currentTarget);
});

document.getElementById("approval-defer").addEventListener("click", async (event) => {
  await submitApprovalDecision("defer", event.currentTarget);
});

clearApprovalDetail("Select a pending approval to inspect it.");

refreshConsole().catch((error) => {
  setText("operator-headline", "Console load failed.");
  setText("operator-next-step", error.message);
});
