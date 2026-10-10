import flet as ft

# Paleta extraída del diseño Figma
BG_WHITE = "#FFFFFF"
BORDER_COLOR = "#EAE6E1"
TEAL_DARK = "#0B4F4F"
TEAL = "#0D6E6E"
TEAL_LIGHT = "#E6F2F2"
TEXT_COLOR = "#1E2A29"
MUTED = "#5C6B69"
ONLINE_GREEN = "#10B981"


def create_sidebar(page: ft.Page, active_route: str = "/admin/dashboard") -> ft.Container:
    """Genera la barra lateral de navegación para el panel interno Educar SGE."""

    # Mapeo de ítems del menú con sus iconos correspondientes
    items_menu = [
        ("Dashboard", "/admin/dashboard", ft.Icons.DASHBOARD_OUTLINED),
        ("Alumnos", "/admin/alumnos", ft.Icons.PEOPLE_OUTLINE),
        ("Profesores", "/admin/profesores", ft.Icons.WORK_OUTLINE),
        ("Niveles Educativos", "/admin/niveles", ft.Icons.SCHOOL_OUTLINED),
        ("Cursos", "/admin/cursos", ft.Icons.FOLDER_OPEN_OUTLINED),
        ("Materias", "/admin/materias", ft.Icons.MENU_BOOK_OUTLINED),
        ("Deportes", "/admin/deportes", ft.Icons.FITNESS_CENTER_OUTLINED),
        ("Horarios", "/admin/horarios", ft.Icons.ACCESS_TIME_OUTLINED),
        ("Inscripciones", "/admin/inscripciones", ft.Icons.DESCRIPTION_OUTLINED),
        ("Transporte", "/admin/transporte", ft.Icons.DIRECTIONS_BUS_OUTLINED),
        ("Comedor", "/admin/comedor", ft.Icons.RESTAURANT_OUTLINED),
        ("Usuarios y Permisos", "/admin/usuarios", ft.Icons.LOCK_OUTLINE),
        ("Reportes", "/admin/reportes", ft.Icons.BAR_CHART_OUTLINED),
    ]

    def item_sidebar(texto: str, ruta: str, icono: ft.IconData) -> ft.Container:
        es_activo = active_route == ruta

        return ft.Container(
            data=ruta,
            height=42,
            border_radius=8,
            padding=ft.Padding(16, 12, 16, 12),
            bgcolor=TEAL_LIGHT if es_activo else "transparent",
            on_click=lambda _: page.go(ruta),
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        icono,
                        size=18,
                        color=TEAL_DARK if es_activo else MUTED,
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Text(
                            texto,
                            size=14,
                            weight=ft.FontWeight.W_600 if es_activo else ft.FontWeight.W_500,
                            color=TEAL_DARK if es_activo else TEXT_COLOR,
                        ),
                    ),
                    # Indicador de selección activo (Rectangle 4x16 px)
                    ft.Container(
                        width=4,
                        height=16,
                        border_radius=2,
                        bgcolor=TEAL if es_activo else "transparent",
                    ),
                ],
            ),
        )

    # 1. Cabecera (Brand)
    brand_section = ft.Row(
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=36,
                height=36,
                bgcolor=TEAL,
                border_radius=18,
                alignment=ft.Alignment(0, 0),
                content=ft.Icon(ft.Icons.SCHOOL, color="white", size=18),
            ),
            ft.Column(
                spacing=2,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "Educar SGE",
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=TEAL_DARK,
                    ),
                    ft.Text(
                        "GESTIÓN INTERNA",
                        size=10,
                        weight=ft.FontWeight.W_600,
                        color=MUTED,
                    ),
                ],
            ),
        ],
    )

    # 2. Lista de Navegación con Scroll
    nav_list = ft.Column(
        spacing=4,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        controls=[item_sidebar(texto, ruta, icono) for texto, ruta, icono in items_menu],
    )

    # 3. Footer de estado del servidor
    footer_section = ft.Column(
        spacing=8,
        controls=[
            ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=8,
                        height=8,
                        bgcolor=ONLINE_GREEN,
                        border_radius=4,
                    ),
                    ft.Text(
                        "Servidor Online",
                        size=12,
                        weight=ft.FontWeight.W_400,
                        color=MUTED,
                    ),
                ],
            ),
            ft.Text(
                "v2.5.0-resistencia",
                size=11,
                weight=ft.FontWeight.W_400,
                color=MUTED,
            ),
        ],
    )

    # Contenedor raíz de la barra lateral (260px ancho)
    return ft.Container(
        width=260,
        bgcolor=BG_WHITE,
        border=ft.Border(right=ft.BorderSide(1, BORDER_COLOR)),
        padding=ft.Padding(16, 24, 16, 24),
        content=ft.Column(
            spacing=20,
            controls=[
                brand_section,
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                nav_list,
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                footer_section,
            ],
        ),
    )