import flet as ft
from frontend.app.components.constants import (
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    MUTED,
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


def get_padre_docentes_view(page: ft.Page) -> ft.Row:
    """Retorna la nómina de Profesores por Materia correspondiente al alumno seleccionado."""

    materias_docentes = [
        {"materia": "Matemática Aplicada", "docente": "Prof. Sánchez, Guillermina", "especialidad": "Matemática y Álgebra", "email": "g.sanchez@educar.edu.ar", "horario": "Lunes 07:30 - 09:00 hs"},
        {"materia": "Física y Química", "docente": "Prof. Martínez, Román Alberto", "especialidad": "Ciencias Naturales", "email": "r.martinez@educar.edu.ar", "horario": "Lunes 09:15 - 10:45 hs"},
        {"materia": "Lengua y Literatura", "docente": "Prof. Duarte, María Florencia", "especialidad": "Lenguas y Comunicación", "email": "f.duarte@educar.edu.ar", "horario": "Miércoles 08:00 - 10:00 hs"},
        {"materia": "Robótica y Programación", "docente": "Prof. Ortega, Luis Humberto", "especialidad": "Informática Aplicada", "email": "l.ortega@educar.edu.ar", "horario": "Jueves 10:30 - 12:00 hs"},
        {"materia": "Educación Física y Natación", "docente": "Prof. Vargas, Esteban Carlos", "especialidad": "Educación Física", "email": "e.vargas@educar.edu.ar", "horario": "Lun y Mié 16:30 - 18:00 hs"},
        {"materia": "Inglés Bilingüe", "docente": "Prof. Vázquez, Emily", "especialidad": "Lenguas Extranjeras", "email": "e.vazquez@educar.edu.ar", "horario": "Viernes 07:30 - 10:00 hs"},
    ]

    columnas = [
        ("Asignatura / Materia", 200, False),
        ("Profesor a Cargo", 200, False),
        ("Especialidad Docente", 180, False),
        ("Horario de Clases", 180, False),
        ("Contacto Institucional", 220, False),
    ]

    header_table = create_table_header(columnas)

    def docente_fila(item: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=200, content=ft.Text(item["materia"], size=14, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=200, content=ft.Text(item["docente"], size=14, weight=ft.FontWeight.W_500, color=TEXT_COLOR)),
                    ft.Container(width=180, content=ft.Text(item["especialidad"], size=13, color=MUTED)),
                    ft.Container(width=180, content=ft.Text(item["horario"], size=13, color=TEXT_COLOR)),
                    ft.Container(width=220, content=ft.Text(item["email"], size=13, color=TEAL)),
                ],
            ),
        )

    tabla_docentes = create_table_container(
        header=header_table,
        rows=[docente_fila(m) for m in materias_docentes],
    )

    info_card = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
        padding=16,
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE, size=20, color=TEAL),
                ft.Text("Docentes del alumno: Santiago Almirón · 5to Año B (Nivel Secundario)", size=14, weight=ft.FontWeight.W_600, color=TEAL_DARK),
            ],
        ),
    )

    return portal_layout(
        page=page,
        titulo="Cuerpo Docente por Materia",
        active_route="/portal/padre/docentes",
        rol="Padre",
        content_controls=[
            info_card,
            tabla_docentes,
        ],
    )