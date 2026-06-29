@echo off
REM ============================================================
REM  build.bat — Genera el .exe de ClipTítulos con PyInstaller
REM  Ejecutar desde la carpeta raíz del proyecto
REM ============================================================

echo.
echo  Instalando dependencias...
pip install -r requirements.txt

echo.
echo  Generando .exe...
pyinstaller ^
    --onefile ^
    --noconsole ^
    --name ClipTitulos ^
    --add-data "data;data" ^
    --add-data "src;src" ^
    --hidden-import "pystray._win32" ^
    --hidden-import "PIL._tkinter_finder" ^
    main.py

echo.
echo  ============================================================
echo   Listo! El ejecutable esta en:  dist\ClipTitulos.exe
echo   Copiar junto con la carpeta data\ para distribuir.
echo  ============================================================
pause
