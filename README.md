# LLM Agent Skills

Skills developed by Carl Kibler to build better products and some random tasks. 
Should work in Claude Code, Codex, and others.

## Install

### Claude Code

Add this repo as a Claude Code marketplace:

```
/plugin marketplace add carlkibler/agent-skills
```

**Start with these two — you won't be disappointed:**

```
/plugin install pre-mortem@carl-tools
/plugin install empathy-audit@carl-tools
```

**`/pre-mortem:run`** — Point it at any project or idea. Parallel agents attack it from different failure angles and return a ranked, concrete list of what will actually kill the launch.

**`/empathy-audit:run`** — Run it on any feature after you think it's done. Reviews through four lenses (user, machine, developer, support) and surfaces real defects — leaks, silent data loss, perf cliffs — plus the UX that "works" but shouldn't ship.

Or install anything from the full list below, or browse via `/plugin` → **Discover** tab.

After installing, run `/reload-plugins` to activate.

### Claude Desktop

Claude Desktop installs skills from a `.zip` upload, not the marketplace. Prebuilt,
upload-ready zips for every skill live in **[`desktop-install-ready/`](desktop-install-ready/README.md)** —
that folder's README lists each skill with its purpose and a one-click download link.
Grab a zip, then in Claude Desktop go to Settings → Capabilities → Skills → **Upload skill**.

### Codex CLI / Codex app

This repo now includes native Codex integration in two forms:

- repo-local skill discovery via `.agents/skills/`
- repo-local Codex marketplace via `.agents/plugins/marketplace.json` and `plugins/*/.codex-plugin/plugin.json`

To use the skills directly from a checked-out repo, open the repo in Codex and type `$` or `/skills`. Codex will discover the skills from `.agents/skills` automatically.

To test the packaged Codex plugins locally, restart Codex after cloning the repo, open the plugin directory, and look for the **Carl Tools** local marketplace sourced from this repo.

### Codex web / cloud

Repo-local skills under `.agents/skills/` travel with the repository and are available when Codex checks out the repo in a cloud task.

A few skills are intentionally local-machine-centric and work best in CLI/app sessions on your own machine, not generic cloud containers. Examples: `chezmoi-drift`, `profile-me`, and parts of `handle-pr`.

Cloud-friendlier skills: `pre-mortem`, `trust-audit`, `support-storm`, `first-contact`, `parallel-isolated-app-testing` and `second-opinions`.

## Usage

Skills are namespaced by plugin name. Invoke directly or let Claude trigger them automatically:

```
/pre-mortem:run
/empathy-audit:run
```

Or just ask naturally — Claude will invoke the right skill based on context.

## Skills

⭐ = Carl's favorites — start here.

### For Anyone

Broadly useful, no coding required — point them at a plan, your contacts, or a person and go.

| Skill | |
|-------|---|
| **contacts-unify** | Clean up the mess of contacts scattered across Apple, Google, and your phone — dedupe the duplicates and make it make sense again.<br><sub>`/plugin install contacts-unify@carl-tools`</sub> |
| ⭐ **pre-mortem** | Before you commit to a plan, find out how it could fail — a team of critics stress-tests it and hands you the real risks, ranked.<br><sub>`/plugin install pre-mortem@carl-tools`</sub> |
| **profile-me** | Turn your digital footprint into a profile any AI can read, so assistants actually get you from the first message.<br><sub>`/plugin install profile-me@carl-tools`</sub> |
| **research-person** | Get the rundown on someone before a meeting or intro — pulled from public sources into one tidy, confidence-rated brief.<br><sub>`/plugin install research-person@carl-tools`</sub> |
| ⭐ **second-opinions** | About to make a big call? Get a gut-check from a second AI with a different perspective before you commit.<br><sub>`/plugin install second-opinions@carl-tools`</sub> |
| ⭐ **wide-open-brainstorm** | A room full of idea generators, serious and playful, riffing on your product or problem from every angle.<br><sub>`/plugin install wide-open-brainstorm@carl-tools`</sub> |

### Product & Launch

Stress-test a product before real users do: onboarding, trust, support load, launch readiness.

| Skill | |
|-------|---|
| **first-contact** | See where brand-new users get confused, stuck, or give up during setup — before they actually do.<br><sub>`/plugin install first-contact@carl-tools`</sub> |
| **launch-sequence** | Run the whole pre-launch gauntlet in one pass and get a single go / caution / no-go call.<br><sub>`/plugin install launch-sequence@carl-tools`</sub> |
| **post-mortem** | Something broke? Reconstruct what really happened, find the root cause, and turn the lesson into a lasting fix.<br><sub>`/plugin install post-mortem@carl-tools`</sub> |
| **scope-hammer** | Drowning in ideas? Cut a bloated wishlist down to the smallest thing you can actually ship.<br><sub>`/plugin install scope-hammer@carl-tools`</sub> |
| **status-copy-trust-audit** | Make your app's status and progress messages say what actually changed, so people trust what they're reading.<br><sub>`/plugin install status-copy-trust-audit@carl-tools`</sub> |
| **support-storm** | Preview the support emails, refunds, and 1-star reviews a launch will trigger, then fix the causes first.<br><sub>`/plugin install support-storm@carl-tools`</sub> |
| ⭐ **trust-audit** | Find the moments your product feels sketchy — surprise charges, scary permissions, silent failures — and close the trust gaps.<br><sub>`/plugin install trust-audit@carl-tools`</sub> |

### Dev Workflow

Tools for the day-to-day of writing, reviewing, and releasing code.

| Skill | |
|-------|---|
| **agent-log-forensics** | Mine your AI coding sessions for the habits that quietly waste time, and turn them into workflow fixes.<br><sub>`/plugin install agent-log-forensics@carl-tools`</sub> |
| **changelog-writer** | Turn a pile of git commits into a changelog your users will actually understand.<br><sub>`/plugin install changelog-writer@carl-tools`</sub> |
| **chezmoi-drift** | Catch when your dotfiles have drifted from what's committed, and when a skill install silently broke.<br><sub>`/plugin install chezmoi-drift@carl-tools`</sub> |
| **decision-log** | Capture why you picked this over the alternatives, so future-you never has to re-litigate the choice.<br><sub>`/plugin install decision-log@carl-tools`</sub> |
| **dependency-pinning** | Lock dependencies to safe, pinned versions with cooldowns so a bad release can't blindside you.<br><sub>`/plugin install dependency-pinning@carl-tools`</sub> |
| **django-smoke-alarm** | Sort a noisy Django security scan into what's actually dangerous, what's hygiene, and what's a false alarm.<br><sub>`/plugin install django-smoke-alarm@carl-tools`</sub> |
| ⭐ **empathy-audit** | Review a feature through four sets of eyes — user, machine, developer, support — to catch what plain code review misses.<br><sub>`/plugin install empathy-audit@carl-tools`</sub> |
| **handle-pr** | Hand off your PR review comments and let it implement, test, and reply to every thread on its own.<br><sub>`/plugin install handle-pr@carl-tools`</sub> |
| **parallel-isolated-app-testing** | Test an app many ways at once without the runs tripping over each other's shared state.<br><sub>`/plugin install parallel-isolated-app-testing@carl-tools`</sub> |
| **ralph-loop** | Run repeatable multi-AI hardening passes over a codebase to shake out bugs and weak spots.<br><sub>`/plugin install ralph-loop@carl-tools`</sub> |
| **release-operator** | Drive a release end to end — version, build, publish — and confirm the install actually works afterward.<br><sub>`/plugin install release-operator@carl-tools`</sub> |
| **remote-host-verifier** | Prove a fix works on the real remote machine, not just your laptop, before you call it done.<br><sub>`/plugin install remote-host-verifier@carl-tools`</sub> |
| **visual-qa-loop** | Catch visual regressions with repeatable before/after screenshots and tight review notes.<br><sub>`/plugin install visual-qa-loop@carl-tools`</sub> |

## Managing plugins

```
# Disable without uninstalling
/plugin disable handle-pr@carl-tools

# Re-enable
/plugin enable handle-pr@carl-tools

# Uninstall
/plugin uninstall handle-pr@carl-tools

# Update marketplace listings
/plugin marketplace update carl-tools
```

## Generated vs hand-edited files

**Hand-edited:**
- `skills/*/SKILL.md`
- `README.md` prose outside the generated skills table
- `CLAUDE.md`
- `.claude-plugin/*`

**Generated by `python3 scripts/sync_codex_packaging.py`:**
- `.agents/skills/*`
- `.agents/plugins/marketplace.json`
- `plugins/*/.codex-plugin/plugin.json`
- `skills/*/agents/openai.yaml`
- `skills/*/assets/icon.svg`
- the `## Skills` section in `README.md`
- `desktop-install-ready/*.zip` and `desktop-install-ready/README.md`

If you edit generated files manually, the sync script will cheerfully overwrite your artisanal snowflake.

## Codex-friendly repo layout

```
.agents/skills/                  # Codex repo-local skill discovery
.agents/plugins/marketplace.json # Codex local marketplace catalog
plugins/<skill>/.codex-plugin/   # One Codex plugin per skill
skills/<skill>/agents/openai.yaml# Codex app metadata
skills/<skill>/assets/icon.svg   # Codex icon asset
scripts/sync_codex_packaging.py  # Regenerates Codex packaging artifacts
```

After adding or renaming a skill, run:

```bash
python3 scripts/sync_codex_packaging.py
```

## Scope

Install at user scope (default, available across all projects) or project scope:

```
# Project scope — adds to .claude/settings.json, shared with team
claude plugin install pre-mortem@carl-tools --scope project
```

## Pre-configure for a team

Add to your project's `.claude/settings.json` to prompt teammates to install on first run:

```json
{
  "extraKnownMarketplaces": {
    "carl-tools": {
      "source": {
        "source": "github",
        "repo": "carlkibler/agent-skills"
      }
    }
  }
}
```

## Local development

Test locally without installing from GitHub:

```bash
claude --plugin-dir ./skills/pre-mortem
```

Run helper contract tests after editing `bin/agent`:

```bash
tests/test_agent.sh
```
