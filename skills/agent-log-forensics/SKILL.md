---
name: agent-log-forensics
description: Scan Claude/Codex session logs to find agent behavior patterns, Toolsmith adoption gaps, repeated frustrations, and candidates for new skills/tools.
display_name: "Agent Log Forensics"
brand_color: "#6D28D9"
local_only: true
group: "Dev Workflow"
usage: "/agent-log-forensics:run"
summary: "Turn local and remote agent session logs into workflow improvements"
default_prompt: "Scan recent Claude and Codex session logs on this machine and any named remote hosts. Report Toolsmith adoption, lost opportunities, recurring frustrations, and concrete new skills/scripts to add. Keep examples privacy-light."
---

# Agent Log Forensics

Use this when the goal is not one bug fix, but making the human+agent system smarter after observing real sessions.

## When to Use

- The user asks whether agents are using a tool, skill, MCP server, or workflow
- The user wants "lost opportunities" where agents should have used better tools
- The user asks for patterns in interactions, repeated frustrations, jank, or productivity bottlenecks
- You need to turn observed behavior into new user-level skills, scripts, or project instructions

## When NOT to Use

- One isolated transcript or pasted error is enough
- The user asks for a narrow code change unrelated to agent behavior
- Logs may contain sensitive data and the user did not ask for forensic analysis

---

<process>

## Phase 1: Scope the Observation Window

Default to the last 7 days unless the user names a different range. Include remote hosts explicitly named by the user, commonly `vesta`.

Prefer Toolsmith's built-in scanner when available:

```bash
toolsmith scan-agent-logs --days 7 --max-examples 12
toolsmith opportunities --days 7 --max-examples 8
toolsmith scan-agent-logs --days 7 --remote vesta --max-examples 12
```

If the scanner is not installed yet, say that and fall back to a lightweight count of recent `~/.claude/projects/**/*.jsonl` and `~/.codex/sessions/**/*.jsonl` files rather than dumping raw prompts.

## Phase 2: Preserve Privacy

- Do not paste raw user prompts or full transcript content.
- Redact home paths, secrets, tokens, keys, cookies, project-private filenames when they look sensitive.
- Prefer counts, categories, tool names, workspace basenames, and short sanitized examples.
- Treat shell commands with secrets as sensitive snippets.

## Phase 3: Classify Findings

Create three sections:

1. **Tool adoption** — registered vs actually called, by agent/client, with evidence counts.
2. **Lost opportunities** — where the agent used a worse tool. Separate hard misses from candidates.
3. **Behavior/productivity themes** — repeated user frustrations, recurring workflow patterns, and quality gaps.

For Toolsmith, classify:

- Hard miss: native `Read`/`Edit`/`Write`, `cat`, `nl`, or broad `sed -n` on >200-line files.
- Candidate: `apply_patch` on a large file after a search/read could have used anchors, but may still be acceptable.
- Positive adoption: `file_skeleton`, `find_and_anchor`, `get_function`, `anchored_read`, `anchored_edit`, `symbol_replace`.

## Phase 4: Convert Observations Into Improvements

For each repeated pattern, propose one of:

- **Skill** — when judgment, sequencing, or cross-tool behavior matters.
- **Script** — when the action is deterministic and repeatable.
- **Project instruction** — when it is repo-specific and should activate automatically.
- **Tool/MCP improvement** — when missing affordances prevent agents from doing the right thing.

Use this table:

| Signal | Better artifact |
|---|---|
| Same review checklist repeated | Skill |
| Same shell command chain repeated | Script |
| Same repo-specific gotcha repeated | CLAUDE.md / AGENTS.md update |
| Agents know the right thing but forget | Prompt snippet / guardrail |
| Agents cannot inspect evidence cheaply | Toolsmith/MCP feature |

## Phase 5: Write the Report

Store reports in:

- Temporary artifacts: `~/dev/agent-notes/<project>/`
- Durable reports: Obsidian project folder if the user asks or the work should guide future sessions

Include:

- Date range and hosts
- What was scanned
- Adoption verdict
- Lost-opportunity examples, sanitized
- Skills/scripts/tools to add next
- Follow-up observation plan

</process>

<scripts>

Use `scripts/collect_toolsmith_scan.py` to run local and remote Toolsmith scans and write a combined Markdown report.

</scripts>

<interlocks>

- Use `remote-host-verifier` when comparing a command across local and remote hosts.
- Use `skill-creator` when turning findings into new skills.
- Use `status-copy-trust-audit` when confusing CLI output appears repeatedly in logs.

</interlocks>
