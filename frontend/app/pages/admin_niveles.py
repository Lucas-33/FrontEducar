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
TEXT_COLOR = "#1E2A29"
MUTED = "#5C6B69"
BADGE_NEUTRAL_BG = "#EEF1F0"


def get_admin_niveles_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa de Niveles Educativos y Estructura Académica."""

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
                        "Configuración del Sistema Educativo K-12",
                        size=12,
                        weight=ft.FontWeight.W_400,
                        color=MUTED,
                    ),
                    ft.Text(
                        "Niveles Educativos y Estructura Académica",
                        size=26,
                        weight=ft.FontWeight.W_600,
                        color=TEAL_DARK,
                    ),
                    ft.Text(
                        "Supervise la jerarquía de ciclos lectivos, cursos asociados y cupos de matrícula por nivel formativo.",
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
                        ft.Text("Nuevo Nivel", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
                    ],
                ),
                bgcolor=TEAL,
                height=41,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding(16, 11, 16, 11),
                ),
                on_click=lambda _: None,
            ),
        ],
    )

    # ==================== 2. RESUMEN INSTITUCIONAL ====================
    def indicador_kpi(valor: str, rotulo: str, ancho: int) -> ft.Column:
        return ft.Column(
            spacing=3,
            width=ancho,
            controls=[
                ft.Text(valor, size=26, weight=ft.FontWeight.W_600, color=BG_WHITE),
                ft.Text(rotulo, size=12, color=TEAL_LIGHT),
            ],
        )

    resumen_institucional = ft.Container(
        height=98,
        bgcolor=TEAL_DARK,
        border_radius=16,
        padding=22,
        content=ft.Row(
            spacing=32,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=4,
                    expand=True,
                    controls=[
                        ft.Text("Ciclo Lectivo 2025 — Activo y Homologado", size=20, weight=ft.FontWeight.W_600, color=BG_WHITE),
                        ft.Text("Estructura curricular completa conforme al Ministerio de Educación y normativas provinciales.", size=13, color=TEAL_LIGHT),
                    ],
                ),
                indicador_kpi("3", "Niveles K-12", 79),
                indicador_kpi("32", "Cursos totales", 77),
                indicador_kpi("1,248", "Matrícula total", 118),
            ],
        ),
    )

    # ==================== 3. TARJETAS DE NIVELES Y CURSOS ====================
    def curso_item(nombre: str, detalle: str) -> ft.Container:
        return ft.Container(
            height=62,
            bgcolor=BG_PAGE,
            border_radius=8,
            padding=12,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=3,
                        expand=True,
                        controls=[
                            ft.Text(nombre, size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                            ft.Text(detalle, size=12, color=MUTED),
                        ],
                    ),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16, color=TEAL),
                ],
            ),
        )

    def nivel_card(
        icono: ft.IconData,
        titulo: str,
        descripcion: str,
        alumnos: str,
        cursos: str,
        turno_info: str,
        cursos_asociados: list[tuple[str, str]],
    ) -> ft.Container:
        return ft.Container(
            width=358.67,
            height=546,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=16,
            content=ft.Column(
                spacing=0,
                controls=[
                    # Presentación del nivel (280 px)
                    ft.Container(
                        padding=24,
                        content=ft.Column(
                            spacing=16,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Container(
                                            width=44,
                                            height=44,
                                            bgcolor=TEAL_LIGHT,
                                            border_radius=12,
                                            alignment=ft.Alignment(0, 0),
                                            content=ft.Icon(icono, size=22, color=TEAL),
                                        ),
                                        ft.Container(
                                            padding=ft.Padding(8, 4, 8, 4),
                                            bgcolor=TEAL_LIGHT,
                                            border_radius=4,
                                            content=ft.Text("Activo", size=12, weight=ft.FontWeight.W_600, color=TEAL),
                                        ),
                                    ],
                                ),
                                ft.Column(
                                    spacing=6,
                                    controls=[
                                        ft.Text(titulo, size=24, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                                        ft.Text(descripcion, size=13, color=MUTED),
                                    ],
                                ),
                                ft.Row(
                                    spacing=24,
                                    controls=[
                                        ft.Column(
                                            spacing=3,
                                            expand=True,
                                            controls=[
                                                ft.Text(alumnos, size=30, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                                                ft.Text("Alumnos", size=12, color=MUTED),
                                            ],
                                        ),
                                        ft.Column(
                                            spacing=3,
                                            expand=True,
                                            controls=[
                                                ft.Text(cursos, size=30, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                                                ft.Text("Cursos", size=12, color=MUTED),
                                            ],
                                        ),
                                    ],
                                ),
                                ft.Container(
                                    padding=ft.Padding(8, 4, 8, 4),
                                    bgcolor=BADGE_NEUTRAL_BG,
                                    border_radius=4,
                                    content=ft.Text(turno_info, size=12, weight=ft.FontWeight.W_600, color=MUTED),
                                ),
                            ],
                        ),
                    ),
                    ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                    # Cursos asociados y acciones (265 px)
                    ft.Container(
                        padding=24,
                        content=ft.Column(
                            spacing=12,
                            controls=[
                                ft.Text("Cursos destacados del ciclo", size=12, weight=ft.FontWeight.W_600, color=MUTED),
                                *[curso_item(nombre, detalle) for nombre, detalle in cursos_asociados],
                                ft.Row(
                                    spacing=12,
                                    alignment=ft.MainAxisAlignment.START,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Container(
                                            height=41,
                                            bgcolor=BG_WHITE,
                                            border=ft.Border.all(1, BORDER_COLOR),
                                            border_radius=8,
                                            padding=ft.Padding(16, 11, 16, 11),
                                            alignment=ft.Alignment(0, 0),
                                            content=ft.Text("Editar", size=14, weight=ft.FontWeight.W_600, color=TEAL),
                                            on_click=lambda _: None,
                                        ),
                                        ft.TextButton(
                                            "Ver todos",
                                            style=ft.ButtonStyle(color=TEAL, padding=0),
                                            on_click=lambda _: None,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    fila_niveles = ft.Row(
        spacing=20,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            nivel_card(
                icono=ft.Icons.CHILD_CARE_OUTLINED,
                titulo="Nivel Inicial",
                descripcion="Salas de 3, 4 y 5 años (Jardín)",
                alumnos="214",
                cursos="6",
                turno_info="Turno Mañana y Tarde",
                cursos_asociados=[
                    ("Sala de 4 años — Turno Tarde", "Cupo: 28 / 30 alumnos (93%)"),
                    ("Sala de 5 años B — Turno Mañana", "Cupo: 25 / 25 alumnos (Lleno)"),
                ],
            ),
            nivel_card(
                icono=ft.Icons.SCHOOL_OUTLINED,
                titulo="Nivel Primario",
                descripcion="1ro a 7mo Grado (Educación General)",
                alumnos="582",
                cursos="14",
                turno_info="Jornada Completa",
                cursos_asociados=[
                    ("4to Grado A — Turno Mañana", "Cupo: 32 / 35 alumnos (91%)"),
                    ("6to Grado C — Turno Tarde", "Cupo: 30 / 35 alumnos (85%)"),
                ],
            ),
            nivel_card(
                icono=ft.Icons.ACCOUNT_BALANCE_OUTLINED,
                titulo="Nivel Secundario",
                descripcion="1ro a 6to Año (Ciclo Orientado)",
                alumnos="452",
                cursos="12",
                turno_info="Turno Mañana y Tarde",
                cursos_asociados=[
                    ("3er Año A — Turno Mañana", "Cupo: 34 / 35 alumnos (97%)"),
                    ("5to Año B — Turno Tarde", "Cupo: 31 / 35 alumnos (88%)"),
                ],
            ),
        ],
    )

    # ==================== 4. PANEL DE GESTIÓN Y JERARQUÍA ====================
    def estado_jerarquia(texto: str) -> ft.Container:
        return ft.Container(
            padding=ft.Padding(8, 4, 8, 4),
            bgcolor=TEAL_LIGHT,
            border_radius=4,
            content=ft.Text(texto, size=12, weight=ft.FontWeight.W_600, color=TEAL),
        )

    panel_gestion = ft.Container(
        height=112,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Jerarquía del Sistema Educativo Institucional", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Row(
                    spacing=20,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        estado_jerarquia("Nivel Inicial"),
                        ft.Icon(ft.Icons.ARROW_FORWARD, size=18, color=TEAL),
                        estado_jerarquia("Nivel Primario"),
                        ft.Icon(ft.Icons.ARROW_FORWARD, size=18, color=TEAL),
                        estado_jerarquia("Nivel Secundario"),
                        ft.Text(
                            "Continuidad pedagógica asegurada con articulación directa entre directores de nivel.",
                            size=13,
                            color=MUTED,
                            expand=True,
                        ),
                    ],
                ),
            ],
        ),
    )

    # ==================== 5. BANNER INFORMATIVO Y NOTA AL PIE ====================
    banner_info = ft.Container(
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
                    "Las modificaciones en las orientaciones o planes de estudio del nivel secundario deben ser informadas a Supervisión Pedagógica.",
                    size=13,
                    color=TEAL_DARK,
                    expand=True,
                ),
            ],
        ),
    )

    nota_pie = ft.Text(
        "* La apertura o cierre de divisiones está sujeta a la aprobación de cupos por parte del Consejo General de Educación.",
        size=11,
        color=MUTED,
    )

    # ==================== 6. ENSAMBLE DEL LAYOUT GENERAL ====================
    sidebar = create_sidebar(page, active_route="/admin/niveles")
    topbar = create_topbar(page, titulo="Niveles Educativos — Estructura académica")

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
                            resumen_institucional,
                            fila_niveles,
                            panel_gestion,
                            banner_info,
                            nota_pie,
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
        page.title = "Educar SGE - Niveles Educativos"
        page.padding = 0
        page.bgcolor = BG_PAGE
        page.add(get_admin_niveles_view(page))

    ft.run(main)