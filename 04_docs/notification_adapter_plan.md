# Notification Adapter Plan

## Purpose

Notifications should make blocked or approval-needed work visible without pretending that external messaging is already implemented.

## First Channel

- local dashboard notification mode

This is the only real channel in this batch. It is enough to expose approval-needed and human-needed state inside the operator console.

## Later Possible Channels

- email
- SMS
- WhatsApp
- push

## Current Rule

This batch only creates the notification abstraction and local payload structure. It does not add real delivery integrations.

## Why This Matters

A patient supervisor needs a clean way to say:

- a task is waiting
- a task needs approval
- a task is blocked and needs the human

That signaling layer should exist before real external channels are added.
