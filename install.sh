#!/usr/bin/env bash
# Blackheart installer: Python deps + the system tools some tabs need.
set -e
cd "$(dirname "$0")"

python3 -m venv .venv
. .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt   # Flask, PyYAML, markdown, pygments, weasyprint

# System packages:
#   pandoc              -> Report Builder (md -> HTML)
#   WeasyPrint runtime  -> Report Builder (HTML -> PDF): pango/cairo/gdk-pixbuf/ffi
#   tmux                -> Integrated terminal (injection target)
#   ttyd                -> Integrated terminal (renders the tmux session in the
#                          browser). NOTE: 'ttyd' is NOT in every apt repo
#                          (e.g. some Kali/Ubuntu setups), so it's handled
#                          separately below with a static-binary fallback.
# tmux + ttyd both run on 127.0.0.1 only.
if command -v apt >/dev/null 2>&1; then
  sudo apt update
  sudo apt install -y pandoc \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libffi-dev libcairo2 fonts-crosextra-carlito \
    tmux
elif command -v brew >/dev/null 2>&1; then
  brew install pandoc pango gdk-pixbuf libffi cairo tmux ttyd
else
  echo "!! Install 'pandoc' + WeasyPrint runtime libs (pango, cairo, gdk-pixbuf) and 'tmux' with your package manager."
fi

# ---- ttyd (non-fatal: never abort the install if it can't be found) --------
ensure_ttyd() {
  if command -v ttyd >/dev/null 2>&1; then
    echo "ttyd: found on PATH ($(command -v ttyd))"; return 0
  fi
  if [ -x "./bin/ttyd" ]; then
    echo "ttyd: using bundled ./bin/ttyd"; return 0
  fi

  # try the package manager first (works where the repo carries it)
  if command -v apt >/dev/null 2>&1; then
    sudo apt install -y ttyd >/dev/null 2>&1 || true
  elif command -v brew >/dev/null 2>&1; then
    brew install ttyd >/dev/null 2>&1 || true
  fi
  if command -v ttyd >/dev/null 2>&1; then
    echo "ttyd: installed via package manager"; return 0
  fi

  # fallback: prebuilt static binary from GitHub releases -> ./bin/ttyd
  local os arch asset
  os="$(uname -s)"; arch="$(uname -m)"
  if [ "$os" != "Linux" ]; then
    echo "!! ttyd not found. Install it manually (no static fallback for $os)."; return 1
  fi
  case "$arch" in
    x86_64|amd64)   asset="ttyd.x86_64" ;;
    aarch64|arm64)  asset="ttyd.aarch64" ;;
    armv7l|armv6l|arm) asset="ttyd.arm" ;;
    i686|i386)      asset="ttyd.i686" ;;
    *) echo "!! ttyd not found and no static build for arch '$arch'. Install manually."; return 1 ;;
  esac

  echo "ttyd not in repos; downloading static binary ($asset) -> ./bin/ttyd"
  mkdir -p bin
  local url="https://github.com/tsl0922/ttyd/releases/latest/download/$asset"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL -o bin/ttyd "$url" || { echo "!! ttyd download failed. Install manually."; return 1; }
  elif command -v wget >/dev/null 2>&1; then
    wget -qO bin/ttyd "$url" || { echo "!! ttyd download failed. Install manually."; return 1; }
  else
    echo "!! need curl or wget to fetch ttyd. Install manually."; return 1
  fi
  chmod +x bin/ttyd
  echo "ttyd: installed to ./bin/ttyd"
}
ensure_ttyd || true

echo "Done. Start with ./run.sh"
