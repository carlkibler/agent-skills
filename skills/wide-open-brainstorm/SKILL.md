---
name: wide-open-brainstorm
description: "Run multi-model brainstorming for product strategy and experience design."
display_name: "Wide-Open Brainstorm"
brand_color: "#C87941"
local_only: false
group: "For Anyone"
usage: "/wide-open-brainstorm:run"
summary: "A room full of idea generators, serious and playful, riffing on your product or problem from every angle."
favorite: true
default_prompt: "Run a wide-open brainstorming room for this product idea. Move between big-picture strategy, project-level organization, tactical actions, and whimsical metaphors; then distill the strongest differentiated concepts."
---

# Wide-Open Brainstorm

Run an expansive product/experience brainstorm that is both strategic and playful. Use this skill when the user wants to go wide, pull ideas from multiple perspectives, blend practical/actionable concepts with whimsical metaphors, and discover a product's deeper thesis rather than merely produce a feature list.

## Core stance

Treat the session as a **brainstorming room**: part product strategy, part systems design, part improv, part command-center fantasy, part ruthless distillation.

Optimize for:

- serious ideas with operational leverage;
- whimsical ideas that reveal non-obvious organizing metaphors;
- movement across altitudes: strategic overview, project/group structure, tactical actions;
- concrete next actions without prematurely narrowing the dream;
- a final synthesis that captures the "why," not only the "what."

Avoid:

- staying at one altitude;
- turning the session into immediate implementation planning too soon;
- producing a flat list of features with no thesis;
- letting whimsy become decoration instead of sense-making;
- losing the user's own language and vibe.

## Workflow

### 1. Capture the seed

Restate the user's idea in a richer prompt that preserves their language and expands the intent. Include:

- the core product/problem area;
- the human outcome the user wants;
- the tactical state being managed;
- the strategic/big-picture state being understood;
- the desired emotional/brand flavor;
- explicit permission to be practical, silly, weird, and ambitious.

If the user provided enough direction, proceed without questions. If not, ask one short question about the desired domain or artifact.

### 2. Choose how roles run

Default: every role runs as an in-session subagent. Code-aware roles get the repo; fresh-eyes roles get only the seed brief (no files, no codebase hints), because anchoring context kills divergence. Using an outside CLI for the fresh-eyes roles adds real model diversity, but only after the permission check below.

**External model CLIs (ask first)**

In-session subagents need no extra permission and are the default for every role below.
Launching a separate agent CLI (`claude -p`, `codex exec`, `omp -p`, `pi -p`) is different:
it spends the user's quota and sends project content to that provider. Before the first launch:

1. Read `${XDG_CONFIG_HOME:-$HOME/.config}/agent-skills/external-clis.json` if it exists.
   A CLI listed under `skills.wide-open-brainstorm.allow` or top-level `allow` may run without asking;
   one listed under `deny` (either level) must not run. Skill-level entries win.
2. Otherwise run `command -v claude codex omp pi`, then ask once: which installed CLIs may this
   skill launch, and should the answer apply to this run, always for this skill, or always?
3. For "always", create or update the file (merge; never drop other skills' entries), e.g.
   `{"allow": ["codex"], "deny": [], "skills": {"wide-open-brainstorm": {"allow": ["claude", "codex"]}}}`.
4. Bound every call (`timeout 600 …`). Report which CLI and model actually answered. If none
   ran, say the outside cross-check did not happen rather than presenting subagent output as one.

Equivalent one-shot forms: `claude -p --model <m> "<prompt>"`,
`codex exec -m <m> --sandbox read-only "<prompt>"`, `omp -p --model <m> "<prompt>"`, `pi -p "<prompt>"`.
Prefer a CLI from a different company than the current session for outsider roles.

### 3. Role assignment

Use the **7 core roles** below (the Executioner is always one of them). Run roles in parallel; spread them across whatever model tiers and approved CLIs are available.

#### Core roles

| Role | What they generate | Ideal agent type |
|---|---|---|
| **Strategist** | Product thesis, priorities, what existing tools miss, positioning | Code-aware subagent (reads local README, docs, recent git) |
| **Operator** | Concrete workflows, statuses, actions, edge cases, day-to-day mechanics | Code-aware subagent |
| **Cartographer** | Views, maps, grouping patterns, zoom levels, navigation metaphors | Fresh-eyes (no codebase access) |
| **Archivist** | Memory, synthesis, knowledge capture, long-term coherence, recovery flows | Fresh-eyes |
| **Trickster** | Whimsical metaphors, silly-but-useful delight, strange UI lenses, absurdist reframes | Fresh-eyes (most creative divergence happens with no anchoring context) |
| **Skeptic** | What becomes noise, what users ignore, what shouldn't ship, local maxima | Balanced tier with a blunt mandate |
| **Executioner** | The strongest honest case for never building this at all — wrong timing, wrong audience, wrong founder, already solved, fundamental flaw in premise | Any model with a blunt mandate — always included, never optional |

#### Perspective-expanding roles (add at least 2)

| Role | What they generate | Ideal agent type |
|---|---|---|
| **Future Self** | 6/12/24-month horizon ideas; what smart teams converge on; leapfrog moves | Strongest tier |
| **Outsider / Cultural Stranger** | Assumptions the team never questioned; non-default user perspectives | Fresh-eyes |
| **Customer Whisperer** | Emotional arc the user goes through; delight moments; trust signals | Fresh-eyes |
| **Devil's Advocate** | The honest thing nobody wants to say; core assumption challenges | Any model with a blunt mandate |

**Default panel for full-diversity mode:** all 7 core + Future Self + Outsider.

**Default panel for single-agent mode:** Strategist, Operator, Trickster, Skeptic, Executioner, Future Self — as subagents with strongly differentiated tones.

**The Executioner is always included.** A brainstorm without a kill test is a yes-machine.

### 4. Fan-out — launch all roles in parallel

Dispatch **all roles simultaneously** in a single turn. Do not wait for one to finish before launching the next.

#### Prompt template for every role

Every role gets the **seed brief** (from step 1) plus a role-specific lens:

```text
=== WIDE-OPEN BRAINSTORM ===

PRODUCT / IDEA: [from seed]
AUDIENCE: [who it is for]
CORE OUTCOME: [what "success" means to the user]
EMOTIONAL FLAVOR: [desired brand/experience tone]
PERMISSION: Be practical, silly, weird, and ambitious. All altitudes welcome.

YOUR ROLE: [role name]
YOUR MANDATE: [role-specific mandate — see below]
YOUR TONE: [e.g., "wide-open strategist" / "whimsical inventor" / "dry skeptic"]

INSTRUCTIONS:
1. Think across at least three altitudes:
   - 10,000 feet: goals, strategy, direction, what matters and why
   - 1,000 feet: projects, workstreams, groupings, operational patterns
   - Ground level: exact items, statuses, actions, next clicks
2. Generate ideas across your assigned lens. Don't self-censor.
3. For whimsical ideas: explain what the metaphor REVEALS, not just what it is.
4. For practical ideas: name the specific workflow it enables.
5. Include a time-horizon pass:
   - 6 months: what would smart builders do once the rough edges are fixed?
   - 12 months: what do teams converge on when the pattern is legible?
   - 24 months: what does the mature version assume as table stakes?
   - Leapfrog: what bypasses the expected roadmap and gets closer to THE FUTURE now?
6. Name your 3 strongest ideas. Good names make ideas sticky.
7. End with: "The thing most people miss about this: [one non-obvious insight]"

FORMAT: Flowing prose or numbered list, your choice. No hedging. No meta-commentary.
```

#### Role mandates (insert into template)

| Role | Mandate |
|---|---|
| **Strategist** | Identify the product's true north star, what the competitive alternatives get wrong, and the one insight that makes this genuinely different. Think like a founder writing a first-principles memo. |
| **Operator** | Map the real workflow: what does the user actually do, step by step, when this product is working? Find the five micro-decisions the product must make easier. |
| **Cartographer** | Design the views, maps, and grouping systems. How does the user see everything at once? How do they navigate without getting lost? What metaphor makes the product's structure legible? |
| **Archivist** | Design the memory and synthesis layer. How does the product get smarter over time? What does it remember, surface, and forget? How does the user recover when context is lost? |
| **Trickster** | Generate whimsical reframes and strange metaphors. What if this product were a ship's bridge? A garden? A detective's evidence board? A jazz session? Push until at least one idea feels genuinely surprising. |
| **Skeptic** | Be the voice of restraint. What will users ignore? What adds noise without signal? What is the most common mistake products like this make? What should NOT be built? |
| **Future Self** | Assume it is now [18 months from today]. The category has matured. What do all the good versions of this product have in common? What leapfrog move gets there before the obvious roadmap does? |
| **Outsider** | Approach this product as someone who doesn't share any of the builder's assumptions. What is confusing about the framing? What assumption is being treated as obvious that isn't? |
| **Customer Whisperer** | Map the user's emotional arc: what do they feel when they discover this, when it first works, when it fails, when it becomes a habit? Where does delight live? Where does trust get built or broken? |
| **Devil's Advocate** | Make the strongest honest case against the core premise. What if the fundamental assumption is wrong? What would make this irrelevant? |
| **Executioner** | Your job is not to find flaws — it is to argue that this idea should be abandoned entirely. Find the single strongest reason it should never be built: wrong timing, already exists and is better, fundamental audience mismatch, wrong founder for this problem, market that won't pay, regulatory trap, or premise that sounds good but collapses on first contact with reality. You are not here to balance — you are here to kill the idea if it deserves killing. If you cannot find a compelling reason to kill it, say so explicitly: "This idea survived the kill test. Here's why." That verdict is a green light. |

#### Capability tiers

Each role runs as a subagent, or an approved external CLI. Tiers, not model names (names go stale): **fast** = cheapest capable model, **balanced** = default workhorse, **strongest** = best available reasoning model.

| Role | Context | Tier |
|---|---|---|
| Strategist | Code-aware (local files) | balanced |
| Operator | Code-aware | balanced |
| Cartographer | Fresh-eyes | strongest |
| Archivist | Fresh-eyes | balanced |
| Trickster | Fresh-eyes | fast (cheap, high-variance is the point) |
| Skeptic | Fresh-eyes | balanced |
| Future Self | Fresh-eyes | strongest |
| Outsider | Fresh-eyes | balanced |
| Customer Whisperer | Fresh-eyes | balanced |
| Devil's Advocate | Fresh-eyes | balanced |
| Executioner | Fresh-eyes | strongest, explicit kill-test mandate |

If a role fails or times out, say so and rerun it as a subagent; never present a missing role as covered.

### 5. Force altitude switching (apply during synthesis)

Ensure the combined output covers all three levels:

- **10,000 feet:** goals, campaigns, strategy, health, drift, priorities.
- **1,000 feet:** projects, workstreams, branches, tickets, docs, grouped activity.
- **Ground level:** individual items, exact statuses, actions, recovery, tooltips, next clicks.

Look for interaction patterns that let the user smoothly zoom out, zoom in, and jump precisely. If any altitude is thin, ask the relevant role to extend its output there (one follow-up, no more).

### 5.5. Time-horizon leapfrog pass (during synthesis)

After collecting role outputs, surface ideas from the future-self and leapfrog lens explicitly:

- **6 months:** what would the smart, competent solution look like once the obvious rough edges are fixed?
- **12 months:** what would smart teams converge on after the pattern becomes legible and the first wave of tooling exists?
- **24 months:** what would the mature, deeply integrated version assume as table stakes?
- **Leapfrog:** what bypasses even those smart 6/12/24-month ideas and arrives closer to **THE FUTURE** now?

For each horizon, distinguish:

- predictable improvements smart people will independently invent;
- compounding advantages that become possible only after the system has memory, usage data, trust, integrations, or a stronger conceptual model;
- assumptions that stop mattering because the future version reframes the problem;
- the weird, brave move that feels premature today but may become obvious later.

Do not treat the far future as sci-fi garnish. Use it to identify which near-term choices keep optionality open, which ideas are local maxima, and which design thesis can leapfrog the expected market path.

### 6. Optional cross-pollination round

One round maximum.

After collecting first-round outputs, run a second round when:

- Roles produced surprisingly different framings
- One role surfaced something the others completely missed
- The synthesis feels too neat — good tension should feel messy

Send each agent a digest of what the other roles found, then ask:
1. What from the other perspectives is WRONG or overblown — why?
2. What did you miss in the first round that now seems important?
3. What combination of ideas creates something the others didn't see?

### 7. Distill hard — synthesize across all outputs

Separate ideas into:

- practical now ideas;
- high-leverage product concepts;
- LLM-backed or automation-heavy ideas;
- 6/12/24-month horizon ideas;
- leapfrog-to-THE-FUTURE ideas that make expected solutions feel incremental;
- whimsical metaphors that clarify state;
- delightful but optional flourishes;
- ideas to avoid because they add noise.

Note where multiple roles **independently converged** on the same idea — that convergence is a signal.

Name the strongest concepts. Good names make ideas reusable and spreadable.

### 7.5. The Kill Test — process the Executioner's verdict

Treat the Executioner's output separately from the other roles.

**If the Executioner could not find a compelling reason to kill the idea:**
- Note this explicitly in the synthesis: "The idea survived the kill test."
- This is a genuine positive signal — the Executioner tried and couldn't make the case.
- Mention what the Executioner probed and why it didn't hold.

**If the Executioner found a compelling reason to kill the idea:**
- Do not bury it. Surface it prominently in the final artifact.
- State whether the other roles' outputs change in light of this finding.
- Give the user a clear "build or don't build" frame: if this kill argument is correct, what would have to be true to proceed anyway?
- This is not a reason to suppress the brainstorm output — the ideas still have value even if the premise needs rethinking. But the kill argument gets its own named section.

### 8. Produce the final artifact

Use this structure unless the user requested another format:

1. North Star / product thesis
2. What existing tools or current approaches miss
3. Big ideas from practical to wild
4. Views and organizing metaphors
5. Detection/status/intelligence ideas
6. Actions and workflows
7. LLM-backed synthesis or automation ideas
8. Whimsical delight ideas
9. Top differentiated ideas (named and defined)
10. Time horizons: 6 months, 12 months, 24 months
11. Leapfrog ideas: what gets to THE FUTURE sooner
12. What to build first vs. what to dream about
13. Where roles converged (highest-signal ideas)
14. **Kill test verdict** — did the idea survive? If not, what's the strongest argument against, and what would have to be true to proceed anyway?
15. Reformulated reusable prompt

Keep the final answer crisp enough to read, but rich enough to preserve the spark.

## Optional file artifact

When the user asks to save the brainstorm, create a dated Markdown file in the most relevant project docs folder or durable notes location. Include:

- date and context;
- reformulated prompt;
- synthesized output;
- raw or distilled notes from model participants;
- follow-up planning prompt.

Prefer project-local `docs/` for project-specific brainstorms. Prefer the user's durable notes location for cross-project life/work strategy.

## Reusable prompt template

Load `references/wide-open-brainstorm-prompt.md` when a full prompt template is useful.
