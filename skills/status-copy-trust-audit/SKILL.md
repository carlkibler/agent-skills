---
name: status-copy-trust-audit
description: Audit CLI/app status output for confusing, inconsistent, or trust-eroding wording; verify idempotent repeated runs and align labels across clients.
display_name: "Status Copy Trust Audit"
brand_color: "#B45309"
local_only: true
group: "Better Products"
usage: "/status-copy-trust-audit:run"
summary: "Make status/update/doctor output explain exactly what changed and why"
default_prompt: "Audit this CLI/status output. Make the states consistent, idempotent, and plain-language. Verify repeated runs and update tests/docs so the output stays trustworthy."
---

# Status Copy Trust Audit

Status text is product UI. If it says "updated" when nothing updated, trust leaks out through a tiny hole and then somehow the whole boat is wet.

## When to Use

- The user says output is odd, confusing, or "not sure what happened"
- Repeated runs print different words for equivalent states
- Commands like update/setup/doctor/register/install report both no-op and changed states
- Scope, provenance, or safety status is unclear

## When NOT to Use

- The output is purely internal debug logging
- The command has no user-facing status surface
- The issue is a real functional failure, not wording/state semantics

---

<process>

## Phase 1: Capture Real Transcripts

Run the command at least twice. If scope flags exist, test the default and explicit scope.

```bash
<tool> update
<tool> update
<tool> update --scope user
<tool> doctor --smoke
```

Keep exact stdout/stderr snippets in notes or tests.

## Phase 2: Define State Semantics

For each line, label what it means:

| Word | Should mean |
|---|---|
| registered | created a missing config entry |
| refreshed | rewrote an existing config entry intentionally |
| already configured | no write happened |
| updated | package/binary version changed |
| already current | package/binary did not change |
| skipped | user requested no action or client missing |

Never use "updated" for both package version changes and config refreshes.

## Phase 3: Align Related Clients

If multiple clients are shown together, make their grammar parallel:

```text
Claude Code: refreshed (scope: user)
Codex: refreshed
Gemini CLI: refreshed (scope: user, trusted)
```

If one client has extra concepts (scope/trust), state them explicitly rather than omitting them elsewhere.

## Phase 4: Verify Idempotence

Second run should be boring and explain whether it wrote anything. Decide intentionally between:

- default no-op for idempotent setup
- forced refresh for update commands that must rewrite local paths after package changes

If update refreshes registrations by default, document why and provide an opt-out such as `--no-setup`.

## Phase 5: Lock It Down

Add tests for:

- aliases (`doc` -> `doctor`, `install` -> `setup`)
- repeated update/setup output
- no-op vs refresh vs version change wording
- scope/trust label consistency

</process>

<interlocks>

- Use `release-operator` before shipping changed status text.
- Use `remote-host-verifier` to confirm the same status semantics on remote hosts.

</interlocks>
