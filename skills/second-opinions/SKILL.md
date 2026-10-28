---
name: second-opinions
description: "Run a bounded, read-only independent code review by a different-company model CLI, with full git scope context and honest reporting."
display_name: "Second Opinions"
brand_color: "#4F46E5"
local_only: false
group: "For Anyone"
usage: "/second-opinions:run"
summary: "Get a time-bounded independent review before committing or merging."
favorite: true
default_prompt: "Run a bounded independent review of the complete requested worktree or diff and summarize actionable findings."
---

# Second Opinions

Get an independent reviewer on a change before committing or merging. The reviewer is a collaborator,
not an authority. A timeout or CLI failure is a failed review, never approval.

## When to use

Mandatory for complex multi-file changes, security or PHI work, performance-critical code, design
decisions with real tradeoffs, and work that has consumed more than two hours. Skip trivial fixes.

## External model CLIs (ask first)

In-session subagents need no extra permission and are the default for every role below.
Launching a separate agent CLI (`claude -p`, `codex exec`, `omp -p`, `pi -p`) is different:
it spends the user's quota and sends project content to that provider. Before the first launch:

1. Read `${XDG_CONFIG_HOME:-$HOME/.config}/agent-skills/external-clis.json` if it exists.
   A CLI listed under `skills.second-opinions.allow` or top-level `allow` may run without asking;
   one listed under `deny` (either level) must not run. Skill-level entries win.
2. Otherwise run `command -v claude codex omp pi`, then ask once: which installed CLIs may this
   skill launch, and should the answer apply to this run, always for this skill, or always?
3. For "always", create or update the file (merge; never drop other skills' entries), e.g.
   `{"allow": ["codex"], "deny": [], "skills": {"second-opinions": {"allow": ["claude", "codex"]}}}`.
4. Bound every call (`timeout 600 ...`). Report which CLI and model actually answered. If none
   ran, say the outside cross-check did not happen rather than presenting subagent output as one.

Equivalent one-shot forms: `claude -p --model <m> "<prompt>"`,
`codex exec -m <m> --sandbox read-only "<prompt>"`, `omp -p --model <m> "<prompt>"`, `pi -p "<prompt>"`.
Prefer a CLI from a different company than the current session for outsider roles.
Pick a capability tier, not a pinned model name: fast, balanced, or strongest. Use each CLI's
current model list or default to map the tier; omit `--model` if unsure.

For this skill, prefer the strongest tier on a different company than the current session
(Codex session: `claude`; Claude session: `codex`). If only same-company CLIs are allowed, ask
before using one, and label the result "same-company review". Do not chain automatic fallbacks:
if the chosen CLI fails or times out, say so and ask which to try next.

## 1. Fix the scope

Decide exactly what is reviewed and state it before launching. Never review a bare SHA.

- Uncommitted work: `git status --short`, `git diff HEAD` (plus untracked files, listed by name).
- Topic branch: `git merge-base HEAD <base>`, then `git diff <base>...HEAD`. Default base is
  `main` or `master`, whichever exists.
- Selected history: `git diff OLD..NEW` or `git show <sha>` for each requested commit.

Capture the absolute worktree path, branch, the changed-file list (`--stat`), and the complete diff.
If the diff is empty or the scope is ambiguous, stop and ask. Do not review a guess.

## 2. Run one bounded read-only call

Write the prompt to a temp file (scope, project instruction files, changed-file list, full diff, the
review lens below, and "do not edit files or run mutating commands"). Run exactly one approved CLI
from the worktree (`omp` and `pi` forms are in the policy above):

```bash
timeout 600 codex exec --sandbox read-only "$(cat "$PROMPT")"
timeout 600 claude -p "$(cat "$PROMPT")"      # add --model <strongest> only if you know it
```

Large diffs: give the changed-file list plus the diff path and let the reviewer read it, rather than
exceeding argument limits. Exit code 124 means timeout.

If `review-watch` is installed, it wraps this whole flow (scope, heartbeat, process-tree kill);
run it with no arguments to see its usage. It is a shortcut, not a requirement, and it selects
providers on its own, so confirm its choice matches the CLI permission above.

## Review lens

Check correctness and regressions first, then security/PHI, real outbound effects, performance, and
maintainability. Return `PASS` or `NEEDS CHANGES`. Every finding needs severity, path, line, concrete
evidence, and the smallest fix.

## 3. Report honestly

State: which CLI and model reviewed, same- or cross-company (cross-model yes/no), exact scope,
exit status, verdict, and findings. Verify each finding against the source before acting; classify
as accept, reject (with reason), or needs decision. On timeout, failure, or empty output, report
"review did not happen" and never present it as a pass. Record this in the review note or merge receipt.
