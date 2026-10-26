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


async def get_admin_alumnos_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa del directorio de alumnos con soporte de edición y baja."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    estado: dict = {
        "alumnos": [],
        "cursos": [],
        "texto": "",
        "nivel": "Todos",
        "curso": "Todos",
    }

    try:
        estado["alumnos"] = await api_client.get_alumnos(solo_activos=False)
    except Exception:
        estado["alumnos"] = []

    try:
        estado["cursos"] = await api_client.get_cursos()
    except Exception:
        estado["cursos"] = []

    curso_map = {
        c["id_curso"]: f"{c.get('nombre', '')} {c.get('division', '')}".strip()
        for c in estado["cursos"]
    }

    # ==================== 1. FILTROS Y ACCIONES ====================
    search_field = ft.TextField(
        hint_text="Buscar por apellido, nombre o legajo...",
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

    btn_nuevo_alumno = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                ft.Text(
                    "Nuevo Alumno", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE
                ),
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
                controls=[search_input],
            ),
            btn_nuevo_alumno,
        ],
    )

    aviso_error = ft.Text(
        "", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False
    )

    columnas_alumnos = [
        ("Legajo", 90, False),
        ("DNI", 110, False),
        ("Apellido", 130, False),
        ("Nombre", 140, False),
        ("Curso", 150, False),
        ("Teléfono", 120, False),
        ("Correo Electrónico", 200, False),
        ("Estado", 95, False),
    ]

    header_table = create_table_header(columnas_alumnos)
    table_holder = ft.Container()
    pagination_holder = ft.Container()

    def mostrar_error(mensaje: str):
        aviso_error.value = f"⚠️ {mensaje}"
        aviso_error.visible = True
        page.update()

    # ==================== 2. DIÁLOGOS DE EDICIÓN Y ELIMINACIÓN ====================
    def abrir_editar_alumno(alumno: dict):
        legajo = alumno.get("legajo")
        nombre_field = ft.TextField(
            label="Nombres *",
            value=alumno.get("nombre", ""),
            text_size=14,
            input_filter=ft.InputFilter(
                allow=True, regex_string=r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'\-]*$"
            ),
        )
        apellido_field = ft.TextField(
            label="Apellidos *",
            value=alumno.get("apellido", ""),
            text_size=14,
            input_filter=ft.InputFilter(
                allow=True, regex_string=r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'\-]*$"
            ),
        )
        domicilio_field = ft.TextField(
            label="Domicilio Real",
            value=alumno.get("domicilio", "") or "",
            text_size=14,
        )
        telefono_field = ft.TextField(
            label="Teléfono",
            value=alumno.get("telefono", "") or "",
            text_size=14,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9\-\+\s]*$"),
        )
        correo_field = ft.TextField(
            label="Correo Electrónico",
            value=alumno.get("correo_electronico", "") or "",
            text_size=14,
        )

        id_curso_actual = str(alumno.get("id_curso", ""))
        curso_dropdown = ft.Dropdown(
            label="Curso Asignado",
            value=id_curso_actual
            if id_curso_actual in [str(c["id_curso"]) for c in estado["cursos"]]
            else None,
            options=[
                ft.dropdown.Option(
                    key=str(c["id_curso"]),
                    text=f"{c.get('nombre', '')} {c.get('division', '')}".strip(),
                )
                for c in estado["cursos"]
            ],
        )

        estado_actual = str(alumno.get("estado_alumno", "ACTIVO")).upper()
        estado_dropdown = ft.Dropdown(
            label="Estado",
            value=estado_actual
            if estado_actual in ["ACTIVO", "INACTIVO"]
            else "ACTIVO",
            options=[
                ft.dropdown.Option("ACTIVO"),
                ft.dropdown.Option("INACTIVO"),
            ],
        )

        error_modal = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar_edicion(e):
            nom = (nombre_field.value or "").strip()
            ape = (apellido_field.value or "").strip()
            if not nom or not ape:
                error_modal.value = "Nombre y Apellido son obligatorios."
                error_modal.visible = True
                error_modal.update()
                return

            payload = {
                "nombre": nom,
                "apellido": ape,
                "domicilio": (domicilio_field.value or "").strip() or None,
                "telefono": (telefono_field.value or "").strip() or None,
                "correo_electronico": (correo_field.value or "").strip() or None,
                "estado_alumno": estado_dropdown.value,
            }
            if curso_dropdown.value:
                payload["id_curso"] = int(curso_dropdown.value)

            try:
                await api_client.update_alumno(int(legajo), payload)
                page.pop_dialog()
                await recargar()
            except httpx.HTTPStatusError as err:
                det = "Error al actualizar alumno."
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
                f"Editar Alumno #{legajo}", size=18, weight=ft.FontWeight.BOLD
            ),
            content=ft.Column(
                spacing=12,
                width=420,
                tight=True,
                controls=[
                    nombre_field,
                    apellido_field,
                    domicilio_field,
                    telefono_field,
                    correo_field,
                    curso_dropdown,
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

    def confirmar_eliminar_alumno(alumno: dict):
        legajo = alumno.get("legajo")
        error_modal = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def dar_de_baja(e):
            try:
                await api_client.delete_alumno(int(legajo))
                page.pop_dialog()
                await recargar()
            except httpx.HTTPStatusError as err:
                det = "No se pudo dar de baja al alumno."
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
                f"Dar de baja Alumno #{legajo}", size=18, weight=ft.FontWeight.BOLD
            ),
            content=ft.Column(
                spacing=10,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        f"¿Desea dar de baja a {alumno.get('apellido')}, {alumno.get('nombre')}? "
                        "El registro pasará a estado INACTIVO conservando su historial.",
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

    def abrir_panel_acciones(alumno: dict):
        dlg = ft.AlertDialog(
            modal=False,
            title=ft.Text(
                f"Opciones: {alumno.get('apellido')}, {alumno.get('nombre')}",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=TEAL_DARK,
            ),
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Text(
                        "Seleccione la acción que desea realizar con este registro:",
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
                                    "Editar datos del alumno",
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
                            abrir_editar_alumno(alumno),
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
                            confirmar_eliminar_alumno(alumno),
                        ),
                    ),
                ],
            ),
            actions=[ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog())],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    # ==================== 3. RENDERIZADO DE TABLA ====================
    def alumno_row(item: dict) -> ft.Container:
        legajo = str(item.get("legajo", ""))
        dni = str(item.get("dni", ""))
        apellido = item.get("apellido", "")
        nombre = item.get("nombre", "")
        id_curso = item.get("id_curso")
        curso_nombre = curso_map.get(
            id_curso, f"Curso #{id_curso}" if id_curso else "Sin Asignar"
        )
        telefono = item.get("telefono") or "-"
        correo = item.get("correo_electronico") or "-"
        estado_texto = str(item.get("estado_alumno") or item.get("estado") or "ACTIVO")

        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            ink=True,  # Efecto visual al hacer clic
            on_click=lambda e, al=item: abrir_panel_acciones(
                al
            ),  # Abre el menú al tocar la fila
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=90,
                        content=ft.Text(
                            legajo, size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK
                        ),
                    ),
                    ft.Container(
                        width=110, content=ft.Text(dni, size=13, color=TEXT_COLOR)
                    ),
                    ft.Container(
                        width=130,
                        content=ft.Text(
                            apellido,
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=140, content=ft.Text(nombre, size=14, color=TEXT_COLOR)
                    ),
                    ft.Container(
                        width=150, content=ft.Text(curso_nombre, size=13, color=TEAL)
                    ),
                    ft.Container(
                        width=120, content=ft.Text(telefono, size=13, color=TEXT_COLOR)
                    ),
                    ft.Container(
                        width=200, content=ft.Text(correo, size=13, color=MUTED)
                    ),
                    ft.Container(width=95, content=status_badge(estado_texto)),
                    # Se eliminó la última columna de acciones aquí
                ],
            ),
        )

    def alumnos_filtrados() -> list[dict]:
        texto = (estado["texto"] or "").strip().lower()
        if not texto:
            return estado["alumnos"]
        return [
            a
            for a in estado["alumnos"]
            if texto
            in f"{a.get('apellido', '')} {a.get('nombre', '')} {a.get('legajo', '')} {a.get('dni', '')}".lower()
        ]

    def render():
        visibles = alumnos_filtrados()
        table_holder.content = create_table_container(
            header=header_table,
            rows=[alumno_row(a) for a in visibles]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "No se encontraron alumnos registrados.", size=13, color=MUTED
                    ),
                )
            ],
            min_width=1120,
        )
        pagination_holder.content = create_pagination_bar(
            texto_info=f"Mostrando {len(visibles)} de {len(estado['alumnos'])} alumnos",
            pagina_actual=1,
            total_paginas=max(1, (len(visibles) + 9) // 10),
        )
        page.update()

    async def recargar():
        try:
            estado["alumnos"] = await api_client.get_alumnos(solo_activos=False)
            estado["cursos"] = await api_client.get_cursos()
        except Exception as err:
            mostrar_error(f"No se pudo refrescar la lista: {err}")
        render()

    search_field.on_change = lambda e: (
        estado.update({"texto": search_field.value or ""}),
        render(),
    )

    render()

    return admin_layout(
        page=page,
        titulo="Directorio de Estudiantes",
        active_route="/admin/alumnos",
        content_controls=[
            filters_bar,
            aviso_error,
            table_holder,
            pagination_holder,
        ],
    )
