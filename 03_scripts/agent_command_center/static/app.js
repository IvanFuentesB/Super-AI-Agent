"use strict";

const summary = document.querySelector("#summary");
const queue = document.querySelector("#queue");
const agents = document.querySelector("#agents");
const gates = document.querySelector("#gates");
const paperclip = document.querySelector("#paperclip");
const scenarioMode = document.querySelector("#scenario-mode");

function textNode(tag, value, className) {
  const element = document.createElement(tag);
  element.textContent = value;
  if (className) element.className = className;
  return element;
}

async function getJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  return response.json();
}

function renderSummary(status) {
  summary.replaceChildren();
  const values = [
    ["Memory sources", `${status.memory.verified_sources}/${status.memory.indexed_sources}`],
    ["Scenarios", String(status.available_scenarios.length)],
    ["Agents", String(status.agents.length)],
    ["Paperclip", status.agent_systems.paperclip.mode],
  ];
  values.forEach(([label, value]) => {
    const item = document.createElement("div");
    item.append(textNode("span", label), textNode("strong", value));
    summary.append(item);
  });
}

function renderAgents(arena) {
  agents.replaceChildren();
  arena.agents.forEach((agent) => {
    const card = document.createElement("article");
    card.append(textNode("strong", agent.name), textNode("span", agent.role), textNode("em", agent.state));
    agents.append(card);
  });
}

function renderQueue(plan) {
  queue.replaceChildren();
  scenarioMode.textContent = `${plan.business_lane} / simulation`;
  plan.tasks.forEach((task) => {
    const row = document.createElement("article");
    row.append(textNode("strong", task.id), textNode("span", task.description), textNode("em", task.role));
    queue.append(row);
  });
}

function renderGates(plan) {
  gates.replaceChildren();
  plan.blocked_actions.slice(0, 10).forEach((action) => gates.append(textNode("span", action)));
}

function renderPaperclip(preview) {
  paperclip.replaceChildren();
  paperclip.append(textNode("strong", preview.company_name));
  paperclip.append(textNode("span", preview.note));
  preview.departments.forEach((department) => {
    paperclip.append(textNode("em", `${department.role}: ${department.work_item_ids.length} work item(s)`));
  });
}

async function loadScenario(id) {
  const [plan, arena, preview] = await Promise.all([
    getJson(`/api/scenario/${id}`),
    getJson(`/api/arena/${id}`),
    getJson(`/api/paperclip/${id}`),
  ]);
  renderQueue(plan);
  renderAgents(arena);
  renderGates(plan);
  renderPaperclip(preview);
}

document.querySelectorAll("[data-scenario]").forEach((button) => {
  button.addEventListener("click", () => loadScenario(button.dataset.scenario));
});

Promise.all([getJson("/api/status"), loadScenario("content-revenue-research")])
  .then(([status]) => renderSummary(status))
  .catch(() => {
    summary.replaceChildren(textNode("strong", "Command center data unavailable"));
  });
