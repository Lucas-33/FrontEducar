import flet as ft
from frontend.app.components.constants import (
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    MUTED,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.form_controls import status_badge
from frontend.app.components.portal_layout import portal_layout


def get_padre_dashboard_view(page: ft.Page) -> ft.Row:
    """Retorna el panel principal del padre/tutor con selector interactivo de hijos."""

    # DATOS DE LOS HIJOS ASOCIADOS AL TUTOR (Regla: Un padre puede tener uno o varios hijos)
    hijos = [
        {
            "id": 1,
            "nombre": "Santiago Almirón",
            "legajo": "#10245",
            "nivel": "Nivel Secundario",
            "curso": "5to Año División B",
            "turno": "Jornada Extendida (07:30 a 17:30 hs)",
            "deportes": ["Natación Climatizada", "Fútbol Campo"],
            "comedor": "Activo (Turno Intermedio)",
            "transporte": "Recorrido 1 Norte (Parada Sarmiento)",
            "estado": "Regular",
        },
        {
            "id": 2,
            "nombre": "Sofía Valentina Díaz",
            "legajo": "#10248",
            "nivel": "Nivel Inicial",
            "curso": "Sala de 5 años B",
            "turno": "Jornada Extendida (08:00 a 16:00 hs)",
            "deportes": ["Danza Contemporánea"],
            "comedor": "Activo (Menú Infantil)",
            "transporte": "Recorrido 4 Este",
            "estado": "Regular",
        },
    ]

    hijo_seleccionado = {"idx": 0}

    # CONTENEDOR REACTIVO DEL DETALLE
    detalle_container = ft.Column(spacing=20)

    def render_detalle():
        h = hijos[hijo_seleccionado["idx"]]
        detalle_container.controls = [
            # Tarjeta de Datos Académicos
            ft.Container(
                bgcolor=BG_WHITE,
                border=ft.Border.all(1, BORDER_COLOR),
                border_radius=CARD_RADIUS,
                padding=24,
                content=ft.Column(
                    spacing=16,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=12,
                                    controls=[
                                        ft.Container(
                                            width=48,
                                            height=48,
                                            bgcolor=TEAL_LIGHT,
                                            border_radius=24,
                                            alignment=ft.Alignment(0, 0),
                                            content=ft.Icon(ft.Icons.SCHOOL, size=24, color=TEAL_DARK),
                                        ),
                                        ft.Column(
                                            spacing=2,
                                            controls=[
                                                ft.Text(h["nombre"], size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                                                ft.Text(f"{h['nivel']} · {h['curso']} · Legajo {h['legajo']}", size=13, color=MUTED),
                                            ],
                                        ),
                                    ],
                                ),
                                status_badge(h["estado"]),
                            ],
                        ),
                        ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                        ft.Row(
                            spacing=32,
                            controls=[
                                ft.Column([ft.Text("Régimen Escolar", size=11, color=MUTED), ft.Text(h["turno"], size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR)], spacing=3),
                                ft.Column([ft.Text("Ciclo Lectivo", size=11, color=MUTED), ft.Text("2027 (Activo)", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR)], spacing=3),
                            ],
                        ),
                    ],
                ),
            ),
            # Grilla de Servicios y Deportes Activos
            ft.ResponsiveRow(
                columns=12,
                spacing=20,
                controls=[
                    # Deportes
                    ft.Container(
                        col={"sm": 12, "md": 4},
                        bgcolor=BG_WHITE,
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=CARD_RADIUS,
                        padding=20,
                        content=ft.Column(
                            spacing=12,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("Deportes Inscriptos", size=15, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                                        ft.Icon(ft.Icons.FITNESS_CENTER, size=18, color=ORANGE),
                                    ],
                                ),
                                ft.Column(
                                    spacing=6,
                                    controls=[
                                        ft.Container(
                                            bgcolor=TEAL_LIGHT,
                                            border_radius=6,
                                            padding=8,
                                            content=ft.Text(f"• {dep}", size=13, weight=ft.FontWeight.W_500, color=TEAL_DARK),
                                        )
                                        for dep in h["deportes"]
                                    ],
                                ),
                                ft.TextButton("Modificar deportes", on_click=lambda _: page.go("/portal/padre/deportes")),
                            ],
                        ),
                    ),
                    # Comedor
                    ft.Container(
                        col={"sm": 12, "md": 4},
                        bgcolor=BG_WHITE,
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=CARD_RADIUS,
                        padding=20,
                        content=ft.Column(
                            spacing=12,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("Comedor Escolar", size=15, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                                        ft.Icon(ft.Icons.RESTAURANT, size=18, color=TEAL),
                                    ],
                                ),
                                ft.Text(h["comedor"], size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                ft.Text("Menú balanceado supervisado por nutricionistas.", size=12, color=MUTED),
                                ft.TextButton("Ver régimen de viandas", on_click=lambda _: page.go("/portal/padre/servicios")),
                            ],
                        ),
                    ),
                    # Transporte
                    ft.Container(
                        col={"sm": 12, "md": 4},
                        bgcolor=BG_WHITE,
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=CARD_RADIUS,
                        padding=20,
                        content=ft.Column(
                            spacing=12,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("Transporte Institucional", size=15, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                                        ft.Icon(ft.Icons.DIRECTIONS_BUS, size=18, color=TEAL),
                                    ],
                                ),
                                ft.Text(h["transporte"], size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                ft.Text("Seguimiento de micro escolar por recorrido.", size=12, color=MUTED),
                                ft.TextButton("Cambiar recorrido", on_click=lambda _: page.go("/portal/padre/servicios")),
                            ],
                        ),
                    ),
                ],
            ),
        ]

    # SELECTOR DE HIJOS (Botones de pestaña)
    botones_hijos = []
    for i, hijo in enumerate(hijos):
        activo = i == hijo_seleccionado["idx"]

        def cambiar_hijo(e, indice=i):
            hijo_seleccionado["idx"] = indice
            render_detalle()
            for idx_b, b in enumerate(botones_hijos):
                b.bgcolor = TEAL if idx_b == indice else BG_WHITE
                b.content.controls[1].color = "white" if idx_b == indice else TEXT_COLOR
                b.border = None if idx_b == indice else ft.Border.all(1, BORDER_COLOR)
                b.update()
            detalle_container.update()

        btn = ft.Container(
            height=46,
            bgcolor=TEAL if activo else BG_WHITE,
            border=None if activo else ft.Border.all(1, BORDER_COLOR),
            border_radius=BORDER_RADIUS,
            padding=ft.Padding(16, 0, 16, 0),
            on_click=cambiar_hijo,
            content=ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.PERSON, size=18, color="white" if activo else TEAL),
                    ft.Text(hijo["nombre"], size=14, weight=ft.FontWeight.BOLD, color="white" if activo else TEXT_COLOR),
                ],
            ),
        )
        botones_hijos.append(btn)

    selector_bar = ft.Row(
        spacing=12,
        controls=[
            ft.Text("Seleccionar Hijo:", size=14, weight=ft.FontWeight.W_600, color=TEAL_DARK),
            *botones_hijos,
        ],
    )

    render_detalle()

    return portal_layout(
        page=page,
        titulo="Panel de Familias — Información del Alumno",
        active_route="/portal/padre/dashboard",
        rol="Padre",
        content_controls=[
            selector_bar,
            detalle_container,
        ],
    )