# PROMPT — Mine iMessage history → rank key people → build dossiers

> Optional Phase B, separate from the contacts-unify core. Runs on the local Mac or headless over
> SSH to a machine you control (`ssh <host>` → `sudo -u <user> -i`). Read-only mining first; dossier
> build second. The dossier step uses the `research-person` skill.

---

## Consent first

This phase researches *other people* from the user's private message data. Only build a dossier on
someone the user **names explicitly**. The ranking below *informs the conversation* — it does not
authorize research. Never infer a shortlist from message volume and run it unattended. Do not
dossier minors or obviously sensitive relationships.

## Phase 1 — Mine the message graph (read-only, privacy-careful)

Source: `~/Library/Messages/chat.db` (SQLite). **Read-only** (`mode=ro`), copy to a working file
first — never write to the live DB. Full Disk Access may be required for the running user.

For each handle/contact, compute:

- **Volume**: total messages exchanged, sent vs received. NOTE: chat.db attaches the user's own
  sent messages to a null handle, so per-handle `sent`/`reciprocity` is unreliable until identities
  are resolved against the address book — rank on volume + recency, treat reciprocity as advisory.
- **Recency**: last message date; active-in-last-90d flag.
- **Cadence**: distinct days with contact, longest streak, trailing-90d trend (rising/fading).
  (Compute distinct days by bucketing to calendar day — not `DISTINCT` on the raw nanosecond ts.)
- **Intimacy signals**: 1:1 vs group-only, avg message length, reactions.
- **Identity resolution**: join handles → the unified contacts book (from the contacts-unify work)
  so a person split across phone+email collapses to one row.

Output a ranked `people-signal.csv/json`: top talked-with people with the metrics above, so the user
can pick who's worth a dossier. Flag anyone high-frequency but **not in contacts** (worth adding) and
anyone in contacts but **never messaged** (dead weight). The bundled `scripts/imessage_signal.py`
does this ranking.

## Phase 2 — Dossier collection for the named people

For each person the user selects, kick off a **`research-person`** dossier (→ Obsidian `People/`
note, confidence-marked, cross-linked). Feed it:

- What we know from messages (name variants, numbers, emails, context clues — kept private, not
  published).
- **Public sources** to enrich, chosen for the person's world. Examples:
  - LinkedIn and general web / news / org "about" pages.
  - For public-official or civic figures: state legislature sites, committee/bill records, and
    lobbyist/disclosure registries (e.g. a state's `le.<state>.gov` and disclosures portal).
  - For arts/nonprofit figures: org websites (boards, staff, event rosters).

Each dossier: who they are, role/affiliations, how the user knows them (from message context), best
contact info (reconciled with the unified book), and confidence per claim. Keep private message
content **out** of published notes — cite it only as internal context.

## Safety

- Read-only on `chat.db`; work on a copy.
- Dry-run the ranking before any dossier fan-out; let the user approve the named list.
- Nothing about message *content* leaves the machine or lands in a shared vault.
- Rate-limit / be gentle on public sources; dossiers are research, not scraping campaigns.

## Deliverables

1. `imessage_signal.py` → `people-signal.(csv|json)` ranked list + the two "worth adding / dead
   weight" gap lists.
2. Approved-list → `research-person` dossiers in the vault's `People/` folder.
3. Short summary: top people, who's missing from contacts, who to research first.
