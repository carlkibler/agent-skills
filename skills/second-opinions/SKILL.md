---
name: second-opinions
description: Get validation from Claude before committing major changes, using the subscribed `claude -p` CLI directly.
display_name: "Second Opinions"
brand_color: "#4F46E5"
local_only: false
group: "For Anyone"
usage: "/second-opinions:run"
summary: "About to make a big call? Get a gut-check from a second AI with a different perspective before you commit."
favorite: true
default_prompt: "Get a second opinion on this implementation or design decision and summarize the strongest agreement, disagreement, and actionable feedback."
---

# Second Opinions

Get validation from a different AI before committing. Any single model — regardless of which one is running — has blind spots shaped by its training, context, and the conversation so far. A different architecture, temperature, or framing catches different things.

## When to Use

**Mandatory:**
- Complex multi-file changes before merge
- Design decisions with multiple valid approaches
- After 2+ hours on a single approach (tunnel vision risk)
- Security-sensitive or performance-critical code

**Skip for:** trivial fixes, style questions, crystal-clear requirements

## Claude Detection

`claude -p` is the only second-opinion path. Check once:

```bash
command -v claude >/dev/null 2>&1 && echo "claude available"
```

If Claude is unavailable or fails, tell the user and skip the cross-check. Do not silently fall back
to another CLI or provider.

## Model Selection

Second opinions are about **deep analysis**, not speed. Use the smartest model available:

| Work | Invocation |
|---|---|
| Deep review or architecture | `claude -p --model opus "..."` |
| Normal review | `claude -p "..."` |
| Fast sanity check | `claude -p --model haiku "..."` |

For **pre-merge review, design validation, or architecture decisions**, use Opus. Calls fail closed: no OpenRouter, `codex exec`, or provider fallback.

## How to Ask

The prompt is the same regardless of model — pick the invocation from the Model Selection table above and substitute your actual prompt.

### Pre-Merge Review (Most Common)

Show the diff and ask for a production-readiness check:

```
Review my git changes for production readiness.

Show the diff from main and check for:
- Correctness and edge cases
- Architecture and design
- Performance implications
- Security concerns
```

### Design Decision Validation

Describe the options and constraints, then ask: *What trade-offs am I not seeing?*

### Targeted Question

Ask one specific question about the implementation — don't fish for general feedback.

## Interpreting Results

The other agent is a **collaborator, not an authority.** Classify each piece of feedback:

| Category | Action |
|----------|--------|
| **Must-fix** | Bug, security issue, correctness problem → implement immediately |
| **Should-fix** | Genuine simplification, better error handling → implement if clean |
| **Nice-to-have** | Alternative approach, style preference → mention to user |
| **Reject** | Over-engineering, conflicts with project conventions → skip with reason |

If the other agent and your analysis disagree, explain the disagreement to the user and let them decide.

## The Red Flags

These thoughts mean STOP and get a second opinion:
- "It works in my tests" — tests only prove known scenarios
- "I've spent 3 hours on this" — sunk cost isn't validation
- "I'm confident this is right" — confidence correlates with blind spots
- "It's obviously the best approach" — obvious to you ≠ optimal

**5 minutes of external validation prevents hours of debugging.**
