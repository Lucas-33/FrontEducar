import flet as ft

from frontend.app.api_client import api_client
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
from frontend.app.components.portal_layout import portal_layout


def _plural(cantidad: int, singular: str, plural: str) -> str:
    """Devuelve 'N singular' o 'N plural' según corresponda."""
    return f"{cantidad} {singular if cantidad == 1 else plural}"


def _resumen(textos: list[str], limite: int = 40) -> str:
    """Une textos para subtítulos de KPI, recortando el resultado si es muy largo."""
    if not textos:
        return ""
    unido = ", ".join(textos)
    return unido if len(unido) <= limite else unido[: limite - 1].rstrip() + "…"


def _nombre_docente(perfil: dict | None, legajo: int | None) -> str:
    """Extrae el nombre legible del docente desde 'vinculacion' (ej: 'Docente: Gómez, Laura (#2001)')."""
    vinculo = (perfil or {}).get("vinculacion") or ""
    if ":" in vinculo:
        vinculo = vinculo.split(":", 1)[1]
    vinculo = vinculo.split("(#", 1)[0].strip()
    return vinculo or (f"Docente #{legajo}" if legajo else "Docente")


async def get_docente_dashboard_view(page: ft.Page) -> ft.Row:
    """Panel principal del portal docente conectado a la API (sin datos ficticios)."""

    # ==================== 0. IDENTIDAD DEL DOCENTE ====================
    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and api_client.token != token_almacenado:
        api_client.set_token(token_almacenado)

    try:
        perfil = await api_client.get_mi_perfil()
    except Exception:
        perfil = None

    legajo_docente = (perfil or {}).get("legajo_profesor")

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
                    ft.Text(
                        "No se pudo identificar al docente.",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=TEAL_DARK,
                    ),
                    ft.Text(
                        "Inicie sesión nuevamente para acceder al panel docente.",
                        size=13,
                        color=MUTED,
                    ),
                ],
            ),
        )

    if not legajo_docente:
        return portal_layout(
            page=page,
            titulo="Panel Docente — Mi Actividad",
            active_route="/portal/docente/dashboard",
            rol="Docente",
            usuario_nombre="Docente",
            usuario_sub="Sesión no identificada",
            content_controls=[tarjeta_sin_identidad()],
        )

    # ==================== 1. CARGA DE DATOS REALES ====================
    estado: dict = {
        "asignaciones": [],
        "alumnos": [],
        "deportes": [],
        "grupos": [],
        "inscripciones": [],
    }
    hubo_error = False

    try:
        asignaciones = await api_client.get_asignaciones()
    except Exception:
        asignaciones = []
        hubo_error = True
    estado["asignaciones"] = [
        a for a in asignaciones if a.get("legajo_profesor") == legajo_docente
    ]

    try:
        estado["alumnos"] = await api_client.get_alumnos(solo_activos=False)
    except Exception:
        estado["alumnos"] = []
        hubo_error = True

    try:
        deportes = await api_client.get_deportes()
    except Exception:
        deportes = []
        hubo_error = True
    estado["deportes"] = [
        d for d in deportes if d.get("legajo_profesor_responsable") == legajo_docente
    ]

    try:
        estado["grupos"] = await api_client.get_grupos_deporte()
    except Exception:
        estado["grupos"] = []
        hubo_error = True

    try:
        estado["inscripciones"] = await api_client.get_inscripciones_deporte()
    except Exception:
        estado["inscripciones"] = []
        hubo_error = True

    # ==================== 2. CÁLCULOS DERIVADOS ====================
    ids_cursos = sorted(
        {
            a.get("id_curso")
            for a in estado["asignaciones"]
            if a.get("id_curso") is not None
        }
    )
    alumnos_de_mis_cursos = [
        a for a in estado["alumnos"] if a.get("id_curso") in ids_cursos
    ]
    alumnos_activos = len(
        [
            a
            for a in alumnos_de_mis_cursos
            if (a.get("estado_alumno") or "").upper() == "ACTIVO"
        ]
    )

    alumnos_por_curso: dict = {}
    for alumno in alumnos_de_mis_cursos:
        id_curso = alumno.get("id_curso")
        alumnos_por_curso[id_curso] = alumnos_por_curso.get(id_curso, 0) + 1

    materias_distintas: dict = {}
    for a in estado["asignaciones"]:
        materias_distintas[a.get("id_materia")] = a.get("materia") or "-"

    cursos_distintos: dict = {}
    for a in estado["asignaciones"]:
        cursos_distintos[a.get("id_curso")] = a.get("curso") or "-"

    ids_deportes = {d.get("id_deporte") for d in estado["deportes"]}
    grupos_por_deporte: dict = {}
    for grupo in estado["grupos"]:
        if grupo.get("id_deporte") in ids_deportes:
            grupos_por_deporte.setdefault(grupo.get("id_deporte"), []).append(grupo)

    ids_grupos = {
        g.get("id_grupo") for grupos in grupos_por_deporte.values() for g in grupos
    }
    inscriptos_por_grupo: dict = {}
    for inscripcion in estado["inscripciones"]:
        if inscripcion.get("id_grupo") in ids_grupos:
            id_grupo = inscripcion.get("id_grupo")
            inscriptos_por_grupo[id_grupo] = inscriptos_por_grupo.get(id_grupo, 0) + 1

    total_inscriptos_deportes = sum(inscriptos_por_grupo.values())

    # ==================== 3. BANNER DOCENTE ====================
    banner_docente = ft.Container(
        bgcolor=TEAL_DARK,
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text(
                            f"¡Buen día, Prof. {_nombre_docente(perfil, legajo_docente)}!",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=BG_WHITE,
                        ),
                        ft.Text(
                            f"Legajo #{legajo_docente} · {_plural(len(materias_distintas), 'materia', 'materias')} en "
                            f"{_plural(len(cursos_distintos), 'curso', 'cursos')} · "
                            f"{_plural(len(estado['deportes']), 'deporte a cargo', 'deportes a cargo')}",
                            size=13,
                            color=TEAL_LIGHT,
                        ),
                    ],
                ),
                ft.Button(
                    content=ft.Row(
                        spacing=6,
                        controls=[
                            ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=16, color=BG_WHITE),
                            ft.Text(
                                "Nómina de Alumnos",
                                size=13,
                                weight=ft.FontWeight.W_600,
                                color=BG_WHITE,
                            ),
                        ],
                    ),
                    bgcolor=ORANGE,
                    height=38,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)
                    ),
                    on_click=lambda _: page.go("/portal/docente/alumnos"),
                ),
            ],
        ),
    )

    aviso_error = ft.Text(
        "⚠️ Algunos datos del panel no se pudieron cargar desde el backend.",
        size=13,
        weight=ft.FontWeight.W_600,
        color=BADGE_RED_TXT,
        visible=hubo_error,
    )

    # ==================== 4. TARJETAS DE RESUMEN (KPIs REALES) ====================
    def kpi_docente(
        titulo: str, valor: str, subtitulo: str, icono: ft.IconData, bg_icon: str
    ) -> ft.Container:
        return ft.Container(
            expand=True,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=20,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                titulo, size=12, weight=ft.FontWeight.W_600, color=MUTED
                            ),
                            ft.Container(
                                width=34,
                                height=34,
                                bgcolor=bg_icon,
                                border_radius=8,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(icono, size=18, color=TEAL_DARK),
                            ),
                        ],
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                valor,
                                size=26,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                            ft.Text(subtitulo, size=11, color=MUTED),
                        ],
                    ),
                ],
            ),
        )

    kpis_row = ft.Row(
        spacing=16,
        controls=[
            kpi_docente(
                "MATERIAS A CARGO",
                str(len(materias_distintas)),
                _resumen(list(materias_distintas.values())) or "Sin materias asignadas",
                ft.Icons.MENU_BOOK_OUTLINED,
                TEAL_LIGHT,
            ),
            kpi_docente(
                "CURSOS ASIGNADOS",
                str(len(cursos_distintos)),
                _resumen(list(cursos_distintos.values())) or "Sin cursos asignados",
                ft.Icons.PEOPLE_OUTLINE,
                TEAL_LIGHT,
            ),
            kpi_docente(
                "ALUMNOS EN MIS CURSOS",
                str(len(alumnos_de_mis_cursos)),
                f"{alumnos_activos} activos de {len(alumnos_de_mis_cursos)}",
                ft.Icons.SCHOOL_OUTLINED,
                TEAL_LIGHT,
            ),
            kpi_docente(
                "DEPORTES A CARGO",
                str(len(estado["deportes"])),
                _resumen([d.get("nombre") or "-" for d in estado["deportes"]])
                or "Sin deportes asignados",
                ft.Icons.FITNESS_CENTER_OUTLINED,
                TEAL_LIGHT,
            ),
        ],
    )

    # ==================== 5. MIS CURSOS Y MATERIAS (REEMPLAZA CRONOGRAMA FICTICIO) ====================
    def item_materia(a: dict) -> ft.Container:
        id_curso = a.get("id_curso")
        return ft.Container(
            bgcolor=BG_PAGE,
            border_radius=BORDER_RADIUS,
            padding=14,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=14,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=4, height=38, border_radius=2, bgcolor=TEAL
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        f"{a.get('materia') or '-'} — {a.get('curso') or '-'}",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_COLOR,
                                    ),
                                    ft.Text(
                                        f"{a.get('nivel') or 'Sin nivel'}",
                                        size=12,
                                        color=MUTED,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Container(
                        padding=ft.Padding(8, 3, 8, 3),
                        bgcolor=BG_WHITE,
                        border_radius=4,
                        content=ft.Text(
                            _plural(
                                alumnos_por_curso.get(id_curso, 0), "alumno", "alumnos"
                            ),
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=TEAL_DARK,
                        ),
                    ),
                ],
            ),
        )

    contenido_materias = [item_materia(a) for a in estado["asignaciones"]] or [
        ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.MENU_BOOK_OUTLINED, size=18, color=MUTED),
                ft.Text(
                    "No tiene materias asignadas actualmente.", size=13, color=MUTED
                ),
            ],
        )
    ]

    mis_materias_card = ft.Container(
        expand=True,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "Mis Cursos y Materias",
                            size=17,
                            weight=ft.FontWeight.BOLD,
                            color=TEAL_DARK,
                        ),
                        ft.TextButton(
                            "Ver Todas mis Materias",
                            on_click=lambda _: page.go("/portal/docente/materias"),
                        ),
                    ],
                ),
                ft.Column(spacing=10, controls=contenido_materias),
            ],
        ),
    )

    # ==================== 6. MIS GRUPOS DEPORTIVOS (REEMPLAZA COMUNICACIONES FICTICIAS) ====================
    def item_deporte(d: dict) -> ft.Container:
        grupos_del_deporte = grupos_por_deporte.get(d.get("id_deporte"), [])
        total_inscriptos = sum(
            inscriptos_por_grupo.get(g.get("id_grupo"), 0) for g in grupos_del_deporte
        )

        detalle_grupos = [
            ft.Text(
                f"• {g.get('nivel') or 'Sin nivel'}: {g.get('horario') or 'Horario a confirmar'} "
                f"· {_plural(inscriptos_por_grupo.get(g.get('id_grupo'), 0), 'inscripto', 'inscriptos')}",
                size=12,
                color=MUTED,
            )
            for g in grupos_del_deporte
        ] or [ft.Text("Sin grupos registrados.", size=12, color=MUTED)]

        return ft.Container(
            bgcolor=BG_PAGE,
            border_radius=BORDER_RADIUS,
            padding=14,
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                d.get("nombre") or "-",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT_COLOR,
                            ),
                            ft.Container(
                                padding=ft.Padding(8, 3, 8, 3),
                                bgcolor=BG_WHITE,
                                border_radius=4,
                                content=ft.Text(
                                    f"{_plural(len(grupos_del_deporte), 'grupo', 'grupos')} · "
                                    f"{_plural(total_inscriptos, 'inscripto', 'inscriptos')}",
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEAL_DARK,
                                ),
                            ),
                        ],
                    ),
                    *detalle_grupos,
                ],
            ),
        )

    contenido_deportes = [item_deporte(d) for d in estado["deportes"]] or [
        ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.FITNESS_CENTER_OUTLINED, size=18, color=MUTED),
                ft.Text("No tiene deportes a cargo actualmente.", size=13, color=MUTED),
            ],
        )
    ]

    mis_deportes_card = ft.Container(
        width=380,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "Mis Grupos Deportivos",
                            size=17,
                            weight=ft.FontWeight.BOLD,
                            color=TEAL_DARK,
                        ),
                        ft.TextButton(
                            "Ver Deportes",
                            on_click=lambda _: page.go("/portal/docente/deportes"),
                        ),
                    ],
                ),
                ft.Column(spacing=10, controls=contenido_deportes),
                ft.Text(
                    f"Total de inscriptos en sus grupos: {total_inscriptos_deportes}",
                    size=12,
                    color=MUTED,
                ),
            ],
        ),
    )

    fila_inferior = ft.Row(
        spacing=24,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[mis_materias_card, mis_deportes_card],
    )

    return portal_layout(
        page=page,
        titulo="Panel Docente — Mi Actividad",
        active_route="/portal/docente/dashboard",
        rol="Docente",
        usuario_nombre=_nombre_docente(perfil, legajo_docente),
        usuario_sub=f"Legajo #{legajo_docente}",
        content_controls=[
            banner_docente,
            aviso_error,
            kpis_row,
            fila_inferior,
        ],
    )
