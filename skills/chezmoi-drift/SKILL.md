---
name: chezmoi-drift
description: "Check chezmoi dotfiles for drift, unmanaged files, and broken skill links."
display_name: "Chezmoi Drift"
brand_color: "#2563EB"
local_only: true
group: "Dev Workflow"
usage: "/chezmoi-drift:run"
summary: "Catch when your dotfiles have drifted from what's committed, and when a skill install silently broke."
default_prompt: "Audit this machine or dotfiles setup for chezmoi drift and broken shared skill installs. Report first; don't mutate anything unless I explicitly ask."
---

# Chezmoi Drift

Use this skill as a dotfiles weekly checkup. Report first; mutate later.

## Quick Start

```bash
src_dir=$(chezmoi source-path)
chezmoi status 2>&1
chezmoi unmanaged 2>&1 | grep -Ev '\.DS_Store|__pycache__|/Library/|/Caches/' | head -60
```

If `chezmoi status` is empty, managed files are in sync.

## Workflow

### 1. Check managed-file drift

Run:

```bash
chezmoi status 2>&1
```

Interpret status codes:
- `M` = modified in target
- `A` = present in source but not applied
- `R` = present in target but removed from source

Report exact paths and codes. Do not paraphrase away the useful bits.

### 2. Find unmanaged files worth tracking

Run:

```bash
chezmoi unmanaged 2>&1 | grep -Ev '\.DS_Store|__pycache__|/Library/|/Caches/' | head -60
```

Flag only files that look intentional and reusable, especially in:
- `~/`
- `~/.local/bin/`
- `~/.config/`
- `~/.claude/`, `~/.codex/`, `~/.gemini/`, `~/.continue/`, `~/.cursor/`
- `~/.local/share/opencode/`

Skip app noise, caches, session files, logs, and secrets.

### 3. Check script and config coverage

Run:

```bash
src_dir=$(chezmoi source-path)
comm -23 \
  <(command ls ~/.local/bin | sort) \
  <(command ls "$src_dir/dot_local/bin" | sed 's/^executable_//' | sort)

comm -23 \
  <(command ls ~/.config | sort) \
  <(command ls "$src_dir/dot_config" | sort)
```

Report new scripts or config directories that look worth managing.

### 4. Check shared skill install health

If a local agent-skills repo checkout exists (e.g. `~/dev/agent-skills/skills`; ask or search if unsure), prefer symlinks from the live skill directories back to that repo rather than copying.

Inspect:

```bash
for host in \
  ~/.claude/skills \
  ~/.codex/skills \
  ~/.agents/skills \
  ~/.local/share/opencode/skills \
  ~/.gemini/skills \
  ~/.continue/skills \
  ~/.cursor/skills; do
  [ -d "$host" ] || continue
  echo "== $host =="
  command ls -ld "$host"/chezmoi-drift 2>/dev/null || true
  readlink "$host"/chezmoi-drift 2>/dev/null || true
done
```

Call out:
- missing installs
- copied directories where a symlink should exist
- stale links (broken or pointing to a moved/deleted source)

### 5. Detect double-installed skills (symlink + plugin)

A skill must load through **one** mechanism only. The expensive failure mode is a skill present **both** as a symlink in `~/.claude/skills/<name>` **and** as an installed plugin (`<name>@<marketplace>`). It then appears twice in every agent's skill list — wasted context and confusing UX. This happens when a plugin marketplace built from the same skills repo overlaps live repo symlinks.

This check is Claude Code specific: skip it if the `claude` CLI isn't installed (say so in the report).

Use `command ls`, not bare `ls`. If `ls` is aliased to `eza` or similar, it prints
`name -> target` for symlinks, so symlinked skills fail to match and the
check silently under-reports.

```bash
comm -12 \
  <(command ls -1 ~/.claude/skills 2>/dev/null | sort -u) \
  <(claude plugin list 2>/dev/null | grep '❯' | sed 's/^[^❯]*❯ *//; s/@.*//' | grep . | sort -u)
```

Any name printed is double-installed. The fix is to keep **one** mechanism:
- On a machine where the skills repo is checked out and edited, **symlinks are canonical** (live edits show instantly). Remove the plugin: `claude plugin uninstall <name>@<marketplace>`.
- On a machine without the repo, plugin install is canonical. Remove the stray symlink instead.

Never install a plugin derived from the skills repo on a machine that already symlinks the live repo.

A marketplace with `"autoUpdate": true` in `~/.claude/settings.json` will keep
reinstating its plugins. Uninstalling the plugins is not enough — remove the
marketplace too: `claude plugin marketplace remove <name>`.

### 6. Report

Use this format:

```text
DRIFT REPORT
============
Managed files with drift: ...
Unmanaged files worth tracking: ...
Scripts not in chezmoi: ...
Config dirs not in chezmoi: ...
Shared skill install issues: ...
Double-installed skills (symlink + plugin): ...
```

Then propose exact commands for anything worth fixing.

## Action Rules

- Do **not** run `chezmoi add`, `chezmoi re-add`, `chezmoi apply`, `rm`, or git commands unless the user explicitly asks.
- Prefer `chezmoi source-path` over hard-coding the source repo path.
- Never add secrets or token-bearing files without converting them to a safe template first.
- For shared skills, prefer `ln -sfn <repo>/skills/<skill> <target>` over copying directories around.
