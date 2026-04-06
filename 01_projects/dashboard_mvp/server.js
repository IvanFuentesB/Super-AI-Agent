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

async function handleApiRequest(request, response, requestUrl) {
  if (request.method === "GET" && requestUrl.pathname === "/api/health") {
    sendJson(response, 200, {
      ok: true,
      service: "dashboard-mvp",
      port: dashboardPort,
    });
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/capability-summary") {
    const result = await runRuntimeCli(["capability-matrix"]);
    sendJson(response, result.ok ? 200 : 500, result);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/github-status") {
    const result = await runRuntimeCli(["github-status"]);
    sendJson(response, result.ok ? 200 : 500, result);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/artifacts") {
    sendJson(response, 200, {
      ok: true,
      artifacts: listRecentArtifacts(),
    });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/scaffold/internship") {
    const payload = await readJsonBody(request);
    requireFields(payload, ["targetRole", "company", "jobSource", "fitSummary"]);
    const result = await runRuntimeCli([
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
    sendJson(response, result.ok ? 200 : 500, {
      ...result,
      artifacts: listRecentArtifacts(),
    });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/scaffold/showcase") {
    const payload = await readJsonBody(request);
    requireFields(payload, ["projectName", "objective", "highlights"]);
    const result = await runRuntimeCli([
      "scaffold-showcase-case-study",
      "--project-name",
      String(payload.projectName),
      "--objective",
      String(payload.objective),
      "--highlights",
      String(payload.highlights),
    ]);
    sendJson(response, result.ok ? 200 : 500, {
      ...result,
      artifacts: listRecentArtifacts(),
    });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/scaffold/portfolio") {
    const payload = await readJsonBody(request);
    requireFields(payload, ["projectName", "summary", "stack"]);
    const result = await runRuntimeCli([
      "scaffold-portfolio-project-page",
      "--project-name",
      String(payload.projectName),
      "--summary",
      String(payload.summary),
      "--stack",
      String(payload.stack),
    ]);
    sendJson(response, result.ok ? 200 : 500, {
      ...result,
      artifacts: listRecentArtifacts(),
    });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/browser/smoke") {
    const result = await runBrowserDemo(false, false);
    sendJson(response, result.ok ? 200 : 500, {
      ...result,
      artifacts: listRecentArtifacts(),
    });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/browser/visible") {
    const payload = await readJsonBody(request);
    const result = await runBrowserDemo(true, Boolean(payload.checkOnly));
    sendJson(response, result.ok ? 200 : 500, {
      ...result,
      artifacts: listRecentArtifacts(),
    });
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
    sendJson(response, 500, {
      ok: false,
      error: error.message,
    });
  }
}

if (process.argv.includes("--check")) {
  const python = resolvePython();
  console.log("dashboard_check: ok");
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
