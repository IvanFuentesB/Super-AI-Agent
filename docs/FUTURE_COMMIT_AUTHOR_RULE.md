# Future Commit Author Rule

Before commit:

- Confirm `git config user.name` and `git config user.email` identify the
  approved human committer.
- Use a commit message without co-author trailers.
- Do not include agent names in author, committer, or trailer fields.

After commit:

```powershell
git log -1 --format="%an <%ae>%n%s%n%b"
```

If the latest commit contains an agent author or co-author trailer, fix it
before pushing. Do not rewrite older history for attribution cleanup unless the
owner explicitly asks.
