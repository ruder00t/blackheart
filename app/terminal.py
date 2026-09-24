"""
Integrated tmux terminal + "send to terminal" backend.

================================  S E C U R I T Y  ============================
These routes SHELL OUT TO tmux. `tmux send-keys` is arbitrary command execution
wired to the web app: anything that can reach these endpoints can type (and run)
commands in your terminal panes. They are therefore LOCALHOST-ONLY and every
route below refuses to serve any non-loopback client (403). Blackheart already
binds to 127.0.0.1 (see run.py); ttyd is likewise bound to 127.0.0.1. Do NOT
expose this app, or ttyd's port, on any routable interface.
==============================================================================

Fixed naming convention (do not change):
  session "blackheart", window 0, a 2x2 grid of panes.
Quadrants used by the UI are 0..3 = TL, TR, BL, BR. They are resolved to the
real tmux pane indices by sorting panes on (top, left), so the mapping is
correct regardless of how a given tmux version happens to number panes.

Unix/tmux only (fine for Kali/Parrot). tmux + ttyd are runtime deps; if either
is missing the endpoints report it cleanly instead of crashing.
"""
import atexit
import json
import os
import shutil
import subprocess
import time
from functools import wraps
from pathlib import Path

from flask import Blueprint, abort, jsonify, render_template, request

term_bp = Blueprint("terminal", __name__)

BASE = Path(__file__).resolve().parent.parent      # project root

SESSION = "blackheart"
WINDOW = 0
TTYD_HOST = "127.0.0.1"
TTYD_PORT = 7681
TTYD_URL = "http://%s:%d" % (TTYD_HOST, TTYD_PORT)

# Blackheart terminal theme (xterm.js ITheme, applied by ttyd via -t theme=...).
# Deliberately minimal: set only the background, the default (uncoloured) text
# colour and the cursor from the app's tokens (see app/static/css/app.css :root).
# The 16-colour ANSI palette is left at xterm.js defaults ON PURPOSE, so coloured
# tool output (nmap, ls, git, grep --color) and your shell prompt render exactly
# as they do in a normal terminal -- only the background/cursor read on-brand.
# `foreground` affects only text with no ANSI colour of its own; it does not
# touch coloured output. Prompt (user@host / pwd) colours live in the shell's
# PS1, not here.
TTYD_THEME = {
    "background": "#0a0a0c",           # --bg
    "foreground": "#e9e4d6",           # --bone (uncoloured text only)
    "cursor": "#e11d2a",               # --red-bright
    "cursorAccent": "#0a0a0c",         # --bg
    "selectionBackground": "#7a1a20",  # --red-dim (text stays readable on top)
    "selectionForeground": "#ffffff",
    "selection": "#7a1a20",            # legacy key for older xterm.js builds
}

# On-brand shell prompt (red user@host, white pwd) applied to freshly created
# panes so the terminal reads black/red/white without editing your dotfiles.
#   - Runs ONLY when Blackheart first creates the session, never on one that
#     already exists, so it can't clobber a session you've customised.
#   - Only bash and zsh are touched; any other shell is left exactly as-is.
#   - Uses the terminal's own ANSI red/white (slots 1 & 15), matching the
#     "leave the palette default" choice above -- no truecolor / tmux config
#     needed. For exact brand hex, colour the prompt in your rc instead.
# Set env BH_TERM_PROMPT=0 (or off/false/no) to disable. If your rc sets a
# themed prompt (oh-my-zsh, powerlevel10k, starship), that rc wins -- disable
# this and style the prompt there.
PROMPT_ENABLED = os.environ.get("BH_TERM_PROMPT", "1").lower() \
    not in ("0", "off", "false", "no")
PROMPT_DELAY = 0.35  # give each pane's shell time to source its rc before typing
# Space-prefixed so the line is kept out of history (ignorespace); `clear` wipes
# the injected line so a fresh pane still reads as 1 line -> BLUE for the tiles.
_PROMPTS = {
    "bash": r""" PS1='\[\e[1;31m\]\u@\h\[\e[0m\]:\[\e[1;97m\]\w\[\e[0m\]\$ '; clear""",
    "zsh":  r""" PROMPT='%B%F{red}%n@%m%f:%F{white}%~%f%b%# '; clear""",
}

# No-prefix pane switching: move focus between the 4 panes with <mod>+arrow,
# instead of the tmux default (prefix, then arrow). select-pane -U/-D/-L/-R
# moves by direction, which for the 2x2 grid maps arrows to spatial neighbours.
#   - BH_TERM_PANENAV_MOD picks the modifier: "C" = Ctrl (default, as requested),
#     "M" = Alt/Meta. NOTE: Ctrl+Left / Ctrl+Right shadow readline's word-jump
#     in the shell (the keys are caught by tmux before the shell sees them); use
#     "M" if you want to keep word-jump.
#   - Set BH_TERM_PANENAV=0 to disable and keep tmux's default prefix+arrow.
#   - tmux keybindings are server-wide, so this also applies to other sessions
#     on the same tmux server.
PANE_NAV_ENABLED = os.environ.get("BH_TERM_PANENAV", "1").lower() \
    not in ("0", "off", "false", "no")
_nav_mod = os.environ.get("BH_TERM_PANENAV_MOD", "C").strip().upper()
PANE_NAV_MOD = _nav_mod if _nav_mod in ("C", "M") else "C"  # C=Ctrl, M=Alt

_LOOPBACK = {"127.0.0.1", "::1", "localhost"}
_ttyd_proc = None  # our ttyd child, if we spawned one


# ----------------------------------------------------------------------------
# loopback guard
# ----------------------------------------------------------------------------
def _host_is_loopback():
    host = (request.host or "").split(":")[0].strip("[]").lower()
    return host in _LOOPBACK


def loopback_only(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if request.remote_addr not in _LOOPBACK or not _host_is_loopback():
            abort(403)  # tmux injection endpoints never serve non-loopback
        return fn(*a, **kw)
    return wrapper


# ----------------------------------------------------------------------------
# dependency detection
# ----------------------------------------------------------------------------
def _have(cmd):
    return shutil.which(cmd) is not None


def _ttyd_bin():
    """ttyd on PATH, or the static binary install.sh drops in ./bin/ttyd
    (Kali/Ubuntu repos don't always carry a 'ttyd' package)."""
    w = shutil.which("ttyd")
    if w:
        return w
    local = BASE / "bin" / "ttyd"
    if local.exists() and os.access(str(local), os.X_OK):
        return str(local)
    return None


def _missing():
    m = []
    if not _have("tmux"):
        m.append("tmux")
    if _ttyd_bin() is None:
        m.append("ttyd")
    return m


# ----------------------------------------------------------------------------
# tmux helpers
# ----------------------------------------------------------------------------
def _tmux(*args):
    """Run a tmux command; return (returncode, stdout). Never raises."""
    try:
        p = subprocess.run(
            ["tmux", *args],
            capture_output=True, text=True, timeout=5,
        )
        return p.returncode, p.stdout
    except Exception:
        return 1, ""


def _session_exists():
    rc, _ = _tmux("has-session", "-t", SESSION)
    return rc == 0


def _ensure_session():
    """Create session `blackheart` with a 2x2 tiled grid if it isn't there."""
    if not _have("tmux"):
        return False
    if _session_exists():
        return True
    # detached session with a comfortable virtual size, then a 2x2 tiled split.
    _tmux("new-session", "-d", "-s", SESSION, "-x", "220", "-y", "50")
    tgt = "%s:%d" % (SESSION, WINDOW)
    _tmux("split-window", "-h", "-t", tgt)
    _tmux("split-window", "-v", "-t", tgt)
    _tmux("select-layout", "-t", tgt, "tiled")
    _tmux("split-window", "-v", "-t", tgt)
    _tmux("select-layout", "-t", tgt, "tiled")
    _tmux("select-pane", "-t", "%s.0" % tgt)
    _apply_pane_nav()   # <mod>+arrow to move between the 4 panes (no prefix)
    _apply_prompt()   # on-brand prompt for the freshly created panes (bash/zsh)
    return _session_exists()


def _pane_order():
    """Return real tmux pane indices ordered as quadrants [TL, TR, BL, BR].

    Sort panes by (top, left): row-major visual order == TL, TR, BL, BR for a
    2x2. Falls back to [0,1,2,3] if the query fails."""
    rc, out = _tmux(
        "list-panes", "-t", "%s:%d" % (SESSION, WINDOW),
        "-F", "#{pane_index} #{pane_top} #{pane_left}",
    )
    panes = []
    if rc == 0:
        for line in out.splitlines():
            parts = line.split()
            if len(parts) == 3:
                try:
                    panes.append((int(parts[0]), int(parts[1]), int(parts[2])))
                except ValueError:
                    pass
    if len(panes) < 4:
        return [0, 1, 2, 3]
    panes.sort(key=lambda x: (x[1], x[2]))       # (top, left)
    return [p[0] for p in panes[:4]]


def _pane_shells():
    """Map real pane index -> the shell currently running in it (lowercased),
    e.g. {0: "bash", 1: "zsh"}. Empty on failure."""
    rc, out = _tmux(
        "list-panes", "-t", "%s:%d" % (SESSION, WINDOW),
        "-F", "#{pane_index} #{pane_current_command}",
    )
    shells = {}
    if rc == 0:
        for line in out.splitlines():
            parts = line.split(None, 1)
            if len(parts) == 2:
                try:
                    shells[int(parts[0])] = parts[1].strip().lower()
                except ValueError:
                    pass
    return shells


def _apply_prompt():
    """Type the on-brand prompt into each freshly created bash/zsh pane, then
    clear it. Best-effort and non-fatal: unknown shells are skipped, and any
    tmux failure is swallowed by _tmux(). Only ever called from _ensure_session
    on the creation path, so it runs once and never on an existing session."""
    if not PROMPT_ENABLED:
        return
    time.sleep(PROMPT_DELAY)          # let the shells finish sourcing their rc
    shells = _pane_shells()
    for idx in _pane_order():
        line = _PROMPTS.get(shells.get(idx, ""))
        if not line:
            continue                  # non-bash/zsh (or unknown) -> leave as-is
        tgt = "%s:%d.%d" % (SESSION, WINDOW, idx)
        _tmux("send-keys", "-t", tgt, "-l", "--", line)
        _tmux("send-keys", "-t", tgt, "Enter")


def _apply_pane_nav():
    """Bind <mod>+arrow (no prefix) to directional pane selection so the four
    panes can be switched like a window manager. tmux root-table bindings are
    server-wide and idempotent; re-binding the same key is harmless. Best-effort
    -- _tmux() swallows any failure."""
    if not PANE_NAV_ENABLED:
        return
    for key, flag in (("Up", "-U"), ("Down", "-D"),
                      ("Left", "-L"), ("Right", "-R")):
        _tmux("bind-key", "-n", "%s-%s" % (PANE_NAV_MOD, key),
              "select-pane", flag)


def _quadrant_target(quadrant):
    """Map UI quadrant 0..3 to a tmux pane target string, or None if invalid."""
    try:
        q = int(quadrant)
    except (TypeError, ValueError):
        return None
    if q < 0 or q > 3:
        return None
    idx = _pane_order()[q]
    return "%s:%d.%d" % (SESSION, WINDOW, idx)


def _pane_state(quadrant):
    """BLUE (empty) vs GREEN (has content), read straight from the pane.

    A cleared pane (or fresh shell) shows only its prompt line -> one non-blank
    line -> blue. Any output above the prompt -> >=2 non-blank lines -> green.
    Ctrl+L clears the pane, so it naturally reads blue on the next poll."""
    tgt = _quadrant_target(quadrant)
    if tgt is None:
        return "blue"
    rc, out = _tmux("capture-pane", "-t", tgt, "-p")
    if rc != 0:
        return "blue"
    nonblank = [ln for ln in out.splitlines() if ln.strip()]
    return "green" if len(nonblank) >= 2 else "blue"


def _all_states():
    return [_pane_state(q) for q in range(4)]


# ----------------------------------------------------------------------------
# ttyd helpers  (ttyd itself is bound to loopback via -i 127.0.0.1)
# ----------------------------------------------------------------------------
def _ttyd_alive():
    global _ttyd_proc
    return _ttyd_proc is not None and _ttyd_proc.poll() is None


def _ensure_ttyd():
    """Spawn ttyd against the blackheart session if we haven't already."""
    global _ttyd_proc
    ttyd = _ttyd_bin()
    if ttyd is None:
        return False
    if _ttyd_alive():
        return True
    try:
        _ttyd_proc = subprocess.Popen(
            [
                ttyd,
                "-i", TTYD_HOST,     # bind to loopback only
                "-p", str(TTYD_PORT),
                "-W",                # writable (client can type into the panes)
                # black/red/white Blackheart theme for the xterm.js frontend
                "-t", "theme=" + json.dumps(TTYD_THEME, separators=(",", ":")),
                "tmux", "new", "-A", "-s", SESSION,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception:
        _ttyd_proc = None
        return False


@atexit.register
def _kill_ttyd():
    global _ttyd_proc
    if _ttyd_alive():
        try:
            _ttyd_proc.terminate()
        except Exception:
            pass


# ----------------------------------------------------------------------------
# routes
# ----------------------------------------------------------------------------
@term_bp.route("/terminal")
@loopback_only
def terminal_page():
    """Standalone 2x2 pop-out view of the blackheart tmux session."""
    return render_template("terminal.html", ttyd_url=TTYD_URL, active="")


@term_bp.route("/api/term/ensure", methods=["POST"])
@loopback_only
def api_ensure():
    missing = _missing()
    if missing:
        return jsonify(ok=False, missing=missing)
    _ensure_session()
    _ensure_ttyd()
    return jsonify(
        ok=True, missing=[], session=_session_exists(),
        ttyd=_ttyd_alive(), ttyd_url=TTYD_URL,
        panes=_pane_order(), tiles=_all_states(),
    )


@term_bp.route("/api/term/send", methods=["POST"])
@loopback_only
def api_send():
    if not _have("tmux"):
        return jsonify(ok=False, missing=["tmux"])
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "")
    run = bool(data.get("run", False))
    tgt = _quadrant_target(data.get("pane", 0))
    if tgt is None:
        return jsonify(ok=False, error="bad pane"), 400
    if not isinstance(text, str) or text == "":
        return jsonify(ok=False, error="empty text"), 400
    _ensure_session()
    # -l sends the text literally (no tmux key-name interpretation of ; $ etc.)
    _tmux("send-keys", "-t", tgt, "-l", "--", text)
    if run:
        _tmux("send-keys", "-t", tgt, "Enter")
    return jsonify(ok=True)


@term_bp.route("/api/term/status")
@loopback_only
def api_status():
    have_tmux = _have("tmux")
    return jsonify(
        ok=True,
        missing=_missing(),
        tmux=have_tmux,
        ttyd=_ttyd_alive(),
        session=_session_exists() if have_tmux else False,
        ttyd_url=TTYD_URL,
        panes=_pane_order() if (have_tmux and _session_exists()) else [0, 1, 2, 3],
        tiles=_all_states() if (have_tmux and _session_exists()) else ["blue"] * 4,
    )
