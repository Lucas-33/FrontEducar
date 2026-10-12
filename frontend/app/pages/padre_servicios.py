import flet as ft
from frontend.app.components.constants import (
    BG_PAGE,
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
from frontend.app.components.portal_layout import portal_layout


def get_padre_servicios_view(page: ft.Page) -> ft.Row:
    """Retorna la vista para gestionar Comedor Escolar y Transporte Institucional (4 Recorridos)."""

    # 1. TARJETA COMEDOR
    comedor_card = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=28,
        content=ft.Column(
            spacing=18,
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
                                ft.Text("Servicio de Comedor Escolar", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ],
                        ),
                        ft.Switch(value=True, active_color=TEAL),
                    ],
                ),
                ft.Text("Almuerzo diario durante la jornada extendida supervisado por nutricionistas matriculados.", size=13, color=MUTED),
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                ft.ResponsiveRow(
                    columns=12,
                    spacing=16,
                    controls=[
                        ft.Container(
                            col={"sm": 12, "md": 6},
                            content=ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text("Menú Nutricional Asignado", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                    ft.Dropdown(
                                        value="Estándar K-12",
                                        text_size=14,
                                        border_color=BORDER_COLOR,
                                        border_radius=BORDER_RADIUS,
                                        content_padding=ft.Padding(12, 0, 8, 12),
                                        options=[
                                            ft.dropdown.Option("Estándar K-12"),
                                            ft.dropdown.Option("Menú Celíaco (Sin TACC)"),
                                            ft.dropdown.Option("Vegetariano"),
                                            ft.dropdown.Option("Intolerancia a la Lactosa"),
                                        ],
                                    ),
                                ],
                            ),
                        ),
                        ft.Container(
                            col={"sm": 12, "md": 6},
                            content=ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text("Turno de Comedor Asignado", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                    ft.Container(
                                        height=CONTROL_HEIGHT,
                                        bgcolor=BG_PAGE,
                                        border=ft.Border.all(1, BORDER_COLOR),
                                        border_radius=BORDER_RADIUS,
                                        padding=ft.Padding(12, 0, 12, 0),
                                        alignment=ft.Alignment(-1, 0),
                                        content=ft.Text("Turno Intermedio (12:30 a 13:30 hs)", size=14, color=MUTED),
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )

    # 2. TARJETA TRANSPORTE (Regla: El servicio de transporte tiene 4 recorridos)[cite: 6]
    recorridos = [
        ("Recorrido 1 Norte", "Av. Sarmiento, La Liguria, Villa San Martín — Chofer: Mario Gómez"),
        ("Recorrido 2 Sur", "Fontana, Av. Castelli, Av. Alvear — Chofer: Carlos Valdez"),
        ("Recorrido 3 Centro", "Barranqueras, Plaza 25 de Mayo, Pellegrini — Chofer: Jorge Acosta"),
        ("Recorrido 4 Este", "Ruta 16, Aeropuerto, Autovía Nicolás Avellaneda — Chofer: Daniel Soto"),
    ]

    recorrido_seleccionado = {"valor": "Recorrido 1 Norte"}

    transporte_card = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=28,
        content=ft.Column(
            spacing=18,
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
                                ft.Text("Servicio de Micros de Traslado (4 Recorridos)", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ],
                        ),
                        ft.Switch(value=True, active_color=TEAL),
                    ],
                ),
                ft.Text("Seleccione el recorrido correspondiente al domicilio de residencia para la asignación de parada y celador.", size=13, color=MUTED),
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                ft.Column(
                    spacing=10,
                    controls=[
                        ft.RadioGroup(
                            value=recorrido_seleccionado["valor"],
                            content=ft.Column(
                                spacing=10,
                                controls=[
                                    ft.Radio(value=nombre, label=f"{nombre} ({detalle})", fill_color=TEAL)
                                    for nombre, detalle in recorridos
                                ],
                            ),
                        ),
                    ],
                ),
                ft.Row(
                    spacing=16,
                    controls=[
                        ft.TextField(
                            hint_text="Indique dirección exacta de parada (Ej: Av. Sarmiento 1840)",
                            value="Av. Sarmiento 1840, Resistencia",
                            text_size=14,
                            border_color=BORDER_COLOR,
                            focused_border_color=TEAL,
                            border_radius=BORDER_RADIUS,
                            expand=True,
                            height=CONTROL_HEIGHT,
                        ),
                    ],
                ),
            ],
        ),
    )

    return portal_layout(
        page=page,
        titulo="Gestión de Servicios Complementarios",
        active_route="/portal/padre/servicios",
        rol="Padre",
        content_controls=[
            comedor_card,
            transporte_card,
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.Button(
                        "CONFIRMAR MODIFICACIÓN DE SERVICIOS",
                        bgcolor=TEAL,
                        color="white",
                        height=CONTROL_HEIGHT,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
                        on_click=lambda _: None,
                    ),
                ],
            ),
        ],
    )