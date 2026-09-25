"""Decode (offline). Landing tab with Update + Open buttons.

Bundles CyberChef (GCHQ's cyber swiss-army knife, Apache-2.0): bases, hex, URL,
XOR/ROT/Vigenere with brute-forcers, Morse, dozens of hashes, AES/DES/RC4, and
the "Magic" auto-detect. A committed copy ships under app/static/decode/, so
Open works with zero network from first run. Update re-fetches the latest
CyberChef release and rebuilds; it soft-fails to a status message and leaves the
existing build in place.
"""
import re
from pathlib import Path

from flask import Blueprint, render_template, current_app

from app import store
from app.core import offlinedocs as od
from . import build as builder

bp = Blueprint("decode", __name__)
STATUS = store.DATA / "decode_status.json"


def _out_dir():
    return Path(current_app.static_folder) / "decode"


def _built():
    return (_out_dir() / "index.html").exists()


def _shipped_version():
    try:
        html = (_out_dir() / "index.html").read_text(errors="ignore")
        m = re.search(r"/blob/v([0-9][0-9A-Za-z.\-]*)/", html)
        return m.group(1) if m else None
    except Exception:
        return None


def _status():
    """Recorded status, or a synthesized one for the committed build."""
    st = od.read_status(STATUS)
    if st is not None:
        return st
    if _built():
        ver = _shipped_version()
        return {"last_update": None, "count": 0,
                "message": ("bundled CyberChef%s ready \u2014 Update (needs network) "
                            "to refresh to the latest release")
                           % (" v" + ver if ver else "")}
    return od.default_status("Decode")


def _view(status=None):
    return render_template(
        "decode.html", active="decode", title="Decode", tag="crypto",
        blurb="Encryption and decryption \u2014 a full offline CyberChef build. "
              "Bases, hex, URL, XOR/ROT/Vigen\u00e8re (with brute-force), Morse, "
              "hashes, AES/DES/RC4 and the \u201cMagic\u201d auto-detect. Ships built; "
              "Update (needs network) refreshes it to the latest release.",
        built=_built(), open_url="/static/decode/index.html",
        update_endpoint="decode.update", unit="files",
        status=status or _status())


@bp.route("/decode")
def index():
    return _view()


@bp.route("/decode/update", methods=["POST"])
def update():
    try:
        count, version = builder.build(_out_dir())
        status = {"last_update": od.now(), "count": count,
                  "message": "built CyberChef v%s" % version}
    except Exception:
        status = od.read_status(STATUS) or od.default_status("Decode")
        status["message"] = ("update failed \u2014 no connection to GitHub "
                             + ("(existing build kept)" if _built() else "(nothing built yet)"))
    od.write_status(STATUS, status)
    return _view(status)


MODULE = {"id": "decode", "title": "Decode", "category": "Reference",
          "order": 20, "blueprint": bp, "endpoint": "decode.index"}
