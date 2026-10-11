# src/views/inscripcion.py
import flet as ft

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
    def input_field(label: str, hint: str, col_span: int = 6, keyboard_type: ft.KeyboardType = ft.KeyboardType.TEXT):
        return ft.Container(
            col={"sm": 12, "md": col_span},
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Text(label, size=13, weight=ft.FontWeight.W_500, color=TEXT_COLOR),
                    ft.TextField(
                        hint_text=hint,
                        keyboard_type=keyboard_type,
                        border_color=BORDER_COLOR,
                        focused_border_color=TEAL,
                        bgcolor="#FDFCFB",
                        border_radius=6,
                        content_padding=ft.Padding(12, 10, 12, 10),
                        text_size=14,
                    ),
                ],
            ),
        )

    # ==================== FORMULARIO PRINCIPAL ====================
    form_section = ft.Container(
        col={"sm": 12, "md": 8},
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=40,
        content=ft.Column(
            spacing=24,
            controls=[
                ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text("Formulario de Solicitud", size=28, weight=ft.FontWeight.BOLD, color=GREEN),
                        ft.Text("Por favor, complete los datos para iniciar el proceso de postulación 2025.", size=14, color=MUTED),
                    ],
                ),
                # Datos del Postulante
                ft.Text("DATOS DEL POSTULANTE", size=16, weight=ft.FontWeight.BOLD, color=ORANGE),
                ft.ResponsiveRow(
                    columns=12,
                    controls=[
                        input_field("Nombre", "Ej. Santiago", 6),
                        input_field("Apellido", "Ej. Gómez", 6),
                        input_field("Fecha de Nacimiento", "DD/MM/AAAA", 6),
                        input_field("DNI", "Sin puntos", 6, keyboard_type=ft.KeyboardType.NUMBER),
                        ft.Container(
                            col={"sm": 12, "md": 12},
                            content=ft.Column(
                                spacing=8,
                                controls=[
                                    ft.Text("Nivel al que postula", size=13, weight=ft.FontWeight.W_500, color=TEXT_COLOR),
                                    ft.Dropdown(
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
                                    ),
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
                        input_field("Nombre y Apellido Completo", "Ej. Martín Gómez", 12),
                        input_field("Teléfono de Contacto", "Ej. +54 362 4123456", 6, keyboard_type=ft.KeyboardType.PHONE),
                        input_field("Correo Electrónico", "tutor@ejemplo.com", 6, keyboard_type=ft.KeyboardType.EMAIL),
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
                    # Ejemplo para cuando le des funcionalidad:
                    # on_click=lambda e: print("Enviando formulario...")
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