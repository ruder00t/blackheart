"""JWT debugger (offline). Decode / verify / sign JSON Web Tokens in-browser.

All crypto runs client-side via the Web Crypto API (see static/js/jwt.js) — no
token or key ever leaves the machine. Sits under Decode in the Reference group.
"""
from flask import Blueprint, render_template

bp = Blueprint("jwt", __name__)


@bp.route("/jwt")
def index():
    return render_template("jwt.html", active="jwt")


MODULE = {"id": "jwt", "title": "JWT", "category": "Reference",
          "order": 21, "blueprint": bp, "endpoint": "jwt.index"}
