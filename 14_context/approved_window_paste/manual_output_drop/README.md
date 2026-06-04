# Manual output drop (N+6.20A)

Drop agent replies here as text/markdown files. After you copy a prompt packet to an
agent and it answers, save its reply into this folder (for example
`claude_reply_2026-06-04.md`). Then summarize everything dropped here with:

```
python 03_scripts/approved_window_paste/write_manual_output_summary.py --json
# write the summary file:
python 03_scripts/approved_window_paste/write_manual_output_summary.py --write --json
```

## What is committed vs generated

- **Committed:** this `README.md` only.
- **Generated (never committed):** every dropped output file and every generated
  summary. The rest of this folder is git-ignored.

## Safety

This is a passive local drop folder. Nothing here is sent anywhere, submitted, or
executed. The summary tool reads the dropped files read-only and writes a local
Markdown summary; it runs no commands and reads no secrets.
