import flet as ft
import httpx
from frontend.app.api_client import api_client
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
    """Retorna la vista completa del directorio de alumnos consumiendo la API de FastAPI."""

    # Asegurar token desde client_storage si la página fue recargada
    token_almacenado = page.client_storage.get("auth_token")
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    # ==================== 1. BARRA DE FILTROS Y ACCIÓN ====================
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
                    hint_text="Buscar por apellido o legajo...",
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
                    filtro_dropdown("Nivel: Todos", 140, ["Todos", "Nivel Inicial", "Nivel Primario", "Nivel Secundario"]),
                    filtro_dropdown("Curso: Todos", 140, ["Todos", "Sala 5", "1er Grado", "4to Grado", "5to Año"]),
                ],
            ),
            btn_nuevo_alumno,
        ],
    )

    # ==================== 2. LLAMADA AL BACKEND ====================
    alumnos_data: list[dict] = []
    error_servidor = False

    try:
        alumnos_data = api_client.get_alumnos(solo_activos=True)
    except (httpx.RequestError, httpx.HTTPStatusError):
        error_servidor = True

    columnas_alumnos = [
        ("Legajo", 90, False),
        ("DNI", 110, False),
        ("Apellido", 130, False),
        ("Nombre", 140, False),
        ("Curso", 120, False),
        ("Teléfono", 120, False),
        ("Correo Electrónico", 210, False),
        ("Estado", 95, False),
        ("Acciones", 80, True),
    ]

    header_table = create_table_header(columnas_alumnos)

    def alumno_row(item: dict) -> ft.Container:
        legajo = str(item.get("legajo", ""))
        dni = str(item.get("dni", ""))
        apellido = item.get("apellido", "")
        nombre = item.get("nombre", "")
        curso = str(item.get("curso") or item.get("id_curso") or "Sin Asignar")
        telefono = item.get("telefono") or "-"
        correo = item.get("correo_electronico") or item.get("email") or "-"
        
        # Mapeo de estado si viene booleano o string
        estado_raw = item.get("estado")
        if isinstance(estado_raw, bool):
            estado_texto = "Activo" if estado_raw else "Inactivo"
        elif estado_raw:
            estado_texto = str(estado_raw)
        else:
            estado_texto = "Activo"

        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=90, content=ft.Text(legajo, size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=110, content=ft.Text(dni, size=13, color=TEXT_COLOR)),
                    ft.Container(width=130, content=ft.Text(apellido, size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=140, content=ft.Text(nombre, size=14, color=TEXT_COLOR)),
                    ft.Container(width=120, content=ft.Text(curso, size=13, color=TEAL)),
                    ft.Container(width=120, content=ft.Text(telefono, size=13, color=TEXT_COLOR)),
                    ft.Container(width=210, content=ft.Text(correo, size=13, color=MUTED)),
                    ft.Container(width=95, content=status_badge(estado_texto)),
                    ft.Container(
                        width=80,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=8,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    icon_size=16,
                                    icon_color=TEAL,
                                    tooltip="Editar Alumno",
                                    padding=0,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_size=16,
                                    icon_color=BADGE_RED_TXT,
                                    tooltip="Dar de baja",
                                    padding=0,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    # Construcción de filas según el resultado
    if error_servidor:
        filas_tabla = [
            ft.Container(
                padding=24,
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    "⚠️ No se pudo sincronizar con el servidor backend (FastAPI en http://127.0.0.1:8000). Verifique que esté ejecutándose.",
                    size=13,
                    color=BADGE_RED_TXT,
                ),
            )
        ]
        info_paginador = "Error de sincronización con la API"
    elif not alumnos_data:
        filas_tabla = [
            ft.Container(
                padding=24,
                alignment=ft.Alignment(0, 0),
                content=ft.Text("No se encontraron alumnos registrados en la base de datos.", size=13, color=MUTED),
            )
        ]
        info_paginador = "Mostrando 0 registros"
    else:
        filas_tabla = [alumno_row(a) for a in alumnos_data]
        info_paginador = f"Mostrando {len(alumnos_data)} alumnos registrados en la base de datos"

    table_container = create_table_container(
        header=header_table,
        rows=filas_tabla,
        min_width=1095,
    )

    pagination_bar = create_pagination_bar(
        texto_info=info_paginador,
        pagina_actual=1,
        total_paginas=1,
    )

    # ==================== 3. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Directorio de Estudiantes",
        active_route="/admin/alumnos",
        content_controls=[
            filters_bar,
            table_container,
            pagination_bar,
        ],
    )