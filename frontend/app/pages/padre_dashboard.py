import flet as ft

from frontend.app.api_client import api_client
from frontend.app.components.constants import (
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
from frontend.app.components.form_controls import status_badge
from frontend.app.components.portal_layout import portal_layout


def _nombre_completo(persona: dict) -> str:
    """Devuelve 'Nombre Apellido' a partir del registro real del alumno."""
    nombre = (persona.get("nombre") or "").strip()
    apellido = (persona.get("apellido") or "").strip()
    return f"{nombre} {apellido}".strip() or "Alumno sin nombre"


def _nombre_tutor(perfil: dict | None) -> str:
    """Obtiene un nombre legible del tutor desde la vinculación del perfil autenticado."""
    if not perfil:
        return "Tutor"
    vinculacion = (perfil.get("vinculacion") or "").strip()
    if ":" in vinculacion:
        posible = vinculacion.split(":", 1)[1].strip()
        if posible:
            return posible
    return vinculacion or perfil.get("username", "Tutor")


def _texto_seguro(valor) -> str:
    """Normaliza valores nulos o vacíos para mostrarlos en la interfaz."""
    if valor is None:
        return "-"
    texto = str(valor).strip()
    return texto or "-"


def _estado_vacio(
    mensaje: str, icono: ft.IconData = ft.Icons.INFO_OUTLINE
) -> ft.Container:
    """Tarjeta de estado vacío o error, manteniendo el layout y sin datos ficticios."""
    return ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=40,
        alignment=ft.Alignment(0, 0),
        content=ft.Column(
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(icono, size=36, color=MUTED),
                ft.Text(mensaje, size=14, color=MUTED, text_align=ft.TextAlign.CENTER),
            ],
        ),
    )


async def get_padre_dashboard_view(page: ft.Page) -> ft.Row:
    """Panel principal del padre/tutor con selector interactivo y datos reales de sus hijos."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and api_client.token != token_almacenado:
        api_client.set_token(token_almacenado)

    try:
        perfil = await api_client.get_mi_perfil()
    except Exception:
        perfil = None

    nombre_tutor = _nombre_tutor(perfil)

    def layout(controles: list[ft.Control]) -> ft.Row:
        return portal_layout(
            page=page,
            titulo="Panel de Familias — Información del Alumno",
            active_route="/portal/padre/dashboard",
            rol="Padre",
            usuario_nombre=nombre_tutor,
            usuario_sub="Tutor responsable",
            content_controls=controles,
        )

    id_padre = (perfil or {}).get("id_padre")
    if not perfil or not id_padre:
        return layout(
            [
                _estado_vacio(
                    "No se pudo identificar al tutor. Inicie sesión nuevamente.",
                    ft.Icons.PERSON_OFF_OUTLINED,
                )
            ]
        )

    estado: dict = {
        "hijos": [],
        "cursos": [],
        "niveles": [],
        "asignaciones": [],
        "grupos": [],
        "inscripciones_deporte": [],
        "inscripciones_transporte": [],
        "inscripciones_comedor": [],
        "idx": 0,
    }

    try:
        estado["hijos"] = await api_client.get_hijos(id_padre)
    except Exception:
        estado["hijos"] = []

    if not estado["hijos"]:
        return layout(
            [
                _estado_vacio(
                    "No hay alumnos vinculados a esta cuenta.",
                    ft.Icons.FAMILY_RESTROOM_OUTLINED,
                )
            ]
        )

    # ==================== 1. DATOS REALES COMPLEMENTARIOS ====================
    cargadores = (
        ("cursos", api_client.get_cursos),
        ("niveles", api_client.get_niveles),
        ("asignaciones", api_client.get_asignaciones),
        ("grupos", api_client.get_grupos_deporte),
        ("inscripciones_deporte", api_client.get_inscripciones_deporte),
        ("inscripciones_transporte", api_client.get_inscripciones_transporte),
        ("inscripciones_comedor", api_client.get_inscripciones_comedor),
    )
    for clave, cargador in cargadores:
        try:
            estado[clave] = await cargador()
        except Exception:
            estado[clave] = []

    cursos_por_id = {c.get("id_curso"): c for c in estado["cursos"]}
    niveles_por_id = {n.get("id_nivel"): n for n in estado["niveles"]}

    def curso_de(hijo: dict) -> dict | None:
        return cursos_por_id.get(hijo.get("id_curso"))

    def nivel_de(hijo: dict) -> dict | None:
        curso = curso_de(hijo)
        return niveles_por_id.get(curso.get("id_nivel")) if curso else None

    def materias_de(id_curso) -> list[dict]:
        return [a for a in estado["asignaciones"] if a.get("id_curso") == id_curso]

    def deportes_de(legajo) -> list[dict]:
        return [
            i
            for i in estado["inscripciones_deporte"]
            if i.get("legajo_alumno") == legajo
        ]

    def transporte_de(legajo) -> dict | None:
        for i in estado["inscripciones_transporte"]:
            if i.get("legajo_alumno") == legajo:
                return i
        return None

    def comedor_de(legajo) -> dict | None:
        for i in estado["inscripciones_comedor"]:
            if i.get("legajo_alumno") == legajo:
                return i
        return None

    def descripcion_alumno(hijo: dict) -> str:
        curso = curso_de(hijo)
        nivel = nivel_de(hijo)
        curso_nombre = curso.get("nombre") if curso else "Curso no disponible"
        nivel_nombre = nivel.get("nombre") if nivel else "-"
        return f"{nivel_nombre} · {curso_nombre} · Legajo #{hijo.get('legajo', '-')}"

    # ==================== 2. BANNER DEL TUTOR ====================
    vinculacion = (perfil.get("vinculacion") or f"Tutor: {nombre_tutor}").strip()
    cantidad_hijos = len(estado["hijos"])
    banner_tutor = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
        padding=16,
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.FAMILY_RESTROOM_OUTLINED, size=20, color=TEAL),
                ft.Text(
                    f"{vinculacion} · Alumnos vinculados: {cantidad_hijos}",
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=TEAL_DARK,
                ),
            ],
        ),
    )

    # ==================== 3. DETALLE REACTIVO DEL HIJO SELECCIONADO ====================
    detalle_container = ft.Column(spacing=20)

    def dato(titulo: str, valor: str, col: int = 3) -> ft.Container:
        return ft.Container(
            col={"sm": 6, "md": col},
            content=ft.Column(
                spacing=3,
                controls=[
                    ft.Text(titulo, size=11, color=MUTED),
                    ft.Text(
                        valor, size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR
                    ),
                ],
            ),
        )

    def tarjeta_resumen(
        titulo: str,
        icono: ft.IconData,
        color_icono: str,
        cuerpo: list[ft.Control],
        ruta_texto: str,
        ruta: str,
    ) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 3},
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
                                titulo,
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                            ft.Icon(icono, size=18, color=color_icono),
                        ],
                    ),
                    *cuerpo,
                    ft.TextButton(ruta_texto, on_click=lambda _: page.go(ruta)),
                ],
            ),
        )

    def etiqueta(texto: str) -> ft.Container:
        return ft.Container(
            bgcolor=TEAL_LIGHT,
            border_radius=6,
            padding=8,
            content=ft.Text(
                f"• {texto}", size=13, weight=ft.FontWeight.W_500, color=TEAL_DARK
            ),
        )

    def render_detalle():
        hijo = estado["hijos"][estado["idx"]]
        curso = curso_de(hijo)
        nivel = nivel_de(hijo)
        legajo = hijo.get("legajo")
        materias = materias_de(hijo.get("id_curso"))
        docentes = {a.get("legajo_profesor") for a in materias}
        deportes = deportes_de(legajo)
        transporte = transporte_de(legajo)
        comedor = comedor_de(legajo)

        curso_nombre = curso.get("nombre") if curso else "-"
        nivel_nombre = nivel.get("nombre") if nivel else "-"
        estado_legible = (
            hijo.get("estado_alumno") or ""
        ).strip().capitalize() or "Sin estado"
        iniciales = (
            f"{(hijo.get('nombre') or ' ')[0]}{(hijo.get('apellido') or ' ')[0]}"
        ).upper().strip() or "A"

        tarjeta_datos = ft.Container(
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
                                        width=48,
                                        height=48,
                                        bgcolor=TEAL_LIGHT,
                                        border_radius=24,
                                        alignment=ft.Alignment(0, 0),
                                        content=ft.Text(
                                            iniciales,
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                            color=TEAL_DARK,
                                        ),
                                    ),
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(
                                                _nombre_completo(hijo),
                                                size=18,
                                                weight=ft.FontWeight.BOLD,
                                                color=TEAL_DARK,
                                            ),
                                            ft.Text(
                                                descripcion_alumno(hijo),
                                                size=13,
                                                color=MUTED,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            status_badge(estado_legible),
                        ],
                    ),
                    ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                    ft.ResponsiveRow(
                        columns=12,
                        spacing=16,
                        run_spacing=14,
                        controls=[
                            dato("Legajo", f"#{_texto_seguro(legajo)}"),
                            dato("D.N.I.", _texto_seguro(hijo.get("dni"))),
                            dato("Curso actual", curso_nombre),
                            dato("Nivel educativo", nivel_nombre),
                            dato("Domicilio", _texto_seguro(hijo.get("domicilio"))),
                            dato("Teléfono", _texto_seguro(hijo.get("telefono"))),
                            dato(
                                "Correo electrónico",
                                _texto_seguro(hijo.get("correo_electronico")),
                            ),
                            dato(
                                "Materias asignadas",
                                str(len({a.get("id_materia") for a in materias}))
                                if materias
                                else "-",
                            ),
                        ],
                    ),
                ],
            ),
        )

        cuerpo_materias = (
            [
                ft.Text(
                    f"{len({a.get('id_materia') for a in materias})} materias · {len(docentes)} docentes",
                    size=13,
                    weight=ft.FontWeight.W_600,
                    color=TEXT_COLOR,
                ),
                ft.Text(
                    "Nómina de asignaturas del curso actual del alumno.",
                    size=12,
                    color=MUTED,
                ),
            ]
            if materias
            else [
                ft.Text(
                    "Sin materias asignadas para el curso actual.", size=13, color=MUTED
                )
            ]
        )

        cuerpo_deportes = (
            [etiqueta(i.get("deporte", "Deporte")) for i in deportes]
            if deportes
            else [ft.Text("Sin deportes inscriptos.", size=13, color=MUTED)]
        )

        cuerpo_comedor = (
            [
                ft.Row(
                    spacing=8,
                    controls=[
                        status_badge((comedor.get("estado") or "").capitalize()),
                        ft.Text(
                            f"Alta: {_texto_seguro(comedor.get('fecha_alta'))}",
                            size=12,
                            color=MUTED,
                        ),
                    ],
                ),
                ft.Text(
                    "Servicio de comedor del alumno según registro institucional.",
                    size=12,
                    color=MUTED,
                ),
            ]
            if comedor
            else [
                ft.Text("Sin inscripción registrada al comedor.", size=13, color=MUTED)
            ]
        )

        cuerpo_transporte = (
            [
                ft.Text(
                    _texto_seguro(transporte.get("recorrido")),
                    size=13,
                    weight=ft.FontWeight.W_600,
                    color=TEXT_COLOR,
                ),
                ft.Row(
                    spacing=8,
                    controls=[
                        status_badge((transporte.get("estado") or "").capitalize()),
                        ft.Text(
                            f"Alta: {_texto_seguro(transporte.get('fecha_alta'))}",
                            size=12,
                            color=MUTED,
                        ),
                    ],
                ),
            ]
            if transporte
            else [
                ft.Text(
                    "Sin inscripción registrada al transporte.", size=13, color=MUTED
                )
            ]
        )

        detalle_container.controls = [
            tarjeta_datos,
            ft.ResponsiveRow(
                columns=12,
                spacing=20,
                run_spacing=20,
                controls=[
                    tarjeta_resumen(
                        "Materias y Docentes",
                        ft.Icons.MENU_BOOK_OUTLINED,
                        TEAL,
                        cuerpo_materias,
                        "Ver docentes",
                        "/portal/padre/docentes",
                    ),
                    tarjeta_resumen(
                        "Deportes Inscriptos",
                        ft.Icons.FITNESS_CENTER,
                        ORANGE,
                        cuerpo_deportes,
                        "Gestionar deportes",
                        "/portal/padre/deportes",
                    ),
                    tarjeta_resumen(
                        "Comedor Escolar",
                        ft.Icons.RESTAURANT,
                        TEAL,
                        cuerpo_comedor,
                        "Ver servicios",
                        "/portal/padre/servicios",
                    ),
                    tarjeta_resumen(
                        "Transporte Institucional",
                        ft.Icons.DIRECTIONS_BUS,
                        TEAL,
                        cuerpo_transporte,
                        "Ver servicios",
                        "/portal/padre/servicios",
                    ),
                ],
            ),
        ]
        try:
            page.update()
        except Exception:
            pass

    # ==================== 4. SELECTOR DE HIJOS ====================
    botones_hijos: list[ft.Container] = []

    def cambiar_hijo(e, indice: int):
        estado["idx"] = indice
        for idx_b, boton in enumerate(botones_hijos):
            activo_b = idx_b == indice
            boton.bgcolor = TEAL if activo_b else BG_WHITE
            boton.border = None if activo_b else ft.Border.all(1, BORDER_COLOR)
            boton.content.controls[0].color = "white" if activo_b else TEAL
            boton.content.controls[1].color = "white" if activo_b else TEXT_COLOR
        render_detalle()

    for i, hijo in enumerate(estado["hijos"]):
        activo = i == estado["idx"]
        boton = ft.Container(
            height=46,
            bgcolor=TEAL if activo else BG_WHITE,
            border=None if activo else ft.Border.all(1, BORDER_COLOR),
            border_radius=BORDER_RADIUS,
            padding=ft.Padding(16, 0, 16, 0),
            on_click=lambda e, indice=i: cambiar_hijo(e, indice),
            content=ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        ft.Icons.PERSON, size=18, color="white" if activo else TEAL
                    ),
                    ft.Text(
                        _nombre_completo(hijo),
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color="white" if activo else TEXT_COLOR,
                    ),
                ],
            ),
        )
        botones_hijos.append(boton)

    selector_bar = ft.Row(
        spacing=12,
        wrap=True,
        controls=[
            ft.Text(
                "Seleccionar Hijo:",
                size=14,
                weight=ft.FontWeight.W_600,
                color=TEAL_DARK,
            ),
            *botones_hijos,
        ],
    )

    render_detalle()

    return layout(
        [
            banner_tutor,
            selector_bar,
            detalle_container,
        ]
    )
