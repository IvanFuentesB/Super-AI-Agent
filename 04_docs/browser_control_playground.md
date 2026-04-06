# Browser Control Playground

## Purpose

Create the first real control step in a way that is local, deterministic, and easy to inspect.

## Why Browser Before Full Desktop

- browser workflows are narrower and easier to reason about than full Windows GUI control
- local HTML and a fixed click path are safer than live-site automation
- screenshots and DOM state make verification straightforward

## Why Playwright First

- it is the clearest deterministic browser-control layer in the current stack
- it supports small scripted checks without a heavier executor framework
- it gives the project a real artifact path before broader browser or desktop automation is attempted

## How Other Repos Fit Later

- `browser-use` and `stagehand`: higher-level browser executor references after control boundaries are clearer
- `windows-use` and `windows-mcp`: possible Windows GUI paths after browser control is stable
- `open-interpreter` and `open-computer-use`: broader control experiments, not the first safe step

## Headless Smoke Test

- runs quickly in headless Chromium
- clicks the local demo button and verifies the page text changed
- produces `01_projects/browser_playground/artifacts/smoke-click.png`
- proves the automation path works even when the browser window is not shown

## Visible Headed Demo

- opens a real Chromium window
- uses a small slow-motion delay so the click is easier to watch
- keeps the window open briefly before closing
- still verifies the text change and saves the screenshot artifact

## What This Playground Proves

- Node and Playwright can run locally in this workspace
- a deterministic local click flow can be executed in both headless and headed modes
- browser automation can be demonstrated visibly without touching live sites
- a screenshot proves that scripted interaction happened on the demo page

## What It Does Not Prove Yet

- no browser executor loop
- no live web workflow automation
- no desktop cursor or Windows app control
- no approval-gated live browser actions yet

## Important Distinction

A screenshot artifact proves that Playwright drove the page and changed DOM state. It does not prove moving the Windows cursor, controlling native apps, or running a broader browser executor with observation, approval, and recovery logic.
