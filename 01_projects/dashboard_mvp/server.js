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
const desktopActionsScriptPath = path.join(desktopPlaygroundRoot, "desktop_bridge_actions.ps1");
const dashboardPort = Number.parseInt(process.env.PORT || "3210", 10);
const maxRecentActions = 25;
const runtimeDataDir = path.join(runtimeProjectRoot, "runtime_data");
const activeModeStateFile = path.join(runtimeDataDir, "active_mode_state.json");
const screenshotsDir = path.join(dashboardRoot, ".tmp-screenshots");
const captureFramesDir = path.join(screenshotsDir, "capture_frames");
const captureStateFile = path.join(runtimeDataDir, "screen_capture_state.json");
const captureStopFile = path.join(captureFramesDir, ".stop");
const captureSidecarScript = path.join(runtimeProjectRoot, "src", "super_ai_agent", "screen_capture_sidecar.py");

let captureInterval = null;
let captureFrameCount = 0;
let captureTickRunning = false;
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

function readActiveModeState() {
  const defaults = {
    active: false,
    mode: "idle",
    screen_view_enabled: false,
    audio_enabled: false,
    last_snapshot_path: null,
    last_event_utc: null,
    error: null,
    safety_note: "No hidden recording. Screen capture only when explicitly triggered by operator.",
  };
  try {
    if (!fs.existsSync(activeModeStateFile)) return defaults;
    return { ...defaults, ...JSON.parse(fs.readFileSync(activeModeStateFile, "utf8")) };
  } catch {
    return defaults;
  }
}

function writeActiveModeState(patch) {
  const current = readActiveModeState();
  const next = { ...current, ...patch, last_event_utc: new Date().toISOString() };
  if (!fs.existsSync(runtimeDataDir)) fs.mkdirSync(runtimeDataDir, { recursive: true });
  fs.writeFileSync(activeModeStateFile, JSON.stringify(next, null, 2));
  return next;
}

function readCaptureState() {
  const defaults = {
    capturing: false,
    capture_method: null,
    fps_target: 1,
    frame_count: 0,
    latest_frame_path: null,
    latest_frame_utc: null,
    error: null,
  };
  try {
    if (!fs.existsSync(captureStateFile)) return defaults;
    return { ...defaults, ...JSON.parse(fs.readFileSync(captureStateFile, "utf8")) };
  } catch {
    return defaults;
  }
}

function stopCaptureProcess() {
  if (captureInterval) {
    clearInterval(captureInterval);
    captureInterval = null;
  }
  captureTickRunning = false;
  const current = readCaptureState();
  const stopped = { ...current, capturing: false };
  try {
    if (!fs.existsSync(runtimeDataDir)) fs.mkdirSync(runtimeDataDir, { recursive: true });
    fs.writeFileSync(captureStateFile, JSON.stringify(stopped, null, 2));
  } catch { /* best effort */ }
}

async function captureOneTick(powerShell) {
  if (captureTickRunning) return;
  captureTickRunning = true;
  try {
    const latestPath = path.join(captureFramesDir, "latest.png");
    const framePath = path.join(captureFramesDir, `frame-${String(captureFrameCount).padStart(6, "0")}.png`);
    const latestEsc = latestPath.replace(/\\/g, "\\\\");
    const frameEsc = framePath.replace(/\\/g, "\\\\");
    const psScript = [
      "Add-Type -AssemblyName System.Windows.Forms",
      "Add-Type -AssemblyName System.Drawing",
      "$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds",
      "$bmp = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)",
      "$g = [System.Drawing.Graphics]::FromImage($bmp)",
      "$g.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)",
      "$g.Dispose()",
      `$bmp.Save("${latestEsc}")`,
      `$bmp.Save("${frameEsc}")`,
      "$bmp.Dispose()",
      "Write-Output 'ok'",
    ].join("; ");
    const result = await runCommand(
      powerShell.command,
      [...powerShell.baseArgs, "-ExecutionPolicy", "Bypass", "-Command", psScript],
      { cwd: repoRoot, timeoutMs: 10000 }
    );
    // If stop was called while we were capturing, do not overwrite the stopped state
    if (!captureInterval) return;
    if (result.ok && fs.existsSync(latestPath)) {
      captureFrameCount++;
      const nowUtc = new Date().toISOString();
      if (!fs.existsSync(runtimeDataDir)) fs.mkdirSync(runtimeDataDir, { recursive: true });
      fs.writeFileSync(captureStateFile, JSON.stringify({
        capturing: true,
        capture_method: "powershell-copyfromscreen-loop",
        fps_target: 1,
        frame_count: captureFrameCount,
        latest_frame_path: latestPath,
        latest_frame_utc: nowUtc,
        error: null,
      }, null, 2));
    } else {
      const cur = readCaptureState();
      if (!fs.existsSync(runtimeDataDir)) fs.mkdirSync(runtimeDataDir, { recursive: true });
      fs.writeFileSync(captureStateFile, JSON.stringify({
        ...cur,
        error: result.stderr || result.stdout || "PowerShell capture failed",
      }, null, 2));
    }
  } catch (err) {
    process.stderr.write(`[capture] tick error: ${err.message}\n`);
  } finally {
    captureTickRunning = false;
  }
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

async function runDesktopBridgeAction(action, options = {}) {
  const powerShell = resolvePowerShell();
  if (!powerShell) {
    return {
      ok: false,
      exitCode: 1,
      stdout: "",
      stderr: "PowerShell runtime not found for desktop bridge action.",
      command: "powershell -ExecutionPolicy Bypass -File desktop_bridge_actions.ps1",
      tool: "powershell",
    };
  }

  const args = [
    ...powerShell.baseArgs,
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    desktopActionsScriptPath,
    "-Action",
    String(action || ""),
  ];
  if (options.target) {
    args.push("-Target", String(options.target));
  }
  if (options.artifactPath) {
    args.push("-ArtifactPath", String(options.artifactPath));
  }
  if (options.textContent) {
    args.push("-TextContent", String(options.textContent));
  }

  const result = await runCommand(powerShell.command, args, {
    cwd: desktopPlaygroundRoot,
    env: options.env || process.env,
    timeoutMs: options.timeoutMs || 120000,
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
    failsafeHotkey: parsed.values.failsafe_hotkey || "Ctrl+8",
    desktopControlImplemented: parsed.values.desktop_control_implemented === "yes",
    terminalWindowCount: Number.parseInt(parsed.values.terminal_window_count || "0", 10),
    powerShellProcessCount: Number.parseInt(parsed.values.powershell_process_count || "0", 10),
    nodeProcessCount: Number.parseInt(parsed.values.node_process_count || "0", 10),
    pythonProcessCount: Number.parseInt(parsed.values.python_process_count || "0", 10),
    terminalWindowLimit: Number.parseInt(parsed.values.terminal_window_limit || "0", 10),
    terminalProcessLimit: Number.parseInt(parsed.values.terminal_process_limit || "0", 10),
    ollamaPresent: parsed.values.ollama_present === "yes",
    listWindowsOk: parsed.values.list_windows_ok === "yes",
    activeWindowOk: parsed.values.active_window_ok === "yes",
    openAllowedAppOk: parsed.values.open_allowed_app_ok === "yes",
    duplicateTerminalAvoidanceOk: parsed.values.duplicate_terminal_avoidance_ok === "yes",
    focusWindowOk: parsed.values.focus_window_ok === "yes",
    clipboardWriteOk: parsed.values.clipboard_write_ok === "yes",
    clipboardReadOk: parsed.values.clipboard_read_ok === "yes",
    pasteClipboardOk: parsed.values.paste_clipboard_ok === "yes",
    sendHotkeyOk: parsed.values.send_hotkey_ok === "yes",
    copySelectionOk: parsed.values.copy_selection_ok === "yes",
    waitSecondsOk: parsed.values.wait_seconds_ok === "yes",
    waitForWindowOk: parsed.values.wait_for_window_ok === "yes",
    moveMouseOk: parsed.values.move_mouse_ok === "yes",
    leftClickOk: parsed.values.left_click_ok === "yes",
    scrollMouseOk: parsed.values.scroll_mouse_ok === "yes",
    failsafeInterruptOk: parsed.values.failsafe_interrupt_ok === "yes",
    captureDesktopScreenshotOk: parsed.values.capture_desktop_screenshot_ok === "yes",
    unsupportedActionBlocked: parsed.values.unsupported_action_blocked === "yes",
    resourceGuardOk: parsed.values.resource_guard_ok === "yes",
    clipboardGuardOk: parsed.values.clipboard_guard_ok === "yes",
    availableNow: parsed.listSections.available_now || [],
    missingNow: parsed.listSections.missing_now || [],
  };
}

function parseBrainStatus(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  const notes = (parsed.listSections.brain_notes || [])
    .filter((item) => item !== "none");
  const installedModels = (parsed.listSections.brain_installed_models || [])
    .filter((item) => item !== "none");

  return {
    activeProvider: parsed.values.active_brain_provider || "unknown",
    activeModel: parsed.values.active_brain_model || "none",
    configSource: parsed.values.brain_config_source || "unknown",
    providerReady: parsed.values.brain_provider_ready === "yes",
    inferenceReady: parsed.values.brain_inference_ready === "yes",
    liveCallPath: parsed.values.brain_live_call_path || "none",
    ollamaBaseUrl: parsed.values.brain_ollama_base_url || "none",
    ollamaAvailable: parsed.values.brain_ollama_available === "yes",
    modelInstalled: parsed.values.brain_model_installed === "yes",
    currentTaskUsedModelInference: parsed.values.current_task_used_model_inference === "yes",
    currentTaskModelProvider: parsed.values.current_task_model_provider || "none",
    currentTaskModelName: parsed.values.current_task_model_name || "none",
    currentTaskModelCallStatus: parsed.values.current_task_model_call_status || "not_used",
    lastModelCallStatus: parsed.values.last_model_call_status || "never_called",
    lastModelCallAt: parsed.values.last_model_call_at || "none",
    lastModelCallSource: parsed.values.last_model_call_source || "none",
    lastModelCallTaskId: parsed.values.last_model_call_task_id || "none",
    lastModelCallError: parsed.values.last_model_call_error || "none",
    lastModelResponsePreview: parsed.values.last_model_response_preview || "none",
    runtimeBrainConfigFile: parsed.values.runtime_brain_config_file || "none",
    runtimeBrainStateFile: parsed.values.runtime_brain_state_file || "none",
    notes,
    installedModels,
    headline: `${parsed.values.active_brain_provider || "unknown"} | ${parsed.values.active_brain_model || "none"} | ${parsed.values.last_model_call_status || "never_called"}`,
  };
}

function parseAgentRoleStatus(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  const roles = (parsed.listSections.roles || [])
    .filter((item) => item !== "none");

  return {
    currentRoleId: parsed.values.current_specialist_role || "supervisor",
    currentRolePurpose: parsed.values.current_specialist_role_purpose || "none",
    currentRoleProvider: parsed.values.current_specialist_role_provider || "none",
    currentRoleSensitivity: parsed.values.current_specialist_role_sensitivity || "unknown",
    currentRoleReason: parsed.values.current_specialist_role_reason || "none",
    registryCount: Number.parseInt(parsed.values.specialist_role_registry_count || String(roles.length), 10),
    roles,
    headline: `${parsed.values.current_specialist_role || "supervisor"} | ${parsed.values.specialist_role_registry_count || roles.length} role(s)` ,
  };
}

function parseBrowserStatus(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  const notes = (parsed.listSections.browser_notes || [])
    .filter((item) => item !== "none");

  return {
    browserUseInstalled: parsed.values.browser_use_installed === "yes",
    browserUseVersion: parsed.values.browser_use_version || "none",
    browserUseReady: parsed.values.browser_use_ready === "yes",
    browserSessionSupport: parsed.values.browser_session_support || "not_available",
    browserTaskSupport: parsed.values.browser_task_support || "not_available",
    playwrightInstalled: parsed.values.playwright_installed === "yes",
    playwrightVersion: parsed.values.playwright_version || "none",
    playwrightCliAvailable: parsed.values.playwright_cli_available === "yes",
    playwrightBrowserBinariesInstalled: parsed.values.playwright_browser_binaries_installed === "yes",
    playwrightReady: parsed.values.playwright_ready === "yes",
    currentBrowserRole: parsed.values.current_browser_role || "none",
    currentBrowserAction: parsed.values.current_browser_action || "none",
    currentBrowserSessionId: parsed.values.current_browser_session_id || "none",
    lastBrowserStatus: parsed.values.last_browser_status || "not_used",
    runtimeBrowserStateFile: parsed.values.runtime_browser_state_file || "none",
    notes,
    headline: `${parsed.values.browser_use_installed || "no"} browser_use | ${parsed.values.playwright_ready || "no"} playwright_ready`,
  };
}

function parseMemoryStatus(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  const notes = (parsed.listSections.compact_memory_notes || [])
    .filter((item) => item !== "none");
  const missingFiles = (parsed.listSections.compact_memory_missing_files || [])
    .filter((item) => item !== "none");

  return {
    ready: parsed.values.compact_memory_ready === "yes",
    root: parsed.values.compact_memory_root || "none",
    obsidianMarkdownReady: parsed.values.compact_memory_obsidian_markdown_ready === "yes",
    fileCount: Number.parseInt(parsed.values.compact_memory_file_count || "0", 10),
    newestModifiedAt: parsed.values.compact_memory_newest_modified_at || "none",
    missingFiles,
    notes,
    headline: `${parsed.values.compact_memory_ready || "no"} compact_memory | files=${parsed.values.compact_memory_file_count || "0"}`,
  };
}

function parseRelayStatus(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  const notes = (parsed.listSections.relay_notes || [])
    .filter((item) => item !== "none");

  return {
    relayState: parsed.values.relay_state || "idle",
    currentStep: parsed.values.relay_current_step || "idle",
    sourceTargetAlias: parsed.values.relay_source_target_alias || "chatgpt",
    sourceTargetCandidateId: parsed.values.relay_source_target_candidate_id || "none",
    sourceTargetTitle: parsed.values.relay_source_target_title || "none",
    sourceTargetStatus: parsed.values.relay_source_target_status || "not_bound",
    destinationTargetAlias: parsed.values.relay_destination_target_alias || "codex",
    destinationTargetCandidateId: parsed.values.relay_destination_target_candidate_id || "none",
    destinationTargetTitle: parsed.values.relay_destination_target_title || "none",
    destinationTargetStatus: parsed.values.relay_destination_target_status || "not_bound",
    codexModePreset: parsed.values.relay_codex_mode_preset || "Implementing new feature",
    codexReasoningPreset: parsed.values.relay_codex_reasoning_preset || "Medium",
    presetApplicationStatus: parsed.values.relay_preset_application_status || "stored_only",
    codexExecutionStatus: parsed.values.relay_codex_execution_status || "unknown",
    nextUsageResetAt: parsed.values.relay_next_usage_reset_at || "none",
    resumeAfterUsageReset: parsed.values.relay_resume_after_usage_reset === "yes",
    waitingReason: parsed.values.relay_waiting_reason || "none",
    blockedReason: parsed.values.relay_blocked_reason || "none",
    lastPayloadPreview: parsed.values.relay_last_payload_preview || "none",
    lastResultPreview: parsed.values.relay_last_result_preview || "none",
    lastCompletionStatus: parsed.values.relay_last_completion_status || "none",
    lastTransitionAt: parsed.values.relay_last_transition_at || "none",
    lastUpdatedAt: parsed.values.relay_last_updated_at || "none",
    lastUsedTaskId: parsed.values.relay_last_used_task_id || "none",
    lastKnownDialogStatus: parsed.values.relay_last_known_dialog_status || "none",
    lastKnownDialogNote: parsed.values.relay_last_known_dialog_note || "none",
    runtimeRelayStateFile: parsed.values.runtime_relay_state_file || "none",
    notes,
    headline: `${parsed.values.relay_state || "idle"} | ${parsed.values.relay_current_step || "idle"} | ${parsed.values.relay_codex_execution_status || "unknown"}`,
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
    workspaceScope: labeled.workspace || "no_path_detected",
    workspacePolicy: labeled.policy || "allowed",
    adminRequired: labeled.admin || "unknown",
    detail: [
      labeled.action ? `action=${labeled.action}` : "",
      labeled.target ? `target=${labeled.target}` : "",
      labeled.description ? `description=${labeled.description}` : "",
      labeled.workspace ? `workspace=${labeled.workspace}` : "",
      labeled.policy ? `policy=${labeled.policy}` : "",
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
    taskId: parts[0] || "",
    status: parts[1] || "unknown",
    workspaceScope: labeled.workspace || "no_path_detected",
    workspacePolicy: labeled.policy || "allowed",
    approvalState: labeled.approval || "unknown",
    actionType: labeled.action || "",
    target: labeled.target || "",
    lastSummary: labeled.last || "none",
    nextAction: labeled.next || "Review the task state.",
    detail: labeled.detail || parts.slice(2).join(" | ") || "",
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

function parseTaskHistoryLine(line) {
  const parts = String(line)
    .split(" | ")
    .map((item) => item.trim())
    .filter(Boolean);

  return {
    eventType: parts[0] || "unknown",
    occurredAt: parts[1] || "",
    actor: parts[2]?.replace(/^actor=/, "") || "system",
    note: parts.slice(3).join(" | ").replace(/^note=/, "") || "none",
  };
}

function parseExecutionHistoryLine(line) {
  const parts = String(line)
    .split(" | ")
    .map((item) => item.trim())
    .filter(Boolean);

  const labeled = {};
  for (const part of parts.slice(1)) {
    const separatorIndex = part.indexOf("=");
    if (separatorIndex === -1) {
      continue;
    }
    const key = part.slice(0, separatorIndex).trim();
    const value = part.slice(separatorIndex + 1).trim();
    labeled[key] = value;
  }

  return {
    status: parts[0] || "unknown",
    startedAt: labeled.started || "",
    finishedAt: labeled.finished || "",
    target: labeled.target || "none",
    summary: labeled.summary || "none",
    artifactPath: labeled.artifact || "none",
    attempts: Number.parseInt(labeled.attempts || "1", 10),
    reason: labeled.reason || "none",
  };
}

function parseRecipeStepLine(line) {
  const parts = String(line)
    .split(" | ")
    .map((item) => item.trim())
    .filter(Boolean);

  const labeled = {};
  for (const part of parts.slice(1)) {
    const separatorIndex = part.indexOf("=");
    if (separatorIndex === -1) {
      continue;
    }
    const key = part.slice(0, separatorIndex).trim();
    const value = part.slice(separatorIndex + 1).trim();
    labeled[key] = value;
  }

  return {
    status: parts[0] || "unknown",
    step: Number.parseInt(labeled.step || "0", 10),
    actionType: labeled.action || "unknown",
    target: labeled.target || "none",
    bridgeTarget: labeled.bridge_target || "none",
    label: labeled.label || "recipe step",
    startedAt: labeled.started || "",
    finishedAt: labeled.finished || "",
    summary: labeled.summary || "none",
    artifactPath: labeled.artifact || "none",
    clipboardPreview: labeled.clipboard || "none",
    clipboardClassification: labeled.classification || "none",
    windowAlias: labeled.window || "none",
    windowCandidateId: labeled.candidate || "none",
    windowResolutionMode: labeled.resolution_mode || "none",
    coordinates: labeled.coordinates || "none",
    attempts: Number.parseInt(labeled.attempts || "0", 10),
    maxAttempts: Number.parseInt(labeled.max_attempts || "0", 10),
    required: labeled.required || "yes",
  };
}

function parseWindowCandidateLine(line) {
  const parts = String(line)
    .split(" | ")
    .map((item) => item.trim())
    .filter(Boolean);

  const labeled = {};
  for (const part of parts) {
    const separatorIndex = part.indexOf("=");
    if (separatorIndex === -1) {
      continue;
    }
    const key = part.slice(0, separatorIndex).trim();
    const value = part.slice(separatorIndex + 1).trim();
    labeled[key] = value;
  }

  return {
    aliases: (labeled.aliases || "").split(",").map((item) => item.trim()).filter(Boolean),
    title: labeled.title || "unknown",
    candidateId: labeled.candidate || "none",
    processId: Number.parseInt(labeled.pid || "0", 10),
    isActive: labeled.active === "yes",
    isFixture: labeled.fixture === "yes",
    matchScore: Number.parseInt(labeled.score || "0", 10),
    matchReason: labeled.reason || "none",
  };
}

function parseRecipeRunLine(line) {
  const parts = String(line)
    .split(" | ")
    .map((item) => item.trim())
    .filter(Boolean);

  const labeled = {};
  for (const part of parts.slice(1)) {
    const separatorIndex = part.indexOf("=");
    if (separatorIndex === -1) {
      continue;
    }
    const key = part.slice(0, separatorIndex).trim();
    const value = part.slice(separatorIndex + 1).trim();
    labeled[key] = value;
  }

  return {
    status: parts[0] || "unknown",
    startedAt: labeled.started || "",
    finishedAt: labeled.finished || "",
    summary: labeled.summary || "none",
  };
}

function parseTaskDetail(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  const history = (parsed.listSections.history || [])
    .filter((item) => item !== "none")
    .map(parseTaskHistoryLine);
  const executionHistory = (parsed.listSections.execution_history || [])
    .filter((item) => item !== "none")
    .map(parseExecutionHistoryLine);
  const recipeSteps = (parsed.listSections.recipe_steps || [])
    .filter((item) => item !== "none")
    .map(parseRecipeStepLine);
  const recipeLastRunSteps = (parsed.listSections.recipe_last_run_steps || [])
    .filter((item) => item !== "none")
    .map(parseRecipeStepLine);
  const recipeRunHistory = (parsed.listSections.recipe_run_history || [])
    .filter((item) => item !== "none")
    .map(parseRecipeRunLine);

  return {
    taskId: parsed.values.task_id || "",
    title: parsed.values.title || "Untitled task",
    description: parsed.values.description || "none",
    status: parsed.values.status || "unknown",
    riskLevel: parsed.values.risk_level || "unknown",
    approvalState: parsed.values.approval_state || "unknown",
    approvalRequestId: parsed.values.approval_request_id || "none",
    source: parsed.values.source || "manual",
    executorActionType: parsed.values.executor_action_type || "none",
    executorTarget: parsed.values.executor_target || "none",
    recipeName: parsed.values.recipe_name || "none",
    recipeLabel: parsed.values.recipe_label || "none",
    recipeStatus: parsed.values.recipe_status || "not_run",
    recipeSummary: parsed.values.recipe_summary || "none",
    recipeRunCount: Number.parseInt(parsed.values.recipe_run_count || "0", 10),
    recipeLastRunStartedAt: parsed.values.recipe_last_run_started_at || "",
    recipeLastRunFinishedAt: parsed.values.recipe_last_run_finished_at || "",
    recipeSourceWindow: parsed.values.recipe_source_window || "none",
    recipeTargetWindow: parsed.values.recipe_target_window || "none",
    recipeSourceWindowCandidateId: parsed.values.recipe_source_window_candidate_id || "none",
    recipeTargetWindowCandidateId: parsed.values.recipe_target_window_candidate_id || "none",
    recipeClipboardMode: parsed.values.recipe_clipboard_mode || "none",
    handoffSourceSelectionMode: parsed.values.handoff_source_selection_mode || "none",
    handoffTargetSelectionMode: parsed.values.handoff_target_selection_mode || "none",
    handoffPayloadClassification: parsed.values.handoff_payload_classification || "none",
    handoffPayloadPreview: parsed.values.handoff_payload_preview || "none",
    handoffPayloadReason: parsed.values.handoff_payload_reason || "none",
    handoffPasteAllowed: parsed.values.handoff_paste_allowed || "none",
    handoffSendBehavior: parsed.values.handoff_send_behavior || "none",
    handoffSendAllowed: parsed.values.handoff_send_allowed || "none",
    handoffFallbackDenied: parsed.values.handoff_fallback_denied || "none",
    handoffTargetResolutionStatus: parsed.values.handoff_target_resolution_status || "none",
    handoffManualTargetResolution: parsed.values.handoff_manual_target_resolution || "none",
    handoffSourceMatch: parsed.values.handoff_source_match || "none",
    handoffTargetMatch: parsed.values.handoff_target_match || "none",
    handoffStopReason: parsed.values.handoff_stop_reason || "none",
    handoffBlockedPayloadRepeats: Number.parseInt(parsed.values.handoff_blocked_payload_repeats || "0", 10),
    workspaceScope: parsed.values.workspace_scope || "no_path_detected",
    workspacePolicy: parsed.values.workspace_policy || "allowed",
    workspaceReason: parsed.values.workspace_reason || "none",
    allowedWorkspaceRoot: parsed.values.allowed_workspace_root || "unknown",
    waitingFor: parsed.values.waiting_for || "none",
    blockedReason: parsed.values.blocked_reason || "none",
    requiresHuman: parsed.values.requires_human === "yes",
    adminRequired: parsed.values.admin_required === "yes",
    lastNote: parsed.values.last_note || "none",
    createdAt: parsed.values.created_at || "",
    updatedAt: parsed.values.updated_at || "",
    nextAction: parsed.values.next_action || "Review the task state.",
    executionCount: Number.parseInt(parsed.values.execution_count || "0", 10),
    lastExecutionStatus: parsed.values.last_execution_status || "not_run",
    lastExecutionSummary: parsed.values.last_execution_summary || "none",
    lastArtifactPath: parsed.values.last_artifact_path || "none",
    lastAttemptCount: Number.parseInt(parsed.values.last_attempt_count || "0", 10),
    lastFailureReason: parsed.values.last_failure_reason || "none",
    lastInterruptionReason: parsed.values.last_interruption_reason || "none",
    lastResourceGuardReason: parsed.values.last_resource_guard_reason || "none",
    desktopCurrentAction: parsed.values.desktop_current_action || "none",
    desktopCurrentTarget: parsed.values.desktop_current_target || "none",
    desktopCurrentTypingEnabled: parsed.values.desktop_current_typing_enabled || "no",
    desktopLastAction: parsed.values.desktop_last_action || "none",
    desktopLastTarget: parsed.values.desktop_last_target || "none",
    desktopLastTypingEnabled: parsed.values.desktop_last_typing_enabled || "no",
    desktopLastActionStatus: parsed.values.desktop_last_action_status || "not_run",
    desktopVisualCueStatus: parsed.values.desktop_visual_cue_status || "not_reported",
    desktopVisualCueAction: parsed.values.desktop_visual_cue_action || "none",
    desktopVisualCueTarget: parsed.values.desktop_visual_cue_target || "none",
    desktopLastTextPreview: parsed.values.desktop_last_text_preview || "none",
    retryLimit: Number.parseInt(parsed.values.retry_limit || "0", 10),
    targetPaths: (parsed.listSections.target_paths || []).filter((item) => item !== "none"),
    recipeSteps,
    recipeLastRunSteps,
    recipeRunHistory,
    executionHistory,
    history,
    headline: `${parsed.values.title || "Task"} (${parsed.values.status || "unknown"})`,
  };
}

function parseExecutorTaskLine(line) {
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
    taskId: parts[0] || "",
    status: parts[1] || "unknown",
    actionType: labeled.action || "unknown",
    target: labeled.target || "none",
    taskType: labeled.type || "repo",
    title: labeled.title || "Executor task",
    updatedAt: labeled.updated || "",
    recipeName: labeled.recipe || "none",
    approvalState: labeled.approval || "unknown",
    workspaceScope: labeled.workspace || "no_path_detected",
    workspacePolicy: labeled.policy || "allowed",
    lastSummary: labeled.last || "not_run",
    sourceWindow: labeled.source_window || "none",
    targetWindow: labeled.target_window || "none",
    payloadClassification: labeled.classification || "none",
    sendBehavior: labeled.send_behavior || "none",
    desktopAction: labeled.desktop_action || "none",
    desktopTarget: labeled.desktop_target || "none",
    typingEnabled: labeled.typing_enabled || "no",
    desktopStatus: labeled.desktop_status || "not_run",
    cueStatus: labeled.cue_status || "not_reported",
    detail: [
      labeled.action ? `action=${labeled.action}` : "",
      labeled.target ? `target=${labeled.target}` : "",
      labeled.approval ? `approval=${labeled.approval}` : "",
      labeled.workspace ? `workspace=${labeled.workspace}` : "",
      labeled.policy ? `policy=${labeled.policy}` : "",
      labeled.last ? `last=${labeled.last}` : "",
      labeled.source_window ? `source=${labeled.source_window}` : "",
      labeled.target_window ? `target_window=${labeled.target_window}` : "",
      labeled.classification ? `classification=${labeled.classification}` : "",
      labeled.desktop_action ? `desktop_action=${labeled.desktop_action}` : "",
      labeled.desktop_target ? `desktop_target=${labeled.desktop_target}` : "",
      labeled.typing_enabled ? `typing_enabled=${labeled.typing_enabled}` : "",
      labeled.desktop_status ? `desktop_status=${labeled.desktop_status}` : "",
      labeled.cue_status ? `cue_status=${labeled.cue_status}` : "",
    ].filter(Boolean).join(" | "),
  };
}

function parseExecutorTaskList(stdout) {
  const parsed = parseKeyValueBlock(stdout);
  const tasks = (parsed.listSections.tasks || [])
    .filter((item) => item !== "none")
    .map(parseExecutorTaskLine);
  const count = Number.parseInt(parsed.values.count || String(tasks.length), 10);

  return {
    count,
    tasks,
    headline: count > 0 ? `${count} executor task(s) available.` : "No executor tasks queued yet.",
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
    workspaceScope: parsed.values.workspace_scope || "no_path_detected",
    workspacePolicy: parsed.values.workspace_policy || "allowed",
    workspaceReason: parsed.values.workspace_reason || "none",
    allowedWorkspaceRoot: parsed.values.allowed_workspace_root || "unknown",
    requiresAdmin: parsed.values.requires_admin === "yes",
    reason: parsed.values.reason || "none",
    rollbackPlan: parsed.values.rollback_plan || "none",
    humanNote: parsed.values.human_note || "none",
    targetPaths: (parsed.listSections.target_paths || []).filter((item) => item !== "none"),
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
  const interruptedTasks = (parsed.listSections.interrupted_tasks || [])
    .filter((item) => item !== "none")
    .map(parseTaskStatusLine);
  const waitingTasks = (parsed.listSections.waiting_tasks || [])
    .filter((item) => item !== "none")
    .map(parseTaskStatusLine);
  const readyToResumeTasks = (parsed.listSections.ready_to_resume_tasks || [])
    .filter((item) => item !== "none")
    .map(parseTaskStatusLine);
  const resourceGuardEvents = (parsed.listSections.resource_guard_events || [])
    .filter((item) => item !== "none");

  const status = parsed.values.status || "unknown";
  const pendingApprovalCount = Number.parseInt(parsed.values.pending_approval_count || "0", 10);
  const blockedHumanNeededCount = Number.parseInt(parsed.values.blocked_human_needed_count || "0", 10);
  const interruptedCount = Number.parseInt(parsed.values.interrupted_count || "0", 10);
  const waitingCount = Number.parseInt(parsed.values.waiting_count || "0", 10);
  const readyToResumeCount = Number.parseInt(parsed.values.ready_to_resume_count || "0", 10);
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
    readyToResumeCount,
    pendingApprovalCount,
    blockedHumanNeededCount,
    interruptedCount,
    ghotiState: parsed.values.ghoti_state || "idle",
    ghotiReason: parsed.values.ghoti_reason || "none",
    operatorNextStep: parsed.values.operator_next_step || "Review the local operator state.",
    resourceGuardEventCount: Number.parseInt(parsed.values.resource_guard_event_count || "0", 10),
    notificationMode: parsed.values.notification_mode || "dashboard",
    notificationTitle: parsed.values.notification_title || "Supervisor status",
    lastEvent: parsed.values.last_event || "none",
    updatedAt: parsed.values.updated_at || "",
    allowedWorkspaceRoot: parsed.values.allowed_workspace_root || "unknown",
    resourceGuardEvents,
    pendingApprovals,
    humanNeededTasks,
    interruptedTasks,
    waitingTasks,
    readyToResumeTasks,
    headline:
      pendingApprovalCount > 0
        ? `${pendingApprovalCount} approval request(s) need review.`
        : blockedHumanNeededCount > 0
          ? `${blockedHumanNeededCount} task(s) are blocked on the human.`
        : interruptedCount > 0
          ? `${interruptedCount} task(s) were interrupted by the local failsafe.`
        : waitingCount > 0
          ? `${waitingCount} task(s) are waiting to resume later.`
          : readyToResumeCount > 0
            ? `${readyToResumeCount} task(s) are ready to re-queue.`
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
    path.join(repoRoot, "05_logs", "tmp", "desktop"),
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
    ...listDirectoryArtifacts(
      path.join(repoRoot, "05_logs", "tmp", "desktop"),
      "desktop",
    ),
  ];

  artifacts.sort((left, right) => right.modifiedAt.localeCompare(left.modifiedAt));
  return artifacts.slice(0, 25);
}

function buildOperatorStatus() {
  return {
    localOnly: true,
    headline: "Local operator console for safe, visible, reviewable actions.",
    dashboardUrl: `http://127.0.0.1:${dashboardPort}`,
    emergencyStopHotkey: "Ctrl+8",
    controlCenterDoc: relativeRepoPath(path.join(repoRoot, "04_docs", "ghoti_control_center.md")),
    cliCommands: [
      "python -m super_ai_agent.cli ghoti-help",
      "python -m super_ai_agent.cli ghoti-status",
      "python -m super_ai_agent.cli ghoti-hotkeys",
      "python -m super_ai_agent.cli ghoti-recent",
      "python -m super_ai_agent.cli list-agent-roles",
      "python -m super_ai_agent.cli browser-status",
      "python -m super_ai_agent.cli memory-status",
    ],
    liveNow: [
      "Capability summary and environment-aware status",
      "GitHub read status and remote-capability visibility",
      "Internship, showcase, and portfolio scaffold generation",
      "Allowlisted repo-local executor tasks for safe checker, file, and git actions",
      "Allowlisted desktop bridge tasks for listing windows, checking the active window, focusing allowed windows, opening allowed local apps, capturing repo-local screenshots, clipboard reads and writes, waits, hotkeys, and narrow mouse actions",
      "Narrow operator recipes built from the existing desktop hand primitives",
      "Artifact preview, open, and reveal from the dashboard",
      "Browser smoke demo and visible local browser demo",
      "Desktop bridge status and safe local desktop checks",
      "Supervisor status and approval inbox visibility",
      "Approval queue review with local approve, deny, and defer actions",
      "Manual task review, resume, re-queue, and failsafe interruption visibility",
      "CLI Ghoti help, status, hotkey, and recent-work summaries",
      "Specialist-agent registry with role/provider/approval sensitivity truth",
      "Browser Use and Playwright readiness visibility",
      "Compact markdown memory scaffold visibility",
      "Safe real-window Codex-to-ChatGPT handoff with explicit target verification",
      "Recent artifacts and recent-action log",
    ],
    scaffoldOnly: [
      "GitHub remote write actions remain explicit and approval-gated",
      "Mail, Notion, and LinkedIn remain planning-only",
      "Personal ops packs are generated outputs, not live send or publish flows",
      "Desktop bridge actions and recipes are still narrow, allowlisted, and operator-triggered",
      "Business outreach remains draft-and-review scaffolding only",
      "The handoff workflow remains paste-only by default and still stops for manual target resolution when real window matching is not confident",
      "Notifications are local dashboard summaries only",
    ],
    notImplementedYet: [
      "Full browser executor loop",
      "Arbitrary desktop or Windows app control",
      "Freeform typing, drag-and-drop, or unrestricted mouse automation",
      "Runtime-stored durable Codex or ChatGPT target profiles beyond browser-local remembered candidate picks",
      "A live Browser Use executor path or autonomous browser sessions",
      "Live outreach send, pricing, or negotiation actions",
      "Live mail, Notion, and LinkedIn adapters",
    ],
    nextStep: "Use the Ghoti control center or the new ghoti-* CLI commands to spot the next actionable task, review approvals, and inspect artifacts before queueing another narrow local action.",
  };
}

async function buildGhotiControlCenterResponse(filters = {}) {
  const [capabilityPayload, supervisorPayload, executorPayload, brainPayload, rolePayload, browserPayload, memoryPayload, relayPayload] = await Promise.all([
    buildCapabilityResponse(),
    buildSupervisorResponse(),
    buildExecutorTasksResponse(),
    buildBrainStatusResponse(),
    buildAgentRoleResponse(),
    buildBrowserStatusResponse(),
    buildMemoryStatusResponse(),
    buildRelayStatusResponse(),
  ]);

  const operator = buildOperatorStatus();
  const supervisor = supervisorPayload.summary || {};
  const executorSummary = executorPayload.summary || {};
  const capabilitySummary = capabilityPayload.summary || {};
  const brainSummary = brainPayload.summary || {};
  const roleSummary = rolePayload.summary || {};
  const browserSummary = browserPayload.summary || {};
  const memorySummary = memoryPayload.summary || {};
  const relaySummary = relayPayload.summary || {};
  const tasks = executorSummary.tasks || [];
  const filteredTasks = filterGhotiTasks(tasks, filters);
  const sortedTasks = sortGhotiTasks(tasks).map(decorateGhotiTask);
  const currentTask = sortedTasks.find((item) => item.taskId === supervisor.activeTaskId)
    || sortedTasks.find((item) => String(item.status || "").toLowerCase() === "running")
    || null;
  const watchdog = buildGhotiWatchdogSummary(supervisor, sortedTasks, currentTask);
  const recentFailures = sortedTasks
    .filter((item) => ghotiFailureStatuses.has(String(item.status || "").toLowerCase()))
    .slice(0, 5);
  const artifacts = listRecentArtifacts();
  const availableCapabilities = (capabilitySummary.capabilities || [])
    .filter((item) => String(item.state || "").toLowerCase() === "available")
    .map((item) => item.capabilityId)
    .slice(0, 6);
  const nextSteps = [
    supervisor.operatorNextStep || operator.nextStep,
    "Use Ctrl+8 if a desktop action or recipe needs to stop immediately.",
    supervisor.pendingApprovalCount > 0
      ? "Review pending approvals before trying to run blocked work."
      : "",
    supervisor.blockedHumanNeededCount > 0
      ? "Inspect blocked human-needed tasks and decide whether to review, resume, or re-queue them."
      : "",
    `Open ${operator.controlCenterDoc} for the compact dashboard and CLI usage path.`,
  ].filter(Boolean);

  return {
    ok: capabilityPayload.ok && supervisorPayload.ok && executorPayload.ok && brainPayload.ok && rolePayload.ok && browserPayload.ok && memoryPayload.ok && relayPayload.ok,
    summary: {
      headline: `${supervisor.ghotiState || "idle"} | ${supervisor.headline || "Ghoti control center ready."}`,
      ghotiState: supervisor.ghotiState || "idle",
      ghotiReason: supervisor.ghotiReason || "none",
      operatorNextStep: supervisor.operatorNextStep || operator.nextStep,
      emergencyStopHotkey: operator.emergencyStopHotkey,
      currentTask: currentTask
        ? {
            taskId: currentTask.taskId,
            headline: currentTask.headline,
            status: currentTask.status,
            taskType: currentTask.taskType,
            taskTypeLabel: currentTask.taskTypeLabel,
            detail: currentTask.detail,
            nextAction: currentTask.nextAction || "Inspect the task detail.",
            usedModelInference: brainSummary.currentTaskUsedModelInference === true,
            modelProvider: brainSummary.currentTaskModelProvider || "none",
            modelName: brainSummary.currentTaskModelName || "none",
            modelCallStatus: brainSummary.currentTaskModelCallStatus || "not_used",
            desktopAction: currentTask.desktopAction || "none",
            desktopTarget: currentTask.desktopTarget || "none",
            typingEnabled: currentTask.typingEnabled || "no",
            desktopStatus: currentTask.desktopStatus || "not_run",
            cueStatus: currentTask.cueStatus || "not_reported",
            specialistRole: roleSummary.currentRoleId || "supervisor",
          }
        : null,
      desktopActionTruth: currentTask
        ? {
            currentAction: currentTask.desktopAction || "none",
            currentTarget: currentTask.desktopTarget || "none",
            typingEnabled: currentTask.typingEnabled || "no",
            lastStatus: currentTask.desktopStatus || "not_run",
            cueStatus: currentTask.cueStatus || "not_reported",
            specialistRole: roleSummary.currentRoleId || "supervisor",
          }
        : {
            currentAction: "none",
            currentTarget: "none",
            typingEnabled: "no",
            lastStatus: "not_run",
            cueStatus: "not_reported",
            specialistRole: roleSummary.currentRoleId || "supervisor",
          },
      brain: brainSummary,
      specialistRole: roleSummary,
      browser: browserSummary,
      memory: memorySummary,
      relay: relaySummary,
      pendingApprovalCount: Number(supervisor.pendingApprovalCount || 0),
      blockedTaskCount: Number(supervisor.blockedHumanNeededCount || 0),
      interruptedCount: Number(supervisor.interruptedCount || 0),
      waitingCount: Number(supervisor.waitingCount || 0),
      readyToResumeCount: Number(supervisor.readyToResumeCount || 0),
      recentActionableCount: filteredTasks.filteredCount,
      recentFailureCount: recentFailures.length,
      recentArtifactCount: artifacts.length,
      overlayTarget: watchdog.overlayTarget,
      watchdog,
      recentActionableTasks: filteredTasks.items,
      recentFailures,
      whatGhotiCanDoNow: availableCapabilities.length > 0 ? availableCapabilities : operator.liveNow.slice(0, 6),
      whatOperatorShouldDoNext: nextSteps,
      filters: {
        visibility: filteredTasks.visibility,
        taskType: filteredTasks.taskType,
        taskStatus: filteredTasks.taskStatus,
        activeOnly: filteredTasks.activeOnly,
        limit: filteredTasks.limit,
      },
      dashboardUrl: operator.dashboardUrl,
      controlCenterDoc: operator.controlCenterDoc,
      cliCommands: operator.cliCommands,
      hideCompletedByDefault: filteredTasks.visibility !== "all",
      noDeletionPolicy: "No task deletion without explicit approval. Prefer archive, filter, and history visibility instead.",
      availableCapabilitiesCount: Number(capabilitySummary.availableCount || 0),
    },
    raw: {
      capability: capabilityPayload.raw,
      brain: brainPayload.raw,
      role: rolePayload.raw,
      browser: browserPayload.raw,
      memory: memoryPayload.raw,
      relay: relayPayload.raw,
      supervisor: supervisorPayload.raw,
      executor: executorPayload.raw,
    },
    localOnly: true,
  };
}

const ghotiActionableStatuses = new Set([
  "queued",
  "running",
  "waiting",
  "pending_approval",
  "blocked_human_needed",
  "interrupted",
  "ready_to_resume",
  "failed",
]);

const ghotiActiveStatuses = new Set([
  "queued",
  "running",
  "waiting",
  "pending_approval",
  "blocked_human_needed",
  "interrupted",
  "ready_to_resume",
]);

const ghotiFailureStatuses = new Set([
  "failed",
  "blocked_human_needed",
  "interrupted",
]);

const ghotiDesktopActionTypes = new Set([
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

function parseBooleanQuery(value, fallback = false) {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  return ["1", "true", "yes", "on"].includes(String(value).toLowerCase());
}

function parsePositiveIntQuery(value, fallback) {
  const parsed = Number.parseInt(String(value || ""), 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function isDesktopExecutorAction(actionType) {
  return ghotiDesktopActionTypes.has(String(actionType || "").toLowerCase());
}

function normalizeGhotiText(value) {
  return String(value || "").trim().toLowerCase();
}

function parseGhotiDate(value) {
  const normalized = String(value || "").trim();
  if (!normalized) {
    return null;
  }

  const parsed = new Date(normalized);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function getGhotiTaskAgeMinutes(task) {
  const timestamp = task?.updatedAt || task?.createdAt || "";
  const parsed = parseGhotiDate(timestamp);
  if (!parsed) {
    return null;
  }

  return Math.max(0, Math.round((Date.now() - parsed.getTime()) / 60000));
}

function taskLooksLikeWrongActiveWindowBlock(task) {
  const haystack = [
    task?.detail,
    task?.lastSummary,
    task?.blockedReason,
    task?.target,
  ].map((item) => String(item || "").toLowerCase()).join(" ");

  return (
    haystack.includes("wrong active window")
    || haystack.includes("active window mismatch")
    || haystack.includes("terminal stayed foreground")
    || haystack.includes("manual target resolution is required")
    || haystack.includes("powershell")
  );
}

function isLikelyStalledGhotiTask(task) {
  const status = normalizeGhotiText(task?.status);
  if (!["queued", "running", "waiting"].includes(status)) {
    return false;
  }

  const ageMinutes = getGhotiTaskAgeMinutes(task);
  if (!Number.isFinite(ageMinutes)) {
    return false;
  }

  const thresholdMinutes = status === "running" ? 15 : 20;
  return ageMinutes >= thresholdMinutes;
}

function buildGhotiOverlayTarget(task) {
  if (!task) {
    return {
      kind: "none",
      label: "No visible target",
      detail: "Queue or inspect one narrow task to show Ghoti's next local target.",
    };
  }

  const actionType = normalizeGhotiText(task.actionType);
  const taskType = task.taskType || classifyGhotiTaskType(task);
  const target = String(task.target || "").trim();
  const targetDetail = target && target !== "none"
    ? target
    : task.detail || task.headline || "No specific target recorded yet.";

  if (taskType === "handoff") {
    const sourceWindow = String(task.sourceWindow || "codex").trim() || "codex";
    const targetWindow = String(task.targetWindow || "chatgpt").trim() || "chatgpt";
    const detail = target && target !== "none"
      ? `${sourceWindow} -> ${targetWindow} | ${target}`
      : `${sourceWindow} -> ${targetWindow}`;
    return {
      kind: "handoff",
      label: "Handoff target",
      detail,
    };
  }

  if (["move_mouse", "left_click", "double_click", "right_click", "scroll_mouse"].includes(actionType)) {
    return {
      kind: "pointer",
      label: "Pointer target",
      detail: targetDetail,
    };
  }

  if (["focus_window", "open_allowed_app", "wait_for_window", "get_active_window"].includes(actionType)) {
    return {
      kind: "window",
      label: "Window target",
      detail: targetDetail,
    };
  }

  if (["paste_clipboard", "copy_selection", "set_clipboard_text", "send_hotkey", "get_clipboard_text", "type_text"].includes(actionType)) {
    return {
      kind: "input",
      label: "Input target",
      detail: targetDetail,
    };
  }

  return {
    kind: taskType || "task",
    label: `${task.taskTypeLabel || "Current task"} target`,
    detail: targetDetail,
  };
}

function buildGhotiWatchdogSummary(supervisor, sortedTasks, currentTask) {
  const recentFailures = sortedTasks
    .filter((item) => ghotiFailureStatuses.has(normalizeGhotiText(item.status)))
    .slice(0, 6);
  const wrongWindowBlocks = recentFailures.filter(taskLooksLikeWrongActiveWindowBlock);
  const stalledTasks = sortedTasks.filter(isLikelyStalledGhotiTask).slice(0, 4);
  const didNotCompleteTasks = recentFailures.filter((item) => normalizeGhotiText(item.status) !== "completed");
  const waitingCount = Number(supervisor.waitingCount || 0) + Number(supervisor.readyToResumeCount || 0);
  const pendingApprovalCount = Number(supervisor.pendingApprovalCount || 0);
  const blockedCount = Number(supervisor.blockedHumanNeededCount || 0);
  const interruptedCount = Number(supervisor.interruptedCount || 0);
  const runningCount = Number(supervisor.runningCount || 0);

  let status = "idle";
  let headline = "Ghoti is visible and waiting for the next narrow local action.";

  if (pendingApprovalCount > 0) {
    status = "approval_needed";
    headline = `${pendingApprovalCount} approval request(s) need review before more guarded work can proceed.`;
  } else if (wrongWindowBlocks.length > 0) {
    status = "blocked";
    headline = `Blocked before input on ${wrongWindowBlocks.length} wrong-window handoff attempt(s).`;
  } else if (blockedCount > 0 || didNotCompleteTasks.length > 0) {
    status = "blocked";
    headline = blockedCount > 0
      ? `${blockedCount} task(s) are blocked and need manual intervention.`
      : `${didNotCompleteTasks.length} recent task(s) did not complete cleanly.`;
  } else if (interruptedCount > 0) {
    status = "interrupted";
    headline = `${interruptedCount} task(s) were interrupted and must be reviewed before re-queue.`;
  } else if (runningCount > 0 || normalizeGhotiText(currentTask?.status) === "running") {
    status = "active";
    headline = currentTask
      ? `${currentTask.taskTypeLabel || "Task"} ${currentTask.taskId || ""} is active.`.trim()
      : "Ghoti is actively running a local task.";
  } else if (waitingCount > 0 || stalledTasks.length > 0) {
    status = "waiting";
    headline = waitingCount > 0
      ? `${waitingCount} task(s) are waiting or ready to resume.`
      : `${stalledTasks.length} task(s) look stalled and need operator attention.`;
  }

  const alerts = [
    wrongWindowBlocks.length > 0
      ? `${wrongWindowBlocks.length} recent handoff block(s) stopped before input because the active window did not match the intended Codex or ChatGPT destination.`
      : "",
    stalledTasks.length > 0
      ? `${stalledTasks.length} queued, running, or waiting task(s) have been unchanged for 15-20+ minutes.`
      : "",
    didNotCompleteTasks.length > 0
      ? `${didNotCompleteTasks.length} recent task(s) ended blocked, interrupted, or failed and still need review.`
      : "",
    pendingApprovalCount > 0
      ? `${pendingApprovalCount} approval request(s) are waiting on the operator.`
      : "",
    blockedCount > 0
      ? `${blockedCount} human-needed task(s) remain blocked in the current queue state.`
      : "",
    interruptedCount > 0
      ? `${interruptedCount} interrupted task(s) are visible and require review before any re-queue.`
      : "",
  ].filter(Boolean);

  const focusTask = currentTask
    || wrongWindowBlocks[0]
    || stalledTasks[0]
    || sortedTasks.find((item) => ghotiActionableStatuses.has(normalizeGhotiText(item.status)))
    || null;
  const overlayTarget = buildGhotiOverlayTarget(focusTask);
  const handoffHint = wrongWindowBlocks.length > 0 || overlayTarget.kind === "handoff"
    ? "Codex to ChatGPT handoff stays paste-only by default and blocks before input whenever the wrong window stays foreground or the destination is not confident."
    : "Ctrl+8 is still the emergency stop if a desktop action or operator recipe needs immediate interruption.";

  return {
    status,
    headline,
    alerts,
    wrongWindowBlockCount: wrongWindowBlocks.length,
    stalledTaskCount: stalledTasks.length,
    didNotCompleteCount: didNotCompleteTasks.length,
    attentionRequired: alerts.length > 0,
    handoffHint,
    overlayTarget,
  };
}

function classifyGhotiTaskType(task) {
  const actionType = String(task?.actionType || "").toLowerCase();
  const recipeName = String(task?.recipeName || "").toLowerCase();
  const sourceWindow = String(task?.sourceWindow || "").toLowerCase();
  const targetWindow = String(task?.targetWindow || "").toLowerCase();

  if (actionType === "run_operator_recipe") {
    if (
      recipeName === "codex_to_chatgpt_handoff_mvp"
      || (sourceWindow === "codex" && targetWindow === "chatgpt")
    ) {
      return "handoff";
    }
    return "recipe";
  }

  if (isDesktopExecutorAction(actionType)) {
    return "desktop";
  }

  return "repo";
}

function humanizeGhotiTaskType(taskType) {
  const mapping = {
    repo: "Repo action",
    desktop: "Desktop action",
    recipe: "Operator recipe",
    handoff: "Codex to ChatGPT handoff",
  };
  return mapping[taskType] || "Task";
}

function sortGhotiTasks(tasks) {
  return [...(tasks || [])].sort((left, right) => {
    const leftUpdated = String(left?.updatedAt || "");
    const rightUpdated = String(right?.updatedAt || "");
    const byUpdated = rightUpdated.localeCompare(leftUpdated);
    if (byUpdated !== 0) {
      return byUpdated;
    }
    return String(right?.taskId || "").localeCompare(String(left?.taskId || ""));
  });
}

function decorateGhotiTask(task) {
  const taskType = classifyGhotiTaskType(task);
  const headline = task.title && task.title !== "Executor task"
    ? task.title
    : `${humanizeGhotiTaskType(taskType)} ${task.taskId || ""}`.trim();
  return {
    ...task,
    taskType,
    taskTypeLabel: humanizeGhotiTaskType(taskType),
    headline,
    detail: task.lastSummary || task.detail || "No recent summary.",
  };
}

function filterGhotiTasks(tasks, filters = {}) {
  const visibility = String(filters.visibility || "actionable").toLowerCase();
  const requestedType = String(filters.taskType || "all").toLowerCase();
  const requestedStatus = String(filters.taskStatus || "all").toLowerCase();
  const activeOnly = Boolean(filters.activeOnly);
  const limit = parsePositiveIntQuery(filters.limit, 8);

  let items = sortGhotiTasks((tasks || []).map(decorateGhotiTask));
  const totalCount = items.length;

  if (visibility !== "all") {
    items = items.filter((item) => ghotiActionableStatuses.has(String(item.status || "").toLowerCase()));
  }

  if (activeOnly) {
    items = items.filter((item) => ghotiActiveStatuses.has(String(item.status || "").toLowerCase()));
  }

  if (requestedType !== "all") {
    items = items.filter((item) => item.taskType === requestedType);
  }

  if (requestedStatus !== "all") {
    items = items.filter((item) => String(item.status || "").toLowerCase() === requestedStatus);
  }

  return {
    items: items.slice(0, limit),
    totalCount,
    filteredCount: items.length,
    visibility,
    taskType: requestedType,
    taskStatus: requestedStatus,
    activeOnly,
    limit,
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

async function buildTaskItemResponse(taskId) {
  const raw = await runRuntimeCli(["task-status", "--task-id", taskId]);
  return {
    ok: raw.ok,
    summary: raw.ok ? parseTaskDetail(raw.stdout) : null,
    raw,
    localOnly: true,
  };
}

async function buildExecutorTasksResponse() {
  const raw = await runRuntimeCli(["list-executor-tasks"]);
  return {
    ok: raw.ok,
    summary: raw.ok ? parseExecutorTaskList(raw.stdout) : null,
    raw,
    localOnly: true,
  };
}

function buildCompactSupervisorSummary(summary) {
  if (!summary) {
    return null;
  }

  return {
    headline: summary.headline || "Supervisor status unavailable.",
    status: summary.status || "unknown",
    ghotiState: summary.ghotiState || "idle",
    ghotiReason: summary.ghotiReason || "none",
    operatorNextStep: summary.operatorNextStep || "Refresh supervisor status.",
    pendingApprovalCount: Number(summary.pendingApprovalCount || 0),
    blockedHumanNeededCount: Number(summary.blockedHumanNeededCount || 0),
    waitingCount: Number(summary.waitingCount || 0),
    readyToResumeCount: Number(summary.readyToResumeCount || 0),
    interruptedCount: Number(summary.interruptedCount || 0),
    resourceGuardEventCount: Number(summary.resourceGuardEventCount || 0),
  };
}

function buildCompactExecutorTaskSummary(summary) {
  if (!summary) {
    return null;
  }

  return {
    headline: summary.headline || "No executor tasks queued yet.",
    count: Number(summary.count || 0),
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

async function buildBrainStatusResponse() {
  const raw = await runRuntimeCli(["brain-status"]);
  return {
    ok: raw.ok,
    summary: parseBrainStatus(raw.stdout),
    raw,
    localOnly: true,
  };
}

async function buildAgentRoleResponse() {
  const raw = await runRuntimeCli(["list-agent-roles"]);
  return {
    ok: raw.ok,
    summary: parseAgentRoleStatus(raw.stdout),
    raw,
    localOnly: true,
  };
}

async function buildBrowserStatusResponse() {
  const raw = await runRuntimeCli(["browser-status"]);
  return {
    ok: raw.ok,
    summary: parseBrowserStatus(raw.stdout),
    raw,
    localOnly: true,
  };
}

async function buildMemoryStatusResponse() {
  const raw = await runRuntimeCli(["memory-status"]);
  return {
    ok: raw.ok,
    summary: parseMemoryStatus(raw.stdout),
    raw,
    localOnly: true,
  };
}

async function buildRelayStatusResponse() {
  const raw = await runRuntimeCli(["relay-status"]);
  return {
    ok: raw.ok,
    summary: parseRelayStatus(raw.stdout),
    raw,
    localOnly: true,
  };
}

function parseCliJson(stdout) {
  if (!stdout) {
    return null;
  }

  const normalized = String(stdout).trimEnd();
  const markerMatch = normalized.match(/(?:^|\r?\n)---\r?\n([\s\S]+)$/);
  if (!markerMatch) {
    return null;
  }

  const jsonPart = markerMatch[1].trim();
  if (!jsonPart) {
    return null;
  }

  try {
    const parsed = JSON.parse(jsonPart);
    return parsed && typeof parsed === "object" ? parsed : null;
  } catch (_) {
    return null;
  }
}

function buildCliJsonFailure(raw, error, parsed = null) {
  return {
    ok: false,
    summary: null,
    detail: parsed,
    raw,
    localOnly: true,
    error,
  };
}

function buildCliSummaryResponse(raw, label) {
  const parsed = parseCliJson(raw.stdout);
  if (!raw.ok) {
    return buildCliJsonFailure(raw, raw.stderr || raw.stdout || `${label} failed.`, parsed);
  }
  if (!parsed || typeof parsed !== "object") {
    return buildCliJsonFailure(raw, `${label} returned an invalid CLI JSON payload.`, parsed);
  }
  if (!parsed.summary || typeof parsed.summary !== "object") {
    return buildCliJsonFailure(raw, `${label} returned no summary.`, parsed);
  }
  if (parsed.status === "error") {
    const errors = Array.isArray(parsed.errors) ? parsed.errors.filter(Boolean) : [];
    return buildCliJsonFailure(raw, errors[0] || `${label} returned an error status.`, parsed);
  }
  return {
    ok: true,
    summary: parsed.summary,
    detail: parsed,
    raw,
    localOnly: true,
  };
}

function buildCliActionResponse(raw, label, fallbackHeadline) {
  const parsed = parseCliJson(raw.stdout);
  if (!parsed || typeof parsed !== "object") {
    return {
      ok: false,
      localOnly: true,
      summary: { headline: fallbackHeadline || `${label} failed.` },
      detail: parsed,
      raw,
      error: `${label} returned an invalid CLI JSON payload.`,
    };
  }
  if (!parsed.summary || typeof parsed.summary !== "object") {
    return {
      ok: false,
      localOnly: true,
      summary: { headline: fallbackHeadline || `${label} failed.` },
      detail: parsed,
      raw,
      error: `${label} returned no summary.`,
    };
  }

  const errors = Array.isArray(parsed.errors) ? parsed.errors.filter(Boolean) : [];
  const ok = raw.ok && parsed.status === "ok";
  const headline = parsed.summary.headline || fallbackHeadline || (ok ? `${label} completed.` : `${label} failed.`);

  return {
    ok,
    localOnly: true,
    summary: {
      ...parsed.summary,
      headline,
    },
    detail: parsed,
    raw,
    error: ok ? null : (errors[0] || raw.stderr || raw.stdout || `${label} failed.`),
  };
}

async function buildApprovalInboxResponse() {
  const raw = await runRuntimeCli(["ghoti-approval-list"]);
  return buildCliSummaryResponse(raw, "Approval inbox");
}

async function buildApprovalItemDetailResponse(approvalId) {
  const raw = await runRuntimeCli(["ghoti-approval-view", approvalId]);
  return buildCliSummaryResponse(raw, "Approval item detail");
}

async function buildManualQueueResponse() {
  const raw = await runRuntimeCli(["ghoti-manual-queue-list"]);
  return buildCliSummaryResponse(raw, "Manual queue");
}

async function buildManualQueueItemResponse(itemId) {
  const raw = await runRuntimeCli(["ghoti-manual-queue-view", itemId]);
  return buildCliSummaryResponse(raw, "Manual queue item detail");
}

async function buildAuditTraceResponse(approvalId) {
  const raw = await runRuntimeCli(["ghoti-audit-trace", approvalId]);
  return buildCliSummaryResponse(raw, "Audit trace");
}

async function buildControlCenterStateResponse() {
  const raw = await runRuntimeCli(["ghoti-control-center-state"]);
  return buildCliSummaryResponse(raw, "Control center state");
}

async function buildPipelineStateResponse() {
  const raw = await runRuntimeCli(["ghoti-control-center-state"]);
  return buildCliSummaryResponse(raw, "Pipeline state");
}

async function buildPipelineItemsResponse(statusFilter) {
  const cliArgs = ["ghoti-pipeline-items"];
  if (statusFilter) {
    cliArgs.push("--status", statusFilter);
  }
  const raw = await runRuntimeCli(cliArgs);
  return buildCliSummaryResponse(raw, "Pipeline items");
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

async function buildHandoffTargetCandidatesResponse() {
  const raw = await runDesktopBridgeAction("list_windows");
  const parsed = parseKeyValueBlock(raw.stdout);
  const windows = (parsed.listSections.windows || [])
    .filter((item) => item !== "none")
    .map(parseWindowCandidateLine);
  const codexCandidates = windows.filter((item) => item.aliases.includes("codex"));
  const chatgptCandidates = windows.filter((item) => item.aliases.includes("chatgpt"));

  return {
    ok: raw.ok,
    summary: {
      headline: raw.ok
        ? `Loaded ${codexCandidates.length} Codex and ${chatgptCandidates.length} ChatGPT window candidate(s).`
        : "Failed to load handoff target candidates.",
      codexCandidates,
      chatgptCandidates,
      candidateCount: windows.length,
    },
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

    if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/control-center") {
      const payload = await buildGhotiControlCenterResponse({
      visibility: requestUrl.searchParams.get("visibility") || "actionable",
      taskType: requestUrl.searchParams.get("taskType") || "all",
      taskStatus: requestUrl.searchParams.get("taskStatus") || "all",
      activeOnly: parseBooleanQuery(requestUrl.searchParams.get("activeOnly"), false),
      limit: parsePositiveIntQuery(requestUrl.searchParams.get("limit"), 8),
    });
    pushAction({
      actionType: "status",
      label: "Viewed Ghoti control center",
      status: payload.ok ? "success" : "error",
      summary: payload.summary.headline,
    });
      sendJson(response, payload.ok ? 200 : 500, payload);
      return;
    }

    if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/pipeline-items") {
      const statusFilter = requestUrl.searchParams.get("status") || null;
      const payload = await buildPipelineItemsResponse(statusFilter);
      pushAction({
        actionType: "status",
        label: "Viewed Ghoti pipeline items",
        status: payload.ok ? "success" : "error",
        summary: payload.ok ? `Pipeline items loaded${statusFilter ? ` (filter: ${statusFilter})` : ""}.` : "Pipeline items unavailable.",
      });
      sendJson(response, payload.ok ? 200 : 500, payload);
      return;
    }

    if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/pipeline-state") {
      const payload = await buildPipelineStateResponse();
      pushAction({
        actionType: "status",
        label: "Viewed Ghoti pipeline state",
        status: payload.ok ? "success" : "error",
        summary: payload.ok ? "Pipeline state loaded." : "Pipeline state unavailable.",
      });
      sendJson(response, payload.ok ? 200 : 500, payload);
      return;
    }

    if (request.method === "GET" && requestUrl.pathname === "/api/brain/status") {
      const payload = await buildBrainStatusResponse();
      pushAction({
        actionType: "status",
        label: "Viewed brain status",
        status: payload.ok ? "success" : "error",
        summary: payload.summary.headline,
      });
      sendJson(response, payload.ok ? 200 : 500, payload);
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

  if (request.method === "GET" && requestUrl.pathname === "/api/tasks/item") {
    const taskId = requestUrl.searchParams.get("taskId");
    if (!taskId) {
      throw new Error("Missing taskId query parameter.");
    }

    const payload = await buildTaskItemResponse(taskId);
    pushAction({
      actionType: "task",
      label: "Viewed task item",
      status: payload.ok ? "success" : "error",
      summary: payload.ok && payload.summary
        ? payload.summary.headline
        : (payload.raw.stderr || "Task item lookup failed."),
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/executor/tasks") {
    const payload = await buildExecutorTasksResponse();
    pushAction({
      actionType: "executor",
      label: "Viewed executor task list",
      status: payload.ok ? "success" : "error",
      summary: payload.ok && payload.summary
        ? payload.summary.headline
        : (payload.raw.stderr || "Executor task list failed."),
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

  if (request.method === "POST" && requestUrl.pathname === "/api/executor/queue") {
    const payload = await readJsonBody(request);
    requireFields(payload, ["actionType"]);

    const cliArgs = [
      "queue-executor-action",
      "--action-type",
      String(payload.actionType),
    ];

    if (payload.target) {
      cliArgs.push("--target", String(payload.target));
    }
    if (payload.content) {
      cliArgs.push("--content", String(payload.content));
    }
    cliArgs.push("--source", "dashboard");

    const raw = await runRuntimeCli(cliArgs);
    const taskId = extractOutputPath("task_id", raw.stdout) || "none";
    const taskPayload = taskId !== "none" ? await buildTaskItemResponse(taskId) : { ok: false, summary: null, raw: { stdout: "", stderr: "Task id missing." } };
    const executorPayload = await buildExecutorTasksResponse();
    const supervisorPayload = await buildSupervisorResponse();
    const ok = raw.ok && taskPayload.ok && executorPayload.ok && supervisorPayload.ok;

    const summaryHeadline = ok
      ? (
          taskPayload.summary?.approvalState === "pending"
            ? "Executor task queued and now waiting for approval."
            : "Executor task queued."
        )
      : (raw.stderr || raw.stdout || "Executor task queue failed.");

    pushAction({
      actionType: "executor",
      label: "Queued executor task",
      status: ok ? "success" : "error",
      summary: summaryHeadline,
      outputPath: taskId,
    });

    sendJson(response, ok ? 200 : 500, {
      ok,
      localOnly: true,
      summary: {
        headline: summaryHeadline,
        taskId,
        status: taskPayload.summary?.status || "unknown",
      },
      task: taskPayload.summary,
      taskRaw: taskPayload.raw,
      executorTasks: executorPayload.summary,
      supervisor: supervisorPayload.summary,
      raw: {
        queue: raw,
      },
    });
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
      ? (
          decision === "approve" && approvalPayload.summary?.workspacePolicy === "blocked_by_workspace_policy"
            ? "Approval recorded, but workspace policy still blocks execution."
            : headlineMap[decision]
        )
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

  if (request.method === "POST" && requestUrl.pathname === "/api/tasks/action") {
    const payload = await readJsonBody(request);
    requireFields(payload, ["taskId", "action"]);

    const taskId = String(payload.taskId).trim();
    const action = String(payload.action).trim().toLowerCase();
    const note = payload.note ? String(payload.note) : "";
    const commandMap = {
      review: "review-task",
      resume: "resume",
      requeue: "requeue-task",
      execute: "execute-task",
    };
    const command = commandMap[action];
    if (!command) {
      throw new Error("Unsupported task action.");
    }

    const cliArgs = [command, "--task-id", taskId];
    if (note.trim() && (action === "review" || action === "requeue")) {
      cliArgs.push("--note", note);
    }

    const raw = await runRuntimeCli(cliArgs);
    const taskPayload = await buildTaskItemResponse(taskId);
    const supervisorPayload = await buildSupervisorResponse();
    const executorPayload = await buildExecutorTasksResponse();
    const ok = raw.ok && taskPayload.ok && supervisorPayload.ok && executorPayload.ok;

    const headlineMap = {
      review: "Task review recorded.",
      resume: "Waiting task resumed.",
      requeue: "Task re-queued.",
      execute: "Allowlisted executor action completed.",
    };
    let summaryHeadline = headlineMap[action] || "Task action completed.";
    if (!ok) {
      summaryHeadline = raw.stderr || raw.stdout || "Task action failed.";
    } else if (action === "execute" && taskPayload.summary?.status === "interrupted") {
      summaryHeadline = "Desktop action interrupted by the local failsafe.";
    } else if (
      action === "execute" &&
      taskPayload.summary?.status === "blocked_human_needed" &&
      taskPayload.summary?.lastExecutionStatus === "failed"
    ) {
      summaryHeadline =
        taskPayload.summary?.lastExecutionSummary
        || taskPayload.summary?.blockedReason
        || "Allowlisted executor action was blocked.";
    } else if (
      action === "execute" &&
      taskPayload.summary?.status === "failed" &&
      taskPayload.summary?.lastExecutionStatus === "failed"
    ) {
      summaryHeadline =
        taskPayload.summary?.lastExecutionSummary
        || taskPayload.summary?.lastFailureReason
        || "Allowlisted executor action failed.";
    } else if (
      action === "review" &&
      taskPayload.summary?.workspacePolicy === "blocked_by_workspace_policy" &&
      taskPayload.summary?.status === "blocked_human_needed"
    ) {
      summaryHeadline = "Task review recorded, but workspace policy still blocks it.";
    }

    pushAction({
      actionType: "task",
      label: `${action[0].toUpperCase()}${action.slice(1)} task`,
      status: ok ? "success" : "error",
      summary: summaryHeadline,
      outputPath: taskId,
    });

    sendJson(response, ok ? 200 : 500, {
      ok,
      localOnly: true,
      summary: {
        headline: summaryHeadline,
        taskId,
        action,
        status: taskPayload.summary?.status || "unknown",
      },
      task: taskPayload.summary,
      taskRaw: taskPayload.raw,
      supervisor: buildCompactSupervisorSummary(supervisorPayload.summary),
      executorTasks: buildCompactExecutorTaskSummary(executorPayload.summary),
      raw: {
        action: raw,
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
    const requestPayload = await readJsonBody(request);
    const runFullCheck = requestPayload.fullCheck === true && requestPayload.allowDisruptiveActions === true;
    const payload = await buildDesktopBridgeResponse(!runFullCheck);
    pushAction({
      actionType: "desktop",
      label: runFullCheck ? "Ran desktop bridge check" : "Ran desktop bridge status check",
      status: payload.ok ? "success" : "error",
      summary: payload.summary.headline,
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/desktop-bridge/handoff-targets") {
    const payload = await buildHandoffTargetCandidatesResponse();
    pushAction({
      actionType: "desktop",
      label: "Viewed handoff target candidates",
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

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/control-center-state") {
    const payload = await buildControlCenterStateResponse();
    pushAction({ actionType: "status", label: "Viewed Ghoti control center state", status: payload.ok ? "success" : "error", summary: payload.ok ? "Control center state loaded." : "Control center state unavailable." });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/approval-inbox") {
    const payload = await buildApprovalInboxResponse();
    pushAction({ actionType: "approval", label: "Viewed Ghoti approval inbox", status: payload.ok ? "success" : "error", summary: payload.ok ? "Approval inbox loaded." : "Approval inbox unavailable." });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/approval-item") {
    const id = requestUrl.searchParams.get("id");
    if (!id) {
      sendJson(response, 400, { ok: false, error: "Missing id query parameter." });
      return;
    }
    const payload = await buildApprovalItemDetailResponse(id);
    pushAction({ actionType: "approval", label: "Viewed approval item detail", status: payload.ok ? "success" : "error", summary: payload.ok ? `Approval ${id} loaded.` : `Approval ${id} not found.` });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/manual-queue") {
    const payload = await buildManualQueueResponse();
    pushAction({ actionType: "status", label: "Viewed Ghoti manual queue", status: payload.ok ? "success" : "error", summary: payload.ok ? "Manual queue loaded." : "Manual queue unavailable." });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/manual-queue-item") {
    const id = requestUrl.searchParams.get("id");
    if (!id) {
      sendJson(response, 400, { ok: false, error: "Missing id query parameter." });
      return;
    }
    const payload = await buildManualQueueItemResponse(id);
    pushAction({ actionType: "status", label: "Viewed manual queue item", status: payload.ok ? "success" : "error", summary: payload.ok ? `Queue item ${id} loaded.` : `Queue item ${id} not found.` });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/audit-trace") {
    const id = requestUrl.searchParams.get("approval_id");
    if (!id) {
      sendJson(response, 400, { ok: false, error: "Missing approval_id query parameter." });
      return;
    }
    const payload = await buildAuditTraceResponse(id);
    pushAction({ actionType: "status", label: "Viewed audit trace", status: payload.ok ? "success" : "error", summary: payload.ok ? `Audit trace for ${id} loaded.` : `Audit trace for ${id} unavailable.` });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/approval/approve") {
    const body = await readJsonBody(request);
    requireFields(body, ["approval_id"]);
    const approvalId = String(body.approval_id).trim();
    const raw = await runRuntimeCli(["ghoti-approval-approve", approvalId]);
    const payload = buildCliActionResponse(raw, "Approval approve", "Approval approve failed.");
    pushAction({
      actionType: "approval",
      label: "Approved ghoti approval",
      status: payload.ok ? "success" : "error",
      summary: payload.summary?.headline || payload.error || "Approve failed.",
      outputPath: approvalId,
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/approval/reject") {
    const body = await readJsonBody(request);
    requireFields(body, ["approval_id", "reason"]);
    const approvalId = String(body.approval_id).trim();
    const reason = String(body.reason).trim();
    if (!reason) throw new Error("reason is required to reject an approval.");
    const raw = await runRuntimeCli(["ghoti-approval-reject", approvalId, "--reason", reason]);
    const payload = buildCliActionResponse(raw, "Approval reject", "Approval reject failed.");
    pushAction({
      actionType: "approval",
      label: "Rejected ghoti approval",
      status: payload.ok ? "success" : "error",
      summary: payload.summary?.headline || payload.error || "Reject failed.",
      outputPath: approvalId,
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/manual-queue/review") {
    const body = await readJsonBody(request);
    requireFields(body, ["item_id", "note"]);
    const itemId = String(body.item_id).trim();
    const note = String(body.note).trim();
    if (!note) throw new Error("note is required to mark a queue item reviewed.");
    const raw = await runRuntimeCli(["ghoti-manual-queue-mark-reviewed", itemId, "--note", note]);
    const payload = buildCliActionResponse(raw, "Manual queue review", "Queue item review failed.");
    pushAction({
      actionType: "status",
      label: "Marked queue item reviewed",
      status: payload.ok ? "success" : "error",
      summary: payload.summary?.headline || payload.error || "Review failed.",
      outputPath: itemId,
    });
    sendJson(response, payload.ok ? 200 : 500, payload);
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/active-state") {
    const state = readActiveModeState();
    sendJson(response, 200, { ok: true, state });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/active/start") {
    const state = writeActiveModeState({ active: true, mode: "active", screen_view_enabled: true, error: null });
    pushAction({ actionType: "status", label: "Ghoti Active Mode started", status: "success", summary: "Operator started Ghoti Active Mode." });
    sendJson(response, 200, { ok: true, state });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/active/stop") {
    stopCaptureProcess();
    const state = writeActiveModeState({ active: false, mode: "idle", screen_view_enabled: false, error: null });
    pushAction({ actionType: "status", label: "Ghoti Active Mode stopped", status: "success", summary: "Operator stopped Ghoti Active Mode." });
    sendJson(response, 200, { ok: true, state });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/active/snapshot") {
    if (!fs.existsSync(screenshotsDir)) fs.mkdirSync(screenshotsDir, { recursive: true });
    const snapshotFilename = `ghoti-snapshot-${Date.now()}.png`;
    const snapshotPath = path.join(screenshotsDir, snapshotFilename);
    const powerShell = resolvePowerShell();
    if (!powerShell) {
      const state = writeActiveModeState({ error: "PowerShell not found — cannot capture screenshot." });
      sendJson(response, 500, { ok: false, error: "PowerShell not found.", state });
      return;
    }
    const psScript = [
      "Add-Type -AssemblyName System.Windows.Forms",
      "Add-Type -AssemblyName System.Drawing",
      "$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds",
      "$bmp = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)",
      "$g = [System.Drawing.Graphics]::FromImage($bmp)",
      "$g.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)",
      "$g.Dispose()",
      `$bmp.Save("${snapshotPath.replace(/\\/g, "\\\\")}")`,
      "$bmp.Dispose()",
      "Write-Output 'ok'",
    ].join("; ");
    const result = await runCommand(powerShell.command, [...powerShell.baseArgs, "-ExecutionPolicy", "Bypass", "-Command", psScript], { cwd: repoRoot, timeoutMs: 20000 });
    if (!result.ok || !fs.existsSync(snapshotPath)) {
      const errMsg = result.stderr || result.stdout || "Screenshot capture failed.";
      const state = writeActiveModeState({ error: `Screenshot failed: ${errMsg}` });
      sendJson(response, 500, { ok: false, error: errMsg, state });
      return;
    }
    const relPath = path.relative(repoRoot, snapshotPath).replace(/\\/g, "/");
    const state = writeActiveModeState({ last_snapshot_path: relPath, mode: "active", error: null });
    pushAction({ actionType: "status", label: "Ghoti snapshot captured", status: "success", summary: `Snapshot saved: ${relPath}` });
    sendJson(response, 200, { ok: true, snapshotPath: relPath, state });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/active/message") {
    const body = await readJsonBody(request);
    requireFields(body, ["message"]);
    const msg = String(body.message || "").trim();
    if (!msg) throw new Error("message is required.");
    const state = writeActiveModeState({ mode: "processing", error: null });
    pushAction({ actionType: "status", label: "Ghoti received instruction", status: "success", summary: `Operator message: ${msg.slice(0, 80)}` });
    const ackState = writeActiveModeState({ mode: "waiting_for_approval" });
    sendJson(response, 200, { ok: true, received: msg, note: "Instruction logged. Operator approval required before any action is taken.", state: ackState });
    return;
  }

  if (request.method === "GET" && requestUrl.pathname === "/api/ghoti/active/capture-state") {
    const captureState = readCaptureState();
    sendJson(response, 200, { ok: true, captureState });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/active/capture/start") {
    const activeState = readActiveModeState();
    if (!activeState.active) {
      sendJson(response, 400, { ok: false, error: "Ghoti is not active. Start Ghoti first.", captureState: readCaptureState() });
      return;
    }
    if (captureInterval) {
      sendJson(response, 200, { ok: true, note: "Capture already running.", captureState: readCaptureState() });
      return;
    }

    const powerShell = resolvePowerShell();
    if (!powerShell) {
      sendJson(response, 500, { ok: false, error: "PowerShell not found — cannot start screen capture.", captureState: readCaptureState() });
      return;
    }

    if (!fs.existsSync(runtimeDataDir)) fs.mkdirSync(runtimeDataDir, { recursive: true });
    if (!fs.existsSync(captureFramesDir)) fs.mkdirSync(captureFramesDir, { recursive: true });

    captureFrameCount = 0;
    captureTickRunning = false;

    fs.writeFileSync(captureStateFile, JSON.stringify({
      capturing: true,
      capture_method: "powershell-copyfromscreen-loop",
      fps_target: 1,
      frame_count: 0,
      latest_frame_path: null,
      latest_frame_utc: null,
      error: null,
    }, null, 2));

    // Kick off first frame immediately (non-blocking)
    captureOneTick(powerShell);

    // Then repeat at 1 FPS
    captureInterval = setInterval(() => captureOneTick(powerShell), 1000);

    const captureState = readCaptureState();
    pushAction({ actionType: "status", label: "Screen capture started", status: "success", summary: "Continuous capture at 1 FPS via PowerShell" });
    sendJson(response, 200, { ok: true, captureState });
    return;
  }

  if (request.method === "POST" && requestUrl.pathname === "/api/ghoti/active/capture/stop") {
    stopCaptureProcess();
    const captureState = readCaptureState();
    pushAction({ actionType: "status", label: "Screen capture stopped", status: "success", summary: "Operator stopped continuous capture." });
    sendJson(response, 200, { ok: true, captureState });
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











