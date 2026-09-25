from flask import Blueprint, render_template

bp = Blueprint("wordlists", __name__)

# Copyable paths. Counts are approximate (Kali/SecLists defaults). tpl = path.
CARDS = [
    {"title": "Passwords", "hint": "Point $PASSLIST at one of these.", "blocks": [
        {"tpl": "/usr/share/wordlists/rockyou.txt", "lbl": "rockyou (~14M)"},
        {"tpl": "/usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-1000.txt", "lbl": "top-1000 (~1k)"},
        {"tpl": "/usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-100000.txt", "lbl": "top-100k (~100k)"},
        {"tpl": "/usr/share/seclists/Passwords/darkweb2017-top10000.txt", "lbl": "darkweb2017 (~10k)"},
        {"tpl": "/usr/share/seclists/Passwords/Default-Credentials/default-passwords.txt", "lbl": "default passwords (~2k)"},
    ]},
    {"title": "Usernames", "hint": "Point $USERLIST at one of these.", "blocks": [
        {"tpl": "/usr/share/seclists/Usernames/top-usernames-shortlist.txt", "lbl": "shortlist (~17)"},
        {"tpl": "/usr/share/seclists/Usernames/Names/names.txt", "lbl": "names (~10k)"},
        {"tpl": "/usr/share/seclists/Usernames/xato-net-10-million-usernames.txt", "lbl": "xato 10M (~8.9M)"},
    ]},
    {"title": "Web content / directories", "hint": "Point $WORDLIST here for ffuf/gobuster/feroxbuster.", "blocks": [
        {"tpl": "/usr/share/seclists/Discovery/Web-Content/common.txt", "lbl": "common (~4.7k)"},
        {"tpl": "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt", "lbl": "dirbuster medium (~220k)"},
        {"tpl": "/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt", "lbl": "dirbuster small (~87k)"},
        {"tpl": "/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt", "lbl": "raft medium dirs (~30k)"},
        {"tpl": "/usr/share/seclists/Discovery/Web-Content/raft-large-words.txt", "lbl": "raft large words (~62k)"},
        {"tpl": "/usr/share/seclists/Discovery/Web-Content/big.txt", "lbl": "big (~20k)"},
    ]},
    {"title": "Files & extensions", "blocks": [
        {"tpl": "/usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt", "lbl": "raft medium files (~17k)"},
        {"tpl": "/usr/share/seclists/Discovery/Web-Content/web-extensions.txt", "lbl": "web extensions (~40)"},
        {"tpl": "/usr/share/seclists/Discovery/Web-Content/raft-medium-extensions.txt", "lbl": "raft medium ext (~2.5k)"},
        {"tpl": "/usr/share/seclists/Discovery/Web-Content/CommonBackdoors-PHP.fuzz.txt", "lbl": "php backdoors (~50)"},
    ]},
    {"title": "DNS / subdomains", "blocks": [
        {"tpl": "/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt", "lbl": "top-5k subs (~5k)"},
        {"tpl": "/usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt", "lbl": "top-110k subs (~110k)"},
        {"tpl": "/usr/share/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt", "lbl": "bitquark top-100k (~100k)"},
        {"tpl": "/usr/share/seclists/Discovery/DNS/namelist.txt", "lbl": "namelist (~150k)"},
    ]},
    {"title": "API / parameters", "blocks": [
        {"tpl": "/usr/share/seclists/Discovery/Web-Content/api/api-endpoints.txt", "lbl": "api endpoints (~1.7k)"},
        {"tpl": "/usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt", "lbl": "param names (~2.5k)"},
    ]},
    {"title": "Fuzzing payloads", "blocks": [
        {"tpl": "/usr/share/seclists/Fuzzing/LFI/LFI-Jhaddix.txt", "lbl": "LFI Jhaddix (~900)"},
        {"tpl": "/usr/share/seclists/Fuzzing/XSS/XSS-Jhaddix.txt", "lbl": "XSS Jhaddix (~2.7k)"},
        {"tpl": "/usr/share/seclists/Fuzzing/SQLi/Generic-SQLi.txt", "lbl": "SQLi generic (~250)"},
    ]},
    {"title": "Get SecLists (if missing)", "blocks": [
        {"tpl": "sudo apt install seclists", "lbl": "kali / debian"},
        {"tpl": "git clone https://github.com/danielmiessler/SecLists /usr/share/seclists", "lbl": "from source"},
        {"tpl": "sudo gunzip -k /usr/share/wordlists/rockyou.txt.gz", "lbl": "unpack rockyou"},
    ]},
]


@bp.route("/wordlists")
def index():
    return render_template("cheat.html", active="wordlists",
                           title="Wordlists", tag="engagement",
                           intro="Common wordlist paths (approx counts in parentheses). Copy a path straight into $WORDLIST / $USERLIST / $PASSLIST on the variables page.",
                           cards=CARDS)


MODULE = {"id": "wordlists", "title": "Wordlists", "category": "Engagement",
          "order": 1, "blueprint": bp, "endpoint": "wordlists.index"}
