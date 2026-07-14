#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
# main.py — Detector de Duplicados para R36S
# ============================================================
#
# DESCRIPCION:
#   Este script escanea tu coleccion de ROMs del R36S (o
#   cualquier carpeta con estructura de RetroArch) y genera
#   un reporte CSV con los duplicados encontrados.
#
# TIPOS DE DETECCION:
#   1. Duplicados exactos (mismo hash MD5):
#      Archivos con contenido identico, independientemente
#      del nombre. Puedes borrar todos menos uno.
#
#   2. Duplicados por nombre similar:
#      Archivos con nombres parecidos (limpiando tags de
#      region, idioma, revision). Son el MISMO JUEGO pero
#      en diferente version, region o idioma. Revisa cual
#      version quieres conservar.
#
# USO:
#   Opcion A (recomendada): Haz doble clic en run.bat
#       Te pedira la ruta de tu carpeta de ROMs.
#   Opcion B: python main.py "C:\Ruta\A\Tus\Roms"
#       Pasa la ruta como argumento.
#   Opcion C: Abre config.py y cambia RUTA_BASE manualmente,
#       luego ejecuta: python main.py
#
# REQUISITOS:
#   - Python 3.6 o superior
#   - No requiere dependencias externas (usa solo libreria estandar)
#
# ESTRUCTURA DEL PROYECTO:
#   r36s_duplicate_finder/
#   |-- main.py      <-- Este archivo (punto de entrada)
#   |-- config.py    <-- Configuracion (opcional, solo si no usas el .bat)
#   |-- scanner.py   <-- Logica de escaneo y deteccion
#   |-- utils.py     <-- Funciones auxiliares
#   |-- reporter.py  <-- Generacion del CSV
#   |-- run.bat      <-- Ejecutable para Windows
#   └── README.md    <-- Documentacion
#
# ============================================================

import sys
import os
import time
import threading
import itertools
import sys

def iniciar_spinner(mensaje="Procesando"):
    """Inicia un spinner animado en un hilo separado."""
    spinner_chars = itertools.cycle(["|", "/", "-", "\\"])
    detener = threading.Event()

    def girar():
        while not detener.is_set():
            sys.stdout.write(f"\r  {mensaje} {next(spinner_chars)}")
            sys.stdout.flush()
            detener.wait(0.15)
        sys.stdout.write("\r" + " " * 60 + "\r")
        sys.stdout.flush()

    hilo = threading.Thread(target=girar, daemon=True)
    hilo.start()
    return detener, hilo


def detener_spinner(detener, hilo):
    """Detiene el spinner y limpia la linea."""
    detener.set()
    hilo.join(timeout=0.5)

# Agregar el directorio del script al path para importar modulos
directorio_actual = os.path.dirname(os.path.abspath(__file__))
if directorio_actual not in sys.path:
    sys.path.insert(0, directorio_actual)

# Importar modulos locales
import config
from scanner import escanear_roms, detectar_duplicados_hash, detectar_duplicados_nombre
# from reporter import generar_csv # entregaba el csv en formato de texto plano, ahora se genera un html
from reporter_html import generar_html


def main():
    """
    Funcion principal. Orquesta todo el proceso:
    1. Muestra la configuracion actual
    2. Escanea las ROMs
    3. Detecta duplicados (por hash y por nombre)
    4. Genera el reporte CSV
    """
    inicio = time.time()

    # --- Banner ---
    print()
    print("=" * 60)
    print("  DETECTOR DE DUPLICADOS DE ROMS")
    print("  Escanea tu coleccion de ROMs y encuentra repetidos")
    print("=" * 60)
    print()

    # --- Determinar la ruta a escanear ---
    # Prioridad: argumento CLI > config.py
    if len(sys.argv) > 1:
        # Ruta pasada como argumento (desde run.bat o terminal)
        ruta_base = sys.argv[1]
        config.RUTA_BASE = ruta_base
    else:
        # Usar la ruta de config.py
        ruta_base = config.RUTA_BASE

    # --- Mostrar configuracion actual ---
    print("  Configuracion actual:")
    print(f"    Ruta base:          {ruta_base}")
    print(f"    Ruta existe:        {'SI' if os.path.isdir(ruta_base) else 'NO <-- VERIFICA ESTO'}")
    print()

    # Verificar que la ruta existe antes de continuar
    if not os.path.isdir(ruta_base):
        print("  [ERROR] La ruta no existe o no es una carpeta.")
        print(f"  Ruta ingresada: {ruta_base}")
        print()
        print("  Soluciones:")
        print("    - Ejecuta run.bat e ingresa la ruta correcta.")
        print("    - O pasa la ruta como argumento:")
        print(r'      python main.py "C:\Roms_R36S"')
        print("    - O edita RUTA_BASE en config.py.")
        print()
        print("  Presiona Enter para salir...")
        try:
            input()
        except EOFError:
            pass
        sys.exit(1)

    # --- Paso 1: Escanear ROMs ---
    detener1, hilo1 = iniciar_spinner("[1/3] Escaneando archivos de ROM...")
    roms = escanear_roms()
    detener_spinner(detener1, hilo1)
    print("  [1/3] Escaneando archivos de ROM... listo!")

    if not roms:
        print("  No se encontraron ROMs con las extensiones configuradas.")
        print("  Revisa que RUTA_BASE apunte a la carpeta correcta y que")
        print("  EXTENSIONES_VALIDAS en config.py incluya las extensiones de tus ROMs.")
        print()
        print("  Presiona Enter para salir...")
        try:
            input()
        except EOFError:
            pass
        sys.exit(1)

    total_sistemas = len(set(r["carpeta"] for r in roms))
    print()

    # --- Paso 2: Detectar duplicados ---
    detener2, hilo2 = iniciar_spinner("[2/3] Detectando duplicados (hash MD5)...")
    duplicados_hash = detectar_duplicados_hash(roms)
    detener_spinner(detener2, hilo2)
    print(f"  [2a] Duplicados exactos (hash): {len(duplicados_hash)} grupos")

    detener3, hilo3 = iniciar_spinner("[2/3] Detectando duplicados (nombre similar)...")
    duplicados_nombre = detectar_duplicados_nombre(roms, duplicados_hash)
    detener_spinner(detener3, hilo3)
    print(f"  [2b] Duplicados por nombre: {len(duplicados_nombre)} grupos")

    # Combinar resultados
    todos_los_duplicados = duplicados_hash + duplicados_nombre
    print()

    if not todos_los_duplicados:
        print("  ¡Bien! No se encontraron duplicados.")
        print("  Tu coleccion esta limpia.")
        print()
        print("  Presiona Enter para salir...")
        try:
            input()
        except EOFError:
            pass
        sys.exit(0)

    # --- Paso 3: Generar CSV ---  Antiguo
    # print("[3/3] Generando reporte CSV...")
    # generar_csv(todos_los_duplicados, len(roms), total_sistemas)

    # --- Paso 3: Generar HTML ---
    detener4, hilo4 = iniciar_spinner("[3/3] Generando reporte HTML...")
    generar_html(todos_los_duplicados, len(roms), total_sistemas)
    detener_spinner(detener4, hilo4)
    print("  [3/3] Reporte generado!")

    fin = time.time()
    duracion = fin - inicio
    print(f"\n  Tiempo total: {duracion:.1f} segundos")
    print()

    # Pausa para que el usuario pueda leer el resultado
    print("  Presiona Enter para salir...")
    try:
        input()
    except EOFError:
        pass


if __name__ == "__main__":
    main()