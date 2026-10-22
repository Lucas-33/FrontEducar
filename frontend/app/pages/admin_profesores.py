import flet as ft

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


async def get_admin_profesores_view(page: ft.Page) -> ft.Row:
    """Vista de la Nómina del Personal Docente conectada a la API."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    estado: dict = {"profesores": [], "texto": ""}

    try:
        estado["profesores"] = await api_client.get_profesores(solo_activos=False)
    except Exception:
        estado["profesores"] = []

    # ==================== 1. BARRA DE BÚSQUEDA Y FILTROS ====================
    search_field = ft.TextField(
        hint_text="Buscar docente por especialidad o apellido...",
        hint_style=ft.TextStyle(size=14, color=MUTED),
        text_size=14,
        color=TEXT_COLOR,
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding(0, 0, 0, 10),
        expand=True,
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
                search_field,
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
                ft.Text(
                    "Nuevo Profesor",
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=BG_WHITE,
                ),
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
                        "Estado: Todos",
                        144,
                        ["Todos", "Activo", "Licencia", "Inactivo"],
                    ),
                ],
            ),
            btn_nuevo_profesor,
        ],
    )

    aviso_error = ft.Text(
        "", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False
    )

    # ==================== 2. TABLA DE PROFESORES ====================
    columnas_profesores = [
        ("Legajo", 80, False),
        ("DNI", 105, False),
        ("Apellido", 120, False),
        ("Nombre", 130, False),
        ("Especialidad Principal", 180, False),
        ("Correo Electrónico", 190, False),
        ("Teléfono", 115, False),
        ("Estado", 95, False),
        ("Acciones", 80, True),
    ]

    header_table = create_table_header(columnas_profesores)
    table_holder = ft.Container()
    pagination_holder = ft.Container()

    def mostrar_error(mensaje: str):
        aviso_error.value = f"⚠️ {mensaje}"
        aviso_error.visible = True
        try:
            page.update()
        except Exception:
            pass

    def profesor_row(item: dict) -> ft.Container:
        async def eliminar_profesor(e):
            try:
                await api_client.delete_profesor(int(item["legajo"]))
            except Exception as err:
                mostrar_error(
                    f"No se pudo dar de baja al docente {item['legajo']}: {err}"
                )
                return
            await recargar()

        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=80,
                        content=ft.Text(
                            str(item.get("legajo", "")),
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        width=105,
                        content=ft.Text(
                            str(item.get("dni", "")), size=13, color=TEXT_COLOR
                        ),
                    ),
                    ft.Container(
                        width=120,
                        content=ft.Text(
                            item.get("apellido", ""),
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=130,
                        content=ft.Text(
                            item.get("nombre", ""), size=14, color=TEXT_COLOR
                        ),
                    ),
                    ft.Container(
                        width=180,
                        content=ft.Text(
                            item.get("especialidad", ""), size=13, color=TEXT_COLOR
                        ),
                    ),
                    ft.Container(
                        width=190,
                        content=ft.Text(
                            item.get("correo_electronico", ""), size=13, color=MUTED
                        ),
                    ),
                    ft.Container(
                        width=115,
                        content=ft.Text(
                            item.get("telefono", ""), size=13, color=TEXT_COLOR
                        ),
                    ),
                    ft.Container(
                        width=95,
                        content=status_badge(item.get("estado", "ACTIVO").capitalize()),
                    ),
                    ft.Container(
                        width=80,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=8,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_size=16,
                                    icon_color=BADGE_RED_TXT,
                                    tooltip="Dar de baja",
                                    padding=0,
                                    on_click=eliminar_profesor,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    def profesores_filtrados() -> list[dict]:
        texto = (estado["texto"] or "").lower()
        if not texto:
            return estado["profesores"]
        return [
            p
            for p in estado["profesores"]
            if texto
            in f"{p.get('apellido', '')} {p.get('nombre', '')} {p.get('especialidad', '')} {p.get('legajo', '')}".lower()
        ]

    def render():
        visibles = profesores_filtrados()
        table_holder.content = create_table_container(
            header=header_table,
            rows=[profesor_row(p) for p in visibles]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "No hay docentes que coincidan con la búsqueda.",
                        size=13,
                        color=MUTED,
                    ),
                )
            ],
        )
        pagination_holder.content = create_pagination_bar(
            texto_info=f"Mostrando {len(visibles)} de {len(estado['profesores'])} docentes registrados",
            pagina_actual=1,
            total_paginas=max(1, (len(visibles) + 9) // 10),
        )
        try:
            page.update()
        except Exception:
            pass

    async def recargar():
        try:
            estado["profesores"] = await api_client.get_profesores(solo_activos=False)
        except Exception as err:
            mostrar_error(f"No se pudo refrescar la lista de docentes: {err}")
        render()

    def on_buscar(e):
        estado["texto"] = search_field.value or ""
        render()

    search_field.on_change = on_buscar

    render()

    # ==================== 3. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Nómina del Personal Docente",
        active_route="/admin/profesores",
        content_controls=[
            filters_bar,
            aviso_error,
            table_holder,
            pagination_holder,
        ],
    )
