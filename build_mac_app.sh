#!/bin/sh
set -eu

cd "$(dirname "$0")"

if [ "$(uname -s)" != "Darwin" ]; then
    echo "This script must be run on macOS to build a macOS app." >&2
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 was not found. Install Python 3 and try again." >&2
    exit 1
fi

BUILD_ENV=".build-venv"
BUILD_PYTHON="$BUILD_ENV/bin/python"
APP_NAME="Document Perspective Scanner"

if [ ! -x "$BUILD_PYTHON" ]; then
    python3 -m venv "$BUILD_ENV"
fi

"$BUILD_PYTHON" -m pip install --upgrade pip
"$BUILD_PYTHON" -m pip install -r requirements.txt pyinstaller
"$BUILD_PYTHON" -m PyInstaller \
    --noconfirm \
    --clean \
    --windowed \
    --name "$APP_NAME" \
    --collect-all tkinterdnd2 \
    doc_scanner.py

echo
echo "Build complete: dist/$APP_NAME.app"
