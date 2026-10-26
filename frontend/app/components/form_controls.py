import flet as ft

from frontend.app.components.constants import (
    BADGE_GREEN_BG,
    BADGE_GREEN_TXT,
    BADGE_RED_BG,
    BADGE_RED_TXT,
    BADGE_YELLOW_BG,
    BADGE_YELLOW_TXT,
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    TEXT_COLOR,
)


def input_con_label(
    label: str,
    hint: str = "",
    width: int | None = 289,
    expand: bool = False,
    read_only: bool = False,
    valor_inicial: str | None = None,
    keyboard_type: ft.KeyboardType = ft.KeyboardType.TEXT,
    password: bool = False,
) -> ft.Column:
    """Genera un input estandarizado con su etiqueta superior."""
    text_field = ft.TextField(
        value=valor_inicial or "",
        hint_text=hint if not valor_inicial else None,
        hint_style=ft.TextStyle(size=14, color=MUTED),
        text_size=14,
        color=MUTED if read_only else TEXT_COLOR,
        read_only=read_only,
        password=password,
        keyboard_type=keyboard_type,
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding(0, 0, 0, 10),
        expand=True,
    )

    return ft.Column(
        spacing=6,
        width=width,
        expand=expand,
        controls=[
            ft.Text(
                label,
                size=13,
                weight=ft.FontWeight.W_600,
                color=MUTED if read_only else TEXT_COLOR,
            ),
            ft.Container(
                height=CONTROL_HEIGHT,
                bgcolor=BG_PAGE if read_only else BG_WHITE,
                border=None if read_only else ft.Border.all(1, BORDER_COLOR),
                border_radius=BORDER_RADIUS,
                padding=ft.Padding(12, 0, 12, 0),
                alignment=ft.Alignment(-1, 0),
                content=text_field,
            ),
        ],
    )


def dropdown_con_label(
    label: str,
    valor_default: str | None,
    opciones: list[str],
    width: int | None = 187,
    expand: bool = False,
) -> ft.Column:
    """Genera un selector desplegable estandarizado con su etiqueta superior."""
    return ft.Column(
        spacing=6,
        width=width,
        expand=expand,
        controls=[
            ft.Text(label, size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
            ft.Container(
                height=CONTROL_HEIGHT,
                bgcolor=BG_WHITE,
                border=ft.Border.all(1, BORDER_COLOR),
                border_radius=BORDER_RADIUS,
                content=ft.Dropdown(
                    value=valor_default,
                    text_size=14,
                    border=ft.InputBorder.NONE,
                    content_padding=ft.Padding(12, 0, 8, 12),
                    options=[ft.dropdown.Option(opc) for opc in opciones],
                ),
            ),
        ],
    )


def status_badge(estado: str) -> ft.Container:
    """Genera un badge de estado con colores semánticos consistentes."""
    estado_normalizado = (estado or "").strip().lower()

    if estado_normalizado in ["activo", "regular", "aprobado", "al día"]:
        bg, color = BADGE_GREEN_BG, BADGE_GREEN_TXT
    elif estado_normalizado in ["pendiente", "licencia", "en revisión"]:
        bg, color = BADGE_YELLOW_BG, BADGE_YELLOW_TXT
    else:
        bg, color = BADGE_RED_BG, BADGE_RED_TXT

    return ft.Container(
        padding=ft.Padding(8, 4, 8, 4),
        bgcolor=bg,
        border_radius=4,
        content=ft.Text(estado, size=12, weight=ft.FontWeight.W_600, color=color),
    )
