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


def get_admin_profesores_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa de la Nómina del Personal Docente con AdminLayout."""

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
                    hint_text="Buscar docente por especialidad o apellido...",
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

    btn_nuevo_profesor = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                ft.Text("Nuevo Profesor", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
            ],
        ),
        bgcolor=TEAL,
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            padding=ft.Padding(24, 12, 24, 12),
        ),
        on_click=lambda _: page.go("/admin/profesores/nuevo"),
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
                    filtro_dropdown(
                        "Área: Todas",
                        125,
                        ["Todas", "Ciencias Exactas", "Lenguas", "Educación Física", "Tecnología"],
                    ),
                    filtro_dropdown(
                        "Estado: Activo",
                        144,
                        ["Todos", "Activo", "Licencia", "Inactivo"],
                    ),
                ],
            ),
            btn_nuevo_profesor,
        ],
    )

    # ==================== 2. TABLA DE PROFESORES ====================
    profesores_data = [
        {
            "legajo": "#20101",
            "dni": "31.902.115",
            "apellido": "Martínez",
            "nombre": "Román Alberto",
            "especialidad": "Ciencias Naturales / Física",
            "email": "r.martinez@educar.edu.ar",
            "telefono": "3624-912881",
            "estado": "Activo",
        },
        {
            "legajo": "#20102",
            "dni": "29.448.109",
            "apellido": "Sánchez",
            "nombre": "Guillermina",
            "especialidad": "Matemática Aplicada",
            "email": "g.sanchez@educar.edu.ar",
            "telefono": "3624-402919",
            "estado": "Activo",
        },
        {
            "legajo": "#20103",
            "dni": "35.102.394",
            "apellido": "Vargas",
            "nombre": "Esteban Carlos",
            "especialidad": "Educación Física / Natación",
            "email": "e.vargas@educar.edu.ar",
            "telefono": "3624-001229",
            "estado": "Licencia",
        },
        {
            "legajo": "#20104",
            "dni": "33.910.224",
            "apellido": "Duarte",
            "nombre": "María Florencia",
            "especialidad": "Lengua y Literatura",
            "email": "f.duarte@educar.edu.ar",
            "telefono": "3624-114402",
            "estado": "Activo",
        },
        {
            "legajo": "#20105",
            "dni": "28.990.124",
            "apellido": "Ortega",
            "nombre": "Luis Humberto",
            "especialidad": "Informática / Robótica",
            "email": "l.ortega@educar.edu.ar",
            "telefono": "3624-556601",
            "estado": "Inactivo",
        },
    ]

    # Tuplas: (Título, Ancho px, Alineación derecha)
    columnas_profesores = [
        ("Legajo", 90, False),
        ("DNI", 120, False),
        ("Apellido", 150, False),
        ("Nombre", 150, False),
        ("Especialidad Principal", 220, False),
        ("Correo Electrónico", 220, False),
        ("Teléfono", 120, False),
        ("Estado", 100, False),
        ("Acciones", None, True),
    ]

    header_table = create_table_header(columnas_profesores)

    def profesor_row(item: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=90, content=ft.Text(item["legajo"], size=14, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=120, content=ft.Text(item["dni"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=150, content=ft.Text(item["apellido"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=150, content=ft.Text(item["nombre"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=220, content=ft.Text(item["especialidad"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=220, content=ft.Text(item["email"], size=14, color=MUTED)),
                    ft.Container(width=120, content=ft.Text(item["telefono"], size=14, color=TEXT_COLOR)),
                    ft.Container(width=100, content=status_badge(item["estado"])),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=12,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    icon_size=16,
                                    icon_color=TEAL,
                                    tooltip="Editar",
                                    padding=0,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_size=16,
                                    icon_color=BADGE_RED_TXT,
                                    tooltip="Eliminar",
                                    padding=0,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    table_container = create_table_container(
        header=header_table,
        rows=[profesor_row(p) for p in profesores_data],
    )

    pagination_bar = create_pagination_bar(
        texto_info="Mostrando 1-5 de 86 docentes registrados",
        pagina_actual=1,
        total_paginas=2,
    )

    # ==================== 3. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Nómina del Personal Docente",
        active_route="/admin/profesores",
        content_controls=[
            filters_bar,
            table_container,
            pagination_bar,
        ],
    )