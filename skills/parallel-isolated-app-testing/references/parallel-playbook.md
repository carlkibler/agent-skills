# Parallel Isolated App Testing Playbook

## Recommended Order

1. Build or verify the app.
2. Launch one isolated instance in dry-run mode and inspect the resolved command.
3. Launch one real isolated instance and verify state-root creation.
4. Launch a second isolated instance and verify concurrent processes.
5. Prove no cross-talk with separate inputs and separate history/log artifacts.
6. Add fixture profiles to reach useful states.
7. Split smoke work into named lanes.
8. Run deeper scenario checks only after the isolation proof is solid.

## Lane Design Heuristics

Prefer scenario lanes that do not need the same mutation targets.

Examples:
- Lane A: feedback / diagnostics export
- Lane B: preferences / history / help
- Lane C: onboarding / permission denial recovery
- Lane D: watcher / queue / happy-path rename with fake provider

Avoid combining too much into one lane. Short, attributable lanes are easier to trust.

## Fixture Hierarchy

Start with:
- `smoke-ready`

Then add as needed:
- `history-seeded`
- `misconfigured-auth`
- `paused`
- `fake-provider`
- `diagnostics-heavy`

Each fixture should be:
- named clearly
- narrow in purpose
- documented in terms of seeded defaults/files/state
- reproducible from scratch

## Artifact Discipline

For each lane, keep:
- isolated log file
- isolated state root
- isolated input fixtures
- a short run note with commands and findings

If screenshots or UI dumps are possible, store them under the lane’s root.

## Common Failure Meanings

### Both instances fail the same way immediately
Possible meanings:
- shared dependency outage
- bad build
- broken fixture seeding
- test mode suppressing too much

### Only one lane fails
Possible meanings:
- lane-specific fixture issue
- path-specific permissions
- real product bug in that scenario

### Both lanes see each other’s files or history
Meaning:
- isolation is not working
- stop and fix the collision before further QA

### App never gets past onboarding
Meaning:
- fixture mode is missing or insufficient
- the testing system is not ready for productive parallel smoke yet

## What to Write Down Every Time

At minimum record:
- binary used
- helper script command
- instance ID
- state root
- fixture profile
- observed window/state
- key log lines
- result
- blocker or follow-up
