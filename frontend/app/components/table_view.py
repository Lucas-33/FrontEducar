import flet as ft
from frontend.app.components.constants import (
    BG_WHITE,
    BORDER_COLOR,
    CARD_RADIUS,
    MUTED,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)


def create_table_header(columns: list[tuple[str, int | None, bool]]) -> ft.Container:
    """
    Genera la cabecera estilizada de la tabla.
    columns recibe una lista de tuplas: (nombre_columna, ancho_px, alinear_a_la_derecha)
    Si ancho_px es None, la celda se expande automáticamente.
    """
    controls = []
    for titulo, width, align_right in columns:
        alignment = ft.Alignment(1, 0) if align_right else ft.Alignment(-1, 0)
        controls.append(
            ft.Container(
                width=width,
                expand=width is None,
                alignment=alignment,
                content=ft.Text(
                    titulo,
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
            )
        )

    return ft.Container(
        height=48,
        bgcolor=TEAL_LIGHT,
        padding=ft.Padding(16, 0, 16, 0),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=controls,
        ),
    )


def create_table_container(header: ft.Container, rows: list[ft.Control]) -> ft.Container:
    """Envuelve la cabecera y las filas en una tarjeta blanca con bordes curvos."""
    return ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            spacing=0,
            controls=[
                header,
                *rows,
            ],
        ),
    )


def create_pagination_bar(
    texto_info: str = "Mostrando registros",
    pagina_actual: int = 1,
    total_paginas: int = 3,
    on_page_change=None,
) -> ft.Row:
    """Genera la barra de paginación inferior unificada."""

    def btn_pagina(texto: str, activo: bool = False, icon: ft.IconData | None = None) -> ft.Container:
        return ft.Container(
            width=36,
            height=36,
            bgcolor=TEAL if activo else BG_WHITE,
            border=None if activo else ft.Border.all(1, BORDER_COLOR),
            border_radius=8,
            alignment=ft.Alignment(0, 0),
            on_click=on_page_change,
            content=ft.Icon(icon, size=16, color=TEXT_COLOR)
            if icon
            else ft.Text(
                texto,
                size=14,
                weight=ft.FontWeight.W_600 if activo else ft.FontWeight.W_400,
                color=BG_WHITE if activo else TEXT_COLOR,
            ),
        )

    botones_paginas = [
        btn_pagina("", icon=ft.Icons.CHEVRON_LEFT),
    ]

    for p in range(1, total_paginas + 1):
        botones_paginas.append(btn_pagina(str(p), activo=(p == pagina_actual)))

    botones_paginas.append(btn_pagina("", icon=ft.Icons.CHEVRON_RIGHT))

    return ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text(texto_info, size=14, color=MUTED),
            ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=botones_paginas,
            ),
        ],
    )