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
    """Badge semántico para el estado de cada servicio."""
    if activo:
        return ft.Container(
            padding=ft.Padding(8, 4, 8, 4),
            bgcolor=BADGE_GREEN_BG,
            border_radius=4,
            content=ft.Text("Activo", size=12, weight=ft.FontWeight.W_600, color=BADGE_GREEN_TXT),
        )
    if con_registro:
        return ft.Container(
            padding=ft.Padding(8, 4, 8, 4),
            bgcolor="#FEEBEB",
            border_radius=4,
            content=ft.Text("Inactivo", size=12, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT),
        )
    return ft.Container(
        padding=ft.Padding(8, 4, 8, 4),
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=4,
        content=ft.Text("Sin alta", size=12, weight=ft.FontWeight.W_600, color=MUTED),
    )


def _fila_detalle(etiqueta: str, valor: str, color_valor: str = TEXT_COLOR) -> ft.Row:
    """Fila etiqueta/valor del detalle de cada servicio."""
    return ft.Row(
        [
            ft.Text(etiqueta, size=13, color=MUTED),
            ft.Text(valor, size=13, weight=ft.FontWeight.BOLD, color=color_valor),
        ]
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
                    content=ft.Icon(ft.Icons.PERSON_OFF_OUTLINED, size=26, color=TEAL_DARK),
                ),
                ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Text(mensaje, size=14, color=MUTED, text_align=ft.TextAlign.CENTER),
            ],
        ),
    )


async def get_alumno_servicios_view(page: ft.Page) -> ft.Row:
    """Retorna el estado real de los servicios de comedor y transporte del alumno."""

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
            titulo="Mis Servicios: Comedor y Transporte",
            active_route="/portal/alumno/servicios",
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

    # ==================== 1. DATOS REALES DEL ALUMNO Y SUS SERVICIOS ====================
    estado: dict = {
        "alumno": None,
        "curso": None,
        "transporte": None,
        "comedor": None,
        "recorridos": [],
    }
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

    try:
        inscripciones = await api_client.get_inscripciones_transporte()
        estado["transporte"] = next(
            (i for i in inscripciones if i.get("legajo_alumno") == legajo), None
        )
    except Exception:
        errores.append("inscripciones de transporte")

    try:
        inscripciones = await api_client.get_inscripciones_comedor()
        estado["comedor"] = next(
            (i for i in inscripciones if i.get("legajo_alumno") == legajo), None
        )
    except Exception:
        errores.append("inscripciones de comedor")

    try:
        estado["recorridos"] = await api_client.get_recorridos()
    except Exception:
        estado["recorridos"] = []

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

    estado["curso"] = next(
        (c for c in cursos if c.get("id_curso") == alumno.get("id_curso")), None
    )

    nombre_curso = estado["curso"].get("nombre") if estado["curso"] else "Curso sin asignar"
    nombre_completo = f"{alumno.get('nombre', '')} {alumno.get('apellido', '')}".strip() or "Alumno"

    transporte = estado["transporte"]
    comedor = estado["comedor"]
    transporte_activo = bool(transporte) and _esta_activo(transporte.get("estado"))
    comedor_activo = bool(comedor) and _esta_activo(comedor.get("estado"))

    # ==================== 2. AVISO DE ERROR DE CARGA ====================
    aviso_error = ft.Text(
        f"⚠️ No se pudieron cargar: {', '.join(errores)}." if errores else "",
        size=13,
        weight=ft.FontWeight.W_600,
        color=BADGE_RED_TXT,
        visible=bool(errores),
    )

    # ==================== 3. TARJETA COMEDOR ESCOLAR ====================
    if comedor:
        pie_comedor = ft.Container(
            bgcolor="#EBFEE6" if comedor_activo else BG_PAGE,
            border_radius=BORDER_RADIUS,
            padding=12,
            content=ft.Text(
                (
                    f"Inscripción registrada el {_fecha_corta(comedor.get('fecha_alta'))}."
                    if comedor_activo
                    else f"Inscripción registrada el {_fecha_corta(comedor.get('fecha_alta'))}, "
                    "actualmente dada de baja."
                ),
                size=12,
                color=TEAL_DARK if comedor_activo else MUTED,
            ),
        )
    else:
        pie_comedor = ft.Container(
            bgcolor=BG_PAGE,
            border_radius=BORDER_RADIUS,
            padding=12,
            content=ft.Text(
                "No registrás inscripción al comedor institucional. "
                "Para solicitar el alta, contactá a la Secretaría del colegio.",
                size=12,
                color=MUTED,
            ),
        )

    comedor_card = ft.Container(
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
                        ft.Row(
                            spacing=12,
                            controls=[
                                ft.Container(
                                    width=40,
                                    height=40,
                                    bgcolor=TEAL_LIGHT,
                                    border_radius=20,
                                    alignment=ft.Alignment(0, 0),
                                    content=ft.Icon(ft.Icons.RESTAURANT, size=20, color=TEAL_DARK),
                                ),
                                ft.Text(
                                    "Comedor Escolar",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEAL_DARK,
                                ),
                            ],
                        ),
                        _badge_estado(comedor_activo, bool(comedor)),
                    ],
                ),
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                ft.Column(
                    spacing=8,
                    controls=[
                        _fila_detalle(
                            "Estado del servicio:",
                            (
                                (comedor.get("estado") or "-").capitalize()
                                if comedor
                                else "Sin registro"
                            ),
                        ),
                        _fila_detalle(
                            "Fecha de alta:",
                            _fecha_corta(comedor.get("fecha_alta")) if comedor else "-",
                        ),
                        _fila_detalle("Legajo del alumno:", f"#{legajo}", TEAL),
                    ],
                ),
                pie_comedor,
            ],
        ),
    )

    # ==================== 4. TARJETA TRANSPORTE INSTITUCIONAL ====================
    if transporte:
        pie_transporte = ft.Container(
            bgcolor=BG_PAGE,
            border_radius=BORDER_RADIUS,
            padding=12,
            content=ft.Text(
                "Recordá presentarte 5 minutos antes en la parada asignada con tu credencial.",
                size=12,
                color=MUTED,
            ),
        )
    else:
        descripciones = [r.get("descripcion", "-") for r in estado["recorridos"]]
        texto_recorridos = (
            "Recorridos disponibles: " + " · ".join(descripciones) + "."
            if descripciones
            else "No hay recorridos publicados por el momento."
        )
        pie_transporte = ft.Container(
            bgcolor=BG_PAGE,
            border_radius=BORDER_RADIUS,
            padding=12,
            content=ft.Text(
                "No registrás inscripción al transporte institucional. " + texto_recorridos,
                size=12,
                color=MUTED,
            ),
        )

    transporte_card = ft.Container(
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
                        ft.Row(
                            spacing=12,
                            controls=[
                                ft.Container(
                                    width=40,
                                    height=40,
                                    bgcolor=TEAL_LIGHT,
                                    border_radius=20,
                                    alignment=ft.Alignment(0, 0),
                                    content=ft.Icon(
                                        ft.Icons.DIRECTIONS_BUS, size=20, color=TEAL_DARK
                                    ),
                                ),
                                ft.Text(
                                    "Transporte Institucional",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEAL_DARK,
                                ),
                            ],
                        ),
                        _badge_estado(transporte_activo, bool(transporte)),
                    ],
                ),
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                ft.Column(
                    spacing=8,
                    controls=[
                        _fila_detalle(
                            "Recorrido asignado:",
                            transporte.get("recorrido", "-") if transporte else "-",
                            TEAL,
                        ),
                        _fila_detalle(
                            "Estado del servicio:",
                            (
                                (transporte.get("estado") or "-").capitalize()
                                if transporte
                                else "Sin registro"
                            ),
                        ),
                        _fila_detalle(
                            "Fecha de alta:",
                            _fecha_corta(transporte.get("fecha_alta")) if transporte else "-",
                        ),
                        _fila_detalle("Legajo del alumno:", f"#{legajo}", TEAL),
                    ],
                ),
                pie_transporte,
            ],
        ),
    )

    servicios_row = ft.Row(
        spacing=20,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[comedor_card, transporte_card],
    )

    # ==================== 5. RESUMEN REAL DE SERVICIOS ====================
    texto_resumen = (
        f"Servicios activos: {int(transporte_activo) + int(comedor_activo)} de 2. "
        f"Transporte: {'Activo' if transporte_activo else ('Inactivo' if transporte else 'Sin alta')} · "
        f"Comedor: {'Activo' if comedor_activo else ('Inactivo' if comedor else 'Sin alta')}."
    )

    resumen_card = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
        padding=16,
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE, size=20, color=TEAL),
                ft.Text(texto_resumen, size=13, color=TEAL_DARK, weight=ft.FontWeight.W_500),
            ],
        ),
    )

    holder_contenido = ft.Column(spacing=24, controls=[])

    def render():
        holder_contenido.controls = [resumen_card, servicios_row]
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
