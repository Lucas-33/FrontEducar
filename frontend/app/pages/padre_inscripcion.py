import flet as ft
from frontend.app.components.constants import (
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    ONLINE_GREEN,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.form_controls import status_badge
from frontend.app.components.portal_layout import portal_layout


def get_padre_inscripcion_view(page: ft.Page) -> ft.Row:
    """Retorna la vista del portal de familias para la reinscripción anual de cursado."""

    # ==================== 1. BANNER DEL PERÍODO ====================
    banner_periodo = ft.Container(
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
                    content=ft.Icon(ft.Icons.APP_REGISTRATION, size=22, color=TEAL),
                ),
                ft.Column(
                    spacing=3,
                    expand=True,
                    controls=[
                        ft.Text("Período de Reinscripción Lectiva 2027", size=17, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                        ft.Text("Confirme la plaza y verifique los requisitos académicos y administrativos para el próximo año.", size=13, color=MUTED),
                    ],
                ),
                status_badge("Abierto"),
            ],
        ),
    )

    # ==================== 2. SELECCIÓN DE ALUMNO ====================
    info_alumno_card = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=12,
                            controls=[
                                ft.Container(
                                    width=44,
                                    height=44,
                                    bgcolor=TEAL_LIGHT,
                                    border_radius=22,
                                    alignment=ft.Alignment(0, 0),
                                    content=ft.Text("SA", size=16, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                                ),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text("Santiago Almirón", size=17, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                                        ft.Text("Legajo #10245 · Cursando actualmente: 5to Año B (Nivel Secundario)", size=13, color=MUTED),
                                    ],
                                ),
                            ],
                        ),
                        status_badge("Regular"),
                    ],
                ),
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                ft.ResponsiveRow(
                    columns=12,
                    spacing=16,
                    controls=[
                        ft.Container(
                            col={"sm": 12, "md": 4},
                            content=ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text("Curso a Postular para 2027", size=12, weight=ft.FontWeight.W_600, color=MUTED),
                                    ft.Text("6to Año — División A", size=15, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                                ],
                            ),
                        ),
                        ft.Container(
                            col={"sm": 12, "md": 4},
                            content=ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text("Orientación Académica", size=12, weight=ft.FontWeight.W_600, color=MUTED),
                                    ft.Text("Ciencias Naturales y Exactas", size=15, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                                ],
                            ),
                        ),
                        ft.Container(
                            col={"sm": 12, "md": 4},
                            content=ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text("Régimen Horario", size=12, weight=ft.FontWeight.W_600, color=MUTED),
                                    ft.Text("Jornada Extendida + Deportes", size=15, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )

    # ==================== 3. REQUISITOS Y DOCUMENTACIÓN ====================
    def item_requisito(titulo: str, estado: str, es_valido: bool) -> ft.Row:
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE if es_valido else ft.Icons.ERROR_OUTLINE,
                            size=18,
                            color=ONLINE_GREEN if es_valido else ORANGE,
                        ),
                        ft.Text(titulo, size=14, color=TEXT_COLOR),
                    ],
                ),
                ft.Container(
                    padding=ft.Padding(8, 3, 8, 3),
                    bgcolor="#EBFEE6" if es_valido else "#FFF3E7",
                    border_radius=4,
                    content=ft.Text(
                        estado,
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=ONLINE_GREEN if es_valido else ORANGE,
                    ),
                ),
            ],
        )

    doc_card = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Estado de la Documentación Obligatoria", size=17, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Text("Verifique que todos los ítems se encuentren al día antes de confirmar la reinscripción.", size=13, color=MUTED),
                ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                item_requisito("Ficha Médica y Apto Físico Vigente", "Aprobado", True),
                item_requisito("Libre Deuda Cuota Escolar 2026", "Al Día", True),
                item_requisito("Fotocopia DNI del Alumno y Tutores", "Actualizado", True),
                item_requisito("Certificado de Vacunación Oficial", "Pendiente Presentar", False),
            ],
        ),
    )

    # ==================== 4. CONFIRMACIÓN FINAL ====================
    alerta_resultado = ft.Text("", size=13, weight=ft.FontWeight.W_600)

    def confirmar_inscripcion(e):
        alerta_resultado.value = "✓ Solicitud de reinscripción 2027 enviada correctamente a Secretaría Académica."
        alerta_resultado.color = TEAL
        alerta_resultado.update()

    acciones_card = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            alerta_resultado,
            ft.Button(
                "CONFIRMAR REINSCRIPCIÓN 2027",
                bgcolor=TEAL,
                color="white",
                height=CONTROL_HEIGHT,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
                on_click=confirmar_inscripcion,
            ),
        ],
    )

    return portal_layout(
        page=page,
        titulo="Inscripción de Cursado — Ciclo Lectivo",
        active_route="/portal/padre/inscripcion",
        rol="Padre",
        content_controls=[
            banner_periodo,
            info_alumno_card,
            doc_card,
            acciones_card,
        ],
    )