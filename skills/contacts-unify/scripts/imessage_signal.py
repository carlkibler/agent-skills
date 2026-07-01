#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""imessage_signal.py — rank the people you actually talk to.

Read-only miner over macOS Messages (~/Library/Messages/chat.db). Copies the DB
to a temp file and opens it read-only, so it NEVER touches your live Messages.
Full Disk Access is required for whatever user runs this.

Output: a ranked CSV/JSON of handles with volume, recency, and 1:1-vs-group
signals — the shortlist worth turning into research-person dossiers.

Message *content* never leaves the machine: this reads counts and timestamps only,
not text bodies.

KNOWN LIMITATION — reciprocity is weak. chat.db attaches sent messages
(is_from_me=1) to a null handle, so per-handle "sent" reads ~0 and reciprocity
collapses toward 0 for almost everyone. Rank on volume + recency; treat the
reciprocity column as advisory until identities are resolved against the address
book (the Phase A -> B handoff). Do not present reciprocity as reliable.

Usage:
  python3 imessage_signal.py                 # table to stdout, top 40
  python3 imessage_signal.py --json out.json --csv out.csv --top 100
"""
import argparse, json, os, shutil, sqlite3, sys, tempfile, datetime

APPLE_EPOCH = 978307200  # 2001-01-01 -> unix
DB = os.path.expanduser("~/Library/Messages/chat.db")


def apple_to_unix(ts):
    if ts is None:
        return None
    # modern chat.db stores nanoseconds; older stores seconds
    if ts > 1e12:
        ts = ts / 1e9
    return ts + APPLE_EPOCH


def ago(unix_ts):
    if not unix_ts:
        return ""
    days = (datetime.datetime.now() - datetime.datetime.fromtimestamp(unix_ts)).days
    if days <= 0:
        return "today"
    if days < 30:
        return f"{days}d"
    if days < 365:
        return f"{days // 30}mo"
    return f"{days // 365}yr"


def mine(db_path):
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    # per-handle: totals, sent/received, first/last, distinct-day count, group involvement
    rows = con.execute(
        """
        SELECT h.id AS handle,
               COUNT(*)                                              AS total,
               SUM(CASE WHEN m.is_from_me=1 THEN 1 ELSE 0 END)       AS sent,
               SUM(CASE WHEN m.is_from_me=0 THEN 1 ELSE 0 END)       AS received,
               MIN(m.date)                                           AS first_date,
               MAX(m.date)                                           AS last_date,
               SUM(CASE WHEN cmj.chat_id IN (
                     SELECT chat_id FROM chat_handle_join
                     GROUP BY chat_id HAVING COUNT(*) > 1) THEN 1 ELSE 0 END) AS group_msgs
        FROM message m
        JOIN handle h                ON m.handle_id = h.ROWID
        LEFT JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
        WHERE h.id IS NOT NULL
        GROUP BY h.id
        """
    ).fetchall()
    con.close()

    people = []
    for r in rows:
        last = apple_to_unix(r["last_date"])
        total = r["total"] or 0
        sent = r["sent"] or 0
        received = r["received"] or 0
        group_msgs = r["group_msgs"] or 0
        one_to_one = total - group_msgs
        # reciprocity: 1.0 = perfectly balanced, ->0 = one-way
        recip = round(min(sent, received) / max(sent, received), 2) if sent and received else 0.0
        # simple score: volume, weighted by recency and reciprocity, favoring 1:1
        recency_boost = 2.0 if (last and (datetime.datetime.now().timestamp() - last) < 90 * 86400) else 1.0
        score = round((one_to_one + 0.3 * group_msgs) * (0.5 + recip) * recency_boost, 1)
        people.append({
            "handle": r["handle"],
            "score": score,
            "total": total,
            "sent": sent,
            "received": received,
            "reciprocity": recip,
            "one_to_one": one_to_one,
            "group_msgs": group_msgs,
            "last": ago(last),
            "active_90d": recency_boost > 1.0,
        })
    people.sort(key=lambda p: p["score"], reverse=True)
    return people


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DB)
    ap.add_argument("--json")
    ap.add_argument("--csv")
    ap.add_argument("--top", type=int, default=40)
    args = ap.parse_args()

    if not os.path.exists(args.db):
        sys.exit(f"No Messages DB at {args.db} (need Full Disk Access for this user).")

    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name
    try:
        shutil.copy2(args.db, tmp)
        for side in ("-wal", "-shm"):
            if os.path.exists(args.db + side):
                shutil.copy2(args.db + side, tmp + side)
        people = mine(tmp)
    finally:
        for f in (tmp, tmp + "-wal", tmp + "-shm"):
            if os.path.exists(f):
                os.remove(f)

    if args.json:
        json.dump(people, open(args.json, "w"), indent=2)
        print(f"wrote {args.json} ({len(people)} handles)")
    if args.csv:
        import csv
        if not people:
            print("no messages found — nothing to write to CSV")
        else:
            with open(args.csv, "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(people[0].keys()))
                w.writeheader()
                w.writerows(people)
            print(f"wrote {args.csv}")

    print(f"\nTop {args.top} people by talk-signal:\n")
    print(f"{'score':>7}  {'total':>6}  {'recip':>5}  {'last':>5}  handle")
    for p in people[: args.top]:
        print(f"{p['score']:>7}  {p['total']:>6}  {p['reciprocity']:>5}  {p['last']:>5}  {p['handle']}")
    print("\nNote: 'recip' reads ~0 for most handles (chat.db nulls the sender on "
          "your own messages). Rank on score/total/last; reciprocity is advisory.")


if __name__ == "__main__":
    main()
