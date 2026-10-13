import flet as ft
from frontend.app.components.constants import BG_PAGE
from frontend.app.components.sidebar import create_sidebar
from frontend.app.components.topbar import create_topbar


def admin_layout(
    page: ft.Page,
    titulo: str,
    active_route: str,
    content_controls: list[ft.Control],
    scroll_mode: ft.ScrollMode = ft.ScrollMode.AUTO,
    padding: int = 32,
    spacing: int = 24,
) -> ft.Row:
    """Layout maestro administrativo con sidebar colapsable reactivo."""

    # Estado de colapso guardado directamente en la instancia de la página del usuario
    is_collapsed = getattr(page, "sidebar_collapsed", False)

    sidebar_holder = ft.Container()
    topbar = create_topbar(page, titulo=titulo)

    def toggle_sidebar(e):
        nuevo_estado = not getattr(page, "sidebar_collapsed", False)
        page.sidebar_collapsed = nuevo_estado
        sidebar_holder.content = create_sidebar(
            page,
            active_route=active_route,
            collapsed=nuevo_estado,
            on_toggle=toggle_sidebar,
        )
        sidebar_holder.update()

    sidebar_holder.content = create_sidebar(
        page,
        active_route=active_route,
        collapsed=is_collapsed,
        on_toggle=toggle_sidebar,
    )

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
        controls=[sidebar_holder, main_content],
    )