#!/usr/bin/env bash
# Runs ON a fleet host. Emits a compact, machine-parseable hygiene dump for the driver.
# Read-only. Lines: "KIND value..." prefixed with the host name by the driver.
# IDKEY  = a PRIVATE identity key this host holds (fingerprint + filename). Same fp on two
#          hosts => one private key copied across machines (the thing to never do).
# ETLISTEN = is etserver actually listening on :2022
# CFG    = HostName value configured for each fleet peer (catches stale hardcoded IPs)

me=$(hostname -s 2>/dev/null || hostname)
# etserver runs as root; unprivileged lsof can't see its socket, so detect the process instead.
echo "ETLISTEN $( pgrep -x etserver >/dev/null 2>&1 && echo yes || echo no )"
echo "HASET $(command -v et >/dev/null 2>&1 && echo yes || echo no)"
for f in "$HOME"/.ssh/id_ed25519 "$HOME"/.ssh/id_ed25519_*; do
  case "$f" in *.pub) continue;; esac
  [ -f "$f" ] || continue
  fp=$(ssh-keygen -lf "$f.pub" 2>/dev/null | awk '{print $2}')
  [ -n "$fp" ] && echo "IDKEY $fp ${f##*/}"
done
while read -r _ peer; do
  [ -z "${peer:-}" ] && continue
  [ "$peer" = "$me" ] && continue   # a host needs no Host entry for itself
  hn=$(awk -v h="$peer" '$1=="Host"&&$2==h{f=1;next} f&&$1=="Host"{f=0} f&&$1=="HostName"{print $2;exit}' "$HOME/.ssh/config" 2>/dev/null)
  echo "CFG $peer ${hn:-MISSING}"
done < <(printf 'x %s\n' "$@")
