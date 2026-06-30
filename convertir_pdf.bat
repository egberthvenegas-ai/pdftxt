@echo off
setlocal
cd /d "%~dp0"

if "%~1"=="" (
    echo No se arrastro ningun archivo. Procesando carpeta input\ por defecto...
    python pdf2txt.py
) else (
    echo Procesando: %~1
    python pdf2txt.py "%~1" -o "%~dpn1.txt"
)

echo.
echo Listo. Presiona una tecla para cerrar.
pause >nul
