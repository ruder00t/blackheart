from flask import Blueprint, render_template, request, jsonify

from app import store

bp = Blueprint("home", __name__)


@bp.route("/")
def index():
    return render_template("home.html", active="home")


@bp.route("/api/vars", methods=["POST"])
def save_vars():
    data = request.get_json(force=True, silent=True) or {}
    return jsonify(ok=True, vars=store.save(data))


MODULE = {
    "id": "home", "title": "Variables & home", "category": "Engagement",
    "order": 0, "blueprint": bp, "endpoint": "home.index",
}
