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
ORANGE = "#D97736"
TEXT_COLOR = "#1E2A29"
MUTED = "#5C6B69"


def get_admin_alumno_form_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa del formulario de alta/edición de alumno K-12."""

    # ==================== HELPERS DE ENTRADA ====================
    def input_con_label(label: str, hint: str, width: int = 289, read_only: bool = False, valor_inicial: str = None) -> ft.Column:
        return ft.Column(
            spacing=6,
            width=width,
            controls=[
                ft.Text(label, size=13, weight=ft.FontWeight.W_600, color=MUTED if read_only else TEXT_COLOR),
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

    def dropdown_con_label(label: str, valor_default: str, opciones: list[str], width: int = 187) -> ft.Column:
        return ft.Column(
            spacing=6,
            width=width,
            controls=[
                ft.Text(label, size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                ft.Container(
                    height=41,
                    bgcolor=BG_WHITE,
                    border=ft.Border.all(1, BORDER_COLOR),
                    border_radius=8,
                    content=ft.Dropdown(
                        value=valor_default,
                        text_size=14,
                        border=ft.InputBorder.NONE,
                        content_padding=ft.Padding(12, 0, 8, 12),
                        options=[ft.dropdown.Option(opc) for opc in opciones],
                    ),
                ),
            ],
        )

    # ==================== 1. BARRA SUPERIOR DE ACCIONES ====================
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
                        tooltip="Volver al listado",
                        on_click=lambda _: page.go("/admin/alumnos"),
                        content=ft.Icon(ft.Icons.ARROW_BACK, size=16, color=TEXT_COLOR),
                    ),
                    ft.Text(
                        "Nuevo Alumno (Ciclo 2025)",
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
                        on_click=lambda _: page.go("/admin/alumnos"),
                    ),
                    ft.Button(
                        content=ft.Text("Guardar Ficha", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
                        bgcolor=TEAL,
                        height=37,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.Padding(20, 10, 20, 10),
                        ),
                        on_click=lambda _: page.go("/admin/alumnos"),
                    ),
                ],
            ),
        ],
    )

    # ==================== 2. TARJETAS DE INFORMACIÓN (COLUMNA IZQUIERDA) ====================
    card_info_personal = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text("Información Personal", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Row(
                            spacing=16,
                            controls=[
                                input_con_label("Legajo (Autogenerado)", "", width=289, read_only=True, valor_inicial="#10251"),
                                input_con_label("DNI *", "Ej: 46.124.990", width=289),
                            ],
                        ),
                        ft.Row(
                            spacing=16,
                            controls=[
                                input_con_label("Nombres *", "Ej: Sofía Valentina", width=289),
                                input_con_label("Apellidos *", "Ej: Díaz", width=289),
                            ],
                        ),
                        ft.Row(
                            spacing=16,
                            controls=[
                                ft.Column(
                                    spacing=6,
                                    width=289,
                                    controls=[
                                        ft.Text("Fecha de Nacimiento *", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                        ft.Container(
                                            height=41,
                                            bgcolor=BG_WHITE,
                                            border=ft.Border.all(1, BORDER_COLOR),
                                            border_radius=8,
                                            padding=ft.Padding(12, 0, 12, 0),
                                            content=ft.Row(
                                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                controls=[
                                                    ft.TextField(
                                                        hint_text="DD/MM/AAAA",
                                                        hint_style=ft.TextStyle(size=14, color=MUTED),
                                                        text_size=14,
                                                        color=TEXT_COLOR,
                                                        border=ft.InputBorder.NONE,
                                                        content_padding=ft.Padding(0, 0, 0, 10),
                                                        expand=True,
                                                    ),
                                                    ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, size=16, color=MUTED),
                                                ],
                                            ),
                                        ),
                                    ],
                                ),
                                input_con_label("Domicilio Real *", "Av. Sarmiento 450, Resistencia", width=289),
                            ],
                        ),
                        ft.Row(
                            spacing=16,
                            controls=[
                                input_con_label("Teléfono de Contacto *", "3624-XXXXXX", width=289),
                                input_con_label("Correo Electrónico Tutor", "ejemplo@tutor.com", width=289),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    )

    card_info_academica = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text("Información Académica", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Row(
                    spacing=16,
                    controls=[
                        dropdown_con_label("Nivel Educativo", "Nivel Primario", ["Nivel Inicial", "Nivel Primario", "Nivel Secundario"], width=187),
                        dropdown_con_label("Curso", "4to Grado A", ["Sala 5", "4to Grado A", "6to Grado C", "5to Año B"], width=187),
                        dropdown_con_label("Estado de Matrícula", "Regular", ["Regular", "Pendiente", "Inactivo"], width=187),
                    ],
                ),
            ],
        ),
    )

    columna_izquierda = ft.Column(
        width=642,
        spacing=24,
        controls=[card_info_personal, card_info_academica],
    )

    # ==================== 3. DEPORTES Y SERVICIOS (COLUMNA DERECHA) ====================
    deportes_lista = [
        ("Atletismo", False),
        ("Natación", True),
        ("Fútbol", False),
        ("Artes Marciales", False),
        ("Vóleibol", False),
        ("Danza", False),
        ("Básquet", True),
        ("Ajedrez", False),
    ]

    def item_deporte(nombre: str, marcado: bool) -> ft.Row:
        return ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=20,
                    height=20,
                    bgcolor=TEAL_LIGHT if marcado else BG_WHITE,
                    border=ft.Border.all(1, TEAL if marcado else BORDER_COLOR),
                    border_radius=4,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(ft.Icons.CHECK, size=12, color=TEAL) if marcado else None,
                ),
                ft.Text(nombre, size=14, color=TEXT_COLOR),
            ],
        )

    card_deportes = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text("Inscripción Deportiva", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                        ft.Text("* Permitido un máximo de 2 disciplinas activas.", size=12, color=ORANGE),
                    ],
                ),
                ft.Column(
                    spacing=12,
                    controls=[item_deporte(nombre, status) for nombre, status in deportes_lista],
                ),
            ],
        ),
    )

    card_servicios = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text("Servicios Adicionales", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Column(
                    spacing=16,
                    controls=[
                        # Comedor Escolar (Activo)
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text("Comedor Escolar", size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                        ft.Text("Acceso diario al almuerzo institucional", size=11, color=MUTED),
                                    ],
                                ),
                                ft.Switch(value=True, active_color=TEAL),
                            ],
                        ),
                        ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                        # Transporte Escolar (Inactivo con dropdown deshabilitado)
                        ft.Column(
                            spacing=12,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Column(
                                            spacing=2,
                                            controls=[
                                                ft.Text("Transporte Escolar", size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                                ft.Text("Servicio de traslado puerta a puerta", size=11, color=MUTED),
                                            ],
                                        ),
                                        ft.Switch(value=False, active_color=TEAL),
                                    ],
                                ),
                                ft.Container(
                                    opacity=0.5,
                                    content=ft.Column(
                                        spacing=6,
                                        controls=[
                                            ft.Text("Zona de Recorrido Asignada", size=12, weight=ft.FontWeight.W_600, color=MUTED),
                                            ft.Container(
                                                height=36,
                                                bgcolor=BG_PAGE,
                                                border=ft.Border.all(1, BORDER_COLOR),
                                                border_radius=8,
                                                content=ft.Dropdown(
                                                    hint_text="Ninguna seleccionada",
                                                    hint_style=ft.TextStyle(size=13, color=MUTED),
                                                    text_size=13,
                                                    border=ft.InputBorder.NONE, 
                                                    content_padding=ft.Padding(10, 0, 8, 14),
                                                    options=[
                                                        ft.dropdown.Option("Zona Norte"),
                                                        ft.dropdown.Option("Zona Sur"),
                                                        ft.dropdown.Option("Zona Centro"),
                                                    ],
                                                ),
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    )

    columna_derecha = ft.Column(
        width=450,
        spacing=24,
        controls=[card_deportes, card_servicios],
    )

    # ==================== 4. LAYOUT PRINCIPAL ====================
    sidebar = create_sidebar(page, active_route="/admin/alumnos")
    topbar = create_topbar(page, titulo="Ficha de Alumno — Alta de Matrícula K-12")

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
                                controls=[columna_izquierda, columna_derecha],
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
        page.title = "Educar SGE - Alta de Matrícula"
        page.padding = 0
        page.bgcolor = BG_PAGE
        page.add(get_admin_alumno_form_view(page))

    ft.run(main)