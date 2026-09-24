"""Shared helpers for the offline reference builders (GTFOBins, LOLBAS).

No git and no Jekyll: the source repo is pulled as an HTTPS tarball, parsed, and
rendered into a single self-contained, searchable static page themed to match
Blackheart. Network is touched only when Update is clicked; soft-fails to a
status message and leaves any existing build untouched.
"""
import io
import json
import os
import tarfile
import tempfile
import urllib.request
from datetime import datetime, timezone
from html import escape as _esc

UA = "Blackheart-offlinedocs/1.0 (offline pentest kit)"


def esc(s):
    return _esc(str(s if s is not None else ""))


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def fetch_repo(url):
    """Download + extract a github tarball. Returns (tmp_root, repo_dir).
    Raises on network/extract failure (callers wrap it)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        buf = io.BytesIO(r.read())
    tmp = tempfile.mkdtemp(prefix="bh_doc_")
    with tarfile.open(fileobj=buf, mode="r:gz") as t:
        try:
            t.extractall(tmp, filter="data")   # py>=3.12
        except TypeError:
            t.extractall(tmp)
    dirs = [os.path.join(tmp, e) for e in os.listdir(tmp)
            if os.path.isdir(os.path.join(tmp, e))]
    return tmp, (dirs[0] if len(dirs) == 1 else tmp)


THEME = """
:root{--bg:#0a0a0c;--panel:#141416;--panel2:#1b1b1f;--border:#2a2a2f;
--bone:#e9e4d6;--dim:#a6a196;--faint:#6f6c64;--red:#c1121f;--red2:#e11d2a;
--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;--sans:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--bone);font-family:var(--sans);line-height:1.5}
header{position:sticky;top:0;background:linear-gradient(180deg,#0a0a0c,rgba(10,10,12,.92));
border-bottom:1px solid var(--border);padding:16px 22px;z-index:10}
header h1{margin:0 0 10px;font-size:20px}header h1 .t{color:var(--red2)}
.meta{color:var(--faint);font-size:12px;margin-bottom:12px}
#q{width:100%;max-width:520px;background:var(--panel2);border:1px solid var(--border);color:var(--bone);
font-family:var(--mono);font-size:14px;padding:10px 13px;border-radius:8px}
#q:focus{outline:2px solid var(--red);border-color:var(--red)}
#count{color:var(--faint);font-size:12px;margin-left:12px}
main{padding:18px 22px;max-width:1100px}
.cat{color:var(--faint);text-transform:uppercase;letter-spacing:.05em;font-size:11px;
font-weight:700;margin:26px 0 10px;border-bottom:1px solid var(--border);padding-bottom:6px}
details.entry{background:var(--panel);border:1px solid var(--border);border-radius:8px;margin:8px 0;overflow:hidden}
details.entry>summary{cursor:pointer;padding:12px 15px;font-family:var(--mono);font-size:14px;
list-style:none;display:flex;align-items:center;gap:10px}
details.entry>summary::-webkit-details-marker{display:none}
details.entry>summary::before{content:"+";color:var(--red);font-weight:700;width:12px}
details.entry[open]>summary::before{content:"\\2212"}
details.entry[open]>summary{border-bottom:1px solid var(--border);background:var(--panel2)}
.tags{margin-left:auto;display:flex;gap:5px;flex-wrap:wrap}
.tag{font-family:var(--sans);font-size:10px;font-weight:600;color:var(--dim);
background:var(--panel2);border:1px solid var(--border);border-radius:4px;padding:2px 6px;text-transform:uppercase}
.body{padding:14px 16px}
.fn{margin:0 0 18px}.fn:last-child{margin-bottom:0}
.fn h3{margin:0 0 8px;font-size:13px;color:var(--bone)}
.fn .desc{color:var(--dim);font-size:12.5px;margin:0 0 8px}
.ctx{display:inline-block;font-size:10px;color:var(--red2);border:1px solid var(--red);
border-radius:4px;padding:1px 6px;margin:0 4px 6px 0;text-transform:uppercase;letter-spacing:.03em}
pre{background:#0d0d10;border:1px solid var(--border);border-left:2px solid var(--red);
border-radius:6px;padding:11px 13px;overflow:auto;margin:0 0 8px}
pre code{font-family:var(--mono);font-size:12.5px;color:var(--bone);white-space:pre}
.cmt{color:var(--faint);font-size:12px;margin:0 0 10px;font-style:italic}
table.cmd{width:100%;border-collapse:collapse;font-size:12.5px;margin:0 0 12px}
table.cmd th{text-align:left;color:var(--faint);font-size:10.5px;text-transform:uppercase;
padding:0 10px 7px;border-bottom:1px solid var(--border)}
table.cmd td{padding:9px 10px;border-bottom:1px solid #1f1f23;vertical-align:top}
table.cmd td.c{font-family:var(--mono);color:var(--bone);white-space:pre-wrap;word-break:break-word}
.kv{color:var(--dim);font-size:12px;margin:4px 0}.kv b{color:var(--bone);font-weight:600}
a{color:var(--red2)}a:hover{color:var(--red)}
.links{font-size:12px;margin-top:8px}.links a{display:block;color:var(--dim);margin:2px 0;word-break:break-all}
.hidden{display:none}
footer{color:var(--faint);font-size:11px;padding:22px;text-align:center}
"""


def page(title, subtitle, source_note, body_html):
    """Wrap rendered entries in a full, self-contained searchable HTML page."""
    return """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} \u2014 Blackheart</title>
<style>{css}</style></head><body>
<header>
  <h1><span class="t">{title}</span> <span style="color:var(--faint);font-size:13px">offline</span></h1>
  <div class="meta">{subtitle} &middot; {note}</div>
  <input id="q" type="text" placeholder="filter by name\u2026" autocomplete="off" spellcheck="false"><span id="count"></span>
</header>
<main id="list">{body}</main>
<footer>Rendered offline by Blackheart from the upstream project. Data belongs to the respective project.</footer>
<script>
var q=document.getElementById('q'),entries=[].slice.call(document.querySelectorAll('.entry')),
cats=[].slice.call(document.querySelectorAll('.cat')),cnt=document.getElementById('count');
function upd(){{var t=q.value.trim().toLowerCase(),n=0;
entries.forEach(function(e){{var m=!t||e.getAttribute('data-name').indexOf(t)>-1;
e.classList.toggle('hidden',!m);if(m)n++;}});
cats.forEach(function(c){{var s=c.nextElementSibling,any=false;
while(s&&s.classList.contains('entry')){{if(!s.classList.contains('hidden'))any=true;s=s.nextElementSibling;}}
c.classList.toggle('hidden',!any);}});
cnt.textContent=n+' shown';}}
q.addEventListener('input',upd);cnt.textContent=entries.length+' entries';
</script>
</body></html>""".format(title=esc(title), css=THEME, subtitle=esc(subtitle),
                          note=esc(source_note), body=body_html)


def default_status(name):
    return {"last_update": None, "count": 0,
            "message": "%s not built yet \u2014 click Update once (needs network) to fetch it" % name}


def read_status(path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def write_status(path, status):
    try:
        path.write_text(json.dumps(status, indent=2))
    except Exception:
        pass
