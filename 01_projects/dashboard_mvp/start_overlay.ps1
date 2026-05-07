# start_overlay.ps1 — Opens the Ghoti presence overlay in the default browser.
# Does not start hidden recording. Does not require admin.
# Requires the dashboard server to be running: node server.js

$overlayUrl = "http://127.0.0.1:3210/overlay"
Start-Process $overlayUrl
Write-Host "Ghoti overlay opened: $overlayUrl"
