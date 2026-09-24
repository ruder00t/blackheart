"""Global search index.

Walks every module's static content (CARDS / SHELLS / TABS) plus the CheckMap
service YAMLs and flattens it into a list of searchable command entries. Built
once and cached; served to the client by the /api/search-index route.
"""
import glob
import importlib
import pkgutil

import yaml

_INDEX = None


def _add(out, text, cmd, tab, endpoint):
    cmd = (cmd or "").strip()
    text = (text or "").strip()
    if not cmd:
        return
    out.append({"t": text, "c": cmd, "tab": tab, "e": endpoint})


def _index_cards(out, cards, title, endpoint):
    for c in cards or []:
        ct = c.get("title", "") or ""
        hint = c.get("hint", "") or ""
        for b in c.get("blocks", []):
            tpl = b.get("tpl", "") or b.get("cmd", "")
            lbl = b.get("lbl", "") or ""
            _add(out, " ".join([tpl, lbl, ct, hint]), tpl, title, endpoint)


def build_index():
    global _INDEX
    if _INDEX is not None:
        return _INDEX
    out = []
    import app.modules as pkg
    for m in pkgutil.iter_modules(pkg.__path__):
        try:
            mod = importlib.import_module("app.modules." + m.name)
        except Exception:
            continue
        meta = getattr(mod, "MODULE", None)
        if not meta:
            continue
        title, endpoint = meta["title"], meta["endpoint"]
        _index_cards(out, getattr(mod, "CARDS", None), title, endpoint)
        for s in getattr(mod, "SHELLS", None) or []:
            _add(out, s.get("name", "") + " reverse shell", s.get("cmd", ""), title, endpoint)
        for tab in getattr(mod, "TABS", None) or []:
            # TABS entries are (key, label, cards)
            try:
                _, label, cards = tab
                _index_cards(out, cards, title + " · " + label, endpoint)
            except Exception:
                pass

    # Active Directory playbook commands (tabbed YAML tree)
    for f in sorted(glob.glob("app/modules/activedirectory/data/*.yaml")):
        try:
            d = yaml.safe_load(open(f))
        except Exception:
            continue
        if not d:
            continue
        ttl = d.get("title", "AD")
        for sec in d.get("sections", []):
            sname = sec.get("name", "") or ""
            for st in sec.get("steps", []):
                text = st.get("text", "") or ""
                for c in (st.get("cmds") or []):
                    cmd = c.get("c", "") if isinstance(c, dict) else str(c)
                    cmd = cmd.strip()
                    if cmd and not cmd.startswith("#"):
                        _add(out, cmd + " " + text + " " + sname,
                             cmd, "Active Directory \u00b7 " + ttl,
                             "activedirectory.index")

    # CheckMap service commands
    for f in sorted(glob.glob("app/modules/checkmap/data/*.yaml")):
        if f.endswith("routing.yaml"):
            continue
        try:
            d = yaml.safe_load(open(f))
        except Exception:
            continue
        if not d:
            continue
        name = d.get("name", "")
        for sec in d.get("sections", []):
            for st in sec.get("steps", []):
                text = st.get("text", "") or ""
                for line in (st.get("commands", "") or "").split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        _add(out, line + " " + text + " " + name,
                             line, "CheckMap · " + name, "checkmap.index")

    # de-dupe on (command, tab)
    seen, dedup = set(), []
    for e in out:
        k = (e["c"], e["tab"])
        if k in seen:
            continue
        seen.add(k)
        dedup.append(e)
    _INDEX = dedup
    return dedup
