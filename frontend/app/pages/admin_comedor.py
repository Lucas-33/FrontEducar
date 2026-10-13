import flet as ft
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BADGE_WARN_BG,
    BADGE_WARN_TXT,
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    MUTED,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)


def get_admin_comedor_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa de Inscripción y Control del Servicio de Comedor usando AdminLayout."""

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
                        "Gestión de Servicios Complementarios y Nutrición",
                        size=12,
                        weight=ft.FontWeight.W_400,
                        color=MUTED,
                    ),
                    ft.Text(
                        "Inscripción al Servicio de Comedor Escolar",
                        size=26,
                        weight=ft.FontWeight.W_600,
                        color=TEAL_DARK,
                    ),
                    ft.Text(
                        "Registre el alta del estudiante en el comedor institucional, declare dietas especiales y controle la asignación de turnos.",
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
        border_radius=CARD_RADIUS,
        padding=18,
        content=ft.Row(
            spacing=20,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=6,
                    width=290,
                    controls=[
                        ft.Text("Seleccionar Alumno", size=12, weight=ft.FontWeight.W_600, color=MUTED),
                        ft.Container(
                            height=38,
                            border=ft.Border.all(1, BORDER_COLOR),
                            border_radius=BORDER_RADIUS,
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
                ft.Container(
                    width=44,
                    height=44,
                    bgcolor=TEAL_LIGHT,
                    border_radius=22,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text("SA", size=16, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ),
                ft.Column(
                    spacing=4,
                    expand=True,
                    controls=[
                        ft.Text("Santiago Almirón", size=17, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                        ft.Text("5to Año B · Turno Mañana · Legajo #10245 · Ficha Médica Aprobada", size=13, color=MUTED),
                    ],
                ),
                ft.Container(
                    padding=ft.Padding(8, 4, 8, 4),
                    bgcolor=TEAL_LIGHT,
                    border_radius=4,
                    content=ft.Text("Matrícula Activa", size=12, weight=ft.FontWeight.W_600, color=TEAL),
                ),
            ],
        ),
    )

    # ==================== 3. VERIFICACIÓN ACTUAL DEL SERVICIO ====================
    estado_servicio_banner = ft.Container(
        height=84,
        bgcolor=TEAL_LIGHT,
        border_radius=CARD_RADIUS,
        padding=20,
        content=ft.Row(
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=42,
                    height=42,
                    bgcolor=BG_WHITE,
                    border_radius=10,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(ft.Icons.RESTAURANT_OUTLINED, size=22, color=TEAL),
                ),
                ft.Column(
                    spacing=4,
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Estado del Comedor: Pendiente de Inscripción", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                        ft.Text("El estudiante no registra alta en el servicio de almuerzo para el ciclo lectivo en curso.", size=13, color=MUTED),
                    ],
                ),
                ft.Container(
                    padding=ft.Padding(8, 4, 8, 4),
                    bgcolor=TEAL_LIGHT,
                    border_radius=4,
                    content=ft.Text("Habilitado", size=12, weight=ft.FontWeight.W_600, color=TEAL),
                ),
            ],
        ),
    )

    # ==================== 4. COLUMNA IZQUIERDA: FORMULARIO (FLUIDA) ====================
    card_datos_alta = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Datos de Alta en el Comedor", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Text("Complete la información administrativa para la habilitación de la vianda institucional.", size=13, color=MUTED),
                ft.Row(
                    spacing=16,
                    controls=[
                        ft.Column(
                            spacing=6,
                            expand=True,
                            controls=[
                                ft.Text("Fecha de Inicio *", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                ft.Container(
                                    height=44,
                                    bgcolor=BG_WHITE,
                                    border=ft.Border.all(1, BORDER_COLOR),
                                    border_radius=BORDER_RADIUS,
                                    padding=ft.Padding(12, 0, 12, 0),
                                    content=ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Text("03/03/2025", size=14, color=TEXT_COLOR),
                                            ft.Icon(ft.Icons.CALENDAR_MONTH_OUTLINED, size=16, color=MUTED),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                        ft.Column(
                            spacing=6,
                            expand=True,
                            controls=[
                                ft.Text("Turno de Comedor *", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                ft.Container(
                                    height=44,
                                    bgcolor=BG_PAGE,
                                    border=ft.Border.all(1, BORDER_COLOR),
                                    border_radius=BORDER_RADIUS,
                                    padding=ft.Padding(12, 0, 12, 0),
                                    alignment=ft.Alignment(-1, 0),
                                    content=ft.Text("Turno Intermedio (12:30 a 13:30 hs)", size=14, color=MUTED),
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Row(
                    spacing=16,
                    controls=[
                        ft.Column(
                            spacing=6,
                            expand=True,
                            controls=[
                                ft.Text("Nivel Académico Vinculado", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                ft.Container(
                                    height=44,
                                    bgcolor=BG_PAGE,
                                    border=ft.Border.all(1, BORDER_COLOR),
                                    border_radius=BORDER_RADIUS,
                                    padding=ft.Padding(12, 0, 12, 0),
                                    alignment=ft.Alignment(-1, 0),
                                    content=ft.Text("Nivel Secundario", size=14, color=MUTED),
                                ),
                            ],
                        ),
                        ft.Column(
                            spacing=6,
                            expand=True,
                            controls=[
                                ft.Text("Curso y División", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                                ft.Container(
                                    height=44,
                                    bgcolor=BG_PAGE,
                                    border=ft.Border.all(1, BORDER_COLOR),
                                    border_radius=BORDER_RADIUS,
                                    padding=ft.Padding(12, 0, 12, 0),
                                    alignment=ft.Alignment(-1, 0),
                                    content=ft.Text("5to Año División B", size=14, color=MUTED),
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Text("* El turno de comedor se asigna automáticamente de acuerdo a los horarios de clase del curso.", size=12, color=MUTED),
            ],
        ),
    )

    card_info_complementaria = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Información Nutricional y Médica", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Text("Detalle de restricciones, menú asignado y notas bromatológicas obligatorias.", size=13, color=MUTED),
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text("Tipo de Menú Asignado *", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                        ft.Container(
                            height=44,
                            bgcolor=BG_WHITE,
                            border=ft.Border.all(1, BORDER_COLOR),
                            border_radius=BORDER_RADIUS,
                            padding=ft.Padding(12, 0, 12, 0),
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text("Menú General / Estándar (Balanceado K-12)", size=14, color=TEXT_COLOR, expand=True),
                                    ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=16, color=MUTED),
                                ],
                            ),
                        ),
                    ],
                ),
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text("Alergias o Restricciones Alimentarias", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                        ft.Container(
                            height=70,
                            bgcolor=BG_PAGE,
                            border=ft.Border.all(1, BORDER_COLOR),
                            border_radius=BORDER_RADIUS,
                            padding=12,
                            alignment=ft.Alignment(-1, -1),
                            content=ft.Text("Sin alergias declaradas en la ficha médica de admisión.", size=14, color=MUTED),
                        ),
                    ],
                ),
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text("Observaciones del Servicio Médico y Nutricional", size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                        ft.Container(
                            height=82,
                            bgcolor=BG_PAGE,
                            border=ft.Border.all(1, BORDER_COLOR),
                            border_radius=BORDER_RADIUS,
                            padding=12,
                            alignment=ft.Alignment(-1, -1),
                            content=ft.Text("El estudiante cuenta con apto médico general. No requiere menús diferenciados por celiaquía o intolerancia a la lactosa.", size=14, color=MUTED),
                        ),
                    ],
                ),
                ft.Text("* Toda modificación en la dieta requerirá certificado médico emitido por especialista matriculado.", size=12, color=MUTED),
            ],
        ),
    )

    columna_formulario = ft.Column(
        expand=True,
        spacing=20,
        controls=[card_datos_alta, card_info_complementaria],
    )

    # ==================== 5. COLUMNA DERECHA: RESUMEN Y CONFIRMACIÓN ====================
    def fila_resumen(etiqueta: str, valor: str) -> ft.Row:
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(etiqueta, size=13, color=MUTED),
                ft.Text(valor, size=13, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
            ],
        )

    card_resumen = ft.Container(
        width=360,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Resumen del Alta", size=18, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                ft.Container(
                    padding=ft.Padding(8, 4, 8, 4),
                    bgcolor=BADGE_WARN_BG,
                    border_radius=4,
                    content=ft.Text("Pendiente de Confirmación", size=12, weight=ft.FontWeight.W_600, color=BADGE_WARN_TXT),
                ),
                ft.Text("Verifique los datos nutricionales y de facturación antes de validar la plaza.", size=13, color=MUTED),
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                fila_resumen("Plan de Comedor:", "Completo (Lun a Vie)"),
                fila_resumen("Turno:", "12:30 a 13:30 hs"),
                fila_resumen("Menú asignado:", "General Estándar"),
                fila_resumen("Inicio del servicio:", "03/03/2025"),
                fila_resumen("Alergias:", "Ninguna registrada"),
                fila_resumen("Arancel mensual:", "$ 68.000 / mes"),
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                fila_resumen("Sede:", "Resistencia Central"),
                fila_resumen("Facturación:", "Débito con cuota"),
                ft.Container(
                    bgcolor=TEAL_LIGHT,
                    border_radius=BORDER_RADIUS,
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
                                    ft.Text("Cupo de vianda disponible", size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                                    ft.Text("El salón comedor cuenta con capacidad para el turno asignado.", size=12, color=MUTED),
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
                            ft.Text("Confirmar Inscripción", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE),
                        ],
                    ),
                    bgcolor=TEAL,
                    height=40,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
                        padding=ft.Padding(16, 11, 16, 11),
                    ),
                    on_click=lambda _: None,
                ),
                ft.Text("La confirmación emitirá el carnet digital de comedor escolar del alumno.", size=12, color=MUTED),
                ft.Text("Ver menú mensual", size=13, weight=ft.FontWeight.W_600, color=TEAL),
            ],
        ),
    )

    card_aviso_bromatologico = ft.Container(
        width=360,
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
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
                        ft.Text("Control Bromatológico y Nutricional", size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK),
                        ft.Text("Los menús son supervisados por licenciados en nutrición bajo normas de calidad ISO.", size=12, color=MUTED),
                    ],
                ),
            ],
        ),
    )

    columna_derecha_resumen = ft.Column(
        width=360,
        spacing=20,
        controls=[card_resumen, card_aviso_bromatologico],
    )

    fila_principal_modulo = ft.Row(
        spacing=24,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[columna_formulario, columna_derecha_resumen],
    )

    nota_pie = ft.Text(
        "* Los días de inasistencia programada deben notificarse antes de las 08:30 hs a través del Portal de Familias para la bonificación de vianda.",
        size=11,
        color=MUTED,
    )

    # ==================== 6. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Comedor — Inscripción al servicio",
        active_route="/admin/comedor",
        spacing=20,
        content_controls=[
            encabezado_seccion,
            alumno_card,
            estado_servicio_banner,
            fila_principal_modulo,
            nota_pie,
        ],
    )