import httpx
import flet as ft
from frontend.app.api_client import api_client
from frontend.app.components.constants import (
    BADGE_GREEN_BG,
    BADGE_GREEN_TXT,
    BADGE_RED_BG,
    BADGE_RED_TXT,
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    GRAY_LIGHT,
    MUTED,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
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


def _estado_vacio(mensaje: str, icono: ft.IconData = ft.Icons.INFO_OUTLINE) -> ft.Container:
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


async def get_padre_servicios_view(page: ft.Page) -> ft.Row:
    """Gestión real de Comedor Escolar y Transporte Institucional para cada hijo vinculado."""

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
            titulo="Gestión de Servicios Complementarios",
            active_route="/portal/padre/servicios",
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
        "recorridos": [],
        "inscripciones_transporte": [],
        "inscripciones_comedor": [],
    }

    try:
        estado["hijos"] = await api_client.get_hijos(id_padre)
    except Exception:
        estado["hijos"] = []

    if not estado["hijos"]:
        return layout([_estado_vacio("No hay alumnos vinculados a esta cuenta.", ft.Icons.FAMILY_RESTROOM_OUTLINED)])

    cargadores = (
        ("recorridos", api_client.get_recorridos),
        ("inscripciones_transporte", api_client.get_inscripciones_transporte),
        ("inscripciones_comedor", api_client.get_inscripciones_comedor),
    )
    for clave, cargador in cargadores:
        try:
            estado[clave] = await cargador()
        except Exception:
            estado[clave] = []

    aviso_error = ft.Text("", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False)
    comedor_holder = ft.Container()
    transporte_holder = ft.Container()

    def mostrar_error(mensaje: str):
        aviso_error.value = f"⚠️ {mensaje}"
        aviso_error.visible = True
        try:
            page.update()
        except Exception:
            pass

    def inscripcion_comedor_de(legajo) -> dict | None:
        for i in estado["inscripciones_comedor"]:
            if i.get("legajo_alumno") == legajo:
                return i
        return None

    def inscripcion_transporte_de(legajo) -> dict | None:
        for i in estado["inscripciones_transporte"]:
            if i.get("legajo_alumno") == legajo:
                return i
        return None

    def badge_servicio(valor_estado) -> ft.Container:
        normalizado = (valor_estado or "").strip().upper()
        if normalizado == "ACTIVO":
            bg, color, texto = BADGE_GREEN_BG, BADGE_GREEN_TXT, "Activo"
        elif normalizado == "INACTIVO":
            bg, color, texto = BADGE_RED_BG, BADGE_RED_TXT, "Inactivo"
        else:
            bg, color, texto = GRAY_LIGHT, MUTED, "Sin inscripción"
        return ft.Container(
            padding=ft.Padding(8, 4, 8, 4),
            bgcolor=bg,
            border_radius=4,
            content=ft.Text(texto, size=12, weight=ft.FontWeight.W_600, color=color),
        )

    def fila_hijo(hijo: dict, detalle: list[ft.Control], acciones: list[ft.Control]) -> ft.Container:
        return ft.Container(
            padding=ft.Padding(16, 12, 16, 12),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=12,
                        expand=True,
                        controls=[
                            ft.Container(
                                width=38,
                                height=38,
                                bgcolor=TEAL_LIGHT,
                                border_radius=19,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(ft.Icons.PERSON, size=18, color=TEAL_DARK),
                            ),
                            ft.Column(
                                spacing=3,
                                expand=True,
                                controls=[
                                    ft.Text(
                                        f"{_nombre_completo(hijo)} · Legajo #{hijo.get('legajo', '-')}",
                                        size=14,
                                        weight=ft.FontWeight.W_600,
                                        color=TEXT_COLOR,
                                    ),
                                    ft.Row(spacing=8, wrap=True, controls=detalle),
                                ],
                            ),
                        ],
                    ),
                    ft.Row(spacing=8, controls=acciones),
                ],
            ),
        )

    # ==================== 1. TARJETA COMEDOR ====================
    def render_comedor():
        filas: list[ft.Control] = []
        for hijo in estado["hijos"]:
            inscripcion = inscripcion_comedor_de(hijo.get("legajo"))
            estado_actual = (inscripcion or {}).get("estado")
            detalle: list[ft.Control] = [badge_servicio(estado_actual)]
            if inscripcion:
                detalle.append(
                    ft.Text(f"Alta: {_texto_seguro(inscripcion.get('fecha_alta'))}", size=12, color=MUTED)
                )

            if estado_actual and estado_actual.strip().upper() == "ACTIVO":
                acciones = [
                    ft.TextButton(
                        "Dar de baja",
                        icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                        on_click=lambda e, h=hijo: abrir_baja_comedor(h),
                    )
                ]
            elif estado_actual and estado_actual.strip().upper() == "INACTIVO":
                acciones = [
                    ft.Text(
                        "Servicio inactivo: la reactivación se gestiona en administración.",
                        size=12,
                        color=MUTED,
                    )
                ]
            else:
                acciones = [
                    ft.TextButton(
                        "Inscribir al comedor",
                        icon=ft.Icons.PERSON_ADD_ALT_1_OUTLINED,
                        on_click=lambda e, h=hijo: abrir_inscribir_comedor(h),
                    )
                ]
            filas.append(fila_hijo(hijo, detalle, acciones))

        comedor_holder.content = ft.Container(
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        padding=24,
                        content=ft.Row(
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
                                ft.Column(
                                    spacing=4,
                                    expand=True,
                                    controls=[
                                        ft.Text(
                                            "Servicio de Comedor Escolar",
                                            size=18,
                                            weight=ft.FontWeight.BOLD,
                                            color=TEAL_DARK,
                                        ),
                                        ft.Text(
                                            "Situación registrada de cada alumno vinculado. Las altas y bajas se registran con la fecha del día.",
                                            size=13,
                                            color=MUTED,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),
                    ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                    *filas,
                ],
            ),
        )

    # ==================== 2. TARJETA TRANSPORTE ====================
    def render_transporte():
        descripciones = [r.get("descripcion", "-") for r in estado["recorridos"]]
        filas: list[ft.Control] = []
        for hijo in estado["hijos"]:
            inscripcion = inscripcion_transporte_de(hijo.get("legajo"))
            estado_actual = (inscripcion or {}).get("estado")
            detalle: list[ft.Control] = [badge_servicio(estado_actual)]
            if inscripcion:
                detalle.append(
                    ft.Text(f"Recorrido: {_texto_seguro(inscripcion.get('recorrido'))}", size=12, color=MUTED)
                )
                detalle.append(
                    ft.Text(f"Alta: {_texto_seguro(inscripcion.get('fecha_alta'))}", size=12, color=MUTED)
                )

            if estado_actual and estado_actual.strip().upper() == "ACTIVO":
                acciones = [
                    ft.TextButton(
                        "Dar de baja",
                        icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                        on_click=lambda e, h=hijo: abrir_baja_transporte(h),
                    )
                ]
            elif estado_actual and estado_actual.strip().upper() == "INACTIVO":
                acciones = [
                    ft.Text(
                        "Servicio inactivo: la reactivación se gestiona en administración.",
                        size=12,
                        color=MUTED,
                    )
                ]
            else:
                acciones = [
                    ft.TextButton(
                        "Inscribir al transporte",
                        icon=ft.Icons.PERSON_ADD_ALT_1_OUTLINED,
                        on_click=lambda e, h=hijo: abrir_inscribir_transporte(h),
                    )
                ]
            filas.append(fila_hijo(hijo, detalle, acciones))

        transporte_holder.content = ft.Container(
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        padding=24,
                        content=ft.Row(
                            spacing=12,
                            controls=[
                                ft.Container(
                                    width=40,
                                    height=40,
                                    bgcolor=TEAL_LIGHT,
                                    border_radius=20,
                                    alignment=ft.Alignment(0, 0),
                                    content=ft.Icon(ft.Icons.DIRECTIONS_BUS, size=20, color=TEAL_DARK),
                                ),
                                ft.Column(
                                    spacing=4,
                                    expand=True,
                                    controls=[
                                        ft.Text(
                                            "Servicio de Micros de Traslado",
                                            size=18,
                                            weight=ft.FontWeight.BOLD,
                                            color=TEAL_DARK,
                                        ),
                                        ft.Text(
                                            "Recorridos disponibles: " + (" · ".join(descripciones) if descripciones else "sin recorridos cargados."),
                                            size=13,
                                            color=MUTED,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),
                    ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                    *filas,
                ],
            ),
        )

    # ==================== 3. DIÁLOGOS DE ALTA Y BAJA ====================
    def abrir_inscribir_comedor(hijo: dict):
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar(e):
            try:
                await api_client.inscribir_comedor({"legajo_alumno": int(hijo.get("legajo"))})
            except httpx.HTTPStatusError as err:
                detalle = "No se pudo inscribir al comedor."
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
            title=ft.Text("Inscribir al Comedor Escolar", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                spacing=12,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        f"Se registrará el alta de {_nombre_completo(hijo)} (Legajo #{hijo.get('legajo', '-')}) al servicio de comedor con la fecha del día.",
                        size=13,
                        color=MUTED,
                    ),
                    error_text,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button("Confirmar Alta", bgcolor=TEAL, color=BG_WHITE, on_click=guardar),
            ],
        )
        page.show_dialog(dlg)

    def abrir_baja_comedor(hijo: dict):
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar(e):
            try:
                await api_client.baja_comedor(int(hijo.get("legajo")))
            except httpx.HTTPStatusError as err:
                detalle = "No se pudo dar de baja el servicio de comedor."
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
            title=ft.Text("Baja del Comedor Escolar", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                spacing=12,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        f"¿Confirma la baja de {_nombre_completo(hijo)} (Legajo #{hijo.get('legajo', '-')}) del servicio de comedor?",
                        size=13,
                        color=MUTED,
                    ),
                    ft.Text("El registro queda inactivo y conserva el historial del alumno.", size=12, color=MUTED),
                    error_text,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button("Confirmar Baja", bgcolor=BADGE_RED_TXT, color=BG_WHITE, on_click=guardar),
            ],
        )
        page.show_dialog(dlg)

    def abrir_inscribir_transporte(hijo: dict):
        if not estado["recorridos"]:
            mostrar_error("No hay recorridos de transporte cargados.")
            return

        recorrido_field = ft.Dropdown(
            label="Recorrido *",
            width=380,
            options=[
                ft.dropdown.Option(key=str(r.get("id_recorrido")), text=r.get("descripcion", "-"))
                for r in estado["recorridos"]
            ],
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar(e):
            if not recorrido_field.value:
                error_text.value = "Debe seleccionar un recorrido."
                error_text.visible = True
                error_text.update()
                return
            try:
                await api_client.inscribir_transporte(
                    {
                        "legajo_alumno": int(hijo.get("legajo")),
                        "id_recorrido": int(recorrido_field.value),
                    }
                )
            except httpx.HTTPStatusError as err:
                detalle = "No se pudo inscribir al transporte."
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
            title=ft.Text("Inscribir al Transporte Escolar", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                spacing=12,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        f"Se registrará la inscripción de {_nombre_completo(hijo)} (Legajo #{hijo.get('legajo', '-')}) en el recorrido seleccionado.",
                        size=13,
                        color=MUTED,
                    ),
                    recorrido_field,
                    error_text,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button("Confirmar Alta", bgcolor=TEAL, color=BG_WHITE, on_click=guardar),
            ],
        )
        page.show_dialog(dlg)

    def abrir_baja_transporte(hijo: dict):
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar(e):
            try:
                await api_client.baja_transporte(int(hijo.get("legajo")))
            except httpx.HTTPStatusError as err:
                detalle = "No se pudo dar de baja el servicio de transporte."
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
            title=ft.Text("Baja del Transporte Escolar", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                spacing=12,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        f"¿Confirma la baja de {_nombre_completo(hijo)} (Legajo #{hijo.get('legajo', '-')}) del servicio de transporte?",
                        size=13,
                        color=MUTED,
                    ),
                    ft.Text("El registro queda inactivo y conserva el historial del alumno.", size=12, color=MUTED),
                    error_text,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button("Confirmar Baja", bgcolor=BADGE_RED_TXT, color=BG_WHITE, on_click=guardar),
            ],
        )
        page.show_dialog(dlg)

    # ==================== 4. RECARGA Y RENDER ====================
    async def recargar():
        try:
            estado["recorridos"] = await api_client.get_recorridos()
            estado["inscripciones_transporte"] = await api_client.get_inscripciones_transporte()
            estado["inscripciones_comedor"] = await api_client.get_inscripciones_comedor()
        except Exception as err:
            mostrar_error(f"No se pudo refrescar el estado de los servicios: {err}")
        render()

    def render():
        render_comedor()
        render_transporte()
        try:
            page.update()
        except Exception:
            pass

    render()

    aviso_cambios = ft.Container(
        bgcolor=BG_PAGE,
        border_radius=BORDER_RADIUS,
        padding=14,
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE, size=18, color=TEAL),
                ft.Text(
                    "Los altas y bajas se registran al instante con la fecha del día. Para cambiar un recorrido o reactivar un servicio dado de baja, comuníquese con administración.",
                    size=13,
                    color=MUTED,
                    weight=ft.FontWeight.W_500,
                ),
            ],
        ),
    )

    return layout(
        [
            comedor_holder,
            transporte_holder,
            aviso_cambios,
            aviso_error,
        ]
    )
