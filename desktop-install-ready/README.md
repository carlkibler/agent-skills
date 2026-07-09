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

⭐ = Carl's favorites — start here.

### For Anyone

Broadly useful, no coding required — point them at a plan, your contacts, or a person and go.

| Skill | Purpose | Download |
|-------|---------|----------|
| **contacts-unify** | Clean up the mess of contacts scattered across Apple, Google, and your phone — dedupe the duplicates and make it make sense again. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/contacts-unify.zip) |
| ⭐ **pre-mortem** | Before you commit to a plan, find out how it could fail — a team of critics stress-tests it and hands you the real risks, ranked. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/pre-mortem.zip) |
| **profile-me** | Turn your digital footprint into a profile any AI can read, so assistants actually get you from the first message. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/profile-me.zip) |
| **research-person** | Get the rundown on someone before a meeting or intro — pulled from public sources into one tidy, confidence-rated brief. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/research-person.zip) |
| ⭐ **second-opinions** | About to make a big call? Get a gut-check from a second AI with a different perspective before you commit. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/second-opinions.zip) |
| ⭐ **wide-open-brainstorm** | A room full of idea generators, serious and playful, riffing on your product or problem from every angle. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/wide-open-brainstorm.zip) |

### Product & Launch

Stress-test a product before real users do: onboarding, trust, support load, launch readiness.

| Skill | Purpose | Download |
|-------|---------|----------|
| **first-contact** | See where brand-new users get confused, stuck, or give up during setup — before they actually do. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/first-contact.zip) |
| **launch-sequence** | Run the whole pre-launch gauntlet in one pass and get a single go / caution / no-go call. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/launch-sequence.zip) |
| **post-mortem** | Something broke? Reconstruct what really happened, find the root cause, and turn the lesson into a lasting fix. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/post-mortem.zip) |
| **scope-hammer** | Drowning in ideas? Cut a bloated wishlist down to the smallest thing you can actually ship. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/scope-hammer.zip) |
| **status-copy-trust-audit** | Make your app's status and progress messages say what actually changed, so people trust what they're reading. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/status-copy-trust-audit.zip) |
| **support-storm** | Preview the support emails, refunds, and 1-star reviews a launch will trigger, then fix the causes first. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/support-storm.zip) |
| ⭐ **trust-audit** | Find the moments your product feels sketchy — surprise charges, scary permissions, silent failures — and close the trust gaps. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/trust-audit.zip) |

### Dev Workflow

Tools for the day-to-day of writing, reviewing, and releasing code.

| Skill | Purpose | Download |
|-------|---------|----------|
| **agent-log-forensics** | Mine your AI coding sessions for the habits that quietly waste time, and turn them into workflow fixes. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/agent-log-forensics.zip) |
| **changelog-writer** | Turn a pile of git commits into a changelog your users will actually understand. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/changelog-writer.zip) |
| **chezmoi-drift** | Catch when your dotfiles have drifted from what's committed, and when a skill install silently broke. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/chezmoi-drift.zip) |
| **decision-log** | Capture why you picked this over the alternatives, so future-you never has to re-litigate the choice. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/decision-log.zip) |
| **dependency-pinning** | Lock dependencies to safe, pinned versions with cooldowns so a bad release can't blindside you. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/dependency-pinning.zip) |
| **django-smoke-alarm** | Sort a noisy Django security scan into what's actually dangerous, what's hygiene, and what's a false alarm. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/django-smoke-alarm.zip) |
| ⭐ **empathy-audit** | Review a feature through four sets of eyes — user, machine, developer, support — to catch what plain code review misses. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/empathy-audit.zip) |
| **handle-pr** | Hand off your PR review comments and let it implement, test, and reply to every thread on its own. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/handle-pr.zip) |
| **parallel-isolated-app-testing** | Test an app many ways at once without the runs tripping over each other's shared state. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/parallel-isolated-app-testing.zip) |
| **ralph-loop** | Run repeatable multi-AI hardening passes over a codebase to shake out bugs and weak spots. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/ralph-loop.zip) |
| **release-operator** | Drive a release end to end — version, build, publish — and confirm the install actually works afterward. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/release-operator.zip) |
| **remote-host-verifier** | Prove a fix works on the real remote machine, not just your laptop, before you call it done. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/remote-host-verifier.zip) |
| **visual-qa-loop** | Catch visual regressions with repeatable before/after screenshots and tight review notes. | [Download](https://github.com/carlkibler/agent-skills/raw/main/desktop-install-ready/visual-qa-loop.zip) |

---

_Generated by `scripts/build_desktop_zips.py` (run automatically by
`scripts/sync_codex_packaging.py`). After editing a skill, rebuild with:_

```bash
python3 scripts/build_desktop_zips.py          # all skills
python3 scripts/build_desktop_zips.py pre-mortem # one skill
```
