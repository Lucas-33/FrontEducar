import flet as ft
from frontend.app.api_client import api_client
from frontend.app.components.portal_layout import portal_layout
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_WHITE,
    BORDER_COLOR,
    CARD_RADIUS,
    MUTED,
    ONLINE_GREEN,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)


async def get_padre_dashboard_view(page: ft.Page) -> ft.Container:
    # Textos que inician en "Calculando..." hasta que la API responda
    estado_deuda = ft.Text(
        "Calculando...", size=24, weight=ft.FontWeight.BOLD, color=TEAL_DARK
    )
    estado_vencimiento = ft.Text(
        "-", size=20, weight=ft.FontWeight.BOLD, color=TEXT_COLOR
    )

    def crear_tarjeta_resumen(
        titulo: str,
        control_valor: ft.Control,
        icono: ft.IconData,
        color_icono: str,
        color_fondo: str,
    ):
        return ft.Container(
            bgcolor=BG_WHITE,
            padding=20,
            border_radius=CARD_RADIUS,
            border=ft.Border.all(1, BORDER_COLOR),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(
                                titulo, size=13, color=MUTED, weight=ft.FontWeight.W_600
                            ),
                            control_valor,
                        ],
                    ),
                    ft.Container(
                        width=48,
                        height=48,
                        bgcolor=color_fondo,
                        border_radius=24,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(icono, color=color_icono, size=24),
                    ),
                ],
            ),
        )

    async def cargar_datos():
        try:
            # 🚀 LLAMADA A LA API REAL
            facturas_reales = await api_client.get_mis_facturas()

            # Filtramos solo las facturas que no están pagadas
            pendientes = [
                f
                for f in facturas_reales
                if f.get("estado", "PENDIENTE").upper() != "PAGADA"
            ]

            # 1. Calculamos la suma total de la deuda
            deuda = sum(float(f["total"]) for f in pendientes)
            estado_deuda.value = f"$ {deuda:,.2f}"
            estado_deuda.color = BADGE_RED_TXT if deuda > 0 else ONLINE_GREEN

            # 2. Buscamos el próximo vencimiento
            if pendientes:
                # Tomamos la fecha de la factura pendiente más antigua (la última de la lista ordenada desc)
                estado_vencimiento.value = pendientes[-1].get("fecha_vencimiento", "-")
                estado_vencimiento.color = TEXT_COLOR
            else:
                estado_vencimiento.value = "Al día"
                estado_vencimiento.color = ONLINE_GREEN

        except Exception as e:
            estado_deuda.value = "Error de red"
            estado_deuda.size = 16
            estado_vencimiento.value = "-"

        page.update()

    # Ejecutamos la petición a la API en segundo plano
    page.run_task(cargar_datos)

    btn_ir_facturas = ft.Container(
        margin=ft.Margin(top=16, right=0, bottom=0, left=0),
        content=ft.Button(
            "Ver todas mis facturas",
            icon=ft.Icons.RECEIPT_LONG,
            icon_color=BG_WHITE,
            bgcolor=TEAL_DARK,
            color=BG_WHITE,
            height=45,
            on_click=lambda _: page.go("/portal/padre/facturas"),
        ),
    )

    contenido = [
        ft.Text(
            "Resumen de Cuenta", size=22, weight=ft.FontWeight.BOLD, color=TEAL_DARK
        ),
        ft.ResponsiveRow(
            controls=[
                ft.Container(
                    col={"xs": 12, "sm": 6},
                    content=crear_tarjeta_resumen(
                        "Total Adeudado",
                        estado_deuda,
                        ft.Icons.ACCOUNT_BALANCE_WALLET,
                        TEAL,
                        TEAL_LIGHT,
                    ),
                ),
                ft.Container(
                    col={"xs": 12, "sm": 6},
                    content=crear_tarjeta_resumen(
                        "Próximo Vencimiento",
                        estado_vencimiento,
                        ft.Icons.CALENDAR_TODAY,
                        "#F59E0B",
                        "#FEF3C7",
                    ),
                ),
            ]
        ),
        btn_ir_facturas,
    ]

    return portal_layout(
        page=page,
        titulo="Mi Resumen",
        active_route="/portal/padre/dashboard",
        rol="Padre",
        content_controls=contenido,
    )
