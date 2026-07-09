---
name: vesta-penates
description: "Operate Carl's vesta host: Jolly Roger Jukebox, concierge, nginx/Tailscale/Cloudflare 521s, media containers, backups, and AI-agent restore runbooks."
display_name: "Vesta Penates"
brand_color: "#F97316"
local_only: true
group: "Homelab & Personal Ops"
usage: "/vesta-penates:run"
summary: "Operate vesta host, media stack, nginx/Tailscale/Cloudflare, and restore runbooks"
default_prompt: "Check vesta health with the Penates scripts, diagnose any failures read-only first, and propose the safest fix before running live repair commands."
---

# vesta-penates

Operate vesta through deterministic Penates scripts first, then adapt manually only when the scripted path cannot cover the observed failure.

## Trigger situations

Use this skill for requests involving:

- vesta host health, SSH/mosh recovery, DNS, memory, reboot loops, or failed services
- jollyrogerjukebox.com, concierge, nginx, Cloudflare 521, Tailscale Serve, or public HTTPS smokes
- media-stack containers: concierge, jellyfin, kavita, audiobookshelf, jellyseerr, sabnzbd, flaresolverr, sonarr, radarr, prowlarr
- capturing important configs and restore instructions for an AI agent
- validating that a previous concierge/media-stack repair is still holding

## Deterministic first path

Run the local ops project from Carl's Mac:

```bash
cd /Users/carl/dev/me/penates
bin/penates vesta health --host vesta
```

For the known nginx/Tailscale/Cloudflare concierge failure, dry-run first unless the user already asked to fix it:

```bash
bin/penates vesta fix-concierge --host vesta
bin/penates vesta fix-concierge --host vesta --live
```

For durable backup/runbook capture:

```bash
bin/penates vesta backup-concierge --host vesta
bin/penates vesta backup-concierge --host vesta --live
```

Use `--live` only for intentional mutation. Health checks are read-only.

## Golden invariants

Preserve these unless new evidence proves they changed:

- Public nginx vhosts must bind the LAN IPv4 address, currently `192.168.1.100:443`, not bare `listen 443 ssl;`.
- Bare `listen 443 ssl;` collides with Tailscale Serve on tailnet `:443` and can produce Cloudflare 521.
- Canonical media compose file: `/opt/media-stack/docker-compose.yml`.
- nginx compose file: `/opt/nginx-compose.yml`.
- Concierge repo: `/home/carl/dev/me/concierge`; env file: `/home/carl/dev/me/concierge/.env`; upstream: `127.0.0.1:5070`.
- Secure backups live under `/opt/backups/concierge-media-stack-<timestamp>` and are root-only.
- Human/agent restore docs should also be readable at `/home/carl/dev/agent-notes/vesta/concierge-media-stack-restore.md` and `/opt/backups/concierge-media-stack-restore.md`.

## Manual escalation pattern

If deterministic commands fail:

1. Capture exact failing command and stderr.
2. Check `systemctl --failed --no-pager`, `free -h`, `ss -ltnp`, and `docker ps -a`.
3. Check nginx bind collision before touching app code: `ss -ltnp | grep ':443'`.
4. Check compose labels before recreating containers: `docker inspect -f '{{.Name}} {{index .Config.Labels "com.docker.compose.project.config_files"}} {{.HostConfig.RestartPolicy.Name}} {{.State.Status}}' <container>`.
5. Prefer reconciling containers back to canonical compose files over one-off `docker run` repairs.
6. After any repair, run `bin/penates vesta health --host vesta` and capture a fresh `backup-concierge --live` when configs changed.

## Secret handling

Never print or paste `.env`, private keys, tokens, cookies, DSNs, cert private material, or full config files that may include secrets. Use redacted copies or file paths in chat. Store sensitive backups root-only.
