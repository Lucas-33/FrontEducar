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
from frontend.app.components.table_view import (
    create_table_container,
    create_table_header,
)


def get_docente_deportes_view(page: ft.Page) -> ft.Row:
    """Retorna la vista de disciplinas deportivas a cargo del cuerpo docente."""

    deportes_asignados = [
        {
            "disciplina": "Natación Climatizada",
            "categoria": "Intermedio y Avanzado (Secundario)",
            "dias": "Lunes y Miércoles 16:30 - 18:00 hs",
            "instalacion": "Natatorio Olímpico",
            "inscriptos": "24 / 25",
            "estado_medico": "100% Aptos Presentados",
        },
    ]

    def tarjeta_deporte(d: dict) -> ft.Container:
        return ft.Container(
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=24,
            content=ft.Column(
                spacing=14,
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
                                        content=ft.Icon(ft.Icons.POOL, size=20, color=TEAL_DARK),
                                    ),
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(d["disciplina"], size=17, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                                            ft.Text(d["categoria"], size=13, color=MUTED),
                                        ],
                                    ),
                                ],
                            ),
                            status_badge("Activo"),
                        ],
                    ),
                    ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                    ft.Row(
                        spacing=32,
                        controls=[
                            ft.Column([ft.Text("Días y Horarios", size=11, color=MUTED), ft.Text(d["dias"], size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR)], spacing=3),
                            ft.Column([ft.Text("Instalación Asignada", size=11, color=MUTED), ft.Text(d["instalacion"], size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR)], spacing=3),
                            ft.Column([ft.Text("Cupos Ocupados", size=11, color=MUTED), ft.Text(d["inscriptos"], size=13, weight=ft.FontWeight.BOLD, color=TEAL_DARK)], spacing=3),
                            ft.Column([ft.Text("Fichas Médicas", size=11, color=MUTED), ft.Text(d["estado_medico"], size=13, weight=ft.FontWeight.W_600, color=ONLINE_GREEN)], spacing=3),
                        ],
                    ),
                ],
            ),
        )

    # Alumnos inscriptos en el deporte
    inscriptos_deporte = [
        {"legajo": "#10245", "alumno": "Almirón, Santiago", "curso": "5to Año B", "apto": "Vigente (Dr. Ruiz)", "seguro": "Al Día"},
        {"legajo": "#10249", "alumno": "Flores, Facundo Joaquín", "curso": "6to Año A", "apto": "Vigente (Dra. Ponce)", "seguro": "Al Día"},
        {"legajo": "#10247", "alumno": "Capra, Lautaro", "curso": "6to Grado C", "apto": "Vigente (Dr. Ruiz)", "seguro": "Al Día"},
    ]

    columnas_inscriptos = [
        ("Legajo", 110, False),
        ("Estudiante", 220, False),
        ("Curso", 140, False),
        ("Certificado Apto Médico", 220, False),
        ("Seguro Escolar", 140, False),
    ]

    header_table = create_table_header(columnas_inscriptos)

    def inscripto_row(item: dict) -> ft.Container:
        return ft.Container(
            height=50,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=110, content=ft.Text(item["legajo"], size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=220, content=ft.Text(item["alumno"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=140, content=ft.Text(item["curso"], size=14, color=MUTED)),
                    ft.Container(width=220, content=ft.Text(item["apto"], size=13, weight=ft.FontWeight.W_500, color=ONLINE_GREEN)),
                    ft.Container(width=140, content=ft.Text(item["seguro"], size=13, color=TEXT_COLOR)),
                ],
            ),
        )

    tabla_inscriptos = create_table_container(
        header=header_table,
        rows=[inscripto_row(i) for i in inscriptos_deporte],
        min_width=830,
    )

    return portal_layout(
        page=page,
        titulo="Deportes y Actividades a Cargo",
        active_route="/portal/docente/deportes",
        rol="Docente",
        usuario_nombre="Prof. Román Martínez",
        usuario_sub="Legajo #20101 · Ciencias Exactas",
        content_controls=[
            tarjeta_deporte(deportes_asignados[0]),
            ft.Text("Nómina de Deportistas Inscriptos", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
            tabla_inscriptos,
        ],
    )