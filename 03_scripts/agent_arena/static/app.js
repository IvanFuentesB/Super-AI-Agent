"use strict";

/*
 * Ghoti Agent Arena - front-end renderer (N+6.21A).
 *
 * Fetches the read-only GET /api/simulation endpoint on the same local origin and
 * renders agent cards, a queue/timeline, totals, handoff files, and a replay trace
 * using DOM APIs only. It performs no external request, opens no websocket, uses no
 * dynamic code execution, and has no button that launches or controls anything - the
 * only control is Refresh, which re-reads the simulation.
 */
(function () {
  var SIM_URL = "/api/simulation";

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

  function render(data) {
    var milestone = document.getElementById("milestone");
    if (milestone) { milestone.textContent = data.milestone || ""; }

    var agents = document.getElementById("agents");
    agents.textContent = "";
    (data.agents || []).forEach(function (a) { agents.appendChild(agentCard(a)); });

    var panels = document.getElementById("panels");
    panels.textContent = "";

    var totals = data.totals || {};
    panels.appendChild(panel("Totals (estimates)", function (p) {
      p.appendChild(row("agents", totals.agent_count));
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

    var updated = document.getElementById("updated");
    updated.textContent = "Simulation served " + (data.served_utc || "") +
      " · live execution: " + (data.live_execution ? "on" : "off");
  }

  function showError(message) {
    var agents = document.getElementById("agents");
    agents.textContent = "";
    var c = el("section", "card");
    c.appendChild(el("h2", null, "Simulation unavailable"));
    c.appendChild(el("p", "muted-note", message));
    agents.appendChild(c);
    document.getElementById("panels").textContent = "";
    document.getElementById("updated").textContent = "Could not load /api/simulation.";
  }

  function load() {
    document.getElementById("updated").textContent = "Loading simulation…";
    fetch(SIM_URL, { headers: { "Accept": "application/json" }, cache: "no-store" })
      .then(function (resp) {
        if (!resp.ok) { throw new Error("HTTP " + resp.status); }
        return resp.json();
      })
      .then(render)
      .catch(function (err) { showError(err && err.message ? err.message : "request failed"); });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("refresh");
    if (btn) { btn.addEventListener("click", load); }
    load();
  });
})();
