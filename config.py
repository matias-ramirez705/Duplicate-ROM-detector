# ============================================================
# config.py — Configuracion del detector de duplicados R36S
# ============================================================
# Modifica este archivo para personalizar el comportamiento
# del script sin tocar la logica principal.
# ============================================================

# --------------------------------------------------
# RUTA BASE: Carpeta raiz donde estan las carpetas
# de sistemas (NES, SNES, GBA, etc.)
# Cambia esta ruta a la de tu R36S o carpeta de ROMs.
# --------------------------------------------------
# Ejemplo Windows:  r"C:\Roms_R36S"
# Ejemplo Linux/Mac: "/home/usuario/roms"
# Para R36S conectado por USB: normalmente aparece como
# una letra de unidad (ej: E:\ o F:\)
RUTA_BASE = r"C:\Roms_R36S"  # <--- CAMBIA ESTO

# --------------------------------------------------
# ARCHIVO DE SALIDA CSV
# --------------------------------------------------
# Ruta y nombre del archivo CSV que se generara con
# los resultados del analisis.
SALIDA_CSV = "reporte_duplicados.csv"

# --------------------------------------------------
# EXTENSIONES DE ROMS A ANALIZAR
# --------------------------------------------------
# Solo se procesaran archivos con estas extensiones.
# Agrega o quita extensiones segun tus necesidades.
# (Todo en minusculas)
EXTENSIONES_VALIDAS = [
    ".nes",    # Nintendo Entertainment System
    ".sfc",    # Super Nintendo (Super Famicom)
    ".smc",    # Super Nintendo (otra extension comun)
    ".gba",    # Game Boy Advance
    ".gbc",    # Game Boy Color
    ".gb",     # Game Boy
    ".nds",    # Nintendo DS
    ".n64",    # Nintendo 64
    ".z64",    # Nintendo 64 (otra extension)
    ".smd",    # Sega Mega Drive / Genesis
    ".gen",    # Sega Genesis
    ".bin",    # Generico (multiples sistemas)
    ".cue",    # Imagenes CD (PS1, Sega CD, etc.)
    ".iso",    # Imagenes ISO
    ".pce",    # PC Engine / TurboGrafx-16
    ".ngp",    # Neo Geo Pocket
    ".ngc",    # Neo Geo Pocket Color
    ".ws",     # WonderSwan
    ".wsc",    # WonderSwan Color
    ".fds",    # Famicom Disk System
    ".a26",    # Atari 2600
    ".a78",    # Atari 7800
    ".lnx",    # Atari Lynx
    ".sms",    # Sega Master System
    ".gg",     # Game Gear
    ".32x",    # Sega 32X
    ".s32x",   # Sega 32X (otra extension)
    ".cdi",    # Dreamcast / otros
    ".gdi",    # Dreamcast
    ".cso",    # PSP (CSO comprimido)
    ".pbp",    # PSP (EBOOT)
    ".m3u",    # Playlist multi-disco
    ".zip",    # ROMs comprimidas
    ".7z",     # ROMs comprimidas 7z

    # --- Ports / Scripts / Engines ---
    ".sh",       # Scripts de lanzamiento (ports, ej: "Grand Theft Auto San Andreas.sh")
    ".libretro", # Configuracion de core libretro (ports)
    ".exe",      # Ejecutables Windows (ports PC)
    ".desktop",  # Entradas de escritorio Linux (ports)
    ".py",       # Scripts Python (algunos ports)
]

# --------------------------------------------------
# UMBRAL DE SIMILITUD PARA NOMBRES
# --------------------------------------------------
# Valor entre 0 y 100.
# - 100 = nombres identicos (despues de limpiar tags)
# - 85-95 = buena deteccion de duplicados con variaciones
#   de region/idioma/revision
# - 70-84 = mas agresivo, puede dar falsos positivos
# - Menos de 70 = no recomendado
# Recomendado: 85
UMBRAL_SIMILITUD = 85

# --------------------------------------------------
# EXCLUIR CARPETAS (lista negra)
# --------------------------------------------------
# Nombres de carpetas que se omitiran completamente.
# Util para carpetas de sistema, saves, estados, etc.
EXCLUIR_CARPETAS = [
    "saves",
    "save_states",
    "states",
    "configs",
    "system",
    "bios",
    "thumbnails",
    "images",
    "covers",
    "boxart",
    ".git",
    "__pycache__",
]

# --------------------------------------------------
# CALCULAR HASH MD5 (duplicados exactos)
# --------------------------------------------------
# Si es True, calcula el hash MD5 de cada archivo para
# detectar duplicados EXACTOS (mismo contenido).
# Si es False, solo compara por nombre similar.
# Nota: False es mucho mas rapido.
CALCULAR_HASH = True

# --------------------------------------------------
# EXTENSIONES SIN HASH (no calcular MD5)
# --------------------------------------------------
# Archivos con estas extensiones NO se les calcula el
# hash MD5, aunque CALCULAR_HASH sea True.
#
# Esto evita falsos positivos en archivos de configuracion
# o scripts que comparten la misma plantilla/base pero
# corresponden a juegos diferentes.
#
# Ejemplo: los archivos .libretro son configs que usan
# la misma estructura para todos los ports, entonces
# "2048.libretro" y "anarch.libretro" tienen el mismo
# hash pero son juegos completamente distintos.
#
# Estos archivos SE SIGUEN ESCANEANDO y se detectan
# duplicados por NOMBRE SIMILAR, solo se salta el hash.
EXTENSIONES_SIN_HASH = [
    ".libretro",  # Config de core libretro (misma plantilla para todos)
    ".sh",        # Scripts de lanzamiento (pueden compartir template)
    ".desktop",   # Entradas de escritorio Linux (misma estructura)
    ".py",        # Scripts Python (posible template compartido)
]

# --------------------------------------------------
# LIMITE DE TAMANIO PARA HASH (en MB)
# --------------------------------------------------
# Archivos mas grandes que este limite se saltaran
# el calculo de hash. Se establecera hash = "".
# -1 = sin limite (procesar todos)
LIMITE_TAMANIO_HASH_MB = 100

# --------------------------------------------------
# GENERAR NOMBRE SUGERIDO
# --------------------------------------------------
# Si es True, intenta generar un nombre "limpio"
# quitando tags de region, idioma, codigo, etc.
# Ejemplo: "Super Mario World (USA) [!]" -> "Super Mario World"
GENERAR_NOMBRE_SUGERIDO = True

# --------------------------------------------------
# PATRONES A LIMPIAR DEL NOMBRE
# --------------------------------------------------
# Expresiones regulares que se quitaran al generar
# el nombre sugerido. Cada patron se aplica en orden.
PATRONES_LIMPIEZA_NOMBRE = [
    # Tags entre parentesis: (USA), (Japan), (E), (J), etc.
    r"\([^)]*\)",
    # Tags entre corchetes: [!], [b], [h1C], [T+Eng], etc.
    r"\[[^\]]*\]",
    # Tags entre llaves: {h}, etc.
    r"\{[^}]*\}",
    # Codigo de dump: Rev A, Rev B, v1.0, v1.1, etc.
    r"\b(Rev\s*[A-Z0-9]+|v\d+\.\d+)\b",
    # Separadores multiples: "  " -> " "
    r"\s{2,}",
]

# --------------------------------------------------
# MAPA DE CARPETAS A NOMBRES DE SISTEMA AMIGABLES
# --------------------------------------------------
# Convierte los nombres de carpeta de RetroArch
# en nombres mas legibles para el reporte.
# Agrega tus carpetas personalizadas aqui.
MAPA_SISTEMAS = {
    # === Nintendo ===
    "famicom": "NES / Famicom",
    "nes": "NES / Famicom",
    "sfc": "SNES / Super Famicom",
    "snes": "SNES / Super Famicom",
    "snes-hacks": "SNES / Hacks",
    "snes-msu1": "SNES / MSU-1",
    "snesmsu1": "SNES / MSU-1",
    "sgb": "Super Game Boy",
    "sgb-msu1": "Super Game Boy / MSU-1",
    "satellaview": "Satellaview (SNES)",
    "sufami": "SuFami Turbo (SNES)",
    "gba": "Game Boy Advance",
    "gba2players": "GBA / 2 Jugadores",
    "gbc": "Game Boy Color",
    "gbc2players": "GBC / 2 Jugadores",
    "gb": "Game Boy",
    "gb2players": "GB / 2 Jugadores",
    "n64": "Nintendo 64",
    "n64dd": "Nintendo 64DD",
    "nds": "Nintendo DS",
    "3ds": "Nintendo 3DS",
    "gamecube": "GameCube",
    "wii": "Nintendo Wii",
    "wiiu": "Nintendo Wii U",
    "switch": "Nintendo Switch",
    "switchupdates": "Switch / Actualizaciones",
    "virtualboy": "Virtual Boy",
    "pokemini": "Pokemon Mini",
    "pokemonmini": "Pokemon Mini",
    "fds": "Famicom Disk System",
    "pico": "Nintendo Pico",

    # === Sega ===
    "genesis": "Mega Drive / Genesis",
    "megadrive": "Mega Drive / Genesis",
    "megadrive-msu": "Mega Drive / MSU-1",
    "mastersystem": "Master System",
    "segacd": "Sega CD / Mega CD",
    "megacd": "Sega CD / Mega CD",
    "sega32x": "Sega 32X",
    "32x": "Sega 32X",
    "saturn": "Sega Saturn",
    "dreamcast": "Sega Dreamcast",
    "gamegear": "Game Gear",
    "segastv": "Sega Saturn / ST-V",

    # === PlayStation ===
    "psx": "PlayStation",
    "psx-multidisc": "PlayStation / Multi-disco",
    "ps2": "PlayStation 2",
    "ps3": "PlayStation 3",
    "ps4": "PlayStation 4",
    "psp": "PlayStation Portable",
    "pspminis": "PSP / Minis",
    "psvita": "PlayStation Vita",

    # === Xbox ===
    "xbox": "Xbox",
    "xbox360": "Xbox 360",

    # === Neo Geo ===
    "neogeo": "Neo Geo / Arcade",
    "neogeo64": "Neo Geo 64",
    "neogeocd": "Neo Geo CD",

    # === Arcade ===
    "arcade": "Arcade / MAME",
    "mame": "MAME / Arcade",
    "mame2003": "MAME 2003 / Arcade",
    "hbmame": "HB MAME / Arcade",
    "fbneo": "FinalBurn Neo / Arcade",
    "cps1": "CPS-1 / Arcade",
    "cps2": "CPS-2 / Arcade",
    "cps3": "CPS-3 / Arcade",
    "naomi": "Naomi / Arcade",
    "naomi2": "Naomi 2 / Arcade",
    "atomiswave": "Atomiswave / Arcade",
    "hikaru": "Hikaru / Arcade",
    "namco2x6": "Namco System 246 / Arcade",
    "namco3xx": "Namco System 357 / Arcade",
    "triforce": "Triforce / Arcade",
    "gaelco": "Gaelco / Arcade",
    "sega32x": "Sega 32X",
    "model2": "Model 2 / Arcade",
    "model3": "Model 3 / Arcade",
    "chihiro": "Chihiro / Arcade",
    "zinc": "Zinc / Arcade",
    "cave": "CAVE / Arcade",
    "jaguar": "Atari Jaguar",
    "karaoke": "Karaoke / Arcade",
    "teknoparrot": "TeknoParrot / Arcade",

    # === Computadoras ===
    "amiga": "Amiga",
    "amiga1200": "Amiga 1200",
    "amiga4000": "Amiga 4000",
    "amiga500": "Amiga 500",
    "amigacd32": "Amiga CD32",
    "amigacdtv": "Amiga CDTV",
    "c64": "Commodore 64",
    "c128": "Commodore 128",
    "vic20": "VIC-20",
    "c16": "Commodore 16",
    "c20": "Commodore 16/Plus4",
    "cplus4": "Commodore Plus/4",
    "pet": "Commodore PET",
    "msx": "MSX",
    "msx1": "MSX1",
    "msx2": "MSX2",
    "msx2+": "MSX2+",
    "msxturbor": "MSX Turbo R",
    "pc88": "PC-88",
    "pc98": "PC-98",
    "x1": "Sharp X1",
    "x68000": "Sharp X68000",
    "fm7": "Fujitsu FM-7",
    "fmtowns": "FM Towns",
    "dos": "MS-DOS / PC",
    "windows": "Windows",
    "exodos": "ExoDOS / PC",
    "exowin3x": "ExoWin3x / PC",
    "exowin9x": "ExoWin9x / PC",
    "apple2": "Apple II",
    "apple2gs": "Apple IIGS",
    "atari800": "Atari 800",
    "atarist": "Atari ST",
    "atarijaguar": "Atari Jaguar",
    "atarixegs": "Atari XEGS",
    "xegs": "Atari XEGS",
    "atom": "Acorn Atom",
    "bbcmicro": "BBC Micro",
    "electron": "Acorn Electron",
    "archimedes": "Acorn Archimedes",
    "orica": "Oric Atmos",
    "oricatmos": "Oric Atmos",
    "thomson": "Thomson",
    "samcoupe": "SAM Coupé",
    "dragon32": "Dragon 32",
    "coco": "TRS-80 CoCo",
    "coco3": "TRS-80 CoCo 3",
    "ti99": "Texas Instruments TI-99",
    "p2000t": "Philips P2000T",
    " Enterprise": "Enterprise",
    "bk": "BK-0010",
    "palm": "Palm OS",
    "j2me": "Java ME / Movil",
    "Android": "Android",
    "steam": "Steam / PC",
    "gog": "GOG / PC",

    # === PC Engines ===
    "pcengine": "PC Engine / TurboGrafx-16",
    "pcenginecd": "PC Engine CD",
    "supergrafx": "SuperGrafx",
    "turbografx": "TurboGrafx-16",
    "turbografxcd": "TurboGrafx-CD",

    # === Atari Clasico ===
    "atari2600": "Atari 2600",
    "atari5200": "Atari 5200",
    "atari7800": "Atari 7800",
    "atarilynx": "Atari Lynx",
    "lynx": "Atari Lynx",

    # === Otras consolas ===
    "3do": "3DO",
    "cdi": "Philips CD-i",
    "gameandwatch": "Game & Watch",
    "gamecom": "Game.com",
    "gmaster": "Game Master",
    "gp32": "GP32",
    "megaduck": "Mega Duck",
    "ngage": "N-Gage",
    "ngp": "Neo Geo Pocket",
    "ngpc": "Neo Geo Pocket Color",
    "wonderswan": "WonderSwan",
    "wonderswancolor": "WonderSwan Color",
    "wswan": "WonderSwan",
    "wswanc": "WonderSwan Color",
    "supervision": "Watara Supervision",
    "gamate": "Gamate",
    "gamepock": "Game Pocket",
    "pv1000": "PV-1000",
    "vc4000": "VC 4000",
    " CreatiVision": "CreatiVision",
    "advision": "Adventure Vision",
    "crvision": "CreatiVision",
    "loopy": "Loopy / Casio",
    "uzefox": "Uzebox",
    "uzebox": "Uzebox",
    "vircon32": "Vircon32",
    "videopac": "Videopac / Odyssey 2",
    "odyssey2": "Magnavox Odyssey 2",
    "vg5k": "VG-5000",
    "vsmile": "V.Smile",
    "lcdgames": "LCD / Juegos de Bolsillo",
    "tvgames": "Juegos de TV",

    # === Computadoras antiguas / raras ===
    "aquarius": "Aquarius",
    "alg": "Algorithm / Logic",
    "adam": "Coleco Adam",
    "cassettevision": "Cassette Vision",
    "supracan": "SupraCan",
    "arcadia": "Arcadia 2001",
    "apfm1000": "Archanoid / PlayFM",
    "puzzlescript": "PuzzleScript",
    "tic80": "TIC-80",
    "pico-8": "PICO-8",
    "pico8": "PICO-8",
    "lowresnx": "LowRes NX",
    "wasm4": "WASM-4",

    # === Motores y ports (no son sistemas de ROMs) ===
    "scummvm": "ScummVM / Aventuras",
    "easyrpg": "EasyRPG / RPG Maker",
    "gemrb": "GemRB / Infinity Engine",
    "openbor": "OpenBOR / Beats of Rage",
    "mugen": "MUGEN / Fighting Engine",
    "love": "Love2D / Engine",
    "love2d": "Love2D / Engine",
    "solarus": "Solarus / Engine",
    "flash": "Flash / Browser",
    "ports": "Ports / PC",
    "doom": "DOOM / Engine",
    "doom3": "DOOM 3 / Engine",
    "prboom": "PrBoom+ / DOOM Engine",
    "gzdoom": "GZDoom / Engine",
    "raze": "Raze / Build Engine",
    "eduke32": "eDuke32 / Duke3D",
    "ecwolf": "ecwolf / Wolf3D",
    "wolf": "Wolfenstein 3D",
    "quake": "Quake / Engine",
    "quake2": "Quake 2 / Engine",
    "halflife": "Half-Life / Engine",
    "rtcw": "Return to Castle Wolfenstein",
    "daphne": "DAPHNE / LaserDisc",
    "singe": "Singe / LaserDisc",

    # === Otros (multimedia, herramientas, etc.) ===
    "backup": "Backup (no escanear)",
    "bgmusic": "Musica de fondo",
    "movies": "Peliculas / Videos",
    "videos": "Videos",
    "images": "Imagenes",
    "launchimages": "Imagenes de lanzamiento",
    "tools": "Herramientas",
    "tutor": "Tutoriales",
    "vmu": "VMU / Visual Memory",
    "karaoke": "Karaoke",
    "cannonball": "Cannonball / OutRun Engine",
    "cavestory": "Cave Story",
    "cdogs": "C-Dogs",
    "cgenius": "Commander Genius",
    "devilutionx": "DevilutionX / Diablo",
    "dinothawr": "Dinothawr",
    "dice": "DICE / Engine",
    "ghostship": "Ghost Ship",
    "ikemen": "Ikemen GO / Fighting",
    "onscripter": "ONScripter / Visual Novel",
    "openjazz": "OpenJazz",
    "openlara": "OpenLara / Tomb Raider",
    "reminiscence": "Reminiscence / Flashback",
    "sonic-mania": "Sonic Mania",
    "sonic3-air": "Sonic 3 AIR",
    "sonicretro": "Sonic Retro",
    "superbroswar": "Super Bros. War",
    "theforceengine": "The Force Engine",
    "corsixth": "CorsixTH / Theme Hospital",
    "bennugd": "BennuGD / Engine",
    "fpinball": "Future Pinball",
    "pinballfx": "Pinball FX",
    "pinballfx2": "Pinball FX 2",
    "pinballfx3": "Pinball FX 3",
    "pinballm": "Pinball M",
    "vpinball": "Visual Pinball",
    "zaccariapinball": "Zaccaria Pinball",
    "cave": "CAVE / Shoot-em-up",
    "starship": "StarShip",
    "camplynx": "Camp Lynx",
    "epic": "Epic / Engine",
    "piece": "Piece / Engine",
    "bsyndrome": "B-Syndrome",
    "bstone": "Blake Stone",
    "multivision": "MultiVision",
    "mv": "MultiVision",
    "msumd": "MegaDrive / USB",
    "spectravideo": "Spectravideo",
    "laseractive": "LaserActive",
    "channelf": "Channel F",
    "coleco": "ColecoVision",
    "colecovision": "ColecoVision",
    "intellivision": "Intellivision",
    "vectrex": "Vectrex",
    "sg-1000": "SG-1000",
    "sg1000": "SG-1000",
    "arduboy": "Arduboy",
    "astrocade": "Astrocade",
    "tvc": "TVC / Videoton",
    "zx81": "ZX Spectrum 81",
    "zxspectrum": "ZX Spectrum",
    "pegasus": "Pegasus",
    "2ship": "2Ship",
    "pdark": "Perfect Dark",
    "soh": "Ship of Harkinian / OoT",
    "opengoal": "OpenGOAL / Jak & Daxter",
    "eagames": "EA Games / PC",
}