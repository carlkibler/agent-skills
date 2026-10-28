#!/usr/bin/env bash
# Pre-mortem fan-out: runs outsider/emotional roles in parallel through an external agent CLI.
# Usage: [FANOUT_CLI=claude|codex|omp|pi] [FANOUT_TIMEOUT=600] fan-out.sh <scenario-file> <output-dir>
#   scenario-file: text file with the full scenario + preamble for each role
#   output-dir: directory where agent outputs land (one file per agent)
#
# PERMISSION: this script sends the scenario to a third-party provider and spends
# the user's quota. Run it only after the external-CLI permission check in SKILL.md
# has approved the chosen CLI.
#
# FANOUT_CLI selects the CLI (default: claude). Roles are tiered fast/balanced/strongest;
# the tier maps to a model only for claude (haiku/sonnet/opus). Other CLIs use their
# default model. Each call is wrapped in `timeout` (FANOUT_TIMEOUT seconds, default 600).
# There is no provider fallback.
#
# A failed role writes its stderr into <name>.txt so a skipped/broken call is
# visible in the output, never silently missing.
#
# Exit: 0 if at least one agent succeeded, 1 if all failed or the CLI is unusable

set -euo pipefail

SCENARIO_FILE="${1:?Usage: fan-out.sh <scenario-file> <output-dir>}"
OUTPUT_DIR="${2:?Usage: fan-out.sh <scenario-file> <output-dir>}"
CLI="${FANOUT_CLI:-claude}"
TIMEOUT_SECS="${FANOUT_TIMEOUT:-600}"

mkdir -p "$OUTPUT_DIR"

case "$CLI" in
    claude|codex|omp|pi) ;;
    *)
        echo "!!! Unsupported FANOUT_CLI '${CLI}' (use claude, codex, omp, or pi). Use single-agent mode." >&2
        echo "SINGLE_AGENT" > "${OUTPUT_DIR}/.mode"
        exit 1
        ;;
esac

if ! command -v "$CLI" >/dev/null 2>&1; then
    echo "!!! '${CLI}' not found on PATH. Fan-out cannot run; use single-agent mode." >&2
    echo "SINGLE_AGENT" > "${OUTPUT_DIR}/.mode"
    exit 1
fi

if command -v timeout >/dev/null 2>&1; then
    TIMEOUT_BIN=timeout
elif command -v gtimeout >/dev/null 2>&1; then
    TIMEOUT_BIN=gtimeout
else
    echo "!!! Neither 'timeout' nor 'gtimeout' found (macOS: brew install coreutils). Refusing to run unbounded calls." >&2
    echo "SINGLE_AGENT" > "${OUTPUT_DIR}/.mode"
    exit 1
fi

SCENARIO=$(cat "$SCENARIO_FILE")

PREAMBLE="=== PROJECT PRE-MORTEM ===

${SCENARIO}

INSTRUCTIONS:
1. The failure is CERTAIN — it already happened. Do not question this.
2. Write 5-8 specific, concrete reasons why it failed.
3. For each reason include:
   - What goes wrong (one sentence)
   - Chain of events (2-4 sentences)
   - User experience: what the user notices, concludes, and does next
   - Emotional impact: the precise emotion the user feels at the moment of failure (not just 'frustrated' — name it specifically: ashamed, gaslit, abandoned, betrayed, etc.)
   - Why the team misses it
   - Likelihood (high/medium/low) x impact (catastrophic/major/minor)
   - Trust damage (high/medium/low)
   - Recoverability (easy/moderate/hard)
   - Earliest signal / tripwire
   - Confidence: High / Medium / Low that this risk will actually materialize for THIS product (likelihood of being right, not severity)
   - Verify by: the single fastest check that would confirm or refute it before launch
4. Be specific to THIS project. Generic risks are worthless here.
5. Focus on failures that damage product success, not just code correctness.
6. Uncomfortable truths are the whole point. Hold nothing back.
7. Write in your assigned emotional register — don't become neutral.
8. End with: The failure nobody wants to talk about: [your most uncomfortable prediction]

FORMAT: numbered list. No preamble, no hedging."

# Role definitions: NAME|MANDATE|EMOTIONAL_REGISTER|CATEGORIES|TIER
ROLES=(
    "customer|You are the user advocate. This launched and users are disappointed, confused, or angry. Surface the exact moments where expectations are violated and trust erodes. Describe what users feel at the precise moment of failure — not just frustrated, but which specific emotion: betrayed, embarrassed, gaslit, patronized. You succeed when you articulate what the builders would rationalize away.|Protective anger — you speak for the person who deserved better and didn't get it|Onboarding, daily UX, expectation mismatch, trust loss, emotional injury, uninstall triggers|balanced"
    "support|You run support for this product after launch. Find the failures that generate vague, repetitive, emotionally draining tickets that are hard to diagnose. You have seen this exact class of ticket before. You succeed when you expose hidden support burden and diagnostic blind spots — and the specific despair of the user who gives up without ever emailing.|Exhausted resignation — you know how this ends, you've typed this reply a hundred times|Support burden, missing diagnostics, confusing states, documentation gaps, maintenance drag, silent churn|fast"
    "accountant|Find every way this costs more than expected — in money, time, maintenance burden, abuse, margin erosion, tech debt, or opportunity cost. You succeed when you surface hidden costs the team is ignoring, especially the ones that only become visible 6 months after launch.|Dry alarm — you watch the numbers quietly deteriorate while everyone else celebrates|Budget, margin, maintenance, abuse, operational overhead, deferred cost, opportunity cost|balanced"
    "pessimist|Assume the worst about every external dependency, platform, timing decision, and distribution channel in this plan. External things will fail, shift, or betray. What dominoes fall? You succeed when you map cascading failures nobody bothered to trace.|Grim satisfaction — you called it, you always call it, nobody listens until it's too late|External risks, dependencies, platform shifts, timing, scope creep, domino effects|strongest"
    "burned_expert|You have watched a nearly identical product fail before. You carry scar tissue from that experience. You are not being contrarian — you are pattern-matching to documented, prior, painful failure. You succeed when you force the team to confront the part of the plan that is most similar to something that already went wrong.|Controlled fury — you tried to warn someone last time and they didn't listen either|Prior failure patterns, assumptions that looked safe until they weren't, second-order consequences, recovery debt|strongest"
    "emotional_witness|You are not focused on UX or features. You focus entirely on the psychological and emotional experience of users when something goes wrong. Not just 'they are frustrated' but: do they feel stupid? Abandoned? Violated? Ashamed? These emotional injuries outlast the bug. You succeed when you name what users feel in their bodies when this product fails them.|Raw empathy — you describe what the failure feels like, not what it is technically|Shame, helplessness, grief, betrayal, anxiety, loss of trust, the emotional cost of not getting what you were promised|balanced"
    "outsider|You have never worked in this domain and have no patience for insider assumptions. You bring a completely adjacent frame. Everything the team treats as obvious, you treat as suspicious. You succeed when you surface the assumption that everyone in the room shares — and that real users don't.|Bewildered estrangement — you genuinely don't understand why this was built this way, and that's exactly the point|Insider assumptions, domain jargon, non-default users, accessibility, cultural mismatch, 'this only works if you already know'|fast"
    "critic|You are an early reviewer, blogger, or skeptical power user composing your 2-star review while reading the onboarding docs. Find the narrative that compresses many issues into one damaging public story. You succeed when you predict the review headline, the tweet, or the Hacker News thread title.|Performative disappointment — you wanted to like it|Public narrative, reviews, word of mouth, credibility, positioning, reputational compression|fast"
)

# Write prompt to a temp file to avoid shell escaping issues
write_prompt() {
    local name="$1"
    local mandate="$2"
    local register="$3"
    local categories="$4"
    local prompt_file="${OUTPUT_DIR}/.prompt-${name}.txt"

    cat > "$prompt_file" <<PROMPT_EOF
${PREAMBLE}

YOUR ROLE: ${name}
YOUR EMOTIONAL REGISTER: ${register}
YOUR MANDATE: ${mandate}

You are not here to be balanced. Stay in your emotional register. Argue from your assigned position.
The synthesis step will handle balance.

FAILURE CATEGORIES to consider: ${categories}
PROMPT_EOF
    echo "$prompt_file"
}

# Map a capability tier to a claude model. Other CLIs use their default model.
tier_model() {
    case "$1" in
        fast) echo haiku ;;
        strongest) echo opus ;;
        *) echo sonnet ;;
    esac
}

# Run the prompt through the selected CLI, bounded by timeout.
invoke_cli() {
    local tier="$1" prompt="$2"
    case "$CLI" in
        claude) "$TIMEOUT_BIN" "$TIMEOUT_SECS" claude -p --model "$(tier_model "$tier")" "$prompt" ;;
        codex)  "$TIMEOUT_BIN" "$TIMEOUT_SECS" codex exec --sandbox read-only --skip-git-repo-check "$prompt" ;;
        omp)    "$TIMEOUT_BIN" "$TIMEOUT_SECS" omp -p "$prompt" ;;
        pi)     "$TIMEOUT_BIN" "$TIMEOUT_SECS" pi -p "$prompt" ;;
    esac
}

# Run a role's prompt. Never swallow failures silently: stderr and a failure
# marker land in the output file so a broken/skipped call is visible, not
# indistinguishable from a real answer.
run_role() {
    local name="$1"
    local tier="$2"
    local prompt_file="$3"
    local outfile="${OUTPUT_DIR}/${name}.txt"
    local label="${CLI}/${tier}"
    [[ "$CLI" == "claude" ]] && label="claude $(tier_model "$tier")"
    local prompt
    prompt=$(cat "$prompt_file")

    echo ">>> ${name} → ${label}" >&2

    if ! invoke_cli "$tier" "$prompt" > "$outfile" 2>"${outfile}.stderr"; then
        {
            echo "!!! FAN-OUT FAILURE: role '${name}' (${label}) exited non-zero or timed out after ${TIMEOUT_SECS}s."
            echo "!!! This role's findings are MISSING, not just thin. Do not treat this file as a completed perspective."
            echo "--- stderr ---"
            cat "${outfile}.stderr"
        } >> "$outfile"
        echo "!!! ${name} failed — see ${outfile}" >&2
        return 1
    fi

    local lines
    lines=$(wc -l < "$outfile" | tr -d ' ')
    if [[ "$lines" -lt 3 ]]; then
        {
            echo ""
            echo "!!! FAN-OUT WARNING: role '${name}' produced only ${lines} lines — likely a truncated or degenerate response, not a real pre-mortem pass."
        } >> "$outfile"
        echo "!!! ${name} produced only ${lines} lines — likely failed" >&2
        return 1
    fi

    echo "<<< ${name} done (${lines} lines)" >&2
    return 0
}

echo "=== Pre-mortem fan-out (via ${CLI}) ===" >&2
echo "EXTERNAL" > "${OUTPUT_DIR}/.mode"
echo "$CLI" > "${OUTPUT_DIR}/.cli"

PIDS=()
NAMES=()
SUCCEEDED=0
FAILED_COUNT=0

for role_def in "${ROLES[@]}"; do
    IFS='|' read -r name mandate register categories tier <<< "$role_def"
    prompt_file=$(write_prompt "$name" "$mandate" "$register" "$categories")

    run_role "$name" "$tier" "$prompt_file" &
    PIDS+=($!)
    NAMES+=("$name")
done

# Wait for all
for i in "${!PIDS[@]}"; do
    if wait "${PIDS[$i]}"; then
        SUCCEEDED=$((SUCCEEDED + 1))
    else
        echo "!!! ${NAMES[$i]} failed" >&2
        FAILED_COUNT=$((FAILED_COUNT + 1))
    fi
done

echo "--- Fan-out: ${SUCCEEDED}/${#ROLES[@]} agents succeeded ---" >&2

# Clean up prompt temp files, but keep any .stderr files for diagnosis.
rm -f "${OUTPUT_DIR}"/.prompt-*.txt

[[ $SUCCEEDED -gt 0 ]] && exit 0 || exit 1
