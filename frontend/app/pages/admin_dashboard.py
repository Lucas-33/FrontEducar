import flet as ft

from frontend.app.api_client import api_client
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


async def get_admin_dashboard_view(page: ft.Page) -> ft.Row:
    """Retorna la vista completa del panel interno Educar SGE usando AdminLayout
    con las métricas reales calculadas desde la base de datos."""

    token = getattr(page, "auth_token", None)
    if token and api_client.token != token:
        api_client.set_token(token)

    resumen = {
        "alumnos_activos": "—",
        "docentes_activos": "—",
        "cursos": "—",
        "niveles": "—",
        "solicitudes_pendientes": "—",
        "mensajes_no_leidos": "—",
        "transporte_activos": "—",
        "comedor_activos": "—",
    }
    try:
        resumen.update(await api_client.get_resumen_dashboard())
    except Exception:
        pass

    usuario = getattr(page, "auth_user", None) or "Administración"

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
                            f"¡Buen día, {usuario}! Ciclo Lectivo Activo",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=BG_WHITE,
                        ),
                        ft.Text(
                            f"Hoy hay {resumen['solicitudes_pendientes']} solicitudes de admisión pendientes "
                            f"y {resumen['mensajes_no_leidos']} mensajes de contacto sin leer.",
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
    def kpi_card(
        titulo: str, valor: str, subtitulo: str, icono: ft.IconData, icon_bg: str
    ) -> ft.Container:
        return ft.Container(
            expand=True,
            height=158,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=20,
            content=ft.Column(
                spacing=16,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                titulo, size=12, weight=ft.FontWeight.W_600, color=MUTED
                            ),
                            ft.Container(
                                width=36,
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
                            ft.Text(
                                valor,
                                size=30,
                                weight=ft.FontWeight.W_800,
                                color=TEAL_DARK,
                            ),
                            ft.Text(subtitulo, size=11, color=MUTED),
                        ],
                    ),
                ],
            ),
        )

    kpis_row = ft.Row(
        spacing=16,
        controls=[
            kpi_card(
                "ALUMNOS MATRICULADOS",
                str(resumen["alumnos_activos"]),
                "Matrícula activa en el sistema",
                ft.Icons.PEOPLE_OUTLINE,
                TEAL_LIGHT,
            ),
            kpi_card(
                "PERSONAL DOCENTE",
                str(resumen["docentes_activos"]),
                "Plantel docente activo",
                ft.Icons.WORK_OUTLINE,
                BADGE_YELLOW_BG,
            ),
            kpi_card(
                "INSCRIPCIONES PENDIENTES",
                str(resumen["solicitudes_pendientes"]),
                "Solicitudes de admisión en secretaría",
                ft.Icons.DESCRIPTION_OUTLINED,
                TEAL_LIGHT,
            ),
            kpi_card(
                "CURSOS ACTIVOS",
                str(resumen["cursos"]),
                f"{resumen['niveles']} niveles educativos",
                ft.Icons.FOLDER_OPEN_OUTLINED,
                TEAL_LIGHT,
            ),
        ],
    )

    # ==================== 3. ACCESOS DIRECTOS COMPACTOS ====================
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
            padding=10,
            on_click=lambda _: page.go(ruta),
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=34,
                        height=34,
                        bgcolor=bg_icon,
                        border_radius=BORDER_RADIUS,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(icono, size=16, color=color_icon),
                    ),
                    ft.Column(
                        spacing=2,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                titulo,
                                size=13,
                                weight=ft.FontWeight.W_600,
                                color=TEXT_COLOR,
                            ),
                            ft.Text(subtitulo, size=11, color=MUTED),
                        ],
                    ),
                ],
            ),
        )

    shortcuts_card = ft.Container(
        width=380,
        height=367,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text(
                    "Accesos Directos",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
                ft.Column(
                    spacing=10,
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
                            "Materias y Cursos",
                            "Plan de estudios vigente",
                            ft.Icons.MENU_BOOK_OUTLINED,
                            BADGE_YELLOW_BG,
                            ORANGE,
                            "/admin/materias",
                        ),
                        shortcut_item(
                            "Transporte Escolar",
                            "4 recorridos oficiales",
                            ft.Icons.DIRECTIONS_BUS_OUTLINED,
                            TEAL_LIGHT,
                            ONLINE_GREEN,
                            "/admin/transporte",
                        ),
                        shortcut_item(
                            "Reportes Directivos",
                            "Listados consolidados",
                            ft.Icons.PRINT_OUTLINED,
                            BG_PAGE,
                            MUTED,
                            "/admin/reportes",
                        ),
                    ],
                ),
            ],
        ),
    )

    # ==================== 4. ACTIVIDADES (FLUIDA) ====================
    def activity_item(
        texto_bold: str,
        texto_regular: str,
        tiempo: str,
        categoria: str,
        color_linea: str,
        color_badge: str,
    ) -> ft.Row:
        return ft.Row(
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(width=4, height=38, border_radius=2, bgcolor=color_linea),
                ft.Column(
                    spacing=3,
                    expand=True,
                    controls=[
                        ft.Text(
                            spans=[
                                ft.TextSpan(
                                    texto_bold,
                                    ft.TextStyle(
                                        weight=ft.FontWeight.BOLD, color=TEXT_COLOR
                                    ),
                                ),
                                ft.TextSpan(
                                    f" {texto_regular}", ft.TextStyle(color=TEXT_COLOR)
                                ),
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
            spacing=18,
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
                            "Ver Historial",
                            style=ft.ButtonStyle(color=ORANGE, padding=0),
                            on_click=lambda _: None,
                        ),
                    ],
                ),
                ft.Column(
                    spacing=14,
                    controls=[
                        activity_item(
                            "Preceptora Secundario",
                            "Registró asistencia de 4to Año 'A'.",
                            "Hace 10 mins",
                            "Asistencia",
                            TEAL,
                            TEAL,
                        ),
                        activity_item(
                            "Administración Central",
                            "Validó la inscripción del Legajo #4928.",
                            "Hace 45 mins",
                            "Inscripción",
                            ONLINE_GREEN,
                            ONLINE_GREEN,
                        ),
                        activity_item(
                            "Secretaría Inicial",
                            "Actualizó cupos en Sala de 4 años.",
                            "Hace 2 horas",
                            "Sistema",
                            AMBER_STATE,
                            AMBER_STATE,
                        ),
                        activity_item(
                            "Prof. Martínez Román",
                            "Cargó horarios de Física y Química.",
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
        spacing=20,
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
