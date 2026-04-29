#!/usr/bin/env bash
# Double-click launcher for macOS (also works as ./run.sh on Linux).

set -e
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo
    echo "  Python 3.10 or newer is required, but was not found."
    echo
    echo "  macOS:   brew install python        (install Homebrew from https://brew.sh)"
    echo "  Linux:   sudo apt install python3 python3-venv    (Debian/Ubuntu)"
    echo "           sudo dnf install python3                  (Fedora)"
    echo
    read -p "Press Enter to close..." _
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo
    echo "  First-time setup: creating virtual environment..."
    echo "  (this only happens once and takes about a minute)"
    echo
    python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo
echo "  Checking dependencies..."
pip install --quiet --disable-pip-version-check -r requirements.txt

echo
echo "  ============================================================"
echo "    EveryTools is starting at http://localhost:5000"
echo "    The application window will open in a moment."
echo "    Keep this window open while using the application."
echo "  ============================================================"
echo

# (Browser launch removed because we use PyWebView Native App)

python app.py
