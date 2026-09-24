"""Nmap command builder (offline). Interactive: pick scan type, ports, timing,
discovery, NSE and output — get a ready nmap command wired to $RHOST. Assembly
runs client-side in static/js/nmap.js. Sits at the top of Recon.
"""
from flask import Blueprint, render_template

bp = Blueprint("nmapbuilder", __name__)


@bp.route("/nmap-builder")
def index():
    return render_template("nmapbuilder.html", active="nmapbuilder")


MODULE = {"id": "nmapbuilder", "title": "Nmap builder", "category": "Recon",
          "order": -1, "blueprint": bp, "endpoint": "nmapbuilder.index"}
