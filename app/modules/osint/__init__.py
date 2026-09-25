"""OSINT tab (Engagement).

Three sub-tabs to start — Tools, Websites, Image — with more to come. Entries
are one of three kinds and render accordingly:
  - {"link": "https://...", "name": "...", "note": "..."}  clickable, opens new tab
  - {"cmd": "...", "lbl": "..."}                            copyable command ($VARS fill)
  - {"text": "..."}                                         plain technique note
Cards group related entries under a heading.
"""
import html

from flask import Blueprint, render_template

bp = Blueprint("osint", __name__)


# --------------------------------------------------------------------- data
TOOLS = [
    {"title": "Domains / infra / subdomains", "blocks": [
        {"link": "https://github.com/laramies/theHarvester", "name": "theHarvester",
         "note": "emails, subdomains, hosts from public sources"},
        {"cmd": "theHarvester -d $DOMAIN -b all", "lbl": "run against a domain"},
        {"link": "https://github.com/owasp-amass/amass", "name": "OWASP Amass",
         "note": "in-depth attack-surface / subdomain mapping"},
        {"cmd": "amass enum -d $DOMAIN", "lbl": "passive+active enum"},
        {"link": "https://github.com/projectdiscovery/subfinder", "name": "subfinder",
         "note": "fast passive subdomain discovery"},
        {"cmd": "subfinder -d $DOMAIN -all -silent", "lbl": "all sources"},
        {"link": "https://github.com/s0md3v/Photon", "name": "Photon",
         "note": "OSINT-oriented web crawler (emails, keys, files)"},
        {"cmd": "photon -u https://$DOMAIN -o loot_photon", "lbl": "crawl a site"},
    ]},
    {"title": "Usernames / accounts", "blocks": [
        {"link": "https://github.com/sherlock-project/sherlock", "name": "Sherlock",
         "note": "hunt a username across social networks"},
        {"cmd": "sherlock <username>", "lbl": "single username"},
        {"link": "https://github.com/soxoj/maigret", "name": "Maigret",
         "note": "like Sherlock, more sites + HTML/PDF report"},
        {"cmd": "maigret <username> --html", "lbl": "report output"},
    ]},
    {"title": "Emails / breaches", "blocks": [
        {"link": "https://github.com/megadose/holehe", "name": "holehe",
         "note": "which sites an email is registered on (no password reset sent)"},
        {"cmd": "holehe <email>", "lbl": "check an address"},
        {"link": "https://github.com/khast3x/h8mail", "name": "h8mail",
         "note": "breach / leaked-credential hunting for an email"},
        {"cmd": "h8mail -t <email>", "lbl": "search breaches"},
        {"link": "https://github.com/mxrch/GHunt", "name": "GHunt",
         "note": "Google account OSINT from an email / gaia ID"},
        {"cmd": "ghunt email <email>", "lbl": "profile a Google account"},
    ]},
    {"title": "Phone numbers", "blocks": [
        {"link": "https://github.com/sundowndev/phoneinfoga", "name": "PhoneInfoga",
         "note": "footprint a phone number (carrier, area, footprints)"},
        {"cmd": "phoneinfoga scan -n <number>", "lbl": "scan a number"},
    ]},
    {"title": "Code / secrets leaks", "blocks": [
        {"link": "https://github.com/trufflesecurity/trufflehog", "name": "TruffleHog",
         "note": "find verified secrets in git repos / orgs"},
        {"cmd": "trufflehog github --org=<org>", "lbl": "scan an org"},
        {"link": "https://github.com/gitleaks/gitleaks", "name": "Gitleaks",
         "note": "detect hardcoded secrets in a repo"},
        {"cmd": "gitleaks detect -s <repo_dir> -v", "lbl": "scan a checkout"},
    ]},
    {"title": "Frameworks / automation", "blocks": [
        {"link": "https://github.com/smicallef/spiderfoot", "name": "SpiderFoot",
         "note": "automated OSINT with 200+ modules, web UI"},
        {"cmd": "python3 sf.py -l 127.0.0.1:5001", "lbl": "start the web UI"},
        {"link": "https://github.com/lanmaster53/recon-ng", "name": "recon-ng",
         "note": "modular recon framework (Metasploit-style workflow)"},
        {"cmd": "recon-ng", "lbl": "launch console"},
    ]},
    {"title": "Social media profiling", "blocks": [
        {"link": "https://github.com/Datalux/Osintgram", "name": "Osintgram",
         "note": "Instagram: followers, emails, phones, tagged locations"},
        {"link": "https://github.com/megadose/toutatis", "name": "Toutatis",
         "note": "Instagram: obfuscated email/phone from a profile"},
    ]},
]

WEBSITES = [
    {"title": "Starting points", "blocks": [
        {"link": "https://osintframework.com/", "name": "OSINT Framework",
         "note": "categorised directory of OSINT resources"},
        {"link": "https://inteltechniques.com/tools/", "name": "IntelTechniques Tools",
         "note": "Michael Bazzell's search tool collection"},
    ]},
    {"title": "Host / device search engines", "blocks": [
        {"link": "https://www.shodan.io/", "name": "Shodan",
         "note": "internet-exposed hosts, banners, ICS/IoT"},
        {"link": "https://search.censys.io/", "name": "Censys Search",
         "note": "hosts + certificates, strong for TLS pivoting"},
        {"link": "https://www.zoomeye.org/", "name": "ZoomEye",
         "note": "alternative host/service search engine"},
        {"link": "https://fofa.info/", "name": "FOFA",
         "note": "asset search, good favicon/body queries"},
        {"link": "https://viz.greynoise.io/", "name": "GreyNoise",
         "note": "is this IP scanning the whole internet or targeting you"},
    ]},
    {"title": "Emails / breaches / people", "blocks": [
        {"link": "https://haveibeenpwned.com/", "name": "Have I Been Pwned",
         "note": "is an email in a known breach"},
        {"link": "https://www.dehashed.com/", "name": "DeHashed",
         "note": "breach search across emails/usernames/hashes (paid)"},
        {"link": "https://intelx.io/", "name": "Intelligence X",
         "note": "leaks, pastes, darkweb, historical data"},
        {"link": "https://hunter.io/", "name": "Hunter.io",
         "note": "company email addresses + patterns"},
        {"link": "https://whatsmyname.app/", "name": "WhatsMyName",
         "note": "username enumeration across sites (web)"},
    ]},
    {"title": "Domain / DNS / certs", "blocks": [
        {"link": "https://crt.sh/", "name": "crt.sh",
         "note": "certificate transparency -> subdomains"},
        {"link": "https://dnsdumpster.com/", "name": "DNSDumpster",
         "note": "DNS recon + network map"},
        {"link": "https://securitytrails.com/", "name": "SecurityTrails",
         "note": "historical DNS / WHOIS"},
        {"link": "https://viewdns.info/", "name": "ViewDNS.info",
         "note": "reverse IP, WHOIS, DNS toolset"},
        {"link": "https://urlscan.io/", "name": "urlscan.io",
         "note": "what a URL loads, screenshots, indicators"},
        {"link": "https://www.virustotal.com/", "name": "VirusTotal",
         "note": "files/URLs/domains reputation + relations"},
        {"link": "https://builtwith.com/", "name": "BuiltWith",
         "note": "tech stack fingerprint of a site"},
        {"link": "https://web.archive.org/", "name": "Wayback Machine",
         "note": "historical snapshots of pages / files"},
    ]},
    {"title": "Companies / registries", "blocks": [
        {"link": "https://opencorporates.com/", "name": "OpenCorporates",
         "note": "company registrations worldwide"},
        {"link": "https://www.linkedin.com/", "name": "LinkedIn",
         "note": "employees, roles -> username lists (feed Cracking)"},
        {"link": "https://wigle.net/", "name": "WiGLE",
         "note": "wardriving DB: SSID/BSSID -> geolocation"},
    ]},
]

IMAGE = [
    {"title": "Reverse image search", "hint": "Run the same image through several — each indexes different sources.", "blocks": [
        {"link": "https://lens.google.com/", "name": "Google Lens",
         "note": "objects, text, products, some places"},
        {"link": "https://yandex.com/images/", "name": "Yandex Images",
         "note": "best for faces and places / buildings"},
        {"link": "https://tineye.com/", "name": "TinEye",
         "note": "find where an exact image appears (oldest match)"},
        {"link": "https://www.bing.com/visualsearch", "name": "Bing Visual Search",
         "note": "another distinct index worth checking"},
        {"link": "https://pimeyes.com/", "name": "PimEyes",
         "note": "face search across the web (use responsibly)"},
        {"link": "http://karmadecay.com/", "name": "Karma Decay",
         "note": "reverse search within Reddit"},
    ]},
    {"title": "Metadata / EXIF", "blocks": [
        {"cmd": "exiftool <image>", "lbl": "extract all metadata (GPS, device, timestamps)"},
        {"cmd": "exiftool -gpslatitude -gpslongitude -createdate <image>", "lbl": "just location + time"},
        {"link": "https://jimpl.com/", "name": "Jimpl",
         "note": "online EXIF + map view, no install"},
        {"link": "https://www.metadata2go.com/", "name": "Metadata2Go",
         "note": "browser metadata viewer for many formats"},
    ]},
    {"title": "Forensics / manipulation", "blocks": [
        {"link": "https://fotoforensics.com/", "name": "FotoForensics",
         "note": "Error Level Analysis for edited regions"},
        {"link": "https://29a.ch/photo-forensics/", "name": "Forensically",
         "note": "clone detection, ELA, noise, magnifier"},
        {"link": "https://github.com/GuidoBartoli/sherloq", "name": "Sherloq",
         "note": "open-source image forensics toolset"},
        {"link": "https://github.com/beurtschipper/Depix", "name": "Depix",
         "note": "recover text from pixelated screenshots"},
    ]},
    {"title": "Geolocation techniques", "blocks": [
        {"text": "Read the frame: language on signs, licence-plate style, road markings, power-pole and outlet types, vegetation and climate all narrow the country/region."},
        {"text": "Use shadows for direction and rough time; cross-check with SunCalc for a candidate date/location."},
        {"text": "Pin candidate spots in Google Earth, then confirm with Street View / Mapillary imagery of the exact corner."},
        {"link": "https://www.suncalc.org/", "name": "SunCalc",
         "note": "sun position / shadow direction by place + time"},
        {"link": "https://earth.google.com/", "name": "Google Earth",
         "note": "3D terrain, historical imagery, measure"},
        {"link": "https://www.mapillary.com/", "name": "Mapillary",
         "note": "crowd-sourced street-level imagery (fills Street View gaps)"},
        {"link": "https://wikimapia.org/", "name": "Wikimapia",
         "note": "crowd-labelled places / landmarks"},
    ]},
]

TABS = [("tools", "Tools", TOOLS), ("websites", "Websites", WEBSITES),
        ("image", "Image", IMAGE)]


# ------------------------------------------------------------------- render
def _esc(s):
    return html.escape("" if s is None else str(s))


def _block(b):
    if "link" in b:
        note = ' <span class="osint-note">%s</span>' % _esc(b["note"]) if b.get("note") else ""
        return ('<div class="osint-item"><a class="osint-link" href="%s" target="_blank" '
                'rel="noopener">%s <span class="ext">&#8599;</span></a>%s</div>'
                % (_esc(b["link"]), _esc(b.get("name") or b["link"]), note))
    if "cmd" in b:
        lbl = '<span class="lbl">%s</span>' % _esc(b["lbl"]) if b.get("lbl") else ""
        return '<div class="cmd" data-tpl="%s">%s</div>' % (_esc(b["cmd"]), lbl)
    if "text" in b:
        return '<p class="osint-tech">%s</p>' % _esc(b["text"])
    return ""


def _card(card):
    hint = '<p class="hint">%s</p>' % _esc(card["hint"]) if card.get("hint") else ""
    body = "".join(_block(b) for b in card.get("blocks", []))
    title = '<h3>%s</h3>' % _esc(card["title"]) if card.get("title") else ""
    return '<div class="card">%s%s%s</div>' % (title, hint, body)


def render_panels():
    seg, panels = "", ""
    for i, (key, label, cards) in enumerate(TABS):
        on = ' class="on"' if i == 0 else ""
        seg += '<button type="button" data-tab="%s"%s>%s</button>' % (key, on, _esc(label))
        hidden = "" if i == 0 else " hidden"
        panels += '<div class="tabpanel" data-tab="%s"%s>%s</div>' % (
            key, hidden, "".join(_card(c) for c in cards))
    return seg, panels


@bp.route("/osint")
def index():
    seg, panels = render_panels()
    return render_template("osint.html", active="osint", title="OSINT",
                           tag="engagement",
                           intro="Passive reconnaissance: tools, live web resources, and image "
                                 "intelligence. Links open in a new tab; commands copy and "
                                 "substitute your variables.",
                           seg=seg, panels=panels)


MODULE = {"id": "osint", "title": "OSINT", "category": "Engagement",
          "order": 90, "blueprint": bp, "endpoint": "osint.index"}
