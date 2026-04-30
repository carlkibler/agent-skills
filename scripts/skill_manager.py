#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
skill-manager — CLI for managing skills in the agent-skills repo.

Commands:
  rename <old> <new> [--live]   Rename a skill (dry-run by default)
  new <name> [--live]           Scaffold a new skill
  check                         Run lint_skills.py
  list                          Print a table of all skills
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"
CLAUDE_MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"
SETTINGS_JSON = Path.home() / ".claude" / "settings.json"
SYNC_SCRIPT = REPO / "scripts" / "sync_codex_packaging.py"
LINT_SCRIPT = REPO / "scripts" / "lint_skills.py"


# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return (fields, body_after_closing_dashes). body includes the ---\\n delimiter."""
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}, text
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"')
    rest = text[match.end():]
    return fields, rest


def build_frontmatter(fields: dict[str, str]) -> str:
    lines = ["---"]
    for key, value in fields.items():
        lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def update_frontmatter_field(text: str, key: str, new_value: str) -> str:
    """Replace a single frontmatter field value in-place, preserving order."""
    pattern = rf"(^---\n(?:.*\n)*?){re.escape(key)}:.*(\n(?:.*\n)*?---\n)"
    replacement = rf"\g<1>{key}: {new_value}\2"
    result, count = re.subn(pattern, replacement, text, flags=re.M)
    if count == 0:
        # Field not found — append before closing ---
        result = re.sub(r"\n---\n", f"\n{key}: {new_value}\n---\n", text, count=1)
    return result


# ---------------------------------------------------------------------------
# Marketplace helpers
# ---------------------------------------------------------------------------

def load_marketplace() -> dict:
    return json.loads(CLAUDE_MARKETPLACE.read_text())


def save_marketplace(data: dict, dry_run: bool) -> None:
    content = json.dumps(data, indent=2) + "\n"
    if dry_run:
        print(f"  [dry] would write {CLAUDE_MARKETPLACE}")
    else:
        CLAUDE_MARKETPLACE.write_text(content)
        print(f"  wrote {CLAUDE_MARKETPLACE}")


# ---------------------------------------------------------------------------
# rename
# ---------------------------------------------------------------------------

def cmd_rename(old: str, new: str, live: bool) -> int:
    dry_run = not live
    mode = "dry-run" if dry_run else "live"
    print(f"rename '{old}' -> '{new}'  [{mode}]\n")

    old_path = SKILLS_DIR / old
    new_path = SKILLS_DIR / new

    if not old_path.exists():
        print(f"ERROR: skills/{old}/ does not exist", file=sys.stderr)
        return 1
    if new_path.exists():
        print(f"ERROR: skills/{new}/ already exists", file=sys.stderr)
        return 1

    # 1. git mv
    print(f"  git mv skills/{old} skills/{new}")
    if not dry_run:
        result = subprocess.run(
            ["git", "mv", f"skills/{old}", f"skills/{new}"],
            cwd=REPO,
        )
        if result.returncode != 0:
            print("ERROR: git mv failed", file=sys.stderr)
            return 1

    # 2. Update SKILL.md frontmatter
    skill_md_path = (new_path if not dry_run else old_path) / "SKILL.md"
    skill_md_text = skill_md_path.read_text()
    updated = skill_md_text
    updated = update_frontmatter_field(updated, "name", new)
    # Update usage field if it references /<old>:
    updated = re.sub(rf"/{re.escape(old)}:", f"/{new}:", updated)
    if updated != skill_md_text:
        print(f"  update skills/{new}/SKILL.md frontmatter")
        if not dry_run:
            (new_path / "SKILL.md").write_text(updated)
    else:
        print(f"  skills/{new}/SKILL.md — no frontmatter changes needed")

    # 3. Update .claude-plugin/marketplace.json
    marketplace = load_marketplace()
    updated_marketplace = False
    for plugin in marketplace.get("plugins", []):
        if plugin.get("name") == old:
            plugin["name"] = new
            plugin["skills"] = [f"./skills/{new}"]
            updated_marketplace = True
            break
    if updated_marketplace:
        print(f"  update .claude-plugin/marketplace.json: '{old}' -> '{new}'")
        save_marketplace(marketplace, dry_run)
    else:
        print(f"  WARNING: '{old}' not found in marketplace.json")

    # 4. Update ~/.claude/settings.json enabledPlugins
    old_key = f"{old}@carl-tools"
    new_key = f"{new}@carl-tools"
    if SETTINGS_JSON.exists():
        settings = json.loads(SETTINGS_JSON.read_text())
        enabled = settings.get("enabledPlugins", {})
        if old_key in enabled:
            value = enabled.pop(old_key)
            enabled[new_key] = value
            settings["enabledPlugins"] = enabled
            settings_content = json.dumps(settings, indent=2) + "\n"
            print(f"  update ~/.claude/settings.json: '{old_key}' -> '{new_key}'")
            if not dry_run:
                SETTINGS_JSON.write_text(settings_content)
        else:
            print(f"  ~/.claude/settings.json: '{old_key}' not in enabledPlugins (skipped)")
    else:
        print("  ~/.claude/settings.json not found (skipped)")

    # 5. Run sync + lint
    print(f"\n  running sync_codex_packaging.py")
    if not dry_run:
        subprocess.run(["python3", str(SYNC_SCRIPT)], cwd=REPO, check=True)

    print(f"  running lint_skills.py")
    if not dry_run:
        subprocess.run(["python3", str(LINT_SCRIPT)], cwd=REPO, check=True)

    if dry_run:
        print("\nDry-run complete. No files were modified. Pass --live to apply.")
    else:
        print(f"\nDone. Skill renamed from '{old}' to '{new}'.")
    return 0


# ---------------------------------------------------------------------------
# new
# ---------------------------------------------------------------------------

SKILL_MD_TEMPLATE = """\
---
name: {name}
description: TODO: Add a concise description of what this skill does.
---

# {title}

TODO: Describe what this skill does and when to use it.

## Usage

Invoke with:

```
/{name}:run
```

## Behavior

1. TODO: describe step 1
2. TODO: describe step 2
"""


def cmd_new(name: str, live: bool) -> int:
    dry_run = not live
    mode = "dry-run" if dry_run else "live"
    print(f"new skill '{name}'  [{mode}]\n")

    skill_path = SKILLS_DIR / name
    if skill_path.exists():
        print(f"ERROR: skills/{name}/ already exists", file=sys.stderr)
        return 1

    title = name.replace("-", " ").title()
    skill_md_content = SKILL_MD_TEMPLATE.format(name=name, title=title)

    files_to_create = [
        (skill_path / "SKILL.md", skill_md_content),
        (skill_path / "scripts" / ".keep", ""),
        (skill_path / "references" / ".keep", ""),
    ]

    for path, content in files_to_create:
        print(f"  create {path.relative_to(REPO)}")
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)

    # Add to marketplace.json
    marketplace = load_marketplace()
    new_entry = {
        "name": name,
        "description": "TODO: Add a concise description.",
        "source": "./",
        "skills": [f"./skills/{name}"],
        "category": "productivity",
        "version": "1.0.0",
    }
    marketplace["plugins"].append(new_entry)
    print(f"  add '{name}' to .claude-plugin/marketplace.json")
    save_marketplace(marketplace, dry_run)

    # Run sync
    print(f"\n  running sync_codex_packaging.py")
    if not dry_run:
        subprocess.run(["python3", str(SYNC_SCRIPT)], cwd=REPO, check=True)

    if dry_run:
        print("\nDry-run complete. No files were modified. Pass --live to apply.")
    else:
        print(f"\nDone. Scaffolded skills/{name}/. Edit SKILL.md to fill in the description.")
    return 0


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------

def cmd_check() -> int:
    result = subprocess.run(["python3", str(LINT_SCRIPT)], cwd=REPO)
    return result.returncode


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

def cmd_list() -> int:
    skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    if not skill_dirs:
        print("No skills found.")
        return 0

    rows = []
    for skill_path in skill_dirs:
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            rows.append((skill_path.name, "(no SKILL.md)", "(no SKILL.md)"))
            continue
        fields, _ = parse_frontmatter(skill_md.read_text())
        group = fields.get("group", "")
        display_name = fields.get("display_name", skill_path.name.replace("-", " ").title())
        rows.append((skill_path.name, group, display_name))

    col1 = max(len(r[0]) for r in rows)
    col2 = max(len(r[1]) for r in rows)
    header = f"{'SKILL':<{col1}}  {'GROUP':<{col2}}  DISPLAY NAME"
    print(header)
    print("-" * len(header))
    for skill, group, display_name in rows:
        print(f"{skill:<{col1}}  {group:<{col2}}  {display_name}")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="skill-manager",
        description="Manage skills in the agent-skills repo.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_rename = subparsers.add_parser("rename", help="Rename a skill (dry-run by default)")
    p_rename.add_argument("old", help="Current skill name (folder name)")
    p_rename.add_argument("new", help="New skill name (folder name)")
    p_rename.add_argument("--live", action="store_true", help="Apply changes (default is dry-run)")

    p_new = subparsers.add_parser("new", help="Scaffold a new skill (dry-run by default)")
    p_new.add_argument("name", help="New skill name (kebab-case)")
    p_new.add_argument("--live", action="store_true", help="Apply changes (default is dry-run)")

    subparsers.add_parser("check", help="Run lint_skills.py and return its exit code")
    subparsers.add_parser("list", help="Print a table of all skills")

    args = parser.parse_args()

    if args.command == "rename":
        sys.exit(cmd_rename(args.old, args.new, args.live))
    elif args.command == "new":
        sys.exit(cmd_new(args.name, args.live))
    elif args.command == "check":
        sys.exit(cmd_check())
    elif args.command == "list":
        sys.exit(cmd_list())


if __name__ == "__main__":
    main()
