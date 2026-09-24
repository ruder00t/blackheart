"""
Render the AD playbook YAML tree into HTML that lives inside the Blackheart shell.

Output is a set of tab panels (one per creds-spine level). Each panel holds
collapsible technique sections; each step is a normal .cmd[data-tpl] block, so
the shared app.js handles live $VAR substitution and copy buttons — nothing
here duplicates that logic.

Flag badges (small, coloured) annotate steps: creds level (nocreds/user/admin),
cve, opsec (loud), win (Windows-only host), tool, manual. Unknown flags render
as a neutral badge.
"""
import html

# label shown on each badge; class suffix is the flag key itself
FLAG_LABELS = {
    "nocreds": "NO CREDS",
    "user": "USER",
    "admin": "ADMIN",
    "cve": "CVE",
    "opsec": "LOUD",
    "win": "WINDOWS",
    "tool": "TOOL",
    "manual": "MANUAL",
}


def _esc(s):
    return html.escape("" if s is None else str(s))


def _cmd_block(entry):
    """entry: str, or {c, lbl?, plain?}. Emits a .cmd[data-tpl] div (app.js fills it)."""
    if isinstance(entry, dict):
        tpl = entry.get("c", "")
        lbl = entry.get("lbl", "")
        plain = entry.get("plain", False)
    else:
        tpl, lbl, plain = str(entry), "", False
    # comment-only lines read better as plain (no leading $ prompt)
    if tpl.strip().startswith("#"):
        plain = True
    cls = "cmd plain" if plain else "cmd"
    lbl_html = '<span class="lbl">%s</span>' % _esc(lbl) if lbl else ""
    # data-tpl carries the raw template; app.js does fill + copy on render
    return '<div class="%s" data-tpl="%s">%s</div>' % (
        cls, _esc(tpl), lbl_html)


def _flags(flags):
    if not flags:
        return ""
    out = ""
    for f in flags:
        key = str(f).lower()
        label = FLAG_LABELS.get(key, key.upper())
        out += '<span class="pb-flag pb-flag-%s">%s</span>' % (_esc(key), _esc(label))
    return '<span class="pb-flags">%s</span>' % out


def _step(step):
    text = _esc(step.get("text", ""))
    flags = _flags(step.get("flags"))
    cmds = "".join(_cmd_block(c) for c in (step.get("cmds") or []))
    return ('<div class="pb-step"><div class="pb-step-head">%s%s</div>%s</div>'
            % (text, flags, cmds))


def _section(sec):
    steps = "".join(_step(s) for s in (sec.get("steps") or []))
    if not steps:
        return ""
    n = len(sec.get("steps") or [])
    hint = ('<p class="hint pb-hint">%s</p>' % _esc(sec["hint"])) if sec.get("hint") else ""
    return (
        '<details class="pb-sec">'
        '<summary>%s <span class="count">(%d)</span></summary>'
        '%s%s</details>'
    ) % (_esc(sec.get("name", "")), n, hint, steps)


def render_panels(tabs):
    """tabs: ordered list of tab dicts {tab,title,blurb,sections}. Returns
    (seg_buttons_html, panels_html) for the template."""
    seg, panels = "", ""
    for i, t in enumerate(tabs):
        on = " class=\"on\"" if i == 0 else ""
        seg += '<button type="button" data-tab="%s"%s>%s</button>' % (
            _esc(t["tab"]), on, _esc(t["title"]))
        body = ""
        if t.get("blurb"):
            body += '<p class="pb-blurb">%s</p>' % _esc(t["blurb"])
        body += "".join(_section(s) for s in (t.get("sections") or []))
        hidden = "" if i == 0 else " hidden"
        panels += '<div class="tabpanel" data-tab="%s"%s>%s</div>' % (
            _esc(t["tab"]), hidden, body)
    return seg, panels
