"""HackTricks (offline). Landing tab with Update + Open buttons.

Update downloads the upstream HackTricks Markdown as an HTTPS tarball and renders
it into a single, themed, browsable static site under app/static/hacktricks/ (no
git, no mdBook; needs python-markdown + pygments). Open launches it in a new tab.
Fully offline once built; network is touched only on Update, which soft-fails to
a status message and leaves any existing build untouched.
"""
from pathlib import Path

from flask import Blueprint, render_template, current_app

from app import store
from app.core import offlinedocs as od
from . import build as builder

bp = Blueprint("hacktricks", __name__)
STATUS = store.DATA / "hacktricks_status.json"


def _out_dir():
    return Path(current_app.static_folder) / "hacktricks"


def _built():
    return (_out_dir() / "index.html").exists()


def _view(status=None):
    return render_template(
        "offlinedoc.html", active="hacktricks", title="HackTricks", tag="reference",
        blurb="The HackTricks wiki as a fully offline, themed, searchable static site. "
              "Build once (needs network and python-markdown), then browse it with no connection.",
        built=_built(), open_url="/static/hacktricks/index.html",
        update_endpoint="hacktricks.update", unit="pages",
        status=status or od.read_status(STATUS) or od.default_status("HackTricks"))


@bp.route("/hacktricks")
def index():
    return _view()


@bp.route("/hacktricks/update", methods=["POST"])
def update():
    try:
        count = builder.build(_out_dir())
        status = {"last_update": od.now(), "count": count,
                  "message": "built %d pages" % count}
    except Exception as e:
        status = od.read_status(STATUS) or od.default_status("HackTricks")
        if "markdown" in str(e).lower():
            status["message"] = ("update failed \u2014 python-markdown not installed "
                                 "(pip install markdown pygments)")
        else:
            status["message"] = ("update failed \u2014 no connection to GitHub "
                                 + ("(existing build kept)" if _built() else "(nothing built yet)"))
    od.write_status(STATUS, status)
    return _view(status)


MODULE = {"id": "hacktricks", "title": "HackTricks", "category": "Reference",
          "order": 5, "blueprint": bp, "endpoint": "hacktricks.index"}
