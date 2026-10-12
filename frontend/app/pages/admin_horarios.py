import flet as ft
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
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


def get_admin_horarios_view(page: ft.Page) -> ft.Row:
    """Retorna la vista de asignación y control de grillas horarias académicas y deportivas."""

    # ==================== 1. BARRA DE FILTROS Y ACCIÓN ====================
    search_input = ft.Container(
        width=260,
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
                    hint_text="Buscar materia, deporte o aula...",
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

    btn_nuevo_horario = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                ft.Text("Asignar Bloque Horario", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
            ],
        ),
        bgcolor=TEAL,
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            padding=ft.Padding(20, 10, 20, 10),
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
                    filtro_dropdown("Día: Todos", 125, ["Todos", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]),
                    filtro_dropdown("Nivel: Todos", 135, ["Todos", "Inicial", "Primario", "Secundario"]),
                    filtro_dropdown("Tipo: Todos", 130, ["Todos", "Académico", "Deportivo"]),
                ],
            ),
            btn_nuevo_horario,
        ],
    )

    # ==================== 2. TABLA DE HORARIOS PROGRAMADOS ====================
    horarios_data = [
        {"dia": "Lunes", "franja": "07:30 - 09:00 hs", "actividad": "Matemática Aplicada", "tipo": "Académico", "curso": "5to Año B", "espacio": "Aula 12 (Pabellón B)", "docente": "Sánchez, Guillermina", "estado": "Activo"},
        {"dia": "Lunes", "franja": "09:15 - 10:45 hs", "actividad": "Física y Química", "tipo": "Académico", "curso": "5to Año B", "espacio": "Lab. de Ciencias", "docente": "Martínez, Román", "estado": "Activo"},
        {"dia": "Lunes", "franja": "16:30 - 18:00 hs", "actividad": "Natación Climatizada", "tipo": "Deportivo", "curso": "Primario / Secundario", "espacio": "Natatorio Olímpico", "docente": "Vargas, Esteban", "estado": "Activo"},
        {"dia": "Martes", "franja": "08:00 - 10:00 hs", "actividad": "Inglés Intensivo", "tipo": "Académico", "curso": "4to Grado A", "espacio": "Aula 6", "docente": "Vázquez, Emily", "estado": "Activo"},
        {"dia": "Martes", "franja": "16:30 - 18:00 hs", "actividad": "Fútbol Campo", "tipo": "Deportivo", "curso": "Primario / Secundario", "espacio": "Cancha 1 (Sintético)", "docente": "Acuña, Germán", "estado": "Activo"},
        {"dia": "Miércoles", "franja": "15:00 - 16:30 hs", "actividad": "Atletismo de Pista", "tipo": "Deportivo", "curso": "Secundario Completo", "espacio": "Pista Atletismo", "docente": "Ríos, Marcos", "estado": "Activo"},
    ]

    columnas_horarios = [
        ("Día", 95, False),
        ("Franja Horaria", 140, False),
        ("Actividad / Materia", 180, False),
        ("Ámbito", 110, False),
        ("Curso / Nivel", 160, False),
        ("Espacio / Aula", 170, False),
        ("Profesor Responsable", 170, False),
        ("Estado", 95, False),
        ("Acciones", None, True),
    ]

    header_table = create_table_header(columnas_horarios)

    def horario_row(item: dict) -> ft.Container:
        es_deporte = item["tipo"] == "Deportivo"
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=95, content=ft.Text(item["dia"], size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=140, content=ft.Text(item["franja"], size=13, color=TEXT_COLOR)),
                    ft.Container(width=180, content=ft.Text(item["actividad"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(
                        width=110,
                        content=ft.Container(
                            padding=ft.Padding(6, 2, 6, 2),
                            bgcolor=ORANGE if es_deporte else TEAL_LIGHT,
                            border_radius=4,
                            content=ft.Text(
                                item["tipo"],
                                size=11,
                                weight=ft.FontWeight.BOLD,
                                color=BG_WHITE if es_deporte else TEAL_DARK,
                            ),
                        ),
                    ),
                    ft.Container(width=160, content=ft.Text(item["curso"], size=13, color=MUTED)),
                    ft.Container(width=170, content=ft.Text(item["espacio"], size=13, color=TEXT_COLOR)),
                    ft.Container(width=170, content=ft.Text(item["docente"], size=13, weight=ft.FontWeight.W_500, color=TEXT_COLOR)),
                    ft.Container(width=95, content=status_badge(item["estado"])),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=12,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_size=16, icon_color=TEAL, tooltip="Modificar Horario", padding=0),
                                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_size=16, icon_color=BADGE_RED_TXT, tooltip="Liberar Bloque", padding=0),
                            ],
                        ),
                    ),
                ],
            ),
        )

    table_container = create_table_container(
        header=header_table,
        rows=[horario_row(h) for h in horarios_data],
    )

    pagination_bar = create_pagination_bar(
        texto_info="Mostrando 1-6 de 84 bloques horarios semanales",
        pagina_actual=1,
        total_paginas=14,
    )

    aviso_control_solapamiento = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
        padding=14,
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=18, color=TEAL),
                ft.Text(
                    "Control de Conflictos: El sistema valida automáticamente que no existan superposiciones de horarios entre actividades deportivas y materias regulares.",
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
        titulo="Cronograma y Grilla de Horarios",
        active_route="/admin/horarios",
        content_controls=[
            aviso_control_solapamiento,
            filters_bar,
            table_container,
            pagination_bar,
        ],
    )