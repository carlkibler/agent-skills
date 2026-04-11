# CLAUDE.md

Shared skill collection for Claude Code and Codex.

## Conventions

### Scripts Must Be Standalone

All Python scripts in skills MUST be self-contained and runnable without cloning any other repo.

**Use PEP 723 inline script metadata** so `uv run` handles deps automatically:
```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27", "click>=8.0"]
# ///
```

Also include a `try/except ImportError` fallback for plain `python` usage:
```python
try:
    import click
    import httpx
except ImportError:
    sys.exit("Missing dependencies. Run: pip install httpx click")
```

Invoke scripts with `uv run scripts/my_script.py` — deps install into a temp venv automatically.

### Skill Structure

```
skills/my-skill/
├── SKILL.md              # Required — YAML frontmatter + instructions
├── scripts/              # Standalone Python with PEP 723 headers
├── references/           # Docs loaded into context as needed
└── assets/               # Files used in output (templates, etc.)
```

**SKILL.md frontmatter** — `name` and `description` are required:
```yaml
---
name: my-skill
description: Specific description of what it does and when to use it.
---
```

### Distribution via Plugin Marketplace

This repo is a Claude Code plugin marketplace. Users install via:

```
/plugin marketplace add carlkibler/agent-skills
/plugin install <skill-name>@agent-skills
```

Each skill in `skills/<name>/` is its own installable plugin. Register new skills in `.claude-plugin/marketplace.json`.

Skills follow the [Agent Skills open standard](https://agentskills.io) and work across Claude Code and Codex. Use `${CLAUDE_SKILL_DIR}` in scripts to reference bundled files at runtime instead of hardcoded paths.

### Naming

- Skill directories: lowercase kebab-case (`okta-sso-debugger`)
- Python scripts: snake_case (`okta_api.py`)

### Creating New Skills

Use the `/skill-creator` skill or copy an existing skill as a starting point.

After creating, register in `.claude-plugin/marketplace.json`.

## Security

Never include credentials, API keys, or secrets in skills. Tokens go in `.env` files (gitignored) or environment variables.

## Directory Structure

```
.claude-plugin/
  ├── marketplace.json           # Marketplace catalog (one entry per skill)
  └── plugin.json                # Plugin manifest for the repo itself
skills/
  ├── pre-mortem/                # Multi-agent pre-mortem analysis
  ├── profile-me/                # Build AI profile from digital footprint
  ├── getting-second-opinions/   # Copilot CLI validation with gpt-5.4-codex
  ├── handle-pr/                 # Auto-handle PR review comments
  ├── chezmoi-drift/             # Dotfiles drift + shared-skill install audit
  ├── trust-audit/               # Product trust surface audit
  ├── support-inbox-simulation/  # Pre-launch support email simulation
  ├── first-run-red-team/        # First-run experience red-teaming
  └── wifi-qr/                   # WiFi QR code generator
```
