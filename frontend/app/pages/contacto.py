import flet as ft
import httpx

from frontend.app.api_client import api_client
from frontend.app.components.constants import (
    BG_PAGE_ALT,
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


def get_contacto_view(page: ft.Page) -> list[ft.Control]:
    """Retorna la vista de Contacto, Redes Sociales y Ubicación institucional."""

    tarjeta_info = ft.Container(
        col={"sm": 12, "md": 5},
        bgcolor=TEAL_DARK,
        border_radius=CARD_RADIUS,
        padding=40,
        content=ft.Column(
            spacing=28,
            controls=[
                ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text(
                            "COMUNÍCATE CON NOSOTROS",
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color=ORANGE,
                        ),
                        ft.Text(
                            "Centro Educativo Educar para Transformar",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=BG_WHITE,
                        ),
                        ft.Text(
                            "Estamos a su disposición para coordinar entrevistas pedagógicas y recorridas por el campus.",
                            size=14,
                            color=TEAL_LIGHT,
                        ),
                    ],
                ),
                ft.Divider(color=TEAL, height=1, thickness=1),
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Row(
                            spacing=12,
                            controls=[
                                ft.Icon(
                                    ft.Icons.LOCATION_ON_OUTLINED, color=ORANGE, size=20
                                ),
                                ft.Text(
                                    "Afueras de Resistencia, Chaco (Ruta 16 y Av. Sarmiento)",
                                    size=14,
                                    color=BG_WHITE,
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=12,
                            controls=[
                                ft.Icon(ft.Icons.PHONE_OUTLINED, color=ORANGE, size=20),
                                ft.Text(
                                    "+54 362 445-8900 (Secretaría)",
                                    size=14,
                                    color=BG_WHITE,
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=12,
                            controls=[
                                ft.Icon(ft.Icons.EMAIL_OUTLINED, color=ORANGE, size=20),
                                ft.Text(
                                    "administracion@educar.edu.ar",
                                    size=14,
                                    color=BG_WHITE,
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Divider(color=TEAL, height=1, thickness=1),
                ft.Column(
                    spacing=12,
                    controls=[
                        ft.Text(
                            "CANALES DIRECTOS",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=TEAL_LIGHT,
                        ),
                        ft.Button(
                            content=ft.Row(
                                spacing=8,
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.CHAT_OUTLINED, color=BG_WHITE, size=16
                                    ),
                                    ft.Text(
                                        "Chatear por WhatsApp",
                                        color=BG_WHITE,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                ],
                            ),
                            bgcolor="#25D366",
                            height=42,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)
                            ),
                            url="https://wa.me/5493624551212",
                        ),
                    ],
                ),
            ],
        ),
    )

    # FORMULARIO DE CONSULTA WEB
    campo_nombre = ft.TextField(
        hint_text="Tu nombre",
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        height=CONTROL_HEIGHT,
        text_size=14,
        border_radius=BORDER_RADIUS,
    )
    campo_telefono = ft.TextField(
        hint_text="+54 362 4XXXXXX",
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        height=CONTROL_HEIGHT,
        text_size=14,
        border_radius=BORDER_RADIUS,
    )
    campo_correo = ft.TextField(
        hint_text="tucorreo@ejemplo.com",
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        height=CONTROL_HEIGHT,
        text_size=14,
        border_radius=BORDER_RADIUS,
    )
    campo_mensaje = ft.TextField(
        hint_text="Describa su consulta acerca de niveles, aranceles o visitas...",
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        multiline=True,
        min_lines=4,
        border_radius=BORDER_RADIUS,
    )

    def mostrar_resultado(titulo: str, mensaje: str, error: bool = False):
        dialogo = ft.AlertDialog(
            modal=True,
            bgcolor=BG_WHITE,
            title=ft.Text(
                titulo,
                size=17,
                weight=ft.FontWeight.BOLD,
                color="#B91C1C" if error else TEAL_DARK,
            ),
            content=ft.Text(mensaje, size=14, color=TEXT_COLOR, width=380),
            actions=[
                ft.Button(
                    "Entendido",
                    bgcolor=TEAL,
                    color=BG_WHITE,
                    on_click=lambda _: page.pop_dialog(),
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialogo)

    async def enviar_consulta(e):
        if (
            not campo_nombre.value
            or not campo_telefono.value
            or not campo_correo.value
            or not campo_mensaje.value
        ):
            mostrar_resultado(
                "Faltan datos",
                "Complete todos los campos obligatorios (*) para enviar su consulta.",
                error=True,
            )
            return

        payload = {
            "nombre": campo_nombre.value.strip(),
            "telefono": campo_telefono.value.strip(),
            "correo": campo_correo.value.strip(),
            "mensaje": campo_mensaje.value.strip(),
        }
        try:
            await api_client.enviar_contacto(payload)
        except httpx.HTTPStatusError:
            mostrar_resultado(
                "No se pudo enviar",
                "Revise los datos ingresados e intente nuevamente.",
                error=True,
            )
            return
        except Exception:
            mostrar_resultado(
                "Sin conexión",
                "No se pudo conectar con el servidor. Intente más tarde.",
                error=True,
            )
            return

        campo_nombre.value = ""
        campo_telefono.value = ""
        campo_correo.value = ""
        campo_mensaje.value = ""
        page.update()
        mostrar_resultado(
            "¡Consulta enviada!",
            "Su mensaje fue recibido por secretaría. Le responderemos a la brevedad al correo indicado.",
        )

    tarjeta_formulario = ft.Container(
        col={"sm": 12, "md": 7},
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=40,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text(
                    "Envíanos tu consulta",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
                ft.Text(
                    "Completá el formulario y nuestro equipo de admisiones te responderá en el día.",
                    size=13,
                    color=MUTED,
                ),
                ft.ResponsiveRow(
                    columns=12,
                    spacing=16,
                    controls=[
                        ft.Container(
                            col={"sm": 12, "md": 6},
                            content=ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text(
                                        "Nombre completo *",
                                        size=13,
                                        weight=ft.FontWeight.W_600,
                                        color=TEXT_COLOR,
                                    ),
                                    campo_nombre,
                                ],
                            ),
                        ),
                        ft.Container(
                            col={"sm": 12, "md": 6},
                            content=ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text(
                                        "Teléfono de contacto *",
                                        size=13,
                                        weight=ft.FontWeight.W_600,
                                        color=TEXT_COLOR,
                                    ),
                                    campo_telefono,
                                ],
                            ),
                        ),
                        ft.Container(
                            col={"sm": 12},
                            content=ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text(
                                        "Correo electrónico *",
                                        size=13,
                                        weight=ft.FontWeight.W_600,
                                        color=TEXT_COLOR,
                                    ),
                                    campo_correo,
                                ],
                            ),
                        ),
                        ft.Container(
                            col={"sm": 12},
                            content=ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text(
                                        "Mensaje o consulta *",
                                        size=13,
                                        weight=ft.FontWeight.W_600,
                                        color=TEXT_COLOR,
                                    ),
                                    campo_mensaje,
                                ],
                            ),
                        ),
                    ],
                ),
                ft.Button(
                    "ENVIAR MENSAJE",
                    bgcolor=TEAL,
                    color=BG_WHITE,
                    height=CONTROL_HEIGHT,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)
                    ),
                    on_click=enviar_consulta,
                ),
            ],
        ),
    )

    main_section = ft.Container(
        bgcolor=BG_PAGE_ALT,
        padding=ft.Padding.symmetric(horizontal=80, vertical=80),
        content=ft.ResponsiveRow(
            columns=12,
            spacing=32,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[tarjeta_info, tarjeta_formulario],
        ),
    )

    return [main_section]
