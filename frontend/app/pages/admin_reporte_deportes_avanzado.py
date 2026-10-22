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


def formatear_fecha(valor) -> str:
    """Convierte una fecha ISO (YYYY-MM-DD) al formato local DD/MM/YYYY."""
    texto = str(valor or "").strip()
    if not texto:
        return "—"
    partes = texto.split("-")
    if len(partes) == 3 and all(partes):
        return f"{partes[2]}/{partes[1]}/{partes[0]}"
    return texto


async def get_admin_reporte_deportes_avanzado_view(page: ft.Page) -> ft.Row:
    """Reporte integral de deportes: grupos, niveles, horarios, inscriptos y responsable a cargo."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    estado: dict = {
        "deportes": [],
        "grupos": [],
        "inscripciones": [],
        "profesores": [],
        "alumnos": [],
        "cursos": [],
        "texto": "",
        "deporte": "Todos",
        "nivel": "Todos",
        "horario": "Todos",
    }
    errores: list[str] = []

    async def consultar(etiqueta: str, metodo, *args, **kwargs) -> list:
        """Ejecuta una consulta a la API y acumula los fallos para avisar en pantalla."""
        try:
            return await metodo(*args, **kwargs)
        except httpx.HTTPStatusError as err:
            detalle = "error del servidor"
            try:
                detalle = err.response.json().get("detail", detalle)
            except Exception:
                pass
            errores.append(f"{etiqueta}: {detalle}")
            return []
        except httpx.RequestError:
            errores.append(f"{etiqueta}: sin conexión con el backend")
            return []
        except Exception:
            errores.append(f"{etiqueta}: error inesperado")
            return []

    estado["deportes"] = await consultar("deportes", api_client.get_deportes)
    estado["grupos"] = await consultar(
        "grupos deportivos", api_client.get_grupos_deporte
    )
    estado["inscripciones"] = await consultar(
        "inscripciones deportivas", api_client.get_inscripciones_deporte
    )
    estado["profesores"] = await consultar(
        "docentes", api_client.get_profesores, solo_activos=False
    )
    estado["alumnos"] = await consultar(
        "alumnos", api_client.get_alumnos, solo_activos=False
    )
    estado["cursos"] = await consultar("cursos", api_client.get_cursos)

    grupo_por_id = {g["id_grupo"]: g for g in estado["grupos"]}
    nombre_curso = {c["id_curso"]: c["nombre"] for c in estado["cursos"]}
    curso_por_legajo = {a["legajo"]: a.get("id_curso") for a in estado["alumnos"]}
    nombre_profesor = {
        p["legajo"]: f"{p.get('apellido', '')}, {p.get('nombre', '')}".strip(", ")
        for p in estado["profesores"]
    }

    inscriptos_por_grupo: dict = {}
    for inscripcion in estado["inscripciones"]:
        id_grupo = inscripcion.get("id_grupo")
        inscriptos_por_grupo[id_grupo] = inscriptos_por_grupo.get(id_grupo, 0) + 1

    def responsable_del_deporte(deporte: dict) -> str:
        legajo = deporte.get("legajo_profesor_responsable")
        if not legajo:
            return "Sin responsable asignado"
        return nombre_profesor.get(legajo, f"Legajo #{legajo}")

    def curso_del_alumno(legajo) -> str:
        return nombre_curso.get(curso_por_legajo.get(legajo), "Sin curso asignado")

    aviso_error = ft.Text(
        "", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False
    )
    if errores:
        aviso_error.value = "⚠️ No se pudieron cargar algunos datos: " + " · ".join(
            errores
        )
        aviso_error.visible = True

    # ==================== 1. ENCABEZADO Y ACCIONES ====================
    header_actions = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=36,
                        height=36,
                        bgcolor=BG_WHITE,
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=18,
                        alignment=ft.Alignment(0, 0),
                        tooltip="Volver al Centro de Reportes",
                        on_click=lambda _: page.go("/admin/reportes"),
                        content=ft.Icon(ft.Icons.ARROW_BACK, size=16, color=TEXT_COLOR),
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                "Reporte Integral de Actividades Deportivas",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                            ft.Text(
                                "Alumnos por Deporte, Nivel, Horario y Profesor a Cargo",
                                size=12,
                                color=MUTED,
                            ),
                        ],
                    ),
                ],
            ),
            ft.Row(
                spacing=10,
                controls=[
                    ft.Button(
                        content=ft.Row(
                            spacing=6,
                            controls=[
                                ft.Icon(
                                    ft.Icons.FILE_DOWNLOAD_OUTLINED,
                                    size=15,
                                    color=TEAL_DARK,
                                ),
                                ft.Text(
                                    "Exportar Excel",
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                    color=TEAL_DARK,
                                ),
                            ],
                        ),
                        bgcolor=TEAL_LIGHT,
                        height=36,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)
                        ),
                        on_click=lambda _: page.launch_url(
                            api_client.reporte_url("deportes")
                        ),
                    ),
                    ft.Button(
                        content=ft.Row(
                            spacing=6,
                            controls=[
                                ft.Icon(
                                    ft.Icons.PRINT_OUTLINED, size=15, color=BG_WHITE
                                ),
                                ft.Text(
                                    "Imprimir PDF",
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                    color=BG_WHITE,
                                ),
                            ],
                        ),
                        bgcolor=ORANGE,
                        height=36,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)
                        ),
                        on_click=lambda _: None,
                    ),
                ],
            ),
        ],
    )

    # ==================== 2. INDICADORES REALES ====================
    def kpi_card(
        titulo: str, valor: int, subtitulo: str, icono: ft.IconData
    ) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 6, "lg": 3},
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=12,
            padding=18,
            content=ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=40,
                        height=40,
                        bgcolor=TEAL_LIGHT,
                        border_radius=BORDER_RADIUS,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(icono, size=20, color=TEAL_DARK),
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                str(valor),
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                            ft.Text(
                                titulo,
                                size=13,
                                weight=ft.FontWeight.W_600,
                                color=TEXT_COLOR,
                            ),
                            ft.Text(
                                subtitulo,
                                size=11,
                                color=MUTED,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                    ),
                ],
            ),
        )

    docentes_responsables = len(
        {
            d.get("legajo_profesor_responsable")
            for d in estado["deportes"]
            if d.get("legajo_profesor_responsable") is not None
        }
    )

    kpis = ft.ResponsiveRow(
        columns=12,
        spacing=16,
        run_spacing=16,
        controls=[
            kpi_card(
                "Disciplinas deportivas",
                len(estado["deportes"]),
                "Deportes cargados en el sistema",
                ft.Icons.FITNESS_CENTER_OUTLINED,
            ),
            kpi_card(
                "Grupos conformados",
                len(estado["grupos"]),
                "Grupos por deporte y nivel",
                ft.Icons.GROUPS_OUTLINED,
            ),
            kpi_card(
                "Alumnos inscriptos",
                len(estado["inscripciones"]),
                "Fichas de inscripción registradas",
                ft.Icons.PEOPLE_OUTLINE,
            ),
            kpi_card(
                "Docentes responsables",
                docentes_responsables,
                "Profesores a cargo de disciplinas",
                ft.Icons.WORK_OUTLINE,
            ),
        ],
    )

    # ==================== 3. RESUMEN POR DEPORTE ====================
    def grupo_resumen_linea(grupo: dict) -> ft.Row:
        cantidad = inscriptos_por_grupo.get(grupo["id_grupo"], 0)
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    expand=True,
                    content=ft.Text(
                        f"{grupo.get('nivel', '—')} · {grupo.get('horario', '—')}",
                        size=12,
                        color=MUTED,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ),
                ft.Text(
                    f"{cantidad} inscriptos",
                    size=12,
                    weight=ft.FontWeight.W_600,
                    color=TEAL_DARK,
                ),
            ],
        )

    def deporte_card(deporte: dict) -> ft.Container:
        grupos_deporte = [
            g for g in estado["grupos"] if g.get("id_deporte") == deporte["id_deporte"]
        ]
        total_inscriptos = sum(
            inscriptos_por_grupo.get(g["id_grupo"], 0) for g in grupos_deporte
        )
        return ft.Container(
            col={"sm": 12, "md": 6, "lg": 4},
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=18,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=32,
                                height=32,
                                bgcolor=TEAL_LIGHT,
                                border_radius=BORDER_RADIUS,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(
                                    ft.Icons.FITNESS_CENTER_OUTLINED,
                                    size=16,
                                    color=TEAL_DARK,
                                ),
                            ),
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    deporte.get("nombre", "Deporte"),
                                    size=15,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEAL_DARK,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ),
                        ],
                    ),
                    ft.Text(
                        f"Responsable: {responsable_del_deporte(deporte)}",
                        size=12,
                        color=MUTED,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        f"{len(grupos_deporte)} grupos · {total_inscriptos} inscriptos",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=TEAL,
                    ),
                    ft.Column(
                        spacing=4,
                        controls=[grupo_resumen_linea(g) for g in grupos_deporte]
                        or [ft.Text("Sin grupos conformados.", size=12, color=MUTED)],
                    ),
                ],
            ),
        )

    seccion_resumen = ft.Column(
        spacing=16,
        controls=[
            ft.Text(
                "Resumen por Disciplina Deportiva",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=TEAL_DARK,
            ),
            ft.ResponsiveRow(
                columns=12,
                spacing=16,
                run_spacing=16,
                controls=[deporte_card(d) for d in estado["deportes"]]
                or [
                    ft.Container(
                        col={"sm": 12},
                        padding=20,
                        bgcolor=BG_WHITE,
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=CARD_RADIUS,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(
                            "No hay disciplinas deportivas registradas en el sistema.",
                            size=13,
                            color=MUTED,
                        ),
                    )
                ],
            ),
        ],
    )

    # ==================== 4. FILTROS ====================
    search_field = ft.TextField(
        hint_text="Buscar alumno, legajo o disciplina...",
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

    niveles_disponibles = sorted(
        {g.get("nivel") for g in estado["grupos"] if g.get("nivel")}
    )
    horarios_disponibles = list(
        {g.get("horario") for g in estado["grupos"] if g.get("horario")}
    )

    filtro_deporte_container = filtro_dropdown(
        "Deporte: Todos", 170, ["Todos"] + [d["nombre"] for d in estado["deportes"]]
    )
    filtro_deporte: ft.Dropdown = filtro_deporte_container.content
    filtro_nivel_container = filtro_dropdown(
        "Nivel: Todos", 150, ["Todos"] + niveles_disponibles
    )
    filtro_nivel: ft.Dropdown = filtro_nivel_container.content
    filtro_horario_container = filtro_dropdown(
        "Horario: Todos", 210, ["Todos"] + horarios_disponibles
    )
    filtro_horario: ft.Dropdown = filtro_horario_container.content

    filters_bar = ft.Row(
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            search_input,
            filtro_deporte_container,
            filtro_nivel_container,
            filtro_horario_container,
        ],
    )

    # ==================== 5. TABLA DE INSCRIPTOS ====================
    columnas_deporte = [
        ("Disciplina Deportiva", 150, False),
        ("Nivel Educativo", 130, False),
        ("Curso", 110, False),
        ("Legajo", 90, False),
        ("Alumno Inscripto", 170, False),
        ("Días y Horarios", 190, False),
        ("Docente a Cargo", 170, False),
        ("Fecha de Inscripción", 110, False),
    ]
    header_table = create_table_header(columnas_deporte)
    table_holder = ft.Container()
    pagination_holder = ft.Container()

    def inscripcion_row(inscripcion: dict) -> ft.Container:
        grupo = grupo_por_id.get(inscripcion.get("id_grupo")) or {}
        deporte = next(
            (
                d
                for d in estado["deportes"]
                if d.get("nombre") == inscripcion.get("deporte")
            ),
            None,
        )
        responsable = (
            responsable_del_deporte(deporte) if deporte else "Sin responsable asignado"
        )
        return ft.Container(
            height=50,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=150,
                        content=ft.Text(
                            inscripcion.get("deporte") or "—",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        width=130,
                        content=ft.Text(
                            grupo.get("nivel") or "Sin nivel", size=13, color=MUTED
                        ),
                    ),
                    ft.Container(
                        width=110,
                        content=ft.Text(
                            curso_del_alumno(inscripcion.get("legajo_alumno")),
                            size=13,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=90,
                        content=ft.Text(
                            f"#{inscripcion.get('legajo_alumno', '')}",
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color=TEAL,
                        ),
                    ),
                    ft.Container(
                        width=170,
                        content=ft.Text(
                            str(inscripcion.get("alumno", "")).split(" (")[0],
                            size=14,
                            weight=ft.FontWeight.W_500,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=190,
                        content=ft.Text(
                            grupo.get("horario") or "Sin horario asignado",
                            size=12,
                            color=TEXT_COLOR,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ),
                    ft.Container(
                        width=170,
                        content=ft.Text(
                            responsable,
                            size=13,
                            color=MUTED,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ),
                    ft.Container(
                        width=110,
                        content=ft.Text(
                            formatear_fecha(inscripcion.get("fecha_inscripcion")),
                            size=12,
                            color=MUTED,
                        ),
                    ),
                ],
            ),
        )

    def inscripciones_filtradas() -> list[dict]:
        texto = (estado["texto"] or "").lower()
        resultado = []
        for inscripcion in estado["inscripciones"]:
            grupo = grupo_por_id.get(inscripcion.get("id_grupo")) or {}
            if (
                estado["deporte"] != "Todos"
                and (inscripcion.get("deporte") or "") != estado["deporte"]
            ):
                continue
            if (
                estado["nivel"] != "Todos"
                and (grupo.get("nivel") or "") != estado["nivel"]
            ):
                continue
            if (
                estado["horario"] != "Todos"
                and (grupo.get("horario") or "") != estado["horario"]
            ):
                continue
            if (
                texto
                and texto
                not in f"{inscripcion.get('alumno', '')} {inscripcion.get('deporte', '')} {inscripcion.get('legajo_alumno', '')}".lower()
            ):
                continue
            resultado.append(inscripcion)
        return resultado

    def render():
        visibles = inscripciones_filtradas()
        table_holder.content = create_table_container(
            header=header_table,
            rows=[inscripcion_row(i) for i in visibles]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "No hay alumnos inscriptos que coincidan con los filtros aplicados.",
                        size=13,
                        color=MUTED,
                    ),
                )
            ],
            min_width=1152,
        )
        pagination_holder.content = create_pagination_bar(
            texto_info=f"Mostrando {len(visibles)} de {len(estado['inscripciones'])} alumnos inscriptos en disciplinas deportivas",
            pagina_actual=1,
            total_paginas=max(1, (len(visibles) + 9) // 10),
        )
        try:
            page.update()
        except Exception:
            pass

    def on_buscar(e):
        estado["texto"] = search_field.value or ""
        render()

    def on_filtrar_deporte(e):
        estado["deporte"] = filtro_deporte.value or "Todos"
        render()

    def on_filtrar_nivel(e):
        estado["nivel"] = filtro_nivel.value or "Todos"
        render()

    def on_filtrar_horario(e):
        estado["horario"] = filtro_horario.value or "Todos"
        render()

    search_field.on_change = on_buscar
    filtro_deporte.on_change = on_filtrar_deporte
    filtro_nivel.on_change = on_filtrar_nivel
    filtro_horario.on_change = on_filtrar_horario

    render()

    # ==================== 6. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Reporte: Deportes, Niveles y Horarios",
        active_route="/admin/reportes",
        content_controls=[
            header_actions,
            aviso_error,
            kpis,
            seccion_resumen,
            filters_bar,
            table_holder,
            pagination_holder,
        ],
    )
