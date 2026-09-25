"""Module registry.

Auto-discovers packages under app/modules/ that define a MODULE dict, registers
their blueprint, and builds the sidebar nav. Supports:
  - categories (CATEGORY_ORDER)
  - subgroups within a category (MODULE["group"], e.g. "Privilege Escalation")
  - greyed, non-clickable placeholders (PLACEHOLDERS) for tools not built yet

MODULE = {"id","title","category","order","blueprint","endpoint", "group"?}
"""
import importlib
import pkgutil

CATEGORY_ORDER = [
    "Engagement", "Recon", "Exploitation", "Access",
    "Privilege Escalation", "Post-exploit", "Reference",
    "Libraries", "Additions",
]

# non-clickable, greyed placeholders: (category, title, order, group)
PLACEHOLDERS = [
]


def _sortkey(x):
    return (x["order"], x["title"])


def discover(app):
    import app.modules as pkg

    metas = []
    for m in pkgutil.iter_modules(pkg.__path__):
        mod = importlib.import_module("app.modules." + m.name)
        meta = getattr(mod, "MODULE", None)
        if not meta:
            continue
        app.register_blueprint(meta["blueprint"])
        metas.append(meta)

    cats = {}

    def add(category, item):
        sec = cats.setdefault(category, {"entries": [], "groups": {}})
        if item.get("group"):
            sec["groups"].setdefault(item["group"], []).append(item)
        else:
            sec["entries"].append(item)

    for meta in metas:
        add(meta["category"], {
            "id": meta["id"], "title": meta["title"], "endpoint": meta["endpoint"],
            "order": meta.get("order", 100), "group": meta.get("group"), "soon": False,
            "blank": meta.get("blank", False),
        })
    for category, title, order, group in PLACEHOLDERS:
        add(category, {"id": None, "title": title, "endpoint": None,
                       "order": order, "group": group, "soon": True})

    ordered = [c for c in CATEGORY_ORDER if c in cats] + \
              [c for c in cats if c not in CATEGORY_ORDER]

    nav = []
    for c in ordered:
        sec = cats[c]
        sec["entries"].sort(key=_sortkey)
        groups = []
        for gname, gitems in sec["groups"].items():
            gitems.sort(key=_sortkey)
            groups.append((gname, gitems))
        groups.sort(key=lambda g: min(i["order"] for i in g[1]))
        nav.append((c, {"entries": sec["entries"], "groups": groups}))

    app.config["NAV"] = nav
    return metas
