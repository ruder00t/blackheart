"""Offline grading: parse detected tech, resolve to a source, compare against
the cached latest version, and colour it green / red / grey.

Reads only the local cache written by sources.refresh_cache(). No network here.
"""
import json
import re
from pathlib import Path

from . import sources

MOD = Path(__file__).resolve().parent
_VER_RE = re.compile(r"\d+(?:\.\d+)*")


def load_aliases():
    try:
        raw = json.loads((MOD / "aliases.json").read_text())
    except Exception:
        return {}
    return {k: v for k, v in raw.items()
            if not k.startswith("_") and isinstance(v, dict) and v.get("source")}


def normalize(name):
    return re.sub(r"\s+", " ", str(name or "").strip().lower())


def resolve(name):
    return load_aliases().get(normalize(name))


def _vtuple(s):
    m = _VER_RE.search(str(s or ""))
    if not m:
        return None
    return [int(x) for x in m.group(0).split(".")]


def compare(detected, latest):
    """green if the components the target reports match the latest at those
    positions (so '8.4' vs '8.4.1' is green), red on any mismatch."""
    dv, lv = _vtuple(detected), _vtuple(latest)
    if not dv or not lv:
        return None
    for i in range(min(len(dv), len(lv))):
        if dv[i] != lv[i]:
            return "red"
    return "green"


# ---------- input parsing ----------

def _add(out, name, version):
    name = str(name or "").strip()
    if not name:
        return
    version = str(version or "").strip()
    # skip pure meta keys some tools include
    if name.lower() in ("domain", "results", "target", "url", "http_status"):
        return
    out.append({"name": name, "version": version})


def _walk_wappalyzer_results(results, out):
    # {"PHP:8.1":{}, "Nginx":{}}  (wappalyzergo-style keys)
    for key in results:
        if ":" in key:
            n, v = key.rsplit(":", 1)
            _add(out, n, v)
        else:
            _add(out, key, "")


def _walk_named_versions(d, out):
    # {"PHP": {"versions": ["8.1"], ...}}  or  {"PHP": {"version": "8.1"}}
    for name, meta in d.items():
        if not isinstance(meta, dict):
            continue
        vers = meta.get("versions")
        if isinstance(vers, list) and vers:
            _add(out, name, vers[0])
        else:
            _add(out, name, meta.get("version", ""))


def _walk_whatweb(obj, out):
    # WhatWeb --log-json: [{"plugins": {"WordPress": {"version": ["6.5"]}}}]
    plugins = obj.get("plugins")
    if not isinstance(plugins, dict):
        return
    for name, meta in plugins.items():
        v = ""
        if isinstance(meta, dict):
            ver = meta.get("version")
            if isinstance(ver, list) and ver:
                v = ver[0]
            elif isinstance(ver, str):
                v = ver
        _add(out, name, v)


def _walk_httpx_tech(techs, out):
    # httpx -json: {"tech": ["PHP:8.1", "Nginx"]}
    for t in techs:
        t = str(t)
        if ":" in t:
            n, v = t.rsplit(":", 1)
            _add(out, n, v)
        else:
            _add(out, t, "")


def parse_input(text):
    """Accept WhatWeb, Wappalyzer, or httpx JSON (single object, array, or
    newline-delimited). Returns [{name, version}]. Best-effort, never raises."""
    text = (text or "").strip()
    if not text:
        return []

    docs = []
    try:
        docs = [json.loads(text)]
    except Exception:
        for line in text.splitlines():
            line = line.strip().rstrip(",")
            if not line:
                continue
            try:
                docs.append(json.loads(line))
            except Exception:
                pass
    if not docs:
        return []

    out = []
    stack = list(docs)
    while stack:
        node = stack.pop()
        if isinstance(node, list):
            stack.extend(node)
        elif isinstance(node, dict):
            if "plugins" in node and isinstance(node["plugins"], dict):
                _walk_whatweb(node, out)
            elif "tech" in node and isinstance(node["tech"], list):
                _walk_httpx_tech(node["tech"], out)
            elif "results" in node and isinstance(node["results"], dict):
                _walk_wappalyzer_results(node["results"], out)
            elif "technologies" in node and isinstance(node["technologies"], list):
                for t in node["technologies"]:
                    if isinstance(t, dict):
                        _add(out, t.get("name"), t.get("version"))
            elif all(isinstance(v, dict) for v in node.values()) and node:
                _walk_named_versions(node, out)

    # de-dupe on (name, version)
    seen, uniq = set(), []
    for r in out:
        k = (r["name"].lower(), r["version"])
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    return uniq


# ---------- grading ----------

def grade_rows(items):
    cache = sources.load_cache()
    rows = []
    for it in items:
        name, version = it.get("name", ""), it.get("version", "")
        row = {"name": name, "version": version, "latest": "", "source": "",
               "state": "grey", "note": ""}

        if not _vtuple(version):
            row["note"] = "no version reported"
            rows.append(row)
            continue

        entry = resolve(name)
        if not entry:
            row["note"] = "not in version DB"
            rows.append(row)
            continue

        row["source"] = entry["source"]
        key = "%s:%s" % (entry["source"], entry.get("id", ""))
        cached = cache.get(key)
        if not cached or not cached.get("latest"):
            row["note"] = "no cached latest \u2014 run Update"
            rows.append(row)
            continue

        latest = cached["latest"]
        row["latest"] = latest
        state = compare(version, latest)
        if state == "green":
            row["state"], row["note"] = "green", "up to date"
        elif state == "red":
            row["state"], row["note"] = "red", "outdated \u2014 latest is %s" % latest
        else:
            row["note"] = "could not compare"
        rows.append(row)

    order = {"red": 0, "grey": 1, "green": 2}
    rows.sort(key=lambda r: (order.get(r["state"], 3), r["name"].lower()))
    return rows
