import flet as ft

from frontend.app.api_client import api_client
from frontend.app.components.constants import (
    BADGE_GREEN_BG,
    BADGE_GREEN_TXT,
    BADGE_RED_TXT,
    BADGE_WARN_BG,
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    MUTED,
    ONLINE_GREEN,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.portal_layout import portal_layout


def _fecha_corta(iso: str | None) -> str:
    """Convierte un ISO timestamp del backend en dd/mm/aaaa."""
    if not iso or len(iso) < 10:
        return "-"
    return f"{iso[8:10]}/{iso[5:7]}/{iso[0:4]}"


def _esta_activo(valor: str | None) -> bool:
    """Normaliza los estados ACTIVO/INACTIVO devueltos por el backend."""
    return (valor or "").strip().upper() == "ACTIVO"


def _badge_estado(activo: bool, con_registro: bool) -> ft.Container:
    """Badge semántico para servicios e inscripciones del alumno."""
    if activo:
        return ft.Container(
            padding=ft.Padding(8, 4, 8, 4),
            bgcolor=BADGE_GREEN_BG,
            border_radius=4,
            content=ft.Text(
                "Activo", size=12, weight=ft.FontWeight.W_600, color=BADGE_GREEN_TXT
            ),
        )
    if con_registro:
        return ft.Container(
            padding=ft.Padding(8, 4, 8, 4),
            bgcolor="#FEEBEB",
            border_radius=4,
            content=ft.Text(
                "Inactivo", size=12, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT
            ),
        )
    return ft.Container(
        padding=ft.Padding(8, 4, 8, 4),
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=4,
        content=ft.Text("Sin alta", size=12, weight=ft.FontWeight.W_600, color=MUTED),
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


async def get_alumno_dashboard_view(page: ft.Page) -> ft.Row:
    """Panel principal del estudiante con carnet digital y resumen real de su cursado."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and api_client.token != token_almacenado:
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
            titulo="Portal del Estudiante — Mi Cursado",
            active_route="/portal/alumno/dashboard",
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
    estado: dict = {
        "alumno": None,
        "cursos": [],
        "niveles": [],
        "asignaciones": [],
        "grupos_deporte": [],
        "inscripciones_deporte": [],
        "inscripciones_transporte": [],
        "inscripciones_comedor": [],
    }
    errores: list[str] = []

    try:
        # El listado de alumnos es solo para ADMIN/DOCENTE; el alumno consulta
        # su propia ficha por legajo.
        estado["alumno"] = await api_client.get_alumno(legajo)
    except Exception:
        errores.append("datos del alumno")

    try:
        estado["cursos"] = await api_client.get_cursos()
    except Exception:
        estado["cursos"] = []

    try:
        estado["niveles"] = await api_client.get_niveles()
    except Exception:
        estado["niveles"] = []

    try:
        estado["asignaciones"] = await api_client.get_asignaciones()
    except Exception:
        estado["asignaciones"] = []

    try:
        estado["grupos_deporte"] = await api_client.get_grupos_deporte()
    except Exception:
        estado["grupos_deporte"] = []

    try:
        inscripciones = await api_client.get_inscripciones_deporte()
        estado["inscripciones_deporte"] = [
            i for i in inscripciones if i.get("legajo_alumno") == legajo
        ]
    except Exception:
        errores.append("inscripciones deportivas")

    try:
        inscripciones = await api_client.get_inscripciones_transporte()
        estado["inscripciones_transporte"] = [
            i for i in inscripciones if i.get("legajo_alumno") == legajo
        ]
    except Exception:
        errores.append("inscripciones de transporte")

    try:
        inscripciones = await api_client.get_inscripciones_comedor()
        estado["inscripciones_comedor"] = [
            i for i in inscripciones if i.get("legajo_alumno") == legajo
        ]
    except Exception:
        errores.append("inscripciones de comedor")

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
        (c for c in estado["cursos"] if c.get("id_curso") == alumno.get("id_curso")),
        None,
    )
    nivel = next(
        (
            n
            for n in estado["niveles"]
            if curso and n.get("id_nivel") == curso.get("id_nivel")
        ),
        None,
    )

    nombre_curso = curso.get("nombre") if curso else "Curso sin asignar"
    nombre_nivel = nivel.get("nombre") if nivel else "Sin nivel"
    nombre_completo = (
        f"{alumno.get('nombre', '')} {alumno.get('apellido', '')}".strip() or "Alumno"
    )
    iniciales = (
        f"{alumno.get('nombre', '')[:1]}{alumno.get('apellido', '')[:1]}".upper()
        or "AL"
    )
    estado_alumno = (alumno.get("estado_alumno") or "-").strip().upper()
    matricula_regular = estado_alumno == "ACTIVO"

    asignaciones_curso = [
        a
        for a in estado["asignaciones"]
        if curso and a.get("id_curso") == curso.get("id_curso")
    ]
    materias_unicas = {a.get("id_materia") for a in asignaciones_curso}

    inscripciones_deporte = estado["inscripciones_deporte"]
    nombres_deportes = sorted({i.get("deporte", "-") for i in inscripciones_deporte})
    transporte = (
        estado["inscripciones_transporte"][0]
        if estado["inscripciones_transporte"]
        else None
    )
    comedor = (
        estado["inscripciones_comedor"][0] if estado["inscripciones_comedor"] else None
    )
    transporte_activo = bool(transporte) and _esta_activo(transporte.get("estado"))
    comedor_activo = bool(comedor) and _esta_activo(comedor.get("estado"))
    servicios_activos = int(transporte_activo) + int(comedor_activo)

    # ==================== 2. BANNER ESTUDIANTE ====================
    banner_alumno = ft.Container(
        bgcolor=TEAL_DARK,
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=16,
                    controls=[
                        ft.Container(
                            width=54,
                            height=54,
                            bgcolor=TEAL_LIGHT,
                            border_radius=27,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Text(
                                iniciales,
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                        ),
                        ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text(
                                    f"¡Hola, {nombre_completo}!",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color=BG_WHITE,
                                ),
                                ft.Text(
                                    f"Legajo #{alumno.get('legajo')} · {nombre_curso} · Nivel {nombre_nivel}",
                                    size=13,
                                    color=TEAL_LIGHT,
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Container(
                    bgcolor=ONLINE_GREEN if matricula_regular else BADGE_RED_TXT,
                    border_radius=BORDER_RADIUS,
                    padding=ft.Padding(12, 6, 12, 6),
                    content=ft.Text(
                        "MATRÍCULA REGULAR"
                        if matricula_regular
                        else f"MATRÍCULA {estado_alumno}",
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=BG_WHITE,
                    ),
                ),
            ],
        ),
    )

    # ==================== 3. TARJETAS DE MÉTRICAS REALES ====================
    def kpi_alumno(
        titulo: str, valor: str, subtitulo: str, icono: ft.IconData, color_bg: str
    ) -> ft.Container:
        return ft.Container(
            expand=True,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=20,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                titulo, size=11, weight=ft.FontWeight.W_600, color=MUTED
                            ),
                            ft.Container(
                                width=32,
                                height=32,
                                bgcolor=color_bg,
                                border_radius=8,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(icono, size=16, color=TEAL_DARK),
                            ),
                        ],
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                valor,
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                            ft.Text(subtitulo, size=11, color=MUTED),
                        ],
                    ),
                ],
            ),
        )

    resumen_servicios = (
        f"Transporte: {'Activo' if transporte_activo else 'Inactivo'} · "
        f"Comedor: {'Activo' if comedor_activo else 'Inactivo'}"
    )

    kpis_row = ft.Row(
        spacing=16,
        controls=[
            kpi_alumno(
                "ESTADO DE MATRÍCULA",
                estado_alumno.capitalize() or "-",
                f"DNI {alumno.get('dni', '-')}",
                ft.Icons.BADGE_OUTLINED,
                TEAL_LIGHT,
            ),
            kpi_alumno(
                "MATERIAS DEL CURSO",
                str(len(materias_unicas)),
                f"{nombre_curso} · {nombre_nivel}",
                ft.Icons.MENU_BOOK_OUTLINED,
                TEAL_LIGHT,
            ),
            kpi_alumno(
                "DEPORTES INSCRIPTOS",
                str(len(inscripciones_deporte)),
                ", ".join(nombres_deportes)
                if nombres_deportes
                else "Sin inscripciones",
                ft.Icons.FITNESS_CENTER_OUTLINED,
                BADGE_GREEN_BG,
            ),
            kpi_alumno(
                "SERVICIOS ACTIVOS",
                f"{servicios_activos} de 2",
                resumen_servicios,
                ft.Icons.DIRECTIONS_BUS_OUTLINED,
                BADGE_WARN_BG,
            ),
        ],
    )

    # ==================== 4. RESUMEN DE SERVICIOS Y ACTIVIDADES ====================
    def item_resumen(
        titulo: str, detalle: str, color_barra: str, badge: ft.Control
    ) -> ft.Container:
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
                                width=4, height=36, border_radius=2, bgcolor=color_barra
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        titulo,
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEAL_DARK,
                                    ),
                                    ft.Text(detalle, size=12, color=MUTED),
                                ],
                            ),
                        ],
                    ),
                    badge,
                ],
            ),
        )

    items_resumen: list[ft.Control] = [
        item_resumen(
            "Transporte Institucional",
            (
                f"{transporte.get('recorrido', '-')} · Alta {_fecha_corta(transporte.get('fecha_alta'))}"
                if transporte
                else "Sin inscripción al transporte registrada."
            ),
            TEAL,
            _badge_estado(transporte_activo, bool(transporte)),
        ),
        item_resumen(
            "Comedor Escolar",
            (
                f"Alta {_fecha_corta(comedor.get('fecha_alta'))}"
                if comedor
                else "Sin inscripción al comedor registrada."
            ),
            ORANGE,
            _badge_estado(comedor_activo, bool(comedor)),
        ),
    ]

    if inscripciones_deporte:
        for inscripcion in inscripciones_deporte:
            grupo = next(
                (
                    g
                    for g in estado["grupos_deporte"]
                    if g.get("id_grupo") == inscripcion.get("id_grupo")
                ),
                None,
            )
            detalle = (
                f"Inscripto el {_fecha_corta(inscripcion.get('fecha_inscripcion'))}"
            )
            if grupo and grupo.get("horario"):
                detalle = f"{grupo['horario']} · {detalle}"
            items_resumen.append(
                item_resumen(
                    f"Deporte: {inscripcion.get('deporte', '-')}",
                    detalle,
                    ONLINE_GREEN,
                    _badge_estado(True, True),
                )
            )
    else:
        items_resumen.append(
            item_resumen(
                "Deportes",
                "Sin inscripciones deportivas registradas.",
                ONLINE_GREEN,
                _badge_estado(False, False),
            )
        )

    resumen_card = ft.Container(
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
                            "Mi Resumen de Servicios y Actividades",
                            size=17,
                            weight=ft.FontWeight.BOLD,
                            color=TEAL_DARK,
                        ),
                        ft.TextButton(
                            "Ver Todas las Materias",
                            on_click=lambda _: page.go("/portal/alumno/materias"),
                        ),
                    ],
                ),
                ft.Column(spacing=10, controls=items_resumen),
            ],
        ),
    )

    # ==================== 5. CARNET DIGITAL ESTUDIANTIL ====================
    servicios_habilitados = []
    if comedor_activo:
        servicios_habilitados.append("Comedor")
    if transporte_activo:
        servicios_habilitados.append("Traslado")
    if servicios_habilitados:
        texto_habilitacion = (
            "Habilitado para: " + ", ".join(servicios_habilitados) + "."
        )
    else:
        texto_habilitacion = "Sin servicios activos registrados (comedor o traslado)."

    carnet_card = ft.Container(
        width=380,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "Credencial Digital Estudiantil",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
                ft.Container(
                    width=280,
                    bgcolor=TEAL_LIGHT,
                    border=ft.Border.all(1, TEAL),
                    border_radius=12,
                    padding=20,
                    content=ft.Column(
                        spacing=12,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(
                                        "EDUCAR SGE",
                                        size=11,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEAL_DARK,
                                    ),
                                    ft.Icon(ft.Icons.NFC, size=16, color=TEAL),
                                ],
                            ),
                            ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=54, color=TEAL),
                            ft.Column(
                                spacing=2,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text(
                                        nombre_completo,
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEAL_DARK,
                                    ),
                                    ft.Text(
                                        f"Legajo: #{alumno.get('legajo')} · DNI: {alumno.get('dni', '-')}",
                                        size=11,
                                        color=MUTED,
                                    ),
                                    ft.Text(
                                        f"{nombre_curso} · {nombre_nivel}",
                                        size=12,
                                        weight=ft.FontWeight.W_600,
                                        color=TEXT_COLOR,
                                    ),
                                ],
                            ),
                            ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=6,
                                controls=[
                                    ft.Icon(ft.Icons.QR_CODE, size=18, color=TEAL_DARK),
                                    ft.Text(
                                        f"Estado de matrícula: {estado_alumno.capitalize()}",
                                        size=10,
                                        color=MUTED,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                ft.Text(
                    texto_habilitacion,
                    size=11,
                    color=MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )

    fila_inferior = ft.Row(
        spacing=24,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[resumen_card, carnet_card],
    )

    aviso_error = ft.Text(
        f"⚠️ No se pudieron cargar: {', '.join(errores)}." if errores else "",
        size=13,
        weight=ft.FontWeight.W_600,
        color=BADGE_RED_TXT,
        visible=bool(errores),
    )

    holder_contenido = ft.Column(spacing=24, controls=[])

    def render():
        holder_contenido.controls = [banner_alumno, kpis_row, fila_inferior]
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
