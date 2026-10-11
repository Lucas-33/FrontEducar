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
ORANGE = "#D97736"
TEXT_COLOR = "#1E2A29"
MUTED = "#5C6B69"

# Badges y avisos específicos
BADGE_WARN_BG = "#FFF3E7"
BADGE_WARN_TXT = "#9A5427"


def get_admin_transporte_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa de Selección y Gestión de Rutas de Transporte Escolar."""

    # ==================== 1. ENCABEZADO Y ESTADO ====================
    encabezado_seccion = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                spacing=6,
                expand=True,
                controls=[
                    ft.Text(
                        "Gestión de Logística y Flota Escolar",
                        size=12,
                        weight=ft.FontWeight.W_400,
                        color=MUTED,
                    ),
                    ft.Text(
                        "Asignación de Recorridos y Paradas",
                        size=26,
                        weight=ft.FontWeight.W_600,
                        color=TEAL_DARK,
                    ),
                    ft.Text(
                        "Configure la línea y punto de ascenso/descenso según el domicilio real declarado del estudiante.",
                        size=14,
                        color=MUTED,
                    ),
                ],
            ),
            ft.Container(
                padding=ft.Padding(8, 4, 8, 4),
                bgcolor=TEAL_LIGHT,
                border_radius=4,
                content=ft.Text("Servicio Activo", size=12, weight=ft.FontWeight.W_600, color=TEAL),
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
                        ft.Text("Domicilio: Av. Sarmiento 450 · 5to Año B · Turno Mañana · Legajo #10245", size=13, color=MUTED),
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

    # ==================== 3. RECORRIDOS Y PARADAS (COLUMNA IZQUIERDA) ====================
    def tarjeta_recorrido(
        linea: str,
        zona: str,
        chofer: str,
        cupo_txt: str,
        seleccionado: bool = False,
        ancho: int = 346,
    ) -> ft.Container:
        return ft.Container(
            width=ancho,
            height=134,
            bgcolor=TEAL_LIGHT if seleccionado else BG_WHITE,
            border=ft.Border.all(2 if seleccionado else 1, TEAL if seleccionado else BORDER_COLOR),
            border_radius=8,
            padding=16,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Container(
                                        width=18,
                                        height=18,
                                        border_radius=9,
                                        bgcolor=BG_WHITE if seleccionado else "transparent",
                                        border=ft.Border.all(5 if seleccionado else 1, TEAL if seleccionado else BORDER_COLOR),
                                    ),
                                    ft.Text(linea, size=16, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                                ],
                            ),
                            ft.Container(
                                padding=ft.Padding(8, 4, 8, 4),
                                bgcolor=TEAL_LIGHT,
                                border_radius=4,
                                content=ft.Text("Turno Mañana", size=12, weight=ft.FontWeight.W_600, color=TEAL),
                            )
                            if seleccionado
                            else ft.Container(),
                        ],
                    ),
                    ft.Text(f"Zona de cobertura: {zona}", size=12, color=MUTED),
                    ft.Text(f"Chofer: {chofer}", size=12, color=TEXT_COLOR),
                    ft.Text(f"Disponibilidad: {cupo_txt}", size=12, color=TEXT_COLOR),
                ],
            ),
        )

    card_recorridos = ft.Container(
        width=752,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Recorridos Disponibles", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Text("Seleccione la unidad correspondiente al sector geográfico del estudiante.", size=12, color=MUTED),
                # Fila 1 de opciones
                ft.Row(
                    spacing=12,
                    controls=[
                        tarjeta_recorrido("Línea Norte 1", "Villa San Martín, Los Troncos", "Carlos Maidana", "18 / 24 asientos ocupados", seleccionado=True, ancho=347),
                        tarjeta_recorrido("Línea Norte 2", "Barrio Golf, Santa Inés", "Roberto Gómez", "22 / 24 asientos ocupados", seleccionado=False, ancho=345),
                    ],
                ),
                # Fila 2 de opciones
                ft.Row(
                    spacing=12,
                    controls=[
                        tarjeta_recorrido("Línea Sur 1", "Villa Alvear, Av. Hernandarias", "Jorge Benítez", "15 / 24 asientos ocupados", seleccionado=False, ancho=346),
                        tarjeta_recorrido("Línea Centro", "Macrocentro, Plaza 25 de Mayo", "Martín Almirón", "20 / 24 asientos ocupados", seleccionado=False, ancho=346),
                    ],
                ),
            ],
        ),
    )

    # Esquema gráfico de paradas
    def item_parada(nombre: str, horario: str, color_punto: str, color_texto: str, es_ultima: bool = False) -> ft.Container:
        return ft.Container(
            expand=True,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        spacing=5,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=12,
                                height=12,
                                border_radius=6,
                                bgcolor=color_punto,
                            ),
                            ft.Container(
                                expand=True,
                                height=2,
                                bgcolor=BORDER_COLOR if not es_ultima else "transparent",
                            ),
                        ],
                    ),
                    ft.Text(nombre, size=11, weight=ft.FontWeight.W_600, color=color_texto),
                    ft.Text(horario, size=11, color=MUTED),
                ],
            ),
        )

    card_paradas = ft.Container(
        width=752,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Parada de Ascenso y Descenso", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text("Punto de Parada Asignado", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                        ft.Container(
                            height=44,
                            bgcolor=BG_WHITE,
                            border=ft.Border.all(1, BORDER_COLOR),
                            border_radius=8,
                            padding=ft.Padding(12, 0, 12, 0),
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text("Parada #4 — Av. Sarmiento & Calle Combate de Obligado (07:15 hs)", size=14, color=TEXT_COLOR, expand=True),
                                    ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=16, color=MUTED),
                                ],
                            ),
                        ),
                    ],
                ),
                # Diagrama lineal secuencial de paradas
                ft.Container(
                    bgcolor=BG_PAGE,
                    border_radius=8,
                    padding=14,
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            item_parada("P4: Av. Sarmiento 450", "Ascenso: 07:15 hs", ORANGE, BADGE_WARN_TXT),
                            item_parada("P5: Av. Italia 600", "07:22 hs", TEAL, TEAL_DARK),
                            item_parada("P6: Calle French 120", "07:30 hs", TEAL, TEAL_DARK),
                            item_parada("Colegio Educar", "Arribo: 07:42 hs", TEAL, TEAL_DARK, es_ultima=True),
                        ],
                    ),
                ),
                ft.Text("* El estudiante debe presentarse en la parada con 5 minutos de anticipación al horario pactado.", size=11, color=MUTED),
            ],
        ),
    )

    columna_recorridos = ft.Column(
        width=752,
        spacing=20,
        controls=[card_recorridos, card_paradas],
    )

    # ==================== 4. RESUMEN DE INSCRIPCIÓN (COLUMNA DERECHA) ====================
    def fila_resumen(etiqueta: str, valor: str) -> ft.Row:
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(etiqueta, size=13, color=MUTED),
                ft.Text(valor, size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
            ],
        )

    card_resumen = ft.Container(
        width=340,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Resumen de Inscripción", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Container(
                    padding=ft.Padding(8, 4, 8, 4),
                    bgcolor=BADGE_WARN_BG,
                    border_radius=4,
                    content=ft.Text("Pendiente de Confirmación", size=12, weight=ft.FontWeight.W_600, color=BADGE_WARN_TXT),
                ),
                fila_resumen("Línea:", "Línea Norte 1"),
                fila_resumen("Turno:", "Mañana (K-12)"),
                fila_resumen("Chofer asignado:", "Carlos Maidana"),
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                fila_resumen("Celador a bordo:", "Marta Pereyra"),
                fila_resumen("Horario ida:", "07:15 hs (P4)"),
                fila_resumen("Horario regreso:", "16:45 hs (Puerta)"),
                fila_resumen("Arancel mensual:", "$ 42.500 / mes"),
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                # Mensaje de confirmación
                ft.Container(
                    bgcolor=TEAL_LIGHT,
                    border_radius=8,
                    padding=14,
                    content=ft.Row(
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=18, color=TEAL),
                            ft.Column(
                                spacing=4,
                                expand=True,
                                controls=[
                                    ft.Text("Cupo disponible", size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                                    ft.Text("La unidad cuenta con plaza libre para el turno mañana.", size=12, color=MUTED),
                                ],
                            ),
                        ],
                    ),
                ),
                ft.Button(
                    content=ft.Row(
                        spacing=8,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.CHECK, size=16, color=BG_WHITE),
                            ft.Text("Confirmar Asignación", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
                        ],
                    ),
                    bgcolor=TEAL,
                    height=40,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding(16, 11, 16, 11),
                    ),
                    on_click=lambda _: None,
                ),
                ft.Text("La confirmación registrará automáticamente la planilla de chofer y celador.", size=12, color=MUTED),
                ft.Text("Descargar credencial", size=13, weight=ft.FontWeight.W_600, color=TEAL),
            ],
        ),
    )

    card_aviso_adicional = ft.Container(
        width=340,
        bgcolor=BADGE_WARN_BG,
        border_radius=8,
        padding=14,
        content=ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE, size=18, color=ORANGE),
                ft.Column(
                    spacing=4,
                    expand=True,
                    controls=[
                        ft.Text("Póliza de Seguro de Transporte", size=13, weight=ft.FontWeight.W_600, color=BADGE_WARN_TXT),
                        ft.Text("Todas las unidades poseen cobertura médica de emergencia y rastreo satelital GPS.", size=12, color=MUTED),
                    ],
                ),
            ],
        ),
    )

    columna_derecha_resumen = ft.Column(
        width=340,
        spacing=20,
        controls=[card_resumen, card_aviso_adicional],
    )

    fila_principal_modulo = ft.Row(
        spacing=24,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[columna_recorridos, columna_derecha_resumen],
    )

    # ==================== 5. TABLA INFERIOR: ALUMNOS POR RECORRIDO ====================
    alumnos_transporte_data = [
        {"legajo": "#10245", "nombre": "Almirón, Santiago", "curso": "5to Año B", "parada": "P4: Av. Sarmiento 450", "estado": "Confirmado"},
        {"legajo": "#10246", "nombre": "Benítez, Martina", "curso": "3er Año A", "parada": "P2: Av. Lavalle 800", "estado": "Confirmado"},
        {"legajo": "#10247", "nombre": "Capra, Lautaro", "curso": "6to Grado C", "parada": "P5: Av. Italia 600", "estado": "Confirmado"},
    ]

    header_tabla_alumnos = ft.Container(
        height=36,
        bgcolor=TEAL_LIGHT,
        padding=ft.Padding(20, 10, 20, 10),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(width=110, content=ft.Text("Legajo", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=270, content=ft.Text("Alumno", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=170, content=ft.Text("Curso", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(width=270, content=ft.Text("Parada Asignada", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                ft.Container(expand=True, content=ft.Text("Estado", size=12, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
            ],
        ),
    )

    def alumno_transporte_row(item: dict) -> ft.Container:
        return ft.Container(
            height=48,
            padding=ft.Padding(20, 12, 20, 12),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=110, content=ft.Text(item["legajo"], size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=270, content=ft.Text(item["nombre"], size=13, color=TEXT_COLOR)),
                    ft.Container(width=170, content=ft.Text(item["curso"], size=13, color=TEXT_COLOR)),
                    ft.Container(width=270, content=ft.Text(item["parada"], size=13, color=MUTED)),
                    ft.Container(
                        padding=ft.Padding(8, 4, 8, 4),
                        bgcolor=TEAL_LIGHT,
                        border_radius=4,
                        content=ft.Text(item["estado"], size=12, weight=ft.FontWeight.W_600, color=TEAL),
                    ),
                ],
            ),
        )

    card_tabla_alumnos = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=16,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            spacing=0,
            controls=[
                ft.Container(
                    padding=20,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text("Alumnos por Recorrido", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                                    ft.Text("Nómina de pasajeros asignados a la Línea Norte 1", size=12, color=MUTED),
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
                                    controls=[
                                        ft.Text("Línea Norte 1", size=14, weight=ft.FontWeight.W_600, color=TEAL),
                                        ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=16, color=TEAL),
                                    ],
                                ),
                            ),
                        ],
                    ),
                ),
                header_tabla_alumnos,
                *[alumno_transporte_row(a) for a in alumnos_transporte_data],
            ],
        ),
    )

    nota_final = ft.Text(
        "* Los cambios de parada deben solicitarse con al menos 48 horas de anticipación a la Coordinación de Logística.",
        size=11,
        color=MUTED,
    )

    # ==================== 6. ENSAMBLE DEL LAYOUT GENERAL ====================
    sidebar = create_sidebar(page, active_route="/admin/transporte")
    topbar = create_topbar(page, titulo="Transporte — Selección de recorrido")

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
                            fila_principal_modulo,
                            card_tabla_alumnos,
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
        page.title = "Educar SGE - Transporte Escolar"
        page.padding = 0
        page.bgcolor = BG_PAGE
        page.add(get_admin_transporte_view(page))

    ft.run(main)