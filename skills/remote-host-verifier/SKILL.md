---
name: remote-host-verifier
description: Verify commands across this machine and named SSH hosts, comparing versions, install paths, config, and behavior with clean local/remote evidence.
display_name: "Remote Host Verifier"
brand_color: "#0369A1"
local_only: true
group: "Dev Workflow"
usage: "/remote-host-verifier:run"
summary: "Compare local and remote host behavior before declaring a tool fixed"
default_prompt: "Verify this command locally and on the named remote host(s). Capture versions, paths, output differences, and a final pass/fail verdict with exact commands."
---

# Remote Host Verifier

Use when "works on my machine" is not enough.

## When to Use

- The user names a remote host such as `vesta`
- A CLI install/update/release must work on more than one machine
- You need to compare local vs remote config, version, path, or behavior
- A remote machine has more representative data than the current one

## When NOT to Use

- The command is destructive and no dry-run mode exists
- The user did not name or imply remote validation
- The result depends on GUI state you cannot inspect over SSH

---

<process>

## Phase 1: Verify Connectivity and Identity

Run safe checks first:

```bash
hostname
command -v <tool>
<tool> --version
ssh <host> 'hostname; command -v <tool>; <tool> --version'
```

Capture exact hostnames. Do not assume `vesta` points where it did last time.

## Phase 2: Compare the Same Command

Run the smallest equivalent command locally and remotely. Prefer JSON output where available.

```bash
python3 skills/remote-host-verifier/scripts/remote_compare.py --host vesta -- toolsmith doctor --smoke --json
```

If a command mutates state, look for `--dry-run`, `--check`, `--json`, `--no-setup`, or a disposable temp workspace first.

## Phase 3: Normalize and Interpret

Strip terminal noise and compare:

- version
- binary path
- config path
- installed package source
- command output
- exit status
- notable stderr

Classify differences as:

- **Expected** — hostname, local paths, data volume
- **Action needed** — old version, missing command, config points at stale checkout
- **Unknown** — needs another command to explain

## Phase 4: Close the Loop

If release/install/update was the goal, finish with:

```bash
<tool> --version
<tool> doctor --smoke
ssh <host> '<tool> --version; <tool> doctor --smoke'
```

Report only after both sides have evidence.

</process>

<scripts>

Use `scripts/remote_compare.py` to run the same command locally and on one or more SSH hosts and emit text or JSON.

</scripts>

<interlocks>

- Use `release-operator` before publishing a CLI that must update on remote hosts.
- Use `agent-log-forensics` when the remote host has the richer agent logs to scan.

</interlocks>
