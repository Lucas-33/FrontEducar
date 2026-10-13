import flet as ft
from frontend.app.components.constants import (
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    ONLINE_GREEN,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.form_controls import status_badge
from frontend.app.components.portal_layout import portal_layout
from frontend.app.components.table_view import (
    create_pagination_bar,
    create_table_container,
    create_table_header,
)


def get_docente_alumnos_view(page: ft.Page) -> ft.Row:
    """Retorna la nómina de estudiantes inscriptos en las materias del docente."""

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
                    hint_text="Buscar alumno o legajo...",
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
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    search_input,
                    filtro_dropdown("Materia: Física y Química", 200, ["Física y Química", "Laboratorio Ciencias", "Física I"]),
                    filtro_dropdown("Curso: 5to Año B", 150, ["5to Año B", "4to Año A"]),
                ],
            ),
            ft.Button(
                content=ft.Row(
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.SAVE_OUTLINED, size=16, color=BG_WHITE),
                        ft.Text("Guardar Asistencia", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
                    ],
                ),
                bgcolor=TEAL,
                height=CONTROL_HEIGHT,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
                on_click=lambda _: None,
            ),
        ],
    )

    alumnos_data = [
        {"legajo": "#10245", "alumno": "Almirón, Santiago", "curso": "5to Año B", "asistencia": "94%", "promedio": "8.50", "presente": True},
        {"legajo": "#10249", "alumno": "Flores, Facundo Joaquín", "curso": "5to Año B", "asistencia": "91%", "promedio": "9.00", "presente": True},
        {"legajo": "#10254", "alumno": "Gutiérrez, Ignacio Tomás", "curso": "5to Año B", "asistencia": "88%", "promedio": "7.25", "presente": True},
        {"legajo": "#10258", "alumno": "Navarro, Camila Sol", "curso": "5to Año B", "asistencia": "78%", "promedio": "6.80", "presente": False},
        {"legajo": "#10261", "alumno": "Villalba, Mateo David", "curso": "5to Año B", "asistencia": "96%", "promedio": "9.50", "presente": True},
    ]

    columnas_alumnos = [
        ("Legajo", 100, False),
        ("Estudiante", 220, False),
        ("Curso", 130, False),
        ("% Asistencia", 130, False),
        ("Promedio Actual", 140, False),
        ("Asistencia Hoy", 140, True),
    ]

    header_table = create_table_header(columnas_alumnos)

    def alumno_row(item: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=100, content=ft.Text(item["legajo"], size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=220, content=ft.Text(item["alumno"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=130, content=ft.Text(item["curso"], size=14, color=MUTED)),
                    ft.Container(width=130, content=ft.Text(item["asistencia"], size=13, weight=ft.FontWeight.W_500, color=ONLINE_GREEN)),
                    ft.Container(width=140, content=ft.Text(item["promedio"], size=14, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
                    ft.Container(
                        width=140,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Checkbox(value=item["presente"], active_color=TEAL),
                    ),
                ],
            ),
        )

    tabla_alumnos = create_table_container(
        header=header_table,
        rows=[alumno_row(a) for a in alumnos_data],
        min_width=860,
    )

    pagination_bar = create_pagination_bar(
        texto_info="Mostrando nómina de 5 alumnos en Física y Química (5to B)",
        pagina_actual=1,
        total_paginas=1,
    )

    return portal_layout(
        page=page,
        titulo="Nómina y Asistencia de Alumnos",
        active_route="/portal/docente/alumnos",
        rol="Docente",
        usuario_nombre="Prof. Román Martínez",
        usuario_sub="Legajo #20101 · Ciencias Exactas",
        content_controls=[
            filters_bar,
            tabla_alumnos,
            pagination_bar,
        ],
    )