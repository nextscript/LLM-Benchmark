@echo off
title LLM Benchmark GUI
echo ========================================
echo   LLM Benchmark GUI
echo ========================================
echo.

:: Virtual Environment erstellen (optional)
if not exist "venv" (
    echo [1/3] Virtual Environment wird erstellt...
    python -m venv venv
)

:: Virtual Environment aktivieren
echo [2/3] Abhängigkeiten werden installiert...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

:: App starten
echo [3/3] Server wird gestartet...
echo.
echo ========================================
echo   WebGUI: http://localhost:5000
echo   llama-server: http://127.0.0.1:8080
echo ========================================
echo.
echo Drücke STRG+C zum Beenden.
echo.

uvicorn app:app --host 0.0.0.0 --port 5000 --reload

pause
