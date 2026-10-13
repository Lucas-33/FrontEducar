import flet as ft
from frontend.app.components.constants import (
    AMBER_STATE,
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


def get_docente_dashboard_view(page: ft.Page) -> ft.Row:
    """Retorna el panel principal del portal docente."""

    # ==================== 1. BANNER DOCENTE ====================
    banner_docente = ft.Container(
        bgcolor=TEAL_DARK,
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text("¡Buen día, Prof. Román Martínez!", size=22, weight=ft.FontWeight.BOLD, color=BG_WHITE),
                        ft.Text("Legajo #20101 · Departamento de Ciencias Naturales y Exactas · Ciclo 2027", size=13, color=TEAL_LIGHT),
                    ],
                ),
                ft.Button(
                    content=ft.Row(
                        spacing=6,
                        controls=[
                            ft.Icon(ft.Icons.CHECKLIST, size=16, color=BG_WHITE),
                            ft.Text("Tomar Asistencia Hoy", size=13, weight=ft.FontWeight.W_600, color=BG_WHITE),
                        ],
                    ),
                    bgcolor=ORANGE,
                    height=38,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
                    on_click=lambda _: page.go("/portal/docente/alumnos"),
                ),
            ],
        ),
    )

    # ==================== 2. TARJETAS DE RESUMEN ====================
    def kpi_docente(titulo: str, valor: str, subtitulo: str, icono: ft.IconData, bg_icon: str) -> ft.Container:
        return ft.Container(
            expand=True,
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
                            ft.Text(titulo, size=12, weight=ft.FontWeight.W_600, color=MUTED),
                            ft.Container(
                                width=34,
                                height=34,
                                bgcolor=bg_icon,
                                border_radius=8,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(icono, size=18, color=TEAL_DARK),
                            ),
                        ],
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(valor, size=26, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ft.Text(subtitulo, size=11, color=MUTED),
                        ],
                    ),
                ],
            ),
        )

    kpis_row = ft.Row(
        spacing=16,
        controls=[
            kpi_docente("MATERIAS A CARGO", "3", "Física, Química y Lab.", ft.Icons.MENU_BOOK_OUTLINED, TEAL_LIGHT),
            kpi_docente("CURSOS ASIGNADOS", "2", "4to Año A y 5to Año B", ft.Icons.PEOPLE_OUTLINE, TEAL_LIGHT),
            kpi_docente("HORAS SEMANALES", "18 hs", "Carga lectiva frente a curso", ft.Icons.SCHEDULE, TEAL_LIGHT),
            kpi_docente("ALUMNOS TOTALES", "58", "Activos en nómina", ft.Icons.SCHOOL_OUTLINED, TEAL_LIGHT),
        ],
    )

    # ==================== 3. CRONOGRAMA DE CLASES DE HOY ====================
    clases_hoy = [
        {"hora": "07:30 - 09:00 hs", "materia": "Física y Química", "curso": "5to Año B", "aula": "Aula 12 (Pabellón B)", "estado": "Finalizada"},
        {"hora": "09:15 - 10:45 hs", "materia": "Laboratorio de Ciencias", "curso": "5to Año B", "aula": "Laboratorio Central", "estado": "En Curso"},
        {"hora": "11:00 - 12:30 hs", "materia": "Física I", "curso": "4to Año A", "aula": "Aula 8", "estado": "Próxima"},
    ]

    def item_clase(c: dict) -> ft.Container:
        es_en_curso = c["estado"] == "En Curso"
        return ft.Container(
            bgcolor=TEAL_LIGHT if es_en_curso else BG_PAGE,
            border_radius=BORDER_RADIUS,
            padding=14,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=14,
                        controls=[
                            ft.Container(
                                width=4,
                                height=38,
                                border_radius=2,
                                bgcolor=TEAL if es_en_curso else MUTED,
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(f"{c['materia']} — {c['curso']}", size=14, weight=ft.FontWeight.BOLD, color=TEAL_DARK if es_en_curso else TEXT_COLOR),
                                    ft.Text(f"{c['hora']} · Espacio: {c['aula']}", size=12, color=MUTED),
                                ],
                            ),
                        ],
                    ),
                    ft.Container(
                        padding=ft.Padding(8, 3, 8, 3),
                        bgcolor=ONLINE_GREEN if es_en_curso else BG_WHITE,
                        border_radius=4,
                        content=ft.Text(
                            c["estado"],
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=BG_WHITE if es_en_curso else MUTED,
                        ),
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
                        ft.Text("Cronograma de Clases para Hoy", size=17, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                        ft.TextButton("Ver Semana Completa", on_click=lambda _: page.go("/portal/docente/materias")),
                    ],
                ),
                ft.Column(spacing=10, controls=[item_clase(c) for c in clases_hoy]),
            ],
        ),
    )

    # ==================== 4. AVISOS INSTITUCIONALES ====================
    avisos_card = ft.Container(
        width=380,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Comunicaciones de Dirección", size=17, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Container(
                    bgcolor="#FFF3E7",
                    border_radius=BORDER_RADIUS,
                    padding=14,
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text("Cierre de Notas 1er Trimestre", size=13, weight=ft.FontWeight.BOLD, color=ORANGE),
                            ft.Text("El sistema cerrará actas el viernes 23 a las 18:00 hs.", size=12, color=TEXT_COLOR),
                        ],
                    ),
                ),
                ft.Container(
                    bgcolor=TEAL_LIGHT,
                    border_radius=BORDER_RADIUS,
                    padding=14,
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text("Reserva de Laboratorios", size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ft.Text("Recordar asentar con 24 hs de anticipación los reactivos requeridos a pañol.", size=12, color=TEXT_COLOR),
                        ],
                    ),
                ),
            ],
        ),
    )

    fila_inferior = ft.Row(
        spacing=24,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[agenda_card, avisos_card],
    )

    return portal_layout(
        page=page,
        titulo="Panel Docente — Mi Actividad",
        active_route="/portal/docente/dashboard",
        rol="Docente",
        usuario_nombre="Prof. Román Martínez",
        usuario_sub="Legajo #20101 · Ciencias Exactas",
        content_controls=[
            banner_docente,
            kpis_row,
            fila_inferior,
        ],
    )