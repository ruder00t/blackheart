"""Build the offline LOLBAS page from the upstream repo tarball."""
import os
import shutil

import yaml

from app.core import offlinedocs as od

TARBALL = "https://codeload.github.com/LOLBAS-Project/LOLBAS/tar.gz/refs/heads/master"

CAT_LABELS = {
    "OSBinaries": "OS Binaries", "OSScripts": "OS Scripts", "OSLibraries": "OS Libraries",
    "OtherMSBinaries": "Other MS Binaries", "HonorableMentions": "Honorable Mentions",
}


def _render_commands(cmds):
    if not isinstance(cmds, list) or not cmds:
        return ""
    rows = []
    for c in cmds:
        if not isinstance(c, dict):
            continue
        meta = []
        for k in ("Usecase", "Privileges", "MitreID", "Category"):
            if c.get(k):
                meta.append("%s: %s" % (k, od.esc(c[k])))
        rows.append(
            "<tr><td class=\"c\">%s</td><td>%s<div class=\"kv\">%s</div></td></tr>"
            % (od.esc(c.get("Command", "")), od.esc(c.get("Description", "")),
               " &middot; ".join(meta)))
    if not rows:
        return ""
    return ('<table class="cmd"><thead><tr><th>Command</th><th>Description</th></tr></thead>'
            '<tbody>%s</tbody></table>' % "".join(rows))


def _render_links(title, items, key):
    vals = []
    for it in (items or []):
        if isinstance(it, dict) and it.get(key):
            vals.append(it[key])
        elif isinstance(it, str):
            vals.append(it)
    if not vals:
        return ""
    body = "".join(
        ('<a href="%s" target="_blank" rel="noopener">%s</a>' % (od.esc(v), od.esc(v)))
        if str(v).startswith("http") else '<div class="kv">%s</div>' % od.esc(v)
        for v in vals)
    return '<div class="links"><b style="color:var(--dim);font-size:11px">%s</b>%s</div>' % (od.esc(title), body)


def _render_entry(doc, category):
    name = doc.get("Name", "?")
    tag = '<span class="tag">%s</span>' % od.esc(CAT_LABELS.get(category, category))
    paths = _render_links("Full paths", doc.get("Full_Path"), "Path")
    det = _render_links("Detection", doc.get("Detection"), "Sigma") or _render_links("Detection", doc.get("Detection"), "IOC")
    res = _render_links("Resources", doc.get("Resources"), "Link")
    body = "".join([
        '<p class="desc">%s</p>' % od.esc(doc.get("Description", "")),
        _render_commands(doc.get("Commands")),
        paths, det, res,
    ])
    return ('<details class="entry" data-name="%s"><summary>%s<span class="tags">%s</span></summary>'
            '<div class="body">%s</div></details>'
            % (od.esc(str(name).lower()), od.esc(name), tag, body))


def build(out_dir):
    tmp, repo = od.fetch_repo(TARBALL)
    try:
        yml_root = os.path.join(repo, "yml")
        by_cat, total = {}, 0
        for cat in sorted(os.listdir(yml_root)):
            cdir = os.path.join(yml_root, cat)
            if not os.path.isdir(cdir):
                continue
            items = []
            for fn in sorted(os.listdir(cdir)):
                if not fn.lower().endswith((".yml", ".yaml")):
                    continue
                try:
                    doc = yaml.safe_load(open(os.path.join(cdir, fn)).read())
                except Exception:
                    continue
                if isinstance(doc, dict) and doc.get("Name"):
                    items.append((str(doc["Name"]).lower(), _render_entry(doc, cat)))
                    total += 1
            if items:
                items.sort()
                by_cat[cat] = [h for _, h in items]

        parts = []
        for cat in ["OSBinaries", "OSScripts", "OSLibraries", "OtherMSBinaries", "HonorableMentions"]:
            if cat in by_cat:
                parts.append('<div class="cat">%s (%d)</div>%s'
                             % (od.esc(CAT_LABELS.get(cat, cat)), len(by_cat[cat]), "".join(by_cat[cat])))
        for cat in by_cat:  # any categories not in the fixed order
            if cat not in CAT_LABELS:
                parts.append('<div class="cat">%s (%d)</div>%s'
                             % (od.esc(cat), len(by_cat[cat]), "".join(by_cat[cat])))

        html = od.page("LOLBAS", "Living-off-the-land binaries, scripts and libraries (Windows)",
                       "%d entries" % total, "".join(parts))
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w") as fh:
            fh.write(html)
        return total
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
