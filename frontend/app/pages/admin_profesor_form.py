import flet as ft
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    MUTED,
    TEAL,
    TEAL_DARK,
    TEXT_COLOR,
)
from frontend.app.components.form_controls import dropdown_con_label, input_con_label


def get_admin_profesor_form_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa del formulario de alta y asignación de docentes."""

    # ==================== 1. ENCABEZADO DE ACCIONES ====================
    header_actions = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=36,
                        height=36,
                        bgcolor=BG_WHITE,
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=18,
                        alignment=ft.Alignment(0, 0),
                        tooltip="Volver a la nómina de profesores",
                        on_click=lambda _: page.go("/admin/profesores"),
                        content=ft.Icon(ft.Icons.ARROW_BACK, size=16, color=TEXT_COLOR),
                    ),
                    ft.Text(
                        "Nuevo Docente",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=TEAL_DARK,
                    ),
                ],
            ),
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Button(
                        content=ft.Text("Cancelar", size=14, weight=ft.FontWeight.W_600, color=MUTED),
                        bgcolor=BG_WHITE,
                        height=37,
                        style=ft.ButtonStyle(
                            side=ft.BorderSide(1, BORDER_COLOR),
                            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
                            padding=ft.Padding(20, 10, 20, 10),
                        ),
                        on_click=lambda _: page.go("/admin/profesores"),
                    ),
                    ft.Button(
                        content=ft.Text("Guardar Ficha", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
                        bgcolor=TEAL,
                        height=37,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
                            padding=ft.Padding(20, 10, 20, 10),
                        ),
                        on_click=lambda _: page.go("/admin/profesores"),
                    ),
                ],
            ),
        ],
    )

    # ==================== 2. COLUMNA IZQUIERDA: INFORMACIÓN BÁSICA ====================
    card_info_basica = ft.Container(
        width=612,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text("Información Básica", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Row(
                            spacing=16,
                            controls=[
                                input_con_label("Legajo (Asignado)", "", width=274, read_only=True, valor_inicial="#20106"),
                                input_con_label("DNI *", "Ej: 32.400.912", width=274),
                            ],
                        ),
                        ft.Row(
                            spacing=16,
                            controls=[
                                input_con_label("Nombres *", "Ej: Guillermina", width=274),
                                input_con_label("Apellidos *", "Ej: Sánchez", width=274),
                            ],
                        ),
                        ft.Row(
                            spacing=16,
                            controls=[
                                input_con_label("Especialidad Principal *", "Ej: Matemática Aplicada, Álgebra", width=274),
                                dropdown_con_label("Estado de Contrato *", "Activo", ["Activo", "Licencia", "Inactivo"], width=274),
                            ],
                        ),
                        ft.Row(
                            spacing=16,
                            controls=[
                                input_con_label("Correo Laboral *", "ejemplo@educar.edu.ar", width=274),
                                input_con_label("Teléfono Particular *", "3624-XXXXXX", width=274),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    )

    # ==================== 3. COLUMNA DERECHA: MATERIAS A CARGO ====================
    materias_data = [
        {"nombre": "Matemática", "nivel": "Secundario", "curso": "5to Año B"},
        {"nombre": "Álgebra Lineal", "nivel": "Secundario", "curso": "6to Año A"},
        {"nombre": "Estadística Aplicada", "nivel": "Secundario", "curso": "4to Año A"},
    ]

    def item_materia(materia: dict) -> ft.Container:
        return ft.Container(
            height=64,
            bgcolor=BG_PAGE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=BORDER_RADIUS,
            padding=12,
            content=ft.Column(
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(materia["nombre"], size=14, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ft.IconButton(
                                icon=ft.Icons.CANCEL_OUTLINED,
                                icon_size=14,
                                icon_color=BADGE_RED_TXT,
                                tooltip="Desasignar materia",
                                padding=0,
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.Text(f"Nivel: {materia['nivel']}", size=12, color=MUTED),
                            ft.Text(f"Curso: {materia['curso']}", size=12, color=MUTED),
                        ],
                    ),
                ],
            ),
        )

    card_materias_cargo = ft.Container(
        width=480,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text("Materias a Cargo", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                        ft.Text("Asigne las asignaturas correspondientes para el presente ciclo.", size=12, color=MUTED),
                    ],
                ),
                ft.Column(
                    spacing=12,
                    controls=[item_materia(m) for m in materias_data],
                ),
                ft.Container(
                    height=36,
                    border=ft.Border.all(1, TEAL),
                    border_radius=BORDER_RADIUS,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.ADD, size=14, color=TEAL),
                            ft.Text("Asignar Nueva Materia", size=13, weight=ft.FontWeight.W_600, color=TEAL),
                        ],
                    ),
                    on_click=lambda _: None,
                ),
            ],
        ),
    )

    # ==================== 4. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Ficha de Docente — Alta y Asignación Académica",
        active_route="/admin/profesores",
        content_controls=[
            header_actions,
            ft.Row(
                spacing=24,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[card_info_basica, card_materias_cargo],
            ),
        ],
    )