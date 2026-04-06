# Tool Capability Matrix

| Item | Required Tool(s) | Current Capability State | Blocking Issue |
| --- | --- | --- | --- |
| python runtime | `python` | available via resolved interpreter fallback | not consistently available as a clean PATH command |
| git repo operations | `git` | available | no blocker seen in the current runtime |
| gh CLI | `gh` | blocked in current runtime shell | not on PATH and not yet resolved by fallback detection today |
| GitHub read-only inspection | `git` | available | none |
| GitHub remote write actions | `git`, `gh`, `gh auth` | blocked | `gh` presence and auth still gate remote mutation |
| mail planning adapter | none beyond runtime | available | no live mailbox adapter by design |
| Notion planning adapter | none beyond runtime | available | no live Notion adapter by design |
| browser/app executor | future executor layer | not implemented | executor does not exist yet |

This matrix should stay grounded in what the runtime can actually see, not what might be installed elsewhere on the machine.
