# PROMPT — Unify & clean a person's contacts (multi-source, review-UI, provenance-aware)

> Reusable prompt/plan. Runs on the local Mac (paste into Claude and let it evolve the UI live),
> or headless over SSH to a machine you control (`ssh <host>` → `sudo -u <user> -i`). Start from the
> bundled `scripts/contacts_cleanup.py` (stock-python web-UI merger) — reuse that code as the
> skeleton, don't start from scratch.

---

## Role & goal

You are cleaning up **the user's** contacts. They may have a *huge* number of contacts spread across
several sources, with lots of duplicates, inconsistent/messy names, and stale data. Produce **one
unified, deduplicated, trustworthy address book** — and, because a non-technical person will not
trust a silent auto-merge, give them a **dead-simple review UI** that shows the competing information
for each person (with provenance and edit dates) so they pick the winner and the rest gets demoted to
secondary fields or dropped if clearly outdated.

Core principle (learned the hard way): **duplicates and inconsistency make people stop maintaining
their contacts at all.** The win is a single source of truth they'll actually keep feeding.

## Hard safety rules (non-negotiable)

1. **Dry-run by default.** Nothing mutates unless invoked with `--live`. Print exactly what *would*
   change first.
2. **Back up before touching anything.** Copy the entire local AddressBook DB to `~/Desktop`
   (`Contacts-backup-<ts>/`), and export every source you read to timestamped `.vcf`/`.json`
   snapshots under a working dir.
3. **Every deletion is reversible.** Before deleting any card, export it to `deleted-contacts-<ts>.vcf`.
   Losing-value demotions keep the old value in a labelled secondary field, not oblivion.
4. **Never send anything.** No sync-back to any cloud account until the user explicitly approves a
   named target. Read-and-stage first. Sync is a separate, manually-triggered step with its own
   dry-run — never auto-enable iCloud/Google sync as part of apply.
5. **Auto-merge only the truly-identical.** If two+ cards carry the same normalized phone/email set,
   combine silently (no info lost). Everything else goes to human review.
6. **Only operate on data and machines the user owns or has explicit permission to access.**

## Sources to ingest (do as much retrieval as possible headlessly in bash)

Detect which exist on the machine; skip missing ones gracefully:

- **macOS Contacts** — read `~/Library/Application Support/AddressBook/Sources/*/AddressBook-v22.abcddb`
  (sqlite, read-only `mode=ro`) for rich fields + `ZCREATIONDATE`/`ZMODIFICATIONDATE`; use
  `osascript`/AppleScript for the live active-card list and for writes. (Proven in the bundled script.)
  Note: `ZCREATIONDATE`/`ZMODIFICATIONDATE` are Core Data epoch (seconds since 2001-01-01) — add
  `978307200` to get Unix time, don't treat them as Unix timestamps directly.
- **iCloud** — whichever AddressBook Source maps to the iCloud account (has its own abcddb).
- **Google accounts** (often several) — export via Google Contacts (People API or a
  Takeout/`.vcf`/Google CSV export). Capture *which account* each contact came from as provenance.
- **Any legacy Gmail / old accounts** — same treatment; tag source account.
- **VCF/CSV files** lying around (Desktop, Downloads) — ingest and tag as source.

For each contact record, preserve **provenance metadata**: source account, creation date,
modification date, field labels (home/work/cell/other), and — where derivable — recency-of-use.

## Matching & merge logic

- **Group** by normalized name first, then cross-link groups that share a normalized phone
  (last 10 digits) or email even under different names (catches "Milo" vs "Milo 😍").
- **Name-only cards** (businesses, placeholders with no phone/email) can't be matched on
  identifiers — group by normalized name only and always route them to `review`, never auto-merge.
- **Classify** each group: `identical` (auto-merge), `combine` (overlapping, safe union),
  `review` (disjoint info → possibly different people → default to *keep separate*).
- **Keeper** = card with the most complete info, tie-broken by most-recent modification.
- **Union** all phones/emails/addresses onto the keeper, de-duped by normalized value, preserving labels.

## The review UI (the part the user actually touches)

Self-contained, launched by double-click (`.command`) or `python3 contacts_unify.py`. **Stock macOS
python only — no pip installs.** Local `http.server`, opens the browser. Requirements:

- One card per duplicate **group**, sorted: safe combines first, genuine conflicts (`review`) next;
  identical ones already auto-merged and shown in a collapsed "did these for you" summary.
- For each **competing field value**, show: the value, its **label** (home/work/cell), **which
  source** it came from, and **how old** it is ("added 3mo ago", "edited yesterday"). This is what
  makes "Keep" vs "Delete" *mean something* — without dates/labels the choices are meaningless.
- Let the user **pick the winning value** per field; non-winners can be (a) kept as a secondary
  labelled field or (b) dropped if marked outdated. Default the freshest/most-complete as winner.
- Search/filter box (thousands of contacts — make it fast and keyboard-friendly).
- **Save** button records decisions to a JSON/CSV decision file; a separate **Apply** step performs
  the merges/deletes (still gated by `--live`), backs up, and writes the undo `.vcf`.
- Friendly for a non-technical person: no CSV editing, no jargon, obvious buttons, hard to break.

## Running modes

- **Headless / bash over SSH:** `ssh <host>` → `sudo -u <user> -i` → run the ingest+analysis
  passes, write the decision-ready JSON + a static review HTML the user can open. Retrieval and
  grouping are pure-bash/python; only the final apply needs their review + `--live`.
- **Interactive in Claude on the Mac:** paste this prompt; let Claude iterate the UI live with them.

## Deliverables

1. `contacts_unify.py` (evolved from the bundled cleaner) + `Unify My Contacts.command` launcher.
2. A working dir under `~/dev/agent-notes/me/contacts-merge/<person>/` (or any working folder) with
   all source snapshots, `contacts-data.json`, `contacts-decisions.(csv|json)`, and the review HTML.
3. A short `README.md` a friend could follow, and a one-paragraph summary of what was merged.

## Start by

Reading the bundled `scripts/contacts_cleanup.py` for the proven approach, then extend it to
multi-source + per-field winner selection + provenance. Confirm source inventory with a dry-run
before any `--live`.
