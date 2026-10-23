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


def _nombre_completo(alumno: dict | None) -> str:
    if not alumno:
        return "Alumno"
    nombre = (alumno.get("nombre") or "").strip()
    apellido = (alumno.get("apellido") or "").strip()
    return f"{apellido}, {nombre}".strip(", ") or "Alumno sin nombre"


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
        content=ft.Text(
            estado or "—", size=11, weight=ft.FontWeight.W_600, color=color
        ),
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
                        ft.Text(
                            titulo, size=10, weight=ft.FontWeight.BOLD, color=MUTED
                        ),
                        ft.Text(
                            valor, size=20, weight=ft.FontWeight.BOLD, color=TEAL_DARK
                        ),
                        ft.Text(subtitulo, size=10, color=MUTED),
                    ],
                ),
            ],
        ),
    )


def _tarjeta(titulo: str, subtitulo: str, contenido: ft.Control) -> ft.Container:
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
                        ft.Text(
                            titulo, size=16, weight=ft.FontWeight.BOLD, color=TEAL_DARK
                        ),
                        ft.Text(subtitulo, size=12, color=MUTED),
                    ],
                ),
                contenido,
            ],
        ),
    )


async def get_padre_notas_view(page: ft.Page) -> ft.Row:
    """Seguimiento de calificaciones y presentismo de los hijos del tutor."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    try:
        perfil = await api_client.get_mi_perfil()
    except Exception:
        perfil = None

    nombre_tutor = (perfil or {}).get("username") or "Tutor"
    id_padre = (perfil or {}).get("id_padre")

    def layout(controles: list[ft.Control]) -> ft.Row:
        return portal_layout(
            page=page,
            titulo="Notas y Asistencia de mis Hijos",
            active_route="/portal/padre/notas",
            rol="Padre",
            usuario_nombre=nombre_tutor,
            usuario_sub="Tutor responsable",
            content_controls=controles,
        )

    def estado_vacio(
        mensaje: str, icono: ft.IconData = ft.Icons.INFO_OUTLINE
    ) -> ft.Container:
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
                    ft.Text(
                        mensaje, size=14, color=MUTED, text_align=ft.TextAlign.CENTER
                    ),
                ],
            ),
        )

    if not id_padre:
        return layout(
            [
                estado_vacio(
                    "No se pudo identificar al tutor. Inicie sesión nuevamente.",
                    ft.Icons.PERSON_OFF_OUTLINED,
                )
            ]
        )

    try:
        hijos = await api_client.get_hijos(id_padre)
    except Exception:
        hijos = []

    if not hijos:
        return layout(
            [
                estado_vacio(
                    "No hay alumnos vinculados a esta cuenta.",
                    ft.Icons.FAMILY_RESTROOM_OUTLINED,
                )
            ]
        )

    try:
        cursos = await api_client.get_cursos()
    except Exception:
        cursos = []
    cursos_por_id = {c.get("id_curso"): c for c in cursos}

    estado = {"legajo": hijos[0].get("legajo")}

    def hijo_seleccionado() -> dict | None:
        for h in hijos:
            if h.get("legajo") == estado["legajo"]:
                return h
        return None

    def curso_de(hijo: dict | None) -> str:
        curso = cursos_por_id.get((hijo or {}).get("id_curso"))
        return curso.get("nombre") if curso else "Sin curso asignado"

    def etiqueta_hijo(hijo: dict) -> str:
        return f"{_nombre_completo(hijo)} — {curso_de(hijo)}"

    # ==================== SELECTOR DE HIJO ====================
    hijo_dropdown = ft.Dropdown(
        hint_text="Seleccione un hijo...",
        hint_style=ft.TextStyle(size=14, color=TEXT_COLOR),
        text_size=14,
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding(12, 0, 8, 12),
        options=[
            ft.dropdown.Option(key=str(h.get("legajo")), text=etiqueta_hijo(h))
            for h in hijos
        ],
        value=str(estado["legajo"]),
    )
    hijo_container = ft.Container(
        width=380,
        height=CONTROL_HEIGHT,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=BORDER_RADIUS,
        content=hijo_dropdown,
    )

    # ==================== HOLDERS DINÁMICOS ====================
    kpis_holder = ft.Container()
    notas_holder = ft.Container()
    paginacion_holder = ft.Container()
    asist_holder = ft.Container()
    resumen_texto = ft.Text("", size=13, weight=ft.FontWeight.W_500, color=TEAL_DARK)
    aviso_error = ft.Container(
        bgcolor="#FDE8E8",
        border_radius=BORDER_RADIUS,
        padding=12,
        visible=False,
        content=ft.Text("", size=13, color=BADGE_RED_TXT),
    )

    def mostrar_error(mensaje: str):
        aviso_error.content.value = mensaje
        aviso_error.visible = True
        try:
            page.update()
        except Exception:
            pass

    header_notas = create_table_header(
        [
            ("Materia", 190, False),
            ("Curso", 150, False),
            ("Período", 140, False),
            ("Tipo", 130, False),
            ("Nota", 70, False),
            ("Fecha", 100, False),
            ("Observación", None, False),
        ]
    )
    header_asist = create_table_header(
        [("Fecha", 130, False), ("Estado", 140, False), ("Observación", None, False)]
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
                    ft.Container(
                        width=190,
                        content=ft.Text(
                            cal.get("materia") or "—",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=150,
                        content=ft.Text(cal.get("curso") or "—", size=13, color=MUTED),
                    ),
                    ft.Container(
                        width=140,
                        content=ft.Text(
                            cal.get("periodo") or "—", size=12, color=MUTED
                        ),
                    ),
                    ft.Container(
                        width=130,
                        content=ft.Text(cal.get("tipo") or "—", size=12, color=MUTED),
                    ),
                    ft.Container(
                        width=70,
                        content=ft.Text(
                            f"{nota:.1f}" if isinstance(nota, (int, float)) else "—",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=color_nota,
                        ),
                    ),
                    ft.Container(
                        width=100,
                        content=ft.Text(
                            _fecha_legible(cal.get("fecha")), size=12, color=MUTED
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Text(
                            cal.get("observacion") or "—", size=12, color=MUTED
                        ),
                    ),
                ],
            ),
        )

    def fila_asistencia(registro: dict) -> ft.Container:
        return ft.Container(
            height=48,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=130,
                        content=ft.Text(
                            _fecha_legible(registro.get("fecha")),
                            size=13,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=140, content=_badge_asistencia(registro.get("estado"))
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Text(
                            registro.get("observacion") or "—", size=12, color=MUTED
                        ),
                    ),
                ],
            ),
        )

    def render_datos(
        calificaciones: list[dict], asistencias: list[dict], resumen: dict | None
    ):
        hijo = hijo_seleccionado()

        notas = [c.get("nota") or 0 for c in calificaciones]
        promedio = f"{sum(notas) / len(notas):.2f}" if notas else "—"
        presentismo = (
            f"{resumen.get('porcentaje_presentismo', 0):.1f}%" if resumen else "—"
        )
        inasistencias = (
            (resumen.get("ausentes", 0) + resumen.get("justificados", 0))
            if resumen
            else "—"
        )

        kpis_holder.content = ft.ResponsiveRow(
            columns=12,
            spacing=16,
            controls=[
                _kpi(
                    "PROMEDIO GENERAL",
                    promedio,
                    f"{len(calificaciones)} notas registradas",
                    ft.Icons.STAR_OUTLINE,
                ),
                _kpi(
                    "PRESENTISMO",
                    presentismo,
                    "Asistencia del ciclo",
                    ft.Icons.FACT_CHECK_OUTLINED,
                ),
                _kpi(
                    "INASISTENCIAS",
                    str(inasistencias),
                    "Ausencias y justificadas",
                    ft.Icons.EVENT_BUSY_OUTLINED,
                ),
                _kpi(
                    "CURSO ACTUAL",
                    curso_de(hijo),
                    f"Legajo #{estado['legajo']}",
                    ft.Icons.SCHOOL_OUTLINED,
                ),
            ],
        )

        filas = [fila_nota(c) for c in calificaciones] or [
            ft.Container(
                padding=20,
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    "Todavía no hay calificaciones registradas para este alumno.",
                    size=13,
                    color=MUTED,
                ),
            )
        ]
        notas_holder.content = create_table_container(
            header=header_notas, rows=filas, min_width=1000
        )
        paginacion_holder.content = create_pagination_bar(
            texto_info=f"Mostrando {len(calificaciones)} calificaciones",
            pagina_actual=1,
            total_paginas=max(1, (len(calificaciones) + 9) // 10),
        )

        filas_a = [
            fila_asistencia(r)
            for r in sorted(
                asistencias, key=lambda r: str(r.get("fecha")), reverse=True
            )
        ] or [
            ft.Container(
                padding=20,
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    "Todavía no hay registros de asistencia para este alumno.",
                    size=13,
                    color=MUTED,
                ),
            )
        ]
        asist_holder.content = create_table_container(
            header=header_asist, rows=filas_a, min_width=600
        )

        if resumen:
            resumen_texto.value = (
                f"Presentismo de {_nombre_completo(hijo)}: {resumen.get('presentes', 0)} presentes · "
                f"{resumen.get('tardes', 0)} llegadas tarde · {resumen.get('ausentes', 0)} ausentes · "
                f"{resumen.get('justificados', 0)} justificadas sobre {resumen.get('total', 0)} clases registradas."
            )
        else:
            resumen_texto.value = (
                f"Sin registros de presentismo para {_nombre_completo(hijo)}."
            )
        try:
            page.update()
        except Exception:
            pass

    async def cargar_datos(e=None):
        legajo = estado["legajo"]
        aviso_error.visible = False

        try:
            calificaciones = await api_client.get_calificaciones(legajo_alumno=legajo)
        except Exception:
            calificaciones = []
            mostrar_error("No se pudieron cargar las calificaciones del alumno.")
        try:
            asistencias = await api_client.get_asistencia(legajo_alumno=legajo)
        except Exception:
            asistencias = []
            mostrar_error("No se pudo cargar la asistencia del alumno.")
        try:
            resumen = await api_client.get_resumen_asistencia(legajo)
        except Exception:
            resumen = None

        render_datos(calificaciones, asistencias, resumen)

    def on_cambiar_hijo(e):
        if hijo_dropdown.value is None:
            return
        estado["legajo"] = int(hijo_dropdown.value)
        page.run_task(cargar_datos)

    hijo_dropdown.on_change = on_cambiar_hijo

    # Render inicial vacío y carga asíncrona
    render_datos([], [], None)
    page.run_task(cargar_datos)

    # ==================== RETORNO CON PORTAL_LAYOUT ====================
    return layout(
        [
            ft.Container(
                bgcolor=TEAL_LIGHT,
                border_radius=BORDER_RADIUS,
                padding=16,
                content=ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.FAMILY_RESTROOM_OUTLINED, size=20, color=TEAL),
                        ft.Text(
                            "Seleccione un hijo para consultar sus calificaciones y presentismo.",
                            size=13,
                            weight=ft.FontWeight.W_500,
                            color=TEAL_DARK,
                        ),
                    ],
                ),
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[hijo_container],
            ),
            aviso_error,
            kpis_holder,
            resumen_texto,
            _tarjeta(
                "Calificaciones",
                "Detalle de evaluaciones registradas por los docentes.",
                notas_holder,
            ),
            paginacion_holder,
            _tarjeta(
                "Asistencias",
                "Registro diario de presentismo del alumno.",
                asist_holder,
            ),
        ]
    )
