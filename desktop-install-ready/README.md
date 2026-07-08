# Desktop-install-ready skills

Prebuilt `.zip` bundles of every skill, ready to upload to **Claude Desktop**.

Each zip unpacks to `<skill>/SKILL.md` (name + description in YAML
frontmatter), plus any `scripts/`, `references/`, and `assets/`. The
Codex-only `agents/` dir is excluded — Claude Desktop doesn't use it.

## Install

1. Click **Download** for the skill you want.
2. In Claude Desktop: Settings → Capabilities → Skills → **Upload skill**.
3. Select the `.zip`.

## Skills

| Skill | Purpose | Download |
|-------|---------|----------|
| **agent-log-forensics** | Turn local and remote agent session logs into workflow improvements | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/agent-log-forensics.zip) |
| **changelog-writer** | Transform git commits into user-facing changelog entries segmented by audience | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/changelog-writer.zip) |
| **chezmoi-drift** | Audit chezmoi dotfiles for drift and broken skill installs | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/chezmoi-drift.zip) |
| **contacts-unify** | Multi-source contact dedupe with a provenance-aware review UI, plus optional iMessage-driven dossier collection | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/contacts-unify.zip) |
| **decision-log** | Record decisions with rationale and rejected alternatives for future agent context | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/decision-log.zip) |
| **dependency-pinning** | Audit projects for SHA-pinning + release cooldowns; fix on approval | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/dependency-pinning.zip) |
| **django-smoke-alarm** | Triage Django security smoke checks into real risks, hygiene, and false positives | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/django-smoke-alarm.zip) |
| **empathy-audit** | Four-lens empathy review: user, machine, developer, support | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/empathy-audit.zip) |
| **first-contact** | Red-team onboarding and first-run experience for abandonment traps | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/first-contact.zip) |
| **fleet-mesh** | Verify every host can ssh/et every other host, and catch the hygiene problems that quietly break it | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/fleet-mesh.zip) |
| **handle-pr** | Autonomously address PR review comments end-to-end | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/handle-pr.zip) |
| **launch-sequence** | Full pre-launch gauntlet with GO/CAUTION/NO-GO verdict | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/launch-sequence.zip) |
| **parallel-isolated-app-testing** | Design parallel isolated test lanes for apps with shared local state | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/parallel-isolated-app-testing.zip) |
| **post-mortem** | Blameless post-mortem that feeds learnings back into your skill collection | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/post-mortem.zip) |
| **pre-mortem** | Multi-agent project pre-mortem — ranked risks with mitigations | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/pre-mortem.zip) |
| **profile-me** | Build a portable AI profile from your digital footprint | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/profile-me.zip) |
| **ralph-loop** | Repeatable multi-LLM hardening sweeps for codebases | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/ralph-loop.zip) |
| **release-operator** | End-to-end release execution with post-release install verification | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/release-operator.zip) |
| **remote-host-verifier** | Compare local and remote host behavior before declaring a tool fixed | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/remote-host-verifier.zip) |
| **research-person** | Research a real person from public sources and write/update their Obsidian People note | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/research-person.zip) |
| **scope-hammer** | Compress brainstorm output into MVP scope with DELETE/MOCK/ALREADY EXISTS/SHIP classification | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/scope-hammer.zip) |
| **second-opinions** | Get a second opinion from a different AI on complex changes | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/second-opinions.zip) |
| **status-copy-trust-audit** | Make status/update/doctor output explain exactly what changed and why | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/status-copy-trust-audit.zip) |
| **support-storm** | Simulate the support emails and refunds a launch will generate | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/support-storm.zip) |
| **trust-audit** | Audit a product's trust surface: permissions, privacy, billing, and silent failures | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/trust-audit.zip) |
| **vesta-penates** | Operate vesta host, media stack, nginx/Tailscale/Cloudflare, and restore runbooks | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/vesta-penates.zip) |
| **visual-qa-loop** | Repeatable visual screenshots and review notes for UI changes | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/visual-qa-loop.zip) |
| **wide-open-brainstorm** | Multi-model brainstorming room for product strategy — serious plus whimsical, multi-altitude ideation | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/wide-open-brainstorm.zip) |
| **wifi-qr** | Generate a WiFi QR code PNG | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/wifi-qr.zip) |

---

_Generated by `scripts/build_desktop_zips.py` (run automatically by
`scripts/sync_codex_packaging.py`). After editing a skill, rebuild with:_

```bash
python3 scripts/build_desktop_zips.py          # all skills
python3 scripts/build_desktop_zips.py wifi-qr  # one skill
```
