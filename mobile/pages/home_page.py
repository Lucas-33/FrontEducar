import flet as ft

from mobile.api_client import mobile_api
from mobile.components.constants import (
    BADGE_GREEN_BG,
    BADGE_GREEN_TXT,
    BADGE_RED_BG,
    BADGE_RED_TXT,
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


def get_home_page(page: ft.Page, on_navegar_tab) -> list[ft.Control]:
    """Pantalla principal (Dashboard) móvil para el tutor."""

    usuario = getattr(page, "auth_user", "Familia")
    id_padre = getattr(page, "auth_padre_id", None)

    # Estado
    txt_deuda = ft.Text("...", size=24, weight=ft.FontWeight.BOLD, color=TEAL_DARK)
    txt_sub_deuda = ft.Text("Consultando cuenta...", size=12, color=MUTED)
    btn_pagar_directo = ft.Button(
        "Pagar Cuotas",
        icon=ft.Icons.PAYMENTS_OUTLINED,
        bgcolor=TEAL,
        color=BG_WHITE,
        height=38,
        visible=False,
        on_click=lambda _: on_navegar_tab(1),
    )

    lista_hijos_col = ft.Column(spacing=8)

    async def cargar_datos():
        try:
            # 1. Facturas y saldo
            facturas = await mobile_api.get_mis_facturas()
            pendientes = [
                f for f in facturas if f.get("estado", "PENDIENTE").upper() != "PAGADA"
            ]
            total_deuda = sum(float(f.get("total", 0)) for f in pendientes)

            if total_deuda > 0:
                txt_deuda.value = f"$ {total_deuda:,.2f}"
                txt_deuda.color = BADGE_RED_TXT
                txt_sub_deuda.value = f"{len(pendientes)} cuota(s) pendiente(s)"
                txt_sub_deuda.color = BADGE_RED_TXT
                btn_pagar_directo.visible = True
            else:
                txt_deuda.value = "$ 0.00"
                txt_deuda.color = ONLINE_GREEN
                txt_sub_deuda.value = "Tu cuenta se encuentra al día"
                txt_sub_deuda.color = ONLINE_GREEN
                btn_pagar_directo.visible = False

            # 2. Hijos a cargo
            if id_padre:
                hijos = await mobile_api.get_hijos(id_padre)
                tarjetas_hijos = []
                for h in hijos:
                    nombre_completo = f"{h.get('apellido', '')}, {h.get('nombre', '')}"
                    legajo = h.get("legajo", "-")
                    tarjetas_hijos.append(
                        ft.Container(
                            bgcolor=BG_WHITE,
                            padding=12,
                            border_radius=BORDER_RADIUS,
                            border=ft.Border.all(1, BORDER_COLOR),
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            ft.Container(
                                                width=34,
                                                height=34,
                                                border_radius=17,
                                                bgcolor=TEAL_LIGHT,
                                                alignment=ft.Alignment(0, 0),
                                                content=ft.Icon(
                                                    ft.Icons.FACE,
                                                    color=TEAL_DARK,
                                                    size=18,
                                                ),
                                            ),
                                            ft.Column(
                                                spacing=1,
                                                controls=[
                                                    ft.Text(
                                                        nombre_completo,
                                                        size=13,
                                                        weight=ft.FontWeight.BOLD,
                                                        color=TEXT_COLOR,
                                                    ),
                                                    ft.Text(
                                                        f"Legajo #{legajo}",
                                                        size=11,
                                                        color=MUTED,
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    ft.Container(
                                        bgcolor=BADGE_GREEN_BG,
                                        padding=ft.Padding(8, 3, 8, 3),
                                        border_radius=10,
                                        content=ft.Text(
                                            "REGULAR",
                                            size=10,
                                            weight=ft.FontWeight.BOLD,
                                            color=BADGE_GREEN_TXT,
                                        ),
                                    ),
                                ],
                            ),
                        )
                    )
                lista_hijos_col.controls = (
                    tarjetas_hijos
                    if tarjetas_hijos
                    else [ft.Text("No hay alumnos vinculados.", size=12, color=MUTED)]
                )

        except Exception as ex:
            txt_deuda.value = "Error"
            txt_sub_deuda.value = str(ex)

        page.update()

    page.run_task(cargar_datos)

    # Tarjeta de Estado Financiero
    tarjeta_financiera = ft.Container(
        bgcolor=BG_WHITE,
        padding=18,
        border_radius=CARD_RADIUS,
        border=ft.Border.all(1, BORDER_COLOR),
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "Estado de Cuenta",
                            size=12,
                            color=MUTED,
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.Icon(
                            ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                            color=TEAL,
                            size=20,
                        ),
                    ],
                ),
                txt_deuda,
                txt_sub_deuda,
                btn_pagar_directo,
            ],
        ),
    )

    # Accesos rápidos móviles
    def acceso_rapido_card(
        titulo: str, icono: ft.IconData, color_icono: str, tab_destino: int
    ):
        return ft.Container(
            expand=True,
            bgcolor=BG_WHITE,
            padding=14,
            border_radius=BORDER_RADIUS,
            border=ft.Border.all(1, BORDER_COLOR),
            on_click=lambda _: on_navegar_tab(tab_destino),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Container(
                        width=38,
                        height=38,
                        border_radius=19,
                        bgcolor=TEAL_LIGHT,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(icono, color=color_icono, size=20),
                    ),
                    ft.Text(
                        titulo,
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_COLOR,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )

    grid_accesos = ft.Row(
        spacing=10,
        controls=[
            acceso_rapido_card("Cuotas & Pagos", ft.Icons.RECEIPT_LONG, TEAL, 1),
            acceso_rapido_card("Servicios", ft.Icons.DIRECTIONS_BUS, ORANGE, 2),
            acceso_rapido_card("Mi Perfil", ft.Icons.PERSON, TEAL_DARK, 3),
        ],
    )

    return [
        ft.Column(
            spacing=1,
            controls=[
                ft.Text(
                    f"Hola, {usuario} 👋",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
                ft.Text(
                    "Bienvenido al portal móvil de gestión escolar.",
                    size=12,
                    color=MUTED,
                ),
            ],
        ),
        tarjeta_financiera,
        ft.Text(
            "Accesos Directos", size=14, weight=ft.FontWeight.BOLD, color=TEAL_DARK
        ),
        grid_accesos,
        ft.Text("Mis Hijos", size=14, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
        lista_hijos_col,
    ]
