---
name: agent-skills-agents
description: "Compatibility shim pointing to CLAUDE.md. Source of truth for multi-agent skill conventions."
---

# AGENTS.md

> **Source of truth: [CLAUDE.md](./CLAUDE.md)**
> This file is a thin compatibility shim. All conventions, structure, and requirements live in CLAUDE.md. Read that first.

## What This Repo Is

A shared skill collection designed to work across multiple AI coding agents — Claude Code, Codex, Copilot, Gemini CLI, and any agent that follows the [Agent Skills open standard](https://agentskills.io). Skills are agent-agnostic by design.

## Multi-Agent Support Is Required

Every skill and script must work across agents, not just Claude:

- **Skill instructions** must be written in plain language, not Claude-specific syntax
- **Scripts** must be standalone (PEP 723 headers, `try/except ImportError` fallbacks) — no agent-specific tooling required to run them
- **Distribution** uses both Claude Code marketplace (`.claude-plugin/`) and Codex plugin packaging (`.agents/`, `plugins/`) — both must stay in sync
- Run `python3 scripts/sync_codex_packaging.py` after any skill changes to keep Codex packaging current

## Tool Name Mapping

Skills use Claude Code tool names in their instructions. Other agents should consult their platform's mapping:
- Codex: `references/codex-tools.md`
- Copilot CLI: `references/copilot-tools.md`
- Gemini CLI: tool mapping is loaded automatically via GEMINI.md

## Creating or Modifying Skills

See CLAUDE.md for full conventions. Short version:

1. Skill lives in `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description` required)
2. Scripts go in `skills/<name>/scripts/` — standalone, PEP 723, works without any agent
3. Register in `.claude-plugin/marketplace.json` for Claude, then run the sync script for Codex
4. Use `${CLAUDE_SKILL_DIR}` (or the agent-equivalent env var) to reference bundled files at runtime

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:ca08a54f -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->
