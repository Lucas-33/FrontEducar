import httpx
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
from frontend.app.components.table_view import (
    create_pagination_bar,
    create_table_container,
    create_table_header,
)


async def get_admin_cursos_view(page: ft.Page) -> ft.Row:
    """Vista del directorio de Cursos y Divisiones conectada a la API."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    estado: dict = {"cursos": [], "niveles": [], "alumnos": [], "texto": "", "nivel": "Todos"}

    try:
        estado["cursos"] = await api_client.get_cursos()
    except Exception:
        estado["cursos"] = []
    try:
        estado["niveles"] = await api_client.get_niveles()
    except Exception:
        estado["niveles"] = []
    try:
        estado["alumnos"] = await api_client.get_alumnos(solo_activos=False)
    except Exception:
        estado["alumnos"] = []

    nombre_nivel = {n["id_nivel"]: n["nombre"] for n in estado["niveles"]}

    # ==================== 1. BARRA DE FILTROS Y ACCIÓN ====================
    search_field = ft.TextField(
        hint_text="Buscar curso o división...",
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

    filtro_nivel_container = ft.Container(
        width=180,
        height=CONTROL_HEIGHT,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=BORDER_RADIUS,
        content=ft.Dropdown(
            hint_text="Nivel: Todos",
            hint_style=ft.TextStyle(size=14, color=TEXT_COLOR),
            text_size=14,
            border=ft.InputBorder.NONE,
            content_padding=ft.Padding(12, 0, 8, 12),
            options=[ft.dropdown.Option("Todos")]
            + [ft.dropdown.Option(n["nombre"]) for n in estado["niveles"]],
        ),
    )
    filtro_nivel_dropdown: ft.Dropdown = filtro_nivel_container.content

    btn_nuevo_curso = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                ft.Text("Nuevo Curso", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
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
                controls=[search_input, filtro_nivel_container],
            ),
            btn_nuevo_curso,
        ],
    )

    aviso_error = ft.Text("", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False)

    # ==================== 2. TABLA DE CURSOS ====================
    columnas_cursos = [
        ("Código", 100, False),
        ("Curso / Año", 220, False),
        ("Nivel Educativo", 200, False),
        ("Matrícula Activa", 170, False),
        ("Total Alumnos", 160, False),
        ("Acciones", None, True),
    ]

    header_table = create_table_header(columnas_cursos)
    table_holder = ft.Container()
    pagination_holder = ft.Container()

    def mostrar_error(mensaje: str):
        aviso_error.value = f"⚠️ {mensaje}"
        aviso_error.visible = True
        try:
            page.update()
        except Exception:
            pass

    def fila_acciones(al_editar, al_eliminar) -> ft.Container:
        return ft.Container(
            expand=True,
            alignment=ft.Alignment(1, 0),
            content=ft.Row(
                spacing=6,
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        icon_size=17,
                        icon_color=TEAL,
                        tooltip="Editar curso",
                        padding=0,
                        on_click=al_editar,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=17,
                        icon_color=BADGE_RED_TXT,
                        tooltip="Eliminar curso",
                        padding=0,
                        on_click=al_eliminar,
                    ),
                ],
            ),
        )

    def alumnos_del_curso(id_curso: int) -> list[dict]:
        return [a for a in estado["alumnos"] if a.get("id_curso") == id_curso]

    def curso_row(item: dict) -> ft.Container:
        alumnos_curso = alumnos_del_curso(item["id_curso"])
        activos = len([a for a in alumnos_curso if a.get("estado_alumno") == "ACTIVO"])

        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=100, content=ft.Text(str(item["id_curso"]), size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=220, content=ft.Text(item["nombre"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=200, content=ft.Text(nombre_nivel.get(item["id_nivel"], f"Nivel {item['id_nivel']}"), size=14, color=MUTED)),
                    ft.Container(width=170, content=ft.Text(str(activos), size=14, weight=ft.FontWeight.W_500, color=TEXT_COLOR)),
                    ft.Container(width=160, content=ft.Text(str(len(alumnos_curso)), size=14, color=MUTED)),
                    fila_acciones(
                        lambda e, c=item: abrir_editar_curso(c),
                        lambda e, c=item: confirmar_eliminar_curso(c),
                    ),
                ],
            ),
        )

    def cursos_filtrados() -> list[dict]:
        texto = (estado["texto"] or "").lower()
        resultado = []
        for c in estado["cursos"]:
            nivel = nombre_nivel.get(c["id_nivel"], "")
            if estado["nivel"] != "Todos" and nivel != estado["nivel"]:
                continue
            if texto and texto not in f"{c.get('nombre', '')} {c.get('id_curso', '')}".lower():
                continue
            resultado.append(c)
        return resultado

    def render():
        visibles = cursos_filtrados()
        table_holder.content = create_table_container(
            header=header_table,
            rows=[curso_row(c) for c in visibles]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text("No hay cursos que coincidan con los filtros.", size=13, color=MUTED),
                )
            ],
        )
        pagination_holder.content = create_pagination_bar(
            texto_info=f"Mostrando {len(visibles)} de {len(estado['cursos'])} cursos activos",
            pagina_actual=1,
            total_paginas=max(1, (len(visibles) + 9) // 10),
        )
        try:
            page.update()
        except Exception:
            pass

    async def recargar():
        try:
            estado["cursos"] = await api_client.get_cursos()
            estado["alumnos"] = await api_client.get_alumnos(solo_activos=False)
        except Exception as err:
            mostrar_error(f"No se pudo refrescar la lista de cursos: {err}")
        render()

    def on_buscar(e):
        estado["texto"] = search_field.value or ""
        render()

    def on_filtrar_nivel(e):
        estado["nivel"] = filtro_nivel_dropdown.value or "Todos"
        render()

    search_field.on_change = on_buscar
    filtro_nivel_dropdown.on_change = on_filtrar_nivel

    # ==================== 3. DIÁLOGO NUEVO CURSO ====================
    def abrir_nuevo_curso(e):
        if not estado["niveles"]:
            mostrar_error("No hay niveles educativos cargados. Cree un nivel primero.")
            return

        nombre_field = ft.TextField(label="Nombre del curso *", hint_text="Ej: 2° Año B", width=380)
        nivel_field = ft.Dropdown(
            label="Nivel educativo *",
            width=380,
            options=[ft.dropdown.Option(key=str(n["id_nivel"]), text=n["nombre"]) for n in estado["niveles"]],
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar(e):
            nombre = (nombre_field.value or "").strip()
            if not nombre or not nivel_field.value:
                error_text.value = "Nombre y nivel son obligatorios."
                error_text.visible = True
                error_text.update()
                return
            try:
                await api_client.create_curso({"nombre": nombre, "id_nivel": int(nivel_field.value)})
            except httpx.HTTPStatusError as err:
                detalle = "Error al crear el curso."
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
            title=ft.Text("Nuevo Curso", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(spacing=14, width=380, tight=True, controls=[nombre_field, nivel_field, error_text]),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button("Crear Curso", bgcolor=TEAL, color=BG_WHITE, on_click=guardar),
            ],
        )
        page.show_dialog(dlg)

    btn_nuevo_curso.on_click = abrir_nuevo_curso

    # ==================== 3b. DIÁLOGOS EDITAR / ELIMINAR CURSO ====================
    def abrir_editar_curso(curso: dict):
        nombre_field = ft.TextField(
            label="Nombre del curso *",
            value=curso.get("nombre") or "",
            width=380,
        )
        nivel_field = ft.Dropdown(
            label="Nivel educativo *",
            width=380,
            options=[ft.dropdown.Option(key=str(n["id_nivel"]), text=n["nombre"]) for n in estado["niveles"]],
            value=str(curso.get("id_nivel")),
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar_edicion(e):
            nombre = (nombre_field.value or "").strip()
            if not nombre or not nivel_field.value:
                error_text.value = "Nombre y nivel son obligatorios."
                error_text.visible = True
                error_text.update()
                return
            try:
                await api_client.update_curso(
                    curso["id_curso"],
                    {"nombre": nombre, "id_nivel": int(nivel_field.value)},
                )
            except httpx.HTTPStatusError as err:
                detalle = "Error al actualizar el curso."
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
            title=ft.Text(f"Editar Curso #{curso['id_curso']}", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(spacing=14, width=380, tight=True, controls=[nombre_field, nivel_field, error_text]),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button("Guardar Cambios", bgcolor=TEAL, color=BG_WHITE, on_click=guardar_edicion),
            ],
        )
        page.show_dialog(dlg)

    def confirmar_eliminar_curso(curso: dict):
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def eliminar(e):
            try:
                await api_client.delete_curso(curso["id_curso"])
            except httpx.HTTPStatusError as err:
                detalle = "No se pudo eliminar el curso."
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
            title=ft.Text("Eliminar Curso", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                spacing=14,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        f"¿Confirma eliminar el curso «{curso.get('nombre')}»? "
                        "Solo es posible si no tiene alumnos ni asignaciones asociadas.",
                        size=13,
                        color=TEXT_COLOR,
                    ),
                    error_text,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button("Eliminar", bgcolor=BADGE_RED_TXT, color=BG_WHITE, on_click=eliminar),
            ],
        )
        page.show_dialog(dlg)

    render()

    # ==================== 4. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Gestión Académica — Cursos y Divisiones",
        active_route="/admin/cursos",
        content_controls=[
            filters_bar,
            aviso_error,
            table_holder,
            pagination_holder,
        ],
    )
