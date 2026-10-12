import flet as ft
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    ONLINE_GREEN,
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


def get_admin_reporte_deportes_avanzado_view(page: ft.Page) -> ft.Row:
    """Retorna el reporte de Alumnos por Deporte, Nivel, Horario y Profesor Responsable."""

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
                            ft.Text("Reporte Integral de Actividades Deportivas", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ft.Text("Alumnos por Deporte, Nivel, Horario y Profesor a Cargo", size=12, color=MUTED),
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
        width=260,
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
                    hint_text="Buscar alumno o disciplina...",
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
            filtro_dropdown("Deporte: Natación", 160, ["Todas", "Natación Climatizada", "Fútbol Campo", "Atletismo", "Básquetbol", "Artes Marciales"]),
            filtro_dropdown("Nivel: Secundario", 155, ["Todos", "Nivel Primario", "Nivel Secundario"]),
            filtro_dropdown("Horario: Lun/Mié 16:30", 175, ["Todos", "Lun y Mié 16:30 - 18:00 hs", "Mar y Jue 16:30 - 18:00 hs"]),
        ],
    )

    # Requerimiento: Deporte, Alumno, Legajo, Curso, Nivel educativo, Horario y Profesor a cargo[cite: 5]
    deportes_reporte_data = [
        {"deporte": "Natación Climatizada", "nivel": "Nivel Secundario", "curso": "5to Año B", "legajo": "#10245", "alumno": "Almirón, Santiago", "horario": "Lun/Mié 16:30 - 18:00", "profesor": "Vargas, Esteban Carlos", "apto": "Vigente"},
        {"deporte": "Natación Climatizada", "nivel": "Nivel Secundario", "curso": "6to Año A", "legajo": "#10249", "alumno": "Flores, Facundo", "horario": "Lun/Mié 16:30 - 18:00", "profesor": "Vargas, Esteban Carlos", "apto": "Vigente"},
        {"deporte": "Natación Climatizada", "nivel": "Nivel Primario", "curso": "6to Grado C", "legajo": "#10247", "alumno": "Capra, Lautaro", "horario": "Mar/Jue 16:30 - 18:00", "profesor": "Vargas, Esteban Carlos", "apto": "Vigente"},
        {"deporte": "Fútbol Campo", "nivel": "Nivel Secundario", "curso": "5to Año B", "legajo": "#10245", "alumno": "Almirón, Santiago", "horario": "Mar/Jue 16:30 - 18:00", "profesor": "Acuña, Germán", "apto": "Vigente"},
        {"deporte": "Básquetbol", "nivel": "Nivel Secundario", "curso": "3er Año A", "legajo": "#10246", "alumno": "Benítez, Martina", "horario": "Mar/Jue 15:00 - 16:30", "profesor": "Pérez, Daniel", "apto": "Vigente"},
    ]

    columnas_deporte = [
        ("Disciplina Deportiva", 170, False),
        ("Nivel Educativo", 140, False),
        ("Curso", 110, False),
        ("Legajo", 90, False),
        ("Alumno Inscripto", 170, False),
        ("Días y Horarios", 170, False),
        ("Profesor Responsable", 180, False),
        ("Apto Médico", 100, False),
    ]

    header_table = create_table_header(columnas_deporte)

    def deporte_reporte_row(item: dict) -> ft.Container:
        return ft.Container(
            height=50,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=170, content=ft.Text(item["deporte"], size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=140, content=ft.Text(item["nivel"], size=13, color=MUTED)),
                    ft.Container(width=110, content=ft.Text(item["curso"], size=13, color=TEXT_COLOR)),
                    ft.Container(width=90, content=ft.Text(item["legajo"], size=13, weight=ft.FontWeight.BOLD, color=TEAL)),
                    ft.Container(width=170, content=ft.Text(item["alumno"], size=14, weight=ft.FontWeight.W_500, color=TEXT_COLOR)),
                    ft.Container(width=170, content=ft.Text(item["horario"], size=12, color=TEXT_COLOR)),
                    ft.Container(width=180, content=ft.Text(item["profesor"], size=13, color=MUTED)),
                    ft.Container(
                        width=100,
                        content=ft.Container(
                            padding=ft.Padding(6, 2, 6, 2),
                            bgcolor="#EBFEE6",
                            border_radius=4,
                            content=ft.Text(item["apto"], size=11, weight=ft.FontWeight.BOLD, color=ONLINE_GREEN),
                        ),
                    ),
                ],
            ),
        )

    table_container = create_table_container(
        header=header_table,
        rows=[deporte_reporte_row(d) for d in deportes_reporte_data],
    )

    pagination_bar = create_pagination_bar(
        texto_info="Mostrando alumnos asignados a disciplinas deportivas",
        pagina_actual=1,
        total_paginas=3,
    )

    return admin_layout(
        page=page,
        titulo="Reporte: Deportes, Niveles y Horarios",
        active_route="/admin/reportes",
        content_controls=[
            header_actions,
            filters_bar,
            table_container,
            pagination_bar,
        ],
    )