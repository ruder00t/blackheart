#!/usr/bin/env python3
"""
build_hacktricks.py — turn a HackTricks Markdown clone into a static, fully
offline HTML site, themed to match Blackheart (dark + red). No Docker, no mdBook.

Only dependency: python-markdown + pygments  ->  pip install markdown pygments

Usage:
    # 1. get the markdown once (needs network ONCE, then never again):
    git clone --depth 1 https://github.com/HackTricks-wiki/hacktricks

    # 2. build into Blackheart's static dir:
    python3 tools/build_hacktricks.py --src ./hacktricks --out app/static/hacktricks

The output is self-contained: open out/index.html directly, or let Blackheart
serve it (the HackTricks tab links to /static/hacktricks/index.html).

What it handles (matching hacktricks-preprocessor.py + mdBook behaviour):
  - {{#include ...banners/hacktricks-training.md}}  -> stripped (external ads)
  - {{#include other.md}}                           -> inlined
  - {{#ref}} path {{#endref}}                       -> styled link card
  - {{#file}} name {{#endfile}}                     -> link into files/
  - {{#tabs}}/{{#tab name="x"}}                     -> labelled sections
  - > [!TIP|NOTE|WARNING|DANGER|CAUTION|INFO]       -> coloured callouts
  - README.md -> index.html, *.md -> *.html, link/anchor rewriting
  - copies every non-markdown asset (images, files) verbatim
"""
import argparse
import html
import os
import re
import shutil
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    markdown = None  # checked in build(); lets this module import without the dep

BANNER = "banners/hacktricks-training.md"
CALLOUTS = {"TIP": "tip", "NOTE": "note", "INFO": "note", "IMPORTANT": "note",
            "WARNING": "warn", "CAUTION": "warn", "DANGER": "danger"}

MD_EXTS = ["fenced_code", "tables", "toc", "attr_list", "sane_lists",
           "codehilite", "md_in_html"]
MD_CFG = {"codehilite": {"guess_lang": False, "noclasses": False}}


# ---------- small helpers ----------

def prettify(seg):
    seg = seg.rsplit("/", 1)[-1]
    seg = re.sub(r"\.(md|html)$", "", seg)
    seg = seg.replace("index", "").replace("README", "")
    seg = seg.replace("-", " ").replace("_", " ").strip()
    return seg.title() if seg else "Link"


def md_href(href):
    """Rewrite an inter-page markdown target to its built html path."""
    href = href.strip().replace("`", "")
    if href.startswith(("http://", "https://", "mailto:", "//", "#")):
        return href
    if "#" in href:
        path, anchor = href.split("#", 1)
        anchor = "#" + anchor
    else:
        path, anchor = href, ""
    if path.endswith("/"):
        path += "index.html"
    elif path.endswith("/README.md") or path == "README.md":
        path = path[:-len("README.md")] + "index.html"
    elif path.endswith(".md"):
        path = path[:-3] + ".html"
    return path + anchor


# ---------- custom-syntax preprocessing (before markdown) ----------

def strip_includes(text, base_dir, depth=0):
    def repl(m):
        target = m.group(1).strip()
        if BANNER in target:
            return ""
        if depth > 3:
            return ""
        p = (base_dir / target).resolve()
        if p.exists() and p.suffix == ".md":
            return strip_includes(p.read_text(encoding="utf-8", errors="replace"),
                                  p.parent, depth + 1)
        return ""
    return re.sub(r"\{\{#include\s+([^}]+)\}\}", repl, text)


def conv_refs(text, root_prefix):
    def ref(m):
        inner = m.group(1).strip()
        href = md_href(inner)
        title = prettify(inner)
        return ('<a class="ht-ref" href="%s"><span>%s</span></a>'
                % (html.escape(href), html.escape(title)))
    text = re.sub(r"\{\{\s*#ref\s*\}\}\s*(.*?)\s*\{\{\s*#endref\s*\}\}", ref, text, flags=re.S)

    def fil(m):
        name = m.group(1).strip()
        return ('<a class="ht-ref file" href="%sfiles/%s"><span>%s</span></a>'
                % (root_prefix, html.escape(name), html.escape(name)))
    text = re.sub(r"\{\{\s*#file\s*\}\}\s*(.*?)\s*\{\{\s*#endfile\s*\}\}", fil, text, flags=re.S)
    # neutralise orphan markers (a couple of source pages have unclosed {{#ref}})
    text = re.sub(r"\{\{\s*#(end)?(ref|file)\s*\}\}", "", text)
    return text


def conv_tabs(text):
    text = re.sub(r"\{\{\s*#tab\s+name=\"([^\"]*)\"\s*\}\}", r"\n\n**\1**\n\n", text)
    text = re.sub(r"\{\{\s*#tab\s+name='([^']*)'\s*\}\}", r"\n\n**\1**\n\n", text)
    text = re.sub(r"\{\{\s*#endtab\s*\}\}|\{\{\s*#tabs\s*\}\}|\{\{\s*#endtabs\s*\}\}", "", text)
    return text


def conv_callouts(text, holder):
    """Convert GitHub-style > [!TIP] blockquotes into placeholder tokens whose
    HTML is rendered separately and re-inserted after the main conversion."""
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        m = re.match(r"^\s*>\s*\[!(\w+)\]\s*(.*)$", lines[i])
        if m and m.group(1).upper() in CALLOUTS:
            kind = CALLOUTS[m.group(1).upper()]
            body = []
            first = m.group(2).strip()
            if first:
                body.append(first)
            i += 1
            while i < len(lines) and re.match(r"^\s*>", lines[i]):
                body.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            inner = markdown.markdown("\n".join(body), extensions=MD_EXTS,
                                      extension_configs=MD_CFG)
            inner = rewrite_links(inner)
            token = "\uE000CALL%d\uE000" % len(holder)
            holder[token] = '<div class="ht-callout %s">%s</div>' % (kind, inner)
            out.append("")
            out.append(token)
            out.append("")
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out)


def conv_note(text, holder):
    """{{#note}} ... {{#endnote}} -> note callout box."""
    def note(m):
        inner = markdown.markdown(m.group(1).strip(), extensions=MD_EXTS,
                                  extension_configs=MD_CFG)
        inner = rewrite_links(inner)
        token = "\uE000WRAP%d\uE000" % len(holder)
        holder[token] = '<div class="ht-callout note">%s</div>' % inner
        return "\n\n%s\n\n" % token
    return re.sub(r"\{\{\s*#note\s*\}\}(.*?)\{\{\s*#endnote\s*\}\}", note, text, flags=re.S)


def rewrite_links(htmltext):
    def repl(m):
        return 'href="%s"' % md_href(m.group(1))
    return re.sub(r'href="([^"]+)"', repl, htmltext)


# ---------- SUMMARY parsing / sidebar ----------

def parse_summary(src):
    nav = []  # (level:int, title:str, href:str|None)
    f = src / "SUMMARY.md"
    if not f.exists():
        return nav
    first_h1_seen = False
    for line in f.read_text(encoding="utf-8", errors="replace").split("\n"):
        item = re.match(r"^(\s*)-\s*\[(.*?)\]\((.*?)\)", line)
        if item:
            level = len(item.group(1)) // 2
            nav.append((level, item.group(2).strip(), md_href(item.group(3))))
            continue
        hdr = re.match(r"^#{1,6}\s+(.*)$", line)
        if hdr:
            if not first_h1_seen and hdr.group(1).strip().upper() == "SUMMARY.MD":
                first_h1_seen = True
                continue
            nav.append((-1, hdr.group(1).strip(), None))
    return nav


def sidebar_html(nav, root_prefix, active_href):
    rows = ['<input class="ht-filter" id="htFilter" placeholder="filter…">']
    rows.append('<nav class="ht-nav">')
    for level, title, href in nav:
        if href is None:
            rows.append('<div class="ht-part">%s</div>' % html.escape(title))
            continue
        cls = "ht-link" + (" active" if href == active_href else "")
        pad = 8 + level * 12
        rows.append('<a class="%s" style="padding-left:%dpx" href="%s%s">%s</a>'
                    % (cls, pad, root_prefix, html.escape(href), html.escape(title)))
    rows.append("</nav>")
    return "\n".join(rows)


# ---------- theme + page template ----------

THEME_CSS = """
:root{--bg:#0a0a0c;--side:#08080a;--panel:#141416;--panel2:#1b1b1f;
--border:#2a2a2f;--soft:#1f1f23;--bone:#e9e4d6;--dim:#a6a196;--faint:#6f6c64;
--red:#c1121f;--redb:#e11d2a;--reddim:#7a1a20;
--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
--sans:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
*{box-sizing:border-box}html,body{margin:0}
body{background:var(--bg);color:var(--bone);font:14px/1.6 var(--sans);
display:grid;grid-template-columns:300px 1fr;min-height:100vh}
a{color:var(--redb);text-decoration:none}a:hover{text-decoration:underline}
.ht-side{background:var(--side);border-right:1px solid var(--soft);
position:sticky;top:0;height:100vh;overflow-y:auto;padding:14px 10px;font-size:13px}
.ht-brand{font-family:var(--mono);font-weight:700;font-size:17px;color:var(--bone);
padding:4px 8px 12px;border-bottom:1px solid var(--soft);margin-bottom:10px}
.ht-brand b{color:var(--red)}
.ht-filter{width:100%;background:var(--panel2);border:1px solid var(--border);
color:var(--bone);font:inherit;padding:7px 9px;border-radius:6px;margin-bottom:10px}
.ht-filter:focus{outline:2px solid var(--red);border-color:var(--red)}
.ht-nav{display:flex;flex-direction:column}
.ht-part{color:var(--faint);font-size:11px;font-weight:700;letter-spacing:.03em;
text-transform:uppercase;margin:14px 0 4px;padding:0 8px}
.ht-link{color:var(--dim);padding:5px 8px;border-left:2px solid transparent;
border-radius:0 6px 6px 0;white-space:normal}
.ht-link:hover{background:var(--panel);color:var(--bone);text-decoration:none}
.ht-link.active{background:linear-gradient(90deg,rgba(193,18,31,.16),transparent);
color:var(--bone);border-left-color:var(--red)}
.ht-main{max-width:920px;padding:34px 44px 80px;overflow-x:hidden}
.ht-main h1,.ht-main h2,.ht-main h3{line-height:1.25}
.ht-main h1{font-size:26px;border-bottom:1px solid var(--border);padding-bottom:10px}
.ht-main h2{font-size:20px;margin-top:34px}
.ht-main h3{font-size:16px;color:var(--bone)}
.ht-main code{font-family:var(--mono);font-size:12.5px;background:#060608;
border:1px solid var(--soft);border-radius:4px;padding:1px 5px;color:#f0d9b5}
.ht-main pre{background:#060608;border:1px solid var(--soft);border-radius:8px;
padding:14px 16px;overflow-x:auto}
.ht-main pre code{background:none;border:0;padding:0;color:var(--bone)}
.ht-main img{max-width:100%;height:auto;border-radius:6px}
.ht-main table{border-collapse:collapse;width:100%;margin:14px 0;font-size:13px}
.ht-main th,.ht-main td{border:1px solid var(--border);padding:7px 10px;text-align:left}
.ht-main th{background:var(--panel2)}
.ht-main blockquote{border-left:3px solid var(--reddim);margin:14px 0;
padding:2px 14px;color:var(--dim)}
.ht-ref{display:inline-block;background:var(--panel);border:1px solid var(--border);
border-left:3px solid var(--red);border-radius:6px;padding:9px 13px;margin:8px 0;
color:var(--bone)!important;text-decoration:none!important}
.ht-ref:hover{border-color:var(--red);background:var(--panel2)}
.ht-ref.file{border-left-color:var(--dim)}
.ht-callout{border:1px solid var(--border);border-left:3px solid var(--dim);
background:var(--panel);border-radius:6px;padding:2px 16px;margin:16px 0}
.ht-callout.tip{border-left-color:var(--red)}
.ht-callout.warn{border-left-color:#c9962b}
.ht-callout.danger{border-left-color:var(--redb)}
.ht-callout.note{border-left-color:#3a7bd5}
.ht-callout>:first-child{margin-top:8px}.ht-callout>:last-child{margin-bottom:8px}
@media(max-width:820px){body{grid-template-columns:1fr}.ht-side{display:none}}
"""

NAV_JS = """
(function(){var f=document.getElementById('htFilter');if(!f)return;
var links=[].slice.call(document.querySelectorAll('.ht-nav .ht-link'));
f.addEventListener('input',function(){var q=f.value.toLowerCase();
links.forEach(function(a){a.style.display=a.textContent.toLowerCase().indexOf(q)>-1?'':'none';});});
var act=document.querySelector('.ht-link.active');if(act)act.scrollIntoView({block:'center'});})();
"""

PAGE = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · HackTricks</title>
<link rel="stylesheet" href="{root}_ht/theme.css">
</head><body>
<aside class="ht-side">
<div class="ht-brand">Black<b>heart</b> · HackTricks</div>
{sidebar}
</aside>
<main class="ht-main">{content}</main>
<script src="{root}_ht/nav.js"></script>
</body></html>"""


# ---------- build ----------

def build(src, out):
    if markdown is None:
        raise RuntimeError("python-markdown not installed (pip install markdown pygments)")
    src, out = Path(src).resolve(), Path(out).resolve()
    if not (src / "src" / "SUMMARY.md").exists():
        raise RuntimeError("SUMMARY.md not found under %s/src — is --src a hacktricks clone?" % src)
    src = src / "src"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    nav = parse_summary(src)
    (out / "_ht").mkdir()
    (out / "_ht" / "theme.css").write_text(THEME_CSS)
    (out / "_ht" / "nav.js").write_text(NAV_JS)

    md_files, assets, pages = 0, 0, 0
    for path in src.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        if path.suffix == ".md":
            md_files += 1
            if rel.name.upper() == "SUMMARY.MD":
                continue
            if str(rel).replace(os.sep, "/").startswith("banners/"):
                continue  # external ad banner — not a real page
            # output path: README.md -> index.html, else .html
            if rel.name == "README.md":
                rel_html = rel.parent / "index.html"
            else:
                rel_html = rel.with_suffix(".html")
            depth = str(rel_html).count(os.sep)
            root_prefix = "../" * depth

            raw = path.read_text(encoding="utf-8", errors="replace")
            raw = strip_includes(raw, path.parent)
            raw = conv_tabs(raw)
            raw = conv_refs(raw, root_prefix)
            raw = re.sub(r"\{\{\s*#?reading_time\s*\}\}", "", raw)
            holder = {}
            raw = conv_callouts(raw, holder)
            raw = conv_note(raw, holder)

            body = markdown.markdown(raw, extensions=MD_EXTS, extension_configs=MD_CFG)
            body = rewrite_links(body)
            for tok, hhtml in holder.items():
                body = body.replace("<p>%s</p>" % tok, hhtml).replace(tok, hhtml)

            href_self = str(rel_html).replace(os.sep, "/")
            title = prettify(rel.name) or "HackTricks"
            m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
            if m:
                title = re.sub(r"<[^>]+>", "", m.group(1)).strip() or title

            page = PAGE.format(title=html.escape(title), root=root_prefix,
                               sidebar=sidebar_html(nav, root_prefix, href_self),
                               content=body)
            dest = out / rel_html
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(page, encoding="utf-8")
            pages += 1
        else:
            assets += 1
            dest = out / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)

    # ensure a root index.html exists (src/README.md usually provides it)
    if not (out / "index.html").exists() and nav:
        first = next((h for _, _, h in nav if h), None)
        if first:
            (out / "index.html").write_text(
                PAGE.format(title="HackTricks", root="",
                            sidebar=sidebar_html(nav, "", ""),
                            content='<h1>HackTricks (offline)</h1><p><a href="%s">Start »</a></p>' % first))

    print("markdown files: %d | pages built: %d | assets copied: %d" % (md_files, pages, assets))
    print("output: %s" % out)
    print("open:   %s/index.html" % out)
    return pages


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Build HackTricks markdown into a static offline site.")
    ap.add_argument("--src", default="./hacktricks", help="path to a hacktricks git clone")
    ap.add_argument("--out", default="app/static/hacktricks", help="output directory")
    a = ap.parse_args()
    try:
        build(a.src, a.out)
    except RuntimeError as e:
        sys.exit(str(e))
