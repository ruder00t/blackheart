"""GTFOBins (offline). Landing tab with Update + Open buttons.

Update downloads the upstream repo and rebuilds a single static page into
app/static/gtfobins/. Open launches it in a new tab. Fully offline once built;
network is touched only on Update, which soft-fails to a status message.
"""
from pathlib import Path

from flask import Blueprint, render_template, current_app

from app import store
from app.core import offlinedocs as od
from . import build as builder

bp = Blueprint("gtfobins", __name__)
STATUS = store.DATA / "gtfobins_status.json"


def _out_dir():
    return Path(current_app.static_folder) / "gtfobins"


def _built():
    return (_out_dir() / "index.html").exists()


def _view(status=None):
    return render_template(
        "offlinedoc.html", active="gtfobins", title="GTFOBins", tag="privesc",
        blurb="Unix binaries that can be abused to bypass local security restrictions. "
              "Build once (needs network), then browse and search it fully offline.",
        built=_built(), open_url="/static/gtfobins/index.html",
        update_endpoint="gtfobins.update",
        status=status or od.read_status(STATUS) or od.default_status("GTFOBins"))


@bp.route("/gtfobins")
def index():
    return _view()


@bp.route("/gtfobins/update", methods=["POST"])
def update():
    try:
        count = builder.build(_out_dir())
        status = {"last_update": od.now(), "count": count,
                  "message": "built %d binaries" % count}
    except Exception:
        status = od.read_status(STATUS) or od.default_status("GTFOBins")
        status["message"] = ("update failed \u2014 no connection to GitHub "
                             + ("(existing build kept)" if _built() else "(nothing built yet)"))
    od.write_status(STATUS, status)
    return _view(status)


MODULE = {"id": "gtfobins", "title": "GTFOBins", "category": "Privilege Escalation",
          "order": 10, "blueprint": bp, "endpoint": "gtfobins.index"}
