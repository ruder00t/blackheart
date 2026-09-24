"""VersionCheck module.

Paste WhatWeb (or Wappalyzer / httpx) JSON, or type a product + version by hand,
and each detected technology is graded against a locally-cached "latest version"
table: green = current, red = outdated, grey = unknown / no version.

The latest-version cache is refreshed from public registries only at update time
(a non-blocking try at startup, and the "Update now" button). Grading itself is
fully offline. Lives in Recon, next to CheckMap.
"""
import threading

from flask import Blueprint, render_template, request

from . import grade, sources

bp = Blueprint("versioncheck", __name__)

SUGGEST = "whatweb -a 3 --open-timeout=5 --read-timeout=15 --log-json=whatweb.json http://$RHOST"


def _parse_nmap(fstorage):
    """Pull product/version out of an uploaded nmap scan (xml richest). Reuses
    the CheckMap nmap parser. Only rows that carry a version are kept."""
    import os
    import tempfile
    from app.core import parser as nmap_parser
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".scan")
    try:
        fstorage.save(tmp.name)
        tmp.close()
        hosts = nmap_parser.parse(tmp.name)
    except Exception:
        return []
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
    items = []
    for h in hosts:
        for p in h.get("ports", []):
            name = (p.get("product") or p.get("service") or "").strip()
            ver = (p.get("version") or "").strip()
            if name and ver:
                items.append({"name": name, "version": ver})
    return items


@bp.route("/versioncheck", methods=["GET", "POST"])
def index():
    rows, submitted = [], False
    if request.method == "POST":
        submitted = True
        nmap = request.files.get("nmap")
        manual_name = (request.form.get("product") or "").strip()
        manual_ver = (request.form.get("version") or "").strip()
        pasted = request.form.get("scan") or ""
        if nmap and nmap.filename:
            rows = grade.grade_rows(_parse_nmap(nmap))
        elif manual_name:
            rows = grade.grade_rows([{"name": manual_name, "version": manual_ver}])
        else:
            rows = grade.grade_rows(grade.parse_input(pasted))

    counts = {"green": 0, "red": 0, "grey": 0}
    for r in rows:
        counts[r["state"]] = counts.get(r["state"], 0) + 1

    return render_template(
        "versioncheck.html", active="versioncheck", suggest=SUGGEST,
        rows=rows, counts=counts, submitted=submitted,
        status=sources.load_status(),
        any_red=any(r["state"] == "red" for r in rows),
    )


@bp.route("/versioncheck/update", methods=["POST"])
def update():
    try:
        sources.refresh_cache()
    except Exception:
        pass
    return index()


def kick_startup_refresh(app):
    """Fire a one-shot, non-blocking cache refresh. Never blocks boot, never
    raises: no connection just leaves the cache as-is and records a status note."""
    def _run():
        try:
            sources.refresh_cache()
        except Exception:
            pass
    threading.Thread(target=_run, name="versioncheck-refresh", daemon=True).start()


MODULE = {"id": "versioncheck", "title": "VersionCheck", "category": "Recon",
          "order": 1, "blueprint": bp, "endpoint": "versioncheck.index"}
