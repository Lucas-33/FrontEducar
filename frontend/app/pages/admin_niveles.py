import flet as ft
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.form_controls import status_badge
from frontend.app.components.table_view import (
    create_table_container,
    create_table_header,
)


def get_admin_niveles_view(page: ft.Page) -> ft.Row:
    """Retorna la vista de configuración y control de Niveles Educativos."""

    # ==================== 1. TARJETAS DE NIVELES (KPIS RESUMEN) ====================
    def nivel_kpi_card(
        titulo: str,
        edades: str,
        jornada: str,
        cursos: str,
        alumnos: str,
        coordinador: str,
        icono: ft.IconData,
    ) -> ft.Container:
        return ft.Container(
            expand=True,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=24,
            content=ft.Column(
                spacing=14,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=42,
                                height=42,
                                bgcolor=TEAL_LIGHT,
                                border_radius=BORDER_RADIUS,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(icono, size=22, color=TEAL_DARK),
                            ),
                            status_badge("Activo"),
                        ],
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                            ft.Text(edades, size=12, color=ORANGE, weight=ft.FontWeight.W_600),
                        ],
                    ),
                    ft.Text(f"Régimen: {jornada}", size=12, color=MUTED),
                    ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Cursos Activos:", size=12, color=MUTED),
                            ft.Text(cursos, size=12, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Matrícula:", size=12, color=MUTED),
                            ft.Text(alumnos, size=12, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Coordinación:", size=12, color=MUTED),
                            ft.Text(coordinador, size=12, weight=ft.FontWeight.W_500, color=TEXT_COLOR),
                        ],
                    ),
                ],
            ),
        )

    niveles_cards_row = ft.Row(
        spacing=20,
        controls=[
            nivel_kpi_card(
                "Nivel Inicial",
                "Salas de 3, 4 y 5 años",
                "Jornada Extendida (08:00 a 16:00 hs)",
                "6 salas",
                "148 alumnos",
                "Prof. Mariana Benítez",
                ft.Icons.CHILD_CARE,
            ),
            nivel_kpi_card(
                "Nivel Primario",
                "1er a 6to Grado",
                "Doble Escolaridad (07:30 a 16:30 hs)",
                "14 divisiones",
                "512 alumnos",
                "Lic. Andrea Romero",
                ft.Icons.MENU_BOOK_OUTLINED,
            ),
            nivel_kpi_card(
                "Nivel Secundario",
                "1er a 6to Año (Ciclo Superior)",
                "Doble Turno y Deportes (07:30 a 17:30 hs)",
                "12 divisiones",
                "588 alumnos",
                "Prof. Carlos Maidana",
                ft.Icons.SCHOOL_OUTLINED,
            ),
        ],
    )

    # ==================== 2. DETALLE DE AUTORIDADES Y PLANES ====================
    niveles_data = [
        {"codigo": "NIV-INI", "nombre": "Nivel Inicial", "idiomas": "Inglés Inicial, Portugués", "horario": "08:00 a 16:00 hs", "servicios": "Comedor, Apoyo, Transporte", "estado": "Activo"},
        {"codigo": "NIV-PRI", "nombre": "Nivel Primario", "idiomas": "Inglés Intensivo, Portugués, Francés", "horario": "07:30 a 16:30 hs", "servicios": "Comedor, Deportes, Transporte", "estado": "Activo"},
        {"codigo": "NIV-SEC", "nombre": "Nivel Secundario", "idiomas": "Inglés Bilingüe, Francés, Portugués", "horario": "07:30 a 17:30 hs", "servicios": "Comedor, Deportes Competición, Transporte", "estado": "Activo"},
    ]

    columnas_niveles = [
        ("Código", 110, False),
        ("Nivel Institucional", 180, False),
        ("Oferta de Idiomas", 260, False),
        ("Franja Horaria", 190, False),
        ("Servicios Incluidos", 280, False),
        ("Estado", 100, False),
        ("Acciones", None, True),
    ]

    header_table = create_table_header(columnas_niveles)

    def nivel_row(item: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=110, content=ft.Text(item["codigo"], size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK)),
                    ft.Container(width=180, content=ft.Text(item["nombre"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR)),
                    ft.Container(width=260, content=ft.Text(item["idiomas"], size=13, color=TEXT_COLOR)),
                    ft.Container(width=190, content=ft.Text(item["horario"], size=13, color=MUTED)),
                    ft.Container(width=280, content=ft.Text(item["servicios"], size=13, color=TEXT_COLOR)),
                    ft.Container(width=100, content=status_badge(item["estado"])),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=12,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_size=16, icon_color=TEAL, tooltip="Modificar Nivel", padding=0),
                                ft.IconButton(icon=ft.Icons.INFO_OUTLINE, icon_size=16, icon_color=MUTED, tooltip="Ver Currícula", padding=0),
                            ],
                        ),
                    ),
                ],
            ),
        )

    table_container = create_table_container(
        header=header_table,
        rows=[nivel_row(n) for n in niveles_data],
    )

    # ==================== 3. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Estructura Académica — Niveles Educativos K-12",
        active_route="/admin/niveles",
        content_controls=[
            niveles_cards_row,
            ft.Text("Detalle Pedagógico y Servicios por Nivel", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
            table_container,
        ],
    )