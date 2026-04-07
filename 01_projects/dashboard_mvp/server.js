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
const dashboardPort = Number.parseInt(process.env.PORT || "3210", 10);
const maxRecentActions = 25;
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
    desktopControlImplemented: parsed.values.desktop_control_implemented === "yes",
    availableNow: parsed.listSections.available_now || [],
    missingNow: parsed.listSections.missing_now || [],
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
    adminRequired: labeled.admin || "unknown",
    detail: [
      labeled.action ? `action=${labeled.action}` : "",
      labeled.target ? `target=${labeled.target}` : "",
      labeled.description ? `description=${labeled.description}` : "",
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

  return {
    taskId: parts[0] || "",
    status: parts[1] || "unknown",
    detail: parts.slice(2).join(" | ") || "",
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
    requiresAdmin: parsed.values.requires_admin === "yes",
    reason: parsed.values.reason || "none",
    rollbackPlan: parsed.values.rollback_plan || "none",
    humanNote: parsed.values.human_note || "none",
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
  const waitingTasks = (parsed.listSections.waiting_tasks || [])
    .filter((item) => item !== "none")
    .map(parseTaskStatusLine);

  const status = parsed.values.status || "unknown";
  const pendingApprovalCount = Number.parseInt(parsed.values.pending_approval_count || "0", 10);
  const blockedHumanNeededCount = Number.parseInt(parsed.values.blocked_human_needed_count || "0", 10);
  const waitingCount = Number.parseInt(parsed.values.waiting_count || "0", 10);
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
    pendingApprovalCount,
    blockedHumanNeededCount,
    notificationMode: parsed.values.notification_mode || "dashboard",
    notificationTitle: parsed.values.notification_title || "Supervisor status",
    lastEvent: parsed.values.last_event || "none",
    updatedAt: parsed.values.updated_at || "",
    pendingApprovals,
    humanNeededTasks,
    waitingTasks,
    headline:
      pendingApprovalCount > 0
        ? `${pendingApprovalCount} approval request(s) need review.`
        : blockedHumanNeededCount > 0
          ? `${blockedHumanNeededCount} task(s) are blocked on the human.`
          : waitingCount > 0
            ? `${waitingCount} task(s) are waiting to resume later.`
            : queuedCount > 0 || runningCount > 0
              ? "Supervisor is tracking local work without open approvals."
              : "Supervisor is idle and ready.",
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
      "Artifact preview, open, and reveal from the dashboard",
      "Browser smoke demo and visible local browser demo",
      "Desktop bridge status and safe local desktop checks",
      "Supervisor status and approval inbox visibility",
      "Approval queue review with local approve, deny, and defer actions",
      "Recent artifacts and recent-action log",
    ],
    scaffoldOnly: [
      "GitHub remote write actions remain explicit and approval-gated",
      "Mail, Notion, and LinkedIn remain planning-only",
      "Personal ops packs are generated outputs, not live send or publish flows",
      "Desktop bridge is a foundation layer, not a desktop executor",
      "Notifications are local dashboard summaries only",
    ],
    notImplementedYet: [
      "Full browser executor loop",
      "Desktop or Windows app control",
      "App switching, clicking, typing, or clipboard orchestration",
      "Live mail, Notion, and LinkedIn adapters",
    ],
    nextStep: "Use the approval queue to resolve pending requests locally, then review the desktop bridge status before choosing the real executor path.",
  };
}

async function buildSupervisorResponse() {
  const raw = await runRuntimeCli(["supervisor-status"]);
  return {
    ok: raw.ok,
    summary: parseSupervisorStatus(raw.stdout),
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

  if (request.method === "GET" && requestUrl.pathname === "/api/supervisor/status") {
    const payload = await buildSupervisorResponse();
    pushAction({
      actionType: "supervisor",
      label: "Viewed supervisor status",
      status: payload.ok ? "success" : "error",
      summary: payload.summary.headline,
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
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
      ? headlineMap[decision]
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
    const payload = await buildDesktopBridgeResponse(false);
    pushAction({
      actionType: "desktop",
      label: "Ran desktop bridge check",
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
  console.log("mode: operator_console_v3");
  console.log("local_only: yes");
  console.log(`python: ${python ? python.displayName : "missing"}`);
  console.log(`browser_runner: ${process.execPath}`);
  console.log(`desktop_bridge_script: ${desktopCheckScriptPath}`);
  process.exit(0);
}

const server = http.createServer((request, response) => {
  handleRequest(request, response);
});

server.listen(dashboardPort, "127.0.0.1", () => {
  console.log(`dashboard_url: http://127.0.0.1:${dashboardPort}`);
});
