# ============================================================
# reporter_html.py — Generador del reporte HTML interactivo
# ============================================================
# Genera una pagina web auto-contenida (un solo archivo .html)
# con filtros, busqueda, ordenamiento por columnas y
# estadisticas visuales. No requiere servidor ni internet.
#
# VERSION 2: Python genera todo el HTML (no template literals
# en JS) para evitar errores con caracteres especiales en
# nombres de archivo de RetroBat.
# ============================================================

import os
import html as html_mod
from config import SALIDA_CSV


def _esc(texto):
    """Escapa caracteres HTML especiales."""
    if not texto:
        return ""
    return html_mod.escape(str(texto))


def _esc_attr(texto):
    """Escapa para usar dentro de comillas dobles en atributos HTML."""
    if not texto:
        return ""
    return (str(texto)
            .replace("&", "&amp;")
            .replace('"', "&quot;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


def generar_html(todos_los_duplicados, total_roms, total_sistemas):
    """
    Genera un archivo HTML interactivo con el reporte de duplicados.
    Python genera todo el HTML; JavaScript solo filtra/muestra.
    """
    # --- Ruta de salida ---
    base = os.path.splitext(SALIDA_CSV)[0]
    ruta_salida = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", f"{base}.html"
    )
    ruta_salida = os.path.normpath(ruta_salida)

    # --- Ordenar: hash primero, luego por contador ---
    todos_los_duplicados.sort(
        key=lambda g: (0 if "Hash" in g["tipo"] else 1, -g["contador"]),
    )

    # --- Estadisticas ---
    duplicados_hash = [g for g in todos_los_duplicados if "Hash" in g["tipo"]]
    duplicados_nombre = [g for g in todos_los_duplicados if "Nombre" in g["tipo"]]
    archivos_repetidos = sum(g["contador"] - 1 for g in todos_los_duplicados)

    todos_sistemas = sorted(set(
        s.strip()
        for g in todos_los_duplicados
        for s in g["archivos"][0]["sistema"].split(",")
    ))

    # --- Generar tarjetas HTML desde Python ---
    tarjetas_html = []
    for i, grupo in enumerate(todos_los_duplicados):
        tipo_class = "tipo-hash" if "Hash" in grupo["tipo"] else "tipo-nombre"
        badge_class = "badge-hash" if "Hash" in grupo["tipo"] else "badge-nombre"
        tipo_texto = "Hash" if "Hash" in grupo["tipo"] else "Nombre"

        nombre = _esc(grupo["archivos"][0]["nombre_sugerido"])
        sistemas = sorted(set(a["sistema"] for a in grupo["archivos"]))
        sistema_str = _esc(", ".join(sistemas))
        tamano = _esc(grupo["archivos"][0]["tamano_legible"])
        contador = grupo["contador"]

        # Texto de busqueda (todo en minusculas, sin HTML)
        busqueda_texto = " ".join(
            [grupo["archivos"][0]["nombre_sugerido"]] +
            sistemas +
            [a["archivo"] for a in grupo["archivos"]]
        ).lower()

        # Filas de archivos (generadas por Python, sin template literals)
        filas = []
        for idx, a in enumerate(grupo["archivos"]):
            ruta_escaped = _esc(a["ruta"])
            archivo_escaped = _esc(a["archivo"])
            tamano_escaped = _esc(a["tamano_legible"])
            filas.append(
                '<div class="file-row">'
                f'<div class="file-num">{idx + 1}</div>'
                f'<div class="file-archivo" title="{ruta_escaped}">{archivo_escaped}</div>'
                f'<div class="file-tamano">{tamano_escaped}</div>'
                f'<div class="file-ruta">{ruta_escaped}</div>'
                f'<button class="btn-copiar" data-ruta="{_esc_attr(a["ruta"])}">'
                'Copiar ruta</button>'
                '</div>'
            )
        filas_str = "\n".join(filas)

        tarjeta = (
            f'<div class="group-card {tipo_class}" '
            f'data-tipo="{tipo_texto}" '
            f'data-sistema="{_esc_attr(sistema_str)}" '
            f'data-search="{_esc_attr(busqueda_texto)}">'
            f'<div class="group-header">'
            f'<span class="badge {badge_class}">{tipo_texto}</span>'
            f'<div class="group-name">{nombre}</div>'
            f'<div class="group-sistema">{sistema_str}</div>'
            f'<div class="group-tamano">{tamano}</div>'
            f'<div class="group-contador">'
            f'<span class="contador-num">{contador}</span>'
            '<span>arch.</span>'
            '</div>'
            '<span class="chevron">&#9654;</span>'
            '</div>'
            f'<div class="group-detail">{filas_str}</div>'
            '</div>'
        )
        tarjetas_html.append(tarjeta)

    todas_las_tarjetas = "\n".join(tarjetas_html)
    opciones_sistemas = "".join(
        f'<option value="{_esc(s)}">{_esc(s)}</option>' for s in todos_sistemas
    )

    # --- HTML completo ---
    contenido = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reporte de Duplicados - ROMS</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
    background: #0f1117;
    color: #e0e0e0;
    min-height: 100vh;
}}
.header {{
    background: linear-gradient(135deg, #1a1d2e 0%, #0f1117 100%);
    border-bottom: 1px solid #2a2d3e;
    padding: 24px 32px;
    text-align: center;
}}
.header h1 {{
    font-size: 1.8rem;
    color: #ffffff;
    font-weight: 700;
    letter-spacing: -0.5px;
}}
.header h1 span {{ color: #7c8aff; }}
.header p {{ color: #888; margin-top: 6px; font-size: 0.95rem; }}
.stats {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    padding: 24px 32px 0;
    max-width: 1200px;
    margin: 0 auto;
}}
.stat-card {{
    background: #1a1d2e;
    border: 1px solid #2a2d3e;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: border-color 0.2s;
}}
.stat-card:hover {{ border-color: #7c8aff; }}
.stat-card .number {{ font-size: 2rem; font-weight: 800; color: #fff; line-height: 1; }}
.stat-card .label {{ font-size: 0.8rem; color: #888; margin-top: 8px; text-transform: uppercase; letter-spacing: 0.5px; }}
.stat-card.hash .number {{ color: #ff6b6b; }}
.stat-card.nombre .number {{ color: #ffa94d; }}
.stat-card.eliminar .number {{ color: #51cf66; }}
.controles {{
    padding: 24px 32px;
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
}}
.search-box {{ flex: 1; min-width: 250px; position: relative; }}
.search-box input {{
    width: 100%;
    padding: 12px 16px 12px 44px;
    background: #1a1d2e;
    border: 1px solid #2a2d3e;
    border-radius: 10px;
    color: #e0e0e0;
    font-size: 0.95rem;
    outline: none;
    transition: border-color 0.2s;
}}
.search-box input:focus {{ border-color: #7c8aff; }}
.search-box input::placeholder {{ color: #555; }}
.search-icon {{
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: #555;
    font-size: 1rem;
    pointer-events: none;
}}
.filter-group {{
    display: flex;
    gap: 4px;
    background: #1a1d2e;
    border: 1px solid #2a2d3e;
    border-radius: 10px;
    padding: 4px;
}}
.filter-btn {{
    padding: 8px 16px;
    border: none;
    background: transparent;
    color: #888;
    font-size: 0.85rem;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
}}
.filter-btn:hover {{ color: #e0e0e0; background: #2a2d3e; }}
.filter-btn.active {{ background: #7c8aff; color: #fff; font-weight: 600; }}
.select-filter {{
    padding: 10px 14px;
    background: #1a1d2e;
    border: 1px solid #2a2d3e;
    border-radius: 10px;
    color: #e0e0e0;
    font-size: 0.85rem;
    outline: none;
    cursor: pointer;
    min-width: 180px;
}}
.select-filter:focus {{ border-color: #7c8aff; }}
.tabla-contenedor {{ padding: 0 32px 32px; max-width: 1200px; margin: 0 auto; }}
.result-count {{ color: #666; font-size: 0.85rem; margin-bottom: 12px; }}
.result-count span {{ color: #7c8aff; font-weight: 700; }}
.group-card {{
    background: #1a1d2e;
    border: 1px solid #2a2d3e;
    border-radius: 12px;
    margin-bottom: 10px;
    overflow: hidden;
    transition: border-color 0.2s;
}}
.group-card:hover {{ border-color: #3a3d4e; }}
.group-card.tipo-hash {{ border-left: 4px solid #ff6b6b; }}
.group-card.tipo-nombre {{ border-left: 4px solid #ffa94d; }}
.group-header {{
    display: grid;
    grid-template-columns: auto 1fr auto auto auto auto;
    gap: 16px;
    align-items: center;
    padding: 14px 18px;
    cursor: pointer;
    user-select: none;
    transition: background 0.15s;
}}
.group-header:hover {{ background: #22253a; }}
.badge {{
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
}}
.badge-hash {{ background: rgba(255,107,107,0.15); color: #ff6b6b; }}
.badge-nombre {{ background: rgba(255,169,77,0.15); color: #ffa94d; }}
.group-name {{
    font-weight: 600;
    color: #ffffff;
    font-size: 0.95rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}
.group-name mark {{
    background: rgba(124,138,255,0.3);
    color: #ffffff;
    border-radius: 2px;
    padding: 0 2px;
}}
.group-sistema {{ color: #888; font-size: 0.85rem; white-space: nowrap; }}
.group-tamano {{ color: #666; font-size: 0.85rem; white-space: nowrap; }}
.group-contador {{ display: flex; align-items: center; gap: 6px; font-size: 0.85rem; white-space: nowrap; }}
.contador-num {{
    background: #2a2d3e;
    color: #e0e0e0;
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.8rem;
}}
.chevron {{ color: #555; transition: transform 0.2s; font-size: 0.8rem; }}
.chevron.open {{ transform: rotate(90deg); }}
.group-detail {{ display: none; border-top: 1px solid #2a2d3e; background: #14161f; }}
.group-detail.open {{ display: block; }}
.file-row {{
    display: grid;
    grid-template-columns: 40px 1fr auto 1fr auto;
    gap: 12px;
    align-items: center;
    padding: 10px 18px 10px 36px;
    border-bottom: 1px solid #1e2030;
    font-size: 0.85rem;
    transition: background 0.15s;
}}
.file-row:last-child {{ border-bottom: none; }}
.file-row:hover {{ background: #1a1d2e; }}
.file-num {{ color: #555; font-size: 0.75rem; text-align: center; }}
.file-archivo {{
    color: #c0c0c0;
    font-family: "Cascadia Code", "Fira Code", "Consolas", monospace;
    font-size: 0.8rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}
.file-tamano {{ color: #666; font-size: 0.8rem; }}
.file-ruta {{
    color: #555;
    font-family: "Cascadia Code", "Fira Code", "Consolas", monospace;
    font-size: 0.75rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}
.btn-copiar {{
    padding: 4px 10px;
    background: #2a2d3e;
    border: 1px solid #3a3d4e;
    border-radius: 6px;
    color: #888;
    font-size: 0.72rem;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
}}
.btn-copiar:hover {{ background: #7c8aff; color: #fff; border-color: #7c8aff; }}
.btn-copiar.copied {{ background: #51cf66; color: #fff; border-color: #51cf66; }}
.empty-state {{ text-align: center; padding: 60px 20px; color: #555; }}
.empty-state h3 {{ color: #888; font-size: 1.1rem; margin-bottom: 8px; margin-top: 16px; }}
.toast {{
    position: fixed;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%) translateY(80px);
    background: #51cf66;
    color: #000;
    padding: 10px 24px;
    border-radius: 10px;
    font-size: 0.85rem;
    font-weight: 600;
    opacity: 0;
    transition: all 0.3s;
    pointer-events: none;
    z-index: 1000;
}}
.toast.show {{ opacity: 1; transform: translateX(-50%) translateY(0); }}
::-webkit-scrollbar {{ width: 8px; }}
::-webkit-scrollbar-track {{ background: #0f1117; }}
::-webkit-scrollbar-thumb {{ background: #2a2d3e; border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: #3a3d4e; }}
@media (max-width: 768px) {{
    .header {{ padding: 16px; }}
    .header h1 {{ font-size: 1.3rem; }}
    .stats {{ padding: 16px; gap: 10px; }}
    .controles {{ padding: 16px; }}
    .tabla-contenedor {{ padding: 0 16px 16px; }}
    .group-header {{ grid-template-columns: auto 1fr auto; gap: 8px; }}
    .group-sistema, .group-tamano {{ display: none; }}
    .file-row {{ grid-template-columns: 1fr auto; gap: 8px; padding-left: 18px; }}
    .file-num, .file-tamano, .file-ruta {{ display: none; }}
}}
</style>
</head>
<body>

<div class="header">
    <h1><span>ROMS</span> Reporte de Duplicados</h1>
    <p>{_esc(total_roms)} ROMs analizadas en {total_sistemas} sistemas</p>
</div>

<div class="stats">
    <div class="stat-card hash">
        <div class="number">{len(duplicados_hash)}</div>
        <div class="label">Duplicados exactos</div>
    </div>
    <div class="stat-card nombre">
        <div class="number">{len(duplicados_nombre)}</div>
        <div class="label">Nombres similares</div>
    </div>
    <div class="stat-card eliminar">
        <div class="number">{archivos_repetidos}</div>
        <div class="label">Archivos repetidos</div>
    </div>
    <div class="stat-card">
        <div class="number">{len(todos_los_duplicados)}</div>
        <div class="label">Grupos totales</div>
    </div>
</div>

<div class="controles">
    <div class="search-box">
        <span class="search-icon">&#128269;</span>
        <input type="text" id="searchInput" placeholder="Buscar por nombre de juego..." autocomplete="off">
    </div>
    <div class="filter-group">
        <button class="filter-btn active" data-filter="todos">Todos</button>
        <button class="filter-btn" data-filter="Hash">Hash</button>
        <button class="filter-btn" data-filter="Nombre">Nombre</button>
    </div>
    <select class="select-filter" id="sistemaFilter">
        <option value="">Todos los sistemas</option>
        {opciones_sistemas}
    </select>
</div>

<div class="tabla-contenedor">
    <div class="result-count">Mostrando <span id="countVisible">0</span> de <span id="countTotal">0</span> grupos</div>
    <div id="gruposContainer">
{todas_las_tarjetas}
    </div>
    <div id="emptyState" class="empty-state" style="display:none;">
        <h3>No se encontraron resultados</h3>
        <p>Intenta con otro filtro o termino de busqueda.</p>
    </div>
</div>

<div id="toast" class="toast">Ruta copiada al portapapeles</div>

<script>
(function() {{
    var filtroTipo = "todos";
    var filtroSistema = "";
    var filtroTexto = "";

    var tarjetas = document.querySelectorAll(".group-card");
    var total = tarjetas.length;

    document.getElementById("countTotal").textContent = total;

    function aplicarFiltros() {{
        var texto = filtroTexto.toLowerCase().trim();
        var visibles = 0;

        for (var i = 0; i < tarjetas.length; i++) {{
            var card = tarjetas[i];
            var mostrar = true;

            // Filtro por tipo
            if (filtroTipo !== "todos") {{
                if (card.getAttribute("data-tipo") !== filtroTipo) {{
                    mostrar = false;
                }}
            }}

            // Filtro por sistema
            if (mostrar && filtroSistema) {{
                if (card.getAttribute("data-sistema").indexOf(filtroSistema) === -1) {{
                    mostrar = false;
                }}
            }}

            // Filtro por texto de busqueda
            if (mostrar && texto) {{
                if (card.getAttribute("data-search").indexOf(texto) === -1) {{
                    mostrar = false;
                }}
            }}

            card.style.display = mostrar ? "" : "none";
            if (mostrar) visibles++;
        }}

        document.getElementById("countVisible").textContent = visibles;
        document.getElementById("emptyState").style.display = (visibles === 0) ? "block" : "none";
    }}

    // --- Toggle expandir/colapsar ---
    document.getElementById("gruposContainer").addEventListener("click", function(e) {{
        var header = e.target.closest(".group-header");
        if (!header) {{
            // Chequear si clickearon el boton copiar
            var btn = e.target.closest(".btn-copiar");
            if (btn) {{
                var ruta = btn.getAttribute("data-ruta");
                navigator.clipboard.writeText(ruta).then(function() {{
                    btn.textContent = "Copiado!";
                    btn.classList.add("copied");
                    document.getElementById("toast").classList.add("show");
                    setTimeout(function() {{
                        btn.textContent = "Copiar ruta";
                        btn.classList.remove("copied");
                        document.getElementById("toast").classList.remove("show");
                    }}, 2000);
                }});
            }}
            return;
        }}
        var card = header.parentElement;
        var detail = card.querySelector(".group-detail");
        var chevron = header.querySelector(".chevron");
        if (detail && chevron) {{
            detail.classList.toggle("open");
            chevron.classList.toggle("open");
        }}
    }});

    // --- Busqueda ---
    document.getElementById("searchInput").addEventListener("input", function() {{
        filtroTexto = this.value;
        aplicarFiltros();
    }});

    // --- Filtro por tipo ---
    var botones = document.querySelectorAll(".filter-btn");
    for (var i = 0; i < botones.length; i++) {{
        botones[i].addEventListener("click", function() {{
            for (var j = 0; j < botones.length; j++) botones[j].classList.remove("active");
            this.classList.add("active");
            filtroTipo = this.getAttribute("data-filter");
            aplicarFiltros();
        }});
    }}

    // --- Filtro por sistema ---
    document.getElementById("sistemaFilter").addEventListener("change", function() {{
        filtroSistema = this.value;
        aplicarFiltros();
    }});

    // --- Atajos de teclado ---
    document.addEventListener("keydown", function(e) {{
        if ((e.ctrlKey && e.key === "f") || (e.key === "/" && document.activeElement.tagName !== "INPUT")) {{
            e.preventDefault();
            document.getElementById("searchInput").focus();
        }}
        if (e.key === "Escape") {{
            document.getElementById("searchInput").value = "";
            filtroTexto = "";
            aplicarFiltros();
        }}
    }});

    // --- Inicio ---
    aplicarFiltros();
}})();
</script>

</body>
</html>"""

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(contenido)

    print()
    print("=" * 60)
    print("  REPORTE HTML GENERADO EXITOSAMENTE")
    print("=" * 60)
    print(f"  Archivo: {ruta_salida}")
    print()
    print("  --- Resumen ---")
    print(f"  Total ROMs escaneadas:       {total_roms}")
    print(f"  Sistemas detectados:         {total_sistemas}")
    print(f"  Grupos duplicados (hash):    {len(duplicados_hash)}")
    print(f"  Grupos duplicados (nombre):  {len(duplicados_nombre)}")
    print(f"  Total grupos duplicados:     {len(todos_los_duplicados)}")
    print(f"  Archivos que se pueden eliminar: {archivos_repetidos}")
    print("=" * 60)
    print()
    print("  Abre el archivo HTML en tu navegador.")
    print("=" * 60)