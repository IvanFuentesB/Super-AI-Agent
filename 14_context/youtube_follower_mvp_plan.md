# YouTube Tutorial Follower MVP Plan

## Status
Scaffold only. Not yet implemented. Browser operator not integrated.

## Safe Implementation Path

### Step 1 — User provides YouTube URL
- User submits URL + goal via POST /api/ghoti/youtube-follower/task
- Server validates URL format, stores as a planned task in runtime_data/youtube_follower_tasks.json

### Step 2 — Ghoti records the task request
- Task stored locally with status: "planned", execution_enabled: false
- Unique task ID generated
- User sees confirmation with "needs_user_approval: true"

### Step 3 — Transcript/caption retrieval
- Attempt to fetch auto-generated captions from YouTube (yt-dlp or similar)
- If unavailable: prompt user to paste transcript manually or wait for voice/screen capture capability
- No video playback or downloads by default

### Step 4 — Step extraction
- Parse transcript into ordered step list using Claude/LLM call
- Display proposed steps to user for review
- User can edit, reorder, or reject steps

### Step 5 — User approves step list
- Gate: user must explicitly approve before any execution begins
- No action taken without approval

### Step 6 — Supervised execution (one step at a time)
- Ghoti executes ONE approved step using supervised desktop/browser bridge
- Screenshot taken after each step
- Result shown to user before proceeding

### Step 7 — Approval before risky actions
- Any step involving file writes, installs, form submissions, or system changes requires explicit user approval
- Low-risk steps (reading, navigation) can be pre-approved in batch

### Step 8 — Logging
- Every action, screenshot, and decision logged to task record
- Log accessible at runtime_data/youtube_follower_tasks.json

### Step 9 — Pause on uncertainty
- If Ghoti cannot identify what a step requires, it pauses and asks the user
- Never guesses on destructive or irreversible actions

### Step 10 — Completion report
- Summary of completed steps, screenshots, and any skipped/failed steps
- Stored in task record for review

## Dependencies Not Yet Met
- Browser operator: browser-use is cloned as reference only, not integrated
- yt-dlp or caption API: not installed
- Desktop action bridge: scaffolded but narrow
- LLM step extraction: Claude Code is external, no runtime LLM call path yet

## API Scaffold (implemented)

```
GET  /api/ghoti/youtube-follower/status   — status + task count
POST /api/ghoti/youtube-follower/task     — create planned task (no execution)
```

## Next Integration Step
1. Integrate browser-use or Playwright for supervised browser control
2. Add yt-dlp wrapper for caption fetching
3. Add LLM call path for step extraction
4. Wire approval gate UI in dashboard
