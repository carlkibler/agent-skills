---
name: profile-me
description: "Build a personal AI profile of the user — who they actually are, not their resume. Draws from conversation history, dotfiles, shell config, notes, git identity, and memory files. Default output is a Personal Portrait and compact System Prompt. Professional Portrait is opt-in only. Use when asked to profile me, build my AI profile, get to know me, make a system prompt about me, or help another AI understand who I am."
---

# Profile Me

Build an honest portrait of the user as a *person* — not a resume summary, not a list of their
tech stack. The default goal is personality, not credentials.

Most developers who run this skill have conversation histories dominated by coding work. That
data is real but misleading as a personality source — it's what they did at the desk, not who
they are. The skill must look *through* the work to find the person.

Inspired by Orson Scott Card's Speaker for the Dead: tell the truth about who someone is —
not to flatter, not to judge, but to understand and serve.

**Core principles:**

- **Person over practitioner.** Unless a professional portrait is explicitly requested, keep
  work out of it. Technical skills, frameworks, and job history are not the subject.
- **Truth over comfort, kindness over cruelty.** Report what the evidence shows. Frame it with
  respect. Never sanitize away a real pattern, but never weaponize one either.
- **Evidence-based.** Every claim should trace to observable data. If it can't be evidenced,
  flag it as inference and explain why.
- **Short and true beats long and restated.** A portrait that captures three real things is more
  useful than one that pads with professional biography. If the evidence is thin on a dimension,
  say so and move on.

## When to Use

Trigger on requests like:

- "profile me", "build my profile", "get to know me"
- "create my AI profile" or "build my context document"
- "make a system prompt about me"
- "help another AI get to know me"
- "build a working-with-me guide"
- "what do you know about me"

**Not this skill:** "update my resume", "write my LinkedIn bio", "describe my tech stack" — those are professional documents, use a different prompt or request the Professional Portrait explicitly.

## Data Collection

### Privacy Gate

Before reading ANY data, briefly tell the user what categories of data will be examined (conversation history, shell config, git config, project files, SSH config, AWS config) and ask: **"Anything you'd like me to skip?"**

This is a one-time check, not a per-file approval. Most users will say "go ahead" but some may exclude SSH config, AWS accounts, or specific directories. Respect exclusions completely — don't reference excluded data even indirectly.

### Phase 1: Discovery

Before analyzing anything, map what data sources exist. Not all users will have all sources.
Run discovery in parallel where possible.

**Source 1: AI Agent Conversation History**

Probe for each and read what exists. Don't assume any particular agent is installed.

| Agent | Path | Format | User message field |
|-------|------|--------|-------------------|
| Claude Code | `~/.claude/history.jsonl` | JSONL | `display` |
| Aider | `**/.aider.chat.history.md` (per-project) | Markdown | lines after `#### human` |
| OpenCode | `~/.local/share/opencode/opencode.db` | SQLite | `message` table, `data` col (JSON) |
| Copilot Chat (VS Code) | `~/Library/Application Support/Code/User/globalStorage/github.copilot-chat/**/*.jsonl` | JSONL | `v.requests[].message` |
| Gemini CLI | `~/.gemini/` | metadata only | no conversation data stored locally |
| Cursor | `~/Library/Application Support/Cursor/User/globalStorage/` | SQLite/JSONL | similar to VS Code |
| Windsurf | `~/Library/Application Support/Windsurf/User/globalStorage/` | SQLite/JSONL | similar to VS Code |
| Continue.dev | `~/.continue/` | JSON sessions | `messages[].content` where `role=user` |
| ChatGPT (desktop) | `~/Library/Application Support/ChatGPT/` | SQLite | varies |
| Amazon Q | `~/.aws/amazonq/` | varies | varies |

Discovery commands:
```bash
# Check which agents have data
ls ~/.claude/history.jsonl 2>/dev/null && echo "claude-code"
find ~/dev -name ".aider.chat.history.md" -maxdepth 4 2>/dev/null
ls ~/.local/share/opencode/opencode.db 2>/dev/null && echo "opencode"
ls "~/Library/Application Support/Code/User/globalStorage/github.copilot-chat/" 2>/dev/null && echo "copilot-chat"
ls ~/.continue/ 2>/dev/null && echo "continue"
```

**Source 1b: Claude Code Environment**
```
~/.claude/CLAUDE.md                          # Global instructions — personality, preferences, rules
~/.claude/settings.json                      # Tool preferences, model choices
~/.claude/projects/*/memory/                 # Per-project memories (feedback, user, project, reference types)
~/.claude/projects/*/memory/MEMORY.md        # Memory indexes
~/.claude/agents/                            # Custom agent definitions
~/.claude/skills/                            # Installed skills
~/.claude/bin/                               # Custom scripts and tools
```

**Source 2: Personal Expression (prioritize these over work repos)**
```
~/dev/me/ (or personal equivalent)          # Personal/side projects — names, themes, what they chose to build
~/.local/share/chezmoi/ or ~/dotfiles/      # Dotfiles — configuration as aesthetic choice
~/cloud/ or ~/notes/ or ~/Documents/        # Personal notes, writing, Obsidian vaults
~/.zshrc or ~/.bashrc                       # Aliases and functions — naming reveals personality
~/dev/me/*/README.md                        # Personal project READMEs (distinct from work)
```

**Skip for personal profile:** Work repositories (`~/dev/` excluding personal dir), work project READMEs, CI configs, deployment files. These describe the job, not the person.

**Source 3: Shell & System Configuration**
```
~/.bashrc or ~/.zshrc                        # Shell config — aliases, functions, env vars, PATH
~/.bash_profile or ~/.zprofile               # Login shell config
~/.gitconfig                                 # Git identity, aliases, preferences
~/.ssh/config                                # Connection patterns (work vs personal hosts)
~/.aws/config                                # Cloud account structure (if applicable)
```

**Source 4: Conversation History Analysis**

Harvest user messages from every agent source found in Source 1. Each format requires different extraction:

- **Claude Code** (`history.jsonl`): `jq -r 'select(.display != null and (.display | length) > 20) | .display' ~/.claude/history.jsonl`
- **Aider** (`.aider.chat.history.md`): extract lines after `#### human` markers
- **OpenCode** (SQLite): `sqlite3 ~/.local/share/opencode/opencode.db "SELECT data FROM message"` then parse JSON for role=user
- **Copilot Chat** (JSONL): parse `v.requests[].message` from session files
- **Continue.dev**: parse `messages` arrays from session JSON files, filter `role == "user"`

Combine all sources into a single corpus before analysis. Deduplicate by content where the same text appears across agents. Note which agents were most active — tool diversity is itself a signal.

**Extracting personality from work-heavy histories**

Most developers' conversation histories are 90%+ coding requests. Don't profile the work — look for the person *between* the work. Specifically look for:

- **Off-task moments** — when they stop asking about code and say something else entirely
- **Named frustrations** — what they express irritation about (process? quality? ambiguity? people?)
- **Humor** — dry, self-deprecating, absurdist, pedantic? Look at how they frame problems
- **What they name things** — project names, function names, variable names, alias names reveal aesthetic sense
- **How they handle being wrong** — defensive, curious, matter-of-fact, amused?
- **What triggers verbosity** — a terse person who suddenly writes three paragraphs is showing you what matters to them
- **Correction patterns** — "no, that's not what I meant" style reveals communication expectations
- **What they tolerate vs. what they push back on** — the line between patience and impatience
- **Energy signatures** — excitement markers, relief ("perfect"), disappointment ("ugh"), satisfaction ("exactly")
- **Delegation style** — terse goals? detailed specs? thinking-out-loud as they type?

For the personal portrait, **weight these signals more heavily than project counts or framework choices.** A list of technologies is a LinkedIn section. The texture of how someone talks is a personality.

Extract from the combined corpus:
- **Message length distribution** — terse vs. verbose; and *when* each occurs
- **Vocabulary patterns** — formality level, humor frequency, domain bleed from personal interests
- **Emotional signals** — caps usage, punctuation patterns, frustration/excitement markers
- **Typo patterns** — fast and impulsive vs. careful and deliberate
- **Agent preference patterns** — what tasks they route to which tool (reveals mental model of AI)

### Phase 2: Deep Reading

Read all discovered sources. Use subagents to parallelize across categories:
- Agent 1: Memory files and MEMORY.md indexes (feedback, user-type, and project memories — skip reference-only)
- Agent 2: Global CLAUDE.md/AGENTS.md only (not per-project — those describe work, not person)
- Agent 3: Shell/git/system configuration (aliases, functions, git identity, dotfiles aesthetic)
- Agent 4: Conversation history — **personality pass** (see sampling guidance below)
- Agent 5: Personal notes, Obsidian vault, personal writing, personal project READMEs
- Agent 6: Personal side projects — names, themes, what they chose to build unprompted

**Conversation history sampling for personality:**
Sample broadly in time (beginning, middle, recent), but filter aggressively for personality signals.
Skip: pure code requests, bug descriptions, "add X to Y", pasted content.
Keep: opinions, frustrations, humor, naming choices, how they frame problems, off-task remarks, how they respond to errors, what they thank you for, what they push back on.
Target 40-80 messages that would survive the filter "does this tell me something about who this person is?"

## Analysis Framework

After collecting data, analyze across these dimensions. See `references/analysis-framework.md`
for the full analytical rubric with questions and evidence patterns for each dimension.

### Dimensions

**For personal portrait (default):** use dimensions 3–7 only. Dimensions 1–2 belong in the Professional Portrait.

1. **Professional Identity** *(Professional Portrait only)* — Role, seniority, domain expertise, career trajectory
2. **Technical Profile** *(Professional Portrait only)* — Languages, frameworks, infrastructure, architecture patterns
3. **Communication Style** — Formality, verbosity, humor, emotional expression, delegation patterns
4. **Cognitive Style** — How they approach problems, make decisions, handle uncertainty, what excites vs. bores them
5. **Values & Priorities** — What they actually optimize for (vs. what they say they do), what frustrates them, what impresses them
6. **Creative & Personal** — Side projects, hobbies, interests, aesthetic preferences, what they build when nobody's watching
7. **Relational Patterns** — How they interact with collaborators (human or AI), how they give feedback, what they expect, what they appreciate

### Bias Guardrails

**During analysis, actively guard against:**

- **Halo effect:** A person's technical skill doesn't mean they're right about everything. Note
  areas of strength AND areas where evidence is thin.
- **Confirmation bias:** Don't cherry-pick messages that support a narrative. If someone is
  usually terse but occasionally writes long thoughtful messages, report both patterns.
- **Flattery creep:** It is tempting to write profiles that read like recommendation letters.
  Resist. Report patterns as patterns. "Prefers to work fast and sometimes skips testing
  steps" is more useful than "moves at an impressive pace."
- **Deficit framing:** Don't frame neutral traits as problems. Terse communication is a style,
  not a flaw. Heavy side-project activity is a pattern, not workaholism (unless there's
  evidence of burnout).
- **Gender/identity assumptions:** Use the pronouns and identity markers the person uses in
  their own writing. If unclear, use their name or "they."
- **Projection of values:** If someone doesn't write tests, don't assume they don't value
  testing — maybe they just test differently. Let evidence speak.
- **Recency bias:** Don't over-weight recent conversations. Someone's most active project this
  month may not reflect their long-term identity.

## Output Documents

**Default output:** Personal Portrait + System Prompt. Always produce these two unless the user says otherwise.

Offer the Working-With-Me Guide and Professional Portrait as opt-in extras — mention them briefly after presenting the defaults. Do not produce a Professional Portrait unless explicitly requested.

Store outputs in the user's preferred temp/output directory.

### 1. Personal Portrait (`portrait-personal.md`)

The "Speaker for the Dead" document. Who this person really is — not their resume, their *self*.

**Structure:**
- Opening: 2-3 sentences that capture the essence (the "if you only read this" summary)
- How they think — cognitive patterns, decision-making style, what energizes vs. drains them
- What they care about — values evidenced by behavior, not stated values; the gap between the two if it exists
- The texture — humor, aesthetic taste, naming choices, the small things that make them *them*
- What they make when nobody's asking — personal projects, creative output, things they chose unprompted
- Closing: The through-line — what connects all of this into a coherent person

**Do not include:** tech stack, job history, professional credentials, languages/frameworks. Those belong in the Professional Portrait. If a work pattern is genuinely revealing about personality (e.g., obsessive perfectionism about performance), note the personality trait, not the technical fact.

**Critical writing prompts:**

- **Find the central tension.** Every person has a defining contradiction — two forces that
  coexist and drive them. The person who starts 45 projects but writes "I want stability." The
  person who moves fast but insists on dry-run defaults. Name it explicitly. The tension IS the
  person — don't resolve it, honor it.
- **Identify the most revealing single data point.** Across all the evidence, one fact will tell
  you more about this person than any paragraph of analysis. An essay title, a shell function
  name, a project they keep coming back to, a correction they made. Find it and let it anchor
  the portrait.
- **Longer messages are diagnostic.** When a typically terse person writes at length, pay
  attention to *what* triggers verbosity. It usually reveals what they're protecting or what
  genuinely excites them.

**Tone:** Warm but honest. Like a close friend who knows you well enough to be truthful. Never
sycophantic, never clinical.

### 2. Professional Portrait (`portrait-professional.md`) *(opt-in only)*

**Do not produce this by default.** Only generate if the user explicitly requests it (resume help, LinkedIn, interview prep, "what's my tech stack", etc.).

The document a hiring manager, recruiter, or professional contact should read.

**Structure:**
- Role and positioning (current + aspirational)
- Technical depth — languages, frameworks, cloud, architecture, with evidence of depth level
- Domain expertise — industries, compliance frameworks, specialized knowledge
- Leadership signals — team building, mentoring, architectural decision-making
- Project portfolio — work AND personal, showing range and initiative
- Working style — how they operate day-to-day, what kind of team/org they thrive in

**Proficiency calibration:** For each technical area, assign an evidence-based depth level:

- **Expert:** Daily use, custom tooling, deep configuration, architectural decisions.
  Evidence: high session counts, detailed CLAUDE.md, performance optimization work.
- **Proficient:** Regular use, comfortable across the surface area, some customization.
  Evidence: moderate session counts, working configurations, shipped projects.
- **Familiar:** Has used it, can navigate it, reaches for it when appropriate.
  Evidence: occasional sessions, follows existing patterns rather than creating new ones.

Always show the evidence for the rating. "Expert — 1,136 sessions, custom management commands,
startup optimization from 5s to 1.2s" is credible. "Expert" alone is not.

**Tone:** Professional but not stiff. Third-person. Backed by evidence. Useful for resume
updates, LinkedIn, cover letter context, or interview prep.

### 3. Working-With-Me Guide (`working-with-me.md`)

Direct instructions for an AI assistant or collaborator.

**Structure:**
- Communication quick-reference (how they talk, what signals mean what)
- Response calibration (length, tone, when to be proactive vs. wait)
- Technical environment (key tools, directory structure, common commands)
- Do's and Don'ts (specific, evidenced, actionable)
- What impresses them / what annoys them
- Domain knowledge expected

**Tone:** Imperative, second-person, like agent instruction files (CLAUDE.md/AGENTS.md). Optimized for AI consumption.

### 4. System Prompt (`system-prompt.md`)

A compact (under 1000 word) version of the Working-With-Me Guide, formatted for direct injection into
an AI assistant's system prompt. Everything essential, nothing wasted.

**Structure:** Single flowing document with short sections. No tables or complex formatting.
Must work in any LLM's system prompt field.

## Workflow

### Step 1: Discover
Run Phase 1 discovery. Report what sources were found and their sizes. Ask the user if there
are additional data sources to include (e.g., specific directories, exported chat logs, notes).

### Step 2: Collect
Run Phase 2 deep reading with parallel subagents. This is the most token-intensive step.

### Step 3: Analyze
Apply the analysis framework across all seven dimensions. Compile evidence for each finding.
Flag inferences that are weakly supported.

### Step 4: Draft
Write all requested output documents. Apply bias guardrails during writing.

### Step 5: Present
Share the outputs with the user. Invite feedback. Note that the profile is a snapshot — it
reflects who they are *now*, from the evidence available, and should be updated over time.

### Step 6: Iterate
If the user identifies inaccuracies or missing dimensions, update the documents. The user
knows themselves better than any analysis — their corrections are data too.

## Tips for Effective Profiles

- **Personal projects tell the story; work projects describe the job.** What someone builds
  unprompted — the names they choose, the problems they decide are worth solving, the aesthetic
  choices they make when there's no deadline — reveals character. A work repo tells you their
  employer's stack. A personal repo tells you something real.
- **Patterns over instances.** A single angry message doesn't mean someone is angry. Look for
  patterns across dozens or hundreds of interactions.
- **The gap between stated and revealed preferences is interesting.** If someone says they value
  testing but their history shows they skip it when under pressure, that tension is worth
  noting (gently).
- **Quantify where possible.** "Works across many projects" is less useful than "5,988
  conversation entries across 50+ projects, with the top 3 accounting for 52% of activity."
- **Name the through-line.** Every person has one — the thread that connects their disparate
  activities into a coherent identity. Finding it is the difference between a list of facts
  and a portrait.

## Model Tier Recommendations

The personal portrait quality depends heavily on the writing model's ability to synthesize
narrative from evidence. Use the best available model tier for each task:

- **Flagship / reasoning-tier models** (e.g., Opus, GPT-4o, Gemini Ultra, o3): Best for the
  personal portrait and through-line identification. These produce the narrative cohesion and
  insight density the portrait demands.
- **Mid-tier models** (e.g., Sonnet, GPT-4o-mini, Gemini Flash Pro): Good for the professional
  portrait, working-with-me guide, and system prompt — structured documents where clarity
  matters more than voice.
- **Fast / lightweight models** (e.g., Haiku, Gemini Flash, Cerebras): Suitable for data
  collection, discovery scripts, and stats generation. Save expensive context for synthesis,
  not scanning.

When running all four documents, consider dispatching subagents with model overrides: flagship
tier for the personal portrait, mid-tier for the other three.
