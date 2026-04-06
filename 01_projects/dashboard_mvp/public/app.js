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

function renderResult(targetId, payload) {
  const element = document.getElementById(targetId);
  element.textContent = JSON.stringify(payload, null, 2);
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
        <strong>${artifact.name}</strong>
        <span>${artifact.group}</span>
        <code>${artifact.path}</code>
        <span>${artifact.modifiedAt}</span>
      </article>
    `)
    .join("");
}

async function refreshCapabilities() {
  const payload = await requestJson("/api/capability-summary");
  renderResult("capability-output", payload);
}

async function refreshGithubStatus() {
  const payload = await requestJson("/api/github-status");
  renderResult("github-output", payload);
}

async function refreshArtifacts() {
  const payload = await requestJson("/api/artifacts");
  renderArtifacts(payload);
}

function attachForm(formId, outputId, endpoint) {
  const form = document.getElementById(formId);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(form).entries());

    try {
      renderResult(outputId, { status: "running" });
      const result = await requestJson(endpoint, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      renderResult(outputId, result);
      await refreshArtifacts();
    } catch (error) {
      renderResult(outputId, { error: error.message });
    }
  });
}

function attachButton(buttonId, outputId, endpoint, payload = {}) {
  const button = document.getElementById(buttonId);
  button.addEventListener("click", async () => {
    try {
      renderResult(outputId, { status: "running" });
      const result = await requestJson(endpoint, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      renderResult(outputId, result);
      await refreshArtifacts();
    } catch (error) {
      renderResult(outputId, { error: error.message });
    }
  });
}

document.getElementById("refresh-capabilities").addEventListener("click", async () => {
  try {
    await refreshCapabilities();
  } catch (error) {
    renderResult("capability-output", { error: error.message });
  }
});

document.getElementById("refresh-github").addEventListener("click", async () => {
  try {
    await refreshGithubStatus();
  } catch (error) {
    renderResult("github-output", { error: error.message });
  }
});

document.getElementById("refresh-artifacts").addEventListener("click", async () => {
  try {
    await refreshArtifacts();
  } catch (error) {
    renderArtifacts({
      artifacts: [{ name: "error", path: error.message, group: "system", modifiedAt: "" }],
    });
  }
});

attachForm("internship-form", "internship-output", "/api/scaffold/internship");
attachForm("showcase-form", "showcase-output", "/api/scaffold/showcase");
attachForm("portfolio-form", "portfolio-output", "/api/scaffold/portfolio");
attachButton("run-browser-smoke", "browser-smoke-output", "/api/browser/smoke");
attachButton("run-browser-visible", "browser-visible-output", "/api/browser/visible");

Promise.allSettled([refreshCapabilities(), refreshGithubStatus(), refreshArtifacts()]);
