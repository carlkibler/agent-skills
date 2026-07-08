#!/usr/bin/env bash
# fleet-mesh: verify the ssh+et mesh and surface key/config hygiene problems.
# Read-only. Run from any fleet host that has ssh-config aliases to the others.
#
#   mesh-check.sh                 # matrix + hygiene
#   mesh-check.sh --matrix        # reachability only
#   mesh-check.sh --hygiene       # hygiene only
#   FLEET_CONF=/path mesh-check.sh
#
# Exit 0 = all links up and no critical hygiene finding; 1 = something needs attention.
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="${FLEET_CONF:-$DIR/fleet.conf}"
PROBE="$DIR/mesh-probe.sh"
AUDIT="$DIR/host-audit.sh"
MODE="${1:-all}"
me="$(hostname -s 2>/dev/null || hostname)"
problems=0

HOSTS=(); declare -A ET ADDR SHARED
while read -r name addr et shared _; do
  [[ -z "${name:-}" || "$name" == \#* ]] && continue
  HOSTS+=("$name"); ET[$name]=$et; ADDR[$name]=$addr; SHARED[$name]=$shared
done < "$CONF"

run_on(){ # host, then stdin script, then args
  local h=$1; shift
  if [ "$h" = "$me" ]; then bash /dev/stdin "$@"
  else ssh -o ConnectTimeout=8 -o BatchMode=yes "$h" 'bash -s' "$@" 2>/dev/null; fi
}

matrix(){
  echo "### Reachability matrix (ssh + et)"
  for origin in "${HOSTS[@]}"; do
    local specs=()
    for t in "${HOSTS[@]}"; do [ "$t" = "$origin" ] && continue; specs+=("$t:${ET[$t]}"); done
    echo "FROM $origin:"
    if ! run_on "$origin" "${specs[@]}" < "$PROBE"; then problems=1; fi
  done
}

hygiene(){
  echo "### Hygiene"
  local tmp; tmp="$(mktemp)"
  for h in "${HOSTS[@]}"; do
    run_on "$h" "${HOSTS[@]}" < "$AUDIT" 2>/dev/null | sed "s/^/$h /" >> "$tmp" || echo "$h UNREACHABLE" >> "$tmp"
  done

  # 1) duplicate PRIVATE keys across hosts (same fingerprint held by >1 host)
  echo "-- duplicate private keys across hosts --"
  if awk '
      $2=="IDKEY" && !((($3) SUBSEP ($1)) in seen) { seen[($3) SUBSEP ($1)]=1; cnt[$3]++; who[$3]=who[$3]" "$1"("$4")" }
      END { bad=0; for(fp in cnt) if(cnt[fp]>1){ print "  DUP "fp":"who[fp]; bad=1 } exit bad }' "$tmp"; then
    echo "  none"
  else
    echo "  ^ a private key is copied across machines — mint a unique per-host key and retire the shared one"; problems=1
  fi

  # 2) etserver listening where expected
  echo "-- etserver listening (expected per fleet.conf) --"
  for h in "${HOSTS[@]}"; do
    [ "${ET[$h]}" = yes ] || continue
    local lst; lst=$(awk -v H="$h" '$1==H&&$2=="ETLISTEN"{print $3}' "$tmp")
    if [ "$lst" = yes ]; then echo "  $h: ok"; else echo "  $h: NOT LISTENING on :2022"; problems=1; fi
  done

  # 3) stale config: a non-shared peer addressed by bare IPv4 (should be FQDN) or MISSING
  echo "-- ssh-config HostName staleness --"
  local found=0
  while read -r host _ peer val; do
    [ "$val" = MISSING ] && { echo "  $host -> $peer: no Host entry"; found=1; problems=1; continue; }
    if [[ "$val" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ && "${SHARED[$peer]:-no}" = no ]]; then
      echo "  $host -> $peer: hardcoded IP $val (peer is not shared; prefer FQDN ${ADDR[$peer]})"; found=1; problems=1
    fi
  done < <(awk '$2=="CFG"{print $1, $2, $3, $4}' "$tmp")
  [ "$found" = 0 ] && echo "  none"
  rm -f "$tmp"
}

case "$MODE" in
  --matrix) matrix;;
  --hygiene) hygiene;;
  all|"") matrix; echo; hygiene;;
  -h|--help) sed -n '2,12p' "$0"; exit 0;;
  *) echo "unknown arg: $MODE"; exit 2;;
esac
echo
if [ "$problems" = 0 ]; then echo "RESULT: mesh healthy"; else echo "RESULT: attention needed (see above)"; fi
exit $problems
