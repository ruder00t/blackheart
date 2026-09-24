"""Day0: per-OS setup notes / commands (ParrotOS, Kali, Windows).

User-managed entries persisted to data/day0.json. Entries may contain $VAR
placeholders that substitute live, and each renders as a copyable block.
"""
import json

from flask import Blueprint, render_template, request, jsonify

from app import store

bp = Blueprint("day0", __name__)
FILE = store.DATA / "day0.json"

OSES = [("parrot", "ParrotOS"), ("kali", "Kali"), ("windows", "Windows")]


def load():
    base = {k: [] for k, _ in OSES}
    if FILE.exists():
        try:
            d = json.loads(FILE.read_text())
            for k, _ in OSES:
                if isinstance(d.get(k), list):
                    base[k] = [str(x) for x in d[k] if str(x).strip()]
        except Exception:
            pass
    return base


def save(incoming):
    clean = {}
    for k, _ in OSES:
        clean[k] = [str(x) for x in (incoming.get(k) or []) if str(x).strip()]
    FILE.write_text(json.dumps(clean, indent=2))
    return clean


@bp.route("/day0")
def index():
    return render_template("day0.html", active="day0",
                           day0=load(), oses=OSES,
                           varkeys=[k for k, _, _ in store.VARFIELDS])


@bp.route("/api/day0", methods=["GET", "POST"])
def api():
    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}
        return jsonify(ok=True, day0=save(data))
    return jsonify(load())


MODULE = {"id": "day0", "title": "Day0 (Fresh-OS)", "category": "Reference",
          "order": 10, "blueprint": bp, "endpoint": "day0.index"}
