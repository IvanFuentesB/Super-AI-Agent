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
const dashboardPort = Number.parseInt(process.env.PORT || "3210", 10);
const maxRecentActions = 25;

let actionCounter = 0;
const recentActions = [];

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

function extractOutputPath(label, stdout) {
  const regex = new RegExp(`${label}:\\s*(.+)$`, "m");
  const match = stdout.match(regex);
  return match ? match[1].trim() : null;
}

function relativeRepoPath(absolutePath) {
  return path.relative(repoRoot, absolutePath).replace(/\\/g, "/");
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
  ];

  artifacts.sort((left, right) => right.modifiedAt.localeCompare(left.modifiedAt));
  return artifacts.slice(0, 25);
}

function buildOperatorStatus() {
  return {
    localOnly: true,
    headline: "Local operator console for safe, visible, reviewable actions.",
    liveNow: [
      "Capability summary and environment-aware status",
      "GitHub read status and remote-capability visibility",
      "Internship, showcase, and portfolio scaffold generation",
      "Browser smoke demo and visible local browser demo",
      "Recent artifacts and recent-action log",
    ],
    scaffoldOnly: [
      "GitHub remote write actions remain explicit and approval-gated",
      "Mail, Notion, and LinkedIn remain planning-only",
      "Personal ops packs are generated outputs, not live send or publish flows",
    ],
    notImplementedYet: [
      "Full browser executor loop",
      "Desktop or Windows app control",
      "Approval queue UI",
      "Live mail, Notion, and LinkedIn adapters",
    ],
    nextStep: "Use the dashboard as the visible local control surface, then choose the next executor path deliberately.",
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

  if (request.method === "GET" && requestUrl.pathname === "/api/artifacts") {
    const payload = {
      ok: true,
      localOnly: true,
      artifacts: listRecentArtifacts(),
    };
    sendJson(response, 200, payload);
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
      summary: {
        action: "browser_smoke",
        headline: raw.ok
          ? "Headless browser smoke demo completed."
          : "Headless browser smoke demo failed.",
        mode: browserResult.mode,
        screenshotPath: browserResult.screenshotPath,
      },
      raw,
      artifacts: listRecentArtifacts(),
      localOnly: true,
    };
    pushAction({
      actionType: "browser",
      label: "Ran browser smoke demo",
      status: raw.ok ? "success" : "error",
      summary: responsePayload.summary.headline,
      outputPath: browserResult.screenshotPath,
    });
    sendJson(response, raw.ok ? 200 : 500, responsePayload);
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/browser/visible") {
    const payload = await readJsonBody(request);
    const raw = await runBrowserDemo(true, Boolean(payload.checkOnly));
    const browserResult = parseBrowserResult(raw.stdout);
    const responsePayload = {
      ok: raw.ok,
      summary: {
        action: "browser_visible",
        headline: raw.ok
          ? (payload.checkOnly
              ? "Visible browser demo path checked."
              : "Visible browser demo completed.")
          : "Visible browser demo failed.",
        mode: browserResult.mode,
        screenshotPath: browserResult.screenshotPath,
        headless: browserResult.headless,
        checkOnly: Boolean(payload.checkOnly),
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
      status: raw.ok ? "success" : "error",
      summary: responsePayload.summary.headline,
      outputPath: browserResult.screenshotPath,
    });
    sendJson(response, raw.ok ? 200 : 500, responsePayload);
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
  console.log("mode: operator_console_v2");
  console.log("local_only: yes");
  console.log(`python: ${python ? python.displayName : "missing"}`);
  console.log(`browser_runner: ${process.execPath}`);
  process.exit(0);
}

const server = http.createServer((request, response) => {
  handleRequest(request, response);
});

server.listen(dashboardPort, "127.0.0.1", () => {
  console.log(`dashboard_url: http://127.0.0.1:${dashboardPort}`);
});
