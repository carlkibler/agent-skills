---
name: research-person
description: "Research a person from public sources into a confidence-marked Obsidian People dossier."
display_name: "Research Person"
brand_color: "#0EA5E9"
local_only: true
group: "For Anyone"
usage: "/research-person:run <name> [disambiguators]"
summary: "Get the rundown on someone before a meeting or intro — pulled from public sources into one tidy, confidence-rated brief."
default_prompt: "Research the named person(s) from public sources and create or update their People note in my Obsidian vault, with confidence markers, cross-links, and a raw-research dump in my research folder."
---

# Research Person

Turn a name into a useful, honest **People dossier** in the user's notes vault — the kind of note that makes the next
conversation, intro, or working relationship go better. Built for a personal relationship KB: real friends and
colleagues, researched from **public sources only**, for the user's own private notes.

**Paths below are examples from the original setup.** On first use, confirm with the user: the vault root
(e.g. `~/cloud/gdrive/obsidian-vault-carlkibler/`), the People folders for work vs personal contacts
(e.g. `halo/People/` and `People/`), and the raw-research folder (e.g. `~/dev/agent-notes/<work|me>/people-research/`).
If no vault exists, write one markdown file in the current directory instead and say so.

This is the generalized version of a clean OSINT pass: resolve identity → gather public footprint →
mark confidence → write it where it belongs without trampling what's already there.

## When to use

- "Research <name> and fill out their People note"
- "Build a dossier on these folks: <list of names>"
- Refreshing a stale People note before a meeting, intro, or 1:1
- A new colleague/friend you want context on before working together

## When NOT to use

- A public figure for a general report → use a general research workflow (e.g. `deep-research`) instead (this skill writes to the *People* KB)
- Building a profile of the user themselves → use `profile-me`
- You only need one fact (current employer) → just search; don't spin up the whole dossier

## Ethics & guardrails (read once, apply always)

- **Public sources only.** Things the person has published or that are openly indexed. No paywalled
  background-check services, no scraping behind logins you'd need to deceive to pass, no pretexting.
- **For the user's private KB**, to support real relationships — not surveillance of strangers. If the named
  person isn't someone the user plausibly knows or works with, pause and confirm before researching.
  Don't research minors; don't research someone the user hasn't named.
- **Local and private.** Notes and raw dumps stay in the user's vault. Don't publish them, post them, or put them in a shared or public repo. Contact details go in only if the user already has them or the person publishes them openly.
- **Contain sensitive material.** Home address, family members, health, finances, religion, politics,
  legal history — even when public — go in a clearly-fenced `## Sensitive` block, each line marked
  `⚠️`, never in the orientation blurb or frontmatter. If it isn't relationship-relevant, omit it.
- **Identity confidence is a first-class output.** A confidently-written note about the *wrong* person is
  the main failure mode. Always state how sure you are it's the right individual.

---

<process>

## Phase 0 — Disambiguate before researching

1. Take the name plus any **disambiguators** the user gives: employer, city, role, email, a LinkedIn/GitHub/site
   URL, "the one who…", mutual company.
2. **Check the vault first.** If a note already exists, that note IS the source of truth for who this is —
   read it, reuse its identity, and update in place (Phase 4 routing).
   - Work: `<vault>/<work-folder>/People/<Full Name>.md` (e.g. `halo/People/`)
   - Personal: `<vault>/People/<Full Name>.md`
3. If the name is common (e.g. "Mike Smith") and there are **no disambiguators and no existing note**,
   ask the user for one or two before burning a research pass. Guessing wrong is worse than asking.
4. For a batch, run people **in parallel** (one research effort each) but keep their notes separate.

## Phase 1 — Gather the public footprint

Cast wide, then verify. Aim to answer: *who they are, what they do, where they've been, what they've made,
how the user knows them, and what's useful for the relationship.*

Search/fetch angles (skip what doesn't apply):
- **Identity & current role** — employer, title, location. Cross-check 2+ sources before stating as fact.
- **Professional history** — past roles, companies, education. LinkedIn, company About pages, bios.
- **Builders' trail** — GitHub/GitLab, personal site/blog, Stack Overflow, npm/PyPI, patents.
- **Writing & speaking** — talks, papers (Scholar/academia.edu), podcasts, posts, interviews.
- **Public social presence** — X/Twitter, Mastodon, LinkedIn, Instagram/YouTube *if public and relevant*.
- **News & affiliations** — press mentions, boards, orgs, communities, open-source projects.
- **Shared context** — mutual employers/companies already in the vault, mutual people, overlapping history.

Tooling notes:
- Default to the available web search and page-fetch tools. For **JS-heavy or fetch-blocked sources** (LinkedIn, academia.edu,
  Bandcamp/Spotify, some company sites) use a browser-automation tool if one is available and pull `innerText`,
  `<meta>` tags, and JSON-LD — that's where the verifiable structured data lives.
- When a thread looks deep or multi-source, you can delegate the heavy searching to parallel subagents (or a
  `deep-research` skill, if installed) and curate their findings into the dossier. This skill owns identity-resolution,
  confidence, routing, and the write; the others are just fan-out engines.
- **Delegation hygiene.** When you fan out research to subagents, instruct each to **return** its findings
  as its final message — never to write files. Only the main run writes (the raw dump *and* the vault note);
  a subagent that tries to write is sandbox-blocked and wastes a turn. Give each a crisp identity anchor and
  the exact structured output shape you want back.
- **Dump raw findings as you go** to the research folder (Phase 4) — URLs, quotes, screenshots. The curated
  note links back to it; never make the user re-run the search to see your evidence.

## Phase 2 — Mark confidence on every non-obvious claim

Per vault convention, tag facts inline:
- **VERIFIED** — stated in a credible source you actually read (cite it).
- **INFERRED** — reasoned from evidence, not stated outright.
- **UNKNOWN** — an open question worth listing (these are valuable; they're the next research).

Plus an explicit **identity confidence** line near the top: `Identity match: HIGH | MEDIUM | LOW` with the
basis (e.g. "matched via GitHub→personal site→employer; photo + city consistent"). If MEDIUM/LOW, say what
would raise it.

## Phase 3 — Compose the dossier

Match the existing People-note shape. Two flavors:

### Work colleague (`halo/People/`) — frontmatter
```yaml
---
aliases: [Full Name, nicknames, handle]
tags: [person, <role/team>, confidential]
companies: [[Company A]], [[Company B]]
updated: YYYY-MM-DD
---
```

### Personal friend (`People/`) — frontmatter (no `confidential`, no work tags)
```yaml
---
aliases: [Full Name, nicknames]
tags: [person, friend]
updated: YYYY-MM-DD
---
```

### Body (both flavors)
```markdown
# Full Name

> One-paragraph orientation: who they are, how the user knows them, the single most useful thing to know.

**Identity match:** HIGH — basis in one line.

## Identity & contact
- Role / employer / location — **VERIFIED** (source)
- Handles: GitHub `x` · site `url` · LinkedIn `url` · X `@x`
- Email / phone — only if the user already has it or it's openly published

## Background
- Career history, education, notable work — confidence-marked, sourced.

## Public presence & work
- Projects, writing, talks, repos — with links.

## How the user knows them / shared context
- Mutual companies [[Company]] · mutual people [[Person]] · overlapping history.

## Conversation hooks
- Genuine, specific things to connect on (interests, recent work, shared people). Not flattery.

## Sensitive (public but handle with care)   ← only if any exists
- ⚠️ item — why it's fenced.

## Open questions
- [ ] Unknown to resolve — **UNKNOWN**

## See also
[[Related person]] · [[Company]]

## Sources
Distilled from: `<raw-research path>` (date). Key public sources: <list>.
```

Keep it honest and skimmable: one idea per line, no padding, no LinkedIn-bio voice.

## Phase 4 — Write it where it belongs (auto-write, but never clobber)

**Routing:**
- Existing note anywhere in the vault → **update that file in place.**
- Else, work/HaloHealth colleague → `halo/People/<Full Name>.md`; personal friend → `People/<Full Name>.md`.
- **LOW identity match → do NOT write a vault note.** Keep the research + ruled-out namesakes in the
  raw-research dump only, and report back asking the user for **one** disambiguator (city, employer, a profile
  URL, or "the one who…"). A confident note about the *wrong* person is the exact failure this skill exists
  to avoid. Promote it to a real People note once confidence reaches MEDIUM+ or the user confirms the identity.
  (Exception: if a vault note already exists, leave it and just append the open question.)
- Genuinely ambiguous and no signal → ask the user which.

**Raw research dump (always):**
Use the raw-research folder confirmed in setup. Example layout (adjust to the user's):
- Work → `<raw-research>/work/people-research/<name-slug>/`.
- Personal → `<raw-research>/me/people-research/<name-slug>/`.
- Save `findings.md` (URLs + quotes + confidence) and any screenshots/exports there.

**Merge rule — preserve existing content:**
- Personal notes are often **freeform logs / 1:1 notes**. Do **not** overwrite them. Read the file, then
  **insert a `## Background (researched <date>)` dossier section** (and the other dossier sections) *above
  or below* the existing log, leaving every dated entry and human-written line intact.
- For an existing structured note, **enhance in place** — update stale facts, add new findings, bump
  `updated:`, append to Open questions. Never drop the user's hand-written lines.
- Always finish by updating `updated:` / adding a `(researched YYYY-MM-DD)` marker so refreshes are visible.

**Cross-link both ways:** link every Company and Person the note touches; redlink `[[Like This]]` for
named-but-missing entities (marks a note worth creating). Weave into hubs like [[_People Directory]] when
present.

## Phase 5 — Report back

Tell the user, per person: where the note landed (path), **identity confidence**, the 3–5 most useful new
things found, anything fenced as sensitive, and the top open questions. For a batch, a one-line-per-person
summary table.

</process>

## The handoff version

If the user wants to hand this to a friend, a colleague, or a different agent/tool that can't run this skill,
give them the standalone copy-paste prompt in [`references/handoff-prompt.md`](references/handoff-prompt.md).
It carries the same methodology and guardrails without the vault-write step.
