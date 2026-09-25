"""
Render one host's routed assignments into a single self-contained HTML file.
CSS/JS are inlined so the file works when opened directly from disk (file://).
"""
import html
import os

from app.core import substitute

_TPL_DIR = os.path.join(os.path.dirname(__file__), "templates")


def _read(name):
    with open(os.path.join(_TPL_DIR, name), "r") as fh:
        return fh.read()


def _commands_block(cmd_text):
    """cmd_text is a block scalar (newline-separated). Return list of commands,
    dropping blank lines but keeping comment lines (# ...)."""
    out = []
    for line in cmd_text.splitlines():
        s = line.strip()
        if s:
            out.append(s)
    return out


def _render_step(step, ctx, uid):
    flags = ""
    if step.get("manual"):
        flags += '<span class="flag manual">MANUAL</span>'
    if step.get("authorized"):
        flags += '<span class="flag authorized">AUTHORIZED</span>'
    text = html.escape(step["text"])

    cmds = _commands_block(step.get("commands", "") or "")
    cmd_html = ""
    if cmds:
        rows = ""
        for c in cmds:
            filled = substitute.fill(c, ctx)
            esc = html.escape(filled)
            rows += (
                '<div class="cmd"><code>%s</code>'
                '<button title="copy">copy</button></div>' % esc
            )
        cmd_html = (
            '<button class="cmd-toggle">&#9656; show commands</button>'
            '<div class="cmds">%s</div>' % rows
        )

    return (
        '<div class="step" data-id="%s">'
        '<div class="step-head">'
        '<div class="cb" title="click: check / cross / clear"></div>'
        '<div class="step-text">%s<span class="flags">%s</span></div>'
        '</div>%s</div>'
    ) % (html.escape(uid), text, flags, cmd_html)


def _render_section(section, ctx, tls, prefix):
    # skip TLS-only sections on non-TLS ports
    if section.get("tls_only") and not tls:
        return ""
    steps_html = ""
    n = 0
    sect_authorized = section.get("authorized", False)
    for step in section["steps"]:
        if step.get("tls_only") and not tls:
            continue
        merged = dict(step)
        if sect_authorized:
            merged["authorized"] = True
        uid = "%s:%s:%s" % (prefix, section["id"], step["id"])
        steps_html += _render_step(merged, ctx, uid)
        n += 1
    if not steps_html:
        return ""
    return (
        '<details class="section" open>'
        '<summary>%s <span class="count">(%d)</span></summary>'
        '%s</details>'
    ) % (html.escape(section["name"]), n, steps_html)


def _render_service(module, assignment, ctx):
    port = assignment["port"]
    tls = assignment["tls"]
    scheme = "https" if tls else "http"
    prefix = "%s-%d-%s" % (module["module"], port, scheme)
    sections_html = ""
    for section in module["sections"]:
        only = section.get("only_ports")
        if only and port not in only:
            continue
        sections_html += _render_section(section, ctx, tls, prefix)
    if not sections_html:
        return ""
    svc_label = assignment.get("service") or module["module"]
    ver = " ".join(x for x in (assignment.get("product"),
                               assignment.get("version")) if x)
    tag = "%s %s" % (svc_label, ver) if ver else svc_label
    return (
        '<details class="svc" open>'
        '<summary>%s <span class="tag">:%d &middot; %s</span>'
        '<span class="pill %s">%s</span></summary>'
        '%s</details>'
    ) % (html.escape(module["name"]), port, html.escape(tag),
         scheme, scheme.upper(), sections_html)


def _banner(title, cls, ports, note=""):
    if not ports:
        return ""
    items = ""
    for p in ports:
        desc = p.get("service") or "unknown"
        extra = " ".join(x for x in (p.get("product"), p.get("version")) if x)
        line = "%d/%s  %s%s" % (p["port"], p.get("proto", "tcp"), desc,
                                (" — " + extra) if extra else "")
        items += "<li>%s</li>" % html.escape(line)
    note_html = ('<p class="note">%s</p>' % html.escape(note)) if note else ""
    return ('<div class="banner %s"><h3>%s</h3>%s<ul>%s</ul></div>'
            % (cls, html.escape(title), note_html, items))


def render_host(host_route, modules, run_ns, meta=None, project=None):
    """host_route: one entry from router.route(). modules: {id: module_dict}.
    project: dict of project-wide variables from information.yaml (DOMAIN, WL, ...)."""
    css = _read("style.css")
    js = _read("app.js")
    ip = host_route["ip"] or "target"
    hostname = host_route.get("hostname", "")
    project = project or {}

    body = ""
    body += _banner(
        "\u26a0 Open ports NOT covered by CheckMap \u2014 enumerate manually",
        "known", host_route["unsupported_known"],
        note="Service was named but CheckMap has no checklist for it. "
             "These are not included below \u2014 identify the version and test them by hand.")
    body += _banner(
        "\u26a0 Open ports with UNKNOWN service \u2014 identify manually",
        "unknown", host_route["unsupported_unknown"],
        note="nmap could not name these. Not included below \u2014 fingerprint the port "
             "and test them by hand.")
    body += _banner(
        "Filtered / unreachable \u2014 skipped", "filtered",
        host_route.get("filtered", []),
        note="Not open from your position; no checklist generated.")

    for a in host_route["assignments"]:
        module = modules.get(a["module"])
        if not module:
            continue
        # project-wide vars first, then per-module meta overrides, then host facts.
        # both win: nothing is excluded; anything unfilled stays a placeholder.
        extra = dict(project)
        extra.update((meta or {}).get(a["module"], {}))
        if hostname:
            extra.setdefault("HOST", hostname)
            extra.setdefault("DOMAIN", hostname)
        ctx = substitute.build_context(a["ip"] if a.get("ip") else host_route["ip"],
                                       a["port"], a["tls"], extra)
        body += _render_service(module, a, ctx)


    title = "Blackheart — %s" % (hostname or ip)
    target = html.escape(hostname or ip)
    header_meta = "Target: %s" % target
    if hostname and ip:
        header_meta = "Target: %s &middot; %s" % (html.escape(hostname), ip)
    if meta and meta.get("_generated"):
        header_meta += " &middot; %s" % html.escape(meta["_generated"])

    return """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title><style>%s</style></head>
<body>
<header><h1>Black<span class="brand-map">heart</span></h1><div class="meta">%s</div></header>
<div class="wrap">
<div class="controls">
<button id="expandAll">Expand all</button>
<button id="collapseAll">Collapse all</button>
<button id="reset">Reset progress</button>
<span class="progress" id="progress"></span>
</div>
%s
</div>
<script>window.__RUN_NS__=%r;</script>
<script>%s</script>
</body></html>""" % (html.escape(title), css,
                     header_meta, body, run_ns, js)
