import flet as ft

from frontend.app.api_client import api_client
from frontend.app.components.constants import (
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    MUTED,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.password_dialog import abrir_cambio_password


def portal_layout(
    page: ft.Page,
    titulo: str,
    active_route: str,
    content_controls: list[ft.Control],
    rol: str = "Padre",
    usuario_nombre: str = "Familia",
    usuario_sub: str = "Tutor responsable",
    spacing: int = 24,
) -> ft.Container:
    def _cerrar_sesion(_):
        page.auth_token = None
        page.auth_rol = None
        page.auth_user = None
        api_client.clear_token()
        page.go("/portal")

    auth_user = getattr(page, "auth_user", None)
    if auth_user:
        usuario_nombre = auth_user

    # 1. MENÚS SEGÚN ROL
    if rol.lower() in ["padre", "familia", "tutor"]:
        items_menu = [
            ("Inicio", "/portal/padre/dashboard", ft.Icons.FAMILY_RESTROOM_OUTLINED),
            ("Facturas", "/portal/padre/facturas", ft.Icons.RECEIPT_LONG_OUTLINED),
            ("Notas", "/portal/padre/notas", ft.Icons.ASSESSMENT_OUTLINED),
            ("Deportes", "/portal/padre/deportes", ft.Icons.FITNESS_CENTER_OUTLINED),
            ("Servicios", "/portal/padre/servicios", ft.Icons.RESTAURANT_OUTLINED),
            (
                "Cursado",
                "/portal/padre/inscripcion",
                ft.Icons.APP_REGISTRATION_OUTLINED,
            ),
        ]
        portal_badge = "PORTAL FAMILIAS"
    else:
        items_menu = [
            ("Mi Cursado", "/portal/alumno/dashboard", ft.Icons.SCHOOL_OUTLINED)
        ]
        portal_badge = "PORTAL"

    # ==================== MENÚ DESPLEGABLE MÓVIL (POPUP BULLETPROOF) ====================
    def nav_item(texto: str, ruta: str, icono: ft.IconData):
        return ft.PopupMenuItem(
            content=ft.Row(
                spacing=12,
                controls=[
                    ft.Icon(icono, size=18, color=TEAL_DARK),
                    ft.Text(texto, size=14, color=TEXT_COLOR),
                ],
            ),
            on_click=lambda _: page.go(ruta),
        )

    menu_hamburguesa = ft.PopupMenuButton(
        icon=ft.Icons.MENU,
        icon_color=TEAL_DARK,
        tooltip="Menú Principal",
        items=[nav_item(t, r, i) for t, r, i in items_menu],
    )

    topbar_movil = ft.Container(
        height=60,
        bgcolor=BG_WHITE,
        border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
        padding=ft.Padding.symmetric(horizontal=8),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=4,
                    controls=[
                        menu_hamburguesa,
                        ft.Text(
                            titulo, size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK
                        ),
                    ],
                ),
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.LOCK_RESET,
                            icon_color=TEAL,
                            icon_size=20,
                            on_click=lambda _: abrir_cambio_password(page),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.LOGOUT,
                            icon_color="#EF4444",
                            icon_size=20,
                            on_click=_cerrar_sesion,
                        ),
                    ],
                ),
            ],
        ),
    )

    # ==================== DISEÑO ESCRITORIO (PC) ====================
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
                controls=[
                    ft.Icon(icono, size=18, color=TEAL_DARK if es_activo else MUTED),
                    ft.Text(
                        texto,
                        size=14,
                        weight=ft.FontWeight.W_600
                        if es_activo
                        else ft.FontWeight.W_500,
                        color=TEAL_DARK if es_activo else TEXT_COLOR,
                    ),
                ],
            ),
        )

    sidebar_pc = ft.Container(
        width=260,
        bgcolor=BG_WHITE,
        border=ft.Border(right=ft.BorderSide(1, BORDER_COLOR)),
        padding=ft.Padding(16, 24, 16, 24),
        content=ft.Column(
            spacing=18,
            controls=[
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.Icon(ft.Icons.SCHOOL, color=TEAL, size=32),
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text(
                                    "Educar SGE",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEAL_DARK,
                                ),
                                ft.Text(portal_badge, size=10, color=MUTED),
                            ],
                        ),
                    ],
                ),
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                ft.Column(
                    spacing=4,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[item_sidebar(t, r, i) for t, r, i in items_menu],
                ),
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                ft.Container(
                    height=40,
                    on_click=_cerrar_sesion,
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LOGOUT, size=16, color="#EF4444"),
                            ft.Text("Cerrar Sesión", size=13, color="#EF4444"),
                        ]
                    ),
                ),
            ],
        ),
    )

    topbar_pc = ft.Container(
        height=70,
        bgcolor=BG_WHITE,
        border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
        padding=ft.Padding.symmetric(horizontal=32),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(titulo, size=20, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Container(
                            width=36,
                            height=36,
                            bgcolor=TEAL,
                            border_radius=18,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Text(
                                usuario_nombre[:2].upper(),
                                color="white",
                                weight=ft.FontWeight.BOLD,
                            ),
                        ),
                        ft.Column(
                            spacing=1,
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text(
                                    usuario_nombre, size=13, weight=ft.FontWeight.W_600
                                ),
                                ft.Text(usuario_sub, size=11, color=MUTED),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    )

    layout_dinamico = ft.Container(expand=True)

    def actualizar_layout(e=None):
        es_celular = page.width < 768
        area_contenido = ft.Container(
            expand=True,
            bgcolor=BG_PAGE,
            padding=16 if es_celular else 32,
            content=ft.Column(
                spacing=spacing, scroll=ft.ScrollMode.AUTO, controls=content_controls
            ),
        )

        if es_celular:
            layout_dinamico.content = ft.Column(
                expand=True, spacing=0, controls=[topbar_movil, area_contenido]
            )
        else:
            layout_dinamico.content = ft.Row(
                expand=True,
                spacing=0,
                controls=[
                    sidebar_pc,
                    ft.Column(
                        expand=True, spacing=0, controls=[topbar_pc, area_contenido]
                    ),
                ],
            )
        page.update()

    page.on_resize = actualizar_layout
    actualizar_layout()
    return layout_dinamico
