---
name: visual-qa-loop
description: Run a repeatable before/after visual QA loop for local web/app UI changes, using stable screenshots, artifact folders, and concise visual findings.
display_name: "Visual QA Loop"
brand_color: "#DB2777"
local_only: true
group: "Better Products"
usage: "/visual-qa-loop:run"
summary: "Repeatable visual screenshots and review notes for UI changes"
default_prompt: "Run visual QA for this UI change. Capture before/after screenshots with stable viewport(s), compare them, fix obvious regressions, and save artifacts under agent-notes."
---

# Visual QA Loop

For UI work, "tests pass" is not the same as "eyes pass."

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

Identify the exact pages/windows/states to capture. Prefer the smallest set that covers the changed surface.

For web/file targets on this machine, use `chrome-shot` rather than raw Chrome commands:

```bash
mkdir -p ~/dev/agent-notes/<project>/visual-qa/<run>
chrome-shot -o ~/dev/agent-notes/<project>/visual-qa/<run>/home-1440.png http://localhost:3000/
chrome-shot --size 390x1200 -o ~/dev/agent-notes/<project>/visual-qa/<run>/home-mobile.png http://localhost:3000/
```

## Phase 2: Capture Before and After

If changes are not applied yet, capture `before/`. After edits/build, capture `after/` with the same viewport, route, data, and state.

Use filenames that encode route/state/viewport, not verbose captions.

## Phase 3: Review Like a User

Check:

- layout shifts, overflow, clipping
- copy drift or confusing labels
- hover/focus/selected states too loud or too invisible
- trust fractures: surprise permissions, privacy creep, pricing ambiguity, destructive actions
- mobile density and tap targets
- empty/error/loading states when relevant

## Phase 4: Iterate Once Before Reporting

If an obvious regression is visible, fix it and recapture. Do not hand back known-bad screenshots unless blocked.

## Phase 5: Report Evidence

Return:

- screenshot artifact paths
- what changed visually
- pass/fail verdict
- any remaining concerns

Keep it short. The screenshots are the receipts.

</process>

<interlocks>

- Use `trust-audit` when the visual surface touches permissions, privacy, billing, or destructive file changes.
- Use `status-copy-trust-audit` when UI/CLI wording is the confusing part.

</interlocks>
