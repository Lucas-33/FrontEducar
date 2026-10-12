import flet as ft
from frontend.app.components.constants import (
    BG_PAGE_ALT,
    BG_WHITE,
    BORDER_COLOR,
    MUTED,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)


def get_bienestar_estudiantil_view(page: ft.Page) -> list[ft.Control]:
    """Retorna los bloques de la página de Bienestar Estudiantil, Deportes e Infraestructura."""

    def header_seccion(tag: str, titulo: str, descripcion: str) -> ft.Column:
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Text(tag.upper(), size=13, weight=ft.FontWeight.BOLD, color=ORANGE, text_align=ft.TextAlign.CENTER),
                ft.Text(titulo, size=34, weight=ft.FontWeight.BOLD, color=TEAL_DARK, text_align=ft.TextAlign.CENTER),
                ft.Text(descripcion, size=15, color=MUTED, text_align=ft.TextAlign.CENTER, max_lines=2),
            ],
        )

    # 1. SERVICIOS DE APOYO Y CUIDADO INTEGRAL
    def tarjeta_servicio(icono: ft.IconData, titulo: str, detalle: str, destacado: str) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 4},
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=16,
            padding=32,
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Container(
                        width=48,
                        height=48,
                        bgcolor=TEAL_LIGHT,
                        border_radius=24,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(icono, size=24, color=TEAL_DARK),
                    ),
                    ft.Text(titulo, size=20, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                    ft.Text(detalle, size=14, color=MUTED, height=1.4),
                    ft.Container(
                        bgcolor=TEAL_LIGHT,
                        border_radius=6,
                        padding=ft.Padding(8, 4, 8, 4),
                        content=ft.Text(destacado, size=12, weight=ft.FontWeight.W_600, color=TEAL),
                    ),
                ],
            ),
        )

    servicios_section = ft.Container(
        bgcolor=BG_PAGE_ALT,
        padding=ft.Padding.symmetric(horizontal=80, vertical=80),
        content=ft.Column(
            spacing=48,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                header_seccion(
                    "Cuidado y Acompañamiento",
                    "Servicios de Bienestar Estudiantil",
                    "Garantizamos un entorno seguro, saludable y propicio para el desarrollo de cada estudiante.",
                ),
                ft.ResponsiveRow(
                    columns=12,
                    spacing=24,
                    controls=[
                        tarjeta_servicio(
                            ft.Icons.PSYCHOLOGY_OUTLINED,
                            "Gabinete Psicopedagógico",
                            "Acompañamiento en el aprendizaje, orientación vocacional y contención socio-emocional permanente.",
                            "Atención K-12",
                        ),
                        tarjeta_servicio(
                            ft.Icons.MEDICAL_SERVICES_OUTLINED,
                            "Servicio de Enfermería",
                            "Atención médica de primeros auxilios y seguimiento de fichas de salud durante toda la jornada extendida.",
                            "Enfermeros matriculados",
                        ),
                        tarjeta_servicio(
                            ft.Icons.RESTAURANT_OUTLINED,
                            "Comedor Institucional",
                            "Almuerzos supervisados por nutricionistas matriculados, adaptados a requerimientos celíacos e intolerancias.",
                            "Menú balanceado diario",
                        ),
                    ],
                ),
            ],
        ),
    )

    # 2. INSTALACIONES Y DEPORTES DESTACADOS
    deportes_items = [
        ("Natación Climatizada", "Pileta semiolímpica cubierta para entrenamiento formativo y recreativo."),
        ("Atletismo de Pista", "Pista profesional al aire libre para velocidad, fondo y salto."),
        ("Fútbol Campo", "Canchas de césped sintético y natural reglamentarias con iluminación LED."),
        ("Artes Marciales", "Dojo con tatami profesional para la práctica de Taekwondo y defensa personal."),
        ("Vóleibol Formativo", "Canchas cubiertas en el polideportivo para entrenamiento escolar y competitivo."),
        ("Danza Contemporánea", "Salón con espejos y piso flotante para expresión corporal y rítmica."),
        ("Básquetbol", "Gimnasio techado con piso de parquet homologado y tableros profesionales."),
        ("Ajedrez Estratégico", "Taller de pensamiento lógico en espacios acondicionados de biblioteca."),
    ]

    def item_deporte_card(titulo: str, desc: str) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 6, "lg": 3},
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=12,
            padding=20,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.CHECK_CIRCLE, size=16, color=ORANGE),
                            ft.Text(titulo, size=15, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                        ],
                    ),
                    ft.Text(desc, size=13, color=MUTED),
                ],
            ),
        )

    deportes_section = ft.Container(
        bgcolor=TEAL_LIGHT,
        padding=ft.Padding.symmetric(horizontal=80, vertical=80),
        content=ft.Column(
            spacing=40,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                header_seccion(
                    "Formación Atlética",
                    "Deportes e Infraestructura de Alto Nivel",
                    "Hasta dos disciplinas simultáneas por alumno, guiadas por profesores de educación física especializados.",
                ),
                ft.ResponsiveRow(
                    columns=12,
                    spacing=16,
                    run_spacing=16,
                    controls=[item_deporte_card(t, d) for t, d in deportes_items],
                ),
            ],
        ),
    )

    # 3. LABORATORIOS Y TECNOLOGÍA
    laboratorios_section = ft.Container(
        bgcolor=BG_WHITE,
        padding=ft.Padding.symmetric(horizontal=80, vertical=80),
        content=ft.ResponsiveRow(
            columns=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    col={"sm": 12, "md": 6},
                    content=ft.Column(
                        spacing=20,
                        controls=[
                            ft.Text("ESPACIOS DE CIENCIA Y TECNOLOGÍA", size=13, weight=ft.FontWeight.BOLD, color=ORANGE),
                            ft.Text("Laboratorios Modernos de Informática, Física y Química", size=32, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ft.Text(
                                "Nuestras instalaciones ubicadas a las afueras de Resistencia cuentan con equipamiento de nivel universitario para fomentar el pensamiento científico desde el nivel primario.",
                                size=15,
                                color=MUTED,
                            ),
                            ft.Row(
                                spacing=16,
                                controls=[
                                    ft.Button(
                                        "SOLICITAR VISITA GUIADA",
                                        bgcolor=TEAL,
                                        color=BG_WHITE,
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                        on_click=lambda _: page.go("/contacto"),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    col={"sm": 12, "md": 6},
                    border_radius=16,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=ft.Image(
                        src="https://images.unsplash.com/photo-1562774053-701939374585?w=600&h=400&fit=crop",
                        fit="cover",
                        height=360,
                    ),
                ),
            ],
        ),
    )

    return [servicios_section, deportes_section, laboratorios_section]