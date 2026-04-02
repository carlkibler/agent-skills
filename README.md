# Claude Code Skills

Reusable skills for [Claude Code](https://claude.ai/claude-code) that enhance AI-assisted development workflows.

## Skills

| Skill | Description |
|-------|-------------|
| [pre-mortem](pre-mortem/) | Multi-agent project pre-mortem based on Gary Klein's technique. Spawns parallel AI agents with different failure-finding mandates, synthesizes ranked risks with mitigations. |
| [speaker](speaker/) | Build an honest, multidimensional profile of the user from their digital footprint. Produces personal portraits, professional portraits, working-with-me guides, and system prompts. Inspired by Orson Scott Card's *Speaker for the Dead*. |

## Installation

### Option 1: Symlink individual skills

```bash
ln -s /path/to/claude-skills/pre-mortem ~/.claude/skills/pre-mortem
```

### Option 2: Clone and symlink all

```bash
git clone git@github-personal:carlkibler/claude-skills.git ~/dev/me/claude-skills

for skill in ~/dev/me/claude-skills/*/; do
  name=$(basename "$skill")
  [[ -f "$skill/SKILL.md" ]] && ln -sf "$skill" ~/.claude/skills/"$name"
done
```

### Option 3: Add as Claude Code plugin (coming soon)

Plugin format support is planned for broader distribution.

## Skill Structure

Each skill follows the Claude Code skill format:

```
skill-name/
  SKILL.md              # Entry point with YAML frontmatter
  scripts/              # Helper scripts (executed, not loaded into context)
  references/           # Domain knowledge (read as needed)
```

## Environment Resilience

Skills that use external LLM tools (like pre-mortem) detect available CLIs at runtime and fall back gracefully to Claude-only mode. No external tools are required.

**Supported LLM CLIs** (auto-detected when present):
- `llm` (Simon Willison's tool)
- `gemini` / `ask-gemini`
- `gh copilot` / `ask-copilot`
- `codex`
- `ollama`
- `ask-cerebras`, `ask-zai`

## Contributing

PRs welcome. Each skill should:
1. Have a `SKILL.md` with valid frontmatter (name, description)
2. Work with Claude Code only (no external dependencies required)
3. Degrade gracefully when optional tools aren't available
4. Include clear trigger conditions in the description

## License

MIT
