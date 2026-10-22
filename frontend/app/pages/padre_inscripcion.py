from datetime import datetime

import flet as ft

from frontend.app.api_client import api_client
from frontend.app.components.constants import (
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    ONLINE_GREEN,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.form_controls import status_badge
from frontend.app.components.portal_layout import portal_layout


def _nombre_completo(persona: dict) -> str:
    nombre = (persona.get("nombre") or "").strip()
    apellido = (persona.get("apellido") or "").strip()
    return f"{nombre} {apellido}".strip() or "Alumno sin nombre"


def _texto_seguro(valor) -> str:
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


async def get_padre_inscripcion_view(page: ft.Page) -> ft.Row:
    """Consulta real de datos del alumno para el trámite de Inscripción de Cursado.

    El backend no expone un modelo de solicitudes de reinscripción: esta vista muestra
    información real del alumno y aclara que el trámite formal se realiza en Secretaría
    Académica, sin simular envíos.
    """

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    try:
        perfil = await api_client.get_mi_perfil()
    except Exception:
        perfil = None

    nombre_tutor = perfil.get("username", "Tutor") if perfil else "Tutor"

    def layout(controles: list[ft.Control]) -> ft.Row:
        return portal_layout(
            page=page,
            titulo="Inscripción de Cursado — Ciclo Lectivo",
            active_route="/portal/padre/inscripcion",
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
        "legajo": None,
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

    estado["legajo"] = estado["hijos"][0].get("legajo")

    cargadores = (
        ("cursos", api_client.get_cursos),
        ("niveles", api_client.get_niveles),
    )
    for clave, cargador in cargadores:
        try:
            estado[clave] = await cargador()
        except Exception:
            estado[clave] = []

    cursos_por_id = {c.get("id_curso"): c for c in estado["cursos"]}
    niveles_por_id = {n.get("id_nivel"): n for n in estado["niveles"]}

    def hijo_seleccionado() -> dict | None:
        for h in estado["hijos"]:
            if h.get("legajo") == estado["legajo"]:
                return h
        return None

    def curso_de(hijo: dict) -> dict | None:
        return cursos_por_id.get(hijo.get("id_curso"))

    def nivel_de(hijo: dict) -> dict | None:
        curso = curso_de(hijo)
        return niveles_por_id.get(curso.get("id_nivel")) if curso else None

    def etiqueta_hijo(hijo: dict) -> str:
        curso = curso_de(hijo)
        curso_nombre = curso.get("nombre") if curso else "Sin curso"
        return f"{_nombre_completo(hijo)} — {curso_nombre}"

    # ==================== 1. BANNER DEL PERÍODO ====================
    anio_actual = datetime.now().year
    banner_periodo = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=CARD_RADIUS,
        padding=20,
        content=ft.Row(
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=42,
                    height=42,
                    bgcolor=BG_WHITE,
                    border_radius=10,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(ft.Icons.APP_REGISTRATION, size=22, color=TEAL),
                ),
                ft.Column(
                    spacing=3,
                    expand=True,
                    controls=[
                        ft.Text(
                            f"Cursado y Reinscripción — Ciclo Lectivo {anio_actual}",
                            size=17,
                            weight=ft.FontWeight.BOLD,
                            color=TEAL_DARK,
                        ),
                        ft.Text(
                            "Consulte los datos registrados del alumno. La preinscripción formal se gestiona presencialmente en Secretaría Académica.",
                            size=13,
                            color=MUTED,
                        ),
                    ],
                ),
                ft.Container(
                    padding=ft.Padding(8, 4, 8, 4),
                    bgcolor=BG_WHITE,
                    border_radius=4,
                    content=ft.Text(
                        "Información", size=12, weight=ft.FontWeight.W_600, color=TEAL
                    ),
                ),
            ],
        ),
    )

    # ==================== 2. SELECTOR DE ALUMNO ====================
    alumno_dropdown = ft.Dropdown(
        hint_text="Alumno",
        hint_style=ft.TextStyle(size=14, color=TEXT_COLOR),
        text_size=14,
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding(12, 0, 8, 12),
        options=[
            ft.dropdown.Option(key=str(h.get("legajo")), text=etiqueta_hijo(h))
            for h in estado["hijos"]
        ],
        value=str(estado["legajo"]),
    )
    alumno_selector = ft.Container(
        width=340,
        height=CONTROL_HEIGHT,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=BORDER_RADIUS,
        content=alumno_dropdown,
    )
    selector_bar = ft.Row(
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text(
                "Seleccionar Alumno:",
                size=14,
                weight=ft.FontWeight.W_600,
                color=TEAL_DARK,
            ),
            alumno_selector,
        ],
    )

    # ==================== 3. DATOS DEL ALUMNO Y DOCUMENTACIÓN ====================
    info_alumno_holder = ft.Container()
    doc_holder = ft.Container()

    def item_requisito(titulo: str, estado_texto: str, es_valido: bool) -> ft.Row:
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE
                            if es_valido
                            else ft.Icons.ERROR_OUTLINE,
                            size=18,
                            color=ONLINE_GREEN if es_valido else ORANGE,
                        ),
                        ft.Text(titulo, size=14, color=TEXT_COLOR),
                    ],
                ),
                ft.Container(
                    padding=ft.Padding(8, 3, 8, 3),
                    bgcolor="#EBFEE6" if es_valido else "#FFF3E7",
                    border_radius=4,
                    content=ft.Text(
                        estado_texto,
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=ONLINE_GREEN if es_valido else ORANGE,
                    ),
                ),
            ],
        )

    def render_detalle():
        hijo = hijo_seleccionado()
        if not hijo:
            info_alumno_holder.content = _estado_vacio(
                "Seleccione un alumno para ver su información."
            )
            doc_holder.content = ft.Container()
            try:
                page.update()
            except Exception:
                pass
            return

        curso = curso_de(hijo)
        nivel = nivel_de(hijo)
        curso_nombre = curso.get("nombre") if curso else "-"
        nivel_nombre = nivel.get("nombre") if nivel else "-"
        estado_legible = (
            hijo.get("estado_alumno") or ""
        ).strip().capitalize() or "Sin estado"
        iniciales = (
            f"{(hijo.get('nombre') or ' ')[0]}{(hijo.get('apellido') or ' ')[0]}"
        ).upper().strip() or "A"

        info_alumno_holder.content = ft.Container(
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
                                                size=17,
                                                weight=ft.FontWeight.BOLD,
                                                color=TEAL_DARK,
                                            ),
                                            ft.Text(
                                                f"Legajo #{hijo.get('legajo', '-')} · Cursando actualmente: {curso_nombre} (Nivel {nivel_nombre})",
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
                            ft.Container(
                                col={"sm": 12, "md": 3},
                                content=ft.Column(
                                    spacing=4,
                                    controls=[
                                        ft.Text(
                                            "Legajo",
                                            size=12,
                                            weight=ft.FontWeight.W_600,
                                            color=MUTED,
                                        ),
                                        ft.Text(
                                            f"#{hijo.get('legajo', '-')}",
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                            color=TEXT_COLOR,
                                        ),
                                    ],
                                ),
                            ),
                            ft.Container(
                                col={"sm": 12, "md": 3},
                                content=ft.Column(
                                    spacing=4,
                                    controls=[
                                        ft.Text(
                                            "Curso Actual",
                                            size=12,
                                            weight=ft.FontWeight.W_600,
                                            color=MUTED,
                                        ),
                                        ft.Text(
                                            curso_nombre,
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                            color=TEXT_COLOR,
                                        ),
                                    ],
                                ),
                            ),
                            ft.Container(
                                col={"sm": 12, "md": 3},
                                content=ft.Column(
                                    spacing=4,
                                    controls=[
                                        ft.Text(
                                            "Nivel Educativo",
                                            size=12,
                                            weight=ft.FontWeight.W_600,
                                            color=MUTED,
                                        ),
                                        ft.Text(
                                            nivel_nombre,
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                            color=TEXT_COLOR,
                                        ),
                                    ],
                                ),
                            ),
                            ft.Container(
                                col={"sm": 12, "md": 3},
                                content=ft.Column(
                                    spacing=4,
                                    controls=[
                                        ft.Text(
                                            "Estado de Matrícula",
                                            size=12,
                                            weight=ft.FontWeight.W_600,
                                            color=MUTED,
                                        ),
                                        ft.Text(
                                            estado_legible,
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                            color=TEXT_COLOR,
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )

        tiene_curso = curso is not None
        doc_holder.content = ft.Container(
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=24,
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Text(
                        "Datos Registrados del Alumno",
                        size=17,
                        weight=ft.FontWeight.BOLD,
                        color=TEAL_DARK,
                    ),
                    ft.Text(
                        "Verifique esta información antes de iniciar el trámite. Si algún dato figura como «Sin registrar», acérquese a Secretaría para actualizarlo.",
                        size=13,
                        color=MUTED,
                    ),
                    ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                    item_requisito(
                        "D.N.I. del alumno",
                        _texto_seguro(hijo.get("dni"))
                        if hijo.get("dni")
                        else "Sin registrar",
                        bool(hijo.get("dni")),
                    ),
                    item_requisito(
                        "Domicilio declarado",
                        _texto_seguro(hijo.get("domicilio"))
                        if hijo.get("domicilio")
                        else "Sin registrar",
                        bool(hijo.get("domicilio")),
                    ),
                    item_requisito(
                        "Teléfono de contacto",
                        _texto_seguro(hijo.get("telefono"))
                        if hijo.get("telefono")
                        else "Sin registrar",
                        bool(hijo.get("telefono")),
                    ),
                    item_requisito(
                        "Correo electrónico de contacto",
                        _texto_seguro(hijo.get("correo_electronico"))
                        if hijo.get("correo_electronico")
                        else "Sin registrar",
                        bool(hijo.get("correo_electronico")),
                    ),
                    item_requisito(
                        "Curso asignado en el ciclo",
                        f"{curso_nombre} (Nivel {nivel_nombre})"
                        if tiene_curso
                        else "Sin asignar",
                        tiene_curso,
                    ),
                ],
            ),
        )
        try:
            page.update()
        except Exception:
            pass

    def on_cambiar_alumno(e):
        estado["legajo"] = int(alumno_dropdown.value) if alumno_dropdown.value else None
        render_detalle()

    alumno_dropdown.on_change = on_cambiar_alumno

    # ==================== 4. AVISO DEL TRÁMITE PRESENCIAL ====================
    def abrir_info_inscripcion(e):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Preinscripción Presencial — Secretaría Académica",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            content=ft.Column(
                spacing=12,
                width=420,
                tight=True,
                controls=[
                    ft.Text(
                        "Este portal muestra la información registrada del alumno, pero no envía solicitudes de inscripción en línea.",
                        size=13,
                        color=TEXT_COLOR,
                    ),
                    ft.Text(
                        "Para completar la preinscripción al próximo ciclo:",
                        size=13,
                        weight=ft.FontWeight.W_600,
                        color=TEAL_DARK,
                    ),
                    ft.Text(
                        "1. Verifique en esta página que los datos del alumno estén completos.",
                        size=13,
                        color=MUTED,
                    ),
                    ft.Text(
                        "2. Acérquese a Secretaría Académica con el D.N.I. del alumno y del tutor.",
                        size=13,
                        color=MUTED,
                    ),
                    ft.Text(
                        "3. Complete y firme la ficha de preinscripción del ciclo lectivo correspondiente.",
                        size=13,
                        color=MUTED,
                    ),
                    ft.Text(
                        "El equipo de Secretaría confirmará la vacante y el curso asignado.",
                        size=12,
                        color=MUTED,
                    ),
                ],
            ),
            actions=[
                ft.Button(
                    "Entendido",
                    bgcolor=TEAL,
                    color=BG_WHITE,
                    on_click=lambda e: page.pop_dialog(),
                ),
            ],
        )
        page.show_dialog(dlg)

    btn_como_inscribirme = ft.Button(
        "CÓMO INSCRIBIRME",
        bgcolor=TEAL,
        color="white",
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
        on_click=abrir_info_inscripcion,
    )

    aviso_tramite = ft.Container(
        bgcolor=BG_PAGE,
        border_radius=BORDER_RADIUS,
        padding=16,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=[
                ft.Row(
                    spacing=10,
                    expand=True,
                    controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=20, color=TEAL),
                        ft.Text(
                            "La preinscripción formal se gestiona en Secretaría Académica. Este portal no registra solicitudes en línea.",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ],
                ),
                btn_como_inscribirme,
            ],
        ),
    )

    render_detalle()

    return layout(
        [
            banner_periodo,
            selector_bar,
            info_alumno_holder,
            doc_holder,
            aviso_tramite,
        ]
    )
