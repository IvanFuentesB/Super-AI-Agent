"use strict";
// Daily shell: real same-origin runtime data only. No demo data or legacy execution.
(() => {
  const $ = id => document.getElementById(id);
  const text = (id, value) => { if ($(id).textContent !== String(value)) $(id).textContent = value; };
  const node = (tag, content, className) => {
    const element = document.createElement(tag);
    if (content !== undefined) element.textContent = content;
    if (className) element.className = className;
    return element;
  };
  // Boxes that scroll must be reachable and named for keyboard and assistive-technology users.
  const scrollable = (element, label) => {
    element.tabIndex = 0;
    element.setAttribute("role", "group");
    element.setAttribute("aria-label", label);
    return element;
  };
  const json = value => JSON.stringify(value, null, 2);
  const value = item => item === undefined || item === null ? "not reported" : typeof item === "object" ? json(item) : String(item);
  const labels = {chat: "Chat", computer: "Computer", projects: "Projects", agents: "Agents", memory: "Memory", tools: "Tools", settings: "Settings"};
  function menu(open) {
    $("daily-sidebar").dataset.menuOpen = String(open);
    $("daily-menu").setAttribute("aria-expanded", String(open));
  }
  const hashView = () => String(location.hash || "").slice(1);
  function navigate(view, {remember = true} = {}) {
    if (!labels[view]) return;
    // The hash keeps Back, Reload and bookmarks on the view the person chose.
    if (remember && typeof history === "object" && hashView() !== view) history.pushState(null, "", `#${view}`);
    document.querySelectorAll("[data-daily-panel]").forEach(panel => { panel.hidden = panel.dataset.dailyPanel !== view; });
    document.querySelectorAll("[data-daily-view]").forEach(button => { button.setAttribute("aria-current", button.dataset.dailyView === view ? "page" : "false"); });
    text("daily-title", labels[view]);
    menu(false);
    $("daily-title").focus();
  }
  document.querySelectorAll("[data-daily-view]").forEach(button => button.addEventListener("click", () => navigate(button.dataset.dailyView)));
  document.querySelectorAll("[data-go]").forEach(button => button.addEventListener("click", () => navigate(button.dataset.go)));
  $("daily-menu").addEventListener("click", () => menu($("daily-sidebar").dataset.menuOpen !== "true"));
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && $("daily-sidebar").dataset.menuOpen === "true") { menu(false); $("daily-menu").focus(); }
  });
  document.querySelectorAll("[data-draft]").forEach(button => button.addEventListener("click", () => {
    // Suggestions fill an empty draft only; never overwrite writing or submit a task.
    if (!$("daily-prompt").value.trim()) $("daily-prompt").value = button.dataset.draft;
    $("daily-prompt").focus();
  }));
  $("daily-brand").addEventListener("click", event => { event.preventDefault(); navigate("chat"); });
  const memo = new Map();
  // Navigation carries each view's state so it is visible from any other view.
  const baseTitle = document.title;
  function attention() {
    const tones = ["chat", "computer", "projects", "memory"].map(view => $(`daily-nav-${view}-state`).dataset.state);
    const tone = tones.includes("permission") ? "permission" : tones.some(item => ["disconnected", "unavailable", "attention", "failed", "unconfirmed"].includes(item)) ? "attention" : "";
    if ($("daily-menu").dataset.state !== tone) $("daily-menu").dataset.state = tone;
    const title = tone === "permission" ? `Approval needed · ${baseTitle}` : baseTitle;
    if (document.title !== title) document.title = title;
  }
  function navState(view, label, tone) {
    const badge = $(`daily-nav-${view}-state`);
    if (badge.textContent !== label) badge.textContent = label;
    if (badge.dataset.state !== tone) badge.dataset.state = tone;
    attention();
  }
  // The Computer view writes its own badge; follow it at once so the Menu dot and tab title never trail a state change.
  if (typeof MutationObserver === "function") new MutationObserver(attention).observe($("daily-nav-computer-state"), {attributes: true, childList: true});
  function list(id, entries, empty, makeRow) {
    const signature = json(entries) + empty;
    if (memo.get(id) === signature) return;
    memo.set(id, signature);
    $(id).replaceChildren();
    if (!entries.length) { text(id, empty); return; }
    for (const entry of entries) $(id).append(makeRow(entry));
  }
  const stateOf = item => String(item?.state || item?.status || "").toLowerCase();
  function record(title, description, evidence, state) {
    const row = node("article", undefined, "d-record");
    if (state) row.dataset.state = state;
    row.append(node("strong", title), node("p", description));
    if (evidence) {
      const detail = node("details");
      detail.append(node("summary", "Task details"), scrollable(node("pre", json(evidence), "d-output"), `Task details: ${title}`));
      row.append(detail);
    }
    return row;
  }
  let client;
  let messageNodes = [];
  const phaseLabels = {
    loading: "Connecting to chat…", ready: "Ready when you are.", creating: "Opening your conversation…",
    submitting: "Sending once…", running: "Ghoti is working…", permission: "Your permission is needed. Review the action below.",
    approving: "Sending your decision…", syncing: "Reading the latest updates…", cancelling: "Stopping… waiting for the worker to finish.",
    complete: "Reply ready. Review any proposed actions before proceeding.", cancelled: "Stopped. Earlier actions may already have happened.",
    failed: "This conversation failed. Earlier actions may have happened. Check Developer view for details.",
    ended: "The conversation ended without a confirmed result. Start a new chat when ready.",
    unavailable: "Chat is unavailable. Refresh to reconnect, or check the connection in Settings.",
    disconnected: "Connection lost. Stop is not confirmed; actions may still be running or may already have happened. Nothing will be resent. Start a new chat to continue."
  };
  const working = {label: "Working", tone: "running"};
  const chatNav = {permission: {label: "Needs approval", tone: "permission"}, running: working, submitting: working, creating: working, syncing: working, approving: working,
    cancelling: {label: "Stopping", tone: "cancelling"}, disconnected: {label: "Connection lost", tone: "disconnected"}, unavailable: {label: "Unavailable", tone: "unavailable"}};
  // chat.js locks a disconnected session for good; once its safety stop has settled, a new conversation is the way on.
  const canStartNew = state => ["ready", "complete", "cancelled", "failed", "ended"].includes(state.phase) ||
    (state.phase === "disconnected" && (!state.sessionId || /Safety cancellation|Worker reported idle|Cancellation unconfirmed/.test(state.reason)));
  let permissionShown = false;
  const sessionLabels = {idle: "At rest", running: "Working", awaiting_permission: "Needs permission", cancelling: "Stopping", failed: "Stopped with an error", interrupted: "Interrupted", closed: "Closed"};
  function renderChat(state) {
    const uncertainStop = state.phase === "failed" && /^(tool_cancellation_uncertain|cancel_delivery_uncertain):/.test(state.reason);
    text("daily-chat-state", uncertainStop ? "Stop could not be confirmed. Actions may still be running or may already have happened. Check the runtime in Settings." : phaseLabels[state.phase] || "Chat state unavailable.");
    $("daily-chat-state").dataset.state = state.phase;
    text("daily-chat-reason", state.reason);
    text("daily-model", state.modelId ? `Astra · ${state.mode || "auto"} · effective ${state.effort || "unverified"}` : "Model unavailable");
    $("daily-chat-mode").value = state.mode || "auto";
    $("daily-chat-mode").disabled = !state.available || !["ready", "complete", "cancelled", "ended"].includes(state.phase);
    text("daily-chat-timings", json(state.timings || {}));
    text("daily-settings-model", state.modelId ? `${state.modelId} · ${state.effort}` : "Not verified");
    text("daily-session", state.sessionId ? `Session ${state.sessionId} · event ${state.cursor} · ${state.phase}` : "No session created.");
    $("daily-send").disabled = !state.available || !["ready", "complete", "cancelled", "ended"].includes(state.phase);
    $("daily-cancel").disabled = !state.sessionId || ["ready", "complete", "cancelled", "failed", "ended", "cancelling"].includes(state.phase);
    $("daily-cancel").hidden = ["loading", "unavailable", "ready", "complete", "cancelled", "failed", "ended"].includes(state.phase);
    if (state.phase === "disconnected") $("daily-cancel").disabled = true;
    $("daily-new").disabled = !canStartNew(state);
    navState("chat", chatNav[state.phase]?.label || "", chatNav[state.phase]?.tone || "");
    const stream = $("daily-conversation");
    const follow = stream.scrollHeight - stream.scrollTop - stream.clientHeight < 80;
    stream.hidden = state.messages.length === 0;
    $("daily-welcome").hidden = state.messages.length > 0;
    $("daily-suggestions").hidden = state.messages.length > 0;
    stream.setAttribute("aria-busy", String(["running", "submitting", "syncing"].includes(state.phase)));
    if (state.messages.length < messageNodes.length) { messageNodes = []; stream.replaceChildren(); }
    if (!state.messages.length) stream.replaceChildren();
    for (let index = 0; index < state.messages.length; index += 1) {
      const message = state.messages[index];
      if (!messageNodes[index]) {
        if (index === 0) stream.replaceChildren();
        const article = node("article", undefined, "d-message");
        article.dataset.role = message.role;
        const paragraph = node("p", "");
        article.append(node("strong", message.role === "user" ? "You" : "Ghoti"), paragraph);
        stream.append(article);
        messageNodes[index] = paragraph;
      }
      if (messageNodes[index].textContent !== message.text) messageNodes[index].textContent = message.text;
    }
    if (follow) stream.scrollTop = stream.scrollHeight;
    if (typeof requestAnimationFrame === "function" && !$("daily-panel-chat").hidden &&
        document.visibilityState === "visible" && state.messages.at(-1)?.role === "assistant" &&
        state.messages.at(-1).text.trim() && state.timings?.first_visible_text_ms === undefined) {
      const owner = client, requestId = owner.promptRequest;
      requestAnimationFrame(() => requestAnimationFrame(() => {
        if (client === owner && !$("daily-panel-chat").hidden && document.visibilityState === "visible") owner.noteVisibleText(requestId);
      }));
    }
    const permissions = state.phase === "permission" ? state.permissions : [];
    $("daily-permissions").hidden = permissions.length === 0;
    list("daily-permissions", permissions, "", permission => {
      const card = node("article", undefined, "permission-card");
      const flag = node("span", "Permission required", "d-status");
      flag.dataset.state = "permission";
      card.append(flag, node("h3", permission.title),
        scrollable(node("p", permission.description, "permission-description"), "Permission request text"));
      const identity = node("details");
      identity.append(node("summary", "Request details"), node("code", `Request ${permission.request_id} · session ${state.sessionId}`, "permission-id"));
      card.append(identity);
      const actions = node("div", undefined, "d-actions");
      // Explicitly render only offered fixed choices. Never trust labels as policy.
      for (const choice of ["deny", "allow_once"]) {
        if (!permission.options.some(option => option.id === choice)) continue;
        const button = node("button", choice === "deny" ? "Deny" : "Allow once", `d-button ${choice === "deny" ? "" : "primary"}`);
        button.type = "button";
        button.addEventListener("click", () => client.approve(permission.request_id, choice));
        actions.append(button);
      }
      card.append(actions);
      return card;
    });
    // A new approval request takes focus once, so it cannot sit unnoticed below the composer.
    if (permissions.length && !permissionShown && !$("daily-panel-chat").hidden) $("daily-permissions").focus();
    permissionShown = permissions.length > 0;
    list("daily-tool-events", state.tools, "No tools used in this conversation.", tool => record(tool.title, tool.status, tool, stateOf(tool)));
    renderSessions(state);
  }
  let historyBusy = false;
  function renderSessions(state) {
    const rows = state.sessions.map((session, index) => ({...session, label: `Conversation ${index + 1}`,
      description: `Last reported: ${sessionLabels[session.state] || "state not reported"}`, historyDisabled: ["running", "awaiting_permission", "cancelling"].includes(session.state)}));
    // The owned session has fresh events; other rows are explicitly snapshots.
    if (state.sessionId) {
      let current = rows.find(session => session.session_id === state.sessionId);
      if (!current) { current = {session_id: state.sessionId}; rows.push(current); }
      Object.assign(current, {label: "Current conversation", description: phaseLabels[state.phase] || "State unavailable.", state: state.phase, historyDisabled: true});
    }
    const empty = state.sessionsStatus === "ready" ? "No saved conversations reported yet." : "Conversation list unavailable. Refresh when connected.";
    list("daily-sessions", rows, empty, session => record(session.label, session.description, undefined, session.state));
    list("daily-history-list", rows, empty, session => {
      const row = record(session.label, session.description, undefined, session.state);
      const button = node("button", session.historyDisabled ? "Not available as history" : "Read saved replies", "d-button");
      button.type = "button";
      button.disabled = session.historyDisabled;
      button.addEventListener("click", async () => {
        if (historyBusy) return;
        historyBusy = true;
        const owner = client;
        button.disabled = true;
        const output = $("daily-history-output");
        output.hidden = false;
        output.textContent = "Reading saved replies…";
        try {
          const saved = await owner.readHistory(session.session_id);
          if (client !== owner) return;
          output.replaceChildren(node("h3", session.label));
          if (!saved.replies.length) output.append(node("p", "No assistant replies were saved."));
          if (["failed", "interrupted"].includes(saved.state)) output.append(node("p", "This conversation was interrupted or failed. Saved replies may be incomplete."));
          saved.replies.forEach((reply, index) => {
            const message = node("article", undefined, "d-message");
            message.append(node("strong", `Saved reply ${index + 1}${reply.partial ? " · incomplete" : ""}`), node("p", reply.text));
            output.append(message);
          });
        } catch (_) { if (client === owner) output.textContent = "Saved replies are unavailable or the conversation is active. Refresh the list; nothing was resumed."; }
        finally { historyBusy = false; button.disabled = false; }
      });
      row.append(button);
      return row;
    });
  }
  const newClient = () => {
    const created = new GhotiChat.ChatClient({fetch: (...args) => fetch(...args), onChange: state => {
      if (client === created) renderChat(state);
    }});
    return created;
  };
  client = newClient();
  $("daily-chat-mode").addEventListener("change", () => {
    client.setMode($("daily-chat-mode").value);
    $("daily-chat-mode").value = client.state.mode;
  });
  let stateBusy = false;
  let workerRegistered = false;
  let taskBusy = false;
  let allowedOperations = [];
  let jobs = [], references = [], showAllJobs = false;
  const operations = {capability_lookup: "Find coding capabilities", capability_plan: "Plan capabilities from a lookup", verify_capability_plan: "Check a saved capability plan", summarize_text: "Summarize local text", coding_brief: "Build a coding brief · three local steps"};
  const checkedScopes = new Set(["exact registry result comparison", "source digests, current registry and permission restrictions checked"]);
  function outcome(job) {
    // Execution, verification and memory are separate; provider eligibility is irrelevant.
    const state = String(job.state || job.status || "").toLowerCase();
    if (state === "failed") return "Couldn’t finish · review details";
    if (state === "blocked") return "Blocked · review what’s needed";
    if (state === "interrupted") return "Interrupted · outcome uncertain";
    if (["pending", "created"].includes(state)) return "Queued · not started";
    if (state === "succeeded") {
      const scopes = [job.verification_scope, ...(Array.isArray(job.result?.check_notes) ? job.result.check_notes : [])];
      if (job.result?.checked !== false && scopes.some(scope => checkedScopes.has(scope))) return "Completed · local checks passed";
      if (job.verification === "SUCCESS") return "Completed · computer result checked";
      if (scopes.includes("bounded nonempty safe text; factual accuracy requires human review")) return "Draft ready · review needed";
      return "Finished · review needed";
    }
    if (["executing", "verifying"].includes(state) && job.running === true) return "Working";
    return "Outcome not confirmed";
  }
  function showResult(container, raw) {
    container.replaceChildren();
    const source = typeof raw === "string" ? raw : json(raw);
    let parsed;
    try { parsed = JSON.parse(source); } catch (_) { /* Plain text remains plain text. */ }
    const items = Array.isArray(parsed) ? parsed : parsed?.items;
    if (Array.isArray(items) && items.every(item => item && typeof item.name === "string" && typeof item.use === "string")) {
      if (!items.length) container.append(node("p", "No matching capabilities found. Try a more specific description."));
      for (const item of items) container.append(record(item.name, item.use));
    } else if (parsed && typeof parsed === "object") {
      container.append(node("p", "A structured result was saved. Open result details to inspect it."));
    } else container.append(scrollable(node("p", source, "saved-result"), "Saved result"));
    const detail = node("details", undefined, "d-details");
    detail.append(node("summary", "Result details"), scrollable(node("pre", source, "d-output"), "Result details"));
    container.append(detail);
  }
  function jobRow(job) {
    const state = stateOf(job);
    // A run that no longer reports as live is shown as unconfirmed, matching outcome().
    const row = record(operations[job.title] || job.title || "Local task", outcome(job), job,
      ["executing", "verifying"].includes(state) && job.running !== true ? "unconfirmed" : ["pending", "created"].includes(state) ? "queued" : state);
    // Finishing a task and recording it in memory are separate facts.
    if (["succeeded", "failed", "blocked", "interrupted"].includes(state)) row.append(node("small", job.memory_event_id ? "Saved to memory" : "Not written to memory", "record-meta"));
    if (/^[a-z0-9][a-z0-9-]{2,80}$/.test(job.task_id)) {
      const result = node("div");
      result.hidden = true;
      const button = node("button", "Read saved result", "d-button");
      button.type = "button";
      button.addEventListener("click", async () => {
        button.disabled = true;
        result.hidden = false;
        result.textContent = "Reading saved result…";
        try {
          const output = await request(`/api/runtime/result/${job.task_id}`);
          if (output.task_id !== job.task_id || typeof output.text !== "string" || output.text.length > 8000) throw new Error("Saved result identity did not match");
          showResult(result, output.text);
        } catch (_) { result.textContent = "Saved result unavailable. No result was verified; refresh before retrying."; }
        finally { button.disabled = false; }
      });
      row.append(button, result);
    }
    return row;
  }
  function jobCounts() {
    const count = {running: 0, queued: 0, review: 0, done: 0};
    for (const job of jobs) {
      const state = stateOf(job);
      if (["executing", "verifying"].includes(state)) count[job.running === true ? "running" : "review"] += 1;
      else if (["pending", "created"].includes(state)) count.queued += 1;
      else if (["failed", "blocked", "interrupted"].includes(state)) count.review += 1;
      else if (state === "succeeded") count.done += 1;
    }
    return count;
  }
  function renderJobs() {
    const count = jobCounts();
    text("daily-jobs-summary", [count.running && `${count.running} running`, count.queued && `${count.queued} queued`,
      count.review && `${count.review} need${count.review === 1 ? "s" : ""} review`, count.done && `${count.done} completed`].filter(Boolean).join(" · "));
    navState("projects", count.running ? `${count.running} running` : "", count.running ? "running" : "");
    list("daily-jobs", showAllJobs ? jobs : jobs.slice(0, 5), "No recorded local work yet. Run a task above to get started.", jobRow);
    $("daily-more-jobs").hidden = jobs.length <= 5;
    text("daily-more-jobs", showAllJobs ? "Show recent results only" : `Show all ${jobs.length} results`);
  }
  $("daily-more-jobs").addEventListener("click", () => { showAllJobs = !showAllJobs; renderJobs(); });
  function renderMemory() {
    const query = $("daily-memory-search").value.toLowerCase().trim();
    const filtered = references.filter(ref => `${ref.system} ${ref.reason}`.toLowerCase().includes(query));
    list("daily-memory-list", filtered, query ? "No loaded references match this filter." : "No startup references reported.", ref =>
      record(ref.system === "obsidian" ? "Obsidian reference" : "Memory reference", ref.reason || "Available as startup context."));
    const total = references.length;
    text("daily-memory-count", !total ? "No references loaded." : query ? `${filtered.length} of ${total} references match` : `${total} reference${total === 1 ? "" : "s"} loaded`);
  }
  // The board is a separate local service. Only a runtime-reported status is shown; the page never probes it.
  // A failed status request is not a board report: say the status is unknown, and show the last report only as dated history.
  let lastPaperclip = null;
  const paperclipSummary = report => `${report.status === "STOPPED" ? "stopped" : "running"} · ${
    report.pending_approvals ? `${report.pending_approvals} approval${report.pending_approvals === 1 ? "" : "s"} waiting` : "no approvals waiting"}`;
  // An unchanged refresh must not rewrite the attribute (no mutation churn).
  function paperclipState(state) {
    if ($("daily-paperclip").dataset.state !== state) $("daily-paperclip").dataset.state = state;
  }
  function renderPaperclip(report, {failed = false} = {}) {
    if (failed) {
      text("daily-paperclip", `Couldn’t reach the runtime, so the Paperclip board’s current status is unknown.${
        lastPaperclip ? ` Last reported at ${lastPaperclip.at}: ${paperclipSummary(lastPaperclip.report)}. That may be out of date.` : ""} Open the board to check.`);
      paperclipState("unavailable");
      return;
    }
    const known = report?.schema === "ghoti_paperclip_status/1" && ["RUNNING", "STOPPED"].includes(report.status) &&
      Number.isInteger(report.pending_approvals) && report.pending_approvals >= 0;
    const waiting = known ? report.pending_approvals : 0;
    lastPaperclip = known ? {report: {status: report.status, pending_approvals: waiting}, at: new Date().toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"})} : null;
    text("daily-paperclip", !known ? "This page can’t verify the Paperclip board. The runtime doesn’t report its status yet; open the board to check." :
      report.status === "STOPPED" ? `The Paperclip board is stopped${waiting ? ` · ${waiting} approval${waiting === 1 ? "" : "s"} waiting for you on the board` : ""}. It starts on request.` :
        waiting ? `The Paperclip board is running · ${waiting} approval${waiting === 1 ? "" : "s"} waiting for you on the board.` : "The Paperclip board is running · no approvals waiting.");
    paperclipState(!known ? "unconfirmed" : report.status === "STOPPED" ? "attention" : waiting ? "permission" : "connected");
  }
  $("daily-memory-search").addEventListener("input", renderMemory);
  async function request(url, options = {}) {
    const response = await fetch(url, {cache: "no-store", credentials: "same-origin", redirect: "error", signal: AbortSignal.timeout(30000), ...options});
    const payload = await response.json();
    if (!response.ok) { const error = new Error(`Runtime request failed (HTTP ${response.status})`); error.payload = payload; throw error; }
    return payload;
  }
  const runtimeViews = ["daily-workers", "daily-jobs", "daily-memory", "daily-learning", "daily-computer", "daily-capabilities", "daily-receipts", "daily-observations", "daily-computer-evidence", "daily-memory-evidence", "daily-deployment"];
  function unavailable() {
    text("daily-connection", "Runtime unavailable");
    $("daily-connection").dataset.state = "unavailable";
    for (const id of runtimeViews) {
      text(id, "Unavailable · previous observations are stale. No current state verified.");
      $(id).dataset.state = "attention";
      memo.delete(id);
    }
    text("daily-updated", "Runtime snapshot stale · refresh to check");
    references = [];
    jobs = [];
    text("daily-memory-count", "Memory unavailable.");
    text("daily-jobs-summary", "");
    navState("projects", "", "");
    navState("memory", "", "");
    renderPaperclip(undefined, {failed: true});
    text("daily-memory-list", "Memory unavailable · previous references are stale.");
    memo.delete("daily-memory-list");
    $("daily-memory-search").disabled = true;
    $("daily-more-jobs").hidden = true;
    allowedOperations = [];
    $("daily-run").disabled = true;
    $("daily-operation").disabled = true;
  }
  async function refreshRuntime() {
    if (stateBusy) return;
    stateBusy = true;
    try {
      const data = await request("/api/runtime/state");
      if (data.schema !== "ghoti_deployed_runtime/1" || !Array.isArray(data.jobs) || !Number.isInteger(data.live_workers_running)) throw new Error("Unrecognized runtime state");
      // Only the verified deployed handler serves the root no-cache worker.
      if (!workerRegistered && "serviceWorker" in navigator && ["127.0.0.1", "localhost"].includes(location.hostname)) {
        workerRegistered = true;
        navigator.serviceWorker.register("/service-worker.js?v=daily-core").catch(() => {});
      }
      text("daily-connection", "Local connection");
      $("daily-connection").dataset.state = "connected";
      for (const id of runtimeViews) $(id).dataset.state = "";
      text("daily-updated", `Runtime checked ${new Date().toLocaleTimeString()}`);
      text("daily-workers", data.live_workers_running ? `${data.live_workers_running} local worker(s) running. Chat sessions are separate.` : "No local workers running. Chat sessions are shown separately below.");
      text("daily-deployment", json(data.deployment));
      const memory = data.memory || {};
      const memoryStatus = data.observations?.memory_status;
      text("daily-memory", memoryStatus === "MEMORY_STALE" ? "Some memory updates need attention. Saved work is not fully synchronized." :
        memoryStatus === "written" ? "Recent completion records were written to memory. Full vault synchronization is not verified." : "No recent completion writes observed. Startup references may still be available below.");
      $("daily-memory").dataset.state = memoryStatus === "MEMORY_STALE" ? "attention" : "";
      navState("memory", memoryStatus === "MEMORY_STALE" ? "Needs attention" : "", memoryStatus === "MEMORY_STALE" ? "attention" : "");
      renderPaperclip(data.integrations?.paperclip);
      references = Array.isArray(memory.startup_references) ? memory.startup_references : [];
      $("daily-memory-search").disabled = references.length === 0;
      renderMemory();
      text("daily-memory-evidence", json(memory.startup_references || []));
      text("daily-learning", data.learning?.status === "VERIFIED" ? "A learned procedure passed replay checks. It still needs permission for new actions." : "No verified learned procedure reported. Available tools still require their own checks and permissions.");
      const computer = data.computer_use;
      text("daily-computer", !computer || computer.status === "NOT_RUN" ? "No computer task has been recorded in this runtime." : `${outcome(computer)}. This is a saved observation, not live control.`);
      text("daily-computer-evidence", computer ? json(computer) : "Computer observations unavailable.");
      const observations = data.observations || {};
      text("daily-observations", `${value(observations.scope)} · ${value(observations.verification_scope)}`);
      list("daily-capabilities", observations.capabilities || [], "No recent tool use recorded. A conversation or local task can produce activity here.", cap => record(String(cap.capability_id).replace(/^(tool|skill|memory|verification)\//, "").replaceAll("_", " "),
        cap.status === "ACTIVE" ? "Last observed invocation completed. Task correctness is separate." : cap.status === "BROKEN" ? "Last invocation did not confirm success." : "Selected, but no invocation confirmed.", cap, stateOf(cap)));
      list("daily-receipts", observations.receipts || [], "No validated receipts reported.", receipt => record(`${receipt.task} · ${receipt.state}`, `${value(receipt.model)} / ${value(receipt.harness)} · memory ${value(receipt.memory_status)}`, receipt));
      jobs = data.jobs;
      renderJobs();
      const available = [...(data.safe_operations || []), ...(data.safe_workflows || [])].filter(op => Object.hasOwn(operations, op));
      if (json(available) !== json(allowedOperations)) {
        const selected = $("daily-operation").value;
        $("daily-operation").replaceChildren();
        for (const op of available) { const option = node("option", operations[op]); option.value = op; $("daily-operation").append(option); }
        if (available.includes(selected)) $("daily-operation").value = selected;
      }
      allowedOperations = available;
      $("daily-operation").disabled = taskBusy || !available.length;
      $("daily-run").disabled = taskBusy || !available.length;
    } catch (_) { unavailable(); }
    finally { stateBusy = false; }
  }
  async function submitChat() {
    const prompt = $("daily-prompt").value;
    const error = GhotiChat.promptError(prompt);
    text("daily-input-error", error);
    $("daily-input-error").hidden = !error;
    $("daily-prompt").setAttribute("aria-invalid", String(Boolean(error)));
    if (error) { $("daily-prompt").focus(); return; }
    if (await client.send(prompt)) { if ($("daily-prompt").value === prompt) $("daily-prompt").value = ""; }
  }
  $("daily-chat-form").addEventListener("submit", event => { event.preventDefault(); return submitChat(); });
  $("daily-prompt").addEventListener("keydown", event => {
    if (event.key !== "Enter" || !(event.ctrlKey || event.metaKey) || $("daily-send").disabled) return;
    event.preventDefault();
    return submitChat();
  });
  $("daily-prompt").addEventListener("input", () => {
    $("daily-input-error").hidden = true;
    $("daily-prompt").setAttribute("aria-invalid", "false");
  });
  $("daily-cancel").addEventListener("click", () => client.cancel());
  $("daily-new").addEventListener("click", async () => {
    if (client.submitting || !canStartNew(client.state)) return;
    client = newClient();
    $("daily-history-output").replaceChildren();
    $("daily-history-output").hidden = true;
    navigate("chat");
    await client.bootstrap();
  });
  $("daily-refresh").addEventListener("click", async () => {
    await Promise.all([refreshRuntime(), ["unavailable", "ready"].includes(client.state.phase) ? client.bootstrap() :
      client.state.phase === "disconnected" ? client.refreshSessions().catch(() => {}) : Promise.resolve()]);
  });
  $("daily-history-refresh").addEventListener("click", async () => {
    const button = $("daily-history-refresh");
    const owner = client;
    button.disabled = true;
    try { await owner.refreshSessions(); }
    catch (_) { if (client === owner) { text("daily-history-list", "Conversation history unavailable. Try Refresh when the runtime is connected."); memo.delete("daily-history-list"); } }
    finally { button.disabled = false; }
  });
  $("daily-task-form").addEventListener("submit", async event => {
    event.preventDefault();
    const operation = $("daily-operation").value;
    if (taskBusy || !allowedOperations.includes(operation)) return;
    const input = $("daily-task-text").value;
    if (!input.trim() || input.length > (operation === "coding_brief" ? 200 : 4000) ||
        new TextEncoder().encode(json({operation, text: input})).length > 6000) {
      text("daily-task-result", operation === "coding_brief" ? "Keep a coding brief query under 200 characters." : "This input is too large or empty. Shorten it before running the task.");
      return;
    }
    taskBusy = true;
    $("daily-run").disabled = true;
    $("daily-operation").disabled = true;
    text("daily-task-result", "Submitted once. Waiting for the bounded local task…");
    try {
      const result = await request("/api/runtime/run", {method: "POST", headers: {"Content-Type": "application/json"}, body: json({operation, text: input})});
      const row = record(operations[operation], outcome(result), result, stateOf(result));
      if (result.result?.summary || result.plan) {
        const content = node("div");
        showResult(content, result.result?.summary || result.plan);
        row.append(content);
      }
      $("daily-task-result").replaceChildren(row);
    } catch (error) {
      if (error.payload?.state || error.payload?.status) $("daily-task-result").replaceChildren(record(operations[operation], outcome(error.payload), error.payload, stateOf(error.payload)));
      else text("daily-task-result", "The task could not confirm a result. Check recent work before retrying; nothing will be resent automatically.");
    }
    finally { taskBusy = false; await refreshRuntime(); }
  });
  const active = () => ["creating", "submitting", "running", "permission", "approving", "syncing", "cancelling"].includes(client.state.phase);
  window.addEventListener("offline", () => { unavailable(); if (active()) client.disconnect("Browser is offline"); });
  window.addEventListener("online", () => refreshRuntime());
  window.addEventListener("popstate", () => navigate(hashView() || "chat", {remember: false}));
  window.addEventListener("pagehide", () => { if (active()) client.disconnect("Page disconnected", {keepalive: true}); });

  async function pollChat() { await client.poll(); attention(); setTimeout(pollChat, client.state.hasMore ? 30 : 1000); }
  async function pollRuntime() { await refreshRuntime(); setTimeout(pollRuntime, 10000); }
  if (labels[hashView()] && hashView() !== "chat") navigate(hashView(), {remember: false});
  client.bootstrap();
  pollChat();
  pollRuntime();
})();
