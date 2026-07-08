---
name: fleet-mesh
description: Check personal fleet ssh/et reachability over Tailscale, then flag duplicate private keys, dead etserver, stale IPs, and missing Host entries.
display_name: "Fleet Mesh"
brand_color: "#0EA5E9"
local_only: true
group: "Utilities"
usage: "/fleet-mesh:check"
summary: "Verify every host can ssh/et every other host, and catch the hygiene problems that quietly break it"
default_prompt: "Run the fleet-mesh check from this host and report the reachability matrix and any hygiene findings. If a link is down or a key/config problem is found, diagnose it and propose the fix before changing anything."
---

# Fleet Mesh

Mechanizes the recurring "can every box still reach every other box, and is the key/config hygiene sane?" check for the personal Tailscale fleet. Replaces hand-running an N×N ssh/et matrix and eyeballing `~/.ssh/` across machines.

## When to use

- After adding/removing a host, rotating keys, or a Tailscale/OS upgrade.
- When "I can't ssh/et to X" — get the full matrix instead of guessing.
- Periodically, as an upkeep heartbeat.

## Run it

```bash
skills/fleet-mesh/scripts/mesh-check.sh            # matrix + hygiene
skills/fleet-mesh/scripts/mesh-check.sh --matrix   # reachability only
skills/fleet-mesh/scripts/mesh-check.sh --hygiene  # hygiene only
```

Run from any fleet host that has the `Host <name>` ssh aliases to the others (every fleet host should). Exit code is non-zero if any link is down or a critical hygiene issue is found, so it works in cron/CI too.

## What it checks

**Reachability matrix** — for every ordered pair, `ssh` (and `et` where `et=yes` in `fleet.conf`). `et` is bootstrapped over ssh, so an ssh-ok / et-DOWN row means etserver isn't listening, not an auth problem.

**Hygiene** (the failure modes actually hit building this mesh):
- **Duplicate private keys** — the same private-key fingerprint held by more than one host. That's one key copied across machines: it defeats per-host revocation/audit and lets one box impersonate another. Each host should hold a unique identity key.
- **Dead etserver** — `et=yes` host not listening on `:2022` (so et fails even though ssh works). On macOS the persistent fix is a launchd daemon binding the *current* Tailscale IP (don't hardcode it — TS IPs can change).
- **Stale config** — a non-shared peer addressed by a hardcoded IPv4 instead of its MagicDNS FQDN, or a missing `Host` entry. Hardcoded IPs rot when Tailscale reassigns; FQDNs don't. (Shared cross-tailnet nodes are exempt — their short names don't resolve, so IP is expected there.)

## Configure

Edit `scripts/fleet.conf` — one line per host: `name  address(FQDN-or-IP)  et(yes|no)  shared(yes|no)`. `name` must be the ssh-config `Host` alias that works on every fleet host. `FLEET_CONF=/path` overrides the location.

## Conventions this mesh follows (so the checks stay green)

- One **unique** ed25519 key per host (`carl@<host>`); each host's *public* key in the others' `authorized_keys`. Never copy a private key.
- ssh-config `Host` aliases use **MagicDNS FQDNs** (`<host>.moose-alpha.ts.net`), not IPs — except shared cross-tailnet nodes, reached by IP.
- `StrictHostKeyChecking accept-new` on mesh entries so first-connects auto-learn host keys (non-interactive ssh can't answer the prompt → "Host key verification failed").
- sshd via native Remote Login (reboot-persistent); etserver as a launchd daemon bound to the live Tailscale IP; Tailscale in **Run Unattended** (`UnattendedMode=always`) so the box is reachable before login.

## Repair

The script is read-only by design — it tells you what's wrong; you (or the agent) fix with intent. Common fixes: mint a unique key + distribute pubkey + retire the shared one; install et + launchd etserver; swap a hardcoded IP for the FQDN and add `accept-new`.
