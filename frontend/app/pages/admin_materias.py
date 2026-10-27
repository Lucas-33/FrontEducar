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


async def get_admin_materias_view(page: ft.Page) -> ft.Row:
    """Vista del catálogo de Materias y Asignaturas conectada a la API."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and api_client.token != token_almacenado:
        api_client.set_token(token_almacenado)

    # ==================== ESTADO DE LA VISTA ====================
    estado: dict = {
        "materias": [],
        "asignaciones": [],
        "niveles": [],
        "cursos": [],
        "profesores": [],
        "texto": "",
        "nivel": "Todos",
    }

    try:
        estado["materias"] = await api_client.get_materias()
    except Exception:
        estado["materias"] = []
    try:
        estado["asignaciones"] = await api_client.get_asignaciones()
    except Exception:
        estado["asignaciones"] = []
    try:
        estado["niveles"] = await api_client.get_niveles()
    except Exception:
        estado["niveles"] = []
    try:
        estado["cursos"] = await api_client.get_cursos()
    except Exception:
        estado["cursos"] = []
    try:
        estado["profesores"] = await api_client.get_profesores(solo_activos=False)
    except Exception:
        estado["profesores"] = []

    nombre_nivel = {n["id_nivel"]: n["nombre"] for n in estado["niveles"]}

    # Niveles reales presentes en las asignaciones (para el filtro)
    niveles_disponibles: list[str] = []
    for a in estado["asignaciones"]:
        nivel = a.get("nivel") or nombre_nivel.get(a.get("id_nivel"))
        if nivel and nivel not in niveles_disponibles:
            niveles_disponibles.append(nivel)

    # ==================== 1. FILTROS Y ACCIÓN ====================
    search_field = ft.TextField(
        hint_text="Buscar materia...",
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
            + [ft.dropdown.Option(nivel) for nivel in niveles_disponibles],
        ),
    )
    filtro_nivel_dropdown: ft.Dropdown = filtro_nivel_container.content

    btn_nueva_materia = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                ft.Text(
                    "Nueva Materia", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE
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

    btn_asignar_materia = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.LINK, size=16, color=TEAL),
                ft.Text(
                    "Asignar Materia", size=14, weight=ft.FontWeight.W_600, color=TEAL
                ),
            ],
        ),
        bgcolor=BG_WHITE,
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            padding=ft.Padding(20, 10, 20, 10),
            side=ft.BorderSide(1, TEAL),
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
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[btn_asignar_materia, btn_nueva_materia],
            ),
        ],
    )

    aviso_error = ft.Text(
        "", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False
    )

    # ==================== 2. TABLA DE MATERIAS ====================
    columnas_materias = [
        ("Código", 110, False),
        ("Asignatura / Materia", 220, False),
        ("Nivel Educativo", 200, False),
        ("Cursos que la Dictan", 280, False),
        ("Docente(s) Titulares", 280, False),
        ("Acciones", None, True),
    ]

    header_table = create_table_header(columnas_materias)
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
                        tooltip="Editar materia",
                        padding=0,
                        on_click=al_editar,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=17,
                        icon_color=BADGE_RED_TXT,
                        tooltip="Eliminar materia",
                        padding=0,
                        on_click=al_eliminar,
                    ),
                ],
            ),
        )

    def niveles_materia(id_materia: int) -> list[str]:
        """Niveles educativos únicos de las asignaciones de una materia."""
        nombres: list[str] = []
        for a in estado["asignaciones"]:
            if a.get("id_materia") != id_materia:
                continue
            nivel = a.get("nivel") or nombre_nivel.get(a.get("id_nivel"))
            if nivel and nivel not in nombres:
                nombres.append(nivel)
        return nombres

    def datos_materia(id_materia: int) -> dict:
        """Agrupa cursos y docentes únicos de las asignaciones de una materia."""
        cursos: list[str] = []
        docentes: list[str] = []
        for a in estado["asignaciones"]:
            if a.get("id_materia") != id_materia:
                continue
            curso = a.get("curso")
            if curso and curso not in cursos:
                cursos.append(curso)
            docente = a.get("profesor")
            if docente and docente not in docentes:
                docentes.append(docente)

        niveles = niveles_materia(id_materia)
        return {
            "niveles": ", ".join(niveles) if niveles else "-",
            "cursos": ", ".join(cursos) if cursos else "-",
            "docentes": ", ".join(docentes) if docentes else "-",
        }

    def materia_row(item: dict) -> ft.Container:
        datos = datos_materia(item["id_materia"])

        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=110,
                        content=ft.Text(
                            f"MAT-{item['id_materia']}",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        width=220,
                        content=ft.Text(
                            item["nombre"],
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=200,
                        content=ft.Text(datos["niveles"], size=14, color=MUTED),
                    ),
                    ft.Container(
                        width=280,
                        content=ft.Text(datos["cursos"], size=13, color=TEXT_COLOR),
                    ),
                    ft.Container(
                        width=280,
                        content=ft.Text(
                            datos["docentes"],
                            size=13,
                            weight=ft.FontWeight.W_500,
                            color=TEXT_COLOR,
                        ),
                    ),
                    fila_acciones(
                        lambda e, m=item: abrir_editar_materia(m),
                        lambda e, m=item: confirmar_eliminar_materia(m),
                    ),
                ],
            ),
        )

    def materias_filtradas() -> list[dict]:
        texto = (estado["texto"] or "").strip().lower()
        resultado = []
        for m in estado["materias"]:
            if estado["nivel"] != "Todos" and estado["nivel"] not in niveles_materia(
                m["id_materia"]
            ):
                continue
            etiqueta = f"{m.get('nombre', '')} mat-{m.get('id_materia', '')}".lower()
            if texto and texto not in etiqueta:
                continue
            resultado.append(m)
        return resultado

    def render():
        visibles = materias_filtradas()
        if not estado["materias"]:
            mensaje_vacio = "No hay materias cargadas."
        else:
            mensaje_vacio = "No hay materias que coincidan con los filtros."

        table_holder.content = create_table_container(
            header=header_table,
            rows=[materia_row(m) for m in visibles]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(mensaje_vacio, size=13, color=MUTED),
                )
            ],
        )
        pagination_holder.content = create_pagination_bar(
            texto_info=f"Mostrando {len(visibles)} de {len(estado['materias'])} materias registradas",
            pagina_actual=1,
            total_paginas=max(1, (len(visibles) + 9) // 10),
        )
        try:
            page.update()
        except Exception:
            pass

    async def recargar():
        try:
            estado["materias"] = await api_client.get_materias()
            estado["asignaciones"] = await api_client.get_asignaciones()
        except Exception as err:
            mostrar_error(f"No se pudo refrescar la lista de materias: {err}")
        render()

    def on_buscar(e):
        estado["texto"] = search_field.value or ""
        render()

    def on_filtrar_nivel(e):
        estado["nivel"] = filtro_nivel_dropdown.value or "Todos"
        render()

    search_field.on_change = on_buscar
    filtro_nivel_dropdown.on_select = on_filtrar_nivel

    # ==================== 3. DIÁLOGO NUEVA MATERIA ====================
    def abrir_nueva_materia(e):
        nombre_field = ft.TextField(
            label="Nombre de la materia *",
            hint_text="Ej: Matemática",
            width=380,
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar(e):
            nombre = (nombre_field.value or "").strip()
            if not nombre:
                error_text.value = "El nombre de la materia es obligatorio."
                error_text.visible = True
                error_text.update()
                return
            try:
                await api_client.create_materia({"nombre": nombre})
            except httpx.HTTPStatusError as err:
                detalle = "Error al crear la materia."
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
            title=ft.Text("Nueva Materia", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                spacing=14, width=380, tight=True, controls=[nombre_field, error_text]
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button(
                    "Crear Materia", bgcolor=TEAL, color=BG_WHITE, on_click=guardar
                ),
            ],
        )
        page.show_dialog(dlg)

    btn_nueva_materia.on_click = abrir_nueva_materia

    # ==================== 4. DIÁLOGO ASIGNAR MATERIA ====================
    def abrir_asignar_materia(e):
        faltantes = []
        if not estado["materias"]:
            faltantes.append("materias")
        if not estado["cursos"]:
            faltantes.append("cursos")
        if not estado["profesores"]:
            faltantes.append("profesores")
        if faltantes:
            mostrar_error(
                f"No se puede asignar: no hay {' ni '.join(faltantes)} cargados."
            )
            return

        materia_field = ft.Dropdown(
            label="Materia *",
            width=380,
            options=[
                ft.dropdown.Option(key=str(m["id_materia"]), text=m["nombre"])
                for m in estado["materias"]
            ],
        )
        curso_field = ft.Dropdown(
            label="Curso *",
            width=380,
            options=[
                ft.dropdown.Option(key=str(c["id_curso"]), text=c["nombre"])
                for c in estado["cursos"]
            ],
        )
        profesor_field = ft.Dropdown(
            label="Profesor *",
            width=380,
            options=[
                ft.dropdown.Option(
                    key=str(p["legajo"]),
                    text=f"{p['apellido']}, {p['nombre']} (#{p['legajo']})",
                )
                for p in estado["profesores"]
            ],
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar(e):
            if not (materia_field.value and curso_field.value and profesor_field.value):
                error_text.value = "Debe seleccionar materia, curso y profesor."
                error_text.visible = True
                error_text.update()
                return
            try:
                await api_client.create_asignacion(
                    {
                        "id_materia": int(materia_field.value),
                        "id_curso": int(curso_field.value),
                        "legajo_profesor": int(profesor_field.value),
                    }
                )
            except httpx.HTTPStatusError as err:
                detalle = "Error al crear la asignación."
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
                "Asignar Materia a Curso", size=18, weight=ft.FontWeight.BOLD
            ),
            content=ft.Column(
                spacing=14,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        "Seleccione la materia, el curso y el docente que la dictará.",
                        size=13,
                        color=MUTED,
                    ),
                    materia_field,
                    curso_field,
                    profesor_field,
                    error_text,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button("Asignar", bgcolor=TEAL, color=BG_WHITE, on_click=guardar),
            ],
        )
        page.show_dialog(dlg)

    btn_asignar_materia.on_click = abrir_asignar_materia

    # ==================== 4b. DIÁLOGOS EDITAR / ELIMINAR MATERIA ====================
    def abrir_editar_materia(materia: dict):
        nombre_field = ft.TextField(
            label="Nombre de la materia *",
            value=materia.get("nombre") or "",
            width=380,
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar_edicion(e):
            nombre = (nombre_field.value or "").strip()
            if not nombre:
                error_text.value = "El nombre de la materia es obligatorio."
                error_text.visible = True
                error_text.update()
                return
            try:
                await api_client.update_materia(
                    materia["id_materia"], {"nombre": nombre}
                )
            except httpx.HTTPStatusError as err:
                detalle = "Error al actualizar la materia."
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
                f"Editar Materia MAT-{materia['id_materia']}",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            content=ft.Column(
                spacing=14, width=380, tight=True, controls=[nombre_field, error_text]
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

    def confirmar_eliminar_materia(materia: dict):
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def eliminar(e):
            try:
                await api_client.delete_materia(materia["id_materia"])
            except httpx.HTTPStatusError as err:
                detalle = "No se pudo eliminar la materia."
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
            title=ft.Text("Eliminar Materia", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                spacing=14,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        f"¿Confirma eliminar la materia «{materia.get('nombre')}»? "
                        "Solo es posible si no tiene asignaciones ni calificaciones asociadas.",
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

    # ==================== 5. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Plan de Estudios — Materias y Asignaturas",
        active_route="/admin/materias",
        content_controls=[
            filters_bar,
            aviso_error,
            table_holder,
            pagination_holder,
        ],
    )
