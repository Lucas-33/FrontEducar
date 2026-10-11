import flet as ft
from app.ui.components.sidebar import create_sidebar
from app.ui.components.topbar import create_topbar

# Sa'ykuéra ha tokens visuales Figma-gui
BG_PAGE = "#F5F7F7"
BG_WHITE = "#FFFFFF"
BORDER_COLOR = "#EAE6E1"
TEAL_DARK = "#0B4F4F"
TEAL = "#0D6E6E"
TEAL_LIGHT = "#E6F2F2"
TEXT_COLOR = "#1E2A29"
MUTED = "#5C6B69"

# Sa'y estado-pe g̃uarã
BADGE_GREEN_BG = "#EBFEE6"
BADGE_GREEN_TXT = "#10B981"
BADGE_YELLOW_BG = "#FFF9E6"
BADGE_YELLOW_TXT = "#F59E0B"
BADGE_RED_BG = "#FEEBEB"
BADGE_RED_TXT = "#EF4444"


def get_admin_alumnos_view(page: ft.Page) -> ft.Row:
    """Omoheñói ha omoĩmba tembiapo lista de alumnos rehegua (Sidebar + TopBar + Tabla)."""

    # 1. Barra de Búsqueda ha Filtros
    search_input = ft.Container(
        width=280,
        height=41,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=8,
        padding=ft.Padding(12, 0, 12, 0),
        content=ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SEARCH, size=16, color=MUTED),
                ft.TextField(
                    hint_text="Buscar por nombre o legajo...",
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

    def filtro_dropdown(hint: str, width: int, opciones: list[str]) -> ft.Container:
        return ft.Container(
            width=width,
            height=41,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=8,
            content=ft.Dropdown(
                hint_text=hint,
                hint_style=ft.TextStyle(size=14, color=TEXT_COLOR),
                text_size=14,
                border=ft.InputBorder.NONE,
                content_padding=ft.Padding(12, 0, 8, 12),
                options=[ft.dropdown.Option(opc) for opc in opciones],
            ),
        )

    btn_nuevo_alumno = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                ft.Text("Nuevo Alumno", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
            ],
        ),
        bgcolor=TEAL,
        height=41,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding(24, 12, 24, 12),
        ),
        on_click=lambda _: page.go("/admin/alumnos/nuevo"),
    )

    filters_bar = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    search_input,
                    filtro_dropdown("Nivel: Todos", 135, ["Todos", "Inicial", "Primario", "Secundario"]),
                    filtro_dropdown("Curso: Todos", 140, ["Todos", "Sala 5", "4to Grado", "6to Grado", "3er Año", "5to Año", "6to Año"]),
                    filtro_dropdown("Estado: Activo", 145, ["Activo", "Regular", "Pendiente", "Inactivo"]),
                ],
            ),
            btn_nuevo_alumno,
        ],
    )

    # 2. Datos ha Tabla de Alumnos
    alumnos_data = [
        {"legajo": "#10245", "dni": "44.120.942", "apellido": "Almirón", "nombre": "Santiago", "nivel": "Secundario", "curso": "5to Año B", "estado": "Regular"},
        {"legajo": "#10246", "dni": "45.892.110", "apellido": "Benítez", "nombre": "Martina", "nivel": "Secundario", "curso": "3er Año A", "estado": "Regular"},
        {"legajo": "#10247", "dni": "48.330.124", "apellido": "Capra", "nombre": "Lautaro", "nivel": "Primario", "curso": "6to Grado C", "estado": "Regular"},
        {"legajo": "#10248", "dni": "50.114.992", "apellido": "Díaz", "nombre": "Sofía Valentina", "nivel": "Inicial", "curso": "Sala de 5 años B", "estado": "Pendiente"},
        {"legajo": "#10249", "dni": "43.902.114", "apellido": "Flores", "nombre": "Facundo Joaquín", "nivel": "Secundario", "curso": "6to Año A", "estado": "Regular"},
        {"legajo": "#10250", "dni": "45.102.399", "apellido": "Giménez", "nombre": "Camila Belén", "nivel": "Primario", "curso": "4to Grado A", "estado": "Inactivo"},
    ]

    header_table = ft.Container(
        height=48,
        bgcolor=TEAL_LIGHT,
        padding=ft.Padding(16, 0, 16, 0),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(width=100, content=ft.Text("Legajo", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
                ft.Container(width=140, content=ft.Text("DNI", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
                ft.Container(width=180, content=ft.Text("Apellido", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
                ft.Container(width=180, content=ft.Text("Nombre", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
                ft.Container(width=160, content=ft.Text("Nivel Educativo", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
                ft.Container(width=140, content=ft.Text("Curso", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
                ft.Container(width=120, content=ft.Text("Estado", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
                ft.Container(width=64, alignment=ft.Alignment(1, 0), content=ft.Text("Acciones", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
            ],
        ),
    )

    def estado_badge(estado: str) -> ft.Container:
        if estado == "Regular":
            bg, color = BADGE_GREEN_BG, BADGE_GREEN_TXT
        elif estado == "Pendiente":
            bg, color = BADGE_YELLOW_BG, BADGE_YELLOW_TXT
        else:
            bg, color = BADGE_RED_BG, BADGE_RED_TXT

        return ft.Container(
            padding=ft.Padding(8, 4, 8, 4),
            bgcolor=bg,
            border_radius=4,
            content=ft.Text(estado, size=12, weight=ft.FontWeight.W_600, color=color),
        )

    def alumno_row(item: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=100, content=ft.Text(item["legajo"], size=14, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=140, content=ft.Text(item["dni"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=180, content=ft.Text(item["apellido"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=180, content=ft.Text(item["nombre"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=160, content=ft.Text(item["nivel"], size=14, color=MUTED)),
                    ft.Container(width=140, content=ft.Text(item["curso"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=120, content=estado_badge(item["estado"])),
                    ft.Container(
                        width=64,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=12,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_size=16, icon_color=TEAL, tooltip="Editar", padding=0),
                                ft.IconButton(icon=ft.Icons.REMOVE_RED_EYE_OUTLINED, icon_size=16, icon_color=MUTED, tooltip="Ver legajo", padding=0),
                                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_size=16, icon_color=BADGE_RED_TXT, tooltip="Borrar", padding=0),
                            ],
                        ),
                    ),
                ],
            ),
        )

    table_container = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            spacing=0,
            controls=[
                header_table,
                *[alumno_row(a) for a in alumnos_data],
            ],
        ),
    )

    # 3. Paginación Inferior
    def btn_pagina(texto: str, activo: bool = False, icon: ft.IconData = None) -> ft.Container:
        return ft.Container(
            width=36,
            height=36,
            bgcolor=TEAL if activo else BG_WHITE,
            border=None if activo else ft.Border.all(1, BORDER_COLOR),
            border_radius=8,
            alignment=ft.Alignment(0, 0),
            content=ft.Icon(icon, size=16, color=TEXT_COLOR) if icon else ft.Text(
                texto,
                size=14,
                weight=ft.FontWeight.W_600 if activo else ft.FontWeight.W_400,
                color=BG_WHITE if activo else TEXT_COLOR,
            ),
        )

    pagination_bar = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text("Mostrando 1-6 de 1,248 alumnos matriculados", size=14, color=MUTED),
            ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    btn_pagina("", icon=ft.Icons.CHEVRON_LEFT),
                    btn_pagina("1", activo=True),
                    btn_pagina("2"),
                    btn_pagina("3"),
                    btn_pagina("", icon=ft.Icons.CHEVRON_RIGHT),
                ],
            ),
        ],
    )

    # 4. Ensamble General
    sidebar = create_sidebar(page, active_route="/admin/alumnos")
    topbar = create_topbar(page, titulo="Directorio de Alumnos Matriculados")

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
                        spacing=24,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            filters_bar,
                            table_container,
                            pagination_bar,
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
        page.title = "Educar SGE - Directorio de Alumnos"
        page.padding = 0
        page.bgcolor = BG_PAGE
        page.add(get_admin_alumnos_view(page))

    ft.run(main)