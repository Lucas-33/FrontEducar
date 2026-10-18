import flet as ft
from frontend.app.api_client import api_client
from frontend.app.components.admin_layout import admin_layout
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
    MUTED,
    TEAL,
    TEAL_DARK,
    TEXT_COLOR,
)
from frontend.app.components.table_view import create_table_header


def _fecha_legible(iso: str | None) -> str:
    """Convierte una fecha ISO al formato dd/mm/aaaa."""
    if not iso:
        return "—"
    partes = str(iso)[:10].split("-")
    if len(partes) == 3:
        return f"{partes[2]}/{partes[1]}/{partes[0]}"
    return str(iso)


def _fecha_hora_legible(iso: str | None) -> str:
    """Convierte un datetime ISO al formato dd/mm/aaaa hh:mm."""
    if not iso:
        return "—"
    texto = str(iso)
    fecha = _fecha_legible(texto)
    if "T" in texto:
        hora = texto.split("T", 1)[1][:5]
        return f"{fecha} {hora}"
    return fecha


def _badge(texto: str, bg: str, color: str) -> ft.Container:
    return ft.Container(
        padding=ft.Padding(8, 4, 8, 4),
        bgcolor=bg,
        border_radius=4,
        content=ft.Text(texto, size=12, weight=ft.FontWeight.W_600, color=color),
    )


def _estrellas(cantidad: int) -> ft.Row:
    return ft.Row(
        spacing=2,
        controls=[
            ft.Icon(
                ft.Icons.STAR,
                size=14,
                color="#F59E0B" if i < (cantidad or 0) else BORDER_COLOR,
            )
            for i in range(5)
        ],
    )


async def get_admin_comunidad_view(page: ft.Page) -> ft.Row:
    """Bandeja de entrada de la comunidad: mensajes de contacto y moderación de opiniones."""

    token = getattr(page, "auth_token", None)
    if token and not api_client.token:
        api_client.set_token(token)

    mensajes: list[dict] = []
    opiniones: list[dict] = []
    error_carga = None
    try:
        mensajes = await api_client.get_mensajes_contacto()
    except Exception:
        error_carga = "No se pudieron cargar los mensajes de contacto."
    try:
        opiniones = await api_client.get_opiniones_todas()
    except Exception:
        error_carga = (error_carga + " " if error_carga else "") + "No se pudieron cargar las opiniones."

    # ==================== HELPERS DE UI ====================
    def tarjeta(titulo: str, subtitulo: str, contenido: ft.Control) -> ft.Container:
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
                            ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ft.Text(subtitulo, size=12, color=MUTED),
                        ],
                    ),
                    contenido,
                ],
            ),
        )

    def tabla(filas: ft.Column) -> ft.Container:
        return ft.Container(
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=BORDER_RADIUS,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Row(
                scroll=ft.ScrollMode.AUTO,
                spacing=0,
                controls=[ft.Container(width=1150, content=filas)],
            ),
        )

    def sin_datos(texto: str) -> ft.Container:
        return ft.Container(
            padding=24,
            alignment=ft.Alignment(0, 0),
            content=ft.Text(texto, size=13, color=MUTED),
        )

    # ==================== 1. MENSAJES DE CONTACTO ====================
    header_mensajes = create_table_header(
        [
            ("Remitente", 150, False),
            ("Correo", 190, False),
            ("Teléfono", 130, False),
            ("Mensaje", None, False),
            ("Fecha", 140, False),
            ("Estado", 90, False),
            ("Acciones", 100, True),
        ]
    )
    filas_mensajes = ft.Column(spacing=0, controls=[header_mensajes])

    async def marcar_leido(e, mensaje: dict):
        try:
            await api_client.marcar_mensaje_leido(mensaje["id_mensaje"])
        except Exception:
            page.show_dialog(
                ft.SnackBar(ft.Text("No se pudo marcar el mensaje como leído.", color="white"), bgcolor=BADGE_RED_TXT)
            )
            return
        mensaje["leido"] = True
        render_mensajes()
        page.show_dialog(ft.SnackBar(ft.Text("Mensaje marcado como leído.", color="white"), bgcolor=TEAL))

    def ver_mensaje(e, mensaje: dict):
        dialogo = ft.AlertDialog(
            modal=True,
            bgcolor=BG_WHITE,
            title=ft.Text(
                f"Mensaje de {mensaje.get('nombre') or 'Anónimo'}",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=TEAL_DARK,
            ),
            content=ft.Column(
                spacing=10,
                width=440,
                tight=True,
                controls=[
                    ft.Text(f"Correo: {mensaje.get('correo') or '—'}", size=13, color=TEXT_COLOR),
                    ft.Text(f"Teléfono: {mensaje.get('telefono') or '—'}", size=13, color=TEXT_COLOR),
                    ft.Text(f"Recibido: {_fecha_hora_legible(mensaje.get('fecha'))}", size=13, color=MUTED),
                    ft.Divider(color=BORDER_COLOR, height=1),
                    ft.Text(mensaje.get("mensaje") or "", size=13, color=TEXT_COLOR),
                ],
            ),
            actions=[ft.TextButton("Cerrar", on_click=lambda _: page.pop_dialog())],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialogo)

    def fila_mensaje(mensaje: dict) -> ft.Container:
        leido = bool(mensaje.get("leido"))
        badge = (
            _badge("Leído", BADGE_GREEN_BG, BADGE_GREEN_TXT)
            if leido
            else _badge("Nuevo", BADGE_YELLOW_BG, BADGE_YELLOW_TXT)
        )
        resumen = (mensaje.get("mensaje") or "").strip()
        if len(resumen) > 60:
            resumen = resumen[:57] + "..."
        return ft.Container(
            height=52,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=150, content=ft.Text(mensaje.get("nombre") or "—", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=190, content=ft.Text(mensaje.get("correo") or "—", size=13, color=TEXT_COLOR)),
                    ft.Container(width=130, content=ft.Text(mensaje.get("telefono") or "—", size=13, color=MUTED)),
                    ft.Container(expand=True, content=ft.Text(resumen, size=13, color=MUTED)),
                    ft.Container(width=140, content=ft.Text(_fecha_hora_legible(mensaje.get("fecha")), size=12, color=MUTED)),
                    ft.Container(width=90, content=badge),
                    ft.Container(
                        width=100,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=8,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.MARK_EMAIL_READ_OUTLINED,
                                    icon_size=18,
                                    icon_color=TEAL,
                                    tooltip="Marcar como leído",
                                    padding=0,
                                    visible=not leido,
                                    on_click=lambda e, m=mensaje: marcar_leido(e, m),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.VISIBILITY_OUTLINED,
                                    icon_size=18,
                                    icon_color=TEAL,
                                    tooltip="Ver mensaje completo",
                                    padding=0,
                                    on_click=lambda e, m=mensaje: ver_mensaje(e, m),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    def render_mensajes():
        if not mensajes:
            filas_mensajes.controls = [header_mensajes, sin_datos("No hay mensajes de contacto recibidos.")]
        else:
            filas_mensajes.controls = [header_mensajes, *[fila_mensaje(m) for m in mensajes]]
        page.update()

    # ==================== 2. MODERACIÓN DE OPINIONES ====================
    header_opiniones = create_table_header(
        [
            ("Autor", 150, False),
            ("Vínculo", 150, False),
            ("Comentario", None, False),
            ("Puntaje", 90, False),
            ("Fecha", 110, False),
            ("Estado", 100, False),
            ("Acciones", 100, True),
        ]
    )
    filas_opiniones = ft.Column(spacing=0, controls=[header_opiniones])

    async def aprobar_opinion(e, opinion: dict):
        try:
            await api_client.aprobar_opinion(opinion["id_opinion"])
        except Exception:
            page.show_dialog(
                ft.SnackBar(ft.Text("No se pudo aprobar la opinión.", color="white"), bgcolor=BADGE_RED_TXT)
            )
            return
        opinion["aprobada"] = True
        render_opiniones()
        page.show_dialog(ft.SnackBar(ft.Text("Opinión aprobada y publicada en el sitio.", color="white"), bgcolor=TEAL))

    def confirmar_eliminar(e, opinion: dict):
        async def eliminar_confirmado(e2):
            try:
                await api_client.eliminar_opinion(opinion["id_opinion"])
            except Exception:
                page.pop_dialog()
                page.show_dialog(
                    ft.SnackBar(ft.Text("No se pudo eliminar la opinión.", color="white"), bgcolor=BADGE_RED_TXT)
                )
                return
            page.pop_dialog()
            if opinion in opiniones:
                opiniones.remove(opinion)
            render_opiniones()
            page.show_dialog(ft.SnackBar(ft.Text("Opinión rechazada y eliminada.", color="white"), bgcolor=TEAL))

        dialogo = ft.AlertDialog(
            modal=True,
            bgcolor=BG_WHITE,
            title=ft.Text("Rechazar opinión", size=16, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
            content=ft.Text(
                f"¿Confirma que desea rechazar y eliminar la opinión de {opinion.get('nombre') or 'Anónimo'}?",
                size=13,
                color=TEXT_COLOR,
                width=380,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                ft.Button("Eliminar", bgcolor=BADGE_RED_TXT, color=BG_WHITE, on_click=eliminar_confirmado),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialogo)

    def fila_opinion(opinion: dict) -> ft.Container:
        aprobada = bool(opinion.get("aprobada"))
        badge = (
            _badge("Aprobada", BADGE_GREEN_BG, BADGE_GREEN_TXT)
            if aprobada
            else _badge("Pendiente", BADGE_YELLOW_BG, BADGE_YELLOW_TXT)
        )
        comentario = (opinion.get("comentario") or "").strip()
        if len(comentario) > 60:
            comentario = comentario[:57] + "..."
        return ft.Container(
            height=52,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=150, content=ft.Text(opinion.get("nombre") or "—", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=150, content=ft.Text(opinion.get("vinculo") or "—", size=13, color=MUTED)),
                    ft.Container(expand=True, content=ft.Text(comentario, size=13, color=MUTED)),
                    ft.Container(width=90, content=_estrellas(opinion.get("estrellas"))),
                    ft.Container(width=110, content=ft.Text(_fecha_legible(opinion.get("fecha")), size=12, color=MUTED)),
                    ft.Container(width=100, content=badge),
                    ft.Container(
                        width=100,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=8,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.THUMB_UP_OUTLINED,
                                    icon_size=18,
                                    icon_color=TEAL,
                                    tooltip="Aprobar y publicar",
                                    padding=0,
                                    visible=not aprobada,
                                    on_click=lambda e, o=opinion: aprobar_opinion(e, o),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_size=18,
                                    icon_color=BADGE_RED_TXT,
                                    tooltip="Rechazar / eliminar",
                                    padding=0,
                                    on_click=lambda e, o=opinion: confirmar_eliminar(e, o),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    def render_opiniones():
        if not opiniones:
            filas_opiniones.controls = [header_opiniones, sin_datos("No hay opiniones registradas.")]
        else:
            filas_opiniones.controls = [header_opiniones, *[fila_opinion(o) for o in opiniones]]
        page.update()

    render_mensajes()
    render_opiniones()

    pendientes = sum(1 for o in opiniones if not o.get("aprobada"))
    nuevos = sum(1 for m in mensajes if not m.get("leido"))

    if error_carga:
        aviso = ft.Container(
            bgcolor="#FDE8E8",
            border_radius=BORDER_RADIUS,
            padding=12,
            content=ft.Text(error_carga, size=13, color=BADGE_RED_TXT),
        )
    else:
        aviso = ft.Container()

    # ==================== 3. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Comunidad — Mensajes y Opiniones",
        active_route="/admin/comunidad",
        content_controls=[
            aviso,
            tarjeta(
                "Mensajes de Contacto",
                f"{len(mensajes)} mensajes recibidos · {nuevos} sin leer",
                tabla(filas_mensajes),
            ),
            tarjeta(
                "Moderación de Opiniones",
                f"{len(opiniones)} opiniones · {pendientes} pendientes de aprobación",
                tabla(filas_opiniones),
            ),
        ],
    )
