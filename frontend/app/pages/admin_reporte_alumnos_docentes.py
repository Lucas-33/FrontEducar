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
from frontend.app.components.form_controls import status_badge
from frontend.app.components.table_view import (
    create_pagination_bar,
    create_table_container,
    create_table_header,
)


def get_admin_reporte_alumnos_docentes_view(page: ft.Page) -> ft.Row:
    """Retorna el reporte oficial consolidado de Alumnos por Curso y Docentes por Nivel."""

    # ==================== 1. ENCABEZADO Y ACCIONES DE EXPORTACIÓN ====================
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
                            ft.Text("Nómina Oficial: Alumnos por Curso y Nivel", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ft.Text("Listado administrativo para actas de secretaría académica", size=12, color=MUTED),
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

    # ==================== 2. FILTROS ACADÉMICOS ====================
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
                    hint_text="Filtrar por apellido, legajo...",
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
            filtro_dropdown("Nivel: Todos", 145, ["Todos", "Nivel Inicial", "Nivel Primario", "Nivel Secundario"]),
            filtro_dropdown("Curso: 5to Año B", 155, ["Todos", "Sala 5 A", "4to Grado A", "5to Año B", "6to Año A"]),
            filtro_dropdown("Turno: Mañana", 135, ["Todos", "Mañana", "Tarde", "Jornada Extendida"]),
        ],
    )

    # ==================== 3. TABLA DE REPORTE ====================
    alumnos_curso_data = [
        {"nivel": "Nivel Secundario", "curso": "5to Año B", "legajo": "#10245", "apellido": "Almirón", "nombre": "Santiago", "tutor": "Martín Gómez (3624-912831)", "estado": "Regular"},
        {"nivel": "Nivel Secundario", "curso": "5to Año B", "legajo": "#10249", "apellido": "Flores", "nombre": "Facundo Joaquín", "tutor": "Silvia Flores (3624-774411)", "estado": "Regular"},
        {"nivel": "Nivel Secundario", "curso": "5to Año B", "legajo": "#10254", "apellido": "Gutiérrez", "nombre": "Ignacio Tomás", "tutor": "Paula Ruiz (3624-118822)", "estado": "Regular"},
        {"nivel": "Nivel Secundario", "curso": "5to Año B", "legajo": "#10258", "apellido": "Navarro", "nombre": "Camila Sol", "tutor": "Jorge Navarro (3624-990033)", "estado": "Pendiente"},
        {"nivel": "Nivel Secundario", "curso": "5to Año B", "legajo": "#10261", "apellido": "Villalba", "nombre": "Mateo David", "tutor": "Estela Villalba (3624-331122)", "estado": "Regular"},
    ]

    columnas_reporte = [
        ("Nivel Educativo", 160, False),
        ("Curso / División", 140, False),
        ("Legajo", 100, False),
        ("Apellido", 150, False),
        ("Nombre", 160, False),
        ("Contacto Padre / Tutor", 260, False),
        ("Estado Matrícula", 130, False),
    ]

    header_table = create_table_header(columnas_reporte)

    def alumno_reporte_row(item: dict) -> ft.Container:
        return ft.Container(
            height=50,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=160, content=ft.Text(item["nivel"], size=13, color=MUTED)),
                    ft.Container(width=140, content=ft.Text(item["curso"], size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=100, content=ft.Text(item["legajo"], size=13, weight=ft.FontWeight.BOLD, color=TEAL)),
                    ft.Container(width=150, content=ft.Text(item["apellido"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=160, content=ft.Text(item["nombre"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=260, content=ft.Text(item["tutor"], size=13, color=MUTED)),
                    ft.Container(width=130, content=status_badge(item["estado"])),
                ],
            ),
        )

    table_container = create_table_container(
        header=header_table,
        rows=[alumno_reporte_row(a) for a in alumnos_curso_data],
    )

    pagination_bar = create_pagination_bar(
        texto_info="Mostrando 1-5 de 22 alumnos del curso seleccionado",
        pagina_actual=1,
        total_paginas=5,
    )

    # ==================== 4. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Reporte: Alumnos por Curso y Nivel",
        active_route="/admin/reportes",
        content_controls=[
            header_actions,
            filters_bar,
            table_container,
            pagination_bar,
        ],
    )