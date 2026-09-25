"""Active Directory playbook.

A structured, tabbed attack path (No creds -> Valid user -> Admin -> Post-exploit
-> Trusts -> Persistence) built from the YAML tree in data/. Commands are wired
to the shared engagement variables and rendered as live .cmd blocks by app.js.

Structure and technique coverage follow the Orange Cyberdefense AD mindmap
(v2025.03, GPLv3). A local copy of that mindmap opens from the tab header.
"""
import os

import yaml
from flask import Blueprint, render_template

from . import render as pb

bp = Blueprint("activedirectory", __name__)

MOD = os.path.dirname(__file__)
DATA = os.path.join(MOD, "data")

# order of the top tabs (creds spine)
TAB_ORDER = ["nocreds", "user", "admin", "postexploit", "trusts", "persistence"]


def load_tabs():
    tabs = {}
    for fn in sorted(os.listdir(DATA)):
        if not fn.endswith((".yaml", ".yml")):
            continue
        with open(os.path.join(DATA, fn)) as fh:
            d = yaml.safe_load(fh)
        if d and d.get("tab"):
            tabs[d["tab"]] = d
    ordered = [tabs[k] for k in TAB_ORDER if k in tabs]
    ordered += [v for k, v in tabs.items() if k not in TAB_ORDER]
    return ordered


@bp.route("/activedirectory")
def index():
    seg, panels = pb.render_panels(load_tabs())
    return render_template(
        "adplaybook.html", active="activedirectory",
        title="Active Directory", tag="exploitation",
        intro="Domain attack path, tabbed by the access you hold. netexec (nxc) + "
              "impacket + BloodHound + certipy. Structure mirrors the OCD AD mindmap.",
        seg=seg, panels=panels,
        mindmap_url="/static/activedirectory/mindmap_ad.svg")


MODULE = {"id": "activedirectory", "title": "Active Directory",
          "category": "Exploitation", "order": 5,
          "blueprint": bp, "endpoint": "activedirectory.index"}
