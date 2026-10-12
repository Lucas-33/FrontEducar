import flet as ft
from frontend.app.components.admin_layout import admin_layout
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


def get_admin_reportes_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa del Módulo General de Reportes y Estadísticas usando AdminLayout."""

    # ==================== 1. TARJETAS DE CATEGORÍAS DE REPORTES ====================
    def categoria_card(titulo: str, descripcion: str, icono: ft.IconData, ruta: str | None = None) -> ft.Container:
        return ft.Container(
            width=360,
            height=116,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=12,
            padding=20,
            on_click=lambda _: page.go(ruta) if ruta else None,
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
                                border_radius=BORDER_RADIUS,
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
        ("Reporte por Alumno", "Progreso individual, inasistencias y comportamiento consolidado.", ft.Icons.PERSON_OUTLINE, "/admin/reporte-alumnos-docentes"),
        ("Reporte por Docente", "Horas cátedra dictadas, asignaciones de materias y licencias.", ft.Icons.WORK_OUTLINE, "/admin/reporte-alumnos-docentes"),
        ("Listado por Curso", "Nóminas completas filtradas por grado, turno y nivel académico.", ft.Icons.PEOPLE_OUTLINE, "/admin/reporte-cursos-materias"),
        ("Listado por Materia", "Estadísticas de rendimiento, promedios y aprobados por trimestre.", ft.Icons.MENU_BOOK_OUTLINED, "/admin/reporte-cursos-materias"),
        ("Listado por Deporte", "Alumnos inscriptos por disciplina deportiva para control médico.", ft.Icons.FITNESS_CENTER_OUTLINED, "/admin/reporte-deportes-avanzado"),
        ("Listado por Transporte", "Hojas de ruta por recorrido con datos de tutores y teléfonos.", ft.Icons.DIRECTIONS_BUS_OUTLINED, "/admin/reporte-transporte-pasajeros"),
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
                controls=[categoria_card(t, d, i, r) for t, d, i, r in categorias_data],
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
            "ficha_color": ONLINE_GREEN,
            "seguro": "Al Día",
        },
        {
            "legajo": "#10249",
            "alumno": "Flores, Facundo Joaquín",
            "curso": "6to Año A",
            "ficha": "Aprobada (Vence Nov 25)",
            "ficha_color": ONLINE_GREEN,
            "seguro": "Al Día",
        },
        {
            "legajo": "#10252",
            "alumno": "Pérez, Juan Manuel",
            "curso": "2do Año C",
            "ficha": "Pendiente Presentar",
            "ficha_color": "#EF4444",
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
        border_radius=CARD_RADIUS,
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
                                        shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
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
                                        shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
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

    # ==================== 3. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Módulo General de Reportes y Estadísticas",
        active_route="/admin/reportes",
        spacing=32,
        content_controls=[
            seccion_categorias,
            preview_card,
        ],
    )