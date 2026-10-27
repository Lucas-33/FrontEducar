import flet as ft

from frontend.app.api_client import api_client
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    ONLINE_GREEN,
    TEAL,
    TEAL_DARK,
    TEXT_COLOR,
)
from frontend.app.components.form_controls import status_badge
from frontend.app.components.table_view import create_table_header


def _fecha_legible(iso: str | None) -> str:
    """Convierte una fecha ISO (2026-10-18) al formato dd/mm/aaaa."""
    if not iso:
        return "—"
    partes = str(iso)[:10].split("-")
    if len(partes) == 3:
        return f"{partes[2]}/{partes[1]}/{partes[0]}"
    return str(iso)


def _nro_solicitud(solicitud: dict) -> str:
    anio = str(solicitud.get("fecha") or "")[:4] or "—"
    return f"#SOL-{anio}-{solicitud['id_solicitud']:04d}"


async def get_admin_inscripciones_view(page: ft.Page) -> ft.Row:
    """Vista de Solicitudes de Admisión conectada a la API (aprobación/rechazo reales)."""

    token = getattr(page, "auth_token", None)
    if token and api_client.token != token:
        api_client.set_token(token)

    solicitudes: list[dict] = []
    error_carga = None
    try:
        solicitudes = await api_client.get_solicitudes()
    except Exception:
        error_carga = "No se pudieron cargar las solicitudes desde el servidor."

    # ==================== 1. FILTROS Y ACCIÓN ====================
    search_field = ft.TextField(
        hint_text="Buscar postulante o DNI...",
        hint_style=ft.TextStyle(size=14, color=MUTED),
        text_size=14,
        color=TEXT_COLOR,
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding(0, 0, 0, 10),
        expand=True,
        on_change=lambda _: render_tabla(),
    )
    search_input = ft.Container(
        width=280,
        height=CONTROL_HEIGHT,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=BORDER_RADIUS,
        padding=ft.Padding(12, 0, 12, 0),
        content=ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SEARCH, size=16, color=MUTED),
                search_field,
            ],
        ),
    )

    dropdown_nivel = ft.Dropdown(
        hint_text="Nivel: Todos",
        hint_style=ft.TextStyle(size=14, color=TEXT_COLOR),
        text_size=14,
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding(12, 0, 8, 12),
        options=[
            ft.dropdown.Option(opc)
            for opc in ["Todos", "Inicial", "Primario", "Secundario"]
        ],
    )
    dropdown_estado = ft.Dropdown(
        hint_text="Estado: Todos",
        hint_style=ft.TextStyle(size=14, color=TEXT_COLOR),
        text_size=14,
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding(12, 0, 8, 12),
        options=[
            ft.dropdown.Option(opc)
            for opc in ["Todos", "Pendiente", "Aprobado", "Rechazado"]
        ],
    )
    dropdown_nivel.on_change = lambda _: render_tabla()
    dropdown_estado.on_change = lambda _: render_tabla()

    def filtro_dropdown(dropdown: ft.Dropdown, width: int) -> ft.Container:
        return ft.Container(
            width=width,
            height=CONTROL_HEIGHT,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=BORDER_RADIUS,
            content=dropdown,
        )

    async def exportar_listado(e):
        await page.launch_url(api_client.reporte_url("solicitudes"))

    filters_bar = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    search_input,
                    filtro_dropdown(dropdown_nivel, 140),
                    filtro_dropdown(dropdown_estado, 140),
                ],
            ),
            ft.Button(
                content=ft.Row(
                    spacing=8,
                    controls=[
                        ft.Icon(
                            ft.Icons.FILE_DOWNLOAD_OUTLINED, size=16, color=BG_WHITE
                        ),
                        ft.Text(
                            "Exportar Listado",
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
                on_click=exportar_listado,
            ),
        ],
    )

    # ==================== 2. TABLA DE SOLICITUDES ====================
    columnas_solicitudes = [
        ("N° Solicitud", 130, False),
        ("Aspirante / Postulante", 180, False),
        ("DNI", 120, False),
        ("Nivel Postulado", 180, False),
        ("Padre / Tutor", 160, False),
        ("Teléfono", 130, False),
        ("Fecha", 110, False),
        ("Estado", 110, False),
    ]
    header_table = create_table_header(columnas_solicitudes)
    filas_column = ft.Column(spacing=0, controls=[header_table])

    async def cambiar_estado(e, solicitud: dict, nuevo_estado: str):
        # El token en memoria puede haberse perdido si el backend se reinició.
        token = getattr(page, "auth_token", None)
        if token and api_client.token != token:
            api_client.set_token(token)
        try:
            await api_client.cambiar_estado_solicitud(
                solicitud["id_solicitud"], nuevo_estado
            )
        except Exception:
            page.show_dialog(
                ft.SnackBar(
                    ft.Text("No se pudo actualizar la solicitud.", color="white"),
                    bgcolor=BADGE_RED_TXT,
                )
            )
            return
        solicitud["estado"] = nuevo_estado
        render_tabla()
        page.show_dialog(
            ft.SnackBar(
                ft.Text(
                    f"Solicitud #{solicitud['id_solicitud']} marcada como {nuevo_estado}.",
                    color="white",
                ),
                bgcolor=ONLINE_GREEN,
            )
        )

    def ver_documentacion(e, solicitud: dict):
        def dato(label: str, valor: str) -> ft.Row:
            return ft.Row(
                spacing=8,
                controls=[
                    ft.Text(
                        f"{label}:",
                        size=13,
                        weight=ft.FontWeight.W_600,
                        color=MUTED,
                        width=150,
                    ),
                    ft.Text(valor or "—", size=13, color=TEXT_COLOR, expand=True),
                ],
            )

        dialog = ft.AlertDialog(
            modal=True,
            bgcolor=BG_WHITE,
            title=ft.Text(
                f"Legajo de Admisión {_nro_solicitud(solicitud)}",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=TEAL_DARK,
            ),
            content=ft.Column(
                spacing=10,
                width=420,
                tight=True,
                controls=[
                    dato("Postulante", solicitud.get("postulante")),
                    dato("DNI", solicitud.get("dni")),
                    dato(
                        "Fecha de nacimiento",
                        _fecha_legible(solicitud.get("fecha_nacimiento")),
                    ),
                    dato("Nivel postulado", solicitud.get("nivel")),
                    dato("Padre / Tutor", solicitud.get("tutor")),
                    dato("Teléfono", solicitud.get("telefono")),
                    dato("Correo", solicitud.get("correo")),
                    dato("Fecha de solicitud", _fecha_legible(solicitud.get("fecha"))),
                    dato("Estado", solicitud.get("estado")),
                    dato("Observaciones", solicitud.get("observaciones")),
                ],
            ),
            actions=[ft.TextButton("Cerrar", on_click=lambda _: page.pop_dialog())],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialog)

    def boton_accion_solicitud(
        texto: str,
        icono: ft.IconData,
        color: str,
        on_click,
    ) -> ft.Button:
        return ft.Button(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Icon(icono, size=18, color=BG_WHITE),
                    ft.Text(
                        texto,
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=BG_WHITE,
                    ),
                ],
            ),
            bgcolor=color,
            width=300,
            height=CONTROL_HEIGHT,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
            on_click=on_click,
        )

    def abrir_panel_solicitud(solicitud: dict):
        estado_actual = solicitud.get("estado") or "Pendiente"

        async def aprobar(e):
            page.pop_dialog()
            await cambiar_estado(e, solicitud, "Aprobado")

        async def rechazar(e):
            page.pop_dialog()
            await cambiar_estado(e, solicitud, "Rechazado")

        def ver_documentos(e):
            page.pop_dialog()
            ver_documentacion(e, solicitud)

        dlg = ft.AlertDialog(
            modal=False,
            title=ft.Text(
                f"Solicitud {_nro_solicitud(solicitud)}",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=TEAL_DARK,
            ),
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Text(
                        f"Aspirante: {solicitud.get('postulante') or '—'}",
                        size=13,
                        color=TEXT_COLOR,
                    ),
                    ft.Text(
                        f"DNI: {solicitud.get('dni') or '—'}",
                        size=13,
                        color=MUTED,
                    ),
                    ft.Text(
                        f"Nivel postulado: {solicitud.get('nivel') or '—'}",
                        size=13,
                        color=MUTED,
                    ),
                    ft.Text(
                        f"Estado actual: {estado_actual}",
                        size=13,
                        color=MUTED,
                    ),
                    boton_accion_solicitud(
                        "Aprobar admisión",
                        ft.Icons.CHECK_CIRCLE_OUTLINE,
                        ONLINE_GREEN,
                        aprobar,
                    ),
                    boton_accion_solicitud(
                        "Rechazar solicitud",
                        ft.Icons.CANCEL_OUTLINED,
                        BADGE_RED_TXT,
                        rechazar,
                    ),
                    boton_accion_solicitud(
                        "Ver documentación",
                        ft.Icons.REMOVE_RED_EYE_OUTLINED,
                        TEAL,
                        ver_documentos,
                    ),
                ],
            ),
            actions=[ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog())],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def solicitud_row(solicitud: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            ink=True,
            tooltip="Haga clic para aprobar, rechazar o ver la solicitud",
            on_click=lambda e, s=solicitud: abrir_panel_solicitud(s),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=130,
                        content=ft.Text(
                            _nro_solicitud(solicitud),
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        width=180,
                        content=ft.Text(
                            solicitud.get("postulante") or "—",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=120,
                        content=ft.Text(
                            solicitud.get("dni") or "—", size=14, color=TEXT_COLOR
                        ),
                    ),
                    ft.Container(
                        width=180,
                        content=ft.Text(
                            solicitud.get("nivel") or "—", size=13, color=MUTED
                        ),
                    ),
                    ft.Container(
                        width=160,
                        content=ft.Text(
                            solicitud.get("tutor") or "—", size=14, color=TEXT_COLOR
                        ),
                    ),
                    ft.Container(
                        width=130,
                        content=ft.Text(
                            solicitud.get("telefono") or solicitud.get("correo") or "—",
                            size=13,
                            color=MUTED,
                        ),
                    ),
                    ft.Container(
                        width=110,
                        content=ft.Text(
                            _fecha_legible(solicitud.get("fecha")), size=13, color=MUTED
                        ),
                    ),
                    ft.Container(
                        width=110,
                        content=status_badge(solicitud.get("estado") or "Pendiente"),
                    ),
                ],
            ),
        )

    info_text = ft.Text("", size=14, color=MUTED)

    def render_tabla():
        texto = (search_field.value or "").strip().lower()
        nivel = dropdown_nivel.value
        estado = dropdown_estado.value

        filas = []
        for s in solicitudes:
            if (
                texto
                and texto not in (s.get("postulante") or "").lower()
                and texto not in (s.get("dni") or "")
            ):
                continue
            if nivel and nivel != "Todos" and nivel not in (s.get("nivel") or ""):
                continue
            if estado and estado != "Todos" and s.get("estado") != estado:
                continue
            filas.append(solicitud_row(s))

        filas_column.controls = [header_table, *filas]
        info_text.value = (
            f"Mostrando {len(filas)} de {len(solicitudes)} solicitudes recibidas "
            "· Haga clic en una fila para gestionarla"
        )
        page.update()

    render_tabla()

    if error_carga:
        aviso = ft.Container(
            bgcolor="#FDE8E8",
            border_radius=BORDER_RADIUS,
            padding=12,
            content=ft.Text(error_carga, size=13, color=BADGE_RED_TXT),
        )
    else:
        aviso = ft.Container()

    tabla_card = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Row(
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
            controls=[
                ft.Container(
                    width=1120,
                    content=filas_column,
                ),
            ],
        ),
    )

    pagination_bar = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[info_text],
    )

    # ==================== 3. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Admisiones — Solicitudes de Inscripción",
        active_route="/admin/inscripciones",
        content_controls=[
            aviso,
            filters_bar,
            tabla_card,
            pagination_bar,
        ],
    )
