import flet as ft
from frontend.app.api_client import api_client
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    CONTROL_HEIGHT,
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


def _plural(cantidad: int, singular: str, plural: str) -> str:
    """Devuelve 'N singular' o 'N plural' según corresponda."""
    return f"{cantidad} {singular if cantidad == 1 else plural}"


def _fecha_corta(iso: str | None) -> str:
    """Convierte una fecha ISO del backend (aaaa-mm-dd) en dd/mm/aaaa."""
    if not iso or len(iso) < 10:
        return "-"
    return f"{iso[8:10]}/{iso[5:7]}/{iso[0:4]}"


def _nombre_docente(perfil: dict | None, legajo: int | None) -> str:
    """Extrae el nombre legible del docente desde 'vinculacion' (ej: 'Docente: Gómez, Laura (#2001)')."""
    vinculo = (perfil or {}).get("vinculacion") or ""
    if ":" in vinculo:
        vinculo = vinculo.split(":", 1)[1]
    vinculo = vinculo.split("(#", 1)[0].strip()
    return vinculo or (f"Docente #{legajo}" if legajo else "Docente")


async def get_docente_deportes_view(page: ft.Page) -> ft.Row:
    """Deportes y grupos a cargo del docente, con inscriptos reales de la API."""

    # ==================== 0. IDENTIDAD DEL DOCENTE ====================
    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
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
                        "Inicie sesión nuevamente para consultar sus deportes a cargo.",
                        size=13,
                        color=MUTED,
                    ),
                ],
            ),
        )

    if not legajo_docente:
        return portal_layout(
            page=page,
            titulo="Deportes y Actividades a Cargo",
            active_route="/portal/docente/deportes",
            rol="Docente",
            usuario_nombre="Docente",
            usuario_sub="Sesión no identificada",
            content_controls=[tarjeta_sin_identidad()],
        )

    # ==================== 1. CARGA DE DATOS REALES ====================
    estado: dict = {
        "deportes": [],
        "grupos": [],
        "inscripciones": [],
        "alumnos": [],
        "cursos": [],
    }
    hubo_error = False

    try:
        deportes = await api_client.get_deportes()
    except Exception:
        deportes = []
        hubo_error = True
    estado["deportes"] = [
        d for d in deportes if d.get("legajo_profesor_responsable") == legajo_docente
    ]

    try:
        grupos = await api_client.get_grupos_deporte()
    except Exception:
        grupos = []
        hubo_error = True
    ids_deportes = {d.get("id_deporte") for d in estado["deportes"]}
    estado["grupos"] = [g for g in grupos if g.get("id_deporte") in ids_deportes]

    try:
        inscripciones = await api_client.get_inscripciones_deporte()
    except Exception:
        inscripciones = []
        hubo_error = True
    ids_grupos = {g.get("id_grupo") for g in estado["grupos"]}
    estado["inscripciones"] = [i for i in inscripciones if i.get("id_grupo") in ids_grupos]

    try:
        estado["alumnos"] = await api_client.get_alumnos(solo_activos=False)
    except Exception:
        estado["alumnos"] = []
        hubo_error = True

    try:
        estado["cursos"] = await api_client.get_cursos()
    except Exception:
        estado["cursos"] = []
        hubo_error = True

    nombre_curso = {
        c.get("id_curso"): c.get("nombre") or f"Curso {c.get('id_curso')}" for c in estado["cursos"]
    }
    curso_por_legajo = {a.get("legajo"): a.get("id_curso") for a in estado["alumnos"]}
    grupo_por_id = {g.get("id_grupo"): g for g in estado["grupos"]}

    grupos_por_deporte: dict = {}
    for grupo in estado["grupos"]:
        grupos_por_deporte.setdefault(grupo.get("id_deporte"), []).append(grupo)

    inscriptos_por_grupo: dict = {}
    for inscripcion in estado["inscripciones"]:
        id_grupo = inscripcion.get("id_grupo")
        inscriptos_por_grupo[id_grupo] = inscriptos_por_grupo.get(id_grupo, 0) + 1

    # ==================== 2. TARJETAS DE DEPORTES Y SUS GRUPOS ====================
    cards_holder = ft.Container()

    def tarjeta_deporte(d: dict) -> ft.Container:
        grupos_del_deporte = grupos_por_deporte.get(d.get("id_deporte"), [])
        total_inscriptos = sum(
            inscriptos_por_grupo.get(g.get("id_grupo"), 0) for g in grupos_del_deporte
        )

        detalle_grupos = [
            ft.Container(
                bgcolor=BG_PAGE,
                border_radius=BORDER_RADIUS,
                padding=14,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(ft.Icons.GROUPS_OUTLINED, size=18, color=TEAL),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(
                                            f"{g.get('nivel') or 'Sin nivel'} — Grupo #{g.get('id_grupo', '-')}",
                                            size=13,
                                            weight=ft.FontWeight.W_600,
                                            color=TEXT_COLOR,
                                        ),
                                        ft.Text(
                                            g.get("horario") or "Horario a confirmar",
                                            size=12,
                                            color=MUTED,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        ft.Container(
                            padding=ft.Padding(8, 3, 8, 3),
                            bgcolor=TEAL_LIGHT,
                            border_radius=4,
                            content=ft.Text(
                                _plural(inscriptos_por_grupo.get(g.get("id_grupo"), 0), "inscripto", "inscriptos"),
                                size=11,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                        ),
                    ],
                ),
            )
            for g in grupos_del_deporte
        ] or [ft.Text("Sin grupos registrados para este deporte.", size=13, color=MUTED)]

        return ft.Container(
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=24,
            content=ft.Column(
                spacing=14,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=12,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Container(
                                        width=40,
                                        height=40,
                                        bgcolor=TEAL_LIGHT,
                                        border_radius=20,
                                        alignment=ft.Alignment(0, 0),
                                        content=ft.Icon(ft.Icons.SPORTS_SOCCER, size=20, color=TEAL_DARK),
                                    ),
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(
                                                d.get("nombre") or "-",
                                                size=17,
                                                weight=ft.FontWeight.BOLD,
                                                color=TEAL_DARK,
                                            ),
                                            ft.Text("Profesor responsable a cargo", size=13, color=MUTED),
                                        ],
                                    ),
                                ],
                            ),
                            ft.Container(
                                padding=ft.Padding(8, 3, 8, 3),
                                bgcolor=TEAL_LIGHT,
                                border_radius=4,
                                content=ft.Text(
                                    _plural(len(grupos_del_deporte), "grupo", "grupos"),
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEAL_DARK,
                                ),
                            ),
                        ],
                    ),
                    ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                    ft.Row(
                        spacing=32,
                        controls=[
                            ft.Column(
                                [
                                    ft.Text("Grupos Registrados", size=11, color=MUTED),
                                    ft.Text(
                                        str(len(grupos_del_deporte)),
                                        size=13,
                                        weight=ft.FontWeight.W_600,
                                        color=TEXT_COLOR,
                                    ),
                                ],
                                spacing=3,
                            ),
                            ft.Column(
                                [
                                    ft.Text("Inscriptos Totales", size=11, color=MUTED),
                                    ft.Text(
                                        str(total_inscriptos),
                                        size=13,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEAL_DARK,
                                    ),
                                ],
                                spacing=3,
                            ),
                        ],
                    ),
                    ft.Column(spacing=10, controls=detalle_grupos),
                ],
            ),
        )

    def tarjeta_sin_deportes() -> ft.Container:
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
                    ft.Icon(ft.Icons.FITNESS_CENTER_OUTLINED, size=44, color=MUTED),
                    ft.Text(
                        "No tiene deportes a cargo.",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=TEAL_DARK,
                    ),
                    ft.Text(
                        "La Dirección aún no registró deportes con su legajo como responsable.",
                        size=13,
                        color=MUTED,
                    ),
                ],
            ),
        )

    # ==================== 3. NÓMINA DE INSCRIPTOS ====================
    columnas_inscriptos = [
        ("Legajo", 110, False),
        ("Estudiante", 220, False),
        ("Curso", 150, False),
        ("Deporte", 160, False),
        ("Nivel del Grupo", 150, False),
        ("Inscripción", 130, False),
    ]

    header_table = create_table_header(columnas_inscriptos)
    table_holder = ft.Container()
    pagination_holder = ft.Container()

    def inscripto_row(item: dict) -> ft.Container:
        legajo_alumno = item.get("legajo_alumno")
        nombre = (item.get("alumno") or f"Alumno #{legajo_alumno}").split(" (#", 1)[0].strip()
        curso = nombre_curso.get(curso_por_legajo.get(legajo_alumno), "-")
        nivel_grupo = (grupo_por_id.get(item.get("id_grupo")) or {}).get("nivel") or "-"

        return ft.Container(
            height=50,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=110,
                        content=ft.Text(
                            f"#{legajo_alumno if legajo_alumno is not None else '-'}",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        width=220,
                        content=ft.Text(
                            nombre,
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(width=150, content=ft.Text(curso, size=14, color=MUTED)),
                    ft.Container(
                        width=160,
                        content=ft.Text(item.get("deporte") or "-", size=13, color=TEAL),
                    ),
                    ft.Container(width=150, content=ft.Text(nivel_grupo, size=13, color=MUTED)),
                    ft.Container(
                        width=130,
                        content=ft.Text(_fecha_corta(item.get("fecha_inscripcion")), size=13, color=TEXT_COLOR),
                    ),
                ],
            ),
        )

    nomina_titulo = ft.Text("Nómina de Deportistas Inscriptos", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK)

    def render():
        if estado["deportes"]:
            cards_holder.content = ft.Column(
                spacing=16,
                controls=[tarjeta_deporte(d) for d in estado["deportes"]],
            )
        else:
            cards_holder.content = tarjeta_sin_deportes()

        if estado["inscripciones"]:
            mensaje_vacio = "No hay inscriptos que coincidan con los filtros."
        else:
            mensaje_vacio = "No hay alumnos inscriptos en los grupos de sus deportes."

        table_holder.content = create_table_container(
            header=header_table,
            rows=[inscripto_row(i) for i in estado["inscripciones"]]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(mensaje_vacio, size=13, color=MUTED),
                )
            ],
            min_width=920,
        )
        pagination_holder.content = create_pagination_bar(
            texto_info=f"Mostrando {len(estado['inscripciones'])} inscriptos en sus grupos",
            pagina_actual=1,
            total_paginas=max(1, (len(estado["inscripciones"]) + 9) // 10),
        )

        hay_deportes = bool(estado["deportes"])
        nomina_titulo.visible = hay_deportes
        table_holder.visible = hay_deportes
        pagination_holder.visible = hay_deportes
        acciones_bar_holder.content = build_acciones_bar()

        try:
            page.update()
        except Exception:
            pass

    # ==================== 4. BARRA DE ACCIÓN ====================
    aviso_error = ft.Text(
        "⚠️ Algunos datos de deportes no se pudieron cargar desde el backend." if hubo_error else "",
        size=13,
        weight=ft.FontWeight.W_600,
        color=BADGE_RED_TXT,
        visible=hubo_error,
    )

    def mostrar_error(mensaje: str):
        aviso_error.value = f"⚠️ {mensaje}"
        aviso_error.visible = True
        try:
            page.update()
        except Exception:
            pass

    btn_actualizar = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SYNC, size=16, color=BG_WHITE),
                ft.Text("Actualizar", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
            ],
        ),
        bgcolor=TEAL,
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            padding=ft.Padding(24, 12, 24, 12),
        ),
    )

    acciones_bar_holder = ft.Container()

    def build_acciones_bar() -> ft.Row:
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    f"Legajo #{legajo_docente} · "
                    f"{_plural(len(estado['deportes']), 'deporte a cargo', 'deportes a cargo')} · "
                    f"{_plural(len(estado['grupos']), 'grupo', 'grupos')} y "
                    f"{_plural(len(estado['inscripciones']), 'inscripto', 'inscriptos')} en total",
                    size=14,
                    color=MUTED,
                ),
                btn_actualizar,
            ],
        )

    async def recargar(e=None):
        try:
            deportes = await api_client.get_deportes()
            estado["deportes"] = [
                d for d in deportes if d.get("legajo_profesor_responsable") == legajo_docente
            ]
            ids_deportes_actuales = {d.get("id_deporte") for d in estado["deportes"]}

            grupos = await api_client.get_grupos_deporte()
            estado["grupos"] = [g for g in grupos if g.get("id_deporte") in ids_deportes_actuales]
            ids_grupos_actuales = {g.get("id_grupo") for g in estado["grupos"]}

            inscripciones = await api_client.get_inscripciones_deporte()
            estado["inscripciones"] = [i for i in inscripciones if i.get("id_grupo") in ids_grupos_actuales]

            estado["alumnos"] = await api_client.get_alumnos(solo_activos=False)
            estado["cursos"] = await api_client.get_cursos()

            nombre_curso.clear()
            nombre_curso.update(
                {
                    c.get("id_curso"): c.get("nombre") or f"Curso {c.get('id_curso')}"
                    for c in estado["cursos"]
                }
            )
            curso_por_legajo.clear()
            curso_por_legajo.update({a.get("legajo"): a.get("id_curso") for a in estado["alumnos"]})
            grupo_por_id.clear()
            grupo_por_id.update({g.get("id_grupo"): g for g in estado["grupos"]})
            grupos_por_deporte.clear()
            for grupo in estado["grupos"]:
                grupos_por_deporte.setdefault(grupo.get("id_deporte"), []).append(grupo)
            inscriptos_por_grupo.clear()
            for inscripcion in estado["inscripciones"]:
                id_grupo = inscripcion.get("id_grupo")
                inscriptos_por_grupo[id_grupo] = inscriptos_por_grupo.get(id_grupo, 0) + 1

            aviso_error.visible = False
        except Exception as err:
            mostrar_error(f"No se pudieron refrescar los deportes a cargo: {err}")
        render()

    btn_actualizar.on_click = recargar

    # ==================== 5. TARJETA INFORMATIVA ====================
    info_card = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
        padding=16,
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE, size=20, color=TEAL),
                ft.Text(
                    "Los grupos, horarios e inscripciones se administran desde el módulo de Deportes de la Dirección.",
                    size=13,
                    weight=ft.FontWeight.W_500,
                    color=TEAL_DARK,
                ),
            ],
        ),
    )

    render()

    # ==================== 6. RETORNO CON PORTAL_LAYOUT ====================
    return portal_layout(
        page=page,
        titulo="Deportes y Actividades a Cargo",
        active_route="/portal/docente/deportes",
        rol="Docente",
        usuario_nombre=_nombre_docente(perfil, legajo_docente),
        usuario_sub=f"Legajo #{legajo_docente}",
        content_controls=[
            info_card,
            acciones_bar_holder,
            aviso_error,
            cards_holder,
            nomina_titulo,
            table_holder,
            pagination_holder,
        ],
    )
