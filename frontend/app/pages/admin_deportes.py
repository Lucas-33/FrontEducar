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
ORANGE = "#D97736"
TEXT_COLOR = "#1E2A29"
MUTED = "#5C6B69"

# Badges y estados específicos
BADGE_WARN_BG = "#FFF3E7"
BADGE_WARN_TXT = "#9A5427"
BADGE_DANGER_BG = "#FBEFEE"
BADGE_DANGER_TXT = "#B64C45"
BADGE_NEUTRAL_BG = "#EEF1F0"


def get_admin_deportes_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa de Asignación de Deportes y Control de Cupos."""

    # ==================== 1. ENCABEZADO Y ACCIÓN SUPERIOR ====================
    encabezado_seccion = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                spacing=6,
                expand=True,
                controls=[
                    ft.Text(
                        "Gestión de Educación Física y Talleres Deportivos",
                        size=12,
                        weight=ft.FontWeight.W_400,
                        color=MUTED,
                    ),
                    ft.Text(
                        "Control de Cupos y Asignación de Disciplinas",
                        size=26,
                        weight=ft.FontWeight.W_600,
                        color=TEAL_DARK,
                    ),
                    ft.Text(
                        "Supervise la disponibilidad por turnos, niveles y verifique los requisitos médicos antes de confirmar la inscripción.",
                        size=14,
                        color=MUTED,
                    ),
                ],
            ),
            ft.Container(
                height=40,
                bgcolor=BG_WHITE,
                border=ft.Border.all(1, BORDER_COLOR),
                border_radius=8,
                padding=ft.Padding(16, 11, 16, 11),
                content=ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.TUNE, size=16, color=TEAL),
                        ft.Text("Configurar Cupos", size=14, weight=ft.FontWeight.W_600, color=TEAL),
                    ],
                ),
                on_click=lambda _: None,
            ),
        ],
    )

    # ==================== 2. TARJETA ALUMNO SELECCIONADO ====================
    alumno_card = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=18,
        content=ft.Row(
            spacing=20,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                # Buscador de alumno rápido
                ft.Column(
                    spacing=6,
                    width=290,
                    controls=[
                        ft.Text("Seleccionar Alumno", size=12, weight=ft.FontWeight.W_600, color=MUTED),
                        ft.Container(
                            height=38,
                            border=ft.Border.all(1, BORDER_COLOR),
                            border_radius=8,
                            padding=ft.Padding(10, 0, 10, 0),
                            content=ft.Row(
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(ft.Icons.SEARCH, size=16, color=MUTED),
                                    ft.Text("Almirón, Santiago (#10245)", size=14, color=TEXT_COLOR, expand=True),
                                    ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=14, color=MUTED),
                                ],
                            ),
                        ),
                    ],
                ),
                # Avatar con iniciales
                ft.Container(
                    width=44,
                    height=44,
                    bgcolor=TEAL_LIGHT,
                    border_radius=22,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text("SA", size=16, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ),
                # Ficha breve de datos
                ft.Column(
                    spacing=4,
                    expand=True,
                    controls=[
                        ft.Text("Santiago Almirón", size=17, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                        ft.Text("5to Año B · Turno Mañana · Legajo #10245 · Ficha Médica Aprobada", size=13, color=MUTED),
                    ],
                ),
                # Estado de matrícula
                ft.Container(
                    padding=ft.Padding(8, 4, 8, 4),
                    bgcolor=TEAL_LIGHT,
                    border_radius=4,
                    content=ft.Text("Matrícula Activa", size=12, weight=ft.FontWeight.W_600, color=TEAL),
                ),
            ],
        ),
    )

    # ==================== 3. BLOQUES DE INSCRIPCIÓN Y ASIGNACIÓN ====================
    # Bloque Izquierdo: Inscripción Activa
    bloque_inscripcion_activa = ft.Container(
        width=434,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Inscripción Deportiva", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("1 de 2 cupos", size=22, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                        ft.Container(
                            padding=ft.Padding(8, 4, 8, 4),
                            bgcolor=TEAL_LIGHT,
                            border_radius=4,
                            content=ft.Text("Cupo 1 asignado", size=12, weight=ft.FontWeight.W_600, color=TEAL),
                        ),
                    ],
                ),
                ft.Container(
                    bgcolor=BG_PAGE,
                    border_radius=8,
                    padding=14,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                spacing=4,
                                expand=True,
                                controls=[
                                    ft.Text("Natación — Grupo B (Avanzado)", size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                    ft.Text("Martes y Jueves 15:30 a 17:00 hs · Complejo Acuático", size=13, color=MUTED),
                                ],
                            ),
                            ft.Container(
                                padding=ft.Padding(8, 4, 8, 4),
                                bgcolor=TEAL_LIGHT,
                                border_radius=4,
                                content=ft.Text("Activo", size=12, weight=ft.FontWeight.W_600, color=TEAL),
                            ),
                        ],
                    ),
                ),
                ft.Text("El alumno ya cuenta con la primera disciplina curricular asignada.", size=12, color=MUTED),
            ],
        ),
    )

    # Bloque Derecho: Segunda Disciplina Seleccionada
    bloque_segunda_disciplina = ft.Container(
        expand=True,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Segunda Disciplina Seleccionada", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=4,
                            expand=True,
                            controls=[
                                ft.Text("Básquetbol — Grupo Juvenil B", size=20, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                                ft.Text("Lunes y Miércoles 16:00 a 17:30 hs · Cancha Cubierta 1", size=13, color=MUTED),
                            ],
                        ),
                        ft.Container(
                            padding=ft.Padding(8, 4, 8, 4),
                            bgcolor=BADGE_WARN_BG,
                            border_radius=4,
                            content=ft.Text("Preseleccionado", size=12, weight=ft.FontWeight.W_600, color=BADGE_WARN_TXT),
                        ),
                    ],
                ),
                ft.Text("4 cupos disponibles actualmente para este turno.", size=13, color=TEAL),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "Al confirmar, se reservará la plaza de manera definitiva y se enviará la notificación a Secretaría.",
                            size=12,
                            color=MUTED,
                            expand=True,
                        ),
                        ft.Button(
                            content=ft.Text("Confirmar Asignación", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
                            bgcolor=TEAL,
                            height=40,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.Padding(16, 11, 16, 11),
                            ),
                            on_click=lambda _: None,
                        ),
                    ],
                ),
            ],
        ),
    )

    fila_inscripciones = ft.Row(
        spacing=20,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[bloque_inscripcion_activa, bloque_segunda_disciplina],
    )

    # ==================== 4. TABLA DE DISPONIBILIDAD DE GRUPOS ====================
    # Encabezado y Filtros de la Tabla
    tabla_header_filtros = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                spacing=4,
                controls=[
                    ft.Text("Disponibilidad de Grupos", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                    ft.Text("Oferta académica deportiva para el Ciclo 2025", size=12, color=MUTED),
                ],
            ),
            ft.Row(
                spacing=8,
                controls=[
                    ft.Container(
                        height=40,
                        bgcolor=BG_WHITE,
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=8,
                        padding=ft.Padding(16, 11, 16, 11),
                        content=ft.Row(
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text("Nivel: Todos", size=14, weight=ft.FontWeight.W_600, color=TEAL),
                                ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=16, color=TEAL),
                            ],
                        ),
                    ),
                    ft.Container(
                        height=40,
                        bgcolor=BG_WHITE,
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=8,
                        padding=ft.Padding(16, 11, 16, 11),
                        content=ft.Row(
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text("Turno: Tarde", size=14, weight=ft.FontWeight.W_600, color=TEAL),
                                ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=16, color=TEAL),
                            ],
                        ),
                    ),
                ],
            ),
        ],
    )

    # Cabecera de columnas
    cabecera_columnas = ft.Container(
        height=40,
        bgcolor=TEAL_LIGHT,
        padding=ft.Padding(16, 12, 16, 12),
        content=ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(width=256, content=ft.Text("Disciplina y Grupo", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK), expand=True),
                ft.Container(width=80, content=ft.Text("Nivel", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=130, content=ft.Text("Docente a Cargo", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=144, content=ft.Text("Horario", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=130, content=ft.Text("Capacidad", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=152, content=ft.Text("Validación Médica", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=120, content=ft.Text("Asignación", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
            ],
        ),
    )

    # Datos de grupos deportivos
    grupos_deportivos = [
        {
            "disciplina": "Natación — Grupo B (Avanzado)",
            "espacio": "Complejo Acuático Climatizado",
            "nivel": "Secundario",
            "docente": "Prof. Vargas, E.",
            "dias": "Mar y Jue",
            "horas": "15:30 a 17:00 hs",
            "cupo_txt": "21 / 30 ocupados",
            "porcentaje": 0.70,
            "val_txt": "Aprobada",
            "val_bg": BADGE_NEUTRAL_BG,
            "val_color": MUTED,
            "accion_txt": "Asignado",
            "accion_color": MUTED,
            "seleccionado": False,
        },
        {
            "disciplina": "Básquetbol — Grupo Juvenil B",
            "espacio": "Cancha Cubierta Central 1",
            "nivel": "Secundario",
            "docente": "Prof. Ortega, L.",
            "dias": "Lun y Mié",
            "horas": "16:00 a 17:30 hs",
            "cupo_txt": "21 / 25 ocupados",
            "porcentaje": 0.84,
            "val_txt": "Aprobada",
            "val_bg": TEAL_LIGHT,
            "val_color": TEAL,
            "accion_txt": "Seleccionado",
            "accion_color": TEAL_DARK,
            "seleccionado": True,
        },
        {
            "disciplina": "Fútbol — Cadetes",
            "espacio": "Cancha Sintética Principal",
            "nivel": "Secundario",
            "docente": "Prof. Benítez, R.",
            "dias": "Mar y Jue",
            "horas": "17:00 a 18:30 hs",
            "cupo_txt": "18 / 30 ocupados",
            "porcentaje": 0.60,
            "val_txt": "Sin presentar",
            "val_bg": BADGE_WARN_BG,
            "val_color": BADGE_WARN_TXT,
            "accion_txt": "Seleccionar",
            "accion_color": MUTED,
            "seleccionado": False,
        },
        {
            "disciplina": "Vóleibol — Femenino Juvenil",
            "espacio": "Microestadio Polideportivo",
            "nivel": "Secundario",
            "docente": "Prof. Sánchez, G.",
            "dias": "Lun y Mié",
            "horas": "17:30 a 19:00 hs",
            "cupo_txt": "20 / 20 cupos llenos",
            "porcentaje": 1.00,
            "val_txt": "Aprobada",
            "val_bg": BADGE_DANGER_BG,
            "val_color": BADGE_DANGER_TXT,
            "accion_txt": "Sin cupo",
            "accion_color": MUTED,
            "seleccionado": False,
        },
        {
            "disciplina": "Atletismo — Pista Libre",
            "espacio": "Pista Olímpica Perimetral",
            "nivel": "Primario/Sec",
            "docente": "Prof. Duarte, M.",
            "dias": "Vie",
            "horas": "15:00 a 17:00 hs",
            "cupo_txt": "26 / 40 ocupados",
            "porcentaje": 0.65,
            "val_txt": "Aprobada",
            "val_bg": TEAL_LIGHT,
            "val_color": TEAL,
            "accion_txt": "Seleccionar",
            "accion_color": TEAL,
            "seleccionado": False,
        },
        {
            "disciplina": "Ajedrez — Nivel Competitivo",
            "espacio": "Aula Multiespacio 3",
            "nivel": "K-12",
            "docente": "Prof. Capra, J.",
            "dias": "Sáb",
            "horas": "09:30 a 11:30 hs",
            "cupo_txt": "12 / 18 ocupados",
            "porcentaje": 0.66,
            "val_txt": "Aprobada",
            "val_bg": TEAL_LIGHT,
            "val_color": TEAL,
            "accion_txt": "Seleccionar",
            "accion_color": TEAL,
            "seleccionado": False,
        },
        {
            "disciplina": "Danza y Expresión — Nivel 2",
            "espacio": "Sala de Espejos Planta Baja",
            "nivel": "Primario",
            "docente": "Prof. Flores, A.",
            "dias": "Mar y Jue",
            "horas": "14:00 a 15:30 hs",
            "cupo_txt": "18 / 25 ocupados",
            "porcentaje": 0.72,
            "val_txt": "Aprobada",
            "val_bg": TEAL_LIGHT,
            "val_color": TEAL,
            "accion_txt": "Seleccionar",
            "accion_color": TEAL,
            "seleccionado": False,
        },
        {
            "disciplina": "Gimnasia Artística — Inicial",
            "espacio": "Gimnasio Cubierto 2",
            "nivel": "Primario",
            "docente": "Prof. Martínez, R.",
            "dias": "Lun y Mié",
            "horas": "14:30 a 16:00 hs",
            "cupo_txt": "15 / 24 ocupados",
            "porcentaje": 0.62,
            "val_txt": "Aprobada",
            "val_bg": TEAL_LIGHT,
            "val_color": TEAL,
            "accion_txt": "Seleccionar",
            "accion_color": TEAL,
            "seleccionado": False,
        },
    ]

    def grupo_row(item: dict) -> ft.Container:
        barra_ancho = 112 * item["porcentaje"]
        color_barra = ORANGE if item["porcentaje"] >= 1.0 else TEAL

        return ft.Container(
            height=70,
            bgcolor=TEAL_LIGHT if item["seleccionado"] else BG_WHITE,
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            padding=ft.Padding(16, 12, 16, 12),
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # Disciplina y Espacio
                    ft.Column(
                        spacing=3,
                        expand=True,
                        controls=[
                            ft.Text(item["disciplina"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                            ft.Text(item["espacio"], size=11, color=MUTED),
                        ],
                    ),
                    # Nivel
                    ft.Container(width=80, content=ft.Text(item["nivel"], size=13, color=MUTED)),
                    # Docente
                    ft.Container(width=130, content=ft.Text(item["docente"], size=13, color=TEXT_COLOR)),
                    # Horario
                    ft.Column(
                        spacing=3,
                        width=144,
                        controls=[
                            ft.Text(item["dias"], size=13, color=TEXT_COLOR),
                            ft.Text(item["horas"], size=12, color=MUTED),
                        ],
                    ),
                    # Capacidad con Barra de Progreso
                    ft.Column(
                        spacing=5,
                        width=130,
                        controls=[
                            ft.Text(item["cupo_txt"], size=12, color=TEXT_COLOR),
                            ft.Stack(
                                width=112,
                                height=4,
                                controls=[
                                    ft.Container(width=112, height=4, bgcolor=BORDER_COLOR, border_radius=2),
                                    ft.Container(width=barra_ancho, height=4, bgcolor=color_barra, border_radius=2),
                                ],
                            ),
                        ],
                    ),
                    # Validación médica
                    ft.Container(
                        width=152,
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    padding=ft.Padding(8, 4, 8, 4),
                                    bgcolor=item["val_bg"],
                                    border_radius=4,
                                    content=ft.Text(
                                        item["val_txt"],
                                        size=12,
                                        weight=ft.FontWeight.W_600,
                                        color=item["val_color"],
                                    ),
                                )
                            ]
                        ),
                    ),
                    # Asignación interactiva
                    ft.Container(
                        width=120,
                        content=ft.Text(
                            item["accion_txt"],
                            size=12,
                            weight=ft.FontWeight.W_600,
                            color=item["accion_color"],
                        ),
                    ),
                ],
            ),
        )

    # Resumen inferior de cupos
    resumen_tabla = ft.Container(
        padding=16,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("Total en oferta: 8 disciplinas activas para el ciclo", size=12, color=MUTED),
                ft.Text("Cupos totales: 151 / 202 plazas cubiertas (74.7%)", size=12, color=MUTED),
            ],
        ),
    )

    tabla_contenedor = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            spacing=0,
            controls=[
                ft.Container(padding=20, content=tabla_header_filtros),
                cabecera_columnas,
                *[grupo_row(g) for g in grupos_deportivos],
                resumen_tabla,
            ],
        ),
    )

    # Nota final al pie
    nota_pie = ft.Text(
        "* Los alumnos de nivel inicial y primario realizan natación recreativa y habilidades motrices de forma curricular integrada.",
        size=11,
        color=MUTED,
    )

    # ==================== 5. ENSAMBLE DEL LAYOUT GENERAL ====================
    sidebar = create_sidebar(page, active_route="/admin/deportes")
    topbar = create_topbar(page, titulo="Deportes — Asignación y control de cupos")

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
                            encabezado_seccion,
                            alumno_card,
                            fila_inscripciones,
                            tabla_contenedor,
                            nota_pie,
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
        page.title = "Educar SGE - Deportes y Cupos"
        page.padding = 0
        page.bgcolor = BG_PAGE
        page.add(get_admin_deportes_view(page))

    ft.run(main)