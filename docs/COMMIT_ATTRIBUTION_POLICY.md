# Commit Attribution Policy

Ghoti commits are kept human-authored unless the owner explicitly changes this
policy.

## Rule

- Use the configured human Git author.
- Do not add AI co-author trailers.
- Do not add agent names as commit authors or co-authors.
- Do not rewrite historical commits solely to remove old metadata.
- Verify the latest commit before pushing.

## Verification

```powershell
git log -1 --format="%an <%ae>%n%s%n%b"
```

The latest commit should show the human author, intended subject, and no
co-author trailer.
