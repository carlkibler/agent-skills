---
name: decision-log
description: Capture a technical or product decision with chosen option, rejected alternatives, and rationale — in a format a future agent can read to reconstruct context.
display_name: "Decision Log"
brand_color: "#6366F1"
local_only: false
group: "Dev Workflow"
usage: "/decision-log:run"
summary: "Capture why you picked this over the alternatives, so future-you never has to re-litigate the choice."
default_prompt: "Log this decision: what we chose, what we rejected, and why. Save it in a format a future Claude session can read."
---

# Decision Log

The "why did we do it this way?" skill. Captures decisions at the moment they're made — while the context is alive — so future sessions don't have to reverse-engineer intent from code.

## When to Use

- After a non-obvious architectural or product decision
- When choosing between 2+ viable approaches (especially when rejecting an appealing option)
- Before implementing something that will confuse a future reader
- When the team agrees on something that required significant discussion
- Any time you think "I'll remember why we did this" (you won't)

## When NOT to Use

- Obvious implementation details
- Single-option decisions with no real alternative
- Pure refactors where the logic is self-evident in the diff

---

<process>

## Phase 1: Extract the Decision

Ask the user (or infer from context):

1. **What** — What was decided? One clear sentence.
2. **Why** — What was the core reason? (constraint, performance, simplicity, user need, etc.)
3. **Alternatives rejected** — What were the other options? Why didn't they win?
4. **Context** — What would a future reader need to know to understand this decision? (related files, external constraints, deadlines, team knowledge gaps)
5. **Revisit triggers** — Under what conditions should this decision be reconsidered?

If the user is in the middle of implementation, infer as much as possible from context (open files, recent commits, current CLAUDE.md discussion) and ask only what's missing.

## Phase 2: Write the Decision Log Entry

Create or append to `.decisions/YYYYMMDD-<slug>.md` in the project root. Use today's date and a kebab-case slug from the decision title.

### File format

```markdown
# [Decision Title]

**Date:** YYYY-MM-DD  
**Status:** Active | Superseded by [link] | Deprecated  
**Decider:** [person or team]

## Decision

[One clear sentence: we chose X.]

## Context

[What was the situation? What problem were we solving? What constraints existed?]

## Options Considered

### Option A: [Chosen] ✓
[Description]
**Pros:** [list]
**Cons:** [list]

### Option B: [Rejected]
[Description]
**Pros:** [list]  
**Cons:** [list]  
**Why rejected:** [specific reason]

### Option C: [Rejected] (if applicable)
...

## Rationale

[Why Option A won. The core reasoning. What would have to be true for us to pick differently?]

## Consequences

**Positive:** [what this enables]  
**Negative / Trade-offs:** [what we gave up]  
**Risks:** [what could go wrong with this choice]

## Revisit When

- [Specific trigger: "if X starts taking more than Y seconds"]
- [Technology changes: "if library Z adds support for W"]
- [Scale changes: "if we exceed N users"]

## Related

- [File or module most affected]
- [Other decisions this relates to]
- [External docs or prior art]
```

## Phase 3: Update the Decision Index

Create or update `.decisions/README.md` — a running index of all decisions:

```markdown
# Decision Log

| Date | Decision | Status |
|------|----------|--------|
| YYYY-MM-DD | [Title](./YYYYMMDD-slug.md) | Active |
```

## Phase 4: Confirm and Offer Next Steps

- Show the user the written entry
- Ask if anything needs correction
- Suggest: "You may want to commit this now so it's part of the same PR as the implementation."
- If there's a PR open, suggest adding a reference to it

</process>
