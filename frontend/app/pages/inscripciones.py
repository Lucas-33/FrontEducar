# src/views/inscripcion.py
import httpx
import flet as ft
from frontend.app.api_client import api_client

# Variables de color extraídas del CSS
GREEN = "#0B4F4F"
TEAL = "#0D6E6E"
TEAL_LIGHT = "#E6F2F2"
ORANGE = "#D97736"
TEXT_COLOR = "#1E2A29"
MUTED = "#5C6B69"
BORDER_COLOR = "#EAE6E1"
BG_MAIN = "#FDFBF9"
BG_WHITE = "#FFFFFF"


def get_inscripcion_view(page: ft.Page) -> list[ft.Control]:
    """Retorna únicamente los bloques centrales de la página de Inscripción."""

    # ==================== HELPERS DE FORMULARIO ====================
    def crear_campo(hint: str, keyboard_type: ft.KeyboardType = ft.KeyboardType.TEXT) -> ft.TextField:
        return ft.TextField(
            hint_text=hint,
            keyboard_type=keyboard_type,
            border_color=BORDER_COLOR,
            focused_border_color=TEAL,
            bgcolor="#FDFCFB",
            border_radius=6,
            content_padding=ft.Padding(12, 10, 12, 10),
            text_size=14,
        )

    def input_field(label: str, control: ft.Control, col_span: int = 6) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": col_span},
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Text(label, size=13, weight=ft.FontWeight.W_500, color=TEXT_COLOR),
                    control,
                ],
            ),
        )

    # Campos del formulario con referencia para el envío
    campo_nombre = crear_campo("Ej. Santiago")
    campo_apellido = crear_campo("Ej. Gómez")
    campo_fecha_nac = crear_campo("DD/MM/AAAA")
    campo_dni = crear_campo("Sin puntos", keyboard_type=ft.KeyboardType.NUMBER)
    campo_nivel = ft.Dropdown(
        hint_text="Seleccione nivel...",
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        bgcolor="#FDFCFB",
        border_radius=6,
        options=[
            ft.dropdown.Option("Inicial (Jardín)"),
            ft.dropdown.Option("Primario"),
            ft.dropdown.Option("Secundario"),
        ],
        content_padding=ft.Padding(12, 10, 12, 10),
        text_size=14,
    )
    campo_tutor = crear_campo("Ej. Martín Gómez")
    campo_telefono = crear_campo("Ej. +54 362 4123456", keyboard_type=ft.KeyboardType.PHONE)
    campo_correo = crear_campo("tutor@ejemplo.com", keyboard_type=ft.KeyboardType.EMAIL)

    def limpiar_formulario():
        for campo in [campo_nombre, campo_apellido, campo_fecha_nac, campo_dni, campo_tutor, campo_telefono, campo_correo]:
            campo.value = ""
        campo_nivel.value = None
        page.update()

    async def enviar_solicitud(e):
        # Validación de campos obligatorios
        if not campo_nombre.value or not campo_apellido.value or not campo_dni.value:
            mostrar_dialogo("Datos incompletos", "Complete nombre, apellido y DNI del postulante.", error=True)
            return
        if not campo_nivel.value:
            mostrar_dialogo("Datos incompletos", "Seleccione el nivel al que postula.", error=True)
            return
        if not campo_tutor.value:
            mostrar_dialogo("Datos incompletos", "Indique el nombre del padre, madre o tutor.", error=True)
            return

        payload = {
            "postulante": f"{campo_apellido.value.strip()}, {campo_nombre.value.strip()}",
            "dni": campo_dni.value.strip(),
            "fecha_nacimiento": (campo_fecha_nac.value or "").strip() or None,
            "nivel": campo_nivel.value,
            "tutor": campo_tutor.value.strip(),
            "telefono": (campo_telefono.value or "").strip() or None,
            "correo": (campo_correo.value or "").strip() or None,
        }

        try:
            solicitud = await api_client.crear_solicitud(payload)
        except httpx.HTTPStatusError:
            mostrar_dialogo(
                "No se pudo enviar",
                "Verifique los datos ingresados e intente nuevamente.",
                error=True,
            )
            return
        except Exception:
            mostrar_dialogo(
                "Sin conexión",
                "No se pudo conectar con el servidor. Intente más tarde.",
                error=True,
            )
            return

        anio = str(solicitud.get("fecha") or "")[:4]
        nro = f"#SOL-{anio}-{solicitud['id_solicitud']:04d}"
        limpiar_formulario()
        mostrar_dialogo(
            "¡Solicitud enviada con éxito!",
            f"Su solicitud de admisión fue registrada con el número {nro}. "
            "El equipo de secretaría se comunicará con usted para continuar el proceso.",
        )

    def mostrar_dialogo(titulo: str, mensaje: str, error: bool = False):
        dialogo = ft.AlertDialog(
            modal=True,
            bgcolor=BG_WHITE,
            title=ft.Text(
                titulo,
                size=17,
                weight=ft.FontWeight.BOLD,
                color="#B91C1C" if error else GREEN,
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

    # ==================== COLUMNA IZQUIERDA (FORMULARIO) ====================
    form_section = ft.Container(
        col={"sm": 12, "md": 8},
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=48,
        content=ft.Column(
            spacing=24,
            controls=[
                ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text("Formulario de Solicitud", size=28, weight=ft.FontWeight.BOLD, color=GREEN),
                        ft.Text("Por favor, complete los datos para iniciar el proceso de postulación.", size=14, color=MUTED),
                    ],
                ),
                # Datos del Postulante
                ft.Text("DATOS DEL POSTULANTE", size=16, weight=ft.FontWeight.BOLD, color=ORANGE),
                ft.ResponsiveRow(
                    columns=12,
                    controls=[
                        input_field("Nombre", campo_nombre, 6),
                        input_field("Apellido", campo_apellido, 6),
                        input_field("Fecha de Nacimiento", campo_fecha_nac, 6),
                        input_field("DNI", campo_dni, 6),
                        ft.Container(
                            col={"sm": 12, "md": 12},
                            content=ft.Column(
                                spacing=8,
                                controls=[
                                    ft.Text("Nivel al que postula", size=13, weight=ft.FontWeight.W_500, color=TEXT_COLOR),
                                    campo_nivel,
                                ],
                            ),
                        ),
                    ],
                ),
                ft.Divider(color=BORDER_COLOR, height=20),
                # Datos del Padre / Tutor
                ft.Text("DATOS DEL PADRE / TUTOR", size=16, weight=ft.FontWeight.BOLD, color=ORANGE),
                ft.ResponsiveRow(
                    columns=12,
                    controls=[
                        input_field("Nombre y Apellido Completo", campo_tutor, 12),
                        input_field("Teléfono de Contacto", campo_telefono, 6),
                        input_field("Correo Electrónico", campo_correo, 6),
                    ],
                ),
                ft.Button(
                    "ENVIAR SOLICITUD DE POSTULACIÓN",
                    bgcolor=TEAL,
                    color="white",
                    height=44,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=enviar_solicitud,
                ),
            ],
        ),
    )

    # ==================== BARRA LATERAL (SIDEBAR) ====================
    requisitos = [
        "DNI del alumno y ambos padres (original y copia)",
        "Partida de nacimiento legalizada",
        "Certificado de libre deuda del colegio anterior (si aplica)",
        "Informe psicopedagógico (nivel inicial)",
        "Certificado de aptitud física médica para natación",
        "Constancia de vacunas de calendario completo",
    ]

    sidebar_section = ft.Container(
        col={"sm": 12, "md": 4},
        content=ft.Column(
            spacing=32,
            controls=[
                # Tarjeta Requisitos
                ft.Container(
                    bgcolor=GREEN,
                    border_radius=16,
                    padding=40,
                    content=ft.Column(
                        spacing=24,
                        controls=[
                            ft.Text("Requisitos de Inscripción", size=24, weight=ft.FontWeight.BOLD, color="white"),
                            ft.Column(
                                spacing=16,
                                controls=[
                                    ft.Row(
                                        spacing=12,
                                        vertical_alignment=ft.CrossAxisAlignment.START,
                                        controls=[
                                            ft.Container(
                                                width=20,
                                                height=20,
                                                bgcolor=TEAL,
                                                border_radius=10,
                                                alignment=ft.Alignment(0, 0),
                                                content=ft.Icon(ft.Icons.CHECK, color="white", size=12),
                                            ),
                                            ft.Container(
                                                expand=True,
                                                content=ft.Text(req, size=14, color="white"),
                                            ),
                                        ],
                                    )
                                    for req in requisitos
                                ],
                            ),
                        ],
                    ),
                ),
                # Tarjeta Ayuda / Contacto
                ft.Container(
                    bgcolor=BG_WHITE,
                    border=ft.Border.all(1, BORDER_COLOR),
                    border_radius=16,
                    padding=40,
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            ft.Text("¿Tiene dudas?", size=18, weight=ft.FontWeight.BOLD, color=GREEN),
                            ft.Text(
                                "Nuestro equipo de admisiones está disponible para guiarlo paso a paso. Agende una reunión presencial o telefónica.",
                                size=14,
                                color=MUTED,
                            ),
                            ft.Button(
                                "📞 +54 362 445-8900",
                                bgcolor="transparent",
                                color=TEAL,
                                url="tel:+543624458900",
                                style=ft.ButtonStyle(overlay_color="transparent", elevation=0, padding=0),
                            ),
                            ft.Button(
                                "💬 WhatsApp: +54 9 362 455-1212",
                                bgcolor="transparent",
                                color=TEAL,
                                url="https://wa.me/5493624551212",
                                style=ft.ButtonStyle(overlay_color="transparent", elevation=0, padding=0),
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )

    # ==================== CONTENEDOR PRINCIPAL ====================
    main_layout = ft.Container(
        padding=ft.Padding.symmetric(horizontal=80, vertical=96),
        content=ft.ResponsiveRow(
            columns=12,
            spacing=64,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[form_section, sidebar_section],
        ),
    )

    return [main_layout]
