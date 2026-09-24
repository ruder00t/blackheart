"""Command Obfuscator (offline). Take one command, emit encoded/obfuscated forms
for filter/WAF bypass and constrained shells. All transforms run client-side in
static/js/cmdobf.js. Sits under Decode in the Reference group.
"""
from flask import Blueprint, render_template

bp = Blueprint("cmdobf", __name__)


@bp.route("/cmdobf")
def index():
    return render_template("cmdobf.html", active="cmdobf")


MODULE = {"id": "cmdobf", "title": "Cmd Obfuscator", "category": "Reference",
          "order": 22, "blueprint": bp, "endpoint": "cmdobf.index"}
