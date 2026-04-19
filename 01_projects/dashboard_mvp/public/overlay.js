"use strict";

const DASHBOARD_URL = "http://127.0.0.1:3210";
const POLL_INTERVAL_MS = 3000;
const FRAME_REFRESH_MS = 2000;

let isGhotiActive = false;
let isCapturing = false;
let captureSessionId = null;
let frameRefreshTimer = null;

const activeDot = document.getElementById("active-dot");
const activeLabel = document.getElementById("active-label");
const captureDot = document.getElementById("capture-dot");
const captureLabel = document.getElementById("capture-label");
const framePreviewRow = document.getElementById("frame-preview-row");
const latestFrameImg = document.getElementById("latest-frame-img");
const frameTimestamp = document.getElementById("frame-timestamp");
const feedbackEl = document.getElementById("overlay-feedback");
const toggleActiveBtn = document.getElementById("toggle-active-btn");
const toggleCaptureBtn = document.getElementById("toggle-capture-btn");
const refreshBtn = document.getElementById("refresh-btn");

function showFeedback(msg, isError) {
  feedbackEl.textContent = msg;
  feedbackEl.className = "overlay-feedback" + (isError ? " is-error" : "");
  feedbackEl.hidden = false;
  clearTimeout(showFeedback._timer);
  showFeedback._timer = setTimeout(() => { feedbackEl.hidden = true; }, 4000);
}

function formatTime(utcString) {
  if (!utcString) return "";
  try { return new Date(utcString).toLocaleTimeString(); }
  catch { return utcString; }
}

function setDot(dotEl, state) {
  dotEl.className = "status-dot";
  if (state === "on") dotEl.classList.add("dot-on");
  else if (state === "warn") dotEl.classList.add("dot-warn");
  else dotEl.classList.add("dot-off");
}

function updateActiveButton() {
  toggleActiveBtn.textContent = isGhotiActive ? "Stop Ghoti" : "Start Ghoti";
  toggleActiveBtn.classList.toggle("is-stop", isGhotiActive);
}

function updateCaptureButton() {
  toggleCaptureBtn.disabled = !isGhotiActive;
  toggleCaptureBtn.textContent = isCapturing ? "Stop Watching" : "Start Watching";
  toggleCaptureBtn.classList.toggle("is-stop", isCapturing);
}

function applyActiveState(state) {
  isGhotiActive = Boolean(state?.active);
  if (isGhotiActive) {
    setDot(activeDot, "on");
    activeLabel.textContent = "Active — screen view on";
  } else {
    setDot(activeDot, "off");
    activeLabel.textContent = "Idle";
  }
  updateActiveButton();
  updateCaptureButton();
}

function applyCaptureState(cs) {
  isCapturing = Boolean(cs?.capturing);
  captureSessionId = cs?.session_id || null;

  if (cs?.error && !isCapturing) {
    setDot(captureDot, "warn");
    captureLabel.textContent = "Capture error";
  } else if (isCapturing) {
    setDot(captureDot, "on");
    const count = cs.frame_count || 0;
    captureLabel.textContent = `Watching — ${count} frame${count !== 1 ? "s" : ""}`;
  } else {
    setDot(captureDot, "off");
    captureLabel.textContent = "Not watching";
  }

  const hasFrames = (cs?.frame_count || 0) > 0;
  framePreviewRow.hidden = !hasFrames;
  if (hasFrames) {
    frameTimestamp.textContent = cs.latest_frame_utc ? `Last: ${formatTime(cs.latest_frame_utc)}` : "";
  }

  updateCaptureButton();
  manageFrameRefresh();
}

function buildLatestFrameUrl(sessionId) {
  const base = sessionId
    ? `/api/ghoti/active/latest-frame?session_id=${encodeURIComponent(sessionId)}`
    : "/api/ghoti/active/latest-frame";
  return base + (base.includes("?") ? "&" : "?") + "t=" + Date.now();
}

function refreshLatestFrame() {
  if (latestFrameImg && !framePreviewRow.hidden) {
    latestFrameImg.src = buildLatestFrameUrl(captureSessionId);
  }
}

function manageFrameRefresh() {
  clearInterval(frameRefreshTimer);
  if (isCapturing) {
    frameRefreshTimer = setInterval(refreshLatestFrame, FRAME_REFRESH_MS);
    refreshLatestFrame();
  }
}

async function fetchState() {
  try {
    const [activeRes, captureRes] = await Promise.all([
      fetch(`${DASHBOARD_URL}/api/ghoti/active-state`),
      fetch(`${DASHBOARD_URL}/api/ghoti/active/capture-state`),
    ]);
    const [activeData, captureData] = await Promise.all([
      activeRes.json(),
      captureRes.json(),
    ]);
    applyActiveState(activeData.state);
    applyCaptureState(captureData.captureState);
  } catch (err) {
    setDot(activeDot, "warn");
    activeLabel.textContent = "Dashboard unreachable";
    setDot(captureDot, "off");
    captureLabel.textContent = "—";
  }
}

async function postAction(path) {
  const res = await fetch(`${DASHBOARD_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  return res.json();
}

toggleActiveBtn.addEventListener("click", async () => {
  toggleActiveBtn.disabled = true;
  try {
    const route = isGhotiActive ? "/api/ghoti/active/stop" : "/api/ghoti/active/start";
    const data = await postAction(route);
    if (!data.ok) throw new Error(data.error || "Action failed");
    showFeedback(isGhotiActive ? "Ghoti stopped." : "Ghoti started.", false);
    await fetchState();
  } catch (err) {
    showFeedback(err.message, true);
  } finally {
    toggleActiveBtn.disabled = false;
  }
});

toggleCaptureBtn.addEventListener("click", async () => {
  toggleCaptureBtn.disabled = true;
  try {
    const route = isCapturing ? "/api/ghoti/active/capture/stop" : "/api/ghoti/active/capture/start";
    const data = await postAction(route);
    if (!data.ok) throw new Error(data.error || "Action failed");
    showFeedback(isCapturing ? "Capture stopped." : "Capture started.", false);
    await fetchState();
  } catch (err) {
    showFeedback(err.message, true);
  } finally {
    toggleCaptureBtn.disabled = false;
  }
});

refreshBtn.addEventListener("click", async () => {
  refreshBtn.disabled = true;
  await fetchState();
  refreshBtn.disabled = false;
});

fetchState();
setInterval(fetchState, POLL_INTERVAL_MS);
