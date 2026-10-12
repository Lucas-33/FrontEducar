import flet as ft

# ==============================================================================
# 1. PALETA INSTITUCIONAL (Identidad Visual)
# ==============================================================================
TEAL_DARK = "#0B4F4F"        # Títulos principales, brand y headers[cite: 9, 12]
TEAL = "#0D6E6E"             # Botones de acción, acentos primarios y bordes activos[cite: 9, 19]
TEAL_LIGHT = "#E6F2F2"       # Fondos de badges activos, hover de menú y destacados[cite: 9, 12]
ORANGE = "#D97736"           # Call to action, botones destacados y advertencias visuales[cite: 9, 10, 18]

# ==============================================================================
# 2. LIENZOS Y SUPERFICIES (Fondos)
# ==============================================================================
BG_WHITE = "#FFFFFF"         # Fondo de tarjetas, tablas y modales[cite: 9, 18]
BG_PAGE = "#F5F7F7"          # Lienzo del panel administrativo interno[cite: 18, 19]
BG_PAGE_ALT = "#FDFBF9"      # Lienzo de vistas públicas (Home, Login, Formularios públicos)[cite: 15, 16]
BG_SEARCH = "#F5F7F7"        # Fondo de buscador píldora en TopBar[cite: 13]
BORDER_COLOR = "#EAE6E1"     # Borde gris estándar para tarjetas, inputs y divisores[cite: 9, 12, 13]

# ==============================================================================
# 3. TEXTO Y TIPOGRAFÍA
# ==============================================================================
TEXT_COLOR = "#1E2A29"       # Texto principal (negro atenuado)[cite: 9, 12]
TEXT_SECONDARY = "#5C6B69"   # Subtítulos y descripciones[cite: 9, 14]
MUTED = "#5C6B69"            # Textos secundarios, labels y placeholders[cite: 12, 13]

# ==============================================================================
# 4. ESTADOS Y BADGES SEMÁNTICOS
# ==============================================================================
# Estado Activo / Regular / En Línea[cite: 12, 19, 23]
ONLINE_GREEN = "#10B981"
BADGE_GREEN_BG = "#EBFEE6"
BADGE_GREEN_TXT = "#10B981"

# Estado Pendiente / Licencia / Precaución[cite: 19, 23]
BADGE_YELLOW_BG = "#FFF9E6"
BADGE_YELLOW_TXT = "#F59E0B"

# Estado Inactivo / Baja / Error / Borrado[cite: 19, 22, 23]
BADGE_RED_BG = "#FEEBEB"
BADGE_RED_TXT = "#EF4444"

# Advertencia Nutricional / Comedor[cite: 20]
BADGE_WARN_BG = "#FFF3E7"
BADGE_WARN_TXT = "#9A5427"

# ==============================================================================
# 5. DIMENSIONES ESTÁNDAR DE LA INTERFAZ
# ==============================================================================
SIDEBAR_WIDTH = 260          # Ancho fijo del menú lateral[cite: 12]
TOPBAR_HEIGHT = 70           # Altura fija de la barra superior[cite: 13]
CONTROL_HEIGHT = 41          # Altura estándar de TextFields, Dropdowns y Botones[cite: 19, 21]
BORDER_RADIUS = 8            # Radio de borde estándar para controles[cite: 12, 16, 21]
CARD_RADIUS = 16             # Radio de borde estándar para tarjetas contenedoras[cite: 18, 19, 21]