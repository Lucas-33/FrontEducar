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


def get_admin_materias_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa del catálogo de Materias y Asignaturas."""

    # ==================== 1. FILTROS Y ACCIÓN ====================
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
                    hint_text="Buscar materia o docente...",
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

    btn_nueva_materia = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                ft.Text("Nueva Materia", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
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
                    filtro_dropdown("Área: Todas", 150, ["Todas", "Ciencias Exactas", "Lenguas", "Sociales", "Tecnología"]),
                ],
            ),
            btn_nueva_materia,
        ],
    )

    # ==================== 2. TABLA DE MATERIAS ====================
    materias_data = [
        {"codigo": "MAT-501", "nombre": "Matemática Aplicada", "nivel": "Nivel Secundario", "cursos": "5to Año A, 5to Año B", "carga": "5 hs/sem", "docente": "Sánchez, Guillermina", "estado": "Activo"},
        {"codigo": "FIS-402", "nombre": "Física y Química", "nivel": "Nivel Secundario", "cursos": "4to Año A", "carga": "4 hs/sem", "docente": "Martínez, Román Alberto", "estado": "Activo"},
        {"codigo": "LIT-301", "nombre": "Lengua y Literatura", "nivel": "Nivel Secundario", "cursos": "3er Año A, 3er Año B", "carga": "4 hs/sem", "docente": "Duarte, María Florencia", "estado": "Activo"},
        {"codigo": "ROB-601", "nombre": "Robótica y Programación", "nivel": "Nivel Primario", "cursos": "6to Grado A, B, C", "carga": "3 hs/sem", "docente": "Ortega, Luis Humberto", "estado": "Activo"},
        {"codigo": "ING-001", "nombre": "Inglés Intensivo", "nivel": "Nivel Primario", "cursos": "1ro a 6to Grado", "carga": "6 hs/sem", "docente": "Vázquez, Emily", "estado": "Activo"},
        {"codigo": "EDF-001", "nombre": "Educación Física y Natación", "nivel": "Nivel Secundario", "cursos": "Ciclo Orientado", "carga": "4 hs/sem", "docente": "Vargas, Esteban Carlos", "estado": "Licencia"},
    ]

    columnas_materias = [
        ("Código", 100, False),
        ("Asignatura / Materia", 200, False),
        ("Nivel Educativo", 160, False),
        ("Cursos que la Dictan", 180, False),
        ("Carga Semanal", 130, False),
        ("Profesor Titular a Cargo", 190, False),
        ("Estado", 100, False),
        ("Acciones", None, True),
    ]

    header_table = create_table_header(columnas_materias)

    def materia_row(item: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=100, content=ft.Text(item["codigo"], size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=200, content=ft.Text(item["nombre"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=160, content=ft.Text(item["nivel"], size=14, color=MUTED)),
                    ft.Container(width=180, content=ft.Text(item["cursos"], size=13, color=TEXT_COLOR)),
                    ft.Container(width=130, content=ft.Text(item["carga"], size=13, color=MUTED)),
                    ft.Container(width=190, content=ft.Text(item["docente"], size=14, weight=ft.FontWeight.W_500, color=TEXT_COLOR)),
                    ft.Container(width=100, content=status_badge(item["estado"])),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=12,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_size=16, icon_color=TEAL, tooltip="Editar", padding=0),
                                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_size=16, icon_color=BADGE_RED_TXT, tooltip="Baja", padding=0),
                            ],
                        ),
                    ),
                ],
            ),
        )

    table_container = create_table_container(
        header=header_table,
        rows=[materia_row(m) for m in materias_data],
    )

    pagination_bar = create_pagination_bar(
        texto_info="Mostrando 1-6 de 48 asignaturas curriculares",
        pagina_actual=1,
        total_paginas=8,
    )

    # ==================== 3. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Plan de Estudios — Materias y Asignaturas",
        active_route="/admin/materias",
        content_controls=[
            filters_bar,
            table_container,
            pagination_bar,
        ],
    )