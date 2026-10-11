import flet as ft
from app.ui.components.sidebar import create_sidebar
from app.ui.components.topbar import create_topbar

# Paleta cromática y tokens visuales del sistema
BG_PAGE = "#F5F7F7"
BG_WHITE = "#FFFFFF"
BORDER_COLOR = "#EAE6E1"
TEAL_DARK = "#0B4F4F"
TEAL = "#0D6E6E"
TEAL_LIGHT = "#E6F2F2"
ORANGE = "#D97736"
TEXT_COLOR = "#1E2A29"
MUTED = "#5C6B69"

# Badges y avisos de estado
BADGE_WARN_BG = "#FFF3E7"
BADGE_WARN_TXT = "#A94C16"
BADGE_DANGER_BG = "#FBEFEE"
BADGE_DANGER_TXT = "#A6423A"


def get_admin_inscripciones_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa de la Bandeja de Solicitudes de Inscripción."""

    # ==================== 1. ENCABEZADO Y ACCIÓN SUPERIOR ====================
    encabezado_modulo = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                spacing=6,
                expand=True,
                controls=[
                    ft.Text(
                        "Admisiones y Gestión de Matrícula K-12",
                        size=12,
                        weight=ft.FontWeight.W_400,
                        color=MUTED,
                    ),
                    ft.Text(
                        "Bandeja de Solicitudes de Inscripción",
                        size=26,
                        weight=ft.FontWeight.W_600,
                        color=TEAL_DARK,
                    ),
                    ft.Text(
                        "Valide la documentación de aspirantes ingresantes, controle vacantes disponibles y formalice las altas de matrícula.",
                        size=14,
                        color=MUTED,
                    ),
                ],
            ),
            ft.Button(
                content=ft.Row(
                    spacing=8,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                        ft.Text("Nueva Solicitud", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
                    ],
                ),
                bgcolor=TEAL,
                height=41,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding(16, 11, 16, 11),
                ),
                on_click=lambda _: page.go("/admin/alumnos/nuevo"),
            ),
        ],
    )

    # ==================== 2. RESUMEN DE SOLICITUDES ====================
    def tarjeta_kpi(numero: str, descripcion: str, color_num: str) -> ft.Container:
        return ft.Container(
            expand=True,
            height=74,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=16,
            padding=18,
            content=ft.Row(
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(numero, size=28, weight=ft.FontWeight.W_600, color=color_num),
                    ft.Text(descripcion, size=13, color=MUTED, expand=True),
                ],
            ),
        )

    resumen_solicitudes = ft.Row(
        spacing=16,
        controls=[
            tarjeta_kpi("16", "Pendientes de validación documental", ORANGE),
            tarjeta_kpi("24", "Aprobadas y matriculadas este mes", TEAL_DARK),
            tarjeta_kpi("3", "Rechazadas o canceladas", TEAL_DARK),
        ],
    )

    # ==================== 3. BÚSQUEDA Y FILTROS ====================
    search_bar = ft.Container(
        height=43,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=8,
        padding=ft.Padding(12, 0, 12, 0),
        expand=True,
        content=ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SEARCH, size=16, color=MUTED),
                ft.TextField(
                    hint_text="Buscar por número de solicitud, aspirante o DNI...",
                    hint_style=ft.TextStyle(size=14, color=MUTED),
                    text_size=14,
                    color=TEXT_COLOR,
                    border=ft.InputBorder.NONE,
                    content_padding=ft.Padding(0, 0, 0, 10),
                    expand=True,
                ),
            ],
        ),
    )

    def filtro_desplegable(texto: str, ancho: int) -> ft.Container:
        return ft.Container(
            width=ancho,
            height=43,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=8,
            padding=ft.Padding(12, 0, 12, 0),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(texto, size=14, color=TEXT_COLOR),
                    ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=14, color=MUTED),
                ],
            ),
        )

    filtros_fila = ft.Row(
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            search_bar,
            filtro_desplegable("Nivel: Todos", 118),
            filtro_desplegable("Estado: Pendiente", 119),
            filtro_desplegable("Fecha: Últimos 30 días", 135),
        ],
    )

    # ==================== 4. TABLA DE REGISTROS ====================
    cabecera_tabla = ft.Container(
        height=42,
        bgcolor=TEAL_LIGHT,
        padding=ft.Padding(16, 13, 16, 13),
        content=ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(width=90, content=ft.Text("N° Solicitud", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=190, content=ft.Text("Aspirante", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=461, expand=True, content=ft.Text("Destino Solicitado", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=100, content=ft.Text("Ingreso", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=108, content=ft.Text("Estado", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=75, content=ft.Text("Acciones", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
            ],
        ),
    )

    solicitudes_data = [
        {
            "id": "#SOL-4928",
            "nombre": "Almirón, Santiago",
            "dni": "DNI 44.120.942",
            "destino": "5to Año B — Nivel Secundario",
            "turno": "Turno Tarde · Orientación Economía",
            "fecha": "10/10/2026",
            "estado": "Pendiente",
            "badge_bg": BADGE_WARN_BG,
            "badge_txt": BADGE_WARN_TXT,
            "seleccionado": True,
        },
        {
            "id": "#SOL-4929",
            "nombre": "Benítez, Martina",
            "dni": "DNI 45.892.110",
            "destino": "3er Año A — Nivel Secundario",
            "turno": "Turno Mañana · Ciclo Básico",
            "fecha": "09/10/2026",
            "estado": "Pendiente",
            "badge_bg": BADGE_WARN_BG,
            "badge_txt": BADGE_WARN_TXT,
            "seleccionado": False,
        },
        {
            "id": "#SOL-4930",
            "nombre": "Capra, Lautaro",
            "dni": "DNI 48.330.124",
            "destino": "6to Grado C — Nivel Primario",
            "turno": "Jornada Completa · Comedor y Deportes",
            "fecha": "08/10/2026",
            "estado": "Aprobada",
            "badge_bg": TEAL_LIGHT,
            "badge_txt": TEAL,
            "seleccionado": False,
        },
        {
            "id": "#SOL-4931",
            "nombre": "Díaz, Sofía Valentina",
            "dni": "DNI 50.114.992",
            "destino": "Sala de 5 años B — Nivel Inicial",
            "turno": "Turno Mañana · Servicio de Transporte",
            "fecha": "08/10/2026",
            "estado": "Aprobada",
            "badge_bg": TEAL_LIGHT,
            "badge_txt": TEAL,
            "seleccionado": False,
        },
        {
            "id": "#SOL-4932",
            "nombre": "Flores, Facundo Joaquín",
            "dni": "DNI 43.902.114",
            "destino": "6to Año A — Nivel Secundario",
            "turno": "Turno Mañana · Orientación Ciencias Naturales",
            "fecha": "07/10/2026",
            "estado": "Aprobada",
            "badge_bg": TEAL_LIGHT,
            "badge_txt": TEAL,
            "seleccionado": False,
        },
        {
            "id": "#SOL-4933",
            "nombre": "Giménez, Camila Belén",
            "dni": "DNI 45.102.399",
            "destino": "4to Grado A — Nivel Primario",
            "turno": "Turno Mañana · Vacante sin cupo disponible",
            "fecha": "06/10/2026",
            "estado": "Rechazada",
            "badge_bg": BADGE_DANGER_BG,
            "badge_txt": BADGE_DANGER_TXT,
            "seleccionado": False,
        },
    ]

    def solicitud_row(item: dict) -> ft.Container:
        return ft.Container(
            height=64,
            bgcolor=TEAL_LIGHT if item["seleccionado"] else BG_WHITE,
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            padding=ft.Padding(16, 14, 16, 14),
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=90,
                        content=ft.Text(item["id"], size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                    ),
                    ft.Column(
                        spacing=3,
                        width=190,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text(item["nombre"], size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                            ft.Text(item["dni"], size=11, color=MUTED),
                        ],
                    ),
                    ft.Column(
                        spacing=3,
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text(item["destino"], size=13, color=TEXT_COLOR),
                            ft.Text(item["turno"], size=11, color=MUTED),
                        ],
                    ),
                    ft.Container(
                        width=100,
                        content=ft.Text(item["fecha"], size=13, color=TEXT_COLOR),
                    ),
                    ft.Container(
                        width=108,
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    padding=ft.Padding(8, 4, 8, 4),
                                    bgcolor=item["badge_bg"],
                                    border_radius=4,
                                    content=ft.Text(
                                        item["estado"],
                                        size=12,
                                        weight=ft.FontWeight.W_600,
                                        color=item["badge_txt"],
                                    ),
                                ),
                            ]
                        ),
                    ),
                    ft.Container(
                        width=75,
                        content=ft.TextButton(
                            "Revisar",
                            style=ft.ButtonStyle(color=TEAL, padding=0),
                            on_click=lambda _: None,
                        ),
                    ),
                ],
            ),
        )

    tabla_contenedor = ft.Container(
        height=426,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            spacing=0,
            controls=[
                cabecera_tabla,
                *[solicitud_row(s) for s in solicitudes_data],
            ],
        ),
    )

    nota_tabla = ft.Text(
        "Seleccione una solicitud para desplegar la documentación adjunta, validar requisitos y formalizar el alta.",
        size=12,
        color=MUTED,
    )

    # ==================== 5. BLOQUE DE REVISIÓN DE SOLICITUD ====================
    # Panel Izquierdo: Datos del Aspirante
    panel_aspirante = ft.Container(
        width=420,
        height=394,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Ficha de Solicitud #SOL-4928", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Container(
                    padding=ft.Padding(8, 4, 8, 4),
                    bgcolor=BADGE_WARN_BG,
                    border_radius=4,
                    content=ft.Text("Pendiente de Validación", size=12, weight=ft.FontWeight.W_600, color=BADGE_WARN_TXT),
                ),
                ft.Text("Santiago Almirón", size=20, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Text("DNI: 44.120.942 · Fecha de Nacimiento: 14/05/2010", size=13, color=TEXT_COLOR),
                ft.Text("Destino: 5to Año División B — Nivel Secundario (Turno Tarde)", size=13, color=MUTED),
                # Tutor asociado
                ft.Container(
                    bgcolor=BG_PAGE,
                    border_radius=8,
                    padding=14,
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text("Tutor Responsable Registrado", size=12, weight=ft.FontWeight.W_600, color=MUTED),
                            ft.Text("Almirón, Carlos Alberto (Padre)", size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                            ft.Text("Contacto: 3624-912881 · c.almiron@tutor.com", size=12, color=MUTED),
                        ],
                    ),
                ),
                ft.Text("Domicilio Real Declarado: Av. Sarmiento 450, Resistencia, Chaco", size=13, color=TEXT_COLOR),
                ft.Text("Ingreso registrado vía portal web el 10/10/2026 09:14 hs", size=13, color=MUTED),
            ],
        ),
    )

    # Panel Derecho: Chequeos y Decisión Administrativa
    def item_chequeo(titulo: str, detalle: str) -> ft.Row:
        return ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=18, color=TEAL),
                ft.Column(
                    spacing=3,
                    expand=True,
                    controls=[
                        ft.Text(titulo, size=13, weight=ft.FontWeight.W_600, color=TEAL),
                        ft.Text(detalle, size=12, color=MUTED),
                    ],
                ),
            ],
        )

    panel_chequeos_decision = ft.Container(
        expand=True,
        height=394,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Verificación de Requisitos de Admisión", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Column(
                    spacing=14,
                    controls=[
                        item_chequeo("DNI y Partida de Nacimiento", "Archivos PDF digitalizados legibles y validados con Renaper."),
                        item_chequeo("Libre Deuda y Pase Escolar", "Certificado de pase legalizado de la institución de origen recibido."),
                        item_chequeo("Ficha Médica y Cartilla de Vacunación", "Apto físico y certificado bucodental en regla para inicio de clases."),
                    ],
                ),
                ft.Container(
                    height=50,
                    bgcolor=TEAL_LIGHT,
                    border_radius=8,
                    padding=16,
                    content=ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.INFO_OUTLINE, size=18, color=TEAL),
                            ft.Text(
                                "El curso de destino cuenta con 4 vacantes disponibles para concretar la matrícula inmediata.",
                                size=13,
                                color=TEAL_DARK,
                                expand=True,
                            ),
                        ],
                    ),
                ),
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.Button(
                            content=ft.Text("Aprobar Vacante", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
                            bgcolor=TEAL,
                            height=41,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.Padding(16, 11, 16, 11),
                            ),
                            on_click=lambda _: None,
                        ),
                        ft.Button(
                            content=ft.Text("Rechazar", size=14, weight=ft.FontWeight.W_600, color=TEAL),
                            bgcolor=BG_WHITE,
                            height=41,
                            style=ft.ButtonStyle(
                                side=ft.BorderSide(1, BORDER_COLOR),
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.Padding(16, 11, 16, 11),
                            ),
                            on_click=lambda _: None,
                        ),
                    ],
                ),
            ],
        ),
    )

    fila_revision_solicitud = ft.Row(
        spacing=20,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[panel_aspirante, panel_chequeos_decision],
    )

    nota_final = ft.Text(
        "* La aprobación de la solicitud genera automáticamente el número de legajo provisorio y habilita la facturación de matrícula en Secretaría.",
        size=11,
        color=MUTED,
    )

    # ==================== 6. ENSAMBLE DEL LAYOUT GENERAL ====================
    sidebar = create_sidebar(page, active_route="/admin/inscripciones")
    topbar = create_topbar(page, titulo="Inscripciones — Bandeja de solicitudes")

    main_content = ft.Container(
        expand=True,
        bgcolor=BG_PAGE,
        content=ft.Column(
            spacing=0,
            controls=[
                topbar,
                ft.Container(
                    expand=True,
                    padding=32,
                    content=ft.Column(
                        spacing=20,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            encabezado_modulo,
                            resumen_solicitudes,
                            filtros_fila,
                            tabla_contenedor,
                            nota_tabla,
                            fila_revision_solicitud,
                            nota_final,
                        ],
                    ),
                ),
            ],
        ),
    )

    return ft.Row(
        expand=True,
        spacing=0,
        controls=[sidebar, main_content],
    )


if __name__ == "__main__":
    def main(page: ft.Page):
        page.title = "Educar SGE - Bandeja de Inscripciones"
        page.padding = 0
        page.bgcolor = BG_PAGE
        page.add(get_admin_inscripciones_view(page))

    ft.run(main)