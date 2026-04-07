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
  document.getElementById(id).textContent = value;
}

function renderRaw(id, payload) {
  document.getElementById(id).textContent = JSON.stringify(payload, null, 2);
}

function renderStatusList(id, items) {
  const element = document.getElementById(id);
  element.innerHTML = (items || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
}

function renderOperatorStatus(payload) {
  setText("operator-headline", payload.headline || "Operator mode status loaded.");
  setText("operator-next-step", payload.nextStep || "No next step reported.");
  renderStatusList("live-now-list", payload.liveNow);
  renderStatusList("scaffold-only-list", payload.scaffoldOnly);
  renderStatusList("not-implemented-list", payload.notImplementedYet);
}

function renderCapabilitySummary(payload) {
  const summary = payload.summary || {};
  setText("capability-headline", summary.headline || "Capability summary unavailable.");
  setText(
    "capability-counts",
    `${summary.availableCount ?? 0} available / ${summary.blockedCount ?? 0} blocked`,
  );
  setText("capability-available-count", String(summary.availableCount ?? 0));
  setText("capability-blocked-count", String(summary.blockedCount ?? 0));

  const capabilityList = document.getElementById("capability-list");
  const items = summary.capabilities || [];
  if (items.length === 0) {
    capabilityList.innerHTML = "<p>No capability data returned.</p>";
  } else {
    capabilityList.innerHTML = items
      .map((item) => `
        <article class="capability-item">
          <div class="capability-topline">
            <strong>${escapeHtml(item.capabilityId)}</strong>
            <span class="state-pill state-${escapeHtml(item.state)}">${escapeHtml(item.state)}</span>
          </div>
          <p>Requires: ${escapeHtml(item.requiredTools)}</p>
          <p>Block: ${escapeHtml(item.blockingIssue)}</p>
        </article>
      `)
      .join("");
  }

  renderRaw("capability-raw", payload);
}

function renderGithubUpdates(payload) {
  const summary = payload.summary || {};
  setText("github-headline", summary.headline || "GitHub updates unavailable.");
  setText(
    "github-quick-note",
    summary.remoteWritePossible
      ? "Remote smoke-test capability is currently available."
      : `Remote write blocked: ${summary.blockingIssue || "unknown reason"}`,
  );
  setText("github-branch", summary.branch || "-");
  setText("github-clean", summary.clean ? "clean" : "changes present");
  setText("github-remote-write", summary.remoteWritePossible ? "ready" : "blocked");
  setText("github-auth", summary.ghAuthenticated || "unknown");
  setText(
    "github-summary",
    `Origin: ${summary.originUrl || "none"} | staged ${summary.stagedChanges ?? 0}, unstaged ${summary.unstagedChanges ?? 0}, untracked ${summary.untrackedChanges ?? 0}`,
  );

  const commitsElement = document.getElementById("github-commits");
  const commits = summary.recentCommits || [];
  commitsElement.innerHTML = commits.length
    ? commits.map((item) => `<li>${escapeHtml(item)}</li>`).join("")
    : "<li>No commits reported.</li>";

  renderRaw("github-raw", payload);
}

function renderArtifacts(payload) {
  const container = document.getElementById("artifacts-output");
  const artifacts = payload.artifacts || [];
  if (artifacts.length === 0) {
    container.innerHTML = "<p>No recent artifacts found.</p>";
    return;
  }

  container.innerHTML = artifacts
    .map((artifact) => `
      <article class="artifact-item">
        <div class="artifact-topline">
          <strong>${escapeHtml(artifact.name)}</strong>
          <span>${escapeHtml(artifact.group)}</span>
        </div>
        <code>${escapeHtml(artifact.path)}</code>
        <span>${escapeHtml(artifact.modifiedAt)}</span>
      </article>
    `)
    .join("");
}

function renderRecentActions(payload) {
  const container = document.getElementById("recent-actions-output");
  const actions = payload.actions || [];
  if (actions.length === 0) {
    container.innerHTML = "<p>No recent actions yet.</p>";
    return;
  }

  container.innerHTML = actions
    .map((action) => `
      <article class="log-item">
        <div class="log-topline">
          <strong>${escapeHtml(action.label)}</strong>
          <span class="state-pill state-${escapeHtml(action.status)}">${escapeHtml(action.status)}</span>
        </div>
        <p>${escapeHtml(action.summary || "No summary.")}</p>
        <small>${escapeHtml(action.occurredAt || "")}</small>
      </article>
    `)
    .join("");
}

function renderActionSummary(targetId, payload) {
  const element = document.getElementById(targetId);
  const summary = payload.summary || {};
  const outputPath = summary.outputPath || summary.screenshotPath;
  element.innerHTML = `
    <div class="result-topline">
      <strong>${escapeHtml(summary.headline || "Action complete.")}</strong>
      <span class="state-pill state-${payload.ok ? "available" : "error"}">${payload.ok ? "ok" : "error"}</span>
    </div>
    ${outputPath ? `<p>${escapeHtml(outputPath)}</p>` : ""}
  `;
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

async function refreshArtifacts() {
  const payload = await requestJson("/api/artifacts");
  renderArtifacts(payload);
}

async function refreshRecentActions() {
  const payload = await requestJson("/api/recent-actions");
  renderRecentActions(payload);
}

async function refreshConsole() {
  await Promise.all([
    refreshOperatorStatus(),
    refreshCapabilities(),
    refreshGithubUpdates(),
    refreshArtifacts(),
    refreshRecentActions(),
  ]);
}

function serializeForm(formId) {
  return Object.fromEntries(new FormData(document.getElementById(formId)).entries());
}

async function runScaffold(formId, endpoint, summaryId, rawId) {
  const payload = serializeForm(formId);
  renderActionSummary(summaryId, {
    ok: true,
    summary: { headline: "Running action..." },
  });

  try {
    const result = await requestJson(endpoint, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    renderActionSummary(summaryId, result);
    renderRaw(rawId, result);
    await Promise.all([refreshArtifacts(), refreshRecentActions()]);
    return result;
  } catch (error) {
    renderActionSummary(summaryId, {
      ok: false,
      summary: { headline: error.message },
    });
    renderRaw(rawId, { error: error.message });
    await refreshRecentActions();
    return null;
  }
}

async function runBrowserAction(endpoint, summaryId, rawId, payload = {}) {
  renderActionSummary(summaryId, {
    ok: true,
    summary: { headline: "Running browser action..." },
  });

  try {
    const result = await requestJson(endpoint, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    renderActionSummary(summaryId, result);
    renderRaw(rawId, result);
    await Promise.all([refreshArtifacts(), refreshRecentActions()]);
    return result;
  } catch (error) {
    renderActionSummary(summaryId, {
      ok: false,
      summary: { headline: error.message },
    });
    renderRaw(rawId, { error: error.message });
    await refreshRecentActions();
    return null;
  }
}

document.getElementById("refresh-console").addEventListener("click", async () => {
  try {
    await refreshConsole();
  } catch (error) {
    setText("operator-headline", "Console refresh failed.");
    setText("operator-next-step", error.message);
  }
});

document.getElementById("refresh-github").addEventListener("click", async () => {
  try {
    await Promise.all([refreshGithubUpdates(), refreshRecentActions()]);
  } catch (error) {
    setText("github-headline", "GitHub refresh failed.");
    setText("github-quick-note", error.message);
  }
});

document.getElementById("refresh-artifacts").addEventListener("click", async () => {
  try {
    await Promise.all([refreshArtifacts(), refreshRecentActions()]);
  } catch (error) {
    renderArtifacts({
      artifacts: [{ name: "error", path: error.message, group: "system", modifiedAt: "" }],
    });
  }
});

document.getElementById("refresh-github-panel").addEventListener("click", async () => {
  try {
    await Promise.all([refreshGithubUpdates(), refreshRecentActions()]);
  } catch (error) {
    setText("github-headline", "GitHub panel refresh failed.");
    setText("github-quick-note", error.message);
  }
});

document.getElementById("refresh-capabilities-panel").addEventListener("click", async () => {
  try {
    await Promise.all([refreshCapabilities(), refreshRecentActions()]);
  } catch (error) {
    setText("capability-headline", "Capability refresh failed.");
    setText("capability-counts", error.message);
  }
});

document.getElementById("internship-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  await runScaffold("internship-form", "/api/scaffold/internship", "internship-summary", "internship-raw");
});

document.getElementById("showcase-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  await runScaffold("showcase-form", "/api/scaffold/showcase", "showcase-summary", "showcase-raw");
});

document.getElementById("portfolio-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  await runScaffold("portfolio-form", "/api/scaffold/portfolio", "portfolio-summary", "portfolio-raw");
});

document.getElementById("run-browser-smoke").addEventListener("click", async () => {
  await runBrowserAction("/api/browser/smoke", "browser-smoke-summary", "browser-smoke-raw");
});

document.getElementById("run-browser-visible").addEventListener("click", async () => {
  await runBrowserAction("/api/browser/visible", "browser-visible-summary", "browser-visible-raw");
});

document.getElementById("quick-internship").addEventListener("click", async () => {
  await runScaffold("internship-form", "/api/scaffold/internship", "internship-summary", "internship-raw");
});

document.getElementById("quick-showcase").addEventListener("click", async () => {
  await runScaffold("showcase-form", "/api/scaffold/showcase", "showcase-summary", "showcase-raw");
});

document.getElementById("quick-portfolio").addEventListener("click", async () => {
  await runScaffold("portfolio-form", "/api/scaffold/portfolio", "portfolio-summary", "portfolio-raw");
});

document.getElementById("quick-browser-smoke").addEventListener("click", async () => {
  await runBrowserAction("/api/browser/smoke", "browser-smoke-summary", "browser-smoke-raw");
});

document.getElementById("quick-browser-visible").addEventListener("click", async () => {
  await runBrowserAction("/api/browser/visible", "browser-visible-summary", "browser-visible-raw");
});

Promise.allSettled([refreshConsole()]);
