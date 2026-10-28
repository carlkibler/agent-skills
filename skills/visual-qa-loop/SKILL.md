---
name: visual-qa-loop
description: "Run before/after visual QA for local UI changes with screenshots and concise findings."
display_name: "Visual QA Loop"
brand_color: "#DB2777"
local_only: true
group: "Dev Workflow"
usage: "/visual-qa-loop:run"
summary: "Catch visual regressions with repeatable before/after screenshots and tight review notes."
default_prompt: "Run visual QA for this UI change. Capture before/after screenshots with stable viewport(s), compare them, fix obvious regressions, and save artifacts outside the repo unless asked."
---

# Visual QA Loop

For UI work, "tests pass" is not the same as "eyes pass."

Third-order stance: static screenshots are receipts, not the whole truth. Look for temporal debt, hidden friction, and trust changes between states: loading, empty, error, hover, focus, permission prompts, and the moment after a user clicks.

## When to Use

- The user asks for visual QA, screenshots, design polish, UI review, hover/focus review, or before/after proof
- A frontend/macOS/iOS UI change might alter layout, copy, color, spacing, or trust perception
- The user wants assurance changes are tweaks, not accidental replacement

## When NOT to Use

- Pure backend or CLI changes with no visual surface
- The app cannot be rendered locally and no screenshot path exists
- The user explicitly says not to do visual validation

---

<process>

## Phase 1: Pick Stable Targets

Identify the exact pages/windows/states to capture. Prefer the smallest set that covers the changed surface. Include transition states when relevant: loading, empty, error, first-run, disabled, hover/focus, and post-action success/failure.

Pick the artifact directory first: the project's existing notes/artifacts location if its instructions name one, otherwise a temp directory. Do not add screenshots to the repo unless asked.

Use whatever screenshot path is available, in this order: a project or machine wrapper (for example `chrome-shot`, if `command -v chrome-shot` succeeds), a browser automation tool (Playwright, agent-browser, or an MCP browser), headless Chrome, or `screencapture` for native macOS windows. Example with `chrome-shot`:

```bash
ART=<artifact-dir>/visual-qa/<run>; mkdir -p "$ART"
chrome-shot -o "$ART/home-1440.png" http://localhost:3000/
chrome-shot --size 390x1200 -o "$ART/home-mobile.png" http://localhost:3000/
```

If no tool can capture the target, stop and say so rather than reviewing from code alone.

## Phase 2: Capture Before and After

If changes are not applied yet, capture `before/`. After edits/build, capture `after/` with the same viewport, route, data, and state.

Use filenames that encode route/state/viewport, not verbose captions. If the issue may be motion/jank, capture a short trace, repeated screenshots, or before/after states around the transition rather than only the final settled UI.

## Phase 3: Review Like a User

Check:

- layout shifts, overflow, clipping
- copy drift or confusing labels
- hover/focus/selected states too loud or too invisible
- trust fractures: surprise permissions, privacy creep, pricing ambiguity, destructive actions
- mobile density and tap targets
- empty/error/loading states when relevant
- information density: high-signal details should not disappear behind unnecessary hover/clicks
- temporal debt: flicker, layout shift, stale preview, delayed permission prompt, or post-click ambiguity
- downstream friction: a small visual change near a CTA, filename, price, or destructive action can be larger than its pixel area

## Phase 4: Iterate Once Before Reporting

If an obvious regression is visible, fix it and recapture once (a second failed pass goes in the report, not a third loop). Only fix regressions in the changed surface. Do not hand back known-bad screenshots unless blocked.

## Phase 5: Report Evidence

Return:

- screenshot artifact paths
- what changed visually
- pass/fail verdict
- any remaining concerns
- any "looks fine but may feel wrong over time" temporal/friction concerns

Keep it short. The screenshots are the receipts.

</process>

<interlocks>

- Use `trust-audit` when the visual surface touches permissions, privacy, billing, or destructive file changes.
- Use `status-copy-trust-audit` when UI/CLI wording is the confusing part.
- Use `first-contact` when the visual change touches onboarding or day-zero mental models.
- Use `agent-log-forensics` when recurring user complaints point at visual or interaction jank across sessions.

</interlocks>
