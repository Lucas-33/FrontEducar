import flet as ft
import httpx


TEAL_DARK = "#0B4F4F"
TEAL = "#0D6E6E"
TEAL_LIGHT = "#E6F2F2"
ORANGE = "#D97736"
TEXT_SECONDARY = "#5C6B69"
BG_WHITE = "#FFFFFF"

def home_view(page: ft.Page) -> list[ft.Control]:
    """Retorna los bloques centrales de la página de Inicio."""

    def header_seccion(tag: str, titulo: str):
        return ft.Column(
            spacing=8,
            controls=[
                ft.Text(tag.upper(), size=14, weight=ft.FontWeight.BOLD, color=ORANGE),
                ft.Text(titulo, size=36, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
            ],
        )

    # ==================== HERO ====================
    hero = ft.Container(
        padding=ft.Padding.symmetric(horizontal=80, vertical=96),
        content=ft.ResponsiveRow(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            columns=12,
            controls=[
                ft.Container(
                    col={"sm": 12, "md": 7},
                    content=ft.Column(
                        spacing=24,
                        controls=[
                            ft.Container(
                                bgcolor=TEAL_LIGHT,
                                border_radius=20,
                                padding=ft.Padding.symmetric(horizontal=16, vertical=6),
                                content=ft.Text(
                                    "ADMISIONES ABIERTAS 2025",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEAL_DARK,
                                ),
                            ),
                            ft.Text(
                                "Educar para Transformar",
                                size=56,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                                height=1.1,
                            ),
                            ft.Text(
                                "Inspiramos, desafiamos y empoderamos a todos nuestros alumnos a ser miembros comprometidos y éticos de una comunidad global.",
                                size=18,
                                color=TEXT_SECONDARY,
                            ),
                            ft.Row(
                                spacing=16,
                                controls=[
                                    ft.Button(
                                        "INICIAR INSCRIPCIÓN",
                                        bgcolor=ORANGE,
                                        color=BG_WHITE,
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                        on_click=lambda _: page.run_task(page.push_route, "/inscripcion"),
                                    ),
                                    ft.Button(
                                        "CONOCER PROYECTO EDUCATIVO",
                                        bgcolor="transparent",
                                        color=TEAL_DARK,
                                        style=ft.ButtonStyle(
                                            side=ft.BorderSide(1.5, TEAL_DARK),
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                        ),
                                        on_click=lambda _: page.run_task(page.push_route, "/quienes-somos"),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    col={"sm": 12, "md": 5},
                    border_radius=16,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=ft.Image(
                        src="https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=600&h=450&fit=crop",
                        fit="cover",
                        height=450,
                    ),
                ),
            ],
        ),
    )

    # ==================== NIVELES EDUCATIVOS ====================
    def tarjeta_nivel(icono, titulo, edad, descripcion):
        return ft.Container(
            col={"sm": 12, "md": 4},
            bgcolor=BG_WHITE,
            border_radius=16,
            padding=32,
            border=ft.Border.all(1, "#EAE8E4"),
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Container(
                        width=48,
                        height=48,
                        bgcolor=TEAL_LIGHT,
                        border_radius=12,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(icono, color=TEAL, size=24),
                    ),
                    ft.Text(titulo, size=24, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                    ft.Text(edad, size=14, weight=ft.FontWeight.BOLD, color=ORANGE),
                    ft.Text(descripcion, size=15, color=TEXT_SECONDARY),
                ],
            ),
        )

    niveles = ft.Container(
        padding=ft.Padding.symmetric(horizontal=80, vertical=96),
        content=ft.Column(
            spacing=56,
            controls=[
                header_seccion("Formación Integral", "Niveles Educativos"),
                ft.ResponsiveRow(
                    columns=12,
                    controls=[
                        tarjeta_nivel(
                            ft.Icons.CHILD_CARE,
                            "Inicial",
                            "Salas de 3, 4 y 5 años",
                            "Estimulación temprana, juego guiado y desarrollo socio-emocional en un entorno cálido y seguro.",
                        ),
                        tarjeta_nivel(
                            ft.Icons.MENU_BOOK,
                            "Primario",
                            "6 a 12 años",
                            "Foco en competencias lingüísticas, pensamiento lógico-matemático y descubrimiento del entorno.",
                        ),
                        tarjeta_nivel(
                            ft.Icons.SCHOOL,
                            "Secundario",
                            "13 a 18 años",
                            "Formación académica rigurosa, orientación vocacional y desarrollo de mentalidad de impacto global.",
                        ),
                    ],
                ),
            ],
        ),
    )

    # ==================== DEPORTES E INFRAESTRUCTURA ====================
    deportes_items = ["Natación", "Fútbol", "Atletismo", "Artes Marciales", "Vóley", "Danza", "Básquet", "Ajedrez"]

    def item_instalacion(icono, titulo, descripcion):
        return ft.Row(
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Container(
                    width=40,
                    height=40,
                    bgcolor=TEAL_LIGHT,
                    border_radius=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(icono, color=TEAL, size=20),
                ),
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                        ft.Text(descripcion, size=13, color=TEXT_SECONDARY),
                    ],
                ),
            ],
        )

    deportes = ft.Container(
        bgcolor=TEAL_LIGHT,
        padding=ft.Padding.symmetric(horizontal=80, vertical=96),
        content=ft.Column(
            spacing=56,
            controls=[
                header_seccion("Estilo de vida saludable", "Deportes e Infraestructura"),
                ft.ResponsiveRow(
                    columns=12,
                    controls=[
                        ft.Container(
                            col={"sm": 12, "md": 6},
                            bgcolor=BG_WHITE,
                            border_radius=16,
                            padding=40,
                            content=ft.Column(
                                spacing=24,
                                controls=[
                                    ft.Text("Formación Deportiva", size=24, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                                    ft.Text(
                                        "Fomentamos la disciplina, el compañerismo y la superación a través de un programa de deportes integrados de primer nivel:",
                                        size=15,
                                        color=TEXT_SECONDARY,
                                    ),
                                    ft.Row(
                                        wrap=True,
                                        spacing=10,
                                        run_spacing=10,
                                        controls=[
                                            ft.Container(
                                                padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                                                bgcolor=TEAL_LIGHT,
                                                border_radius=20,
                                                content=ft.Text(tag, size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                                            )
                                            for tag in deportes_items
                                        ],
                                    ),
                                ],
                            ),
                        ),
                        ft.Container(
                            col={"sm": 12, "md": 6},
                            bgcolor=BG_WHITE,
                            border_radius=16,
                            padding=40,
                            content=ft.Column(
                                spacing=20,
                                controls=[
                                    ft.Text("Instalaciones Destacadas", size=24, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                                    item_instalacion(
                                        ft.Icons.POOL,
                                        "Natatorio Olímpico",
                                        "Climatizado para natación recreativa y competitiva durante todo el año.",
                                    ),
                                    item_instalacion(
                                        ft.Icons.BIOTECH,
                                        "Laboratorios Modernos",
                                        "Espacios de experimentación avanzada en informática, física y química.",
                                    ),
                                    item_instalacion(
                                        ft.Icons.SPORTS_SOCCER,
                                        "Pista de Atletismo",
                                        "Pista profesional al aire libre y canchas de fútbol con césped sintético.",
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )

    # ==================== NOTICIAS ====================
    def tarjeta_noticia(img_url, fecha, titulo, extracto):
        return ft.Container(
            col={"sm": 12, "md": 4},
            bgcolor=BG_WHITE,
            border_radius=16,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            border=ft.Border.all(1, "#EAE8E4"),
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Image(src=img_url, height=180, fit="cover"),
                    ft.Container(
                        padding=24,
                        content=ft.Column(
                            spacing=10,
                            controls=[
                                ft.Text(fecha, size=12, weight=ft.FontWeight.BOLD, color=ORANGE),
                                ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                                ft.Text(extracto, size=14, color=TEXT_SECONDARY),
                            ],
                        ),
                    ),
                ],
            ),
        )

    noticias = ft.Container(
        padding=ft.Padding.symmetric(horizontal=80, vertical=96),
        content=ft.Column(
            spacing=56,
            controls=[
                header_seccion("Vida Institucional", "Últimas Novedades"),
                ft.ResponsiveRow(
                    columns=12,
                    controls=[
                        tarjeta_noticia(
                            "https://images.unsplash.com/photo-1562774053-701939374585?w=405&h=180&fit=crop",
                            "15 Oct, 2024",
                            "Inauguración del Nuevo Laboratorio de Ciencias",
                            "Ampliamos nuestra infraestructura tecnológica con equipamiento de física y química de última generación.",
                        ),
                        tarjeta_noticia(
                            "https://images.unsplash.com/photo-1530549387789-4c1017266635?w=405&h=180&fit=crop",
                            "10 Oct, 2024",
                            "Torneo Intercolegial de Natación",
                            "Nuestros alumnos de primaria y secundaria participaron con excelentes resultados en el podio regional.",
                        ),
                        tarjeta_noticia(
                            "https://images.unsplash.com/photo-1567168544813-cc03465b4fa8?w=405&h=180&fit=crop",
                            "02 Oct, 2024",
                            "Feria de Ciencias & Tecnología",
                            "Un espacio donde los estudiantes presentaron sus proyectos innovadores bajo metodologías STEAM.",
                        ),
                    ],
                ),
            ],
        ),
    )

    return [hero, niveles, deportes, noticias]