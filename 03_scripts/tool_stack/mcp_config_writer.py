"""Write disabled-by-default MCP connector config templates.

Templates contain NO secrets and NO real account data. Every template is
`enabled:false` with `manual_setup_required:true`; env vars are named, never
valued. Writing a template connects nothing.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = REPO_ROOT / "14_context" / "mcp_connectors" / "config_templates"

# Each entry becomes one <id>.template.json. allowed/blocked capabilities make
# the safety posture explicit; blocked lists keep dangerous caps off by default.
CONNECTORS = [
    {"id": "github", "name": "GitHub MCP", "purpose": "Read/manage issues, PRs, repo metadata.",
     "required_env_vars": ["GITHUB_TOKEN"], "install": "npx -y @modelcontextprotocol/server-github",
     "allowed": ["repo_read", "issues_read", "pr_read"], "blocked": ["force_push", "secrets_read", "billing"],
     "test": "list open issues on a test repo"},
    {"id": "gmail", "name": "Gmail MCP", "purpose": "Read/draft email (drafts only; no sending).",
     "required_env_vars": ["GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_OAUTH_REFRESH_TOKEN"],
     "install": "see provider docs", "allowed": ["email_read", "draft_create"],
     "blocked": ["email_send", "delete", "contacts_export"], "test": "list latest 5 subjects (read-only)"},
    {"id": "google-calendar", "name": "Google Calendar MCP", "purpose": "Read events, propose times.",
     "required_env_vars": ["GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_OAUTH_REFRESH_TOKEN"],
     "install": "see provider docs", "allowed": ["calendar_read", "freebusy"],
     "blocked": ["event_delete", "invite_send"], "test": "list today's events (read-only)"},
    {"id": "google-drive", "name": "Google Drive MCP", "purpose": "Read/search docs.",
     "required_env_vars": ["GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_OAUTH_REFRESH_TOKEN"],
     "install": "see provider docs", "allowed": ["drive_read", "drive_search"],
     "blocked": ["drive_delete", "share_external"], "test": "search a known filename (read-only)"},
    {"id": "notion", "name": "Notion MCP", "purpose": "Read/append notes and databases.",
     "required_env_vars": ["NOTION_API_KEY"], "install": "see provider docs",
     "allowed": ["page_read", "db_query"], "blocked": ["page_delete", "workspace_admin"],
     "test": "query a test database (read-only)"},
    {"id": "figma", "name": "Figma MCP", "purpose": "Read designs for design-to-code.",
     "required_env_vars": ["FIGMA_ACCESS_TOKEN"], "install": "see provider docs",
     "allowed": ["file_read", "node_read"], "blocked": ["file_write", "team_admin"],
     "test": "read a test file's metadata (read-only)"},
    {"id": "chrome-devtools", "name": "Chrome DevTools MCP", "purpose": "Inspect page DOM/network for debugging.",
     "required_env_vars": [], "install": "see provider docs",
     "allowed": ["dom_read", "console_read"], "blocked": ["navigate", "click", "type", "form_submit", "downloads"],
     "test": "read DOM of a local test page (no interaction)"},
    {"id": "browserbase", "name": "Browserbase MCP", "purpose": "Hosted browser (observation design first).",
     "required_env_vars": ["BROWSERBASE_API_KEY", "BROWSERBASE_PROJECT_ID"], "install": "see provider docs",
     "allowed": ["page_read"], "blocked": ["click", "type", "navigate", "account_login", "purchase"],
     "test": "fetch a public page's text (read-only)"},
    {"id": "composio", "name": "Composio MCP", "purpose": "Managed multi-SaaS connector hub.",
     "required_env_vars": ["COMPOSIO_API_KEY"], "install": "see provider docs",
     "allowed": ["connector_list"], "blocked": ["account_action", "send", "purchase"],
     "test": "list available connectors (read-only)"},
    {"id": "n8n", "name": "n8n MCP", "purpose": "Self-hosted automation flows (design first).",
     "required_env_vars": ["N8N_BASE_URL", "N8N_API_KEY"], "install": "self-host n8n; see docs",
     "allowed": ["workflow_read"], "blocked": ["workflow_execute_live", "credentials_read"],
     "test": "list workflows (read-only)"},
    {"id": "stagehand", "name": "Stagehand", "purpose": "Browser automation framework (observation first).",
     "required_env_vars": ["BROWSERBASE_API_KEY"], "install": "see provider docs",
     "allowed": ["page_read"], "blocked": ["act", "click", "type", "navigate"],
     "test": "extract text from a public page (read-only)"},
    {"id": "firecrawl", "name": "Firecrawl", "purpose": "Crawl/scrape to markdown (TOS-compliant only).",
     "required_env_vars": ["FIRECRAWL_API_KEY"], "install": "see provider docs",
     "allowed": ["crawl_public"], "blocked": ["bypass_paywall", "ignore_robots"],
     "test": "scrape a docs page you are allowed to read"},
    {"id": "apify", "name": "Apify", "purpose": "Actor-based scraping (compliant use only).",
     "required_env_vars": ["APIFY_TOKEN"], "install": "see provider docs",
     "allowed": ["actor_run_public"], "blocked": ["bypass_paywall", "personal_data_harvest"],
     "test": "run a hello-world actor"},
    {"id": "perplexity", "name": "Perplexity / code-context", "purpose": "Search/context (verify canonical MCP first).",
     "required_env_vars": ["PERPLEXITY_API_KEY"], "install": "verify canonical source",
     "allowed": ["search"], "blocked": ["account_action"], "test": "one search query"},
    {"id": "repomix", "name": "Repomix / git ingest", "purpose": "Pack a repo into one AI-friendly file.",
     "required_env_vars": [], "install": "verify npm package; intake-first",
     "allowed": ["repo_read_local"], "blocked": ["network_fetch_unknown"],
     "test": "pack this repo to a temp file (local only)"},
    {"id": "browser-observation-harness", "name": "Local browser observation harness (placeholder)",
     "purpose": "Future observe-only computer-use bridge.", "required_env_vars": [],
     "install": "not built; placeholder", "allowed": ["screen_read_planned"],
     "blocked": ["click", "type", "navigate", "control"], "test": "n/a (placeholder)"},
]


def _template(c: dict) -> dict:
    return {
        "name": c["name"],
        "purpose": c["purpose"],
        "enabled": False,
        "required_env_vars": c["required_env_vars"],
        "install_command_placeholder": c["install"],
        "config_path_placeholder": "23_configs/mcp/%s.json (create from this template)" % c["id"],
        "manual_setup_required": True,
        "allowed_capabilities": c["allowed"],
        "blocked_capabilities": c["blocked"],
        "safety_notes": "Disabled by default. No secrets in repo - set env vars locally. "
                        "Blocked capabilities must stay blocked until a separate safety gate.",
        "test_command": c["test"],
    }


def write_templates() -> dict:
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for c in CONNECTORS:
        path = TEMPLATE_DIR / ("%s.template.json" % c["id"])
        path.write_text(json.dumps(_template(c), indent=2) + "\n", encoding="utf-8")
        written.append(path.relative_to(REPO_ROOT).as_posix())
    return {"ok": True, "action": "write-mcp-templates", "count": len(written),
            "templates": written, "all_disabled": True}


if __name__ == "__main__":
    print(json.dumps(write_templates(), indent=2))
