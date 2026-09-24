"""LOLBAS (offline). Landing tab with Update + Open buttons.

Update downloads the upstream repo and rebuilds a single static page into
app/static/lolbas/. Open launches it in a new tab. Fully offline once built;
network is touched only on Update, which soft-fails to a status message.
"""
from pathlib import Path

from flask import Blueprint, render_template, current_app

from app import store
from app.core import offlinedocs as od
from . import build as builder

bp = Blueprint("lolbas", __name__)
STATUS = store.DATA / "lolbas_status.json"


def _out_dir():
    return Path(current_app.static_folder) / "lolbas"


def _built():
    return (_out_dir() / "index.html").exists()


def _view(status=None):
    return render_template(
        "offlinedoc.html", active="lolbas", title="LOLBAS", tag="privesc",
        blurb="Living-off-the-land Windows binaries, scripts and libraries with legitimate "
              "functions abusable by attackers. Build once (needs network), then browse offline.",
        built=_built(), open_url="/static/lolbas/index.html",
        update_endpoint="lolbas.update",
        status=status or od.read_status(STATUS) or od.default_status("LOLBAS"))


@bp.route("/lolbas")
def index():
    return _view()


@bp.route("/lolbas/update", methods=["POST"])
def update():
    try:
        count = builder.build(_out_dir())
        status = {"last_update": od.now(), "count": count,
                  "message": "built %d binaries" % count}
    except Exception:
        status = od.read_status(STATUS) or od.default_status("LOLBAS")
        status["message"] = ("update failed \u2014 no connection to GitHub "
                             + ("(existing build kept)" if _built() else "(nothing built yet)"))
    od.write_status(STATUS, status)
    return _view(status)


MODULE = {"id": "lolbas", "title": "LOLBAS", "category": "Privilege Escalation",
          "order": 11, "blueprint": bp, "endpoint": "lolbas.index"}
