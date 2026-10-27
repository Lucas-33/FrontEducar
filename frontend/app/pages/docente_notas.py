from datetime import date

import flet as ft
import httpx

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

PERIODOS = ["1° Trimestre", "2° Trimestre", "3° Trimestre", "Evaluación Final"]
TIPOS_EVALUACION = [
    "Parcial",
    "Trabajo Práctico",
    "Oral",
    "Conceptual",
    "Recuperatorio",
]
ESTADOS_ASISTENCIA = ["PRESENTE", "AUSENTE", "TARDE", "JUSTIFICADO"]


def _detalle_error(error: Exception) -> str:
    if isinstance(error, httpx.HTTPStatusError):
        try:
            return error.response.json().get("detail", "Error del servidor")
        except Exception:
            return "Error del servidor"
    return "No se pudo conectar con el servidor."


def _nombre_docente(perfil: dict | None, legajo: int | None) -> str:
    vinculo = (perfil or {}).get("vinculacion") or ""
    if ":" in vinculo:
        vinculo = vinculo.split(":", 1)[1]
    vinculo = vinculo.split("(#", 1)[0].strip()
    return vinculo or (f"Docente #{legajo}" if legajo else "Docente")


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


async def get_docente_notas_view(page: ft.Page) -> ft.Row:
    """Carga de calificaciones y asistencia para el docente autenticado."""

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
                        "Inicie sesión nuevamente para cargar notas y asistencia.",
                        size=13,
                        color=MUTED,
                    ),
                ],
            ),
        )

    if not legajo_docente:
        return portal_layout(
            page=page,
            titulo="Notas y Asistencia",
            active_route="/portal/docente/notas",
            rol="Docente",
            usuario_nombre="Docente",
            usuario_sub="Sesión no identificada",
            content_controls=[tarjeta_sin_identidad()],
        )

    # ==================== 1. CARGA DE DATOS BASE ====================
    try:
        asignaciones = [
            a
            for a in await api_client.get_asignaciones()
            if a.get("legajo_profesor") == legajo_docente
        ]
    except Exception:
        asignaciones = []
    try:
        alumnos = await api_client.get_alumnos(solo_activos=False)
    except Exception:
        alumnos = []

    def alumnos_de_curso(id_curso) -> list[dict]:
        lista = [a for a in alumnos if a.get("id_curso") == id_curso]
        return sorted(
            lista,
            key=lambda a: (
                (a.get("apellido") or "").lower(),
                (a.get("nombre") or "").lower(),
            ),
        )

    estado = {
        "tab": "notas",
        "asignacion": asignaciones[0] if asignaciones else None,
        "calificaciones": [],
        "curso_asistencia": None,
        "fecha_asistencia": str(date.today()),
        "registros_asistencia": [],
    }

    # ==================== 2. SELECTOR DE PESTAÑAS ====================
    tab_notas = ft.Container(
        height=40,
        border_radius=BORDER_RADIUS,
        padding=ft.Padding(18, 8, 18, 8),
        border=ft.Border.all(1, BORDER_COLOR),
        on_click=lambda _: cambiar_tab("notas"),
        content=ft.Row(
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.ASSESSMENT_OUTLINED, size=16, color=BG_WHITE),
                ft.Text(
                    "Calificaciones",
                    size=13,
                    weight=ft.FontWeight.W_600,
                    color=BG_WHITE,
                ),
            ],
        ),
    )
    tab_asistencia = ft.Container(
        height=40,
        border_radius=BORDER_RADIUS,
        padding=ft.Padding(18, 8, 18, 8),
        border=ft.Border.all(1, BORDER_COLOR),
        on_click=lambda _: cambiar_tab("asistencia"),
        content=ft.Row(
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.FACT_CHECK_OUTLINED, size=16, color=TEXT_COLOR),
                ft.Text(
                    "Asistencia", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR
                ),
            ],
        ),
    )
    tabs_row = ft.Row(spacing=10, controls=[tab_notas, tab_asistencia])

    def estilizar_tabs():
        activo_notas = estado["tab"] == "notas"
        tab_notas.bgcolor = TEAL_DARK if activo_notas else BG_WHITE
        tab_notas.content.controls[0].color = BG_WHITE if activo_notas else TEXT_COLOR
        tab_notas.content.controls[1].color = BG_WHITE if activo_notas else TEXT_COLOR
        tab_asistencia.bgcolor = TEAL_DARK if not activo_notas else BG_WHITE
        tab_asistencia.content.controls[0].color = (
            BG_WHITE if not activo_notas else TEXT_COLOR
        )
        tab_asistencia.content.controls[1].color = (
            BG_WHITE if not activo_notas else TEXT_COLOR
        )
        seccion_notas.visible = activo_notas
        seccion_asistencia.visible = not activo_notas

    def cambiar_tab(cual: str):
        estado["tab"] = cual
        estilizar_tabs()
        page.update()

    def mostrar_aviso(mensaje: str, error: bool = False):
        page.show_dialog(
            ft.SnackBar(
                ft.Text(mensaje, color="white"),
                bgcolor=BADGE_RED_TXT if error else TEAL,
            )
        )

    # ==================== 3. SECCIÓN CALIFICACIONES ====================
    asignacion_dropdown = ft.Dropdown(
        hint_text="Seleccione materia y curso...",
        hint_style=ft.TextStyle(size=14, color=TEXT_COLOR),
        text_size=14,
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding(12, 0, 8, 12),
        options=[
            ft.dropdown.Option(
                key=str(indice), text=f"{a.get('materia')} — {a.get('curso')}"
            )
            for indice, a in enumerate(asignaciones)
        ],
        value="0" if asignaciones else None,
    )
    asignacion_container = ft.Container(
        width=340,
        height=CONTROL_HEIGHT,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=BORDER_RADIUS,
        content=asignacion_dropdown,
    )

    columnas_notas = [
        ("Alumno", 200, False),
        ("Materia", 170, False),
        ("Curso", 150, False),
        ("Período", 140, False),
        ("Tipo", 130, False),
        ("Nota", 70, False),
        ("Fecha", 100, False),
        ("Observación", None, False),
        ("Acciones", 90, True),
    ]
    header_notas = create_table_header(columnas_notas)
    notas_holder = ft.Container()
    paginacion_notas = ft.Container()
    info_notas = ft.Text("", size=13, color=MUTED)

    def fila_calificacion(cal: dict) -> ft.Container:
        nota = cal.get("nota")
        color_nota = BADGE_GREEN_TXT if (nota or 0) >= 6 else BADGE_RED_TXT
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=200,
                        content=ft.Text(
                            cal.get("alumno") or "—",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=170,
                        content=ft.Text(
                            cal.get("materia") or "—", size=13, color=TEXT_COLOR
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
                    ft.Container(
                        width=90,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=6,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    icon_size=17,
                                    icon_color=TEAL,
                                    tooltip="Editar nota",
                                    padding=0,
                                    on_click=lambda e, c=cal: abrir_dialogo_nota(c),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_size=17,
                                    icon_color=BADGE_RED_TXT,
                                    tooltip="Eliminar nota",
                                    padding=0,
                                    on_click=lambda e, c=cal: confirmar_eliminar_nota(
                                        c
                                    ),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    async def recargar_calificaciones():
        asignacion = estado["asignacion"]
        if not asignacion:
            estado["calificaciones"] = []
        else:
            try:
                estado["calificaciones"] = await api_client.get_calificaciones(
                    id_materia=asignacion.get("id_materia"),
                    id_curso=asignacion.get("id_curso"),
                )
            except Exception as error:
                estado["calificaciones"] = []
                mostrar_aviso(_detalle_error(error), error=True)
        render_calificaciones()

    def render_calificaciones():
        visibles = estado["calificaciones"]
        if visibles:
            filas = [fila_calificacion(c) for c in visibles]
        else:
            filas = [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "No hay calificaciones cargadas para la asignación seleccionada."
                        if estado["asignacion"]
                        else "No tiene materias asignadas registradas en el sistema.",
                        size=13,
                        color=MUTED,
                    ),
                )
            ]
        notas_holder.content = create_table_container(
            header=header_notas, rows=filas, min_width=1150
        )
        paginacion_notas.content = create_pagination_bar(
            texto_info=f"Mostrando {len(visibles)} calificaciones",
            pagina_actual=1,
            total_paginas=max(1, (len(visibles) + 9) // 10),
        )
        if visibles:
            notas = [c.get("nota") or 0 for c in visibles]
            aprobados = sum(1 for n in notas if n >= 6)
            info_notas.value = (
                f"{len(visibles)} notas cargadas · promedio {sum(notas) / len(notas):.2f} · "
                f"{aprobados} aprobados ({aprobados * 100 // len(visibles)}%)"
            )
        else:
            info_notas.value = ""
        try:
            page.update()
        except Exception:
            pass

    def abrir_dialogo_nota(calificacion: dict | None = None):
        asignacion = estado["asignacion"]
        if not asignacion:
            mostrar_aviso("Seleccione primero una materia y curso.", error=True)
            return

        alumnos_opciones = alumnos_de_curso(asignacion.get("id_curso"))
        alumno_dd = ft.Dropdown(
            label="Alumno *",
            border_color=BORDER_COLOR,
            focused_border_color=TEAL,
            text_size=13,
            options=[
                ft.dropdown.Option(
                    key=str(a.get("legajo")),
                    text=f"{a.get('apellido')}, {a.get('nombre')} (#{a.get('legajo')})",
                )
                for a in alumnos_opciones
            ],
            value=str(calificacion.get("legajo_alumno")) if calificacion else None,
        )
        periodo_dd = ft.Dropdown(
            label="Período *",
            border_color=BORDER_COLOR,
            focused_border_color=TEAL,
            text_size=13,
            options=[ft.dropdown.Option(p) for p in PERIODOS],
            value=(calificacion or {}).get("periodo"),
        )
        tipo_dd = ft.Dropdown(
            label="Tipo de evaluación *",
            border_color=BORDER_COLOR,
            focused_border_color=TEAL,
            text_size=13,
            options=[ft.dropdown.Option(t) for t in TIPOS_EVALUACION],
            value=(calificacion or {}).get("tipo"),
        )
        nota_field = ft.TextField(
            label="Nota (0 a 10) *",
            border_color=BORDER_COLOR,
            focused_border_color=TEAL,
            text_size=13,
            value=str(calificacion.get("nota")) if calificacion else "",
        )
        fecha_field = ft.TextField(
            label="Fecha (AAAA-MM-DD)",
            border_color=BORDER_COLOR,
            focused_border_color=TEAL,
            text_size=13,
            value=str(calificacion.get("fecha"))[:10]
            if calificacion and calificacion.get("fecha")
            else str(date.today()),
        )
        observacion_field = ft.TextField(
            label="Observación (opcional)",
            border_color=BORDER_COLOR,
            focused_border_color=TEAL,
            text_size=13,
            value=(calificacion or {}).get("observacion") or "",
        )
        mensaje_error = ft.Text("", size=12, color=BADGE_RED_TXT)

        async def guardar(e):
            mensaje_error.value = ""
            if not alumno_dd.value or not periodo_dd.value or not tipo_dd.value:
                mensaje_error.value = "Seleccione alumno, período y tipo de evaluación."
                page.update()
                return
            try:
                nota_valor = float(str(nota_field.value).replace(",", "."))
            except (TypeError, ValueError):
                mensaje_error.value = "Ingrese una nota numérica entre 0 y 10."
                page.update()
                return
            if not 0 <= nota_valor <= 10:
                mensaje_error.value = "La nota debe estar entre 0 y 10."
                page.update()
                return

            fecha_valor = (fecha_field.value or "").strip() or None
            payload = {
                "periodo": periodo_dd.value,
                "tipo": tipo_dd.value,
                "nota": nota_valor,
                "fecha": fecha_valor,
                "observacion": (observacion_field.value or "").strip() or None,
            }
            try:
                if calificacion:
                    await api_client.actualizar_calificacion(
                        calificacion["id_calificacion"], payload
                    )
                else:
                    await api_client.crear_calificacion(
                        {
                            "legajo_alumno": int(alumno_dd.value),
                            "id_materia": asignacion.get("id_materia"),
                            "id_curso": asignacion.get("id_curso"),
                            **payload,
                        }
                    )
            except Exception as error:
                mensaje_error.value = _detalle_error(error)
                page.update()
                return

            page.pop_dialog()
            mostrar_aviso("Calificación guardada correctamente.")
            await recargar_calificaciones()

        dialogo = ft.AlertDialog(
            modal=True,
            bgcolor=BG_WHITE,
            title=ft.Text(
                "Editar Calificación" if calificacion else "Cargar Nueva Calificación",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=TEAL_DARK,
            ),
            content=ft.Column(
                spacing=12,
                width=430,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Text(
                        f"{asignacion.get('materia')} — {asignacion.get('curso')}",
                        size=13,
                        weight=ft.FontWeight.W_600,
                        color=TEAL,
                    ),
                    alumno_dd,
                    periodo_dd,
                    tipo_dd,
                    nota_field,
                    fecha_field,
                    observacion_field,
                    mensaje_error,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                ft.Button("Guardar", bgcolor=TEAL, color=BG_WHITE, on_click=guardar),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialogo)

    def confirmar_eliminar_nota(calificacion: dict):
        async def eliminar_confirmado(e):
            try:
                await api_client.eliminar_calificacion(calificacion["id_calificacion"])
            except Exception as error:
                page.pop_dialog()
                mostrar_aviso(_detalle_error(error), error=True)
                return
            page.pop_dialog()
            mostrar_aviso("Calificación eliminada.")
            await recargar_calificaciones()

        dialogo = ft.AlertDialog(
            modal=True,
            bgcolor=BG_WHITE,
            title=ft.Text(
                "Eliminar calificación",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=TEAL_DARK,
            ),
            content=ft.Text(
                f"¿Confirma eliminar la nota {calificacion.get('nota')} de "
                f"{calificacion.get('alumno')} ({calificacion.get('periodo')})?",
                size=13,
                color=TEXT_COLOR,
                width=380,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                ft.Button(
                    "Eliminar",
                    bgcolor=BADGE_RED_TXT,
                    color=BG_WHITE,
                    on_click=eliminar_confirmado,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialogo)

    def on_cambiar_asignacion(e):
        indice = asignacion_dropdown.value
        estado["asignacion"] = asignaciones[int(indice)] if indice is not None else None
        page.run_task(recargar_calificaciones)

    asignacion_dropdown.on_change = on_cambiar_asignacion

    btn_nueva_nota = ft.Button(
        content=ft.Row(
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                ft.Text(
                    "Cargar Nota", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE
                ),
            ],
        ),
        bgcolor=TEAL,
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            padding=ft.Padding(20, 10, 20, 10),
        ),
        on_click=lambda _: abrir_dialogo_nota(),
    )

    seccion_notas = ft.Column(
        spacing=16,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[asignacion_container, info_notas],
                    ),
                    btn_nueva_nota,
                ],
            ),
            notas_holder,
            paginacion_notas,
        ],
    )

    # ==================== 4. SECCIÓN ASISTENCIA ====================
    cursos_docente: list[dict] = []
    vistos = set()
    for a in asignaciones:
        if a.get("id_curso") not in vistos:
            vistos.add(a.get("id_curso"))
            cursos_docente.append(
                {"id_curso": a.get("id_curso"), "curso": a.get("curso")}
            )
    if cursos_docente:
        estado["curso_asistencia"] = cursos_docente[0]

    curso_dropdown = ft.Dropdown(
        hint_text="Seleccione curso...",
        hint_style=ft.TextStyle(size=14, color=TEXT_COLOR),
        text_size=14,
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding(12, 0, 8, 12),
        options=[
            ft.dropdown.Option(
                key=str(indice), text=c.get("curso") or f"Curso #{c.get('id_curso')}"
            )
            for indice, c in enumerate(cursos_docente)
        ],
        value="0" if cursos_docente else None,
    )
    curso_container = ft.Container(
        width=240,
        height=CONTROL_HEIGHT,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=BORDER_RADIUS,
        content=curso_dropdown,
    )

    fecha_field_asistencia = ft.TextField(
        hint_text="AAAA-MM-DD",
        hint_style=ft.TextStyle(size=14, color=MUTED),
        text_size=14,
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding(12, 0, 8, 12),
        value=estado["fecha_asistencia"],
    )
    fecha_container = ft.Container(
        width=160,
        height=CONTROL_HEIGHT,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=BORDER_RADIUS,
        content=fecha_field_asistencia,
    )

    planilla_holder = ft.Column(spacing=8)
    planilla_card = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=20,
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Text(
                    "Planilla de Asistencia Diaria",
                    size=15,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
                ft.Text(
                    "Seleccione curso y fecha, presione «Ver Planilla», marque el estado de cada alumno y guarde.",
                    size=12,
                    color=MUTED,
                ),
                planilla_holder,
            ],
        ),
    )

    estados_por_alumno: dict[int, ft.Dropdown] = {}

    def cargar_planilla(e=None):
        curso = estado["curso_asistencia"]
        if not curso:
            mostrar_aviso(
                "No tiene cursos asignados para cargar asistencia.", error=True
            )
            return
        fecha_valor = (fecha_field_asistencia.value or "").strip()
        if len(fecha_valor) != 10 or fecha_valor[4] != "-" or fecha_valor[7] != "-":
            mostrar_aviso("Ingrese la fecha en formato AAAA-MM-DD.", error=True)
            return

        lista_alumnos = alumnos_de_curso(curso.get("id_curso"))
        estados_por_alumno.clear()
        filas = []
        for alumno in lista_alumnos:
            selector = ft.Dropdown(
                width=170,
                value="PRESENTE",
                border_color=BORDER_COLOR,
                focused_border_color=TEAL,
                text_size=13,
                options=[ft.dropdown.Option(est) for est in ESTADOS_ASISTENCIA],
            )
            estados_por_alumno[alumno.get("legajo")] = selector
            filas.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            f"{alumno.get('apellido')}, {alumno.get('nombre')} (#{alumno.get('legajo')})",
                            size=13,
                            color=TEXT_COLOR,
                        ),
                        selector,
                    ],
                )
            )

        if filas:
            planilla_holder.controls = filas
        else:
            planilla_holder.controls = [
                ft.Text("El curso no tiene alumnos registrados.", size=13, color=MUTED)
            ]
        page.update()
        page.run_task(recargar_registros)

    async def guardar_asistencia(e):
        curso = estado["curso_asistencia"]
        if not curso or not estados_por_alumno:
            mostrar_aviso(
                "Primero presione «Ver Planilla» para cargar los alumnos del curso.",
                error=True,
            )
            return
        fecha_valor = (fecha_field_asistencia.value or "").strip()
        registros = [
            {"legajo_alumno": legajo, "estado": selector.value or "PRESENTE"}
            for legajo, selector in estados_por_alumno.items()
        ]
        try:
            await api_client.registrar_asistencia_lote(
                {
                    "id_curso": curso.get("id_curso"),
                    "fecha": fecha_valor,
                    "registros": registros,
                }
            )
        except Exception as error:
            mostrar_aviso(_detalle_error(error), error=True)
            return
        mostrar_aviso(f"Asistencia guardada para {len(registros)} alumnos.")
        await recargar_registros()

    btn_ver_planilla = ft.Button(
        content=ft.Row(
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.VISIBILITY_OUTLINED, size=16, color=TEAL_DARK),
                ft.Text(
                    "Ver Planilla", size=14, weight=ft.FontWeight.W_600, color=TEAL_DARK
                ),
            ],
        ),
        bgcolor=TEAL_LIGHT,
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            padding=ft.Padding(20, 10, 20, 10),
        ),
        on_click=cargar_planilla,
    )
    btn_guardar_asistencia = ft.Button(
        content=ft.Row(
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.SAVE_OUTLINED, size=16, color=BG_WHITE),
                ft.Text(
                    "Guardar Asistencia",
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=BG_WHITE,
                ),
            ],
        ),
        bgcolor=TEAL,
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            padding=ft.Padding(20, 10, 20, 10),
        ),
        on_click=guardar_asistencia,
    )

    columnas_asist = [
        ("Alumno", 220, False),
        ("Curso", 180, False),
        ("Fecha", 110, False),
        ("Estado", 120, False),
        ("Observación", None, False),
        ("Acciones", 80, True),
    ]
    header_asist = create_table_header(columnas_asist)
    asist_holder = ft.Container()
    paginacion_asist = ft.Container()

    async def eliminar_registro(e, registro: dict):
        async def eliminar_confirmado(e2):
            try:
                await api_client.eliminar_asistencia(registro["id_asistencia"])
            except Exception as error:
                page.pop_dialog()
                mostrar_aviso(_detalle_error(error), error=True)
                return
            page.pop_dialog()
            mostrar_aviso("Registro de asistencia eliminado.")
            await recargar_registros()

        dialogo = ft.AlertDialog(
            modal=True,
            bgcolor=BG_WHITE,
            title=ft.Text(
                "Eliminar registro", size=16, weight=ft.FontWeight.BOLD, color=TEAL_DARK
            ),
            content=ft.Text(
                f"¿Confirma eliminar la asistencia de {registro.get('alumno')} del {_fecha_legible(registro.get('fecha'))}?",
                size=13,
                color=TEXT_COLOR,
                width=380,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                ft.Button(
                    "Eliminar",
                    bgcolor=BADGE_RED_TXT,
                    color=BG_WHITE,
                    on_click=eliminar_confirmado,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialogo)

    def fila_asistencia(registro: dict) -> ft.Container:
        async def eliminar_este_registro(e):
            await eliminar_registro(e, registro)

        return ft.Container(
            height=50,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=220,
                        content=ft.Text(
                            registro.get("alumno") or "—",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=180,
                        content=ft.Text(
                            registro.get("curso") or "—", size=13, color=MUTED
                        ),
                    ),
                    ft.Container(
                        width=110,
                        content=ft.Text(
                            _fecha_legible(registro.get("fecha")), size=12, color=MUTED
                        ),
                    ),
                    ft.Container(
                        width=120, content=_badge_asistencia(registro.get("estado"))
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Text(
                            registro.get("observacion") or "—", size=12, color=MUTED
                        ),
                    ),
                    ft.Container(
                        width=80,
                        alignment=ft.Alignment(1, 0),
                        content=ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_size=17,
                            icon_color=BADGE_RED_TXT,
                            tooltip="Eliminar registro",
                            padding=0,
                            on_click=eliminar_este_registro,
                        ),
                    ),
                ],
            ),
        )

    def render_registros():
        visibles = estado["registros_asistencia"]
        if visibles:
            filas = [fila_asistencia(r) for r in visibles]
        else:
            filas = [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "No hay registros de asistencia para el curso y fecha seleccionados.",
                        size=13,
                        color=MUTED,
                    ),
                )
            ]
        asist_holder.content = create_table_container(
            header=header_asist, rows=filas, min_width=1000
        )
        paginacion_asist.content = create_pagination_bar(
            texto_info=f"Mostrando {len(visibles)} registros",
            pagina_actual=1,
            total_paginas=max(1, (len(visibles) + 9) // 10),
        )
        try:
            page.update()
        except Exception:
            pass

    async def recargar_registros():
        curso = estado["curso_asistencia"]
        fecha_valor = (fecha_field_asistencia.value or "").strip()
        if not curso:
            estado["registros_asistencia"] = []
        else:
            try:
                estado["registros_asistencia"] = await api_client.get_asistencia(
                    id_curso=curso.get("id_curso"),
                    fecha=fecha_valor if len(fecha_valor) == 10 else None,
                )
            except Exception:
                estado["registros_asistencia"] = []
        render_registros()

    def on_cambiar_curso(e):
        indice = curso_dropdown.value
        if indice is not None:
            estado["curso_asistencia"] = cursos_docente[int(indice)]
        estados_por_alumno.clear()
        planilla_holder.controls = []
        page.update()
        page.run_task(recargar_registros)

    curso_dropdown.on_change = on_cambiar_curso

    seccion_asistencia = ft.Column(
        spacing=16,
        visible=False,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[curso_container, fecha_container, btn_ver_planilla],
                    ),
                    btn_guardar_asistencia,
                ],
            ),
            planilla_card,
            asist_holder,
            paginacion_asist,
        ],
    )

    # ==================== 5. RENDER INICIAL ====================
    estilizar_tabs()
    render_calificaciones()
    render_registros()
    if estado["asignacion"]:
        page.run_task(recargar_calificaciones)
    if estado["curso_asistencia"]:
        page.run_task(recargar_registros)

    # ==================== 6. RETORNO CON PORTAL_LAYOUT ====================
    return portal_layout(
        page=page,
        titulo="Notas y Asistencia",
        active_route="/portal/docente/notas",
        rol="Docente",
        usuario_nombre=_nombre_docente(perfil, legajo_docente),
        usuario_sub=f"Legajo #{legajo_docente}",
        content_controls=[tabs_row, seccion_notas, seccion_asistencia],
    )
