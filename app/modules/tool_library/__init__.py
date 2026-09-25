"""Tool library: name + download/link pairs, persisted to data/tool_library.json.
No variable substitution — these are static tool locations you copy."""
import json
from flask import Blueprint, render_template, request, jsonify
from app import store

bp = Blueprint("tool_library", __name__)
FILE = store.DATA / "tool_library.json"


MODDIR = __import__("pathlib").Path(__file__).resolve().parent
STD = MODDIR / "standard.json"


def _std():
    try:
        return json.loads(STD.read_text()).get("tools", [])
    except Exception:
        return []


def load():
    """Standard tools are always injected first, then the user's own additions.
    Deleting a standard entry in-app will not stick — it returns on reload."""
    user = []
    if FILE.exists():
        try:
            d = json.loads(FILE.read_text())
            if isinstance(d, dict) and isinstance(d.get("tools"), list):
                user = d["tools"]
        except Exception:
            pass
    seen, out = set(), []
    for t in _std() + user:
        name = str(t.get("name", "")).strip()
        key = name.lower()
        if not name or key in seen:
            continue
        seen.add(key)
        out.append({"name": name, "path": str(t.get("path", "")).strip()})
    return {"tools": out}


def save(d):
    FILE.write_text(json.dumps(d, indent=2))
    return d


@bp.route("/toollibrary")
def index():
    return render_template("tool_library.html", active="tool_library", data=load())


@bp.route("/api/tool-library", methods=["GET", "POST"])
def api():
    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}
        clean = []
        for t in data.get("tools", []):
            name = str(t.get("name", "")).strip()
            path = str(t.get("path", "")).strip()
            if name and path:
                clean.append({"name": name, "path": path})
        return jsonify(ok=True, data=save({"tools": clean}))
    return jsonify(load())


MODULE = {"id": "tool_library", "title": "Tool Library", "category": "Libraries",
          "order": 1, "blueprint": bp, "endpoint": "tool_library.index"}
