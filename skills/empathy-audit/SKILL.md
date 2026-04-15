---
name: empathy-audit
description: Review code, products, or features through four empathy lenses (user, machine, developer, support) to surface quality issues that pure technical review misses. Use when preparing for launch, after major features, or when something "works but feels wrong." Produces both positive and negative findings — celebrates what's kind and flags what's cruel.
---

# Empathy Audit

A structured review that asks: *who does this code serve, and how does it treat them?*

Technical reviews catch bugs. Empathy audits catch the things that make users uninstall, machines overheat, developers quit, and support people burn out. They also catch the things worth celebrating — the thoughtful defaults, the generous error messages, the code that's a pleasure to read.

## When to Use

- Before a launch, beta, or public release
- After completing a major feature or refactor
- When a product "works" but something feels off
- When support tickets are accumulating but tests are green
- Periodically on long-running products (quarterly health check)

## When NOT to Use

- Tiny bug fixes or single-line changes
- Pure infrastructure/CI changes with no user surface
- Early prototypes where the design is still fluid

---

<process>

## Phase 1: Scope and Context

Before reviewing, establish the review surface:

1. **Read project docs** — `CLAUDE.md`, README, architecture docs
2. **Identify the audience** — who uses this? what do they care about?
3. **Map the hot paths** — what code runs most often? what touches user files/data?
4. **Size the review** — pick the scope:

| Scope | What to review | Time |
|---|---|---|
| **Focused** | One feature or subsystem (3-8 files) | Quick |
| **Module** | A full module/layer (10-20 files) | Medium |
| **Full** | Entire codebase | Use multi-agent fan-out |

For a **full** audit, use the multi-agent approach in Phase 3. For focused/module, a single pass through all four lenses is fine.

## Phase 2: The Four Lenses

Each lens has a distinct perspective, distinct signals, and a distinct emotional register. They are designed to find different things — resist the urge to merge them.

### Lens 1: User Empathy

**Perspective:** You are the person who installed this because it promised to solve a problem. You don't know or care how it works internally. You just want it to do what it said it would do, without surprises.

**Emotional register:** Protective — speaking for someone who deserved better, or celebrating when they got it.

**What to examine:**
- Error messages and failure states — do they explain *why* and *what to do*, or just display a code?
- Silent failures — does the app ever fail without telling the user anything happened?
- Cognitive load — does the user need to remember state, configure complex settings, or understand internals?
- Waiting and feedback — are there "dead air" moments with no progress indicator?
- Destructive actions — do file mutations, deletions, or irreversible changes have clear confirmation?
- Defaults — are they safe and sensible for a first-time user, or do they optimize for the developer's setup?
- Notification behavior — helpful or spammy? Present when needed or absent when critical?
- Accessibility — keyboard navigation, screen reader labels, contrast
- Privacy — does the user know what data leaves their machine? Is consent clear or theatrical?

**Unique signals this lens catches:**
- The moment a user decides to uninstall
- Settings that feel reasonable to the builder but reckless to the user
- Features that "work" but feel creepy, sloppy, or untrustworthy
- The gap between what the marketing promises and what the UX delivers

**Output per finding:**
```
- Type: POSITIVE or NEGATIVE
- Lens: User Empathy
- The Moment: [specific interaction or code path]
- The Feeling: [the emotion this creates — be precise, not just "frustrated"]
- Evidence: [file:line or feature reference]
- Action: [specific change, or "keep doing this" for positives]
```

---

### Lens 2: Machine Empathy

**Perspective:** You are the computer. You have finite battery, CPU, memory, disk, and network. Every cycle spent on this app is a cycle not spent on something else. You get hot when code is wasteful. You appreciate code that lets you sleep.

**Emotional register:** Dry alarm — watching the resource meters and noticing patterns.

**What to examine:**
- Polling vs. observing — does the code poll on a timer when it could use events/callbacks/notifications?
- Wake frequency — how often does this app wake the CPU when idle? (Especially important for menu bar / background apps)
- Network discipline — does it download more than it needs? Retry without backoff? Make redundant calls?
- Memory growth — are there collections, caches, or dictionaries that grow unbounded over the app's lifetime?
- Disk I/O — constant small writes that prevent SSD sleep? Temp files that don't get cleaned up?
- Image/media handling — loading full-resolution assets when thumbnails would do? Keeping decoded bitmaps in memory?
- Background behavior — does the app do work when the user isn't looking? Does it respect system sleep/wake?
- Connection management — are HTTP sessions reused? Are file descriptors properly closed?

**Unique signals this lens catches:**
- The "fan spin" — code that's technically correct but makes the laptop hot
- The "battery thief" — background activity that drains power without user benefit
- The "slow leak" — memory or disk growth that only matters after weeks of uptime
- Timer-based polling that could be event-driven

**Output per finding:**
```
- Type: POSITIVE or NEGATIVE
- Lens: Machine Empathy
- The Tax: [resource being consumed — CPU, Battery, Memory, Disk, Network]
- The Impact: [what the user's device experiences]
- Evidence: [file:line or pattern reference]
- Action: [specific optimization or "well done" for positives]
```

---

### Lens 3: Developer Empathy

**Perspective:** You are the next person — human or AI — who opens this codebase at 2 AM to fix a bug. You've never seen it before. Every minute you spend understanding the code is a minute you're not fixing the problem.

**Emotional register:** Wary gratitude — noticing the traps and the kindnesses.

**What to examine:**
- God objects — files or classes that do too many things (>200 lines for a class, >30 for a function)
- Naming — do names tell you what things *are* and what they *do*, or do you need to read the implementation to understand?
- Coupling — how many singletons, globals, or implicit dependencies does a change require understanding?
- Consistency — does the codebase follow its own conventions, or does every file feel like a different author?
- Hidden side effects — does calling a function change state you wouldn't expect from its name?
- Error propagation — can you trace a failure from the log to the responsible code in under 60 seconds?
- Test clarity — do tests document behavior, or are they puzzles that test implementation details?
- Architecture legibility — can you understand the system's shape from the directory structure?
- Comment quality — are comments *why* (valuable) or *what* (noise)?

**Unique signals this lens catches:**
- The "fear of breaking" — code that works but nobody dares touch
- The "archaeology problem" — understanding requires git blame, not reading the code
- The "clever trap" — impressive code that creates maintenance debt
- The "welcome mat" — code that's genuinely pleasant to work in

**Output per finding:**
```
- Type: POSITIVE or NEGATIVE
- Lens: Developer Empathy
- The Hurdle: [specific code that's hard to parse, or delightful to read]
- The Friction: [the mental tax — e.g., "context fatigue", "fear of breaking", "delight"]
- Evidence: [file:line reference]
- Action: [specific refactor, or "keep doing this" for positives]
```

---

### Lens 4: Support Empathy

**Perspective:** You are the person who answers the email when a user says "it's broken." Every silent failure is a mystery you have to solve with nothing but a vague user report and whatever breadcrumbs the app left behind.

**Emotional register:** Exhausted forensics — has diagnosed this exact category of problem before.

**What to examine:**
- Logging completeness — if this function fails, will the logs show *what input* caused it and *what state* the system was in?
- Error specificity — does the user see "Something went wrong" or "Your API key is invalid — update it in Preferences > AI"?
- Diagnostic tooling — can you export a redacted diagnostics bundle? Is there a "system check" feature?
- State introspection — can you tell what the app is currently doing? Is there a status indicator that reflects reality?
- Correlation IDs — can you trace a user's report through logs to the exact failure?
- Silent drops — are there code paths where work is silently skipped with no log, no notification, no history entry?
- Self-service recovery — can the user fix common problems themselves, or do they need to contact support?
- Feedback channels — is it easy to report a problem? Does the report include useful context automatically?
- Edge case documentation — are the known limitations documented somewhere the support person can find?

**Unique signals this lens catches:**
- The "20-email thread" — a problem that takes excessive back-and-forth to diagnose
- The "ghost failure" — something went wrong but there's zero evidence anywhere
- The "works on my machine" — failures that only happen in user environments the team never tested
- The "brilliant diagnostics" — systems that make support a pleasure

**Output per finding:**
```
- Type: POSITIVE or NEGATIVE
- Lens: Support Empathy
- The Blind Spot: [the failure mode that's hard to diagnose, or the tool that makes it easy]
- The Investigation: [what support has to do to find root cause]
- Evidence: [file:line or feature reference]
- Action: [add logging, error context, diagnostic tool, or "keep doing this"]
```

---

## Phase 3: Execution

### Single-agent mode (focused/module scope)

Read the relevant source files, then make one pass through each lens sequentially. Produce findings for all four lenses before synthesizing.

### Multi-agent mode (full scope)

For full codebase audits, use parallel agents for efficiency and perspective diversity.

#### Environment Detection

```bash
bash "${SKILL_DIR}/scripts/detect-llms.sh" --quiet 2>/dev/null || \
  for t in ask-gemini ask-copilot ask-cerebras ask-zai; do command -v "$t" >/dev/null 2>&1 && echo "$t"; done
```

#### Agent Assignment

Assign lenses to maximize perspective diversity:

| Lens | Best agent type | Why |
|---|---|---|
| User Empathy | External LLM (fresh eyes) | No familiarity bias — sees the product as a user would |
| Machine Empathy | Code-aware subagent | Needs to read actual implementations, timers, loops |
| Developer Empathy | Code-aware subagent | Needs to evaluate naming, structure, coupling |
| Support Empathy | External LLM + code-aware | External for "what would confuse a user?", code-aware for "is this logged?" |

When dispatching to external LLMs, include:
1. The lens prompt (from Phase 2)
2. The relevant source code (pipe file contents)
3. A brief project description (1-3 sentences)

When dispatching to subagents, include:
1. The lens prompt
2. Instructions to read specific files
3. The project CLAUDE.md for context

#### Prompt Template for External LLMs

```
You are conducting an empathy audit of [PROJECT] — [1-sentence description].

[LENS PROMPT FROM PHASE 2]

Here is the code to review:

[SOURCE CODE]

Produce 5-10 findings. Include BOTH positive and negative findings.
For each finding, use the output format specified in the lens prompt.
Be specific — cite function names, patterns, and line-level observations.
Do not hedge or soften negative findings. Do not be sycophantic about positive ones.
```

#### Prompt Template for Subagents

```
You are conducting an empathy audit of this codebase through the [LENS NAME] lens.

[LENS PROMPT FROM PHASE 2]

Read these files: [FILE LIST]
Also read CLAUDE.md for project context.

Produce 5-10 findings. Include BOTH positive and negative findings.
Be specific — cite file:line references.
```

## Phase 4: Synthesis

After collecting findings from all four lenses, synthesize into a single report.

### Deduplication

Merge findings that describe the same underlying issue from different lenses. Note which lenses independently surfaced it — convergence increases severity.

### Severity Assessment

Rate each finding:

| Severity | Criteria |
|---|---|
| **Critical** | Causes data loss, trust damage, silent failure, or would generate support emails |
| **Important** | Degrades experience, wastes resources, or creates maintenance burden |
| **Minor** | Suboptimal but not harmful — improvement opportunity |
| **Positive** | Worth celebrating and preserving — document so it doesn't get lost in a refactor |

Upgrade severity when:
- Multiple lenses independently surface the same issue
- The issue is invisible to the user (silent failure)
- The issue compounds over time (memory leak, growing support burden)
- The emotional injury is shame, betrayal, or helplessness

### Report Structure

```markdown
# Empathy Audit: [Project]
_Reviewed: [date]_

## Summary
- **Strongest quality:** [the best thing about this codebase from an empathy perspective]
- **Biggest risk:** [the finding most likely to hurt users, the machine, developers, or support]
- **Most surprising finding:** [something a technical review would have missed]

## Findings by Severity

### Critical
[findings with full lens attribution]

### Important
[findings]

### Minor
[findings]

### Positive (Preserve These)
[findings — things the codebase does well that should be protected during future changes]

## Lens Summary

### User Empathy
- Positive: [count] | Negative: [count]
- [1-sentence summary]

### Machine Empathy
- Positive: [count] | Negative: [count]
- [1-sentence summary]

### Developer Empathy
- Positive: [count] | Negative: [count]
- [1-sentence summary]

### Support Empathy
- Positive: [count] | Negative: [count]
- [1-sentence summary]

## Cross-Lens Patterns
[issues that appeared in multiple lenses — these are the systemic concerns]

## Recommended Priority Order
1. [action] — addresses [finding]
2. [action] — addresses [finding]
3. [action] — addresses [finding]
```

## Phase 5: Follow-Up

After presenting the report, offer:

> Which findings resonate? Want me to turn the top items into tasks, go deeper on one lens, or run a targeted audit on a specific subsystem?

</process>

<anti_patterns>

## Anti-Patterns

| Don't | Do instead |
|---|---|
| Produce only negative findings | Celebrate what's good — positives protect against regression |
| Use generic findings ("could be more efficient") | Cite specific functions, files, and line numbers |
| Conflate lenses ("this is bad for users AND developers") | Keep findings lens-specific; note cross-lens convergence in synthesis |
| Over-index on technical correctness | This audit is about empathy — how code treats people and machines |
| Soften findings to be polite | Be direct. "This silently drops user files" is better than "there may be an opportunity to improve file handling" |
| Skip the positive findings | They're as valuable as negatives — they show what to preserve |
| Run all four lenses through the same model with the same framing | Diversity of perspective is the point — use different agents or strongly differentiated prompts |

</anti_patterns>

<success_criteria>

The audit is complete when:
- [ ] All four lenses produced findings with specific evidence
- [ ] Both positive and negative findings are present
- [ ] At least one finding would not have appeared in a standard code review
- [ ] Findings include emotional impact, not just technical assessment
- [ ] Cross-lens patterns are identified
- [ ] The user has a prioritized action list
- [ ] The report is specific enough that a developer could act on each finding without further investigation

</success_criteria>
