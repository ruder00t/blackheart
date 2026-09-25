"""Command library: user-managed commands grouped by program, persisted to
data/library.json. Commands may contain $VAR placeholders that substitute live.
"""
import json

from flask import Blueprint, render_template, request, jsonify

from app import store

bp = Blueprint("library", __name__)
LIB = store.DATA / "library.json"


def load_lib():
    if LIB.exists():
        try:
            d = json.loads(LIB.read_text())
            if isinstance(d, dict) and isinstance(d.get("programs"), list):
                return d
        except Exception:
            pass
    return {"programs": []}


def save_lib(d):
    LIB.write_text(json.dumps(d, indent=2))
    return d


@bp.route("/library")
def index():
    return render_template("library.html", active="library",
                           library=load_lib(),
                           varkeys=[k for k, _, _ in store.VARFIELDS])


@bp.route("/api/library", methods=["GET", "POST"])
def api():
    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}
        clean = []
        for p in data.get("programs", []):
            name = str(p.get("name", "")).strip()
            cmds = [str(c) for c in p.get("commands", []) if str(c).strip()]
            if name:
                clean.append({"name": name, "commands": cmds})
        return jsonify(ok=True, library=save_lib({"programs": clean}))
    return jsonify(load_lib())


MODULE = {"id": "library", "title": "Command Library", "category": "Libraries",
          "order": 0, "blueprint": bp, "endpoint": "library.index"}
