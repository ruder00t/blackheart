"""Engagement variables: one shared set, persisted to data/vars.json.

VARFIELDS is the single source of truth. Add a (key, label, default) tuple and
the home form, the vars.json schema, and live substitution all pick it up.
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent   # project root
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)
VARS_FILE = DATA / "vars.json"

VARFIELDS = [
    ("RHOST", "Target host", "10.10.10.10"),
    ("RPORT", "Target port", "80"),
    ("LHOST", "Attacker host", "10.10.14.5"),
    ("LPORT", "Attacker port", "4444"),
    ("DOMAIN", "Domain", ""),
    ("USER", "Username", ""),
    ("PASS", "Password", ""),
    ("USERLIST", "Username list", "/usr/share/seclists/Usernames/top-usernames-shortlist.txt"),
    ("PASSLIST", "Password list", "/usr/share/wordlists/rockyou.txt"),
    ("WORDLIST", "Wordlist", "/usr/share/seclists/Discovery/Web-Content/common.txt"),
    ("OUT", "Output dir", "./loot"),
    # --- Active Directory ---
    ("NTHASH", "NT hash", ""),
    ("SID", "Domain SID", ""),
    ("CA", "ADCS CA name", ""),
    ("TEMPLATE", "Cert template", ""),
    ("TARGET", "Target object", ""),
]


def defaults():
    return {k: d for k, _, d in VARFIELDS}


def load():
    d = defaults()
    if VARS_FILE.exists():
        try:
            saved = json.loads(VARS_FILE.read_text())
            for k in d:
                if k in saved:
                    d[k] = str(saved[k])
        except Exception:
            pass
    return d


def save(incoming):
    d = defaults()
    for k in d:
        if k in incoming:
            d[k] = str(incoming[k])
    VARS_FILE.write_text(json.dumps(d, indent=2))
    return d
