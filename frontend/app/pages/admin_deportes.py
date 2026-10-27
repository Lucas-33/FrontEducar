import flet as ft
import httpx

from frontend.app.api_client import api_client
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.table_view import (
    create_pagination_bar,
    create_table_container,
    create_table_header,
)


def _fecha_corta(iso: str | None) -> str:
    """Convierte un ISO timestamp del backend en dd/mm/aaaa."""
    if not iso or len(iso) < 10:
        return "-"
    return f"{iso[8:10]}/{iso[5:7]}/{iso[0:4]}"


async def get_admin_deportes_view(page: ft.Page) -> ft.Row:
    """Vista del programa deportivo (disciplinas, grupos e inscripciones) conectada a la API."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and api_client.token != token_almacenado:
        api_client.set_token(token_almacenado)

    # ==================== ESTADO DE LA VISTA ====================
    estado: dict = {
        "deportes": [],
        "grupos": [],
        "inscripciones": [],
        "profesores": [],
        "niveles": [],
        "horarios": [],
        "texto": "",
        "nivel": "Todos",
        "deporte": "Todos",
    }

    try:
        estado["deportes"] = await api_client.get_deportes()
    except Exception:
        estado["deportes"] = []
    try:
        estado["grupos"] = await api_client.get_grupos_deporte()
    except Exception:
        estado["grupos"] = []
    try:
        estado["inscripciones"] = await api_client.get_inscripciones_deporte()
    except Exception:
        estado["inscripciones"] = []
    try:
        estado["profesores"] = await api_client.get_profesores(solo_activos=False)
    except Exception:
        estado["profesores"] = []
    try:
        estado["niveles"] = await api_client.get_niveles()
    except Exception:
        estado["niveles"] = []
    try:
        estado["horarios"] = await api_client.get_horarios()
    except Exception:
        estado["horarios"] = []

    profesores_por_legajo = {p.get("legajo"): p for p in estado["profesores"]}

    def nombre_profesor(legajo) -> str:
        if legajo is None:
            return "Sin asignar"
        profesor = profesores_por_legajo.get(legajo)
        if not profesor:
            return f"Legajo {legajo}"
        return f"{profesor.get('apellido', '')}, {profesor.get('nombre', '')}"

    def profesor_de_deporte(id_deporte: int | None) -> str:
        for d in estado["deportes"]:
            if d.get("id_deporte") == id_deporte:
                return nombre_profesor(d.get("legajo_profesor_responsable"))
        return "Sin asignar"

    def inscriptos_de_grupo(id_grupo: int) -> list[dict]:
        return [i for i in estado["inscripciones"] if i.get("id_grupo") == id_grupo]

    # Opciones de filtros (si las entidades base fallan, se derivan de los grupos reales)
    nombres_nivel = [n["nombre"] for n in estado["niveles"] if n.get("nombre")]
    if not nombres_nivel:
        nombres_nivel = sorted(
            {g.get("nivel", "") for g in estado["grupos"] if g.get("nivel")}
        )
    nombres_deporte = [d["nombre"] for d in estado["deportes"] if d.get("nombre")]
    if not nombres_deporte:
        nombres_deporte = sorted(
            {g.get("deporte", "") for g in estado["grupos"] if g.get("deporte")}
        )

    # ==================== 1. TARJETAS DE MÉTRICAS (KPIs) ====================
    def kpi_card(
        titulo: str,
        valor: str,
        subtitulo: str,
        icono: ft.IconData,
        icon_bg: str,
        valor_color: str = TEAL_DARK,
    ) -> ft.Container:
        return ft.Container(
            expand=True,
            height=158,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=20,
            content=ft.Column(
                spacing=16,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                titulo, size=12, weight=ft.FontWeight.W_600, color=MUTED
                            ),
                            ft.Container(
                                width=36,
                                height=36,
                                bgcolor=icon_bg,
                                border_radius=10,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(icono, size=18, color=TEAL_DARK),
                            ),
                        ],
                    ),
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(
                                valor,
                                size=30,
                                weight=ft.FontWeight.W_800,
                                color=valor_color,
                            ),
                            ft.Text(subtitulo, size=11, color=MUTED),
                        ],
                    ),
                ],
            ),
        )

    def render_kpis() -> ft.Row:
        con_docente = len(
            [
                d
                for d in estado["deportes"]
                if d.get("legajo_profesor_responsable") is not None
            ]
        )
        sin_docente = len(estado["deportes"]) - con_docente
        niveles_con_grupos = {
            g.get("nivel", "") for g in estado["grupos"] if g.get("nivel")
        }
        total_inscripciones = len(estado["inscripciones"])
        total_grupos = len(estado["grupos"])
        promedio = (total_inscripciones / total_grupos) if total_grupos else 0

        return ft.Row(
            spacing=16,
            controls=[
                kpi_card(
                    "DISCIPLINAS DEPORTIVAS",
                    str(len(estado["deportes"])),
                    f"{con_docente} con docente asignado",
                    ft.Icons.SPORTS_OUTLINED,
                    TEAL_LIGHT,
                ),
                kpi_card(
                    "GRUPOS DEPORTIVOS",
                    str(total_grupos),
                    f"En {len(niveles_con_grupos)} niveles educativos"
                    if niveles_con_grupos
                    else "Sin grupos registrados",
                    ft.Icons.GROUP_WORK_OUTLINED,
                    TEAL_LIGHT,
                ),
                kpi_card(
                    "ALUMNOS INSCRIPTOS",
                    str(total_inscripciones),
                    f"Promedio {promedio:.1f} por grupo"
                    if total_grupos
                    else "Sin inscripciones registradas",
                    ft.Icons.HOW_TO_REG_OUTLINED,
                    TEAL_LIGHT,
                ),
                kpi_card(
                    "DOCENTES A CARGO",
                    str(con_docente),
                    f"{sin_docente} disciplinas sin responsable"
                    if sin_docente
                    else "Todas las disciplinas cubiertas",
                    ft.Icons.SUPERVISOR_ACCOUNT_OUTLINED,
                    "#FFF3E7" if sin_docente else TEAL_LIGHT,
                    ORANGE if sin_docente else TEAL_DARK,
                ),
            ],
        )

    # ==================== 2. FILTROS Y ACCIONES ====================
    search_field = ft.TextField(
        hint_text="Buscar disciplina, nivel, horario o docente...",
        hint_style=ft.TextStyle(size=14, color=MUTED),
        text_size=14,
        color=TEXT_COLOR,
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding(0, 0, 0, 10),
        expand=True,
    )
    search_input = ft.Container(
        width=320,
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

    filtro_nivel_container = filtro_dropdown(
        "Nivel: Todos", 150, ["Todos"] + nombres_nivel
    )
    filtro_deporte_container = filtro_dropdown(
        "Disciplina: Todas", 170, ["Todos"] + nombres_deporte
    )
    filtro_nivel_dropdown: ft.Dropdown = filtro_nivel_container.content
    filtro_deporte_dropdown: ft.Dropdown = filtro_deporte_container.content

    btn_nuevo_deporte = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                ft.Text(
                    "Nuevo Deporte", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE
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

    btn_nuevo_grupo = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.GROUP_ADD_OUTLINED, size=16, color=TEAL),
                ft.Text("Nuevo Grupo", size=14, weight=ft.FontWeight.W_600, color=TEAL),
            ],
        ),
        bgcolor=BG_WHITE,
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            padding=ft.Padding(24, 12, 24, 12),
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
                controls=[
                    search_input,
                    filtro_nivel_container,
                    filtro_deporte_container,
                ],
            ),
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[btn_nuevo_grupo, btn_nuevo_deporte],
            ),
        ],
    )

    aviso_error = ft.Text(
        "", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False
    )

    # ==================== 3. TABLA DE GRUPOS DEPORTIVOS ====================
    columnas_grupos = [
        ("Disciplina Deportiva", 190, False),
        ("Profesor Responsable", 190, False),
        ("Nivel Destinado", 150, False),
        ("Días y Horarios", 260, False),
        ("Inscriptos", 110, False),
        ("Acciones", None, True),
    ]

    header_table = create_table_header(columnas_grupos)
    kpis_holder = ft.Container()
    table_holder = ft.Container()
    pagination_holder = ft.Container()

    def mostrar_error(mensaje: str):
        aviso_error.value = f"⚠️ {mensaje}"
        aviso_error.visible = True
        try:
            page.update()
        except Exception:
            pass

    def grupo_row(item: dict) -> ft.Container:
        profesor = profesor_de_deporte(item.get("id_deporte"))
        inscriptos = len(inscriptos_de_grupo(item["id_grupo"]))

        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=190,
                        content=ft.Text(
                            item.get("deporte", "-"),
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        width=190,
                        content=ft.Text(
                            profesor,
                            size=13,
                            weight=ft.FontWeight.W_500,
                            color=MUTED if profesor == "Sin asignar" else TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=150,
                        content=ft.Text(item.get("nivel", "-"), size=13, color=MUTED),
                    ),
                    ft.Container(
                        width=260,
                        content=ft.Text(
                            item.get("horario", "-"), size=13, color=TEXT_COLOR
                        ),
                    ),
                    ft.Container(
                        width=110,
                        content=ft.Text(
                            str(inscriptos),
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=12,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.PEOPLE_OUTLINE,
                                    icon_size=16,
                                    icon_color=TEAL,
                                    tooltip="Ver Alumnos Inscriptos",
                                    padding=0,
                                    on_click=lambda e, g=item: abrir_inscriptos(g),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    icon_size=16,
                                    icon_color=TEAL,
                                    tooltip="Editar grupo",
                                    padding=0,
                                    on_click=lambda e, g=item: abrir_editar_grupo(g),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_size=16,
                                    icon_color=BADGE_RED_TXT,
                                    tooltip="Eliminar grupo",
                                    padding=0,
                                    on_click=lambda e, g=item: confirmar_eliminar_grupo(
                                        g
                                    ),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    def grupos_filtrados() -> list[dict]:
        texto = (estado["texto"] or "").lower()
        resultado = []
        for g in estado["grupos"]:
            if estado["nivel"] != "Todos" and g.get("nivel") != estado["nivel"]:
                continue
            if estado["deporte"] != "Todos" and g.get("deporte") != estado["deporte"]:
                continue
            if texto:
                buscable = " ".join(
                    [
                        str(g.get("deporte", "")),
                        str(g.get("nivel", "")),
                        str(g.get("horario", "")),
                        profesor_de_deporte(g.get("id_deporte")),
                        f"grupo {g.get('id_grupo', '')}",
                    ]
                ).lower()
                if texto not in buscable:
                    continue
            resultado.append(g)
        return resultado

    def render():
        visibles = grupos_filtrados()
        kpis_holder.content = render_kpis()
        table_holder.content = create_table_container(
            header=header_table,
            rows=[grupo_row(g) for g in visibles]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "No hay grupos deportivos cargados."
                        if not estado["grupos"]
                        else "No hay grupos deportivos que coincidan con los filtros.",
                        size=13,
                        color=MUTED,
                    ),
                )
            ],
        )
        pagination_holder.content = create_pagination_bar(
            texto_info=(
                f"Mostrando {len(visibles)} de {len(estado['grupos'])} grupos deportivos · "
                f"{len(estado['inscripciones'])} alumnos inscriptos"
            ),
            pagina_actual=1,
            total_paginas=max(1, (len(visibles) + 9) // 10),
        )
        try:
            page.update()
        except Exception:
            pass

    async def recargar():
        try:
            estado["deportes"] = await api_client.get_deportes()
            estado["grupos"] = await api_client.get_grupos_deporte()
            estado["inscripciones"] = await api_client.get_inscripciones_deporte()
        except Exception as err:
            mostrar_error(f"No se pudo refrescar la información deportiva: {err}")
        render()

    def on_buscar(e):
        estado["texto"] = search_field.value or ""
        render()

    def on_filtrar_nivel(e):
        estado["nivel"] = filtro_nivel_dropdown.value or "Todos"
        render()

    def on_filtrar_deporte(e):
        estado["deporte"] = filtro_deporte_dropdown.value or "Todos"
        render()

    search_field.on_change = on_buscar
    filtro_nivel_dropdown.on_select = on_filtrar_nivel
    filtro_deporte_dropdown.on_select = on_filtrar_deporte

    # ==================== 4. DIÁLOGO DE ALUMNOS INSCRIPTOS ====================
    def abrir_inscriptos(grupo: dict):
        inscritos = sorted(
            inscriptos_de_grupo(grupo["id_grupo"]),
            key=lambda i: str(i.get("alumno", "")),
        )

        filas = [
            ft.Container(
                padding=ft.Padding(0, 6, 0, 6),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            i.get("alumno", f"Legajo {i.get('legajo_alumno', '-')}"),
                            size=13,
                            color=TEXT_COLOR,
                        ),
                        ft.Text(
                            _fecha_corta(i.get("fecha_inscripcion")),
                            size=12,
                            color=MUTED,
                        ),
                    ],
                ),
            )
            for i in inscritos
        ] or [
            ft.Text("No hay alumnos inscriptos en este grupo.", size=13, color=MUTED),
        ]

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                f"Alumnos Inscriptos — {grupo.get('deporte', '')}",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            content=ft.Column(
                spacing=12,
                width=420,
                tight=True,
                controls=[
                    ft.Text(
                        f"{grupo.get('nivel', '-')} · {grupo.get('horario', '-')}",
                        size=12,
                        color=MUTED,
                    ),
                    ft.ListView(spacing=0, height=240, controls=filas),
                ],
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: page.pop_dialog()),
            ],
        )
        page.show_dialog(dlg)

    # ==================== 5. DIÁLOGO NUEVO DEPORTE ====================
    def abrir_nuevo_deporte(e):
        nombre_field = ft.TextField(
            label="Nombre de la disciplina *", hint_text="Ej: Natación", width=380
        )
        profesor_field = ft.Dropdown(
            label="Profesor responsable",
            width=380,
            options=[ft.dropdown.Option(key="", text="Sin responsable")]
            + [
                ft.dropdown.Option(
                    key=str(p["legajo"]),
                    text=f"{p.get('apellido', '')}, {p.get('nombre', '')} (#{p['legajo']})",
                )
                for p in estado["profesores"]
            ],
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar(e):
            nombre = (nombre_field.value or "").strip()
            if not nombre:
                error_text.value = "El nombre de la disciplina es obligatorio."
                error_text.visible = True
                error_text.update()
                return

            payload = {
                "nombre": nombre,
                "legajo_profesor_responsable": int(profesor_field.value)
                if profesor_field.value
                else None,
            }
            try:
                await api_client.create_deporte(payload)
            except httpx.HTTPStatusError as err:
                detalle = "Error al crear la disciplina deportiva."
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
                "Nueva Disciplina Deportiva", size=18, weight=ft.FontWeight.BOLD
            ),
            content=ft.Column(
                spacing=14,
                width=380,
                tight=True,
                controls=[nombre_field, profesor_field, error_text],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button(
                    "Crear Deporte", bgcolor=TEAL, color=BG_WHITE, on_click=guardar
                ),
            ],
        )
        page.show_dialog(dlg)

    btn_nuevo_deporte.on_click = abrir_nuevo_deporte

    # ==================== 6. DIÁLOGO NUEVO GRUPO ====================
    def abrir_nuevo_grupo(e):
        if not estado["deportes"] or not estado["niveles"] or not estado["horarios"]:
            mostrar_error(
                "Para crear un grupo se necesitan disciplinas, niveles y horarios cargados."
            )
            return

        deporte_field = ft.Dropdown(
            label="Disciplina deportiva *",
            width=380,
            options=[
                ft.dropdown.Option(key=str(d["id_deporte"]), text=d["nombre"])
                for d in estado["deportes"]
            ],
        )
        nivel_field = ft.Dropdown(
            label="Nivel educativo *",
            width=380,
            options=[
                ft.dropdown.Option(key=str(n["id_nivel"]), text=n["nombre"])
                for n in estado["niveles"]
            ],
        )
        horario_field = ft.Dropdown(
            label="Horario *",
            width=380,
            options=[
                ft.dropdown.Option(key=str(h["id_horario"]), text=h["descripcion"])
                for h in estado["horarios"]
            ],
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar(e):
            if (
                not deporte_field.value
                or not nivel_field.value
                or not horario_field.value
            ):
                error_text.value = "Disciplina, nivel y horario son obligatorios."
                error_text.visible = True
                error_text.update()
                return

            payload = {
                "id_deporte": int(deporte_field.value),
                "id_nivel": int(nivel_field.value),
                "id_horario": int(horario_field.value),
            }
            try:
                await api_client.create_grupo_deporte(payload)
            except httpx.HTTPStatusError as err:
                detalle = "Error al crear el grupo deportivo."
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
            title=ft.Text("Nuevo Grupo Deportivo", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                spacing=14,
                width=380,
                tight=True,
                controls=[deporte_field, nivel_field, horario_field, error_text],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button(
                    "Crear Grupo", bgcolor=TEAL, color=BG_WHITE, on_click=guardar
                ),
            ],
        )
        page.show_dialog(dlg)

    btn_nuevo_grupo.on_click = abrir_nuevo_grupo

    # ==================== 6b. DIÁLOGOS EDITAR / ELIMINAR GRUPO ====================
    def abrir_editar_grupo(grupo: dict):
        deporte_field = ft.Dropdown(
            label="Disciplina deportiva *",
            width=380,
            options=[
                ft.dropdown.Option(key=str(d["id_deporte"]), text=d["nombre"])
                for d in estado["deportes"]
            ],
            value=str(grupo.get("id_deporte")),
        )
        nivel_field = ft.Dropdown(
            label="Nivel educativo *",
            width=380,
            options=[
                ft.dropdown.Option(key=str(n["id_nivel"]), text=n["nombre"])
                for n in estado["niveles"]
            ],
            value=str(grupo.get("id_nivel")),
        )
        horario_field = ft.Dropdown(
            label="Horario *",
            width=380,
            options=[
                ft.dropdown.Option(key=str(h["id_horario"]), text=h["descripcion"])
                for h in estado["horarios"]
            ],
            value=str(grupo.get("id_horario")),
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar_edicion(e):
            if (
                not deporte_field.value
                or not nivel_field.value
                or not horario_field.value
            ):
                error_text.value = "Disciplina, nivel y horario son obligatorios."
                error_text.visible = True
                error_text.update()
                return
            try:
                await api_client.update_grupo_deporte(
                    grupo["id_grupo"],
                    {
                        "id_deporte": int(deporte_field.value),
                        "id_nivel": int(nivel_field.value),
                        "id_horario": int(horario_field.value),
                    },
                )
            except httpx.HTTPStatusError as err:
                detalle = "Error al actualizar el grupo deportivo."
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
                f"Editar Grupo Deportivo #{grupo['id_grupo']}",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            content=ft.Column(
                spacing=14,
                width=380,
                tight=True,
                controls=[deporte_field, nivel_field, horario_field, error_text],
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

    def confirmar_eliminar_grupo(grupo: dict):
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def eliminar(e):
            try:
                await api_client.delete_grupo_deporte(grupo["id_grupo"])
            except httpx.HTTPStatusError as err:
                detalle = "No se pudo eliminar el grupo deportivo."
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
                "Eliminar Grupo Deportivo", size=18, weight=ft.FontWeight.BOLD
            ),
            content=ft.Column(
                spacing=14,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        f"¿Confirma eliminar el grupo de «{grupo.get('deporte', '')}» "
                        f"({grupo.get('nivel', '-')} · {grupo.get('horario', '-')})? "
                        "Solo es posible si no tiene alumnos inscriptos.",
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

    aviso_info = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
        padding=14,
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE, size=18, color=TEAL),
                ft.Text(
                    "Cada grupo deportivo combina una disciplina, un nivel educativo y un horario. La cantidad de inscriptos se calcula con las inscripciones registradas.",
                    size=13,
                    color=TEAL_DARK,
                    weight=ft.FontWeight.W_500,
                ),
            ],
        ),
    )

    render()

    # ==================== 7. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Programa Deportivo, Grupos e Inscripciones",
        active_route="/admin/deportes",
        content_controls=[
            aviso_info,
            aviso_error,
            kpis_holder,
            filters_bar,
            table_holder,
            pagination_holder,
        ],
    )
