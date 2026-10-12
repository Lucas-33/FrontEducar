import flet as ft
from frontend.app.components.sidebar import create_sidebar
from frontend.app.components.topbar import create_topbar
from frontend.app.components.constants import BG_PAGE


def admin_layout(
    page: ft.Page,
    titulo: str,
    active_route: str,
    content_controls: list[ft.Control],
    scroll_mode: ft.ScrollMode = ft.ScrollMode.AUTO,
    padding: int = 32,
    spacing: int = 24,
) -> ft.Row:
    """
    Layout maestro administrativo.
    Ensambla Sidebar (fijo a la izquierda) + TopBar (fijo superior)
    y un área de contenido central con scroll vertical independiente.
    """
    sidebar = create_sidebar(page, active_route=active_route)
    topbar = create_topbar(page, titulo=titulo)

    # Área de contenido con scroll vertical desacoplado de las barras
    main_content = ft.Container(
        expand=True,
        bgcolor=BG_PAGE,
        content=ft.Column(
            spacing=0,
            controls=[
                topbar,
                ft.Container(
                    expand=True,
                    padding=padding,
                    content=ft.Column(
                        spacing=spacing,
                        scroll=scroll_mode,
                        controls=content_controls,
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