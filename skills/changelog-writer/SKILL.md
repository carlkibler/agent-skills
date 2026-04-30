---
name: changelog-writer
description: Generate user-facing changelog entries from git history — plain language, audience-segmented, with optional CHANGELOG.md update.
display_name: "Changelog Writer"
brand_color: "#8B5CF6"
local_only: true
group: "Dev Workflow"
usage: "/changelog-writer:run"
summary: "Transform git commits into user-facing changelog entries segmented by audience"
default_prompt: "Write a user-facing changelog for the changes since the last release. Segment by audience: users, developers, operators. Plain language only — no commit hashes or internal jargon."
---

# Changelog Writer

Turns git commits into changelog entries humans want to read. Covers the gap between "git log --oneline" (too technical) and "nothing" (too common).

## When to Use

- Before a release, version bump, or deployment
- When a CHANGELOG.md needs updating
- When you need release notes for a blog post, email, or app store update
- When commits describe implementation but not user impact

## When NOT to Use

- For internal-only changes with no user-visible effect
- For very first releases (no "since last release" baseline)

---

<process>

## Phase 1: Determine the Scope

Ask or infer:

1. **Git range** — "since last release" (git tags), a specific SHA, or a branch diff. Default: `git log $(git describe --tags --abbrev=0)..HEAD` if tags exist, else `git log HEAD~20..HEAD`.
2. **Audiences** — which sections to generate. Default: all three (Users, Developers, Operators). Skip any that aren't relevant.
3. **Format** — CHANGELOG.md (Keep a Changelog format), Markdown for a blog post, or plain text for an email.
4. **Version** — if known, use it. Otherwise leave as `[NEXT VERSION]`.

### Detect git range automatically

```bash
# Check if tags exist
git describe --tags --abbrev=0 2>/dev/null && \
  echo "Use: git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:'%H %s' --no-merges" || \
  echo "No tags found — use: git log HEAD~20..HEAD --pretty=format:'%H %s' --no-merges"
```

## Phase 2: Read the Git History

Run:
```bash
git log <range> --pretty=format:"%H %s" --no-merges
```

For each commit, also read the full diff summary:
```bash
git show --stat <SHA>
```

Group commits by type if using conventional commits (feat, fix, docs, chore, refactor, perf, test, build, ci). Otherwise, read the commit message and classify by likely intent.

## Phase 3: Classify and Draft

For each commit, decide:

**Affects users?** → Include in "Users" section
- New features, UI changes, behavior changes, bug fixes visible to users
- Write in plain English: "You can now do X" / "Fixed: X no longer happens"
- NEVER include: commit SHA, file names, function names, internal terminology

**Affects developers integrating or extending?** → Include in "Developers" section
- API changes, new hooks/events, SDK changes, breaking changes, new endpoints
- Can include technical terms, but explain impact: "Breaking: X now returns Y instead of Z"

**Affects deployment, configuration, or operations?** → Include in "Operators" section
- New environment variables, config changes, migration steps, infra changes
- Be specific: "New required env var: FEATURE_X_ENABLED (default: false)"

**Internal only?** → SKIP (refactors, test changes, CI changes, code style)

### Transformation examples

| Raw commit | Translated entry |
|---|---|
| `fix: resolve null pointer in UserService.processPayment` | Fixed a bug that caused payment processing to fail for some users. |
| `feat: add dark mode toggle to settings panel` | You can now switch to dark mode in Settings. |
| `perf: replace O(n²) sort in feed ranking` | Feeds with many items now load significantly faster. |
| `chore: upgrade postgres driver to 16.x` | (Operators) Updated database driver — no action required unless pinning the old version. |
| `feat: add /v2/webhooks endpoint with retry logic` | (Developers) New: `/v2/webhooks` endpoint with automatic retry on failure. See API docs. |
| `refactor: extract PaymentGateway interface` | SKIP — internal only. |

## Phase 4: Write the Entries

Rules for writing:
- **Users section**: Plain English. No jargon. Lead with the user benefit, not the implementation. Max 2 sentences per entry. Use "You can now...", "Fixed...", "Improved..."
- **Developers section**: Technical but clear. Always state the migration path for breaking changes.
- **Operators section**: Imperative and specific. "Set X to Y before deploying." "Run migration Z."
- **No filler**: Don't write "Various improvements and bug fixes" — if you can't describe it specifically, skip it.
- **Group related items**: Multiple commits fixing the same area → one entry.

## Phase 5: Format Output

### Keep a Changelog format (default)
```markdown
## [NEXT VERSION] - YYYY-MM-DD

### For Users

- **New:** [feature description]
- **Fixed:** [bug fix description]
- **Changed:** [behavior change and why]

### For Developers

- **Breaking:** [what changed, how to migrate]
- **New:** [new API/hook/event]

### For Operators

- **Action required:** [what to do before deploying]
- **New config:** [variable name and purpose]
```

### Blog post / email format

Omit the markdown headers. Write short prose paragraphs instead of bullet lists. Friendly tone, no technical filler.

### If the user wants to update CHANGELOG.md

1. Read the existing file.
2. Identify the position of the `# Changelog` header (or top of file).
3. Prepend the new section immediately after the header, before any existing entries.
4. Preserve all existing content verbatim.
5. Offer to write it back.

## Phase 6: Review Pass

Before presenting, check:
- Are all user-visible changes covered?
- Is there any internal jargon in the Users section?
- Are breaking changes clearly labeled?
- Would a non-technical user understand the Users section?

If any check fails, revise before presenting.

</process>

<anti_patterns>

## Anti-Patterns

| Don't | Do instead |
|---|---|
| Include commit SHAs or branch names in the Users section | Write about what the user experiences, not what the developer did |
| Write "Various improvements and bug fixes" | Name the specific fix or improvement, or skip it |
| Put refactors and test changes in any audience section | Internal changes have no changelog entry |
| Use function names, file names, or class names in the Users section | Translate to user experience: "payment processing" not "UserService.processPayment" |
| Write passive vague entries ("Performance has been improved") | Name the scenario: "Large dashboards now load in under 2 seconds" |
| Produce a Developers section entry without migration guidance for breaking changes | Always include "Before: X. After: Y. To migrate: Z." |
| Produce an Operators section entry without the exact variable name or command | Be specific: `REDIS_MAX_CONNECTIONS=50` not "configure Redis appropriately" |
| Cover 0 commits in a section when none qualify | Omit the section entirely if it has no entries |

</anti_patterns>

<success_criteria>

The changelog is complete when:
- [ ] Every user-visible change has an entry in plain English
- [ ] No commit SHAs, file names, or function names appear in the Users section
- [ ] Breaking changes are labeled and include a migration path
- [ ] Operator actions are imperative and specific
- [ ] Internal-only commits (refactors, CI, tests) are excluded
- [ ] Related commits are grouped, not listed individually
- [ ] The user has been offered to write/update CHANGELOG.md if applicable

</success_criteria>
