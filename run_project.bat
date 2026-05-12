@echo off
cd /d "%~dp0"
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo Ambiente virtual .venv nao encontrado. Execute: py -3 -m venv .venv
    exit /b 1
)
python -m backend.app
