#!/bin/bash
cd "$(dirname "$0")"
echo "==============================================="
echo "   Starting PathDiver Desktop App for macOS..."
echo "==============================================="

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 was not found."
    echo "Please download Python 3 from https://www.python.org/downloads/macos/"
    read -p "Press enter to exit..."
    exit 1
fi

python3 -c "import webview, pypdf, PIL, send2trash" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "First time setup: installing dependencies..."
    pip3 install -r requirements.txt
fi

echo "Launching PathDiver..."
python3 desktop_main.py
