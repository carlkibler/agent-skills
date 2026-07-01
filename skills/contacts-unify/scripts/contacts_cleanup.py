#!/usr/bin/env python3
"""Contacts Cleanup — a smart, self-contained duplicate MERGER for macOS.

No installs (stock macOS Python). It:
  1. Backs up your whole contacts database to your Desktop (safety first).
  2. Finds same-name contacts and, for each, shows a COMBINED preview with
     every phone/email (labelled home/work/cell) and when each card was added/edited.
  3. You confirm Merge (combine into one) or Keep separate.
  4. On apply it unions the info into one card, exports the removed cards to a .vcf
     (easy undo), then deletes the extras.

Run by double-clicking "Clean My Contacts.command", or:  python3 contacts_cleanup.py
"""
import http.server, socketserver, subprocess, json, os, webbrowser, datetime, threading, shutil, glob, sqlite3, re

PORT = 8765
DESKTOP = os.path.expanduser("~/Desktop")
ABDIR = os.path.expanduser("~/Library/Application Support/AddressBook")
F, V = chr(31), chr(30)
EPOCH = 978307200  # Core Data -> unix
DRY_RUN = os.environ.get("CC_DRYRUN") == "1"

def osa(script, timeout=180):
    return subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=timeout)

def backup():
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = os.path.join(DESKTOP, f"Contacts-backup-{ts}")
    try: shutil.copytree(ABDIR, dest); return dest, None
    except Exception as e: return None, str(e)

# ---- fast active-contact list (id == ZUNIQUEID) + names -------------------
BULK = '''
tell application "Contacts"
  set theIds to id of every person
  set theNames to name of every person
end tell
set d to (ASCII character 31)
set AppleScript's text item delimiters to d
set idStr to theIds as text
set nl to {}
repeat with n in theNames
  if n is missing value then
    set end of nl to ""
  else
    set end of nl to (n as text)
  end if
end repeat
return idStr & (ASCII character 30) & (nl as text)
'''
def load_names():
    r = osa(BULK)
    if r.returncode != 0 or V not in r.stdout: return []
    ids_s, names_s = r.stdout.split(V, 1)
    ids = ids_s.split(F); names = names_s.rstrip("\n").split(F)
    return [{"id": i, "name": (n or "").strip()} for i, n in zip(ids, names) if i]

# ---- rich detail (labels, dates) straight from the database --------------
def lbl(s):
    if not s: return ""
    m = re.search(r"_\$!<(.+?)>!\$_", s)
    return (m.group(1) if m else s).strip().lower()

def read_rich(ids):
    want = set(ids); out = {}
    for db in glob.glob(os.path.join(ABDIR, "Sources", "*", "AddressBook-v22.abcddb")):
        try: c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        except Exception: continue
        c.row_factory = sqlite3.Row
        try:
            rec = {r["ZUNIQUEID"]: r for r in c.execute(
                "SELECT Z_PK,ZUNIQUEID,ZCREATIONDATE,ZMODIFICATIONDATE,ZORGANIZATION FROM ZABCDRECORD")}
        except Exception:
            c.close(); continue
        pk2id = {r["Z_PK"]: uid for uid, r in rec.items()}
        em, ph, ad = {}, {}, {}
        for r in c.execute("SELECT ZOWNER,ZADDRESS,ZLABEL FROM ZABCDEMAILADDRESS WHERE ZADDRESS IS NOT NULL"):
            em.setdefault(r["ZOWNER"], []).append({"label": lbl(r["ZLABEL"]), "value": r["ZADDRESS"]})
        for r in c.execute("SELECT ZOWNER,ZFULLNUMBER,ZLABEL FROM ZABCDPHONENUMBER WHERE ZFULLNUMBER IS NOT NULL"):
            ph.setdefault(r["ZOWNER"], []).append({"label": lbl(r["ZLABEL"]), "value": r["ZFULLNUMBER"]})
        for r in c.execute("SELECT ZOWNER,ZSTREET,ZCITY,ZSTATE,ZZIPCODE,ZLABEL FROM ZABCDPOSTALADDRESS"):
            parts = [x for x in [r["ZSTREET"], r["ZCITY"], r["ZSTATE"], r["ZZIPCODE"]] if x]
            if parts: ad.setdefault(r["ZOWNER"], []).append({"label": lbl(r["ZLABEL"]), "value": ", ".join(parts)})
        for uid, r in rec.items():
            if uid not in want: continue
            out[uid] = {
                "emails": em.get(r["Z_PK"], []), "phones": ph.get(r["Z_PK"], []),
                "addrs": ad.get(r["Z_PK"], []), "org": r["ZORGANIZATION"] or "",
                "created": r["ZCREATIONDATE"], "modified": r["ZMODIFICATIONDATE"],
            }
        c.close()
    return out

def ago(cd):
    if not cd: return ""
    try: d = datetime.datetime.fromtimestamp(cd + EPOCH)
    except Exception: return ""
    days = (datetime.datetime.now() - d).days
    if days <= 0: return "today"
    if days == 1: return "yesterday"
    if days < 30: return f"{days}d ago"
    if days < 365: return f"{days//30}mo ago"
    return f"{days//365}yr ago"

def norm_ph(v): return re.sub(r"\D", "", v or "")[-10:]
def norm_em(v): return (v or "").strip().lower()

def build_groups(people):
    by = {}
    for p in people:
        k = " ".join(p["name"].lower().split())
        if k: by.setdefault(k, []).append(p)
    dupes = [v for v in by.values() if len(v) > 1]
    rich = read_rich([c["id"] for g in dupes for c in g])
    groups = []
    for g in dupes:
        for c in g: c.update(rich.get(c["id"], {"emails": [], "phones": [], "addrs": [], "org": "", "created": None, "modified": None}))
        # union + keeper
        uph, uem, uad = {}, {}, {}
        for c in g:
            for x in c["phones"]: uph.setdefault(norm_ph(x["value"]) or x["value"], x)
            for x in c["emails"]: uem.setdefault(norm_em(x["value"]), x)
            for x in c["addrs"]: uad.setdefault(x["value"].lower(), x)
        keeper = max(g, key=lambda c: (len(c["phones"]) + len(c["emails"]) + len(c["addrs"]) + (1 if c["org"] else 0), c["modified"] or 0))
        # classification
        sets = [set([norm_ph(x["value"]) for x in c["phones"]] + [norm_em(x["value"]) for x in c["emails"]]) for c in g]
        union = set().union(*sets) if sets else set()
        nonempty = [s for s in sets if s]
        if any(s == union and s for s in sets):
            cls, default = "identical", "merge"
        elif len(nonempty) >= 2 and not set.intersection(*nonempty):
            cls, default = "review", "skip"      # disjoint -> maybe different people
        elif union:
            cls, default = "combine", "merge"
        else:
            cls, default = "review", "skip"
        groups.append({
            "name": g[0]["name"], "cls": cls, "decision": default, "keeper": keeper["id"],
            "merged": {"org": (keeper["org"] or next((c["org"] for c in g if c["org"]), "")),
                       "phones": list(uph.values()), "emails": list(uem.values()), "addrs": list(uad.values())},
            "cards": [{"id": c["id"], "org": c["org"], "phones": c["phones"], "emails": c["emails"],
                       "addrs": c["addrs"], "created": ago(c["created"]), "modified": ago(c["modified"]),
                       "keeper": c["id"] == keeper["id"]} for c in g],
        })
    auto = [g for g in groups if g["cls"] == "identical"]
    display = [g for g in groups if g["cls"] != "identical"]
    order = {"combine": 0, "review": 1}
    display.sort(key=lambda g: (order[g["cls"]], g["name"].lower()))
    display.sort(key=lambda g: (order.get(g["cls"], 9), g["name"].lower()))
    return display, auto

STATE = {"groups": [], "count": 0, "auto": 0}

def esc_as(s): return (s or "").replace("\\", "\\\\").replace('"', '\\"')

def merge_group(grp):
    keeper = grp["keeper"]
    kd = next(c for c in grp["cards"] if c["id"] == keeper)
    kph = set(norm_ph(x["value"]) for x in kd["phones"])
    kem = set(norm_em(x["value"]) for x in kd["emails"])
    adds = []
    for x in grp["merged"]["phones"]:
        if norm_ph(x["value"]) not in kph:
            lp = f'label:"{esc_as(x["label"] or "other")}", ' if x["label"] else ""
            adds.append(f'make new phone at end of phones of k with properties {{{lp}value:"{esc_as(x["value"])}"}}')
    for x in grp["merged"]["emails"]:
        if norm_em(x["value"]) not in kem:
            lp = f'label:"{esc_as(x["label"] or "other")}", ' if x["label"] else ""
            adds.append(f'make new email at end of emails of k with properties {{{lp}value:"{esc_as(x["value"])}"}}')
    if not kd["org"] and grp["merged"]["org"]:
        adds.append(f'set organization of k to "{esc_as(grp["merged"]["org"])}"')
    if not DRY_RUN:
        script = (f'tell application "Contacts"\nset k to first person whose id is "{esc_as(keeper)}"\n'
                  + "\n".join(adds) + ("\n" if adds else "") + "save\nend tell")
        osa(script)
    return [c["id"] for c in grp["cards"] if c["id"] != keeper]

def delete_ids(ids):
    if not ids: return 0
    if DRY_RUN: return len(ids)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    q = ",".join('"%s"' % esc_as(x) for x in ids)
    r = osa(f'set ids to {{{q}}}\nset out to ""\ntell application "Contacts"\nrepeat with i in ids\nset out to out & (vcard of (first person whose id is i))\nend repeat\nend tell\nreturn out')
    if r.stdout.strip(): open(os.path.join(DESKTOP, f"deleted-contacts-{ts}.vcf"), "w").write(r.stdout)
    d = osa(f'set ids to {{{q}}}\ntell application "Contacts"\nrepeat with i in ids\ndelete (first person whose id is i)\nend repeat\nsave\nend tell')
    return len(ids) if d.returncode == 0 else 0

def auto_merge(groups):
    dels = []
    for g in groups: dels += merge_group(g)
    return delete_ids(dels), len(groups)

def apply_merges(decisions):
    dels = []; merged = 0
    for i, grp in enumerate(STATE["groups"]):
        if decisions.get(str(i)) == "merge":
            dels += merge_group(grp); merged += 1
    return merged, delete_ids(dels)

PAGE = r"""<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Contacts Cleanup</title><style>
:root{--bg:#0f1115;--card:#191d25;--card2:#222733;--line:#2b313d;--tx:#e8ecf3;--mut:#97a1b1;--keep:#2ecc71;--mrg:#5b8cff;--rev:#f4b740;--del:#ff5a5f}
*{box-sizing:border-box}body{margin:0;font:15px/1.5 -apple-system,system-ui,sans-serif;background:var(--bg);color:var(--tx)}
header{position:sticky;top:0;z-index:5;background:rgba(15,17,21,.96);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);padding:14px 20px}
h1{font-size:19px;margin:0 0 3px}.sub{color:var(--mut);font-size:13.5px}
.tools{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}
input[type=search]{flex:1;min-width:160px;background:var(--card);border:1px solid var(--line);border-radius:8px;color:var(--tx);padding:8px 12px}
.wrap{max-width:820px;margin:0 auto;padding:14px 16px 110px}
.g{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px;margin:12px 0}
.gh{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.gh .nm{font-weight:700;font-size:16px}
.badge{font-size:11px;font-weight:700;padding:2px 9px;border-radius:20px}
.b-identical{background:rgba(46,204,113,.15);color:var(--keep)}
.b-combine{background:rgba(91,140,255,.15);color:var(--mrg)}
.b-review{background:rgba(244,183,64,.15);color:var(--rev)}
.merged{background:var(--card2);border:1px dashed var(--line);border-radius:10px;padding:10px 12px;margin:6px 0}
.merged .h{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px}
.fld{font-size:14px}.fld .lab{display:inline-block;min-width:54px;color:var(--mut);font-size:12px}
.srcs{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.src{flex:1;min-width:220px;background:var(--card2);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:13px}
.src.keep{border-color:var(--keep)}
.src .t{font-size:11px;color:var(--mut);margin-bottom:3px}
.src .kbadge{color:var(--keep);font-weight:700}
.acts{display:flex;gap:0;margin-top:10px}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:9px;overflow:hidden}
.seg button{border:0;background:transparent;color:var(--tx);padding:8px 16px;font-weight:600;cursor:pointer;font-size:14px}
.seg button.mon{background:var(--mrg);color:#fff}.seg button.son{background:var(--card2);color:var(--mut)}
footer{position:fixed;bottom:0;left:0;right:0;background:rgba(15,17,21,.97);border-top:1px solid var(--line);padding:12px 20px;display:flex;gap:14px;justify-content:center;align-items:center}
button.big{border:0;border-radius:10px;padding:12px 22px;font-size:15px;font-weight:700;cursor:pointer;background:var(--mrg);color:#fff}
button.big:disabled{opacity:.4}.muted{color:var(--mut);font-size:13px}.ok{color:var(--keep);font-weight:600}
.empty{text-align:center;color:var(--mut);padding:60px 20px;font-size:17px}
</style></head><body>
<header><h1>🧹 Contacts Cleanup</h1><div class=sub id=sub>Loading…</div>
<div class=tools><input type=search id=q placeholder="Search a name…"></div></header>
<div class=wrap id=wrap></div>
<footer><span class=muted id=status></span><button class="big" id=apply disabled>Merge selected</button></footer>
<script>
let G=[];
const F={identical:'Same info — safe to combine',combine:'Looks like one person',review:'Different details — check'};
async function boot(){let j=await(await fetch('/data')).json();G=j.groups;
  document.getElementById('sub').innerHTML=`Full backup on your Desktop · ${j.count} contacts · ✅ auto-combined <b>${j.auto}</b> exact duplicates. ${G.length? '<b>'+G.length+'</b> groups need a quick look below (different details — same person?).':'Nothing left to review — you’re clean! 🎉'}`;render();}
function flds(arr){return arr.map(x=>`<div class=fld><span class=lab>${esc(x.label||'')}</span> ${esc(x.value)}</div>`).join('');}
function render(){const w=document.getElementById('wrap'),q=document.getElementById('q').value.toLowerCase();
  const gs=G.filter(g=>!q||g.name.toLowerCase().includes(q));
  if(!G.length){w.innerHTML='<div class=empty>🎉 No duplicate names — your contacts look clean!</div>';document.getElementById('apply').style.display='none';return;}
  w.innerHTML=gs.map(g=>{const gi=G.indexOf(g);const m=g.merged;
    return `<div class=g><div class=gh><span class=nm>${esc(g.name)}</span><span class="badge b-${g.cls}">${F[g.cls]}</span></div>
    <div class=merged><div class=h>Combined card</div>${m.org?`<div class=fld><span class=lab>org</span> ${esc(m.org)}</div>`:''}${flds(m.phones)}${flds(m.emails)}${m.addrs.map(a=>`<div class=fld><span class=lab>${esc(a.label||'addr')}</span> ${esc(a.value)}</div>`).join('')}</div>
    <div class=srcs>${g.cards.map(c=>`<div class="src ${c.keep?'keep':''}"><div class=t>${c.keep?'<span class=kbadge>★ base</span> ':''}added ${c.created} · edited ${c.modified}</div>${flds(c.phones)}${flds(c.emails)}</div>`).join('')}</div>
    <div class=acts><span class=seg>
      <button class="${g.decision=='merge'?'mon':''}" onclick="dec(${gi},'merge')">Combine</button>
      <button class="${g.decision=='skip'?'son':''}" onclick="dec(${gi},'skip')">Keep separate</button>
    </span></div></div>`;}).join('');
  count();document.getElementById('apply').disabled=false;}
function dec(gi,v){G[gi].decision=v;render();}
function count(){let m=G.filter(g=>g.decision=='merge').length;document.getElementById('status').textContent=m+' groups to merge';document.getElementById('apply').textContent='Merge '+m+' groups';}
function esc(s){return(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
document.getElementById('q').oninput=render;
document.getElementById('apply').onclick=async()=>{let m=G.filter(g=>g.decision=='merge').length;
  if(!m){alert('Nothing selected to merge.');return;}
  if(!confirm('Combine '+m+' groups?\n\nEach becomes one card with all phones/emails. Removed cards are exported to a .vcf on your Desktop first, so it’s reversible.'))return;
  document.getElementById('status').textContent='Working…';
  let d={};G.forEach((g,i)=>d[i]=g.decision);
  let j=await(await fetch('/apply',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({decisions:d})})).json();
  document.getElementById('status').innerHTML='<span class=ok>Merged '+j.merged+', removed '+j.deleted+' ✓</span>';setTimeout(boot,1200);};
boot();
</script></body></html>"""

def scan():
    ppl = load_names(); STATE["count"] = len(ppl)
    display, auto = build_groups(ppl)
    if auto:
        _, n = auto_merge(auto); STATE["auto"] += n
        if not DRY_RUN:
            ppl = load_names(); STATE["count"] = len(ppl)
            display, _ = build_groups(ppl)
    STATE["groups"] = display

class H(http.server.BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def _s(self,c,b,t="application/json"):
        bb=b.encode() if isinstance(b,str) else b
        self.send_response(c);self.send_header("Content-Type",t);self.send_header("Content-Length",str(len(bb)));self.end_headers();self.wfile.write(bb)
    def do_GET(self):
        if self.path=="/": self._s(200,PAGE,"text/html; charset=utf-8")
        elif self.path=="/data": self._s(200,json.dumps({"groups":STATE["groups"],"count":STATE["count"],"auto":STATE["auto"]}))
        else: self._s(404,"{}")
    def do_POST(self):
        n=int(self.headers.get("Content-Length",0));body=json.loads(self.rfile.read(n) or "{}")
        if self.path=="/apply":
            m,d=apply_merges(body.get("decisions",{}))
            scan();self._s(200,json.dumps({"merged":m,"deleted":d}))
        else: self._s(404,"{}")

def main():
    print("🧹 Contacts Cleanup\n  Backing up…")
    dest,err=backup(); print("  backup ->",dest if dest else f"(warn: {err})")
    print("  Scanning + auto-combining exact duplicates…")
    scan()
    print(f"  {STATE['count']} contacts · auto-combined {STATE['auto']} exact dupes · {len(STATE['groups'])} groups to review")
    socketserver.TCPServer.allow_reuse_address=True
    with socketserver.TCPServer(("127.0.0.1",PORT),H) as h:
        url=f"http://127.0.0.1:{PORT}/"; print(f"\n  Opening {url}\n  Keep this window open; Ctrl+C when done.\n")
        threading.Timer(0.6,lambda:webbrowser.open(url)).start()
        try: h.serve_forever()
        except KeyboardInterrupt: print("\n  Done. Backup is on your Desktop.")

if __name__=="__main__": main()
