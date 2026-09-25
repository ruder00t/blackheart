"""Blackheart - offline pentest kit. Flask app factory."""
from flask import Flask

from . import registry, store


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB scan uploads

    # discover and register every module under app/modules/, build the nav
    registry.discover(app)

    # integrated tmux terminal + "send to terminal" (localhost-only routes)
    from app.terminal import term_bp
    app.register_blueprint(term_bp)

    # Optionally refresh the version DB cache at startup. OFF by default: an
    # "offline" tool must not beacon to ~30 public registries on every boot
    # (opsec leak on an engagement box). The "Update now" button in VersionCheck
    # still works on demand. Set BH_VERSIONCHECK_STARTUP=1 to restore auto-refresh.
    import os
    if os.environ.get("BH_VERSIONCHECK_STARTUP", "0").lower() \
            in ("1", "true", "yes", "on"):
        try:
            from app.modules.versioncheck import kick_startup_refresh
            kick_startup_refresh(app)
        except Exception:
            pass

    @app.context_processor
    def _inject():
        # available in every template: sidebar nav, saved variables, field defs,
        # and the user's additions overlay (injected onto target tabs by app.js)
        from app.modules.additions import load as load_additions
        return {
            "nav": app.config.get("NAV", []),
            "gvars": store.load(),
            "varfields": store.VARFIELDS,
            "additions": load_additions(),
        }

    @app.route("/api/backup/export")
    def backup_export():
        import glob, json, os
        from flask import Response
        from app import store
        bundle = {}
        for f in sorted(glob.glob(str(store.DATA / "*.json"))):
            name = os.path.splitext(os.path.basename(f))[0]
            try:
                bundle[name] = json.loads(open(f).read())
            except Exception:
                pass
        body = json.dumps({"_blackheart_backup": 1, "data": bundle}, indent=2)
        return Response(body, mimetype="application/json",
                        headers={"Content-Disposition": "attachment; filename=blackheart-backup.json"})

    @app.route("/api/backup/import", methods=["POST"])
    def backup_import():
        import json, re
        from flask import request, jsonify
        from app import store
        # Reject cross-site requests: this route writes files to data/, so a
        # drive-by page must not be able to POST to it. Sec-Fetch-Site is
        # browser-set and unforgeable by JS; Origin is the fallback; a
        # non-browser client (no fetch-metadata) is not a CSRF vector.
        _allowed = {"http://127.0.0.1:8090", "http://localhost:8090",
                    "http://[::1]:8090"}
        _sfs = request.headers.get("Sec-Fetch-Site")
        if _sfs is not None:
            if _sfs not in ("same-origin", "same-site", "none"):
                return jsonify(ok=False, error="cross-site"), 403
        else:
            _origin = request.headers.get("Origin")
            if _origin is not None and _origin not in _allowed:
                return jsonify(ok=False, error="cross-site"), 403
        if not request.is_json:
            return jsonify(ok=False, error="json required"), 415
        payload = request.get_json(silent=True) or {}
        data = payload.get("data") if isinstance(payload, dict) and "data" in payload else payload
        if not isinstance(data, dict):
            return jsonify(ok=False, error="invalid backup file"), 400
        written = []
        for name, content in data.items():
            if not re.match(r"^[A-Za-z0-9_-]+$", str(name)):
                continue  # guard against path traversal
            try:
                (store.DATA / (name + ".json")).write_text(json.dumps(content, indent=2))
                written.append(name)
            except Exception:
                pass
        return jsonify(ok=True, written=written)

    @app.route("/api/search-index")
    def search_index():
        from flask import url_for, jsonify
        from app.search import build_index
        out = []
        for e in build_index():
            try:
                url = url_for(e["e"])
            except Exception:
                url = "#"
            out.append({"c": e["c"], "tab": e["tab"], "url": url, "t": e["t"]})
        return jsonify(out)

    return app
