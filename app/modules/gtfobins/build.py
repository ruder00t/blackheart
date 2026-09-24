"""Build the offline GTFOBins page from the upstream repo tarball."""
import os
import shutil

import yaml

from app.core import offlinedocs as od

TARBALL = "https://codeload.github.com/GTFOBins/GTFOBins.github.io/tar.gz/refs/heads/master"


def _labels(repo):
    try:
        data = yaml.safe_load(open(os.path.join(repo, "_data", "functions.yml")).read())
        return {k: (v.get("label") or k) for k, v in (data or {}).items() if isinstance(v, dict)}
    except Exception:
        return {}


def _render_function(fname, label, items):
    out = ['<div class="fn"><h3>%s</h3>' % od.esc(label)]
    for it in items:
        if not isinstance(it, dict):
            continue
        code = it.get("code", "")
        comment = it.get("comment", "")
        frm = it.get("from")
        ctxs = it.get("contexts") or {}
        if frm:
            out.append('<p class="cmt">inherited from <b>%s</b></p>' % od.esc(frm))
        if code:
            out.append("<pre><code>%s</code></pre>" % od.esc(code))
        if comment:
            out.append('<p class="cmt">%s</p>' % od.esc(comment))
        ctx_keys = list(ctxs.keys()) if isinstance(ctxs, dict) else []
        for c in ctx_keys:
            out.append('<span class="ctx">%s</span>' % od.esc(c))
            # a context may override the code (e.g. suid needs -p)
            if isinstance(ctxs.get(c), dict) and ctxs[c].get("code"):
                out.append("<pre><code>%s</code></pre>" % od.esc(ctxs[c]["code"]))
    out.append("</div>")
    return "".join(out)


def _render_entry(name, doc, labels):
    funcs = (doc or {}).get("functions") or {}
    fnames = sorted(funcs.keys())
    tags = "".join('<span class="tag">%s</span>' % od.esc(labels.get(f, f)) for f in fnames)
    body = "".join(_render_function(f, labels.get(f, f.replace("-", " ").title()), funcs[f])
                   for f in fnames if isinstance(funcs[f], list))
    return ('<details class="entry" data-name="%s"><summary>%s<span class="tags">%s</span></summary>'
            '<div class="body">%s</div></details>'
            % (od.esc(name.lower()), od.esc(name), tags, body))


def build(out_dir):
    """Download + render into out_dir/index.html. Returns entry count."""
    tmp, repo = od.fetch_repo(TARBALL)
    try:
        labels = _labels(repo)
        gdir = os.path.join(repo, "_gtfobins")
        names = sorted(f for f in os.listdir(gdir) if os.path.isfile(os.path.join(gdir, f)))
        entries = []
        for name in names:
            try:
                doc = yaml.safe_load(open(os.path.join(gdir, name)).read())
            except Exception:
                continue
            if doc and doc.get("functions"):
                entries.append(_render_entry(name, doc, labels))
        body = '<div class="cat">%d binaries</div>%s' % (len(entries), "".join(entries))
        html = od.page("GTFOBins", "Unix binaries to bypass local security restrictions",
                       "%d entries" % len(entries), body)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w") as fh:
            fh.write(html)
        return len(entries)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
