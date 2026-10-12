import flet as ft
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


def get_opiniones_view(page: ft.Page) -> list[ft.Control]:
    """Retorna la vista de Testimonios y Formulario público para dejar opiniones sin login."""

    # 1. ESTADO Y TESTIMONIOS EXISTENTES
    testimonios_data = [
        {"nombre": "Carolina Ferreyra", "relacion": "Madre Nivel Primario", "estrellas": 5, "fecha": "04 Oct, 2026", "opinion": "La infraestructura deportiva y el natatorio climatizado son únicos en Resistencia. Mis dos hijos van felices y la jornada extendida les permite aprovechar cada minuto."},
        {"nombre": "Prof. Roberto Zampa", "relacion": "Docente Universitario", "estrellas": 5, "fecha": "28 Sep, 2026", "opinion": "El enfoque trilingüe y los laboratorios de ciencias marcan una diferencia notable en el nivel pedagógico con el que egresan los estudiantes secundarios."},
        {"nombre": "Mariana Gómez", "relacion": "Madre Nivel Inicial", "estrellas": 5, "fecha": "15 Sep, 2026", "opinion": "Excelente servicio de comedor y gabinete psicopedagógico. La adaptación en sala de 4 años fue sumamente cálida y personalizada por parte de las maestras."},
    ]

    def tarjeta_testimonio(t: dict) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 4},
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=24,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row([ft.Icon(ft.Icons.STAR, size=16, color=ORANGE) for _ in range(t["estrellas"])]),
                            ft.Text(t["fecha"], size=12, color=MUTED),
                        ],
                    ),
                    ft.Text(f'"{t["opinion"]}"', size=14, color=TEXT_COLOR, italic=True),
                    ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(t["nombre"], size=14, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ft.Text(t["relacion"], size=12, color=MUTED),
                        ],
                    ),
                ],
            ),
        )

    # 2. CONTROLES DEL FORMULARIO PÚBLICO
    nombre_input = ft.TextField(
        hint_text="Ej: Silvina Morales",
        text_size=14,
        color=TEXT_COLOR,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        border_radius=BORDER_RADIUS,
        height=CONTROL_HEIGHT,
        content_padding=ft.Padding(12, 10, 12, 10),
    )

    rol_dropdown = ft.Dropdown(
        value="Familia Aspirante",
        text_size=14,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        border_radius=BORDER_RADIUS,
        content_padding=ft.Padding(12, 0, 8, 12),
        options=[
            ft.dropdown.Option("Padre / Madre de Alumno"),
            ft.dropdown.Option("Familia Aspirante 2027"),
            ft.dropdown.Option("Exalumno / Comunidad"),
            ft.dropdown.Option("Vecino de Resistencia"),
        ],
    )

    opinion_input = ft.TextField(
        hint_text="Escriba aquí su experiencia, opinión o sugerencia para la institución...",
        text_size=14,
        color=TEXT_COLOR,
        multiline=True,
        min_lines=4,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        border_radius=BORDER_RADIUS,
    )

    alerta_mensaje = ft.Text("", size=13, weight=ft.FontWeight.W_600, color=TEAL)

    def enviar_opinion(e):
        if not nombre_input.value or not opinion_input.value:
            alerta_mensaje.value = "Por favor, complete su nombre y comentario antes de enviar."
            alerta_mensaje.color = "#EF4444"
        else:
            alerta_mensaje.value = "¡Gracias por su testimonio! Su opinión ha sido enviada para moderación."
            alerta_mensaje.color = TEAL
            nombre_input.value = ""
            opinion_input.value = ""
        alerta_mensaje.update()

    formulario_card = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=40,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text("Dejar una Opinión Pública", size=22, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Text("Los visitantes pueden compartir su experiencia con el centro educativo sin necesidad de registrarse ni iniciar sesión.", size=13, color=MUTED),
                ft.ResponsiveRow(
                    columns=12,
                    spacing=16,
                    controls=[
                        ft.Container(col={"sm": 12, "md": 6}, content=ft.Column([ft.Text("Su Nombre Completo *", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR), nombre_input], spacing=6)),
                        ft.Container(col={"sm": 12, "md": 6}, content=ft.Column([ft.Text("Vínculo con la Escuela", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR), rol_dropdown], spacing=6)),
                        ft.Container(col={"sm": 12}, content=ft.Column([ft.Text("Su Opinión o Comentario *", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR), opinion_input], spacing=6)),
                    ],
                ),
                alerta_mensaje,
                ft.Button(
                    "PUBLICAR MI OPINIÓN",
                    bgcolor=TEAL,
                    color=BG_WHITE,
                    height=CONTROL_HEIGHT,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
                    on_click=enviar_opinion,
                ),
            ],
        ),
    )

    # 3. ENSAMBLE DE LA VISTA
    main_section = ft.Container(
        bgcolor=BG_PAGE_ALT,
        padding=ft.Padding.symmetric(horizontal=80, vertical=80),
        content=ft.Column(
            spacing=56,
            controls=[
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Text("COMUNIDAD EDUCATIVA", size=13, weight=ft.FontWeight.BOLD, color=ORANGE, text_align=ft.TextAlign.CENTER),
                        ft.Text("Opiniones y Testimonios", size=36, weight=ft.FontWeight.BOLD, color=TEAL_DARK, text_align=ft.TextAlign.CENTER),
                        ft.Text("Conozca la voz de las familias, docentes y vecinos que forman parte de Educar para Transformar.", size=15, color=MUTED, text_align=ft.TextAlign.CENTER),
                    ],
                ),
                ft.ResponsiveRow(
                    columns=12,
                    spacing=20,
                    controls=[tarjeta_testimonio(t) for t in testimonios_data],
                ),
                formulario_card,
            ],
        ),
    )

    return [main_section]