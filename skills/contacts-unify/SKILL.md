---
name: contacts-unify
description: Consolidate/dedupe contacts from macOS, iCloud, Google, Zoho, or VCF with provenance-aware review, backups, and optional approved dossiers.
display_name: "Contacts Unify"
brand_color: "#22C55E"
local_only: true
group: "For Anyone"
usage: "Ask to fix/merge/clean up contacts, optionally naming whose (local Mac or an SSH host you control)."
summary: "Multi-source contact dedupe with a provenance-aware review UI, plus optional iMessage-driven dossier collection"
default_prompt: "Consolidate and dedupe my contacts across all sources into one address book, giving me a simple review UI that shows competing values with provenance and edit dates so I choose the winners. Back up first, dry-run before any change."
---

# Contacts Unify

Turn a messy, multi-source pile of contacts into **one deduplicated, trustworthy address
book** — with a review UI simple enough for a non-technical person to drive. Optionally, mine
iMessage history to find the people worth a deeper OSINT dossier.

**Why this matters:** duplicates and inconsistency make people stop maintaining their contacts at
all. The win is a single source of truth they'll actually keep feeding.

**Scope of `local_only`:** Phase A (dedupe) is fully local — no network egress. Phase B is opt-in
and its dossier step (`research-person`) *does* reach the public web (LinkedIn, gov/org sites). Treat
Phase B network access as a deliberate, separately-approved step, never an automatic follow-on.

**Consent & authorization (read before running):** only operate on contacts/messages belonging to
the user, on a machine they own or have explicit permission to access (including any SSH host). Phase
B researches *other people* from the user's private data — only build a dossier on someone the user
**names explicitly**. Never infer a research shortlist from message volume and run it unattended, and
don't dossier minors or obviously sensitive relationships.

## When to use

- "Fix / clean up / merge my contacts", duplicate cards, contacts scattered across accounts.
- Consolidating iCloud + several Google accounts + Zoho + stray VCF/CSV exports.
- "Who do I talk to most?" → rank message contacts, then research the important ones.

## Two phases (run either or both)

### Phase A — Unify & dedupe (the core)

Full plan: **`references/unify-plan.md`** (read it before building). Summary of the workflow:

1. **Confirm the target + sources.** Whose contacts? On the local Mac, or over SSH to another box
   (e.g. `ssh <host>` → `sudo -u <user> -i`)? Inventory which sources exist:
   - macOS Contacts / iCloud — sqlite `~/Library/Application Support/AddressBook/Sources/*/AddressBook-v22.abcddb`
     (read `mode=ro` for rich fields + `ZCREATIONDATE`/`ZMODIFICATIONDATE`); `osascript` for the live
     list and for writes.
   - Google accounts (often several) — Google Contacts export / People API / Takeout `.vcf`/CSV.
   - Zoho, legacy Gmail, and any loose `.vcf`/`.csv` on Desktop/Downloads.
   - **Tag every contact with its source account** as provenance.
2. **Back up first, always.** Whole AddressBook DB → `~/Desktop/Contacts-backup-<ts>/`; every source
   → timestamped snapshot in the working dir. This is non-negotiable.
3. **Group & classify.** Group by normalized name; cross-link groups sharing a normalized phone
   (last 10 digits) or email even under different names. Classify each: `identical` (auto-merge),
   `combine` (safe union), `review` (disjoint → maybe different people → default keep-separate).
   Name-only cards (businesses, placeholders with no phone/email) can't be matched on identifiers —
   group them by normalized name only and always route them to `review`, never silent auto-merge.
4. **Review UI.** Launch the self-contained web page (stock macOS python, `http.server`, no pip).
   Each duplicate group shows every **competing field value** with its **label** (home/work/cell),
   **source account**, and **age** ("edited yesterday", "added 3mo ago"). The user picks the winning
   value per field; losers become secondary labelled fields or are dropped if marked outdated.
   Search/filter for large books. **Save** records decisions; **Apply** performs merges/deletes.
   *Without dates + labels, "Keep/Delete" is meaningless — dates and labels are mandatory.*
5. **Apply — dry-run by default.** Nothing mutates without `--live`. Before any delete, export the
   removed cards to `deleted-contacts-<ts>.vcf` (drag-to-restore undo). Auto-merge only truly
   identical cards (same normalized phone/email set — no info lost).
6. **Never sync back** to any cloud account until the user names an explicit target and approves.

**Starter code:** `scripts/contacts_cleanup.py` is the proven single-source (macOS) merger with the
full web review UI, backup, undo, and classification already working. Read it, then extend it to
multi-source ingest + per-field winner selection. Do not rebuild from scratch.

### Phase B — iMessage mining → dossiers (optional deep dive)

Full plan: **`references/imessage-dossier-plan.md`**.

1. **Ask the user who's worth a deep dive.** Before mining, offer to focus: high-value people,
   specific groups, or traits (e.g. "Utah legislators", "arts-org board members", "clients",
   "family"). Let them steer the shortlist — don't research everyone. The ranking *informs* the
   conversation; it does not authorize research. A dossier runs only for a person the user names.
2. **Mine the message graph (read-only).** Run `scripts/imessage_signal.py` — it copies `chat.db`
   to a temp file, opens it read-only, and ranks handles by volume and recency (plus a 1:1-vs-group
   signal). It reads counts and timestamps only; **message content never leaves the machine**.
   *Reciprocity is an unreliable column* — chat.db nulls the sender on the user's own messages, so
   rank on volume + recency, not reciprocity. Output: ranked `people-signal.csv/json` + gap lists
   ("high-frequency but not in contacts" / "in contacts but never messaged"). Full Disk Access
   required for the running user.
3. **Resolve identities** against the unified address book from Phase A (collapse phone+email splits).
4. **Fan out dossiers.** For the approved shortlist, invoke the **`research-person`** skill to build
   confidence-marked Obsidian `People/` notes, enriched from public sources appropriate to the
   person's world — LinkedIn, and (Utah-centric example) the state legislature site (le.utah.gov),
   arts-group/nonprofit sites, and the lobbyist registry (disclosures.utah.gov). Private message
   content stays internal context, never published.

## Safety rules (both phases)

- Dry-run by default; `--live` only after the user sees what would change.
- Back up before any mutation; every delete is reversible via exported `.vcf`.
- Read-only on `chat.db` (work on a copy); never write the live Messages or Contacts DB directly
  except through the reviewed, `--live`-gated apply step.
- No outbound sync and no message content in any shared vault without explicit approval.

## Deliverables

- Working dir (e.g. `~/dev/agent-notes/me/contacts-merge/<person>/`) with source snapshots,
  `contacts-data.json`, `contacts-decisions.(csv|json)`, and the review HTML.
- `Unify My Contacts.command` launcher + a friend-readable `README.md`.
- (Phase B) `people-signal.(csv|json)` + `research-person` dossiers for the approved shortlist.
