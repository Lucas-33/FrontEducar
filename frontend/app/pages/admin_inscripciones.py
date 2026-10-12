import flet as ft
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    ONLINE_GREEN,
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


def get_admin_inscripciones_view(page: ft.Page) -> ft.Row:
    """Retorna la vista de Solicitudes de Admisión e Inscripción al Ciclo Lectivo."""

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
                    hint_text="Buscar postulante o DNI...",
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
                    filtro_dropdown("Nivel: Todos", 140, ["Todos", "Nivel Inicial", "Nivel Primario", "Nivel Secundario"]),
                    filtro_dropdown("Estado: Todos", 140, ["Todos", "Pendiente", "Aprobado", "Rechazado"]),
                ],
            ),
            ft.Button(
                content=ft.Row(
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.FILE_DOWNLOAD_OUTLINED, size=16, color=BG_WHITE),
                        ft.Text("Exportar Listado", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
                    ],
                ),
                bgcolor=TEAL,
                height=CONTROL_HEIGHT,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
                    padding=ft.Padding(20, 10, 20, 10),
                ),
                on_click=lambda _: None,
            ),
        ],
    )

    # ==================== 2. TABLA DE SOLICITUDES ====================
    solicitudes_data = [
        {"nro": "#SOL-2025-081", "postulante": "Gómez, Santiago", "dni": "52.410.220", "nivel": "Nivel Primario (1er Grado)", "tutor": "Martín Gómez", "contacto": "3624-412345", "fecha": "14/10/2026", "estado": "Pendiente"},
        {"nro": "#SOL-2025-080", "postulante": "Sosa, Valentina Lucía", "dni": "53.881.092", "nivel": "Nivel Inicial (Sala 4)", "tutor": "Carla Morales", "contacto": "3624-998811", "fecha": "13/10/2026", "estado": "Pendiente"},
        {"nro": "#SOL-2025-079", "postulante": "Valdez, Matías Joaquín", "dni": "47.102.399", "nivel": "Nivel Secundario (1er Año)", "tutor": "Esteban Valdez", "contacto": "3624-001928", "fecha": "12/10/2026", "estado": "Aprobado"},
        {"nro": "#SOL-2025-078", "postulante": "Romero, Camila Sofía", "dni": "49.112.441", "nivel": "Nivel Primario (3er Grado)", "tutor": "Silvia Almirón", "contacto": "3624-332211", "fecha": "11/10/2026", "estado": "Aprobado"},
        {"nro": "#SOL-2025-077", "postulante": "Fernández, Tomás", "dni": "46.992.112", "nivel": "Nivel Secundario (4to Año)", "tutor": "Hugo Fernández", "contacto": "3624-771122", "fecha": "10/10/2026", "estado": "Rechazado"},
    ]

    columnas_solicitudes = [
        ("N° Solicitud", 130, False),
        ("Aspirante / Postulante", 180, False),
        ("DNI", 120, False),
        ("Nivel Postulado", 180, False),
        ("Padre / Tutor", 160, False),
        ("Teléfono", 130, False),
        ("Fecha", 110, False),
        ("Estado", 110, False),
        ("Acciones de Secretaría", None, True),
    ]

    header_table = create_table_header(columnas_solicitudes)

    def solicitud_row(item: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=130, content=ft.Text(item["nro"], size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=180, content=ft.Text(item["postulante"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=120, content=ft.Text(item["dni"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=180, content=ft.Text(item["nivel"], size=13, color=MUTED)),
                    ft.Container(width=160, content=ft.Text(item["tutor"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=130, content=ft.Text(item["contacto"], size=13, color=MUTED)),
                    ft.Container(width=110, content=ft.Text(item["fecha"], size=13, color=MUTED)),
                    ft.Container(width=110, content=status_badge(item["estado"])),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=12,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(icon=ft.Icons.CHECK_CIRCLE_OUTLINE, icon_size=18, icon_color=ONLINE_GREEN, tooltip="Aprobar Admisión", padding=0),
                                ft.IconButton(icon=ft.Icons.REMOVE_RED_EYE_OUTLINED, icon_size=18, icon_color=TEAL, tooltip="Ver Documentación", padding=0),
                                ft.IconButton(icon=ft.Icons.CANCEL_OUTLINED, icon_size=18, icon_color=BADGE_RED_TXT, tooltip="Rechazar", padding=0),
                            ],
                        ),
                    ),
                ],
            ),
        )

    table_container = create_table_container(
        header=header_table,
        rows=[solicitud_row(s) for s in solicitudes_data],
    )

    pagination_bar = create_pagination_bar(
        texto_info="Mostrando 1-5 de 45 solicitudes recibidas",
        pagina_actual=1,
        total_paginas=9,
    )

    # ==================== 3. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Admisiones — Solicitudes de Inscripción",
        active_route="/admin/inscripciones",
        content_controls=[
            filters_bar,
            table_container,
            pagination_bar,
        ],
    )