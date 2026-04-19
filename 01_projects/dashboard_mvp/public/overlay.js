"use strict";

const DASHBOARD_URL = "http://127.0.0.1:3210";
const POLL_INTERVAL_MS = 2000;
const FRAME_REFRESH_MS = 2000;

let isGhotiActive = false;
let isCapturing = false;
let isMuted = true;
let captureSessionId = null;
let frameRefreshTimer = null;

const activeDot = document.getElementById("active-dot");
const activeLabel = document.getElementById("active-label");
const captureDot = document.getElementById("capture-dot");
const captureLabel = document.getElementById("capture-label");
const voiceDot = document.getElementById("voice-dot");
const voiceLabel = document.getElementById("voice-label");
const brainDot = document.getElementById("brain-dot");
const brainLabel = document.getElementById("brain-label");
const operatorDot = document.getElementById("operator-dot");
const operatorLabel = document.getElementById("operator-label");
const ytDot = document.getElementById("yt-dot");
const ytLabel = document.getElementById("yt-label");
const framePreviewRow = document.getElementById("frame-preview-row");
const latestFrameImg = document.getElementById("latest-frame-img");
const frameTimestamp = document.getElementById("frame-timestamp");
const feedbackEl = document.getElementById("overlay-feedback");
const toggleActiveBtn = document.getElementById("toggle-active-btn");
const toggleCaptureBtn = document.getElementById("toggle-capture-btn");
const toggleMuteBtn = document.getElementById("toggle-mute-btn");
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

function updateMuteButton() {
  toggleMuteBtn.textContent = isMuted ? "Unmute" : "Mute";
  toggleMuteBtn.classList.toggle("is-stop", !isMuted);
}

function applyActiveState(state) {
  isGhotiActive = Boolean(state?.active);
  if (isGhotiActive) {
    setDot(activeDot, "on");
    activeLabel.textContent = "Active";
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

function applyVoiceState(v) {
  if (!v) { voiceLabel.textContent = "Voice: unavailable"; setDot(voiceDot, "warn"); return; }
  isMuted = Boolean(v.muted);
  const muteText = v.muted ? "Muted" : "Unmuted";
  const listenText = v.listening ? "Listening" : "Not listening";
  voiceLabel.textContent = `Voice: ${muteText} / ${listenText} (placeholder)`;
  setDot(voiceDot, v.muted ? "off" : "warn");
  updateMuteButton();
}

function applyBrainState(payload) {
  if (!payload?.ok) { brainLabel.textContent = "Brain: unavailable"; setDot(brainDot, "warn"); return; }
  const s = payload.summary || {};
  const provider = s.activeProvider || payload.activeProvider || "unknown";
  const model = s.activeModel || payload.activeModel || "none";
  const ready = s.inferenceReady || payload.inferenceReady;
  brainLabel.textContent = `Brain: ${provider} / ${model}`;
  setDot(brainDot, ready ? "on" : "off");
}

function applyOperatorState(payload) {
  if (!payload?.ok) { operatorLabel.textContent = "Operator: unavailable"; setDot(operatorDot, "warn"); return; }
  const op = payload.operator || {};
  const desktop = op.desktop_actions_available ? "Desktop: available" : "Desktop: unavailable";
  const browser = op.browser_actions_available ? "Browser: available" : "Browser: not integrated";
  operatorLabel.textContent = `${desktop} | ${browser}`;
  setDot(operatorDot, op.desktop_actions_available ? "warn" : "off");
}

function applyYoutubeState(payload) {
  if (!payload?.ok) { ytLabel.textContent = "YouTube follower: unavailable"; setDot(ytDot, "warn"); return; }
  const count = payload.task_count || 0;
  ytLabel.textContent = `YouTube follower: scaffold only (${count} task${count !== 1 ? "s" : ""})`;
  setDot(ytDot, "off");
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

async function safeFetch(url) {
  try {
    const res = await fetch(`${DASHBOARD_URL}${url}`);
    if (!res.ok) return null;
    return res.json();
  } catch { return null; }
}

async function fetchState() {
  const [activeData, captureData, voiceData, operatorData, brainData, ytData] = await Promise.all([
    safeFetch("/api/ghoti/active-state"),
    safeFetch("/api/ghoti/active/capture-state"),
    safeFetch("/api/ghoti/voice/state"),
    safeFetch("/api/ghoti/operator/status"),
    safeFetch("/api/ghoti/brain/status"),
    safeFetch("/api/ghoti/youtube-follower/status"),
  ]);

  if (activeData) applyActiveState(activeData.state);
  else { setDot(activeDot, "warn"); activeLabel.textContent = "Dashboard unreachable"; }

  if (captureData) applyCaptureState(captureData.captureState);
  else { setDot(captureDot, "off"); captureLabel.textContent = "—"; }

  applyVoiceState(voiceData?.voice || null);
  applyBrainState(brainData);
  applyOperatorState(operatorData);
  applyYoutubeState(ytData);
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

toggleMuteBtn.addEventListener("click", async () => {
  toggleMuteBtn.disabled = true;
  try {
    const route = isMuted ? "/api/ghoti/voice/unmute" : "/api/ghoti/voice/mute";
    const data = await postAction(route);
    if (!data.ok) throw new Error(data.error || "Action failed");
    applyVoiceState(data.voice);
    showFeedback(isMuted ? "Voice unmuted." : "Voice muted.", false);
  } catch (err) {
    showFeedback(err.message, true);
  } finally {
    toggleMuteBtn.disabled = false;
  }
});

refreshBtn.addEventListener("click", async () => {
  refreshBtn.disabled = true;
  await fetchState();
  refreshBtn.disabled = false;
});

fetchState();
setInterval(fetchState, POLL_INTERVAL_MS);
