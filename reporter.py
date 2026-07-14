# ============================================================
# reporter.py — Generador del reporte CSV
# ============================================================
# Este modulo toma los resultados del escaneo y genera
# el archivo CSV final con toda la informacion.
# ============================================================

import csv
import os
from config import SALIDA_CSV


def generar_csv(todos_los_duplicados, total_roms, total_sistemas):
    """
    Genera el archivo CSV con el reporte de duplicados.

    El CSV tiene las siguientes columnas:
        1. tipo_duplicado      - "Hash exacto" o "Nombre similar"
        2. nombre_sugerido     - Nombre limpio del juego
        3. sistema             - Nombre del sistema (ej: "SNES / Super Famicom")
        4. archivo_principal   - Nombre del primer archivo del grupo
        5. tamano              - Tamano del archivo principal
        6. contador            - Cuantos archivos similares/encontrados
        7. nombres_repetidos   - Lista de todos los archivos del grupo
        8. rutas_completas     - Rutas completas de todos los archivos

    Parametros:
        todos_los_duplicados: Lista combinada de grupos duplicados.
        total_roms: Total de ROMs escaneadas.
        total_sistemas: Total de sistemas detectados.
    """
    # Determinar ruta de salida (misma carpeta que el script)
    ruta_salida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", SALIDA_CSV)
    ruta_salida = os.path.normpath(ruta_salida)

    # Ordenar: primero los de hash (mas importantes), luego por contador
    todos_los_duplicados.sort(
        key=lambda g: (0 if "Hash" in g["tipo"] else 1, -g["contador"]),
    )

    # Cabeceras del CSV
    cabeceras = [
        "tipo_duplicado",
        "nombre_sugerido",
        "sistema",
        "archivo_principal",
        "tamano",
        "contador",
        "nombres_repetidos",
        "rutas_completas",
    ]

    filas = []

    for grupo in todos_los_duplicados:
        # Tomar el primer archivo como "principal"
        principal = grupo["archivos"][0]

        # Recopilar todos los sistemas del grupo
        sistemas = sorted(set(r["sistema"] for r in grupo["archivos"]))
        sistema_str = ", ".join(sistemas) if len(sistemas) > 1 else sistemas[0]

        # Nombre sugerido del principal
        nombre_sug = principal["nombre_sugerido"]

        # Construir fila
        fila = {
            "tipo_duplicado": grupo["tipo"],
            "nombre_sugerido": nombre_sug,
            "sistema": sistema_str,
            "archivo_principal": f"[{principal['carpeta']}] {principal['archivo']}",
            "tamano": principal["tamano_legible"],
            "contador": grupo["contador"],
            "nombres_repetidos": grupo["nombres"],
            "rutas_completas": " | ".join(r["ruta"] for r in grupo["archivos"]),
        }
        filas.append(fila)

    # Escribir CSV (usando utf-8-sig para compatibilidad con Excel en espanol)
    with open(ruta_salida, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=cabeceras)
        writer.writeheader()
        writer.writerows(filas)

    # Estadisticas finales
    duplicados_hash = sum(1 for g in todos_los_duplicados if "Hash" in g["tipo"])
    duplicados_nombre = sum(1 for g in todos_los_duplicados if "Nombre" in g["tipo"])
    archivos_repetidos = sum(g["contador"] - 1 for g in todos_los_duplicados)

    print()
    print("=" * 60)
    print("  REPORTE GENERADO EXITOSAMENTE")
    print("=" * 60)
    print(f"  Archivo: {ruta_salida}")
    print()
    print("  --- Resumen ---")
    print(f"  Total ROMs escaneadas:     {total_roms}")
    print(f"  Sistemas detectados:       {total_sistemas}")
    print(f"  Grupos duplicados (hash):  {duplicados_hash}")
    print(f"  Grupos duplicados (nombre):{duplicados_nombre}")
    print(f"  Total grupos duplicados:   {len(todos_los_duplicados)}")
    print(f"  Archivos que se pueden eliminar: {archivos_repetidos}")
    print("=" * 60)
    print()
    print("  Sugerencia: Abre el CSV con Excel o Google Sheets.")
    print("  Filtra por 'tipo_duplicado' para ver duplicados exactos")
    print("  o por nombre similar.")
    print("  La columna 'rutas_completas' te ayudara a localizar")
    print("  los archivos para eliminar los que no quieras.")
    print("=" * 60)