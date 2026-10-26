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
from frontend.app.components.table_view import (
    create_pagination_bar,
    create_table_container,
    create_table_header,
)


async def get_admin_horarios_view(page: ft.Page) -> ft.Row:
    """Vista de Turnos y Horarios conectada a la API."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    # ==================== ESTADO DE LA VISTA ====================
    estado: dict = {"horarios": [], "texto": ""}

    try:
        estado["horarios"] = await api_client.get_horarios()
    except Exception:
        estado["horarios"] = []

    # ==================== 1. BARRA DE FILTROS Y ACCIÓN ====================
    search_field = ft.TextField(
        hint_text="Buscar horario o turno...",
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

    btn_nuevo_horario = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                ft.Text(
                    "Nuevo Horario", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE
                ),
            ],
        ),
        bgcolor=TEAL,
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            padding=ft.Padding(24, 12, 24, 12),
        ),
    )

    filters_bar = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[search_input],
            ),
            btn_nuevo_horario,
        ],
    )

    aviso_error = ft.Text(
        "", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False
    )

    # ==================== 2. TABLA DE HORARIOS ====================
    columnas_horarios = [
        ("Código", 140, False),
        ("Descripción del Horario", None, False),
        ("Acciones", 120, True),
    ]

    header_table = create_table_header(columnas_horarios)
    table_holder = ft.Container()
    pagination_holder = ft.Container()

    def mostrar_error(mensaje: str):
        aviso_error.value = f"⚠️ {mensaje}"
        aviso_error.visible = True
        try:
            page.update()
        except Exception:
            pass

    def horario_row(item: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=140,
                        content=ft.Text(
                            f"HOR-{item['id_horario']}",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Text(
                            item.get("descripcion", "-"),
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=120,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=6,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    icon_size=17,
                                    icon_color=TEAL,
                                    tooltip="Editar horario",
                                    padding=0,
                                    on_click=lambda e, h=item: abrir_editar_horario(h),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_size=17,
                                    icon_color=BADGE_RED_TXT,
                                    tooltip="Eliminar horario",
                                    padding=0,
                                    on_click=lambda e, h=item: (
                                        confirmar_eliminar_horario(h)
                                    ),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    def horarios_filtrados() -> list[dict]:
        texto = (estado["texto"] or "").strip().lower()
        resultado = []
        for h in estado["horarios"]:
            etiqueta = (
                f"{h.get('descripcion', '')} hor-{h.get('id_horario', '')}".lower()
            )
            if texto and texto not in etiqueta:
                continue
            resultado.append(h)
        return resultado

    def render():
        visibles = horarios_filtrados()
        if not estado["horarios"]:
            mensaje_vacio = "No hay horarios cargados."
        else:
            mensaje_vacio = "No hay horarios que coincidan con la búsqueda."

        table_holder.content = create_table_container(
            header=header_table,
            rows=[horario_row(h) for h in visibles]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(mensaje_vacio, size=13, color=MUTED),
                )
            ],
            min_width=720,
        )
        pagination_holder.content = create_pagination_bar(
            texto_info=f"Mostrando {len(visibles)} de {len(estado['horarios'])} horarios registrados",
            pagina_actual=1,
            total_paginas=max(1, (len(visibles) + 9) // 10),
        )
        try:
            page.update()
        except Exception:
            pass

    async def recargar():
        try:
            estado["horarios"] = await api_client.get_horarios()
        except Exception as err:
            mostrar_error(f"No se pudo refrescar la lista de horarios: {err}")
        render()

    def on_buscar(e):
        estado["texto"] = search_field.value or ""
        render()

    search_field.on_change = on_buscar

    # ==================== 3. DIÁLOGO NUEVO HORARIO ====================
    def abrir_nuevo_horario(e):
        descripcion_field = ft.TextField(
            label="Descripción del horario *",
            hint_text="Ej: Turno Mañana (08:00 - 12:00)",
            width=380,
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar(e):
            descripcion = (descripcion_field.value or "").strip()
            if not descripcion:
                error_text.value = "La descripción del horario es obligatoria."
                error_text.visible = True
                error_text.update()
                return
            try:
                await api_client.create_horario({"descripcion": descripcion})
            except httpx.HTTPStatusError as err:
                detalle = "Error al crear el horario."
                try:
                    detalle = err.response.json().get("detail", detalle)
                except Exception:
                    pass
                error_text.value = f"⚠️ {detalle}"
                error_text.visible = True
                error_text.update()
                return
            except httpx.RequestError:
                error_text.value = "⚠️ Error de conexión con el backend."
                error_text.visible = True
                error_text.update()
                return
            page.pop_dialog()
            await recargar()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nuevo Horario", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                spacing=14,
                width=380,
                tight=True,
                controls=[descripcion_field, error_text],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button(
                    "Crear Horario", bgcolor=TEAL, color=BG_WHITE, on_click=guardar
                ),
            ],
        )
        page.show_dialog(dlg)

    btn_nuevo_horario.on_click = abrir_nuevo_horario

    # ==================== 3b. DIÁLOGOS EDITAR / ELIMINAR HORARIO ====================
    def abrir_editar_horario(horario: dict):
        descripcion_field = ft.TextField(
            label="Descripción del horario *",
            value=horario.get("descripcion") or "",
            width=380,
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar_edicion(e):
            descripcion = (descripcion_field.value or "").strip()
            if not descripcion:
                error_text.value = "La descripción del horario es obligatoria."
                error_text.visible = True
                error_text.update()
                return
            try:
                await api_client.update_horario(
                    horario["id_horario"], {"descripcion": descripcion}
                )
            except httpx.HTTPStatusError as err:
                detalle = "Error al actualizar el horario."
                try:
                    detalle = err.response.json().get("detail", detalle)
                except Exception:
                    pass
                error_text.value = f"⚠️ {detalle}"
                error_text.visible = True
                error_text.update()
                return
            except httpx.RequestError:
                error_text.value = "⚠️ Error de conexión con el backend."
                error_text.visible = True
                error_text.update()
                return
            page.pop_dialog()
            await recargar()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                f"Editar Horario HOR-{horario['id_horario']}",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            content=ft.Column(
                spacing=14,
                width=380,
                tight=True,
                controls=[descripcion_field, error_text],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button(
                    "Guardar Cambios",
                    bgcolor=TEAL,
                    color=BG_WHITE,
                    on_click=guardar_edicion,
                ),
            ],
        )
        page.show_dialog(dlg)

    def confirmar_eliminar_horario(horario: dict):
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def eliminar(e):
            try:
                await api_client.delete_horario(horario["id_horario"])
            except httpx.HTTPStatusError as err:
                detalle = "No se pudo eliminar el horario."
                try:
                    detalle = err.response.json().get("detail", detalle)
                except Exception:
                    pass
                error_text.value = f"⚠️ {detalle}"
                error_text.visible = True
                error_text.update()
                return
            except httpx.RequestError:
                error_text.value = "⚠️ Error de conexión con el backend."
                error_text.visible = True
                error_text.update()
                return
            page.pop_dialog()
            await recargar()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Eliminar Horario", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                spacing=14,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        f"¿Confirma eliminar el horario «{horario.get('descripcion')}»? "
                        "Solo es posible si no está asignado a grupos o actividades.",
                        size=13,
                        color=TEXT_COLOR,
                    ),
                    error_text,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button(
                    "Eliminar", bgcolor=BADGE_RED_TXT, color=BG_WHITE, on_click=eliminar
                ),
            ],
        )
        page.show_dialog(dlg)

    render()

    # ==================== 4. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Gestión Académica — Turnos y Horarios",
        active_route="/admin/horarios",
        content_controls=[
            filters_bar,
            aviso_error,
            table_holder,
            pagination_holder,
        ],
    )
