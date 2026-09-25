"""Latest-version fetchers, one per ecosystem, plus the cache refresher.

Network is touched ONLY here, and ONLY at update time (startup try, or the
"Update now" button). Every fetch is wrapped, short-timeout, and soft-fails to
None. The rest of the app (grading) reads the local cache and never goes online.

Cache  : data/versioncheck_cache.json   { "source:id": {latest, source, id, fetched} }
Status : data/versioncheck_status.json  { last_run, ok[], failed[], count, message }
"""
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from app import store

CACHE = store.DATA / "versioncheck_cache.json"
STATUS = store.DATA / "versioncheck_status.json"

UA = "Blackheart-versioncheck/1.0 (offline pentest kit)"
TIMEOUT = 5


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


# ---------- per-source: return latest version string, or None ----------

def _endoflife(pid):
    data = _get("https://endoflife.date/api/%s.json" % urllib.parse.quote(pid))
    if isinstance(data, list) and data:
        # cycles are newest-first; take the newest cycle's latest patch
        for cyc in data:
            v = cyc.get("latest")
            if v:
                return str(v)
    return None


def _npm(pkg):
    p = pkg.replace("/", "%2F")
    return str(_get("https://registry.npmjs.org/%s/latest" % p).get("version") or "") or None


def _pypi(pkg):
    return str(_get("https://pypi.org/pypi/%s/json" % urllib.parse.quote(pkg))
               .get("info", {}).get("version") or "") or None


def _rubygems(gem):
    return str(_get("https://rubygems.org/api/v1/versions/%s/latest.json"
                    % urllib.parse.quote(gem)).get("version") or "") or None


def _packagist(name):
    data = _get("https://repo.packagist.org/p2/%s.json" % name)
    versions = data.get("packages", {}).get(name, [])
    for v in versions:  # newest-first
        ver = str(v.get("version", ""))
        if ver and "dev" not in ver.lower():
            return ver.lstrip("v")
    return None


def _crates(name):
    c = _get("https://crates.io/api/v1/crates/%s" % urllib.parse.quote(name)).get("crate", {})
    return str(c.get("max_stable_version") or c.get("newest_version") or "") or None


def _wp_plugin(slug):
    url = ("https://api.wordpress.org/plugins/info/1.2/"
           "?action=plugin_information&request[slug]=%s" % urllib.parse.quote(slug))
    d = _get(url)
    if isinstance(d, dict) and d.get("version"):
        return str(d["version"])
    return None


def _wp_theme(slug):
    url = ("https://api.wordpress.org/themes/info/1.2/"
           "?action=theme_information&request[slug]=%s" % urllib.parse.quote(slug))
    d = _get(url)
    if isinstance(d, dict) and d.get("version"):
        return str(d["version"])
    return None


def _wp_core(_id):
    d = _get("https://api.wordpress.org/core/version-check/1.7/")
    offers = d.get("offers") if isinstance(d, dict) else None
    if offers:
        return str(offers[0].get("version") or "") or None
    return None


FETCHERS = {
    "endoflife": _endoflife,
    "npm": _npm,
    "pypi": _pypi,
    "rubygems": _rubygems,
    "packagist": _packagist,
    "crates": _crates,
    "wordpress": _wp_plugin,
    "wordpress-theme": _wp_theme,
    "wordpress-core": _wp_core,
}


# ---------- cache / status ----------

def load_cache():
    if CACHE.exists():
        try:
            return json.loads(CACHE.read_text())
        except Exception:
            return {}
    return {}


def load_status():
    if STATUS.exists():
        try:
            return json.loads(STATUS.read_text())
        except Exception:
            pass
    return {"last_run": None, "ok": [], "failed": [], "count": 0,
            "message": "never updated \u2014 cache is empty, everything grades grey until you Update"}


def _write_status(s):
    try:
        STATUS.write_text(json.dumps(s, indent=2))
    except Exception:
        pass


def refresh_cache():
    """Fetch latest for every (source,id) in the alias map. Soft-fail throughout.

    Bails out early if the first handful of calls all fail (looks offline), so a
    disconnected box never hangs on ~30 timeouts.
    """
    from .grade import load_aliases

    targets = {}  # "source:id" -> (source, id)
    for entry in load_aliases().values():
        src, pid = entry.get("source"), entry.get("id", "")
        if src in FETCHERS:
            targets["%s:%s" % (src, pid)] = (src, pid)

    cache = load_cache()
    ok, failed = [], []
    consecutive_fail = 0
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    for key, (src, pid) in sorted(targets.items()):
        try:
            latest = FETCHERS[src](pid)
        except Exception:
            latest = None
        if latest:
            cache[key] = {"latest": latest, "source": src, "id": pid, "fetched": now}
            ok.append(key)
            consecutive_fail = 0
        else:
            failed.append(key)
            consecutive_fail += 1
            # nothing succeeded yet and several in a row failed -> assume no link
            if not ok and consecutive_fail >= 4:
                status = {"last_run": now, "ok": ok, "failed": failed,
                          "count": len(cache),
                          "message": "update skipped \u2014 no connection to the version databases "
                                     "(using the cache as-is)"}
                _write_status(status)
                return status
        time.sleep(0.05)  # be polite

    try:
        CACHE.write_text(json.dumps(cache, indent=2))
    except Exception:
        pass

    if ok and failed:
        msg = "updated %d, %d source(s) unreachable" % (len(ok), len(failed))
    elif ok:
        msg = "updated %d products" % len(ok)
    else:
        msg = "update failed \u2014 no products refreshed (offline?)"
    status = {"last_run": now, "ok": ok, "failed": failed, "count": len(cache), "message": msg}
    _write_status(status)
    return status
