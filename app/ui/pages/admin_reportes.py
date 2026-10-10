import flet as ft
from app.ui.components.sidebar import create_sidebar
from app.ui.components.topbar import create_topbar

# Paleta cromática y tokens visuales
BG_PAGE = "#F5F7F7"
BG_WHITE = "#FFFFFF"
BORDER_COLOR = "#EAE6E1"
TEAL_DARK = "#0B4F4F"
TEAL = "#0D6E6E"
TEAL_LIGHT = "#E6F2F2"
ORANGE = "#D97736"
TEXT_COLOR = "#1E2A29"
MUTED = "#5C6B69"
GREEN_STATE = "#10B981"
RED_STATE = "#EF4444"


def get_admin_reportes_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa del Módulo General de Reportes y Estadísticas."""

    # ==================== 1. TARJETAS DE CATEGORÍAS DE REPORTES ====================
    def categoria_card(titulo: str, descripcion: str, icono: ft.IconData) -> ft.Container:
        return ft.Container(
            width=360,
            height=116,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=12,
            padding=20,
            on_click=lambda _: None,
            content=ft.Column(
                spacing=12,
                alignment=ft.MainAxisAlignment.START,
                controls=[
                    ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=32,
                                height=32,
                                bgcolor=TEAL_LIGHT,
                                border_radius=8,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(icono, size=16, color=TEAL_DARK),
                            ),
                            ft.Text(
                                titulo,
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                        ],
                    ),
                    ft.Text(
                        descripcion,
                        size=13,
                        color=MUTED,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
            ),
        )

    categorias_data = [
        ("Reporte por Alumno", "Progreso individual, inasistencias y comportamiento consolidado.", ft.Icons.PERSON_OUTLINE),
        ("Reporte por Docente", "Horas cátedra dictadas, asignaciones de materias y licencias.", ft.Icons.WORK_OUTLINE),
        ("Listado por Curso", "Nóminas completas filtradas por grado, turno y nivel académico.", ft.Icons.PEOPLE_OUTLINE),
        ("Listado por Materia", "Estadísticas de rendimiento, promedios y aprobados por trimestre.", ft.Icons.MENU_BOOK_OUTLINED),
        ("Listado por Deporte", "Alumnos inscriptos por disciplina deportiva para control médico.", ft.Icons.FITNESS_CENTER_OUTLINED),
        ("Listado por Transporte", "Hojas de ruta por zona con datos de tutores y teléfonos.", ft.Icons.DIRECTIONS_BUS_OUTLINED),
    ]

    seccion_categorias = ft.Column(
        spacing=16,
        controls=[
            ft.Text(
                "Categorías de Reportes Disponibles",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=TEAL_DARK,
            ),
            ft.Row(
                wrap=True,
                spacing=16,
                run_spacing=16,
                controls=[categoria_card(t, d, i) for t, d, i in categorias_data],
            ),
        ],
    )

    # ==================== 2. VISTA PREVIA DE REPORTE FILTRADO ====================
    alumnos_deporte_data = [
        {
            "legajo": "#10245",
            "alumno": "Almirón, Santiago",
            "curso": "5to Año B",
            "ficha": "Aprobada (Vence Oct 25)",
            "ficha_color": GREEN_STATE,
            "seguro": "Al Día",
        },
        {
            "legajo": "#10249",
            "alumno": "Flores, Facundo Joaquín",
            "curso": "6to Año A",
            "ficha": "Aprobada (Vence Nov 25)",
            "ficha_color": GREEN_STATE,
            "seguro": "Al Día",
        },
        {
            "legajo": "#10252",
            "alumno": "Pérez, Juan Manuel",
            "curso": "2do Año C",
            "ficha": "Pendiente Presentar",
            "ficha_color": RED_STATE,
            "seguro": "Al Día",
        },
    ]

    header_reporte = ft.Container(
        height=39,
        bgcolor=BG_PAGE,
        padding=ft.Padding(12, 0, 12, 0),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(width=120, content=ft.Text("Legajo", size=12, weight=ft.FontWeight.BOLD, color=TEXT_COLOR)),
                ft.Container(width=220, content=ft.Text("Alumno", size=12, weight=ft.FontWeight.BOLD, color=TEXT_COLOR)),
                ft.Container(width=150, content=ft.Text("Curso", size=12, weight=ft.FontWeight.BOLD, color=TEXT_COLOR)),
                ft.Container(width=180, content=ft.Text("Ficha Médica", size=12, weight=ft.FontWeight.BOLD, color=TEXT_COLOR)),
                ft.Container(expand=True, content=ft.Text("Seguro Escolar", size=12, weight=ft.FontWeight.BOLD, color=TEXT_COLOR)),
            ],
        ),
    )

    def reporte_row(item: dict, con_borde: bool = True) -> ft.Container:
        return ft.Container(
            height=40,
            padding=ft.Padding(12, 0, 12, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)) if con_borde else None,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=120, content=ft.Text(item["legajo"], size=13, weight=ft.FontWeight.W_600, color=TEAL)),
                    ft.Container(width=220, content=ft.Text(item["alumno"], size=13, color=TEXT_COLOR)),
                    ft.Container(width=150, content=ft.Text(item["curso"], size=13, color=TEXT_COLOR)),
                    ft.Container(
                        width=180,
                        content=ft.Text(item["ficha"], size=13, weight=ft.FontWeight.W_500, color=item["ficha_color"]),
                    ),
                    ft.Container(expand=True, content=ft.Text(item["seguro"], size=13, color=TEXT_COLOR)),
                ],
            ),
        )

    tabla_preview = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=12,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            spacing=0,
            controls=[
                header_reporte,
                reporte_row(alumnos_deporte_data[0], con_borde=True),
                reporte_row(alumnos_deporte_data[1], con_borde=True),
                reporte_row(alumnos_deporte_data[2], con_borde=False),
            ],
        ),
    )

    preview_card = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text(
                                    "Vista Previa de Reporte Filtrado: Alumnos por Deporte (Natación)",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEAL_DARK,
                                ),
                                ft.Text(
                                    "Listado oficial de alumnos con ficha médica habilitada para el natatorio del complejo.",
                                    size=13,
                                    color=MUTED,
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Button(
                                    content=ft.Row(
                                        spacing=8,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Icon(ft.Icons.FILE_DOWNLOAD_OUTLINED, size=14, color=TEAL_DARK),
                                            ft.Text("Exportar Excel", size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                                        ],
                                    ),
                                    bgcolor=TEAL_LIGHT,
                                    height=32,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                        padding=ft.Padding(16, 8, 16, 8),
                                    ),
                                    on_click=lambda _: None,
                                ),
                                ft.Button(
                                    content=ft.Row(
                                        spacing=8,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Icon(ft.Icons.PRINT_OUTLINED, size=14, color=BG_WHITE),
                                            ft.Text("Imprimir PDF", size=13, weight=ft.FontWeight.W_600, color=BG_WHITE),
                                        ],
                                    ),
                                    bgcolor=ORANGE,
                                    height=32,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                        padding=ft.Padding(16, 8, 16, 8),
                                    ),
                                    on_click=lambda _: None,
                                ),
                            ],
                        ),
                    ],
                ),
                tabla_preview,
            ],
        ),
    )

    # ==================== 3. ENSAMBLE DEL LAYOUT ====================
    sidebar = create_sidebar(page, active_route="/admin/reportes")
    topbar = create_topbar(page, titulo="Módulo General de Reportes y Estadísticas")

    main_content = ft.Container(
        expand=True,
        bgcolor=BG_PAGE,
        content=ft.Column(
            spacing=0,
            controls=[
                topbar,
                ft.Container(
                    expand=True,
                    padding=32,
                    content=ft.Column(
                        spacing=32,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            seccion_categorias,
                            preview_card,
                        ],
                    ),
                ),
            ],
        ),
    )

    return ft.Row(
        expand=True,
        spacing=0,
        controls=[sidebar, main_content],
    )


if __name__ == "__main__":
    def main(page: ft.Page):
        page.title = "Educar SGE - Reportes y Estadísticas"
        page.padding = 0
        page.bgcolor = BG_PAGE
        page.add(get_admin_reportes_view(page))

    ft.run(main)