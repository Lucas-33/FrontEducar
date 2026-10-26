import flet as ft

from frontend.app.api_client import api_client
from frontend.app.components.constants import (
    BG_WHITE,
    BORDER_COLOR,
    MUTED,
    ONLINE_GREEN,
    SIDEBAR_WIDTH,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.password_dialog import abrir_cambio_password


def create_sidebar(
    page: ft.Page,
    active_route: str = "/admin/dashboard",
    collapsed: bool = False,
    on_toggle=None,
) -> ft.Container:
    """Barra lateral administrativa con soporte para modo colapsado y expandido."""

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
        ("Comunidad", "/admin/comunidad", ft.Icons.FORUM_OUTLINED),
        ("Transporte", "/admin/transporte", ft.Icons.DIRECTIONS_BUS_OUTLINED),
        ("Comedor", "/admin/comedor", ft.Icons.RESTAURANT_OUTLINED),
        ("Usuarios y Permisos", "/admin/usuarios", ft.Icons.LOCK_OUTLINE),
        ("Reportes", "/admin/reportes", ft.Icons.BAR_CHART_OUTLINED),
    ]

    def _cerrar_sesion(_):
        """Cierra la sesión del usuario: borra el token y vuelve al login."""
        page.auth_token = None
        page.auth_rol = None
        page.auth_user = None
        api_client.clear_token()
        page.go("/portal")

    ancho_actual = 72 if collapsed else SIDEBAR_WIDTH

    def item_sidebar(texto: str, ruta: str, icono: ft.IconData) -> ft.Container:
        es_activo = active_route == ruta

        if collapsed:
            # Modo compacto: Icono centrado de 42x42 px con tooltip descriptivo
            return ft.Container(
                data=ruta,
                height=42,
                width=42,
                border_radius=8,
                tooltip=texto,
                alignment=ft.Alignment(0, 0),
                bgcolor=TEAL_LIGHT if es_activo else "transparent",
                on_click=lambda _: page.go(ruta),
                content=ft.Icon(
                    icono,
                    size=20,
                    color=TEAL_DARK if es_activo else MUTED,
                ),
            )

        # Modo extendido: Icono + Nombre + Indicador de ruta activa
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
                    ft.Icon(icono, size=18, color=TEAL_DARK if es_activo else MUTED),
                    ft.Container(
                        expand=True,
                        content=ft.Text(
                            texto,
                            size=14,
                            weight=ft.FontWeight.W_600
                            if es_activo
                            else ft.FontWeight.W_500,
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

    # Cabecera con adaptación vertical cuando está colapsado para que el botón no se recorte
    if collapsed:
        brand_section = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Container(
                    width=36,
                    height=36,
                    bgcolor=TEAL,
                    border_radius=18,
                    alignment=ft.Alignment(0, 0),
                    tooltip="Educar SGE",
                    content=ft.Icon(ft.Icons.SCHOOL, color="white", size=18),
                ),
                ft.IconButton(
                    icon=ft.Icons.MENU,
                    icon_size=20,
                    icon_color=TEAL_DARK,
                    tooltip="Expandir menú lateral",
                    on_click=on_toggle,
                ),
            ],
        )
    else:
        brand_section = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=10,
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
                            spacing=1,
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text(
                                    "Educar SGE",
                                    size=15,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEAL_DARK,
                                ),
                                ft.Text(
                                    "GESTIÓN",
                                    size=10,
                                    weight=ft.FontWeight.W_600,
                                    color=MUTED,
                                ),
                            ],
                        ),
                    ],
                ),
                ft.IconButton(
                    icon=ft.Icons.MENU_OPEN,
                    icon_size=18,
                    icon_color=TEAL_DARK,
                    tooltip="Contraer menú lateral",
                    on_click=on_toggle,
                ),
            ],
        )

    nav_list = ft.Column(
        spacing=6,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
        if collapsed
        else ft.CrossAxisAlignment.START,
        controls=[
            item_sidebar(texto, ruta, icono) for texto, ruta, icono in items_menu
        ],
    )

    if collapsed:
        footer_section = ft.Column(
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.LOCK_RESET,
                    icon_size=18,
                    icon_color=TEAL,
                    tooltip="Cambiar mi contraseña",
                    on_click=lambda _: abrir_cambio_password(page),
                ),
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    icon_size=18,
                    icon_color="#EF4444",
                    tooltip="Cerrar sesión",
                    on_click=_cerrar_sesion,
                ),
                ft.Container(
                    tooltip="Servidor Online",
                    content=ft.Container(
                        width=8,
                        height=8,
                        bgcolor=ONLINE_GREEN,
                        border_radius=4,
                    ),
                ),
            ],
        )
    else:
        footer_section = ft.Column(
            spacing=4,
            controls=[
                ft.Container(
                    height=36,
                    border_radius=8,
                    padding=ft.Padding(8, 6, 8, 6),
                    on_click=lambda _: abrir_cambio_password(page),
                    content=ft.Row(
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.LOCK_RESET, size=15, color=TEAL),
                            ft.Text("Cambiar Contraseña", size=12, color=TEXT_COLOR),
                        ],
                    ),
                ),
                ft.Container(
                    height=36,
                    border_radius=8,
                    padding=ft.Padding(8, 6, 8, 6),
                    on_click=_cerrar_sesion,
                    content=ft.Row(
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.LOGOUT, size=15, color="#EF4444"),
                            ft.Text("Cerrar Sesión", size=12, color="#EF4444"),
                        ],
                    ),
                ),
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=8, height=8, bgcolor=ONLINE_GREEN, border_radius=4
                        ),
                        ft.Text("Servidor Online", size=12, color=MUTED),
                    ],
                ),
                ft.Text("v2.5.0-resistencia", size=10, color=MUTED),
            ],
        )

    return ft.Container(
        width=ancho_actual,
        animate_size=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        bgcolor=BG_WHITE,
        border=ft.Border(right=ft.BorderSide(1, BORDER_COLOR)),
        padding=ft.Padding(12 if collapsed else 16, 20, 12 if collapsed else 16, 20),
        content=ft.Column(
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
            if collapsed
            else ft.CrossAxisAlignment.START,
            controls=[
                brand_section,
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                nav_list,
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                footer_section,
            ],
        ),
    )
