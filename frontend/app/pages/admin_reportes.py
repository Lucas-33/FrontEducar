import flet as ft
import httpx

from frontend.app.api_client import api_client
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    MUTED,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
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


async def get_admin_reportes_view(page: ft.Page) -> ft.Row:
    """Índice general de reportes con indicadores reales y vista previa en vivo desde la API."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    estado: dict = {
        "alumnos": [],
        "profesores": [],
        "cursos": [],
        "inscripciones_deporte": [],
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
    estado["inscripciones_deporte"] = await consultar(
        "inscripciones deportivas", api_client.get_inscripciones_deporte
    )

    alumnos_activos = len(
        [
            a
            for a in estado["alumnos"]
            if str(a.get("estado_alumno", "")).upper() == "ACTIVO"
        ]
    )
    docentes_activos = len(
        [
            p
            for p in estado["profesores"]
            if str(p.get("estado", "")).upper() == "ACTIVO"
        ]
    )

    aviso_error = ft.Text(
        "", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False
    )
    if errores:
        aviso_error.value = "⚠️ No se pudieron cargar algunos datos: " + " · ".join(
            errores
        )
        aviso_error.visible = True

    # ==================== 1. INDICADORES REALES ====================
    def kpi_card(
        titulo: str,
        valor: int,
        subtitulo: str,
        icono: ft.IconData,
        ruta: str,
    ) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 6, "lg": 3},
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=12,
            padding=18,
            on_click=lambda _: page.go(ruta),
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
                "Alumnos activos",
                alumnos_activos,
                f"{len(estado['alumnos'])} registrados en total",
                ft.Icons.PERSON_OUTLINE,
                "/admin/reporte-alumnos-docentes",
            ),
            kpi_card(
                "Docentes activos",
                docentes_activos,
                f"{len(estado['profesores'])} registrados en total",
                ft.Icons.WORK_OUTLINE,
                "/admin/reporte-alumnos-docentes",
            ),
            kpi_card(
                "Cursos y divisiones",
                len(estado["cursos"]),
                "Divisiones cargadas en el sistema",
                ft.Icons.CLASS_OUTLINED,
                "/admin/reporte-cursos-materias",
            ),
            kpi_card(
                "Inscriptos a deportes",
                len(estado["inscripciones_deporte"]),
                "Fichas de inscripción registradas",
                ft.Icons.FITNESS_CENTER_OUTLINED,
                "/admin/reporte-deportes-avanzado",
            ),
        ],
    )

    seccion_indicadores = ft.Column(
        spacing=16,
        controls=[
            ft.Text(
                "Indicadores Generales del Sistema",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=TEAL_DARK,
            ),
            kpis,
        ],
    )

    # ==================== 2. TARJETAS DE CATEGORÍAS RESPONSIVAS ====================
    def categoria_card(
        titulo: str, descripcion: str, icono: ft.IconData, ruta: str | None = None
    ) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 6, "lg": 4},
            height=116,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=12,
            padding=18,
            on_click=lambda _: page.go(ruta) if ruta else None,
            content=ft.Column(
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
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
                                content=ft.Icon(icono, size=16, color=TEAL_DARK),
                            ),
                            ft.Text(
                                titulo,
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                        ],
                    ),
                    ft.Text(
                        descripcion,
                        size=12,
                        color=MUTED,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
            ),
        )

    categorias_data = [
        (
            "Reporte por Alumno",
            "Nómina de alumnos por curso y nivel con su estado de matrícula.",
            ft.Icons.PERSON_OUTLINE,
            "/admin/reporte-alumnos-docentes",
        ),
        (
            "Reporte por Docente",
            "Plantel docente agrupado por especialidad y estado registrado.",
            ft.Icons.WORK_OUTLINE,
            "/admin/reporte-alumnos-docentes",
        ),
        (
            "Listado por Curso",
            "Cursos y divisiones con matrícula activa y materias asignadas.",
            ft.Icons.PEOPLE_OUTLINE,
            "/admin/reporte-cursos-materias",
        ),
        (
            "Listado por Materia",
            "Materias dictadas, docente a cargo e inscriptos por curso.",
            ft.Icons.MENU_BOOK_OUTLINED,
            "/admin/reporte-cursos-materias",
        ),
        (
            "Listado por Deporte",
            "Grupos, niveles, horarios e inscriptos por disciplina deportiva.",
            ft.Icons.FITNESS_CENTER_OUTLINED,
            "/admin/reporte-deportes-avanzado",
        ),
        (
            "Listado por Transporte",
            "Pasajeros por recorrido con estado de alta y datos de contacto.",
            ft.Icons.DIRECTIONS_BUS_OUTLINED,
            "/admin/reporte-transporte-pasajeros",
        ),
    ]

    seccion_categorias = ft.Column(
        spacing=16,
        controls=[
            ft.Text(
                "Categorías de Reportes Disponibles",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=TEAL_DARK,
            ),
            ft.ResponsiveRow(
                columns=12,
                spacing=16,
                run_spacing=16,
                controls=[categoria_card(t, d, i, r) for t, d, i, r in categorias_data],
            ),
        ],
    )

    # ==================== 3. VISTA PREVIA DE REPORTE (DATOS REALES) ====================
    nombre_curso = {c["id_curso"]: c["nombre"] for c in estado["cursos"]}
    curso_por_legajo = {a["legajo"]: a.get("id_curso") for a in estado["alumnos"]}

    ultimas_inscripciones = sorted(
        estado["inscripciones_deporte"],
        key=lambda i: str(i.get("fecha_inscripcion") or ""),
        reverse=True,
    )[:3]

    header_reporte = ft.Container(
        height=39,
        bgcolor=BG_PAGE,
        padding=ft.Padding(12, 0, 12, 0),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=120,
                    content=ft.Text(
                        "Legajo", size=12, weight=ft.FontWeight.BOLD, color=TEXT_COLOR
                    ),
                ),
                ft.Container(
                    width=220,
                    content=ft.Text(
                        "Alumno", size=12, weight=ft.FontWeight.BOLD, color=TEXT_COLOR
                    ),
                ),
                ft.Container(
                    width=150,
                    content=ft.Text(
                        "Curso", size=12, weight=ft.FontWeight.BOLD, color=TEXT_COLOR
                    ),
                ),
                ft.Container(
                    width=180,
                    content=ft.Text(
                        "Disciplina Deportiva",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_COLOR,
                    ),
                ),
                ft.Container(
                    expand=True,
                    content=ft.Text(
                        "Fecha de Inscripción",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_COLOR,
                    ),
                ),
            ],
        ),
    )

    def reporte_row(item: dict, con_borde: bool = True) -> ft.Container:
        curso = nombre_curso.get(
            curso_por_legajo.get(item.get("legajo_alumno")), "Sin curso asignado"
        )
        return ft.Container(
            height=40,
            padding=ft.Padding(12, 0, 12, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR))
            if con_borde
            else None,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=120,
                        content=ft.Text(
                            f"#{item.get('legajo_alumno', '')}",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL,
                        ),
                    ),
                    ft.Container(
                        width=220,
                        content=ft.Text(
                            str(item.get("alumno", "")).split(" (")[0],
                            size=13,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=150, content=ft.Text(curso, size=13, color=TEXT_COLOR)
                    ),
                    ft.Container(
                        width=180,
                        content=ft.Text(
                            item.get("deporte") or "—",
                            size=13,
                            weight=ft.FontWeight.W_500,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Text(
                            formatear_fecha(item.get("fecha_inscripcion")),
                            size=13,
                            color=MUTED,
                        ),
                    ),
                ],
            ),
        )

    if ultimas_inscripciones:
        filas_preview = [
            reporte_row(item, con_borde=(indice < len(ultimas_inscripciones) - 1))
            for indice, item in enumerate(ultimas_inscripciones)
        ]
    else:
        filas_preview = [
            ft.Container(
                padding=20,
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    "No hay inscripciones deportivas registradas en el sistema.",
                    size=13,
                    color=MUTED,
                ),
            )
        ]

    tabla_preview = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=12,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            spacing=0,
            controls=[
                header_reporte,
                *filas_preview,
            ],
        ),
    )

    preview_card = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text(
                                    "Vista Previa de Reporte: Inscripciones Deportivas",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEAL_DARK,
                                ),
                                ft.Text(
                                    "Últimas fichas de inscripción registradas en las disciplinas deportivas.",
                                    size=13,
                                    color=MUTED,
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Button(
                                    content=ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.FILE_DOWNLOAD_OUTLINED,
                                                size=14,
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
                                    height=32,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(
                                            radius=BORDER_RADIUS
                                        ),
                                        padding=ft.Padding(16, 8, 16, 8),
                                    ),
                                    on_click=lambda _: page.launch_url(
                                        api_client.reporte_url("deportes")
                                    ),
                                ),
                                ft.Button(
                                    content=ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.PRINT_OUTLINED,
                                                size=14,
                                                color=BG_WHITE,
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
                                    height=32,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(
                                            radius=BORDER_RADIUS
                                        ),
                                        padding=ft.Padding(16, 8, 16, 8),
                                    ),
                                    on_click=lambda _: None,
                                ),
                            ],
                        ),
                    ],
                ),
                tabla_preview,
            ],
        ),
    )

    # ==================== 4. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Módulo General de Reportes y Estadísticas",
        active_route="/admin/reportes",
        spacing=32,
        content_controls=[
            aviso_error,
            seccion_indicadores,
            seccion_categorias,
            preview_card,
        ],
    )
