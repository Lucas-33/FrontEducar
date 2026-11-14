import flet as ft

from mobile.api_client import mobile_api
from mobile.components.constants import (
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    MUTED,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)


def create_mobile_scaffold(
    page: ft.Page,
    titulo: str,
    contenido: list[ft.Control],
    indice_activo: int = 0,
    on_cambiar_tab=None,
    on_refresh=None,
) -> ft.Container:
    """Scaffold móvil nativo con TopBar y Bottom Navigation Bar."""

    usuario_nombre = getattr(page, "auth_user", "Familia")
    iniciales = (usuario_nombre[:2] if usuario_nombre else "FA").upper()

    # Barra superior móvil compacta
    topbar = ft.Container(
        height=62,
        bgcolor=BG_WHITE,
        padding=ft.Padding(16, 0, 16, 0),
        border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Container(
                            width=34,
                            height=34,
                            bgcolor=TEAL_LIGHT,
                            border_radius=17,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Icon(ft.Icons.SCHOOL, color=TEAL_DARK, size=18),
                        ),
                        ft.Column(
                            spacing=0,
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text(
                                    titulo,
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEAL_DARK,
                                ),
                                ft.Text(
                                    "Educar Móvil",
                                    size=10,
                                    color=MUTED,
                                    weight=ft.FontWeight.W_500,
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Row(
                    spacing=6,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            icon_color=TEAL,
                            icon_size=20,
                            tooltip="Actualizar",
                            on_click=lambda _: on_refresh()
                            if on_refresh
                            else page.update(),
                        ),
                        ft.Container(
                            width=32,
                            height=32,
                            bgcolor=TEAL_DARK,
                            border_radius=16,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Text(
                                iniciales,
                                size=11,
                                weight=ft.FontWeight.BOLD,
                                color="white",
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )

    # Barra de navegación inferior móvil (Bottom Navigation Bar)
    def handle_nav_change(e):
        nuevo_indice = e.control.selected_index
        if on_cambiar_tab:
            on_cambiar_tab(nuevo_indice)

    nav_bar = ft.NavigationBar(
        selected_index=indice_activo,
        on_change=handle_nav_change,
        bgcolor=BG_WHITE,
        indicator_color=TEAL_LIGHT,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Inicio",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.RECEIPT_LONG_OUTLINED,
                selected_icon=ft.Icons.RECEIPT_LONG,
                label="Cuotas",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.DIRECTIONS_BUS_OUTLINED,
                selected_icon=ft.Icons.DIRECTIONS_BUS,
                label="Servicios",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.PERSON_OUTLINE,
                selected_icon=ft.Icons.PERSON,
                label="Perfil",
            ),
        ],
    )

    # Cuerpo scrolleable
    cuerpo = ft.Container(
        expand=True,
        bgcolor=BG_PAGE,
        padding=ft.Padding(16, 16, 16, 20),
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
            controls=contenido,
        ),
    )

    return ft.Container(
        expand=True,
        bgcolor=BG_PAGE,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[topbar, cuerpo, nav_bar],
        ),
    )
