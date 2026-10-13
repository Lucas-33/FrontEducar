import flet as ft
from frontend.app.components.constants import (
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    MUTED,
    ONLINE_GREEN,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.form_controls import status_badge
from frontend.app.components.portal_layout import portal_layout


def get_alumno_servicios_view(page: ft.Page) -> ft.Row:
    """Retorna la consulta de servicios de comedor escolar y transporte institucional."""

    # 1. COMEDOR ESCOLAR
    comedor_card = ft.Container(
        expand=True,
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
                                    width=40,
                                    height=40,
                                    bgcolor=TEAL_LIGHT,
                                    border_radius=20,
                                    alignment=ft.Alignment(0, 0),
                                    content=ft.Icon(ft.Icons.RESTAURANT, size=20, color=TEAL_DARK),
                                ),
                                ft.Text("Comedor Escolar", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ],
                        ),
                        status_badge("Activo"),
                    ],
                ),
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                ft.Column(
                    spacing=8,
                    controls=[
                        ft.Row([ft.Text("Turno asignado:", size=13, color=MUTED), ft.Text("Intermedio (12:30 a 13:30 hs)", size=13, weight=ft.FontWeight.BOLD, color=TEXT_COLOR)]),
                        ft.Row([ft.Text("Menú registrado:", size=13, color=MUTED), ft.Text("Estándar K-12 Balanceado", size=13, weight=ft.FontWeight.BOLD, color=TEXT_COLOR)]),
                        ft.Row([ft.Text("Alergias o intolerancias:", size=13, color=MUTED), ft.Text("Ninguna registrada", size=13, weight=ft.FontWeight.W_500, color=TEXT_COLOR)]),
                    ],
                ),
                ft.Container(
                    bgcolor=BG_PAGE,
                    border_radius=BORDER_RADIUS,
                    padding=12,
                    content=ft.Text("Plato del día: Pollo al horno con puré de calabaza y fruta de estación.", size=12, color=TEXT_COLOR),
                ),
            ],
        ),
    )

    # 2. TRANSPORTE ESCOLAR (4 RECORRIDOS)
    transporte_card = ft.Container(
        expand=True,
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
                                    width=40,
                                    height=40,
                                    bgcolor=TEAL_LIGHT,
                                    border_radius=20,
                                    alignment=ft.Alignment(0, 0),
                                    content=ft.Icon(ft.Icons.DIRECTIONS_BUS, size=20, color=TEAL_DARK),
                                ),
                                ft.Text("Transporte Institucional", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ],
                        ),
                        status_badge("Activo"),
                    ],
                ),
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                ft.Column(
                    spacing=8,
                    controls=[
                        ft.Row([ft.Text("Recorrido asignado:", size=13, color=MUTED), ft.Text("Recorrido 1 Norte (Micro M-01)", size=13, weight=ft.FontWeight.BOLD, color=TEAL)]),
                        ft.Row([ft.Text("Parada asignada:", size=13, color=MUTED), ft.Text("Av. Sarmiento 1840", size=13, weight=ft.FontWeight.BOLD, color=TEXT_COLOR)]),
                        ft.Row([ft.Text("Horario de recogida:", size=13, color=MUTED), ft.Text("06:45 hs (Turno Mañana)", size=13, weight=ft.FontWeight.BOLD, color=TEXT_COLOR)]),
                        ft.Row([ft.Text("Chofer a cargo:", size=13, color=MUTED), ft.Text("Mario Gómez (Celador: Estela Ríos)", size=13, color=MUTED)]),
                    ],
                ),
                ft.Container(
                    bgcolor=BG_PAGE,
                    border_radius=BORDER_RADIUS,
                    padding=12,
                    content=ft.Text("Recordá presentarte 5 minutos antes en la parada asignada con tu credencial.", size=12, color=MUTED),
                ),
            ],
        ),
    )

    servicios_row = ft.Row(
        spacing=20,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[comedor_card, transporte_card],
    )

    return portal_layout(
        page=page,
        titulo="Mis Servicios: Comedor y Transporte",
        active_route="/portal/alumno/servicios",
        rol="Alumno",
        usuario_nombre="Santiago Almirón",
        usuario_sub="Legajo #10245 · 5to Año B",
        content_controls=[
            servicios_row,
        ],
    )