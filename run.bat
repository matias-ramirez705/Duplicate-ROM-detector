@echo off
chcp 65001 >nul 2>&1

:: ============================================================
:: run.bat - Ejecutable para Windows
:: ============================================================
:: Haz doble clic en este archivo para ejecutar el script.
:: Te pedira la ruta de tu carpeta de ROMs y hara todo
:: automaticamente, sin necesidad de editar ningun .py
:: ============================================================

:: --------------------------------------------------
:: RUTA A PYTHON (ajusta si es necesario)
:: --------------------------------------------------
:: Si "python" no funciona, intenta con "python3" o
:: la ruta completa, por ejemplo:
::   set PYTHON="C:\Users\TuUsuario\AppData\Local\Programs\Python\Python311\python.exe"
:: --------------------------------------------------
set PYTHON=python

:: --------------------------------------------------
:: CAMBIAR AL DIRECTORIO DEL SCRIPT
:: --------------------------------------------------
cd /d "%~dp0"

:: --------------------------------------------------
:: VERIFICAR QUE PYTHON ESTA DISPONIBLE
:: --------------------------------------------------
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [ERROR] No se encontro Python.
    echo.
    echo  Asegurate de tener Python 3.6+ instalado.
    echo  Descargalo desde: https://www.python.org/downloads/
    echo.
    echo  IMPORTANTE: Durante la instalacion, marca la opcion
    echo  "Add Python to PATH" para que funcione este .bat.
    echo.
    pause
    exit /b 1
)

:: ============================================================
:: SOLICITAR RUTA DE LAS ROMS AL USUARIO
:: ============================================================
:pedir_ruta
echo.
echo  ========================================================
echo   DETECTOR DE ROMS DUPLICADOS
echo  ========================================================
echo.
echo  Ingresa la ruta de tu carpeta de ROMs.
echo  (la que contiene las subcarpetas de cada sistema: nes, snes, gba, etc.)
echo.
echo  Ejemplos:
echo    C:\Roms_R36S
echo    E:\Roms
echo    D:\retroarch\roms
echo.
echo  Tambien puedes arrastrar la carpeta aqui con el mouse
echo  y presionar Enter.
echo.

set /p RUTA_ROMS="  Ruta: "

:: Quitar comillas si el usuario las puso (Windows las agrega al arrastrar)
set RUTA_ROMS=%RUTA_ROMS:"=%

:: Verificar que la ruta no este vacia
if "%RUTA_ROMS%"=="" (
    echo.
    echo  [ERROR] No ingresaste ninguna ruta.
    echo.
    goto pedir_ruta
)

:: Verificar que la ruta existe
if not exist "%RUTA_ROMS%\" (
    echo.
    echo  [ERROR] La ruta no existe: "%RUTA_ROMS%"
    echo  Verifica que la hayas escrito correctamente.
    echo.
    goto pedir_ruta
)

:: Mostrar confirmacion
echo.
echo  Carpeta seleccionada: %RUTA_ROMS%
echo.

:: --------------------------------------------------
:: EJECUTAR EL SCRIPT PASANDO LA RUTA COMO ARGUMENTO
:: --------------------------------------------------
%PYTHON% main.py "%RUTA_ROMS%"

:: Mantener ventana abierta al finalizar
echo.
pause