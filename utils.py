# ============================================================
# utils.py — Funciones utilitarias del detector de duplicados
# ============================================================
# Este modulo contiene funciones auxiliares:
#   - Limpieza de nombres de ROMs
#   - Calculo de hash MD5
#   - Formateo de tamano de archivos
#   - Resolucion de nombre de sistema
# ============================================================

import os
import re
import hashlib
from config import (
    PATRONES_LIMPIEZA_NOMBRE,
    MAPA_SISTEMAS,
    LIMITE_TAMANIO_HASH_MB,
    GENERAR_NOMBRE_SUGERIDO,
)


def limpiar_nombre(nombre_archivo: str) -> str:
    """
    Limpia el nombre de un archivo ROM removiendo tags comunes
    de region, idioma, revision, codigos de dump, etc.

    Ejemplos:
        "Super Mario World (USA) [!].sfc" -> "Super Mario World.sfc"
        "Zelda no Densetsu (J) [h1C].sfc" -> "Zelda no Densetsu.sfc"
        "Sonic 2 (Rev A) [!].bin"         -> "Sonic 2.bin"

    Parametros:
        nombre_archivo: Nombre del archivo (con extension).

    Retorna:
        Nombre limpiado de tags.
    """
    if not GENERAR_NOMBRE_SUGERIDO:
        return nombre_archivo

    resultado = nombre_archivo

    # Aplicar cada patron de limpieza en orden
    for patron in PATRONES_LIMPIEZA_NOMBRE:
        resultado = re.sub(patron, " ", resultado, flags=re.IGNORECASE)

    # Limpiar espacios al inicio y final, y espacios antes de la extension
    resultado = resultado.strip()

    # Intentar preservar la extension limpiamente
    # Separar nombre base de la extension
    nombre_base, extension = os.path.splitext(resultado)

    # Limpiar espacios internos del nombre base
    nombre_base = re.sub(r"\s+", " ", nombre_base).strip()

    # Reconstruir con extension
    resultado = nombre_base + extension.lower() if extension else nombre_base

    return resultado


def generar_nombre_sugerido(nombre_archivo: str) -> str:
    """
    Genera un nombre sugerido sin tags, sin extension,
    ideal para comparar y agrupar juegos similares.

    Ejemplo:
        "Super Mario World (USA) [!].sfc" -> "Super Mario World"

    Parametros:
        nombre_archivo: Nombre del archivo original.

    Retorna:
        Nombre sugerido limpio (sin extension ni tags).
    """
    limpio = limpiar_nombre(nombre_archivo)
    nombre_base, _ = os.path.splitext(limpio)
    return nombre_base.strip()


def calcular_hash_md5(ruta_archivo: str) -> str:
    """
    Calcula el hash MD5 de un archivo.

    Lee el archivo en bloques de 8KB para no consumir
    demasiada memoria con archivos grandes.

    Parametros:
        ruta_archivo: Ruta completa al archivo.

    Retorna:
        Hash MD5 en formato hexadecimal, o cadena vacia
        si el archivo excede el limite de tamano o hay error.
    """
    limite_bytes = LIMITE_TAMANIO_HASH_MB * 1024 * 1024

    try:
        tamano = os.path.getsize(ruta_archivo)
        if limite_bytes > 0 and tamano > limite_bytes:
            # Archivo demasiado grande, se salta el hash
            return ""

        hash_md5 = hashlib.md5()
        with open(ruta_archivo, "rb") as f:
            # Leer en bloques de 8KB
            for bloque in iter(lambda: f.read(8192), b""):
                hash_md5.update(bloque)

        return hash_md5.hexdigest()

    except (OSError, IOError, PermissionError):
        return ""


def formatear_tamano(bytes_num: int) -> str:
    """
    Convierte un tamano en bytes a una representacion
    legible (B, KB, MB, GB).

    Parametros:
        bytes_num: Tamano en bytes.

    Retorna:
        Cadena con el tamano formateado, ej: "4.2 MB"
    """
    if bytes_num < 1024:
        return f"{bytes_num} B"
    elif bytes_num < 1024 * 1024:
        return f"{bytes_num / 1024:.1f} KB"
    elif bytes_num < 1024 * 1024 * 1024:
        return f"{bytes_num / (1024 * 1024):.1f} MB"
    else:
        return f"{bytes_num / (1024 * 1024 * 1024):.2f} GB"


def obtener_nombre_sistema(nombre_carpeta: str) -> str:
    """
    Convierte el nombre de una carpeta de RetroArch
    a un nombre de sistema mas legible.

    Usa el MAPA_SISTEMAS de config.py. Si la carpeta
    no esta en el mapa, devuelve el nombre original.

    Parametros:
        nombre_carpeta: Nombre de la carpeta del sistema.

    Retorna:
        Nombre legible del sistema, o el original si
        no se encuentra en el mapa.
    """
    clave = nombre_carpeta.lower().strip()
    return MAPA_SISTEMAS.get(clave, nombre_carpeta)