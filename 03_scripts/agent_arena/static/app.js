"use strict";

/*
 * Ghoti Agent Arena - front-end renderer (N+6.21A; trace view added N+6.23A).
 *
 * Fetches read-only GET JSON on the same local origin and renders agent cards, a
 * queue/timeline, totals, handoff files, and a replay trace using DOM APIs only.
 * Two views share the same renderer:
 *   - "Sample simulation" reads /api/simulation (illustrative data).
 *   - "Local trace" reads /api/trace, which a file-only loader builds from existing
 *     local report files, and shows status cards for the recent project state.
 * It performs no external request, opens no live socket, uses no dynamic code
 * execution, and has no button that launches or controls anything - the controls only
 * re-read JSON and switch which read-only endpoint is shown.
 */
(function () {
  var SIM_URL = "/api/simulation";
  var TRACE_URL = "/api/trace";
  var currentView = "simulation";

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) { node.className = className; }
    if (text !== undefined && text !== null) { node.textContent = String(text); }
    return node;
  }

  function stateBadge(state) {
    var value = state || "idle";
    return el("span", "state state-" + value, value);
  }

  function row(label, value) {
    var r = el("div", "row");
    r.appendChild(el("span", "k", label));
    var v = el("span", "v");
    if (value === null || value === undefined || value === "") {
      v.textContent = "—";
      v.classList.add("muted");
    } else {
      v.textContent = String(value);
    }
    r.appendChild(v);
    return r;
  }

  function codeLine(text) {
    var pre = el("pre", "code");
    pre.textContent = String(text || "—");
    return pre;
  }

  function agentCard(a) {
    var c = el("section", "card agent");
    var head = el("div", "agent-head");
    head.appendChild(el("h3", null, a.name || a.id || "agent"));
    head.appendChild(stateBadge(a.state));
    c.appendChild(head);
    c.appendChild(el("p", "role", a.role || ""));
    c.appendChild(row("task", a.current_task));
    c.appendChild(row("branch", a.branch));
    c.appendChild(row("worktree", a.worktree));
    c.appendChild(row("token estimate", a.token_estimate));
    c.appendChild(row("cost estimate (USD)", a.cost_estimate_usd));
    if (a.note) { c.appendChild(el("p", "muted-note", a.note)); }
    return c;
  }

  function panel(title, build) {
    var p = el("section", "card panel");
    p.appendChild(el("h2", null, title));
    build(p);
    return p;
  }

  function statusCard(label, value, tone, sub) {
    var c = el("div", "status-card" + (tone ? " " + tone : ""));
    c.appendChild(el("div", "sc-label", label));
    var v = el("div", "sc-value");
    v.textContent = (value === null || value === undefined || value === "") ? "—" : String(value);
    c.appendChild(v);
    if (sub) { c.appendChild(el("div", "sc-sub", sub)); }
    return c;
  }

  function renderStatus(status) {
    var host = document.getElementById("status-cards");
    if (!host) { return; }
    host.textContent = "";
    if (!status || currentView !== "trace") {
      host.hidden = true;
      return;
    }
    host.hidden = false;
    host.appendChild(statusCard("Latest main commit (recorded)", status.latest_main_commit_recorded));
    host.appendChild(statusCard("Latest Claude branch", status.latest_claude_branch, null,
      status.latest_claude_milestone || ""));
    host.appendChild(statusCard("Latest Codex audit", status.latest_codex_audit));
    host.appendChild(statusCard("Memory vault", status.memory_vault_present ? "present" : "missing",
      status.memory_vault_present ? "sc-ok" : "sc-warn"));
    host.appendChild(statusCard("Tool intake", status.tool_intake_present ? "present" : "missing",
      status.tool_intake_present ? "sc-ok" : "sc-warn"));
    host.appendChild(statusCard("Reports parsed", status.report_count));
  }

  function render(data) {
    var milestone = document.getElementById("milestone");
    if (milestone) { milestone.textContent = data.milestone || ""; }

    renderStatus(data.status);

    var agents = document.getElementById("agents");
    agents.textContent = "";
    (data.agents || []).forEach(function (a) { agents.appendChild(agentCard(a)); });

    var panels = document.getElementById("panels");
    panels.textContent = "";

    var totals = data.totals || {};
    panels.appendChild(panel("Totals (estimates)", function (p) {
      p.appendChild(row("agents", totals.agent_count));
      if (totals.report_count !== undefined) { p.appendChild(row("reports", totals.report_count)); }
      p.appendChild(row("token estimate", totals.token_estimate));
      p.appendChild(row("cost estimate (USD)", totals.cost_estimate_usd));
      if (totals.estimate_basis) { p.appendChild(el("p", "muted-note", totals.estimate_basis)); }
    }));

    panels.appendChild(panel("Queue / timeline", function (p) {
      (data.queue || []).forEach(function (q) {
        var r = el("div", "timeline-row");
        r.appendChild(stateBadge(q.state));
        r.appendChild(el("span", "tl-title", (q.title || q.task_id || "") + " · " + (q.assigned_agent || "")));
        p.appendChild(r);
      });
      (data.timeline || []).forEach(function (ev) {
        p.appendChild(el("p", "tl-event",
          (ev.t || "") + "  " + (ev.agent || "") + ": " + (ev.from_state || "") +
          " → " + (ev.to_state || "") + (ev.note ? ("  (" + ev.note + ")") : "")));
      });
    }));

    panels.appendChild(panel("Handoff files", function (p) {
      (data.handoffs || []).forEach(function (h) {
        p.appendChild(el("p", "handoff", (h.from || "") + " → " + (h.to || "") +
          (h.kind ? ("  [" + h.kind + "]") : "")));
        p.appendChild(codeLine(h.file));
      });
    }));

    panels.appendChild(panel("Trace / replay", function (p) {
      (data.traces || []).forEach(function (tr) {
        p.appendChild(el("p", "trace", "#" + (tr.step !== undefined ? tr.step : "") + " " +
          (tr.agent || "") + " - " + (tr.action || "") + (tr.note ? (": " + tr.note) : "")));
      });
    }));

    if (data.reports && data.reports.length) {
      panels.appendChild(panel("Reports (local)", function (p) {
        data.reports.forEach(function (r) {
          p.appendChild(el("p", "trace", (r.milestone || "") + "  " + (r.agent || "") +
            "  [" + (r.verdict || "") + "]  " + (r.title || "")));
          if (r.branch) { p.appendChild(codeLine(r.branch)); }
        });
      }));
    }

    var updated = document.getElementById("updated");
    if (currentView === "trace") {
      updated.textContent = "Local trace served " + (data.served_utc || "") +
        " · source: " + (data.source || "local report files") +
        " · live execution: " + (data.live_execution ? "on" : "off");
    } else {
      updated.textContent = "Simulation served " + (data.served_utc || "") +
        " · live execution: " + (data.live_execution ? "on" : "off");
    }
  }

  function showError(message) {
    var agents = document.getElementById("agents");
    agents.textContent = "";
    var c = el("section", "card");
    c.appendChild(el("h2", null, currentView === "trace" ? "Local trace unavailable" : "Simulation unavailable"));
    c.appendChild(el("p", "muted-note", message));
    agents.appendChild(c);
    document.getElementById("panels").textContent = "";
    var sc = document.getElementById("status-cards");
    if (sc) { sc.textContent = ""; sc.hidden = true; }
    document.getElementById("updated").textContent =
      "Could not load " + (currentView === "trace" ? TRACE_URL : SIM_URL) + ".";
  }

  function load() {
    var url = (currentView === "trace") ? TRACE_URL : SIM_URL;
    document.getElementById("updated").textContent =
      (currentView === "trace") ? "Loading local trace…" : "Loading simulation…";
    fetch(url, { headers: { "Accept": "application/json" }, cache: "no-store" })
      .then(function (resp) {
        if (!resp.ok) { throw new Error("HTTP " + resp.status); }
        return resp.json();
      })
      .then(render)
      .catch(function (err) { showError(err && err.message ? err.message : "request failed"); });
  }

  function setView(view) {
    currentView = (view === "trace") ? "trace" : "simulation";
    var simBtn = document.getElementById("view-sim");
    var traceBtn = document.getElementById("view-trace");
    if (simBtn) { simBtn.classList.toggle("is-active", currentView === "simulation"); }
    if (traceBtn) { traceBtn.classList.toggle("is-active", currentView === "trace"); }
    var note = document.getElementById("view-note");
    if (note) {
      note.textContent = (currentView === "trace")
        ? "Local trace - built read-only from existing report files."
        : "Sample simulation - illustrative data.";
    }
    var sc = document.getElementById("status-cards");
    if (sc && currentView !== "trace") { sc.textContent = ""; sc.hidden = true; }
    load();
  }

  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("refresh");
    if (btn) { btn.addEventListener("click", load); }
    var simBtn = document.getElementById("view-sim");
    if (simBtn) { simBtn.addEventListener("click", function () { setView("simulation"); }); }
    var traceBtn = document.getElementById("view-trace");
    if (traceBtn) { traceBtn.addEventListener("click", function () { setView("trace"); }); }
    load();
  });
})();
