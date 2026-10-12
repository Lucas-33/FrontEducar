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


def get_admin_reporte_transporte_pasajeros_view(page: ft.Page) -> ft.Row:
    """Retorna el reporte oficial de Pasajeros agrupados por Recorrido de Transporte Escolar."""

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
                            ft.Text("Hoja de Ruta: Pasajeros por Recorrido de Transporte", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ft.Text("Planilla operativa para choferes y celadores institucionales", size=12, color=MUTED),
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
            filtro_dropdown("Recorrido: Recorrido 1 Norte", 220, ["Todos", "Recorrido 1 Norte", "Recorrido 2 Sur", "Recorrido 3 Centro", "Recorrido 4 Este"]),
            filtro_dropdown("Turno: Mañana", 140, ["Todos", "Mañana", "Tarde"]),
            filtro_dropdown("Nivel: Todos", 140, ["Todos", "Inicial", "Primario", "Secundario"]),
        ],
    )

    # Requerimiento: Alumnos por recorrido del servicio de transporte[cite: 5]
    pasajeros_reporte_data = [
        {"recorrido": "Recorrido 1 Norte", "legajo": "#10245", "alumno": "Almirón, Santiago", "curso": "5to Año B", "parada": "Av. Sarmiento 1840", "horario_recogida": "06:45 hs", "tutor_contacto": "Martín Gómez (3624-912831)", "estado": "Activo"},
        {"recorrido": "Recorrido 1 Norte", "legajo": "#10249", "alumno": "Flores, Facundo", "curso": "6to Año A", "parada": "Av. Sabin 320", "horario_recogida": "06:55 hs", "tutor_contacto": "Silvia Flores (3624-774411)", "estado": "Activo"},
        {"recorrido": "Recorrido 1 Norte", "legajo": "#10255", "alumno": "Méndez, Joaquín", "curso": "2do Grado A", "parada": "Av. Italia 1200", "horario_recogida": "07:05 hs", "tutor_contacto": "Carlos Méndez (3624-665544)", "estado": "Activo"},
        {"recorrido": "Recorrido 1 Norte", "legajo": "#10260", "alumno": "Suárez, Milagros", "curso": "Sala 4 A", "parada": "Ruta 16 y Av. Sarmiento", "horario_recogida": "07:15 hs", "tutor_contacto": "Romina Suárez (3624-223344)", "estado": "Activo"},
    ]

    columnas_transporte = [
        ("Recorrido Oficial", 160, False),
        ("Legajo", 90, False),
        ("Alumno Pasajero", 170, False),
        ("Curso", 110, False),
        ("Dirección / Parada", 220, False),
        ("Hora Recogida", 120, False),
        ("Teléfono Padre / Tutor", 190, False),
        ("Estado", 90, False),
    ]

    header_table = create_table_header(columnas_transporte)

    def pasajero_reporte_row(item: dict) -> ft.Container:
        return ft.Container(
            height=50,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=160, content=ft.Text(item["recorrido"], size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=90, content=ft.Text(item["legajo"], size=13, weight=ft.FontWeight.BOLD, color=TEAL)),
                    ft.Container(width=170, content=ft.Text(item["alumno"], size=14, weight=ft.FontWeight.W_500, color=TEXT_COLOR)),
                    ft.Container(width=110, content=ft.Text(item["curso"], size=13, color=MUTED)),
                    ft.Container(width=220, content=ft.Text(item["parada"], size=13, color=TEXT_COLOR)),
                    ft.Container(width=120, content=ft.Text(item["horario_recogida"], size=12, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=190, content=ft.Text(item["tutor_contacto"], size=12, color=MUTED)),
                    ft.Container(width=90, content=status_badge(item["estado"])),
                ],
            ),
        )

    table_container = create_table_container(
        header=header_table,
        rows=[pasajero_reporte_row(p) for p in pasajeros_reporte_data],
    )

    pagination_bar = create_pagination_bar(
        texto_info="Mostrando 4 de 28 pasajeros del Recorrido 1 Norte",
        pagina_actual=1,
        total_paginas=7,
    )

    return admin_layout(
        page=page,
        titulo="Reporte: Alumnos por Recorrido de Transporte",
        active_route="/admin/reportes",
        content_controls=[
            header_actions,
            filters_bar,
            table_container,
            pagination_bar,
        ],
    )