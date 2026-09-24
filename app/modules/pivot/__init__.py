from flask import Blueprint, render_template

bp = Blueprint("pivot", __name__)


@bp.route("/pivot")
def index():
    return render_template("pivot.html", active="pivot")


MODULE = {
    "id": "pivot", "title": "Pivoting", "category": "Post-exploit",
    "order": 0, "blueprint": bp, "endpoint": "pivot.index",
}
