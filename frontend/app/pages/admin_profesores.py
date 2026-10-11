import flet as ft
from app.ui.components.sidebar import create_sidebar
from app.ui.components.topbar import create_topbar

# Paleta cromática de la identidad visual
BG_PAGE = "#F5F7F7"
BG_WHITE = "#FFFFFF"
BORDER_COLOR = "#EAE6E1"
TEAL_DARK = "#0B4F4F"
TEAL = "#0D6E6E"
TEAL_LIGHT = "#E6F2F2"
TEXT_COLOR = "#1E2A29"
MUTED = "#5C6B69"

# Badges de estado
BADGE_GREEN_BG = "#EBFEE6"
BADGE_GREEN_TXT = "#10B981"
BADGE_YELLOW_BG = "#FFF9E6"
BADGE_YELLOW_TXT = "#F59E0B"
BADGE_RED_BG = "#FEEBEB"
BADGE_RED_TXT = "#EF4444"


def get_admin_profesores_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa de la Nómina del Personal Docente."""

    # ==================== 1. BARRA DE BÚSQUEDA Y FILTROS ====================
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
                    hint_text="Buscar docente por especialidad o apellido...",
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

    btn_nuevo_profesor = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                ft.Text("Nuevo Profesor", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
            ],
        ),
        bgcolor=TEAL,
        height=41,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding(24, 12, 24, 12),
        ),
        on_click=lambda _: page.go("/admin/profesores/nuevo"),
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
                    filtro_dropdown(
                        "Área: Todas",
                        125,
                        ["Todas", "Ciencias Exactas", "Lenguas", "Educación Física", "Tecnología"],
                    ),
                    filtro_dropdown(
                        "Estado: Activo",
                        144,
                        ["Todos", "Activo", "Licencia", "Inactivo"],
                    ),
                ],
            ),
            btn_nuevo_profesor,
        ],
    )

    # ==================== 2. TABLA DE PROFESORES ====================
    profesores_data = [
        {
            "legajo": "#20101",
            "dni": "31.902.115",
            "apellido": "Martínez",
            "nombre": "Román Alberto",
            "especialidad": "Ciencias Naturales / Física",
            "email": "r.martinez@educar.edu.ar",
            "telefono": "3624-912881",
            "estado": "Activo",
        },
        {
            "legajo": "#20102",
            "dni": "29.448.109",
            "apellido": "Sánchez",
            "nombre": "Guillermina",
            "especialidad": "Matemática Aplicada",
            "email": "g.sanchez@educar.edu.ar",
            "telefono": "3624-402919",
            "estado": "Activo",
        },
        {
            "legajo": "#20103",
            "dni": "35.102.394",
            "apellido": "Vargas",
            "nombre": "Esteban Carlos",
            "especialidad": "Educación Física / Natación",
            "email": "e.vargas@educar.edu.ar",
            "telefono": "3624-001229",
            "estado": "Licencia",
        },
        {
            "legajo": "#20104",
            "dni": "33.910.224",
            "apellido": "Duarte",
            "nombre": "María Florencia",
            "especialidad": "Lengua y Literatura",
            "email": "f.duarte@educar.edu.ar",
            "telefono": "3624-114402",
            "estado": "Activo",
        },
        {
            "legajo": "#20105",
            "dni": "28.990.124",
            "apellido": "Ortega",
            "nombre": "Luis Humberto",
            "especialidad": "Informática / Robótica",
            "email": "l.ortega@educar.edu.ar",
            "telefono": "3624-556601",
            "estado": "Inactivo",
        },
    ]

    header_table = ft.Container(
        height=48,
        bgcolor=TEAL_LIGHT,
        padding=ft.Padding(16, 0, 16, 0),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(width=90, content=ft.Text("Legajo", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
                ft.Container(width=120, content=ft.Text("DNI", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
                ft.Container(width=150, content=ft.Text("Apellido", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
                ft.Container(width=150, content=ft.Text("Nombre", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
                ft.Container(width=220, content=ft.Text("Especialidad Principal", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
                ft.Container(width=220, content=ft.Text("Correo Electrónico", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
                ft.Container(width=120, content=ft.Text("Teléfono", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
                ft.Container(width=100, content=ft.Text("Estado", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
                ft.Container(expand=True, alignment=ft.Alignment(1, 0), content=ft.Text("Acciones", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
            ],
        ),
    )

    def estado_badge(estado: str) -> ft.Container:
        if estado == "Activo":
            bg, color = BADGE_GREEN_BG, BADGE_GREEN_TXT
        elif estado == "Licencia":
            bg, color = BADGE_YELLOW_BG, BADGE_YELLOW_TXT
        else:
            bg, color = BADGE_RED_BG, BADGE_RED_TXT

        return ft.Container(
            padding=ft.Padding(8, 4, 8, 4),
            bgcolor=bg,
            border_radius=4,
            content=ft.Text(estado, size=12, weight=ft.FontWeight.W_600, color=color),
        )

    def profesor_row(item: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=90, content=ft.Text(item["legajo"], size=14, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=120, content=ft.Text(item["dni"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=150, content=ft.Text(item["apellido"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=150, content=ft.Text(item["nombre"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=220, content=ft.Text(item["especialidad"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=220, content=ft.Text(item["email"], size=14, color=MUTED)),
                    ft.Container(width=120, content=ft.Text(item["telefono"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=100, content=estado_badge(item["estado"])),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=12,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    icon_size=16,
                                    icon_color=TEAL,
                                    tooltip="Editar",
                                    padding=0,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_size=16,
                                    icon_color=BADGE_RED_TXT,
                                    tooltip="Eliminar",
                                    padding=0,
                                ),
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
                *[profesor_row(p) for p in profesores_data],
            ],
        ),
    )

    # ==================== 3. ENSAMBLE DEL LAYOUT ====================
    sidebar = create_sidebar(page, active_route="/admin/profesores")
    topbar = create_topbar(page, titulo="Nómina del Personal Docente")

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
        page.title = "Educar SGE - Personal Docente"
        page.padding = 0
        page.bgcolor = BG_PAGE
        page.add(get_admin_profesores_view(page))

    ft.run(main)