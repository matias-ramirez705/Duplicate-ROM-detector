# ============================================================
# reporter_inventory.py — Generador del inventario HTML
# ============================================================
# Genera una pagina web auto-contenida que lista TODAS las
# ROMs organizadas por sistema. Es una vista de inventario/
# navegador, complementaria al reporte de duplicados.
#
# Patron: Python genera TODO el HTML. JavaScript solo hace
# show/hide filtrando por data-* attributes.
# No se usan template literals en JS.
# ============================================================

import os
import html


def _esc(texto):
    """Escapa caracteres HTML especiales para evitar inyeccion."""
    if not texto:
        return ""
    return html.escape(str(texto))


def generar_inventario(roms):
    """
    Genera un archivo HTML con el inventario completo de todas
    las ROMs, organizadas por sistema en secciones colapsables.

    El HTML incluye:
    - Tarjetas de estadisticas (total ROMs, sistemas, tamaño)
    - Barra de busqueda por texto
    - Filtro por sistema (dropdown)
    - Secciones colapsables por sistema con lista de juegos
    - Boton para copiar la ruta de cada archivo

    Parametros:
        roms: Lista completa de diccionarios de ROMs (de escanear_roms).
    """
    # --- Ruta de salida (mismo directorio que el otro HTML) ---
    ruta_salida = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "inventario_roms.html"
    )
    ruta_salida = os.path.normpath(ruta_salida)

    # --- Agrupar ROMs por sistema ---
    sistemas_dict = {}
    for rom in roms:
        carpeta = rom["carpeta"]
        if carpeta not in sistemas_dict:
            sistemas_dict[carpeta] = {
                "carpeta": carpeta,
                "sistema": rom["sistema"],
                "roms": [],
            }
        sistemas_dict[carpeta]["roms"].append(rom)

    # Ordenar sistemas por nombre legible
    sistemas_ordenados = sorted(sistemas_dict.values(), key=lambda s: s["sistema"].lower())

    # --- Calcular estadisticas ---
    total_roms = len(roms)
    total_sistemas = len(sistemas_ordenados)
    total_bytes = sum(r["tamano_bytes"] for r in roms)

    # Formatear tamano total
    if total_bytes < 1024:
        tamano_total = f"{total_bytes} B"
    elif total_bytes < 1024 * 1024:
        tamano_total = f"{total_bytes / 1024:.1f} KB"
    elif total_bytes < 1024 * 1024 * 1024:
        tamano_total = f"{total_bytes / (1024 * 1024):.1f} MB"
    else:
        tamano_total = f"{total_bytes / (1024 * 1024 * 1024):.2f} GB"

    # --- Generar HTML de secciones de sistemas ---
    secciones_html = []
    for idx, sis in enumerate(sistemas_ordenados):
        # Ordenar ROMs dentro del sistema por nombre
        roms_ordenadas = sorted(sis["roms"], key=lambda r: r["archivo"].lower())
        cantidad = len(roms_ordenadas)

        # Tamano total del sistema
        tam_sis = sum(r["tamano_bytes"] for r in roms_ordenadas)
        if tam_sis < 1024:
            tam_sis_str = f"{tam_sis} B"
        elif tam_sis < 1024 * 1024:
            tam_sis_str = f"{tam_sis / 1024:.1f} KB"
        elif tam_sis < 1024 * 1024 * 1024:
            tam_sis_str = f"{tam_sis / (1024 * 1024):.1f} MB"
        else:
            tam_sis_str = f"{tam_sis / (1024 * 1024 * 1024):.2f} GB"

        # Generar filas de ROMs
        filas_html = []
        for rom in roms_ordenadas:
            filas_html.append(
                f'<div class="file-row" data-search="{_esc(rom["archivo"].lower())}">'
                f'  <div class="file-archivo" title="{_esc(rom["archivo"])}">'
                f'    {_esc(rom["archivo"])}'
                f'  </div>'
                f'  <div class="file-tamano">{_esc(rom["tamano_legible"])}</div>'
                f'  <div class="file-nombre">{_esc(rom["nombre_sugerido"])}</div>'
                f'  <button class="btn-copiar" data-ruta="{_esc(rom["ruta"])}">'
                f'    Copiar ruta'
                f'  </button>'
                f'</div>'
            )

        filas_str = "\n".join(filas_html)

        secciones_html.append(
            f'<div class="system-card" data-sistema="{_esc(sis["sistema"])}" '
            f'data-search="{_esc(sis["sistema"].lower())}">'
            f'  <div class="system-header" data-idx="{idx}">'
            f'    <span class="chevron" id="chev-{idx}">&#9654;</span>'
            f'    <div class="system-info">'
            f'      <span class="system-name">{_esc(sis["sistema"])}</span>'
            f'      <span class="system-carpeta">{_esc(sis["carpeta"])}</span>'
            f'    </div>'
            f'    <div class="system-stats">'
            f'      <span class="contador-badge">{cantidad} ROMs</span>'
            f'      <span class="tamano-badge">{tam_sis_str}</span>'
            f'    </div>'
            f'  </div>'
            f'  <div class="system-detail" id="detail-{idx}">'
            f'    {filas_str}'
            f'  </div>'
            f'</div>'
        )

    secciones_str = "\n".join(secciones_html)

    # --- Generar opciones del select de sistemas ---
    opciones_html = "".join(
        f'<option value="{_esc(s["sistema"])}">{_esc(s["sistema"])} '
        f'({len(s["roms"])})</option>'
        for s in sistemas_ordenados
    )

    # --- Construir el HTML completo ---
    contenido = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Inventario de ROMs</title>
<style>
/* ========== RESET Y BASE ========== */
* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
    background: #0f1117;
    color: #e0e0e0;
    min-height: 100vh;
}}

/* ========== ENCABEZADO ========== */
.header {{
    background: linear-gradient(135deg, #1a2e1d 0%, #0f1117 100%);
    border-bottom: 1px solid #2a3e2e;
    padding: 24px 32px;
    text-align: center;
}}

.header h1 {{
    font-size: 1.8rem;
    color: #ffffff;
    font-weight: 700;
    letter-spacing: -0.5px;
}}

.header h1 span {{
    color: #51cf66;
}}

.header p {{
    color: #888;
    margin-top: 6px;
    font-size: 0.95rem;
}}

/* ========== ESTADISTICAS ========== */
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

.stat-card:hover {{
    border-color: #51cf66;
}}

.stat-card .number {{
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1;
}}

.stat-card .label {{
    font-size: 0.8rem;
    color: #888;
    margin-top: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.stat-card.roms .number {{ color: #7c8aff; }}
.stat-card.sistemas .number {{ color: #51cf66; }}
.stat-card.tamano .number {{ color: #ffa94d; }}

/* ========== CONTROLES / FILTROS ========== */
.controles {{
    padding: 24px 32px;
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
}}

.search-box {{
    flex: 1;
    min-width: 250px;
    position: relative;
}}

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

.search-box input:focus {{
    border-color: #51cf66;
}}

.search-box input::placeholder {{
    color: #555;
}}

.search-box::before {{
    content: "\\1F50D";
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1rem;
    opacity: 0.5;
}}

.select-filter {{
    padding: 10px 14px;
    background: #1a1d2e;
    border: 1px solid #2a2d3e;
    border-radius: 10px;
    color: #e0e0e0;
    font-size: 0.85rem;
    outline: none;
    cursor: pointer;
    min-width: 200px;
}}

.select-filter:focus {{
    border-color: #51cf66;
}}

.btn-expand {{
    padding: 10px 18px;
    background: #1a1d2e;
    border: 1px solid #2a2d3e;
    border-radius: 10px;
    color: #888;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
}}

.btn-expand:hover {{
    color: #e0e0e0;
    background: #2a2d3e;
}}

/* ========== CONTENEDOR ========== */
.contenedor {{
    padding: 0 32px 32px;
    max-width: 1200px;
    margin: 0 auto;
}}

.result-count {{
    color: #666;
    font-size: 0.85rem;
    margin-bottom: 12px;
}}

.result-count span {{
    color: #51cf66;
    font-weight: 700;
}}

/* ========== TARJETA DE SISTEMA ========== */
.system-card {{
    background: #1a1d2e;
    border: 1px solid #2a2d3e;
    border-radius: 12px;
    margin-bottom: 10px;
    overflow: hidden;
    transition: border-color 0.2s;
}}

.system-card:hover {{
    border-color: #3a3d4e;
}}

.system-header {{
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 18px;
    cursor: pointer;
    user-select: none;
    transition: background 0.15s;
}}

.system-header:hover {{
    background: #22253a;
}}

.chevron {{
    color: #555;
    transition: transform 0.2s;
    font-size: 0.8rem;
    flex-shrink: 0;
}}

.chevron.open {{
    transform: rotate(90deg);
}}

.system-info {{
    flex: 1;
    min-width: 0;
}}

.system-name {{
    font-weight: 600;
    color: #ffffff;
    font-size: 0.95rem;
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}

.system-name mark {{
    background: rgba(81,207,102,0.3);
    color: #ffffff;
    border-radius: 2px;
    padding: 0 2px;
}}

.system-carpeta {{
    color: #555;
    font-size: 0.75rem;
    font-family: "Cascadia Code", "Fira Code", "Consolas", monospace;
}}

.system-stats {{
    display: flex;
    gap: 8px;
    flex-shrink: 0;
}}

.contador-badge {{
    background: #2a2d3e;
    color: #7c8aff;
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.8rem;
    white-space: nowrap;
}}

.tamano-badge {{
    background: #2a2d3e;
    color: #ffa94d;
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.8rem;
    white-space: nowrap;
}}

/* ========== DETALLE EXPANDIDO ========== */
.system-detail {{
    display: none;
    border-top: 1px solid #2a2d3e;
    background: #14161f;
}}

.system-detail.open {{
    display: block;
}}

/* Encabezado de columnas dentro de cada sistema */
.file-header {{
    display: grid;
    grid-template-columns: 1fr auto 1fr auto;
    gap: 12px;
    align-items: center;
    padding: 8px 18px 8px 50px;
    border-bottom: 1px solid #1e2030;
    font-size: 0.7rem;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
}}

/* Fila de cada ROM */
.file-row {{
    display: grid;
    grid-template-columns: 1fr auto 1fr auto;
    gap: 12px;
    align-items: center;
    padding: 8px 18px 8px 50px;
    border-bottom: 1px solid #1e2030;
    font-size: 0.85rem;
    transition: background 0.15s;
}}

.file-row:last-child {{
    border-bottom: none;
}}

.file-row:hover {{
    background: #1a1d2e;
}}

.file-row.hidden {{
    display: none;
}}

.file-archivo {{
    color: #c0c0c0;
    font-family: "Cascadia Code", "Fira Code", "Consolas", monospace;
    font-size: 0.8rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}

.file-archivo mark {{
    background: rgba(81,207,102,0.3);
    color: #ffffff;
    border-radius: 2px;
    padding: 0 2px;
}}

.file-tamano {{
    color: #666;
    font-size: 0.8rem;
    white-space: nowrap;
}}

.file-nombre {{
    color: #888;
    font-size: 0.78rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-style: italic;
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

.btn-copiar:hover {{
    background: #51cf66;
    color: #ffffff;
    border-color: #51cf66;
}}

.btn-copiar.copied {{
    background: #51cf66;
    color: #ffffff;
    border-color: #51cf66;
}}

/* ========== ESTADO VACIO ========== */
.empty-state {{
    text-align: center;
    padding: 60px 20px;
    color: #555;
}}

.empty-state .icon {{
    font-size: 3rem;
    margin-bottom: 16px;
}}

.empty-state h3 {{
    color: #888;
    font-size: 1.1rem;
    margin-bottom: 8px;
}}

/* ========== SCROLLBAR ========== */
::-webkit-scrollbar {{
    width: 8px;
}}

::-webkit-scrollbar-track {{
    background: #0f1117;
}}

::-webkit-scrollbar-thumb {{
    background: #2a2d3e;
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: #3a3d4e;
}}

/* ========== RESPONSIVE ========== */
@media (max-width: 768px) {{
    .header {{ padding: 16px; }}
    .header h1 {{ font-size: 1.3rem; }}
    .stats {{ padding: 16px; gap: 10px; }}
    .controles {{ padding: 16px; }}
    .contenedor {{ padding: 0 16px 16px; }}
    .system-stats {{ flex-direction: column; gap: 4px; }}
    .file-row {{
        grid-template-columns: 1fr auto;
        gap: 8px;
        padding-left: 32px;
    }}
    .file-header {{ display: none; }}
    .file-nombre {{ display: none; }}
}}

/* ========== TOAST ========== */
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

.toast.show {{
    opacity: 1;
    transform: translateX(-50%) translateY(0);
}}
</style>
</head>
<body>

<!-- Encabezado -->
<div class="header">
    <h1><span>Inventario</span> de ROMs</h1>
    <p>{_esc(total_roms)} ROMs en {_esc(total_sistemas)} sistemas &mdash; Tama&ntilde;o total: {_esc(tamano_total)}</p>
</div>

<!-- Estadisticas -->
<div class="stats">
    <div class="stat-card roms">
        <div class="number">{_esc(total_roms)}</div>
        <div class="label">Total ROMs</div>
    </div>
    <div class="stat-card sistemas">
        <div class="number">{_esc(total_sistemas)}</div>
        <div class="label">Sistemas</div>
    </div>
    <div class="stat-card tamano">
        <div class="number">{_esc(tamano_total)}</div>
        <div class="label">Tama&ntilde;o total</div>
    </div>
</div>

<!-- Controles -->
<div class="controles">
    <div class="search-box">
        <input type="text" id="searchInput" placeholder="Buscar por nombre de ROM o sistema..." autocomplete="off">
    </div>
    <select class="select-filter" id="sistemaFilter">
        <option value="">Todos los sistemas</option>
        {opciones_html}
    </select>
    <button class="btn-expand" id="btnExpandAll">Expandir todos</button>
</div>

<!-- Contenido principal -->
<div class="contenedor">
    <div class="result-count">Mostrando <span id="countVisible">0</span> de <span id="countTotal">{_esc(total_sistemas)}</span> sistemas</div>
    <div id="sistemasContainer">
        {secciones_str}
    </div>
    <div id="emptyState" class="empty-state" style="display:none;">
        <div class="icon">&#128269;</div>
        <h3>No se encontraron resultados</h3>
        <p>Intenta con otro filtro o t&eacute;rmino de b&uacute;squeda.</p>
    </div>
</div>

<!-- Toast -->
<div id="toast" class="toast">Ruta copiada al portapapeles</div>

<script>
// ============================================================
// ESTADO
// ============================================================
var filtroSistema = "";
var filtroTexto = "";
var todosExpandidos = false;

// ============================================================
// FILTRADO
// ============================================================
function aplicarFiltros() {{
    var texto = filtroTexto.toLowerCase().trim();
    var cards = document.querySelectorAll(".system-card");
    var visibles = 0;

    for (var i = 0; i < cards.length; i++) {{
        var card = cards[i];
        var sistemaMatch = !filtroSistema || card.getAttribute("data-sistema") === filtroSistema;
        var textoMatch = !texto || card.getAttribute("data-search").indexOf(texto) !== -1;

        // Si hay texto de busqueda, tambien buscar dentro de las filas
        var filaMatch = false;
        if (texto && sistemaMatch) {{
            var filas = card.querySelectorAll(".file-row");
            for (var j = 0; j < filas.length; j++) {{
                if (filas[j].getAttribute("data-search").indexOf(texto) !== -1) {{
                    filaMatch = true;
                    break;
                }}
            }}
        }}

        var mostrar = sistemaMatch && (!texto || textoMatch || filaMatch);
        card.style.display = mostrar ? "" : "none";

        if (mostrar) {{
            visibles++;
            // Si hay busqueda y match por fila, ocultar filas que no matchean
            if (texto && !textoMatch && filaMatch) {{
                var filas2 = card.querySelectorAll(".file-row");
                for (var k = 0; k < filas2.length; k++) {{
                    if (filas2[k].getAttribute("data-search").indexOf(texto) !== -1) {{
                        filas2[k].classList.remove("hidden");
                    }} else {{
                        filas2[k].classList.add("hidden");
                    }}
                }}
                // Auto-expandir cuando hay busqueda con match interno
                var idx = card.querySelector(".system-header").getAttribute("data-idx");
                document.getElementById("detail-" + idx).classList.add("open");
                document.getElementById("chev-" + idx).classList.add("open");
            }} else {{
                // Restaurar todas las filas visibles
                var filas3 = card.querySelectorAll(".file-row");
                for (var m = 0; m < filas3.length; m++) {{
                    filas3[m].classList.remove("hidden");
                }}
            }}
        }}
    }}

    document.getElementById("countVisible").textContent = visibles;
    document.getElementById("countTotal").textContent = cards.length;
    document.getElementById("emptyState").style.display = visibles === 0 ? "block" : "none";
}}

// ============================================================
// TOGGLE SECCION
// ============================================================
function toggleSection(idx) {{
    var detail = document.getElementById("detail-" + idx);
    var chevron = document.getElementById("chev-" + idx);
    detail.classList.toggle("open");
    chevron.classList.toggle("open");
}}

// ============================================================
// EXPANDIR / COLAPSAR TODOS
// ============================================================
function toggleTodos() {{
    todosExpandidos = !todosExpandidos;
    var detalles = document.querySelectorAll(".system-detail");
    var chevrons = document.querySelectorAll(".chevron");
    for (var i = 0; i < detalles.length; i++) {{
        if (todosExpandidos) {{
            detalles[i].classList.add("open");
            chevrons[i].classList.add("open");
        }} else {{
            detalles[i].classList.remove("open");
            chevrons[i].classList.remove("open");
        }}
    }}
    document.getElementById("btnExpandAll").textContent = todosExpandidos ? "Colapsar todos" : "Expandir todos";
}}

// ============================================================
// COPIAR RUTA
// ============================================================
function copiarRuta(btn) {{
    var ruta = btn.getAttribute("data-ruta");
    navigator.clipboard.writeText(ruta).then(function() {{
        btn.textContent = "Copiado!";
        btn.classList.add("copied");
        showToast("Ruta copiada al portapapeles");
        setTimeout(function() {{
            btn.textContent = "Copiar ruta";
            btn.classList.remove("copied");
        }}, 2000);
    }});
}}

function showToast(msg) {{
    var toast = document.getElementById("toast");
    toast.textContent = msg;
    toast.classList.add("show");
    setTimeout(function() {{ toast.classList.remove("show"); }}, 2000);
}}

// ============================================================
// UTILIDADES HTML
// ============================================================
function escapeHTML(str) {{
    var div = document.createElement("div");
    div.textContent = str || "";
    return div.innerHTML;
}}

function escapeRegex(str) {{
    return str.replace(/[.*+?^${{}}()|[\\]\\\\]/g, "\\\\$&");
}}

// ============================================================
// HIGHLIGHT en nombre de sistema (header)
// ============================================================
function highlightText(elemento, texto) {{
    if (!texto) {{
        elemento.innerHTML = escapeHTML(elemento.textContent);
        return;
    }}
    var regex = new RegExp("(" + escapeRegex(texto) + ")", "gi");
    var nombreSpan = elemento.querySelector(".system-name");
    if (nombreSpan) {{
        var nombreOriginal = nombreSpan.getAttribute("data-original");
        if (!nombreOriginal) {{
            nombreOriginal = nombreSpan.textContent;
            nombreSpan.setAttribute("data-original", nombreOriginal);
        }}
        nombreSpan.innerHTML = escapeHTML(nombreOriginal).replace(regex, "<mark>$1</mark>");
    }}
}}

// ============================================================
// EVENTOS
// ============================================================

// Busqueda
document.getElementById("searchInput").addEventListener("input", function() {{
    filtroTexto = this.value;
    aplicarFiltros();
}});

// Filtro por sistema
document.getElementById("sistemaFilter").addEventListener("change", function() {{
    filtroSistema = this.value;
    aplicarFiltros();
}});

// Click en headers de sistema (delegacion de eventos)
document.getElementById("sistemasContainer").addEventListener("click", function(e) {{
    var header = e.target.closest(".system-header");
    if (header) {{
        var idx = header.getAttribute("data-idx");
        toggleSection(parseInt(idx));
        return;
    }}
    var btnCopiar = e.target.closest(".btn-copiar");
    if (btnCopiar) {{
        copiarRuta(btnCopiar);
    }}
}});

// Expandir/colapsar todos
document.getElementById("btnExpandAll").addEventListener("click", toggleTodos);

// Atajos de teclado
document.addEventListener("keydown", function(e) {{
    if ((e.ctrlKey && e.key === "f") || (e.key === "/" && document.activeElement.tagName !== "INPUT")) {{
        e.preventDefault();
        document.getElementById("searchInput").focus();
    }}
    if (e.key === "Escape") {{
        document.getElementById("searchInput").value = "";
        filtroTexto = "";
        aplicarFiltros();
        document.getElementById("searchInput").blur();
    }}
}});

// ============================================================
// INICIO
// ============================================================
aplicarFiltros();
</script>

</body>
</html>"""

    # --- Escribir el archivo ---
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(contenido)

    # --- Mostrar resultado ---
    print()
    print("=" * 60)
    print("  INVENTARIO HTML GENERADO EXITOSAMENTE")
    print("=" * 60)
    print(f"  Archivo: {ruta_salida}")
    print()
    print("  --- Resumen ---")
    print(f"  Total ROMs:          {total_roms}")
    print(f"  Total sistemas:      {total_sistemas}")
    print(f"  Tamano total:        {tamano_total}")
    print("=" * 60)