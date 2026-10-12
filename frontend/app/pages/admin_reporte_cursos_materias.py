import flet as ft
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.table_view import (
    create_pagination_bar,
    create_table_container,
    create_table_header,
)


def get_admin_reporte_cursos_materias_view(page: ft.Page) -> ft.Row:
    """Retorna el reporte oficial de Alumnos por Materia y Docente a cargo."""

    header_actions = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=36,
                        height=36,
                        bgcolor=BG_WHITE,
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=18,
                        alignment=ft.Alignment(0, 0),
                        tooltip="Volver al Centro de Reportes",
                        on_click=lambda _: page.go("/admin/reportes"),
                        content=ft.Icon(ft.Icons.ARROW_BACK, size=16, color=TEXT_COLOR),
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text("Nómina Curricular: Alumnos por Materia", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ft.Text("Materia, Curso, Docente a Cargo y Nómina de Alumnos Inscriptos", size=12, color=MUTED),
                        ],
                    ),
                ],
            ),
            ft.Row(
                spacing=10,
                controls=[
                    ft.Button(
                        content=ft.Row(
                            spacing=6,
                            controls=[
                                ft.Icon(ft.Icons.FILE_DOWNLOAD_OUTLINED, size=15, color=TEAL_DARK),
                                ft.Text("Exportar Excel", size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                            ],
                        ),
                        bgcolor=TEAL_LIGHT,
                        height=36,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
                        on_click=lambda _: None,
                    ),
                    ft.Button(
                        content=ft.Row(
                            spacing=6,
                            controls=[
                                ft.Icon(ft.Icons.PRINT_OUTLINED, size=15, color=BG_WHITE),
                                ft.Text("Imprimir PDF", size=13, weight=ft.FontWeight.W_600, color=BG_WHITE),
                            ],
                        ),
                        bgcolor=ORANGE,
                        height=36,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
                        on_click=lambda _: None,
                    ),
                ],
            ),
        ],
    )

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

    filters_bar = ft.Row(
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            search_input,
            filtro_dropdown("Materia: Matemática", 170, ["Todas", "Matemática Aplicada", "Física y Química", "Robótica", "Lengua"]),
            filtro_dropdown("Nivel: Secundario", 155, ["Todos", "Nivel Inicial", "Nivel Primario", "Nivel Secundario"]),
            filtro_dropdown("Curso: 5to Año B", 145, ["Todos", "5to Año B", "6to Año A"]),
        ],
    )

    # Requerimiento: Nivel educativo, Curso, Materia, Profesor a cargo, Alumno, Legajo
    materias_reporte_data = [
        {"nivel": "Nivel Secundario", "curso": "5to Año B", "materia": "Matemática Aplicada", "profesor": "Sánchez, Guillermina", "alumno": "Almirón, Santiago", "legajo": "#10245"},
        {"nivel": "Nivel Secundario", "curso": "5to Año B", "materia": "Matemática Aplicada", "profesor": "Sánchez, Guillermina", "alumno": "Flores, Facundo Joaquín", "legajo": "#10249"},
        {"nivel": "Nivel Secundario", "curso": "5to Año B", "materia": "Matemática Aplicada", "profesor": "Sánchez, Guillermina", "alumno": "Gutiérrez, Ignacio Tomás", "legajo": "#10254"},
        {"nivel": "Nivel Secundario", "curso": "5to Año B", "materia": "Matemática Aplicada", "profesor": "Sánchez, Guillermina", "alumno": "Navarro, Camila Sol", "legajo": "#10258"},
        {"nivel": "Nivel Secundario", "curso": "5to Año B", "materia": "Matemática Aplicada", "profesor": "Sánchez, Guillermina", "alumno": "Villalba, Mateo David", "legajo": "#10261"},
    ]

    columnas_materia = [
        ("Nivel Educativo", 150, False),
        ("Curso", 120, False),
        ("Asignatura / Materia", 190, False),
        ("Profesor Titular a Cargo", 190, False),
        ("Alumno Inscripto", 180, False),
        ("Legajo", 110, False),
    ]

    header_table = create_table_header(columnas_materia)

    def materia_reporte_row(item: dict) -> ft.Container:
        return ft.Container(
            height=50,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=150, content=ft.Text(item["nivel"], size=13, color=MUTED)),
                    ft.Container(width=120, content=ft.Text(item["curso"], size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=190, content=ft.Text(item["materia"], size=14, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=190, content=ft.Text(item["profesor"], size=13, weight=ft.FontWeight.W_500, color=TEXT_COLOR)),
                    ft.Container(width=180, content=ft.Text(item["alumno"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=110, content=ft.Text(item["legajo"], size=13, weight=ft.FontWeight.BOLD, color=TEAL)),
                ],
            ),
        )

    table_container = create_table_container(
        header=header_table,
        rows=[materia_reporte_row(m) for m in materias_reporte_data],
    )

    pagination_bar = create_pagination_bar(
        texto_info="Mostrando nómina de 5 alumnos inscriptos en la materia",
        pagina_actual=1,
        total_paginas=1,
    )

    return admin_layout(
        page=page,
        titulo="Reporte: Alumnos por Materia y Docente",
        active_route="/admin/reportes",
        content_controls=[
            header_actions,
            filters_bar,
            table_container,
            pagination_bar,
        ],
    )