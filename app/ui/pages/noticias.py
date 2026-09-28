# src/views/noticias.py
import flet as ft

# Variables de color extraídas de la identidad visual
GREEN = "#0B4F4F"
TEAL = "#0D6E6E"
TEAL_LIGHT = "#E6F2F2"
ORANGE = "#D97736"
TEXT_COLOR = "#1E2A29"
MUTED = "#5C6B69"
BORDER_COLOR = "#EAE6E1"
BG_WHITE = "#FFFFFF"

def get_noticias_view(page: ft.Page) -> list[ft.Control]:
    """Retorna únicamente los bloques centrales de la página Noticias."""

    # ==================== SECCIÓN DESTACADA (FEATURED) ====================
    featured_section = ft.Container(
        padding=ft.Padding(80, 96, 80, 48),
        content=ft.Column(
            spacing=40,
            controls=[
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Text("ACTUALIDAD", size=14, weight=ft.FontWeight.BOLD, color=ORANGE),
                        ft.Text("Portal de Novedades", size=36, weight=ft.FontWeight.BOLD, color=GREEN),
                    ],
                ),
                ft.Container(
                    bgcolor=BG_WHITE,
                    border=ft.Border.all(1, BORDER_COLOR),
                    border_radius=16,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=ft.ResponsiveRow(
                        columns=12,
                        spacing=0,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                col={"sm": 12, "md": 7},
                                content=ft.Image(
                                    src="https://images.unsplash.com/photo-1577896851231-70ef18881754?w=800&h=500&fit=crop",
                                    fit="cover",
                                    height=450,
                                ),
                            ),
                            ft.Container(
                                col={"sm": 12, "md": 5},
                                padding=ft.Padding(48, 48, 48, 48),
                                content=ft.Column(
                                    spacing=16,
                                    controls=[
                                        ft.Row(
                                            spacing=8,
                                            controls=[
                                                ft.Text("DESTACADO", size=12, weight=ft.FontWeight.BOLD, color=ORANGE),
                                                ft.Text("·  20 Oct, 2024", size=12, color=MUTED),
                                            ],
                                        ),
                                        ft.Text(
                                            "Nuevos Convenios Internacionales de Idioma",
                                            size=30,
                                            weight=ft.FontWeight.BOLD,
                                            color=GREEN,
                                            height=1.2,
                                        ),
                                        ft.Text(
                                            "Nos complace anunciar una alianza estratégica para certificar los niveles de inglés con Cambridge y de francés con la Alianza Francesa, potenciando el perfil global de nuestros graduados.",
                                            size=15,
                                            color=MUTED,
                                        ),
                                        ft.Container(height=10),
                                        ft.Button(
                                            "LEER ARTÍCULO COMPLETO",
                                            bgcolor=TEAL,
                                            color="white",
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(radius=8),
                                            ),
                                            # on_click=lambda _: page.run_task(page.push_route, "/noticias/convenios")
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )

    # ==================== DATA Y GRILLA DE NOTICIAS ====================
    noticias_data = [
        {
            "categoria": "comunidad",
            "cat_label": "Comunidad",
            "fecha": "18 Oct",
            "titulo": "Proyecto Ecológico: Huerta en Inicial",
            "img": "https://images.unsplash.com/photo-1592417817098-8f3d6eb22510?w=405&h=180&fit=crop",
        },
        {
            "categoria": "deportes",
            "cat_label": "Deportes",
            "fecha": "14 Oct",
            "titulo": "Convocatoria para el Club de Ajedrez",
            "img": "https://images.unsplash.com/photo-1529699211952-734e80c4d42b?w=405&h=180&fit=crop",
        },
        {
            "categoria": "academicas",
            "cat_label": "Académicas",
            "fecha": "09 Oct",
            "titulo": "Ganadores de las Olimpiadas Matemáticas",
            "img": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=405&h=180&fit=crop",
        },
        {
            "categoria": "eventos",
            "cat_label": "Eventos",
            "fecha": "05 Oct",
            "titulo": "Visita al Parque Nacional Chaco",
            "img": "https://images.unsplash.com/photo-1448375240586-882707db888b?w=405&h=180&fit=crop",
        },
        {
            "categoria": "comunidad",
            "cat_label": "Comunidad",
            "fecha": "28 Sep",
            "titulo": "Charla de Salud y Nutrición Escolar",
            "img": "https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=405&h=180&fit=crop",
        },
        {
            "categoria": "eventos",
            "cat_label": "Eventos",
            "fecha": "20 Sep",
            "titulo": "Inscripciones Abiertas Ciclo Lectivo 2025",
            "img": "https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=405&h=180&fit=crop",
        },
    ]

    card_controls = []
    for item in noticias_data:
        card = ft.Container(
            col={"sm": 12, "md": 4},
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=16,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Image(src=item["img"], height=180, fit="cover"),
                    ft.Container(
                        padding=24,
                        content=ft.Column(
                            spacing=10,
                            controls=[
                                ft.Row(
                                    spacing=6,
                                    controls=[
                                        ft.Text(item["cat_label"].upper(), size=11, weight=ft.FontWeight.BOLD, color=ORANGE),
                                        ft.Text(f"· {item['fecha']}", size=11, color=MUTED),
                                    ],
                                ),
                                ft.Text(item["titulo"], size=18, weight=ft.FontWeight.BOLD, color=GREEN, height=1.35),
                            ],
                        ),
                    ),
                ],
            ),
            data=item["categoria"],  # Guardamos la categoría para filtrado
        )
        card_controls.append(card)

    news_grid = ft.ResponsiveRow(
        columns=12,
        spacing=32,
        run_spacing=32,
        controls=card_controls,
    )

    # ==================== FILTRADO REACTIVO ====================
    categoria_activa = "todas"
    filter_buttons = []

    def filtrar_noticias(e):
        nonlocal categoria_activa
        categoria_activa = e.control.data

        # Actualizar estilo de los botones de filtro
        for btn in filter_buttons:
            if btn.data == categoria_activa:
                btn.bgcolor = TEAL
                btn.color = "white"
                btn.style = ft.ButtonStyle(side=ft.BorderSide(1, TEAL))
            else:
                btn.bgcolor = BG_WHITE
                btn.color = TEXT_COLOR
                btn.style = ft.ButtonStyle(side=ft.BorderSide(1, BORDER_COLOR))
            btn.update()

        # Mostrar/Ocultar tarjetas
        for c in card_controls:
            c.visible = (categoria_activa == "todas") or (c.data == categoria_activa)
        news_grid.update()

    filtros = [
        ("Todas", "todas"),
        ("Académicas", "academicas"),
        ("Deportes", "deportes"),
        ("Eventos", "eventos"),
        ("Comunidad", "comunidad"),
    ]

    for label, slug in filtros:
        es_activo = slug == categoria_activa
        btn = ft.Button(
            label,
            data=slug,
            bgcolor=TEAL if es_activo else BG_WHITE,
            color="white" if es_activo else TEXT_COLOR,
            on_click=filtrar_noticias,
            style=ft.ButtonStyle(
                side=ft.BorderSide(1, TEAL if es_activo else BORDER_COLOR),
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.Padding(18, 8, 18, 8),
            ),
        )
        filter_buttons.append(btn)

    filters_row = ft.Row(
        spacing=12,
        wrap=True,
        controls=filter_buttons,
    )

    news_section = ft.Container(
        padding=ft.Padding(80, 0, 80, 96),
        content=ft.Column(
            spacing=36,
            controls=[filters_row, news_grid],
        ),
    )

    return [featured_section, news_section]