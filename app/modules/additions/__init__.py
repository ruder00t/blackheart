"""Additions: a persistent overlay that lets you append your own notes/commands
to any existing tab without editing source.

Stored in data/additions.json, keyed by target module id:
    { "<module_id>": [ {"id": str, "text": str, "pos": "top"|"bottom"}, ... ] }

The overlay is injected into every page client-side (see app.js) so entries show
up on their target tab, in the normal card style, with a copy button. Export /
import make the overlay survive a fresh download of the program.
"""
import json

from flask import Blueprint, render_template, request, jsonify, current_app, Response

from app import store

bp = Blueprint("additions", __name__)
FILE = store.DATA / "additions.json"

# never offer these as targets
SKIP_TARGETS = {"additions", "home"}


def load():
    if FILE.exists():
        try:
            d = json.loads(FILE.read_text())
            if isinstance(d, dict):
                return d
        except Exception:
            pass
    return {}


def _clean(data):
    out = {}
    for mid, items in (data or {}).items():
        if not isinstance(items, list):
            continue
        clean = []
        for it in items:
            if not isinstance(it, dict):
                continue
            text = str(it.get("text", "")).strip()
            if not text:
                continue
            pos = "top" if it.get("pos") == "top" else "bottom"
            clean.append({
                "id": str(it.get("id") or ""),
                "text": text,
                "pos": pos,
            })
        if clean:
            out[str(mid)] = clean
    return out


def save(data):
    clean = _clean(data)
    FILE.write_text(json.dumps(clean, indent=2))
    return clean


def targets():
    """Flatten the sidebar nav into selectable targets: [{id, label}]."""
    out = []
    for category, section in current_app.config.get("NAV", []):
        def take(it):
            if it.get("soon") or not it.get("id"):
                return
            if it["id"] in SKIP_TARGETS:
                return
            out.append({"id": it["id"], "label": category + " — " + it["title"]})
        for it in section["entries"]:
            take(it)
        for gname, gitems in section["groups"]:
            for it in gitems:
                take(it)
    return out


@bp.route("/additions")
def index():
    return render_template("additions.html", active="additions",
                           additions=load(), targets=targets(),
                           varkeys=[k for k, _, _ in store.VARFIELDS])


@bp.route("/api/additions", methods=["GET", "POST"])
def api():
    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}
        return jsonify(ok=True, additions=save(data))
    return jsonify(load())


@bp.route("/api/additions/export")
def export():
    body = json.dumps(load(), indent=2)
    return Response(body, mimetype="application/json",
                    headers={"Content-Disposition": "attachment; filename=blackheart-additions.json"})


MODULE = {"id": "additions", "title": "Additions", "category": "Additions",
          "order": 0, "blueprint": bp, "endpoint": "additions.index"}
