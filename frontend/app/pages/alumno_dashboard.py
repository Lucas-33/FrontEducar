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
from frontend.app.components.portal_layout import portal_layout


def get_alumno_dashboard_view(page: ft.Page) -> ft.Row:
    """Retorna el panel principal del estudiante con carnet digital y agenda diaria."""

    # ==================== 1. BANNER ESTUDIANTE ====================
    banner_alumno = ft.Container(
        bgcolor=TEAL_DARK,
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=16,
                    controls=[
                        ft.Container(
                            width=54,
                            height=54,
                            bgcolor=TEAL_LIGHT,
                            border_radius=27,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Text("SA", size=20, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                        ),
                        ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text("¡Hola, Santiago Almirón!", size=22, weight=ft.FontWeight.BOLD, color=BG_WHITE),
                                ft.Text("Legajo #10245 · 5to Año División B · Ciclo Lectivo 2027", size=13, color=TEAL_LIGHT),
                            ],
                        ),
                    ],
                ),
                ft.Container(
                    bgcolor=ONLINE_GREEN,
                    border_radius=BORDER_RADIUS,
                    padding=ft.Padding(12, 6, 12, 6),
                    content=ft.Text("MATRÍCULA REGULAR", size=11, weight=ft.FontWeight.BOLD, color=BG_WHITE),
                ),
            ],
        ),
    )

    # ==================== 2. TARJETAS DE MÉTRICAS ====================
    def kpi_alumno(titulo: str, valor: str, subtitulo: str, icono: ft.IconData, color_bg: str) -> ft.Container:
        return ft.Container(
            expand=True,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=20,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(titulo, size=11, weight=ft.FontWeight.W_600, color=MUTED),
                            ft.Container(
                                width=32,
                                height=32,
                                bgcolor=color_bg,
                                border_radius=8,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(icono, size=16, color=TEAL_DARK),
                            ),
                        ],
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(valor, size=24, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ft.Text(subtitulo, size=11, color=MUTED),
                        ],
                    ),
                ],
            ),
        )

    kpis_row = ft.Row(
        spacing=16,
        controls=[
            kpi_alumno("PROMEDIO GENERAL", "8.50", "1er Trimestre", ft.Icons.AUTO_GRAPH, TEAL_LIGHT),
            kpi_alumno("ASISTENCIA GLOBAL", "94%", "2 inasistencias justificadas", ft.Icons.HOW_TO_REG, "#EBFEE6"),
            kpi_alumno("MATERIAS CURSANDO", "6", "Plan Orientado", ft.Icons.MENU_BOOK_OUTLINED, TEAL_LIGHT),
            kpi_alumno("DEPORTES ACTIVOS", "2 de 2", "Natación y Fútbol", ft.Icons.FITNESS_CENTER_OUTLINED, "#FFF3E7"),
        ],
    )

    # ==================== 3. HORARIO DE HOY ====================
    clases_hoy = [
        {"hora": "07:30 - 09:00 hs", "materia": "Matemática Aplicada", "profesor": "Prof. Guillermina Sánchez", "aula": "Aula 12"},
        {"hora": "09:15 - 10:45 hs", "materia": "Física y Química", "profesor": "Prof. Román Martínez", "aula": "Laboratorio Central"},
        {"hora": "12:30 - 13:30 hs", "materia": "Almuerzo Institucional", "profesor": "Comedor Turno Intermedio", "aula": "Salón Comedor"},
        {"hora": "16:30 - 18:00 hs", "materia": "Natación Climatizada", "profesor": "Prof. Esteban Vargas", "aula": "Natatorio Olímpico"},
    ]

    def item_clase(c: dict) -> ft.Container:
        es_comedor = "Almuerzo" in c["materia"]
        es_deporte = "Natación" in c["materia"]
        color_barra = ORANGE if es_comedor else (ONLINE_GREEN if es_deporte else TEAL)

        return ft.Container(
            bgcolor=BG_PAGE,
            border_radius=BORDER_RADIUS,
            padding=14,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.Container(width=4, height=36, border_radius=2, bgcolor=color_barra),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(c["materia"], size=14, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                                    ft.Text(f"{c['profesor']} · Espacio: {c['aula']}", size=12, color=MUTED),
                                ],
                            ),
                        ],
                    ),
                    ft.Container(
                        padding=ft.Padding(8, 4, 8, 4),
                        bgcolor=BG_WHITE,
                        border_radius=4,
                        content=ft.Text(c["hora"], size=12, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                    ),
                ],
            ),
        )

    agenda_card = ft.Container(
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
                        ft.Text("Mi Horario y Actividades de Hoy", size=17, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                        ft.TextButton("Ver Todas las Materias", on_click=lambda _: page.go("/portal/alumno/materias")),
                    ],
                ),
                ft.Column(spacing=10, controls=[item_clase(c) for c in clases_hoy]),
            ],
        ),
    )

    # ==================== 4. CARNET DIGITAL ESTUDIANTIL ====================
    carnet_card = ft.Container(
        width=380,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Credencial Digital Estudiantil", size=16, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Container(
                    width=280,
                    bgcolor=TEAL_LIGHT,
                    border=ft.Border.all(1, TEAL),
                    border_radius=12,
                    padding=20,
                    content=ft.Column(
                        spacing=12,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("EDUCAR SGE", size=11, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                                    ft.Icon(ft.Icons.NFC, size=16, color=TEAL),
                                ],
                            ),
                            ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=54, color=TEAL),
                            ft.Column(
                                spacing=2,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text("Santiago Almirón", size=15, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                                    ft.Text("Legajo: #10245 · DNI: 46.124.990", size=11, color=MUTED),
                                    ft.Text("5to Año B · Secundario", size=12, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                ],
                            ),
                            ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=6,
                                controls=[
                                    ft.Icon(ft.Icons.QR_CODE, size=18, color=TEAL_DARK),
                                    ft.Text("Válido ciclo lectivo 2027", size=10, color=MUTED),
                                ],
                            ),
                        ],
                    ),
                ),
                ft.Text("Habilitado para Comedor, Traslado y Biblioteca.", size=11, color=MUTED, text_align=ft.TextAlign.CENTER),
            ],
        ),
    )

    fila_inferior = ft.Row(
        spacing=24,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[agenda_card, carnet_card],
    )

    return portal_layout(
        page=page,
        titulo="Portal del Estudiante — Mi Cursado",
        active_route="/portal/alumno/dashboard",
        rol="Alumno",
        usuario_nombre="Santiago Almirón",
        usuario_sub="Legajo #10245 · 5to Año B",
        content_controls=[
            banner_alumno,
            kpis_row,
            fila_inferior,
        ],
    )