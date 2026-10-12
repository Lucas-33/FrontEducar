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


def get_empleo_view(page: ft.Page) -> list[ft.Control]:
    """Retorna la vista de Oportunidades Laborales y Postulación en Educar para Transformar."""

    vacantes = [
        {"puesto": "Profesor/a de Nivel Secundario — Ciencias Exactas", "area": "Física y Química / Matemática", "jornada": "Jornada Completa", "sede": "Resistencia"},
        {"puesto": "Docente de Idioma Francés / Inglés", "area": "Departamento de Lenguas Extranjeras", "jornada": "Part-Time", "sede": "Resistencia"},
        {"puesto": "Enfermero/a Profesional Matriculado/a", "area": "Gabinete de Salud y Enfermería", "jornada": "Turno Mañana (07:30 a 14:00)", "sede": "Resistencia"},
        {"puesto": "Chofer para Micro Escolar (Licencia D2)", "area": "Servicio de Transporte Institucional", "jornada": "Jornada Extendida", "sede": "Resistencia"},
    ]

    def item_vacante(v: dict) -> ft.Container:
        return ft.Container(
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=BORDER_RADIUS,
            padding=20,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(v["puesto"], size=16, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Text(v["area"], size=13, color=MUTED),
                                    ft.Text("•", size=13, color=MUTED),
                                    ft.Text(v["jornada"], size=13, weight=ft.FontWeight.W_500, color=ORANGE),
                                    ft.Text("•", size=13, color=MUTED),
                                    ft.Text(v["sede"], size=13, color=MUTED),
                                ],
                            ),
                        ],
                    ),
                    ft.Button(
                        "POSTULARME",
                        bgcolor=TEAL_LIGHT,
                        color=TEAL_DARK,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
                        on_click=lambda _: None,
                    ),
                ],
            ),
        )

    # FORMULARIO DE ENVÍO DE CV
    form_postulacion = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=40,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text("Formulario de Postulación Espontánea", size=22, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Text("Si su perfil no coincide con las búsquedas abiertas, puede dejarnos sus antecedentes para futuras vacantes.", size=13, color=MUTED),
                ft.ResponsiveRow(
                    columns=12,
                    spacing=16,
                    controls=[
                        ft.Container(
                            col={"sm": 12, "md": 6},
                            content=ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text("Nombre y Apellido *", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                    ft.TextField(hint_text="Ej: María Eugenia Romero", border_color=BORDER_COLOR, focused_border_color=TEAL, height=CONTROL_HEIGHT, text_size=14, border_radius=BORDER_RADIUS),
                                ],
                            ),
                        ),
                        ft.Container(
                            col={"sm": 12, "md": 6},
                            content=ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text("Correo Electrónico *", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                    ft.TextField(hint_text="postulante@ejemplo.com", border_color=BORDER_COLOR, focused_border_color=TEAL, height=CONTROL_HEIGHT, text_size=14, border_radius=BORDER_RADIUS),
                                ],
                            ),
                        ),
                        ft.Container(
                            col={"sm": 12, "md": 6},
                            content=ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text("Área / Especialidad Docente o Técnica *", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                    ft.TextField(hint_text="Ej: Ciencias Biológicas, Conducción, Preceptoría", border_color=BORDER_COLOR, focused_border_color=TEAL, height=CONTROL_HEIGHT, text_size=14, border_radius=BORDER_RADIUS),
                                ],
                            ),
                        ),
                        ft.Container(
                            col={"sm": 12, "md": 6},
                            content=ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text("Adjuntar CV (PDF) *", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                    ft.Container(
                                        height=CONTROL_HEIGHT,
                                        bgcolor=BG_PAGE_ALT,
                                        border=ft.Border.all(1, BORDER_COLOR),
                                        border_radius=BORDER_RADIUS,
                                        padding=ft.Padding(12, 0, 12, 0),
                                        content=ft.Row(
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            controls=[
                                                ft.Text("Seleccionar archivo curriculum.pdf...", size=13, color=MUTED),
                                                ft.Icon(ft.Icons.UPLOAD_FILE_OUTLINED, size=18, color=TEAL),
                                            ],
                                        ),
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
                ft.Button(
                    "ENVIAR ANTECEDENTES",
                    bgcolor=TEAL,
                    color=BG_WHITE,
                    height=CONTROL_HEIGHT,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
                    on_click=lambda _: None,
                ),
            ],
        ),
    )

    main_section = ft.Container(
        bgcolor=BG_PAGE_ALT,
        padding=ft.Padding.symmetric(horizontal=80, vertical=80),
        content=ft.Column(
            spacing=48,
            controls=[
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Text("TRABAJA CON NOSOTROS", size=13, weight=ft.FontWeight.BOLD, color=ORANGE, text_align=ft.TextAlign.CENTER),
                        ft.Text("Oportunidades de Empleo", size=36, weight=ft.FontWeight.BOLD, color=TEAL_DARK, text_align=ft.TextAlign.CENTER),
                        ft.Text("Sumate al equipo de profesionales comprometidos con transformar la educación en el Chaco.", size=15, color=MUTED, text_align=ft.TextAlign.CENTER),
                    ],
                ),
                ft.Column(spacing=12, controls=[item_vacante(v) for v in vacantes]),
                form_postulacion,
            ],
        ),
    )

    return [main_section]