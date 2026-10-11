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
BADGE_NEUTRAL_BG = "#EEF1F0"


def get_admin_horarios_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa de Horarios y Organización Semanal."""

    # ==================== 1. ENCABEZADO Y ACCIÓN SUPERIOR ====================
    encabezado_modulo = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                spacing=6,
                expand=True,
                controls=[
                    ft.Text(
                        "Planificación y Cronograma Escolar",
                        size=12,
                        weight=ft.FontWeight.W_400,
                        color=MUTED,
                    ),
                    ft.Text(
                        "Horarios y Organización Semanal",
                        size=26,
                        weight=ft.FontWeight.W_600,
                        color=TEAL_DARK,
                    ),
                    ft.Text(
                        "Configure la grilla horaria semanal por división, valide solapamientos de aulas y compatibilidad con talleres extracurriculares.",
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
                        ft.Text("Nuevo Horario", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
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

    # ==================== 2. SELECTOR DE MODALIDAD ====================
    selector_modalidad = ft.Row(
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                height=41,
                bgcolor=TEAL,
                border=ft.Border.all(1, TEAL),
                border_radius=8,
                padding=ft.Padding(16, 11, 16, 11),
                content=ft.Text("Por Curso", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
                on_click=lambda _: None,
            ),
            ft.Container(
                height=41,
                bgcolor=BG_WHITE,
                border=ft.Border.all(1, BORDER_COLOR),
                border_radius=8,
                padding=ft.Padding(16, 11, 16, 11),
                content=ft.Text("Por Docente", size=14, weight=ft.FontWeight.W_600, color=TEAL),
                on_click=lambda _: None,
            ),
            ft.Text("Vista actual configurada para la grilla horaria completa del curso seleccionado.", size=12, color=MUTED, expand=True),
        ],
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
                    hint_text="Buscar por materia, profesor o aula...",
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
            filtro_desplegable("Curso: 5to B", 137),
            filtro_desplegable("Turno: Tarde", 144),
            filtro_desplegable("Día: Todos", 118),
        ],
    )

    # ==================== 4. CALENDARIO ACADÉMICO SEMANAL ====================
    cabecera_calendario = ft.Container(
        padding=20,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("5to Año B — Turno Tarde", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Row(
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            padding=ft.Padding(8, 4, 8, 4),
                            bgcolor=TEAL_LIGHT,
                            border_radius=4,
                            content=ft.Text("Turno Tarde", size=12, weight=ft.FontWeight.W_600, color=TEAL),
                        ),
                        ft.Container(
                            padding=ft.Padding(8, 4, 8, 4),
                            bgcolor=BADGE_NEUTRAL_BG,
                            border_radius=4,
                            content=ft.Text("Contraturno", size=12, weight=ft.FontWeight.W_600, color=MUTED),
                        ),
                        ft.Text("Recreos: 15 min", size=12, color=MUTED),
                    ],
                ),
            ],
        ),
    )

    cabecera_dias = ft.Container(
        height=42,
        bgcolor=TEAL_LIGHT,
        padding=ft.Padding(16, 12, 16, 12),
        content=ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(width=104, content=ft.Text("Hora", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(expand=True, content=ft.Text("Lunes", size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(expand=True, content=ft.Text("Martes", size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(expand=True, content=ft.Text("Miércoles", size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(expand=True, content=ft.Text("Jueves", size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(expand=True, content=ft.Text("Viernes", size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
            ],
        ),
    )

    def celda_clase(materia: str, docente: str, es_contraturno: bool = False) -> ft.Container:
        bg = BADGE_NEUTRAL_BG if es_contraturno else TEAL_LIGHT
        border_col = BORDER_COLOR if es_contraturno else TEAL
        return ft.Container(
            expand=True,
            height=62,
            bgcolor=bg,
            border=ft.Border(left=ft.BorderSide(3, border_col)),
            border_radius=6,
            padding=10,
            content=ft.Column(
                spacing=4,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text(materia, size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                    ft.Text(docente, size=11, color=MUTED),
                ],
            ),
        )

    def franja_horaria(hora: str, clases: list[tuple[str, str, bool]]) -> ft.Container:
        return ft.Container(
            height=76,
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            padding=ft.Padding(16, 7, 16, 7),
            content=ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=104, content=ft.Text(hora, size=12, color=MUTED)),
                    ft.Row(
                        spacing=8,
                        expand=True,
                        controls=[celda_clase(m, d, c) for m, d, c in clases],
                    ),
                ],
            ),
        )

    def franja_recreo(hora: str, titulo: str) -> ft.Container:
        return ft.Container(
            height=46,
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            padding=ft.Padding(16, 7, 16, 7),
            content=ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=104, content=ft.Text(hora, size=12, color=MUTED)),
                    ft.Container(
                        expand=True,
                        height=32,
                        bgcolor=BG_PAGE,
                        border_radius=6,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(titulo, size=12, color=MUTED),
                    ),
                ],
            ),
        )

    # Datos estructurados del cronograma semanal
    grilla_calendario = ft.Container(
        height=654,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            spacing=0,
            controls=[
                cabecera_calendario,
                cabecera_dias,
                franja_horaria("13:15 - 14:00", [
                    ("Matemática", "Prof. Sánchez", False),
                    ("Lengua", "Prof. Duarte", False),
                    ("Matemática", "Prof. Sánchez", False),
                    ("Física", "Prof. Martínez", False),
                    ("Historia", "Prof. Morales", False),
                ]),
                franja_horaria("14:00 - 14:45", [
                    ("Matemática", "Prof. Sánchez", False),
                    ("Lengua", "Prof. Duarte", False),
                    ("Biología", "Prof. Gómez", False),
                    ("Física", "Prof. Martínez", False),
                    ("Historia", "Prof. Morales", False),
                ]),
                franja_recreo("14:45 - 15:00", "Recreo general de media tarde"),
                franja_horaria("15:00 - 15:45", [
                    ("Inglés Técnico", "Prof. Rossi", False),
                    ("Química", "Prof. Capra", False),
                    ("Informática", "Prof. Ortega", False),
                    ("Filosofía", "Prof. Romero", False),
                    ("Geografía", "Prof. Benítez", False),
                ]),
                franja_horaria("15:45 - 16:30", [
                    ("Inglés Técnico", "Prof. Rossi", False),
                    ("Química", "Prof. Capra", False),
                    ("Informática", "Prof. Ortega", False),
                    ("Filosofía", "Prof. Romero", False),
                    ("Geografía", "Prof. Benítez", False),
                ]),
                franja_recreo("16:30 - 16:45", "Recreo de articulación con contraturno"),
                franja_horaria("16:45 - 17:30", [
                    ("Ed. Física", "Prof. Vargas", True),
                    ("Taller Contable", "Prof. Benítez", True),
                    ("Ed. Física", "Prof. Vargas", True),
                    ("Taller Contable", "Prof. Benítez", True),
                    ("Tutoría", "Prof. Sánchez", True),
                ]),
            ],
        ),
    )

    # ==================== 5. CONTROL, DETALLE Y COMPATIBILIDAD ====================
    def tarjeta_actividad_contraturno(nombre: str, horario: str, espacio: str) -> ft.Container:
        return ft.Container(
            expand=True,
            height=82,
            bgcolor=BG_PAGE,
            border_radius=8,
            padding=12,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(nombre, size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                    ft.Text(horario, size=12, color=MUTED),
                    ft.Text(espacio, size=12, color=MUTED),
                ],
            ),
        )

    panel_validacion_solapamientos = ft.Container(
        width=776,
        height=242,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Validación de Carga Horaria y Contraturno", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "Compatibilidad con talleres extracurriculares y disciplinas deportivas registradas.",
                            size=13,
                            color=TEXT_COLOR,
                            expand=True,
                        ),
                        ft.Container(
                            padding=ft.Padding(8, 4, 8, 4),
                            bgcolor=TEAL_LIGHT,
                            border_radius=4,
                            content=ft.Text("Sin solapamientos", size=12, weight=ft.FontWeight.W_600, color=TEAL),
                        ),
                    ],
                ),
                ft.Row(
                    spacing=12,
                    controls=[
                        tarjeta_actividad_contraturno("Natación — Grupo B (Avanzado)", "Martes y Jueves 15:30 a 17:00 hs", "Complejo Acuático Climatizado"),
                        tarjeta_actividad_contraturno("Básquetbol — Grupo Juvenil B", "Lunes y Miércoles 16:00 a 17:30 hs", "Cancha Cubierta Central 1"),
                    ],
                ),
                ft.Text(
                    "Todos los módulos curriculares respetan el intervalo reglamentario con los talleres extracurriculares.",
                    size=12,
                    color=TEAL,
                ),
            ],
        ),
    )

    panel_detalle_curso = ft.Container(
        width=320,
        height=316,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Detalle del Curso", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Container(
                    padding=ft.Padding(8, 4, 8, 4),
                    bgcolor=TEAL_LIGHT,
                    border_radius=4,
                    content=ft.Text("Aula 204", size=12, weight=ft.FontWeight.W_600, color=TEAL),
                ),
                ft.Text("5to Año División B", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Text("Preceptor a cargo: Prof. Benítez, R.", size=13, color=TEXT_COLOR),
                ft.Text("Carga horaria: 30 hs cátedra semanales", size=13, color=MUTED),
                ft.Text(
                    "Los cambios en las asignaciones de aulas físicas deben coordinarse con Intendencia del edificio.",
                    size=12,
                    color=MUTED,
                ),
                ft.Text("Descargar grilla oficial en PDF", size=12, weight=ft.FontWeight.W_600, color=TEAL),
            ],
        ),
    )

    fila_control_detalle = ft.Row(
        spacing=20,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[panel_validacion_solapamientos, panel_detalle_curso],
    )

    nota_final = ft.Text(
        "* La asignación horaria respeta los límites de jornada continua establecidos en el Reglamento General de Escuelas Secundarias.",
        size=11,
        color=MUTED,
    )

    # ==================== 6. ENSAMBLE DEL LAYOUT GENERAL ====================
    sidebar = create_sidebar(page, active_route="/admin/horarios")
    topbar = create_topbar(page, titulo="Horarios — Organización semanal")

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
                            selector_modalidad,
                            filtros_fila,
                            grilla_calendario,
                            fila_control_detalle,
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
        page.title = "Educar SGE - Horarios y Organización Semanal"
        page.padding = 0
        page.bgcolor = BG_PAGE
        page.add(get_admin_horarios_view(page))

    ft.run(main)