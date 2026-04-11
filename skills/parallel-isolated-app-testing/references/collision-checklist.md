# Collision Checklist for Parallel App Testing

Use this checklist before running multiple app instances in parallel.

## State and Storage

Check whether instances share:
- `UserDefaults` / preferences domains
- config files
- app-support directories
- caches
- temp directories
- SQLite databases
- lock files
- logs
- export bundles
- key stores / credential files

Questions:
- Can each instance point at a separate root?
- Are state paths derived from bundle ID or hardcoded names?
- Are there any assumptions that only one writer exists?

## Inputs and Watchers

Check whether instances share:
- screenshot folders
- watched folders
- inbox / outbox dirs
- test fixtures
- file debouncers / recent-file guards

Questions:
- Can each instance watch a unique folder?
- Can two instances process similarly named files without collision?
- Does one watcher see files intended for another lane?

## OS Integrations

Check whether instances interact with:
- login items
- launch agents / daemons
- notification center
- system extensions
- auto-updaters
- accessibility APIs
- camera/mic/screen recording permissions
- menu bar state

Questions:
- Should these be suppressed in test mode?
- Are prompts or registrations machine-global instead of instance-local?

## App Lifecycle and Singletons

Check for:
- duplicate-instance guards
- app-wide singletons with mutable global state
- hardcoded IPC channels
- sockets / ports / named pipes
- global dispatch queues that assume one process

Questions:
- Can multiple processes run at once?
- Does the app activate/focus or quit other instances?
- Does one instance steal state or UI from another?

## First-Run and Fixtures

Check for:
- onboarding gates
- setup-required windows
- auth-required startup blockers
- migration prompts
- extra-discovery prompts
- startup scans

Questions:
- Can a fixture profile skip this cleanly?
- What is the minimum seeded state for a useful smoke lane?

## External Dependencies

Check whether the app depends on:
- live APIs
- local model servers
- cloud credentials
- OS-specific secrets or accounts

Questions:
- Is a fake-provider or stub mode needed?
- Can tests fail for dependency reasons unrelated to the app itself?

## Evidence to Collect

Before declaring the setup parallel-safe, collect proof for:
- concurrent PIDs
- separate roots on disk
- separate DB rows/log files per instance
- distinct watched inputs
- no cross-talk in outputs
- clean targeted teardown
