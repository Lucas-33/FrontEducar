import flet as ft
import httpx

from frontend.app.api_client import api_client
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BADGE_RED_BG,
    BADGE_RED_TXT,
    BG_PAGE,
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
from frontend.app.components.form_controls import status_badge
from frontend.app.components.table_view import (
    create_pagination_bar,
    create_table_container,
    create_table_header,
)


async def get_admin_reporte_alumnos_docentes_view(page: ft.Page) -> ft.Row:
    """Reporte consolidado de alumnos por curso/nivel y docentes por especialidad, con datos reales."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and api_client.token != token_almacenado:
        api_client.set_token(token_almacenado)

    estado: dict = {
        "alumnos": [],
        "profesores": [],
        "cursos": [],
        "niveles": [],
        "texto": "",
        "nivel": "Todos",
        "curso": "Todos",
        "matricula": "Todos",
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

    estado["alumnos"] = await consultar(
        "alumnos", api_client.get_alumnos, solo_activos=False
    )
    estado["profesores"] = await consultar(
        "docentes", api_client.get_profesores, solo_activos=False
    )
    estado["cursos"] = await consultar("cursos", api_client.get_cursos)
    estado["niveles"] = await consultar("niveles", api_client.get_niveles)

    curso_por_id = {c["id_curso"]: c for c in estado["cursos"]}
    nivel_por_id = {n["id_nivel"]: n["nombre"] for n in estado["niveles"]}

    def nombre_curso(id_curso) -> str:
        curso = curso_por_id.get(id_curso)
        return curso["nombre"] if curso else "Sin curso asignado"

    def nivel_del_alumno(alumno: dict) -> str:
        curso = curso_por_id.get(alumno.get("id_curso"))
        if not curso:
            return "Sin nivel"
        return nivel_por_id.get(curso.get("id_nivel"), f"Nivel {curso.get('id_nivel')}")

    alumnos_activos = len(
        [
            a
            for a in estado["alumnos"]
            if str(a.get("estado_alumno", "")).upper() == "ACTIVO"
        ]
    )
    alumnos_inactivos = len(estado["alumnos"]) - alumnos_activos
    docentes_activos = len(
        [
            p
            for p in estado["profesores"]
            if str(p.get("estado", "")).upper() == "ACTIVO"
        ]
    )
    docentes_inactivos = len(estado["profesores"]) - docentes_activos

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
                                "Nómina Oficial: Alumnos por Curso y Nivel",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                            ft.Text(
                                "Matrícula por nivel educativo y plantel docente por especialidad",
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
                            api_client.reporte_url("alumnos")
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
        titulo: str,
        valor: int,
        subtitulo: str,
        icono: ft.IconData,
        icono_color: str = TEAL_DARK,
        icono_bg: str = TEAL_LIGHT,
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
                        bgcolor=icono_bg,
                        border_radius=BORDER_RADIUS,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(icono, size=20, color=icono_color),
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
                "Alumnos activos",
                alumnos_activos,
                f"{len(estado['alumnos'])} alumnos registrados",
                ft.Icons.PERSON_OUTLINE,
            ),
            kpi_card(
                "Alumnos inactivos",
                alumnos_inactivos,
                "Matrículas dadas de baja",
                ft.Icons.PERSON_OUTLINE,
                BADGE_RED_TXT,
                BADGE_RED_BG,
            ),
            kpi_card(
                "Docentes activos",
                docentes_activos,
                f"{len(estado['profesores'])} docentes registrados",
                ft.Icons.WORK_OUTLINE,
            ),
            kpi_card(
                "Docentes inactivos",
                docentes_inactivos,
                "Docentes fuera de actividad",
                ft.Icons.WORK_OUTLINE,
                BADGE_RED_TXT,
                BADGE_RED_BG,
            ),
        ],
    )

    # ==================== 3. DISTRIBUCIONES (BARRAS PROPORCIONALES) ====================
    def barra_distribucion(
        nombre: str, valor: int, maximo: int, color: str = TEAL
    ) -> ft.Column:
        ancho = int(220 * valor / maximo) if maximo else 0
        return ft.Column(
            spacing=4,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            expand=True,
                            content=ft.Text(
                                nombre,
                                size=13,
                                color=TEXT_COLOR,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ),
                        ft.Text(
                            str(valor),
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ],
                ),
                ft.Container(
                    width=220,
                    height=10,
                    bgcolor=BG_PAGE,
                    border_radius=5,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=ft.Row(
                        spacing=0,
                        controls=[
                            ft.Container(
                                width=max(ancho, 4) if valor else 0,
                                height=10,
                                bgcolor=color,
                                border_radius=5,
                            ),
                        ],
                    ),
                ),
            ],
        )

    conteo_por_nivel: dict[str, int] = {}
    for alumno in estado["alumnos"]:
        nombre_nivel = nivel_del_alumno(alumno)
        conteo_por_nivel[nombre_nivel] = conteo_por_nivel.get(nombre_nivel, 0) + 1

    conteo_por_especialidad: dict[str, int] = {}
    for profesor in estado["profesores"]:
        especialidad = (
            profesor.get("especialidad") or "Sin especialidad"
        ).strip() or "Sin especialidad"
        conteo_por_especialidad[especialidad] = (
            conteo_por_especialidad.get(especialidad, 0) + 1
        )

    maximo_nivel = max(conteo_por_nivel.values()) if conteo_por_nivel else 0
    maximo_especialidad = (
        max(conteo_por_especialidad.values()) if conteo_por_especialidad else 0
    )

    def tarjeta_distribucion(
        titulo: str,
        subtitulo: str,
        filas: list[ft.Control],
    ) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 6},
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=20,
            content=ft.Column(
                spacing=14,
                controls=[
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(
                                titulo,
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                            ft.Text(subtitulo, size=12, color=MUTED),
                        ],
                    ),
                    *filas,
                ],
            ),
        )

    distribucion_alumnos = tarjeta_distribucion(
        "Alumnos por Nivel Educativo",
        f"{alumnos_activos} activos de {len(estado['alumnos'])} alumnos registrados",
        [
            barra_distribucion(nombre, cantidad, maximo_nivel)
            for nombre, cantidad in conteo_por_nivel.items()
        ]
        or [
            ft.Text("No hay alumnos registrados para distribuir.", size=13, color=MUTED)
        ],
    )

    especialidades_ordenadas = sorted(
        conteo_por_especialidad.items(), key=lambda par: par[1], reverse=True
    )
    distribucion_docentes = tarjeta_distribucion(
        "Docentes por Especialidad",
        f"{docentes_activos} activos de {len(estado['profesores'])} docentes registrados",
        [
            barra_distribucion(nombre, cantidad, maximo_especialidad, color=ORANGE)
            for nombre, cantidad in especialidades_ordenadas
        ]
        or [
            ft.Text(
                "No hay docentes registrados para distribuir.", size=13, color=MUTED
            )
        ],
    )

    # ==================== 4. FILTROS ACADÉMICOS ====================
    search_field = ft.TextField(
        hint_text="Filtrar por apellido, legajo...",
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

    filtro_nivel_container = filtro_dropdown(
        "Nivel: Todos", 160, ["Todos"] + [n["nombre"] for n in estado["niveles"]]
    )
    filtro_nivel: ft.Dropdown = filtro_nivel_container.content
    filtro_curso_container = filtro_dropdown(
        "Curso: Todos", 170, ["Todos"] + [c["nombre"] for c in estado["cursos"]]
    )
    filtro_curso: ft.Dropdown = filtro_curso_container.content
    filtro_matricula_container = filtro_dropdown(
        "Estado: Todos", 145, ["Todos", "Activo", "Inactivo"]
    )
    filtro_matricula: ft.Dropdown = filtro_matricula_container.content

    filters_bar = ft.Row(
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            search_input,
            filtro_nivel_container,
            filtro_curso_container,
            filtro_matricula_container,
        ],
    )

    # ==================== 5. TABLA DE ALUMNOS ====================
    columnas_reporte = [
        ("Nivel Educativo", 150, False),
        ("Curso / División", 150, False),
        ("Legajo", 100, False),
        ("Apellido", 140, False),
        ("Nombre", 160, False),
        ("Correo / Teléfono", 240, False),
        ("Estado Matrícula", 130, False),
    ]

    header_table = create_table_header(columnas_reporte)
    table_holder = ft.Container()
    pagination_holder = ft.Container()

    def alumno_reporte_row(item: dict) -> ft.Container:
        contacto = (
            item.get("correo_electronico")
            or item.get("telefono")
            or "Sin contacto registrado"
        )
        legajo = str(item.get("legajo", ""))
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
                        content=ft.Text(nivel_del_alumno(item), size=13, color=MUTED),
                    ),
                    ft.Container(
                        width=150,
                        content=ft.Text(
                            nombre_curso(item.get("id_curso")),
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        width=100,
                        content=ft.Text(
                            f"#{legajo}", size=13, weight=ft.FontWeight.BOLD, color=TEAL
                        ),
                    ),
                    ft.Container(
                        width=140,
                        content=ft.Text(
                            item.get("apellido", ""),
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=160,
                        content=ft.Text(
                            item.get("nombre", ""), size=14, color=TEXT_COLOR
                        ),
                    ),
                    ft.Container(
                        width=240, content=ft.Text(contacto, size=13, color=MUTED)
                    ),
                    ft.Container(
                        width=130,
                        content=status_badge(item.get("estado_alumno") or "Sin estado"),
                    ),
                ],
            ),
        )

    def alumnos_filtrados() -> list[dict]:
        texto = (estado["texto"] or "").lower()
        resultado = []
        for alumno in estado["alumnos"]:
            if (
                estado["nivel"] != "Todos"
                and nivel_del_alumno(alumno) != estado["nivel"]
            ):
                continue
            if (
                estado["curso"] != "Todos"
                and nombre_curso(alumno.get("id_curso")) != estado["curso"]
            ):
                continue
            if (
                estado["matricula"] != "Todos"
                and str(alumno.get("estado_alumno") or "").capitalize()
                != estado["matricula"]
            ):
                continue
            if (
                texto
                and texto
                not in f"{alumno.get('apellido', '')} {alumno.get('nombre', '')} {alumno.get('legajo', '')} {alumno.get('dni', '')}".lower()
            ):
                continue
            resultado.append(alumno)
        return resultado

    def render():
        visibles = alumnos_filtrados()
        table_holder.content = create_table_container(
            header=header_table,
            rows=[alumno_reporte_row(a) for a in visibles]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "No hay alumnos que coincidan con los filtros aplicados.",
                        size=13,
                        color=MUTED,
                    ),
                )
            ],
            min_width=1102,
        )
        pagination_holder.content = create_pagination_bar(
            texto_info=f"Mostrando {len(visibles)} de {len(estado['alumnos'])} alumnos registrados",
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

    def on_filtrar_nivel(e):
        estado["nivel"] = filtro_nivel.value or "Todos"
        render()

    def on_filtrar_curso(e):
        estado["curso"] = filtro_curso.value or "Todos"
        render()

    def on_filtrar_matricula(e):
        estado["matricula"] = filtro_matricula.value or "Todos"
        render()

    search_field.on_change = on_buscar
    filtro_nivel.on_change = on_filtrar_nivel
    filtro_curso.on_change = on_filtrar_curso
    filtro_matricula.on_change = on_filtrar_matricula

    render()

    # ==================== 6. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Reporte: Alumnos por Curso y Nivel",
        active_route="/admin/reportes",
        content_controls=[
            header_actions,
            aviso_error,
            kpis,
            ft.ResponsiveRow(
                columns=12,
                spacing=16,
                run_spacing=16,
                controls=[distribucion_alumnos, distribucion_docentes],
            ),
            filters_bar,
            table_holder,
            pagination_holder,
        ],
    )
