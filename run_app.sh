#!/bin/sh

cd "$(dirname "$0")" || {
    echo "Could not switch to the project directory." >&2
    exit 1
}

if [ -x ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "Python 3 was not found."
    echo "Install Python 3 and try again."
    exit 1
fi

"$PYTHON_CMD" "doc_scanner.py"
status=$?
if [ "$status" -ne 0 ]; then
    echo
    echo "Document Perspective Scanner could not start."
    echo "Install the required packages with:"
    echo "  $PYTHON_CMD -m pip install -r requirements.txt"
    exit "$status"
fi
