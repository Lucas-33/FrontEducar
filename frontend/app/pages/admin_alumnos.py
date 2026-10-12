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


def get_admin_alumnos_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa de administración de alumnos usando AdminLayout."""

    # ==================== 1. BARRA DE BÚSQUEDA Y FILTROS ====================
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
                    hint_text="Buscar por nombre o legajo...",
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

    btn_nuevo_alumno = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                ft.Text("Nuevo Alumno", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
            ],
        ),
        bgcolor=TEAL,
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            padding=ft.Padding(24, 12, 24, 12),
        ),
        on_click=lambda _: page.go("/admin/alumnos/nuevo"),
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
                    filtro_dropdown("Nivel: Todos", 135, ["Todos", "Inicial", "Primario", "Secundario"]),
                    filtro_dropdown("Curso: Todos", 140, ["Todos", "Sala 5", "4to Grado", "6to Grado", "3er Año", "5to Año", "6to Año"]),
                    filtro_dropdown("Estado: Activo", 145, ["Activo", "Regular", "Pendiente", "Inactivo"]),
                ],
            ),
            btn_nuevo_alumno,
        ],
    )

    # ==================== 2. TABLA DE ALUMNOS ====================
    alumnos_data = [
        {"legajo": "#10245", "dni": "44.120.942", "apellido": "Almirón", "nombre": "Santiago", "nivel": "Secundario", "curso": "5to Año B", "estado": "Regular"},
        {"legajo": "#10246", "dni": "45.892.110", "apellido": "Benítez", "nombre": "Martina", "nivel": "Secundario", "curso": "3er Año A", "estado": "Regular"},
        {"legajo": "#10247", "dni": "48.330.124", "apellido": "Capra", "nombre": "Lautaro", "nivel": "Primario", "curso": "6to Grado C", "estado": "Regular"},
        {"legajo": "#10248", "dni": "50.114.992", "apellido": "Díaz", "nombre": "Sofía Valentina", "nivel": "Inicial", "curso": "Sala de 5 años B", "estado": "Pendiente"},
        {"legajo": "#10249", "dni": "43.902.114", "apellido": "Flores", "nombre": "Facundo Joaquín", "nivel": "Secundario", "curso": "6to Año A", "estado": "Regular"},
        {"legajo": "#10250", "dni": "45.102.399", "apellido": "Giménez", "nombre": "Camila Belén", "nivel": "Primario", "curso": "4to Grado A", "estado": "Inactivo"},
    ]

    # Columnas: (Nombre, Ancho px, Alinear a la derecha)
    columnas_definicion = [
        ("Legajo", 100, False),
        ("DNI", 140, False),
        ("Apellido", 180, False),
        ("Nombre", 180, False),
        ("Nivel Educativo", 160, False),
        ("Curso", 140, False),
        ("Estado", 120, False),
        ("Acciones", 64, True),
    ]

    header_table = create_table_header(columnas_definicion)

    def alumno_row(item: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=100, content=ft.Text(item["legajo"], size=14, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=140, content=ft.Text(item["dni"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=180, content=ft.Text(item["apellido"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=180, content=ft.Text(item["nombre"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=160, content=ft.Text(item["nivel"], size=14, color=MUTED)),
                    ft.Container(width=140, content=ft.Text(item["curso"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=120, content=status_badge(item["estado"])),
                    ft.Container(
                        width=64,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=12,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_size=16, icon_color=TEAL, tooltip="Editar", padding=0),
                                ft.IconButton(icon=ft.Icons.REMOVE_RED_EYE_OUTLINED, icon_size=16, icon_color=MUTED, tooltip="Ver legajo", padding=0),
                                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_size=16, icon_color=BADGE_RED_TXT, tooltip="Borrar", padding=0),
                            ],
                        ),
                    ),
                ],
            ),
        )

    table_container = create_table_container(
        header=header_table,
        rows=[alumno_row(a) for a in alumnos_data],
    )

    # ==================== 3. BARRA DE PAGINACIÓN ====================
    pagination_bar = create_pagination_bar(
        texto_info="Mostrando 1-6 de 1,248 alumnos matriculados",
        pagina_actual=1,
        total_paginas=3,
    )

    # ==================== 4. LAYOUT ADMINISTRATIVO ====================
    return admin_layout(
        page=page,
        titulo="Directorio de Alumnos Matriculados",
        active_route="/admin/alumnos",
        content_controls=[
            filters_bar,
            table_container,
            pagination_bar,
        ],
    )