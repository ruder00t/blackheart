"""
Parse nmap output into a normalized structure. Accepts, in order of reliability:
  1. nmap XML  (-oX)   -- richest: service names, product/version, ssl tunnel
  2. nmap grepable (-oG)
  3. nmap normal (-oN) / any text listing PORT STATE SERVICE
Extension is ignored; content is sniffed.

Output: list[Host], where Host = {ip, hostname, ports: [Port]}
Port = {port:int, proto:str, state:str, service:str, product:str,
        version:str, tls:bool, source:str}

State is preserved verbatim (open / filtered / open|filtered / closed...).
The router decides what to do with each state; the parser keeps anything
that is not plainly 'closed' so filtered ports can be surfaced.
"""
import re
import xml.etree.ElementTree as ET


def _keep(state):
    """Keep open and filtered-ish states; drop closed."""
    return state and state != "closed"


def parse(path):
    with open(path, "r", errors="replace") as fh:
        raw = fh.read()
    stripped = raw.lstrip()
    if stripped.startswith("<?xml") or "<nmaprun" in stripped[:2000]:
        try:
            return _parse_xml(raw)
        except ET.ParseError:
            pass
    if re.search(r"^Host:\s.*Ports:", raw, re.M):
        return _parse_grepable(raw)
    return _parse_normal(raw)


def _tls_from(service, extra=""):
    s = (service or "").lower()
    return s.startswith(("https", "ssl/")) or "ssl" in (extra or "").lower()


def _parse_xml(raw):
    root = ET.fromstring(raw)
    hosts = []
    for h in root.findall("host"):
        st = h.find("status")
        if st is not None and st.get("state") == "down":
            continue
        ip = ""
        for addr in h.findall("address"):
            if addr.get("addrtype") in ("ipv4", "ipv6"):
                ip = addr.get("addr")
                break
        hostname = ""
        hn = h.find("hostnames/hostname")
        if hn is not None:
            hostname = hn.get("name", "")
        ports = []
        for p in h.findall("ports/port"):
            state_el = p.find("state")
            state = state_el.get("state") if state_el is not None else ""
            if not _keep(state):
                continue
            svc = p.find("service")
            service = svc.get("name", "") if svc is not None else ""
            product = svc.get("product", "") if svc is not None else ""
            version = svc.get("version", "") if svc is not None else ""
            tunnel = svc.get("tunnel", "") if svc is not None else ""
            tls = tunnel == "ssl" or _tls_from(service)
            ports.append({
                "port": int(p.get("portid")), "proto": p.get("protocol", "tcp"),
                "state": state, "service": service, "product": product,
                "version": version, "tls": tls, "source": "xml",
            })
        if ports:
            hosts.append({"ip": ip, "hostname": hostname, "ports": ports})
    return hosts


def _parse_grepable(raw):
    hosts = []
    for line in raw.splitlines():
        m = re.match(r"Host:\s+(\S+).*?Ports:\s+(.*)", line)
        if not m:
            continue
        ip, portblob = m.group(1), m.group(2)
        ports = []
        for chunk in portblob.split(","):
            f = chunk.strip().split("/")
            if len(f) < 3 or not _keep(f[1]):
                continue
            service = f[4] if len(f) > 4 else ""
            product = f[6] if len(f) > 6 else ""
            ports.append({
                "port": int(f[0]), "proto": f[2], "state": f[1],
                "service": service, "product": product, "version": "",
                "tls": _tls_from(service, chunk), "source": "grepable",
            })
        if ports:
            hosts.append({"ip": ip, "hostname": "", "ports": ports})
    return hosts


def _parse_normal(raw):
    blocks = re.split(r"(?=Nmap scan report for )", raw)
    hosts = []
    for blk in blocks:
        m = re.search(r"Nmap scan report for (\S+)(?:\s+\(([\d.]+)\))?", blk)
        if m:
            name, ip = m.group(1), m.group(2)
            if ip is None:
                ip, hostname = name, ""
            else:
                hostname = name
        else:
            ip, hostname = "", ""
        ports = _extract_port_lines(blk)
        if ports:
            hosts.append({"ip": ip, "hostname": hostname, "ports": ports})
    return hosts


# port/proto  STATE  service  version...   (STATE may be 'open' or 'open|filtered' etc.)
_PORT_LINE = re.compile(
    r"^(\d+)/(tcp|udp)[ \t]+(\S+)[ \t]+(\S+)?[ \t]*([^\n]*)$", re.M)


def _extract_port_lines(text):
    ports = []
    for m in _PORT_LINE.finditer(text):
        port, proto, state, service, rest = m.groups()
        if not _keep(state):
            continue
        service = service or ""
        ports.append({
            "port": int(port), "proto": proto, "state": state,
            "service": service, "product": rest.strip(), "version": "",
            "tls": _tls_from(service), "source": "normal",
        })
    return ports
