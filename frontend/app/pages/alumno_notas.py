import flet as ft
from frontend.app.api_client import api_client
from frontend.app.components.constants import (
    BADGE_GREEN_BG,
    BADGE_GREEN_TXT,
    BADGE_RED_BG,
    BADGE_RED_TXT,
    BADGE_YELLOW_BG,
    BADGE_YELLOW_TXT,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    MUTED,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.portal_layout import portal_layout
from frontend.app.components.table_view import (
    create_pagination_bar,
    create_table_container,
    create_table_header,
)


def _nombre_alumno(perfil: dict | None, legajo: int | None) -> str:
    vinculo = (perfil or {}).get("vinculacion") or ""
    if ":" in vinculo:
        vinculo = vinculo.split(":", 1)[1]
    vinculo = vinculo.split("(#", 1)[0].strip()
    return vinculo or (f"Alumno #{legajo}" if legajo else "Alumno")


def _fecha_legible(iso: str | None) -> str:
    if not iso:
        return "—"
    partes = str(iso)[:10].split("-")
    if len(partes) == 3:
        return f"{partes[2]}/{partes[1]}/{partes[0]}"
    return str(iso)


def _badge_asistencia(estado: str) -> ft.Container:
    mapa = {
        "PRESENTE": (BADGE_GREEN_BG, BADGE_GREEN_TXT),
        "TARDE": (BADGE_YELLOW_BG, BADGE_YELLOW_TXT),
        "JUSTIFICADO": (TEAL_LIGHT, TEAL_DARK),
        "AUSENTE": (BADGE_RED_BG, BADGE_RED_TXT),
    }
    bg, color = mapa.get((estado or "").upper(), (BADGE_RED_BG, BADGE_RED_TXT))
    return ft.Container(
        padding=ft.Padding(8, 4, 8, 4),
        bgcolor=bg,
        border_radius=4,
        content=ft.Text(estado or "—", size=11, weight=ft.FontWeight.W_600, color=color),
    )


def _kpi(titulo: str, valor: str, subtitulo: str, icono: ft.IconData) -> ft.Container:
    return ft.Container(
        col={"sm": 6, "md": 3},
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=16,
        content=ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=40,
                    height=40,
                    bgcolor=TEAL_LIGHT,
                    border_radius=8,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(icono, size=20, color=TEAL_DARK),
                ),
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(titulo, size=10, weight=ft.FontWeight.BOLD, color=MUTED),
                        ft.Text(valor, size=20, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                        ft.Text(subtitulo, size=10, color=MUTED),
                    ],
                ),
            ],
        ),
    )


async def get_alumno_notas_view(page: ft.Page) -> ft.Row:
    """Calificaciones y presentismo del alumno autenticado."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    try:
        perfil = await api_client.get_mi_perfil()
    except Exception:
        perfil = None

    legajo = (perfil or {}).get("legajo_alumno")

    def tarjeta_sin_identidad() -> ft.Container:
        return ft.Container(
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=48,
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.PERSON_OFF_OUTLINED, size=44, color=MUTED),
                    ft.Text("No se pudo identificar al alumno.", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                    ft.Text("Inicie sesión nuevamente para consultar sus notas.", size=13, color=MUTED),
                ],
            ),
        )

    if not legajo:
        return portal_layout(
            page=page,
            titulo="Mis Notas y Asistencia",
            active_route="/portal/alumno/notas",
            rol="Alumno",
            usuario_nombre="Alumno",
            usuario_sub="Sesión no identificada",
            content_controls=[tarjeta_sin_identidad()],
        )

    # ==================== 1. CARGA DE DATOS ====================
    calificaciones: list[dict] = []
    asistencias: list[dict] = []
    resumen: dict | None = None
    cursos: list[dict] = []
    hubo_error = False

    try:
        calificaciones = await api_client.get_calificaciones()
    except Exception:
        hubo_error = True
    try:
        asistencias = await api_client.get_asistencia(legajo_alumno=legajo)
    except Exception:
        hubo_error = True
    try:
        resumen = await api_client.get_resumen_asistencia(legajo)
    except Exception:
        resumen = None
    try:
        cursos = await api_client.get_cursos()
    except Exception:
        cursos = []

    id_curso_actual = next((c.get("id_curso") for c in calificaciones if c.get("id_curso")), None) or next(
        (a.get("id_curso") for a in asistencias if a.get("id_curso")), None
    )
    curso_actual = next((c.get("nombre") for c in cursos if c.get("id_curso") == id_curso_actual), None)

    # ==================== 2. KPIs ====================
    notas = [c.get("nota") or 0 for c in calificaciones]
    promedio = f"{sum(notas) / len(notas):.2f}" if notas else "—"
    presentismo = f"{resumen.get('porcentaje_presentismo', 0):.1f}%" if resumen else "—"
    inasistencias = (resumen.get("ausentes", 0) + resumen.get("justificados", 0)) if resumen else "—"
    materias = len({c.get("id_materia") for c in calificaciones})

    kpis_row = ft.ResponsiveRow(
        columns=12,
        spacing=16,
        controls=[
            _kpi("PROMEDIO GENERAL", promedio, "Sobre todas las evaluaciones", ft.Icons.STAR_OUTLINE),
            _kpi("PRESENTISMO", presentismo, "Asistencia registrada", ft.Icons.FACT_CHECK_OUTLINED),
            _kpi("INASISTENCIAS", str(inasistencias), "Ausencias y justificadas", ft.Icons.EVENT_BUSY_OUTLINED),
            _kpi("MATERIAS EVALUADAS", str(materias), f"{len(calificaciones)} calificaciones cargadas", ft.Icons.MENU_BOOK_OUTLINED),
        ],
    )

    # ==================== 3. TABLA DE CALIFICACIONES ====================
    header_notas = create_table_header(
        [
            ("Materia", 200, False),
            ("Curso", 160, False),
            ("Período", 140, False),
            ("Tipo", 140, False),
            ("Nota", 70, False),
            ("Fecha", 100, False),
            ("Observación", None, False),
        ]
    )

    def fila_nota(cal: dict) -> ft.Container:
        nota = cal.get("nota")
        color_nota = BADGE_GREEN_TXT if (nota or 0) >= 6 else BADGE_RED_TXT
        return ft.Container(
            height=52,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=200, content=ft.Text(cal.get("materia") or "—", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=160, content=ft.Text(cal.get("curso") or "—", size=13, color=MUTED)),
                    ft.Container(width=140, content=ft.Text(cal.get("periodo") or "—", size=12, color=MUTED)),
                    ft.Container(width=140, content=ft.Text(cal.get("tipo") or "—", size=12, color=MUTED)),
                    ft.Container(width=70, content=ft.Text(f"{nota:.1f}" if isinstance(nota, (int, float)) else "—", size=14, weight=ft.FontWeight.BOLD, color=color_nota)),
                    ft.Container(width=100, content=ft.Text(_fecha_legible(cal.get("fecha")), size=12, color=MUTED)),
                    ft.Container(expand=True, content=ft.Text(cal.get("observacion") or "—", size=12, color=MUTED)),
                ],
            ),
        )

    filas_notas = [fila_nota(c) for c in calificaciones] or [
        ft.Container(
            padding=20,
            alignment=ft.Alignment(0, 0),
            content=ft.Text("Todavía no hay calificaciones registradas.", size=13, color=MUTED),
        )
    ]
    tabla_notas = create_table_container(header=header_notas, rows=filas_notas, min_width=1050)
    paginacion_notas = create_pagination_bar(
        texto_info=f"Mostrando {len(calificaciones)} calificaciones",
        pagina_actual=1,
        total_paginas=max(1, (len(calificaciones) + 9) // 10),
    )

    # ==================== 4. PROMEDIO POR MATERIA ====================
    acumulado: dict[str, list[float]] = {}
    for c in calificaciones:
        acumulado.setdefault(c.get("materia") or "Sin materia", []).append(c.get("nota") or 0)

    filas_promedios = []
    for materia, valores in sorted(acumulado.items()):
        prom = sum(valores) / len(valores)
        color = BADGE_GREEN_TXT if prom >= 6 else BADGE_RED_TXT
        filas_promedios.append(
            ft.Container(
                height=48,
                padding=ft.Padding(16, 0, 16, 0),
                border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
                content=ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(expand=True, content=ft.Text(materia, size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                        ft.Container(width=100, content=ft.Text(f"{len(valores)} notas", size=12, color=MUTED)),
                        ft.Container(
                            width=90,
                            content=ft.Text(f"{prom:.2f}", size=14, weight=ft.FontWeight.BOLD, color=color),
                        ),
                    ],
                ),
            )
        )

    header_promedios = create_table_header([("Materia", None, False), ("Evaluaciones", 100, False), ("Promedio", 90, True)])
    tabla_promedios = create_table_container(
        header=header_promedios,
        rows=filas_promedios
        or [
            ft.Container(
                padding=20,
                alignment=ft.Alignment(0, 0),
                content=ft.Text("Sin datos para calcular promedios.", size=13, color=MUTED),
            )
        ],
        min_width=600,
    )

    # ==================== 5. TABLA DE ASISTENCIAS ====================
    header_asist = create_table_header([("Fecha", 130, False), ("Estado", 140, False), ("Observación", None, False)])
    filas_asist = []
    for registro in sorted(asistencias, key=lambda r: str(r.get("fecha")), reverse=True):
        filas_asist.append(
            ft.Container(
                height=48,
                padding=ft.Padding(16, 0, 16, 0),
                border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
                content=ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(width=130, content=ft.Text(_fecha_legible(registro.get("fecha")), size=13, color=TEXT_COLOR)),
                        ft.Container(width=140, content=_badge_asistencia(registro.get("estado"))),
                        ft.Container(expand=True, content=ft.Text(registro.get("observacion") or "—", size=12, color=MUTED)),
                    ],
                ),
            )
        )

    tabla_asist = create_table_container(
        header=header_asist,
        rows=filas_asist
        or [
            ft.Container(
                padding=20,
                alignment=ft.Alignment(0, 0),
                content=ft.Text("Todavía no hay registros de asistencia.", size=13, color=MUTED),
            )
        ],
        min_width=600,
    )

    def tarjeta(titulo: str, subtitulo: str, contenido: ft.Control) -> ft.Container:
        return ft.Container(
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=20,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ft.Text(subtitulo, size=12, color=MUTED),
                        ],
                    ),
                    contenido,
                ],
            ),
        )

    # ==================== 6. INFO Y AVISOS ====================
    detalle_curso = f" · Curso: {curso_actual}" if curso_actual else ""
    info_card = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
        padding=16,
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE, size=20, color=TEAL),
                ft.Text(
                    f"Legajo #{legajo}{detalle_curso} · Resumen de calificaciones y presentismo del ciclo lectivo.",
                    size=13,
                    weight=ft.FontWeight.W_500,
                    color=TEAL_DARK,
                ),
            ],
        ),
    )

    aviso_error = ft.Container(
        bgcolor="#FDE8E8",
        border_radius=BORDER_RADIUS,
        padding=12,
        visible=hubo_error,
        content=ft.Text("Algunos datos no se pudieron cargar desde el servidor.", size=13, color=BADGE_RED_TXT),
    )

    # ==================== 7. RETORNO CON PORTAL_LAYOUT ====================
    return portal_layout(
        page=page,
        titulo="Mis Notas y Asistencia",
        active_route="/portal/alumno/notas",
        rol="Alumno",
        usuario_nombre=_nombre_alumno(perfil, legajo),
        usuario_sub=f"Legajo #{legajo}",
        content_controls=[
            info_card,
            aviso_error,
            kpis_row,
            tarjeta("Mis Calificaciones", "Detalle de todas las evaluaciones registradas por tus docentes.", tabla_notas),
            paginacion_notas,
            tarjeta("Promedio por Materia", "Desempeño promedio calculado sobre las notas cargadas.", tabla_promedios),
            tarjeta("Mis Asistencias", "Registro diario de presentismo.", tabla_asist),
        ],
    )
