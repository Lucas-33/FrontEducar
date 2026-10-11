import flet as ft
from frontend.app.components.sidebar import create_sidebar
from frontend.app.components.topbar import create_topbar

# Paleta cromática y tokens visuales del sistema
BG_PAGE = "#F5F7F7"
BG_WHITE = "#FFFFFF"
BORDER_COLOR = "#EAE6E1"
TEAL_DARK = "#0B4F4F"
TEAL = "#0D6E6E"
TEAL_LIGHT = "#E6F2F2"
TEXT_COLOR = "#1E2A29"
MUTED = "#5C6B69"


def get_admin_materias_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa de Catálogo de Materias y Asignación Docente."""

    # ==================== 1. ENCABEZADO Y ACCIONES ====================
    encabezado_modulo = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                spacing=6,
                expand=True,
                controls=[
                    ft.Text(
                        "Plan de Estudios y Malla Curricular Institucional",
                        size=12,
                        weight=ft.FontWeight.W_400,
                        color=MUTED,
                    ),
                    ft.Text(
                        "Materias y Asignaciones Académicas",
                        size=26,
                        weight=ft.FontWeight.W_600,
                        color=TEAL_DARK,
                    ),
                    ft.Text(
                        "Administre las asignaturas por nivel, carga horaria semanal y designación de profesores titulares y suplentes.",
                        size=14,
                        color=MUTED,
                    ),
                ],
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
                        content=ft.Text("Exportar Plan", size=14, weight=ft.FontWeight.W_600, color=TEAL),
                        on_click=lambda _: None,
                    ),
                    ft.Button(
                        content=ft.Row(
                            spacing=8,
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                                ft.Text("Nueva Materia", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
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
            ),
        ],
    )

    # ==================== 2. CATÁLOGO ACADÉMICO ====================
    panel_resumen_materias = ft.Container(
        width=330,
        height=247,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Catálogo General", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Text("48", size=30, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Text("Asignaturas homologadas en vigencia", size=13, color=MUTED),
                ft.Text(
                    "Distribuidas en 3 niveles formativos con articulación curricular K-12.",
                    size=13,
                    color=TEXT_COLOR,
                ),
                ft.Text("Ver plan curricular completo", size=12, weight=ft.FontWeight.W_600, color=TEAL),
            ],
        ),
    )

    def tarjeta_asignacion_curso(curso: str, docente: str, horas: str) -> ft.Container:
        return ft.Container(
            expand=True,
            height=105,
            bgcolor=BG_PAGE,
            border_radius=8,
            padding=16,
            content=ft.Column(
                spacing=6,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        padding=ft.Padding(8, 4, 8, 4),
                        bgcolor=TEAL_LIGHT,
                        border_radius=4,
                        content=ft.Text(curso, size=12, weight=ft.FontWeight.W_600, color=TEAL),
                    ),
                    ft.Text(f"Profesor: {docente}", size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                    ft.Text(f"Carga: {horas} · Turno Tarde", size=13, color=MUTED),
                ],
            ),
        )

    panel_detalle_asignaciones = ft.Container(
        expand=True,
        height=227,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Asignaciones Activas — Matemática", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Row(
                    spacing=16,
                    controls=[
                        tarjeta_asignacion_curso("5to Año B", "Prof. Sánchez, G.", "5 horas cátedra"),
                        tarjeta_asignacion_curso("6to Año A", "Prof. Martínez, R.", "4 horas cátedra"),
                    ],
                ),
                ft.Text(
                    "100% de cobertura horaria asignada para el departamento de Ciencias Exactas.",
                    size=13,
                    color=MUTED,
                ),
            ],
        ),
    )

    fila_catalogo = ft.Row(
        spacing=20,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[panel_resumen_materias, panel_detalle_asignaciones],
    )

    # ==================== 3. BÚSQUEDA Y FILTROS ====================
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
                    hint_text="Buscar materia por nombre, código o área temática...",
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
            filtro_desplegable("Área: Todas", 123),
            filtro_desplegable("Nivel: Secundario", 129),
            filtro_desplegable("Carga: Todas", 137),
        ],
    )

    # ==================== 4. TABLA DE REGISTROS ====================
    cabecera_tabla = ft.Container(
        height=42,
        bgcolor=TEAL_LIGHT,
        padding=ft.Padding(16, 13, 16, 13),
        content=ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(width=459, expand=True, content=ft.Text("Materia y Código", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=100, content=ft.Text("Nivel", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=145, content=ft.Text("Área Temática", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=160, content=ft.Text("Carga Semanal", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=95, content=ft.Text("Estado", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=65, content=ft.Text("Acciones", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
            ],
        ),
    )

    materias_data = [
        {"codigo": "MAT-501", "nombre": "Matemática Aplicada y Álgebra", "nivel": "Secundario", "area": "Ciencias Exactas", "horas": "5 hs cátedra / semana"},
        {"codigo": "LIT-502", "nombre": "Lengua y Literatura Española", "nivel": "Secundario", "area": "Humanidades", "horas": "4 hs cátedra / semana"},
        {"codigo": "FIS-503", "nombre": "Física y Termodinámica", "nivel": "Secundario", "area": "Ciencias Naturales", "horas": "4 hs cátedra / semana"},
        {"codigo": "HIS-504", "nombre": "Historia Argentina y Latinoamericana", "nivel": "Secundario", "area": "Ciencias Sociales", "horas": "3 hs cátedra / semana"},
        {"codigo": "BIO-505", "nombre": "Biología Celular y Genética", "nivel": "Secundario", "area": "Ciencias Naturales", "horas": "3 hs cátedra / semana"},
        {"codigo": "INF-506", "nombre": "Informática, Redes y Robótica", "nivel": "Secundario", "area": "Tecnología", "horas": "3 hs cátedra / semana"},
        {"codigo": "ING-507", "nombre": "Inglés Técnico / Nivel Intermedio", "nivel": "Secundario", "area": "Lenguas Extranjeras", "horas": "3 hs cátedra / semana"},
        {"codigo": "EDF-508", "nombre": "Educación Física y Deportes", "nivel": "Secundario", "area": "Desarrollo Corporal", "horas": "3 hs cátedra / semana"},
    ]

    def materia_row(item: dict) -> ft.Container:
        return ft.Container(
            height=62,
            bgcolor=BG_WHITE,
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            padding=ft.Padding(16, 14, 16, 14),
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=459,
                        expand=True,
                        content=ft.Text(f"{item['nombre']} ({item['codigo']})", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                    ),
                    ft.Container(
                        width=100,
                        content=ft.Text(item["nivel"], size=13, color=TEXT_COLOR),
                    ),
                    ft.Container(
                        width=145,
                        content=ft.Text(item["area"], size=13, color=TEXT_COLOR),
                    ),
                    ft.Container(
                        width=160,
                        content=ft.Text(item["horas"], size=13, color=TEXT_COLOR),
                    ),
                    ft.Container(
                        width=95,
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
                        width=65,
                        content=ft.Row(
                            spacing=10,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.REMOVE_RED_EYE_OUTLINED,
                                    icon_size=16,
                                    icon_color=TEAL,
                                    tooltip="Ver programa",
                                    padding=0,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_NOTE_OUTLINED,
                                    icon_size=16,
                                    icon_color=TEAL,
                                    tooltip="Editar materia",
                                    padding=0,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    tabla_contenedor = ft.Container(
        height=538,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            spacing=0,
            controls=[
                cabecera_tabla,
                *[materia_row(m) for m in materias_data],
            ],
        ),
    )

    nota_tabla = ft.Text(
        "Haga clic en una asignatura para desplegar los programas analíticos y la asignación docente por división.",
        size=12,
        color=MUTED,
    )

    # ==================== 5. PANEL DE ASIGNACIÓN DOCENTE ====================
    def selector_campo_asignacion(etiqueta: str, valor: str) -> ft.Column:
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

    panel_gestion_asignacion = ft.Container(
        height=208,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Asignación de Cátedra a División", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Row(
                    spacing=16,
                    controls=[
                        selector_campo_asignacion("Materia Seleccionada", "Matemática Aplicada (MAT-501)"),
                        selector_campo_asignacion("Curso / División", "5to Año División B — Turno Tarde"),
                        selector_campo_asignacion("Profesor Titular a Cargo", "Prof. Sánchez, Guillermina"),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "La designación impactará de forma inmediata en el módulo de Horarios y en las listas de asistencia docente.",
                            size=13,
                            color=MUTED,
                            expand=True,
                        ),
                        ft.Container(
                            height=41,
                            bgcolor=BG_WHITE,
                            border=ft.Border.all(1, BORDER_COLOR),
                            border_radius=8,
                            padding=ft.Padding(16, 11, 16, 11),
                            content=ft.Text("Asignar Docente", size=14, weight=ft.FontWeight.W_600, color=TEAL),
                            on_click=lambda _: None,
                        ),
                    ],
                ),
            ],
        ),
    )

    nota_final = ft.Text(
        "* Los planes de estudio se encuentran homologados de acuerdo al Diseño Curricular de la Provincia del Chaco.",
        size=11,
        color=MUTED,
    )

    # ==================== 6. ENSAMBLE DEL LAYOUT GENERAL ====================
    sidebar = create_sidebar(page, active_route="/admin/materias")
    topbar = create_topbar(page, titulo="Materias — Catálogo y asignaciones")

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
                            fila_catalogo,
                            filtros_fila,
                            tabla_contenedor,
                            nota_tabla,
                            panel_gestion_asignacion,
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
        page.title = "Educar SGE - Materias y Catálogo"
        page.padding = 0
        page.bgcolor = BG_PAGE
        page.add(get_admin_materias_view(page))

    ft.run(main)