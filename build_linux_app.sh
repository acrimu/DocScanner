#!/bin/sh
set -eu

cd "$(dirname "$0")"

if [ "$(uname -s)" != "Linux" ]; then
    echo "This script must be run on Linux to build a Linux app." >&2
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 was not found. Install Python 3 and try again." >&2
    exit 1
fi

if ! python3 -c 'import tkinter' >/dev/null 2>&1; then
    echo "Tkinter is not available in this Python installation." >&2
    echo "On Debian or Ubuntu, install it with: sudo apt install python3-tk" >&2
    exit 1
fi

BUILD_ENV=".build-venv-linux"
BUILD_PYTHON="$BUILD_ENV/bin/python"
APP_NAME="Document Perspective Scanner"

if [ ! -x "$BUILD_PYTHON" ]; then
    if ! python3 -m venv "$BUILD_ENV"; then
        echo "Could not create the build environment." >&2
        echo "On Debian or Ubuntu, install venv support with: sudo apt install python3-venv" >&2
        exit 1
    fi
fi

"$BUILD_PYTHON" -m pip install --upgrade pip
"$BUILD_PYTHON" -m pip install -r requirements.txt pyinstaller
"$BUILD_PYTHON" -m PyInstaller \
    --noconfirm \
    --clean \
    --name "$APP_NAME" \
    --collect-all tkinterdnd2 \
    doc_scanner.py

echo
echo "Build complete: dist/$APP_NAME/$APP_NAME"
