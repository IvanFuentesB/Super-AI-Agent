# Latest Report Summary

Source: `14_context/codex_three_repo_clone_truth_crosscheck_n3_4.md`

- Normal `git -C` inspection of the nested eval repos is blocked by Git dubious-ownership protection because the nested repos are owned by `Ivan-G14/Navif` while this process runs as `Ivan-G14/ai_sandbox`. Codex did not modify global `safe.directory`. HEAD and remote URL were crosschecked by reading each nested repo's `.git/HEAD`, ref file, and `.git/config` directly.

This is a deterministic local_demo summary. No live APIs were used.
