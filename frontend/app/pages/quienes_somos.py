# src/views/quienes_somos.py
import flet as ft

# Variables de color
GREEN = "#0B4F4F"
TEAL = "#117C7C"
TEAL_LIGHT = "#E6F2F2"
ORANGE = "#D97736"
MUTED = "#5C6B69"

def get_quienes_somos_view(page: ft.Page) -> list[ft.Control]:
    """Retorna únicamente los bloques centrales de la página Quiénes Somos."""

    # ==================== SECCIÓN INTRO (HISTORIA Y FILOSOFÍA) ====================
    intro = ft.Container(
        padding=ft.Padding.symmetric(horizontal=80, vertical=96),
        content=ft.ResponsiveRow(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            columns=12,
            controls=[
                ft.Container(
                    col={"sm": 12, "md": 7},
                    content=ft.Column(
                        spacing=16,
                        controls=[
                            ft.Text("CONOCENOS", size=14, weight=ft.FontWeight.BOLD, color=ORANGE),
                            ft.Text(
                                "Nuestra Historia y Filosofía",
                                size=36,
                                weight=ft.FontWeight.BOLD,
                                color=GREEN,
                                height=1.2,
                            ),
                            ft.Text(
                                "Fundado en la ciudad de Resistencia, Chaco, el Colegio Privado “Educar para Transformar” nació con el firme propósito de redefinir el paradigma educativo tradicional. Creemos en una educación activa, donde el alumno sea protagonista de su propio aprendizaje y desarrolle valores sólidos para ser un ciudadano global ético.",
                                size=16,
                                color=MUTED,
                            ),
                            ft.Text(
                                "Nuestra institución se destaca por su propuesta de jornada extendida, inmersión lingüística en múltiples idiomas (inglés, portugués y francés), y una robusta infraestructura deportiva y tecnológica que prepara a los líderes del mañana.",
                                size=16,
                                color=MUTED,
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    col={"sm": 12, "md": 5},
                    border_radius=16,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=ft.Image(
                        src="https://images.unsplash.com/photo-1541829070764-84a7d30dd3f3?w=600&h=380&fit=crop",
                        fit="cover",
                        height=380,
                    ),
                ),
            ],
        ),
    )

    # ==================== SECCIÓN PURPOSE (MISIÓN Y VISIÓN) ====================
    def tarjeta_proposito(titulo: str, descripcion: str):
        return ft.Container(
            col={"sm": 12, "md": 6},
            bgcolor=TEAL,
            border_radius=16,
            padding=40,
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Text(titulo, size=28, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text(
                        descripcion,
                        size=16,
                        color=TEAL_LIGHT,
                    ),
                ],
            ),
        )

    proposito = ft.Container(
        bgcolor=GREEN,
        padding=ft.Padding.symmetric(horizontal=80, vertical=80),
        content=ft.ResponsiveRow(
            columns=12,
            controls=[
                tarjeta_proposito(
                    "Nuestra Misión",
                    "Inspiramos, desafiamos y empoderamos a todos nuestros alumnos a ser miembros comprometidos y éticos de una comunidad global. Buscamos formar mentes abiertas y corazones solidarios listos para el futuro.",
                ),
                tarjeta_proposito(
                    "Nuestra Visión",
                    "Ser reconocidos como el centro educativo líder en el nordeste argentino por nuestra innovación pedagógica, excelencia académica, bilingüismo, y el alto compromiso social y medioambiental de nuestros egresados.",
                ),
            ],
        ),
    )

    # ==================== SECCIÓN GALLERY (CAMPUS) ====================
    galeria = ft.Container(
        padding=ft.Padding.symmetric(horizontal=80, vertical=96),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Text("GALERÍA", size=14, weight=ft.FontWeight.BOLD, color=ORANGE),
                ft.Text("La Vida en Nuestro Campus", size=36, weight=ft.FontWeight.BOLD, color=GREEN),
                ft.Container(height=20),
                ft.ResponsiveRow(
                    columns=12,
                    controls=[
                        ft.Container(
                            col={"sm": 12, "md": 4},
                            border_radius=16,
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                            content=ft.Image(
                                src="https://images.unsplash.com/photo-1509062522246-3755977927d7?w=405&h=400&fit=crop",
                                fit="cover",
                                height=400,
                            ),
                        ),
                        ft.Container(
                            col={"sm": 12, "md": 5},
                            border_radius=16,
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                            content=ft.Image(
                                src="https://images.unsplash.com/photo-1577896851231-70ef18881754?w=515&h=400&fit=crop",
                                fit="cover",
                                height=400,
                            ),
                        ),
                        ft.Container(
                            col={"sm": 12, "md": 3},
                            border_radius=16,
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                            content=ft.Image(
                                src="https://images.unsplash.com/photo-1588072432836-e10032774350?w=296&h=400&fit=crop",
                                fit="cover",
                                height=400,
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )

    return [intro, proposito, galeria]