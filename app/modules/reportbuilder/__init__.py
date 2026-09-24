"""Report Builder (Additions).

Turns a CPTS-style report.md into a themed PDF via the bundled engine
(pandoc -> HTML/CSS -> WeasyPrint). Colours, font, font colour and logo are set
here and persisted; three ways to feed the source: upload a .md, point at a
folder on disk, or upload a .md+images zip. Images resolve/embed from the base
directory, so absolute local paths and (with a base dir) relative paths both
work.

pandoc + WeasyPrint are heavy, external, and optional: they're imported/checked
lazily so the rest of Blackheart runs without them, and the tab shows an install
hint when they're absent.
"""
import glob
import os
import re
import shutil
import tempfile
import zipfile
from importlib.util import find_spec
from pathlib import Path

from flask import (Blueprint, render_template, request, send_file, redirect,
                   url_for, Response)
from werkzeug.utils import secure_filename

from app import store
from . import engine

bp = Blueprint("reportbuilder", __name__)

MOD = Path(__file__).resolve().parent
STATE = store.DATA / "reportbuilder.json"
LOGODIR = store.DATA / "reportbuilder"

DEFAULTS = {
    "accent": "#f2811d", "accent_strong": "#ff9d45", "page": "#1c1e22",
    "surface": "#2a2e34", "ink": "#e6e8ea", "muted": "#99a2ad",
    "critical": "#9e1b28", "high": "#e03131", "medium": "#ffb224",
    "low": "#4899e8", "info": "#8b949e",
    "font": "Carlito, 'Liberation Sans', sans-serif", "logo": "",
}

_HEX = re.compile(r"^#[0-9A-Fa-f]{3,8}$")
_FONT_OK = re.compile(r"^[\w ,'\"\-]+$")


def deps():
    return {"pandoc": bool(shutil.which("pandoc")),
            "weasyprint": bool(find_spec("weasyprint"))}


def load_state():
    import json
    s = dict(DEFAULTS)
    if STATE.exists():
        try:
            s.update({k: v for k, v in json.loads(STATE.read_text()).items() if k in DEFAULTS})
        except Exception:
            pass
    return s


def save_state(s):
    import json
    STATE.write_text(json.dumps(s, indent=2))


def style_override(s):
    varmap = {
        "--accent": s["accent"], "--accent-strong": s["accent_strong"],
        "--page": s["page"], "--surface": s["surface"], "--ink": s["ink"],
        "--muted": s["muted"], "--critical": s["critical"], "--high": s["high"],
        "--medium": s["medium"], "--low": s["low"], "--info": s["info"],
    }
    root = ";".join("%s:%s" % (k, v) for k, v in varmap.items() if _HEX.match(str(v)))
    font = s.get("font", "")
    css = ":root{%s}" % root
    if _FONT_OK.match(font):
        css += "body,.report-body{font-family:%s !important}" % font
    return css


def chart_colours(s):
    return {"Critical": s["critical"], "High": s["high"], "Medium": s["medium"],
            "Low": s["low"], "Info": s["info"]}


def logo_path(s):
    if s.get("logo"):
        p = LOGODIR / s["logo"]
        if p.exists():
            return p
    return None


def _view(error=None, built_note=None):
    return render_template("reportbuilder.html", active="reportbuilder",
                           deps=deps(), s=load_state(), error=error,
                           built_note=built_note)


@bp.route("/reportbuilder")
def index():
    return _view()


@bp.route("/reportbuilder/example")
def example():
    return send_file(MOD / "example" / "report.md", as_attachment=True,
                     download_name="report.md", mimetype="text/markdown")


@bp.route("/reportbuilder/style", methods=["POST"])
def style():
    s = load_state()
    for k in DEFAULTS:
        if k in ("logo",):
            continue
        if request.form.get(k):
            s[k] = request.form.get(k).strip()
    logo = request.files.get("logo")
    if logo and logo.filename:
        LOGODIR.mkdir(parents=True, exist_ok=True)
        name = "logo" + os.path.splitext(secure_filename(logo.filename))[1].lower()
        logo.save(LOGODIR / name)
        s["logo"] = name
    if request.form.get("clear_logo"):
        s["logo"] = ""
    save_state(s)
    return redirect(url_for("reportbuilder.index"))


def _resolve_source(work):
    """Return (md_path, base_dir, dl_name) from whichever input was given, or
    raise ValueError with a user-facing message."""
    zf = request.files.get("zip")
    md = request.files.get("md")
    disk = (request.form.get("base_dir") or "").strip()
    md_name = (request.form.get("md_name") or "report.md").strip()

    if zf and zf.filename:
        src = work / "src"
        src.mkdir()
        zpath = work / secure_filename(zf.filename)
        zf.save(zpath)
        with zipfile.ZipFile(zpath) as z:
            z.extractall(src)
        mds = sorted(glob.glob(str(src / "**" / "*.md"), recursive=True))
        pref = [m for m in mds if os.path.basename(m).lower() == "report.md"]
        if not mds:
            raise ValueError("no .md found inside the zip")
        chosen = Path(pref[0] if pref else mds[0])
        return chosen, chosen.parent, chosen.stem + ".pdf"

    if md and md.filename:
        dest = work / "report.md"
        md.save(dest)
        base = Path(disk) if disk else work
        if disk and not base.is_dir():
            raise ValueError("image base directory does not exist: %s" % disk)
        return dest, base, Path(secure_filename(md.filename)).stem + ".pdf"

    if disk:
        base = Path(disk)
        if not base.is_dir():
            raise ValueError("directory does not exist: %s" % disk)
        mp = base / md_name
        if not mp.is_file():
            raise ValueError("no %s in %s" % (md_name, disk))
        return mp, base, mp.stem + ".pdf"

    raise ValueError("give a .md upload, a folder path, or a zip")


@bp.route("/reportbuilder/build", methods=["POST"])
def build():
    d = deps()
    if not (d["pandoc"] and d["weasyprint"]):
        return _view(error="pandoc and/or WeasyPrint are not installed \u2014 run install.sh")

    work = Path(tempfile.mkdtemp(prefix="bh_report_"))
    try:
        md_path, base, dl_name = _resolve_source(work)
        s = load_state()
        out = work / "report.pdf"
        engine.build(md_path, out, base_dir=base,
                     style_override=style_override(s),
                     chart_colours=chart_colours(s),
                     logo_override=logo_path(s))
        data = out.read_bytes()
        return Response(data, mimetype="application/pdf", headers={
            "Content-Disposition": 'attachment; filename="%s"' % dl_name})
    except ValueError as e:
        return _view(error=str(e))
    except Exception as e:
        msg = str(e).strip().splitlines()[-1] if str(e).strip() else e.__class__.__name__
        return _view(error="build failed: %s" % msg)
    finally:
        shutil.rmtree(work, ignore_errors=True)


MODULE = {"id": "reportbuilder", "title": "Report Builder", "category": "Additions",
          "order": -1, "blueprint": bp, "endpoint": "reportbuilder.index"}
