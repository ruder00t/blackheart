"""
Route parsed ports to modules.

Only 'open' ports are routed to modules. Anything with a non-open state
(filtered, open|filtered, ...) is set aside into `filtered` so the HTML can
list it without generating a checklist for an unreachable port.

Resolution order for open ports:
  1. service name (and aliases) in routing.services
  2. port number in routing.ports
  3. unsupported (named vs unrecognized)

TLS per port: nmap-reported tls flag OR port in routing.tls_ports.
"""


def _is_open(state):
    return state == "open"


def route(hosts, routing):
    services = {k.lower(): v for k, v in routing.get("services", {}).items()}
    ports_map = {str(k): v for k, v in routing.get("ports", {}).items()}
    tls_ports = set(routing.get("tls_ports", []))

    out = []
    for h in hosts:
        assignments, unk_known, unk_unknown, filtered = [], [], [], []
        for p in h["ports"]:
            if not _is_open(p.get("state")):
                filtered.append(p)
                continue
            svc = (p.get("service") or "").lower()
            module = services.get(svc) or ports_map.get(str(p["port"]))
            tls = bool(p.get("tls")) or p["port"] in tls_ports
            if module:
                assignments.append({
                    "port": p["port"], "tls": tls, "module": module,
                    "service": p.get("service", ""),
                    "product": p.get("product", ""),
                    "version": p.get("version", ""),
                })
            elif svc:
                unk_known.append(p)
            else:
                unk_unknown.append(p)
        out.append({
            "ip": h["ip"], "hostname": h.get("hostname", ""),
            "assignments": assignments,
            "unsupported_known": unk_known,
            "unsupported_unknown": unk_unknown,
            "filtered": filtered,
        })
    return out
