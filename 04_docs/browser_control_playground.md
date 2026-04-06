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

## What This Playground Proves

- Node and Playwright can run locally in this workspace
- a deterministic local click flow can be executed
- a visible screenshot artifact can be produced from a controlled local page
- browser automation can be checked without touching live sites

## What It Does Not Prove Yet

- no browser executor loop
- no live web workflow automation
- no Windows desktop control
- no approval-gated live browser actions yet
