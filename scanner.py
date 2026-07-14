# ============================================================
# scanner.py — Modulo de escaneo y deteccion de duplicados
# ============================================================
# Este modulo se encarga de:
#   1. Escanear las carpetas de ROMs
#   2. Construir la lista maestra de archivos
#   3. Detectar duplicados por hash (exactos)
#   4. Detectar duplicados por nombre similar (fuzzy matching)
#   5. Agrupar resultados
# ============================================================

import os
from collections import defaultdict
from difflib import SequenceMatcher
import config
from config import (
    EXTENSIONES_VALIDAS,
    EXCLUIR_CARPETAS,
    CALCULAR_HASH,
    UMBRAL_SIMILITUD,
)
from utils import (
    calcular_hash_md5,
    generar_nombre_sugerido,
    limpiar_nombre,
    obtener_nombre_sistema,
    formatear_tamano,
)


def escanear_roms():
    """
    Escanea recursivamente la carpeta base en busca de
    archivos ROM y construye una lista con su informacion.

    Estructura esperada:
        RUTA_BASE/
            nes/
                Super Mario Bros (USA).nes
                Zelda.nes
            snes/
                Super Mario World (USA).sfc
            gba/
                Pokemon Ruby (USA).gba

    Retorna:
        Lista de diccionarios, cada uno con:
        - "archivo": nombre de archivo original
        - "ruta": ruta completa al archivo
        - "carpeta": nombre de la carpeta del sistema
        - "sistema": nombre legible del sistema
        - "tamano_bytes": tamano en bytes
        - "tamano_legible": tamano formateado (ej: "2.4 MB")
        - "hash": hash MD5 (o "" si no se calculo)
        - "nombre_sugerido": nombre limpio sin tags ni extension
    """
    ruta = config.RUTA_BASE
    roms = []
    extensiones_set = set(EXTENSIONES_VALIDAS)
    excluidas_set = set(c.lower() for c in EXCLUIR_CARPETAS)

    # Verificar que la ruta base existe
    if not os.path.isdir(ruta):
        print(f"[ERROR] La ruta base no existe: {ruta}")
        print("       Edit config.py y cambia RUTA_BASE a tu carpeta de ROMs.")
        return roms

    total_archivos = 0
    total_omitidos = 0

    # Recorrer cada subcarpeta (cada sistema)
    for nombre_carpeta in sorted(os.listdir(ruta)):
        ruta_carpeta = os.path.join(ruta, nombre_carpeta)

        # Saltar si no es una carpeta
        if not os.path.isdir(ruta_carpeta):
            continue

        # Saltar carpetas excluidas
        if nombre_carpeta.lower() in excluidas_set:
            continue

        # Obtener nombre legible del sistema
        sistema = obtener_nombre_sistema(nombre_carpeta)

        # Recorrer archivos dentro de esta carpeta
        for nombre_archivo in sorted(os.listdir(ruta_carpeta)):
            ruta_archivo = os.path.join(ruta_carpeta, nombre_archivo)

            # Solo procesar archivos (no subcarpetas)
            if not os.path.isfile(ruta_archivo):
                continue

            # Verificar extension
            _, extension = os.path.splitext(nombre_archivo)
            if extension.lower() not in extensiones_set:
                total_omitidos += 1
                continue

            # Obtener informacion del archivo
            tamano = os.path.getsize(ruta_archivo)
            hash_md5 = calcular_hash_md5(ruta_archivo) if CALCULAR_HASH else ""
            nombre_sugerido = generar_nombre_sugerido(nombre_archivo)

            roms.append({
                "archivo": nombre_archivo,
                "ruta": ruta_archivo,
                "carpeta": nombre_carpeta,
                "sistema": sistema,
                "tamano_bytes": tamano,
                "tamano_legible": formatear_tamano(tamano),
                "hash": hash_md5,
                "nombre_sugerido": nombre_sugerido,
            })
            total_archivos += 1

    print(f"  Escaneo completo:")
    print(f"    - ROMs encontradas: {total_archivos}")
    print(f"    - Archivos omitidos (otra extension): {total_omitidos}")
    print(f"    - Sistemas detectados: {len(set(r['carpeta'] for r in roms))}")

    return roms


def detectar_duplicados_hash(roms):
    """
    Detecta duplicados EXACTOS comparando hashes MD5.

    Agrupa archivos que tienen el mismo hash (contenido
    identico), sin importar si estan en diferentes
    carpetas o tienen diferentes nombres.

    Parametros:
        roms: Lista de diccionarios de ROMs (de escanear_roms).

    Retorna:
        Lista de grupos, donde cada grupo es:
        - "tipo": "hash" (duplicado exacto)
        - "hash": el hash MD5 compartido
        - "archivos": lista de ROMs con ese hash
        - "contador": cantidad de archivos en el grupo
        - "nombres": nombres de archivo separados por " | "
    """
    # Agrupar por hash
    grupos_hash = defaultdict(list)

    for rom in roms:
        if rom["hash"]:  # Solo si se calculo el hash
            grupos_hash[rom["hash"]].append(rom)

    # Filtrar solo grupos con mas de 1 archivo
    duplicados = []

    for hash_val, archivos in grupos_hash.items():
        if len(archivos) > 1:
            duplicados.append({
                "tipo": "Hash exacto (contenido identico)",
                "hash": hash_val,
                "archivos": archivos,
                "contador": len(archivos),
                "nombres": " | ".join(
                    f"[{a['sistema']}] {a['archivo']}" for a in archivos
                ),
            })

    return duplicados


def calcular_similitud(nombre_a: str, nombre_b: str) -> float:
    """
    Calcula la similitud entre dos nombres sugeridos
    usando SequenceMatcher (difflib), que es parte de
    la libreria estandar de Python (no requiere instalar nada).

    Parametros:
        nombre_a: Primer nombre sugerido.
        nombre_b: Segundo nombre sugerido.

    Retorna:
        Valor de similitud entre 0.0 y 100.0.
    """
    if not nombre_a or not nombre_b:
        return 0.0

    # Normalizar: minusculas y quitar espacios extra
    a = " ".join(nombre_a.lower().split())
    b = " ".join(nombre_b.lower().split())

    return SequenceMatcher(None, a, b).ratio() * 100


def detectar_duplicados_nombre(roms, duplicados_hash):
    """
    Detecta duplicados por NOMBRE SIMILAR, incluso si
    el contenido del archivo es diferente (distinta
    region, idioma, revision, hack, etc.).

    Tambien detecta archivos cuyo nombre coincide con un
    grupo de duplicados por hash (por ejemplo, una revision
    diferente del mismo juego).

    Parametros:
        roms: Lista completa de ROMs.
        duplicados_hash: Lista de duplicados por hash
                         (para expandir sus grupos).

    Retorna:
        Lista de grupos similares a detectar_duplicados_hash,
        pero con "tipo": "Nombre similar".
    """
    # --- FASE 1: Archivos con nombre similar entre si ---
    # que NO estan en ningun grupo de hash

    # Recolectar hashes ya marcados como duplicados exactos
    hashes_duplicados = set()
    for grupo in duplicados_hash:
        for rom in grupo["archivos"]:
            hashes_duplicados.add(rom["hash"])

    # Filtrar ROMs que NO son duplicados exactos
    roms_a_comparar = [
        r for r in roms
        if r["hash"] not in hashes_duplicados and r["nombre_sugerido"]
    ]

    # Para eficiencia, agrupar primero por carpeta
    por_carpeta = defaultdict(list)
    for rom in roms_a_comparar:
        por_carpeta[rom["carpeta"]].append(rom)

    duplicados = []
    procesados = set()

    # Comparar dentro de cada carpeta
    for carpeta, lista_roms in por_carpeta.items():
        for i in range(len(lista_roms)):
            for j in range(i + 1, len(lista_roms)):
                rom_a = lista_roms[i]
                rom_b = lista_roms[j]

                par_id = (min(rom_a["ruta"], rom_b["ruta"]),
                          max(rom_a["ruta"], rom_b["ruta"]))
                if par_id in procesados:
                    continue
                procesados.add(par_id)

                similitud = calcular_similitud(
                    rom_a["nombre_sugerido"],
                    rom_b["nombre_sugerido"]
                )

                if similitud >= UMBRAL_SIMILITUD:
                    duplicados.append((rom_a, rom_b, similitud))

    # --- FASE 2: Archivos que coinciden con grupos de hash ---
    # Ejemplo: Super Mario World (Rev 1) tiene contenido diferente
    # (otro hash), pero su nombre coincide con el grupo de hash
    # de "Super Mario World" (USA/Japan/Europe).

    archivos_no_hash = {r["ruta"]: r for r in roms_a_comparar}

    for grupo_h in duplicados_hash:
        # Obtener el nombre sugerido del grupo de hash
        nombre_grupo = grupo_h["archivos"][0]["nombre_sugerido"]
        carpeta_grupo = grupo_h["archivos"][0]["carpeta"]

        # Buscar archivos fuera del grupo con nombre similar
        for ruta, rom in archivos_no_hash.items():
            if rom["carpeta"] != carpeta_grupo:
                continue  # Solo comparar dentro de la misma carpeta

            similitud = calcular_similitud(nombre_grupo, rom["nombre_sugerido"])
            if similitud >= UMBRAL_SIMILITUD:
                # Agregar como par: primer archivo del grupo hash + este archivo
                duplicados.append((grupo_h["archivos"][0], rom, similitud))

    # Agrupar todos los pares en grupos conexos
    grupos = _agrupar_pares(duplicados)

    resultado = []
    for grupo in grupos:
        resultado.append({
            "tipo": "Nombre similar (posible duplicado)",
            "hash": "",
            "archivos": grupo,
            "contador": len(grupo),
            "nombres": " | ".join(
                f"[{a['sistema']}] {a['archivo']}" for a in grupo
            ),
        })

    return resultado


def _agrupar_pares(pares):
    """
    Agrupa pares de duplicados en grupos conexos usando
    un algoritmo de union-find (disjoint set).

    Si A es similar a B, y B es similar a C, entonces
    {A, B, C} forman un solo grupo.

    Parametros:
        pares: Lista de tuplas (rom_a, rom_b, similitud).

    Retorna:
        Lista de grupos (cada grupo es una lista de ROMs).
    """
    # Union-Find
    padre = {}

    def encontrar(x):
        if x not in padre:
            padre[x] = x
        while padre[x] != x:
            padre[x] = padre[padre[x]]  # Compresion de camino
            x = padre[x]
        return x

    def unir(x, y):
        px, py = encontrar(x), encontrar(y)
        if px != py:
            padre[px] = py

    # Unir todos los pares
    for rom_a, rom_b, _ in pares:
        unir(rom_a["ruta"], rom_b["ruta"])

    # Agrupar por raiz
    grupos_dict = defaultdict(list)
    for rom_a, rom_b, _ in pares:
        raiz = encontrar(rom_a["ruta"])
        if rom_a not in grupos_dict[raiz]:
            grupos_dict[raiz].append(rom_a)
        if rom_b not in grupos_dict[raiz]:
            grupos_dict[raiz].append(rom_b)

    # Retornar solo grupos con mas de 1 miembro
    return [g for g in grupos_dict.values() if len(g) > 1]