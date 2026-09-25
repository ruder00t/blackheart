"""Script library: named multi-line scripts, persisted to data/script_library.json.
Bodies may contain $VAR placeholders that substitute live."""
import json
from flask import Blueprint, render_template, request, jsonify
from app import store

bp = Blueprint("script_library", __name__)
FILE = store.DATA / "script_library.json"


def load():
    if FILE.exists():
        try:
            d = json.loads(FILE.read_text())
            if isinstance(d, dict) and isinstance(d.get("scripts"), list):
                return d
        except Exception:
            pass
    return {"scripts": []}


def save(d):
    FILE.write_text(json.dumps(d, indent=2))
    return d


@bp.route("/scriptlibrary")
def index():
    return render_template("script_library.html", active="script_library",
                           data=load(),
                           varkeys=[k for k, _, _ in store.VARFIELDS])


@bp.route("/api/script-library", methods=["GET", "POST"])
def api():
    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}
        clean = []
        for s in data.get("scripts", []):
            name = str(s.get("name", "")).strip()
            body = str(s.get("body", ""))
            if name and body.strip():
                clean.append({"name": name, "body": body})
        return jsonify(ok=True, data=save({"scripts": clean}))
    return jsonify(load())


MODULE = {"id": "script_library", "title": "Script Library", "category": "Libraries",
          "order": 2, "blueprint": bp, "endpoint": "script_library.index"}
