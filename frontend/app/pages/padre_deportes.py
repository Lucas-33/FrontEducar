import flet as ft
import httpx

from frontend.app.api_client import api_client
from frontend.app.components.constants import (
    BADGE_GREEN_BG,
    BADGE_GREEN_TXT,
    BADGE_RED_TXT,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.portal_layout import portal_layout
from frontend.app.components.table_view import (
    create_table_container,
    create_table_header,
)


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


async def get_padre_deportes_view(page: ft.Page) -> ft.Row:
    """Inscripción deportiva real: grupos disponibles por nivel del alumno e inscripciones vigentes."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and api_client.token != token_almacenado:
        api_client.set_token(token_almacenado)

    try:
        perfil = await api_client.get_mi_perfil()
    except Exception:
        perfil = None

    nombre_tutor = perfil.get("username", "Tutor") if perfil else "Tutor"

    def layout(controles: list[ft.Control]) -> ft.Row:
        return portal_layout(
            page=page,
            titulo="Inscripción y Horarios Deportivos",
            active_route="/portal/padre/deportes",
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
        "grupos": [],
        "inscripciones": [],
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
        ("grupos", api_client.get_grupos_deporte),
        ("inscripciones", api_client.get_inscripciones_deporte),
    )
    for clave, cargador in cargadores:
        try:
            estado[clave] = await cargador()
        except Exception:
            estado[clave] = []

    cursos_por_id = {c.get("id_curso"): c for c in estado["cursos"]}
    niveles_por_id = {n.get("id_nivel"): n for n in estado["niveles"]}
    grupos_por_id = {g.get("id_grupo"): g for g in estado["grupos"]}
    legajos_hijos = {h.get("legajo") for h in estado["hijos"]}

    def curso_de(hijo: dict) -> dict | None:
        return cursos_por_id.get(hijo.get("id_curso"))

    def nivel_de(hijo: dict) -> dict | None:
        curso = curso_de(hijo)
        return niveles_por_id.get(curso.get("id_nivel")) if curso else None

    def hijo_seleccionado() -> dict | None:
        for h in estado["hijos"]:
            if h.get("legajo") == estado["legajo"]:
                return h
        return None

    def etiqueta_hijo(hijo: dict) -> str:
        curso = curso_de(hijo)
        curso_nombre = curso.get("nombre") if curso else "Sin curso"
        return f"{_nombre_completo(hijo)} — {curso_nombre}"

    def inscripcion_de(legajo, id_grupo) -> dict | None:
        for i in estado["inscripciones"]:
            if i.get("legajo_alumno") == legajo and i.get("id_grupo") == id_grupo:
                return i
        return None

    def grupos_del_hijo(hijo: dict | None) -> list[dict]:
        nivel = nivel_de(hijo) if hijo else None
        if not nivel:
            return []
        return [
            g for g in estado["grupos"] if g.get("id_nivel") == nivel.get("id_nivel")
        ]

    def texto_grupo(grupo: dict) -> str:
        return f"{grupo.get('deporte', '-')} · {grupo.get('nivel', '-')} · {grupo.get('horario', '-')}"

    # ==================== 1. ENCABEZADO Y SELECTOR ====================
    encabezado_holder = ft.Container()

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

    btn_nueva_inscripcion = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                ft.Text(
                    "Nueva Inscripción Deportiva",
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
            padding=ft.Padding(24, 12, 24, 12),
        ),
    )

    filtros_bar = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "Alumno:", size=14, weight=ft.FontWeight.W_600, color=TEAL_DARK
                    ),
                    alumno_selector,
                ],
            ),
            btn_nueva_inscripcion,
        ],
    )

    aviso_error = ft.Text(
        "", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False
    )

    # ==================== 2. TARJETAS DE GRUPOS ====================
    grupos_holder = ft.Container()

    def badge_nivel(texto: str) -> ft.Container:
        return ft.Container(
            padding=ft.Padding(8, 3, 8, 3),
            bgcolor=TEAL_LIGHT,
            border_radius=4,
            content=ft.Text(texto, size=11, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
        )

    def badge_inscripto(texto: str) -> ft.Container:
        return ft.Container(
            padding=ft.Padding(8, 3, 8, 3),
            bgcolor=BADGE_GREEN_BG,
            border_radius=4,
            content=ft.Text(
                texto, size=11, weight=ft.FontWeight.BOLD, color=BADGE_GREEN_TXT
            ),
        )

    def tarjeta_grupo(grupo: dict, hijo: dict) -> ft.Container:
        inscripcion = inscripcion_de(hijo.get("legajo"), grupo.get("id_grupo"))
        pie: list[ft.Control] = []
        if inscripcion:
            pie.append(
                ft.Row(
                    spacing=8,
                    controls=[
                        badge_inscripto("Inscripto"),
                        ft.Text(
                            f"Fecha: {_texto_seguro(inscripcion.get('fecha_inscripcion'))}",
                            size=12,
                            color=MUTED,
                        ),
                    ],
                )
            )
        else:
            pie.append(
                ft.TextButton(
                    "Inscribir",
                    icon=ft.Icons.PERSON_ADD_ALT_1_OUTLINED,
                    on_click=lambda e, g=grupo: abrir_inscripcion(grupo=g),
                )
            )

        return ft.Container(
            col={"sm": 12, "md": 6},
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=20,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Column(
                        spacing=8,
                        expand=True,
                        controls=[
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Text(
                                        grupo.get("deporte", "Deporte"),
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEAL_DARK,
                                    ),
                                    badge_nivel(grupo.get("nivel", "Nivel")),
                                ],
                            ),
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.SCHEDULE, size=14, color=ORANGE),
                                    ft.Text(
                                        _texto_seguro(grupo.get("horario")),
                                        size=12,
                                        color=MUTED,
                                    ),
                                ],
                            ),
                            ft.Text(
                                f"Grupo #{grupo.get('id_grupo', '-')}",
                                size=11,
                                color=MUTED,
                            ),
                            *pie,
                        ],
                    ),
                ],
            ),
        )

    # ==================== 3. TABLA DE INSCRIPCIONES ====================
    columnas = [
        ("Alumno", 260, False),
        ("Deporte", 200, False),
        ("Horario del Grupo", 320, False),
        ("Fecha de Inscripción", 200, False),
    ]
    header_table = create_table_header(columnas)
    tabla_holder = ft.Container()

    def inscripciones_filas() -> list[dict]:
        filas = []
        for inscripcion in estado["inscripciones"]:
            if inscripcion.get("legajo_alumno") not in legajos_hijos:
                continue
            grupo = grupos_por_id.get(inscripcion.get("id_grupo"))
            filas.append({"inscripcion": inscripcion, "grupo": grupo})
        return filas

    def fila_inscripcion(fila: dict) -> ft.Container:
        inscripcion = fila["inscripcion"]
        grupo = fila["grupo"] or {}
        horario = grupo.get("horario") or "-"
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=260,
                        content=ft.Text(
                            inscripcion.get("alumno", "-"),
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        width=200,
                        content=ft.Text(
                            inscripcion.get("deporte", "-"), size=14, color=TEXT_COLOR
                        ),
                    ),
                    ft.Container(
                        width=320, content=ft.Text(horario, size=13, color=MUTED)
                    ),
                    ft.Container(
                        width=200,
                        content=ft.Text(
                            _texto_seguro(inscripcion.get("fecha_inscripcion")),
                            size=13,
                            color=MUTED,
                        ),
                    ),
                ],
            ),
        )

    # ==================== 4. RENDER ====================
    def mostrar_error(mensaje: str):
        aviso_error.value = f"⚠️ {mensaje}"
        aviso_error.visible = True
        try:
            page.update()
        except Exception:
            pass

    def render():
        hijo = hijo_seleccionado()
        curso = curso_de(hijo) if hijo else None
        nivel = nivel_de(hijo) if hijo else None
        curso_nombre = curso.get("nombre") if curso else "-"
        nivel_nombre = nivel.get("nombre") if nivel else "-"

        if hijo:
            encabezado_holder.content = ft.Container(
                bgcolor=TEAL_LIGHT,
                border_radius=BORDER_RADIUS,
                padding=16,
                content=ft.Row(
                    spacing=10,
                    controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=20, color=TEAL),
                        ft.Text(
                            f"Alumno: {_nombre_completo(hijo)} ({curso_nombre}) · Grupos disponibles para Nivel {nivel_nombre}",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ],
                ),
            )
        else:
            encabezado_holder.content = ft.Container()

        grupos = grupos_del_hijo(hijo)
        if hijo and grupos:
            grupos_holder.content = ft.ResponsiveRow(
                columns=12,
                spacing=16,
                run_spacing=16,
                controls=[tarjeta_grupo(g, hijo) for g in grupos],
            )
        else:
            grupos_holder.content = _estado_vacio(
                "No hay grupos deportivos disponibles para el nivel de este alumno."
                if hijo
                else "Seleccione un alumno para ver los grupos disponibles."
            )

        filas = inscripciones_filas()
        tabla_holder.content = create_table_container(
            header=header_table,
            rows=[fila_inscripcion(f) for f in filas]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "Todavía no hay inscripciones deportivas de sus hijos.",
                        size=13,
                        color=MUTED,
                    ),
                )
            ],
            min_width=1000,
        )
        try:
            page.update()
        except Exception:
            pass

    async def recargar():
        try:
            estado["grupos"] = await api_client.get_grupos_deporte()
            estado["inscripciones"] = await api_client.get_inscripciones_deporte()
        except Exception as err:
            mostrar_error(f"No se pudo refrescar la información deportiva: {err}")
        render()

    # ==================== 5. DIÁLOGO DE INSCRIPCIÓN ====================
    def abrir_inscripcion(e=None, grupo: dict | None = None):
        if not estado["hijos"] or not estado["grupos"]:
            mostrar_error(
                "No hay alumnos o grupos deportivos disponibles para inscribir."
            )
            return

        hijo_actual = hijo_seleccionado() or estado["hijos"][0]
        hijo_field = ft.Dropdown(
            label="Alumno *",
            width=380,
            options=[
                ft.dropdown.Option(key=str(h.get("legajo")), text=etiqueta_hijo(h))
                for h in estado["hijos"]
            ],
            value=str(hijo_actual.get("legajo")),
        )
        grupo_field = ft.Dropdown(
            label="Grupo deportivo *",
            width=380,
            options=[
                ft.dropdown.Option(key=str(g.get("id_grupo")), text=texto_grupo(g))
                for g in estado["grupos"]
            ],
            value=str(grupo.get("id_grupo")) if grupo else None,
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar(e):
            if not hijo_field.value or not grupo_field.value:
                error_text.value = "Debe seleccionar el alumno y el grupo deportivo."
                error_text.visible = True
                error_text.update()
                return
            try:
                await api_client.inscribir_deporte(
                    {
                        "legajo_alumno": int(hijo_field.value),
                        "id_grupo": int(grupo_field.value),
                    }
                )
            except httpx.HTTPStatusError as err:
                detalle = "No se pudo registrar la inscripción deportiva."
                try:
                    detalle = err.response.json().get("detail", detalle)
                except Exception:
                    pass
                error_text.value = f"⚠️ {detalle}"
                error_text.visible = True
                error_text.update()
                return
            except httpx.RequestError:
                error_text.value = "⚠️ Error de conexión con el backend."
                error_text.visible = True
                error_text.update()
                return
            page.pop_dialog()
            await recargar()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Nueva Inscripción Deportiva", size=18, weight=ft.FontWeight.BOLD
            ),
            content=ft.Column(
                spacing=14,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        "Seleccione el alumno y el grupo en el que desea inscribirlo.",
                        size=13,
                        color=MUTED,
                    ),
                    hijo_field,
                    grupo_field,
                    error_text,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button("Inscribir", bgcolor=TEAL, color=BG_WHITE, on_click=guardar),
            ],
        )
        page.show_dialog(dlg)

    btn_nueva_inscripcion.on_click = abrir_inscripcion

    def on_cambiar_alumno(e):
        estado["legajo"] = int(alumno_dropdown.value) if alumno_dropdown.value else None
        render()

    alumno_dropdown.on_select = on_cambiar_alumno

    render()

    return layout(
        [
            encabezado_holder,
            filtros_bar,
            aviso_error,
            grupos_holder,
            ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.LIST_ALT_OUTLINED, size=20, color=TEAL),
                    ft.Text(
                        "Inscripciones vigentes de mis hijos",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=TEAL_DARK,
                    ),
                ],
            ),
            tabla_holder,
        ]
    )
