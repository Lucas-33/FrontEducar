import flet as ft
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    AMBER_STATE,
    BADGE_YELLOW_BG,
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    MUTED,
    ONLINE_GREEN,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)


def get_admin_dashboard_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa del panel interno Educar SGE usando AdminLayout."""

    # ==================== 1. BANNER INSTITUCIONAL ====================
    welcome_banner = ft.Container(
        height=110,
        bgcolor=TEAL_DARK,
        border_radius=CARD_RADIUS,
        padding=ft.Padding(20, 20, 20, 20),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=8,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "¡Buen día, Estela! Ciclo Lectivo 2025 Activo",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=BG_WHITE,
                        ),
                        ft.Text(
                            "El período de inscripciones para el nivel inicial y primario cuenta con alta demanda de solicitudes esta semana. Revisa los módulos pendientes debajo.",
                            size=14,
                            color=TEAL_LIGHT,
                        ),
                    ],
                ),
                ft.Button(
                    content=ft.Text(
                        "Ver Solicitudes Nuevas",
                        size=13,
                        weight=ft.FontWeight.W_600,
                        color=BG_WHITE,
                    ),
                    bgcolor=ORANGE,
                    height=36,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
                        padding=ft.Padding(20, 10, 20, 10),
                    ),
                    on_click=lambda _: page.go("/admin/inscripciones"),
                ),
            ],
        ),
    )

    # ==================== 2. TARJETAS DE MÉTRICAS (KPIS) ====================
    def kpi_card(titulo: str, valor: str, subtitulo: str, icono: ft.IconData, icon_bg: str) -> ft.Container:
        return ft.Container(
            expand=True,
            height=158,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=24,
            content=ft.Column(
                spacing=16,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(titulo, size=13, weight=ft.FontWeight.W_600, color=MUTED),
                            ft.Container(
                                width=38,
                                height=36,
                                bgcolor=icon_bg,
                                border_radius=10,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(icono, size=18, color=TEAL_DARK),
                            ),
                        ],
                    ),
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(valor, size=32, weight=ft.FontWeight.W_800, color=TEAL_DARK),
                            ft.Text(subtitulo, size=12, color=MUTED),
                        ],
                    ),
                ],
            ),
        )

    kpis_row = ft.Row(
        spacing=20,
        controls=[
            kpi_card(
                "ALUMNOS MATRICULADOS",
                "1,248",
                "98% asistencia promedio hoy",
                ft.Icons.PEOPLE_OUTLINE,
                TEAL_LIGHT,
            ),
            kpi_card(
                "PERSONAL DOCENTE",
                "86",
                "3 profesores con licencia activa",
                ft.Icons.WORK_OUTLINE,
                BADGE_YELLOW_BG,
            ),
            kpi_card(
                "INSCRIPCIONES PENDIENTES",
                "45",
                "Requieren validación de secretaría",
                ft.Icons.DESCRIPTION_OUTLINED,
                TEAL_LIGHT,
            ),
            kpi_card(
                "CURSOS ACTIVOS",
                "32",
                "Salas iniciales a secundarios completos",
                ft.Icons.FOLDER_OPEN_OUTLINED,
                TEAL_LIGHT,
            ),
        ],
    )

    # ==================== 3. ACCESOS DIRECTOS ADMINISTRATIVOS ====================
    def shortcut_item(
        titulo: str,
        subtitulo: str,
        icono: ft.IconData,
        bg_icon: str,
        color_icon: str,
        ruta: str,
    ) -> ft.Container:
        return ft.Container(
            height=60,
            bgcolor=BG_PAGE,
            border_radius=BORDER_RADIUS,
            padding=12,
            on_click=lambda _: page.go(ruta),
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=36,
                        height=36,
                        bgcolor=bg_icon,
                        border_radius=BORDER_RADIUS,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(icono, size=18, color=color_icon),
                    ),
                    ft.Column(
                        spacing=2,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text(titulo, size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR),
                            ft.Text(subtitulo, size=11, color=MUTED),
                        ],
                    ),
                ],
            ),
        )

    shortcuts_card = ft.Container(
        width=450,
        height=367,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text(
                    "Accesos Directos Administrativos",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
                ft.Column(
                    spacing=12,
                    controls=[
                        shortcut_item(
                            "Registrar Nuevo Alumno",
                            "Formulario unificado K-12",
                            ft.Icons.PERSON_ADD_ALT_1_OUTLINED,
                            TEAL_LIGHT,
                            TEAL_DARK,
                            "/admin/alumnos/nuevo",
                        ),
                        shortcut_item(
                            "Cargar Calificaciones",
                            "Boletines de trimestre en curso",
                            ft.Icons.MENU_BOOK_OUTLINED,
                            BADGE_YELLOW_BG,
                            ORANGE,
                            "/admin/calificaciones",
                        ),
                        shortcut_item(
                            "Asignar Ruta de Transporte",
                            "Zonas norte, sur y centro",
                            ft.Icons.DIRECTIONS_BUS_OUTLINED,
                            TEAL_LIGHT,
                            ONLINE_GREEN,
                            "/admin/transporte",
                        ),
                        shortcut_item(
                            "Emitir Boletín General",
                            "Reportes consolidados por nivel",
                            ft.Icons.PRINT_OUTLINED,
                            BG_PAGE,
                            MUTED,
                            "/admin/reportes/boletines",
                        ),
                    ],
                ),
            ],
        ),
    )

    # ==================== 4. ÚLTIMOS MOVIMIENTOS ====================
    def activity_item(
        texto_bold: str,
        texto_regular: str,
        tiempo: str,
        categoria: str,
        color_linea: str,
        color_badge: str,
    ) -> ft.Row:
        return ft.Row(
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=4,
                    height=40,
                    border_radius=2,
                    bgcolor=color_linea,
                ),
                ft.Column(
                    spacing=4,
                    expand=True,
                    controls=[
                        ft.Text(
                            spans=[
                                ft.TextSpan(texto_bold, ft.TextStyle(weight=ft.FontWeight.BOLD, color=TEXT_COLOR)),
                                ft.TextSpan(f" {texto_regular}", ft.TextStyle(color=TEXT_COLOR)),
                            ],
                            size=13,
                        ),
                        ft.Row(
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text(tiempo, size=11, color=MUTED),
                                ft.Text("•", size=11, color=MUTED),
                                ft.Text(
                                    categoria.upper(),
                                    size=10,
                                    weight=ft.FontWeight.W_600,
                                    color=color_badge,
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

    activities_card = ft.Container(
        expand=True,
        height=367,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "Últimos Movimientos del Sistema",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=TEAL_DARK,
                        ),
                        ft.TextButton(
                            "Ver Historial Completo",
                            style=ft.ButtonStyle(color=ORANGE, padding=0),
                            on_click=lambda _: page.go("/admin/historial"),
                        ),
                    ],
                ),
                ft.Column(
                    spacing=16,
                    controls=[
                        activity_item(
                            "Preceptora Nivel Secundario",
                            "Registró la asistencia del aula 4to Año 'A' - Turno Mañana.",
                            "Hace 10 mins",
                            "Asistencia",
                            TEAL,
                            TEAL,
                        ),
                        activity_item(
                            "Administración Central",
                            "Aprobó el pago de arancel e inscripción 2025 para alumno ingresante Legajo #4928.",
                            "Hace 45 mins",
                            "Inscripción",
                            ONLINE_GREEN,
                            ONLINE_GREEN,
                        ),
                        activity_item(
                            "Secretaría Inicial",
                            "Actualizó los cupos correspondientes para Sala de 4 años (Turno Tarde).",
                            "Hace 2 horas",
                            "Sistema",
                            AMBER_STATE,
                            AMBER_STATE,
                        ),
                        activity_item(
                            "Prof. Martínez Román",
                            "Modificó las materias a cargo correspondientes a Física Aplicada.",
                            "Ayer, 18:30",
                            "Docentes",
                            ORANGE,
                            ORANGE,
                        ),
                    ],
                ),
            ],
        ),
    )

    bottom_row = ft.Row(
        spacing=24,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[shortcuts_card, activities_card],
    )

    # ==================== 5. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Tablero Principal de Control",
        active_route="/admin/dashboard",
        content_controls=[
            welcome_banner,
            kpis_row,
            bottom_row,
        ],
    )