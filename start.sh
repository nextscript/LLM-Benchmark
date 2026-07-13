#!/bin/bash
# LLM Benchmark GUI - Startscript (Linux/macOS)

set -e

echo "========================================"
echo "  LLM Benchmark GUI"
echo "========================================"
echo ""

# Virtual Environment erstellen (optional)
if [ ! -d "venv" ]; then
    echo "[1/3] Virtual Environment wird erstellt..."
    python3 -m venv venv
fi

# Virtual Environment aktivieren
echo "[2/3] Abhängigkeiten werden installiert..."
source venv/bin/activate
pip install -r requirements.txt --quiet

# App starten
echo "[3/3] Server wird gestartet..."
echo ""
echo "========================================"
echo "  WebGUI: http://localhost:5000"
echo "  llama-server: http://127.0.0.1:8080"
echo "========================================"
echo ""
echo "STRG+C zum Beenden."
echo ""

uvicorn app:app --host 0.0.0.0 --port 5000 --reload
