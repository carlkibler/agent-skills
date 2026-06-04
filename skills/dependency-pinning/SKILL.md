---
name: dependency-pinning
description: Dependency safety scan. Audit one or many projects/repos for SHA/digest pinning and release cooldowns across Docker, GitHub Actions, npm/pnpm/yarn/bun/deno, Python (uv/pdm/poetry/pip), .NET (NuGet), and Terraform. Report violations, then apply fixes and add cooldowns only with the user's OK. Triggers on "dependency pinning", "pin deps", "supply chain", "cooldown", "are my deps safe".
display_name: "Dependency Pinning"
brand_color: "#15803D"
group: "Dev Workflow"
usage: "/dependency-pinning"
summary: "Audit projects for SHA-pinning + release cooldowns; fix on approval"
default_prompt: "Scan this project (or the repos I point you at) for dependency pinning and release-cooldown hygiene across Docker, CI, JS, Python, and Terraform. Report first; propose exact fixes and ask before changing anything."
---

# Dependency Pinning

A dependency **safety** scan — not a CVE scan. It checks two things across every
ecosystem in scope:

1. **Pinning** — dependencies pinned to an immutable **content SHA / digest**, not a
   movable tag. Tags can be silently re-pointed to altered or malicious artifacts
   (the tj-actions class of supply-chain attacks). A digest can't.
2. **Cooldown** — a project never adopts an artifact newer than **N days** (default
   **7**). A fresh release is where a compromise lands first; the cooldown buys time
   for it to be caught before it reaches the build.

**Report first. Mutate only on explicit approval.** Bumping a pin is itself risky, so
every proposed change names the new SHA and flags it for a supply-chain check.

## Scope

Ask what to scan if unclear: a single project, a list of repos, or "everything under
`~/dev/work`". Then discover dependency manifests:

```bash
ROOT="${1:-.}"
/usr/bin/find "$ROOT" -type d \( -name node_modules -o -name .git -o -name .terraform \
    -o -name vendor -o -name packages -o -name bin -o -name obj -o -path '*/assets/libs' \) -prune -o \
  -type f \( \
    -iname 'Dockerfile*' -o -name 'docker-compose*.y*ml' -o -name 'compose*.y*ml' \
    -o -path '*/.github/workflows/*.y*ml' \
    -o -name 'package.json' -o -name 'deno.json*' \
    -o -name 'pyproject.toml' -o -name 'requirements*.txt' \
    -o -name '*.csproj' -o -name 'packages.config' -o -name 'Directory.Packages.props' \
    -o -name '*.tf' \
  \) -print 2>/dev/null
# Also catch images pulled from scripts/CI, not just Dockerfiles/compose:
grep -rEn 'docker (run|pull|build)[^|]*[a-z0-9./-]+:[a-z0-9._-]+' "$ROOT" \
  --include='*.sh' --include='*.y*ml' --include='Makefile' 2>/dev/null
```
Ignore vendored/minified asset trees (`*/assets/**`, `*.min.*`) — those `package.json`
files are bundled libraries, not your declared dependencies.

## What "good" looks like, how to detect violations, how to fix

### Docker / Compose  (pinning: required · cooldown: manual)
- **Good:** `FROM repo/img@sha256:<digest>`  ·  `image: repo/img@sha256:<digest>`
- **Bad:** `:latest`, floating tags, no digest.
- **Detect:** `grep -rEn '^\s*FROM |image:\s' <files>` → flag any ref without `@sha256:`.
  Also scan scripts/CI/Makefiles for `docker run|pull|build ... img:tag` — images
  pulled outside Dockerfiles/compose are easy to miss and just as swappable.
- **Fix:** resolve the digest of a tag that is **≥ N days old**:
  `docker buildx imagetools inspect repo/img:<ver> --format '{{.Manifest.Digest}}'`
  then write `repo/img@sha256:<digest>  # <ver>`.
- **Cooldown:** no native support — enforce by choosing a digest for an old-enough tag.

### GitHub Actions  (pinning: required · cooldown: via tooling)
- **Good:** `uses: owner/repo@<40-hex-sha>  # vX.Y.Z`
- **Bad:** `@v4`, `@main`, `@<branch>`.
- **Detect:** `grep -rEn 'uses:\s' .github/workflows` → flag any ref not matching a 40-char hex SHA.
- **Fix:** `git ls-remote https://github.com/<owner>/<repo> refs/tags/<ver>` → SHA; pin with the version in a trailing comment.
- **Cooldown / automation:** `ratchet` (sethvargo/ratchet) or `pinact` pin+update actions by SHA;
  Renovate/Dependabot `minimumReleaseAge` / cooldown gates the version that gets pinned.

### JavaScript — npm / yarn / pnpm / bun / deno  (pinning: lockfile · cooldown: tooling)
- **Good:** lockfile **committed** (`package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` /
  `bun.lock` / `deno.lock`) with integrity hashes, and CI installs frozen
  (`npm ci`, `pnpm i --frozen-lockfile`, `yarn --immutable`, `deno install --frozen`).
- **Bad:** no lockfile committed; relying on `^`/`~`/`latest` without a lock; `npm install` in CI.
- **Detect:** manifest present but lockfile missing/gitignored; CI using non-frozen installs.
- **Fix:** generate + commit the lockfile; switch CI to the frozen install command.
- **Cooldown:** **pnpm** has native `minimumReleaseAge` (config/`.npmrc`). For npm/yarn/bun,
  add **Renovate `minimumReleaseAge: "7 days"`** (or Dependabot cooldown). Deno: pin exact
  versions in import map / `deno.json`; `deno.lock` carries integrity.

### Python — uv / pdm / poetry / pip  (pinning: lockfile+hashes · cooldown: uv native / tooling)
- **Good:** lockfile committed with hashes (`uv.lock`, `pdm.lock`, `poetry.lock`) and
  installed locked (`uv sync --locked`, `pdm sync`, `poetry install`); for bare pip,
  hashed pins via `pip-compile --generate-hashes` + `pip install --require-hashes`.
- **Bad:** unpinned/`>=`/`*` requirements, no lockfile, no hashes.
- **Detect:** `pyproject.toml`/`requirements.txt` present but no lockfile/hashes; ranges without a lock.
- **Fix:** adopt a lock workflow or generate hashed requirements; commit the lock.
- **Cooldown:** **uv** has native `exclude-newer` / `UV_EXCLUDE_NEWER` (resolve as of a date —
  a true cooldown). Otherwise Renovate `minimumReleaseAge`.

### .NET — NuGet  (pinning: exact versions + lockfile · cooldown: tooling)
- **Good:** exact versions (`packages.config` `version="x.y.z"`, or `<PackageReference
  Version="x.y.z"/>` with no range/`*`) **plus a committed `packages.lock.json`**
  (enable `<RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>`, restore
  with `dotnet restore --locked-mode`). The lockfile carries `contentHash` per package.
- **Bad:** floating versions (`Version="*"`, `Version="[1.0,)"`), no lockfile, packages
  restored from a non-pinned feed.
- **Detect:** `grep -rEn 'Version="\*"|Version="\[' **/*.csproj`; `.csproj`/`packages.config`
  present but no `packages.lock.json` beside it; check `Directory.Packages.props` for
  central versions if used.
- **Fix:** pin exact versions; enable + commit `packages.lock.json`; pin the feed in
  `nuget.config`.
- **Cooldown:** no native NuGet cooldown — use **Renovate `minimumReleaseAge`** (NuGet supported).

### Terraform  (pinning: lock + version constraints)
- **Good:** `.terraform.lock.hcl` **committed** with **multi-platform** hashes
  (`terraform providers lock -platform=linux_amd64 -platform=darwin_arm64 ...`);
  providers pinned in `required_providers`; modules pinned by version or git commit SHA;
  AMIs/data sources pinned by ID (no `most_recent = true`).
- **Bad:** lock gitignored, missing platforms, `most_recent = true`, modules on `main`.
- **Detect:** lock in `.gitignore`; `grep -rn 'most_recent\s*=\s*true' *.tf`; module sources on a branch.
- **Fix:** un-ignore + commit the lock (multi-platform); pin module/AMI refs.

## Adding cooldowns where supported (offer these)
- **Renovate** (cross-ecosystem): `"minimumReleaseAge": "7 days"` in `renovate.json` — the
  single best lever; gates npm/pip/docker/actions/etc. behind the cooldown.
- **Dependabot**: `cooldown:` block in `.github/dependabot.yml`.
- **pnpm**: `minimumReleaseAge` · **uv**: `exclude-newer` · **GH Actions**: ratchet/pinact.

## Report format

```text
DEPENDENCY SAFETY REPORT  (cooldown target: 7 days)
===================================================
<repo/path>
  Docker        : 2 images unpinned (FROM node:20, postgres:16) — PIN MISSING
  GH Actions    : 3 actions on tags (@v4) — PIN MISSING
  JS (pnpm)     : lockfile committed ✓ · no cooldown — COOLDOWN MISSING
  Python (uv)   : uv.lock ✓ · exclude-newer not set — COOLDOWN MISSING
  Terraform     : .terraform.lock.hcl gitignored — LOCK NOT COMMITTED
  ...
SUMMARY: 4 pin gaps, 3 cooldown gaps, 1 uncommitted lock across N repos.
```

Classify each as: `OK` · `PIN MISSING` · `COOLDOWN MISSING` · `LOCK NOT COMMITTED`.
Then list **exact fixes** (the resolved SHA/digest, the config snippet) per item.

## Action rules
- Default to **read-only**. Do not edit files, run installers, or commit until the user approves.
- When approved, change **one ecosystem at a time**; show the diff.
- Every pin bump names the new SHA/digest and reminds the user to do a supply-chain
  check and respect the cooldown (no artifact newer than N days).
- Never weaken an existing pin. Never add a `:latest`/floating ref as a "fix".
- Keep the human-readable version in a trailing comment beside every SHA pin.
- Commit lockfiles — never gitignore them.
