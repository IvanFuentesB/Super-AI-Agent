"use strict";

/*
 * Ghoti Operator Dashboard - front-end renderer (N+6.18A).
 *
 * Fetches the read-only GET /api/status endpoint on the same local origin and
 * renders it into cards using DOM APIs only (textContent, never innerHTML with
 * data). It performs no external requests, opens no websocket, and uses no dynamic
 * code execution. There are no buttons that start or stop services and no forms that
 * submit actions; the only control is a Refresh button that re-reads the status.
 */
(function () {
  var STATUS_URL = "/api/status";

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) { node.className = className; }
    if (text !== undefined && text !== null) { node.textContent = String(text); }
    return node;
  }

  function row(label, value) {
    var r = el("div", "row");
    r.appendChild(el("span", "k", label));
    var v = el("span", "v");
    if (value === true) {
      v.textContent = "yes";
      v.classList.add("ok");
    } else if (value === false) {
      v.textContent = "no";
      v.classList.add("off");
    } else if (value === null || value === undefined || value === "") {
      v.textContent = "—";
      v.classList.add("muted");
    } else {
      v.textContent = String(value);
    }
    r.appendChild(v);
    return r;
  }

  function card(title, rows) {
    var c = el("section", "card");
    c.appendChild(el("h2", null, title));
    (rows || []).forEach(function (rw) { if (rw) { c.appendChild(rw); } });
    return c;
  }

  function codeBlock(text) {
    var pre = el("pre", "code");
    pre.textContent = String(text || "—");
    return pre;
  }

  function chipList(items) {
    var wrap = el("div", "chips");
    (items || []).forEach(function (item) {
      wrap.appendChild(el("span", "chip", item));
    });
    return wrap;
  }

  function render(data) {
    var cards = document.getElementById("cards");
    cards.textContent = "";

    var milestone = document.getElementById("milestone");
    if (milestone && data.milestone) { milestone.textContent = data.milestone; }

    var rh = data.runtime_health || {};
    cards.appendChild(card("Runtime health", [
      row("overall ok", !!rh.ok),
      row("source", rh.source),
      row("origin/main", data.origin_main_short),
      row("branch", rh.current_branch),
      row("commits ahead of main", rh.commits_ahead_of_main),
      row("n6 test methods", rh.n6_test_count),
      row("status bridge present", rh.status_bridge_ok),
      row("status brain present", rh.status_brain_ok)
    ]));

    var pr = data.python_resolver || {};
    cards.appendChild(card("Python resolver", [
      row("ok", !!pr.ok),
      row("executable", pr.executable),
      row("source", pr.source),
      row("resolver script present", pr.resolver_script_present)
    ]));

    var sb = data.status_bridge || {};
    var sbrain = data.status_brain || {};
    cards.appendChild(card("Status bridge & brain", [
      row("status bridge available", sb.available),
      row("status bridge source", sb.source),
      row("status brain available", sbrain.available)
    ]));

    var tg = data.telegram_status_readiness || {};
    cards.appendChild(card("Telegram (status-only)", [
      row("bot script present", tg.bot_script_present),
      row("runtime status", tg.runtime_status),
      row("mode", tg.mode),
      row("/run enabled", tg.run_commands_enabled),
      row("/send enabled", tg.send_commands_enabled),
      row("live control enabled", tg.live_control_enabled)
    ]));

    var hs = data.hermes_session || {};
    var hCard = card("WSL Hermes session", [
      row("wsl available", hs.wsl_available),
      row("distro", hs.distro),
      row("session id", hs.session_id),
      row("repo mount", hs.repo_mount),
      row("hermes is WSL-only now", hs.hermes_wsl_only)
    ]);
    hCard.appendChild(el("p", "muted-note", "Resume command (preview only — this page runs nothing):"));
    hCard.appendChild(codeBlock(hs.command_preview));
    cards.appendChild(hCard);

    var og = data.ollama_gemma || {};
    cards.appendChild(card("Ollama / Gemma", [
      row("ollama available", og.ollama_available),
      row("gemma available", og.gemma_available),
      row("probe ran", og.checked)
    ]));

    var cu = data.computer_use_sandbox || {};
    cards.appendChild(card("Computer-use sandbox", [
      row("available", cu.available),
      row("mode", cu.mode || "dry_run_only"),
      row("browser launched", cu.browser_launched),
      row("dom action performed", cu.dom_action_performed),
      row("os input used", cu.os_input_used),
      row("live website", cu.live_website)
    ]));

    var dc = data.disabled_capabilities || {};
    var dCard = card("Disabled capabilities", [
      row("dashboard flags all false", dc.dashboard_flags_all_false),
      row("only status-commands flag enabled", dc.only_status_commands_flag_enabled)
    ]);
    dCard.appendChild(el("p", "muted-note", "These stay disabled and out of scope:"));
    dCard.appendChild(chipList(dc.capabilities_disabled));
    cards.appendChild(dCard);

    var nextCard = card("Next recommended action", []);
    nextCard.appendChild(el("p", "next", data.next_recommended_action));
    cards.appendChild(nextCard);

    var updated = document.getElementById("updated");
    updated.textContent = "Updated " + (data.generated_utc || "") +
      " · milestone " + (data.milestone || "");
  }

  function showError(message) {
    var cards = document.getElementById("cards");
    cards.textContent = "";
    cards.appendChild(card("Status unavailable", [row("error", message)]));
    var updated = document.getElementById("updated");
    updated.textContent = "Could not load /api/status.";
  }

  function load() {
    var updated = document.getElementById("updated");
    updated.textContent = "Loading status…";
    fetch(STATUS_URL, { headers: { "Accept": "application/json" }, cache: "no-store" })
      .then(function (resp) {
        if (!resp.ok) { throw new Error("HTTP " + resp.status); }
        return resp.json();
      })
      .then(render)
      .catch(function (err) {
        showError(err && err.message ? err.message : "request failed");
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("refresh");
    if (btn) { btn.addEventListener("click", load); }
    load();
  });
})();
