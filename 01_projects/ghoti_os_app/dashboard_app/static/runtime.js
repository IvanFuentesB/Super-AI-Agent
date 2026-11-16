"use strict";
// This panel reads actual durable jobs; it never infers activity from capacity cards.
(() => {
  let polling = false;
  const text = (id, value) => { document.getElementById(id).textContent = value; };
  function rows(id, entries, empty) {
    const target = document.getElementById(id);
    target.replaceChildren();
    for (const [heading, description] of entries) {
      const row = document.createElement("article");
      row.className = "row";
      const title = document.createElement("strong");
      title.textContent = heading;
      const detail = document.createElement("p");
      detail.textContent = description;
      row.append(title, detail);
      target.append(row);
    }
    if (!entries.length) target.textContent = empty;
  }
  async function refresh() {
    if (polling) return;
    polling = true;
    try {
      const response = await fetch("/api/runtime/state", { cache: "no-store" });
      if (!response.ok) throw new Error("Runtime state unavailable");
      const data = await response.json();
      const deploy = data.deployment;
      text("last-updated", `Live runtime state · ${new Date().toLocaleTimeString()}`);
      text("global-agent-state", data.live_workers_running ? "WORKING" : "IDLE");
      text("runtime-health", `${deploy.status} · release ${deploy.release_commit || "not deployed"} · ${data.live_workers_running} active worker(s)`);
      text("runtime-memory", `${data.memory.obsidian_reference_count} Obsidian startup references · ${data.memory.native_run_count} native run records`);
      text("runtime-learning", `Procedural skill: ${data.learning.status}${data.learning.active_version ? " · version " + data.learning.active_version : ""} · replay verification grants no new permissions`);
      const computer = data.computer_use;
      text("runtime-computer", computer && typeof computer === "object" ?
        `Recorded task ${computer.task || "none"} · ${computer.status} · ${computer.mode || "not selected"} · target ${computer.target?.document || "none"} · observation ${computer.observation?.status || computer.observation || "not started"} · action ${computer.last_action || "none"} · verification ${computer.verification || "UNVERIFIED"} · memory ${computer.memory_status || "MEMORY_STALE"} · trajectory ${computer.trajectory || "none"} · skill ${computer.skill || "none"} · invoked ${(computer.capabilities_invoked || []).join(", ") || "none"} · CUA ${computer.cua_health?.status || "not probed"}` :
        "Computer observation unavailable; no control is implied.");
      const observed = data.observations;
      text("runtime-observations", `${observed.scope} · ${observed.record_count} validated receipts · ${observed.active_count} shown ACTIVE · memory ${observed.memory_status} · ${observed.invalid_records} invalid records · pending completion ${observed.pending_completion ? "yes" : "no"}${observed.capabilities_truncated ? " · capability list truncated" : ""} · ${observed.verification_scope}`);
      rows("runtime-capabilities", observed.capabilities.map(capability => [
        `${capability.capability_id} — ${capability.status}`,
        `${capability.usage_count} successful / ${capability.attempt_count} attempted · last used ${capability.last_used || "never invoked"} · task ${capability.last_task} · ${capability.model} / ${capability.harness} · ${capability.impact}`,
      ]), "No observed capability invocations in this window.");
      rows("runtime-receipts", observed.receipts.map(receipt => [
        `${receipt.task} — ${receipt.state} · ${receipt.task_id}`,
        `${receipt.model} / ${receipt.harness} · memory ${receipt.memory_status} · cost ${receipt.cost} · successful: ${receipt.usage_counted.join(", ") || "none"} · selected but not invoked: ${receipt.selected_not_invoked.join(", ") || "none"} · source ${receipt.source}`,
      ]), "No validated native receipts yet.");
      const jobs = document.getElementById("runtime-jobs");
      jobs.replaceChildren();
      for (const job of data.jobs) {
        const row = document.createElement("article");
        row.className = "row";
        const title = document.createElement("strong");
        title.textContent = `${job.title} — ${job.state}`;
        const detail = document.createElement("p");
        detail.textContent = `${job.worker?.role || "unassigned"} · ${job.route?.selected?.model_id || "no eligible model"} · ${job.verification_scope || "not verified"} · ${job.memory_event_id ? "memory recorded" : "no completion memory"}${job.collaboration_id ? " · " + job.collaboration_id : ""}`;
        row.append(title, detail);
        jobs.append(row);
      }
      if (!data.jobs.length) jobs.textContent = "No recorded jobs yet.";
    } catch (error) {
      text("runtime-health", error.message);
      text("runtime-computer", "STALE: computer task observation unavailable; no current state verified.");
      text("runtime-observations", "MEMORY_STALE: native observations unavailable; no refreshed status is verified.");
      rows("runtime-capabilities", [], "Capability observations unavailable.");
      rows("runtime-receipts", [], "Receipt observations unavailable.");
    } finally { polling = false; }
  }
  document.addEventListener("ghoti-runtime-ready", () => {
    document.getElementById("integrated-runtime").hidden = false;
    refresh();
    setInterval(refresh, 3000);
  }, { once: true });
  document.getElementById("runtime-task-form").addEventListener("submit", async event => {
    event.preventDefault();
    const button = event.target.querySelector("button");
    button.disabled = true;
    text("runtime-task-result", "Executing a bounded local task...");
    try {
      const response = await fetch("/api/runtime/run", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ operation: document.getElementById("runtime-operation").value,
          text: document.getElementById("runtime-text").value }) });
      const result = await response.json();
      text("runtime-task-result", JSON.stringify(result, null, 2));
    } catch (error) {
      text("runtime-task-result", `Request failed: ${error.message}. Check persisted state before retrying.`);
    } finally { button.disabled = false; await refresh(); }
  });
})();
