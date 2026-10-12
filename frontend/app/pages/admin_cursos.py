import flet as ft
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    TEAL,
    TEAL_DARK,
    TEXT_COLOR,
)
from frontend.app.components.form_controls import status_badge
from frontend.app.components.table_view import (
    create_pagination_bar,
    create_table_container,
    create_table_header,
)


def get_admin_cursos_view(page: ft.Page) -> ft.Row:
    """Retorna la vista del directorio de Cursos y Divisiones institucionales."""

    # ==================== 1. BARRA DE FILTROS Y ACCIÓN ====================
    search_input = ft.Container(
        width=280,
        height=CONTROL_HEIGHT,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=BORDER_RADIUS,
        padding=ft.Padding(12, 0, 12, 0),
        content=ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SEARCH, size=16, color=MUTED),
                ft.TextField(
                    hint_text="Buscar curso o división...",
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
            height=CONTROL_HEIGHT,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=BORDER_RADIUS,
            content=ft.Dropdown(
                hint_text=hint,
                hint_style=ft.TextStyle(size=14, color=TEXT_COLOR),
                text_size=14,
                border=ft.InputBorder.NONE,
                content_padding=ft.Padding(12, 0, 8, 12),
                options=[ft.dropdown.Option(opc) for opc in opciones],
            ),
        )

    btn_nuevo_curso = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                ft.Text("Nuevo Curso", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
            ],
        ),
        bgcolor=TEAL,
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            padding=ft.Padding(24, 12, 24, 12),
        ),
        on_click=lambda _: None,
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
                    filtro_dropdown("Nivel: Todos", 140, ["Todos", "Nivel Inicial", "Nivel Primario", "Nivel Secundario"]),
                    filtro_dropdown("Turno: Todos", 130, ["Todos", "Mañana", "Tarde", "Jornada Extendida"]),
                ],
            ),
            btn_nuevo_curso,
        ],
    )

    # ==================== 2. TABLA DE CURSOS ====================
    cursos_data = [
        {"codigo": "INI-S5-A", "nombre": "Sala de 5 años", "division": "División A", "nivel": "Nivel Inicial", "turno": "Mañana", "cupo": "25 / 25", "preceptor": "Gómez, Laura", "estado": "Activo"},
        {"codigo": "PRI-1G-B", "nombre": "1er Grado", "division": "División B", "nivel": "Nivel Primario", "turno": "Jornada Extendida", "cupo": "28 / 30", "preceptor": "Ramírez, Clara", "estado": "Activo"},
        {"codigo": "PRI-4G-A", "nombre": "4to Grado", "division": "División A", "nivel": "Nivel Primario", "turno": "Jornada Extendida", "cupo": "30 / 30", "preceptor": "Vega, Lucas", "estado": "Activo"},
        {"codigo": "SEC-3A-A", "nombre": "3er Año", "division": "División A", "nivel": "Nivel Secundario", "turno": "Mañana", "cupo": "26 / 32", "preceptor": "Díaz, Marcos", "estado": "Activo"},
        {"codigo": "SEC-5A-B", "nombre": "5to Año", "division": "División B", "nivel": "Nivel Secundario", "turno": "Mañana", "cupo": "22 / 30", "preceptor": "Benítez, Sonia", "estado": "Activo"},
        {"codigo": "SEC-6A-A", "nombre": "6to Año", "division": "División A", "nivel": "Nivel Secundario", "turno": "Tarde", "cupo": "18 / 30", "preceptor": "Díaz, Marcos", "estado": "Activo"},
    ]

    columnas_cursos = [
        ("Código", 110, False),
        ("Curso / Año", 160, False),
        ("División", 130, False),
        ("Nivel Educativo", 160, False),
        ("Turno", 150, False),
        ("Matrícula / Cupo", 140, False),
        ("Preceptor / Tutor", 160, False),
        ("Estado", 100, False),
        ("Acciones", None, True),
    ]

    header_table = create_table_header(columnas_cursos)

    def curso_row(item: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=110, content=ft.Text(item["codigo"], size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=160, content=ft.Text(item["nombre"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=130, content=ft.Text(item["division"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=160, content=ft.Text(item["nivel"], size=14, color=MUTED)),
                    ft.Container(width=150, content=ft.Text(item["turno"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=140, content=ft.Text(item["cupo"], size=14, weight=ft.FontWeight.W_500, color=TEXT_COLOR)),
                    ft.Container(width=160, content=ft.Text(item["preceptor"], size=14, color=MUTED)),
                    ft.Container(width=100, content=status_badge(item["estado"])),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=12,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_size=16, icon_color=TEAL, tooltip="Editar Curso", padding=0),
                                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_size=16, icon_color=BADGE_RED_TXT, tooltip="Desactivar", padding=0),
                            ],
                        ),
                    ),
                ],
            ),
        )

    table_container = create_table_container(
        header=header_table,
        rows=[curso_row(c) for c in cursos_data],
    )

    pagination_bar = create_pagination_bar(
        texto_info="Mostrando 1-6 de 32 cursos activos",
        pagina_actual=1,
        total_paginas=6,
    )

    # ==================== 3. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Gestión Académica — Cursos y Divisiones",
        active_route="/admin/cursos",
        content_controls=[
            filters_bar,
            table_container,
            pagination_bar,
        ],
    )