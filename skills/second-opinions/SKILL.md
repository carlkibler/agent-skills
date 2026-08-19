---
name: second-opinions
description: "Run a bounded independent code review with the opposite-company model first, complete git scope context, and a same-company fallback."
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

Use an independent provider before committing meaningful changes. The reviewer is a collaborator,
not an authority. A timeout or provider failure is a failed review, never approval.

## When to use

Mandatory for complex multi-file changes, security or PHI work, performance-critical code, design
decisions with real tradeoffs, and work that has consumed more than two hours. Skip trivial fixes.

## One bounded entrypoint

Use the installed `review-watch` command. It has a **10-minute total deadline** across both attempts,
prints 15-second heartbeats, captures output, and terminates the entire review process tree on timeout.
Do not invoke bare `codex review`, `claude -p`, `codex exec`, or an unbounded agent call for review.
A naked `review-watch` invocation prints copy-pasteable examples instead of failing with a grammar
error. `--agent` prints the same contract for a first-pass agent.

Tell it which provider is running the current task. It tries the opposite company first, then the same
company if the first provider is unavailable, exhausted, or returns an error while time remains:

```bash
# Running under Codex: Claude first, Codex fallback
review-watch --current-provider codex --worktree "$PWD"

# Running under Claude: Codex first, Claude fallback
review-watch --current-provider claude --worktree "$PWD"
```

The script uses Claude Opus and Codex `gpt-5.6-sol` by default. It accepts common aliases such as
`openai`/`gpt`, `anthropic`/`opus`, `--against` for `--base`, `--diff` for `--range`, comma-separated
SHAs, bare worktree/ref/range positional arguments, and durations such as `10m`, `600s`, or `1h`.
Override only when needed: `--claude-model MODEL`, `--codex-model MODEL`, `--timeout SEC`, or
`--heartbeat SEC`. Use `--json` when a caller needs a designed machine-readable receipt; progress and
provider diagnostics stay on stderr so stdout remains valid JSON.

## Scope is explicit

A bare SHA is not enough context for a branch review. Prefer the complete branch diff:

```bash
review-watch --current-provider codex --worktree /absolute/path/to/worktree --base main
```

On a topic branch with no scope flags, the script automatically reviews the branch against its
`main` merge-base. Use these forms when the scope is narrower or spans selected history:

```bash
review-watch --current-provider codex --worktree "$PWD" --commit 470907dae
review-watch --current-provider codex --worktree "$PWD" --commit SHA1 --commit SHA2
review-watch --current-provider codex --worktree "$PWD" --range OLD..NEW
```

`--worktree` changes the checkout the provider inspects. The prompt always includes its absolute path,
branch, status snapshot, exact scope, and the instruction to inspect the complete diff. The provider
must not edit files or perform live mutations. Output restates canonical `WORKTREE`, `BRANCH`,
`SCOPE`, provider order, deadline, and ends with runnable `Next commands` plus `REVIEW_STATUS`,
`REVIEW_PROVIDER`, and `REVIEW_EXIT` keys.

## Review lens

Check correctness and regressions first, then security/PHI, real outbound effects, performance, and
maintainability. Return `PASS` or `NEEDS CHANGES`. Every finding needs severity, path, line, concrete
evidence, and the smallest fix. If the scope is unavailable or ambiguous, fail closed.

Record the provider, exact command, scope, exit status, and findings in the review note or merge
receipt. A fallback is a real review; report that the primary provider failed and which fallback ran.
