#!/usr/bin/env bash
# Sync agent-skills bin/ tools into the user-level ~/.local/bin via chezmoi.
#
# Source of truth:  this repo's bin/<tool>
# chezmoi owns the deployed copy:  dot_local/bin/executable_<tool>  ->  ~/.local/bin/<tool>
#
# Why ~/.local/bin and not ~/.claude/bin:
#   - It's already ahead of ~/.claude/bin on PATH, so this copy wins automatically.
#   - It owes nothing to Claude Code. `agent` keeps working if .claude is wiped,
#     reinstalled, or never present (fresh machine after `chezmoi apply`).
#
# Dry run by default. Pass --live to copy into the chezmoi source and apply.
set -euo pipefail

REPO_BIN="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/bin"

# Tools to keep in sync. Add more as they migrate off the .claude wrapper.
TOOLS=(agent)

LIVE=0
case "${1:-}" in
    --live) LIVE=1 ;;
    "" ) ;;
    -h|--help)
        echo "Usage: $0 [--live]"
        echo "  (no args)  Dry run — show what would change."
        echo "  --live     Copy bin/<tool> into chezmoi source and apply to ~/.local/bin."
        exit 0 ;;
    *) echo "Error: unknown argument: $1" >&2; exit 2 ;;
esac

command -v chezmoi >/dev/null 2>&1 || { echo "Error: chezmoi not found on PATH" >&2; exit 1; }

CHEZMOI_SRC="$(chezmoi source-path)"
DEST_SRC_DIR="$CHEZMOI_SRC/dot_local/bin"
mkdir -p "$DEST_SRC_DIR"

changed=()
for tool in "${TOOLS[@]}"; do
    src="$REPO_BIN/$tool"
    dst="$DEST_SRC_DIR/executable_$tool"
    if [ ! -f "$src" ]; then
        echo "skip: $src missing" >&2
        continue
    fi
    if [ -f "$dst" ] && diff -q "$src" "$dst" >/dev/null 2>&1; then
        echo "ok:   $tool — chezmoi source already matches repo"
        continue
    fi
    changed+=("$tool")
    if [ "$LIVE" -eq 1 ]; then
        cp "$src" "$dst"
        chmod +x "$dst"
        echo "sync: $tool -> $dst"
    else
        echo "diff: $tool would update $dst"
        diff -u "$dst" "$src" 2>/dev/null | head -40 || true
    fi
done

if [ "$LIVE" -eq 1 ]; then
    for tool in "${TOOLS[@]}"; do
        chezmoi apply "$HOME/.local/bin/$tool"
    done
    echo "applied: ~/.local/bin/{${TOOLS[*]// /,}}"
    echo
    echo "Note: chezmoi source is in the dotfiles repo. Commit & push it there to persist."
elif [ ${#changed[@]} -eq 0 ]; then
    echo "Nothing to do — everything in sync."
else
    echo
    echo "Dry run. Re-run with --live to copy into chezmoi and apply."
fi
