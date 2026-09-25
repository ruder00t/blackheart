"""
Fill variables in a command string.

Auto-filled: $IP, $PORT, and (when derivable) $HOST, $URL.
Everything else ($DOMAIN, $WL, $OUT, ...) is left as a literal placeholder
unless a value was supplied in `ctx`.

$URL is built from tls + host + port. $HOST falls back to the IP.
"""
import re

_VAR = re.compile(r"\$([A-Z_]+)")


def build_context(ip, port, tls, extra=None):
    ctx = dict(extra or {})
    ctx.setdefault("IP", ip)
    ctx.setdefault("PORT", str(port))
    host = ctx.get("HOST") or ip
    ctx["HOST"] = host
    if "URL" not in ctx or not ctx["URL"]:
        scheme = "https" if tls else "http"
        # omit default ports for cleanliness
        if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
            ctx["URL"] = f"{scheme}://{host}"
        else:
            ctx["URL"] = f"{scheme}://{host}:{port}"
    return ctx


def fill(command, ctx):
    def repl(m):
        key = m.group(1)
        val = ctx.get(key)
        return val if val not in (None, "") else m.group(0)  # keep $VAR if unknown
    return _VAR.sub(repl, command)
