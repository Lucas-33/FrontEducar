import flet as ft
from app.ui.components.sidebar import create_sidebar
from app.ui.components.topbar import create_topbar

# Paleta cromática de la identidad visual
BG_PAGE = "#F5F7F7"
BG_WHITE = "#FFFFFF"
BORDER_COLOR = "#EAE6E1"
TEAL_DARK = "#0B4F4F"
TEAL = "#0D6E6E"
TEAL_LIGHT = "#E6F2F2"
TEXT_COLOR = "#1E2A29"
MUTED = "#5C6B69"
RED_ACTION = "#EF4444"


def get_admin_profesor_form_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa del formulario de alta y asignación académica de docentes."""

    # ==================== HELPERS DE ENTRADA ====================
    def input_con_label(
        label: str,
        hint: str,
        width: int = 274,
        read_only: bool = False,
        valor_inicial: str = None,
    ) -> ft.Column:
        return ft.Column(
            spacing=6,
            width=width,
            controls=[
                ft.Text(
                    label,
                    size=13,
                    weight=ft.FontWeight.W_600,
                    color=MUTED if read_only else TEXT_COLOR,
                ),
                ft.Container(
                    height=41,
                    bgcolor=BG_PAGE if read_only else BG_WHITE,
                    border=None if read_only else ft.Border.all(1, BORDER_COLOR),
                    border_radius=8,
                    padding=ft.Padding(12, 0, 12, 0),
                    alignment=ft.Alignment(-1, 0),
                    content=ft.TextField(
                        value=valor_inicial or "",
                        hint_text=hint if not valor_inicial else None,
                        hint_style=ft.TextStyle(size=14, color=MUTED),
                        text_size=14,
                        color=MUTED if read_only else TEXT_COLOR,
                        read_only=read_only,
                        border=ft.InputBorder.NONE,
                        content_padding=ft.Padding(0, 0, 0, 10),
                    ),
                ),
            ],
        )

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
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.Padding(20, 10, 20, 10),
                        ),
                        on_click=lambda _: page.go("/admin/profesores"),
                    ),
                    ft.Button(
                        content=ft.Text("Guardar Ficha", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
                        bgcolor=TEAL,
                        height=37,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
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
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text(
                    "Información Básica",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
                ft.Column(
                    spacing=16,
                    controls=[
                        # Fila 1: Legajo y DNI
                        ft.Row(
                            spacing=16,
                            controls=[
                                input_con_label(
                                    "Legajo (Asignado)",
                                    "",
                                    width=274,
                                    read_only=True,
                                    valor_inicial="#20106",
                                ),
                                input_con_label("DNI *", "Ej: 32.400.912", width=274),
                            ],
                        ),
                        # Fila 2: Nombres y Apellidos
                        ft.Row(
                            spacing=16,
                            controls=[
                                input_con_label("Nombres *", "Ej: Guillermina", width=274),
                                input_con_label("Apellidos *", "Ej: Sánchez", width=274),
                            ],
                        ),
                        # Fila 3: Especialidad y Estado de Contrato
                        ft.Row(
                            spacing=16,
                            controls=[
                                input_con_label(
                                    "Especialidad Principal *",
                                    "Ej: Matemática Aplicada, Álgebra",
                                    width=274,
                                ),
                                ft.Column(
                                    spacing=6,
                                    width=274,
                                    controls=[
                                        ft.Text(
                                            "Estado de Contrato *",
                                            size=13,
                                            weight=ft.FontWeight.W_600,
                                            color=TEXT_COLOR,
                                        ),
                                        ft.Container(
                                            height=41,
                                            bgcolor=BG_WHITE,
                                            border=ft.Border.all(1, BORDER_COLOR),
                                            border_radius=8,
                                            content=ft.Dropdown(
                                                value="Activo",
                                                text_size=14,
                                                border=ft.InputBorder.NONE,
                                                content_padding=ft.Padding(12, 0, 8, 12),
                                                options=[
                                                    ft.dropdown.Option("Activo"),
                                                    ft.dropdown.Option("Licencia"),
                                                    ft.dropdown.Option("Inactivo"),
                                                ],
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        # Fila 4: Correo Laboral y Teléfono Particular
                        ft.Row(
                            spacing=16,
                            controls=[
                                input_con_label(
                                    "Correo Laboral *",
                                    "ejemplo@educar.edu.ar",
                                    width=274,
                                ),
                                input_con_label(
                                    "Teléfono Particular *",
                                    "3624-XXXXXX",
                                    width=274,
                                ),
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
            border_radius=8,
            padding=12,
            content=ft.Column(
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                materia["nombre"],
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CANCEL_OUTLINED,
                                icon_size=14,
                                icon_color=RED_ACTION,
                                tooltip="Desasignar materia",
                                padding=0,
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.Text(
                                f"Nivel: {materia['nivel']}",
                                size=12,
                                color=MUTED,
                            ),
                            ft.Text(
                                f"Curso: {materia['curso']}",
                                size=12,
                                color=MUTED,
                            ),
                        ],
                    ),
                ],
            ),
        )

    card_materias_cargo = ft.Container(
        width=480,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(
                            "Materias a Cargo",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=TEAL_DARK,
                        ),
                        ft.Text(
                            "Asigne las asignaturas correspondientes para el presente ciclo.",
                            size=12,
                            color=MUTED,
                        ),
                    ],
                ),
                # Lista de materias
                ft.Column(
                    spacing=12,
                    controls=[item_materia(m) for m in materias_data],
                ),
                # Botón de asignación
                ft.Container(
                    height=36,
                    border=ft.Border.all(1, TEAL),
                    border_radius=8,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.ADD, size=14, color=TEAL),
                            ft.Text(
                                "Asignar Nueva Materia",
                                size=13,
                                weight=ft.FontWeight.W_600,
                                color=TEAL,
                            ),
                        ],
                    ),
                    on_click=lambda _: None,
                ),
            ],
        ),
    )

    # ==================== 4. LAYOUT PRINCIPAL ====================
    sidebar = create_sidebar(page, active_route="/admin/profesores")
    topbar = create_topbar(page, titulo="Ficha de Docente — Alta y Asignación Académica")

    formulario_body = ft.Container(
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
                        spacing=24,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            header_actions,
                            ft.Row(
                                spacing=24,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                                controls=[card_info_basica, card_materias_cargo],
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )

    return ft.Row(
        expand=True,
        spacing=0,
        controls=[sidebar, formulario_body],
    )


if __name__ == "__main__":
    def main(page: ft.Page):
        page.title = "Educar SGE - Alta de Docente"
        page.padding = 0
        page.bgcolor = BG_PAGE
        page.add(get_admin_profesor_form_view(page))

    ft.run(main)