import flet as ft
from frontend.app.components.constants import (
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    MUTED,
    ONLINE_GREEN,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.form_controls import status_badge
from frontend.app.components.portal_layout import portal_layout


def get_alumno_deportes_view(page: ft.Page) -> ft.Row:
    """Retorna las disciplinas deportivas en las que participa el estudiante."""

    deportes_alumno = [
        {
            "disciplina": "Natación Climatizada",
            "profesor": "Prof. Esteban Carlos Vargas",
            "dias": "Lunes y Miércoles 16:30 - 18:00 hs",
            "instalacion": "Natatorio Olímpico Cubierto",
            "apto_medico": "Aprobado (Dr. Ruiz)",
            "icono": ft.Icons.POOL,
        },
        {
            "disciplina": "Fútbol Campo",
            "profesor": "Prof. Germán Acuña",
            "dias": "Martes y Jueves 16:30 - 18:00 hs",
            "instalacion": "Cancha 1 (Césped Sintético)",
            "apto_medico": "Aprobado (Dra. Ponce)",
            "icono": ft.Icons.SPORTS_SOCCER,
        },
    ]

    def tarjeta_deporte(d: dict) -> ft.Container:
        return ft.Container(
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
                                        width=44,
                                        height=44,
                                        bgcolor=TEAL_LIGHT,
                                        border_radius=22,
                                        alignment=ft.Alignment(0, 0),
                                        content=ft.Icon(d["icono"], size=22, color=TEAL_DARK),
                                    ),
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(d["disciplina"], size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                                            ft.Text(f"A cargo de: {d['profesor']}", size=13, color=MUTED),
                                        ],
                                    ),
                                ],
                            ),
                            status_badge("Activo"),
                        ],
                    ),
                    ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                    ft.Row(
                        spacing=20,
                        controls=[
                            ft.Column([ft.Text("Días y Horarios", size=11, color=MUTED), ft.Text(d["dias"], size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR)], spacing=3),
                            ft.Column([ft.Text("Instalación", size=11, color=MUTED), ft.Text(d["instalacion"], size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR)], spacing=3),
                        ],
                    ),
                    ft.Container(
                        bgcolor="#EBFEE6",
                        border_radius=BORDER_RADIUS,
                        padding=12,
                        content=ft.Row(
                            spacing=8,
                            controls=[
                                ft.Icon(ft.Icons.CHECK_CIRCLE, size=16, color=ONLINE_GREEN),
                                ft.Text(f"Apto físico y médico: {d['apto_medico']}", size=12, weight=ft.FontWeight.W_600, color=ONLINE_GREEN),
                            ],
                        ),
                    ),
                ],
            ),
        )

    deportes_row = ft.Row(
        spacing=20,
        controls=[tarjeta_deporte(d) for d in deportes_alumno],
    )

    regla_info = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
        padding=16,
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE, size=20, color=TEAL),
                ft.Text("Cupo de disciplinas completado: Contás con las 2 actividades deportivas permitidas en simultáneo.", size=13, color=TEAL_DARK, weight=ft.FontWeight.W_500),
            ],
        ),
    )

    return portal_layout(
        page=page,
        titulo="Mis Deportes y Actividades Físicas",
        active_route="/portal/alumno/deportes",
        rol="Alumno",
        usuario_nombre="Santiago Almirón",
        usuario_sub="Legajo #10245 · 5to Año B",
        content_controls=[
            regla_info,
            deportes_row,
        ],
    )