"""Deploy the offline CyberChef build into app/static/decode/.

CyberChef (v11+) is no longer a single self-contained HTML file: it ships as a
multi-file build (entry HTML + assets/ + modules/ + images/) inside a release
zip whose asset name is commit-hash based. The download URL is therefore
scraped from the GitHub release page rather than constructed.

A committed copy under app/static/decode/ means Open works with zero network
from first run. Update re-fetches the latest release; it soft-fails and leaves
any existing build untouched (handled by the caller).
"""
import io
import os
import re
import shutil
import tempfile
import urllib.request
import zipfile

REPO = "gchq/CyberChef"
UA = "Blackheart-decode/1.0 (offline pentest kit)"
LATEST = "https://github.com/%s/releases/latest" % REPO
EXPANDED = "https://github.com/%s/releases/expanded_assets/%s"

_ENTRY_RE = re.compile(r"^CyberChef_v.*\.html$")


def _get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=timeout)


def _latest_tag():
    # /releases/latest 302-redirects to /releases/tag/<tag>
    with _get(LATEST) as r:
        return r.geturl().rstrip("/").split("/")[-1]


def _asset_url(tag):
    with _get(EXPANDED % (REPO, tag)) as r:
        html = r.read().decode("utf-8", "replace")
    hits = re.findall(
        r'href="(/%s/releases/download/[^"]+\.zip)"' % re.escape(REPO), html)
    if not hits:
        raise RuntimeError("no zip asset on release page")
    return "https://github.com" + hits[0]


def _download(url):
    with _get(url, timeout=300) as r:
        return r.read()


def deploy(zip_bytes, out_dir, tag=None):
    """Extract the CyberChef zip into out_dir, entry HTML written as index.html.

    Drops precompressed .gz/.br siblings that duplicate an uncompressed file
    (the Flask dev server does no content-encoding negotiation, so it serves the
    plain files); standalone .gz data assets, e.g. tesseract lang-data, are kept.
    Returns (file_count, version_string).
    """
    tmp = tempfile.mkdtemp(prefix="bh_decode_")
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            z.extractall(tmp)

        # some zips wrap everything in a single top-level dir; find the real root
        top = [os.path.join(tmp, e) for e in os.listdir(tmp)]
        subdirs = [p for p in top if os.path.isdir(p)]
        topfiles = [p for p in top if os.path.isfile(p)]
        root = subdirs[0] if (len(subdirs) == 1 and not topfiles) else tmp

        entry = version = None
        for name in os.listdir(root):
            if _ENTRY_RE.match(name):
                entry = name
                m = re.search(r"_v([^ /]+)\.html$", name)
                version = m.group(1) if m else None
                break
        if not entry:
            raise RuntimeError("CyberChef entry HTML not found in release")

        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir, exist_ok=True)

        count = 0
        for dirpath, _dirs, filenames in os.walk(root):
            rel = os.path.relpath(dirpath, root)
            dst_dir = out_dir if rel == "." else os.path.join(out_dir, rel)
            os.makedirs(dst_dir, exist_ok=True)
            for fn in filenames:
                # entry html is (re)generated as index.html; skip its compressed twins
                if fn in ("index.html.gz", "index.html.br"):
                    continue
                if fn.endswith((".gz", ".br")) and \
                        os.path.exists(os.path.join(dirpath, fn[:-3])):
                    continue
                dst_name = "index.html" if fn == entry else fn
                shutil.copy2(os.path.join(dirpath, fn),
                             os.path.join(dst_dir, dst_name))
                count += 1

        return count, (version or (tag.lstrip("v") if tag else "unknown"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def build(out_dir):
    """Resolve latest release, download it, deploy. Returns (count, version)."""
    tag = _latest_tag()
    return deploy(_download(_asset_url(tag)), out_dir, tag=tag)
