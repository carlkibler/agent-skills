---
name: remote-host-verifier
description: "Compare commands, versions, config, and behavior across local and SSH hosts."
display_name: "Remote Host Verifier"
brand_color: "#0369A1"
local_only: true
group: "Dev Workflow"
usage: "/remote-host-verifier:run"
summary: "Prove a fix works on the real remote machine, not just your laptop, before you call it done."
default_prompt: "Verify this command locally and on the named remote host(s). Capture versions, paths, output differences, and a final pass/fail verdict with exact commands."
---

# Remote Host Verifier

Use when "works on my machine" is not enough.

Third-order stance: do not stop at whether the command works now. Ask whether this host will diverge, decay, or betray the next agent tomorrow because PATH, time, shell startup, package source, disk, or dotfiles are drifting.

## When to Use

- The user names a remote host (an SSH alias such as `devbox`)
- A CLI install/update/release must work on more than one machine
- You need to compare local vs remote config, version, path, or behavior
- A remote machine has more representative data than the current one
- The task depends on environment parity, time sync, package provenance, or user-level dotfiles

## When NOT to Use

- The command is destructive and no dry-run mode exists
- The user hasn't said which hosts you may connect to (don't pick hosts from ~/.ssh/config yourself)
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

Capture exact hostnames. Do not assume an SSH alias points where it did last time. Use non-interactive SSH (`ssh -o BatchMode=yes <host> ...`) so a password or host-key prompt fails fast instead of hanging; if it fails, report the connection error rather than guessing.

Also capture environment risk signals before trusting the comparison:

```bash
ssh <host> 'date -u "+%Y-%m-%dT%H:%M:%SZ"; uptime; df -h .; echo "$SHELL"; printf "%s\n" "$PATH"'
date -u "+%Y-%m-%dT%H:%M:%SZ"; uptime; df -h .; echo "$SHELL"; printf "%s\n" "$PATH"
```

Look for time skew, nearly-full disks, different shells, and PATH order changes. These are predictive failures: the current command may pass while the next release/update fails.

## Phase 2: Compare the Same Command

Run the smallest equivalent command locally and remotely. Prefer JSON output where available.

```bash
# path relative to this skill's directory; add --probe-env for time/PATH/disk probes
python3 scripts/remote_compare.py --host <host> --probe-env -- <tool> doctor --smoke --json
```

For a mutating command, use a documented read-only or dry-run mode, or an authorized disposable workspace. A `--json` flag changes output format and does not establish read-only behavior.

## Phase 3: Normalize and Interpret

Strip terminal noise and compare:

- version
- binary path
- config path
- installed package source
- command output
- exit status
- notable stderr
- time, PATH, shell, disk, and package-manager drift

Classify differences as:

- **Expected** — hostname, local paths, data volume
- **Action needed** — old version, missing command, config points at stale checkout
- **Unknown** — needs another command to explain
- **Predictive failure** — works now but environmental drift makes the next command risky

## Phase 4: Close the Loop

If release/install/update was the goal, finish with:

```bash
<tool> --version
<tool> doctor --smoke
ssh <host> '<tool> --version; <tool> doctor --smoke'
```

Report only after both sides have evidence. Finish with a verdict per host (PASS / FAIL / INCONCLUSIVE), the exact commands run, the differences classified as above, and a small "tomorrow risk" note if drift is present even when the command passes. Stop once each named host has a verdict; don't widen to other hosts.

</process>

<scripts>

Use `scripts/remote_compare.py` to run the same command locally and on one or more SSH hosts and emit text or JSON. Add `--probe-env` to include time, shell, PATH, cwd, disk, and uptime probes.

</scripts>

<interlocks>

- Use `release-operator` before publishing a CLI that must update on remote hosts.
- Use `agent-log-forensics` when the remote host has the richer agent logs to scan.
- Use `chezmoi-drift` when environment parity points at dotfile or shared-skill drift.

</interlocks>
