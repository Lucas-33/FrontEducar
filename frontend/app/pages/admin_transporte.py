import flet as ft
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BADGE_RED_TXT,
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
from frontend.app.components.table_view import (
    create_pagination_bar,
    create_table_container,
    create_table_header,
)


def get_admin_transporte_view(page: ft.Page) -> ft.Row:
    """Retorna la vista del Servicio de Transporte Escolar (Gestión de los 4 Recorridos)."""

    # ==================== 1. TARJETAS DE LOS 4 RECORRIDOS ====================
    def recorrido_card(num: int, nombre: str, chofer: str, capacidad: str, ocupacion: float, celador: str) -> ft.Container:
        return ft.Container(
            expand=True,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=20,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Container(
                                        width=28,
                                        height=28,
                                        bgcolor=TEAL_LIGHT,
                                        border_radius=14,
                                        alignment=ft.Alignment(0, 0),
                                        content=ft.Text(str(num), size=12, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                                    ),
                                    ft.Text(f"Recorrido {num}", size=15, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                                ],
                            ),
                            status_badge("Activo"),
                        ],
                    ),
                    ft.Text(nombre, size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Ocupación plazas", size=11, color=MUTED),
                                    ft.Text(capacidad, size=11, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                                ],
                            ),
                            ft.ProgressBar(value=ocupacion, color=TEAL, bgcolor=TEAL_LIGHT, height=6),
                        ],
                    ),
                    ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(f"Chofer: {chofer}", size=12, color=TEXT_COLOR),
                            ft.Text(f"Celador/a: {celador}", size=11, color=MUTED),
                        ],
                    ),
                ],
            ),
        )

    recorridos_banner = ft.Row(
        spacing=16,
        controls=[
            recorrido_card(1, "Zona Norte / La Liguria", "Mario Gómez (M-01)", "28 / 30", 0.93, "Estela Ríos"),
            recorrido_card(2, "Zona Sur / Fontana", "Carlos Valdez (M-02)", "25 / 30", 0.83, "Beatriz Silva"),
            recorrido_card(3, "Zona Centro / Barranqueras", "Jorge Acosta (M-03)", "30 / 30", 1.0, "Marcos Romero"),
            recorrido_card(4, "Zona Este / Aeropuerto", "Daniel Soto (M-04)", "20 / 30", 0.66, "Norma Maidana"),
        ],
    )

    # ==================== 2. BARRA DE FILTROS ====================
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
                    hint_text="Buscar alumno o parada...",
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

    btn_asignar = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                ft.Text("Nueva Asignación", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
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
                    filtro_dropdown("Recorrido: Todos", 170, ["Todos", "Recorrido 1 Norte", "Recorrido 2 Sur", "Recorrido 3 Centro", "Recorrido 4 Este"]),
                    filtro_dropdown("Turno: Mañana", 130, ["Todos", "Mañana", "Tarde"]),
                ],
            ),
            btn_asignar,
        ],
    )

    # ==================== 3. TABLA DE PASAJEROS ====================
    pasajeros_data = [
        {"legajo": "#10245", "alumno": "Almirón, Santiago", "curso": "5to Año B", "recorrido": "Recorrido 1 Norte", "parada": "Av. Sarmiento 1840", "tutor_tel": "3624-912831", "estado": "Activo"},
        {"legajo": "#10246", "alumno": "Benítez, Martina", "curso": "3er Año A", "recorrido": "Recorrido 3 Centro", "parada": "Pellegrini 450", "tutor_tel": "3624-551122", "estado": "Activo"},
        {"legajo": "#10247", "alumno": "Capra, Lautaro", "curso": "6to Grado C", "recorrido": "Recorrido 2 Sur", "parada": "Av. Castelli 820", "tutor_tel": "3624-884401", "estado": "Activo"},
        {"legajo": "#10248", "alumno": "Díaz, Sofía Valentina", "curso": "Sala 5 B", "recorrido": "Recorrido 4 Este", "parada": "Ruta 16 Km 14.5", "tutor_tel": "3624-119933", "estado": "Activo"},
        {"legajo": "#10249", "alumno": "Flores, Facundo", "curso": "6to Año A", "recorrido": "Recorrido 1 Norte", "parada": "Av. Sabin 320", "tutor_tel": "3624-774411", "estado": "Activo"},
    ]

    columnas_transporte = [
        ("Legajo", 90, False),
        ("Estudiante", 180, False),
        ("Curso", 130, False),
        ("Recorrido Asignado", 170, False),
        ("Dirección / Parada", 220, False),
        ("Teléfono Tutor", 140, False),
        ("Estado", 100, False),
        ("Acciones", None, True),
    ]

    header_table = create_table_header(columnas_transporte)

    def pasajero_row(item: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=90, content=ft.Text(item["legajo"], size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=180, content=ft.Text(item["alumno"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=130, content=ft.Text(item["curso"], size=14, color=MUTED)),
                    ft.Container(width=170, content=ft.Text(item["recorrido"], size=13, weight=ft.FontWeight.W_500, color=TEAL)),
                    ft.Container(width=220, content=ft.Text(item["parada"], size=13, color=TEXT_COLOR)),
                    ft.Container(width=140, content=ft.Text(item["tutor_tel"], size=13, color=MUTED)),
                    ft.Container(width=100, content=status_badge(item["estado"])),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=12,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_size=16, icon_color=TEAL, tooltip="Cambiar Recorrido", padding=0),
                                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_size=16, icon_color=BADGE_RED_TXT, tooltip="Baja del Servicio", padding=0),
                            ],
                        ),
                    ),
                ],
            ),
        )

    table_container = create_table_container(
        header=header_table,
        rows=[pasajero_row(p) for p in pasajeros_data],
    )

    pagination_bar = create_pagination_bar(
        texto_info="Mostrando 1-5 de 103 alumnos con servicio activo",
        pagina_actual=1,
        total_paginas=21,
    )

    # ==================== 4. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Servicio de Transporte Escolar (4 Recorridos)",
        active_route="/admin/transporte",
        content_controls=[
            recorridos_banner,
            filters_bar,
            table_container,
            pagination_bar,
        ],
    )