import flet as ft
from frontend.app.components.constants import (
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    MUTED,
    ONLINE_GREEN,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)


def portal_layout(
    page: ft.Page,
    titulo: str,
    active_route: str,
    content_controls: list[ft.Control],
    rol: str = "Padre",
    usuario_nombre: str = "Martín Gómez",
    usuario_sub: str = "Tutor responsable",
    spacing: int = 24,
) -> ft.Row:
    """
    Layout maestro para los portales de autogestión (Padres, Docentes y Alumnos).
    Adapta el sidebar y topbar con accesos pertinentes al rol autenticado.
    """

    # 1. MENÚS SEGÚN ROL
    if rol.lower() in ["padre", "familia", "tutor"]:
        items_menu = [
            ("Mis Hijos", "/portal/padre/dashboard", ft.Icons.FAMILY_RESTROOM_OUTLINED),
            ("Inscripción Cursado", "/portal/padre/inscripcion", ft.Icons.APP_REGISTRATION_OUTLINED),
            ("Deportes y Horarios", "/portal/padre/deportes", ft.Icons.FITNESS_CENTER_OUTLINED),
            ("Comedor y Transporte", "/portal/padre/servicios", ft.Icons.RESTAURANT_OUTLINED),
            ("Docentes de mis Hijos", "/portal/padre/docentes", ft.Icons.SCHOOL_OUTLINED),
        ]
        portal_badge = "PORTAL FAMILIAS"
    elif rol.lower() in ["docente", "profesor"]:
        items_menu = [
            ("Mi Panel", "/portal/docente/dashboard", ft.Icons.DASHBOARD_OUTLINED),
            ("Mis Cursos y Materias", "/portal/docente/materias", ft.Icons.MENU_BOOK_OUTLINED),
            ("Nómina de Alumnos", "/portal/docente/alumnos", ft.Icons.PEOPLE_OUTLINE),
            ("Deportes a Cargo", "/portal/docente/deportes", ft.Icons.FITNESS_CENTER_OUTLINED),
        ]
        portal_badge = "PORTAL DOCENTE"
    else:  # Alumno
        items_menu = [
            ("Mi Cursado", "/portal/alumno/dashboard", ft.Icons.SCHOOL_OUTLINED),
            ("Materias y Profesores", "/portal/alumno/materias", ft.Icons.MENU_BOOK_OUTLINED),
            ("Mis Deportes", "/portal/alumno/deportes", ft.Icons.FITNESS_CENTER_OUTLINED),
            ("Comedor y Transporte", "/portal/alumno/servicios", ft.Icons.DIRECTIONS_BUS_OUTLINED),
        ]
        portal_badge = "PORTAL ESTUDIANTE"

    def item_sidebar(texto: str, ruta: str, icono: ft.IconData) -> ft.Container:
        es_activo = active_route == ruta
        return ft.Container(
            height=42,
            border_radius=8,
            padding=ft.Padding(16, 12, 16, 12),
            bgcolor=TEAL_LIGHT if es_activo else "transparent",
            on_click=lambda _: page.go(ruta),
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icono, size=18, color=TEAL_DARK if es_activo else MUTED),
                    ft.Container(
                        expand=True,
                        content=ft.Text(
                            texto,
                            size=14,
                            weight=ft.FontWeight.W_600 if es_activo else ft.FontWeight.W_500,
                            color=TEAL_DARK if es_activo else TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=4,
                        height=16,
                        border_radius=2,
                        bgcolor=TEAL if es_activo else "transparent",
                    ),
                ],
            ),
        )

    # 2. BRANDING DEL SIDEBAR
    brand_header = ft.Row(
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
                    ft.Text("Educar para Transformar", size=14, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                    ft.Text(portal_badge, size=10, weight=ft.FontWeight.W_600, color=MUTED),
                ],
            ),
        ],
    )

    sidebar_container = ft.Container(
        width=260,
        bgcolor=BG_WHITE,
        border=ft.Border(right=ft.BorderSide(1, BORDER_COLOR)),
        padding=ft.Padding(16, 24, 16, 24),
        content=ft.Column(
            spacing=18,
            controls=[
                brand_header,
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                ft.Column(
                    spacing=4,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[item_sidebar(t, r, i) for t, r, i in items_menu],
                ),
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                # Botón de desconexión
                ft.Container(
                    height=40,
                    border_radius=8,
                    padding=ft.Padding(12, 8, 12, 8),
                    on_click=lambda _: page.go("/portal"),
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.LOGOUT, size=16, color="#EF4444"),
                            ft.Text("Cerrar Sesión", size=13, weight=ft.FontWeight.W_600, color="#EF4444"),
                        ],
                    ),
                ),
            ],
        ),
    )

    # 3. TOPBAR SIMPLIFICADO DEL PORTAL
    topbar_container = ft.Container(
        height=70,
        bgcolor=BG_WHITE,
        border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
        padding=ft.Padding.symmetric(horizontal=32),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(titulo, size=20, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Row(
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=36,
                            height=36,
                            bgcolor=TEAL_LIGHT,
                            border_radius=18,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Icon(ft.Icons.NOTIFICATIONS_NONE_OUTLINED, size=18, color=TEAL),
                        ),
                        ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    width=36,
                                    height=36,
                                    bgcolor=TEAL,
                                    border_radius=18,
                                    alignment=ft.Alignment(0, 0),
                                    content=ft.Text(usuario_nombre[:2].upper(), size=13, weight=ft.FontWeight.BOLD, color="white"),
                                ),
                                ft.Column(
                                    spacing=1,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text(usuario_nombre, size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                        ft.Text(usuario_sub, size=11, color=MUTED),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    )

    # 4. CONTENIDO PRINCIPAL
    main_content = ft.Container(
        expand=True,
        bgcolor=BG_PAGE,
        content=ft.Column(
            spacing=0,
            controls=[
                topbar_container,
                ft.Container(
                    expand=True,
                    padding=32,
                    content=ft.Column(
                        spacing=spacing,
                        scroll=ft.ScrollMode.AUTO,
                        controls=content_controls,
                    ),
                ),
            ],
        ),
    )

    return ft.Row(
        expand=True,
        spacing=0,
        controls=[sidebar_container, main_content],
    )