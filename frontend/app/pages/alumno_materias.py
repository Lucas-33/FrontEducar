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
from frontend.app.components.portal_layout import portal_layout
from frontend.app.components.table_view import (
    create_table_container,
    create_table_header,
)


def get_alumno_materias_view(page: ft.Page) -> ft.Row:
    """Retorna las materias curriculares en las que el alumno está inscripto."""

    materias_data = [
        {"codigo": "MAT-501", "materia": "Matemática Aplicada", "profesor": "Prof. Guillermina Sánchez", "horario": "Lun 07:30 - 09:00 hs", "aula": "Aula 12", "nota_t1": "8.50", "asistencia": "96%"},
        {"codigo": "FIS-402", "materia": "Física y Química", "profesor": "Prof. Román Martínez", "horario": "Lun 09:15 - 10:45 hs", "aula": "Lab. Ciencias", "nota_t1": "9.00", "asistencia": "94%"},
        {"codigo": "LIT-301", "materia": "Lengua y Literatura", "profesor": "Prof. María Florencia Duarte", "horario": "Mié 08:00 - 10:00 hs", "aula": "Aula 12", "nota_t1": "8.00", "asistencia": "92%"},
        {"codigo": "ROB-601", "materia": "Robótica y Programación", "profesor": "Prof. Luis Humberto Ortega", "horario": "Jue 10:30 - 12:00 hs", "aula": "Lab. Informática", "nota_t1": "9.50", "asistencia": "98%"},
        {"codigo": "ING-001", "materia": "Inglés Bilingüe", "profesor": "Prof. Emily Vázquez", "horario": "Vie 07:30 - 10:00 hs", "aula": "Aula 12", "nota_t1": "7.50", "asistencia": "90%"},
    ]

    columnas = [
        ("Código", 100, False),
        ("Asignatura / Materia", 210, False),
        ("Profesor a Cargo", 200, False),
        ("Días y Horarios", 180, False),
        ("Espacio / Aula", 140, False),
        ("Nota 1° Trim.", 110, False),
        ("Asistencia", 110, True),
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
                    ft.Container(width=210, content=ft.Text(item["materia"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=200, content=ft.Text(item["profesor"], size=13, color=MUTED)),
                    ft.Container(width=180, content=ft.Text(item["horario"], size=13, color=TEXT_COLOR)),
                    ft.Container(width=140, content=ft.Text(item["aula"], size=13, color=MUTED)),
                    ft.Container(width=110, content=ft.Text(item["nota_t1"], size=14, weight=ft.FontWeight.BOLD, color=TEAL_DARK)),
                    ft.Container(width=110, alignment=ft.Alignment(1, 0), content=ft.Text(item["asistencia"], size=13, weight=ft.FontWeight.W_600, color=ONLINE_GREEN)),
                ],
            ),
        )

    tabla_materias = create_table_container(
        header=header_table,
        rows=[materia_row(m) for m in materias_data],
        min_width=1050,
    )

    info_card = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
        padding=16,
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE, size=20, color=TEAL),
                ft.Text("Plan Curricular de 5to Año B: Los exámenes del segundo trimestre se publicarán a partir de la próxima semana.", size=13, color=TEAL_DARK),
            ],
        ),
    )

    return portal_layout(
        page=page,
        titulo="Mis Materias y Profesores",
        active_route="/portal/alumno/materias",
        rol="Alumno",
        usuario_nombre="Santiago Almirón",
        usuario_sub="Legajo #10245 · 5to Año B",
        content_controls=[
            info_card,
            tabla_materias,
        ],
    )