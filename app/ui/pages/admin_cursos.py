import flet as ft
from app.ui.components.sidebar import create_sidebar
from app.ui.components.topbar import create_topbar

# Paleta cromática y tokens visuales del sistema
BG_PAGE = "#F5F7F7"
BG_WHITE = "#FFFFFF"
BORDER_COLOR = "#EAE6E1"
TEAL_DARK = "#0B4F4F"
TEAL = "#0D6E6E"
TEAL_LIGHT = "#E6F2F2"
TEXT_COLOR = "#1E2A29"
MUTED = "#5C6B69"


def get_admin_cursos_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa de Gestión de Cursos y Divisiones."""

    # ==================== 1. ENCABEZADO Y ACCIÓN PRINCIPAL ====================
    encabezado_modulo = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                spacing=6,
                expand=True,
                controls=[
                    ft.Text(
                        "Administración Académica y Organización Escolar",
                        size=12,
                        weight=ft.FontWeight.W_400,
                        color=MUTED,
                    ),
                    ft.Text(
                        "Cursos y Gestión de Divisiones",
                        size=26,
                        weight=ft.FontWeight.W_600,
                        color=TEAL_DARK,
                    ),
                    ft.Text(
                        "Supervise las aulas, preceptores a cargo, cupos de matrícula y división de turnos para el presente ciclo.",
                        size=14,
                        color=MUTED,
                    ),
                ],
            ),
            ft.Button(
                content=ft.Row(
                    spacing=8,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                        ft.Text("Nuevo Curso", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
                    ],
                ),
                bgcolor=TEAL,
                height=41,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding(16, 11, 16, 11),
                ),
                on_click=lambda _: None,
            ),
        ],
    )

    # ==================== 2. BÚSQUEDA Y FILTROS ====================
    search_bar = ft.Container(
        height=43,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=8,
        padding=ft.Padding(12, 0, 12, 0),
        expand=True,
        content=ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SEARCH, size=16, color=MUTED),
                ft.TextField(
                    hint_text="Buscar curso por año, división o preceptor...",
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

    def filtro_desplegable(texto: str, ancho: int) -> ft.Container:
        return ft.Container(
            width=ancho,
            height=43,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=8,
            padding=ft.Padding(12, 0, 12, 0),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(texto, size=14, color=TEXT_COLOR),
                    ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=14, color=MUTED),
                ],
            ),
        )

    filtros_fila = ft.Row(
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            search_bar,
            filtro_desplegable("Nivel: Todos", 123),
            filtro_desplegable("Turno: Todos", 118),
            filtro_desplegable("Estado: Activo", 138),
        ],
    )

    # ==================== 3. RESUMEN DEL LISTADO Y TABLA ====================
    resumen_listado = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text("Divisiones Activas", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
            ft.Text("Mostrando 6 de 32 divisiones", size=13, color=MUTED),
        ],
    )

    cabecera_tabla = ft.Container(
        height=42,
        bgcolor=TEAL_LIGHT,
        padding=ft.Padding(16, 13, 16, 13),
        content=ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(width=404, expand=True, content=ft.Text("Curso y División", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=190, content=ft.Text("Nivel Educativo", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=90, content=ft.Text("Turno", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=130, content=ft.Text("Matrícula", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=120, content=ft.Text("Estado", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=90, content=ft.Text("Acciones", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
            ],
        ),
    )

    cursos_data = [
        {"nombre": "Sala de 4 años — Turno Tarde", "nivel": "Nivel Inicial", "turno": "Tarde", "matricula": "28 / 30 alumnos", "seleccionado": False},
        {"nombre": "Sala de 5 años División B", "nivel": "Nivel Inicial", "turno": "Mañana", "matricula": "25 / 25 alumnos", "seleccionado": False},
        {"nombre": "4to Grado División A", "nivel": "Nivel Primario", "turno": "Mañana", "matricula": "32 / 35 alumnos", "seleccionado": True},
        {"nombre": "6to Grado División C", "nivel": "Nivel Primario", "turno": "Tarde", "matricula": "30 / 35 alumnos", "seleccionado": False},
        {"nombre": "3er Año División A", "nivel": "Nivel Secundario", "turno": "Mañana", "matricula": "34 / 35 alumnos", "seleccionado": False},
        {"nombre": "5to Año División B", "nivel": "Nivel Secundario", "turno": "Tarde", "matricula": "31 / 35 alumnos", "seleccionado": False},
    ]

    def curso_row(item: dict) -> ft.Container:
        return ft.Container(
            height=62,
            bgcolor=TEAL_LIGHT if item["seleccionado"] else BG_WHITE,
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            padding=ft.Padding(16, 14, 16, 14),
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=404,
                        expand=True,
                        content=ft.Text(item["nombre"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                    ),
                    ft.Container(
                        width=190,
                        content=ft.Text(item["nivel"], size=13, color=TEXT_COLOR),
                    ),
                    ft.Container(
                        width=90,
                        content=ft.Text(item["turno"], size=13, color=TEXT_COLOR),
                    ),
                    ft.Container(
                        width=130,
                        content=ft.Text(item["matricula"], size=13, color=TEXT_COLOR),
                    ),
                    ft.Container(
                        width=120,
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    padding=ft.Padding(8, 4, 8, 4),
                                    bgcolor=TEAL_LIGHT,
                                    border_radius=4,
                                    content=ft.Text("Activo", size=12, weight=ft.FontWeight.W_600, color=TEAL),
                                ),
                            ]
                        ),
                    ),
                    ft.Container(
                        width=90,
                        content=ft.Row(
                            spacing=10,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.REMOVE_RED_EYE_OUTLINED,
                                    icon_size=16,
                                    icon_color=TEAL,
                                    tooltip="Ver detalle",
                                    padding=0,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_NOTE_OUTLINED,
                                    icon_size=16,
                                    icon_color=TEAL,
                                    tooltip="Modificar",
                                    padding=0,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    tabla_contenedor = ft.Container(
        height=414,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            spacing=0,
            controls=[
                cabecera_tabla,
                *[curso_row(c) for c in cursos_data],
            ],
        ),
    )

    nota_tabla = ft.Text(
        "Haga clic en una fila para desplegar y editar los datos específicos de la división seleccionada.",
        size=12,
        color=MUTED,
    )

    # ==================== 4. DETALLE Y RELACIONES DEL CURSO ====================
    def selector_campo(etiqueta: str, valor: str) -> ft.Column:
        return ft.Column(
            spacing=6,
            expand=True,
            controls=[
                ft.Text(etiqueta, size=12, weight=ft.FontWeight.W_600, color=MUTED),
                ft.Container(
                    height=41,
                    border=ft.Border.all(1, BORDER_COLOR),
                    border_radius=8,
                    padding=ft.Padding(11, 0, 11, 0),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(valor, size=14, color=TEXT_COLOR, expand=True),
                            ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=14, color=MUTED),
                        ],
                    ),
                ),
            ],
        )

    panel_detalle_curso = ft.Container(
        width=776,
        height=288,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Configuración de División Seleccionada", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("5to Año División B — Nivel Secundario", size=22, weight=ft.FontWeight.W_600, color=TEAL_DARK, expand=True),
                        ft.Container(
                            padding=ft.Padding(8, 4, 8, 4),
                            bgcolor=TEAL_LIGHT,
                            border_radius=4,
                            content=ft.Text("Activo", size=12, weight=ft.FontWeight.W_600, color=TEAL),
                        ),
                    ],
                ),
                ft.Row(
                    spacing=16,
                    controls=[
                        selector_campo("Preceptor / Tutor a Cargo", "Prof. Benítez, R."),
                        selector_campo("Aula Física Asignada", "Aula 204 (Planta Alta)"),
                        selector_campo("Orientación / Modalidad", "Economía y Gestión"),
                    ],
                ),
                ft.Text(
                    "Capacidad máxima de 35 bancas por aula homologada por normativa de infraestructura.",
                    size=13,
                    color=MUTED,
                ),
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.Container(
                            height=41,
                            bgcolor=BG_WHITE,
                            border=ft.Border.all(1, BORDER_COLOR),
                            border_radius=8,
                            padding=ft.Padding(16, 11, 16, 11),
                            content=ft.Text("Guardar", size=14, weight=ft.FontWeight.W_600, color=TEAL),
                            on_click=lambda _: None,
                        ),
                        ft.Container(
                            height=41,
                            bgcolor=BG_WHITE,
                            border=ft.Border.all(1, BORDER_COLOR),
                            border_radius=8,
                            padding=ft.Padding(16, 11, 16, 11),
                            content=ft.Text("Ver Alumnos", size=14, weight=ft.FontWeight.W_600, color=TEAL),
                            on_click=lambda _: page.go("/admin/alumnos"),
                        ),
                    ],
                ),
            ],
        ),
    )

    panel_capacidad_curso = ft.Container(
        width=320,
        height=298,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Ocupación de Matrícula", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Text("31 / 35", size=30, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Text("88.5% del cupo total cubierto para el ciclo lectivo.", size=13, color=MUTED),
                ft.Container(
                    bgcolor=BG_PAGE,
                    border_radius=8,
                    padding=14,
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text("Almirón, Santiago", size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                            ft.Text("Delegado de curso — Legajo #10245", size=12, color=MUTED),
                        ],
                    ),
                ),
                ft.Text("4 vacantes disponibles para reasignación o traslados.", size=13, color=MUTED),
            ],
        ),
    )

    fila_detalle_relaciones = ft.Row(
        spacing=20,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[panel_detalle_curso, panel_capacidad_curso],
    )

    # ==================== 5. ALERTA INFORMATIVA Y PIE ====================
    alerta_info = ft.Container(
        height=50,
        bgcolor=TEAL_LIGHT,
        border_radius=8,
        padding=16,
        content=ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE, size=18, color=TEAL),
                ft.Text(
                    "El traspaso de alumnos entre divisiones del mismo año debe ser asentado en Libro Matriz y refrendado por Secretaría.",
                    size=13,
                    color=TEAL_DARK,
                    expand=True,
                ),
            ],
        ),
    )

    nota_final = ft.Text(
        "* La asignación horaria y de materias por curso se gestiona desde el módulo de Materias y Horarios.",
        size=11,
        color=MUTED,
    )

    # ==================== 6. ENSAMBLE GENERAL ====================
    sidebar = create_sidebar(page, active_route="/admin/cursos")
    topbar = create_topbar(page, titulo="Cursos — Gestión de divisiones")

    main_content = ft.Container(
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
                        spacing=20,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            encabezado_modulo,
                            filtros_fila,
                            resumen_listado,
                            tabla_contenedor,
                            nota_tabla,
                            fila_detalle_relaciones,
                            alerta_info,
                            nota_final,
                        ],
                    ),
                ),
            ],
        ),
    )

    return ft.Row(
        expand=True,
        spacing=0,
        controls=[sidebar, main_content],
    )


if __name__ == "__main__":
    def main(page: ft.Page):
        page.title = "Educar SGE - Cursos y Divisiones"
        page.padding = 0
        page.bgcolor = BG_PAGE
        page.add(get_admin_cursos_view(page))

    ft.run(main)