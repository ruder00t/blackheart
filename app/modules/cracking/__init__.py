from flask import Blueprint, render_template

bp = Blueprint("cracking", __name__)

CARDS = [
    {"title": "hashcat — most used", "hint": "-m mode, -a attack. $PASSLIST from your variables.", "blocks": [
        {"tpl": "hashcat -m <mode> hash.txt $PASSLIST", "lbl": "straight dictionary (-a 0 default)"},
        {"tpl": "hashcat -m <mode> hash.txt $PASSLIST -r /usr/share/hashcat/rules/best64.rule", "lbl": "dict + rules"},
        {"tpl": "hashcat -m <mode> hash.txt -a 3 '?u?l?l?l?l?d?d'", "lbl": "mask / brute (-a 3)"},
        {"tpl": "hashcat -m <mode> hash.txt $PASSLIST --show", "lbl": "show cracked"},
        {"tpl": "hashcat -m <mode> hash.txt $PASSLIST --username", "lbl": "hashes prefixed with user:"},
        {"tpl": "hashcat --identify hash.txt", "lbl": "guess the mode"},
        {"tpl": "hashcat -m <mode> hash.txt $PASSLIST -O -w 3", "lbl": "optimised + high workload"},
    ]},
    {"title": "hashcat — common modes", "blocks": [
        {"tpl": "0=MD5  100=SHA1  1400=SHA256  1700=SHA512", "plain": True},
        {"tpl": "1000=NTLM  5600=NetNTLMv2  5500=NetNTLMv1", "plain": True},
        {"tpl": "1800=sha512crypt($6$)  500=md5crypt($1$)  3200=bcrypt", "plain": True},
        {"tpl": "13100=Kerberoast TGS  18200=AS-REP", "plain": True},
        {"tpl": "22000=WPA-PBKDF2/PMKID  16800=WPA-PMKID(old)", "plain": True},
        {"tpl": "1000=NTLM  13000=RAR5  12500=RAR3  13600=ZIP  11600=7-Zip", "plain": True},
        {"tpl": "22921=RSA/DSA/EC/OpenSSH key  1731=MSSQL2012+  112=Oracle11g", "plain": True},
    ]},
    {"title": "John the Ripper — most used", "hint": "Auto-detects format; override with --format.", "blocks": [
        {"tpl": "john --wordlist=$PASSLIST hash.txt"},
        {"tpl": "john --wordlist=$PASSLIST --rules hash.txt", "lbl": "with mangling rules"},
        {"tpl": "john --format=<fmt> --wordlist=$PASSLIST hash.txt"},
        {"tpl": "john --show hash.txt", "lbl": "show cracked"},
        {"tpl": "john --incremental hash.txt", "lbl": "brute (no wordlist)"},
        {"tpl": "john --list=formats | tr ',' '\\n' | grep -i <kw>", "lbl": "find a format"},
    ]},
    {"title": "*2john — extract a crackable hash", "hint": "Convert a file/artifact into a hash John & hashcat can eat.", "blocks": [
        {"tpl": "ssh2john id_rsa > id_rsa.hash", "lbl": "SSH private key  (hashcat -m 22921)"},
        {"tpl": "zip2john file.zip > zip.hash", "lbl": "ZIP  (-m 13600)"},
        {"tpl": "rar2john file.rar > rar.hash", "lbl": "RAR  (-m 13000/12500)"},
        {"tpl": "7z2john file.7z > 7z.hash", "lbl": "7-Zip  (-m 11600)"},
        {"tpl": "office2john file.docx > office.hash", "lbl": "Office docs  (-m 9400+)"},
        {"tpl": "pdf2john file.pdf > pdf.hash", "lbl": "PDF  (-m 10500+)"},
        {"tpl": "keepass2john file.kdbx > kp.hash", "lbl": "KeePass  (-m 13400)"},
        {"tpl": "gpg2john file.gpg > gpg.hash", "lbl": "GPG key"},
        {"tpl": "bitlocker2john -i drive.img > bl.hash", "lbl": "BitLocker  (-m 22100)"},
        {"tpl": "keytab2john file.keytab > kt.hash", "lbl": "Kerberos keytab"},
    ]},
    {"title": "Wordlist prep & rules", "blocks": [
        {"tpl": "sudo gunzip -k /usr/share/wordlists/rockyou.txt.gz", "lbl": "unpack rockyou"},
        {"tpl": "cewl -d 2 -m 5 -w custom.txt http://$RHOST", "lbl": "scrape a site for words"},
        {"tpl": "hashcat --stdout $PASSLIST -r best64.rule > mutated.txt", "lbl": "pre-mutate a list"},
        {"tpl": "/usr/share/hashcat/rules/ : best64, d3ad0ne, dive, OneRuleToRuleThemAll", "plain": True, "lbl": "rule files"},
    ]},
    {"title": "Custom username lists — username-anarchy", "hint": "Turn real names into likely account names, then feed $USERLIST.", "blocks": [
        {"tpl": "./username-anarchy Firstname Lastname", "lbl": "permute one name to stdout"},
        {"tpl": "./username-anarchy -i names.txt > users.txt", "lbl": "bulk from a names file (space/CSV/TAB)"},
        {"tpl": "./username-anarchy -f first.last,flast,firstl Firstname Lastname", "lbl": "only chosen formats"},
        {"tpl": "./username-anarchy -l", "lbl": "list available format plugins"},
        {"tpl": "git clone https://github.com/urbanadventurer/username-anarchy", "lbl": "install"},
    ]},
    {"title": "Custom password lists — CUPP", "hint": "Profile a target from personal details into a targeted $PASSLIST.", "blocks": [
        {"tpl": "cupp -i", "lbl": "interactive profile (name, dates, pet, ...)"},
        {"tpl": "cupp -w existing.txt", "lbl": "improve/extend an existing list"},
        {"tpl": "cupp -l", "lbl": "fetch bundled wordlists"},
        {"tpl": "cupp -a", "lbl": "default creds from the Alecto DB"},
        {"tpl": "git clone https://github.com/Mebus/cupp", "lbl": "install (or: apt install cupp)"},
    ]},
    {"title": "Identify a hash", "blocks": [
        {"tpl": "hashid '<hash>'"},
        {"tpl": "nth --text '<hash>'", "lbl": "name-that-hash"},
        {"tpl": "hashcat --identify hash.txt"},
    ]},
]


@bp.route("/cracking")
def index():
    return render_template("cheat.html", active="cracking",
                           title="Cracking", tag="reference",
                           intro="Offline password / hash cracking: hashcat, John, and the *2john extractors. Identify the hash, pick the mode, point it at $PASSLIST.",
                           cards=CARDS)


MODULE = {"id": "cracking", "title": "Cracking", "category": "Reference",
          "order": 8, "blueprint": bp, "endpoint": "cracking.index"}
