#!/usr/bin/env bash
# Dry-run contract tests for bin/agent. No network/API key required.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
AGENT="$ROOT/bin/agent"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

assert_contains() {
  local file="$1"
  local needle="$2"
  grep -Fq -- "$needle" "$file" || {
    echo "--- $file ---" >&2
    cat "$file" >&2
    fail "expected to find: $needle"
  }
}

assert_not_contains() {
  local file="$1"
  local needle="$2"
  if grep -Fq -- "$needle" "$file"; then
    echo "--- $file ---" >&2
    cat "$file" >&2
    fail "did not expect to find: $needle"
  fi
}

assert_fails() {
  local name="$1"
  shift
  if "$@" >"$TMPDIR/$name.out" 2>"$TMPDIR/$name.err"; then
    echo "--- $TMPDIR/$name.out ---" >&2
    cat "$TMPDIR/$name.out" >&2
    echo "--- $TMPDIR/$name.err ---" >&2
    cat "$TMPDIR/$name.err" >&2
    fail "$name should have failed"
  fi
}

printf 'FILE ONE\n' > "$TMPDIR/one.txt"
printf 'FILE TWO\n' > "$TMPDIR/two.txt"

bash -n "$AGENT"

printf 'PIPE DATA' | "$AGENT" --dry-run --file "$TMPDIR/one.txt" --context "$TMPDIR/two.txt" flash 'Main prompt' >"$TMPDIR/combined.out" 2>"$TMPDIR/combined.err"
assert_contains "$TMPDIR/combined.err" 'agent: routes=deepseek|deepseek-v4-flash,openrouter|deepseek/deepseek-v4-flash'
assert_contains "$TMPDIR/combined.err" 'files=2'
assert_contains "$TMPDIR/combined.out" 'Main prompt'
assert_contains "$TMPDIR/combined.out" "--- file: $TMPDIR/one.txt ---"
assert_contains "$TMPDIR/combined.out" 'FILE ONE'
assert_contains "$TMPDIR/combined.out" "--- file: $TMPDIR/two.txt ---"
assert_contains "$TMPDIR/combined.out" 'FILE TWO'
assert_contains "$TMPDIR/combined.out" '--- stdin ---'
assert_contains "$TMPDIR/combined.out" 'PIPE DATA'

printf 'PIPE ONLY' | "$AGENT" --dry-run --stdin 'Main prompt' >"$TMPDIR/stdin.out" 2>"$TMPDIR/stdin.err"
assert_contains "$TMPDIR/stdin.out" 'PIPE ONLY'

"$AGENT" --dry-run "@$TMPDIR/one.txt" grok 'Prompt' >"$TMPDIR/atfile.out" 2>"$TMPDIR/atfile.err"
assert_contains "$TMPDIR/atfile.err" 'agent: routes=openrouter|x-ai/grok-4.3'
assert_contains "$TMPDIR/atfile.out" 'FILE ONE'

"$AGENT" --dry-run --no-stdin 'Prompt' < "$TMPDIR/one.txt" >"$TMPDIR/no-stdin.out" 2>"$TMPDIR/no-stdin.err"
assert_contains "$TMPDIR/no-stdin.out" 'Prompt'
assert_not_contains "$TMPDIR/no-stdin.out" 'FILE ONE'

"$AGENT" --dry-run --model=openai/gpt-5.5 --timeout 12 'Prompt' >"$TMPDIR/model-eq.out" 2>"$TMPDIR/model-eq.err"
assert_contains "$TMPDIR/model-eq.err" 'agent: routes=openrouter|openai/gpt-5.5'
assert_contains "$TMPDIR/model-eq.err" 'timeout=12'

"$AGENT" --dry-run --frontier 'Prompt' >"$TMPDIR/frontier.out" 2>"$TMPDIR/frontier.err"
assert_contains "$TMPDIR/frontier.err" 'agent: routes=codex_cli|,openrouter|z-ai/glm-5.2'

"$AGENT" --dry-run opus 'Prompt' >"$TMPDIR/opus.out" 2>"$TMPDIR/opus.err"
assert_contains "$TMPDIR/opus.err" 'agent: routes=claude_cli|opus'
assert_not_contains "$TMPDIR/opus.err" 'openrouter|anthropic'

assert_fails missing "$AGENT" --dry-run --file "$TMPDIR/missing.txt" 'Prompt'
assert_contains "$TMPDIR/missing.err" 'cannot read file'

assert_fails empty-stdin "$AGENT" --dry-run --stdin 'Prompt'
assert_contains "$TMPDIR/empty-stdin.err" 'stdin was empty'

assert_fails bad-temp "$AGENT" --dry-run --temperature high 'Prompt'
assert_contains "$TMPDIR/bad-temp.err" 'must be numeric'

assert_fails bad-timeout "$AGENT" --dry-run --timeout nope 'Prompt'
assert_contains "$TMPDIR/bad-timeout.err" 'must be numeric'

assert_fails bad-max-tokens "$AGENT" --dry-run --max-tokens 0 'Prompt'
assert_contains "$TMPDIR/bad-max-tokens.err" 'positive integer'

"$AGENT" --help >"$TMPDIR/help.out"
assert_contains "$TMPDIR/help.out" '--file, -f PATH'
assert_contains "$TMPDIR/help.out" '--timeout N'
assert_contains "$TMPDIR/help.out" 'agent --file review-packet.md --smart'

printf 'agent dry-run contract tests passed\n'
