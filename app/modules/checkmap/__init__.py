"""CheckMap module.

Two ways to build a per-host checklist, both fed by the shared engagement
variables and rendered by the same engine (app.core parser/router + render.py):
  - upload an nmap scan (xml / grepable / normal)
  - manual: pick supported ports as chips and generate against $RHOST
"""
import os
import re
import tempfile
from pathlib import Path

import yaml
from flask import (Blueprint, render_template, request, redirect, url_for,
                   send_from_directory, abort)

from app import store
from app.core import parser as nmap_parser
from app.core import router as router_mod
from . import render as ck

bp = Blueprint("checkmap", __name__)

MOD = Path(__file__).resolve().parent
DATA = MOD / "data"
OUT = store.DATA / "checkmap"


def load_routing():
    with open(DATA / "routing.yaml") as fh:
        return yaml.safe_load(fh)


def load_modules():
    mods = {}
    for fn in sorted(os.listdir(DATA)):
        if fn == "routing.yaml" or not fn.endswith((".yaml", ".yml")):
            continue
        with open(DATA / fn) as fh:
            m = yaml.safe_load(fh)
        if m and m.get("module"):
            mods[m["module"]] = m
    return mods


def project_ctx():
    p = {k: v for k, v in store.load().items() if v}
    if p.get("WORDLIST"):
        p.setdefault("WL", p["WORDLIST"])
    return p


def safe(ip):
    return re.sub(r"[^A-Za-z0-9._-]", "_", ip or "target")


def manual_groups():
    """Supported ports grouped by service module, for the manual chips."""
    ports = load_routing().get("ports", {})
    groups = {}
    for port, module in ports.items():
        groups.setdefault(module, []).append(int(port))
    return sorted(((m, sorted(ps)) for m, ps in groups.items()), key=lambda x: x[0])


def _write_host(host_route):
    ipdir = OUT / safe(host_route["ip"])
    ipdir.mkdir(parents=True, exist_ok=True)
    ns = "blackheart:%s" % safe(host_route["ip"])
    html = ck.render_host(host_route, load_modules(), ns, None, project_ctx())
    (ipdir / "checklist.html").write_text(html, encoding="utf-8")


def _existing():
    if not OUT.exists():
        return []
    return sorted(d.name for d in OUT.iterdir() if (d / "checklist.html").exists())


@bp.route("/checkmap", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        f = request.files.get("scan")
        if not f or not f.filename:
            error = "Choose a scan file."
        else:
            suffix = os.path.splitext(f.filename)[1] or ".xml"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            f.save(tmp.name)
            tmp.close()
            try:
                hosts = nmap_parser.parse(tmp.name)
            finally:
                try:
                    os.unlink(tmp.name)
                except OSError:
                    pass
            if not hosts:
                error = "No open ports parsed. Use nmap -sV -oX (XML preferred)."
            else:
                for hr in router_mod.route(hosts, load_routing()):
                    _write_host(hr)
                return redirect(url_for("checkmap.index"))

    return render_template("checkmap.html", active="checkmap",
                           outputs=_existing(), manual_groups=manual_groups(),
                           error=error)


@bp.route("/checkmap/manual", methods=["POST"])
def manual():
    ip = (request.form.get("ip") or "").strip() or "target"
    selected = request.form.getlist("ports")
    routing = load_routing()
    pmap = {str(k): v for k, v in routing.get("ports", {}).items()}
    tls_ports = set(routing.get("tls_ports", []))
    project = project_ctx()

    assignments = []
    for ps in selected:
        try:
            port = int(ps)
        except ValueError:
            continue
        module = pmap.get(str(port))
        if not module:
            continue
        assignments.append({
            "port": port, "tls": port in tls_ports, "module": module,
            "service": module, "product": "", "version": "",
        })

    if assignments:
        _write_host({
            "ip": ip, "hostname": project.get("DOMAIN", ""),
            "assignments": assignments,
            "unsupported_known": [], "unsupported_unknown": [], "filtered": [],
        })
    return redirect(url_for("checkmap.index"))


@bp.route("/checkmap/view/<ip>")
def view(ip):
    d = OUT / safe(ip)
    if not (d / "checklist.html").exists():
        abort(404)
    return send_from_directory(d, "checklist.html")


MODULE = {"id": "checkmap", "title": "CheckMap", "category": "Recon",
          "order": 0, "blueprint": bp, "endpoint": "checkmap.index"}
