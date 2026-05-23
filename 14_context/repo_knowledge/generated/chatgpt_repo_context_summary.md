# ChatGPT Repo Context Summary

Ghoti now has a local repo knowledge lane. It generates a selected file map,
latest report index, subsystem index, and compact task bundles so Ivan can
paste focused context instead of a giant prompt.

Repo knowledge readiness: 55%. Local file map and task bundles are available. Graphify runtime: roadmap only/not wired; no external repo runtime; no network.

Use:

- `python 03_scripts/ghoti_product_launcher.py --repo-map --json`
- `python 03_scripts/ghoti_product_launcher.py --repo-bundle next-milestone --json`
- `python 03_scripts/ghoti_product_launcher.py --context-pack --json`

Graphify remains a roadmap layer. The current implementation is local JSON and
Markdown only, with no external repo runtime and no network.
