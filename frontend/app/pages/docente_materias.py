import flet as ft
from frontend.app.components.constants import (
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
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


def get_docente_materias_view(page: ft.Page) -> ft.Row:
    """Retorna la vista de asignaturas curriculares a cargo del docente."""

    materias_data = [
        {"codigo": "FIS-402", "nombre": "Física y Química", "curso": "5to Año B", "nivel": "Nivel Secundario", "carga": "4 hs/sem", "horario": "Lunes 07:30 - 09:00 y Lab.", "aula": "Aula 12", "alumnos": "22 alumnos"},
        {"codigo": "LAB-501", "nombre": "Laboratorio de Ciencias Experimentales", "curso": "5to Año B", "nivel": "Nivel Secundario", "carga": "2 hs/sem", "horario": "Lunes 09:15 - 10:45", "aula": "Laboratorio Central", "alumnos": "22 alumnos"},
        {"codigo": "FIS-301", "nombre": "Física I", "curso": "4to Año A", "nivel": "Nivel Secundario", "carga": "4 hs/sem", "horario": "Miércoles y Viernes 08:00 - 09:30", "aula": "Aula 8", "alumnos": "26 alumnos"},
    ]

    columnas = [
        ("Código", 100, False),
        ("Asignatura / Materia", 220, False),
        ("Curso Asignado", 140, False),
        ("Carga Semanal", 120, False),
        ("Días y Horarios", 210, False),
        ("Espacio / Aula", 150, False),
        ("Inscriptos", 110, False),
        ("Acciones", 120, True),
    ]

    header_table = create_table_header(columnas)

    def materia_row(item: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=100, content=ft.Text(item["codigo"], size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=220, content=ft.Text(item["nombre"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=140, content=ft.Text(item["curso"], size=14, color=TEAL)),
                    ft.Container(width=120, content=ft.Text(item["carga"], size=13, color=MUTED)),
                    ft.Container(width=210, content=ft.Text(item["horario"], size=13, color=TEXT_COLOR)),
                    ft.Container(width=150, content=ft.Text(item["aula"], size=13, color=MUTED)),
                    ft.Container(width=110, content=ft.Text(item["alumnos"], size=13, weight=ft.FontWeight.W_500, color=TEXT_COLOR)),
                    ft.Container(
                        width=120,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Button(
                            "Ver Alumnos",
                            height=30,
                            bgcolor=TEAL_LIGHT,
                            color=TEAL_DARK,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=6),
                                padding=ft.Padding(10, 4, 10, 4),
                                text_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_600),
                            ),
                            on_click=lambda _: page.go("/portal/docente/alumnos"),
                        ),
                    ),
                ],
            ),
        )

    tabla_materias = create_table_container(
        header=header_table,
        rows=[materia_row(m) for m in materias_data],
        min_width=1170,
    )

    info_card = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
        padding=16,
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE, size=20, color=TEAL),
                ft.Text("Planificación Curricular 2027: Todas las asignaturas cuentan con libro de temas digital habilitado.", size=13, weight=ft.FontWeight.W_500, color=TEAL_DARK),
            ],
        ),
    )

    return portal_layout(
        page=page,
        titulo="Mis Cursos y Materias Asignadas",
        active_route="/portal/docente/materias",
        rol="Docente",
        usuario_nombre="Prof. Román Martínez",
        usuario_sub="Legajo #20101 · Ciencias Exactas",
        content_controls=[
            info_card,
            tabla_materias,
        ],
    )