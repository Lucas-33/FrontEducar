import flet as ft

from frontend.app.api_client import api_client
from frontend.app.components.constants import (
    BADGE_GREEN_BG,
    BADGE_GREEN_TXT,
    BADGE_RED_TXT,
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    MUTED,
    ONLINE_GREEN,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.portal_layout import portal_layout

# Icono representativo por disciplina deportiva registrada en el backend
ICONOS_DEPORTE = {
    "fútbol": ft.Icons.SPORTS_SOCCER,
    "vóleibol": ft.Icons.SPORTS_VOLLEYBALL,
    "basquetbol": ft.Icons.SPORTS_BASKETBALL,
    "básquetbol": ft.Icons.SPORTS_BASKETBALL,
    "handball": ft.Icons.SPORTS_HANDBALL,
    "natación": ft.Icons.POOL,
    "atletismo": ft.Icons.DIRECTIONS_RUN,
}


def _fecha_corta(iso: str | None) -> str:
    """Convierte un ISO timestamp del backend en dd/mm/aaaa."""
    if not iso or len(iso) < 10:
        return "-"
    return f"{iso[8:10]}/{iso[5:7]}/{iso[0:4]}"


def _icono_deporte(nombre: str | None) -> ft.IconData:
    """Devuelve un icono existente para la disciplina, o uno genérico."""
    return ICONOS_DEPORTE.get(
        (nombre or "").strip().lower(), ft.Icons.FITNESS_CENTER_OUTLINED
    )


def _estado_vacio(titulo: str, mensaje: str) -> ft.Container:
    """Tarjeta de estado vacío para cuando el alumno no puede identificarse."""
    return ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=40,
        content=ft.Column(
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=56,
                    height=56,
                    bgcolor=TEAL_LIGHT,
                    border_radius=28,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(
                        ft.Icons.PERSON_OFF_OUTLINED, size=26, color=TEAL_DARK
                    ),
                ),
                ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Text(mensaje, size=14, color=MUTED, text_align=ft.TextAlign.CENTER),
            ],
        ),
    )


async def get_alumno_deportes_view(page: ft.Page) -> ft.Row:
    """Retorna los grupos deportivos disponibles y las inscripciones reales del alumno."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    try:
        perfil = await api_client.get_mi_perfil()
    except Exception:
        perfil = None

    legajo = (perfil or {}).get("legajo_alumno")

    def construir_layout(
        usuario_nombre: str, usuario_sub: str, controles: list[ft.Control]
    ) -> ft.Row:
        return portal_layout(
            page=page,
            titulo="Mis Deportes y Actividades Físicas",
            active_route="/portal/alumno/deportes",
            rol="Alumno",
            usuario_nombre=usuario_nombre,
            usuario_sub=usuario_sub,
            content_controls=controles,
        )

    if perfil is None or legajo is None:
        return construir_layout(
            "Estudiante",
            "Sesión no identificada",
            [
                _estado_vacio(
                    "Alumno no identificado",
                    "No se pudo identificar al alumno. Inicie sesión nuevamente.",
                )
            ],
        )

    # ==================== 1. DATOS REALES DEL ALUMNO ====================
    estado: dict = {"alumno": None, "nivel": None, "grupos": [], "inscripciones": []}
    errores: list[str] = []

    try:
        alumnos = await api_client.get_alumnos(solo_activos=False)
        estado["alumno"] = next((a for a in alumnos if a.get("legajo") == legajo), None)
    except Exception:
        errores.append("datos del alumno")

    try:
        cursos = await api_client.get_cursos()
    except Exception:
        cursos = []
        errores.append("cursos")

    try:
        niveles = await api_client.get_niveles()
    except Exception:
        niveles = []

    try:
        grupos = await api_client.get_grupos_deporte()
    except Exception:
        grupos = []
        errores.append("grupos deportivos")

    try:
        inscripciones = await api_client.get_inscripciones_deporte()
        estado["inscripciones"] = [
            i for i in inscripciones if i.get("legajo_alumno") == legajo
        ]
    except Exception:
        errores.append("inscripciones deportivas")

    alumno = estado["alumno"]
    if alumno is None:
        return construir_layout(
            "Estudiante",
            f"Legajo #{legajo}",
            [
                _estado_vacio(
                    "Registro de alumno no encontrado",
                    f"No se encontró el legajo #{legajo} en el padrón de alumnos. "
                    "Verifique su matrícula con la Secretaría del colegio.",
                )
            ],
        )

    curso = next(
        (c for c in cursos if c.get("id_curso") == alumno.get("id_curso")), None
    )
    estado["nivel"] = next(
        (n for n in niveles if curso and n.get("id_nivel") == curso.get("id_nivel")),
        None,
    )

    nombre_curso = curso.get("nombre") if curso else "Curso sin asignar"
    nombre_nivel = estado["nivel"].get("nombre") if estado["nivel"] else None
    nombre_completo = (
        f"{alumno.get('nombre', '')} {alumno.get('apellido', '')}".strip() or "Alumno"
    )

    ids_inscriptos = {i.get("id_grupo") for i in estado["inscripciones"]}
    estado["grupos"] = sorted(
        [
            g
            for g in grupos
            if estado["nivel"] and g.get("id_nivel") == estado["nivel"].get("id_nivel")
        ],
        key=lambda g: (
            0 if g.get("id_grupo") in ids_inscriptos else 1,
            g.get("id_grupo", 0),
        ),
    )

    # ==================== 2. AVISO DE ERROR DE CARGA ====================
    aviso_error = ft.Text(
        f"⚠️ No se pudieron cargar: {', '.join(errores)}." if errores else "",
        size=13,
        weight=ft.FontWeight.W_600,
        color=BADGE_RED_TXT,
        visible=bool(errores),
    )

    # ==================== 3. TARJETAS DE GRUPOS DISPONIBLES ====================
    def badge_grupo(inscripto: bool) -> ft.Container:
        if inscripto:
            return ft.Container(
                padding=ft.Padding(8, 4, 8, 4),
                bgcolor=BADGE_GREEN_BG,
                border_radius=4,
                content=ft.Text(
                    "Inscripto",
                    size=12,
                    weight=ft.FontWeight.W_600,
                    color=BADGE_GREEN_TXT,
                ),
            )
        return ft.Container(
            padding=ft.Padding(8, 4, 8, 4),
            bgcolor=TEAL_LIGHT,
            border_radius=4,
            content=ft.Text(
                "Disponible", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK
            ),
        )

    def tarjeta_grupo(grupo: dict) -> ft.Container:
        inscripto = grupo.get("id_grupo") in ids_inscriptos
        inscripcion = next(
            (
                i
                for i in estado["inscripciones"]
                if i.get("id_grupo") == grupo.get("id_grupo")
            ),
            None,
        )

        if inscripto:
            pie = ft.Container(
                bgcolor="#EBFEE6",
                border_radius=BORDER_RADIUS,
                padding=12,
                content=ft.Row(
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=16, color=ONLINE_GREEN),
                        ft.Text(
                            f"Inscripción registrada: {_fecha_corta((inscripcion or {}).get('fecha_inscripcion'))}",
                            size=12,
                            weight=ft.FontWeight.W_600,
                            color=ONLINE_GREEN,
                        ),
                    ],
                ),
            )
        else:
            pie = ft.Container(
                bgcolor=BG_PAGE,
                border_radius=BORDER_RADIUS,
                padding=12,
                content=ft.Row(
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=MUTED),
                        ft.Text(
                            "Sin inscripción registrada en este grupo.",
                            size=12,
                            color=MUTED,
                        ),
                    ],
                ),
            )

        return ft.Container(
            width=430,
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
                            ft.Row(
                                spacing=12,
                                controls=[
                                    ft.Container(
                                        width=44,
                                        height=44,
                                        bgcolor=TEAL_LIGHT,
                                        border_radius=22,
                                        alignment=ft.Alignment(0, 0),
                                        content=ft.Icon(
                                            _icono_deporte(grupo.get("deporte")),
                                            size=22,
                                            color=TEAL_DARK,
                                        ),
                                    ),
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(
                                                grupo.get("deporte", "-"),
                                                size=18,
                                                weight=ft.FontWeight.BOLD,
                                                color=TEAL_DARK,
                                            ),
                                            ft.Text(
                                                f"Nivel {grupo.get('nivel', '-')} · Grupo #{grupo.get('id_grupo')}",
                                                size=13,
                                                color=MUTED,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            badge_grupo(inscripto),
                        ],
                    ),
                    ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                    ft.Row(
                        spacing=20,
                        controls=[
                            ft.Column(
                                [
                                    ft.Text("Días y Horarios", size=11, color=MUTED),
                                    ft.Text(
                                        grupo.get("horario", "-"),
                                        size=13,
                                        weight=ft.FontWeight.W_600,
                                        color=TEXT_COLOR,
                                    ),
                                ],
                                spacing=3,
                            ),
                            ft.Column(
                                [
                                    ft.Text("Nivel Educativo", size=11, color=MUTED),
                                    ft.Text(
                                        grupo.get("nivel", "-"),
                                        size=13,
                                        weight=ft.FontWeight.W_600,
                                        color=TEXT_COLOR,
                                    ),
                                ],
                                spacing=3,
                            ),
                        ],
                    ),
                    pie,
                ],
            ),
        )

    if estado["grupos"]:
        seccion_grupos: ft.Control = ft.Row(
            spacing=20,
            run_spacing=20,
            wrap=True,
            controls=[tarjeta_grupo(g) for g in estado["grupos"]],
        )
    elif nombre_nivel:
        seccion_grupos = ft.Container(
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=20,
            alignment=ft.Alignment(0, 0),
            content=ft.Text(
                f"No hay grupos deportivos cargados para el nivel {nombre_nivel}.",
                size=13,
                color=MUTED,
            ),
        )
    else:
        seccion_grupos = ft.Container(
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=20,
            alignment=ft.Alignment(0, 0),
            content=ft.Text(
                "No se pudo determinar el nivel del alumno para listar los grupos deportivos disponibles.",
                size=13,
                color=MUTED,
            ),
        )

    # ==================== 4. MIS INSCRIPCIONES ACTUALES ====================
    def fila_inscripcion(inscripcion: dict) -> ft.Container:
        return ft.Container(
            bgcolor=BG_PAGE,
            border_radius=BORDER_RADIUS,
            padding=14,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.Container(
                                width=4,
                                height=36,
                                border_radius=2,
                                bgcolor=ONLINE_GREEN,
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        inscripcion.get("deporte", "-"),
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEAL_DARK,
                                    ),
                                    ft.Text(
                                        inscripcion.get("alumno", f"Legajo #{legajo}"),
                                        size=12,
                                        color=MUTED,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Container(
                        padding=ft.Padding(8, 4, 8, 4),
                        bgcolor=BG_WHITE,
                        border_radius=4,
                        content=ft.Text(
                            f"Alta {_fecha_corta(inscripcion.get('fecha_inscripcion'))}",
                            size=12,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_COLOR,
                        ),
                    ),
                ],
            ),
        )

    inscripciones_card = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text(
                    "Mis Inscripciones Actuales",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
                ft.Column(
                    spacing=10,
                    controls=[fila_inscripcion(i) for i in estado["inscripciones"]]
                    or [
                        ft.Text(
                            "No registrás inscripciones deportivas por el momento.",
                            size=13,
                            color=MUTED,
                        )
                    ],
                ),
            ],
        ),
    )

    # ==================== 5. AVISO INFORMATIVO REAL ====================
    if estado["inscripciones"]:
        nombres = ", ".join(
            sorted({i.get("deporte", "-") for i in estado["inscripciones"]})
        )
        texto_regla = f"Estás inscripto en {len(estado['inscripciones'])} disciplina(s): {nombres}."
    else:
        texto_regla = "No registrás inscripciones deportivas por el momento."
    if nombre_nivel:
        texto_regla += f" Grupos disponibles para el Nivel {nombre_nivel}: {len(estado['grupos'])}."

    regla_info = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
        padding=16,
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE, size=20, color=TEAL),
                ft.Text(
                    texto_regla,
                    size=13,
                    color=TEAL_DARK,
                    weight=ft.FontWeight.W_500,
                ),
            ],
        ),
    )

    holder_contenido = ft.Column(spacing=24, controls=[])

    def render():
        holder_contenido.controls = [regla_info, inscripciones_card, seccion_grupos]
        try:
            page.update()
        except Exception:
            pass

    render()

    # ==================== 6. RETORNO CON PORTAL_LAYOUT ====================
    return construir_layout(
        nombre_completo,
        f"Legajo #{alumno.get('legajo')} · {nombre_curso}",
        [aviso_error, holder_contenido],
    )
