---
name: chezmoi-drift
description: Audit chezmoi dotfiles for drift, unmanaged files, and broken agent skill symlinks across Claude Code, Codex, Gemini, and other harnesses.
display_name: "Chezmoi Drift"
brand_color: "#2563EB"
local_only: true
group: "Dev Workflow"
usage: "/chezmoi-drift:run"
summary: "Audit chezmoi dotfiles for drift and broken skill installs"
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
  <(ls ~/.local/bin | sort) \
  <(ls "$src_dir/dot_local/bin" | sed 's/^executable_//' | sort)

comm -23 \
  <(ls ~/.config | sort) \
  <(ls "$src_dir/dot_config" | sort)
```

Report new scripts or config directories that look worth managing.

### 4. Check shared skill install health

If a local agent-skills repo exists (e.g. `~/dev/me/agent-skills/skills`), prefer symlinks from the live skill directories back to that repo rather than copying.

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
  ls -ld "$host"/chezmoi-drift 2>/dev/null || true
  readlink "$host"/chezmoi-drift 2>/dev/null || true
done
```

Call out:
- missing installs
- copied directories where a symlink should exist
- stale links (broken or pointing to a moved/deleted source)

### 5. Detect double-installed skills (symlink + plugin)

A skill must load through **one** mechanism only. The expensive failure mode is a skill present **both** as a symlink in `~/.claude/skills/<name>` **and** as an installed plugin (`<name>@<marketplace>`). It then appears twice in every agent's skill list — wasted context and confusing UX. This has bitten this setup before (the `carl-tools` marketplace overlapping the live repo symlinks); keep it dead.

```bash
comm -12 \
  <(ls -1 ~/.claude/skills 2>/dev/null | sort -u) \
  <(claude plugin list 2>/dev/null | sed -E 's/.*[❯> ]+//; s/@.*//' | grep . | sort -u)
```

Any name printed is double-installed. The fix is to keep **one** mechanism:
- On a machine where the `agent-skills` repo is checked out and edited (any of Carl's boxes — gauss/euler/vesta), **symlinks are canonical** (live edits show instantly). Remove the plugin: `claude plugin uninstall <name>@<marketplace>`.
- On a machine without the repo, plugin install is canonical. Remove the stray symlink instead.

Never install a `carl-tools` (or any agent-skills-derived) plugin on a box that already symlinks the live repo.

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
