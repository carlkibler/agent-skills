#!/usr/bin/env bash
# Runs ON a fleet host. Args: target specs "name:et" (et = yes|no).
# Prints one line per target: ssh + et reachability. Self-contained, no `timeout` needed
# (macOS lacks it) — uses a perl-based alarm so a hung et/ssh can't wedge the probe.
to(){ perl -e 'my $t=shift;my $p=fork;if($p==0){exec @ARGV or exit 127}local $SIG{ALRM}=sub{kill 9,$p;exit 124};alarm $t;waitpid $p,0;exit($?>>8)' "$@"; }
rc=0
for spec in "$@"; do
  t=${spec%%:*}; tet=${spec##*:}
  printf "  -> %-10s ssh:" "$t"
  if to 12 ssh -o ConnectTimeout=8 -o BatchMode=yes "$t" true >/dev/null 2>&1; then printf "ok "; else printf "DOWN"; rc=1; fi
  if [ "$tet" = yes ]; then
    printf "  et:"
    # et is slower than ssh and needs a brief cooldown between back-to-back -c sessions;
    # settle + retry once so the sweep doesn't report false DOWNs.
    ok=0
    for try in 1 2; do
      if TERM=xterm-256color to 25 et "$t" -c 'echo __ETOK__' 2>/dev/null | grep -aq __ETOK__; then ok=1; break; fi
      sleep 2
    done
    if [ "$ok" = 1 ]; then printf "ok"; else printf "DOWN"; rc=1; fi
  else
    printf "  et:n/a"
  fi
  echo
done
exit $rc
