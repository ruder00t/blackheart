"""CVSS v3.1 calculator (Base + Temporal).

Client-side scoring — official v3.1 formula in static/js/cvss.js. Produces the
score, severity rating and the CVSS vector string for pasting into a report.
Sits just above the Report Builder in the Additions group.
"""
from flask import Blueprint, render_template

bp = Blueprint("cvss", __name__)


@bp.route("/cvss")
def index():
    return render_template("cvss.html", active="cvss", title="CVSS Calculator",
                           tag="v3.1")


MODULE = {"id": "cvss", "title": "CVSS Calculator", "category": "Additions",
          "order": -2, "blueprint": bp, "endpoint": "cvss.index"}
