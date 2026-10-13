import flet as ft
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.form_controls import status_badge
from frontend.app.components.table_view import (
    create_pagination_bar,
    create_table_container,
    create_table_header,
)


def get_admin_deportes_view(page: ft.Page) -> ft.Row:
    """Retorna la vista de gestión de Deportes e Infraestructura deportiva."""

    # ==================== 1. FILTROS Y ACCIÓN ====================
    search_input = ft.Container(
        width=280,
        height=CONTROL_HEIGHT,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=BORDER_RADIUS,
        padding=ft.Padding(12, 0, 12, 0),
        content=ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SEARCH, size=16, color=MUTED),
                ft.TextField(
                    hint_text="Buscar disciplina o docente...",
                    hint_style=ft.TextStyle(size=14, color=MUTED),
                    text_size=14,
                    color=TEXT_COLOR,
                    border=ft.InputBorder.NONE,
                    content_padding=ft.Padding(0, 0, 0, 10),
                    expand=True,
                ),
            ],
        ),
    )

    def filtro_dropdown(hint: str, width: int, opciones: list[str]) -> ft.Container:
        return ft.Container(
            width=width,
            height=CONTROL_HEIGHT,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=BORDER_RADIUS,
            content=ft.Dropdown(
                hint_text=hint,
                hint_style=ft.TextStyle(size=14, color=TEXT_COLOR),
                text_size=14,
                border=ft.InputBorder.NONE,
                content_padding=ft.Padding(12, 0, 8, 12),
                options=[ft.dropdown.Option(opc) for opc in opciones],
            ),
        )

    btn_nuevo_deporte = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                ft.Text("Nueva Disciplina", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
            ],
        ),
        bgcolor=TEAL,
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            padding=ft.Padding(24, 12, 24, 12),
        ),
        on_click=lambda _: None,
    )

    filters_bar = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    search_input,
                    filtro_dropdown("Nivel: Todos", 140, ["Todos", "Nivel Primario", "Nivel Secundario"]),
                    filtro_dropdown("Instalación: Todas", 160, ["Todas", "Natatorio Olímpico", "Canchas Fútbol", "Pista Atletismo", "Gimnasio"]),
                ],
            ),
            btn_nuevo_deporte,
        ],
    )

    # ==================== 2. TABLA DE DISCIPLINAS ====================
    deportes_data = [
        {"disciplina": "Natación Climatizada", "profesor": "Vargas, Esteban Carlos", "instalacion": "Natatorio Olímpico", "horarios": "Lun y Mié 16:30 - 18:00 hs", "inscriptos": "48 / 50", "nivel": "Primario y Secundario", "estado": "Activo"},
        {"disciplina": "Fútbol Campo", "profesor": "Acuña, Germán", "instalacion": "Canchas de Fútbol (Césped)", "horarios": "Mar y Jue 16:30 - 18:00 hs", "inscriptos": "60 / 60", "nivel": "Primario y Secundario", "estado": "Activo"},
        {"disciplina": "Atletismo de Pista", "profesor": "Ríos, Marcos", "instalacion": "Pista Profesional", "horarios": "Lun y Mié 15:00 - 16:30 hs", "inscriptos": "32 / 40", "nivel": "Secundario", "estado": "Activo"},
        {"disciplina": "Artes Marciales (Taekwondo)", "profesor": "Sensei Navarro, Hiroshi", "instalacion": "Gimnasio Cubierto (Dojo)", "horarios": "Viernes 16:30 - 18:30 hs", "inscriptos": "25 / 30", "nivel": "Primario y Secundario", "estado": "Activo"},
        {"disciplina": "Básquetbol", "profesor": "Pérez, Daniel", "instalacion": "Gimnasio Cubierto (Cancha 1)", "horarios": "Mar y Jue 15:00 - 16:30 hs", "inscriptos": "28 / 35", "nivel": "Primario y Secundario", "estado": "Activo"},
        {"disciplina": "Danza Contemporánea", "profesor": "Sosa, Valeria", "instalacion": "Salón de Expresión Corporal", "horarios": "Mié y Vie 16:30 - 18:00 hs", "inscriptos": "22 / 25", "nivel": "Inicial y Primario", "estado": "Activo"},
        {"disciplina": "Vóleibol Formativo", "profesor": "López, Andrea", "instalacion": "Gimnasio Cubierto (Cancha 2)", "horarios": "Mar y Jue 16:30 - 18:00 hs", "inscriptos": "26 / 30", "nivel": "Secundario", "estado": "Activo"},
        {"disciplina": "Ajedrez Estratégico", "profesor": "Maestro FIDE Blanco, Jorge", "instalacion": "Biblioteca Central", "horarios": "Lunes 16:30 - 18:00 hs", "inscriptos": "18 / 20", "nivel": "Todos los Niveles", "estado": "Activo"},
    ]

    columnas_deportes = [
        ("Disciplina Deportiva", 190, False),
        ("Profesor Responsable", 180, False),
        ("Instalación Asignada", 180, False),
        ("Días y Horarios", 190, False),
        ("Plazas / Cupo", 120, False),
        ("Nivel Destinado", 160, False),
        ("Estado", 100, False),
        ("Acciones", None, True),
    ]

    header_table = create_table_header(columnas_deportes)

    def deporte_row(item: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=190, content=ft.Text(item["disciplina"], size=14, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=180, content=ft.Text(item["profesor"], size=14, weight=ft.FontWeight.W_500, color=TEXT_COLOR)),
                    ft.Container(width=180, content=ft.Text(item["instalacion"], size=13, color=MUTED)),
                    ft.Container(width=190, content=ft.Text(item["horarios"], size=13, color=TEXT_COLOR)),
                    ft.Container(width=120, content=ft.Text(item["inscriptos"], size=13, weight=ft.FontWeight.BOLD, color=TEXT_COLOR)),
                    ft.Container(width=160, content=ft.Text(item["nivel"], size=13, color=MUTED)),
                    ft.Container(width=100, content=status_badge(item["estado"])),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=12,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_size=16, icon_color=TEAL, tooltip="Editar Horarios y Cupos", padding=0),
                                ft.IconButton(icon=ft.Icons.PEOPLE_OUTLINE, icon_size=16, icon_color=MUTED, tooltip="Ver Alumnos Inscriptos", padding=0),
                            ],
                        ),
                    ),
                ],
            ),
        )

    table_container = create_table_container(
        header=header_table,
        rows=[deporte_row(d) for d in deportes_data],
    )

    aviso_regla = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
        padding=14,
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE, size=18, color=TEAL),
                ft.Text(
                    "Regla de Negocio: Cada estudiante puede inscribirse en hasta dos disciplinas deportivas simultáneamente, sin conflicto de horarios.",
                    size=13,
                    color=TEAL_DARK,
                    weight=ft.FontWeight.W_500,
                ),
            ],
        ),
    )

    # ==================== 3. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Programa Deportivo e Infraestructura (8 Disciplinas)",
        active_route="/admin/deportes",
        content_controls=[
            aviso_regla,
            filters_bar,
            table_container,
        ],
    )