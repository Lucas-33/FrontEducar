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


async def get_admin_profesores_view(page: ft.Page) -> ft.Row:
    """Vista de la Nómina del Personal Docente con edición y baja lógica."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    estado: dict = {"profesores": [], "texto": "", "filtro_estado": "Todos"}

    try:
        estado["profesores"] = await api_client.get_profesores(solo_activos=False)
    except Exception:
        estado["profesores"] = []

    # ==================== 1. FILTROS Y ACCIÓN ====================
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

    filtro_estado_dropdown = ft.Dropdown(
        hint_text="Estado: Todos",
        hint_style=ft.TextStyle(size=14, color=TEXT_COLOR),
        text_size=14,
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding(12, 0, 8, 12),
        options=[
            ft.dropdown.Option(opc)
            for opc in ["Todos", "Activo", "Licencia", "Inactivo"]
        ],
    )

    filtro_estado_container = ft.Container(
        width=150,
        height=CONTROL_HEIGHT,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=BORDER_RADIUS,
        content=filtro_estado_dropdown,
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
                controls=[search_input, filtro_estado_container],
            ),
            btn_nuevo_profesor,
        ],
    )

    aviso_error = ft.Text(
        "", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False
    )

    columnas_profesores = [
        ("Legajo", 80, False),
        ("DNI", 105, False),
        ("Apellido", 120, False),
        ("Nombre", 130, False),
        ("Especialidad Principal", 180, False),
        ("Correo Electrónico", 190, False),
        ("Teléfono", 115, False),
        ("Estado", 95, False),
    ]

    header_table = create_table_header(columnas_profesores)
    table_holder = ft.Container()
    pagination_holder = ft.Container()

    def mostrar_error(mensaje: str):
        aviso_error.value = f"⚠️ {mensaje}"
        aviso_error.visible = True
        page.update()

    # ==================== 2. DIÁLOGOS DE EDICIÓN Y BAJA ====================
    def abrir_editar_profesor(profesor: dict):
        legajo = profesor.get("legajo")
        nombre_field = ft.TextField(
            label="Nombres *",
            value=profesor.get("nombre", ""),
            text_size=14,
            input_filter=ft.InputFilter(
                allow=True, regex_string=r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'\-]*$"
            ),
        )
        apellido_field = ft.TextField(
            label="Apellidos *",
            value=profesor.get("apellido", ""),
            text_size=14,
            input_filter=ft.InputFilter(
                allow=True, regex_string=r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'\-]*$"
            ),
        )
        especialidad_field = ft.TextField(
            label="Especialidad *",
            value=profesor.get("especialidad", ""),
            text_size=14,
        )
        telefono_field = ft.TextField(
            label="Teléfono",
            value=profesor.get("telefono", "") or "",
            text_size=14,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9\-\+\s]*$"),
        )
        correo_field = ft.TextField(
            label="Correo Laboral",
            value=profesor.get("correo_electronico", "") or "",
            text_size=14,
        )

        estado_actual = str(profesor.get("estado", "ACTIVO")).upper()
        estado_dropdown = ft.Dropdown(
            label="Estado",
            value=estado_actual
            if estado_actual in ["ACTIVO", "LICENCIA", "INACTIVO"]
            else "ACTIVO",
            options=[
                ft.dropdown.Option("ACTIVO"),
                ft.dropdown.Option("LICENCIA"),
                ft.dropdown.Option("INACTIVO"),
            ],
        )

        error_modal = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar_edicion(e):
            nom = (nombre_field.value or "").strip()
            ape = (apellido_field.value or "").strip()
            esp = (especialidad_field.value or "").strip()

            if not nom or not ape or not esp:
                error_modal.value = (
                    "Nombres, Apellidos y Especialidad son obligatorios."
                )
                error_modal.visible = True
                error_modal.update()
                return

            payload = {
                "nombre": nom,
                "apellido": ape,
                "especialidad": esp,
                "telefono": (telefono_field.value or "").strip() or None,
                "correo_electronico": (correo_field.value or "").strip() or None,
                "estado": estado_dropdown.value,
            }

            try:
                await api_client.update_profesor(int(legajo), payload)
                page.pop_dialog()
                await recargar()
            except httpx.HTTPStatusError as err:
                det = "Error al actualizar docente."
                try:
                    det = err.response.json().get("detail", det)
                except Exception:
                    pass
                error_modal.value = f"⚠️ {det}"
                error_modal.visible = True
                error_modal.update()
            except Exception as err:
                error_modal.value = f"⚠️ Error: {err}"
                error_modal.visible = True
                error_modal.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                f"Editar Docente #{legajo}", size=18, weight=ft.FontWeight.BOLD
            ),
            content=ft.Column(
                spacing=12,
                width=420,
                tight=True,
                controls=[
                    nombre_field,
                    apellido_field,
                    especialidad_field,
                    correo_field,
                    telefono_field,
                    estado_dropdown,
                    error_modal,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                ft.Button(
                    "Guardar", bgcolor=TEAL, color=BG_WHITE, on_click=guardar_edicion
                ),
            ],
        )
        page.show_dialog(dlg)

    def confirmar_eliminar_profesor(profesor: dict):
        legajo = profesor.get("legajo")
        error_modal = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def dar_de_baja(e):
            try:
                await api_client.delete_profesor(int(legajo))
                page.pop_dialog()
                await recargar()
            except httpx.HTTPStatusError as err:
                det = "No se pudo dar de baja al docente."
                try:
                    det = err.response.json().get("detail", det)
                except Exception:
                    pass
                error_modal.value = f"⚠️ {det}"
                error_modal.visible = True
                error_modal.update()
            except Exception as err:
                error_modal.value = f"⚠️ Error: {err}"
                error_modal.visible = True
                error_modal.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                f"Dar de baja Docente #{legajo}", size=18, weight=ft.FontWeight.BOLD
            ),
            content=ft.Column(
                spacing=10,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        f"¿Desea dar de baja al docente {profesor.get('apellido')}, {profesor.get('nombre')}? "
                        "Su estado pasará a INACTIVO.",
                        size=13,
                        color=TEXT_COLOR,
                    ),
                    error_modal,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                ft.Button(
                    "Confirmar Baja",
                    bgcolor=BADGE_RED_TXT,
                    color=BG_WHITE,
                    on_click=dar_de_baja,
                ),
            ],
        )
        page.show_dialog(dlg)

    def abrir_panel_acciones(profesor: dict):
        dlg = ft.AlertDialog(
            modal=False,
            title=ft.Text(
                f"Opciones: {profesor.get('apellido')}, {profesor.get('nombre')}",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=TEAL_DARK,
            ),
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Text(
                        "Seleccione la acción que desea realizar con este docente:",
                        size=13,
                        color=MUTED,
                    ),
                    ft.Button(
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=8,
                            controls=[
                                ft.Icon(
                                    ft.Icons.EDIT_OUTLINED, size=18, color=BG_WHITE
                                ),
                                ft.Text(
                                    "Editar datos del docente",
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                    color=BG_WHITE,
                                ),
                            ],
                        ),
                        bgcolor=TEAL,
                        width=300,
                        height=CONTROL_HEIGHT,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)
                        ),
                        on_click=lambda e: (
                            page.pop_dialog(),
                            abrir_editar_profesor(profesor),
                        ),
                    ),
                    ft.Button(
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=8,
                            controls=[
                                ft.Icon(
                                    ft.Icons.DELETE_OUTLINE, size=18, color=BG_WHITE
                                ),
                                ft.Text(
                                    "Dar de baja",
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                    color=BG_WHITE,
                                ),
                            ],
                        ),
                        bgcolor=BADGE_RED_TXT,
                        width=300,
                        height=CONTROL_HEIGHT,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)
                        ),
                        on_click=lambda e: (
                            page.pop_dialog(),
                            confirmar_eliminar_profesor(profesor),
                        ),
                    ),
                ],
            ),
            actions=[ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog())],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    # ==================== 3. FILAS Y TABLA ====================
    def profesor_row(item: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            ink=True,  # Efecto visual al hacer clic
            on_click=lambda e, pr=item: abrir_panel_acciones(
                pr
            ),  # Conecta la fila con el panel
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
                            item.get("telefono", "") or "-", size=13, color=TEXT_COLOR
                        ),
                    ),
                    ft.Container(
                        width=95,
                        content=status_badge(item.get("estado", "ACTIVO").capitalize()),
                    ),
                    # La columna de acciones fue eliminada de aquí
                ],
            ),
        )

    def profesores_filtrados() -> list[dict]:
        texto = (estado["texto"] or "").lower()
        resultado = []
        for p in estado["profesores"]:
            est = str(p.get("estado", "ACTIVO")).capitalize()
            if estado["filtro_estado"] != "Todos" and est != estado["filtro_estado"]:
                continue
            if (
                texto
                and texto
                not in f"{p.get('apellido', '')} {p.get('nombre', '')} {p.get('especialidad', '')} {p.get('legajo', '')}".lower()
            ):
                continue
            resultado.append(p)
        return resultado

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
            min_width=940,
        )
        pagination_holder.content = create_pagination_bar(
            texto_info=f"Mostrando {len(visibles)} de {len(estado['profesores'])} docentes registrados",
            pagina_actual=1,
            total_paginas=max(1, (len(visibles) + 9) // 10),
        )
        page.update()

    async def recargar():
        try:
            estado["profesores"] = await api_client.get_profesores(solo_activos=False)
        except Exception as err:
            mostrar_error(f"No se pudo refrescar la lista de docentes: {err}")
        render()

    search_field.on_change = lambda e: (
        estado.update({"texto": search_field.value or ""}),
        render(),
    )
    filtro_estado_dropdown.on_change = lambda e: (
        estado.update({"filtro_estado": filtro_estado_dropdown.value or "Todos"}),
        render(),
    )

    render()

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
