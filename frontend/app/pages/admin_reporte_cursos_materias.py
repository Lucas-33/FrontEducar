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


async def get_admin_reporte_cursos_materias_view(page: ft.Page) -> ft.Row:
    """Reporte de cursos por nivel con su matrícula, materias asignadas y docente a cargo."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and api_client.token != token_almacenado:
        api_client.set_token(token_almacenado)

    estado: dict = {
        "niveles": [],
        "cursos": [],
        "alumnos": [],
        "asignaciones": [],
        "texto": "",
        "materia": "Todas",
        "nivel": "Todos",
        "curso": "Todos",
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

    estado["niveles"] = await consultar("niveles", api_client.get_niveles)
    estado["cursos"] = await consultar("cursos", api_client.get_cursos)
    estado["alumnos"] = await consultar(
        "alumnos", api_client.get_alumnos, solo_activos=False
    )
    estado["asignaciones"] = await consultar(
        "asignaciones", api_client.get_asignaciones
    )

    nivel_por_id = {n["id_nivel"]: n["nombre"] for n in estado["niveles"]}
    nombre_nivel_por_curso = {
        c["id_curso"]: nivel_por_id.get(c.get("id_nivel"), f"Nivel {c.get('id_nivel')}")
        for c in estado["cursos"]
    }

    def alumnos_del_curso(id_curso) -> list[dict]:
        return [a for a in estado["alumnos"] if a.get("id_curso") == id_curso]

    def asignaciones_del_curso(id_curso) -> list[dict]:
        return [a for a in estado["asignaciones"] if a.get("id_curso") == id_curso]

    def docentes_del_curso(id_curso) -> list[str]:
        nombres: list[str] = []
        for asignacion in asignaciones_del_curso(id_curso):
            profesor = asignacion.get("profesor")
            if profesor and profesor not in nombres:
                nombres.append(profesor)
        return nombres

    def materias_del_curso(id_curso) -> list[str]:
        materias: list[str] = []
        for asignacion in asignaciones_del_curso(id_curso):
            materia = asignacion.get("materia")
            if materia and materia not in materias:
                materias.append(materia)
        return materias

    total_materias = len(
        {
            a.get("id_materia")
            for a in estado["asignaciones"]
            if a.get("id_materia") is not None
        }
    )
    total_docentes_asignados = len(
        {
            a.get("legajo_profesor")
            for a in estado["asignaciones"]
            if a.get("legajo_profesor") is not None
        }
    )

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
                                "Nómina Curricular: Cursos y Materias",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                            ft.Text(
                                "Matrícula por curso, materias asignadas y docente a cargo",
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
                            api_client.reporte_url("cursos-materias")
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

    kpis = ft.ResponsiveRow(
        columns=12,
        spacing=16,
        run_spacing=16,
        controls=[
            kpi_card(
                "Niveles educativos",
                len(estado["niveles"]),
                "Niveles cargados en el sistema",
                ft.Icons.LAYERS_OUTLINED,
            ),
            kpi_card(
                "Cursos y divisiones",
                len(estado["cursos"]),
                "Divisiones activas",
                ft.Icons.CLASS_OUTLINED,
            ),
            kpi_card(
                "Materias dictadas",
                total_materias,
                "Materias con al menos una asignación",
                ft.Icons.MENU_BOOK_OUTLINED,
            ),
            kpi_card(
                "Docentes asignados",
                total_docentes_asignados,
                "Docentes con materias a cargo",
                ft.Icons.PERSON_OUTLINE,
            ),
        ],
    )

    # ==================== 3. FILTROS ====================
    search_field = ft.TextField(
        hint_text="Buscar materia, curso o docente...",
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

    materias_disponibles = sorted(
        {a.get("materia") for a in estado["asignaciones"] if a.get("materia")}
    )

    filtro_materia_container = filtro_dropdown(
        "Materia: Todas", 190, ["Todas"] + materias_disponibles
    )
    filtro_materia: ft.Dropdown = filtro_materia_container.content
    filtro_nivel_container = filtro_dropdown(
        "Nivel: Todos", 160, ["Todos"] + [n["nombre"] for n in estado["niveles"]]
    )
    filtro_nivel: ft.Dropdown = filtro_nivel_container.content
    filtro_curso_container = filtro_dropdown(
        "Curso: Todos", 170, ["Todos"] + [c["nombre"] for c in estado["cursos"]]
    )
    filtro_curso: ft.Dropdown = filtro_curso_container.content

    filters_bar = ft.Row(
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            search_input,
            filtro_materia_container,
            filtro_nivel_container,
            filtro_curso_container,
        ],
    )

    # ==================== 4. TABLA RESUMEN DE CURSOS ====================
    columnas_resumen = [
        ("Nivel Educativo", 150, False),
        ("Curso / División", 160, False),
        ("Alumnos Totales", 130, False),
        ("Alumnos Activos", 140, False),
        ("Materias Asignadas", 150, False),
        ("Docentes a Cargo", 290, False),
    ]
    header_resumen = create_table_header(columnas_resumen)
    table_holder_resumen = ft.Container()

    def curso_resumen_row(curso: dict) -> ft.Container:
        id_curso = curso["id_curso"]
        alumnos_curso = alumnos_del_curso(id_curso)
        activos = len(
            [
                a
                for a in alumnos_curso
                if str(a.get("estado_alumno", "")).upper() == "ACTIVO"
            ]
        )
        docentes = docentes_del_curso(id_curso)
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=150,
                        content=ft.Text(
                            nombre_nivel_por_curso.get(id_curso, "Sin nivel"),
                            size=13,
                            color=MUTED,
                        ),
                    ),
                    ft.Container(
                        width=160,
                        content=ft.Text(
                            curso.get("nombre", ""),
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        width=130,
                        content=ft.Text(
                            str(len(alumnos_curso)),
                            size=14,
                            weight=ft.FontWeight.W_500,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=140,
                        content=ft.Text(
                            str(activos),
                            size=14,
                            weight=ft.FontWeight.W_500,
                            color=TEAL,
                        ),
                    ),
                    ft.Container(
                        width=150,
                        content=ft.Text(
                            str(len(materias_del_curso(id_curso))),
                            size=14,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=290,
                        content=ft.Text(
                            ", ".join(docentes) if docentes else "Sin docente asignado",
                            size=13,
                            color=MUTED,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ),
                ],
            ),
        )

    def cursos_filtrados() -> list[dict]:
        texto = (estado["texto"] or "").lower()
        resultado = []
        for curso in estado["cursos"]:
            nivel = nombre_nivel_por_curso.get(curso["id_curso"], "")
            if estado["nivel"] != "Todos" and nivel != estado["nivel"]:
                continue
            if estado["curso"] != "Todos" and curso.get("nombre") != estado["curso"]:
                continue
            if estado["materia"] != "Todas" and estado[
                "materia"
            ] not in materias_del_curso(curso["id_curso"]):
                continue
            if texto:
                heno = (
                    f"{curso.get('nombre', '')} {nivel} "
                    + " ".join(materias_del_curso(curso["id_curso"]))
                    + " "
                    + " ".join(docentes_del_curso(curso["id_curso"]))
                )
                if texto not in heno.lower():
                    continue
            resultado.append(curso)
        return resultado

    # ==================== 5. TABLA DE ASIGNACIONES ====================
    columnas_asignaciones = [
        ("Nivel Educativo", 150, False),
        ("Curso", 150, False),
        ("Asignatura / Materia", 200, False),
        ("Docente Titular a Cargo", 220, False),
        ("Alumnos Inscriptos", 130, False),
    ]
    header_asignaciones = create_table_header(columnas_asignaciones)
    table_holder_asignaciones = ft.Container()

    def asignacion_row(asignacion: dict) -> ft.Container:
        inscriptos = len(alumnos_del_curso(asignacion.get("id_curso")))
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
                            asignacion.get("nivel") or "Sin nivel", size=13, color=MUTED
                        ),
                    ),
                    ft.Container(
                        width=150,
                        content=ft.Text(
                            asignacion.get("curso") or "—",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=200,
                        content=ft.Text(
                            asignacion.get("materia") or "—",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        width=220,
                        content=ft.Text(
                            asignacion.get("profesor") or "Sin docente asignado",
                            size=13,
                            weight=ft.FontWeight.W_500,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=130, content=ft.Text(str(inscriptos), size=14, color=TEAL)
                    ),
                ],
            ),
        )

    def asignaciones_filtradas() -> list[dict]:
        texto = (estado["texto"] or "").lower()
        resultado = []
        for asignacion in estado["asignaciones"]:
            if (
                estado["nivel"] != "Todos"
                and (asignacion.get("nivel") or "") != estado["nivel"]
            ):
                continue
            if (
                estado["curso"] != "Todos"
                and (asignacion.get("curso") or "") != estado["curso"]
            ):
                continue
            if (
                estado["materia"] != "Todas"
                and (asignacion.get("materia") or "") != estado["materia"]
            ):
                continue
            if (
                texto
                and texto
                not in f"{asignacion.get('materia', '')} {asignacion.get('curso', '')} {asignacion.get('profesor', '')}".lower()
            ):
                continue
            resultado.append(asignacion)
        return resultado

    pagination_holder = ft.Container()

    def render():
        cursos_visibles = cursos_filtrados()
        asignaciones_visibles = asignaciones_filtradas()

        table_holder_resumen.content = create_table_container(
            header=header_resumen,
            rows=[curso_resumen_row(c) for c in cursos_visibles]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "No hay cursos que coincidan con los filtros aplicados.",
                        size=13,
                        color=MUTED,
                    ),
                )
            ],
            min_width=1052,
        )
        table_holder_asignaciones.content = create_table_container(
            header=header_asignaciones,
            rows=[asignacion_row(a) for a in asignaciones_visibles]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "No hay materias asignadas que coincidan con los filtros aplicados.",
                        size=13,
                        color=MUTED,
                    ),
                )
            ],
            min_width=882,
        )
        pagination_holder.content = create_pagination_bar(
            texto_info=f"Mostrando {len(cursos_visibles)} de {len(estado['cursos'])} cursos y {len(asignaciones_visibles)} de {len(estado['asignaciones'])} asignaciones",
            pagina_actual=1,
            total_paginas=max(1, (len(cursos_visibles) + 9) // 10),
        )
        try:
            page.update()
        except Exception:
            pass

    def on_buscar(e):
        estado["texto"] = search_field.value or ""
        render()

    def on_filtrar_materia(e):
        estado["materia"] = filtro_materia.value or "Todas"
        render()

    def on_filtrar_nivel(e):
        estado["nivel"] = filtro_nivel.value or "Todos"
        render()

    def on_filtrar_curso(e):
        estado["curso"] = filtro_curso.value or "Todos"
        render()

    search_field.on_change = on_buscar
    filtro_materia.on_select = on_filtrar_materia
    filtro_nivel.on_select = on_filtrar_nivel
    filtro_curso.on_select = on_filtrar_curso

    render()

    # ==================== 6. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Reporte: Cursos, Materias y Docentes",
        active_route="/admin/reportes",
        content_controls=[
            header_actions,
            aviso_error,
            kpis,
            filters_bar,
            ft.Column(
                spacing=12,
                controls=[
                    ft.Text(
                        "Resumen de Cursos y Divisiones por Nivel",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=TEAL_DARK,
                    ),
                    table_holder_resumen,
                ],
            ),
            ft.Column(
                spacing=12,
                controls=[
                    ft.Text(
                        "Asignaciones: Materia, Curso y Docente a Cargo",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=TEAL_DARK,
                    ),
                    table_holder_asignaciones,
                ],
            ),
            pagination_holder,
        ],
    )
