import flet as ft

# ==============================================================================
# 1. PALETA INSTITUCIONAL (Identidad Visual)
# ==============================================================================
TEAL_DARK = "#0B4F4F"        # Títulos principales, brand y headers
TEAL = "#0D6E6E"             # Botones de acción, acentos primarios y bordes activos
TEAL_LIGHT = "#E6F2F2"       # Fondos de badges activos, hover de menú y destacados
ORANGE = "#D97736"           # Call to action, botones destacados y advertencias

# ==============================================================================
# 2. LIENZOS Y SUPERFICIES (Fondos)
# ==============================================================================
BG_WHITE = "#FFFFFF"         # Fondo de tarjetas, tablas y modales
BG_PAGE = "#F5F7F7"          # Lienzo del panel administrativo interno
BG_PAGE_ALT = "#FDFBF9"      # Lienzo de vistas públicas (Home, Login, Formularios)
BG_SEARCH = "#F5F7F7"        # Fondo de buscador píldora en TopBar
BORDER_COLOR = "#EAE6E1"     # Borde gris estándar para tarjetas e inputs

# ==============================================================================
# 3. TEXTO Y TIPOGRAFÍA
# ==============================================================================
TEXT_COLOR = "#1E2A29"       # Texto principal
TEXT_SECONDARY = "#5C6B69"   # Subtítulos y descripciones
MUTED = "#5C6B69"            # Textos secundarios, labels y placeholders

# ==============================================================================
# 4. ESTADOS Y BADGES SEMÁNTICOS
# ==============================================================================
# Estados Verdes (Activo / Regular / En Línea)
ONLINE_GREEN = "#10B981"
GREEN_STATE = "#10B981"
GREEN_LIGHT = "#E6FAF2"
BADGE_GREEN_BG = "#EBFEE6"
BADGE_GREEN_TXT = "#10B981"

# Estados Amarillos / Ámbar (Pendiente / Licencia / Precaución)
AMBER_STATE = "#F59E0B"
ORANGE_LIGHT = "#FFEAD2"
BADGE_YELLOW_BG = "#FFF9E6"
BADGE_YELLOW_TXT = "#F59E0B"

# Estados Rojos (Inactivo / Baja / Bloqueado / Error)
RED_STATE = "#EF4444"
BADGE_RED_TXT = "#EF4444"
BADGE_RED_BG = "#FEEBEB"

# Estados Grises / Auxiliares
GRAY_LIGHT = "#EAEAEA"
BADGE_WARN_BG = "#FFF3E7"
BADGE_WARN_TXT = "#9A5427"

# ==============================================================================
# 5. DIMENSIONES ESTÁNDAR DE LA INTERFAZ
# ==============================================================================
SIDEBAR_WIDTH = 260          # Ancho fijo del menú lateral
TOPBAR_HEIGHT = 70           # Altura fija de la barra superior
CONTROL_HEIGHT = 41          # Altura estándar de TextFields, Dropdowns y Botones
BORDER_RADIUS = 8            # Radio de borde estándar para controles
CARD_RADIUS = 16             # Radio de borde estándar para tarjetas contenedoras